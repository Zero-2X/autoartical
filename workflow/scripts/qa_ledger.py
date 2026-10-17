#!/usr/bin/env python3
"""Hash-bound QA ledger: automatic checks and human review kept apart.

Two record kinds live under ``workspace/quality/``:

``auto-check.json``   written by ``word_pipeline.py``: measurable layout facts.
``human-review.json`` written here by ``record``: what a person (or a reviewing
                      agent) actually looked at, how, and what they found.

A record is *current* only if every hash it captured still matches the files
on disk: the manuscript source, each embedded asset, the exporter code, the
delivered DOCX/PDF and, for human review, the page renders that were inspected.
``verify`` recomputes everything and reports stale records; the export gate
calls it, so editing a figure, the text or the exporter invalidates old passes.

Human review rules:

* the inspection method is recorded (``full-page`` at ≥100 dpi, ``thumbnail``,
  ``text-only``); only ``full-page`` coverage of every page may be described as
  “逐页核验”;
* each finding is stored with page and severity; open ``blocker``/``major``
  findings keep the record at ``fail``;
* semantic review (argument, evidence, figures vs. text) is a separate section
  and cannot be satisfied by layout inspection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word_pipeline import input_fingerprint, sha256_file  # noqa: E402

METHODS = {"full-page", "thumbnail", "text-only"}
SEMANTIC_ITEMS = (
    "argument_chain",      # 研究问题链是否闭合
    "evidence_strength",   # 结论强度与证据匹配
    "figures_match_text",  # 图意与正文、证据边界一致
    "tables_interpretable",# 表格维度、单位、来源、缺失值说明
    "terminology",         # 术语、缩写、符号统一
    "planned_vs_measured", # 计划/待实测与实测结果区分
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def quality_dir(topic: Path) -> Path:
    return topic / "workspace" / "quality"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def check_auto(topic: Path, source: Path, docx: Path, pdf: Path) -> dict:
    record = load(quality_dir(topic) / "auto-check.json")
    if not record:
        return {"status": "missing"}
    stale = []
    markdown = source.read_text(encoding="utf-8")
    current = input_fingerprint(markdown, topic)
    if current["source_markdown_sha256"] != record["inputs"]["source_markdown_sha256"]:
        stale.append("正文源文件已变化")
    for name, digest in current["assets"].items():
        if record["inputs"]["assets"].get(name) != digest:
            stale.append(f"图像资产变化或新增：{name}")
    for name in set(record["inputs"]["assets"]) - set(current["assets"]):
        stale.append(f"图像资产已移除：{name}")
    for name, digest in current["exporter_code"].items():
        if record["inputs"]["exporter_code"].get(name) != digest:
            stale.append(f"排版代码变化：{name}")
    if not docx.exists() or sha256_file(docx) != record["outputs"]["docx_sha256"]:
        stale.append("DOCX 与检查记录不一致")
    if not pdf.exists() or sha256_file(pdf) != record["outputs"]["pdf_sha256"]:
        stale.append("PDF 与检查记录不一致")
    return {"status": "stale" if stale else record["verdict"], "stale_reasons": stale,
            "failures": record.get("failures", []), "warnings": record.get("warnings", []),
            "page_counts": record.get("layout", {}).get("counts")}


def check_human(topic: Path) -> dict:
    record = load(quality_dir(topic) / "human-review.json")
    auto = load(quality_dir(topic) / "auto-check.json")
    if not record:
        return {"status": "missing"}
    stale = []
    if not auto or record.get("pdf_sha256") != auto.get("outputs", {}).get("pdf_sha256"):
        stale.append("人工审查针对的 PDF 已被替换")
    render_dir = quality_dir(topic) / "pages"
    for page in record.get("visual", {}).get("pages_inspected", []):
        image = render_dir / f"page-{page['page']:03}.png"
        if not image.exists() or sha256_file(image) != page["render_sha256"]:
            stale.append(f"第 {page['page']} 页渲染图已变化")
            break
    open_blockers = [f for f in record.get("findings", []) if f["status"] == "open" and f["severity"] in ("blocker", "major")]
    semantic = record.get("semantic", {})
    missing_semantic = [k for k in SEMANTIC_ITEMS if semantic.get(k, {}).get("verdict") not in ("pass", "fail")]
    failed_semantic = [k for k in SEMANTIC_ITEMS if semantic.get(k, {}).get("verdict") == "fail"]
    status = "stale" if stale else ("fail" if open_blockers or failed_semantic or missing_semantic else "pass")
    return {"status": status, "stale_reasons": stale, "open_blockers": len(open_blockers),
            "missing_semantic": missing_semantic, "failed_semantic": failed_semantic,
            "coverage": record.get("visual", {}).get("coverage_claim")}


def cmd_record(args: argparse.Namespace) -> int:
    topic = args.topic.resolve()
    auto = load(quality_dir(topic) / "auto-check.json")
    if not auto:
        raise SystemExit("缺少 auto-check.json：先运行 word_pipeline.py 生成交付文件与页面渲染")
    pages_meta = {p["page"]: p for p in auto["pdf"]["pages"]}
    total = len(pages_meta)
    if args.pages == "all":
        pages = list(range(1, total + 1))
    else:
        pages = sorted({int(x) for x in args.pages.split(",") if x.strip()})
    if args.method not in METHODS:
        raise SystemExit(f"--method 必须是 {sorted(METHODS)}")
    render_dir = quality_dir(topic) / "pages"
    inspected = []
    for page in pages:
        image = render_dir / f"page-{page:03}.png"
        if not image.exists():
            raise SystemExit(f"缺少第 {page} 页渲染图 {image}；不能登记未查看的页面")
        inspected.append({"page": page, "render_sha256": sha256_file(image)})
    if args.method == "full-page" and set(pages) == set(range(1, total + 1)):
        coverage = f"逐页全幅查看 {total}/{total} 页"
    else:
        coverage = f"{args.method} 方式查看 {len(pages)}/{total} 页（不得表述为逐页核验）"
    findings = json.loads(Path(args.findings).read_text(encoding="utf-8")) if args.findings else []
    semantic = json.loads(Path(args.semantic).read_text(encoding="utf-8")) if args.semantic else {}
    for item in findings:
        item.setdefault("status", "open")
        if item.get("severity") not in ("blocker", "major", "minor"):
            raise SystemExit(f"findings 中 severity 无效：{item}")
    record = {
        "kind": "human-review",
        "reviewer": args.reviewer,
        "recorded_at": now(),
        "pdf_sha256": auto["outputs"]["pdf_sha256"],
        "docx_sha256": auto["outputs"]["docx_sha256"],
        "visual": {"method": args.method, "dpi": args.dpi, "pages_inspected": inspected, "coverage_claim": coverage},
        "semantic": semantic,
        "findings": findings,
        "note": args.note,
        "rule": "人工记录只陈述实际查看的内容；自动检查结论不得复制为人工结论。",
    }
    out = quality_dir(topic) / "human-review.json"
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(check_human(topic), ensure_ascii=False, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    topic = args.topic.resolve()
    result = {
        "verified_at": now(),
        "auto_check": check_auto(topic, args.source, args.docx, args.pdf),
        "human_review": check_human(topic),
    }
    result["deliverable"] = "pass" if result["auto_check"]["status"] == "pass" and result["human_review"]["status"] == "pass" else "blocked"
    out = quality_dir(topic) / "qa-status.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["deliverable"] == "pass" else 2


def cmd_render(args: argparse.Namespace) -> int:
    """Regenerate page renders from the delivered PDF (deterministic), so the
    renders need not be committed for human-review hashes to be checkable."""
    from word_pipeline import analyse_pdf

    out = quality_dir(args.topic.resolve()) / "pages"
    analyse_pdf(args.pdf.resolve(), out)
    print(out)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="哈希绑定的质量记录：自动检查与人工审查分开登记")
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record", help="登记人工视觉与语义审查")
    rec.add_argument("topic", type=Path)
    rec.add_argument("--reviewer", required=True)
    rec.add_argument("--method", required=True)
    rec.add_argument("--dpi", type=int, default=110)
    rec.add_argument("--pages", required=True, help="all 或逗号分隔页码")
    rec.add_argument("--findings", help="JSON 列表：page/severity/issue/action/status")
    rec.add_argument("--semantic", help="JSON 对象：各语义项 verdict 与 note")
    rec.add_argument("--note", required=True)
    rec.set_defaults(func=cmd_record)
    ver = sub.add_parser("verify", help="重新计算哈希，判断记录是否仍有效")
    ver.add_argument("topic", type=Path)
    ver.add_argument("--source", type=Path, required=True)
    ver.add_argument("--docx", type=Path, required=True)
    ver.add_argument("--pdf", type=Path, required=True)
    ver.set_defaults(func=cmd_verify)
    ren = sub.add_parser("render-pages", help="由交付 PDF 重新生成页面渲染（结果与审查时逐字节一致）")
    ren.add_argument("topic", type=Path)
    ren.add_argument("--pdf", type=Path, required=True)
    ren.set_defaults(func=cmd_render)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

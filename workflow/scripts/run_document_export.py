#!/usr/bin/env python3
"""Build the final delivery package from one formal source and enforce gates.

Pipeline (each step's output is the next step's input):

1. ``manuscript_lint``  structure, citation order, figure/table numbering,
   meta-text, unsupported result numbers;
2. content and visual gates (evidence-backed figures, editable tables);
3. ``word_pipeline``    DOCX -> Word -> PDF and automatic layout checks;
4. ``qa_ledger verify`` hash freshness of automatic and human records.

The PDF is always exported by Word from the delivered DOCX.  There is no
second layout engine, no content scaling and no page-count exception: if Word
is unavailable the run stops at HTML preview and reports ``blocked``.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_depth import DEFAULT_CONTRACT, build_content_depth_gate  # noqa: E402
from delivery_contract import build_figure_table_gate  # noqa: E402
from manuscript_lint import lint  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _resolve_image_file(source: str, base_dir: Path | None = None) -> Path | None:
    path = Path(source.strip().strip("<>"))
    candidates = [path] if path.is_absolute() else ([base_dir / path] if base_dir else []) + [Path.cwd() / path]
    return next((item.resolve() for item in candidates if item.is_file()), None)


def _image_data_uri(source: str, base_dir: Path | None = None) -> str:
    resolved = _resolve_image_file(source, base_dir)
    if resolved is None:
        return ""
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}.get(
        resolved.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(resolved.read_bytes()).decode('ascii')}"


def markdown_to_html(markdown: str, title: str, base_dir: Path | None = None, *, inline_images: bool = True) -> str:
    """Browser preview only; never a substitute for the Word/PDF delivery."""
    styles = (
        "<style>body{font-family:'SimSun','Noto Serif CJK SC',serif;color:#111;line-height:1.7;max-width:860px;margin:0 auto;}"
        "h1,h2,h3,h4{font-family:'SimHei','Noto Sans CJK SC',sans-serif;}h1{text-align:center;}"
        "p{text-align:justify;text-indent:2em;}table{border-collapse:collapse;width:100%;margin:8px 0;border-top:2px solid #000;border-bottom:2px solid #000;}"
        "th{border-bottom:1px solid #000;}th,td{padding:4px 8px;font-size:10.5pt;}"
        "figure{text-align:center;margin:14px auto;}figure img{max-width:100%;}figcaption,.caption{text-align:center;font-size:10.5pt;}"
        "</style>"
    )
    out = ["<!doctype html>", '<html lang="zh-CN"><head><meta charset="utf-8">', f"<title>{html.escape(title)}</title>", styles,
           "</head><body>", '<p class="caption">预览文件：正式版式以 Word 及其导出的 PDF 为准</p>']

    def inline(value: str) -> str:
        escaped = html.escape(value)
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
        escaped = re.sub(r"\[(\d+(?:[,，\-–]\d+)*)\]", r"<sup>[\1]</sup>", escaped)
        return escaped

    in_table = header_done = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            if in_table:
                out.append("</table>")
                in_table = False
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
        elif line.strip() == "[[TOC]]":
            out.append("<p class=\"caption\">（目录由 Word 生成）</p>")
        elif line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            if not in_table:
                out.append("<table>")
                in_table, header_done = True, False
            tag = "td" if header_done else "th"
            header_done = True
            out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
        elif re.match(r"!\[[^\]]*\]\([^)]*\)", line):
            alt, source = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line).groups()
            if inline_images:
                src = _image_data_uri(source, base_dir)
            else:
                resolved = _resolve_image_file(source, base_dir)
                src = os.path.relpath(resolved, (base_dir / "output") if base_dir else Path.cwd()).replace("\\", "/") if resolved else ""
            out.append(f'<figure><img src="{html.escape(src)}" alt="{html.escape(alt)}"><figcaption>{html.escape(alt)}</figcaption></figure>'
                       if src else f"<p>{html.escape(alt)}（图形资产缺失）</p>")
        elif re.match(r"^[表图]\s*\d+-\d+", line):
            out.append(f'<p class="caption">{inline(line)}</p>')
        elif line.startswith("$$"):
            out.append(f'<p class="caption">{html.escape(line.strip("$ "))}</p>')
        else:
            out.append(f"<p>{inline(line.lstrip('> ').lstrip('- '))}</p>")
    if in_table:
        out.append("</table>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def word_available() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import win32com.client  # noqa: F401
    except ImportError:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="以 Word 为唯一正式源导出并执行交付门禁")
    parser.add_argument("topic_dir")
    parser.add_argument("--source", default="workspace/document_writing/正式稿.md", help="正式稿 Markdown（相对主题目录）")
    parser.add_argument("--skip-word", action="store_true", help="只生成预览并报告 blocked（用于无 Word 的环境）")
    parser.add_argument("--force-rebuild", action="store_true", help="输入未变也重新导出（会使人工审查失效）")
    args = parser.parse_args()
    topic = Path(args.topic_dir).expanduser().resolve()
    source = topic / args.source
    plan_path = topic / "workspace" / "document_plan" / "section-plan.json"
    review_path = topic / "workspace" / "document_review" / "quality-gate.json"
    if not source.exists():
        raise SystemExit(f"缺少正式稿：{source}")
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else {}
    review = json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else {}
    draft = source.read_text(encoding="utf-8")
    contract = {**DEFAULT_CONTRACT, **plan.get("content_contract", {})}
    contract["target_pages"] = contract.get("target_pages") or [40, None]
    quality = topic / "workspace" / "quality"

    from cross_section_audit import load_glossary

    lint_report = lint(draft, glossary=load_glossary(topic / "workspace" / "document_plan" / "glossary.json"))
    write_json(quality / "manuscript-lint.json", lint_report)
    content_gate = build_content_depth_gate(draft, plan.get("sections", []), contract) if plan.get("sections") else {"passed": False, "failures": ["缺少 section-plan 章节计划"]}
    visual_gate = build_figure_table_gate(topic, draft, contract.get("visual_contract", {}))

    project = plan.get("project_name", topic.name) or topic.name
    slug = re.sub(r"[^\w.-]+", "_", project, flags=re.UNICODE).strip("._") or topic.name
    out_dir = topic / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    docx_out, pdf_out = out_dir / f"作品书_{slug}.docx", out_dir / f"作品书_{slug}.pdf"
    html_out = out_dir / f"作品书_{slug}.预览.html"
    html_out.write_text(markdown_to_html(draft, project, topic, inline_images=False), encoding="utf-8")

    failures: list[str] = []
    failures += [f"[正文检查] {f}" for f in lint_report["failures"]]
    failures += [f"[篇幅] {f}" for f in content_gate.get("failures", [])]
    failures += [f"[图表] {f}" for f in visual_gate.get("failures", [])]
    # A review verdict counts only for the text it reviewed.  Older gates stored
    # no hash, so their "pass" silently carried over to rewritten drafts.
    import hashlib

    draft_hash = hashlib.sha256(draft.encode("utf-8")).hexdigest()
    if review and review.get("source_sha256") != draft_hash:
        review_note = "document_review 未绑定当前正式稿（缺少或不匹配 source_sha256），不采信其结论"
    elif review.get("verdict") != "pass" and review:
        review_note = f"document_review 未通过：{review.get('verdict')}"
    else:
        review_note = ""
    if review_note:
        failures.append(f"[联合审查] {review_note}；语义审查以 human-review.json 为准")

    auto = {}
    from qa_ledger import check_auto as _check_auto

    previous = _check_auto(topic, source, docx_out, pdf_out)
    if previous["status"] in ("pass", "fail") and not args.force_rebuild:
        # Every input hash still matches: reuse the delivered files so the
        # human review of these exact pages stays valid.
        auto = json.loads((quality / "auto-check.json").read_text(encoding="utf-8"))
        failures += [f"[版式] {f}" for f in auto["failures"]]
    elif args.skip_word or not word_available():
        failures.append("[版式] 未运行 Word 导出：不能声称 DOCX/PDF 已交付或页数已核验")
    else:
        from word_pipeline import build

        auto = build(source, docx_out, pdf_out, quality / "auto-check.json", base=topic, title=plan.get("running_title", ""),  # empty: header = cover title
                     subject=plan.get("subject", ""), contract={"target_pages": contract["target_pages"], "min_body_fill": 0.75},
                     render_dir=quality / "pages")
        failures += [f"[版式] {f}" for f in auto["failures"]]

    from qa_ledger import check_auto, check_human

    auto_status = check_auto(topic, source, docx_out, pdf_out)
    human_status = check_human(topic)
    if auto_status["status"] == "stale":
        failures.append("[质量记录] 自动检查已过期：" + "；".join(auto_status["stale_reasons"]))
    if human_status["status"] != "pass":
        failures.append(f"[质量记录] 人工视觉/语义审查状态：{human_status['status']}"
                        + (("；" + "；".join(human_status.get("stale_reasons", []))) if human_status.get("stale_reasons") else ""))

    manifest = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "project_name": project,
        "source": str(source.relative_to(topic)).replace("\\", "/"),
        "formats": {"docx": docx_out.name if docx_out.exists() else "", "pdf": pdf_out.name if pdf_out.exists() else "",
                    "html_preview": html_out.name},
        "pdf_producer": "Microsoft Word（由交付 DOCX 导出）" if auto else "未生成",
        "page_policy": contract.get("page_policy", "正文不少于 40 页"),
        "page_counts": (auto.get("layout") or {}).get("counts"),
        "manuscript_lint": {"verdict": lint_report["verdict"], "stats": lint_report["stats"]},
        "content_gate": {k: content_gate.get(k) for k in ("passed", "prose_units", "duplicate_paragraph_groups")},
        "visual_gate": {k: visual_gate.get(k) for k in ("passed", "figures", "tables")},
        "auto_check": auto_status,
        "human_review": human_status,
        "final_verdict": "pass" if not failures else "blocked",
        "failures": failures,
        "rule": "自动检查、人工审查与内容门禁分别记录；任一记录过期或未通过即 blocked。",
    }
    write_json(topic / "workspace" / "document_export" / "export-manifest.json", manifest)
    print(json.dumps({"verdict": manifest["final_verdict"], "page_counts": manifest["page_counts"], "failures": failures},
                     ensure_ascii=False, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())

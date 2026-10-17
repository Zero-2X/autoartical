#!/usr/bin/env python3
"""Audit the repository's long-form workflow and produce a corrective report."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from content_depth import DEFAULT_CONTRACT, content_metrics


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def audit(root: Path) -> dict:
    workflow = read(root / "run_workflow.py")
    evaluator = read(root / "workflow" / "scripts" / "evaluate_document.py")
    review = read(root / "workflow" / "scripts" / "run_document_review.py")
    export = read(root / "workflow" / "scripts" / "run_document_export.py")
    delivery = read(root / "workflow" / "scripts" / "delivery_contract.py")
    visual = read(root / "workflow" / "scripts" / "run_visual_assets.py")
    plan = read(root / "workflow" / "scripts" / "run_document_plan.py")
    writing = read(root / "workflow" / "scripts" / "run_document_writing.py")
    writing_contract = read(root / "workflow" / "scripts" / "proposal_workflow.py")
    checks = {
        "pipeline_has_research": "run_research.py" in workflow,
        "pipeline_has_visual_assets": "run_visual_assets.py" in workflow,
        "pipeline_has_export_gate": "run_document_export.py" in workflow,
        "content_contract_min_40_pages": list(DEFAULT_CONTRACT.get("target_pages", []))[:1] == [40],
        "content_min_is_24000": DEFAULT_CONTRACT.get("body_units_min") >= 24000,
        "visual_contract_is_explicit": bool(DEFAULT_CONTRACT.get("visual_contract")),
        "review_checks_visual_gate": "build_visual_gate" in review,
        "export_uses_word_and_hash_ledger": "word_pipeline" in export and "check_human" in export and "check_auto" in export,
        "per_figure_and_table_note_gate": "build_figure_table_gate" in delivery and "表注" in delivery,
        "evaluator_has_long_form_mode": "long_form_required" in evaluator and "--allow-short" in evaluator,
        "planner_carries_content_contract": "content_contract" in plan,
        "visual_script_writes_requests": "request.json" in visual,
        "writing_is_agent_orchestrated": "real LLM agents" in writing_contract and "agent-runtime.json" in writing,
    }
    sample_docs = []
    for path in sorted((root / "examples").rglob("*.md")) if (root / "examples").exists() else []:
        if any(part in {"workspace", "output"} for part in path.parts):
            continue
        metrics = content_metrics(read(path))
        sample_docs.append({"path": str(path.relative_to(root)), "prose_units": metrics["prose_units"], "short_against_default_contract": metrics["prose_units"] < DEFAULT_CONTRACT["body_units_min"]})
    findings = [
        {"severity": "fixed", "area": "数量", "finding": "旧评估器只按关键词和格式打分，短文可获得 pass；现在默认进入 long_form_required，低于 24000 有效正文单位直接 revise。"},
        {"severity": "fixed", "area": "视觉", "finding": "视觉请求与真实素材曾经分离；现在由视觉台账、素材存在性、正文引用和数量门禁共同检查。"},
        {"severity": "fixed", "area": "导出", "finding": "PDF 曾由第二个排版引擎生成并允许缩放到 55%；现在 PDF 由 Word 从交付 DOCX 导出，版式检查与人工审查记录绑定文件哈希，详见 docs/audit-2026-10.md。"},
        {"severity": "fixed", "area": "表格质量", "finding": "表格数量不再是唯一要求；含表格的正文必须提供单位、数据来源、统计口径和缺失值规则，否则进入 revise。"},
        {"severity": "known_limit", "area": "写作执行", "finding": "章节写作仍由真实 LLM agent/外部写作执行完成，CLI 负责状态、证据、章节门禁和汇编，不伪造正文。没有章节批准时不能称为完成。"},
        {"severity": "known_limit", "area": "数据真实性", "finding": "素材请求文件不等于图像；实验指标和案例结果必须来自真实数据，自动化不会填入虚构结果。"},
    ]
    failures = [key for key, value in checks.items() if not value]
    return {
        "contract": DEFAULT_CONTRACT,
        "checks": checks,
        "failed_checks": failures,
        "sample_docs": sample_docs,
        "findings": findings,
        "verdict": "pass" if not failures else "revise",
        "interpretation": "选题文本、摘要和章节种子不是完整长文；只有经过 document_plan、章节批准、content_depth、visual、render 和 export 门禁的文件才是最终交付。",
    }


def render(report: dict) -> str:
    lines = ["# 工作流质量审计", "", "## 结论", "", report["interpretation"], "", f"- 审计结论：`{report['verdict']}`", f"- 失败的结构检查：{len(report['failed_checks'])}", ""]
    lines.extend(["## 已经强制的门禁", ""])
    lines.extend(f"- {'通过' if value else '失败'}：{key}" for key, value in report["checks"].items())
    lines.extend(["", "## 当前仓库中短于完整交付合同的示例", ""])
    for item in report["sample_docs"]:
        status = "短于 24000，不能作为最终长文" if item["short_against_default_contract"] else "达到最低正文量"
        lines.append(f"- `{item['path']}`：{item['prose_units']} 有效正文单位；{status}。")
    lines.extend(["", "## 问题分析与修复状态", ""])
    for item in report["findings"]:
        lines.append(f"- **{item['severity']} / {item['area']}**：{item['finding']}")
    lines.extend(["", "## 完整交付判定", "", "必须同时满足：研究 Gate 通过、章节计划存在、每章正文和审计批准、有效正文达到 24000 最低单位、每幅图有论证作用与可追溯来源、每张表有来源表注、Word 实排正文不少于 40 页且版式检查通过、人工视觉与语义审查已登记且与当前文件哈希一致、export-manifest.json 为 pass。"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 AutoArtical 工作流的内容、视觉和交付门禁")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    report = audit(root)
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "workflow-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (docs / "workflow-audit.md").write_text(render(report), encoding="utf-8")
    print(json.dumps({"verdict": report["verdict"], "failed_checks": report["failed_checks"], "report": "docs/workflow-audit.md"}, ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the final delivery package and enforce content/visual/render gates."""
from __future__ import annotations

import argparse
import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from content_depth import DEFAULT_CONTRACT, build_content_depth_gate
from delivery_contract import build_visual_gate


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def markdown_to_html(markdown: str, title: str) -> str:
    styles = (
        "<style>"
        "@page{size:A4;margin:20mm 18mm 18mm;}"
        "body{font-family:'Noto Sans CJK SC','Microsoft YaHei',sans-serif;color:#172033;line-height:1.75;max-width:900px;margin:0 auto;}"
        "h1{font-size:28px;margin:0 0 24px;}h2{font-size:22px;margin-top:30px;border-bottom:1px solid #d6deea;padding-bottom:6px;page-break-after:avoid;}"
        "h3{font-size:18px;margin-top:22px;page-break-after:avoid;}h4{font-size:16px;margin-top:16px;page-break-after:avoid;}"
        "p{text-align:justify;orphans:3;widows:3;}table{border-collapse:collapse;width:100%;margin:16px 0;page-break-inside:avoid;}"
        "th,td{border:1px solid #cbd5e1;padding:7px 9px;vertical-align:top;}th{background:#e8f0fa;}"
        "blockquote{margin:16px 0;padding:10px 14px;border-left:4px solid #2563eb;background:#f5f8fc;}"
        "</style>"
    )
    lines = ["<!doctype html>", '<html lang="zh-CN"><head><meta charset="utf-8">', f"<title>{html.escape(title)}</title>", styles, "</head><body>"]
    in_table = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            if in_table:
                lines.append("</table>")
                in_table = False
            continue
        if line.startswith("# "):
            lines.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            lines.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
        elif line.startswith("#### "):
            lines.append(f"<h4>{html.escape(line[5:].strip())}</h4>")
        elif line.startswith("> "):
            lines.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
        elif line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(set(cell) <= set("-: ") for cell in cells):
                continue
            if not in_table:
                lines.append("<table>")
                in_table = True
                lines.append("<tr>" + "".join(f"<th>{html.escape(cell)}</th>" for cell in cells) + "</tr>")
            else:
                lines.append("<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in cells) + "</tr>")
        elif line.startswith("- "):
            lines.append(f"<p>• {html.escape(line[2:])}</p>")
        else:
            lines.append(f"<p>{html.escape(line)}</p>")
    if in_table:
        lines.append("</table>")
    lines.append("</body></html>")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="执行内容、视觉、渲染和最终交付门禁")
    parser.add_argument("topic_dir")
    parser.add_argument("--allow-html-only", action="store_true", help="只允许 HTML 交付；不会宣称 PDF 页数已核验")
    args = parser.parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    plan_path = topic_dir / "workspace" / "document_plan" / "section-plan.json"
    draft_path = topic_dir / "workspace" / "document_writing" / "作品书草稿.md"
    review_path = topic_dir / "workspace" / "document_review" / "quality-gate.json"
    if not plan_path.exists() or not draft_path.exists() or not review_path.exists():
        raise SystemExit("缺少 section-plan、作品书草稿或 quality-gate，不能导出。")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    draft = draft_path.read_text(encoding="utf-8")
    review = json.loads(review_path.read_text(encoding="utf-8"))
    contract = plan.get("content_contract", DEFAULT_CONTRACT)
    content_gate = build_content_depth_gate(draft, plan.get("sections", []), contract)
    visual_gate = build_visual_gate(topic_dir, plan, draft)
    renderer = shutil.which("pandoc") or shutil.which("typst") or shutil.which("libreoffice") or shutil.which("soffice")
    render_report_path = topic_dir / "workspace" / "document_export" / "render-report.json"
    render_report = {}
    if render_report_path.exists():
        try:
            render_report = json.loads(render_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            render_report = {}
    page_count = render_report.get("page_count")
    target_pages = contract.get("target_pages", [40, 50])
    page_in_range = isinstance(page_count, int) and len(target_pages) == 2 and target_pages[0] <= page_count <= target_pages[1]
    verified = bool(render_report.get("verified")) and page_in_range and render_report.get("visual_qa") == "pass"
    render_gate = {
        "verified": verified,
        "renderer_available": bool(renderer),
        "backend": Path(renderer).name if renderer else render_report.get("backend", "none"),
        "page_count": page_count,
        "page_range": target_pages,
        "visual_qa": render_report.get("visual_qa", "pending"),
        "report_path": str(render_report_path.relative_to(topic_dir)) if render_report_path.exists() else "",
        "note": "必须通过 PDF/DOCX 实际渲染逐页核验并写入 render-report.json；HTML 生成不等于页数核验。",
    }
    failures = []
    if review.get("verdict") != "pass":
        failures.append(f"document_review 未通过：{review.get('verdict', 'missing')}")
    failures.extend(content_gate.get("failures", []))
    failures.extend(visual_gate.get("failures", []))
    if not render_gate["verified"] and not args.allow_html_only:
        if not renderer:
            failures.append("未发现 Pandoc、Typst 或 LibreOffice 渲染器；不能宣称 40–50 页已核验")
        else:
            failures.append("缺少有效 render-report.json：必须记录 PDF/DOCX 页数在 40–50 页内且逐页视觉 QA 通过")
    out_dir = topic_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    project = plan.get("project_name", topic_dir.name) or topic_dir.name
    markdown_out = out_dir / f"作品书_{project}.md"
    html_out = out_dir / f"作品书_{project}.html"
    markdown_out.write_text(draft, encoding="utf-8")
    html_out.write_text(markdown_to_html(draft, project), encoding="utf-8")
    manifest = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "project_name": project,
        "formats": {"markdown": str(markdown_out.relative_to(topic_dir)), "html": str(html_out.relative_to(topic_dir))},
        "content_gate": content_gate,
        "visual_gate": visual_gate,
        "render_gate": render_gate,
        "review_verdict": review.get("verdict", "missing"),
        "final_verdict": "pass" if not failures else "blocked",
        "failures": failures,
        "rule": "只有内容、视觉、引用、渲染和逐页视觉 QA 都通过，才能称为完整 40–50 页交付。",
    }
    write_json(topic_dir / "workspace" / "document_export" / "export-manifest.json", manifest)
    (topic_dir / "workspace" / "document_export" / "export-notes.md").write_text(
        "# 导出与交付记录\n\n" + "\n".join(f"- {item}" for item in failures or ["全部自动门禁通过，仍需保留最终渲染证据。"]) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"verdict": manifest["final_verdict"], "failures": failures, "html": str(html_out)}, ensure_ascii=False, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())

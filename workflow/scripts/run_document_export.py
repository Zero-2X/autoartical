#!/usr/bin/env python3
"""Build the final delivery package and enforce content/visual/render gates."""
from __future__ import annotations

import argparse
import base64
import html
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from content_depth import DEFAULT_CONTRACT, build_content_depth_gate
from delivery_contract import build_visual_gate


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _image_data_uri(source: str, base_dir: Path | None = None) -> str:
    """Inline a local figure so HTML/PDF renderers cannot silently drop it."""
    raw = source.strip().strip("<>")
    path = Path(raw)
    candidates = [path]
    if base_dir and not path.is_absolute():
        candidates.insert(0, base_dir / path)
    if not path.is_absolute():
        candidates.append(Path.cwd() / path)
    resolved = next((item.resolve() for item in candidates if item.exists() and item.is_file()), None)
    if resolved is None:
        return ""
    suffix = resolved.suffix.lower()
    if suffix == ".svg":
        # PyMuPDF's HTML engine is more reliable with a raster data URI than
        # with an SVG data URI, while the source SVG remains the versioned asset.
        try:
            import fitz
            svg_doc = fitz.open(stream=resolved.read_bytes(), filetype="svg")
            payload = svg_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).tobytes("png")
            return f"data:image/png;base64,{base64.b64encode(payload).decode('ascii')}"
        except Exception:
            pass
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(suffix, "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(resolved.read_bytes()).decode('ascii')}"


def markdown_to_html(markdown: str, title: str, base_dir: Path | None = None) -> str:
    styles = (
        "<style>"
        "@page{size:A4;margin:20mm 18mm 18mm;}"
        "body{font-family:'Noto Sans CJK SC','Microsoft YaHei',sans-serif;color:#172033;line-height:1.75;max-width:900px;margin:0 auto;}"
        "h1{font-size:28px;margin:0 0 24px;}h2{font-size:22px;margin-top:30px;border-bottom:1px solid #d6deea;padding-bottom:6px;page-break-after:avoid;}"
        "h3{font-size:18px;margin-top:22px;page-break-after:avoid;}h4{font-size:16px;margin-top:16px;page-break-after:avoid;}"
        "p{text-align:justify;orphans:3;widows:3;}table{border-collapse:collapse;width:100%;margin:16px 0;page-break-inside:avoid;}"
        "th,td{border:1px solid #cbd5e1;padding:7px 9px;vertical-align:top;}th{background:#e8f0fa;}"
        "blockquote{margin:16px 0;padding:10px 14px;border-left:4px solid #2563eb;background:#f5f8fc;}"
        "figure{margin:18px auto;text-align:center;page-break-inside:avoid;}figure img{max-width:100%;max-height:260mm;height:auto;}figcaption{font-size:9pt;color:#526174;margin-top:5px;}"
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
        elif re.match(r"!\[[^\]]*\]\([^)]*\)", line):
            match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
            if match:
                alt, source = match.groups()
                uri = _image_data_uri(source, base_dir)
                if uri:
                    lines.append(f'<figure><img src="{uri}" alt="{html.escape(alt)}"><figcaption>{html.escape(alt)}</figcaption></figure>')
                else:
                    lines.append(f"<p>{html.escape(alt)}（图形资产缺失）</p>")
        elif line.startswith("- "):
            lines.append(f"<p>• {html.escape(line[2:])}</p>")
        else:
            lines.append(f"<p>{html.escape(line)}</p>")
    if in_table:
        lines.append("</table>")
    lines.append("</body></html>")
    return "\n".join(lines) + "\n"


def _markdown_units(line: str) -> int:
    return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]|[A-Za-z0-9]+(?:[-_/][A-Za-z0-9]+)*", line))


def _split_render_chunks(markdown: str, target_units: int = 1000) -> list[str]:
    """Split at paragraph/table boundaries so PyMuPDF can render stable pages."""
    chunks: list[str] = []
    current: list[str] = []
    units = 0
    in_table = False
    for line in markdown.splitlines():
        stripped = line.strip()
        is_row = stripped.startswith("|") and stripped.endswith("|")
        current.append(line)
        if is_row:
            in_table = True
        elif not stripped and in_table:
            in_table = False
        units += _markdown_units(line)
        if not in_table and not stripped and units >= target_units:
            chunks.append("\n".join(current).strip())
            current = []
            units = 0
    if current and "\n".join(current).strip():
        chunks.append("\n".join(current).strip())
    return chunks


def _split_chunk_for_render(chunk: str) -> tuple[str, str] | None:
    """Split an overfull page at Markdown block boundaries, keeping headings attached."""
    blocks = [part.strip() for part in re.split(r"\n\s*\n", chunk.strip()) if part.strip()]
    grouped: list[str] = []
    index = 0
    while index < len(blocks):
        block = blocks[index]
        if block.startswith("#") and index + 1 < len(blocks):
            grouped.append(block + "\n\n" + blocks[index + 1])
            index += 2
        else:
            grouped.append(block)
            index += 1
    if len(grouped) < 2:
        return None

    def weight(block: str) -> int:
        units = _markdown_units(block)
        images = sum(1 for line in block.splitlines() if line.startswith("!["))
        table_rows = sum(1 for line in block.splitlines() if line.strip().startswith("|"))
        return max(units, 1) + images * 360 + table_rows * 14

    weights = [weight(block) for block in grouped]
    midpoint = sum(weights) / 2
    candidates = []
    for split_at in range(1, len(grouped)):
        left = "\n\n".join(grouped[:split_at])
        right = "\n\n".join(grouped[split_at:])
        left_units = _markdown_units(left)
        right_units = _markdown_units(right)
        if left_units < 40 or right_units < 40:
            continue
        candidates.append((abs(sum(weights[:split_at]) - midpoint), left, right))
    if not candidates:
        return None
    _, left, right = min(candidates, key=lambda item: item[0])
    return left, right


def render_with_pymupdf(markdown: str, title: str, pdf_path: Path) -> dict:
    """Render an actual PDF when office/Typst binaries are unavailable."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("PyMuPDF 不可用") from exc
    chunks = _split_render_chunks(markdown)
    document = fitz.open()
    page_rect = fitz.paper_rect("a4")
    margin = 42
    css_body = "<style>body{font-family:'Microsoft YaHei','Noto Sans CJK SC',sans-serif;font-size:13pt;line-height:1.55;color:#172033;}h1{font-size:22pt;margin:0 0 16pt;}h2{font-size:18pt;margin:0 0 14pt;}h3{font-size:15pt;margin:0 0 11pt;}h4{font-size:12.5pt;margin:0 0 9pt;}p{margin:0 0 9pt;text-align:justify;}table{border-collapse:collapse;width:100%;font-size:9.5pt;}th,td{border:0.5pt solid #9aa8bb;padding:4pt;vertical-align:top;}th{background:#e8f0fa;}blockquote{border-left:3pt solid #2563eb;padding-left:8pt;}figure{margin:12pt auto;text-align:center;page-break-inside:avoid;}figure img{width:auto;height:220pt;max-width:480pt;}figcaption{font-size:8.5pt;color:#526174;}</style>"
    pending = list(chunks)
    splits = 0
    while pending:
        chunk = pending.pop(0)
        full = markdown_to_html(chunk, title, Path.cwd())
        body = full.split("<body>", 1)[1].rsplit("</body>", 1)[0]
        page = document.new_page(width=page_rect.width, height=page_rect.height)
        result = page.insert_htmlbox(fitz.Rect(margin, margin, page_rect.width - margin, page_rect.height - margin), css_body + body)
        if isinstance(result, tuple) and result[1] < 0.55:
            parts = _split_chunk_for_render(chunk)
            if parts is None:
                raise RuntimeError(f"渲染页无法在保持可读性的前提下排入页面：scale={result[1]:.2f}")
            document.delete_page(-1)
            pending[0:0] = [parts[0], parts[1]]
            splits += 1
            if splits > 32:
                raise RuntimeError("页面自适应分块超过上限；需重新规划图文分页。")
    page_total = len(document)
    for page_number, page in enumerate(document, start=1):
        footer_y = page_rect.height - 30
        page.draw_line((margin, footer_y), (page_rect.width - margin, footer_y), color=(0.82, 0.86, 0.91), width=0.55)
        page.insert_text((page_rect.width / 2 - 18, page_rect.height - 14), f"{page_number} / {page_total}",
                         fontname="helv", fontsize=8.5, color=(0.28, 0.35, 0.45))
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    # Dynamic split attempts leave superseded image objects in the document.
    # Collect them and deflate streams so generated figures do not inflate the PDF.
    document.save(pdf_path, garbage=4, deflate=True)
    document.close()
    check = fitz.open(pdf_path)
    page_text_lengths = [len(page.get_text().strip()) for page in check]
    image_count = sum(len(page.get_images(full=True)) for page in check)
    check.close()
    if not page_text_lengths or any(length < 20 for length in page_text_lengths):
        raise RuntimeError("PDF 存在空白或文本不足页面")
    if image_count == 0:
        raise RuntimeError("PDF 未嵌入任何图形资产")
    return {"page_count": len(page_text_lengths), "page_text_lengths": page_text_lengths, "image_count": image_count, "backend": "pymupdf"}


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
    draft_hash = hashlib.sha256(draft.encode("utf-8")).hexdigest()
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
    out_dir = topic_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    project = plan.get("project_name", topic_dir.name) or topic_dir.name
    file_slug = re.sub(r"[^\w.-]+", "_", project, flags=re.UNICODE).strip("._") or topic_dir.name
    pdf_out = out_dir / f"作品书_{file_slug}.pdf"
    can_render = content_gate.get("passed", False) and visual_gate.get("passed", False) and review.get("verdict") == "pass"
    existing_pdf_hash = hashlib.sha256(pdf_out.read_bytes()).hexdigest() if pdf_out.exists() else ""
    render_is_current = (render_report.get("pdf_sha256") == existing_pdf_hash and bool(existing_pdf_hash) and
                         render_report.get("draft_sha256") == draft_hash)
    if not renderer and can_render and not render_is_current:
        try:
            rendered = render_with_pymupdf(draft, project, pdf_out)
            pdf_hash = hashlib.sha256(pdf_out.read_bytes()).hexdigest()
            previous_qa = render_report if render_report.get("pdf_sha256") == pdf_hash and render_report.get("draft_sha256") == draft_hash else {}
            render_report = {
                "verified": previous_qa.get("visual_qa") == "pass",
                "visual_qa": previous_qa.get("visual_qa", "pending"),
                "page_count": rendered["page_count"],
                "backend": rendered["backend"],
                "page_text_lengths": rendered["page_text_lengths"],
                "image_count": rendered["image_count"],
                "pdf_sha256": pdf_hash,
                "draft_sha256": draft_hash,
                "raster_qa_samples": previous_qa.get("raster_qa_samples", []),
                "visual_qa_note": previous_qa.get("visual_qa_note", ""),
                "qa_rule": "PDF 必须由实际渲染生成，且嵌入图形资产；随后使用 pdftoppm 栅格化并抽检页面。",
            }
            write_json(render_report_path, render_report)
            renderer = "pymupdf"
        except Exception as exc:  # pragma: no cover - environment dependent
            render_report = {"verified": False, "visual_qa": "failed", "backend": "pymupdf", "error": str(exc)}
    elif not renderer and render_is_current:
        renderer = render_report.get("backend", "pymupdf")
    page_count = render_report.get("page_count")
    target_pages = contract.get("target_pages", [40, 50])
    page_in_range = isinstance(page_count, int) and len(target_pages) == 2 and target_pages[0] <= page_count <= target_pages[1]
    page_occupancy = render_report.get("page_occupancy_ratios", [])
    density_pass = (render_report.get("density_check") == "pass" and len(page_occupancy) == page_count and
                    all(isinstance(value, (int, float)) and value >= 0.55 for value in page_occupancy))
    current_pdf_hash = hashlib.sha256(pdf_out.read_bytes()).hexdigest() if pdf_out.exists() else ""
    verified = (can_render and bool(render_report.get("verified")) and page_in_range and
                render_report.get("visual_qa") == "pass" and
                density_pass and
                render_report.get("pdf_sha256") == current_pdf_hash and
                render_report.get("draft_sha256") == draft_hash and
                bool(render_report.get("raster_qa_samples")))
    render_gate = {
        "verified": verified,
        "renderer_available": bool(renderer),
        "backend": Path(renderer).name if renderer else render_report.get("backend", "none"),
        "page_count": page_count,
        "page_range": target_pages,
        "embedded_image_count": render_report.get("image_count", 0),
        "raster_qa_samples": render_report.get("raster_qa_samples", []),
        "density_check": render_report.get("density_check", "pending"),
        "minimum_page_occupancy": min(page_occupancy) if page_occupancy else None,
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
    markdown_out = out_dir / f"作品书_{file_slug}.md"
    html_out = out_dir / f"作品书_{file_slug}.html"
    markdown_out.write_text(draft, encoding="utf-8")
    html_out.write_text(markdown_to_html(draft, project, Path.cwd()), encoding="utf-8")
    manifest = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "project_name": project,
        "formats": {
            "markdown": str(markdown_out.relative_to(topic_dir)),
            "html": str(html_out.relative_to(topic_dir)),
            **({"pdf": str(pdf_out.relative_to(topic_dir))} if verified else {}),
        },
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

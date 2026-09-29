#!/usr/bin/env python3
"""Editable Word export for the doctoral-style manuscript delivery copy."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


def _set_east_asia_font(font, name: str) -> None:
    font.name = name
    element = font._element
    rpr = element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        from docx.oxml import OxmlElement

        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", name)
    rfonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii", "Times New Roman")
    rfonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi", "Times New Roman")


def _set_run_font(run, name: str = "宋体", size_pt: float = 12, bold: bool | None = None) -> None:
    _set_east_asia_font(run.font, name)
    from docx.shared import Pt

    run.font.size = Pt(size_pt)
    if bold is not None:
        run.bold = bold


def _configure_style(style, name: str, size_pt: float, *, bold: bool = False) -> None:
    from docx.shared import Pt
    from docx.enum.style import WD_STYLE_TYPE

    if style.type == WD_STYLE_TYPE.PARAGRAPH:
        style.font.bold = bold
    _set_east_asia_font(style.font, name)
    style.font.size = Pt(size_pt)
    style.font.bold = bold
    style.font.italic = False
    style.font.underline = False
    try:
        from docx.shared import RGBColor

        style.font.color.rgb = RGBColor(23, 32, 51)
    except Exception:
        pass


def _clear_style_borders(style) -> None:
    """Remove Word's default decorative title/heading borders and colors."""
    p_pr = style._element.get_or_add_pPr()
    for child in list(p_pr):
        if child.tag.endswith("}pBdr"):
            p_pr.remove(child)


def _set_cell_shading(cell, fill: str) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def _set_cell_margins(cell, top: int = 80, start: int = 100, bottom: int = 80, end: int = 100) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def _add_field(paragraph, instruction: str) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {instruction} "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    _set_run_font(run, "Times New Roman", 10.5)


def _resolve_asset(source: str, base_dirs: Iterable[Path]) -> Path | None:
    raw = source.strip().strip("<>")
    path = Path(raw)
    candidates = [path] if path.is_absolute() else []
    candidates.extend(directory / path for directory in base_dirs)
    candidates.append(Path.cwd() / path)
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved.is_file():
            return resolved
    return None


def _plain_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    return text.replace("**", "").replace("__", "").replace("`", "")


def _add_inline_runs(paragraph, text: str, *, size_pt: float = 12, default_font: str = "宋体") -> None:
    """Keep simple bold labels such as ``关键词`` while removing Markdown syntax."""
    pattern = re.compile(r"(\*\*|__)(.+?)\1")
    cursor = 0
    for match in pattern.finditer(text):
        if match.start() > cursor:
            run = paragraph.add_run(_plain_inline(text[cursor : match.start()]))
            _set_run_font(run, default_font, size_pt)
        run = paragraph.add_run(_plain_inline(match.group(2)))
        _set_run_font(run, default_font, size_pt, bold=True)
        cursor = match.end()
    if cursor < len(text):
        run = paragraph.add_run(_plain_inline(text[cursor:]))
        _set_run_font(run, default_font, size_pt)


def _set_paragraph_body(paragraph, *, indent: bool = True, space_after: float = 0) -> None:
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING

    fmt = paragraph.paragraph_format
    fmt.line_spacing = Pt(20)
    fmt.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    fmt.space_after = Pt(space_after)
    fmt.space_before = Pt(0)
    fmt.first_line_indent = Pt(24) if indent else Pt(0)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.widow_control = True


def _parse_table(block: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(set(cell) <= set("-: ") for cell in cells):
            continue
        rows.append(cells)
    return rows


def _add_table(document, block: str) -> None:
    from docx.shared import Pt
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

    rows = _parse_table(block)
    if not rows:
        return
    columns = max(len(row) for row in rows)
    table = document.add_table(rows=len(rows), cols=columns)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    for row_index, row in enumerate(rows):
        for col_index in range(columns):
            cell = table.cell(row_index, col_index)
            _set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.text = ""
            paragraph = cell.paragraphs[0]
            _set_paragraph_body(paragraph, indent=False, space_after=0)
            text = row[col_index] if col_index < len(row) else ""
            run = paragraph.add_run(_plain_inline(text))
            _set_run_font(run, "宋体", 10.5, bold=row_index == 0)
            if row_index == 0:
                _set_cell_shading(cell, "D9E5F2")
    # Keep the table immediately adjacent to the following prose; the table's
    # cell padding supplies the visual separation required for print.


def _add_image(document, block: str, base_dirs: Iterable[Path]) -> bool:
    from io import BytesIO
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", block.strip())
    if not match:
        return False
    alt, source = match.groups()
    path = _resolve_asset(source, base_dirs)
    if path is None:
        paragraph = document.add_paragraph()
        _set_paragraph_body(paragraph, indent=False)
        run = paragraph.add_run(f"{alt}（图形资产缺失：{source}）")
        _set_run_font(run, "宋体", 10.5)
        return True
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(2)
    run = paragraph.add_run()
    # ImageGen assets are retained as PNG in the evidence workspace.  Word
    # copies those pixels into the DOCX; converting the editable copy to a
    # high-quality JPEG keeps the document portable without changing the
    # source asset or its ImageGen hash.  1,400 px is sufficient for the
    # 11.5 cm printed figure width at normal office viewing distance.
    try:
        from PIL import Image

        with Image.open(path) as source_image:
            image = source_image.convert("RGB")
            if image.width > 1400:
                height = round(image.height * 1400 / image.width)
                image = image.resize((1400, height), Image.Resampling.LANCZOS)
            stream = BytesIO()
            image.save(stream, format="JPEG", quality=92, optimize=True, progressive=True)
            stream.seek(0)
            run.add_picture(stream, width=Cm(11.5))
    except Exception:
        run.add_picture(str(path), width=Cm(11.5))
    _set_run_font(run, "宋体", 10.5)
    caption = document.add_paragraph()
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_before = Pt(0)
    caption.paragraph_format.space_after = Pt(2)
    caption_run = caption.add_run(_plain_inline(alt))
    _set_run_font(caption_run, "宋体", 10.5)
    return True


def export_docx(markdown: str, output_path: Path, *, title: str = "", base_dirs: Iterable[Path] = ()) -> dict:
    """Create a fully editable DOCX and return its basic export metadata."""
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt

    document = Document()
    section = document.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(3.0)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.6)
    section.right_margin = Cm(2.6)
    section.header_distance = Cm(1.5)
    section.footer_distance = Cm(1.3)

    styles = document.styles
    _configure_style(styles["Normal"], "宋体", 12)
    _configure_style(styles["Title"], "黑体", 18, bold=True)
    for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12), ("Heading 4", 12)):
        _configure_style(styles[name], "黑体", size, bold=True)
        _clear_style_borders(styles[name])
        styles[name].paragraph_format.keep_with_next = True
        styles[name].paragraph_format.space_before = Pt(4 if name != "Heading 1" else 8)
        styles[name].paragraph_format.space_after = Pt(3)
    if "Caption" in styles:
        _configure_style(styles["Caption"], "宋体", 10.5)
    _clear_style_borders(styles["Title"])

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header.add_run(title[:48])
    _set_run_font(header_run, "宋体", 10.5)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    prefix = footer.add_run("— ")
    _set_run_font(prefix, "Times New Roman", 10.5)
    _add_field(footer, "PAGE")
    separator = footer.add_run(" / ")
    _set_run_font(separator, "Times New Roman", 10.5)
    _add_field(footer, "NUMPAGES")
    suffix = footer.add_run(" —")
    _set_run_font(suffix, "Times New Roman", 10.5)

    blocks = [part.strip() for part in re.split(r"\n\s*\n", markdown.strip()) if part.strip()]
    seen_title = False
    for block_index, block in enumerate(blocks):
        if _add_image(document, block, base_dirs):
            continue
        if all(line.strip().startswith("|") for line in block.splitlines() if line.strip()):
            _add_table(document, block)
            continue
        lines = block.splitlines()
        if len(lines) == 1:
            line = lines[0].strip()
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                level = len(heading.group(1))
                text = _plain_inline(heading.group(2).strip())
                if level == 1:
                    paragraph = document.add_paragraph(style="Title")
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    paragraph.paragraph_format.space_after = Pt(10)
                    run = paragraph.add_run(text)
                    _set_run_font(run, "黑体", 18, bold=True)
                    seen_title = True
                else:
                    style_name = f"Heading {min(level, 4)}"
                    paragraph = document.add_paragraph(style=style_name)
                    next_block = blocks[block_index + 1] if block_index + 1 < len(blocks) else ""
                    next_is_heading = bool(re.match(r"^#{1,6}\s+", next_block.strip()))
                    # Keep a heading with its first body block, but do not let
                    # a run of empty headings travel as one giant keep-together
                    # chain onto a nearly blank page.
                    paragraph.paragraph_format.keep_with_next = not next_is_heading
                    run = paragraph.add_run(text)
                    _set_run_font(run, "黑体", {2: 16, 3: 14, 4: 12}.get(level, 12), bold=True)
                continue
            if line.startswith("> "):
                paragraph = document.add_paragraph()
                _set_paragraph_body(paragraph, indent=False, space_after=2)
                paragraph.paragraph_format.left_indent = Cm(0.5)
                run = paragraph.add_run(_plain_inline(line[2:]))
                _set_run_font(run, "宋体", 10.5)
                continue
            if line.startswith(("- ", "* ", "+ ")):
                paragraph = document.add_paragraph(style="List Bullet")
                _set_paragraph_body(paragraph, indent=False, space_after=2)
                run = paragraph.add_run(_plain_inline(line[2:]))
                _set_run_font(run, "宋体", 10.5)
                continue

        if all(line.strip().startswith("> ") for line in lines if line.strip()):
            for line in lines:
                paragraph = document.add_paragraph()
                _set_paragraph_body(paragraph, indent=False, space_after=1)
                paragraph.paragraph_format.left_indent = Cm(0.5)
                run = paragraph.add_run(_plain_inline(line.strip()[2:]))
                _set_run_font(run, "宋体", 10.5)
            continue

        if all(line.strip().startswith(("- ", "* ", "+ ")) for line in lines if line.strip()):
            for line in lines:
                paragraph = document.add_paragraph(style="List Bullet")
                _set_paragraph_body(paragraph, indent=False, space_after=2)
                run = paragraph.add_run(_plain_inline(line.strip()[2:]))
                _set_run_font(run, "宋体", 10.5)
            continue

        paragraph = document.add_paragraph()
        _set_paragraph_body(paragraph)
        _add_inline_runs(paragraph, "".join(line.strip() for line in lines))

    document.core_properties.title = title or "博士论文式竞赛申报书"
    document.core_properties.subject = "开放词汇遥感目标检测与可靠语义校准"
    document.core_properties.comments = "Generated by autoartical doctoral-thesis document workflow"
    settings = document.settings.element
    update_fields = settings.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}updateFields")
    if update_fields is None:
        from docx.oxml import OxmlElement

        update_fields = OxmlElement("w:updateFields")
        settings.append(update_fields)
    update_fields.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val", "true")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path)
    return {"path": str(output_path), "format": "docx", "editable": True}

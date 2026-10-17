#!/usr/bin/env python3
"""Word-as-source delivery: DOCX -> (Word updates fields) -> PDF -> layout checks.

The PDF is exported by Microsoft Word from the delivered DOCX, never laid out
by a second engine.  Afterwards this module measures the *actual* files:

* page ranges of front matter, body, references and appendices;
* headings stranded at the bottom of a page, figures separated from captions,
  tables split across pages;
* fonts actually embedded in the PDF and the dominant body font size
  (catches scaled-down pages and fallback fonts);
* text-area fill measured inside the type area only (header/footer bands are
  excluded, so they cannot inflate a bounding box);
* objects overflowing the type area.

Every result is written to ``auto-check.json`` together with SHA-256 hashes of
the delivered files and all inputs that affect them; ``qa_ledger.py`` treats
any hash change as invalidating the check.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

CM = 72 / 2.54
PAGE_W, PAGE_H = 21.0 * CM, 29.7 * CM
MARGIN = {"top": 3.0 * CM, "bottom": 2.5 * CM, "left": 2.6 * CM, "right": 2.6 * CM}
LINE_GAP_PT = 30  # 1.5 × 20pt line pitch: glyph boxes leave inter-line gaps that are not blank space
ALLOWED_FONT_TOKENS = ("SimSun", "SimHei", "TimesNewRoman", "Times New Roman", "CambriaMath", "Symbol", "宋体", "黑体")
EXPORTER_FILES = ("docx_export.py", "word_pipeline.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def referenced_assets(markdown: str, base: Path) -> dict[str, str]:
    assets = {}
    for source in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", markdown):
        path = (base / source).resolve() if not Path(source).is_absolute() else Path(source)
        assets[source] = sha256_file(path) if path.is_file() else "MISSING"
    return assets


def input_fingerprint(markdown: str, base: Path) -> dict:
    scripts = Path(__file__).resolve().parent
    return {
        "source_markdown_sha256": sha256_text(markdown),
        "assets": referenced_assets(markdown, base),
        "exporter_code": {name: sha256_file(scripts / name) for name in EXPORTER_FILES},
    }


# ---------------------------------------------------------------- Word (COM)

def word_update_and_export(docx: Path, pdf: Path) -> dict:
    """Update TOC/fields in Word, save the DOCX, export PDF, return layout facts."""
    if sys.platform != "win32":
        raise RuntimeError("需要 Windows 上的 Microsoft Word；不能用其他排版引擎冒充 Word 版式。")
    import pythoncom
    import win32com.client

    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    facts: dict = {"word_version": str(word.Version)}
    try:
        doc = word.Documents.Open(str(docx.resolve()), ReadOnly=False, AddToRecentFiles=False)
        doc.Fields.Update()
        for toc in doc.TablesOfContents:
            toc.Update()
            # Word builds TOC entries with its own TOC styles (theme fonts);
            # set them to the thesis fonts so no fallback font enters the PDF.
            toc.Range.Font.Name = "Times New Roman"
            toc.Range.Font.NameFarEast = "宋体"
        doc.Repaginate()
        doc.Save()
        WD_PAGE = 3  # wdActiveEndPageNumber
        headings, figures, captions = [], [], []
        paragraphs = doc.Paragraphs
        count = paragraphs.Count
        previous_kind = None
        for i in range(1, count + 1):
            p = paragraphs(i)
            style = str(p.Style.NameLocal) if p.Style is not None else ""
            text = p.Range.Text.strip()
            if style.startswith(("Heading", "标题")) and text and not text.startswith("目"):
                start_page = p.Range.Characters.First.Information(WD_PAGE)
                nxt = paragraphs(i + 1) if i < count else None
                next_page = nxt.Range.Characters.First.Information(WD_PAGE) if nxt is not None else start_page
                headings.append({"text": text[:60], "level": style[-1:], "page": start_page,
                                 "next_block_page": next_page})
            if p.Range.InlineShapes.Count > 0:
                figures.append({"page": p.Range.Information(WD_PAGE), "index": i})
                previous_kind = "figure"
                continue
            if previous_kind == "figure" and re.match(r"^图\s*\d+-\d+", text):
                captions.append({"text": text[:40], "page": p.Range.Information(WD_PAGE),
                                 "figure_page": figures[-1]["page"]})
            previous_kind = None
        tables = []
        for t in doc.Tables:
            first = t.Rows(1).Range.Information(WD_PAGE)
            last = t.Rows(t.Rows.Count).Range.Information(WD_PAGE)
            after = t.Range.Next(4, 1)  # wdParagraph: the paragraph right after the table
            note_page = None
            if after is not None and after.Text.strip().startswith("注："):
                note_page = after.Characters.First.Information(WD_PAGE)
            tables.append({"rows": t.Rows.Count, "first_page": first, "last_page": last, "note_page": note_page})
        facts.update({
            "pages": doc.Range().Information(4),  # wdNumberOfPagesInDocument
            "headings": headings,
            "figure_captions": captions,
            "tables": tables,
            "inline_shapes": doc.InlineShapes.Count,
        })
        doc.ExportAsFixedFormat(str(pdf.resolve()), 17, False, 0, 0, 0, 0, 0, True, True, 1, True, True, False)
    finally:
        if doc is not None:
            doc.Close(False)
        word.Quit()
    return facts


# ---------------------------------------------------------------- PDF checks

def analyse_pdf(pdf: Path, render_dir: Path | None = None, dpi: int = 110) -> dict:
    import fitz

    content = fitz.Rect(MARGIN["left"], MARGIN["top"], PAGE_W - MARGIN["right"], PAGE_H - MARGIN["bottom"])
    pages = []
    fonts: dict[str, int] = {}
    sizes: list[float] = []
    with fitz.open(pdf) as document:
        for number, page in enumerate(document, start=1):
            for font in page.get_fonts(full=True):
                name = font[3].split("+")[-1]
                fonts[name] = fonts.get(name, 0) + 1
            blocks = []
            overflow = []
            text = page.get_text("dict")
            for block in text["blocks"]:
                rect = fitz.Rect(block["bbox"])
                if rect.y1 <= content.y0 - 2 or rect.y0 >= content.y1 + 2:
                    continue  # header/footer band: not counted as content
                if block.get("type") == 1 and (rect.x0 < content.x0 - 3 or rect.x1 > content.x1 + 3):
                    overflow.append([round(v, 1) for v in rect])
                blocks.append(rect & content)
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span["text"].strip():
                            sizes.extend([round(span["size"], 1)] * len(span["text"].strip()))
            # Text overflow is judged on visible glyphs only: a trailing space
            # at a justified line end has a box but no ink.
            for block in page.get_text("rawdict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        for char in span.get("chars", []):
                            if char["c"].strip() and (char["bbox"][2] > content.x1 + 1.5 or char["bbox"][0] < content.x0 - 1.5):
                                overflow.append([round(v, 1) for v in char["bbox"]])
            covered = 0.0
            intervals = sorted((b.y0, b.y1) for b in blocks if not b.is_empty)
            cur = None
            for y0, y1 in intervals:
                if cur is None or y0 > cur[1] + LINE_GAP_PT:
                    if cur:
                        covered += cur[1] - cur[0]
                    cur = [y0, y1]
                else:
                    cur[1] = max(cur[1], y1)
            if cur:
                covered += cur[1] - cur[0]
            raw = page.get_text().strip()
            pages.append({
                "page": number,
                "fill": round(covered / content.height, 3),
                "chars": len(raw),
                "images": len(page.get_images()),
                "overflow": overflow,
                "head": raw[:40].replace("\n", " "),
            })
            if render_dir is not None:
                render_dir.mkdir(parents=True, exist_ok=True)
                target = render_dir / f"page-{number:03}.png"
                page.get_pixmap(dpi=dpi).save(target)
                pages[-1]["render"] = target.name
                pages[-1]["render_sha256"] = sha256_file(target)
    body_size = statistics.mode(sizes) if sizes else 0
    return {"pages": pages, "fonts": fonts, "dominant_font_size_pt": body_size}


def classify_pages(pdf_pages: list[dict], headings: list[dict]) -> dict:
    """Map pages to front/body/references/appendix from first-level headings."""
    total = len(pdf_pages)
    first_level = [h for h in headings if h["level"] == "1"]
    body_start = next((h["page"] for h in first_level if re.match(r"^(第\s*1\s*章|一、)", h["text"])), None)
    refs = next((h["page"] for h in first_level if h["text"].startswith("参考文献")), None)
    appendix = next((h["page"] for h in first_level if h["text"].startswith("附录")), None)
    if body_start is None:
        return {"error": "未找到“第1章”标题，无法划分正文页"}
    body_end = (refs or appendix or total + 1) - 1
    ranges = {
        "front": [1, body_start - 1],
        "body": [body_start, body_end],
        "references": [refs, (appendix or total + 1) - 1] if refs else None,
        "appendix": [appendix, total] if appendix else None,
    }
    counts = {k: (v[1] - v[0] + 1 if v else 0) for k, v in ranges.items()}
    chapter_last_pages = set()
    starts = sorted(h["page"] for h in first_level)
    for s in starts[1:]:
        chapter_last_pages.add(s - 1)
    chapter_last_pages.add(total)
    return {"ranges": ranges, "counts": counts, "chapter_last_pages": sorted(chapter_last_pages)}


def evaluate(facts: dict, pdf_info: dict, contract: dict) -> dict:
    failures, warnings = [], []
    layout = classify_pages(pdf_info["pages"], facts["headings"])
    if "error" in layout:
        failures.append(layout["error"])
        return {"failures": failures, "warnings": warnings, "layout": layout}
    lo, hi = (list(contract.get("target_pages", [40, None])) + [None])[:2]
    body_pages = layout["counts"]["body"]
    other = f"（前置 {layout['counts']['front']} 页、参考文献 {layout['counts']['references']} 页、附录 {layout['counts']['appendix']} 页另计）"
    if body_pages < lo:
        failures.append(f"正文页数 {body_pages} 低于下限 {lo} 页{other}；须补充实质内容，不得调版式凑页")
    elif hi is not None and body_pages > hi:
        failures.append(f"正文页数 {body_pages} 超过上限 {hi} 页{other}")
    if len(pdf_info["pages"]) != facts["pages"]:
        failures.append(f"Word 统计页数 {facts['pages']} 与导出 PDF 页数 {len(pdf_info['pages'])} 不一致")
    stranded = [h for h in facts["headings"] if h["next_block_page"] != h["page"]]
    if stranded:
        failures.append("标题孤立在页尾：" + "；".join(f"p{h['page']} {h['text']}" for h in stranded[:8]))
    split_captions = [c for c in facts["figure_captions"] if c["page"] != c["figure_page"]]
    if split_captions:
        failures.append("图与图注分页：" + "；".join(f"{c['text']}" for c in split_captions))
    split_notes = [t for t in facts["tables"] if t.get("note_page") and t["note_page"] != t["last_page"]]
    if split_notes:
        failures.append(f"{len(split_notes)} 个表格与表注分页：首页 {[t['first_page'] for t in split_notes]}")
    split_tables = [t for t in facts["tables"] if t["first_page"] != t["last_page"]]
    short_split = [t for t in split_tables if t["rows"] <= 8]
    if short_split:
        failures.append(f"{len(short_split)} 个短表（≤8 行）被拆到两页")
    if split_tables and not short_split:
        warnings.append(f"{len(split_tables)} 个长表跨页（已设置表头重复，需人工确认）")
    bad_fonts = {name: n for name, n in pdf_info["fonts"].items()
                 if not any(token.replace(" ", "").lower() in name.replace(" ", "").replace("-", "").lower()
                            for token in ALLOWED_FONT_TOKENS)}
    if bad_fonts:
        failures.append("PDF 中出现规范外或回退字体：" + "、".join(sorted(bad_fonts)))
    size = pdf_info["dominant_font_size_pt"]
    if abs(size - 12) > 0.3:
        failures.append(f"正文主字号为 {size}pt，偏离规定的 12pt（可能被缩放）")
    body_range = layout["ranges"]["body"]
    last_pages = set(layout["chapter_last_pages"])
    sparse = [p["page"] for p in pdf_info["pages"]
              if body_range[0] <= p["page"] <= body_range[1] and p["page"] not in last_pages
              and p["fill"] < contract.get("min_body_fill", 0.75)]
    if sparse:
        failures.append(f"正文非章末页版心填充率低于 {contract.get('min_body_fill', 0.75)}：{sparse}")
    tiny_tail = [p["page"] for p in pdf_info["pages"] if p["page"] in last_pages and p["fill"] < 0.12 and body_range[0] <= p["page"] <= body_range[1]]
    if tiny_tail:
        warnings.append(f"章末页内容过少（<12% 版心），应在内容层面调整：{tiny_tail}")
    overflow = [p["page"] for p in pdf_info["pages"] if p["overflow"]]
    if overflow:
        failures.append(f"对象越出版心：{overflow}")
    blank = [p["page"] for p in pdf_info["pages"] if p["chars"] < 20 and not p["images"]]
    if blank:
        failures.append(f"空白或近空白页：{blank}")
    return {"failures": failures, "warnings": warnings, "layout": layout}


def build(markdown_path: Path, docx_path: Path, pdf_path: Path, report_path: Path, *,
          base: Path, title: str, subject: str = "", contract: dict | None = None,
          render_dir: Path | None = None) -> dict:
    from docx_export import export_docx

    contract = contract or {"target_pages": [40, None], "min_body_fill": 0.75}
    markdown = markdown_path.read_text(encoding="utf-8")
    export_meta = export_docx(markdown, docx_path, title=title, subject=subject, base_dirs=(base,))
    facts = word_update_and_export(docx_path, pdf_path)
    if render_dir is not None:
        for old in render_dir.glob("page-*.png"):
            old.unlink()
    pdf_info = analyse_pdf(pdf_path, render_dir)
    result = evaluate(facts, pdf_info, contract)
    report = {
        "kind": "automatic-layout-check",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "inputs": input_fingerprint(markdown, base),
        "outputs": {"docx": docx_path.name, "docx_sha256": sha256_file(docx_path),
                    "pdf": pdf_path.name, "pdf_sha256": sha256_file(pdf_path),
                    "pdf_producer": "Microsoft Word ExportAsFixedFormat from the delivered DOCX"},
        "export": export_meta,
        "word": {k: v for k, v in facts.items() if k not in ("headings",)},
        "headings": facts["headings"],
        "pdf": pdf_info,
        "contract": contract,
        **result,
        "verdict": "pass" if not result["failures"] else "fail",
        "scope_note": "自动检查只覆盖可测量的版式事实；语义质量、图意与逐页视觉判断见 human-review.json，二者不能互相替代。",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="以 Word 为唯一正式源生成 DOCX/PDF 并做版式自动检查")
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--docx", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True, help="解析图片相对路径的根目录")
    parser.add_argument("--title", default="")
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--min-pages", type=int, default=40, help="正文最少页数；默认不设上限")
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args()
    lo, hi = args.min_pages, args.max_pages
    report = build(args.markdown, args.docx, args.pdf, args.report, base=args.base, title=args.title,
                   contract={"target_pages": [lo, hi], "min_body_fill": 0.75}, render_dir=args.render_dir)
    print(json.dumps({"verdict": report["verdict"], "failures": report["failures"],
                      "warnings": report["warnings"], "pages": report["layout"].get("counts")},
                     ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "pass" else 2


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())

#!/usr/bin/env python3
"""Record visual QA for the rendered Word delivery copy.

The renderer used by the documents skill produces one PNG per page.  This
script records all-page density checks and a set of inspected samples next to
the export manifest so a DOCX is not treated as verified merely because it
exists on disk.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops


def main() -> int:
    parser = argparse.ArgumentParser(description="登记 Word 栅格化后的逐页视觉审查")
    parser.add_argument("topic_dir", type=Path)
    parser.add_argument("--sample", action="append", required=True, help="页码:已查看的 PNG 路径，可重复")
    parser.add_argument("--page-renders", required=True, type=Path)
    parser.add_argument("--note", required=True)
    args = parser.parse_args()
    root = args.topic_dir.resolve()
    plan = json.loads((root / "workspace" / "document_plan" / "section-plan.json").read_text(encoding="utf-8"))
    project = plan.get("project_name", root.name)
    slug = re.sub(r"[^\w.-]+", "_", project, flags=re.UNICODE).strip("._") or root.name
    docx = root / "output" / f"作品书_{slug}.docx"
    formatted_markdown = root / "output" / f"作品书_{slug}.md"
    if not docx.exists():
        parser.error(f"缺少 Word 文件：{docx}")
    if len(args.note) < 30:
        parser.error("审查记录需具体说明字体、分页、图注、表格和段落密度")
    page_dir = args.page_renders.resolve()
    rendered: list[tuple[int, Path]] = []
    for path in page_dir.glob("*.png"):
        match = re.search(r"(\d+)(?=\.png$)", path.name)
        if match:
            rendered.append((int(match.group(1)), path))
    rendered.sort(key=lambda item: item[0])
    page_count = len(rendered)
    if page_count < 1:
        parser.error("未找到 Word 栅格页面")
    samples: list[dict] = []
    sample_dir = root / "workspace" / "document_export" / "docx_qa_samples"
    sample_dir.mkdir(parents=True, exist_ok=True)
    for old in sample_dir.glob("page-*.png"):
        old.unlink()
    for raw in args.sample:
        page_raw, sep, image_raw = raw.partition(":")
        if not sep or not page_raw.isdecimal() or not (1 <= int(page_raw) <= page_count):
            parser.error(f"无效样本页：{raw}")
        image = Path(image_raw).resolve()
        if not image.is_file() or image.stat().st_size < 10_000:
            parser.error(f"缺少有效栅格页面：{image}")
        page_number = int(page_raw)
        saved = sample_dir / f"page-{page_number:02}.png"
        shutil.copyfile(image, saved)
        samples.append({"page": page_number, "image": str(saved.relative_to(root)).replace("\\", "/")})
    if len({item["page"] for item in samples}) < 4 or not any(item["page"] == 1 for item in samples) or not any(item["page"] == page_count for item in samples):
        parser.error("至少检查四个不同页面，且包括首页和末页")

    occupancy = []
    for number, image_path in rendered:
        if image_path.stat().st_size < 10_000:
            parser.error(f"第 {number} 页栅格图异常：{image_path}")
        with Image.open(image_path) as source:
            page = source.convert("RGB")
            difference = ImageChops.difference(page, Image.new("RGB", page.size, "white"))
            bounds = difference.point(lambda value: 255 if value > 22 else 0).convert("L").getbbox()
            ratio = 0.0 if bounds is None else ((bounds[2] - bounds[0]) * (bounds[3] - bounds[1])) / (page.width * page.height)
        occupancy.append({"page": number, "ratio": round(ratio, 4)})
    minimum = min(item["ratio"] for item in occupancy)
    if minimum < 0.55:
        parser.error(f"Word 页面内容占用率低于 0.55：{[item['page'] for item in occupancy if item['ratio'] < 0.55]}")
    report = {
        "docx": str(docx.relative_to(root)).replace("\\", "/"),
        "docx_sha256": hashlib.sha256(docx.read_bytes()).hexdigest(),
        "source_formatted_sha256": hashlib.sha256(formatted_markdown.read_text(encoding="utf-8").encode("utf-8")).hexdigest() if formatted_markdown.exists() else "",
        "page_count": page_count,
        "raster_qa_samples": samples,
        "page_occupancy_ratios": [item["ratio"] for item in occupancy],
        "minimum_page_occupancy": round(minimum, 4),
        "density_threshold": 0.55,
        "density_check": "pass",
        "visual_qa": "pass",
        "verified": True,
        "visual_qa_note": args.note,
        "visual_qa_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "rule": "DOCX 必须由 documents skill 实际渲染为全部页面 PNG，且逐页检查字体、段落密度、图表和分页。",
    }
    report_path = root / "workspace" / "document_export" / "docx-render-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

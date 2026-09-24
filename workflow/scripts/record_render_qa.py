#!/usr/bin/env python3
"""Record visual inspection of rendered PDF pages for the current draft."""
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
    parser = argparse.ArgumentParser(description="登记 PDF 栅格化后的人工逐页/抽样视觉审查")
    parser.add_argument("topic_dir", type=Path)
    parser.add_argument("--sample", action="append", required=True, help="页码:已查看的 PNG 路径，可重复")
    parser.add_argument("--page-renders", required=True, type=Path, help="全部 PDF 页面 PNG 的目录；文件名需含页码")
    parser.add_argument("--note", required=True, help="记录字体、图注、图表断页、页密度检查结论")
    args = parser.parse_args()
    root = args.topic_dir.resolve()
    report_path = root / "workspace" / "document_export" / "render-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    plan = json.loads((root / "workspace" / "document_plan" / "section-plan.json").read_text(encoding="utf-8"))
    project = plan.get("project_name", root.name)
    file_slug = re.sub(r"[^\w.-]+", "_", project, flags=re.UNICODE).strip("._") or root.name
    pdf = root / "output" / f"作品书_{file_slug}.pdf"
    draft = (root / "workspace" / "document_writing" / "作品书草稿.md").read_text(encoding="utf-8")
    if not pdf.exists() or report.get("pdf_sha256") != hashlib.sha256(pdf.read_bytes()).hexdigest():
        parser.error("PDF 与 render-report.json 不一致，请重新导出")
    if report.get("draft_sha256") != hashlib.sha256(draft.encode("utf-8")).hexdigest():
        parser.error("正文在渲染后发生变化，请重新导出")
    if len(args.note) < 30:
        parser.error("审查记录需具体说明看到的图文质量与问题")
    page_count = int(report.get("page_count", 0))
    samples = []
    sample_dir = root / "workspace" / "document_export" / "qa_samples"
    sample_dir.mkdir(parents=True, exist_ok=True)
    for old_sample in sample_dir.glob("page-*.png"):
        old_sample.unlink()
    for raw in args.sample:
        page_raw, sep, image_raw = raw.partition(":")
        if not sep or not page_raw.isdecimal() or not (1 <= int(page_raw) <= page_count):
            parser.error(f"无效的样本页：{raw}")
        image = Path(image_raw).resolve()
        if not image.is_file() or image.stat().st_size < 10_000:
            parser.error(f"缺少有效的栅格化页面：{image}")
        page_number = int(page_raw)
        saved_sample = sample_dir / f"page-{page_number:02}.png"
        shutil.copyfile(image, saved_sample)
        samples.append({"page": page_number, "image": str(saved_sample.relative_to(root)).replace("\\", "/")})
    if len({item["page"] for item in samples}) < 4 or not any(item["page"] == 1 for item in samples) or not any(item["page"] == page_count for item in samples):
        parser.error("至少检查四个不同页面，且包括首页和末页")
    render_dir = args.page_renders.resolve()
    rendered_pages = []
    for image_path in render_dir.glob("*.png"):
        match = re.search(r"(\d+)(?=\.png$)", image_path.name)
        if match:
            rendered_pages.append((int(match.group(1)), image_path))
    rendered_pages.sort(key=lambda item: item[0])
    if [number for number, _ in rendered_pages] != list(range(1, page_count + 1)):
        parser.error(f"必须提供全部 {page_count} 页的 PNG 栅格；当前发现 {len(rendered_pages)} 页")
    occupancy = []
    for number, image_path in rendered_pages:
        if image_path.stat().st_size < 10_000:
            parser.error(f"第 {number} 页栅格图异常或为空: {image_path}")
        with Image.open(image_path) as source:
            page = source.convert("RGB")
            difference = ImageChops.difference(page, Image.new("RGB", page.size, "white"))
            bounds = difference.point(lambda value: 255 if value > 22 else 0).convert("L").getbbox()
            ratio = 0.0 if bounds is None else ((bounds[2] - bounds[0]) * (bounds[3] - bounds[1])) / (page.width * page.height)
        occupancy.append({"page": number, "ratio": round(ratio, 4)})
    minimum_occupancy = min((item["ratio"] for item in occupancy), default=0.0)
    if minimum_occupancy < 0.55:
        sparse_pages = [item["page"] for item in occupancy if item["ratio"] < 0.55]
        parser.error(f"页面内容占用率低于 0.55：{sparse_pages}")
    import fitz
    with fitz.open(pdf) as document:
        for number, page in enumerate(document, start=1):
            if f"{number} / {page_count}" not in page.get_text():
                parser.error(f"第 {number} 页缺失或未识别页码")
    report["raster_qa_samples"] = samples
    report["page_occupancy_ratios"] = [item["ratio"] for item in occupancy]
    report["density_threshold"] = 0.55
    report["density_check"] = "pass"
    report["minimum_page_occupancy"] = round(minimum_occupancy, 4)
    report["visual_qa_note"] = args.note
    report["visual_qa"] = "pass"
    report["verified"] = True
    report["visual_qa_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

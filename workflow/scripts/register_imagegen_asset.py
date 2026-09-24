#!/usr/bin/env python3
"""Register a visually reviewed PNG returned by Codex's built-in ImageGen tool."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="登记已检查的 Codex 内置 ImageGen 配图")
    parser.add_argument("topic_dir", type=Path)
    parser.add_argument("--figure-id", required=True)
    parser.add_argument("--source", required=True, type=Path, help="内置 ImageGen 返回的 generated_images PNG 路径")
    parser.add_argument("--review-note", required=True, help="记录语义、可读性、独特性和事实检查结论")
    args = parser.parse_args()
    figure_dir = args.topic_dir.resolve() / "workspace" / "document_assets" / "figures"
    request_path = figure_dir / f"{args.figure_id}.request.json"
    if not request_path.exists():
        parser.error("缺少逐图请求文件，请先运行 run_visual_assets.py")
    request = json.loads(request_path.read_text(encoding="utf-8"))
    understanding = request.get("article_understanding", {})
    if not all([len(str(understanding.get("context_excerpt", ""))) >= 60,
                len(str(understanding.get("key_message", ""))) >= 15,
                len(str(understanding.get("evidence_boundary", ""))) >= 15,
                len(understanding.get("visual_elements", [])) >= 3]):
        parser.error("请先理解正文并填写 article_understanding")
    prompt = str(request.get("prompt", ""))
    if len(prompt) < 400:
        parser.error("请先根据正文理解撰写至少 400 字符的完整逐图 Prompt")
    if len(args.review_note) < 20:
        parser.error("review-note 需写明实际视觉检查，不能只写‘通过’")
    source = args.source.resolve()
    if "generated_images" not in source.parts or source.suffix.lower() != ".png" or not source.is_file():
        parser.error("source 必须是 Codex 内置 ImageGen 的 generated_images PNG")
    data = source.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 100_000:
        parser.error("生成图片不是有效的完整 PNG")
    width, height = struct.unpack(">II", data[16:24])
    if width < 1000 or height < 500:
        parser.error("生成图片分辨率不足")
    draft_path = args.topic_dir.resolve() / "workspace" / "document_writing" / "作品书草稿.md"
    if draft_path.exists():
        draft = draft_path.read_text(encoding="utf-8")
        source_text = "\n".join(line for line in draft.splitlines() if not line.lstrip().startswith("!["))
        draft_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        if request.get("source_draft_sha256") != draft_hash:
            parser.error("正文在该 Prompt 创建后已变化，请重新审读正文、理解图意并生成 Prompt")
    destination = figure_dir / f"{args.figure_id}.png"
    shutil.copyfile(source, destination)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    request["generation"] = {
        "tool": "image_gen.imagegen",
        "source_path": f"generated_images/{source.name}",
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "asset_sha256": hashlib.sha256(data).hexdigest(),
        "generated_at": now,
        "dimensions": [width, height],
    }
    request["visual_review"] = {
        "status": "pass",
        "semantic_fidelity": True,
        "legibility": True,
        "uniqueness": True,
        "no_fabrication": True,
        "note": args.review_note,
        "reviewed_at": now,
    }
    request["status"] = "reviewed"
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figure_id": args.figure_id, "asset": str(destination), "sha256": request["generation"]["asset_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

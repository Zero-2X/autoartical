"""Prepare one article-grounded figure request (same contract as run_visual_assets)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from delivery_contract import iter_visual_specs
from visual_prompting import request_brief


def main() -> int:
    parser = argparse.ArgumentParser(description="从正文和计划生成单张图的理解请求")
    parser.add_argument("project", type=Path)
    parser.add_argument("--figure-id", required=True)
    args = parser.parse_args()
    root = args.project.resolve()
    plan = json.loads((root / "workspace" / "document_plan" / "section-plan.json").read_text(encoding="utf-8"))
    draft_path = root / "workspace" / "document_writing" / "作品书草稿.md"
    if not draft_path.exists():
        parser.error("先完成章节正文，再从正文理解生成 Prompt")
    draft = draft_path.read_text(encoding="utf-8")
    spec = next((item for item in iter_visual_specs(plan) if item.get("visual_id") == args.figure_id), None)
    if spec is None:
        parser.error("图号不在 section-plan.json 中")
    request = request_brief(spec, draft, str(plan.get("project_name", root.name)))
    if len(request["article_understanding"]["context_excerpt"]) < 60:
        parser.error("正文上下文不足，不能先生成图片")
    out = root / "workspace" / "document_assets" / "figures" / f"{args.figure_id}.request.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Materialize figure briefs from the manuscript and the document plan."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from delivery_contract import build_visual_gate, iter_visual_specs
from visual_prompting import request_brief


def main() -> int:
    parser = argparse.ArgumentParser(description="从章节计划生成图表、流程图、图标和界面素材请求清单")
    parser.add_argument("topic_dir")
    args = parser.parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    plan_path = topic_dir / "workspace" / "document_plan" / "section-plan.json"
    if not plan_path.exists():
        raise SystemExit("缺少 section-plan.json，请先运行 run_document_plan.py。")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    draft_path = topic_dir / "workspace" / "document_writing" / "作品书草稿.md"
    draft = draft_path.read_text(encoding="utf-8") if draft_path.exists() else ""
    figure_dir = topic_dir / "workspace" / "document_assets" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    specs = iter_visual_specs(plan)
    created = 0
    for spec in specs:
        if str(spec.get("visual_type", "")).lower() == "table":
            continue
        visual_id = str(spec.get("visual_id", "")).strip()
        if not visual_id:
            continue
        request_path = figure_dir / f"{visual_id}.request.json"
        if request_path.exists():
            existing = json.loads(request_path.read_text(encoding="utf-8"))
            brief = request_brief(spec, draft, str(plan.get("project_name", topic_dir.name)))
            if existing.get("status") == "reviewed" and existing.get("generation", {}).get("tool") == "image_gen.imagegen":
                if existing.get("source_draft_sha256") == brief["source_draft_sha256"]:
                    continue
                existing["status"] = "stale_manuscript"
                existing["stale_reason"] = "正文章节在生图审查后发生了变化，需重读全文、重写 Prompt 并重新检查图片。"
                existing["source_draft_sha256"] = brief["source_draft_sha256"]
                request_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                created += 1
                continue
            if existing.get("source_draft_sha256") != brief["source_draft_sha256"]:
                existing["article_understanding"] = brief["article_understanding"]
                existing["source_draft_sha256"] = brief["source_draft_sha256"]
                existing["status"] = "stale_manuscript"
                existing["stale_reason"] = "正文在 Prompt 撰写或生成后发生变化，请复核文章理解并重写 Prompt。"
                existing.pop("generation", None)
                existing.pop("visual_review", None)
            request_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            created += 1
            continue
        payload = request_brief(spec, draft, str(plan.get("project_name", topic_dir.name)))
        if not payload["article_understanding"]["context_excerpt"]:
            payload["status"] = "awaiting_manuscript"
        request_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created += 1
    gate = build_visual_gate(topic_dir, plan, draft)
    manifest = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "required_specs": len([item for item in specs if item.get("required", True)]),
        "request_files_created": created,
        "generation_route": "Codex built-in image_gen for figures; evidence-backed markdown tables for tables",
        "gate_before_generation": gate,
        "rule": "必须先理解正文并写完整逐图 Prompt，再调用内置 ImageGen；请求和旧 SVG 均不能替代带生成记录及视觉审查的 PNG。",
    }
    out = topic_dir / "workspace" / "document_assets" / "visual-manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"requests_created": created, "required_specs": manifest["required_specs"], "manifest": str(out)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

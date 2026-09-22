#!/usr/bin/env python3
"""Materialize auditable visual requests from the document plan."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from delivery_contract import build_visual_gate, iter_visual_specs


def main() -> int:
    parser = argparse.ArgumentParser(description="从章节计划生成图表、流程图、图标和界面素材请求清单")
    parser.add_argument("topic_dir")
    args = parser.parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    plan_path = topic_dir / "workspace" / "document_plan" / "section-plan.json"
    if not plan_path.exists():
        raise SystemExit("缺少 section-plan.json，请先运行 run_document_plan.py。")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
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
            continue
        purpose = spec.get("purpose", "支撑正文论证")
        content = f"标题：{spec.get('title', visual_id)}；放置小节：{spec.get('suggested_subsection', '')}；正文目的：{purpose}。"
        payload = {
            "figure_id": visual_id,
            "visual_type": spec.get("visual_type", "figure"),
            "title": spec.get("title", ""),
            "purpose": purpose,
            "content": content,
            "aspect": "16:9",
            "route": "Codex built-in image_gen",
            "prompt": (
                f"为研究申报书生成信息图。{content} 只使用已有术语和来源，不创造实验数据、数值、机构标志或虚构引用；"
                "图中文字保持简洁，适合正式中文文档，输出清晰的流程、结构或机制解释。"
            ),
            "source_refs": spec.get("evidence_ids", []),
            "asset_candidates": spec.get("asset_candidates", []),
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "status": "awaiting_generation",
        }
        request_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created += 1
    gate = build_visual_gate(topic_dir, plan, "")
    manifest = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "required_specs": len([item for item in specs if item.get("required", True)]),
        "request_files_created": created,
        "generation_route": "Codex built-in image_gen for figures; evidence-backed markdown tables for tables",
        "gate_before_writing": gate,
        "rule": "请求文件不是视觉资产；最终导出前必须有真实生成文件或明确可审计的表格来源。",
    }
    out = topic_dir / "workspace" / "document_assets" / "visual-manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"requests_created": created, "required_specs": manifest["required_specs"], "manifest": str(out)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

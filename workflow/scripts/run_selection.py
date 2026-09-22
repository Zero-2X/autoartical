#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IDEA_REGISTRY_PATH = REPO_ROOT / "sample" / "databases" / "ideas" / "idea-registry.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sync_selected_idea(topic_dir: Path, idea: dict, selection_reason: str) -> str:
    if not IDEA_REGISTRY_PATH.exists():
        write_json(IDEA_REGISTRY_PATH, {"ideas": []})
    registry = read_json(IDEA_REGISTRY_PATH)
    signature_seed = "|".join([idea.get("project_name", ""), idea.get("problem", ""), ",".join(idea.get("theme_keywords", []))])
    registry_entry_id = "idea_" + hashlib.sha1(signature_seed.encode("utf-8")).hexdigest()[:10]
    for item in registry.get("ideas", []):
        if item.get("registry_entry_id") == registry_entry_id:
            return registry_entry_id

    step1_path = topic_dir / "workspace" / "requirements" / "competition-spec.json"
    competition_name = ""
    if step1_path.exists():
        competition_name = read_json(step1_path).get("competition_name", "")

    registry["ideas"].append(
        {
            "registry_entry_id": registry_entry_id,
            "project_name": idea.get("project_name", ""),
            "source_topic": topic_dir.name,
            "competition_name": competition_name,
            "idea_id": idea.get("idea_id", ""),
            "problem": idea.get("problem", ""),
            "solution_summary": idea.get("solution_summary", ""),
            "core_innovations": idea.get("core_innovations", []),
            "theme_keywords": idea.get("theme_keywords", []),
            "evidence_refs": idea.get("evidence_refs", []),
            "selection_reason": selection_reason,
            "selected_at": datetime.now().isoformat(timespec="seconds"),
            "status": "selected",
        }
    )
    write_json(IDEA_REGISTRY_PATH, registry)
    return registry_entry_id


def total_score(idea: dict) -> int:
    score = idea.get("score", {})
    return int(score.get("novelty", 0)) + int(score.get("feasibility", 0)) + int(score.get("fit_to_rules", 0)) + int(score.get("communication_potential", 0))


def top_alignment_lines(idea: dict) -> list[str]:
    alignment = idea.get("template_alignment", {})
    lines = []
    opening = alignment.get("opening_summary", "")
    if opening:
        lines.append(f"   - 开场总述：{opening}")
    blind_spots = alignment.get("blind_spots", [])
    if blind_spots:
        lines.append(f"   - 关键盲区：{'；'.join(blind_spots[:2])}")
    closing = alignment.get("closing_summary", "")
    if closing:
        lines.append(f"   - 收口判断：{closing}")
    return lines


def update_workspace_state(topic_dir: Path, selected_id: str) -> None:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not state_path.exists():
        return
    state = read_json(state_path)
    if selected_id:
        state["current_step"] = "concept"
        state["workflow_status"]["selection"] = "completed"
        state["workflow_status"]["concept"] = "active"
        state["selected_idea_id"] = selected_id
        state["next_action"] = "run_concept"
        state["required_inputs"] = []
    else:
        state["current_step"] = "selection"
        state["workflow_status"]["selection"] = "active"
        state["selected_idea_id"] = ""
        state["next_action"] = "human_select_idea"
        state["required_inputs"] = ["人工确认 selected_id"]
    state["blocking_reason"] = ""
    write_json(state_path, state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AutoSearch MVP step3 selection gate.")
    parser.add_argument("topic_dir", help="Topic directory, such as sample/topic_xx")
    parser.add_argument("--select-id", default="", help="Optional selected idea id, such as idea_a")
    parser.add_argument(
        "--auto-select",
        action="store_true",
        help="Automatically select the top-ranked idea when --select-id is not provided.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    step_dir = topic_dir / "workspace" / "selection"
    scorecard_path = topic_dir / "workspace" / "ideas" / "idea-scorecard.json"
    if not scorecard_path.exists():
        raise SystemExit("idea-scorecard.json not found. Run step2 first.")

    ideas = read_json(scorecard_path).get("ideas", [])
    if not ideas:
        raise SystemExit("No ideas found in idea-scorecard.json.")

    ranked = sorted(ideas, key=total_score, reverse=True)
    selected_id = args.select_id.strip()
    auto_selected = False
    if not selected_id and args.auto_select and ranked:
        selected_id = ranked[0]["idea_id"]
        auto_selected = True
    selected_idea = next((idea for idea in ideas if idea["idea_id"] == selected_id), None) if selected_id else None

    lines = [
        "# Selection Package",
        "",
        "## Recommended Order",
    ]
    for index, idea in enumerate(ranked, start=1):
        lines.extend(
            [
                f"{index}. `{idea['idea_id']}` {idea['project_name']}（总分 {total_score(idea)}）",
                f"   - 推荐理由：创新性 {idea['score']['novelty']}，可行性 {idea['score']['feasibility']}，匹配度 {idea['score']['fit_to_rules']}，展示潜力 {idea['score']['communication_potential']}",
                f"   - 主要风险：{'；'.join(idea.get('risk_notes', [])[:2]) or 'none'}",
                f"   - 候选察言预览：{idea.get('candidate_preview_path', 'none')}",
            ]
        )
        lines.extend(top_alignment_lines(idea))
    lines.extend(["", "## Selection Status"])
    registry_entry_id = ""
    selection_reason = ""
    if selected_idea:
        selection_reason = "按最高总分自动选中进入下一流程。" if auto_selected else "已人工确认进入下一流程。"
        registry_entry_id = sync_selected_idea(topic_dir, selected_idea, selection_reason)
        lines.extend(
            [
                f"- Human Selected ID: `{selected_idea['idea_id']}`",
                f"- Selected Project: {selected_idea['project_name']}",
                f"- Reason Summary: {selection_reason}",
                f"- Idea Registry Entry: `{registry_entry_id}`",
            ]
        )
    else:
        lines.extend(
            [
                "- Human Selected ID: pending",
                "- Gate Status: waiting_for_human_selection",
                "- Action Required: 请在 `idea_a / idea_b / idea_c` 中人工选择一个最终方向。",
            ]
        )

    rejected = []
    if selected_idea:
        rejected = [
            {
                "idea_id": idea["idea_id"],
                "reason": "本轮未被人工选中，保留为备选方向。"
            }
            for idea in ideas
            if idea["idea_id"] != selected_idea["idea_id"]
        ]

    payload = {
        "status": "selected" if selected_idea else "pending_human_selection",
        "selected_id": selected_idea["idea_id"] if selected_idea else "",
        "recommended_order": [idea["idea_id"] for idea in ranked],
        "selection_reason": selection_reason if selected_idea else "",
        "rejected_ideas": rejected,
        "selected_registry_entry_id": registry_entry_id,
        "selected_candidate_preview_path": selected_idea.get("candidate_preview_path", "") if selected_idea else "",
        "selection_mode": "auto_top_ranked" if auto_selected else ("manual" if selected_idea else "pending"),
    }

    write_text(step_dir / "selection-package.md", "\n".join(lines) + "\n")
    write_json(step_dir / "selected-idea.json", payload)
    update_workspace_state(topic_dir, selected_id=payload["selected_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

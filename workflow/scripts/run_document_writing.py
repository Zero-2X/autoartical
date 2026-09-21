#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from proposal_workflow import (
    archive_stale_chapter_dirs,
    assemble_approved_draft,
    backup_legacy_draft,
    build_action_ledger,
    build_chapter_specs,
    build_runtime,
    ensure_state_scaffold,
    load_json_template,
    read_json,
    reconcile_chapters,
    render_review_log,
    render_writing_status,
    sync_workspace_state,
    write_json,
    write_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AutoSearch writing proposal draft with chapter-level multi-agent orchestration.")
    parser.add_argument("topic_dir", help="Topic directory, such as sample/topic_xx")
    return parser


def update_workflow_status(topic_dir: Path, *, writing_status: str, review_status: str, export_status: str | None = None) -> None:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not state_path.exists():
        return
    state = read_json(state_path)
    state.setdefault("workflow_status", {})["document_plan"] = "completed"
    state.setdefault("workflow_status", {})["document_writing"] = writing_status
    state.setdefault("workflow_status", {})["document_review"] = review_status
    if export_status is not None:
        state.setdefault("workflow_status", {})["document_export"] = export_status
    write_json(state_path, state)


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    ensure_state_scaffold(topic_dir)
    step_dir = topic_dir / "workspace" / "document_writing"
    output_dir = topic_dir / "output"
    card_path = topic_dir / "workspace" / "concept" / "idea-card.json"
    plan_path = topic_dir / "workspace" / "document_plan" / "section-plan.json"
    structure_gate_path = topic_dir / "workspace" / "document_plan" / "outline-structure-gate.json"

    if not card_path.exists() or not plan_path.exists():
        raise SystemExit("Missing inputs for document_writing.")
    if not structure_gate_path.exists():
        raise SystemExit("Missing outline-structure-gate.json for document_writing.")
    structure_gate = read_json(structure_gate_path)
    if structure_gate.get("verdict") != "pass":
        raise SystemExit("Step5 outline structure gate must pass before document_writing.")

    step_dir.mkdir(parents=True, exist_ok=True)
    (step_dir / "chapters").mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    idea_card = read_json(card_path)
    section_plan = read_json(plan_path)
    legacy_backup = backup_legacy_draft(step_dir)

    manifest_path = step_dir / "chapter-manifest.json"
    runtime_path = step_dir / "agent-runtime.json"
    ledger_path = step_dir / "action-ledger.json"

    existing_manifest = read_json(manifest_path) if manifest_path.exists() else load_json_template("chapter-manifest.template.json")
    existing_runtime = read_json(runtime_path) if runtime_path.exists() else load_json_template("document-writing-agent-runtime.template.json")
    existing_ledger = read_json(ledger_path) if ledger_path.exists() else load_json_template("document-writing-action-ledger.template.json")

    chapter_specs = build_chapter_specs(section_plan, idea_card)
    chapters = reconcile_chapters(topic_dir, step_dir, chapter_specs, existing_manifest)
    archived_dirs = archive_stale_chapter_dirs(step_dir, chapters)
    manifest = load_json_template("chapter-manifest.template.json")
    manifest["chapters"] = chapters
    runtime = build_runtime(chapters, existing_runtime)
    if legacy_backup:
        runtime.setdefault("notes", []).append(f"Legacy one-shot draft archived to {legacy_backup}.")
    if archived_dirs:
        runtime.setdefault("notes", []).append("Archived stale chapter dirs: " + "、".join(archived_dirs))
    ledger = build_action_ledger(chapters, existing_ledger)
    assembled = assemble_approved_draft(idea_card, chapters, topic_dir)

    write_json(manifest_path, manifest)
    write_json(runtime_path, runtime)
    write_json(ledger_path, ledger)
    write_text(step_dir / "status.md", render_writing_status(runtime, chapters))
    write_text(step_dir / "review-log.md", render_review_log(runtime, chapters))
    write_text(step_dir / "作品书草稿.md", assembled)
    write_text(output_dir / f"作品书_{idea_card.get('project_name', '')}.md", assembled)

    if runtime.get("workflow_status") == "ready_for_review":
        update_workflow_status(topic_dir, writing_status="completed", review_status="active", export_status="pending")
        sync_workspace_state(
            topic_dir,
            step="document_review",
            workflow_status="active",
            next_action="run_document_review",
            required_inputs=[
                "workspace/document_writing/chapter-manifest.json",
                "workspace/document_writing/作品书草稿.md",
            ],
            resume_entrypoint="workspace/document_writing/agent-runtime.json",
            last_completed_artifact="workspace/document_writing/作品书草稿.md",
            active_focus="所有章节已通过审计，等待总体验收",
            current_direction="沿用 agent1/agent2/agent3 的真实 LLM 线程进入 Step7 全书验收",
            note="Step6 chapter approvals complete.",
        )
    else:
        writing_status = "blocked" if runtime.get("workflow_status") == "blocked" else "active"
        update_workflow_status(topic_dir, writing_status=writing_status, review_status="pending", export_status="pending")
        sync_workspace_state(
            topic_dir,
            step="document_writing",
            workflow_status=writing_status,
            next_action="run_document_dispatch",
            required_inputs=runtime.get("required_inputs", []),
            resume_entrypoint="workspace/document_writing/agent-runtime.json",
            last_completed_artifact="workspace/document_writing/chapter-manifest.json",
            active_focus=f"当前章节：{runtime.get('current_chapter_heading', '')}",
            current_direction=f"先运行 dispatcher，下发当前动作：{runtime.get('next_action', '')}",
            blocking_reason=runtime.get("blocking_reason", ""),
            note="Step6 is running in real-LLM chapter mode.",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

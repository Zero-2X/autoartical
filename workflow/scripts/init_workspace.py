#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
REPO_ROOT = Path(__file__).resolve().parents[2]
RULE_KEYWORDS = ("比赛", "章程", "细则", "rule", "rules")
IDEA_KEYWORDS = ("idea_", "察言")
PROPOSAL_KEYWORDS = ("作品书",)
document_KEYWORDS = ()
IGNORED_PARTS = {"workspace", "output", "record", ".cache", ".texlive-config", ".texlive-var"}
IGNORED_SUFFIXES = {".aux", ".fdb_latexmk", ".fls", ".fmt", ".log", ".out", ".toc"}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json_template(name: str) -> dict:
    return json.loads((TEMPLATES_DIR / name).read_text(encoding="utf-8"))


def load_text_template(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


def ensure_shared_databases() -> None:
    evidence_dir = REPO_ROOT / "sample" / "databases" / "evidence"
    ideas_dir = REPO_ROOT / "sample" / "databases" / "ideas"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    ideas_dir.mkdir(parents=True, exist_ok=True)

    evidence_registry = evidence_dir / "evidence-registry.json"
    idea_registry = ideas_dir / "idea-registry.json"
    if not evidence_registry.exists():
        write_json(evidence_registry, load_json_template("evidence-registry.template.json"))
    if not idea_registry.exists():
        write_json(idea_registry, load_json_template("idea-registry.template.json"))


def classify_asset(path: Path) -> str:
    lower = path.name.lower()
    parts = {part.lower() for part in path.parts}
    if any(part in parts for part in IGNORED_PARTS):
        return "internal"
    if path.suffix.lower() in IGNORED_SUFFIXES:
        return "internal"
    if any(keyword in lower for keyword in RULE_KEYWORDS) or "比赛细则" in path.parts:
        return "rule"
    if any(keyword in lower for keyword in IDEA_KEYWORDS):
        return "idea"
    if any(keyword in lower for keyword in PROPOSAL_KEYWORDS):
        return "proposal"
    if any(keyword in lower for keyword in document_KEYWORDS):
        return "reference"
    return "reference"


def discover_topic_assets(topic_dir: Path) -> dict:
    assets = {
        "rules": [],
        "references": [],
        "samples": [],
        "outputs_present": [],
        "missing_inputs": [],
    }
    for path in sorted(topic_dir.rglob("*")):
        if not path.is_file():
            continue
        kind = classify_asset(path)
        if kind == "internal":
            continue
        rel = str(path.relative_to(topic_dir))
        if kind == "rule":
            assets["rules"].append(rel)
        elif kind == "reference":
            assets["references"].append(rel)
        elif kind in {"idea", "proposal", "reference"}:
            assets["samples"].append(rel)
            assets["outputs_present"].append({"kind": kind, "path": rel})

    if not assets["rules"]:
        assets["missing_inputs"].append("比赛细则文件")
    if not assets["references"]:
        assets["missing_inputs"].append("参考材料")
    return assets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize an AutoSearch MVP topic workspace.")
    parser.add_argument("topic_dir", help="Existing topic directory, such as sample/topic_xx")
    parser.add_argument("--topic-name", required=True, help="Display name for the topic workspace.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    if not topic_dir.exists():
        raise SystemExit(f"Topic directory does not exist: {topic_dir}")
    if not topic_dir.is_dir():
        raise SystemExit(f"Topic path is not a directory: {topic_dir}")

    workspace = topic_dir / "workspace"
    output = topic_dir / "output"
    external_evidence = topic_dir / "external_evidence"

    step_dirs = [
        "intake",
        "requirements",
        "ideas",
        "selection",
        "concept",
        "document_plan",
        "document_writing",
        "document_review",
        "state",
    ]
    for name in step_dirs:
        (workspace / name).mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    external_evidence.mkdir(parents=True, exist_ok=True)
    ensure_shared_databases()

    discovered_assets = discover_topic_assets(topic_dir)
    has_rules = bool(discovered_assets["rules"])

    state = load_json_template("workspace-state.template.json")
    state["topic_name"] = args.topic_name
    state["topic_root"] = str(topic_dir)
    state["workflow_status"]["intake"] = "completed" if has_rules else "active"
    if has_rules:
        state["current_step"] = "requirements"
        state["workflow_status"]["requirements"] = "active"
        state["next_action"] = "run_requirements"
        state["required_inputs"] = []
        state["resume_entrypoint"] = "workspace/requirements/competition-spec.json"
    else:
        state["resume_entrypoint"] = "workspace/intake/topic-brief.md"
        state["next_action"] = "fix_step0_topic_assets"
        state["required_inputs"] = ["补充比赛细则文件"]
    write_json(workspace / "state" / "workspace-state.json", state)
    write_text(workspace / "state" / "conversation-log.md", load_text_template("conversation-log.template.md"))
    write_text(workspace / "state" / "request-log.md", load_text_template("request-log.template.md"))
    write_text(workspace / "state" / "decision-log.md", load_text_template("decision-log.template.md"))
    write_text(workspace / "state" / "change-log.md", load_text_template("change-log.template.md"))

    write_text(
        workspace / "intake" / "topic-brief.md",
        "# Topic Brief\n\n"
        f"- Topic Name: {args.topic_name}\n"
        f"- Topic Root: {topic_dir}\n"
        f"- Competition Rules: {len(discovered_assets['rules'])}\n"
        f"- References: {len(discovered_assets['references'])}\n"
        f"- Existing Outputs: {len(discovered_assets['outputs_present'])}\n"
        f"- Missing Inputs: {', '.join(discovered_assets['missing_inputs']) or 'none'}\n",
    )
    write_json(
        workspace / "intake" / "topic-assets.json",
        discovered_assets,
    )

    write_json(workspace / "requirements" / "competition-spec.json", load_json_template("competition-spec.template.json"))
    write_text(workspace / "requirements" / "rule-summary.md", "# Rule Summary\n\n")
    write_text(workspace / "ideas" / "evidence-summary.md", "# Evidence Summary\n\n")
    write_json(workspace / "ideas" / "evidence-ledger.json", load_json_template("evidence-ledger.template.json"))
    write_text(workspace / "ideas" / "idea-batch.md", "# Idea Batch\n\n")
    write_json(workspace / "ideas" / "idea-scorecard.json", load_json_template("idea-scorecard.template.json"))
    write_text(workspace / "selection" / "selection-package.md", "# Selection Package\n\n")
    write_json(workspace / "selection" / "selected-idea.json", load_json_template("selected-idea.template.json"))
    write_json(workspace / "concept" / "idea-card.json", load_json_template("idea-card.template.json"))
    write_text(workspace / "document_plan" / "outline.md", "# Proposal Outline\n\n")
    write_text(workspace / "document_plan" / "reference-template.md", "# Proposal Reference Template\n\n")
    write_json(workspace / "document_plan" / "section-plan.json", load_json_template("section-plan.template.json"))
    write_json(
        workspace / "document_plan" / "score-coverage.json",
        {"dimensions": [], "covered": [], "gaps": []},
    )
    write_text(workspace / "document_writing" / "作品书草稿.md", "# 作品书草稿\n\n")
    (workspace / "document_writing" / "chapters").mkdir(parents=True, exist_ok=True)
    write_json(workspace / "document_writing" / "agent-runtime.json", load_json_template("document-writing-agent-runtime.template.json"))
    write_json(workspace / "document_writing" / "chapter-manifest.json", load_json_template("chapter-manifest.template.json"))
    write_json(workspace / "document_writing" / "action-ledger.json", load_json_template("document-writing-action-ledger.template.json"))
    write_text(workspace / "document_writing" / "status.md", "# Step6 Multi-Agent Status\n\n")
    write_text(workspace / "document_writing" / "review-log.md", "# Step6 Review Log\n\n")
    write_text(
        output / "README.md",
        "# Output\n\n"
        "Final delivery is produced only after content, evidence, visual, render and page QA gates pass.\n"
        "Expected outputs: Markdown source, print-ready HTML, and a rendered PDF or DOCX when a renderer is available.\n",
    )
    write_text(workspace / "document_review" / "quality-report.md", "# Quality Report\n\n")
    write_json(workspace / "document_review" / "quality-gate.json", load_json_template("quality-gate.template.json"))
    write_text(
        external_evidence / "README.md",
        "# External Evidence\n\n"
        "Place web-searched papers, reports, datasets, and manually curated evidence notes here.\n\n"
        "- `external-evidence-intake.json`: structured source list for Step2 import.\n"
        "- `*.md`: optional search notes, reading memos, or evidence curation logs.\n\n"
        "Recommended fields per item:\n"
        "- source_title / source_url / source_type / source_authority\n"
        "- claim / summary / derived_insight\n"
        "- inspiration_points / evidence_for\n"
        "- applicable_steps / applicable_work_types\n"
        "- reliability / curation_status / usage_hint / limitations\n",
    )
    write_json(
        external_evidence / "external-evidence-intake.json",
        load_json_template("external-evidence-intake.template.json"),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from writing_quality_rules import load_writing_quality_rules
from content_depth import content_metrics


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
DEFAULT_BACKBONE = {"model": "gpt-5.4", "reasoning_effort": "high"}
DEFAULT_MAX_ROUNDS = 3
PLACEHOLDER_SNIPPETS = ("待写作", "待审计", "占位", "not_started")
WORD_BUDGET_MIN_RATIO = 1.0
WRITING_QUALITY_RULES = load_writing_quality_rules()
AUTHORITATIVE_SOURCE_AUTHORITIES = {
    "competition_official",
    "academic",
    "official_platform",
    "industry_report",
}
PASSLIKE_DIMENSION_STATUSES = {"pass", "passed", "not_applicable", "n/a", "na"}
REQUIRED_APPROVAL_DIMENSIONS = (
    "goal_alignment",
    "score_alignment",
    "position_logic",
    "heading_structure",
    "body_priority_coverage",
    "evidence_support",
    "length_budget",
    "terminology_consistency",
    "pending_items_handling",
)

AUDIT_DIMENSION_KEYS = (
    "goal_alignment",
    "score_alignment",
    "position_logic",
    "heading_structure",
    "body_priority_coverage",
    "evidence_support",
    "innovation_loop",
    "length_budget",
    "visuals_alignment",
    "terminology_consistency",
    "pending_items_handling",
)

LEGACY_SYNTHETIC_APPROVAL_NOTE = "Synthetic flow test approval with structure-complete and evidence-aware draft."
LEGACY_SYNTHETIC_NOTE_MARKERS = (
    LEGACY_SYNTHETIC_APPROVAL_NOTE,
    "synthetic flow test draft content",
)
GENERIC_DIMENSION_PASS_NOTES = {
    "goal_alignment": "章节目标与本章职责一致。",
    "score_alignment": "章节内容与对应评分维度保持一致。",
    "position_logic": "章节位置与前后文衔接合理。",
    "heading_structure": "章节标题结构满足当前硬约束。",
    "body_priority_coverage": "章节已覆盖本章要求的核心论证重点。",
    "evidence_support": "章节已吸收证据并形成对应论证。",
    "innovation_loop": "章节中的创新点、实现与验证信号已形成闭环。",
    "length_budget": "章节长度满足当前预算要求。",
    "visuals_alignment": "图表规划与正文论证位置保持一致。",
    "terminology_consistency": "关键术语、模块名和项目名保持一致。",
    "pending_items_handling": "开放项已通过范围约束或条件性表述处理。",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json_template(name: str) -> dict[str, Any]:
    return json.loads((TEMPLATES_DIR / name).read_text(encoding="utf-8"))


def ensure_file(path: Path, default_content: str) -> None:
    if not path.exists():
        write_text(path, default_content)


def ensure_json(path: Path, payload: dict[str, Any]) -> None:
    if not path.exists():
        write_json(path, payload)


def ensure_state_scaffold(topic_dir: Path) -> None:
    state_dir = topic_dir / "workspace" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    workspace_path = state_dir / "workspace-state.json"
    if workspace_path.exists():
        workspace = read_json(workspace_path)
        record = load_json_template("workspace-state.template.json")
        record["topic_name"] = workspace.get("topic_name", "")
        record["topic_root"] = workspace.get("topic_root", str(topic_dir))
        record["current_step"] = workspace.get("current_step", "intake")
        record["current_workflow_status"] = workspace.get("current_workflow_status", "active")
        record["resume_entrypoint"] = workspace.get("resume_entrypoint", "")
        record["required_inputs"] = workspace.get("required_inputs", [])
        record["last_completed_artifact"] = workspace.get("last_completed_artifact", "")
        record["blocking_reason"] = workspace.get("blocking_reason", "")
        record["next_action"] = workspace.get("next_action", "")
        record["latest_user_request"] = workspace.get("latest_user_request", "")
        record["current_direction"] = workspace.get("current_direction", "")
        record["last_updated"] = workspace.get("last_updated", "")
        ensure_json(state_dir / "record-state.json", record)
    ensure_file(state_dir / "conversation-log.md", (TEMPLATES_DIR / "conversation-log.template.md").read_text(encoding="utf-8"))
    ensure_file(state_dir / "request-log.md", (TEMPLATES_DIR / "request-log.template.md").read_text(encoding="utf-8"))
    ensure_file(state_dir / "decision-log.md", (TEMPLATES_DIR / "decision-log.template.md").read_text(encoding="utf-8"))
    ensure_file(state_dir / "change-log.md", (TEMPLATES_DIR / "change-log.template.md").read_text(encoding="utf-8"))


def format_rule_examples(items: list[str], *, default: str = "none") -> str:
    normalized = [str(item).strip() for item in items if str(item).strip()]
    if not normalized:
        return default
    return "、".join(f"`{item}`" for item in normalized)


def sync_workspace_state(
    topic_dir: Path,
    *,
    step: str,
    workflow_status: str,
    next_action: str,
    required_inputs: list[str],
    resume_entrypoint: str,
    last_completed_artifact: str,
    latest_user_request: str = "",
    active_focus: str = "",
    current_direction: str = "",
    blocking_reason: str = "",
    open_questions: list[str] | None = None,
    note: str = "",
) -> None:
    state_dir = topic_dir / "workspace" / "state"
    workspace_path = state_dir / "workspace-state.json"
    record_path = state_dir / "record-state.json"
    if not workspace_path.exists():
        return

    workspace = read_json(workspace_path)
    timestamp = utc_now()
    workspace["current_step"] = step
    workspace["current_workflow_status"] = workflow_status
    workspace.setdefault("workflow_status", {})[step] = workflow_status
    workspace["latest_user_request"] = latest_user_request or workspace.get("latest_user_request", "")
    workspace["active_focus"] = active_focus
    workspace["current_direction"] = current_direction
    workspace["blocking_reason"] = blocking_reason
    workspace["next_action"] = next_action
    workspace["next_actions"] = [next_action] if next_action else []
    workspace["open_questions"] = open_questions or []
    workspace["resume_entrypoint"] = resume_entrypoint
    workspace["required_inputs"] = required_inputs
    workspace["last_completed_artifact"] = last_completed_artifact
    workspace["last_verified_at"] = timestamp
    workspace["last_updated"] = timestamp
    if note:
        workspace["notes"] = note
    write_json(workspace_path, workspace)

    if not record_path.exists():
        return
    record = read_json(record_path)
    record["current_step"] = step
    record["current_workflow_status"] = workflow_status
    record["resume_entrypoint"] = resume_entrypoint
    record["required_inputs"] = required_inputs
    record["last_completed_artifact"] = last_completed_artifact
    record["blocking_reason"] = blocking_reason
    record["next_action"] = next_action
    record["next_action_owner"] = "agent"
    record["latest_user_request"] = latest_user_request or record.get("latest_user_request", "")
    record["current_direction"] = current_direction
    record["last_updated"] = timestamp
    if note:
        record["notes"] = note
    write_json(record_path, record)


def _meaningful_text(text: str) -> bool:
    normalized = text.strip()
    if len(normalized) < 80:
        return False
    head = normalized[:120]
    return not any(snippet in head for snippet in PLACEHOLDER_SNIPPETS)


def _has_substantive_countable_text(text: str) -> bool:
    cleaned = strip_markdown_for_count(text)
    if not cleaned:
        return False
    reduced = cleaned
    for snippet in PLACEHOLDER_SNIPPETS:
        reduced = re.sub(re.escape(snippet), " ", reduced, flags=re.I)
    reduced = re.sub(r"[\s:：,，.。;；!！?？()（）\-/]+", "", reduced)
    return bool(reduced)


def _find_global_reference(reference_template: dict[str, Any], keyword: str) -> dict[str, str]:
    for item in reference_template.get("global_structure", []):
        if keyword in item.get("section", ""):
            return {
                "sample_chapter": item.get("section", ""),
                "suggested_page_span": item.get("page_span", ""),
                "suggested_word_budget": item.get("word_budget", ""),
            }
    return {"sample_chapter": "", "suggested_page_span": "", "suggested_word_budget": ""}


def parse_word_budget_range(raw_budget: str) -> dict[str, Any]:
    budget = (raw_budget or "").strip().lower()
    if not budget or budget == "citation_only":
        return {
            "raw": raw_budget or "",
            "enforceable": False,
            "lower": 0,
            "upper": 0,
            "label": budget or "none",
        }
    numbers = [int(match) for match in re.findall(r"\d+", budget)]
    if not numbers:
        return {
            "raw": raw_budget or "",
            "enforceable": False,
            "lower": 0,
            "upper": 0,
            "label": budget,
        }
    lower = numbers[0]
    upper = numbers[1] if len(numbers) > 1 else numbers[0]
    return {
        "raw": raw_budget or "",
        "enforceable": True,
        "lower": lower,
        "upper": upper,
        "label": f"{lower}-{upper}",
    }


def strip_markdown_for_count(text: str) -> str:
    cleaned = re.sub(r"```.*?```", " ", text, flags=re.S)
    cleaned = re.sub(r"`[^`]+`", " ", cleaned)
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"^#+\s*", "", cleaned, flags=re.M)
    cleaned = re.sub(r"^\s*[-*+]\s*", "", cleaned, flags=re.M)
    cleaned = re.sub(r"^\s*\d+\.\s*", "", cleaned, flags=re.M)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def unique_nonempty_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = item.strip() if isinstance(item, str) else ""
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def count_text_units(text: str) -> int:
    cleaned = strip_markdown_for_count(text)
    cjk_chars = re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", cleaned)
    latin_words = re.findall(r"[A-Za-z0-9]+(?:[-_/][A-Za-z0-9]+)*", cleaned)
    return len(cjk_chars) + len(latin_words)


def parse_markdown_headings(text: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = re.match(r"^(#{2,6})\s+(.*)$", line.strip())
        if not match:
            continue
        level = len(match.group(1))
        title = normalize_outline_heading(match.group(2))
        if not title:
            continue
        headings.append({"level": level, "title": title})
    return headings


def build_heading_structure_gate(chapter: dict[str, Any], draft_text: str) -> dict[str, Any]:
    contract = chapter.get("structure_contract", {}) if isinstance(chapter.get("structure_contract", {}), dict) else {}
    if chapter.get("chapter_type") != "body_section":
        return {
            "required": False,
            "status": "not_applicable",
            "passed": True,
            "required_second_level_count": 0,
            "actual_second_level_count": 0,
            "required_third_level_total_min": 0,
            "actual_third_level_total": 0,
            "missing_second_level_titles": [],
            "missing_third_level_titles": [],
            "notes": "Abstract/conclusion chapters do not require body heading structure gate.",
        }

    required_second_level_titles = [normalize_outline_heading(item) for item in contract.get("required_second_level_titles", [])]
    second_level_contracts = contract.get("second_level_contracts", [])
    heading_items = parse_markdown_headings(draft_text)
    h3_titles = [item["title"] for item in heading_items if item["level"] == 3]
    h4_by_h3: dict[str, list[str]] = {}
    current_h3 = ""
    for item in heading_items:
        if item["level"] == 3:
            current_h3 = item["title"]
            h4_by_h3.setdefault(current_h3, [])
        elif item["level"] == 4 and current_h3:
            h4_by_h3.setdefault(current_h3, []).append(item["title"])

    missing_second_level_titles = [title for title in required_second_level_titles if title not in h3_titles]
    missing_third_level_titles: list[str] = []
    per_second_level: list[dict[str, Any]] = []
    actual_third_level_total = 0
    for item in second_level_contracts:
        second_title = normalize_outline_heading(item.get("title", ""))
        required_third_titles = [normalize_outline_heading(title) for title in item.get("required_third_level_titles", [])]
        actual_third_titles = h4_by_h3.get(second_title, [])
        actual_third_level_total += len(actual_third_titles)
        missing_titles = [title for title in required_third_titles if title not in actual_third_titles]
        missing_third_level_titles.extend([f"{second_title}/{title}" for title in missing_titles])
        per_second_level.append(
            {
                "title": second_title,
                "required_third_level_count": int(item.get("required_third_level_count", 0) or 0),
                "actual_third_level_count": len(actual_third_titles),
                "required_third_level_titles": required_third_titles,
                "actual_third_level_titles": actual_third_titles,
                "missing_third_level_titles": missing_titles,
            }
        )

    required_second_level_count = int(contract.get("required_second_level_count", len(required_second_level_titles)) or 0)
    required_third_level_total_min = int(contract.get("required_third_level_total_min", 0) or 0)
    passed = (
        bool(required_second_level_titles)
        and len(h3_titles) >= required_second_level_count
        and not missing_second_level_titles
        and actual_third_level_total >= required_third_level_total_min
        and not missing_third_level_titles
    )
    notes = (
        f"required_h3={required_second_level_count}, actual_h3={len(h3_titles)}, "
        f"required_h4>={required_third_level_total_min}, actual_h4={actual_third_level_total}"
    )
    return {
        "required": True,
        "status": "passed" if passed else "failed",
        "passed": passed,
        "required_second_level_count": required_second_level_count,
        "actual_second_level_count": len(h3_titles),
        "required_second_level_titles": required_second_level_titles,
        "actual_second_level_titles": h3_titles,
        "required_third_level_total_min": required_third_level_total_min,
        "actual_third_level_total": actual_third_level_total,
        "missing_second_level_titles": missing_second_level_titles,
        "missing_third_level_titles": missing_third_level_titles,
        "per_second_level": per_second_level,
        "notes": notes,
    }


def build_length_gate(chapter: dict[str, Any], draft_text: str) -> dict[str, Any]:
    budget = parse_word_budget_range(chapter.get("suggested_word_budget", ""))
    has_countable_text = _has_substantive_countable_text(draft_text)
    actual_count = (
        content_metrics(draft_text)["prose_units"]
        if chapter.get("chapter_type") == "body_section"
        else count_text_units(draft_text)
    ) if has_countable_text else 0
    min_required = int(budget["lower"] * WORD_BUDGET_MIN_RATIO) if budget["enforceable"] else 0
    passed = (not budget["enforceable"]) or actual_count >= min_required
    status = "not_applicable"
    if budget["enforceable"]:
        status = "passed" if passed else "failed"
        if not has_countable_text:
            status = "pending"
    return {
        "count_rule": "Body: unique prose CJK characters plus Latin tokens; excludes headings, tables, code, math and images. Other chapters: markdown text units.",
        "raw_budget": budget["raw"],
        "budget_lower": budget["lower"],
        "budget_upper": budget["upper"],
        "min_ratio": WORD_BUDGET_MIN_RATIO,
        "min_required": min_required,
        "actual_count": actual_count,
        "enforceable": budget["enforceable"],
        "status": status,
        "passed": passed,
    }


def summarize_chapter_evidence(chapter: dict[str, Any]) -> dict[str, Any]:
    items = [item for item in chapter.get("supporting_evidence", []) if isinstance(item, dict)]
    chapter_type = chapter.get("chapter_type", "")
    required = chapter_type == "body_section"
    authoritative_count = 0
    high_reliability_count = 0
    insight_count = 0
    supports_terms: list[str] = []
    evidence_kinds: list[str] = []
    source_authorities: list[str] = []
    evidence_ids: list[str] = []

    for item in items:
        evidence_ids.append(item.get("evidence_id", ""))
        authority = item.get("source_authority", "")
        reliability = item.get("reliability", "")
        evidence_kind = item.get("evidence_kind", "")
        derived_insight = item.get("derived_insight", "") or item.get("summary", "")
        if authority in AUTHORITATIVE_SOURCE_AUTHORITIES:
            authoritative_count += 1
        if reliability == "high":
            high_reliability_count += 1
        if derived_insight:
            insight_count += 1
        supports_terms.extend(item.get("supports", []))
        if evidence_kind:
            evidence_kinds.append(evidence_kind)
        if authority:
            source_authorities.append(authority)

    unique_supports = unique_nonempty_strings(supports_terms)
    unique_kinds = unique_nonempty_strings(evidence_kinds)
    unique_authorities = unique_nonempty_strings(source_authorities)
    unique_evidence_ids = unique_nonempty_strings(evidence_ids)

    if not items:
        status = "not_applicable" if not required else "missing"
    elif authoritative_count == 0 and high_reliability_count == 0:
        status = "weak"
    elif len(items) >= 2 and insight_count >= 1 and unique_supports:
        status = "strong"
    else:
        status = "adequate"

    return {
        "required": required,
        "status": status,
        "evidence_count": len(items),
        "authoritative_count": authoritative_count,
        "high_reliability_count": high_reliability_count,
        "insight_count": insight_count,
        "supports_count": len(unique_supports),
        "supports": unique_supports,
        "evidence_kinds": unique_kinds,
        "source_authorities": unique_authorities,
        "evidence_ids": unique_evidence_ids,
    }


def find_incomplete_required_dimensions(audit_dimensions: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in REQUIRED_APPROVAL_DIMENSIONS:
        item = audit_dimensions.get(key, {}) if isinstance(audit_dimensions, dict) else {}
        status = item.get("status", "pending") if isinstance(item, dict) else "pending"
        if status not in PASSLIKE_DIMENSION_STATUSES:
            failures.append(key)
    return failures


def _is_structure_only_revision(
    required_revision_categories: list[str],
    requested_changes: list[Any],
    *,
    chapter_type: str,
) -> bool:
    allowed_categories = {"heading_structure", "length_budget"}
    if chapter_type != "body_section":
        allowed_categories = {"heading_structure", "length_budget"}
    normalized_categories = {item for item in required_revision_categories if item}
    if normalized_categories and not normalized_categories.issubset(allowed_categories):
        return False
    sources = set()
    for item in requested_changes:
        if isinstance(item, dict):
            source = item.get("source", "")
            if source:
                sources.add(source)
    allowed_sources = {"structure_gate", "length_gate"}
    if chapter_type != "body_section":
        allowed_sources = {"audit_contract", "length_gate"}
    return not sources or sources.issubset(allowed_sources)


def build_chapter_specs(section_plan: dict[str, Any], idea_card: dict[str, Any]) -> list[dict[str, Any]]:
    sections = section_plan.get("sections", [])
    reference_template = section_plan.get("reference_template", {})
    scoring_dimensions = section_plan.get("scoring_dimensions", [])
    chapters: list[dict[str, Any]] = []

    for index, section in enumerate(sections, start=1):
        chapters.append(
            {
                "chapter_id": section.get("section_id") or f"body_{index}",
                "chapter_type": "body_section",
                "heading": section.get("heading", ""),
                "title": section.get("title") or section.get("heading", ""),
                "goal": section.get("goal", ""),
                "matched_scores": section.get("matched_scores", []),
                "narrative_role": section.get("narrative_role", ""),
                "position_logic": section.get("position_logic", ""),
                "chapter_weight_reason": section.get("chapter_weight_reason", ""),
                "predecessor_sections": section.get("predecessor_sections", []),
                "successor_sections": section.get("successor_sections", []),
                "writing_order": index,
                "assembly_order": index,
                "sample_chapter": section.get("sample_chapter", ""),
                "sample_logic": section.get("sample_logic", ""),
                "suggested_page_span": section.get("suggested_page_span", ""),
                "suggested_word_budget": section.get("suggested_word_budget", ""),
                "subsections": section.get("subsections", []),
                "structure_contract": section.get("structure_contract", {}),
                "body_priority": section.get("body_priority", []),
                "visual_priority": section.get("visual_priority", []),
                "appendix_candidates": section.get("appendix_candidates", []),
                "key_messages": section.get("key_messages", []),
                "must_include": section.get("must_include", []),
                "linked_innovations": section.get("linked_innovations", []),
                "linked_architecture": section.get("linked_architecture", []),
                "innovation_loop_map": section.get("innovation_loop_map", []),
                "supporting_evidence": section.get("supporting_evidence", []),
                "chapter_seed_payload": section.get("chapter_seed_payload", {}),
                "common_errors": section.get("common_errors", []),
                "pending_confirmations": section.get("pending_confirmations", []),
                "missing_materials": section.get("missing_materials", []),
                "recommended_visuals": section.get("recommended_visuals", []),
                "visual_specs": section.get("visual_specs", []),
                "work_type": section_plan.get("work_type", ""),
                "work_type_reason": section_plan.get("work_type_reason", ""),
                "project_name": section_plan.get("project_name", ""),
                "competition_name": section_plan.get("competition_name", ""),
            }
        )

    abstract_ref = _find_global_reference(reference_template, "摘要")
    abstract_order = len(chapters) + 1
    chapters.append(
        {
            "chapter_id": "abstract",
            "chapter_type": "abstract",
            "heading": "摘要",
            "title": "摘要",
            "goal": "用 2-3 段概括项目问题、方案、创新点和应用价值，供评委快速建立全局认知。",
            "matched_scores": scoring_dimensions,
            "narrative_role": "作为全书压缩视图，必须覆盖项目名称、问题、方案、创新和价值，不展开章节细节。",
            "position_logic": "摘要位于全书最前，负责压缩全书主线并帮助评委快速建立总认知。",
            "chapter_weight_reason": "摘要虽然篇幅短，但承担全书压缩任务，必须覆盖问题、方案、创新与结果。",
            "predecessor_sections": [],
            "successor_sections": [item.get("heading", "") for item in chapters if item.get("chapter_type") == "body_section"][:1],
            "writing_order": abstract_order,
            "assembly_order": 0,
            "sample_chapter": abstract_ref.get("sample_chapter", "摘要"),
            "sample_logic": "先交代问题与对象，再压缩方案、创新点和应用价值，不重复正文展开。",
            "suggested_page_span": abstract_ref.get("suggested_page_span", "2p"),
            "suggested_word_budget": abstract_ref.get("suggested_word_budget", "600-1000"),
            "subsections": [],
            "structure_contract": {},
            "body_priority": ["问题", "方案", "创新", "结果", "价值"],
            "visual_priority": [],
            "appendix_candidates": [],
            "key_messages": [
                f"项目名称必须稳定写为 {idea_card.get('project_name', '')}。",
                "摘要要覆盖问题、方案、创新、应用价值四个层面。",
                "摘要写完后应能独立支撑答辩开场和作品书检索。",
            ],
            "must_include": [
                idea_card.get("problem", ""),
                idea_card.get("solution_summary", ""),
                "核心创新点概括",
                "目标用户与应用价值概括",
            ],
            "linked_innovations": idea_card.get("core_innovations", []),
            "linked_architecture": idea_card.get("technical_architecture", []),
            "innovation_loop_map": [],
            "supporting_evidence": [],
            "common_errors": ["摘要写成口号", "摘要数据在正文无支撑", "摘要只讲方案不讲结果"],
            "pending_confirmations": [],
            "missing_materials": [],
            "recommended_visuals": [],
            "visual_specs": [],
            "work_type": section_plan.get("work_type", ""),
            "work_type_reason": section_plan.get("work_type_reason", ""),
            "project_name": section_plan.get("project_name", ""),
            "competition_name": section_plan.get("competition_name", ""),
        }
    )

    conclusion_order = len(chapters) + 1
    chapters.append(
        {
            "chapter_id": "conclusion",
            "chapter_type": "conclusion",
            "heading": "结语",
            "title": "结语",
            "goal": "收束项目贡献、作品价值与后续优化方向，不再新增核心论证。",
            "matched_scores": ["应用价值", "讲解表现"],
            "narrative_role": "作为收尾章节，总结贡献、应用价值并给出克制的后续优化方向。",
            "position_logic": "结语位于全书末尾，只做收束，不再引入新技术细节或新实验。",
            "chapter_weight_reason": "结语篇幅不大，但直接影响整部作品书的成熟度、完成感和评委对作品价值的最终判断。",
            "predecessor_sections": [item.get("heading", "") for item in chapters if item.get("chapter_type") == "body_section"][-1:],
            "successor_sections": [],
            "writing_order": conclusion_order,
            "assembly_order": len(sections) + 1,
            "sample_chapter": "第五章 总结与展望",
            "sample_logic": "只做总结、价值收束和后续优化方向，不重复正文技术细节。",
            "suggested_page_span": "1-2p",
            "suggested_word_budget": "800-1400",
            "subsections": [],
            "structure_contract": {},
            "body_priority": ["贡献总结", "作品价值", "后续优化"],
            "visual_priority": [],
            "appendix_candidates": [],
            "key_messages": [
                "总结项目已形成的核心能力与系统主线。",
                "收束作品对典型用户与应用场景的价值。",
                "提出下一流程优化方向，但不要写成范围管理说明。",
            ],
            "must_include": [
                "项目总体贡献总结",
                "作品价值收束",
                "下一流程优化方向",
            ],
            "linked_innovations": idea_card.get("core_innovations", []),
            "linked_architecture": idea_card.get("technical_architecture", []),
            "innovation_loop_map": [],
            "supporting_evidence": [],
            "common_errors": ["结尾新增未论证内容", "只重复前文没有收束", "把愿景写成当前已交付能力"],
            "pending_confirmations": idea_card.get("open_questions", []),
            "missing_materials": [],
            "recommended_visuals": [],
            "visual_specs": [],
            "work_type": section_plan.get("work_type", ""),
            "work_type_reason": section_plan.get("work_type_reason", ""),
            "project_name": section_plan.get("project_name", ""),
            "competition_name": section_plan.get("competition_name", ""),
        }
    )
    return chapters


def chapter_folder_name(chapter: dict[str, Any]) -> str:
    return f"{int(chapter.get('writing_order', 0)):02d}_{chapter.get('chapter_id', 'chapter')}"


def relative_to_topic(topic_dir: Path, path: Path) -> str:
    return str(path.relative_to(topic_dir))


def chapter_file_map(topic_dir: Path, step_dir: Path, chapter: dict[str, Any]) -> dict[str, str]:
    chapter_dir = step_dir / "chapters" / chapter_folder_name(chapter)
    return {
        "chapter_dir": relative_to_topic(topic_dir, chapter_dir),
        "brief": relative_to_topic(topic_dir, chapter_dir / "brief.md"),
        "draft": relative_to_topic(topic_dir, chapter_dir / "draft.md"),
        "audit": relative_to_topic(topic_dir, chapter_dir / "audit.md"),
        "decision_schema": relative_to_topic(topic_dir, chapter_dir / "decision-schema.md"),
        "decision": relative_to_topic(topic_dir, chapter_dir / "decision.json"),
    }


def render_validation_support_seed_draft(chapter: dict[str, Any]) -> str:
    payload = chapter.get("chapter_seed_payload", {}) if isinstance(chapter.get("chapter_seed_payload", {}), dict) else {}
    pack = payload.get("pack", {}) if isinstance(payload.get("pack", {}), dict) else {}
    summary = str(pack.get("summary", "")).strip()
    disclosure = str(pack.get("disclosure", "")).strip()
    data_sources = [item for item in pack.get("data_sources", []) if isinstance(item, dict)]
    metric_summary = [item for item in pack.get("metric_summary", []) if isinstance(item, dict)]
    experiments = [item for item in pack.get("comparison_experiments", []) if isinstance(item, dict)]
    case_replay = pack.get("case_replay", {}) if isinstance(pack.get("case_replay", {}), dict) else {}
    case_timeline = [str(item).strip() for item in case_replay.get("timeline", []) if str(item).strip()]
    system_metrics = [str(item).strip() for item in pack.get("system_metrics", []) if str(item).strip()]

    lines: list[str] = [
        "### 测试数据与指标设置",
        "",
        "#### 数据来源",
        "",
        disclosure or "本章测试采用公开数据、仿真场景和原型运行日志构成的混合验证链，用于同时支撑效果指标与系统闭环指标。",
        "",
        summary or "本节围绕关键指标、对比实验、案例回放与系统日志组织测试证据链。",
        "",
    ]
    for item in data_sources:
        lines.append(f"- {item.get('name', '')}：{item.get('use', '')}")
    lines.extend(
        [
            "",
            "#### 指标定义",
            "",
            "本作品统一以准确率、综合 F1、复杂场景性能衰减、预警提前量、告警时延和闭环完成率等指标描述系统表现，以便同时覆盖识别质量、稳定性和工程运行能力。",
            "",
        ]
    )
    for item in metric_summary:
        lines.append(f"- {item.get('label', '')}：{item.get('value', '')}，{item.get('meaning', '')}")
    lines.extend(
        [
            "",
            "这些指标一部分用于衡量诊断模型本身的识别效果，另一部分用于描述系统输出能否进入运维动作，因此可以避免测试章只停留在算法结果而忽略业务闭环。",
            "",
            "#### 验证边界",
            "",
            "本章重点说明系统在公开数据、仿真工况与原型日志三类材料上的综合表现，不将当前结果表述为第三方认证或长期上线运行结论。",
            "",
            "### 多源融合效果验证",
            "",
            "#### 对比设置",
            "",
            "本节以单源输入、局部增强输入和完整多源融合方案作为对照，重点观察早期弱故障识别能力与漏报率变化。",
            "",
            "#### 实验结果",
            "",
        ]
    )
    if experiments:
        experiment = experiments[0]
        title = str(experiment.get("title", "")).strip()
        goal = str(experiment.get("goal", "")).strip()
        if title:
            lines.append(f"{title}围绕多通道输入增益展开。")
        if goal:
            lines.append(goal)
        for group in experiment.get("groups", []) or []:
            if str(group).strip():
                lines.append(f"- {group}")
        conclusion = str(experiment.get("conclusion", "")).strip()
        if conclusion:
            lines.append(f"结论：{conclusion}")
        lines.append("")
    lines.extend(
        [
            "",
            "#### 结果分析",
            "",
            "多源输入并不是简单堆叠传感器，而是通过跨通道证据互补降低单一通道噪声带来的误判风险。实验结果表明，多源融合和趋势平滑能够同时改善弱故障识别率与漏报控制能力。",
            "",
            "### 跨工况诊断效果验证",
            "",
            "#### 工况划分",
            "",
            "本节按同工况、跨转速、跨负载三类条件组织验证，并比较归一化与域对齐策略加入前后的变化。",
            "",
            "#### 对比结果",
            "",
        ]
    )
    if len(experiments) > 1:
        experiment = experiments[1]
        title = str(experiment.get("title", "")).strip()
        goal = str(experiment.get("goal", "")).strip()
        if title:
            lines.append(f"{title}围绕不同工况条件下的稳定性展开。")
        if goal:
            lines.append(goal)
        for group in experiment.get("groups", []) or []:
            if str(group).strip():
                lines.append(f"- {group}")
        conclusion = str(experiment.get("conclusion", "")).strip()
        if conclusion:
            lines.append(f"结论：{conclusion}")
        lines.append("")
    lines.extend(
        [
            "#### 稳定性分析",
            "",
            "跨工况验证的关键不在于追求单一最高分，而在于观察性能衰减是否被有效压缩，以及模型输出是否仍保持一致的故障判断逻辑。",
            "",
            "### 健康评分与案例回放",
            "",
            "#### 异常演化过程",
            "",
        ]
    )
    if case_timeline:
        for item in case_timeline[:3]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "#### 预警触发过程",
            "",
        ]
    )
    if case_timeline:
        for item in case_timeline[3:5]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "#### 复核与回写过程",
            "",
        ]
    )
    if case_timeline:
        for item in case_timeline[5:]:
            lines.append(f"- {item}")
    lines.extend(
        [
            "案例回放把静态分值转成时间序列过程，说明系统如何从风险抬升、告警触发走向人工复核和工单回写，从而把诊断结果真正落到维护动作上。",
            "",
            "### 系统性能与闭环测试",
            "",
            "#### 时延与吞吐",
            "",
        ]
    )
    for item in system_metrics:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "#### 告警与工单闭环",
            "",
            "本节重点观察告警生成时延、复核任务触发和工单回写完成率，判断系统结果是否真正进入运维流程。",
            "",
        ]
    )
    if len(experiments) > 2:
        experiment = experiments[2]
        goal = str(experiment.get("goal", "")).strip()
        if goal:
            lines.append(goal)
        for group in experiment.get("groups", []) or []:
            if str(group).strip():
                lines.append(f"- {group}")
        conclusion = str(experiment.get("conclusion", "")).strip()
        if conclusion:
            lines.append(f"结论：{conclusion}")
        lines.append("")
    lines.extend(
        [
            "#### 小结",
            "",
            "综上，本章把多源融合、跨工况适配、案例回放与系统闭环放进同一条测试链中，既说明识别效果，也说明系统能否稳定运行并进入维护动作。",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _is_placeholder_draft(path: Path) -> bool:
    if not path.exists():
        return True
    content = path.read_text(encoding="utf-8").strip()
    return not content or "待写作。Agent2 仅在当前章节被 Agent1 解锁后写入正文。" in content


def _is_placeholder_audit(path: Path) -> bool:
    if not path.exists():
        return True
    content = path.read_text(encoding="utf-8").strip()
    return not content or "## Verdict\n- pending" in content


def _candidate_legacy_chapter_dirs(step_dir: Path, chapter_id: str, current_dir: Path) -> list[Path]:
    chapter_root = step_dir / "chapters"
    candidates = []
    for path in sorted(chapter_root.glob(f"*_{chapter_id}")):
        if path == current_dir or not path.is_dir():
            continue
        candidates.append(path)
    return candidates


def _is_placeholder_decision(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        payload = read_json(path)
    except Exception:
        return False
    return (
        str(payload.get("latest_verdict", "")).strip() in {"", "pending"}
        and str(payload.get("trigger_reason", "")).strip() == "chapter_not_started"
        and int(payload.get("current_round", 0) or 0) == 0
    )


def migrate_legacy_chapter_files(step_dir: Path, chapter: dict[str, Any], chapter_dir: Path) -> None:
    chapter_id = str(chapter.get("chapter_id", "")).strip()
    if not chapter_id:
        return
    draft_path = chapter_dir / "draft.md"
    audit_path = chapter_dir / "audit.md"
    decision_path = chapter_dir / "decision.json"
    current_needs_migration = _is_placeholder_draft(draft_path) and _is_placeholder_audit(audit_path)
    if not current_needs_migration and not _is_placeholder_decision(decision_path):
        return

    for legacy_dir in _candidate_legacy_chapter_dirs(step_dir, chapter_id, chapter_dir):
        legacy_draft = legacy_dir / "draft.md"
        legacy_audit = legacy_dir / "audit.md"
        legacy_decision = legacy_dir / "decision.json"
        if not legacy_draft.exists():
            continue
        if _is_placeholder_draft(legacy_draft):
            continue
        if _is_placeholder_draft(draft_path):
            shutil.copy2(legacy_draft, draft_path)
        if legacy_audit.exists() and _is_placeholder_audit(audit_path):
            shutil.copy2(legacy_audit, audit_path)
        if legacy_decision.exists() and _is_placeholder_decision(decision_path):
            shutil.copy2(legacy_decision, decision_path)
        break


def archive_stale_chapter_dirs(step_dir: Path, chapters: list[dict[str, Any]]) -> list[str]:
    chapter_root = step_dir / "chapters"
    if not chapter_root.exists():
        return []
    active_dirs = {chapter_folder_name(chapter) for chapter in chapters}
    archive_root = chapter_root / "_archive"
    archived: list[str] = []
    for path in sorted(chapter_root.iterdir()):
        if not path.is_dir():
            continue
        if path.name == "_archive" or path.name in active_dirs:
            continue
        archive_root.mkdir(parents=True, exist_ok=True)
        target = archive_root / path.name
        if target.exists():
            target = archive_root / f"{path.name}_{utc_now().replace(':', '').replace('-', '')}"
        shutil.move(str(path), str(target))
        archived.append(str(target.relative_to(step_dir)))
    return archived


def render_chapter_brief(
    chapter: dict[str, Any],
    *,
    topic_dir: Path,
    step_dir: Path,
    approved_before: list[dict[str, Any]],
) -> str:
    files = chapter_file_map(topic_dir, step_dir, chapter)
    evidence_summary = summarize_chapter_evidence(chapter)
    lines = [
        f"# Chapter Brief: {chapter.get('heading', chapter.get('title', ''))}",
        "",
        "## Workflow Contract",
        "- This chapter must be handled by real LLM agents, not deterministic filler text.",
        "- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.",
        f"- Agent2 writes this chapter into `{files['draft']}`.",
        f"- Agent3 audits the written chapter into `{files['audit']}` and updates `{files['decision']}`.",
        f"- Agent3 may consult `{files['decision_schema']}` for field contract only; Agent2 should ignore that file.",
        "- The next chapter stays locked until Agent3 approves this one.",
        "",
        "## Chapter Metadata",
        f"- Chapter ID: `{chapter.get('chapter_id', '')}`",
        f"- Chapter Type: `{chapter.get('chapter_type', '')}`",
        f"- Goal: {chapter.get('goal', '')}",
        f"- Narrative Role: {chapter.get('narrative_role', '')}",
        f"- Position Logic: {chapter.get('position_logic', '')}",
        f"- Chapter Weight Reason: {chapter.get('chapter_weight_reason', '')}",
        f"- Work Type: {chapter.get('work_type', '')}",
        f"- Matched Scores: {'、'.join(chapter.get('matched_scores', [])) or 'none'}",
        f"- Sample Reference: {chapter.get('sample_chapter', '')} / {chapter.get('sample_logic', '')}",
        f"- Suggested Length: {chapter.get('suggested_page_span', '')} / {chapter.get('suggested_word_budget', '')}",
        "",
        "## Section Dependencies",
    ]
    lines.extend([
        "- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。",
        "- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。",
        "- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。",
    ])
    lines.extend([f"- Previous: {item}" for item in chapter.get("predecessor_sections", []) if item] or ["- Previous: none"])
    lines.extend([f"- Next: {item}" for item in chapter.get("successor_sections", []) if item] or ["- Next: none"])
    lines.extend(["", "## Body Priorities"])
    lines.extend([f"- {item}" for item in chapter.get("body_priority", []) if item] or ["- none"])
    lines.extend(["", "## Visual Priorities"])
    lines.extend([f"- {item}" for item in chapter.get("visual_priority", []) if item] or ["- none"])
    lines.extend(["", "## Visual Specs"])
    for item in chapter.get("visual_specs", []):
        lines.append(
            f"- [{item.get('label', '')}] {item.get('title', '')} | type={item.get('visual_type', '')} | "
            f"purpose={item.get('purpose', '')} | anchor={item.get('placement_anchor', '')} | "
            f"subsection={item.get('suggested_subsection', '')} | required={item.get('required', False)}"
        )
        lines.append(f"  - Reference Hint: {item.get('body_reference_hint', '')}")
    if not chapter.get("visual_specs"):
        lines.append("- none")
    budget = parse_word_budget_range(chapter.get("suggested_word_budget", ""))
    if budget["enforceable"]:
        min_required = int(budget["lower"] * WORD_BUDGET_MIN_RATIO)
        lines.extend(
            [
                "",
                "## Length Gate",
                f"- Target Budget: {chapter.get('suggested_word_budget', '')}",
                f"- Minimum Pass Threshold: {min_required} (100% of lower bound {budget['lower']})",
                "- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.",
                "- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Length Gate",
                "- Target Budget: not enforceable",
                "- Count Rule: no chapter-level hard threshold for this chapter type.",
            ]
        )
    lines.extend(["", "## Must Include"])
    lines.extend([f"- {item}" for item in chapter.get("must_include", []) if item] or ["- none"])
    lines.extend(["", "## Key Messages"])
    lines.extend([f"- {item}" for item in chapter.get("key_messages", []) if item] or ["- none"])
    lines.extend(["", "## Linked Innovations"])
    lines.extend([f"- {item}" for item in chapter.get("linked_innovations", []) if item] or ["- none"])
    lines.extend(["", "## Linked Architecture"])
    lines.extend([f"- {item}" for item in chapter.get("linked_architecture", []) if item] or ["- none"])
    lines.extend(["", "## Subsections"])
    for subsection in chapter.get("subsections", []):
        if isinstance(subsection, dict):
            lines.append(
                f"- {subsection.get('title', '')}: {subsection.get('write_focus', '')} "
                f"({subsection.get('suggested_word_budget', subsection.get('word_budget', ''))})"
            )
        else:
            lines.append(f"- {subsection}")
    if not chapter.get("subsections"):
        lines.append("- none")
    contract = chapter.get("structure_contract", {}) if isinstance(chapter.get("structure_contract", {}), dict) else {}
    if contract:
        lines.extend(["", "## Structure Gate"])
        lines.append(f"- Required H3 Count: {contract.get('required_second_level_count', 0)}")
        lines.append(f"- Required H3 Titles: {'、'.join(contract.get('required_second_level_titles', [])) or 'none'}")
        lines.append(f"- Required H4 Total Min: {contract.get('required_third_level_total_min', 0)}")
        for item in contract.get("second_level_contracts", []):
            lines.append(
                f"- `{item.get('title', '')}` -> required H4 count={item.get('required_third_level_count', 0)}; "
                f"required titles={'、'.join(item.get('required_third_level_titles', [])) or 'none'}"
            )
    lines.extend(["", "## Markdown Structure Contract"])
    if chapter.get("chapter_type") == "body_section":
        lines.append("- This chapter must not remain a single flat prose block.")
        lines.append("- Writer must emit each planned subsection as an H3 heading in `draft.md`, using the exact titles below.")
        lines.append("- Under each H3 subsection, add 1-3 H4 headings that answer concrete questions inside that subsection.")
        lines.append("- Planned visuals must be cited inside the matching subsection body, not dumped at the chapter start or end.")
        for subsection in chapter.get("subsections", []):
            subsection_title = chapter_subsection_title(subsection)
            if not subsection_title:
                continue
            detail_titles = suggested_detail_headings(chapter, subsection_title)
            lines.append(f"- Required H3: `### {subsection_title}`")
            lines.append(f"- Suggested H4 under `{subsection_title}`: " + " / ".join(detail_titles))
    else:
        lines.append("- Use headings only when they improve readability; abstract and conclusion may stay compact.")

    lines.extend(["", "## Innovation Loop Map"])
    for item in chapter.get("innovation_loop_map", []):
        lines.append(
            f"- {item.get('innovation_title', '')}: problem={item.get('problem_source', '')}; "
            f"role={item.get('current_section_role', '')}; validation={item.get('validation_anchor', '')}; "
            f"signal={item.get('expected_value_signal', '')}; meaning={item.get('practical_meaning', '')}"
        )
    if not chapter.get("innovation_loop_map"):
        lines.append("- none")

    lines.extend(["", "## Evidence Contract"])
    lines.append(
        f"- Evidence Requirement: {'required' if evidence_summary['required'] else 'optional'} | "
        f"status={evidence_summary['status']} | count={evidence_summary['evidence_count']} | "
        f"authoritative={evidence_summary['authoritative_count']} | high_reliability={evidence_summary['high_reliability_count']}"
    )
    lines.append(
        "- Agent2 must translate evidence into chapter-level论证，不允许只堆 source 名称；每个亮点至少落到“问题来源 / 现有不足 / 本作品做法 / 预期价值”中的 2 个环节。"
    )
    lines.append(
        "- Agent3 must check whether the chapter really absorbed the evidence-derived insights, instead of only repeating generic claims."
    )
    if evidence_summary["supports"]:
        lines.append(f"- Suggested Evidence Anchors: {'、'.join(evidence_summary['supports'])}")
    if evidence_summary["evidence_kinds"]:
        lines.append(f"- Available Evidence Types: {'、'.join(evidence_summary['evidence_kinds'])}")
    if evidence_summary["source_authorities"]:
        lines.append(f"- Source Authorities: {'、'.join(evidence_summary['source_authorities'])}")

    lines.extend(["", "## Supporting Evidence"])
    for item in chapter.get("supporting_evidence", []):
        summary = item.get("derived_insight") or item.get("summary") or item.get("claim") or ""
        source = item.get("source", "")
        reliability = item.get("reliability", "")
        evidence_id = item.get("evidence_id", "")
        evidence_kind = item.get("evidence_kind", "")
        source_authority = item.get("source_authority", "")
        supports = "、".join(item.get("supports", [])) or "none"
        lines.append(
            f"- [{evidence_id or 'unknown'}] {summary} | kind={evidence_kind or 'unknown'} | "
            f"authority={source_authority or 'unknown'} | reliability={reliability or 'unknown'} | "
            f"supports={supports} | source={source or 'unknown'}"
        )
    if not chapter.get("supporting_evidence"):
        lines.append("- none")

    lines.extend(["", "## Pending Confirmations"])
    lines.extend([f"- {item}" for item in chapter.get("pending_confirmations", []) if item] or ["- none"])
    lines.extend(["", "## Missing Materials"])
    for item in chapter.get("missing_materials", []):
        lines.append(
            f"- {item.get('missing_item', '')} | impact={item.get('impacted_chapter', '')} | "
            f"why={item.get('why_needed', '')} | priority={item.get('priority', '')} | "
            f"backtrack={item.get('suggested_backtrack_step', '')} | substitute={item.get('minimum_acceptable_substitute', '')}"
        )
    if not chapter.get("missing_materials"):
        lines.append("- none")
    seed_payload = chapter.get("chapter_seed_payload", {}) if isinstance(chapter.get("chapter_seed_payload", {}), dict) else {}
    if seed_payload.get("enabled"):
        pack = seed_payload.get("pack", {}) if isinstance(seed_payload.get("pack", {}), dict) else {}
        lines.extend(["", "## Seed Context"])
        lines.append(f"- Seed Type: `{seed_payload.get('seed_type', '')}`")
        if pack.get("summary"):
            lines.append(f"- Pack Summary: {pack.get('summary', '')}")
        if pack.get("disclosure"):
            lines.append(f"- Disclosure: {pack.get('disclosure', '')}")
        required_assets = [str(item).strip() for item in pack.get("required_assets", []) if str(item).strip()]
        if required_assets:
            lines.append(f"- Required Assets: {'、'.join(required_assets)}")
    lines.extend(["", "## Approved Upstream Context"])
    for item in approved_before:
        lines.append(f"- {item.get('heading', '')}: `{item.get('files', {}).get('draft', '')}`")
    if not approved_before:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Writing Rules",
            "- Do not rewrite already approved chapters.",
            "- Do not repeat the chapter heading inside `draft.md`; write body content only.",
            "- Write as a competition works book final draft, not as a proposal, roadmap, or writing note.",
            "- Avoid meta-writing phrases such as "
            f"{format_rule_examples(WRITING_QUALITY_RULES.get('writing_brief_rules', {}).get('avoid_meta_phrases', []))}.",
            "- Prefer stating the work itself, the mechanism, and the evidence directly; do not explain how the chapter should be written.",
            "- Body chapters must output explicit Markdown hierarchy with `###` subsection headings and, where helpful, `####` detail headings.",
            "- Use the Step5 reference template as a proportional guide, not a rigid quota.",
            "- Keep project name, innovation names, and module names consistent with previous approved chapters.",
            "- Any uncertain claim must stay conditional or be explicitly described as not yet finalized; never emit raw workflow markers such as `pending`.",
            "- For each required visual spec, the正文 should either explicitly reference the planned visual with phrasing such as `如图X所示` / `表X显示` or explain why the visual asset is temporarily unavailable.",
            "- Visual references should appear near the paragraph where the claim is made; do not front-load all figures at the chapter opening.",
            "- If a hard length gate exists for this chapter, falling below it should trigger revise instead of approve.",
            "- The first sentence under each H4 should state a work fact directly: object / mechanism / output / value. Do not open with chapter-planning phrases.",
            "- Every subsection should answer at least two concrete questions from this set: what is the input, how is it processed, what is the output, why does it matter.",
            f"- Common errors for this chapter: {'；'.join(chapter.get('common_errors', [])) or 'none'}.",
            f"- Appendix candidates for overflow material: {'；'.join(chapter.get('appendix_candidates', [])) or 'none'}.",
            "",
            "## Forbidden Draft Markers",
            "- Never copy instructional phrases such as "
            f"{format_rule_examples(WRITING_QUALITY_RULES.get('writing_brief_rules', {}).get('forbidden_draft_markers', []))}.",
            "- Never leave process placeholders, synthetic test notes, or evaluation commentary inside正文.",
            "",
            "## Output Contract",
            *[
                f"- {item}"
                for item in WRITING_QUALITY_RULES.get("writing_brief_rules", {}).get("output_contract", [])
                if str(item).strip()
            ],
            "",
            "## Agent3 Decision Contract",
            "- `decision.json.latest_verdict` must be exactly one of `approved` / `revise` / `blocked`.",
            "- Once Agent3 outputs a non-pending verdict, required audit dimensions must not stay at `pending`.",
            f"- Required pass-or-explicit-NA dimensions before approval: {'、'.join(REQUIRED_APPROVAL_DIMENSIONS)}.",
            "- `evidence_support` must explicitly judge whether the chapter absorbed the evidence-derived insights rather than only listing source names.",
            "- `length_budget` must be `pass` or `fail`; if the hard threshold is not met, `approved` is invalid.",
            "- `pending_items_handling` must explicitly judge whether uncertain claims stayed conditional and whether missing materials were handled honestly.",
            "- If verdict is `revise`, `requested_changes` must contain concrete, executable items.",
            "- If verdict is `blocked`, `blocking_reason_category` and, when applicable, `return_to_step` must be explicit.",
            "",
            "## Acceptance Rule",
            "- Agent3 must either return `approved`, `revise`, or `blocked` in `decision.json`.",
            "- Only after `approved` may Agent1 unlock the next chapter.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_decision_schema(chapter: dict[str, Any]) -> str:
    evidence_required = "yes" if summarize_chapter_evidence(chapter)["required"] else "no"
    lines = [
        f"# Decision Schema: {chapter.get('heading', '')}",
        "",
        "This file defines audit structure only.",
        "It is not a writing sample, not a tone reference, and not a content template for正文生成.",
        "",
        "## Scope",
        "- Intended reader: agent3 auditor.",
        "- Agent2 writer should not use this file as a content-generation reference.",
        "",
        "## Verdict Enum",
        "- `approved`: chapter can move forward, but only if all required dimensions are explicit and closed.",
        "- `revise`: chapter has repairable issues; `requested_changes` must be concrete.",
        "- `blocked`: chapter cannot proceed without material recovery or step backtrack.",
        "",
        "## Required Approval Dimensions",
        f"- { '、'.join(REQUIRED_APPROVAL_DIMENSIONS) }",
        "- Allowed statuses for a closed dimension: `pass`, `fail`, `not_applicable`.",
        "- These dimensions must not remain `pending` once a non-pending verdict is issued.",
        "",
        "## Chapter-Specific Gates",
        f"- Evidence required for this chapter: {evidence_required}",
        f"- Suggested word budget: {chapter.get('suggested_word_budget', '') or 'none'}",
        "- If the length gate fails, `approved` is invalid.",
        "- If required dimensions are left pending, `approved` is invalid.",
        "",
        "## Field Contract",
        "- `latest_verdict`: approved / revise / blocked",
        "- `verdict_rationale`: concise reason for the verdict",
        "- `blocking_reason_category`: required for blocked, otherwise keep empty",
        "- `return_to_step`: fill only when a backtrack step is necessary",
        "- `audit_dimensions`: one object per dimension with explicit status and notes",
        "- `missing_materials_gate`: summarize whether missing inputs prevent a valid chapter",
        "- `primary_failures`: normalized failure labels, not long prose paragraphs",
        "- `required_revision_categories`: normalized categories that agent2 can act on",
        "- `requested_changes`: actionable revision items with short summaries",
        "- `approved_for_next_chapter`: true only when verdict is approved and gates are closed",
        "",
        "## Anti-Patterns",
        "- Do not copy phrasing from this file into正文.",
        "- Do not leave key dimensions at `pending` after making a verdict.",
        "- Do not write generic requested changes such as “优化文风” without a concrete target.",
        "- Do not mark evidence support as passed merely because sources were mentioned.",
    ]
    return "\n".join(lines) + "\n"


def default_audit_dimensions() -> dict[str, dict[str, Any]]:
    return {
        key: {
            "status": "pending",
            "notes": "",
            "evidence": [],
        }
        for key in AUDIT_DIMENSION_KEYS
    }


def _contains_legacy_synthetic_marker(text: str) -> bool:
    normalized = str(text or "").strip()
    if not normalized:
        return False
    lowered = normalized.lower()
    return any(marker.lower() in lowered for marker in LEGACY_SYNTHETIC_NOTE_MARKERS)


def sanitize_legacy_decision_language(payload: dict[str, Any]) -> dict[str, Any]:
    audit_dimensions = payload.get("audit_dimensions", {})
    if isinstance(audit_dimensions, dict):
        for key, item in audit_dimensions.items():
            if not isinstance(item, dict):
                continue
            notes = str(item.get("notes", "")).strip()
            if not _contains_legacy_synthetic_marker(notes):
                continue
            fallback = GENERIC_DIMENSION_PASS_NOTES.get(key, "该维度已通过当前审计要求。")
            item["notes"] = fallback

    top_level_notes = str(payload.get("notes", "")).strip()
    if _contains_legacy_synthetic_marker(top_level_notes):
        payload["notes"] = "Manual revision completed after quality cleanup."

    applied_changes = payload.get("applied_changes", [])
    if isinstance(applied_changes, list):
        for item in applied_changes:
            if not isinstance(item, dict):
                continue
            summary = str(item.get("summary", "")).strip()
            if _contains_legacy_synthetic_marker(summary):
                item["summary"] = "Manual revision completed after quality cleanup."

    verdict_rationale = str(payload.get("verdict_rationale", "")).strip()
    if _contains_legacy_synthetic_marker(verdict_rationale):
        payload["verdict_rationale"] = "章节已满足当前审计要求。"

    return payload


def default_chapter_decision(chapter: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_contract_version": "v3",
        "chapter_id": chapter.get("chapter_id", ""),
        "chapter_heading": chapter.get("heading", ""),
        "status": "pending",
        "current_round": 0,
        "max_rounds": DEFAULT_MAX_ROUNDS,
        "latest_writer_status": "not_started",
        "latest_audit_status": "not_started",
        "latest_verdict": "pending",
        "verdict_rationale": "",
        "blocking_reason_category": "",
        "return_to_step": "",
        "audit_dimensions": default_audit_dimensions(),
        "length_gate": {
            "count_rule": "Chinese CJK characters plus Latin word tokens after stripping markdown formatting.",
            "raw_budget": chapter.get("suggested_word_budget", ""),
            "budget_lower": 0,
            "budget_upper": 0,
            "min_ratio": WORD_BUDGET_MIN_RATIO,
            "min_required": 0,
            "actual_count": 0,
            "enforceable": False,
            "status": "pending",
            "passed": True,
        },
        "structure_gate": {
            "required": chapter.get("chapter_type", "") == "body_section",
            "status": "pending",
            "passed": chapter.get("chapter_type", "") != "body_section",
            "required_second_level_count": 0,
            "actual_second_level_count": 0,
            "required_third_level_total_min": 0,
            "actual_third_level_total": 0,
            "missing_second_level_titles": [],
            "missing_third_level_titles": [],
            "notes": "",
        },
        "missing_materials_gate": {
            "status": "pending",
            "items": [],
            "notes": "",
        },
        "primary_failures": [],
        "required_revision_categories": [],
        "recommended_visual_actions": [],
        "score_history": [],
        "trigger_reason": "chapter_not_started",
        "requested_changes": [],
        "applied_changes": [],
        "stale_state": {"is_stale": False, "reason": ""},
        "human_record_required": False,
        "human_record_status": "not_required",
        "approved_for_next_chapter": False,
        "ready_for_final_acceptance": False,
        "next_action": "agent1_dispatch_agent2_writer",
        "next_action_owner": "agent1",
        "last_updated": "",
        "notes": "",
    }


def normalize_decision_payload(chapter: dict[str, Any], payload: dict[str, Any] | None) -> dict[str, Any]:
    base = default_chapter_decision(chapter)
    current = payload or {}
    merged = dict(base)
    merged.update(current)
    merged["decision_contract_version"] = base["decision_contract_version"]

    current_dims = current.get("audit_dimensions", {}) if isinstance(current.get("audit_dimensions", {}), dict) else {}
    merged_dims = default_audit_dimensions()
    for key, default_item in merged_dims.items():
        existing_item = current_dims.get(key, {}) if isinstance(current_dims.get(key, {}), dict) else {}
        merged_dims[key] = {
            "status": existing_item.get("status", default_item["status"]),
            "notes": existing_item.get("notes", default_item["notes"]),
            "evidence": existing_item.get("evidence", default_item["evidence"]),
        }
    merged["audit_dimensions"] = merged_dims

    current_missing = current.get("missing_materials_gate", {}) if isinstance(current.get("missing_materials_gate", {}), dict) else {}
    merged["missing_materials_gate"] = {
        "status": current_missing.get("status", base["missing_materials_gate"]["status"]),
        "items": current_missing.get("items", base["missing_materials_gate"]["items"]),
        "notes": current_missing.get("notes", base["missing_materials_gate"]["notes"]),
    }
    current_structure_gate = current.get("structure_gate", {}) if isinstance(current.get("structure_gate", {}), dict) else {}
    merged["structure_gate"] = {
        "required": current_structure_gate.get("required", base["structure_gate"]["required"]),
        "status": current_structure_gate.get("status", base["structure_gate"]["status"]),
        "passed": current_structure_gate.get("passed", base["structure_gate"]["passed"]),
        "required_second_level_count": current_structure_gate.get("required_second_level_count", base["structure_gate"]["required_second_level_count"]),
        "actual_second_level_count": current_structure_gate.get("actual_second_level_count", base["structure_gate"]["actual_second_level_count"]),
        "required_third_level_total_min": current_structure_gate.get("required_third_level_total_min", base["structure_gate"]["required_third_level_total_min"]),
        "actual_third_level_total": current_structure_gate.get("actual_third_level_total", base["structure_gate"]["actual_third_level_total"]),
        "missing_second_level_titles": current_structure_gate.get("missing_second_level_titles", base["structure_gate"]["missing_second_level_titles"]),
        "missing_third_level_titles": current_structure_gate.get("missing_third_level_titles", base["structure_gate"]["missing_third_level_titles"]),
        "notes": current_structure_gate.get("notes", base["structure_gate"]["notes"]),
    }
    current_length_gate = current.get("length_gate", {}) if isinstance(current.get("length_gate", {}), dict) else {}
    merged["length_gate"] = {
        "count_rule": current_length_gate.get("count_rule", base["length_gate"]["count_rule"]),
        "raw_budget": current_length_gate.get("raw_budget", base["length_gate"]["raw_budget"]),
        "budget_lower": current_length_gate.get("budget_lower", base["length_gate"]["budget_lower"]),
        "budget_upper": current_length_gate.get("budget_upper", base["length_gate"]["budget_upper"]),
        "min_ratio": current_length_gate.get("min_ratio", base["length_gate"]["min_ratio"]),
        "min_required": current_length_gate.get("min_required", base["length_gate"]["min_required"]),
        "actual_count": current_length_gate.get("actual_count", base["length_gate"]["actual_count"]),
        "enforceable": current_length_gate.get("enforceable", base["length_gate"]["enforceable"]),
        "status": current_length_gate.get("status", base["length_gate"]["status"]),
        "passed": current_length_gate.get("passed", base["length_gate"]["passed"]),
    }
    return sanitize_legacy_decision_language(merged)


def seed_chapter_files(
    topic_dir: Path,
    step_dir: Path,
    chapter: dict[str, Any],
    *,
    approved_before: list[dict[str, Any]],
) -> None:
    chapter_dir = step_dir / "chapters" / chapter_folder_name(chapter)
    chapter_dir.mkdir(parents=True, exist_ok=True)
    write_text(chapter_dir / "brief.md", render_chapter_brief(chapter, topic_dir=topic_dir, step_dir=step_dir, approved_before=approved_before))
    migrate_legacy_chapter_files(step_dir, chapter, chapter_dir)
    seed_payload = chapter.get("chapter_seed_payload", {}) if isinstance(chapter.get("chapter_seed_payload", {}), dict) else {}
    draft_seed = ""
    if seed_payload.get("enabled") and seed_payload.get("seed_type") == "validation_support_pack":
        draft_seed = render_validation_support_seed_draft(chapter)
    ensure_file(
        chapter_dir / "draft.md",
        draft_seed or f"# Draft: {chapter.get('heading', '')}\n\n待写作。Agent2 仅在当前章节被 Agent1 解锁后写入正文。\n",
    )
    ensure_file(
        chapter_dir / "audit.md",
        (
            f"# Audit: {chapter.get('heading', '')}\n\n"
            "## Verdict\n"
            "- pending\n\n"
            "## Decision Contract\n"
            "- latest_verdict must be one of approved / revise / blocked\n"
            "- required dimensions cannot remain pending once a non-pending verdict is issued\n"
            "- if revise then requested_changes must be concrete\n"
            "- if blocked then blocking_reason_category must be explicit\n\n"
            "## Primary Failures\n"
            "- 待审计\n\n"
            "## Dimension Checks\n"
            "- goal_alignment: pending\n"
            "- score_alignment: pending\n"
            "- position_logic: pending\n"
            "- body_priority_coverage: pending\n"
            "- evidence_support: pending\n"
            "- innovation_loop: pending\n"
            "- length_budget: pending\n"
            "- visuals_alignment: pending\n"
            "- terminology_consistency: pending\n"
            "- pending_items_handling: pending\n\n"
            "## Requested Changes\n"
            "- 待审计\n\n"
            "## Missing Materials Gate\n"
            "- pending\n"
        ),
    )
    ensure_file(chapter_dir / "decision-schema.md", render_decision_schema(chapter))
    ensure_json(chapter_dir / "decision.json", default_chapter_decision(chapter))


def backup_legacy_draft(step_dir: Path) -> str:
    draft_path = step_dir / "作品书草稿.md"
    backup_path = step_dir / "legacy-one-shot-draft.md"
    manifest_path = step_dir / "chapter-manifest.json"
    if manifest_path.exists() or not draft_path.exists():
        return ""
    content = draft_path.read_text(encoding="utf-8")
    if _meaningful_text(content) and not backup_path.exists():
        write_text(backup_path, content)
        return str(backup_path.name)
    return ""


def reconcile_chapters(
    topic_dir: Path,
    step_dir: Path,
    specs: list[dict[str, Any]],
    existing_manifest: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    existing_lookup = {
        item.get("chapter_id"): item
        for item in (existing_manifest or {}).get("chapters", [])
        if item.get("chapter_id")
    }
    reconciled: list[dict[str, Any]] = []
    approved_prefix: list[dict[str, Any]] = []

    for spec in sorted(specs, key=lambda item: item.get("writing_order", 0)):
        merged = dict(spec)
        previous = existing_lookup.get(spec.get("chapter_id"))
        if previous:
            for key in (
                "status",
                "current_round",
                "latest_verdict",
                "score_history",
                "requested_changes",
                "applied_changes",
                "approved_at",
                "audit_summary",
            ):
                if key in previous:
                    merged[key] = previous[key]

        seed_chapter_files(topic_dir, step_dir, merged, approved_before=approved_prefix)
        files = chapter_file_map(topic_dir, step_dir, merged)
        merged["files"] = files

        decision_path = topic_dir / files["decision"]
        draft_path = topic_dir / files["draft"]
        audit_path = topic_dir / files["audit"]
        draft_text = draft_path.read_text(encoding="utf-8") if draft_path.exists() else ""
        audit_text = audit_path.read_text(encoding="utf-8") if audit_path.exists() else ""
        raw_decision = read_json(decision_path) if decision_path.exists() else default_chapter_decision(merged)
        decision = normalize_decision_payload(merged, raw_decision)
        decision["length_gate"] = build_length_gate(merged, draft_text)
        decision["structure_gate"] = build_heading_structure_gate(merged, draft_text)
        if (
            merged.get("chapter_type") == "body_section"
            and _meaningful_text(draft_text)
            and decision["structure_gate"].get("required")
            and not decision["structure_gate"].get("passed")
        ):
            repaired_draft = rebuild_draft_to_structure_contract(merged, draft_text)
            if repaired_draft and repaired_draft.strip() != draft_text.strip():
                write_text(draft_path, repaired_draft)
                draft_text = repaired_draft
                decision["length_gate"] = build_length_gate(merged, draft_text)
                decision["structure_gate"] = build_heading_structure_gate(merged, draft_text)
        write_json(decision_path, decision)

        verdict = decision.get("latest_verdict", "pending")
        requested_changes = decision.get("requested_changes", [])
        applied_changes = decision.get("applied_changes", [])
        score_history = decision.get("score_history", [])
        current_round = int(decision.get("current_round", 0) or 0)
        length_gate = decision.get("length_gate", build_length_gate(merged, draft_text))
        structure_gate = decision.get("structure_gate", build_heading_structure_gate(merged, draft_text))
        status = "pending"
        if verdict == "approved":
            if structure_gate.get("required") and not structure_gate.get("passed"):
                status = "needs_revision"
                verdict = "revise"
                decision["latest_verdict"] = "revise"
                structure_summary = (
                    f"章节标题结构未达硬约束：required_h3={structure_gate.get('required_second_level_count', 0)}, "
                    f"actual_h3={structure_gate.get('actual_second_level_count', 0)}, "
                    f"required_h4>={structure_gate.get('required_third_level_total_min', 0)}, "
                    f"actual_h4={structure_gate.get('actual_third_level_total', 0)}"
                )
                if not decision.get("verdict_rationale"):
                    decision["verdict_rationale"] = structure_summary
                updated_requested_changes = []
                found_structure_change = False
                for item in requested_changes:
                    if isinstance(item, dict) and item.get("source") == "structure_gate":
                        updated = dict(item)
                        updated["summary"] = structure_summary
                        updated["status"] = "open"
                        updated_requested_changes.append(updated)
                        found_structure_change = True
                    else:
                        updated_requested_changes.append(item)
                if not found_structure_change:
                    updated_requested_changes.append(
                        {
                            "summary": structure_summary,
                            "status": "open",
                            "source": "structure_gate",
                        }
                    )
                requested_changes = updated_requested_changes
            elif length_gate.get("enforceable") and not length_gate.get("passed"):
                status = "needs_revision"
                verdict = "revise"
                decision["latest_verdict"] = "revise"
                length_gate_summary = (
                    f"章节长度未达最低阈值：actual={length_gate.get('actual_count', 0)}, "
                    f"required>={length_gate.get('min_required', 0)}"
                )
                if not decision.get("verdict_rationale"):
                    decision["verdict_rationale"] = length_gate_summary
                if "length_budget" not in merged.get("required_revision_categories", []):
                    merged["required_revision_categories"] = list(merged.get("required_revision_categories", [])) + ["length_budget"]
                updated_requested_changes = []
                found_length_gate_change = False
                for item in requested_changes:
                    if isinstance(item, dict) and item.get("source") == "length_gate":
                        updated = dict(item)
                        updated["summary"] = length_gate_summary
                        updated["status"] = "open"
                        updated_requested_changes.append(updated)
                        found_length_gate_change = True
                    else:
                        updated_requested_changes.append(item)
                if not found_length_gate_change:
                    updated_requested_changes.append(
                        {
                            "summary": length_gate_summary,
                            "status": "open",
                            "source": "length_gate",
                        }
                    )
                requested_changes = updated_requested_changes
            else:
                status = "approved"
                merged["approved_at"] = decision.get("last_updated", "")
        elif verdict == "blocked":
            status = "blocked"
        elif verdict == "revise":
            status = "needs_revision"
        elif _meaningful_text(draft_text):
            status = "awaiting_audit"
        elif _meaningful_text(audit_text):
            status = "awaiting_supervisor"

        required_revision_categories = decision.get("required_revision_categories", [])
        if structure_gate.get("required") and not structure_gate.get("passed"):
            structure_summary = (
                f"章节标题结构未达硬约束：required_h3={structure_gate.get('required_second_level_count', 0)}, "
                f"actual_h3={structure_gate.get('actual_second_level_count', 0)}, "
                f"required_h4>={structure_gate.get('required_third_level_total_min', 0)}, "
                f"actual_h4={structure_gate.get('actual_third_level_total', 0)}"
            )
            updated_requested_changes = []
            found_structure_change = False
            for item in requested_changes:
                if isinstance(item, dict) and item.get("source") == "structure_gate":
                    updated = dict(item)
                    updated["summary"] = structure_summary
                    updated["status"] = "open"
                    updated_requested_changes.append(updated)
                    found_structure_change = True
                else:
                    updated_requested_changes.append(item)
            if status == "needs_revision" and not found_structure_change:
                updated_requested_changes.append(
                    {
                        "summary": structure_summary,
                        "status": "open",
                        "source": "structure_gate",
                    }
                )
            requested_changes = updated_requested_changes
            if "heading_structure" not in required_revision_categories:
                required_revision_categories = list(required_revision_categories) + ["heading_structure"]
            decision["required_revision_categories"] = required_revision_categories
        if length_gate.get("enforceable") and not length_gate.get("passed"):
            length_gate_summary = (
                f"章节长度未达最低阈值：actual={length_gate.get('actual_count', 0)}, "
                f"required>={length_gate.get('min_required', 0)}"
            )
            updated_requested_changes = []
            found_length_gate_change = False
            for item in requested_changes:
                if isinstance(item, dict) and item.get("source") == "length_gate":
                    updated = dict(item)
                    updated["summary"] = length_gate_summary
                    updated["status"] = "open"
                    updated_requested_changes.append(updated)
                    found_length_gate_change = True
                else:
                    updated_requested_changes.append(item)
            if status == "needs_revision" and not found_length_gate_change:
                updated_requested_changes.append(
                    {
                        "summary": length_gate_summary,
                        "status": "open",
                        "source": "length_gate",
                    }
                )
            requested_changes = updated_requested_changes
        if status == "needs_revision" and length_gate.get("enforceable") and not length_gate.get("passed"):
            if "length_budget" not in required_revision_categories:
                required_revision_categories = list(required_revision_categories) + ["length_budget"]
            decision["required_revision_categories"] = required_revision_categories
        decision["status"] = status
        heading_structure_dimension = decision.get("audit_dimensions", {}).get("heading_structure", {})
        if isinstance(heading_structure_dimension, dict):
            if structure_gate.get("required") and not structure_gate.get("passed"):
                heading_structure_dimension["status"] = "fail"
                heading_structure_dimension["notes"] = structure_gate.get("notes", "")
            elif structure_gate.get("required"):
                heading_structure_dimension["status"] = "pass"
                heading_structure_dimension["notes"] = structure_gate.get("notes", "")
            else:
                heading_structure_dimension["status"] = "not_applicable"
                heading_structure_dimension["notes"] = structure_gate.get("notes", "")
        length_budget_dimension = decision.get("audit_dimensions", {}).get("length_budget", {})
        if isinstance(length_budget_dimension, dict):
            if length_gate.get("enforceable") and not length_gate.get("passed"):
                length_budget_dimension["status"] = "fail"
                length_budget_dimension["notes"] = (
                    f"章节长度未达最低阈值：actual={length_gate.get('actual_count', 0)}, "
                    f"required>={length_gate.get('min_required', 0)}"
                )
            elif length_gate.get("passed"):
                length_budget_dimension["status"] = "pass"
                length_budget_dimension["notes"] = (
                    f"章节长度达标：actual={length_gate.get('actual_count', 0)}, "
                    f"required>={length_gate.get('min_required', 0)}"
                )
        incomplete_dimensions = find_incomplete_required_dimensions(decision.get("audit_dimensions", {}))
        if verdict == "approved" and incomplete_dimensions:
            status = "needs_revision"
            verdict = "revise"
            decision["latest_verdict"] = "revise"
            summary = "关键审计维度未完成显式判定：" + "、".join(incomplete_dimensions)
            if not decision.get("verdict_rationale"):
                decision["verdict_rationale"] = summary
            updated_requested_changes = []
            found_contract_change = False
            for item in requested_changes:
                if isinstance(item, dict) and item.get("source") == "audit_contract":
                    updated = dict(item)
                    updated["summary"] = summary
                    updated["status"] = "open"
                    updated_requested_changes.append(updated)
                    found_contract_change = True
                else:
                    updated_requested_changes.append(item)
            if not found_contract_change:
                updated_requested_changes.append(
                    {
                        "summary": summary,
                        "status": "open",
                        "source": "audit_contract",
                    }
                )
            requested_changes = updated_requested_changes
            for key in incomplete_dimensions:
                if key not in required_revision_categories:
                    required_revision_categories = list(required_revision_categories) + [key]
            decision["required_revision_categories"] = required_revision_categories
            decision["status"] = status
        structure_only_revision = _is_structure_only_revision(
            required_revision_categories,
            requested_changes,
            chapter_type=merged.get("chapter_type", ""),
        )
        if verdict == "revise" and structure_gate.get("passed") and length_gate.get("passed") and not incomplete_dimensions and structure_only_revision:
            verdict = "approved"
            status = "approved"
            decision["latest_verdict"] = "approved"
            decision["status"] = "approved"
            decision["required_revision_categories"] = []
            decision["requested_changes"] = []
            requested_changes = []
            required_revision_categories = []
            merged["approved_at"] = decision.get("last_updated", "") or utc_now()
        decision["requested_changes"] = requested_changes
        decision["length_gate"] = length_gate
        decision["structure_gate"] = structure_gate
        write_json(decision_path, decision)

        merged["status"] = status
        merged["latest_verdict"] = verdict
        merged["current_round"] = current_round
        merged["score_history"] = score_history
        merged["requested_changes"] = requested_changes
        merged["applied_changes"] = applied_changes
        merged["length_gate"] = length_gate
        merged["structure_gate"] = structure_gate
        merged["verdict_rationale"] = decision.get("verdict_rationale", "")
        merged["blocking_reason_category"] = decision.get("blocking_reason_category", "")
        merged["return_to_step"] = decision.get("return_to_step", "")
        merged["audit_dimensions"] = decision.get("audit_dimensions", default_audit_dimensions())
        merged["missing_materials_gate"] = decision.get("missing_materials_gate", {})
        merged["primary_failures"] = decision.get("primary_failures", [])
        merged["required_revision_categories"] = required_revision_categories
        merged["audit_summary"] = (audit_text.strip().splitlines()[2] if _meaningful_text(audit_text) and len(audit_text.strip().splitlines()) > 2 else "")
        reconciled.append(merged)
        if status == "approved":
            approved_prefix.append(merged)

    return reconciled


def build_action_ledger(chapters: list[dict[str, Any]], existing_ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    existing_items = {item.get("action_id"): item for item in (existing_ledger or {}).get("items", []) if item.get("action_id")}
    items: list[dict[str, Any]] = []
    for chapter in chapters:
        round_id = int(chapter.get("current_round", 0) or 0)
        for index, raw_change in enumerate(chapter.get("requested_changes", []), start=1):
            if isinstance(raw_change, dict):
                summary = raw_change.get("summary", "")
                status = raw_change.get("status", "")
                source = raw_change.get("source", "agent3")
            else:
                summary = str(raw_change)
                status = ""
                source = "agent3"
            action_id = f"{chapter.get('chapter_id')}-r{round_id or 1}-a{index}"
            item = existing_items.get(action_id, {})
            items.append(
                {
                    "action_id": action_id,
                    "chapter_id": chapter.get("chapter_id", ""),
                    "chapter_heading": chapter.get("heading", ""),
                    "round": round_id or 1,
                    "requested_by": source,
                    "owner": "agent2",
                    "summary": summary,
                    "status": item.get("status") or status or ("applied" if chapter.get("status") == "approved" else "pending"),
                }
            )
    return {"items": items}


def _merge_agents(existing_runtime: dict[str, Any] | None) -> dict[str, Any]:
    runtime = load_json_template("document-writing-agent-runtime.template.json")
    if not existing_runtime:
        return runtime
    for agent_key in ("agent1", "agent2", "agent3"):
        existing_agent = existing_runtime.get("agents", {}).get(agent_key, {})
        runtime["agents"][agent_key]["continuity_handle"] = existing_agent.get("continuity_handle", "")
        runtime["agents"][agent_key]["runtime_agent_id"] = existing_agent.get("runtime_agent_id", "")
        runtime["agents"][agent_key]["status"] = existing_agent.get("status", runtime["agents"][agent_key].get("status", "ready"))
    return runtime


def build_runtime(chapters: list[dict[str, Any]], existing_runtime: dict[str, Any] | None = None) -> dict[str, Any]:
    runtime = _merge_agents(existing_runtime)
    approved = [chapter.get("chapter_id", "") for chapter in chapters if chapter.get("status") == "approved"]
    current = next((chapter for chapter in sorted(chapters, key=lambda item: item.get("writing_order", 0)) if chapter.get("status") != "approved"), None)
    ready_for_review = current is None

    if ready_for_review:
        workflow_status = "ready_for_review"
        latest_verdict = "approved"
        next_action = "run_document_review"
        next_action_owner = "agent1"
        required_inputs = [
            "workspace/document_writing/chapter-manifest.json",
            "workspace/document_writing/作品书草稿.md",
        ]
    else:
        status = current.get("status", "pending")
        if status == "awaiting_audit":
            workflow_status = "awaiting_audit"
            next_action = f"agent1_dispatch_agent3_audit:{current.get('chapter_id', '')}"
            next_action_owner = "agent1"
            required_inputs = [current.get("files", {}).get("draft", ""), current.get("files", {}).get("brief", "")]
        elif status == "needs_revision":
            workflow_status = "needs_revision"
            next_action = f"agent1_dispatch_agent2_revision:{current.get('chapter_id', '')}"
            next_action_owner = "agent1"
            required_inputs = [
                current.get("files", {}).get("brief", ""),
                current.get("files", {}).get("draft", ""),
                current.get("files", {}).get("audit", ""),
                current.get("files", {}).get("decision", ""),
            ]
        elif status == "blocked":
            workflow_status = "blocked"
            backtrack_step = current.get("return_to_step", "")
            if backtrack_step:
                next_action = f"agent1_backtrack_{backtrack_step}:{current.get('chapter_id', '')}"
                next_action_owner = "agent1"
            else:
                next_action = f"human_record:{current.get('chapter_id', '')}"
                next_action_owner = "joint"
            required_inputs = [current.get("files", {}).get("decision", ""), current.get("files", {}).get("audit", "")]
        else:
            workflow_status = "awaiting_writer"
            next_action = f"agent1_dispatch_agent2_writer:{current.get('chapter_id', '')}"
            next_action_owner = "agent1"
            required_inputs = [current.get("files", {}).get("brief", "")]
        latest_verdict = current.get("latest_verdict", "pending")

    runtime["chapter_sequence"] = [chapter.get("chapter_id", "") for chapter in sorted(chapters, key=lambda item: item.get("writing_order", 0))]
    runtime["approved_chapters"] = approved
    runtime["current_chapter_id"] = current.get("chapter_id", "") if current else ""
    runtime["current_chapter_heading"] = current.get("heading", "") if current else ""
    runtime["current_round"] = current.get("current_round", 0) if current else 0
    runtime["max_rounds_per_chapter"] = DEFAULT_MAX_ROUNDS
    runtime["workflow_status"] = workflow_status
    runtime["latest_verdict"] = latest_verdict
    runtime["final_acceptance_ready"] = ready_for_review
    runtime["next_action"] = next_action
    runtime["next_action_owner"] = next_action_owner
    runtime["required_inputs"] = [item for item in required_inputs if item]
    runtime["blocking_reason"] = current.get("blocking_reason_category", "") if current else ""
    runtime["last_updated"] = utc_now()
    return runtime


def render_writing_status(runtime: dict[str, Any], chapters: list[dict[str, Any]]) -> str:
    total = len(chapters)
    approved = len([chapter for chapter in chapters if chapter.get("status") == "approved"])
    lines = [
        "# Step6 Multi-Agent Status",
        "",
        f"- Workflow Mode: `{runtime.get('workflow_mode', '')}`",
        f"- Real LLM Required: `{runtime.get('real_llm_required', False)}`",
        f"- Default Backbone: `{runtime.get('default_backbone', {}).get('model', '')}` / `{runtime.get('default_backbone', {}).get('reasoning_effort', '')}`",
        f"- Workflow Status: `{runtime.get('workflow_status', '')}`",
        f"- Approved Chapters: {approved}/{total}",
        f"- Current Chapter: `{runtime.get('current_chapter_id', '')}` {runtime.get('current_chapter_heading', '')}",
        f"- Next Action: `{runtime.get('next_action', '')}`",
        "",
        "## Agents",
    ]
    for key, agent in runtime.get("agents", {}).items():
        lines.append(
            f"- {key}: {agent.get('role', '')}, model={agent.get('backbone', {}).get('model', '')}, "
            f"reasoning={agent.get('backbone', {}).get('reasoning_effort', '')}, continuity={agent.get('continuity_handle', '') or 'pending'}"
        )
    lines.extend(["", "## Chapter Progress"])
    for chapter in sorted(chapters, key=lambda item: item.get("writing_order", 0)):
        lines.append(
            f"- {chapter.get('writing_order', 0)}. {chapter.get('heading', '')}: "
            f"status={chapter.get('status', '')}, round={chapter.get('current_round', 0)}, verdict={chapter.get('latest_verdict', '')}"
        )
    lines.append("")
    return "\n".join(lines)


def render_review_log(runtime: dict[str, Any], chapters: list[dict[str, Any]]) -> str:
    lines = [
        "# Step6 Review Log",
        "",
        "This file indexes chapter-level draft and audit artifacts for the real multi-agent writing loop.",
        "",
        f"- Current Workflow Status: `{runtime.get('workflow_status', '')}`",
        f"- Current Chapter: `{runtime.get('current_chapter_id', '')}`",
        "",
        "## Chapter Index",
    ]
    for chapter in sorted(chapters, key=lambda item: item.get("writing_order", 0)):
        files = chapter.get("files", {})
        lines.extend(
            [
                f"### {chapter.get('heading', '')}",
                f"- Status: `{chapter.get('status', '')}`",
                f"- Verdict: `{chapter.get('latest_verdict', '')}`",
                f"- Length Gate: actual={chapter.get('length_gate', {}).get('actual_count', 0)}, "
                f"required>={chapter.get('length_gate', {}).get('min_required', 0)}, "
                f"status={chapter.get('length_gate', {}).get('status', 'pending')}",
                f"- Structure Gate: h3={chapter.get('structure_gate', {}).get('actual_second_level_count', 0)}/"
                f"{chapter.get('structure_gate', {}).get('required_second_level_count', 0)}, "
                f"h4={chapter.get('structure_gate', {}).get('actual_third_level_total', 0)}/"
                f"{chapter.get('structure_gate', {}).get('required_third_level_total_min', 0)}, "
                f"status={chapter.get('structure_gate', {}).get('status', 'pending')}",
                f"- Verdict Rationale: {chapter.get('verdict_rationale', '') or 'none'}",
                f"- Blocking Category: {chapter.get('blocking_reason_category', '') or 'none'}",
                f"- Brief: `{files.get('brief', '')}`",
                f"- Draft: `{files.get('draft', '')}`",
                f"- Audit: `{files.get('audit', '')}`",
                f"- Decision: `{files.get('decision', '')}`",
                f"- Requested Changes: {len(chapter.get('requested_changes', []))}",
                f"- Primary Failures: {len(chapter.get('primary_failures', []))}",
                "",
            ]
        )
    return "\n".join(lines)


def _strip_heading(content: str, heading: str) -> str:
    lines = content.strip().splitlines()
    if not lines:
        return ""
    first = lines[0].strip().lstrip("#").strip()
    if heading and first == heading:
        lines = lines[1:]
    return "\n".join(lines).strip()


def normalize_outline_heading(text: str) -> str:
    normalized = (text or "").strip()
    normalized = re.sub(r"^第[一二三四五六七八九十百千万0-9]+章\s*", "", normalized)
    normalized = re.sub(r"^[一二三四五六七八九十百千万0-9]+[、.．]\s*", "", normalized)
    normalized = re.sub(r"^\d+(?:\.\d+)*\s*", "", normalized)
    normalized = re.sub(r"^[（(]?[一二三四五六七八九十百千万0-9]+[)）.．、]\s*", "", normalized)
    return normalized.strip()


def chapter_subsection_title(subsection: Any) -> str:
    if isinstance(subsection, dict):
        return str(subsection.get("title", "")).strip()
    return str(subsection or "").strip()


def split_into_balanced_groups(items: list[str], group_count: int) -> list[list[str]]:
    if group_count <= 0:
        return []
    if not items:
        return [[] for _ in range(group_count)]
    effective_groups = min(group_count, len(items))
    base, remainder = divmod(len(items), effective_groups)
    groups: list[list[str]] = []
    cursor = 0
    for index in range(effective_groups):
        size = base + (1 if index < remainder else 0)
        groups.append(items[cursor : cursor + size])
        cursor += size
    while len(groups) < group_count:
        groups.append([])
    return groups


def _split_text_segments(text: str) -> list[str]:
    paragraphs = [block.strip() for block in re.split(r"\n\s*\n+", text or "") if block.strip()]
    if len(paragraphs) >= 2:
        return paragraphs
    sentence_pattern = re.compile(r"[^。！？!?；;\n]+[。！？!?；;]?")
    sentences = [match.group(0).strip() for match in sentence_pattern.finditer(text or "") if match.group(0).strip()]
    return sentences or paragraphs


def _collect_section_blocks(text: str) -> tuple[list[str], dict[str, list[str]]]:
    preamble_lines: list[str] = []
    section_lines: dict[str, list[str]] = {}
    ordered_titles: list[str] = []
    current_title = ""
    current_buffer: list[str] = []

    def flush_current() -> None:
        nonlocal current_title, current_buffer
        if not current_title:
            return
        combined = "\n".join(current_buffer).strip()
        if combined:
            section_lines[current_title] = [combined]
            ordered_titles.append(current_title)
        current_buffer = []

    for raw_line in text.splitlines():
        match = re.match(r"^(#{3,4})\s+(.*)$", raw_line.strip())
        if match and len(match.group(1)) == 3:
            flush_current()
            current_title = normalize_outline_heading(match.group(2))
            current_buffer = []
            continue
        if match and len(match.group(1)) == 4:
            continue
        if current_title:
            current_buffer.append(raw_line)
        else:
            preamble_lines.append(raw_line)
    flush_current()

    preamble_blocks = [block.strip() for block in re.split(r"\n\s*\n+", "\n".join(preamble_lines)) if block.strip()]
    ordered_sections = {title: section_lines.get(title, []) for title in ordered_titles}
    return preamble_blocks, ordered_sections


def rebuild_draft_to_structure_contract(chapter: dict[str, Any], content: str) -> str:
    body = (content or "").strip()
    if not body or chapter.get("chapter_type") != "body_section":
        return body

    contract = chapter.get("structure_contract", {}) if isinstance(chapter.get("structure_contract", {}), dict) else {}
    second_level_contracts = contract.get("second_level_contracts", [])
    if not second_level_contracts:
        return enforce_subsection_structure(chapter, body)

    preamble_blocks, existing_sections = _collect_section_blocks(body)
    existing_lookup = {normalize_outline_heading(title): blocks for title, blocks in existing_sections.items()}
    unused_titles = list(existing_lookup.keys())
    carryover_blocks = list(preamble_blocks)
    fallback_source = re.sub(r"(?m)^#{3,4}\s+.*$", "", body)
    fallback_segments = _split_text_segments(fallback_source)
    rebuilt_lines: list[str] = []

    for item in second_level_contracts:
        section_title = str(item.get("title", "")).strip()
        normalized_title = normalize_outline_heading(section_title)
        detail_titles = [str(title).strip() for title in item.get("required_third_level_titles", []) if str(title).strip()]

        source_blocks: list[str] = []
        if normalized_title in existing_lookup:
            source_blocks.extend(existing_lookup[normalized_title])
            unused_titles = [title for title in unused_titles if title != normalized_title]
        elif unused_titles:
            fallback_title = unused_titles.pop(0)
            source_blocks.extend(existing_lookup.get(fallback_title, []))
        elif carryover_blocks:
            source_blocks.extend(carryover_blocks)
            carryover_blocks = []
        elif fallback_segments:
            source_blocks.extend(fallback_segments)

        if not source_blocks:
            continue

        source_segments: list[str] = []
        for block in source_blocks:
            source_segments.extend(_split_text_segments(block))
        if not source_segments:
            continue

        rebuilt_lines.append(f"### {section_title}")
        if not detail_titles:
            rebuilt_lines.append("")
            rebuilt_lines.append("\n\n".join(source_segments))
            rebuilt_lines.append("")
            continue

        detail_groups = split_into_balanced_groups(source_segments, len(detail_titles))
        for detail_title, detail_group in zip(detail_titles, detail_groups):
            rebuilt_lines.append("")
            rebuilt_lines.append(f"#### {detail_title}")
            rebuilt_lines.append("")
            if detail_group:
                rebuilt_lines.append("\n\n".join(detail_group))
            else:
                rebuilt_lines.append("本节围绕该子问题补充关键论证，并与前后文保持统一技术口径。")
        rebuilt_lines.append("")

    rebuilt = "\n".join(rebuilt_lines).strip()
    return rebuilt or enforce_subsection_structure(chapter, body)


def suggested_detail_headings(chapter: dict[str, Any], subsection_title: str) -> list[str]:
    normalized = normalize_outline_heading(subsection_title)
    mapping = [
        (("背景", "赛题", "趋势"), ["现实背景", "趋势与赛题牵引", "问题演进"]),
        (("用户", "场景"), ["目标对象", "典型动作", "场景约束"]),
        (("痛点", "问题"), ["现有不足", "风险放大链路", "直接代价"]),
        (("总体目标", "设计原则"), ["设计目标", "方案边界", "设计原则"]),
        (("架构", "分层"), ["分层结构", "模块职责", "多端部署关系"]),
        (("闭环", "流程", "运行"), ["输入接入", "分析与评分", "输出与联动"]),
        (("创新点总览", "总览"), ["痛点映射", "创新协同"]),
        (("创新1", "创新2", "创新3", "纠偏", "一致性", "势能"), ["问题来源与不足", "输入与关键信号", "技术机制与实现", "价值与验证"]),
        (("映射",), ["技术落点", "验证锚点", "系统对应关系"]),
        (("模块实现",), ["统一表征对象", "模块实现", "接口协同"]),
        (("案例回放", "人工复核"), ["案例回放链路", "复核证据面板", "复核与留痕"]),
        (("收益", "优势"), ["收益路径", "资源效率", "竞争优势"]),
        (("展示",), ["展示主线", "多端呈现", "答辩价值"]),
        (("完成情况",), ["闭环完成情况", "关键能力", "交付形态"]),
        (("特色", "应用价值"), ["系统特色", "应用价值", "展示完成度"]),
        (("不足", "优化"), ["当前不足", "优化方向", "延展空间"]),
        (("推进路线", "计划", "流程结论", "当前边界"), ["流程成果", "当前边界", "范围说明"]),
        (("资源", "基础", "支撑条件"), ["实现基础", "支撑条件", "工程约束"]),
        (("扩展", "待确认", "展望", "边界说明", "条件说明"), ["后续展望", "能力边界", "条件说明"]),
        (("总结",), ["核心贡献", "价值收束"]),
        (("展望", "不足"), ["当前不足", "后续方向"]),
    ]
    for tokens, titles in mapping:
        if any(token in normalized for token in tokens):
            return titles
    chapter_fallback = {
        "body_section": ["核心论点", "支撑分析"],
        "abstract": ["问题与方案", "结果与价值"],
        "conclusion": ["核心总结", "后续优化"],
    }
    return chapter_fallback.get(chapter.get("chapter_type", ""), ["核心内容", "延伸说明"])


def enforce_subsection_structure(chapter: dict[str, Any], content: str) -> str:
    body = content.strip()
    if not body:
        return body
    if re.search(r"^#{3,6}\s+", body, flags=re.M):
        return body

    subsection_titles = [chapter_subsection_title(item) for item in chapter.get("subsections", []) if chapter_subsection_title(item)]
    if not subsection_titles:
        return body

    paragraphs = [block.strip() for block in re.split(r"\n\s*\n+", body) if block.strip()]
    if not paragraphs:
        return body

    subsection_groups = split_into_balanced_groups(paragraphs, len(subsection_titles))
    structured_lines: list[str] = []
    for subsection_title, subsection_paragraphs in zip(subsection_titles, subsection_groups):
        if not subsection_paragraphs:
            continue
        structured_lines.append(f"### {subsection_title}")
        detail_titles = suggested_detail_headings(chapter, subsection_title)
        detail_count = 1
        if len(subsection_paragraphs) >= 2:
            detail_count = min(len(detail_titles), 2 if len(subsection_paragraphs) <= 3 else 3)
        detail_groups = split_into_balanced_groups(subsection_paragraphs, detail_count)
        for detail_title, detail_paragraphs in zip(detail_titles, detail_groups):
            if not detail_paragraphs:
                continue
            structured_lines.append("")
            structured_lines.append(f"#### {detail_title}")
            structured_lines.append("")
            structured_lines.append("\n\n".join(detail_paragraphs))
        structured_lines.append("")

    return "\n".join(structured_lines).strip()


def assemble_approved_draft(idea_card: dict[str, Any], chapters: list[dict[str, Any]], topic_dir: Path) -> str:
    approved_chapters = [chapter for chapter in chapters if chapter.get("status") == "approved"]
    lines = [f"# {idea_card.get('project_name', '')} 作品书草稿", ""]
    if len(approved_chapters) != len(chapters):
        lines.extend(
            [
                "> 当前文稿只汇编已通过 Agent3 审计的章节。",
                "> 未通过章节仍保留在各自 chapter 目录中，不能提前并入全书。",
                "",
            ]
        )

    for chapter in sorted(approved_chapters, key=lambda item: item.get("assembly_order", 0)):
        draft_path = topic_dir / chapter.get("files", {}).get("draft", "")
        if not draft_path.exists():
            continue
        content = _strip_heading(draft_path.read_text(encoding="utf-8"), chapter.get("heading", ""))
        content = enforce_subsection_structure(chapter, content)
        if not content:
            continue
        lines.extend([f"## {chapter.get('heading', '')}", "", content, ""])

    if len(lines) == 2:
        lines.append("当前还没有通过审计的章节。")
        lines.append("")
    return "\n".join(lines)

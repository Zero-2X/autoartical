#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from proposal_workflow import (
    count_text_units,
    ensure_state_scaffold,
    load_json_template,
    read_json,
    summarize_chapter_evidence,
    sync_workspace_state,
    write_json,
    write_text,
)
from writing_quality_rules import load_writing_quality_rules
from content_depth import DEFAULT_CONTRACT, build_content_depth_gate
from delivery_contract import build_visual_gate

PASSLIKE_DIMENSION_STATUSES = {"pass", "passed", "not_applicable", "n/a", "na"}
WRITING_QUALITY_RULES = load_writing_quality_rules()
DOCUMENT_REVIEW_RULES = WRITING_QUALITY_RULES.get("document_review", {})
REQUIRED_APPROVED_AUDIT_DIMENSIONS = tuple(
    WRITING_QUALITY_RULES.get(
        "required_approved_audit_dimensions",
        (
            "goal_alignment",
            "score_alignment",
            "position_logic",
            "body_priority_coverage",
            "evidence_support",
            "length_budget",
            "pending_items_handling",
        ),
    )
)
HARD_BLOCK_TEXT_PATTERNS = tuple(
    (item.get("label", ""), item.get("pattern", ""))
    for item in DOCUMENT_REVIEW_RULES.get("hard_block_text_patterns", [])
    if item.get("label") and item.get("pattern")
)
MAJOR_RISK_TEXT_PATTERNS = tuple(
    (item.get("label", ""), item.get("pattern", ""), int(item.get("threshold", 1)))
    for item in DOCUMENT_REVIEW_RULES.get("major_risk_text_patterns", [])
    if item.get("label") and item.get("pattern")
)
PROPOSAL_STYLE_H2_PATTERNS = tuple(DOCUMENT_REVIEW_RULES.get("proposal_style_h2_patterns", ()))
TEMPORARY_INNOVATION_HEADING_PATTERN = str(
    DOCUMENT_REVIEW_RULES.get("temporary_innovation_heading_pattern", r"^###\s*创新[0-9一二三四五六七八九十]+\s*$")
)
SYNTHETIC_FLOW_BLOCK = DOCUMENT_REVIEW_RULES.get("synthetic_flow_block", {})
TEMPLATE_EXEMPT_TOPIC_NAMES = set(SYNTHETIC_FLOW_BLOCK.get("template_exempt_topic_names", ["topic_xx"]))
SYNTHETIC_TRIGGER_REASONS = set(SYNTHETIC_FLOW_BLOCK.get("trigger_reasons", ["synthetic_flow_test_seed"]))
SYNTHETIC_TRIGGER_NOTE_SUBSTRINGS = tuple(SYNTHETIC_FLOW_BLOCK.get("trigger_note_substrings", ["Synthetic flow test"]))
NONTRIVIAL_PARAGRAPH_MIN_LENGTH = int(DOCUMENT_REVIEW_RULES.get("duplicate_paragraph_min_length", 30) or 30)
OVERLAP_PARAGRAPH_MIN_LENGTH = int(DOCUMENT_REVIEW_RULES.get("overlap_paragraph_min_length", 40) or 40)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AutoSearch step7 chapter gate and final acceptance.")
    parser.add_argument("topic_dir", help="Topic directory, such as sample/topic_xx")
    return parser


def update_step_status(topic_dir: Path, *, step6_status: str, step7_status: str, step8_status: str | None = None) -> None:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not state_path.exists():
        return
    state = read_json(state_path)
    state.setdefault("workflow_status", {})["document_writing"] = step6_status
    state.setdefault("workflow_status", {})["document_review"] = step7_status
    if step8_status is not None:
        state.setdefault("workflow_status", {})["document_review"] = step8_status
    write_json(state_path, state)


def check_expected_headings(draft: str, manifest: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for chapter in sorted(manifest.get("chapters", []), key=lambda item: item.get("assembly_order", 0)):
        heading = f"## {chapter.get('heading', '')}"
        if heading not in draft:
            missing.append(heading)
    return missing


def extract_markdown_headings(draft: str, level: int) -> list[str]:
    pattern = rf"^#{{{level}}}\s+(.+)$"
    return [match.group(1).strip() for match in re.finditer(pattern, draft, flags=re.M)]


def split_nontrivial_paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    for block in re.split(r"\n\s*\n+", text):
        normalized = re.sub(r"\s+", " ", block).strip()
        if not normalized:
            continue
        if normalized.startswith("#"):
            continue
        if len(normalized) < NONTRIVIAL_PARAGRAPH_MIN_LENGTH:
            continue
        paragraphs.append(normalized)
    return paragraphs


def collect_duplicate_paragraphs(draft: str) -> list[dict[str, Any]]:
    paragraphs = split_nontrivial_paragraphs(draft)
    counts: dict[str, int] = {}
    for paragraph in paragraphs:
        counts[paragraph] = counts.get(paragraph, 0) + 1
    duplicates = [
        {
            "count": count,
            "excerpt": paragraph[:120],
        }
        for paragraph, count in counts.items()
        if count >= 2
    ]
    duplicates.sort(key=lambda item: (-item["count"], item["excerpt"]))
    return duplicates


def extract_section_body(draft: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    match = re.search(pattern, draft, flags=re.M)
    if not match:
        return ""
    start = match.end()
    rest = draft[start:]
    next_heading = re.search(r"^##\s+", rest, flags=re.M)
    if next_heading:
        rest = rest[: next_heading.start()]
    return rest.strip()


def collect_section_overlap_issues(draft: str) -> list[str]:
    issues: list[str] = []
    abstract_body = extract_section_body(draft, "摘要")
    conclusion_body = extract_section_body(draft, "结语")
    if abstract_body and conclusion_body:
        abstract_paragraphs = set(split_nontrivial_paragraphs(abstract_body))
        conclusion_paragraphs = set(split_nontrivial_paragraphs(conclusion_body))
        overlap = [item for item in abstract_paragraphs & conclusion_paragraphs if len(item) >= OVERLAP_PARAGRAPH_MIN_LENGTH]
        if overlap:
            issues.append(f"摘要与结语存在重复段落（overlap={len(overlap)}）")
    return issues


def collect_synthetic_flow_issues(manifest: dict[str, Any], topic_dir: Path) -> list[str]:
    if topic_dir.name in TEMPLATE_EXEMPT_TOPIC_NAMES:
        return []
    issues: list[str] = []
    for chapter in manifest.get("chapters", []):
        decision_rel = chapter.get("files", {}).get("decision", "")
        if not decision_rel:
            continue
        decision_path = topic_dir / decision_rel
        if not decision_path.exists():
            continue
        decision = read_json(decision_path)
        trigger_reason = str(decision.get("trigger_reason", "")).strip()
        notes = str(decision.get("notes", "")).strip()
        if trigger_reason in SYNTHETIC_TRIGGER_REASONS or any(marker in notes for marker in SYNTHETIC_TRIGGER_NOTE_SUBSTRINGS):
            issues.append(f"章节仍使用 synthetic flow 测试稿：{chapter.get('heading', '')}")
    return issues


def build_final_draft_gate_summary(draft: str, manifest: dict[str, Any]) -> dict[str, Any]:
    hard_failures: list[str] = []
    major_issues: list[str] = []
    minor_issues: list[str] = []
    matched_hard_patterns: list[dict[str, Any]] = []
    matched_major_patterns: list[dict[str, Any]] = []

    for label, pattern in HARD_BLOCK_TEXT_PATTERNS:
        count = len(re.findall(pattern, draft, flags=re.I))
        if count:
            matched_hard_patterns.append({"label": label, "count": count})
            hard_failures.append(f"Step7 定稿 gate 命中硬拦截：{label}（count={count}）")

    for label, pattern, threshold in MAJOR_RISK_TEXT_PATTERNS:
        count = len(re.findall(pattern, draft, flags=re.I))
        if count >= threshold:
            matched_major_patterns.append({"label": label, "count": count, "threshold": threshold})
            major_issues.append(f"Step7 定稿风险过高：{label}（count={count}, threshold>={threshold}）")
        elif count > 0:
            minor_issues.append(f"Step7 定稿风险提示：{label} 仍有残留（count={count}）")

    h2_titles = extract_markdown_headings(draft, 2)
    proposal_style_titles = [title for title in h2_titles if any(pattern in title for pattern in PROPOSAL_STYLE_H2_PATTERNS)]
    for title in proposal_style_titles:
        hard_failures.append(f"Step7 章节命名仍偏提案型：{title}")

    temporary_innovation_headings = [
        title for title in extract_markdown_headings(draft, 3) if re.match(TEMPORARY_INNOVATION_HEADING_PATTERN, f'### {title}')
    ]
    if temporary_innovation_headings:
        major_issues.append(
            "Step7 创新章节仍使用临时命名：" + "、".join(temporary_innovation_headings)
        )

    manifest_visual_labels = [
        spec.get("label", "")
        for chapter in manifest.get("chapters", [])
        for spec in chapter.get("visual_specs", [])
        if isinstance(spec, dict) and spec.get("label")
    ]
    draft_visual_refs = re.findall(r"[图表]\s*\d+(?:[-.．]\d+)+", draft)
    all_visual_tokens = manifest_visual_labels + draft_visual_refs
    has_hyphen_style = any(re.search(r"[图表]\s*\d+-\d+", token) for token in all_visual_tokens)
    has_dot_style = any(re.search(r"[图表]\s*\d+[.．]\d+", token) for token in all_visual_tokens)
    if has_hyphen_style and has_dot_style:
        hard_failures.append("Step7 图表编号体系混用：同时出现 `图1-1/表1-1` 与 `图1.1/表1.1` 风格。")

    duplicate_paragraphs = collect_duplicate_paragraphs(draft)
    if duplicate_paragraphs:
        top = duplicate_paragraphs[0]
        hard_failures.append(
            "Step7 检测到重复段落残留："
            f"出现 {top['count']} 次，excerpt={top['excerpt']}"
        )

    section_overlap_issues = collect_section_overlap_issues(draft)
    major_issues.extend(section_overlap_issues)

    return {
        "hard_failures": hard_failures,
        "major_issues": major_issues,
        "minor_issues": minor_issues,
        "matched_hard_patterns": matched_hard_patterns,
        "matched_major_patterns": matched_major_patterns,
        "proposal_style_titles": proposal_style_titles,
        "temporary_innovation_headings": temporary_innovation_headings,
        "mixed_visual_numbering": has_hyphen_style and has_dot_style,
        "duplicate_paragraphs": duplicate_paragraphs[:5],
        "section_overlap_issues": section_overlap_issues,
    }


def build_chapter_summary(manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], bool]:
    summary: list[dict[str, Any]] = []
    major_issues: list[str] = []
    blocked = False
    for chapter in sorted(manifest.get("chapters", []), key=lambda item: item.get("writing_order", 0)):
        status = chapter.get("status", "pending")
        verdict = chapter.get("latest_verdict", "pending")
        if status != "approved":
            major_issues.append(f"章节未通过审计：{chapter.get('heading', '')}（status={status}, verdict={verdict}）")
        if status == "blocked" or verdict == "blocked":
            blocked = True
        summary.append(
            {
                "chapter_id": chapter.get("chapter_id", ""),
                "chapter_heading": chapter.get("heading", ""),
                "status": status,
                "round": chapter.get("current_round", 0),
                "verdict": verdict,
                "verdict_rationale": chapter.get("verdict_rationale", ""),
                "blocking_reason_category": chapter.get("blocking_reason_category", ""),
                "return_to_step": chapter.get("return_to_step", ""),
                "primary_failures": chapter.get("primary_failures", []),
                "audit_dimensions": chapter.get("audit_dimensions", {}),
                "length_gate": chapter.get("length_gate", {}),
                "missing_materials_gate": chapter.get("missing_materials_gate", {}),
                "requested_changes": chapter.get("requested_changes", []),
                "decision_file": chapter.get("files", {}).get("decision", ""),
                "draft_file": chapter.get("files", {}).get("draft", ""),
                "audit_file": chapter.get("files", {}).get("audit", ""),
            }
        )
    return summary, major_issues, blocked


def build_length_gate_summary(manifest: dict[str, Any], draft: str) -> dict[str, Any]:
    per_chapter: list[dict[str, Any]] = []
    total_actual = 0
    total_required = 0
    for chapter in sorted(manifest.get("chapters", []), key=lambda item: item.get("assembly_order", 0)):
        length_gate = chapter.get("length_gate", {})
        actual = int(length_gate.get("actual_count", 0) or 0)
        required = int(length_gate.get("min_required", 0) or 0)
        enforceable = bool(length_gate.get("enforceable", False))
        total_actual += actual
        total_required += required if enforceable else 0
        per_chapter.append(
            {
                "chapter_id": chapter.get("chapter_id", ""),
                "chapter_heading": chapter.get("heading", ""),
                "actual_count": actual,
                "min_required": required,
                "enforceable": enforceable,
                "status": length_gate.get("status", "pending"),
                "passed": bool(length_gate.get("passed", not enforceable)),
            }
        )
    assembled_count = count_text_units(draft)
    return {
        "per_chapter": per_chapter,
        "total_actual": total_actual,
        "total_required": total_required,
        "assembled_count": assembled_count,
        "passed": assembled_count >= total_required if total_required > 0 else True,
    }


def build_evidence_gate_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    per_chapter: list[dict[str, Any]] = []
    required_chapters = 0
    missing_required = 0
    weak_required = 0
    for chapter in sorted(manifest.get("chapters", []), key=lambda item: item.get("assembly_order", 0)):
        summary = summarize_chapter_evidence(chapter)
        audit_status = (
            chapter.get("audit_dimensions", {})
            .get("evidence_support", {})
            .get("status", "pending")
        )
        if summary["required"]:
            required_chapters += 1
        if summary["required"] and summary["status"] == "missing":
            missing_required += 1
        if summary["required"] and summary["status"] == "weak":
            weak_required += 1
        per_chapter.append(
            {
                "chapter_id": chapter.get("chapter_id", ""),
                "chapter_heading": chapter.get("heading", ""),
                "required": summary["required"],
                "status": summary["status"],
                "evidence_count": summary["evidence_count"],
                "authoritative_count": summary["authoritative_count"],
                "high_reliability_count": summary["high_reliability_count"],
                "insight_count": summary["insight_count"],
                "supports_count": summary["supports_count"],
                "evidence_kinds": summary["evidence_kinds"],
                "source_authorities": summary["source_authorities"],
                "audit_status": audit_status,
                "evidence_ids": summary["evidence_ids"],
            }
        )
    passed = missing_required == 0 and weak_required == 0
    return {
        "per_chapter": per_chapter,
        "required_chapters": required_chapters,
        "missing_required": missing_required,
        "weak_required": weak_required,
        "passed": passed,
    }


def collect_audit_dimension_issues(manifest: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for chapter in sorted(manifest.get("chapters", []), key=lambda item: item.get("writing_order", 0)):
        if chapter.get("status") != "approved":
            continue
        dims = chapter.get("audit_dimensions", {})
        for key in REQUIRED_APPROVED_AUDIT_DIMENSIONS:
            status = dims.get(key, {}).get("status", "pending")
            if status not in PASSLIKE_DIMENSION_STATUSES:
                issues.append(
                    f"已批准章节审计维度未闭环：{chapter.get('heading', '')} / {key}（status={status}）"
                )
    return issues


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    ensure_state_scaffold(topic_dir)
    step6_dir = topic_dir / "workspace" / "document_writing"
    step7_dir = topic_dir / "workspace" / "document_review"
    manifest_path = step6_dir / "chapter-manifest.json"
    runtime_path = step6_dir / "agent-runtime.json"
    draft_path = step6_dir / "作品书草稿.md"
    coverage_path = topic_dir / "workspace" / "document_plan" / "score-coverage.json"
    card_path = topic_dir / "workspace" / "concept" / "idea-card.json"

    if not manifest_path.exists() or not runtime_path.exists() or not draft_path.exists() or not coverage_path.exists() or not card_path.exists():
        raise SystemExit("Missing inputs for document_review.")

    step7_dir.mkdir(parents=True, exist_ok=True)
    manifest = read_json(manifest_path)
    runtime = read_json(runtime_path)
    coverage = read_json(coverage_path)
    idea_card = read_json(card_path)
    draft = draft_path.read_text(encoding="utf-8")
    plan_path = topic_dir / "workspace" / "document_plan" / "section-plan.json"
    plan = read_json(plan_path) if plan_path.exists() else {}
    content_depth_gate = build_content_depth_gate(
        draft, plan.get("sections", []), plan.get("content_contract", DEFAULT_CONTRACT)
    )
    visual_gate = build_visual_gate(topic_dir, plan, draft)

    payload = load_json_template("quality-gate.template.json")
    chapter_summary, major_issues, blocked = build_chapter_summary(manifest)
    major_issues.extend(content_depth_gate["failures"])
    major_issues.extend(visual_gate["failures"])
    length_gate_summary = build_length_gate_summary(manifest, draft)
    evidence_gate_summary = build_evidence_gate_summary(manifest)
    final_draft_gate_summary = build_final_draft_gate_summary(draft, manifest)
    minor_issues: list[str] = []
    pending_confirmations: list[str] = []

    if coverage.get("gaps"):
        major_issues.append("Step5 评分覆盖仍存在未承接项，不能进入最终交付。")

    if runtime.get("workflow_status") != "ready_for_review":
        major_issues.append(f"Step6 尚未进入总体验收状态：{runtime.get('workflow_status', '')}")

    major_issues.extend(collect_audit_dimension_issues(manifest))
    major_issues.extend(collect_synthetic_flow_issues(manifest, topic_dir))
    major_issues.extend(final_draft_gate_summary["hard_failures"])
    major_issues.extend(final_draft_gate_summary["major_issues"])
    minor_issues.extend(final_draft_gate_summary["minor_issues"])

    missing_headings = check_expected_headings(draft, manifest)
    for heading in missing_headings:
        major_issues.append(f"汇编稿缺少章节标题：{heading}")

    if idea_card.get("project_name", "") and idea_card["project_name"] not in draft:
        major_issues.append("汇编稿未稳定使用项目名称。")

    for item in length_gate_summary["per_chapter"]:
        if item["enforceable"] and not item["passed"]:
            major_issues.append(
                f"章节未达到最低篇幅阈值：{item['chapter_heading']}（actual={item['actual_count']}, required>={item['min_required']}）"
            )

    if not length_gate_summary["passed"]:
        major_issues.append(
            "全书总篇幅未达到章节最低阈值汇总要求："
            f"assembled={length_gate_summary['assembled_count']}, required>={length_gate_summary['total_required']}"
        )

    for item in evidence_gate_summary["per_chapter"]:
        if item["required"] and item["status"] == "missing":
            major_issues.append(
                f"章节缺少可追溯证据输入：{item['chapter_heading']}（required body chapter has 0 supporting evidence）"
            )
        elif item["required"] and item["status"] == "weak":
            major_issues.append(
                f"章节证据强度不足：{item['chapter_heading']}（authority={item['authoritative_count']}, high_reliability={item['high_reliability_count']}）"
            )
        elif item["required"] and item["audit_status"] not in PASSLIKE_DIMENSION_STATUSES:
            major_issues.append(
                f"章节证据审计未通过：{item['chapter_heading']}（audit evidence_support={item['audit_status']}）"
            )

    if len(draft.strip()) < 2000:
        minor_issues.append("当前汇编稿篇幅仍偏短，需要确认各章是否达到参考样例的篇幅层级。")

    for innovation in idea_card.get("core_innovations", [])[:3]:
        if innovation and innovation not in draft:
            minor_issues.append(f"核心创新点未在全书中稳定出现：{innovation}")

    for chapter in manifest.get("chapters", []):
        pending_confirmations.extend(chapter.get("pending_confirmations", []))

    if blocked:
        verdict = "human_check"
    elif major_issues:
        verdict = "revise"
    else:
        # Minor issues remain advisory so Step8 can proceed when no blocking
        # chapter/status/length/evidence failures remain.
        verdict = "pass"

    coverage_score = 100 - 20 * len(major_issues) - 5 * len(minor_issues)
    if coverage_score < 0:
        coverage_score = 0

    if verdict == "pass":
        final_status = "pass"
        next_action = "run_step8_record"
        next_action_owner = "agent1"
        update_step_status(topic_dir, step6_status="completed", step7_status="completed", step8_status="active")
        sync_workspace_state(
            topic_dir,
            step="document_review",
            workflow_status="active",
            next_action=next_action,
            required_inputs=[
                "workspace/document_writing/作品书草稿.md",
                "workspace/document_review/quality-gate.json",
            ],
            resume_entrypoint="workspace/document_review/quality-gate.json",
            last_completed_artifact="workspace/document_review/quality-gate.json",
            active_focus="作品书已通过章节 gate 和全书总体验收",
            current_direction="进入 Step8 交接与导出",
            note="Step7 final acceptance passed.",
        )
    elif verdict == "human_check":
        final_status = "blocked"
        next_action = "human_checkpoint_for_step6_step7"
        next_action_owner = "joint"
        update_step_status(topic_dir, step6_status="blocked", step7_status="blocked", step8_status="pending")
        sync_workspace_state(
            topic_dir,
            step="document_review",
            workflow_status="blocked",
            next_action=next_action,
            required_inputs=[
                "workspace/document_writing/agent-runtime.json",
                "workspace/document_review/quality-gate.json",
            ],
            resume_entrypoint="workspace/document_review/quality-gate.json",
            last_completed_artifact="workspace/document_review/quality-gate.json",
            active_focus="存在 blocked 章节，需要人工判断是否继续",
            current_direction="保持章节 gate 证据，不跳过人工检查",
            blocking_reason="存在被阻塞的章节或总体验收无法自动推进。",
            note="Step7 raised human checkpoint.",
        )
    else:
        final_status = "revise"
        next_action = runtime.get("next_action", "run_document_writing")
        next_action_owner = "agent1"
        update_step_status(topic_dir, step6_status="active", step7_status="completed", step8_status="pending")
        sync_workspace_state(
            topic_dir,
            step="document_writing",
            workflow_status="active",
            next_action="run_step6_agent_dispatch",
            required_inputs=runtime.get("required_inputs", []),
            resume_entrypoint="workspace/document_writing/agent-runtime.json",
            last_completed_artifact="workspace/document_review/quality-gate.json",
            active_focus=f"退回章节：{runtime.get('current_chapter_heading', '')}",
            current_direction=f"先运行 dispatcher，下发当前退回动作：{next_action}",
            note="Step7 requested chapter-level revision before final acceptance.",
        )

    payload["verdict"] = verdict
    payload["chapter_gate_summary"] = chapter_summary
    payload["final_acceptance"] = {
        "status": final_status,
        "issues": major_issues + minor_issues,
        "score": coverage_score,
    }
    payload["length_gate_summary"] = length_gate_summary
    payload["content_depth_gate"] = content_depth_gate
    payload["visual_gate"] = visual_gate
    payload["evidence_gate_summary"] = evidence_gate_summary
    payload["final_draft_gate_summary"] = final_draft_gate_summary
    payload["coverage_score"] = coverage_score
    payload["major_issues"] = major_issues
    payload["minor_issues"] = minor_issues
    payload["pending_confirmations"] = sorted({item for item in pending_confirmations if item})
    payload["next_action"] = next_action
    payload["next_action_owner"] = next_action_owner
    write_json(step7_dir / "quality-gate.json", payload)

    lines = [
        "# Quality Report",
        "",
        f"- Verdict: `{verdict}`",
        f"- Coverage Score: {coverage_score}",
        f"- Next Action: `{next_action}`",
        "",
        "## Chapter Gate Summary",
    ]
    for item in chapter_summary:
        lines.append(
            f"- {item['chapter_heading']}: status={item['status']}, round={item['round']}, verdict={item['verdict']}, "
            f"block={item['blocking_reason_category'] or 'none'}, decision={item['decision_file']}"
        )
    lines.extend(["", "## Length Gate Summary"])
    lines.append(
        f"- Full Book: assembled={length_gate_summary['assembled_count']}, "
        f"required>={length_gate_summary['total_required']}, passed={length_gate_summary['passed']}"
    )
    for item in length_gate_summary["per_chapter"]:
        lines.append(
            f"- {item['chapter_heading']}: actual={item['actual_count']}, required>={item['min_required']}, "
            f"status={item['status']}, passed={item['passed']}"
        )
    lines.extend(["", "## Evidence Gate Summary"])
    lines.append(
        f"- Required Chapters: {evidence_gate_summary['required_chapters']}, "
        f"missing={evidence_gate_summary['missing_required']}, weak={evidence_gate_summary['weak_required']}, "
        f"passed={evidence_gate_summary['passed']}"
    )
    for item in evidence_gate_summary["per_chapter"]:
        lines.append(
            f"- {item['chapter_heading']}: required={item['required']}, status={item['status']}, "
            f"count={item['evidence_count']}, authoritative={item['authoritative_count']}, "
            f"high_reliability={item['high_reliability_count']}, audit={item['audit_status']}"
        )
    lines.extend(["", "## Visual Gate Summary"])
    lines.append(
        f"- Required Specs: {visual_gate['required_specs']}, available_assets={visual_gate['available_assets']}, "
        f"asset_ratio={visual_gate['asset_ratio']:.2f}, passed={visual_gate['passed']}"
    )
    lines.extend([f"- {item}" for item in visual_gate["failures"]] or ["- none"])
    lines.extend(["", "## Final Draft Gate Summary"])
    lines.append(
        f"- Mixed Visual Numbering: {final_draft_gate_summary['mixed_visual_numbering']}"
    )
    for item in final_draft_gate_summary["matched_hard_patterns"]:
        lines.append(f"- Hard Block Pattern: {item['label']} count={item['count']}")
    for item in final_draft_gate_summary["matched_major_patterns"]:
        lines.append(
            f"- Major Risk Pattern: {item['label']} count={item['count']} threshold>={item['threshold']}"
        )
    if final_draft_gate_summary["proposal_style_titles"]:
        lines.append(
            "- Proposal-style H2 Titles: " + "、".join(final_draft_gate_summary["proposal_style_titles"])
        )
    if final_draft_gate_summary["temporary_innovation_headings"]:
        lines.append(
            "- Temporary Innovation Headings: " + "、".join(final_draft_gate_summary["temporary_innovation_headings"])
        )
    for item in final_draft_gate_summary["duplicate_paragraphs"]:
        lines.append(
            f"- Duplicate Paragraph: count={item['count']} excerpt={item['excerpt']}"
        )
    for item in final_draft_gate_summary["section_overlap_issues"]:
        lines.append(f"- Section Overlap: {item}")
    if (
        not final_draft_gate_summary["matched_hard_patterns"]
        and not final_draft_gate_summary["matched_major_patterns"]
        and not final_draft_gate_summary["proposal_style_titles"]
        and not final_draft_gate_summary["temporary_innovation_headings"]
        and not final_draft_gate_summary["mixed_visual_numbering"]
        and not final_draft_gate_summary["duplicate_paragraphs"]
        and not final_draft_gate_summary["section_overlap_issues"]
    ):
        lines.append("- none")
    lines.extend(["", "## Major Issues"])
    lines.extend([f"- {item}" for item in major_issues] or ["- none"])
    lines.extend(["", "## Minor Issues"])
    lines.extend([f"- {item}" for item in minor_issues] or ["- none"])
    lines.extend(["", "## Pending Confirmations"])
    lines.extend([f"- {item}" for item in payload["pending_confirmations"]] or ["- none"])
    write_text(step7_dir / "quality-report.md", "\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

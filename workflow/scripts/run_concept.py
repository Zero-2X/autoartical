#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from topic_profiles import resolve_topic_profile
from validation_support_builder import build_validation_support_pack


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sanitize_filename(name: str) -> str:
    return name.replace("/", "-").replace("\\", "-").strip()


def build_evidence_lookup(ledger: dict) -> dict[str, dict]:
    return {item.get("evidence_id", ""): item for item in ledger.get("evidence_items", []) if item.get("evidence_id")}


def summarize_evidence(evidence_ids: list[str], evidence_lookup: dict[str, dict]) -> list[str]:
    lines: list[str] = []
    for evidence_id in evidence_ids:
        item = evidence_lookup.get(evidence_id)
        if not item:
            continue
        source_title = shorten_source_title(item.get("source_title", "") or item.get("source_path", ""))
        summary = evidence_display_summary(item)
        lines.append(f"{evidence_id} | {source_title}：{summary}")
    return lines


def join_cn(items: list[str], sep: str = "；") -> str:
    return sep.join([item for item in items if item])


def shorten_source_title(title: str) -> str:
    clean = title.lstrip("# ").strip()
    for delimiter in [":", "："]:
        if delimiter in clean:
            return clean.split(delimiter, 1)[0].strip()
    return clean


def normalize_inline_text(text: str) -> str:
    cleaned = " ".join(text.replace("\n", " ").split()).strip("。； ")
    cleaned = re.sub(r"^\d+\.\s*", "", cleaned)
    return cleaned


def clean_evidence_candidate(item: dict, text: str) -> str:
    cleaned = normalize_inline_text(text)
    if not cleaned:
        return ""

    raw_title = item.get("source_title", "") or ""
    short_title = shorten_source_title(raw_title) if raw_title else ""
    title_candidates = [candidate for candidate in [raw_title.lstrip("# ").strip(), short_title] if candidate]
    file_candidates: list[str] = []
    source_path = item.get("source_path", "") or item.get("source_locator", "") or ""
    if source_path:
        path = Path(source_path)
        file_candidates.extend([path.name, path.stem])

    prefixes = [prefix for prefix in [*file_candidates, *title_candidates] if prefix]
    changed = True
    while changed:
        changed = False
        for prefix in prefixes:
            pattern = rf"^\#?\s*{re.escape(prefix)}\s*(?:主要涉及)?\s*[:：;；/\-]*\s*"
            updated = re.sub(pattern, "", cleaned, flags=re.I).strip()
            if updated != cleaned:
                cleaned = updated
                changed = True
    cleaned = cleaned.lstrip("# ").strip("。； ")
    return cleaned


def evidence_display_summary(item: dict) -> str:
    candidates = [
        clean_evidence_candidate(item, item.get("summary", "")),
        clean_evidence_candidate(item, item.get("claim", "")),
        clean_evidence_candidate(item, item.get("excerpt", "")),
    ]
    candidates = [text for text in candidates if text]
    if not candidates:
        fallback = normalize_inline_text(item.get("summary", "") or item.get("claim", "") or item.get("excerpt", ""))
        return fallback
    return max(candidates, key=len)


def evidence_text_penalty(text: str) -> int:
    penalty = 0
    if re.search(r"\.(md|pdf|tex|docx?|documentx?|xlsx?)\b", text, flags=re.I):
        penalty += 4
    if "/" in text or "\\" in text:
        penalty += 3
    if "主要涉及" in text:
        penalty += 3
    if text.startswith("#"):
        penalty += 2
    return penalty


def compact_evidence_claim(item: dict, max_len: int = 56) -> str:
    summary = clean_evidence_candidate(item, item.get("summary", ""))
    claim = clean_evidence_candidate(item, item.get("claim", ""))
    excerpt = clean_evidence_candidate(item, item.get("excerpt", ""))
    candidates = [text for text in [summary, claim, excerpt] if text]
    if not candidates:
        return ""

    bounded = [text for text in candidates if len(text) <= max_len]
    if bounded:
        return min(bounded, key=lambda text: (evidence_text_penalty(text), len(text)))

    clauses: list[str] = []
    for text in candidates:
        for delimiter in ["。", "；", ";", "：", ":"]:
            if delimiter not in text:
                continue
            prefix = text.split(delimiter, 1)[0].strip()
            if 12 <= len(prefix) <= max_len:
                clauses.append(prefix)
    if clauses:
        return min(clauses, key=lambda text: (evidence_text_penalty(text), len(text)))

    return max(candidates, key=len)


def build_evidence_digest(evidence_ids: list[str], evidence_lookup: dict[str, dict], limit: int = 2) -> str:
    chunks: list[str] = []
    for evidence_id in evidence_ids[:limit]:
        item = evidence_lookup.get(evidence_id)
        if not item:
            continue
        source_name = shorten_source_title(item.get("source_title", "") or item.get("source_path", ""))
        claim = compact_evidence_claim(item)
        if claim.startswith(source_name):
            chunks.append(claim)
        else:
            chunks.append(f"{source_name} 表明 {claim}")
    return join_cn(chunks, sep="；")


def normalize_solution_summary(text: str) -> str:
    return text.replace("以“以“", "以“").replace("”为总主轴", "”为主轴")


def normalize_point_text(text: str) -> str:
    return text.strip().strip("。；，、 ")


def is_risk_like_point(text: str) -> bool:
    stripped = normalize_point_text(text)
    if not stripped:
        return False
    risk_markers = (
        "需要",
        "待确认",
        "需补",
        "需明确",
        "避免",
        "控制",
        "第一版",
        "实现复杂度",
        "讲解",
        "叙事",
        "样机",
        "模拟",
        "术语",
    )
    return stripped.startswith(("需要", "待确认")) or any(marker in stripped for marker in risk_markers)


def collect_problem_pain_points(idea: dict, alignment: dict) -> list[str]:
    risk_set = {normalize_point_text(item) for item in idea.get("risk_notes", []) if normalize_point_text(item)}
    candidates = alignment.get("blind_spots", []) or idea.get("blind_spots", []) or []
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw_item in candidates:
        item = normalize_point_text(raw_item)
        if not item or item in seen or item in risk_set or is_risk_like_point(item):
            continue
        seen.add(item)
        cleaned.append(item)
    problem = normalize_point_text(idea.get("problem", ""))
    if problem and problem not in seen:
        cleaned.insert(0, problem)
        seen.add(problem)
    return cleaned[:3]


def should_rebuild_opening_summary(raw_summary: str, risk_notes: list[str]) -> bool:
    summary = raw_summary.strip()
    if not summary:
        return True
    if "。、" in summary or "并以 创新" in summary:
        return True
    normalized_summary = normalize_point_text(summary)
    return any(note and normalize_point_text(note) in normalized_summary for note in risk_notes)


def build_opening_summary(project_name: str, problem: str, pain_points: list[str], innovation_titles: list[str], raw_summary: str, risk_notes: list[str]) -> str:
    if not should_rebuild_opening_summary(raw_summary, risk_notes):
        return raw_summary.strip()
    point_text = join_cn(pain_points[:3], sep="；") or problem
    innovation_text = "、".join([title for title in innovation_titles if title]) or "核心创新"
    return (
        f"{project_name}聚焦的问题并不是单点异常判断，而是围绕 {point_text} 形成的一组连续业务盲区。"
        f"本方案尝试把这些问题串成一个完整闭环，并以 {innovation_text} 作为主要突破口。"
    )


def infer_module_position(title: str) -> str:
    if "反讽" in title or "情绪" in title:
        return "前端内容理解与情绪校正层"
    if "一致性" in title or "叙事" in title or "真伪" in title or "配文" in title:
        return "中段叙事校验与风险识别层"
    if "预警" in title or "分级" in title or "处置" in title or "介入" in title:
        return "后段评分决策与人工介入层"
    if "传播" in title or "势能" in title or "节点" in title or "沙盘" in title:
        return "传播研判与决策支撑层"
    if "展示" in title or "答辩" in title or "回放" in title:
        return "展示表达与运营联动层"
    return "系统链路中的关键模块"


def build_innovation_paragraphs(idea_card: dict, evidence_lookup: dict[str, dict]) -> list[tuple[str, str]]:
    paragraphs: list[tuple[str, str]] = []
    innovation_evidence_map = idea_card.get("innovation_evidence_map", [])
    evidence_map_by_title = {item.get("title", ""): item for item in innovation_evidence_map}
    for detail in idea_card.get("innovation_details", []):
        title = detail.get("title", "")
        summary = detail.get("summary", "").strip()
        mapping = evidence_map_by_title.get(title, {})
        evidence_ids = mapping.get("supporting_evidence_ids", [])
        digest = build_evidence_digest(evidence_ids, evidence_lookup, limit=2)
        module_position = infer_module_position(title)
        if digest:
            paragraph = (
                f"{summary} 在整体架构中，这一模块承担 {module_position}，"
                f"{digest}；因此它不是孤立功能点，而是后续系统闭环得以成立的关键支点。"
            )
        else:
            paragraph = f"{summary} 在整体架构中，这一模块承担 {module_position}，用于把方案从概念描述推进到可落地的系统设计。"
        paragraphs.append((title, paragraph))
    return paragraphs


def build_idea_card_from_step2(idea: dict) -> dict:
    alignment = dict(idea.get("template_alignment", {}))
    innovation_blocks = alignment.get("innovation_blocks", [])
    technical_architecture = idea.get("technical_architecture", [])
    if not technical_architecture:
        technical_architecture = [
            "多模态数据接入层",
            "内容理解与风险分析层",
            "评分与决策层",
            "展示与运营联动层",
        ]
    application_scenarios = idea.get("application_scenarios", []) or idea.get("target_users", [])
    cleaned_pain_points = collect_problem_pain_points(idea, alignment)
    innovation_titles = [block.get("title", "") for block in innovation_blocks]
    alignment["blind_spots"] = cleaned_pain_points
    alignment["opening_summary"] = build_opening_summary(
        idea.get("project_name", ""),
        normalize_point_text(idea.get("problem", "")),
        cleaned_pain_points,
        innovation_titles,
        alignment.get("opening_summary", ""),
        idea.get("risk_notes", []),
    )
    idea_card = {
        "idea_id": idea["idea_id"],
        "project_name": idea["project_name"],
        "slogan": idea.get("slogan", "") or alignment.get("closing_summary", "")[:32],
        "problem": idea["problem"],
        "target_users": idea["target_users"],
        "pain_points": cleaned_pain_points,
        "solution_summary": idea["solution_summary"],
        "core_innovations": [block.get("title", "") for block in innovation_blocks] or idea["core_innovations"],
        "innovation_details": innovation_blocks,
        "technical_architecture": technical_architecture,
        "application_scenarios": application_scenarios,
        "competitive_advantages": idea.get("value_notes", []),
        "implementation_feasibility": idea.get("feasibility_notes", []),
        "business_value": idea.get("value_notes", []),
        "open_questions": idea.get("risk_notes", []),
        "evidence_refs": idea.get("evidence_refs", []),
        "evidence_claim_map": idea.get("analysis_basis", {"problem_basis": [], "solution_basis": [], "fit_basis": []}),
        "innovation_evidence_map": idea.get("innovation_evidence_map", []),
        "template_alignment": alignment,
        "candidate_preview_path": idea.get("candidate_preview_path", ""),
        "topic_name": idea.get("topic_name", ""),
        "topic_profile": idea.get("topic_profile", {}),
        "validation_evidence_mode": "unspecified",
        "validation_support_pack": {
            "mode": "unspecified",
            "status": "not_configured",
            "disclosure": "",
            "chapter_title": "",
            "summary": "",
            "metric_summary": [],
            "comparison_experiments": [],
            "case_replay": {"title": "", "timeline": []},
            "system_metrics": [],
            "required_assets": [],
        },
    }
    return idea_card


def build_brief_markdown(idea_card: dict, spec: dict, evidence_lookup: dict[str, dict]) -> str:
    alignment = idea_card.get("template_alignment", {})
    project_name = idea_card["project_name"]
    evidence_claim_map = idea_card.get("evidence_claim_map", {})
    problem_evidence = summarize_evidence(evidence_claim_map.get("problem_basis", []), evidence_lookup)
    solution_evidence = summarize_evidence(evidence_claim_map.get("solution_basis", []), evidence_lookup)
    fit_evidence = summarize_evidence(evidence_claim_map.get("fit_basis", []), evidence_lookup)
    problem_digest = build_evidence_digest(evidence_claim_map.get("problem_basis", []), evidence_lookup, limit=2)
    solution_digest = build_evidence_digest(evidence_claim_map.get("solution_basis", []), evidence_lookup, limit=3)
    fit_digest = build_evidence_digest(evidence_claim_map.get("fit_basis", []), evidence_lookup, limit=2)
    normalized_points = [normalize_point_text(item) for item in idea_card.get("pain_points", []) if normalize_point_text(item)]
    problem_text = join_cn(normalized_points, sep="；")
    solution_text = normalize_solution_summary(idea_card.get("solution_summary", ""))
    value_text = join_cn(idea_card.get("business_value", []), sep="；")
    feasibility_text = join_cn(idea_card.get("implementation_feasibility", []), sep="；")
    risk_text = join_cn(idea_card.get("open_questions", []), sep="；")
    innovation_paragraphs = build_innovation_paragraphs(idea_card, evidence_lookup)
    background_paragraph = (
        f"{spec.get('competition_name') or '本次竞赛'}强调作品的创意、技术方案及其实现质量、应用价值和讲解表现。"
        f"{alignment.get('opening_summary', '')}"
        f"{('从现有研究与样例脉络看，' + problem_digest + '，这说明该方向对应的是持续存在、且适合做成系统闭环的真实问题。') if problem_digest else ''}"
    )
    problem_paragraph = (
        f"{project_name}聚焦的不是单点异常判断，而是围绕 {problem_text or normalize_point_text(idea_card.get('problem', ''))} 形成的一组连续盲区。"
        f"如果这些问题仍然彼此割裂，团队就很难把分析结果真正转化为及时决策与联动动作。"
    )
    solution_paragraph = (
        f"方案定位上，{solution_text}"
        f"系统不再把采集、判断和处置建议拆成彼此孤立的模块，而是按“数据接入 - 状态分析 - 结果评估 - 联动执行”的链路组织。"
        f"{('结合 ' + solution_digest + '，当前更合理的做法不是只做一个分类器，而是搭建可解释、可联动、可扩展的分层流程。') if solution_digest else ''}"
    )
    lines = [
        f"# {project_name}",
        "",
        "## 项目背景",
        "",
        background_paragraph,
        "",
        "## 问题痛点",
        "",
        problem_paragraph,
        "",
    ]
    lines.extend([f"- {item}" for item in normalized_points] or [normalize_point_text(idea_card.get("problem", ""))])
    if problem_evidence:
        lines.extend(["", "### 对应证据", ""])
        lines.extend([f"- {item}" for item in problem_evidence])
    lines.extend(
        [
            "",
            "## 核心方案",
            "",
            solution_paragraph,
            "",
            "## 关键创新",
            "",
        ]
    )
    for title, detail_paragraph in innovation_paragraphs:
        lines.extend(
            [
                f"### {title}",
                "",
                detail_paragraph,
                "",
            ]
        )
    if solution_evidence:
        lines.extend(["### 方案依据", ""])
        lines.extend([f"- {item}" for item in solution_evidence])
        lines.append("")
    if not innovation_paragraphs:
        lines.extend([f"- {item}" for item in idea_card.get("core_innovations", [])] or ["- none", ""])
    lines.extend(
        [
            "## 技术架构",
            "",
        ]
    )
    lines.extend([f"{index}. {item}" for index, item in enumerate(idea_card.get("technical_architecture", []), start=1)] or ["1. 待补充"])
    lines.extend(
        [
            "",
            "## 应用场景",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in idea_card.get("application_scenarios", [])] or ["- none"])
    lines.extend(
        [
            "",
            "## 落地价值",
            "",
            f"{project_name}更适合被做成系统型比赛作品，而不是单点模型展示。其直接价值可概括为：{value_text or '具备明确应用价值'}。",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in idea_card.get("business_value", [])] or ["- none"])
    if feasibility_text:
        lines.extend(["", "## 实现可行性", "", f"现流程的可行性判断主要基于：{feasibility_text}。", ""])
    lines.extend(
        [
            "## 风险与待确认",
            "",
            f"需要提前控制的风险主要包括：{risk_text or '暂无'}。",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in idea_card.get("open_questions", [])] or ["- none"])
    lines.extend(
        [
            "",
            "## 证据依据",
            "",
            f"- Evidence Refs: {', '.join(idea_card.get('evidence_refs', [])) or 'none'}",
            f"- Problem Basis: {', '.join(idea_card.get('evidence_claim_map', {}).get('problem_basis', [])) or 'none'}",
            f"- Solution Basis: {', '.join(idea_card.get('evidence_claim_map', {}).get('solution_basis', [])) or 'none'}",
            f"- Fit Basis: {', '.join(idea_card.get('evidence_claim_map', {}).get('fit_basis', [])) or 'none'}",
            "",
        ]
    )
    if fit_evidence:
        lines.extend(["### 比赛匹配依据", ""])
        lines.extend([f"- {item}" for item in fit_evidence])
        lines.append("")
    validation_pack = idea_card.get("validation_support_pack", {}) or {}
    if validation_pack.get("status") == "ready":
        lines.extend(
            [
                "## 仿真验证包",
                "",
                validation_pack.get("disclosure", ""),
                "",
                validation_pack.get("summary", ""),
                "",
                "### 建议补入作品书的验证资产",
                "",
            ]
        )
        lines.extend([f"- {item}" for item in validation_pack.get("required_assets", [])] or ["- none"])
        lines.extend(
            [
                "",
                "### 建议优先展示的关键指标",
                "",
            ]
        )
        for item in validation_pack.get("metric_summary", []):
            lines.append(f"- {item.get('label', '')}：{item.get('value', '')}。{item.get('meaning', '')}")
        lines.append("")
    lines.extend(
        [
            "## 收口总结",
            "",
            f"{alignment.get('closing_summary', '')} {('同时，' + fit_digest + '，也说明该方向在比赛语境下更容易被讲清、被展示、被评委快速理解。') if fit_digest else ''}",
            "",
        ]
    )
    return "\n".join(lines)


def update_workspace_state(topic_dir: Path) -> None:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not state_path.exists():
        return
    state = read_json(state_path)
    workflow_status = state.setdefault("workflow_status", {})
    state["current_step"] = "research"
    workflow_status["selection"] = "completed"
    workflow_status["concept"] = "completed"
    workflow_status["research"] = "active"
    workflow_status["document_plan"] = "pending"
    state["next_action"] = "run_research"
    state["blocking_reason"] = ""
    state["required_inputs"] = []
    write_json(state_path, state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AutoSearch MVP step4 idea brief generation.")
    parser.add_argument("topic_dir", help="Topic directory, such as sample/topic_xx")
    parser.add_argument("--topic", default="", help="Optional topic override. Defaults to workspace topic_name.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    step_dir = topic_dir / "workspace" / "concept"
    selected_path = topic_dir / "workspace" / "selection" / "selected-idea.json"
    scorecard_path = topic_dir / "workspace" / "ideas" / "idea-scorecard.json"
    spec_path = topic_dir / "workspace" / "requirements" / "competition-spec.json"
    evidence_path = topic_dir / "workspace" / "ideas" / "evidence-ledger.json"

    if not selected_path.exists() or not scorecard_path.exists() or not spec_path.exists() or not evidence_path.exists():
        raise SystemExit("Missing step inputs for concept.")

    selected = read_json(selected_path)
    selected_id = selected.get("selected_id", "")
    if not selected_id:
        raise SystemExit("No selected idea id found. Complete step3 selection first.")

    ideas = read_json(scorecard_path).get("ideas", [])
    idea = next((item for item in ideas if item.get("idea_id") == selected_id), None)
    if not idea:
        raise SystemExit(f"Selected idea id not found in scorecard: {selected_id}")

    spec = read_json(spec_path)
    evidence_lookup = build_evidence_lookup(read_json(evidence_path))
    idea_card = build_idea_card_from_step2(idea)
    if args.topic.strip():
        topic_profile = resolve_topic_profile(topic_dir, explicit_topic=args.topic)
        idea_card["topic_name"] = topic_profile.get("topic_name", "")
        idea_card["topic_profile"] = {
            "profile_id": topic_profile.get("profile_id", ""),
            "display_name": topic_profile.get("display_name", ""),
            "domain_label": topic_profile.get("domain_label", ""),
            "cover_title_suffix": topic_profile.get("cover_title_suffix", ""),
            "hero_visual_hint": topic_profile.get("hero_visual_hint", ""),
            "background_focus": topic_profile.get("background_focus", ""),
            "goal_focus": topic_profile.get("goal_focus", ""),
            "innovation_focus": topic_profile.get("innovation_focus", ""),
            "value_focus": topic_profile.get("value_focus", ""),
            "keywords": topic_profile.get("keywords", []),
        }
    validation_pack = build_validation_support_pack(idea_card)
    idea_card["validation_evidence_mode"] = validation_pack.get("mode", "unspecified")
    idea_card["validation_support_pack"] = validation_pack
    brief_text = build_brief_markdown(idea_card, spec, evidence_lookup)

    idea_filename = f"Idea_{sanitize_filename(idea['project_name'])}.md"
    write_text(step_dir / idea_filename, brief_text)
    write_json(step_dir / "idea-card.json", idea_card)
    write_json(step_dir / "validation-support-pack.json", validation_pack)
    update_workspace_state(topic_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

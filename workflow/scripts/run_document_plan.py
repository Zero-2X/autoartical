#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from proposal_workflow import ensure_state_scaffold, sync_workspace_state
from topic_profiles import resolve_topic_profile
from validation_support_builder import build_validation_support_pack
from content_depth import DEFAULT_CONTRACT, allocate_budgets

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_json_template(name: str) -> dict[str, Any]:
    return read_json(TEMPLATES_DIR / name)


def unique_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def join_cn(items: list[str], sep: str = "、") -> str:
    return sep.join([item for item in items if item])


def strip_trailing_punct(text: str) -> str:
    return str(text or "").strip().rstrip("。；;，, ")


def shorten(text: str, limit: int = 72) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


def sanitize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def build_evidence_index(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = ledger.get("evidence_items") or ledger.get("items") or ledger.get("evidence") or []
    return {item.get("evidence_id", ""): item for item in items if item.get("evidence_id")}


def serialize_evidence(evidence_ids: list[str], evidence_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    serialized: list[dict[str, Any]] = []
    for evidence_id in unique_list(evidence_ids):
        item = evidence_index.get(evidence_id, {})
        serialized.append(
            {
                "evidence_id": evidence_id,
                "source": item.get("source_path") or item.get("source_locator") or "",
                "claim": item.get("claim", ""),
                "summary": item.get("summary", ""),
                "derived_insight": item.get("derived_insight", ""),
                "evidence_kind": item.get("evidence_kind", ""),
                "source_authority": item.get("source_authority", ""),
                "supports": item.get("supports", []),
                "reliability": item.get("reliability", ""),
                "tags": item.get("tags", []),
            }
        )
    return serialized


def collect_innovation_evidence_ids(idea_card: dict[str, Any]) -> list[str]:
    evidence_ids: list[str] = []
    for innovation in idea_card.get("innovation_evidence_map", []):
        primary = innovation.get("primary_evidence_id", "")
        supporting = innovation.get("supporting_evidence_ids", [])
        if primary:
            evidence_ids.append(primary)
        evidence_ids.extend(supporting)
    return unique_list(evidence_ids)


def chapter_reference_map(reference_template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for chapter in reference_template.get("chapter_logic", []):
        chapter_title = chapter.get("chapter", "")
        sections = chapter.get("sections", [])
        for section in sections:
            title = section.get("title", "")
            if " " in title:
                _, normalized_title = title.split(" ", 1)
            else:
                normalized_title = title
            mapping[normalized_title] = {
                "chapter": chapter_title,
                "logic": chapter.get("logic", ""),
                "page_span": section.get("page_span", ""),
                "word_budget": section.get("word_budget", ""),
            }
    return mapping


def global_reference_for(reference_template: dict[str, Any], keyword: str) -> dict[str, Any]:
    for item in reference_template.get("global_structure", []):
        if keyword in item.get("section", ""):
            return item
    return {}


def infer_work_type(idea_card: dict[str, Any]) -> tuple[str, str]:
    text_parts = [
        idea_card.get("project_name", ""),
        idea_card.get("problem", ""),
        idea_card.get("solution_summary", ""),
        " ".join(idea_card.get("core_innovations", [])),
        " ".join(idea_card.get("technical_architecture", [])),
        " ".join(idea_card.get("application_scenarios", [])),
    ]
    text = " ".join(text_parts)

    if any(keyword in text for keyword in ("传感器", "设备", "终端", "边缘", "硬件", "采集端", "网关", "物联网")):
        return "软硬件结合型", "项目描述包含设备端、边缘侧或物联网接入特征，作品书需显式交代硬件链路、部署边界与实测条件。"
    if any(keyword in text for keyword in ("平台", "监测", "预警", "大屏", "运营", "联动", "治理", "工作流", "闭环", "Web")):
        return "平台应用型", "项目强调平台能力、用户场景和运营闭环，作品书应提高问题场景、系统流程和应用价值的章节权重。"
    if any(keyword in text for keyword in ("论文", "专利", "成果", "转化", "原型")):
        return "科研成果转化型", "项目带有研究成果落地特征，作品书需同时说明研究基础、工程化改造与转化价值。"
    if any(keyword in text for keyword in ("算法", "优化", "模型", "损失", "鲁棒", "泛化", "识别", "检测", "生成")):
        return "算法创新型", "项目以算法机制与效果提升为主，作品书应强化关键技术和实验验证章节。"
    return "工程系统型", "项目具备明显系统集成与流程实现特征，作品书需重视总体架构、运行流程和系统测试。"


def build_problem_focus_message(idea_card: dict[str, Any], target_users: list[str]) -> str:
    problem = strip_trailing_punct(idea_card.get("problem", ""))
    users = join_cn(target_users)
    if problem:
        return f"核心用户聚焦 {users}，项目要解决的关键问题是：{problem}。"
    return f"核心用户聚焦 {users}，本章需要把问题定义、用户动作和系统价值讲清。"


def build_targeted_design_rationale(idea_card: dict[str, Any]) -> str:
    topic_profile = idea_card.get("topic_profile", {})
    domain_label = topic_profile.get("display_name", "") or idea_card.get("topic_name", "") or "目标场景"
    return f"证明项目不是通用系统的简单拼装，而是围绕 {domain_label} 场景中的关键问题做了针对性设计。"


def make_missing_materials(
    items: list[str],
    *,
    impacted_chapter: str,
    why_needed: str,
    suggested_backtrack_step: str,
    minimum_acceptable_substitute: str,
    priority: str = "medium",
) -> list[dict[str, str]]:
    return [
        {
            "missing_item": item,
            "impacted_chapter": impacted_chapter,
            "why_needed": why_needed,
            "priority": priority,
            "suggested_backtrack_step": suggested_backtrack_step,
            "minimum_acceptable_substitute": minimum_acceptable_substitute,
        }
        for item in unique_list(items)
        if item
    ]


def build_innovation_loop_map(
    idea_card: dict[str, Any],
    *,
    current_section_role: str,
    validation_anchor: str,
    expected_value_signal: str,
) -> list[dict[str, str]]:
    evidence_map = {
        item.get("title", ""): item
        for item in idea_card.get("innovation_evidence_map", [])
        if item.get("title")
    }
    results: list[dict[str, str]] = []
    for innovation in idea_card.get("innovation_details", []):
        title = innovation.get("title", "")
        summary = innovation.get("summary", "")
        rationale = evidence_map.get(title, {}).get("rationale", "")
        results.append(
            {
                "innovation_title": title,
                "problem_source": summary or rationale,
                "current_section_role": current_section_role,
                "validation_anchor": validation_anchor,
                "expected_value_signal": expected_value_signal,
                "practical_meaning": summary,
            }
        )
    return results


def infer_visual_type(name: str) -> str:
    if any(token in name for token in ("表", "清单", "矩阵", "接口")):
        return "table"
    return "figure"


def infer_visual_purpose(name: str, fallback: str) -> str:
    mapping = [
        (("趋势", "时间线", "态势"), "支撑背景趋势、需求演进或问题紧迫性的论证。"),
        (("架构", "分层"), "说明系统由哪些模块组成，以及模块之间如何协同。"),
        (("流程", "时序", "闭环"), "说明系统运行步骤、数据流向或业务闭环。"),
        (("对照", "映射"), "对齐痛点、创新点、模块或证据之间的对应关系。"),
        (("截图", "界面"), "展示用户可见功能或系统操作路径。"),
        (("矩阵", "场景"), "说明典型场景、目标用户或应用覆盖范围。"),
        (("边界", "里程碑", "风险"), "说明 MVP 范围、流程路线或待确认事项。"),
    ]
    for tokens, purpose in mapping:
        if any(token in name for token in tokens):
            return purpose
    return fallback or "支撑当前章节的核心论证，而不是只用于填充版面。"


def build_visual_specs(
    *,
    section_id: str,
    heading: str,
    chapter_number: int,
    subsections: list[str],
    visual_priority: list[str],
    recommended_visuals: list[str],
) -> list[dict[str, Any]]:
    visual_names = unique_list(recommended_visuals or visual_priority)
    specs: list[dict[str, Any]] = []
    chapter_title = heading.split("、", 1)[-1]
    fallback_purpose = f"支撑《{chapter_title}》章节中的核心论证。"
    for index, name in enumerate(visual_names, start=1):
        visual_type = infer_visual_type(name)
        label_prefix = "表" if visual_type == "table" else "图"
        purpose = infer_visual_purpose(name, visual_priority[min(index - 1, len(visual_priority) - 1)] if visual_priority else fallback_purpose)
        suggested_subsection = subsections[min(index - 1, len(subsections) - 1)] if subsections else chapter_title
        visual_id = f"{section_id}_{sanitize_token(name) or f'visual_{index}'}"
        specs.append(
            {
                "visual_id": visual_id,
                "label": f"{label_prefix}{chapter_number}-{index}",
                "visual_type": visual_type,
                "title": name,
                "purpose": purpose,
                "placement_anchor": suggested_subsection or chapter_title,
                "suggested_subsection": suggested_subsection,
                "body_reference_hint": f"建议在正文中使用“如{label_prefix.lower()}{chapter_number}-{index}所示”或“{label_prefix}{chapter_number}-{index}显示”来引用该{label_prefix}。",
                "asset_candidates": [
                    f"figures/{visual_id}.png",
                    f"figures/{visual_id}.pdf",
                    f"workspace/document_export/assets/visuals/{visual_id}.png",
                    f"workspace/document_export/assets/visuals/{visual_id}.pdf",
                ],
                "required": True,
                "fallback_render": "latex_placeholder",
            }
        )
    return specs


def normalize_outline_heading(text: str) -> str:
    normalized = (text or "").strip()
    normalized = re.sub(r"^第[一二三四五六七八九十百千万0-9]+章\s*", "", normalized)
    normalized = re.sub(r"^[一二三四五六七八九十百千万0-9]+[、.．]\s*", "", normalized)
    normalized = re.sub(r"^\d+(?:\.\d+)*\s*", "", normalized)
    normalized = re.sub(r"^[（(]?[一二三四五六七八九十百千万0-9]+[)）.．、]\s*", "", normalized)
    return normalized.strip()


def is_generic_innovation_title(title: str) -> bool:
    normalized = normalize_outline_heading(title)
    return bool(re.fullmatch(r"创新[0-9一二三四五六七八九十]+", normalized))


def resolve_innovation_display_title(item: dict[str, Any]) -> str:
    title = (item.get("title", "") or "").strip()
    summary = (item.get("summary", "") or "").strip()
    if is_generic_innovation_title(title) and summary:
        return summary
    return title or summary


def detail_heading_contracts(title: str) -> tuple[list[str], str]:
    normalized = normalize_outline_heading(title)
    mapping = [
        (("背景", "赛题", "趋势"), (["现实背景", "趋势与赛题牵引", "问题演进"], "交代问题为何成立、为何紧迫。")),
        (("用户", "场景"), (["目标对象", "典型动作", "场景约束"], "说明给谁用、在什么动作链里用。")),
        (("痛点", "问题"), (["现有不足", "风险放大链路", "直接代价"], "把现有流程的断点和代价拆开说清。")),
        (("总体目标", "设计原则"), (["设计目标", "方案边界", "设计原则"], "先定义目标，再交代边界与原则。")),
        (("架构", "分层"), (["分层结构", "模块职责", "多端部署关系"], "解释系统结构和模块分工。")),
        (("闭环", "流程", "运行"), (["输入接入", "分析与评分", "输出与联动"], "讲清输入、处理、输出如何闭合。")),
        (("创新点总览", "总览"), (["痛点映射", "创新协同"], "先总览创新对应关系，再说明协同逻辑。")),
        (("创新二", "跨工况"), (["核心内容", "实现方法", "支撑说明"], "技术创新章节要先解释方法机制，再说明为何有效。")),
        (("创新1", "创新2", "创新3", "纠偏", "一致性", "势能"), (["问题来源与不足", "输入与关键信号", "技术机制与实现", "价值与验证"], "每个创新必须形成问题到验证的闭环。")),
        (("映射",), (["技术落点", "验证锚点", "系统对应关系"], "把创新与系统结构重新对齐。")),
        (("模块实现",), (["统一表征对象", "模块实现", "接口协同"], "说明模块如何落地与协作。")),
        (("案例回放", "人工复核"), (["案例回放链路", "复核证据面板", "复核与留痕"], "说明系统如何进入人工闭环。")),
        (("测试数据", "指标设置", "指标体系", "测试口径"), (["数据来源", "指标定义", "验证边界"], "先说明测试材料和指标，再交代结果适用边界。")),
        (("多源融合",), (["对比设置", "实验结果", "结果分析"], "围绕创新一给出清晰的对照组、结果与结论。")),
        (("鲁棒", "泛化", "跨工况"), (["工况划分", "对比结果", "稳定性分析"], "证明系统不是只在理想条件下有效。")),
        (("案例回放", "评分"), (["异常演化过程", "预警触发过程", "复核与回写过程"], "把静态指标转成可追踪的闭环过程。")),
        (("系统性能", "闭环验证"), (["时延与吞吐", "告警与工单闭环", "小结"], "补齐系统级性能和业务闭环结果。")),
        (("收益", "优势"), (["收益路径", "资源效率", "竞争优势"], "把技术能力翻译为收益闭环。")),
        (("展示",), (["展示主线", "多端呈现", "演示价值"], "说明比赛展示逻辑而不是泛泛应用价值。")),
        (("完成情况",), (["闭环完成情况", "关键能力", "交付形态"], "总结本作品已经形成的核心能力和当前交付状态。")),
        (("特色", "应用价值"), (["系统特色", "应用价值", "交付成熟度"], "把系统特点、应用价值和当前交付成熟度收束到一起。")),
        (("不足", "优化"), (["当前不足", "优化方向", "延展空间"], "如实说明不足，并交代后续优化方向。")),
        (("推进路线", "计划", "流程结论", "当前边界"), (["流程成果", "当前边界", "范围说明"], "说明现流程展示版已经形成什么、边界停在哪里。")),
        (("资源", "基础", "支撑条件"), (["实现基础", "支撑条件", "工程约束"], "说明当前落地依赖、支撑条件与工程约束。")),
        (("扩展", "待确认", "展望", "边界说明", "条件说明"), (["后续展望", "能力边界", "条件说明"], "把后续方向、能力边界与尚需核定的信息区分开。")),
    ]
    for tokens, payload in mapping:
        if any(token in normalized for token in tokens):
            return payload
    return ["核心内容", "支撑说明"], "保持两级细化，避免只有章标题和大段正文。"


def build_structure_contract(section_id: str, heading: str, subsections: list[str]) -> dict[str, Any]:
    second_level_contracts: list[dict[str, Any]] = []
    third_level_total_min = 0
    for subsection in subsections:
        detail_titles, writing_purpose = detail_heading_contracts(subsection)
        second_level_contracts.append(
            {
                "title": subsection,
                "writing_purpose": writing_purpose,
                "required_third_level_count": len(detail_titles),
                "required_third_level_titles": detail_titles,
            }
        )
        third_level_total_min += len(detail_titles)
    return {
        "contract_id": f"{section_id}_structure",
        "chapter_heading": heading,
        "required_second_level_count": len(subsections),
        "required_second_level_titles": subsections,
        "required_third_level_total_min": third_level_total_min,
        "required_third_level_total_target": third_level_total_min,
        "second_level_contracts": second_level_contracts,
        "failure_action": "rerun_planning_outline_recomposition",
    }


def validate_structure_contracts(sections: list[dict[str, Any]]) -> dict[str, Any]:
    chapter_checks: list[dict[str, Any]] = []
    issues: list[str] = []
    total_second_level_required = 0
    total_third_level_required = 0
    for section in sections:
        contract = section.get("structure_contract", {})
        required_titles = contract.get("required_second_level_titles", [])
        subsection_titles = section.get("subsections", [])
        second_level_ok = subsection_titles == required_titles
        second_level_count_ok = len(subsection_titles) == int(contract.get("required_second_level_count", 0) or 0)
        missing_detail_contracts = []
        for item in contract.get("second_level_contracts", []):
            if not item.get("required_third_level_titles"):
                missing_detail_contracts.append(item.get("title", ""))
        passed = second_level_ok and second_level_count_ok and not missing_detail_contracts
        if not passed:
            if not second_level_ok:
                issues.append(f"{section.get('heading', '')} 的二级目录标题未与硬约束完全一致。")
            if not second_level_count_ok:
                issues.append(f"{section.get('heading', '')} 的二级目录数量未达硬约束。")
            if missing_detail_contracts:
                issues.append(f"{section.get('heading', '')} 缺少三级目录硬约束：{join_cn(missing_detail_contracts)}")
        total_second_level_required += int(contract.get("required_second_level_count", 0) or 0)
        total_third_level_required += int(contract.get("required_third_level_total_min", 0) or 0)
        chapter_checks.append(
            {
                "section_id": section.get("section_id", ""),
                "heading": section.get("heading", ""),
                "required_second_level_count": contract.get("required_second_level_count", 0),
                "actual_second_level_count": len(subsection_titles),
                "required_second_level_titles": required_titles,
                "actual_second_level_titles": subsection_titles,
                "required_third_level_total_min": contract.get("required_third_level_total_min", 0),
                "second_level_contracts": contract.get("second_level_contracts", []),
                "passed": passed,
            }
        )
    verdict = "pass" if not issues else "fail"
    return {
        "verdict": verdict,
        "body_chapter_count": len(sections),
        "required_second_level_total": total_second_level_required,
        "required_third_level_total_min": total_third_level_required,
        "chapter_checks": chapter_checks,
        "issues": issues,
        "next_action": "" if verdict == "pass" else "rerun_document_plan",
    }


def render_structure_gate_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Outline Structure Gate",
        "",
        f"- Verdict: `{payload.get('verdict', '')}`",
        f"- Body Chapters: {payload.get('body_chapter_count', 0)}",
        f"- Required Second-Level Total: {payload.get('required_second_level_total', 0)}",
        f"- Required Third-Level Total Min: {payload.get('required_third_level_total_min', 0)}",
        "",
        "## Chapter Checks",
    ]
    for item in payload.get("chapter_checks", []):
        lines.extend(
            [
                f"### {item.get('heading', '')}",
                f"- Passed: `{item.get('passed', False)}`",
                f"- Required Second-Level Count: {item.get('required_second_level_count', 0)}",
                f"- Actual Second-Level Count: {item.get('actual_second_level_count', 0)}",
                f"- Required Second-Level Titles: {join_cn(item.get('required_second_level_titles', []))}",
                f"- Required Third-Level Total Min: {item.get('required_third_level_total_min', 0)}",
            ]
        )
        for contract in item.get("second_level_contracts", []):
            lines.append(
                f"- `{contract.get('title', '')}`: 必须包含 {contract.get('required_third_level_count', 0)} 个三级目录 -> "
                f"{join_cn(contract.get('required_third_level_titles', []))}"
            )
        lines.append("")
    lines.extend(["## Issues"])
    lines.extend([f"- {issue}" for issue in payload.get("issues", [])] or ["- none"])
    lines.append("")
    return "\n".join(lines)


def build_section(
    *,
    section_id: str,
    heading: str,
    goal: str,
    matched_scores: list[str],
    narrative_role: str,
    position_logic: str,
    chapter_weight_reason: str,
    predecessor_sections: list[str],
    successor_sections: list[str],
    sample_chapter: str,
    sample_logic: str,
    suggested_page_span: str,
    suggested_word_budget: str,
    subsections: list[str],
    structure_contract: dict[str, Any],
    body_priority: list[str],
    visual_priority: list[str],
    appendix_candidates: list[str],
    key_messages: list[str],
    must_include: list[str],
    linked_innovations: list[str],
    linked_architecture: list[str],
    innovation_loop_map: list[dict[str, str]],
    evidence_ids: list[str],
    evidence_index: dict[str, dict[str, Any]],
    recommended_visuals: list[str],
    visual_specs: list[dict[str, Any]],
    common_errors: list[str],
    risks: list[str],
    pending_confirmations: list[str] | None = None,
    missing_materials: list[dict[str, str]] | None = None,
    chapter_seed_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "heading": heading,
        "title": heading.split("、", 1)[-1],
        "goal": goal,
        "matched_scores": matched_scores,
        "narrative_role": narrative_role,
        "position_logic": position_logic,
        "chapter_weight_reason": chapter_weight_reason,
        "predecessor_sections": unique_list(predecessor_sections),
        "successor_sections": unique_list(successor_sections),
        "sample_chapter": sample_chapter,
        "sample_logic": sample_logic,
        "suggested_page_span": suggested_page_span,
        "suggested_word_budget": suggested_word_budget,
        "subsections": subsections,
        "structure_contract": structure_contract,
        "body_priority": unique_list(body_priority),
        "visual_priority": unique_list(visual_priority),
        "appendix_candidates": unique_list(appendix_candidates),
        "key_messages": unique_list(key_messages),
        "must_include": unique_list(must_include),
        "linked_innovations": unique_list(linked_innovations),
        "linked_architecture": unique_list(linked_architecture),
        "innovation_loop_map": innovation_loop_map,
        "supporting_evidence_ids": unique_list(evidence_ids),
        "supporting_evidence": serialize_evidence(evidence_ids, evidence_index),
        "recommended_visuals": unique_list(recommended_visuals),
        "visual_specs": visual_specs,
        "common_errors": unique_list(common_errors),
        "risks": unique_list(risks),
        "pending_confirmations": unique_list(pending_confirmations or []),
        "missing_materials": missing_materials or [],
        "chapter_seed_payload": chapter_seed_payload or {},
    }


def build_sections(
    spec: dict[str, Any],
    idea_card: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
    reference_template: dict[str, Any],
) -> list[dict[str, Any]]:
    template_alignment = idea_card.get("template_alignment", {})
    evidence_claim_map = idea_card.get("evidence_claim_map", {})
    innovation_titles = [item.get("title", "") for item in idea_card.get("innovation_details", [])]
    innovation_display_titles = [resolve_innovation_display_title(item) for item in idea_card.get("innovation_details", [])]
    innovation_summaries = [item.get("summary", "") for item in idea_card.get("innovation_details", [])]
    architecture = idea_card.get("technical_architecture", [])
    pain_points = idea_card.get("pain_points", [])
    target_users = idea_card.get("target_users", [])
    application_scenarios = idea_card.get("application_scenarios", [])
    implementation = idea_card.get("implementation_feasibility", [])
    open_questions = idea_card.get("open_questions", [])
    validation_pack = build_validation_support_pack(idea_card)
    idea_card["validation_support_pack"] = validation_pack
    validation_ready = validation_pack.get("status") == "ready"
    validation_summary = str(validation_pack.get("summary", "")).strip()
    validation_disclosure = str(validation_pack.get("disclosure", "")).strip()
    validation_assets = unique_list(validation_pack.get("required_assets", []) or [])
    validation_metric_labels = unique_list(
        [str(item.get("label", "")).strip() for item in validation_pack.get("metric_summary", []) or [] if str(item.get("label", "")).strip()]
    )
    validation_experiment_titles = unique_list(
        [str(item.get("title", "")).strip() for item in validation_pack.get("comparison_experiments", []) or [] if str(item.get("title", "")).strip()]
    )
    validation_reference = global_reference_for(reference_template, "作品测试与分析")
    blind_spots = template_alignment.get("blind_spots", []) or pain_points
    pending_confirmations = spec.get("pending_confirmations", [])
    innovation_evidence_ids = collect_innovation_evidence_ids(idea_card)
    reference_map = chapter_reference_map(reference_template)
    work_type, _work_type_reason = infer_work_type(idea_card)
    profile_id = str((idea_card.get("topic_profile", {}) or {}).get("profile_id", ""))
    is_remote_sensing_ovd = profile_id == "remote_sensing_open_vocabulary_detection"
    validation_subsections = (
        [
            "评测协议与数据划分",
            "Current methods 基线对比",
            "开放类别与旋转定位效果",
            "可靠性校准与查询稳定性",
            "系统延迟与案例证据",
        ]
        if is_remote_sensing_ovd
        else ["测试数据与指标设置", "多源融合效果验证", "跨工况诊断效果验证", "健康评分与案例回放", "系统性能与闭环测试"]
    )
    validation_body_priority = (
        [
            "公开基准与 base/novel/generalized 划分",
            "Grounding DINO、Detic、YOLO-World 和闭集上限对照",
            "HBB/OBB、小目标与细粒度结果",
            "ECE、Brier、高置信假阳性和同义查询一致性",
            "延迟、显存、证据卡与跨区域外测",
        ]
        if is_remote_sensing_ovd
        else ["数据来源与验证边界", "关键指标体系", "多源融合结果", "跨工况稳定性", "案例回放", "系统性能与闭环指标"]
    )
    validation_visual_priority = (
        ["数据集与 base/novel 划分图", "方法类别对照表", "HBB/OBB 结果表", "校准曲线与查询一致性图", "案例证据卡与延迟面板"]
        if is_remote_sensing_ovd
        else ["关键性能汇总表", "对比实验结果表", "案例回放时序图", "系统性能指标表"]
    )
    global_missing_materials = make_missing_materials(
        pending_confirmations + open_questions,
        impacted_chapter="全书规划",
        why_needed="这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。",
        suggested_backtrack_step="step1/step4",
        minimum_acceptable_substitute="在正文中显式标为待确认项，并降低结论强度。",
        priority="high",
    )

    def reference_for(title: str) -> dict[str, Any]:
        return reference_map.get(title, {})

    return [
        build_section(
            section_id="s1",
            heading="一、作品概述与问题定义",
            goal="讲清赛题背景、业务痛点、目标用户和项目切入问题，先把“为什么值得做”说透。",
            matched_scores=["创意", "应用价值"],
            narrative_role="用真实业务矛盾把项目拉进评委视野，避免作品书一开始就陷入模型堆砌。",
            position_logic="作为首个正文主体章节，本章必须先建立问题、对象和必要性，才能让后续总体方案与技术细节显得顺理成章。",
            chapter_weight_reason=f"当前项目判定为{work_type}，本章需要承担问题立论与用户场景落地职责，避免作品书一上来就堆技术名词。",
            predecessor_sections=[],
            successor_sections=["二、作品设计与总体架构"],
            sample_chapter=reference_for("选题背景").get("chapter", "第一章 作品概述"),
            sample_logic=reference_for("选题背景").get("logic", "先讲问题背景，再铺痛点与必要性。"),
            suggested_page_span=reference_for("选题背景").get("page_span", "4p"),
            suggested_word_budget=reference_for("选题背景").get("word_budget", "1200-2000"),
            subsections=["背景与赛题价值", "目标用户与问题场景", "业务痛点拆解"],
            structure_contract=build_structure_contract("s1", "一、作品概述与问题定义", ["背景与赛题价值", "目标用户与问题场景", "业务痛点拆解"]),
            body_priority=["问题紧迫性", "目标用户与使用动作", "现有流程代价", "项目切入必要性"],
            visual_priority=["背景趋势图", "问题链路图", "用户-痛点对应表"],
            appendix_candidates=["补充背景统计口径", "扩展案例或法规原文摘录"],
            key_messages=[
                template_alignment.get("opening_summary", ""),
                build_problem_focus_message(idea_card, target_users),
                "本章需要把“识别盲区”和“处置低效”两类问题同时讲清，给后文方案设计留足必要性。",
            ],
            must_include=[
                idea_card.get("problem", ""),
                *blind_spots,
                "目标用户为什么会在当前流程中持续承受漏检、误判和响应迟缓成本。",
            ],
            linked_innovations=[],
            linked_architecture=[],
            innovation_loop_map=[],
            evidence_ids=evidence_claim_map.get("problem_basis", []) + evidence_claim_map.get("fit_basis", []),
            evidence_index=evidence_index,
            recommended_visuals=["问题场景图", "背景趋势图", "目标用户与痛点对应表", "问题链路图"],
            visual_specs=build_visual_specs(
                section_id="s1",
                heading="一、作品概述与问题定义",
                chapter_number=1,
                subsections=["背景与赛题价值", "背景与赛题价值", "目标用户与问题场景", "业务痛点拆解"],
                visual_priority=["背景趋势图", "问题链路图", "用户-痛点对应表", "问题链路图"],
                recommended_visuals=["问题场景图", "背景趋势图", "目标用户与痛点对应表", "问题链路图"],
            ),
            common_errors=["背景写成社会议题口号", "只有风险描述，没有用户动作", "问题没有自然导向后文方案"],
            risks=["背景不能写成泛化社会议题口号", "不能只写识别难，还要写处置链路为何断裂"],
            pending_confirmations=pending_confirmations,
            missing_materials=global_missing_materials,
        ),
        build_section(
            section_id="s2",
            heading="二、作品设计与总体架构",
            goal="按作品书成稿口径交代总体设计、系统主线和输入输出闭环，让整体结构先成立，再展开细节。",
            matched_scores=["创意", "技术方案及其实现质量", "讲解表现"],
            narrative_role="承上启下，把前文的问题压缩为作品书中的总体设计与总体架构，避免正文长期停留在提案式说明口吻。",
            position_logic="本章承接问题定义，把前文痛点转成可运行系统的总体设计与总体架构，为后续关键技术和实现流程提供坐标。",
            chapter_weight_reason=f"针对{work_type}项目，本章是整部作品书的总图坐标；若总体设计与边界不清，后文技术章节会显得碎片化。",
            predecessor_sections=["一、作品概述与问题定义"],
            successor_sections=["三、核心创新与关键技术", "四、作品实现与运行闭环"],
            sample_chapter=reference_for("系统架构与工作流程").get("chapter", "第二章 作品设计与实现"),
            sample_logic=reference_for("系统架构与工作流程").get("logic", "先说明系统长什么样，再解释模块如何衔接。"),
            suggested_page_span=reference_for("系统架构与工作流程").get("page_span", "6p"),
            suggested_word_budget=reference_for("系统架构与工作流程").get("word_budget", "1800-2800"),
            subsections=["总体目标与设计原则", "系统总体架构", "输入-处理-输出闭环"],
            structure_contract=build_structure_contract("s2", "二、作品设计与总体架构", ["总体目标与设计原则", "系统总体架构", "输入-处理-输出闭环"]),
            body_priority=["总体目标与边界", "输入-处理-输出闭环", "模块职责", "人工介入位置"],
            visual_priority=["总体架构图", "数据流图", "MVP 边界图"],
            appendix_candidates=["模块接口字段表", "非核心扩展能力清单"],
            key_messages=[
                idea_card.get("solution_summary", ""),
                f"系统链路围绕 {join_cn(architecture)} 展开，先强调闭环，再逐层解释模块。",
                "本章必须主动说明 MVP 为何这样划定边界，哪些能力先落地、哪些能力作为后续扩展。",
            ],
            must_include=[
                idea_card.get("solution_summary", ""),
                "系统输入、核心处理链路、输出结果和人工介入位置。",
                "MVP 版本优先完成哪些能力，哪些能力属于后续扩展。",
            ],
            linked_innovations=[],
            linked_architecture=architecture,
            innovation_loop_map=[],
            evidence_ids=(
                evidence_claim_map.get("solution_basis", [])
                + evidence_claim_map.get("fit_basis", [])
                + evidence_claim_map.get("communication_basis", [])
            ),
            evidence_index=evidence_index,
            recommended_visuals=["总体架构图", "模块职责分层图", "输入-处理-输出闭环图", "多端联动部署图", "MVP 范围边界图"],
            visual_specs=build_visual_specs(
                section_id="s2",
                heading="二、作品设计与总体架构",
                chapter_number=2,
                subsections=["总体目标与设计原则", "系统总体架构", "输入-处理-输出闭环", "系统总体架构", "输入-处理-输出闭环"],
                visual_priority=["总体架构图", "数据流图", "MVP 边界图", "部署拓扑图", "MVP 边界图"],
                recommended_visuals=["总体架构图", "模块职责分层图", "输入-处理-输出闭环图", "多端联动部署图", "MVP 范围边界图"],
            ),
            common_errors=["只有总框图，没有输入输出闭环", "没有说明 MVP 范围", "把未来扩展能力写成当前已有能力"],
            risks=["如果没有总图，答辩时会显得碎片化", "方案边界不清会被追问当前版本与后续扩展的分界依据"],
            missing_materials=make_missing_materials(
                open_questions,
                impacted_chapter="二、作品设计与总体架构",
                why_needed="这些问题会影响系统边界、模块职责和 MVP 范围定义。",
                suggested_backtrack_step="step4",
                minimum_acceptable_substitute="在本章显式写明假设条件与暂不覆盖范围。",
                priority="high",
            ),
        ),
        build_section(
            section_id="s3",
            heading="三、核心创新与关键技术",
            goal="把创新点拆成可论证、可对应技术结构的章节，而不是停留在口号式命名。",
            matched_scores=["创意", "技术方案及其实现质量"],
            narrative_role=build_targeted_design_rationale(idea_card),
            position_logic="在总体方案已经建立后，本章负责回答“核心新东西到底是什么、为什么这样设计、落在什么技术抓手上”。",
            chapter_weight_reason=f"{work_type}项目的高分通常来自这一章与测试章形成的双重闭环，因此本章应承担创新定义、机制落点与技术解释的主要篇幅。",
            predecessor_sections=["二、作品设计与总体架构"],
            successor_sections=["四、作品实现与运行闭环", "五、测试与效果分析"],
            sample_chapter=reference_for("关键技术原理与实现").get("chapter", "第二章 作品设计与实现"),
            sample_logic=reference_for("关键技术原理与实现").get("logic", "先给总体概述，再分模块展开核心算法与工程实现。"),
            suggested_page_span=reference_for("关键技术原理与实现").get("page_span", "23p"),
            suggested_word_budget=reference_for("关键技术原理与实现").get("word_budget", "6000-10000"),
            subsections=["创新点总览", *innovation_display_titles, "创新与技术层映射"],
            structure_contract=build_structure_contract("s3", "三、核心创新与关键技术", ["创新点总览", *innovation_display_titles, "创新与技术层映射"]),
            body_priority=["创新点与痛点一一对应", "技术机制解释", "模块落点", "与系统结构映射"],
            visual_priority=["创新点-痛点对照表", "关键技术分层图", "原理流程图"],
            appendix_candidates=["公式推导", "扩展模块实现细节", "补充伪代码"],
            key_messages=[
                *innovation_summaries,
                "创新点必须一一落到识别难题、风险决策或展示联动上，不能和普通功能列表混在一起。",
            ],
            must_include=[
                *innovation_display_titles,
                *innovation_summaries,
                *architecture,
            ],
            linked_innovations=innovation_display_titles,
            linked_architecture=architecture,
            innovation_loop_map=build_innovation_loop_map(
                idea_card,
                current_section_role="提出本作品做法，并把创新点落到具体模块、机制或工程抓手上。",
                validation_anchor="五、测试与效果分析 / 创新性说明",
                expected_value_signal="相对基线的方法改进、消融贡献或系统能力增强",
            ),
            evidence_ids=evidence_claim_map.get("novelty_basis", []) + innovation_evidence_ids,
            evidence_index=evidence_index,
            recommended_visuals=["创新点-痛点对照表", *[f"{title}示意图" for title in innovation_display_titles], "关键技术分层图", "创新模块证据映射表"],
            visual_specs=build_visual_specs(
                section_id="s3",
                heading="三、核心创新与关键技术",
                chapter_number=3,
                subsections=["创新点总览", *innovation_display_titles, "创新与技术层映射", "创新与技术层映射"],
                visual_priority=["创新点-痛点对照表", "关键技术分层图", "原理流程图"],
                recommended_visuals=["创新点-痛点对照表", *[f"{title}示意图" for title in innovation_display_titles], "关键技术分层图", "创新模块证据映射表"],
            ),
            common_errors=["创新点只有命名没有机制", "创新点与实现模块重复叙述", "未区分技术亮点和核心创新"],
            risks=["创新点不能只剩命名，需要给出对应痛点和技术抓手", "需要区分创新点与实现模块，避免章节逻辑重复"],
            missing_materials=make_missing_materials(
                [item for item in innovation_display_titles if item] + open_questions,
                impacted_chapter="三、核心创新与关键技术",
                why_needed="创新章节要求每个创新点都有技术机制、实现落点和后续验证锚点。",
                suggested_backtrack_step="step4",
                minimum_acceptable_substitute="将尚未闭环的条目降级为功能亮点或待实现方向。",
                priority="high",
            ),
        ),
        build_section(
            section_id="s4",
            heading="四、作品实现与运行闭环",
            goal="把模块如何协同运行、数据如何流转和人工如何介入写具体，建立完成度感。",
            matched_scores=["技术方案及其实现质量", "讲解表现"],
            narrative_role="把抽象方案落到工程链路，回答“这个系统究竟怎么跑起来”。",
            position_logic="本章位于创新与应用之间，负责把前章的机制变成可运行流程，证明项目不只是概念图和模块名。",
            chapter_weight_reason=f"对于{work_type}项目，本章决定评委对完成度的直观判断，尤其影响“实现质量”和“讲解表现”。",
            predecessor_sections=["二、作品设计与总体架构", "三、核心创新与关键技术"],
            successor_sections=["五、测试与效果分析", "六、应用前景与落地价值"],
            sample_chapter=reference_for("系统功能与界面").get("chapter", "第二章 作品设计与实现"),
            sample_logic=reference_for("系统功能与界面").get("logic", "先给用户可见界面和操作，再解释运行流程。"),
            suggested_page_span=reference_for("系统功能与界面").get("page_span", "4p"),
            suggested_word_budget=reference_for("系统功能与界面").get("word_budget", "1000-1800"),
            subsections=["模块实现说明", "运行流程", "案例回放与人工复核"],
            structure_contract=build_structure_contract("s4", "四、作品实现与运行闭环", ["模块实现说明", "运行流程", "案例回放与人工复核"]),
            body_priority=["模块协同关系", "运行流程", "人工复核与回放机制", "可运行性证明"],
            visual_priority=["运行流程图", "时序图", "界面截图或模块接口表"],
            appendix_candidates=["接口协议", "详细运行日志", "工程参数配置"],
            key_messages=[
                "系统运行主线是采集、理解、评分、告警、复核，重点说明每一步如何承接前一步结果。",
                *implementation,
                "本章要主动体现作品是可运行 MVP，而不是只有概念框图。",
            ],
            must_include=[
                "多模态数据接入方式和统一表征思路。",
                "风险评分与预警生成逻辑。",
                "人工复核、案例留痕和展示联动如何进入闭环。",
                *implementation,
            ],
            linked_innovations=[title for title in innovation_titles if "预警" in title or "联动" in title or "一致性" in title],
            linked_architecture=architecture,
            innovation_loop_map=build_innovation_loop_map(
                idea_card,
                current_section_role="把前章创新机制落成运行流程、接口交互和工程实现闭环。",
                validation_anchor="五、测试与效果分析 / 六、应用前景与落地价值",
                expected_value_signal="流程可运行、模块可协作、系统可演示",
            ),
            evidence_ids=evidence_claim_map.get("solution_basis", []) + innovation_evidence_ids,
            evidence_index=evidence_index,
            recommended_visuals=["统一表征与接入链路图", "运行流程图", "评分与告警链路图", "模块接口表", "案例流转时序图", "多端工作台示意"],
            visual_specs=build_visual_specs(
                section_id="s4",
                heading="四、作品实现与运行闭环",
                chapter_number=4,
                subsections=["模块实现说明", "运行流程", "运行流程", "模块实现说明", "案例回放与人工复核", "案例回放与人工复核"],
                visual_priority=["运行流程图", "时序图", "界面截图或模块接口表"],
                recommended_visuals=["统一表征与接入链路图", "运行流程图", "评分与告警链路图", "模块接口表", "案例流转时序图", "多端工作台示意"],
            ),
            common_errors=["只有模块清单没有流程", "流程图与正文不一致", "把尚未实现的能力写成已完成功能"],
            risks=["只有模块名没有运行逻辑会显得完成度不足", "需要避免把未来扩展能力误写成当前已实现功能"],
            missing_materials=make_missing_materials(
                implementation + open_questions,
                impacted_chapter="四、作品实现与运行闭环",
                why_needed="实现章节需要明确系统当前能跑到哪一步、哪些能力已具备、哪些仍是规划。",
                suggested_backtrack_step="step4",
                minimum_acceptable_substitute="用 MVP 范围说明替代完整实现承诺，并标出人工介入位置。",
                priority="medium",
            ),
        ),
        build_section(
            section_id="s_validation",
            heading="五、测试与效果分析",
            goal="围绕关键性能、对比实验、复杂场景稳定性和系统闭环指标，形成与创新点一一对应的验证链，而不是只在结尾补几条结果。",
            matched_scores=["技术方案及其实现质量", "创意", "讲解表现"],
            narrative_role="把前文提出的创新点和系统闭环转成可被评委验证的结果证据，形成“创新提出 - 机制实现 - 效果证明”的完整闭环。",
            position_logic="本章位于系统实现之后、应用价值之前，负责回答“作品做出来以后到底是否有效、稳定、可运行”。",
            chapter_weight_reason=f"{work_type}项目若缺少正式测试章，创新与实现很难转化为可信的评审印象，因此本章必须承担关键证据链的组织任务。",
            predecessor_sections=["三、核心创新与关键技术", "四、作品实现与运行闭环"],
            successor_sections=["六、应用前景与落地价值"],
            sample_chapter=validation_reference.get("section", "第三章 作品测试与分析"),
            sample_logic=(
                "先冻结公开基准、base/novel 划分和提示词协议，再按基线对比、旋转定位、可靠性校准、查询稳定性和系统案例展开分析。"
                if is_remote_sensing_ovd
                else "先交代测试数据与指标设置，再按多源融合、跨工况、案例回放和系统闭环展开分析。"
            ),
            suggested_page_span="4-6p",
            suggested_word_budget="2200-3600",
            subsections=validation_subsections,
            structure_contract=build_structure_contract("s_validation", "五、测试与效果分析", validation_subsections),
            body_priority=validation_body_priority,
            visual_priority=validation_visual_priority,
            appendix_candidates=["补充实验说明", "扩展曲线图", "更多案例回放截图"],
            key_messages=[
                validation_summary or "测试章需要把指标口径、对比实验、复杂场景稳定性和系统性能补齐。",
                validation_disclosure or "测试章必须说明公开数据、仿真工况和原型日志各自承担什么验证任务。",
                "每个核心创新至少要在本章找到一个对应的实验、案例或系统级指标支撑。",
            ],
            must_include=[
                validation_disclosure or "验证数据的来源边界与适用范围说明。",
                "关键指标汇总与对应含义说明。",
                "对比实验设置、结果和结论解释。",
                "复杂场景稳定性或跨工况表现说明。",
                "系统时延、吞吐、闭环完成率等系统级结果。",
                *validation_metric_labels,
                *validation_experiment_titles,
            ],
            linked_innovations=innovation_display_titles,
            linked_architecture=architecture,
            innovation_loop_map=build_innovation_loop_map(
                idea_card,
                current_section_role="用指标、实验、案例和系统级性能把前文创新点落实为可验证结果。",
                validation_anchor="五、测试与效果分析",
                expected_value_signal="指标改善、稳定性提升、闭环效率与系统性能",
            ),
            evidence_ids=evidence_claim_map.get("solution_basis", []) + evidence_claim_map.get("novelty_basis", []),
            evidence_index=evidence_index,
            recommended_visuals=validation_assets or validation_visual_priority,
            visual_specs=build_visual_specs(
                section_id="s_validation",
                heading="五、测试与效果分析",
                chapter_number=5,
                subsections=validation_subsections,
                visual_priority=validation_visual_priority,
                recommended_visuals=validation_assets or validation_visual_priority,
            ),
            common_errors=["只罗列几个好看的数字", "没有交代指标口径和数据边界", "把系统性能和分类效果混在一起", "把仿真示例值写成真实实测结果"],
            risks=["测试章必须显式说明数据来源边界", "每项创新若没有对应实验或案例支撑，会削弱前文创新说服力"],
            missing_materials=make_missing_materials(
                validation_assets + open_questions,
                impacted_chapter="五、测试与效果分析",
                why_needed="测试章要求结果、图表和案例回放一起构成完整证据链。",
                suggested_backtrack_step="step4",
                minimum_acceptable_substitute="至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。",
                priority="high",
            ),
            chapter_seed_payload={
                "seed_type": "validation_support_pack",
                "enabled": validation_ready,
                "pack": validation_pack,
            },
        ),
        build_section(
            section_id="s5",
            heading="六、应用前景与落地价值",
            goal="讲清系统给谁用、在什么情境里用、具体带来什么收益，并兼顾答辩展示价值。",
            matched_scores=["应用价值", "讲解表现"],
            narrative_role="把技术能力翻译成可落地价值，避免作品书后半段只剩技术术语。",
            position_logic="在已经说明技术与实现之后，本章把能力翻译成场景、动作与收益，回答“为什么真的值得用”。",
            chapter_weight_reason=f"{work_type}项目通常会在应用价值上被重点追问，因此本章必须把用户、流程、收益和展示价值说具体。",
            predecessor_sections=["五、测试与效果分析"],
            successor_sections=["七、总结与展望"],
            sample_chapter=reference_for("应用前景").get("chapter", "第一章 作品概述"),
            sample_logic=reference_for("应用前景").get("logic", "在技术说明之后回到落地场景，明确用户收益与部署前景。"),
            suggested_page_span=reference_for("应用前景").get("page_span", "4p"),
            suggested_word_budget=reference_for("应用前景").get("word_budget", "1000-1600"),
            subsections=["目标用户与典型场景", "业务收益与竞争优势", "比赛展示价值"],
            structure_contract=build_structure_contract("s5", "六、应用前景与落地价值", ["目标用户与典型场景", "业务收益与竞争优势", "比赛展示价值"]),
            body_priority=["典型场景", "用户动作", "收益闭环", "展示价值"],
            visual_priority=["场景矩阵图", "部署流程图", "价值闭环图"],
            appendix_candidates=["扩展业务流程", "成本收益测算假设"],
            key_messages=[
                f"应用场景聚焦 {join_cn(application_scenarios)}，每类用户都需要对应一条清晰的使用动作。",
                *idea_card.get("business_value", []),
                *idea_card.get("competitive_advantages", []),
            ],
            must_include=[
                *application_scenarios,
                *idea_card.get("business_value", []),
                *idea_card.get("competitive_advantages", []),
            ],
            linked_innovations=[],
            linked_architecture=[],
            innovation_loop_map=[],
            evidence_ids=evidence_claim_map.get("fit_basis", []) + evidence_claim_map.get("communication_basis", []),
            evidence_index=evidence_index,
            recommended_visuals=["应用场景矩阵", "角色-动作-收益表", "预警工单联动流程图", "价值闭环图", "答辩展示页示意"],
            visual_specs=build_visual_specs(
                section_id="s5",
                heading="六、应用前景与落地价值",
                chapter_number=6,
                subsections=["目标用户与典型场景", "目标用户与典型场景", "业务收益与竞争优势", "业务收益与竞争优势", "比赛展示价值"],
                visual_priority=["场景矩阵图", "部署流程图", "价值闭环图"],
                recommended_visuals=["应用场景矩阵", "角色-动作-收益表", "预警工单联动流程图", "价值闭环图", "答辩展示页示意"],
            ),
            common_errors=["应用场景只有名词没有流程", "价值只有口号没有收益路径", "把商业化愿景当成当前落地能力"],
            risks=["应用价值不能只写口号，必须落到具体用户收益", "需要兼顾业务落地与比赛展示，不要只写商业化想象"],
            missing_materials=make_missing_materials(
                application_scenarios + idea_card.get("business_value", []),
                impacted_chapter="六、应用前景与落地价值",
                why_needed="应用章节必须说明给谁用、怎么用、用了以后有什么变化。",
                suggested_backtrack_step="step4",
                minimum_acceptable_substitute="至少给出 2-3 个典型角色及其使用动作链。",
                priority="medium",
            ),
        ),
        build_section(
            section_id="s6",
            heading="七、总结与展望",
            goal="用作品书收束口径总结当前成果、边界与后续展望，避免把尾章写成项目排期表或提案附页。",
            matched_scores=["技术方案及其实现质量", "应用价值"],
            narrative_role="用作品书定稿口径收束全书，说明作品已经形成的能力、系统特色和后续优化方向。",
            position_logic="作为收束章节，本章负责总结作品完成情况、系统价值与不足展望，避免尾章写成项目计划或内部待办说明。",
            chapter_weight_reason=f"对于{work_type}项目，本章不是附属排期页，而是成熟度说明；它直接影响评委对项目完成度与延展性的判断。",
            predecessor_sections=["六、应用前景与落地价值"],
            successor_sections=[],
            sample_chapter=reference_for("总结与展望").get("chapter", "第五章 总结与展望"),
            sample_logic=reference_for("总结与展望").get("logic", "收束作品完成情况，明确系统特色、当前不足和后续优化方向。"),
            suggested_page_span="1-2p",
            suggested_word_budget="800-1400",
            subsections=["作品完成情况", "系统特色与应用价值", "不足与后续优化"],
            structure_contract=build_structure_contract("s6", "七、总结与展望", ["作品完成情况", "系统特色与应用价值", "不足与后续优化"]),
            body_priority=["完成情况", "系统特色", "应用价值", "不足与后续方向"],
            visual_priority=["完成情况对照表", "系统价值闭环图", "优化方向图"],
            appendix_candidates=["详细排期表", "资源依赖表"],
            key_messages=[
                *implementation,
                *open_questions,
                template_alignment.get("closing_summary", ""),
            ],
            must_include=[
                *implementation,
                "作品已经形成的闭环能力与交付形态。",
                "系统特色、应用价值和交付成熟度。",
                "当前不足与后续优化方向。",
            ],
            linked_innovations=[],
            linked_architecture=architecture,
            innovation_loop_map=[],
            evidence_ids=evidence_claim_map.get("solution_basis", []) + evidence_claim_map.get("fit_basis", []),
            evidence_index=evidence_index,
            recommended_visuals=["完成情况对照表", "系统价值闭环图", "优化方向图"],
            visual_specs=build_visual_specs(
                section_id="s6",
                heading="七、总结与展望",
                chapter_number=7,
                subsections=["作品完成情况", "系统特色与应用价值", "不足与后续优化"],
                visual_priority=["完成情况对照表", "系统价值闭环图", "优化方向图"],
                recommended_visuals=["完成情况对照表", "系统价值闭环图", "优化方向图"],
            ),
            common_errors=["把尾章写成项目排期表", "把远期愿景写成当前承诺", "总结章节仍在解释写作边界"],
            risks=["不要把远期愿景写成当前交付承诺", "需要明确物联网侧接入边界，避免被追问概念不落地"],
            pending_confirmations=[],
            missing_materials=global_missing_materials,
        ),
    ]


def build_score_coverage(spec: dict[str, Any], sections: list[dict[str, Any]]) -> dict[str, Any]:
    dimensions = spec.get("scoring_dimensions", [])
    covered: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for dimension in dimensions:
        matched_sections = [
            {"section_id": section["section_id"], "heading": section["heading"]}
            for section in sections
            if dimension in section["matched_scores"]
        ]
        item = {"dimension": dimension, "sections": matched_sections}
        if matched_sections:
            covered.append(item)
        else:
            gaps.append(item)
    return {"dimensions": dimensions, "covered": covered, "gaps": gaps}


def render_outline(spec: dict[str, Any], idea_card: dict[str, Any], sections: list[dict[str, Any]]) -> str:
    work_type, work_type_reason = infer_work_type(idea_card)
    lines = [
        "# Proposal Outline",
        "",
        f"- Project Name: {idea_card.get('project_name', '')}",
        f"- Competition: {spec.get('competition_name', '')}",
        f"- Inferred Work Type: {work_type}",
        f"- Work Type Reason: {work_type_reason}",
        f"- Scoring Dimensions: {join_cn(spec.get('scoring_dimensions', []))}",
        f"- Deliverable Constraint: {spec.get('submission_format', '')}",
        "",
    ]
    for section in sections:
        lines.extend(
            [
                f"## {section['heading']}",
                "",
                f"- Goal: {section['goal']}",
                f"- Narrative Role: {section['narrative_role']}",
                f"- Position Logic: {section['position_logic']}",
                f"- Chapter Weight Reason: {section['chapter_weight_reason']}",
                f"- Matched Scores: {join_cn(section['matched_scores'])}",
                f"- Sample Reference: {section['sample_chapter']} / {section['sample_logic']}",
                f"- Suggested Length: {section['suggested_page_span']} / {section['suggested_word_budget']} 字",
                f"- Previous Sections: {join_cn(section['predecessor_sections']) or 'none'}",
                f"- Next Sections: {join_cn(section['successor_sections']) or 'none'}",
                "- Subsections:",
            ]
        )
        lines.extend([f"  - {item}" for item in section["subsections"]])
        contract = section.get("structure_contract", {})
        if contract:
            lines.append("- Structure Contract:")
            lines.append(f"  - Required second-level count: {contract.get('required_second_level_count', 0)}")
            lines.append(f"  - Required third-level total min: {contract.get('required_third_level_total_min', 0)}")
            for item in contract.get("second_level_contracts", []):
                lines.append(
                    f"  - {item.get('title', '')}: must contain {item.get('required_third_level_count', 0)} third-level headings -> "
                    f"{join_cn(item.get('required_third_level_titles', []))}"
                )
        lines.append("- Body Priorities:")
        lines.extend([f"  - {item}" for item in section["body_priority"]])
        lines.append("- Visual Priorities:")
        lines.extend([f"  - {item}" for item in section["visual_priority"]])
        lines.append("- Key Messages:")
        lines.extend([f"  - {item}" for item in section["key_messages"]])
        lines.append("- Must Include:")
        lines.extend([f"  - {item}" for item in section["must_include"]])
        if section["linked_innovations"]:
            lines.append("- Linked Innovations:")
            lines.extend([f"  - {item}" for item in section["linked_innovations"]])
        if section["linked_architecture"]:
            lines.append("- Linked Architecture:")
            lines.extend([f"  - {item}" for item in section["linked_architecture"]])
        if section["supporting_evidence"]:
            lines.append("- Key Evidence:")
            for evidence in section["supporting_evidence"]:
                summary = shorten(evidence.get("derived_insight") or evidence.get("summary") or evidence.get("claim", ""))
                source = evidence.get("source", "")
                reliability = evidence.get("reliability", "")
                evidence_kind = evidence.get("evidence_kind", "")
                source_authority = evidence.get("source_authority", "")
                supports = join_cn(evidence.get("supports", []))
                lines.append(
                    f"  - [{evidence['evidence_id']}] {summary} | kind={evidence_kind or 'unknown'} | authority={source_authority or 'unknown'} | source={source or 'unknown'} | reliability={reliability or 'unknown'} | supports={supports or 'none'}"
                )
        lines.append("- Recommended Visuals:")
        lines.extend([f"  - {item}" for item in section["recommended_visuals"]])
        if section.get("visual_specs"):
            lines.append("- Visual Specs:")
            for item in section["visual_specs"]:
                lines.append(
                    f"  - [{item['label']}] {item['title']} | type={item['visual_type']} | purpose={item['purpose']} | anchor={item['placement_anchor']} | subsection={item['suggested_subsection']}"
                )
        if section["innovation_loop_map"]:
            lines.append("- Innovation Loop Map:")
            for item in section["innovation_loop_map"]:
                lines.append(
                    f"  - {item['innovation_title']}: role={item['current_section_role']}; validation={item['validation_anchor']}; signal={item['expected_value_signal']}"
                )
        lines.append("- Risks:")
        lines.extend([f"  - {item}" for item in section["risks"]])
        lines.append("- Common Errors:")
        lines.extend([f"  - {item}" for item in section["common_errors"]])
        lines.append("- Appendix Candidates:")
        lines.extend([f"  - {item}" for item in section["appendix_candidates"]])
        if section["pending_confirmations"]:
            lines.append("- Pending Confirmations:")
            lines.extend([f"  - {item}" for item in section["pending_confirmations"]])
        if section["missing_materials"]:
            lines.append("- Missing Materials:")
            for item in section["missing_materials"]:
                lines.append(
                    f"  - {item['missing_item']} | impact={item['impacted_chapter']} | backtrack={item['suggested_backtrack_step']} | priority={item['priority']}"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


def render_reference_template(reference_template: dict[str, Any]) -> str:
    lines = [
        "# Proposal Reference Template",
        "",
        f"- Reference Name: {reference_template.get('reference_name', '')}",
        f"- Reference Source: {reference_template.get('reference_source', '')}",
        "",
        "## Notes",
    ]
    lines.extend([f"- {item}" for item in reference_template.get("notes", [])] or ["- none"])
    lines.extend(["", "## Global Structure"])
    for item in reference_template.get("global_structure", []):
        lines.append(
            f"- {item.get('section', '')}: {item.get('page_span', '')}, suggested words {item.get('word_budget', '')}"
        )
    lines.extend(["", "## Chapter Logic"])
    for chapter in reference_template.get("chapter_logic", []):
        lines.append(f"### {chapter.get('chapter', '')}")
        lines.append(f"- Logic: {chapter.get('logic', '')}")
        for section in chapter.get("sections", []):
            lines.append(
                f"- {section.get('title', '')}: {section.get('page_span', '')}, suggested words {section.get('word_budget', '')}"
            )
        lines.append("")
    lines.extend(["## Subsection Budget Rules"])
    for item in reference_template.get("subsection_budget_rules", []):
        lines.append(f"- {item.get('type', '')}: {item.get('word_budget', '')}")
    lines.extend(["", "## Page Density Rules"])
    for item in reference_template.get("page_density_rules", []):
        lines.append(f"- {item.get('layout_type', '')}: {item.get('word_budget', '')}")
    lines.append("")
    return "\n".join(lines)


def update_workspace_state(topic_dir: Path, structure_gate: dict[str, Any]) -> None:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not state_path.exists():
        return
    state = read_json(state_path)
    passed = structure_gate.get("verdict") == "pass"
    state["workflow_status"]["document_plan"] = "completed" if passed else "blocked"
    state["workflow_status"]["document_writing"] = "active" if passed else "pending"
    write_json(state_path, state)
    if passed:
        sync_workspace_state(
            topic_dir,
            step="document_writing",
            workflow_status="active",
            next_action="run_document_writing",
            required_inputs=[
                "workspace/document_plan/section-plan.json",
                "workspace/document_plan/reference-template.md",
                "workspace/document_plan/outline-structure-gate.json",
            ],
            resume_entrypoint="workspace/document_plan/section-plan.json",
            last_completed_artifact="workspace/document_plan/outline-structure-gate.json",
            active_focus="将 Step5 大纲切换为逐章多 agent 写作输入",
            current_direction="使用 Step5 模板信息驱动 Step6 的真实 LLM 逐章写作流",
        )
    else:
        sync_workspace_state(
            topic_dir,
            step="document_plan",
            workflow_status="blocked",
            next_action="rerun_document_plan",
            required_inputs=[
                "workspace/document_plan/outline-structure-gate.json",
                "workspace/document_plan/outline-structure-report.md",
            ],
            resume_entrypoint="workspace/document_plan/outline-structure-gate.json",
            last_completed_artifact="workspace/document_plan/outline-structure-gate.json",
            active_focus="Step5 目录结构 gate 未通过",
            current_direction="先重编排目录结构，再进入 Step6 正文写作",
            blocking_reason="Step5 outline structure gate failed.",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AutoSearch MVP planning proposal outline.")
    parser.add_argument("topic_dir", help="Topic directory, such as sample/topic_xx")
    parser.add_argument("--topic", default="", help="Optional topic override. Defaults to workspace topic_name.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    ensure_state_scaffold(topic_dir)
    step_dir = topic_dir / "workspace" / "document_plan"
    spec_path = topic_dir / "workspace" / "requirements" / "competition-spec.json"
    card_path = topic_dir / "workspace" / "concept" / "idea-card.json"
    evidence_path = topic_dir / "workspace" / "ideas" / "evidence-ledger.json"
    research_gate_path = topic_dir / "workspace" / "research" / "research-gate.json"
    research_brief_path = topic_dir / "workspace" / "research" / "research-brief.json"

    if not spec_path.exists() or not card_path.exists():
        raise SystemExit("Missing step inputs for document_plan.")
    if not research_gate_path.exists():
        raise SystemExit("Missing research-gate.json. Run run_research.py before document planning.")
    research_gate = read_json(research_gate_path)
    if research_gate.get("verdict") != "pass":
        raise SystemExit("Automatic research gate is not passed; complete research evidence before document planning.")
    if not research_brief_path.exists():
        raise SystemExit("Missing research-brief.json. Run run_research.py before document planning.")
    research_brief = read_json(research_brief_path)

    idea_card = read_json(card_path)
    idea_card["research_brief"] = research_brief
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
    spec = read_json(spec_path)
    reference_template = load_json_template("proposal-reference.template.json")
    evidence_index = build_evidence_index(read_json(evidence_path)) if evidence_path.exists() else {}
    sections = build_sections(spec, idea_card, evidence_index, reference_template)
    content_contract = dict(DEFAULT_CONTRACT)
    allocate_budgets(sections, content_contract)
    # A research proposal reserves most prose for mechanisms and evaluation.
    # Budgets are fixed before writing; never fit thresholds to a short draft.
    profile_id = (idea_card.get("topic_profile") or {}).get("profile_id", "")
    if profile_id == "remote_sensing_open_vocabulary_detection":
        minima = dict(s1=2400, s2=1300, s3=1450, s4=2500, s_validation=4000, s5=1100, s6=11250)
        for section in sections:
            value = minima[section["section_id"]]
            section["suggested_word_budget"] = f"{value}-{round(value * 4 / 3)}"
            # The fifth application visual is a real presentation panel; keep
            # the title explicit so the case/UI visual quota is auditable.
            if section["section_id"] == "s5":
                for visual in section.get("visual_specs", []):
                    if visual.get("visual_id") == "s5_visual_5":
                        visual["title"] = "竞赛答辩演示界面板"
            if section["section_id"] == "s2":
                for visual in section.get("visual_specs", []):
                    if visual.get("visual_id") == "s2_mvp":
                        visual["title"] = "最小可行范围边界图"
    coverage = build_score_coverage(spec, sections)
    outline = render_outline(spec, idea_card, sections)
    reference_text = render_reference_template(reference_template)
    work_type, work_type_reason = infer_work_type(idea_card)
    structure_gate = validate_structure_contracts(sections)

    write_text(step_dir / "outline.md", outline)
    write_text(step_dir / "reference-template.md", reference_text)
    write_text(step_dir / "outline-structure-report.md", render_structure_gate_report(structure_gate))
    write_json(
        step_dir / "section-plan.json",
        {
            "project_name": idea_card.get("project_name", ""),
            "competition_name": spec.get("competition_name", ""),
            "work_type": work_type,
            "work_type_reason": work_type_reason,
            "skill_reference": {
                "path": "works_book_writing_skill.md",
                "role": "planning_writing_shared_writing_spec",
            },
            "scoring_dimensions": spec.get("scoring_dimensions", []),
            "reference_template": reference_template,
            "outline_structure_gate": structure_gate,
            "research_gate": research_gate,
            "research_brief": research_brief,
            "sections": sections,
            "content_contract": content_contract,
        },
    )
    write_json(step_dir / "score-coverage.json", coverage)
    write_json(step_dir / "outline-structure-gate.json", structure_gate)
    update_workspace_state(topic_dir, structure_gate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

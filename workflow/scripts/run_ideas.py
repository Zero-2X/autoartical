#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from topic_profiles import build_profile_ideas, collect_all_profile_keywords, resolve_topic_profile


REPO_ROOT = Path(__file__).resolve().parents[2]
IDEA_REGISTRY_PATH = REPO_ROOT / "sample" / "databases" / "ideas" / "idea-registry.json"

SIMILARITY_KEYWORDS = [
    "多模态",
    "短视频",
    "舆情",
    "风险",
    "监测",
    "预警",
    "治理",
    "物联网",
    "内容安全",
    "传播",
    "平台",
    "审核",
    "真实性",
] + collect_all_profile_keywords()

IDEA_FOCUS_MAP = {
    "idea_a": {
        "focus_tags": ["风险", "预警", "监测", "反讽", "审核", "内容安全"],
        "focus_summary": "风险识别与预警闭环",
    },
    "idea_b": {
        "focus_tags": ["真实性", "传播", "平台", "审核"],
        "focus_summary": "真实性与叙事一致性校验",
    },
    "idea_c": {
        "focus_tags": ["传播", "舆情", "风险", "预警"],
        "focus_summary": "传播势能评估与干预决策",
    },
}

EVIDENCE_HINT_MAP = {
    "反讽": ["反讽", "sarcasm", "情感", "中文", "玩梗", "多模态冲突"],
    "情绪": ["情感", "反讽", "中文", "多模态"],
    "一致性": ["一致性", "虚假信息", "评论", "字幕", "社会上下文", "短视频"],
    "叙事": ["叙事", "虚假信息", "评论", "字幕", "社会上下文"],
    "配文": ["字幕", "评论", "虚假信息", "短视频"],
    "真伪": ["虚假信息", "谣言识别", "可核查性", "社会上下文"],
    "预警": ["风险", "监测", "审核", "人工介入", "流水线"],
    "分级": ["风险", "审核", "人工介入", "流水线"],
    "处置": ["人工介入", "流水线", "审核", "演示"],
    "介入": ["人工介入", "流水线", "审核"],
    "传播": ["传播", "社会上下文", "平台", "风险"],
    "势能": ["传播", "风险", "平台", "监测"],
    "节点": ["传播", "社会上下文", "平台"],
    "展示": ["演示", "排版模板", "平台", "治理"],
    "答辩": ["演示", "排版模板", "平台"],
    "回放": ["演示", "平台"],
    "沙盘": ["传播", "演示", "平台"],
}


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


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword.lower() in text.lower() for keyword in keywords)


def load_registry() -> list[dict]:
    if not IDEA_REGISTRY_PATH.exists():
        write_json(IDEA_REGISTRY_PATH, {"ideas": []})
    return read_json(IDEA_REGISTRY_PATH).get("ideas", [])


def load_context_text(topic_dir: Path) -> str:
    assets_path = topic_dir / "workspace" / "intake" / "topic-assets.json"
    if not assets_path.exists():
        return ""
    assets = read_json(assets_path)
    return "\n".join(assets.get("rules", []) + assets.get("references", []) + assets.get("samples", []))


def gather_relevant_evidence(ledger: dict, role: str = "") -> list[dict]:
    items = ledger.get("evidence_items", [])
    if not role:
        return items
    return [item for item in items if item.get("source_role") == role]


def filter_format_evidence(items: list[dict]) -> list[dict]:
    return [item for item in items if item.get("source_role") != "format_reference"]


def evidence_text(item: dict) -> str:
    return " ".join(item.get("tags", []) + [item.get("claim", ""), item.get("summary", ""), item.get("source_title", "")]).lower()


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def select_evidence_ids(items: list[dict], tag_candidates: list[str], limit: int = 3) -> list[str]:
    selected: list[str] = []
    lowered = [tag.lower() for tag in tag_candidates]
    for item in items:
        haystack = evidence_text(item)
        if any(tag in haystack for tag in lowered):
            selected.append(item["evidence_id"])
        if len(selected) >= limit:
            break
    if not selected:
        selected = [item["evidence_id"] for item in items[:limit]]
    return selected


def contains_keyword(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def find_item_by_id(ledger: dict, evidence_id: str) -> dict | None:
    for item in ledger.get("evidence_items", []):
        if item.get("evidence_id") == evidence_id:
            return item
    return None


def choose_focus_profile(idea: dict) -> dict:
    explicit_summary = str(idea.get("focus_summary", "")).strip()
    if explicit_summary:
        focus_tags = dedupe_preserve_order(
            [
                *idea.get("core_innovations", [])[:2],
                explicit_summary,
                idea.get("project_name", ""),
            ]
        )
        return {
            "focus_tags": focus_tags,
            "focus_summary": explicit_summary,
        }
    profile = IDEA_FOCUS_MAP.get(idea.get("idea_id", ""), {})
    if profile:
        return profile
    return {
        "focus_tags": idea.get("core_innovations", [])[:2],
        "focus_summary": "通用方向",
    }


def attach_evidence(idea: dict, ledger: dict) -> dict:
    rule_items = gather_relevant_evidence(ledger, "rule")
    domain_items = filter_format_evidence(
        [item for item in ledger.get("evidence_items", []) if item.get("source_role") in {"reference", "external_research", "seed_direction", "sample"}]
    )
    sample_items = gather_relevant_evidence(ledger, "sample")
    format_items = gather_relevant_evidence(ledger, "format_reference")
    focus_profile = choose_focus_profile(idea)
    keywords = focus_profile["focus_tags"] + idea.get("core_innovations", []) + [idea.get("project_name", ""), idea.get("problem", "")]

    problem_basis = select_evidence_ids(domain_items or rule_items, focus_profile["focus_tags"] + [idea.get("problem", "")], limit=2)
    solution_basis = select_evidence_ids(domain_items or rule_items, keywords, limit=3)
    fit_basis = [item["evidence_id"] for item in rule_items[:2]]
    novelty_basis = select_evidence_ids(domain_items, focus_profile["focus_tags"] + idea.get("core_innovations", []), limit=2)
    communication_basis = select_evidence_ids(format_items + sample_items, ["格式参考", "演示", "平台"] + focus_profile["focus_tags"], limit=2)
    idea["evidence_refs"] = list(dict.fromkeys(problem_basis + solution_basis + fit_basis + communication_basis))
    idea["analysis_basis"] = {
        "problem_basis": problem_basis,
        "solution_basis": solution_basis,
        "fit_basis": fit_basis,
        "novelty_basis": novelty_basis,
        "communication_basis": communication_basis,
    }
    idea["focus_summary"] = focus_profile["focus_summary"]
    idea["inference_notes"] = [
        "候选 idea 的命名和模块拆分属于系统推演，不是源材料中的直接表述。",
        "如果 evidence 不能支撑某个 claim，该 claim 只能降级为待验证假设。",
    ]
    if not problem_basis or not solution_basis:
        idea["inference_notes"].append("当前方向的领域证据仍偏少，后续需要补充外部论文、案例或行业材料。")
    idea["evidence_ref_details"] = [
        {
            "evidence_id": evidence_id,
            "source_role": (find_item_by_id(ledger, evidence_id) or {}).get("source_role", ""),
        }
        for evidence_id in idea["evidence_refs"]
    ]
    return idea


def infer_innovation_keywords(block: dict, idea: dict) -> list[str]:
    text = " ".join([block.get("title", ""), block.get("summary", "")])
    keywords: list[str] = []
    for anchor, hinted_keywords in EVIDENCE_HINT_MAP.items():
        if anchor in text:
            keywords.extend(hinted_keywords)
    if not keywords:
        keywords.extend(idea.get("core_innovations", [])[:2])
    keywords.extend(idea.get("theme_keywords", []))
    return dedupe_preserve_order(keywords)


def score_block_evidence(item: dict, keywords: list[str], preferred_ids: list[str], allow_format: bool = False) -> int:
    if item.get("source_role") == "format_reference" and not allow_format:
        return -100
    if item.get("source_role") == "seed_direction":
        return -100
    haystack = evidence_text(item)
    score = 0
    for keyword in keywords:
        if keyword.lower() in haystack:
            score += 3
    if item.get("evidence_id") in preferred_ids:
        score += 4
    if item.get("source_role") == "external_research":
        score += 2
    if item.get("source_role") == "sample":
        score += 1
    if item.get("source_role") == "rule":
        score -= 3 if not allow_format else 0
    if allow_format and item.get("source_role") == "format_reference":
        score += 6
    return score


def summarize_block_rationale(title: str, evidence_titles: list[str]) -> str:
    joined = "、".join(evidence_titles)
    if "反讽" in title or "情绪" in title:
        return f"{joined} 共同支撑该模块对隐性情绪与反话表达的识别论证。"
    if "一致性" in title or "叙事" in title or "真伪" in title or "配文" in title:
        return f"{joined} 共同支撑该模块对跨模态叙事错位与误导风险的识别论证。"
    if "预警" in title or "分级" in title or "处置" in title or "介入" in title:
        return f"{joined} 共同支撑该模块把识别结果转成分级预警与人工介入建议。"
    if "传播" in title or "势能" in title or "节点" in title or "沙盘" in title:
        return f"{joined} 共同支撑该模块对传播态势研判和决策支撑的设计。"
    if "展示" in title or "答辩" in title or "回放" in title:
        return f"{joined} 共同支撑该模块在答辩展示与业务讲解中的表达方式。"
    return f"{joined} 共同支撑该模块的系统设计与论证边界。"


def build_innovation_evidence_map(idea: dict, ledger: dict) -> list[dict]:
    evidence_items = ledger.get("evidence_items", [])
    analysis_basis = idea.get("analysis_basis", {})
    solution_ids = analysis_basis.get("solution_basis", [])
    novelty_ids = analysis_basis.get("novelty_basis", [])
    communication_ids = analysis_basis.get("communication_basis", [])
    fit_ids = analysis_basis.get("fit_basis", [])
    mapped_blocks: list[dict] = []

    for block in idea.get("template_alignment", {}).get("innovation_blocks", []):
        title = block.get("title", "")
        summary = block.get("summary", "")
        allow_format = contains_keyword(title + summary, ["展示", "答辩", "回放", "沙盘", "运营"])
        prefers_process = contains_keyword(title + summary, ["预警", "分级", "处置", "介入", "回溯", "流水线"])
        preferred_ids = solution_ids + novelty_ids + fit_ids
        if allow_format:
            preferred_ids = communication_ids + fit_ids + solution_ids + novelty_ids
        elif prefers_process:
            preferred_ids = solution_ids + novelty_ids + communication_ids + fit_ids
        keywords = infer_innovation_keywords(block, idea)
        ranked = sorted(
            evidence_items,
            key=lambda item: score_block_evidence(item, keywords, preferred_ids, allow_format=allow_format),
            reverse=True,
        )
        selected_pool = [
            item for item in ranked
            if score_block_evidence(item, keywords, preferred_ids, allow_format=allow_format) > 0
        ]
        substantive_pool = [
            item for item in selected_pool
            if item.get("source_role") not in {"rule", "format_reference"}
        ]
        rule_pool = [item for item in selected_pool if item.get("source_role") == "rule"]
        format_pool = [item for item in selected_pool if item.get("source_role") == "format_reference"]

        selected = substantive_pool[:2]
        if len(selected) < 2 and allow_format:
            selected.extend(format_pool[: 2 - len(selected)])
        if len(selected) < 2:
            selected.extend(rule_pool[: 2 - len(selected)])
        if not selected:
            selected = [
                item for item in evidence_items
                if item.get("evidence_id") in dedupe_preserve_order(preferred_ids)
            ][:2]
        if len(selected) > 1:
            scored_selected = [
                (
                    item,
                    score_block_evidence(item, keywords, preferred_ids, allow_format=allow_format),
                )
                for item in selected
            ]
            scored_selected.sort(key=lambda pair: pair[1], reverse=True)
            lead_score = scored_selected[0][1]
            keep_threshold = max(4, int(lead_score * 0.4))
            selected = [
                item
                for index, (item, score) in enumerate(scored_selected)
                if index == 0 or score >= keep_threshold
            ][:2]
        evidence_titles = [item.get("source_title", "") for item in selected if item.get("source_title")]
        mapped_blocks.append(
            {
                "title": title,
                "summary": summary,
                "keywords": keywords,
                "primary_evidence_id": selected[0].get("evidence_id", "") if selected else "",
                "supporting_evidence_ids": [item.get("evidence_id", "") for item in selected if item.get("evidence_id")],
                "rationale": summarize_block_rationale(title, evidence_titles) if evidence_titles else "",
            }
        )
    return mapped_blocks


def compute_theme_keywords(text: str) -> list[str]:
    return [keyword for keyword in SIMILARITY_KEYWORDS if keyword.lower() in text.lower()]


def attach_similarity_hits(idea: dict, registry: list[dict]) -> dict:
    combined = " ".join(
        [idea.get("project_name", ""), idea.get("problem", ""), idea.get("solution_summary", ""), *idea.get("core_innovations", [])]
    )
    keywords = set(compute_theme_keywords(combined))
    hits: list[dict] = []
    if keywords:
        for item in registry:
            existing = set(item.get("theme_keywords", []))
            overlap = sorted(existing & keywords)
            if len(overlap) >= 4:
                hits.append(
                    {
                        "registry_entry_id": item.get("registry_entry_id", ""),
                        "project_name": item.get("project_name", ""),
                        "source_topic": item.get("source_topic", ""),
                        "overlap_keywords": overlap,
                    }
                )
    idea["similar_registry_hits"] = hits[:3]
    idea["theme_keywords"] = sorted(keywords)
    return idea


def build_template_alignment(idea: dict) -> dict:
    risk_notes = [item.strip() for item in idea.get("risk_notes", []) if item.strip()]

    def is_risk_like(text: str) -> bool:
        stripped = text.strip()
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
            "展示",
            "术语",
            "样机",
            "模拟",
        )
        return stripped.startswith(("需要", "待确认")) or any(marker in stripped for marker in risk_markers)

    seen: set[str] = set()
    blind_spots: list[str] = []
    for raw_item in idea.get("blind_spots", []):
        item = raw_item.strip()
        if not item or item in seen or is_risk_like(item):
            continue
        seen.add(item)
        blind_spots.append(item)
    if not blind_spots and idea.get("problem", "").strip():
        blind_spots.append(idea.get("problem", "").strip())

    innovation_blocks = idea.get("template_innovation_blocks", [])
    if not innovation_blocks:
        innovation_blocks = [
            {
                "title": f"创新{i}",
                "summary": summary,
            }
            for i, summary in enumerate(idea.get("core_innovations", [])[:4], start=1)
        ]
    opening_summary = idea.get("opening_summary", "").strip()
    if not opening_summary:
        spot_text = "、".join([spot for spot in blind_spots[:3] if spot]) or idea.get("problem", "")
        innovation_titles = "、".join(block["title"] for block in innovation_blocks[:4]) or "核心创新"
        opening_summary = (
            f"{idea['project_name']}聚焦的问题并不只是单点识别，而是围绕 {spot_text} 形成的一组系统性盲区。"
            f"本方案尝试把这些问题串成一个完整闭环，并以 {innovation_titles} 作为主要突破口。"
        )
    closing_summary = idea.get("closing_summary", "").strip()
    if not closing_summary:
        value_text = "；".join(idea.get("value_notes", [])[:2]) or "具备明确应用价值"
        closing_summary = (
            f"整体上，该方向适合在比赛中做成系统型作品，既能展示技术链路，也便于讲清落地场景。"
            f"当前判断的主要价值在于：{value_text}。"
        )
    return {
        "opening_summary": opening_summary,
        "blind_spots": blind_spots[:3],
        "innovation_blocks": innovation_blocks[:4],
        "closing_summary": closing_summary,
    }


def render_template_alignment_markdown(alignment: dict) -> list[str]:
    lines = [
        "- Template-Aligned Preview:",
        f"  - Opening Summary: {alignment.get('opening_summary', '')}",
        "  - Blind Spots:",
    ]
    lines.extend([f"    - {item}" for item in alignment.get("blind_spots", [])] or ["    - none"])
    lines.append("  - Innovation Blocks:")
    for item in alignment.get("innovation_blocks", []):
        lines.append(f"    - {item.get('title', '')}: {item.get('summary', '')}")
    if not alignment.get("innovation_blocks"):
        lines.append("    - none")
    lines.append(f"  - Closing Summary: {alignment.get('closing_summary', '')}")
    return lines


def render_innovation_evidence_markdown(entries: list[dict]) -> list[str]:
    lines = ["- Innovation Evidence Map:"]
    for entry in entries:
        lines.append(
            f"  - {entry.get('title', '')}: {', '.join(entry.get('supporting_evidence_ids', [])) or 'none'}"
        )
        if entry.get("rationale"):
            lines.append(f"    - Rationale: {entry['rationale']}")
    if len(lines) == 1:
        lines.append("  - none")
    return lines


def build_candidate_preview_markdown(idea: dict, spec: dict) -> str:
    alignment = idea["template_alignment"]
    lines = [
        f"# {idea['project_name']}",
        "",
        "## 开场总述",
        "",
        alignment.get("opening_summary", ""),
        "",
        "## 关键盲区",
        "",
    ]
    lines.extend([f"- {item}" for item in alignment.get("blind_spots", [])] or ["- none"])
    lines.extend(
        [
            "",
            "## 核心方案定位",
            "",
            idea.get("solution_summary", ""),
            "",
            "## 创新块预览",
            "",
        ]
    )
    for block in alignment.get("innovation_blocks", []):
        lines.extend(
            [
                f"### {block.get('title', '')}",
                "",
                block.get("summary", ""),
                "",
            ]
        )
    lines.extend(
        [
            "## 应用场景与价值",
            "",
            f"- 面向用户：{'、'.join(idea.get('target_users', [])) or 'none'}",
            *[f"- {item}" for item in idea.get("value_notes", [])],
            "",
            "## 风险与待确认",
            "",
            *[f"- {item}" for item in idea.get("risk_notes", [])],
            "",
            "## 证据依据",
            "",
            f"- Competition: {spec.get('competition_name') or 'unknown'}",
            f"- Evidence Refs: {', '.join(idea.get('evidence_refs', [])) or 'none'}",
            f"- Problem Basis: {', '.join(idea.get('analysis_basis', {}).get('problem_basis', [])) or 'none'}",
            f"- Solution Basis: {', '.join(idea.get('analysis_basis', {}).get('solution_basis', [])) or 'none'}",
            f"- Fit Basis: {', '.join(idea.get('analysis_basis', {}).get('fit_basis', [])) or 'none'}",
            "",
            "## 收口判断",
            "",
            alignment.get("closing_summary", ""),
            "",
        ]
    )
    return "\n".join(lines)


def build_seed_variants(seed_text: str, spec: dict) -> list[dict]:
    seed = seed_text.strip()
    matched_scores = spec.get("scoring_dimensions", [])
    return [
        {
            "idea_id": "idea_a",
            "project_name": "察言·风险雷达",
            "problem": "短视频平台面对反讽表达、恶意配文和风险内容扩散时，缺少能快速识别高危事件的监测系统。",
            "target_users": ["平台内容安全团队", "政府网信与宣传部门", "品牌公关团队"],
            "solution_summary": f"以“{seed}”为主轴，优先做风险识别与预警闭环，突出高风险内容发现、分级预警和人工介入建议。",
            "core_innovations": ["多模态短视频风险识别", "反讽与情绪矫正判别", "风险分级告警与处置建议"],
            "feasibility_notes": ["适合做 MVP，先把识别和告警链跑通", "大屏展示和案例演示效果强"],
            "value_notes": ["风险预警价值清晰", "适合评委快速理解核心能力"],
            "risk_notes": ["传播预测部分可先弱化，避免第一版系统过重", "需要明确物联网侧数据接入角色"],
            "blind_spots": [
                "中文反讽和玩梗表达容易被字面情感模型误判",
                "真视频被恶意配文后，叙事风险无法通过单一内容审核发现",
                "识别结果与运营处置之间缺少统一的风险分级和介入建议",
            ],
            "template_innovation_blocks": [
                {"title": "创新一 · 反讽矫正", "summary": "优先解决中文短视频场景里最难识别的阴阳怪气和隐性负面表达。"},
                {"title": "创新二 · 多模态一致性校验", "summary": "联合画面、字幕、评论识别“真视频假叙事”这类语义错位风险。"},
                {"title": "创新三 · 风险分级与预警", "summary": "把内容理解结果转成可执行的风险等级和人工介入建议。"},
                {"title": "创新四 · 运营联动展示", "summary": "以大屏和案例回放形式展示系统输出，方便答辩和业务讲解。"},
            ],
            "opening_summary": "短视频舆情治理的核心难点不是单点违规检测，而是反讽表达、叙事误导和运营处置脱节同时存在。本方案希望以风险识别与预警闭环为主轴，把内容理解、风险分级和人工介入建议串成一套完整系统。",
            "closing_summary": "这一方向最适合作为 Step2 的主推荐方案，因为它问题明确、系统边界清楚、展示效果强，也最容易自然过渡到后续作品书和答辩场景。",
            "matched_scoring_dimensions": matched_scores,
            "score": {"novelty": 8, "feasibility": 8, "fit_to_rules": 8, "communication_potential": 9},
        },
        {
            "idea_id": "idea_b",
            "project_name": "察言·鉴真哨兵",
            "problem": "真实视频被恶意配文、剪辑或二次传播后，容易形成错误叙事并诱发舆情风险。",
            "target_users": ["平台审核团队", "融媒体中心", "应急与舆情处置部门"],
            "solution_summary": f"围绕“{seed}”做真实性与一致性增强版本，强调视频、字幕、评论和外部信源的联合校验。",
            "core_innovations": ["跨模态叙事一致性检测", "疑似误导内容标注", "舆情事件证据链回溯"],
            "feasibility_notes": ["方向聚焦，技术故事完整", "适合讲清和普通内容审核的差异"],
            "value_notes": ["可信治理价值强", "适合政府与平台场景"],
            "risk_notes": ["传播势能部分需要简化，不然重点会发散", "需要控制学术术语密度"],
            "blind_spots": [
                "视频画面真实但字幕或评论故意劫持叙事时，传统检测链难以识别",
                "平台审核常常只能判断内容真假，难以判断叙事是否有误导性",
                "事件处置时缺少可追溯的证据链支撑人工决策",
            ],
            "template_innovation_blocks": [
                {"title": "创新一 · 叙事一致性建模", "summary": "把视频、字幕、评论放在同一条分析链上，判断叙事是否一致。"},
                {"title": "创新二 · 误导内容标注", "summary": "重点捕捉“真素材 + 假解读”这类比 deepfake 更隐蔽的风险。"},
                {"title": "创新三 · 证据链回溯", "summary": "给出触发原因和证据来源，而不是只输出一个风险分数。"},
                {"title": "创新四 · 审核差异化支撑", "summary": "突出它与普通内容审核工具的结构差异和治理价值。"},
            ],
            "opening_summary": "很多短视频风险并不是内容本身造假，而是叙事被后续字幕、剪辑或评论带偏。本方案把重点放在“真实性与一致性校验”上，试图识别那些画面真实但叙事被劫持的高风险内容。",
            "closing_summary": "这一方向的优势在于治理价值强、故事聚焦、容易与现有审核工具做差异化对比，但需要控制术语密度，避免变成过学术的论证。",
            "matched_scoring_dimensions": matched_scores,
            "score": {"novelty": 9, "feasibility": 7, "fit_to_rules": 8, "communication_potential": 8},
        },
        {
            "idea_id": "idea_c",
            "project_name": "察言·势能沙盘",
            "problem": "即使识别出负面内容，运营方也难以判断事件后续传播趋势和不同干预动作的影响。",
            "target_users": ["平台运营团队", "品牌公关团队", "政府舆情研判团队"],
            "solution_summary": f"围绕“{seed}”做决策增强版本，把监测结果、传播预测和干预模拟结合成可视化决策沙盘。",
            "core_innovations": ["舆情传播势能评分", "关键传播节点识别", "干预动作反事实模拟"],
            "feasibility_notes": ["展示潜力很强，适合答辩", "适合和前两案形成明显分化"],
            "value_notes": ["从监测上升到辅助决策，商业化叙事更完整"],
            "risk_notes": ["实现复杂度最高", "第一版需要明确哪些能力是模拟、哪些能力是真实可跑"],
            "blind_spots": [
                "很多系统能识别内容风险，但不能告诉运营团队后续会如何扩散",
                "不同干预动作可能带来完全不同的传播结果，目前缺少模拟能力",
                "识别结果与处置决策之间仍然依赖人工经验拼接",
            ],
            "template_innovation_blocks": [
                {"title": "创新一 · 势能评分", "summary": "把内容风险、传播敏感度和节点影响力合成统一风险势能指标。"},
                {"title": "创新二 · 关键节点识别", "summary": "提前识别可能放大事件的传播节点或账号。"},
                {"title": "创新三 · 干预动作模拟", "summary": "将“限流、回应、不动作”等策略转成可对比的走势预测。"},
                {"title": "创新四 · 可视化决策沙盘", "summary": "把复杂模型输出组织成适合运营和评委理解的决策界面。"},
            ],
            "opening_summary": "如果系统只能告诉运营团队“这条内容有风险”，那它仍然没有走到真正的决策层。本方案试图从监测进一步上升到传播势能评估和干预动作模拟，做成一个更强的决策增强版本。",
            "closing_summary": "这一方向展示潜力最高，商业叙事也最完整，但它同时是 Step2 里实现复杂度最高的方向，因此更适合作为答辩增强案或后续升级案。",
            "matched_scoring_dimensions": matched_scores,
            "score": {"novelty": 9, "feasibility": 6, "fit_to_rules": 7, "communication_potential": 10},
        },
    ]


def choose_idea_pool(spec: dict, context_text: str, seed_text: str = "") -> list[dict]:
    if seed_text.strip():
        return build_seed_variants(seed_text, spec)

    combined = f"{spec.get('competition_name', '')}\n{context_text}"
    if contains_any(combined, ["舆情", "短视频", "内容安全", "谣言", "情感"]):
        return [
            {
                "idea_id": "idea_a",
                "project_name": "察言哨兵",
                "problem": "短视频平台对反讽、恶意配文和舆情放大链条识别不足，难以及时干预风险事件。",
                "target_users": ["平台内容安全团队", "政府宣传与网信部门", "品牌公关团队"],
                "solution_summary": "构建多模态舆情风险监测系统，联动视频内容理解、语义一致性检测与传播热度预警。",
                "core_innovations": ["反讽与玩梗情绪纠偏", "视频-字幕-评论跨模态一致性校验", "舆情事件传播势能预估"],
                "feasibility_notes": ["可基于现有开源视觉语言模型与语音识别能力搭建原型", "适合做系统型作品展示"],
                "value_notes": ["风险预警价值强", "适合展示大屏和事件闭环流程"],
                "risk_notes": ["需要控制方案复杂度，避免讲解过于学术化", "需要补强物联网终端接入叙事"],
                "matched_scoring_dimensions": ["创意", "技术方案及其实现质量", "应用价值", "讲解表现"],
                "score": {"novelty": 9, "feasibility": 7, "fit_to_rules": 7, "communication_potential": 9},
            },
            {
                "idea_id": "idea_b",
                "project_name": "城感巡盾",
                "problem": "城市公共场所存在设备异常、环境风险和事件响应慢的问题，缺少统一感知与联动处置。",
                "target_users": ["园区管理方", "城市治理部门", "安保运维团队"],
                "solution_summary": "将摄像头、环境传感器与事件联动平台结合，形成城市微场景风险感知与处置系统。",
                "core_innovations": ["多源感知融合告警", "风险分级处置引擎", "处置流程可视化回放"],
                "feasibility_notes": ["IoT 叙事更强", "可做传感器 + 平台双层演示"],
                "value_notes": ["落地场景直观", "评委容易理解应用价值"],
                "risk_notes": ["创新点容易偏传统安防，需要差异化表达", "需要控制与已有智慧园区方案的重复感"],
                "matched_scoring_dimensions": ["创意", "技术方案及其实现质量", "应用价值", "讲解表现"],
                "score": {"novelty": 7, "feasibility": 8, "fit_to_rules": 9, "communication_potential": 8},
            },
            {
                "idea_id": "idea_c",
                "project_name": "信链鉴真",
                "problem": "公共事件中现场数据、终端上传记录与网络传播内容容易割裂，导致追溯困难。",
                "target_users": ["应急管理部门", "校园管理方", "大型活动主办方"],
                "solution_summary": "利用 IoT 终端采集、事件时间线归档和内容真实性标注，实现现场数据与网络内容的联合追溯。",
                "core_innovations": ["终端侧证据链采集", "传播内容与现场数据对照校验", "事件追溯时间轴自动生成"],
                "feasibility_notes": ["系统边界清晰", "适合做原型演示和流程型答辩"],
                "value_notes": ["突出可信追溯价值", "与安全治理场景贴合"],
                "risk_notes": ["需要明确终端形态与采集范围", "概念表达要避免过于抽象"],
                "matched_scoring_dimensions": ["创意", "技术方案及其实现质量", "应用价值", "讲解表现"],
                "score": {"novelty": 8, "feasibility": 7, "fit_to_rules": 8, "communication_potential": 8},
            },
        ]

    if contains_any(combined, ["物联网", "iot"]):
        return [
            {
                "idea_id": "idea_a",
                "project_name": "智安实验室",
                "problem": "高校实验室存在设备异常、危险气体泄露和违规操作难以及时发现的问题。",
                "target_users": ["高校实验室管理者", "师生实验人员", "校园安全部门"],
                "solution_summary": "搭建面向高校实验室的多传感器安全监管系统，实现环境感知、异常识别和应急联动。",
                "core_innovations": ["环境与设备双通道监测", "异常事件分级预警", "应急联动闭环处置"],
                "feasibility_notes": ["硬件和平台边界清晰", "适合做实物演示与场景化讲解"],
                "value_notes": ["校园场景明确", "安全价值强，评委容易理解"],
                "risk_notes": ["需要避免和传统安防方案同质化", "需要突出智能决策而不是只堆硬件"],
                "matched_scoring_dimensions": ["创意", "技术方案及其实现质量", "应用价值", "讲解表现"],
                "score": {"novelty": 7, "feasibility": 9, "fit_to_rules": 9, "communication_potential": 8},
            },
            {
                "idea_id": "idea_b",
                "project_name": "康护随联",
                "problem": "独居老人和慢病人群在居家场景下存在跌倒、异常滞留和求助不及时的问题。",
                "target_users": ["社区养老机构", "家庭用户", "基层医疗与民政部门"],
                "solution_summary": "构建居家健康监测与应急联动系统，融合可穿戴设备、环境传感器和告警平台。",
                "core_innovations": ["非接触与可穿戴联合感知", "异常行为识别", "家庭-社区-医疗三级联动"],
                "feasibility_notes": ["应用场景成熟", "适合做终端 + 小程序 + 平台一体展示"],
                "value_notes": ["社会价值突出", "容易讲清用户收益"],
                "risk_notes": ["创新性需靠联动机制和体验设计拉开差距", "隐私保护叙事需要补足"],
                "matched_scoring_dimensions": ["创意", "技术方案及其实现质量", "应用价值", "讲解表现"],
                "score": {"novelty": 7, "feasibility": 8, "fit_to_rules": 8, "communication_potential": 8},
            },
            {
                "idea_id": "idea_c",
                "project_name": "维脉工守",
                "problem": "中小制造场景中设备故障预警弱、人工巡检压力大、停机损失高。",
                "target_users": ["工厂设备运维团队", "中小制造企业管理者", "产业园运维部门"],
                "solution_summary": "打造工业设备健康管理系统，通过振动、电流和温度等数据进行预测性维护。",
                "core_innovations": ["轻量多传感器接入", "设备故障趋势评分", "运维工单自动联动"],
                "feasibility_notes": ["工业 IoT 叙事稳健", "技术方案容易拆解展示"],
                "value_notes": ["降本增效价值明确", "适合做数据看板和维护闭环演示"],
                "risk_notes": ["演示场景可能较硬核，需要优化讲解亲和力", "需要展示样机或模拟数据"],
                "matched_scoring_dimensions": ["创意", "技术方案及其实现质量", "应用价值", "讲解表现"],
                "score": {"novelty": 6, "feasibility": 9, "fit_to_rules": 9, "communication_potential": 7},
            },
        ]

    return [
        {
            "idea_id": "idea_a",
            "project_name": "场景智能管家",
            "problem": "目标场景中的数据感知、分析与响应链路割裂，难以形成完整闭环。",
            "target_users": ["场景运营方", "管理部门", "一线执行人员"],
            "solution_summary": "围绕一个具体场景搭建感知、分析、决策和执行联动系统。",
            "core_innovations": ["多源数据接入", "规则与模型融合决策", "闭环执行反馈"],
            "feasibility_notes": ["框架通用", "适合作为兜底候选方案"],
            "value_notes": ["应用价值容易表达"],
            "risk_notes": ["需要后续结合具体赛道细化"],
            "matched_scoring_dimensions": spec.get("scoring_dimensions", []),
            "score": {"novelty": 6, "feasibility": 7, "fit_to_rules": 7, "communication_potential": 7},
        },
        {
            "idea_id": "idea_b",
            "project_name": "可信数据助手",
            "problem": "场景数据来源分散、可信度不足，影响后续决策质量。",
            "target_users": ["平台管理者", "运营团队", "业务决策者"],
            "solution_summary": "通过采集、清洗和异常识别模块，提升数据可用性与业务响应效率。",
            "core_innovations": ["可信采集机制", "异常识别", "结果反馈闭环"],
            "feasibility_notes": ["容易做 MVP 原型"],
            "value_notes": ["适合讲效率提升"],
            "risk_notes": ["需要补足场景差异化"],
            "matched_scoring_dimensions": spec.get("scoring_dimensions", []),
            "score": {"novelty": 6, "feasibility": 8, "fit_to_rules": 7, "communication_potential": 6},
        },
        {
            "idea_id": "idea_c",
            "project_name": "智慧联动平台",
            "problem": "现有系统分散，人工协调成本高，无法形成跨环节联动处置。",
            "target_users": ["管理部门", "平台运营者", "协同单位"],
            "solution_summary": "建设统一联动平台，将感知事件、分析结果和执行动作连接起来。",
            "core_innovations": ["统一事件总线", "可视化联动", "策略化处置"],
            "feasibility_notes": ["实现边界清晰"],
            "value_notes": ["展示逻辑完整"],
            "risk_notes": ["如果没有具体场景会显得偏空"],
            "matched_scoring_dimensions": spec.get("scoring_dimensions", []),
            "score": {"novelty": 5, "feasibility": 7, "fit_to_rules": 7, "communication_potential": 7},
        },
    ]


def update_workspace_state(topic_dir: Path) -> None:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not state_path.exists():
        return
    state = read_json(state_path)
    state["current_step"] = "selection"
    state["workflow_status"]["ideas"] = "completed"
    state["workflow_status"]["selection"] = "active"
    state["next_action"] = "run_selection"
    state["blocking_reason"] = ""
    state["required_inputs"] = ["人工选择最终 idea"]
    write_json(state_path, state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AutoSearch MVP step2 idea generation.")
    parser.add_argument("topic_dir", help="Topic directory, such as sample/topic_xx")
    parser.add_argument("--topic", default="", help="Optional topic override. Defaults to workspace topic_name.")
    parser.add_argument("--idea-seed", default="", help="Optional idea seed text to generate same-axis variants around.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    step_dir = topic_dir / "workspace" / "ideas"
    spec_path = topic_dir / "workspace" / "requirements" / "competition-spec.json"
    evidence_path = step_dir / "evidence-ledger.json"
    if not spec_path.exists():
        raise SystemExit("competition-spec.json not found. Run step1 first.")
    if not evidence_path.exists():
        raise SystemExit("evidence-ledger.json not found. Run step2 evidence sweep first.")

    spec = read_json(spec_path)
    ledger = read_json(evidence_path)
    context_text = load_context_text(topic_dir)
    seed_text = args.idea_seed.strip() or ledger.get("seed_direction", "").strip()
    topic_profile = resolve_topic_profile(
        topic_dir,
        explicit_topic=args.topic,
        context_text=context_text,
        seed_text=seed_text,
        extra_tags=ledger.get("summary", {}).get("top_themes", []),
    )
    ideas = build_profile_ideas(topic_profile, spec, seed_text=seed_text)
    registry = load_registry()
    candidates_dir = step_dir / "candidates"

    enriched: list[dict] = []
    for idea in ideas:
        idea["topic_name"] = topic_profile.get("topic_name", topic_dir.name)
        idea["topic_profile"] = idea.get(
            "topic_profile",
            {
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
            },
        )
        idea = attach_evidence(idea, ledger)
        idea = attach_similarity_hits(idea, registry)
        idea["template_alignment"] = build_template_alignment(idea)
        idea["innovation_evidence_map"] = build_innovation_evidence_map(idea, ledger)
        preview_name = f"IdeaCandidate_{sanitize_filename(idea['project_name'])}.md"
        idea["candidate_preview_path"] = f"workspace/ideas/candidates/{preview_name}"
        write_text(candidates_dir / preview_name, build_candidate_preview_markdown(idea, spec))
        enriched.append(idea)

    batch_lines = [
        "# Idea Batch",
        "",
        f"- Topic: {topic_profile.get('topic_name', topic_dir.name)}",
        f"- Topic Profile: {topic_profile.get('display_name', 'unknown')}",
        f"- Competition: {spec.get('competition_name') or 'unknown'}",
        f"- Idea Seed: {seed_text or 'none'}",
        f"- Generated Ideas: {len(enriched)}",
        "",
        "## Evidence-First Rules",
        "- 每个候选 idea 都必须能回溯到 evidence_refs。",
        "- evidence 不足以支撑的部分，只能写成 inference_notes。",
        "- 与 idea 数据库中高度相似的方向需要显式提示。",
        "",
    ]
    for index, idea in enumerate(enriched, start=1):
        batch_lines.extend(
            [
                f"## Idea {index}: {idea['project_name']}",
                "",
                f"- Idea ID: `{idea['idea_id']}`",
                f"- Focus Summary: {idea.get('focus_summary', 'none')}",
                f"- Candidate Preview: `{idea.get('candidate_preview_path', '')}`",
                f"- Problem: {idea['problem']}",
                f"- Target Users: {'、'.join(idea['target_users'])}",
                f"- Solution Summary: {idea['solution_summary']}",
                f"- Evidence Refs: {', '.join(idea.get('evidence_refs', [])) or 'none'}",
                f"- Similar Registry Hits: {len(idea.get('similar_registry_hits', []))}",
                "- Core Innovations:",
            ]
        )
        batch_lines.extend([f"  - {item}" for item in idea["core_innovations"]])
        batch_lines.append("- Feasibility Notes:")
        batch_lines.extend([f"  - {item}" for item in idea["feasibility_notes"]])
        batch_lines.append("- Value Notes:")
        batch_lines.extend([f"  - {item}" for item in idea["value_notes"]])
        batch_lines.append("- Risk Notes:")
        batch_lines.extend([f"  - {item}" for item in idea["risk_notes"]])
        batch_lines.append("- Analysis Basis:")
        batch_lines.append(f"  - Problem Basis: {', '.join(idea['analysis_basis']['problem_basis']) or 'none'}")
        batch_lines.append(f"  - Solution Basis: {', '.join(idea['analysis_basis']['solution_basis']) or 'none'}")
        batch_lines.append(f"  - Fit Basis: {', '.join(idea['analysis_basis']['fit_basis']) or 'none'}")
        batch_lines.append(f"  - Novelty Basis: {', '.join(idea['analysis_basis']['novelty_basis']) or 'none'}")
        batch_lines.append(f"  - Communication Basis: {', '.join(idea['analysis_basis'].get('communication_basis', [])) or 'none'}")
        batch_lines.extend(render_template_alignment_markdown(idea["template_alignment"]))
        batch_lines.extend(render_innovation_evidence_markdown(idea.get("innovation_evidence_map", [])))
        if idea.get("similar_registry_hits"):
            batch_lines.append("- Similar Registry Hits Detail:")
            for hit in idea["similar_registry_hits"]:
                batch_lines.append(
                    f"  - {hit['project_name']} [{hit['registry_entry_id']}] from {hit['source_topic']} via {'、'.join(hit['overlap_keywords'])}"
                )
        batch_lines.append("- Matched Scoring Dimensions:")
        batch_lines.extend([f"  - {item}" for item in idea["matched_scoring_dimensions"]])
        batch_lines.append(
            f"- Scores: 创新性 {idea['score']['novelty']}/10, 可行性 {idea['score']['feasibility']}/10, 匹配度 {idea['score']['fit_to_rules']}/10, 展示潜力 {idea['score']['communication_potential']}/10"
        )
        batch_lines.append("")

    scorecard = {"ideas": enriched}
    write_text(step_dir / "idea-batch.md", "\n".join(batch_lines) + "\n")
    write_json(step_dir / "idea-scorecard.json", scorecard)
    update_workspace_state(topic_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

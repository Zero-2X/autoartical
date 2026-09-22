#!/usr/bin/env python3
"""Build an evidence-aware research brief between idea selection and planning."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip("。；; ")


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in (clean(item) for item in values) if value))


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_items(topic_dir: Path) -> list[dict[str, Any]]:
    path = topic_dir / "workspace" / "ideas" / "evidence-ledger.json"
    if not path.exists():
        return []
    payload = read_json(path)
    return payload.get("evidence_items", payload.get("items", []))


def build_questions(topic: str, subdomain: str) -> list[dict[str, Any]]:
    subject = subdomain or topic
    return [
        {"id": "Q1", "question": f"{topic} 所属的研究领域是什么，为什么值得研究？", "required_evidence": ["权威背景", "影响事实"]},
        {"id": "Q2", "question": f"{subject} 是什么子领域，为什么选择这个方向？", "required_evidence": ["任务定义", "应用边界", "代表工作"]},
        {"id": "Q3", "question": "子领域有哪些通用挑战，它们造成什么可测影响？", "required_evidence": ["挑战分类", "失败后果"]},
        {"id": "Q4", "question": "Current methods 可以分为哪些类别？每类的机制、优点、缺点和适用边界是什么？", "required_evidence": ["代表工作", "统一分类依据"]},
        {"id": "Q5", "question": "现有缺陷如何收敛为一个可检验的关键研究问题？", "required_evidence": ["缺陷对照", "未解决矛盾"]},
        {"id": "Q6", "question": "科学设计是什么？每个组件为什么必要，rationale 如何对应缺陷？", "required_evidence": ["机制假设", "可证伪预测"]},
        {"id": "Q7", "question": "case study 与主实验如何验证想法？benchmark、baseline、metrics 分别测什么、证明什么？", "required_evidence": ["案例材料", "实验协议"]},
    ]


def derive_brief(topic_dir: Path, idea: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    profile = idea.get("topic_profile", {}) or {}
    topic = clean(idea.get("topic_name") or idea.get("project_name") or topic_dir.name)
    domain = clean(profile.get("display_name") or profile.get("domain_label") or topic)
    subdomain = clean(idea.get("focus_summary") or (idea.get("core_innovations") or [""])[0] or idea.get("solution_summary"))
    sources = [item for item in items if item.get("source_role") in {"external_research", "reference", "rule"}]
    reviewed = [item for item in sources if item.get("verification_status") in {"verified", "reviewed"} or item.get("curation_status") == "reviewed"]
    external = [item for item in sources if item.get("source_role") == "external_research" and item.get("evidence_kind") != "research_query"]
    challenges = unique((idea.get("pain_points") or []) + (idea.get("open_questions") or [])) or ["待由文献归纳通用挑战；项目痛点不能直接当作领域事实。"]
    methods = [{"category": clean(value), "mechanism": "待由代表性工作归纳", "strengths": [], "limitations": [], "evidence_ids": [], "status": "needs_sources"} for value in idea.get("core_innovations", [])[:4] if clean(value)]
    if not methods:
        methods = [{"category": "待建立统一分类", "mechanism": "不能从项目描述推断 current methods 分类", "strengths": [], "limitations": [], "evidence_ids": [], "status": "needs_sources"}]
    case = idea.get("validation_support_pack", {}).get("case_replay", {}) or {}
    return {
        "schema_version": "research-brief.v1", "generated_at": now(), "topic": topic,
        "domain": {"name": domain, "why_research": clean(profile.get("background_focus") or idea.get("problem")), "evidence_ids": [x.get("evidence_id") for x in reviewed[:3] if x.get("evidence_id")]},
        "subdomain": {"name": subdomain, "why_direction": clean(idea.get("problem") or idea.get("solution_summary")), "evidence_ids": [x.get("evidence_id") for x in external[:3] if x.get("evidence_id")]},
        "common_challenges": [{"challenge": value, "impact": "待用外部证据解释影响", "evidence_ids": []} for value in challenges],
        "current_methods": methods,
        "key_gap": {"statement": "待由 current methods 的共同缺陷收敛为可检验研究问题", "research_question": "", "evidence_ids": [], "status": "needs_synthesis"},
        "design_rationale": [{"design": clean(x), "rationale": "待映射到已核验缺陷", "testable_prediction": "", "evidence_ids": []} for x in idea.get("core_innovations", [])[:4]],
        "case_study": {"title": clean(case.get("title")), "timeline": case.get("timeline", []), "purpose": "验证机制在具体情境中的行为与失败边界", "status": "planned" if case else "needs_case_material"},
        "experiment_plan": {"benchmarks": [], "baselines": [], "metrics": idea.get("validation_support_pack", {}).get("metric_summary", []) or [], "questions": [{"id": "Q1", "purpose": "主方法相对强基线的有效性"}, {"id": "Q2", "purpose": "关键组件贡献"}, {"id": "Q3", "purpose": "鲁棒性、效率或边界"}, {"id": "Q4", "purpose": "案例解释机制与失败模式"}], "success_criteria": [], "status": "needs_protocol"},
        "evidence_summary": {"total_candidates": len(items), "usable_sources": len(sources), "reviewed_sources": len(reviewed), "unverified_sources": max(0, len(sources) - len(reviewed)), "external_research_sources": len(external)},
        "research_questions": build_questions(topic, subdomain),
    }


def gate(brief: dict[str, Any]) -> dict[str, Any]:
    missing = []
    evidence_summary = brief.get("evidence_summary", {}) or {}
    if evidence_summary.get("unverified_sources", 0) > 0:
        missing.append("evidence.fulltext_verification")
    if not brief["domain"]["why_research"]: missing.append("domain.why_research")
    if not brief["subdomain"]["name"]: missing.append("subdomain.name")
    if not brief["domain"]["evidence_ids"]: missing.append("domain.evidence_ids")
    if not brief["subdomain"]["evidence_ids"]: missing.append("subdomain.evidence_ids")
    if not brief["current_methods"] or any(not row.get("evidence_ids") or not row.get("strengths") or not row.get("limitations") for row in brief["current_methods"]): missing.append("current_methods evidence and pros/cons")
    experiment = brief.get("experiment_plan", {})
    if not experiment.get("benchmarks"): missing.append("experiment_plan.benchmarks")
    if not experiment.get("baselines"): missing.append("experiment_plan.baselines")
    if not experiment.get("success_criteria"): missing.append("experiment_plan.success_criteria")
    if not brief.get("key_gap", {}).get("research_question"): missing.append("key_gap.research_question")
    if not brief.get("design_rationale") or any(not row.get("rationale") or not row.get("testable_prediction") for row in brief["design_rationale"]): missing.append("design_rationale rationale and prediction")
    return {"verdict": "needs_research" if missing else "pass", "missing": unique(missing), "blocking": bool(missing), "rule": "queries and unverified sources never count as findings"}


def render_plan(brief: dict[str, Any], research_gate: dict[str, Any]) -> str:
    lines = ["# 自动研究计划", "", f"- 领域：{brief['domain']['name'] or '待确认'}", f"- 子领域：{brief['subdomain']['name'] or '待确认'}", f"- Gate：`{research_gate['verdict']}`", "", "## 研究问题"]
    lines.extend(f"{q['id']}. {q['question']}" for q in brief["research_questions"])
    lines.extend(["", "## 规则", "", "- 查询计划、搜索摘要和项目假设不能冒充研究事实。", "- Current methods 必须有统一分类依据，并为每类记录优点、缺点和代表来源。", "- 主实验必须固定 benchmark、baseline、metrics、对照目的和成功判据。", "", "## 当前阻塞项"])
    lines.extend(f"- {x}" for x in research_gate["missing"] or ["none"])
    return "\n".join(lines) + "\n"


def build_query_plan(brief: dict[str, Any]) -> list[dict[str, Any]]:
    topic = brief["topic"]
    subdomain = brief["subdomain"]["name"] or topic
    return [
        {"id": "Q1", "query": f"{topic} field background significance review", "source_types": ["official_report", "survey", "policy"]},
        {"id": "Q2", "query": f"{subdomain} task definition benchmark survey", "source_types": ["paper", "dataset"]},
        {"id": "Q3", "query": f"{subdomain} common challenges limitations failure analysis", "source_types": ["paper", "benchmark"]},
        {"id": "Q4", "query": f"{subdomain} methods taxonomy comparison baseline", "source_types": ["paper", "official_code"]},
        {"id": "Q5", "query": f"{subdomain} case study deployment evaluation metrics", "source_types": ["case_report", "benchmark"]},
    ]


def update_state(topic_dir: Path, research_gate: dict[str, Any]) -> None:
    path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not path.exists(): return
    state = read_json(path)
    state.setdefault("workflow_status", {})["research"] = "completed" if research_gate["verdict"] == "pass" else "blocked"
    state["current_step"] = "research"
    state["next_action"] = "run_document_plan" if research_gate["verdict"] == "pass" else "complete_research_evidence"
    state["blocking_reason"] = "" if research_gate["verdict"] == "pass" else "自动研究 Gate 未通过：需要补充领域、方法和实验协议证据。"
    state["required_inputs"] = ["workspace/research/research-brief.json", "workspace/research/research-gate.json"]
    write_json(path, state)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成选题自动研究问题、证据地图与实验契约")
    parser.add_argument("topic_dir"); parser.add_argument("--topic", default="")
    parser.add_argument("--reset", action="store_true", help="丢弃已有研究 brief，重新生成骨架")
    args = parser.parse_args(); topic_dir = Path(args.topic_dir).expanduser().resolve()
    card_path = topic_dir / "workspace" / "concept" / "idea-card.json"
    if not card_path.exists(): raise SystemExit("缺少 idea-card.json，请先完成选题说明。")
    idea = read_json(card_path)
    if args.topic: idea["topic_name"] = args.topic
    research_dir = topic_dir / "workspace" / "research"
    brief_path = research_dir / "research-brief.json"
    if brief_path.exists() and not args.reset:
        brief = read_json(brief_path)
    else:
        brief = derive_brief(topic_dir, idea, load_items(topic_dir))
    research_gate = gate(brief)
    write_json(research_dir / "research-brief.json", brief); write_json(research_dir / "research-gate.json", research_gate)
    write_json(research_dir / "research-queries.json", {"topic": brief["topic"], "queries": build_query_plan(brief), "rule": "query plans are not evidence"})
    write_text(research_dir / "research-plan.md", render_plan(brief, research_gate)); update_state(topic_dir, research_gate)
    print(json.dumps({"verdict": research_gate["verdict"], "missing": research_gate["missing"]}, ensure_ascii=False, indent=2))
    return 0 if research_gate["verdict"] == "pass" else 2


if __name__ == "__main__": raise SystemExit(main())

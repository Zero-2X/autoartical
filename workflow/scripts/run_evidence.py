#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

from topic_profiles import build_recommended_directions, collect_all_profile_keywords, resolve_topic_profile
from source_ingestion import SUPPORTED_SUFFIXES, extract_source


REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_REGISTRY_PATH = REPO_ROOT / "sample" / "databases" / "evidence" / "evidence-registry.json"
EVIDENCE_SCHEMA_VERSION = "v2"

KEYWORD_TAGS = [
    "多模态",
    "短视频",
    "舆情",
    "风险",
    "监测",
    "预警",
    "治理",
    "物联网",
    "平台",
    "内容安全",
    "反讽",
    "情绪",
    "传播",
    "审核",
] + collect_all_profile_keywords()

FORMAT_REFERENCE_KEYWORDS = [
    "latex",
    "template",
    "目录",
    "封面",
    "摘要",
    "目录页",
    "格式",
    "排版",
    "toc",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def unique_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        value = item.strip() if isinstance(item, str) else ""
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def normalize_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = text.replace("\uf06d", " ")
    text = text.replace("\x0c", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        chunks: list[str] = []
        for page in reader.pages[:5]:
            text = page.extract_text() or ""
            if text.strip():
                chunks.append(text)
        return normalize_text("\n".join(chunks))
    except Exception:
        pass

    helper = """
from pypdf import PdfReader
from pathlib import Path
import sys
path = Path(sys.argv[1])
reader = PdfReader(str(path))
chunks = []
for page in reader.pages[:5]:
    text = page.extract_text() or ""
    if text.strip():
        chunks.append(text)
print("\\n".join(chunks))
"""
    result = subprocess.run(
        ["/usr/bin/python3", "-c", helper, str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return normalize_text(result.stdout)


def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return extract_pdf_text(path)
    if path.suffix.lower() in {".md", ".txt", ".json"}:
        return normalize_text(path.read_text(encoding="utf-8"))
    return ""


def short_sentences(text: str, limit: int = 2) -> list[str]:
    parts = re.split(r"[。！？\n]+", text)
    results = [" ".join(part.split()) for part in parts if part.strip()]
    return results[:limit]


def detect_tags(text: str) -> list[str]:
    return [tag for tag in KEYWORD_TAGS if tag.lower() in text.lower()]


def is_format_reference(rel_path: str, raw_text: str) -> bool:
    lower_path = rel_path.lower()
    if "latex_template/" in lower_path:
        return True
    if lower_path.endswith((".tex", ".sty")):
        return True
    return any(keyword in lower_path or keyword in raw_text.lower() for keyword in FORMAT_REFERENCE_KEYWORDS)


def infer_source_role(rel_path: str, raw_text: str, default_role: str) -> str:
    if default_role == "reference" and is_format_reference(rel_path, raw_text):
        return "format_reference"
    return default_role


def should_skip_reference(rel_path: str) -> bool:
    lower_path = rel_path.replace("\\", "/").lower()
    if lower_path == "external_evidence/readme.md":
        return True
    return False


def build_reference_summary(path: Path, raw_text: str, source_role: str, snippets: list[str]) -> tuple[str, str]:
    if source_role == "format_reference":
        summary = "该材料主要提供作品书或模板格式参考，可用于约束版式结构和交付呈现，不直接作为领域问题证据。"
        claim = f"{path.name} 主要提供作品书模板/版式参考"
        return claim, summary
    summary = "；".join(snippets[:2]) if snippets else path.stem
    claim = f"{path.name} 主要涉及：{summary[:120]}"
    return claim, summary


def build_evidence_id(seed: str) -> str:
    return "ev_" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]


def infer_source_authority(source_role: str, source_type: str, source_title: str = "") -> str:
    if source_role == "rule":
        return "competition_official"
    if source_role == "external_research":
        lower_type = source_type.lower()
        if lower_type in {"paper", "dataset"}:
            return "academic"
        if lower_type in {"report", "whitepaper"}:
            return "industry_report"
        if lower_type in {"official_doc", "platform_doc"}:
            return "official_platform"
        return "external_curated"
    if source_role == "format_reference":
        return "format_reference"
    if source_role == "sample":
        return "internal_sample"
    if source_role == "reference":
        return "internal_reference"
    if source_role == "seed_direction":
        return "human_input"
    if "README" in source_title or "模板" in source_title:
        return "internal_reference"
    return "unknown"


def infer_evidence_kind(source_role: str, source_type: str, claim: str, summary: str) -> str:
    text = f"{claim} {summary}"
    if source_role == "rule":
        if "评分" in text or "得分" in text:
            return "scoring_rule"
        if "提交" in text or "演示" in text or "文档" in text:
            return "submission_requirement"
        return "compliance_constraint"
    if source_role == "format_reference":
        return "format_pattern"
    if source_role == "sample":
        return "sample_pattern"
    if source_role == "seed_direction":
        return "direction_constraint"
    if source_role == "external_research":
        lower_type = source_type.lower()
        if lower_type == "dataset" or "数据集" in text or "benchmark" in text.lower():
            return "dataset_signal"
        if lower_type in {"report", "whitepaper"}:
            return "industry_signal"
        return "research_finding"
    return "reference_note"


def infer_applicable_steps(source_role: str, evidence_kind: str) -> list[str]:
    if source_role == "rule":
        return ["requirements", "ideas", "document_plan", "document_writing", "document_review"]
    if source_role == "external_research":
        return ["ideas", "concept", "document_plan", "document_writing"]
    if source_role == "sample":
        return ["ideas", "concept", "document_plan", "document_writing"]
    if source_role == "format_reference" or evidence_kind == "format_pattern":
        return ["requirements", "document_plan", "document_writing", "document_export"]
    if source_role == "seed_direction":
        return ["ideas"]
    return ["ideas", "document_plan"]


def infer_reusability_tier(source_role: str, reusable: bool) -> str:
    if not reusable:
        return "low"
    if source_role in {"rule", "external_research", "format_reference"}:
        return "high"
    if source_role in {"reference", "seed_direction"}:
        return "medium"
    return "low"


def infer_inspiration_points(
    source_role: str,
    evidence_kind: str,
    summary: str,
    notes: str,
    supports: list[str],
) -> list[str]:
    if supports:
        return unique_list([f"可直接支撑：{item}" for item in supports[:3]])
    if source_role == "rule" and evidence_kind == "scoring_rule":
        return ["可用来约束 idea 的评分匹配叙事和作品书章节轻重。"]
    if source_role == "rule" and evidence_kind == "submission_requirement":
        return ["可用来约束交付形式、演示结构和最终 record 产物。"]
    if source_role == "format_reference":
        return ["可复用其版式结构、章节顺序和交付样式，但不能作为领域事实证据。"]
    if source_role == "sample":
        return ["可借鉴其问题组织、系统闭环和表达节奏，但不能直接复用其中事实、数据或结论。"]
    if source_role == "external_research":
        if notes:
            return unique_list([notes])
        return [f"可从中提炼出：{summary}"]
    if source_role == "seed_direction":
        return ["这是选题边界条件，只用于限制发散方向，不可直接当作事实证据。"]
    return [f"可复用启发：{summary}"] if summary else []


def normalize_evidence_item(item: dict) -> dict:
    normalized = dict(item)
    source_role = normalized.get("source_role", "")
    source_type = normalized.get("source_type", "")
    claim = normalized.get("claim", "")
    summary = normalized.get("summary", "")
    notes = normalized.get("notes", "")
    supports = unique_list(
        (normalized.get("supports", []) or [])
        + (normalized.get("evidence_for", []) or [])
    )
    reusable = bool(normalized.get("reusable", False))
    normalized["source_authority"] = normalized.get("source_authority") or infer_source_authority(
        source_role,
        source_type,
        normalized.get("source_title", ""),
    )
    normalized["source_origin"] = normalized.get("source_origin") or (
        "manual_external_intake" if source_role == "external_research" else "local_workspace_scan"
    )
    normalized["evidence_kind"] = normalized.get("evidence_kind") or infer_evidence_kind(
        source_role,
        source_type,
        claim,
        summary,
    )
    normalized["supports"] = supports
    normalized["derived_insight"] = normalized.get("derived_insight") or summary or claim
    normalized["inspiration_points"] = unique_list(
        normalized.get("inspiration_points", []) or infer_inspiration_points(
            source_role,
            normalized["evidence_kind"],
            summary,
            notes,
            supports,
        )
    )
    normalized["applicable_steps"] = unique_list(
        normalized.get("applicable_steps", []) or infer_applicable_steps(source_role, normalized["evidence_kind"])
    )
    normalized["applicable_work_types"] = unique_list(normalized.get("applicable_work_types", []) or [])
    normalized["reusability_tier"] = normalized.get("reusability_tier") or infer_reusability_tier(source_role, reusable)
    normalized["curation_status"] = normalized.get("curation_status") or ("reviewed" if source_role in {"rule", "external_research"} else "normalized")
    normalized["usage_hint"] = normalized.get("usage_hint", "") or (notes if source_role == "external_research" else "")
    normalized["limitations"] = normalized.get("limitations", "")
    normalized["schema_version"] = EVIDENCE_SCHEMA_VERSION
    return normalized


def ensure_registry() -> dict:
    if not EVIDENCE_REGISTRY_PATH.exists():
        write_json(EVIDENCE_REGISTRY_PATH, {"schema_version": EVIDENCE_SCHEMA_VERSION, "items": []})
    registry = read_json(EVIDENCE_REGISTRY_PATH)
    items = registry.get("items", [])
    registry["schema_version"] = EVIDENCE_SCHEMA_VERSION
    registry["items"] = [normalize_evidence_item(item) for item in items]
    return registry


def merge_registry_item(existing_item: dict, new_item: dict) -> dict:
    merged = normalize_evidence_item(existing_item)
    incoming = normalize_evidence_item(new_item)

    for key in (
        "source_title",
        "source_locator",
        "source_authority",
        "source_origin",
        "evidence_kind",
        "published_at",
        "claim",
        "summary",
        "excerpt",
        "derived_insight",
        "usage_hint",
        "limitations",
        "notes",
    ):
        current = str(merged.get(key, "") or "")
        candidate = str(incoming.get(key, "") or "")
        if not current or (candidate and len(candidate) > len(current)):
            merged[key] = candidate

    for key in (
        "tags",
        "supports",
        "inspiration_points",
        "applicable_steps",
        "applicable_work_types",
    ):
        merged[key] = unique_list((merged.get(key, []) or []) + (incoming.get(key, []) or []))

    merged["reusable"] = bool(merged.get("reusable", False) or incoming.get("reusable", False))
    reliability_order = {"low": 1, "medium": 2, "high": 3}
    current_rel = str(merged.get("reliability", "medium") or "medium")
    incoming_rel = str(incoming.get("reliability", "medium") or "medium")
    merged["reliability"] = incoming_rel if reliability_order.get(incoming_rel, 0) > reliability_order.get(current_rel, 0) else current_rel

    current_tier = str(merged.get("reusability_tier", "low") or "low")
    incoming_tier = str(incoming.get("reusability_tier", "low") or "low")
    merged["reusability_tier"] = incoming_tier if reliability_order.get(incoming_tier, 0) > reliability_order.get(current_tier, 0) else current_tier

    current_status = str(merged.get("curation_status", "raw") or "raw")
    incoming_status = str(incoming.get("curation_status", "raw") or "raw")
    status_order = {"raw": 1, "normalized": 2, "reviewed": 3}
    merged["curation_status"] = incoming_status if status_order.get(incoming_status, 0) > status_order.get(current_status, 0) else current_status

    meta = merged.get("registry_meta", {}) if isinstance(merged.get("registry_meta", {}), dict) else {}
    meta["first_seen_at"] = meta.get("first_seen_at") or incoming.get("collected_at", "") or now_iso()
    meta["last_seen_at"] = now_iso()
    meta["seen_in_topics"] = unique_list((meta.get("seen_in_topics", []) or []) + [incoming.get("topic_name", "")])
    meta["import_count"] = int(meta.get("import_count", 0) or 0) + 1
    meta["last_seen_source_path"] = incoming.get("source_path", "") or incoming.get("source_locator", "")
    merged["registry_meta"] = meta
    merged["schema_version"] = EVIDENCE_SCHEMA_VERSION
    return merged


def upsert_registry_item(existing: list[dict], new_item: dict) -> str:
    incoming = normalize_evidence_item(new_item)
    for index, item in enumerate(existing):
        if item.get("fingerprint") == incoming.get("fingerprint"):
            existing[index] = merge_registry_item(item, incoming)
            return "updated"
    created = merge_registry_item({}, incoming)
    existing.append(created)
    return "created"


def build_source_overview(topic_dir: Path) -> dict:
    assets_path = topic_dir / "workspace" / "intake" / "topic-assets.json"
    assets = {"rules": [], "references": [], "samples": []}
    if assets_path.exists():
        assets = read_json(assets_path)
    external_items = [
        str(path.relative_to(topic_dir))
        for path in sorted((topic_dir / "external_evidence").rglob("*"))
        if path.is_file() and path.name.lower() != "readme.md"
    ] if (topic_dir / "external_evidence").exists() else []
    base_references = [
        rel for rel in assets.get("references", [])
        if not rel.replace("\\", "/").startswith("external_evidence/")
    ]
    return {
        "rules": assets.get("rules", []),
        "references": base_references,
        "external_evidence": external_items,
        "samples": assets.get("samples", []),
    }


def build_spec_evidence(topic_dir: Path, spec: dict) -> list[dict]:
    rule_rel = ""
    source_overview = build_source_overview(topic_dir)
    if source_overview["rules"]:
        rule_rel = source_overview["rules"][0]
    common = {
        "topic_name": topic_dir.name,
        "source_type": "local_file",
        "source_role": "rule",
        "source_path": rule_rel,
        "source_title": spec.get("competition_name") or "比赛细则",
        "source_locator": "workspace/requirements/competition-spec.json",
        "collected_at": now_iso(),
        "reusable": True,
        "reliability": "high",
        "source_origin": "requirements",
        "source_authority": "competition_official",
        "applicable_work_types": [],
        "curation_status": "reviewed",
        "limitations": "",
    }
    items: list[dict] = []
    if spec.get("scoring_dimensions"):
        claim = "比赛评分重点集中在：" + "、".join(spec["scoring_dimensions"])
        items.append(
            {
                **common,
                "evidence_id": build_evidence_id("scoring|" + claim),
                "claim": claim,
                "summary": "评分维度直接决定 idea 的匹配度叙事和后续作品书章节分配。",
                "excerpt": claim,
                "tags": ["评分标准", *spec["scoring_dimensions"]],
                "supports": ["评分维度对齐", "章节权重分配"],
                "inspiration_points": ["可直接映射到作品书的章节轻重、创新表述和答辩重心。"],
                "derived_insight": "评分标准决定后续 idea 叙事和作品书结构取舍。",
                "fingerprint": hashlib.sha1(claim.encode("utf-8")).hexdigest(),
            }
        )
    if spec.get("submission_format"):
        claim = spec["submission_format"]
        items.append(
            {
                **common,
                "evidence_id": build_evidence_id("format|" + claim),
                "claim": claim,
                "summary": "交付形式要求作品不能只有概念描述，还要便于演示和答辩呈现。",
                "excerpt": claim,
                "tags": ["交付要求", "演示"],
                "supports": ["交付形式设计", "答辩展示结构"],
                "inspiration_points": ["需要同步考虑文档、文档说明、document record，而不是只生成文字方案。"],
                "derived_insight": "交付要求会反向约束系统展示方式和 record 结构。",
                "fingerprint": hashlib.sha1(claim.encode("utf-8")).hexdigest(),
            }
        )
    for item in spec.get("forbidden_points", []):
        items.append(
            {
                **common,
                "evidence_id": build_evidence_id("forbidden|" + item),
                "claim": item,
                "summary": "这是 idea 选型和作品书撰写流程必须持续满足的硬约束。",
                "excerpt": item,
                "tags": ["禁区", "原创性"],
                "supports": ["合规约束"],
                "inspiration_points": ["后续所有方案扩展都不能越过原创性和知识产权边界。"],
                "derived_insight": "这是选题和写作流程都必须持续满足的硬约束。",
                "fingerprint": hashlib.sha1(item.encode("utf-8")).hexdigest(),
            }
        )
    return [normalize_evidence_item(item) for item in items]


def build_file_evidence(topic_dir: Path, rel_path: str, source_role: str) -> dict | None:
    path = topic_dir / rel_path
    if not path.exists():
        return None
    if should_skip_reference(rel_path):
        return None
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return None
    extraction = extract_source(path, topic_dir / "workspace" / "sources")
    raw_text = extraction["text"]
    if not raw_text:
        return None
    source_role = infer_source_role(rel_path, raw_text, source_role)
    snippets = short_sentences(raw_text, limit=3)
    title = snippets[0] if snippets else path.stem
    claim, summary = build_reference_summary(path, raw_text, source_role, snippets)
    excerpt = " / ".join(snippets[:2])[:240]
    tags = detect_tags(raw_text) or [source_role]
    if source_role == "format_reference":
        tags = ["格式参考", "排版模板", *[tag for tag in tags if tag not in {"format_reference"}]]
    item = {
        "evidence_id": build_evidence_id(f"{source_role}|{rel_path}|{claim}"),
        "topic_name": topic_dir.name,
        "source_type": "local_file",
        "source_role": source_role,
        "source_path": rel_path,
        "source_title": title[:80],
        "source_locator": rel_path,
        "collected_at": now_iso(),
        "claim": claim,
        "summary": summary[:240],
        "excerpt": excerpt,
        "tags": tags,
        "reusable": source_role != "sample",
        "reliability": "low",
        "verification_status": "unverified",
        "source_sha256": extraction["source_sha256"],
        "extraction_record": str(Path(extraction["cache_path"]).relative_to(topic_dir)),
        "extraction_warnings": extraction["warnings"],
        "source_positions": [segment["locator"] for segment in extraction["segments"] if segment["text"].strip()][:3],
        "supports": detect_tags(raw_text)[:3],
        "derived_insight": summary[:240],
        "source_origin": "topic_workspace_scan",
        "applicable_work_types": [],
        "usage_hint": "",
        "limitations": "",
        "fingerprint": hashlib.sha1(f"{rel_path}|{excerpt}".encode("utf-8")).hexdigest(),
    }
    if source_role == "sample":
        item["inspiration_points"] = [
            "可借鉴其问题组织、模块拆分和论证节奏，但不得直接复用其中事实、数据或结论。"
        ]
        item["limitations"] = "样例只能提供表达和结构启发，不能直接充当当前项目的事实依据。"
    elif source_role == "format_reference":
        item["inspiration_points"] = [
            "可复用其排版结构、章节顺序和交付样式，但不能直接当作领域问题证据。"
        ]
        item["supports"] = ["排版结构", "交付样式"]
    else:
        item["inspiration_points"] = [f"可复用启发：{summary[:120]}"]
    return normalize_evidence_item(item)


def build_external_research_evidence(topic_dir: Path, rel_path: str) -> list[dict]:
    path = topic_dir / rel_path
    if not path.exists() or path.suffix.lower() != ".json":
        return []
    payload = read_json(path)
    items: list[dict] = []
    for index, raw in enumerate(payload.get("items", []), start=1):
        source_title = raw.get("source_title", "").strip()
        source_url = raw.get("source_url", "").strip()
        claim = raw.get("claim", "").strip()
        summary = raw.get("summary", "").strip()
        if not (source_title and claim and summary):
            continue
        tags = list(dict.fromkeys((raw.get("tags", []) or []) + (raw.get("evidence_for", []) or []) + detect_tags(" ".join([claim, summary, source_title]))))
        seed = f"{rel_path}|{source_url}|{claim}|{summary}"
        items.append(
            normalize_evidence_item(
                {
                    "evidence_id": build_evidence_id(seed),
                    "topic_name": topic_dir.name,
                    "source_type": raw.get("source_type", "paper"),
                    "source_role": "external_research",
                    "source_path": rel_path,
                    "source_title": source_title[:120],
                    "source_locator": source_url or f"{rel_path}#item-{index}",
                    "published_at": raw.get("published_at", "").strip(),
                    "collected_at": now_iso(),
                    "claim": claim,
                    "summary": summary[:300],
                    "excerpt": (raw.get("notes", "") or summary)[:240],
                    "tags": tags or ["external_research"],
                    "reusable": True,
                    "reliability": raw.get("reliability", "high"),
                    "notes": raw.get("notes", "").strip(),
                    "source_authority": raw.get("source_authority", "").strip(),
                    "source_origin": raw.get("source_origin", "").strip() or "manual_external_intake",
                    "evidence_kind": raw.get("evidence_kind", "").strip(),
                    "supports": raw.get("evidence_for", []) or [],
                    "derived_insight": raw.get("derived_insight", "").strip() or summary[:300],
                    "inspiration_points": raw.get("inspiration_points", []) or [],
                    "applicable_steps": raw.get("applicable_steps", []) or [],
                    "applicable_work_types": raw.get("applicable_work_types", []) or [],
                    "curation_status": raw.get("curation_status", "").strip() or "reviewed",
                    "usage_hint": raw.get("usage_hint", "").strip(),
                    "limitations": raw.get("limitations", "").strip(),
                    "fingerprint": hashlib.sha1(seed.encode("utf-8")).hexdigest(),
                }
            )
        )
    return items


def build_seed_evidence(topic_dir: Path, seed_text: str) -> dict | None:
    seed = seed_text.strip()
    if not seed:
        return None
    return normalize_evidence_item(
        {
        "evidence_id": build_evidence_id("seed|" + seed),
        "topic_name": topic_dir.name,
        "source_type": "human_seed",
        "source_role": "seed_direction",
        "source_path": "",
        "source_title": "人工主轴输入",
        "source_locator": "cli:--seed-text",
        "collected_at": now_iso(),
        "claim": seed,
        "summary": "这是人工指定的主轴，不是外部事实证据，后续只允许在这个方向内扩展变体。",
        "excerpt": seed,
        "tags": detect_tags(seed) or ["人工主轴"],
        "reusable": True,
        "reliability": "medium",
        "supports": ["选题边界"],
        "derived_insight": "人工主轴只用于限制扩展方向，不可直接当作事实依据。",
        "inspiration_points": ["后续变体应围绕这条主轴扩展，但所有论证仍需补事实证据。"],
        "source_origin": "human_cli_input",
        "applicable_work_types": [],
        "usage_hint": "只在 Step2 做同轴变体约束使用。",
        "limitations": "不是事实证据，不能直接出现在作品书论证链中。",
        "fingerprint": hashlib.sha1(seed.encode("utf-8")).hexdigest(),
        }
    )


def update_workspace_state(topic_dir: Path, success: bool, blocking_reason: str) -> None:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not state_path.exists():
        return
    state = read_json(state_path)
    state["current_step"] = "ideas"
    state["workflow_status"]["ideas"] = "active"
    state["next_action"] = "run_ideas" if success else "fix_evidence"
    state["blocking_reason"] = blocking_reason
    state["required_inputs"] = [] if success else ["补充可读取的参考材料或主轴输入"]
    write_json(state_path, state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AutoSearch MVP step2 evidence sweep.")
    parser.add_argument("topic_dir", help="Topic directory, such as sample/topic_xx")
    parser.add_argument("--topic", default="", help="Optional topic override. Defaults to workspace topic_name.")
    parser.add_argument("--seed-text", default="", help="Optional human seed direction for same-axis idea expansion.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    spec_path = topic_dir / "workspace" / "requirements" / "competition-spec.json"
    step_dir = topic_dir / "workspace" / "ideas"
    if not spec_path.exists():
        raise SystemExit("competition-spec.json not found. Run step1 first.")

    spec = read_json(spec_path)
    source_overview = build_source_overview(topic_dir)
    evidence_items = build_spec_evidence(topic_dir, spec)

    for rel in source_overview["references"]:
        item = build_file_evidence(topic_dir, rel, "reference")
        if item:
            evidence_items.append(item)
    for rel in source_overview.get("external_evidence", []):
        if rel.endswith(".json"):
            evidence_items.extend(build_external_research_evidence(topic_dir, rel))
            continue
        item = build_file_evidence(topic_dir, rel, "reference")
        if item:
            evidence_items.append(item)
    for rel in source_overview["samples"]:
        item = build_file_evidence(topic_dir, rel, "sample")
        if item:
            evidence_items.append(item)

    seed_item = build_seed_evidence(topic_dir, args.seed_text)
    if seed_item:
        evidence_items.append(seed_item)

    if not evidence_items:
        update_workspace_state(topic_dir, success=False, blocking_reason="未生成任何有效证据项")
        raise SystemExit("No evidence items generated for step2.")

    tags: list[str] = []
    for item in evidence_items:
        for tag in item.get("tags", []):
            if tag not in tags:
                tags.append(tag)

    scoring_focus = spec.get("scoring_dimensions", [])
    domain_tags = [tag for tag in tags if tag not in {"格式参考", "排版模板", "交付要求", "演示"}]
    topic_profile = resolve_topic_profile(
        topic_dir,
        explicit_topic=args.topic,
        context_text="\n".join(
            source_overview["rules"] + source_overview["references"] + source_overview["samples"] + source_overview.get("external_evidence", [])
        ),
        seed_text=args.seed_text,
        extra_tags=domain_tags,
    )
    recommended_direction = build_recommended_directions(
        topic_profile,
        seed_text=args.seed_text,
        domain_tags=domain_tags,
    )

    ledger = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "topic_name": topic_profile.get("topic_name", topic_dir.name),
        "topic_profile": {
            "profile_id": topic_profile.get("profile_id", ""),
            "display_name": topic_profile.get("display_name", ""),
            "domain_label": topic_profile.get("domain_label", ""),
            "keywords": topic_profile.get("keywords", []),
        },
        "competition_name": spec.get("competition_name", ""),
        "seed_direction": args.seed_text.strip(),
        "source_overview": source_overview,
        "evidence_items": evidence_items,
        "summary": {
            "top_themes": domain_tags[:8],
            "scoring_focus": scoring_focus,
            "recommended_direction": recommended_direction,
            "open_gaps": spec.get("pending_confirmations", []),
        },
        "shared_registry_sync": {
            "registry_schema_version": EVIDENCE_SCHEMA_VERSION,
            "registry_path": str(EVIDENCE_REGISTRY_PATH.relative_to(REPO_ROOT)),
            "created_ids": [],
            "updated_ids": [],
        },
    }

    registry = ensure_registry()
    created_ids: list[str] = []
    updated_ids: list[str] = []
    for item in evidence_items:
        result = upsert_registry_item(registry["items"], item)
        if result == "created":
            created_ids.append(item["evidence_id"])
        else:
            updated_ids.append(item["evidence_id"])
    write_json(EVIDENCE_REGISTRY_PATH, registry)
    ledger["shared_registry_sync"]["created_ids"] = created_ids
    ledger["shared_registry_sync"]["updated_ids"] = updated_ids

    summary_lines = [
        "# Evidence Summary",
        "",
        f"- Topic: {topic_profile.get('topic_name', topic_dir.name)}",
        f"- Topic Profile: {topic_profile.get('display_name', 'unknown')}",
        f"- Competition: {spec.get('competition_name') or 'unknown'}",
        f"- Seed Direction: {args.seed_text.strip() or 'none'}",
        f"- Evidence Items: {len(evidence_items)}",
        f"- Shared Registry Created: {len(created_ids)}",
        f"- Shared Registry Updated: {len(updated_ids)}",
        "",
        "## Source Overview",
        f"- Rules: {len(source_overview['rules'])}",
        f"- References: {len(source_overview['references'])}",
        f"- External Evidence Files: {len(source_overview.get('external_evidence', []))}",
        f"- Samples: {len(source_overview['samples'])}",
        "",
        "## Theme Summary",
        f"- Domain Themes: {'、'.join(domain_tags[:8]) or 'none'}",
        f"- Format Themes: {'、'.join([tag for tag in tags if tag in {'格式参考', '排版模板', '交付要求', '演示'}]) or 'none'}",
        "",
        "## Recommended Direction",
    ]
    summary_lines.extend([f"- {item}" for item in recommended_direction] or ["- pending"])
    summary_lines.extend(["", "## Evidence Items"])
    for item in evidence_items:
        summary_lines.extend(
            [
                f"### {item['evidence_id']} | {item['source_role']}",
                f"- Source: {item['source_path'] or item['source_locator']}",
                f"- Source Authority: {item.get('source_authority', '') or 'unknown'}",
                f"- Source Origin: {item.get('source_origin', '') or 'unknown'}",
                f"- Evidence Kind: {item.get('evidence_kind', '') or 'unknown'}",
                f"- Claim: {item['claim']}",
                f"- Summary: {item['summary']}",
                f"- Derived Insight: {item.get('derived_insight', '') or 'none'}",
                f"- Inspiration: {'；'.join(item.get('inspiration_points', [])) or 'none'}",
                f"- Supports: {'、'.join(item.get('supports', [])) or 'none'}",
                f"- Applicable Steps: {'、'.join(item.get('applicable_steps', [])) or 'none'}",
                f"- Applicable Work Types: {'、'.join(item.get('applicable_work_types', [])) or 'none'}",
                f"- Tags: {'、'.join(item.get('tags', [])) or 'none'}",
                f"- Reliability: {item['reliability']}",
                f"- Reusability Tier: {item.get('reusability_tier', '') or 'unknown'}",
                f"- Curation Status: {item.get('curation_status', '') or 'unknown'}",
                f"- Usage Hint: {item.get('usage_hint', '') or 'none'}",
                f"- Limitations: {item.get('limitations', '') or 'none'}",
                "",
            ]
        )
    summary_lines.extend(["## Open Gaps"])
    summary_lines.extend([f"- {item}" for item in ledger["summary"]["open_gaps"]] or ["- none"])

    write_json(step_dir / "evidence-ledger.json", ledger)
    write_text(step_dir / "evidence-summary.md", "\n".join(summary_lines) + "\n")
    update_workspace_state(topic_dir, success=True, blocking_reason="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Final delivery gates for complete long-form documents."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def iter_visual_specs(plan: dict[str, Any]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for section in plan.get("sections", []):
        for item in section.get("visual_specs", []):
            if isinstance(item, dict):
                copy = dict(item)
                copy.setdefault("section_id", section.get("section_id", ""))
                copy.setdefault("section_heading", section.get("heading", ""))
                copy.setdefault("evidence_ids", section.get("supporting_evidence_ids", []))
                specs.append(copy)
    return specs


def _asset_candidates(topic_dir: Path, spec: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    visual_id = str(spec.get("visual_id", "")).strip()
    for raw in spec.get("asset_candidates", []):
        value = str(raw).strip()
        if not value:
            continue
        path = Path(value)
        if path.is_absolute():
            candidates.append(path)
        else:
            candidates.extend(
                [
                    topic_dir / path,
                    topic_dir / "workspace" / "document_assets" / "figures" / path.name,
                    topic_dir / "workspace" / "document_export" / "assets" / "visuals" / path.name,
                ]
            )
    if visual_id:
        for suffix in (".png", ".svg", ".pdf", ".jpg", ".jpeg"):
            candidates.extend(
                [
                    topic_dir / "workspace" / "document_assets" / "figures" / f"{visual_id}{suffix}",
                    topic_dir / "workspace" / "document_export" / "assets" / "visuals" / f"{visual_id}{suffix}",
                ]
            )
    return list(dict.fromkeys(candidates))


def _is_table(spec: dict[str, Any]) -> bool:
    return str(spec.get("visual_type", "")).lower() == "table" or "表" in str(spec.get("title", ""))


def _is_diagram(spec: dict[str, Any]) -> bool:
    title = str(spec.get("title", ""))
    return any(token in title for token in ("图", "架构", "流程", "链路", "时序", "闭环", "拓扑", "示意", "映射", "矩阵"))


def _is_case_or_ui(spec: dict[str, Any]) -> bool:
    title = str(spec.get("title", ""))
    return any(token in title for token in ("案例", "回放", "界面", "截图", "工作台", "演示", "交互"))


def _count_markdown_tables(draft: str) -> int:
    count = 0
    in_table = False
    for line in draft.splitlines():
        is_row = line.strip().startswith("|") and line.strip().endswith("|")
        if is_row and not in_table:
            count += 1
        in_table = is_row
    return count


def _table_quality(draft: str) -> dict[str, bool]:
    return {
        "has_units": "单位" in draft,
        "has_sources": "来源" in draft or "数据来源" in draft,
        "has_statistical_basis": "统计" in draft or "统计口径" in draft or "置信区间" in draft,
        "has_missing_value_rule": "缺失" in draft or bool(re.search(r"\b(?:NA|N/A|null)\b", draft, re.I)),
    }


def build_visual_gate(topic_dir: Path, plan: dict[str, Any], draft: str) -> dict[str, Any]:
    contract = plan.get("content_contract", {}).get("visual_contract", {}) or {}
    specs = iter_visual_specs(plan)
    required = [item for item in specs if item.get("required", True)]
    external = [item for item in required if not _is_table(item)]
    available: list[str] = []
    requested: list[str] = []
    missing: list[str] = []
    for spec in external:
        visual_id = str(spec.get("visual_id", ""))
        if any(path.exists() and path.stat().st_size > 0 for path in _asset_candidates(topic_dir, spec)):
            available.append(visual_id)
        else:
            request = topic_dir / "workspace" / "document_assets" / "figures" / f"{visual_id}.request.json"
            (requested if request.exists() else missing).append(visual_id)

    labels = [str(item.get("label", "")).strip() for item in required if item.get("label")]
    references = set(re.findall(r"[图表]\s*\d+(?:[-.．]\d+)+", draft))
    uncited = [label for label in labels if label and not any(label.replace(" ", "") in ref.replace(" ", "") for ref in references)]
    tables_in_draft = _count_markdown_tables(draft)
    table_quality = _table_quality(draft)
    diagrams = sum(_is_diagram(item) for item in required)
    case_or_ui = sum(_is_case_or_ui(item) for item in required)
    required_assets_min = int(contract.get("required_external_assets_min", 0) or 0)
    ratio = (len(available) / len(external)) if external else 1.0
    failures: list[str] = []
    if len(required) < int(contract.get("required_specs_min", 0) or 0):
        failures.append(f"视觉规格不足：{len(required)} < {contract.get('required_specs_min', 0)}")
    if len(available) < required_assets_min:
        failures.append(f"可用外部视觉资产不足：{len(available)} < {required_assets_min}")
    if ratio < float(contract.get("required_asset_ratio", 1.0) or 1.0):
        failures.append(f"外部视觉资产完成率不足：{ratio:.2f} < {contract.get('required_asset_ratio', 1.0)}")
    if tables_in_draft < int(contract.get("required_tables_min", 0) or 0):
        failures.append(f"正文表格不足：{tables_in_draft} < {contract.get('required_tables_min', 0)}")
    if tables_in_draft and int(contract.get("required_tables_min", 0) or 0):
        missing_table_fields = [key for key, passed in table_quality.items() if not passed]
        if missing_table_fields:
            failures.append("表格解释元数据缺失：" + "、".join(missing_table_fields))
    if diagrams < int(contract.get("required_diagrams_min", 0) or 0):
        failures.append(f"图示规格不足：{diagrams} < {contract.get('required_diagrams_min', 0)}")
    if case_or_ui < int(contract.get("required_case_or_ui_visuals_min", 0) or 0):
        failures.append(f"案例/界面视觉规格不足：{case_or_ui} < {contract.get('required_case_or_ui_visuals_min', 0)}")
    if contract.get("all_visuals_must_be_cited", True) and uncited:
        failures.append("正文未引用全部必需视觉项：" + "、".join(uncited[:12]))
    return {
        "passed": not failures,
        "failures": failures,
        "required_specs": len(required),
        "external_specs": len(external),
        "available_assets": len(available),
        "requested_assets": len(requested),
        "missing_assets": len(missing),
        "available_ids": available,
        "requested_ids": requested,
        "missing_ids": missing,
        "uncited_labels": uncited,
        "tables_in_draft": tables_in_draft,
        "table_quality": table_quality,
        "diagram_specs": diagrams,
        "case_or_ui_specs": case_or_ui,
        "asset_ratio": ratio,
        "contract": contract,
    }

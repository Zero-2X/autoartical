"""Final delivery gates for complete long-form documents."""
from __future__ import annotations

import re
import hashlib
import json
import struct
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


def _imagegen_record(topic_dir: Path, visual_id: str, draft: str) -> tuple[bool, str, str]:
    """Validate the actual image, manuscript link, prompt provenance and visual review."""
    figures = topic_dir / "workspace" / "document_assets" / "figures"
    asset = figures / f"{visual_id}.png"
    request_path = figures / f"{visual_id}.request.json"
    if not request_path.exists():
        return False, "缺少逐图理解与 Prompt 记录", ""
    try:
        request = json.loads(request_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, "逐图记录无法读取", ""
    understanding = request.get("article_understanding", {})
    if request.get("status") != "reviewed":
        return False, "该图尚未完成 ImageGen 生成与目视审查", ""
    if draft:
        from visual_prompting import manuscript_sha256
        if request.get("source_draft_sha256") != manuscript_sha256(draft):
            return False, "文章正文已变化，图像理解和 Prompt 需要重新审查", ""
    if not isinstance(understanding, dict) or not all(
        [len(str(understanding.get("context_excerpt", ""))) >= 60,
         len(str(understanding.get("key_message", ""))) >= 15,
         len(str(understanding.get("evidence_boundary", ""))) >= 15,
         len(understanding.get("visual_elements", [])) >= 3]
    ):
        return False, "缺少从正文提炼的图意、元素或证据边界", ""
    prompt = str(request.get("prompt", ""))
    if len(prompt) < 400:
        return False, "ImageGen Prompt 不够完整（至少 400 字符）", ""
    required_prompt_content = [
        str(understanding.get("key_message", "")),
        str(understanding.get("evidence_boundary", "")),
        str(understanding.get("visual_direction", "")),
        *(str(item) for item in understanding.get("visual_elements", [])),
    ]
    if any(not item or item not in prompt for item in required_prompt_content):
        return False, "完整 Prompt 未采用该图的文章主张、视觉元素、边界和构图", ""
    generation = request.get("generation", {})
    if (request.get("route") != "Codex built-in image_gen" or
            generation.get("tool") != "image_gen.imagegen" or
            "generated_images" not in str(generation.get("source_path", "")) or
            generation.get("prompt_sha256") != hashlib.sha256(prompt.encode("utf-8")).hexdigest()):
        return False, "缺少 Codex 内置 ImageGen 生成来源或提示词校验", ""
    if not asset.exists() or asset.stat().st_size < 100_000:
        return False, "缺少有效 ImageGen PNG", ""
    data = asset.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        return False, "资产不是有效 PNG", ""
    width, height = struct.unpack(">II", data[16:24])
    if width < 1000 or height < 500:
        return False, "ImageGen 图片分辨率不足", ""
    image_hash = hashlib.sha256(data).hexdigest()
    if generation.get("asset_sha256") != image_hash:
        return False, "图片与生成记录的散列不一致", ""
    review = request.get("visual_review", {})
    if (request.get("status") != "reviewed" or review.get("status") != "pass" or
            not all(review.get(key) is True for key in ("semantic_fidelity", "legibility", "uniqueness", "no_fabrication")) or
            len(str(review.get("note", ""))) < 20):
        return False, "缺少逐图语义、可读性、独特性和事实审查", ""
    if draft and not any(visual_id + ".png" in line for line in draft.splitlines() if line.lstrip().startswith("![")):
        return False, "正文未嵌入该 ImageGen PNG", ""
    return True, "", image_hash


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
    invalid_assets: dict[str, str] = {}
    seen_hashes: dict[str, str] = {}
    seen_prompts: dict[str, str] = {}
    for spec in external:
        visual_id = str(spec.get("visual_id", ""))
        valid, reason, image_hash = _imagegen_record(topic_dir, visual_id, draft)
        request_path = topic_dir / "workspace" / "document_assets" / "figures" / f"{visual_id}.request.json"
        if valid:
            request_data = json.loads(request_path.read_text(encoding="utf-8"))
            prompt_hash = hashlib.sha256(str(request_data.get("prompt", "")).encode("utf-8")).hexdigest()
            if prompt_hash in seen_prompts:
                valid, reason = False, f"与 {seen_prompts[prompt_hash]} 复用了同一 Prompt"
        if valid and image_hash in seen_hashes:
            valid, reason = False, f"与 {seen_hashes[image_hash]} 重复使用同一图片"
        if valid:
            available.append(visual_id)
            seen_hashes[image_hash] = visual_id
            seen_prompts[prompt_hash] = visual_id
        else:
            (requested if request_path.exists() else missing).append(visual_id)
            invalid_assets[visual_id] = reason

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
    if invalid_assets:
        failures.append("ImageGen 逐图记录或资产未通过：" + "；".join(f"{key}: {value}" for key, value in list(invalid_assets.items())[:12]))
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
        "invalid_assets": invalid_assets,
        "uncited_labels": uncited,
        "tables_in_draft": tables_in_draft,
        "table_quality": table_quality,
        "diagram_specs": diagrams,
        "case_or_ui_specs": case_or_ui,
        "asset_ratio": ratio,
        "contract": contract,
    }

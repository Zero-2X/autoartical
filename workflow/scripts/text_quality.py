"""Auditable prose quality checks for long-form documents."""
from __future__ import annotations

import re
from typing import Any

from content_depth import DEFAULT_CONTRACT, content_metrics, prose_paragraphs


def _table_blocks(text: str) -> int:
    count = 0
    active = False
    for line in text.splitlines():
        row = line.strip().startswith("|") and line.strip().endswith("|")
        if row and not active:
            count += 1
        active = row
    return count


def _table_quality(text: str) -> dict[str, bool]:
    """Check the minimum metadata needed to interpret evidence tables."""
    return {
        "has_units": "单位" in text,
        "has_sources": "来源" in text or "数据来源" in text,
        "has_statistical_basis": "统计" in text or "统计口径" in text or "置信区间" in text,
        "has_missing_value_rule": "缺失" in text or bool(re.search(r"\b(?:NA|N/A|null)\b", text, re.I)),
    }


def _visual_references(text: str) -> int:
    return len(set(re.findall(r"[图表]\s*\d+(?:[-.．]\d+)+", text)))


def _heading_count(text: str) -> int:
    return len(re.findall(r"(?m)^#{1,6}\s+\S+", text))


def _paragraph_units(paragraph: str) -> int:
    return len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]|[A-Za-z0-9]+(?:[-_/][A-Za-z0-9]+)*", paragraph))


def audit_text_quality(text: str, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or DEFAULT_CONTRACT
    metrics = content_metrics(text)
    paragraphs = prose_paragraphs(text)
    paragraph_units = [_paragraph_units(item) for item in paragraphs]
    paragraph_count = len(paragraph_units)
    thin_threshold = 48
    thin = [value for value in paragraph_units if value < thin_threshold]
    thin_ratio = (len(thin) / paragraph_count) if paragraph_count else 1.0
    citation_count = len(set(re.findall(r"\[[0-9]+\]|https?://\S+", text)))
    table_blocks = _table_blocks(text)
    table_quality = _table_quality(text)
    required_terms = {
        "problem_definition": ["研究问题", "关键问题", "问题"],
        "method_mechanism": ["输入", "输出", "机制", "方法"],
        "experiment_protocol": ["benchmark", "基线", "指标", "数据划分", "消融"],
        "boundary_and_risk": ["边界", "风险", "局限"],
    }
    term_status = {key: any(term in text for term in terms) for key, terms in required_terms.items()}
    failures: list[str] = []
    minimum = int(contract.get("body_units_min", DEFAULT_CONTRACT["body_units_min"]) or 0)
    if metrics["prose_units"] < minimum:
        failures.append(f"有效正文不足：{metrics['prose_units']} < {minimum}")
    if metrics["duplicate_paragraph_groups"]:
        failures.append("存在重复正文段落，重复内容不计入有效篇幅")
    if thin_ratio > 0.35 and paragraph_count >= 10:
        failures.append(f"薄段落比例过高：{thin_ratio:.2f} > 0.35")
    if citation_count < 3:
        failures.append(f"可追溯引用不足：{citation_count} < 3")
    if table_blocks:
        missing_table_fields = [key for key, passed in table_quality.items() if not passed]
        if missing_table_fields:
            failures.append("表格解释元数据缺失：" + "、".join(missing_table_fields))
    missing_term_groups = [key for key, passed in term_status.items() if not passed]
    if missing_term_groups:
        failures.append("关键论证信息缺失：" + "、".join(missing_term_groups))
    return {
        "passed": not failures,
        "failures": failures,
        "prose_units": metrics["prose_units"],
        "body_units_min": minimum,
        "body_units_target": int(contract.get("body_units_target", DEFAULT_CONTRACT["body_units_target"]) or 0),
        "paragraph_count": paragraph_count,
        "thin_paragraph_count": len(thin),
        "thin_paragraph_ratio": round(thin_ratio, 3),
        "duplicate_paragraph_groups": metrics["duplicate_paragraph_groups"],
        "heading_count": _heading_count(text),
        "citation_count": citation_count,
        "table_blocks": table_blocks,
        "table_quality": table_quality,
        "visual_references": _visual_references(text),
        "term_status": term_status,
        "short_document": metrics["prose_units"] < minimum,
    }

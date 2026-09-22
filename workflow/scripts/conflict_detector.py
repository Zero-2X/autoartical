from __future__ import annotations

import re
from typing import Any


NUMBER_RE = re.compile(r"\d+(?:\.\d+)?%?")
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
METRIC_KEYWORDS = [
    "准确率",
    "召回率",
    "精度",
    "F1",
    "成本",
    "时延",
    "延迟",
    "吞吐",
    "增长",
    "下降",
    "提升",
    "降低",
    "占比",
    "比例",
    "规模",
    "数量",
    "排名",
    "得分",
]
RELIABLE_LEVELS = {"high", "medium"}
IGNORED_SOURCE_TYPES = {"research_query"}
IGNORED_EVIDENCE_KINDS = {"research_query"}


def is_comparable_item(item: dict[str, Any]) -> bool:
    if str(item.get("source_type", "")) in IGNORED_SOURCE_TYPES:
        return False
    if str(item.get("evidence_kind", "")) in IGNORED_EVIDENCE_KINDS:
        return False
    if str(item.get("reliability", "low")).lower() not in RELIABLE_LEVELS:
        return False
    claim = str(item.get("claim") or item.get("summary") or "")
    if not claim or claim.lstrip().startswith(("{", "[")):
        return False
    return bool(extract_numeric_signature(claim))


def extract_numeric_signature(claim: str) -> dict[str, set[str]]:
    numbers = set(NUMBER_RE.findall(claim))
    years = set(YEAR_RE.findall(claim))
    numbers -= years
    if not numbers:
        return {}
    metrics = {keyword for keyword in METRIC_KEYWORDS if keyword in claim}
    percentages = {number for number in numbers if number.endswith("%")}
    plain_numbers = numbers - percentages
    signature: dict[str, set[str]] = {}
    if percentages and metrics:
        for metric in metrics:
            signature[f"percent:{metric}"] = percentages
    if plain_numbers and metrics:
        for metric in metrics:
            signature[f"number:{metric}"] = plain_numbers
    return signature


def detect_conflicts(items: list[dict[str, Any]]) -> dict[str, Any]:
    by_tag: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        if not is_comparable_item(item):
            continue
        for tag in item.get("tags", []) or ["untagged"]:
            by_tag.setdefault(str(tag), []).append(item)
    conflicts = []
    for tag, tagged_items in by_tag.items():
        by_metric: dict[str, list[dict[str, Any]]] = {}
        for item in tagged_items:
            claim = str(item.get("claim") or item.get("summary") or "")
            for metric, values in extract_numeric_signature(claim).items():
                by_metric.setdefault(metric, []).append({"claim": claim, "values": sorted(values)})
        for metric, metric_claims in by_metric.items():
            value_sets = {tuple(entry["values"]) for entry in metric_claims}
            if len(metric_claims) >= 2 and len(value_sets) > 1:
                conflicts.append(
                    {
                        "tag": tag,
                        "metric": metric,
                        "reason": "different_numeric_claims",
                        "claims": [entry["claim"] for entry in metric_claims[:5]],
                    }
                )
    return {
        "verdict": "pass" if not conflicts else "warn",
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "checked_item_count": sum(1 for item in items if is_comparable_item(item)),
    }

from __future__ import annotations

import re
from typing import Any


URL_RE = re.compile(r"https?://")


def check_citations(items: list[dict[str, Any]]) -> dict[str, Any]:
    warnings = []
    for item in items:
        source_type = item.get("source_type", "")
        url = item.get("source_url", "") or item.get("source_locator", "")
        if source_type in {"paper", "industry_report", "official_platform", "web"} and not URL_RE.search(str(url)):
            warnings.append({"source_title": item.get("source_title", ""), "warning": "missing_url"})
        if item.get("source_type") == "research_query":
            warnings.append({"source_title": item.get("source_title", ""), "warning": "query_plan_not_fact_source"})
    return {
        "verdict": "pass" if not warnings else "warn",
        "warnings": warnings,
        "warning_count": len(warnings),
    }


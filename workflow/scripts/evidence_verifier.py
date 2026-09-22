from __future__ import annotations

from typing import Any


HIGH_AUTHORITY = {"competition_official", "academic", "official_platform", "industry_report", "local_material"}


def verify_evidence_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    results = []
    issues = []
    for item in items:
        item_issues = []
        if item.get("verification_status") == "unverified":
            item_issues.append("source_claim_requires_verification")
        if not item.get("source_title"):
            item_issues.append("missing_source_title")
        if not item.get("claim"):
            item_issues.append("missing_claim")
        if not item.get("summary"):
            item_issues.append("missing_summary")
        if item.get("source_authority") not in HIGH_AUTHORITY and item.get("reliability") == "high":
            item_issues.append("high_reliability_without_authority")
        if item_issues:
            issues.append({"source_title": item.get("source_title", ""), "issues": item_issues})
        results.append({"source_title": item.get("source_title", ""), "passed": not item_issues, "issues": item_issues})
    return {
        "verdict": "pass" if not issues else "warn",
        "checked": len(items),
        "issues": issues,
        "results": results,
    }


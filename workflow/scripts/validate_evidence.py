from __future__ import annotations
import argparse
import json
from pathlib import Path
from citation_checker import check_citations
from evidence_verifier import verify_evidence_items
from conflict_detector import detect_conflicts
def validate_ledger(data: object) -> dict:
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("evidence_items", data.get("items"))
    else:
        items = None
    if not isinstance(items, list) or not items or not all(isinstance(item, dict) for item in items):
        return {"verdict": "fail", "issues": ["证据台账必须包含非空 evidence_items/items 对象列表"]}
    report = {"citation_check": check_citations(items), "evidence_check": verify_evidence_items(items),
              "conflict_check": detect_conflicts(items)}
    report["verdict"] = "pass" if all(check["verdict"] == "pass" for check in report.values()) else "warn"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="核验证据台账结构、引用字段和潜在数值冲突；不代替原文核验")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--strict", action="store_true", help="存在告警时返回非零退出码")
    args = parser.parse_args()
    report = validate_ledger(json.loads(args.ledger.read_text(encoding="utf-8")))
    out = args.out or args.ledger.with_name("evidence-review.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["verdict"] == "fail" or (args.strict and report["verdict"] != "pass") else 0
if __name__=='__main__': raise SystemExit(main())

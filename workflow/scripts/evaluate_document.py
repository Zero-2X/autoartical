from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from text_quality import audit_text_quality

REQUIRED = ["摘要", "问题", "方案", "创新", "实施", "风险", "参考文献"]
GENERIC = ["本文将", "综上所述", "具有重要意义", "赋能", "打造", "助力", "显著提升", "值得注意的是"]


def main() -> int:
    parser = argparse.ArgumentParser(description="按论文、竞赛说明书、基金申报书和长文合同审查文档")
    parser.add_argument("document", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--allow-short", action="store_true", help="仅用于选题卡/短摘要等非最终文档，不能用于完整交付")
    args = parser.parse_args()

    text = args.document.read_text(encoding="utf-8")
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
    headings = re.findall(r"^#{1,4}\s+(.+)$", text, re.M)
    tables = [line for line in text.splitlines() if "|" in line and line.count("|") >= 2]
    cites = re.findall(r"\[[0-9]+\]|https?://\S+", text)
    table_quality = {
        "has_units": "单位" in text,
        "has_sources": "来源" in text or "数据来源" in text,
        "has_statistical_basis": "统计" in text or "置信区间" in text,
    }
    mermaid = "```mermaid" in text
    images = bool(re.search(r"!\[[^]]*\]\([^)]*\)", text))
    generic = {word: text.count(word) for word in GENERIC if text.count(word)}
    repeated = [paragraph[:80] for paragraph in paragraphs if len(paragraph) > 60 and paragraphs.count(paragraph) > 1]
    rubric = {
        "论文": {
            "问题与贡献": any(key in text for key in ["研究问题", "贡献"]),
            "方法与验证": any(key in text for key in ["方法", "验证", "实验"]),
            "引用可追溯": len(cites) >= 3,
        },
        "竞赛说明书": {
            "需求覆盖": any(key in text for key in ["需求", "用户"]),
            "方案闭环": all(key in text for key in ["方案", "实施", "风险"]),
            "评审友好": len(tables) >= 1,
        },
        "基金申报书": {
            "科学问题": any(key in text for key in ["科学问题", "关键问题"]),
            "技术路线": any(key in text for key in ["技术路线", "研究内容"]),
            "可行性与风险": all(key in text for key in ["可行性", "风险"]),
        },
    }
    score = sum(sum(bool(value) for value in group.values()) for group in rubric.values()) / 9
    quality = audit_text_quality(text)
    missing_sections = [item for item in REQUIRED if item not in text]
    hard_quality_failures = [] if args.allow_short else quality["failures"]
    verdict = "pass" if score >= 0.75 and not repeated and not missing_sections and not hard_quality_failures else "revise"
    report = {
        "document": str(args.document),
        "generated_checks": {
            "heading_count": len(headings),
            "paragraph_count": len(paragraphs),
            "table_line_count": len(tables),
            "citation_count": len(cites),
            "has_mermaid": mermaid,
            "has_embedded_image": images,
            "table_quality": table_quality,
            "generic_phrase_counts": generic,
            "repeated_paragraphs": repeated,
        },
        "text_quality": quality,
        "rubric": rubric,
        "coverage_score": round(score, 3),
        "ai_style_risks": generic,
        "verdict": verdict,
        "missing_sections": missing_sections,
        "mode": "short_allowed" if args.allow_short else "long_form_required",
    }
    out = args.out or args.document.with_name(args.document.stem + "-review.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

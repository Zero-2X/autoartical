#!/usr/bin/env python3
"""Explainable style checks for professional, author-preserving academic prose.

This is a quality lint, not an AI-detector and not a detector-evasion score.
It skips headings, tables, code, figure references and bibliography-like blocks.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any


PROHIBITED_UNSOURCED = [
    ("模糊归因", r"(?:专家认为|业内普遍认为|有观点认为|研究表明)(?![^。！？]{0,40}[\[（(][^。！？]{0,20}[\]）)])"),
]
EMPTY_CLOSERS = [
    ("泛化价值结论", r"(?:具有重要意义|意义重大|意义深远|前景广阔|开辟了新方向|提供了新思路)"),
    ("段末总结套句", r"(?:综上所述|由此可见|不难发现|可以看出)[，。]?$"),
]
FILLERS = [
    "值得注意的是", "需要指出的是", "总体而言", "在一定程度上", "从某种意义上说",
    "进行深入分析", "系统梳理", "综合运用", "充分说明", "不可或缺",
]


def _paragraphs(markdown: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", markdown)
    out: list[str] = []
    in_fence = False
    for block in blocks:
        text = block.strip()
        if text.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not text or text.startswith("#") or text.startswith("|"):
            continue
        if text.startswith("![") or text.startswith(">"):
            continue
        if re.match(r"^(?:参考文献|参考资料|附录)\b", text):
            continue
        out.append(text)
    return out


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[。！？；!?;]+", text) if part.strip()]


def build_style_gate(markdown: str) -> dict[str, Any]:
    paragraphs = _paragraphs(markdown)
    hard: list[str] = []
    warnings: list[str] = []
    pattern_counts: dict[str, int] = {}
    for label, pattern in PROHIBITED_UNSOURCED:
        count = sum(len(re.findall(pattern, paragraph)) for paragraph in paragraphs)
        pattern_counts[label] = count
        if count:
            hard.append(f"{label}：{count} 处未给出可核验出处")
    for label, pattern in EMPTY_CLOSERS:
        count = sum(len(re.findall(pattern, paragraph)) for paragraph in paragraphs)
        pattern_counts[label] = count
        if count:
            hard.append(f"{label}：{count} 处需要改为具体判断或可检验推论")
    filler_counts = Counter()
    for paragraph in paragraphs:
        for filler in FILLERS:
            if filler in paragraph:
                filler_counts[filler] += paragraph.count(filler)
    for filler, count in filler_counts.items():
        if count >= 3:
            warnings.append(f"填充/高频表达 `{filler}` 出现 {count} 次，检查是否承载信息")

    starts = [re.split(r"[，。；：:、\s]", p, maxsplit=1)[0] for p in paragraphs if p]
    repeated_starts = {key: count for key, count in Counter(starts).items() if len(key) >= 2 and count >= 4}
    if repeated_starts:
        warnings.append("连续段落可能重复使用同一段首结构：" + "、".join(f"{k}×{v}" for k, v in repeated_starts.items()))

    lengths = [len(s) for p in paragraphs for s in _sentences(p)]
    rhythm = {
        "sentence_count": len(lengths),
        "mean_chars": round(sum(lengths) / len(lengths), 2) if lengths else 0,
        "min_chars": min(lengths) if lengths else 0,
        "max_chars": max(lengths) if lengths else 0,
        "length_variation": round((max(lengths) - min(lengths)) / max(sum(lengths) / len(lengths), 1), 2) if lengths else 0,
    }
    if lengths and rhythm["length_variation"] < 0.35 and len(lengths) >= 20:
        warnings.append("句长变化较小；仅在不损失严谨性的前提下调整长短句节奏")

    score = max(0, 100 - len(hard) * 25 - len(warnings) * 5)
    return {
        "passed": not hard,
        "paragraph_count": len(paragraphs),
        "pattern_counts": pattern_counts,
        "filler_counts": dict(filler_counts),
        "repeated_starts": repeated_starts,
        "rhythm": rhythm,
        "hard_failures": hard,
        "warnings": warnings,
        "score": score,
        "disclaimer": "该 gate 评估专业化和模板化风险，不等同于任何商用 AI 检测器读数，也不用于规避检测。",
    }


if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown")
    parser.add_argument("--json")
    args = parser.parse_args()
    report = build_style_gate(open(args.markdown, encoding="utf-8").read())
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 2)


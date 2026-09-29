#!/usr/bin/env python3
"""Explainable style checks for professional, author-preserving academic prose.

This is a quality lint, not an AI-detector and not a detector-evasion score.
It skips headings, tables, code, figure references and bibliography-like blocks.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from document_formatting import drop_empty_headings, markdown_units, merge_fragmented_paragraphs, placeholder_heading_count


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
        if re.match(r"^(?:参考文献|参考资料|附录|图|表|表格解释|图形说明)\b", text):
            continue
        out.append(text)
    return out


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[。！？；!?;]+", text) if part.strip()]


def build_style_gate(markdown: str) -> dict[str, Any]:
    paragraphs = _paragraphs(markdown)
    normalized_markdown = merge_fragmented_paragraphs(drop_empty_headings(markdown))
    normalized_paragraphs = _paragraphs(normalized_markdown)
    raw_empty_headings = placeholder_heading_count(markdown)
    normalized_empty_headings = placeholder_heading_count(normalized_markdown)
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

    short_paragraphs = [paragraph for paragraph in paragraphs if markdown_units(paragraph) < 120]
    normalized_short_paragraphs = [paragraph for paragraph in normalized_paragraphs if markdown_units(paragraph) < 120]
    raw_ratio = round(len(short_paragraphs) / len(paragraphs), 3) if paragraphs else 0
    normalized_ratio = round(len(normalized_short_paragraphs) / len(normalized_paragraphs), 3) if normalized_paragraphs else 0
    fragmentation_passed = normalized_ratio <= 0.30
    if raw_ratio > 0.35:
        warnings.append(
            f"原稿短段落占比 {raw_ratio:.0%}；交付副本已按同一小节自动合并，合并后为 {normalized_ratio:.0%}"
        )
    if not fragmentation_passed:
        hard.append(
            f"段落过碎：自动合并后短段落占比仍为 {normalized_ratio:.0%}，应补充同一论证链而非继续拆段"
        )
    if raw_empty_headings:
        warnings.append(
            f"原稿存在 {raw_empty_headings} 个无正文标题；交付副本已删除连续占位标题，剩余 {normalized_empty_headings} 个需补证据"
        )
    if normalized_empty_headings:
        hard.append(f"交付副本仍有 {normalized_empty_headings} 个无正文标题，应补充论证或删除标题")

    score = max(0, 100 - len(hard) * 25 - len(warnings) * 5)
    return {
        "passed": not hard,
        "paragraph_count": len(paragraphs),
        "normalized_paragraph_count": len(normalized_paragraphs),
        "fragmentation": {
            "raw_short_paragraph_count": len(short_paragraphs),
            "raw_short_paragraph_ratio": raw_ratio,
            "normalized_short_paragraph_count": len(normalized_short_paragraphs),
            "normalized_short_paragraph_ratio": normalized_ratio,
            "passed": fragmentation_passed,
            "merge_rule": "同一标题范围内，短于 120 有效字元的连续正文段合并至 140–360，有图表、列表、引用和标题时停止。",
        },
        "empty_headings": {
            "raw_count": raw_empty_headings,
            "normalized_count": normalized_empty_headings,
            "passed": normalized_empty_headings == 0,
            "rule": "无正文、表格或图片的连续占位标题不进入交付副本。",
        },
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

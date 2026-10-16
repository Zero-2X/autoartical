#!/usr/bin/env python3
"""Structural and academic-expression checks on the formal manuscript source.

These checks target defects found in earlier deliveries rather than surface
"AI style" scores:

* repeated or generic headings (``核心内容``/``支撑说明``/``图形证据``),
  workflow/QA meta-text leaking into the manuscript body;
* citation integrity: every ``[n]`` resolves, every reference is cited, and
  numbering follows first appearance (GB/T 7714 顺序编码制);
* figure/table numbering continuity, and each figure/table cited in prose
  before (or at) its appearance;
* numbers that look like experimental results without a source citation or a
  “待实测/计划” marker;
* fragmentary paragraphs, near-duplicate paragraphs, chapter balance
  (conclusion chapters must not carry the technical argument);
* unnecessary English in Chinese headings;
* optional CJK spacing/punctuation lint through ``autocorrect-py`` (MIT,
  huacnlee/autocorrect) when installed.

A pass here is necessary, not sufficient: semantic review is recorded
separately in ``human-review.json``.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

GENERIC_HEADINGS = {
    "核心内容", "支撑说明", "图形证据", "背景与意义", "研究意义", "优势", "展望", "现实背景",
    "赛题价值", "实现方法", "技术落点", "验证锚点", "交付形态", "延展空间", "总结", "其他",
}
META_TERMS = (
    "门禁", "Gate", "gate", "manifest", "工作流自检", "签核", "交付声明", "版本封存", "skill",
    "ImageGen", "Prompt", "提示词", "质量检测的含义", "文本质量的约束", "申报书阅读导航", "审查脚本",
)
ENGLISH_IN_HEADING_ALLOW = re.compile(
    r"^(?:[A-Z][A-Za-z0-9\-]*|HBB|OBB|mAP|AP\d*|ECE|D-ECE|CLIP|DOTA|DIOR|FAIR1M|LAE|OVD|RS|AUROC|FPS|OpenRSI-Calibrator)$")
RESULT_NUMBER = re.compile(r"(?:mAP|AP\d*|召回率|准确率|ECE|FPS|提升|提高|下降)[^。；\n]{0,12}?\d+(?:\.\d+)?\s*(?:%|个百分点|FPS)?")
PLAN_MARKERS = ("待实测", "计划", "预期", "拟", "假设", "若", "如果", "阈值", "设定为", "不低于", "不超过", "至少")


def strip_back_matter(text: str) -> tuple[str, str]:
    match = re.search(r"(?m)^#{2,4}\s+参考文献\s*$", text)
    if not match:
        return text, ""
    return text[:match.start()], text[match.start():]


def body_paragraphs(text: str) -> list[str]:
    out = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith(("#", "|", "![", ">", "$$", "[[")) or re.match(r"^[表图]\s*\d+-\d+", block) or block.startswith("注："):
            continue
        out.append(block)
    return out


def lint(text: str) -> dict:
    failures: list[str] = []
    warnings: list[str] = []
    body, back = strip_back_matter(text)
    headings = [(len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"(?m)^(#{2,4})\s+(.+)$", body)]

    # Headings ---------------------------------------------------------
    norm = Counter(re.sub(r"^[\d.第章\s]+", "", h) for _, h in headings)
    dup = [h for h, n in norm.items() if n > 1 and h not in ("摘要",)]
    if dup:
        failures.append("重复标题：" + "、".join(dup[:12]))
    generic = [h for _, h in headings if re.sub(r"^[\d.\s]+", "", h) in GENERIC_HEADINGS]
    if generic:
        failures.append("空泛标题：" + "、".join(generic[:12]))
    english = []
    for _, h in headings:
        for word in re.findall(r"[A-Za-z][A-Za-z\-]+", h):
            if not ENGLISH_IN_HEADING_ALLOW.match(word) and h not in ("Abstract",):
                english.append(h)
                break
    if english:
        failures.append("中文标题中存在不必要英文：" + "、".join(english[:8]))
    depth = max((lvl for lvl, _ in headings), default=0)

    # Meta text --------------------------------------------------------
    meta_hits = [t for t in META_TERMS if t in body]
    if meta_hits:
        failures.append("正文混入工作流/质检元信息：" + "、".join(meta_hits))

    # Citations --------------------------------------------------------
    refs = dict(re.findall(r"(?m)^\[(\d+)\]\s+(.+)$", back))
    cited_order: list[int] = []
    for group in re.findall(r"\[(\d+(?:\s*[,，\-–]\s*\d+)*)\]", body):
        for part in re.split(r"[,，]", group):
            if re.search(r"[-–]", part):
                a, b = (int(x) for x in re.split(r"[-–]", part))
                nums = list(range(a, b + 1))
            else:
                nums = [int(part)]
            for n in nums:
                if n not in cited_order:
                    cited_order.append(n)
    missing_refs = [n for n in cited_order if str(n) not in refs]
    uncited = [int(n) for n in refs if int(n) not in cited_order]
    if not refs:
        failures.append("缺少参考文献表")
    if missing_refs:
        failures.append(f"正文引用了不存在的文献编号：{missing_refs}")
    if uncited:
        failures.append(f"参考文献未在正文引用：{uncited}")
    if cited_order and cited_order != sorted(cited_order):
        first_bad = next(i for i in range(len(cited_order)) if cited_order[i] != i + 1)
        failures.append(f"文献编号未按首次出现顺序排列（顺序编码制），首个错位：第 {first_bad + 1} 次新引用为 [{cited_order[first_bad]}]")

    # Figures and tables ----------------------------------------------
    for kind in ("图", "表"):
        if kind == "图":
            labels = re.findall(r"(?m)^!\[(图\s*\d+-\d+)", body)
        else:
            labels = re.findall(r"(?m)^(表\s*\d+-\d+)", body)
        labels = [l.replace(" ", "") for l in labels]
        by_chapter: dict[int, list[int]] = {}
        for label in labels:
            c, i = (int(x) for x in label[1:].split("-"))
            by_chapter.setdefault(c, []).append(i)
        for c, seq in by_chapter.items():
            if seq != list(range(1, len(seq) + 1)):
                failures.append(f"{kind}编号不连续：第{c}章 {seq}")
        for label in labels:
            positions = [m.start() for m in re.finditer(re.escape(label), body)]
            caption_pos = body.find(("![" + label) if kind == "图" else ("\n" + label))
            prose_refs = [p for p in positions if p != caption_pos and p != caption_pos + (2 if kind == "图" else 1)]
            if not prose_refs:
                failures.append(f"{label} 未在正文中被引用")
        if kind == "表":
            table_blocks = re.findall(r"(?m)^(表\s*\d+-\d+.*)\n(\|.*\n)+(?:\n注：(.*))?", body)
            for caption, _, note in table_blocks:
                pass

    # Unsupported result numbers --------------------------------------
    suspicious = []
    for para in body_paragraphs(body):
        for sentence in re.split(r"(?<=[。；])", para):
            if RESULT_NUMBER.search(sentence) and not re.search(r"\[\d+", sentence) and not any(m in sentence for m in PLAN_MARKERS):
                suspicious.append(sentence.strip()[:80])
    if suspicious:
        failures.append(f"疑似未注明来源或未标注待实测的结果数字 {len(suspicious)} 处：" + " | ".join(suspicious[:5]))

    # Paragraph shape --------------------------------------------------
    paras = body_paragraphs(body)
    lengths = [len(re.sub(r"\s", "", p)) for p in paras]
    short = [p[:30] for p, n in zip(paras, lengths) if n < 80 and not p.startswith(("- ", "1.", "（"))]
    if paras and len(short) / len(paras) > 0.12:
        failures.append(f"碎片段落比例过高：{len(short)}/{len(paras)} 段少于 80 字")
    elif short:
        warnings.append(f"{len(short)} 个短段落需确认是否承担独立论点")
    shingles = []
    for p in paras:
        s = re.sub(r"[\W_]+", "", p)
        shingles.append({s[i:i + 8] for i in range(0, max(len(s) - 8, 1), 4)})
    near_dup = []
    for i in range(len(shingles)):
        for j in range(i + 1, len(shingles)):
            a, b = shingles[i], shingles[j]
            if len(a) > 15 and len(b) > 15 and len(a & b) / min(len(a), len(b)) > 0.45:
                near_dup.append((paras[i][:24], paras[j][:24]))
    if near_dup:
        failures.append(f"近重复段落 {len(near_dup)} 对：" + " | ".join(f"{a}… ≈ {b}…" for a, b in near_dup[:4]))

    # Chapter balance ---------------------------------------------------
    chapters = re.split(r"(?m)^##\s+(第\s*\d+\s*章.*)$", body)
    sizes = {}
    for i in range(1, len(chapters), 2):
        sizes[chapters[i].strip()] = len(re.findall(r"[一-鿿]", chapters[i + 1]))
    total = sum(sizes.values()) or 1
    if sizes:
        last_title, last_size = list(sizes.items())[-1]
        if last_size / total > 0.10:
            failures.append(f"末章“{last_title}”占正文 {last_size / total:.0%}，技术论证应放回相应章节")

    # Optional CJK typography lint -------------------------------------
    autocorrect = {"available": False}
    try:
        import autocorrect_py

        diffs = 0
        samples = []
        for p in paras:
            fixed = autocorrect_py.format(p)
            if fixed != p:
                diffs += 1
                if len(samples) < 3:
                    samples.append(p[:40])
        autocorrect = {"available": True, "paragraphs_with_suggestions": diffs, "samples": samples}
        if diffs:
            warnings.append(f"autocorrect 对 {diffs} 段给出中英文间距/标点建议")
    except ImportError:
        pass

    return {
        "verdict": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
        "stats": {"headings": len(headings), "heading_depth": depth, "paragraphs": len(paras),
                  "median_paragraph_chars": sorted(lengths)[len(lengths) // 2] if lengths else 0,
                  "references": len(refs), "citations_distinct": len(cited_order), "chapter_chars": sizes},
        "autocorrect": autocorrect,
        "scope_note": "结构与引用一致性检查；不判断论证是否成立，语义审查另行记录。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="正式稿结构、引用、图表与表达检查")
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    text = args.markdown.read_text(encoding="utf-8")
    result = lint(text)
    import hashlib

    result["source_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["verdict"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())

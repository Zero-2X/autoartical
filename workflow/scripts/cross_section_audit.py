"""Cross-section consistency audit for long Chinese (and English) manuscripts.

The checks re-implement, for Chinese thesis-style documents, the ideas behind
the cross-section rules of mumdark/nature-writing-studio (hedge ladder,
entity continuity, abbreviation expansion, transition hooks, numeric format,
reference density) and its tiered AI-tell list.  No rule text or data from
that repository is copied (it carries no licence); the patterns below were
written for this workflow.

Every check returns plain failures/warnings so that ``manuscript_lint`` can
merge them.  Failures block delivery; warnings ask for a human decision.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ---------------------------------------------------------------- claim strength
# Three evidence tiers.  A sentence about *this work* may only use the tier its
# evidence supports; a plan document (results 待实测) may not use the causal tier.
CAUSAL = r"(证明了|证实了|验证了|表明了本|显著(?:提升|提高|优于|降低)了|大幅(?:提升|提高|降低)|取得了|实现了.{0,6}(?:提升|突破)|优于所有|达到了?最优|state-of-the-art)"
ASSOCIATIVE = r"(提示|支持|与.{1,12}一致|表明|说明)"
SPECULATIVE = r"(可能|或许|推测|有望|预期|假设)"
OWN_WORK = r"(本文|本作品|本方法|本方案|我们的方法|所提方法|OpenRSI-Calibrator|完整方案)"
PLAN_MARKERS = ("待实测", "计划", "预期", "拟", "假设", "若", "如果", "将", "能否", "是否", "否证", "判定", "预计", "目标是")

# ---------------------------------------------------------------- unsourced background
BACKGROUND = r"(已有研究|大量研究|研究表明|研究发现|文献表明|普遍认为|广泛认为|业界普遍|众所周知|被广泛(?:应用|使用|认可)|专家认为|有学者指出)"

# ---------------------------------------------------------------- AI-tell tiers (written for this workflow)
ZH_SEVERE = ["赋能", "助力", "深度融合", "全方位", "多维度赋能", "开创性地", "颠覆性", "划时代", "具有重要意义",
             "具有重大意义", "前景广阔", "意义深远", "不可或缺", "至关重要的作用", "发挥着重要作用", "日益凸显",
             "随着.{0,12}的(?:快速|飞速|迅猛)发展", "在当今.{0,6}时代", "综上所述", "总而言之"]
ZH_MILD = ["值得注意的是", "需要指出的是", "不难发现", "毋庸置疑", "显而易见", "进一步地", "此外，?值得一提", "可以说(?!明)"]
EN_SEVERE = [r"\bdelve[sd]? into\b", r"\bnavigat\w+ the complexit", r"\bintricate landscape\b", r"\btapestry\b",
             r"\bshed(?:s|ding)? light on\b", r"\bharness(?:es|ing)? the power\b", r"\bpivotal role\b",
             r"\bgame[- ]chang", r"\bparadigm shift\b", r"\bunlock(?:s|ing)? the potential\b", r"\bin the realm of\b",
             r"\bever-evolving\b", r"\bplays? a (?:crucial|key|vital) role\b"]
EN_MILD = [r"\bit is worth noting\b", r"\bit is important to note\b", r"\bnotably,", r"\bimportantly,", r"\bmoreover,",
           r"\bfurthermore,", r"\butili[sz]e[sd]?\b", r"\bleverag(?:e|es|ed|ing)\b", r"\brobust\b", r"\bcomprehensive\b",
           r"\bseamless(?:ly)?\b", r"\bcutting-edge\b"]

ACRONYM = re.compile(r"(?<![A-Za-z0-9-])([A-Z][A-Za-z]*[A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9.]+)*)(?![A-Za-z0-9])")


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[。！？；])", text) if s.strip()]


def _prose_blocks(body: str) -> list[str]:
    out = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block or block.startswith(("#", "|", "![", "$$", "[[", ">")) or re.match(r"^[表图]\d+-\d+", block):
            continue
        out.append(block)
    return out


def split_chapters(body: str) -> list[tuple[str, str]]:
    parts = re.split(r"(?m)^##\s+(第\s*\d+\s*章.*)$", body)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def load_glossary(path: Path | None) -> dict:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def audit(text: str, body: str, refs: dict, *, glossary: dict | None = None) -> dict:
    failures: list[str] = []
    warnings: list[str] = []
    stats: dict = {}
    prose = _prose_blocks(body)
    is_plan = "待实测" in body

    # 1. Claim strength must match evidence (hedge ladder) -----------------
    overclaims = []
    for block in prose:
        for s in sentences(block):
            if re.search(OWN_WORK, s) and re.search(CAUSAL, s) and not re.search(r"\[\d", s):
                if is_plan and not any(m in s for m in PLAN_MARKERS):
                    overclaims.append(s[:70])
    if overclaims:
        failures.append(f"结论强度超过证据：实验待实测，却对本文工作使用“证明/验证/显著提升”等因果档措辞 {len(overclaims)} 处：" + " | ".join(overclaims[:4]))

    # 2. Background claims need a citation ----------------------------------
    unsourced = [s[:60] for block in prose for s in sentences(block)
                 if re.search(BACKGROUND, s) and not re.search(r"\[\d", s)]
    if unsourced:
        failures.append(f"背景性断言缺少引用 {len(unsourced)} 处（如“研究表明”“普遍认为”）：" + " | ".join(unsourced[:4]))

    # 3. AI-tell tiers ------------------------------------------------------
    joined = "\n".join(prose)
    severe = [p for p in ZH_SEVERE if re.search(p, joined)]
    mild = [p for p in ZH_MILD if re.search(p, joined)]
    abstract_en = ""
    m = re.search(r"(?ms)^##\s+Abstract\s*$(.*?)(?=^##\s)", text)
    if m:
        abstract_en = m.group(1)
    en_severe = [p for p in EN_SEVERE if re.search(p, abstract_en + "\n" + joined, re.I)]
    en_mild = [p for p in EN_MILD if re.search(p, abstract_en, re.I)]
    if severe or en_severe:
        failures.append("宣传性或模板化套话：" + "、".join(severe + [p.strip("\\b") for p in en_severe]))
    if mild or en_mild:
        warnings.append("轻度套话，确认是否承担信息：" + "、".join(mild + [p.strip("\\b") for p in en_mild]))
    if "—" in abstract_en:
        failures.append("英文摘要含 em dash（U+2014），按期刊习惯改为逗号、冒号或拆句")

    # 4. Glossary: preferred terms and forbidden variants -------------------
    glossary = glossary or {}
    drift = []
    for preferred, spec in glossary.get("terms", {}).items():
        for variant in spec.get("avoid", []):
            if variant in joined:
                drift.append(f"“{variant}”应统一为“{preferred}”")
    if drift:
        failures.append("术语不统一：" + "；".join(drift[:8]))

    # 5. Abbreviation expansion at first use --------------------------------
    # Only generic technical abbreviations (AP, IoU, DETR…) need expansion.
    # Named works (datasets, methods) are identified by a citation right after
    # their first mention, by appearing in a reference title, or by the glossary.
    names = {w for title in refs.values() for w in ACRONYM.findall(title)}
    names |= set(glossary.get("names", []))
    exempt = set(glossary.get("abbreviations_known", []))
    first_use_missing = []
    seen = set()
    for match in re.finditer(r"(?<![A-Za-z0-9-])([A-Za-z][A-Za-z]{1,5})(?![A-Za-z0-9-])", joined):
        word = match.group(1)
        if word in seen or sum(c.isupper() for c in word) < 2:
            continue
        seen.add(word)
        if word in names or word in exempt:
            continue
        after = joined[match.end(): match.end() + 80]
        if re.search(r"\[\d", after):
            continue  # cited named work
        window = joined[max(0, match.start() - 40): match.end() + 40]
        if not re.search(r"[（(][^）)]*" + re.escape(word) + r"[^）)]*[）)]|" + re.escape(word) + r"\s*[（(]", window):
            first_use_missing.append(word)
    if first_use_missing:
        warnings.append("缩写首次出现未给出全称或中文释义：" + "、".join(first_use_missing[:12]))
    stats["abbreviations_first_use_missing"] = first_use_missing

    # 6. Chapter-to-chapter transition hooks --------------------------------
    chapters = split_chapters(body)
    no_hook = []
    for idx, (title, content) in enumerate(chapters[1:], start=2):
        first = next((b for b in _prose_blocks(content)), "")
        if not re.search(r"第\s*\d+\s*章|上一章|前一章|前文|前述|上述", first[:200]):
            no_hook.append(title)
    if no_hook:
        warnings.append("章首未承接前文（读者不清楚本章回答前文留下的哪个问题）：" + "、".join(no_hook))

    # 7. Numeric format consistency ----------------------------------------
    grouped = re.findall(r"(?<![\d.])\d{1,3}(?:,\d{3})+(?![\d.])", joined)
    plain = re.findall(r"(?<![\d.,])\d{5,}(?![\d.,])", joined)
    if grouped and plain:
        warnings.append(f"大数写法不统一：千分位 {grouped[:2]} 与不分隔 {plain[:2]} 混用")
    pct_space = len(re.findall(r"\d\s+%", joined))
    pct_tight = len(re.findall(r"\d%", joined))
    if pct_space and pct_tight:
        warnings.append("百分号前空格写法不统一")

    # 8. Citation density per chapter --------------------------------------
    density = {}
    for title, content in chapters:
        chars = max(1, len(re.findall(r"[一-鿿]", content)))
        cites = len(re.findall(r"\[\d+(?:[,，\-–]\d+)*\]", content))
        density[title] = round(cites / chars * 1000, 2)
    stats["citations_per_1000_chars"] = density
    for title, value in density.items():
        if re.search(r"相关|综述|现状|研究进展", title) and value < 2.0:
            warnings.append(f"“{title}”引用密度偏低（{value} 条/千字），综述章节的判断需要文献支撑")

    return {"failures": failures, "warnings": warnings, "stats": stats}

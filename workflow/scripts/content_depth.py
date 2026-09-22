"""Conservative prose-volume checks; never a substitute for evidence review."""
from __future__ import annotations

import re
from collections import Counter


DEFAULT_CONTRACT = {
    "target_pages": [40, 50],
    "body_units_min": 24000,
    "body_units_target": 32000,
    "page_scope": "正文；不含封面、目录、参考文献及附录",
    "count_rule": "中文字符与英文单词；不计标题、表格、代码、公式、图片及重复段落",
    "visual_contract": {
        "required_specs_min": 18,
        "required_external_assets_min": 12,
        "required_tables_min": 5,
        "required_diagrams_min": 8,
        "required_case_or_ui_visuals_min": 4,
        "required_asset_ratio": 1.0,
        "all_visuals_must_be_cited": True,
        "rule": "图表、流程图、图标和界面素材必须服务于正文论证，不能用重复截图或空白占页。",
    },
    "export_contract": {
        "required_formats": ["markdown", "html", "pdf_or_docx"],
        "render_verification": "required_before_delivery",
        "page_count_must_be_in_range": True,
        "visual_qa_required": True,
    },
    "render_verification": "required_before_delivery",
}


def allocate_budgets(sections: list[dict], contract: dict) -> None:
    """Keep the existing relative chapter weights, with exact total budgets."""
    if not sections:
        raise ValueError("正文计划不能为空")
    weights = []
    for section in sections:
        values = re.findall(r"\d+", section.get("suggested_word_budget", ""))
        weights.append(max(1, int(values[0])) if values else 1)
    allocations = []
    for key in ("body_units_min", "body_units_target"):
        total = contract[key]
        values = [total * weight // sum(weights) for weight in weights]
        for index in range(total - sum(values)):
            values[index % len(values)] += 1
        allocations.append(values)
    for index, section in enumerate(sections):
        section["suggested_word_budget"] = f"{allocations[0][index]}-{allocations[1][index]}"


def prose_paragraphs(text: str) -> list[str]:
    # A nested appendix/reference section is not body prose. Resume only at
    # a heading at the same or higher level, so heading depth cannot hide padding.
    kept, excluded_level = [], None
    for line in text.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+)", line)
        if heading:
            level, title = len(heading[1]), heading[2].strip()
            if excluded_level is not None and level <= excluded_level:
                excluded_level = None
            if re.match(r"(?:附录|参考文献|参考资料|Appendix\b|References\b)", title, re.I):
                excluded_level = level
        if excluded_level is None:
            kept.append(line)
    text = "\n".join(kept)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$", "", text)
    text = re.sub(r"\$\$.*?\$\$|\\\[.*?\\\]", "", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"(?m)^\s*(?:#{1,6}\s.*|\|.*|\[[^\]]+\]:.*)$", "", text)
    text = re.sub(r"`[^`]*`|\$[^$\n]+\$|\[\d+(?:[,，–-]\d+)*\]", "", text)
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def content_metrics(text: str) -> dict:
    paragraphs = prose_paragraphs(text)
    normalized = [re.sub(r"[\W_]+", "", p) for p in paragraphs]
    counts = Counter(p for p in normalized if len(p) >= 30)
    seen = set()
    units = 0
    for paragraph, key in zip(paragraphs, normalized):
        if key in seen:
            continue
        seen.add(key)
        units += len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]|[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*", paragraph))
    return {"prose_units": units, "duplicate_paragraph_groups": sum(n > 1 for n in counts.values())}


def build_content_depth_gate(draft: str, sections: list[dict], contract: dict) -> dict:
    # Select only planned body chapters from the actual assembled manuscript.
    chunks = re.split(r"(?m)^##\s+(.+?)\s*$", draft)
    bodies: dict[str, list[str]] = {}
    for index in range(1, len(chunks), 2):
        bodies.setdefault(chunks[index].strip(), []).append(chunks[index + 1])
    failures = []
    rows = []
    selected = []
    if not sections:
        failures.append("缺少正文内容计划，不能验收正文体量。")
    for section in sections:
        heading = section.get("heading", "")
        matches = bodies.get(heading, [])
        content = "\n\n".join(matches)
        selected.append(content)
        metrics = content_metrics(content)
        numbers = re.findall(r"\d+", section.get("suggested_word_budget", ""))
        minimum = int(numbers[0]) if numbers else 0
        if len(matches) != 1 or not minimum or metrics["prose_units"] < minimum:
            failures.append(f"正文内容不足或章节重复/缺失：{heading}，有效正文 {metrics['prose_units']}，最低 {minimum}。")
        rows.append({"heading": heading, "minimum": minimum, **metrics})
    totals = content_metrics("\n\n".join(selected))
    if totals["prose_units"] < contract["body_units_min"]:
        failures.append(f"有效正文总量不足：{totals['prose_units']} < {contract['body_units_min']}；需补充论证与证据，不能靠排版扩页。")
    if totals["duplicate_paragraph_groups"]:
        failures.append("正文存在重复段落；重复内容不计入篇幅。")
    return {"passed": not failures, "failures": failures, "per_chapter": rows,
            **totals, "contract": contract,
            "semantic_review": "required: evidence, specificity, nonredundancy",
            "render_verification": "pending; prose volume does not establish page count"}

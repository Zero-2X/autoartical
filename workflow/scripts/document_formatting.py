#!/usr/bin/env python3
"""Deterministic manuscript formatting helpers shared by export and lint gates.

The source manuscript stays readable and evidence-oriented.  These helpers
only normalize the delivery copy: headings receive a stable dissertation-style
number, while adjacent prose fragments are joined when doing so preserves the
same section and does not swallow a caption, table, list, or visual.
"""
from __future__ import annotations

import re


FRONT_MATTER_TITLES = {
    "摘要",
    "英文摘要",
    "材料真实性与数据许可说明",
    "目录",
    "符号说明",
    "缩略语表",
}


def markdown_units(text: str) -> int:
    """Count Chinese characters and Latin/number tokens used for prose gates."""
    return len(
        re.findall(
            r"[\u3400-\u4dbf\u4e00-\u9fff]|[A-Za-z0-9]+(?:[-_/][A-Za-z0-9]+)*",
            text,
        )
    )


def _strip_heading_number(text: str) -> str:
    """Remove a previous chapter/section prefix before assigning a new one."""
    text = re.sub(r"^\s*第[^\s]+章\s*[：:、.．-]?\s*", "", text)
    text = re.sub(
        r"^\s*(?:\d+(?:\.\d+)*|[零〇一二三四五六七八九十百千万]+)\s*[、.．:：-]?\s+",
        "",
        text,
    )
    # A Chinese chapter prefix can be adjacent to its punctuation.
    text = re.sub(r"^\s*[零〇一二三四五六七八九十百千万]+[、.．]\s*", "", text)
    return text.strip()


def number_markdown_headings(markdown: str) -> str:
    """Number every section heading in a stable chapter.section hierarchy.

    The document title (H1) remains a title.  H2--H6 receive explicit text
    prefixes rather than relying on a renderer's automatic numbering, so the
    same numbering appears in Markdown, HTML, PDF, and Word.  Front matter is
    assigned ``0.x`` labels; body chapters use ``第N章`` followed by decimal
    section numbers.
    """
    counters = [0, 0, 0, 0, 0]
    front_counter = 0
    output: list[str] = []
    in_fence = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            output.append(line)
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line) if not in_fence else None
        if not match:
            output.append(line)
            continue
        hashes, raw_title = match.groups()
        level = len(hashes)
        if level == 1:
            output.append(f"# {raw_title.strip()}")
            continue

        title = _strip_heading_number(raw_title)
        if level == 2 and title in FRONT_MATTER_TITLES:
            front_counter += 1
            counters = [0, 0, 0, 0, 0]
            output.append(f"{'#' * level} 0.{front_counter} {title}")
            continue

        index = level - 2
        counters[index] += 1
        for reset in range(index + 1, len(counters)):
            counters[reset] = 0

        if level == 2:
            output.append(f"## 第{counters[0]}章 {title}")
        else:
            prefix_parts = counters[: index + 1]
            # A subsection directly under front matter is rare but still gets
            # a visible, collision-free number instead of an unnumbered title.
            if counters[0] == 0:
                prefix = "0." + ".".join(str(value) for value in prefix_parts[1:])
            else:
                prefix = ".".join(str(value) for value in prefix_parts)
            output.append(f"{'#' * level} {prefix} {title}")
    return "\n".join(output).rstrip() + "\n"


def _is_caption_or_visual(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    return bool(
        re.match(r"^(?:图|表|图形|表格|Figure|Table)\s*[A-Za-z0-9一二三四五六七八九十-]+", compact, re.I)
        or compact.startswith("表格解释")
        or compact.startswith("图形说明")
    )


def _is_plain_prose(block: str) -> bool:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if not lines:
        return False
    if any(
        line.startswith(("#", ">", "|", "!", "- ", "* ", "+ ", "```", "~~~"))
        for line in lines
    ):
        return False
    if _is_caption_or_visual(" ".join(lines)):
        return False
    return True


def _join_blocks(left: str, right: str) -> str:
    left = left.rstrip()
    right = right.lstrip()
    # Chinese prose reads naturally without an inserted space.  Keep a space
    # when either side starts with a Latin token to avoid joining identifiers.
    if left and right and re.match(r"[A-Za-z0-9]", right) and re.match(r"[A-Za-z0-9]", left[-1:]):
        return f"{left} {right}"
    return left + right


def merge_fragmented_paragraphs(
    markdown: str,
    *,
    target_units: int = 140,
    max_units: int = 360,
) -> str:
    """Join short adjacent prose blocks within one heading scope.

    Captions, figures, tables, lists, blockquotes, and headings are hard
    boundaries.  A merge is limited to ``max_units`` so a compact paragraph is
    not turned into an unreadable wall of text.
    """
    blocks = [part.strip() for part in re.split(r"\n\s*\n", markdown.strip()) if part.strip()]
    merged: list[str] = []
    for block in blocks:
        if (
            merged
            and _is_plain_prose(merged[-1])
            and _is_plain_prose(block)
            and markdown_units(merged[-1]) < target_units
            and markdown_units(block) < target_units
            and markdown_units(merged[-1]) + markdown_units(block) <= max_units
        ):
            merged[-1] = _join_blocks(merged[-1], block)
        else:
            merged.append(block)
    # A second pass handles three or more adjacent fragments without touching
    # a long paragraph that the first pass has already stabilized.
    changed = True
    while changed:
        changed = False
        result: list[str] = []
        for block in merged:
            if (
                result
                and _is_plain_prose(result[-1])
                and _is_plain_prose(block)
                and markdown_units(result[-1]) < target_units
                and markdown_units(block) < target_units
                and markdown_units(result[-1]) + markdown_units(block) <= max_units
            ):
                result[-1] = _join_blocks(result[-1], block)
                changed = True
            else:
                result.append(block)
        merged = result
    return "\n\n".join(merged) + ("\n" if merged else "")


def drop_empty_headings(markdown: str) -> str:
    """Remove heading-only blocks that contain no prose, table, or visual.

    A long run of placeholder headings creates a page of labels with no
    argument underneath.  Such placeholders are retained in the source draft
    for future chapter planning but are omitted from a delivery copy until
    their evidence or prose is written.
    """
    blocks = [part.strip() for part in re.split(r"\n\s*\n", markdown.strip()) if part.strip()]
    kept: list[str] = []
    for index, block in enumerate(blocks):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) == 1 and re.match(r"^#{2,6}\s+", lines[0]):
            next_block = blocks[index + 1] if index + 1 < len(blocks) else ""
            next_lines = [line.strip() for line in next_block.splitlines() if line.strip()]
            current_heading = re.match(r"^(#{2,6})\s+", lines[0])
            next_heading = re.match(r"^(#{2,6})\s+", next_lines[0]) if next_lines else None
            if current_heading and next_heading and len(current_heading.group(1)) == len(next_heading.group(1)):
                continue
        kept.append(block)
    return "\n\n".join(kept) + ("\n" if kept else "")


def placeholder_heading_count(markdown: str) -> int:
    """Count only heading blocks immediately followed by another heading."""
    blocks = [part.strip() for part in re.split(r"\n\s*\n", markdown.strip()) if part.strip()]
    count = 0
    for index, block in enumerate(blocks[:-1]):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        next_lines = [line.strip() for line in blocks[index + 1].splitlines() if line.strip()]
        current_heading = re.match(r"^(#{2,6})\s+", lines[0]) if len(lines) == 1 else None
        next_heading = re.match(r"^(#{2,6})\s+", next_lines[0]) if next_lines else None
        if current_heading and next_heading and len(current_heading.group(1)) == len(next_heading.group(1)):
            count += 1
    return count

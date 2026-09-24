"""Prepare figure briefs from the actual manuscript before ImageGen is called."""
from __future__ import annotations

import hashlib
import re
from typing import Any


def manuscript_context(draft: str, spec: dict[str, Any]) -> dict[str, str]:
    """Prefer the planned subsection's prose over a grouped figure appendix."""
    visual_id = str(spec["visual_id"])
    lines = draft.splitlines()
    subsection = str(spec.get("suggested_subsection", "")).strip()
    if subsection:
        starts = [i for i, line in enumerate(lines) if line.startswith("### ") and subsection in line]
        if starts:
            start = starts[0]
            end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith(("### ", "## "))), len(lines))
            prose = [line.strip() for line in lines[start + 1:end] if line.strip() and not line.lstrip().startswith(("!", "|", "#"))]
            if prose:
                return {"section_heading": lines[start].lstrip("# ").strip(), "context_excerpt": "\n".join(prose)[:3000]}
    matches = [i for i, line in enumerate(lines) if visual_id in line and line.lstrip().startswith("![")]
    if not matches:
        return {"section_heading": "", "context_excerpt": ""}
    index = matches[0]
    heading = next((line.lstrip("# ").strip() for line in reversed(lines[:index]) if line.startswith("## ")), "")
    prose: list[str] = []
    for line in lines[max(0, index - 36):min(len(lines), index + 20)]:
        value = line.strip()
        if not value or value.startswith(("!", "|", "#")) or re.fullmatch(r"[-:| ]+", value):
            continue
        prose.append(value)
    return {"section_heading": heading, "context_excerpt": "\n".join(prose)[:2400]}


def request_brief(spec: dict[str, Any], draft: str, project_name: str) -> dict[str, Any]:
    visual_id = str(spec["visual_id"])
    context = manuscript_context(draft, spec)
    return {
        "figure_id": visual_id,
        "visual_type": spec.get("visual_type", "figure"),
        "label": spec.get("label", ""),
        "title": spec.get("title", ""),
        "purpose": spec.get("purpose", ""),
        "project_name": project_name,
        "source_draft_sha256": manuscript_sha256(draft),
        "suggested_subsection": spec.get("suggested_subsection", ""),
        "source_refs": spec.get("evidence_ids", []),
        "article_understanding": {
            **context,
            "key_message": "",
            "visual_elements": [],
            "evidence_boundary": "",
            "visual_direction": "",
        },
        "prompt": "",
        "route": "Codex built-in image_gen",
        "status": "needs_article_interpretation",
        "required_steps": [
            "阅读完整小节和相邻正文，提炼本图唯一要证明的主张、实体关系及证据边界",
            "填写 article_understanding，再据此撰写逐图、完整、详细的 ImageGen prompt",
            "调用 Codex 内置 image_gen；检查生成图；记录来源、提示词散列和视觉审查",
            "将 PNG 插入 Markdown、HTML、PDF 并重新运行全部门禁",
        ],
    }


def manuscript_sha256(draft: str) -> str:
    """Ignore figure embed lines so registering a PNG cannot stale every prompt."""
    source_text = "\n".join(line for line in draft.splitlines() if not line.lstrip().startswith("!["))
    return hashlib.sha256(source_text.encode("utf-8")).hexdigest()


def compose_prompt(request: dict[str, Any]) -> str:
    """Compose a detailed prompt only after a human/agent has interpreted the article."""
    understanding = request.get("article_understanding", {})
    message = str(understanding.get("key_message", "")).strip()
    elements = understanding.get("visual_elements", [])
    boundary = str(understanding.get("evidence_boundary", "")).strip()
    direction = str(understanding.get("visual_direction", "")).strip()
    context = str(understanding.get("context_excerpt", "")).strip()
    if not message or len(elements) < 3 or not boundary or not direction or len(context) < 60:
        raise ValueError("先填写完整文章理解、具体视觉元素、证据边界与独立构图方向")
    return (
        f"Use case: scientific-educational; asset type: a publication-quality 16:9 figure for a Chinese competition research proposal. "
        f"Project: {request.get('project_name', '')}. Figure {request.get('label', '')} {request.get('title', '')}, "
        f"placed in the section {understanding.get('section_heading', '')}. The one claim this figure must convey is: {message} "
        f"Depict these exact objects and relationships, not generic interchangeable boxes: {'；'.join(map(str, elements))}. "
        f"Article-specific visual concept and composition: {direction} "
        f"Use the nearby manuscript as semantic grounding: {context[:1200]} "
        f"Evidence and status boundary: {boundary} "
        "Create a coherent scientific editorial illustration with a clear visual reading order, distinct foreground/midground/background, "
        "precise remote-sensing geometry where relevant, generous but purposeful spacing, restrained navy/teal/coral accents, "
        "crisp high-resolution detail and strong contrast at printed-page size. Make this figure compositionally distinct from adjacent figures. "
        "No title in the artwork, no paragraphs, no fake Chinese or English labels, no numerical charts, no invented metric values, "
        "no unsupported performance claim, no institutional logo, no watermark, and no decorative repeated flowchart template. "
        "The printed caption outside the image will carry exact terminology and evidence attribution."
    )

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def normalize_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = text.replace("\uf06d", " ")
    text = text.replace("\x0c", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        chunks: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                chunks.append(text)
        return normalize_text("\n\n".join(chunks))
    except Exception:
        pass

    helper = """
from pypdf import PdfReader
from pathlib import Path
import sys
path = Path(sys.argv[1])
reader = PdfReader(str(path))
chunks = []
for page in reader.pages:
    text = page.extract_text() or ""
    if text.strip():
        chunks.append(text)
print("\\n\\n".join(chunks))
"""
    result = subprocess.run(
        ["/usr/bin/python3", "-c", helper, str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return normalize_text(result.stdout)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(path)
    return normalize_text(path.read_text(encoding="utf-8"))


def find_rule_files(topic_dir: Path) -> list[Path]:
    assets_path = topic_dir / "workspace" / "intake" / "topic-assets.json"
    rules: list[Path] = []
    if assets_path.exists():
        assets = read_json(assets_path)
        for rel in assets.get("rules", []):
            path = topic_dir / rel
            if path.exists():
                rules.append(path)
    if rules:
        return rules
    fallback: list[Path] = []
    for path in sorted(topic_dir.rglob("*")):
        if not path.is_file():
            continue
        if "workspace" in path.parts or "output" in path.parts or "record" in path.parts:
            continue
        name = path.name.lower()
        if "比赛" in path.name or "细则" in path.name or "章程" in path.name or "rule" in name:
            fallback.append(path)
    return fallback


def guess_competition_name(raw_text: str, rule_file: Path) -> str:
    candidates = [
        r"全国大学生物联网设计竞赛",
        r"物联网设计竞赛",
    ]
    for pattern in candidates:
        match = re.search(pattern, raw_text)
        if match:
            return match.group(0)
    stem = rule_file.stem
    stem = re.sub(r"^\d{4}", "", stem)
    return stem.strip(" _-")


def extract_dates(raw_text: str) -> list[str]:
    return re.findall(r"20\d{2}\s*年\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?", raw_text)


def find_line(raw_text: str, keyword: str) -> str:
    for line in raw_text.splitlines():
        if keyword in line:
            return " ".join(line.split())
    return ""


def build_competition_spec(raw_text: str, rule_file: Path) -> dict:
    competition_name = guess_competition_name(raw_text, rule_file)
    submission_deadline = find_line(raw_text, "作品完整方案和文档说明提交截止日期")
    if not submission_deadline:
        submission_deadline = find_line(raw_text, "作品完整设计")

    submission_format = find_line(raw_text, "线上提交的作品完整设计方案文档和文档说明")
    if not submission_format:
        submission_format = "线上提交作品完整设计方案文档与实物文档说明"

    scoring_dimensions: list[str] = []
    if "创意" in raw_text:
        scoring_dimensions.append("创意")
    if "技术方案及其实现质量" in raw_text:
        scoring_dimensions.append("技术方案及其实现质量")
    if "应用价值" in raw_text:
        scoring_dimensions.append("应用价值")
    if "讲解" in raw_text:
        scoring_dimensions.append("讲解表现")
    if "演示效果" in raw_text:
        scoring_dimensions.append("作品演示效果")

    bonus_points: list[str] = []
    bonus_line = find_line(raw_text, "加分")
    if bonus_line:
        bonus_points.append("使用赛道推荐技术平台参赛可获得适当加分")

    forbidden_points: list[str] = []
    original_line = find_line(raw_text, "参赛作品必须是学生原创")
    if original_line:
        forbidden_points.append("参赛作品必须学生原创，不得直接使用导师课题或未修改的他赛作品")
    ip_line = find_line(raw_text, "不得侵犯他人的知识产权")
    if ip_line:
        forbidden_points.append("不得侵犯他人的知识产权或其他权益")

    template_requirements: list[str] = []
    template_line = find_line(raw_text, "文档和视频需要按照组委会发布的文档内容和格式要求制作")
    if template_line:
        template_requirements.append("文档和视频需按组委会发布的内容与格式要求制作")

    pending_confirmations = [
        "当前章程未给出作品书具体章节模板，需要补充命题文件或文档格式要求。",
        "当前 topic 的具体赛道 / 命题方向尚未从章程中唯一确定，需要结合命题文件确认。",
        "当前章程未明确作品书字数或页数限制，需要补充模板文件确认。",
    ]

    return {
        "competition_name": competition_name,
        "track_name": "",
        "deadline": submission_deadline,
        "submission_format": submission_format,
        "word_limit": "",
        "page_limit": "",
        "required_sections": [],
        "optional_sections": [],
        "scoring_dimensions": scoring_dimensions,
        "bonus_points": bonus_points,
        "forbidden_points": forbidden_points,
        "template_requirements": template_requirements,
        "pending_confirmations": pending_confirmations,
    }


def update_workspace_state(topic_dir: Path, success: bool, blocking_reason: str) -> None:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if not state_path.exists():
        return
    state = read_json(state_path)
    if success:
        state["current_step"] = "ideas"
        state["workflow_status"]["requirements"] = "completed"
        state["workflow_status"]["ideas"] = "active"
        state["next_action"] = "run_evidence"
        state["blocking_reason"] = ""
        state["required_inputs"] = []
    else:
        state["current_step"] = "requirements"
        state["workflow_status"]["requirements"] = "active"
        state["next_action"] = "fix_requirements"
        state["blocking_reason"] = blocking_reason
        state["required_inputs"] = ["有效的比赛细则文件"]
    write_json(state_path, state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AutoSearch MVP step1 rule parsing.")
    parser.add_argument("topic_dir", help="Topic directory, such as sample/topic_xx")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    topic_dir = Path(args.topic_dir).expanduser().resolve()
    step_dir = topic_dir / "workspace" / "requirements"
    rules = find_rule_files(topic_dir)

    if not rules:
        update_workspace_state(topic_dir, success=False, blocking_reason="未找到比赛细则文件")
        raise SystemExit("No rule files found for requirements.")

    raw_chunks: list[str] = []
    for rule_file in rules:
        raw_text = extract_text(rule_file)
        raw_chunks.append(f"# Source: {rule_file.relative_to(topic_dir)}\n\n{raw_text}")

    combined_text = "\n\n".join(raw_chunks).strip()
    primary_rule = rules[0]
    spec = build_competition_spec(combined_text, primary_rule)

    dates = extract_dates(combined_text)
    summary_lines = [
        "# Rule Summary",
        "",
        f"- Competition Name: {spec['competition_name'] or 'unknown'}",
        f"- Primary Rule File: {primary_rule.relative_to(topic_dir)}",
        f"- Submission Deadline: {spec['deadline'] or 'pending'}",
        f"- Submission Format: {spec['submission_format'] or 'pending'}",
        "",
        "## Scoring Dimensions",
    ]
    summary_lines.extend([f"- {item}" for item in spec["scoring_dimensions"]] or ["- pending"])
    summary_lines.extend(["", "## Bonus Points"])
    summary_lines.extend([f"- {item}" for item in spec["bonus_points"]] or ["- none detected"])
    summary_lines.extend(["", "## Forbidden Points"])
    summary_lines.extend([f"- {item}" for item in spec["forbidden_points"]] or ["- none detected"])
    summary_lines.extend(["", "## Dates Mentioned"])
    summary_lines.extend([f"- {item}" for item in dates] or ["- none detected"])
    summary_lines.extend(["", "## Pending Confirmations"])
    summary_lines.extend([f"- {item}" for item in spec["pending_confirmations"]] or ["- none"])

    write_json(step_dir / "competition-spec.json", spec)
    write_text(step_dir / "rule-summary.md", "\n".join(summary_lines) + "\n")
    write_text(step_dir / "rule-source.md", "# Rule Source Extract\n\n" + combined_text[:20000] + "\n")

    update_workspace_state(topic_dir, success=True, blocking_reason="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

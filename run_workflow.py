from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "workflow" / "scripts"

COMMANDS = [
    ("init_workspace.py", "初始化工作区"),
    ("run_requirements.py", "解析要求"),
    ("run_evidence.py", "整理证据"),
    ("run_ideas.py", "生成候选选题"),
    ("run_selection.py", "确认选题"),
    ("run_concept.py", "形成选题说明"),
    ("run_research.py", "自动研究与实验契约"),
    ("run_document_plan.py", "规划文档结构"),
    ("run_document_writing.py", "撰写文档"),
    ("run_document_review.py", "审查文档"),
]


def main() -> int:
    p = argparse.ArgumentParser(description="从选题到文档成稿的完整工作流")
    p.add_argument("topic_dir", help="已有资料的主题目录")
    p.add_argument("--topic", default="", help="主题显示名")
    p.add_argument("--select-id", default="", help="人工确认的候选编号，例如 idea_a")
    p.add_argument("--seed-text", default="", help="证据整理的补充方向")
    p.add_argument("--idea-seed", default="", help="候选生成的补充方向")
    p.add_argument("--from-step", dest="from_step", choices=[name[:-3] for name, _ in COMMANDS], default="init_workspace")
    p.add_argument("--dry-run", action="store_true", help="只显示将要执行的命令")
    args = p.parse_args()
    topic = Path(args.topic_dir).expanduser().resolve()
    if not topic.exists():
        raise SystemExit(f"主题目录不存在: {topic}")
    start = next(i for i, (name, _) in enumerate(COMMANDS) if name[:-3] == args.from_step)
    common = [str(topic)]
    extras = {
        "init_workspace.py": (["--topic-name", args.topic or topic.name],),
        "run_requirements.py": ([],),
        "run_evidence.py": ((["--topic", args.topic] if args.topic else []) + (["--seed-text", args.seed_text] if args.seed_text else []),),
        "run_ideas.py": ((["--topic", args.topic] if args.topic else []) + (["--idea-seed", args.idea_seed] if args.idea_seed else []),),
        "run_selection.py": ((["--select-id", args.select_id] if args.select_id else []),),
        "run_concept.py": ((["--topic", args.topic] if args.topic else []),),
        "run_research.py": ((["--topic", args.topic] if args.topic else []),),
        "run_document_plan.py": ((["--topic", args.topic] if args.topic else []),),
        "run_document_writing.py": ([],),
        "run_document_review.py": ([],),
    }
    for name, label in COMMANDS[start:]:
        cmd = [sys.executable, str(SCRIPTS / name), *common, *extras[name][0]]
        print(f"[{label}] {' '.join(cmd)}")
        if args.dry_run:
            continue
        result = subprocess.run(cmd, cwd=SCRIPTS, text=True)
        if result.returncode != 0:
            print(f"工作流在“{label}”处停止，返回码 {result.returncode}", file=sys.stderr)
            return result.returncode
    if not args.dry_run:
        print(f"文档工作流完成，结果位于: {topic / 'output'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

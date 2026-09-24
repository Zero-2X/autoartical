#!/usr/bin/env python3
"""Write a full per-figure ImageGen prompt after article interpretation is filled."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from visual_prompting import compose_prompt


def main() -> int:
    parser = argparse.ArgumentParser(description="由逐图文章理解生成完整的 Codex 内置 ImageGen Prompt")
    parser.add_argument("topic_dir", type=Path)
    parser.add_argument("--figure-id", required=True)
    args = parser.parse_args()
    path = args.topic_dir / "workspace" / "document_assets" / "figures" / f"{args.figure_id}.request.json"
    request = json.loads(path.read_text(encoding="utf-8"))
    request["prompt"] = compose_prompt(request)
    request["status"] = "awaiting_generation"
    request.pop("generation", None)
    request.pop("visual_review", None)
    request.pop("stale_reason", None)
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(request["prompt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

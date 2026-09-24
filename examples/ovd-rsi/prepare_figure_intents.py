"""Apply editorial figure interpretations for this example proposal."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "workflow" / "scripts"))
from visual_prompting import compose_prompt, manuscript_sha256  # noqa: E402


def main() -> None:
    intents = json.loads((HERE / "workspace" / "document_assets" / "figure-intents.json").read_text(encoding="utf-8"))
    figures = HERE / "workspace" / "document_assets" / "figures"
    draft = (HERE / "workspace" / "document_writing" / "作品书草稿.md").read_text(encoding="utf-8")
    draft_hash = manuscript_sha256(draft)
    for figure_id, intent in intents.items():
        path = figures / f"{figure_id}.request.json"
        request = json.loads(path.read_text(encoding="utf-8"))
        request["source_draft_sha256"] = draft_hash
        generation = request.get("generation", {})
        if generation.get("source_path"):
            generation["source_path"] = f"generated_images/{Path(generation['source_path']).name}"
        if request.get("status") == "reviewed":
            path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            continue
        understanding = request["article_understanding"]
        understanding["key_message"] = intent["message"]
        understanding["visual_elements"] = intent["elements"]
        understanding["visual_direction"] = intent["direction"]
        understanding["evidence_boundary"] = (
            "本图用于解释已写明的研究问题或拟议系统机制，不代表实验已经完成；"
            "不得虚构 benchmark 数值、性能曲线、商业部署状态、具体地理坐标或可识别机构标识。"
        )
        request["prompt"] = compose_prompt(request)
        request["status"] = "awaiting_generation"
        path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"prepared {len(intents)} article-grounded figure prompts")


if __name__ == "__main__":
    main()

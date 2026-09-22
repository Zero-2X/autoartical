from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    p=argparse.ArgumentParser(description="为文档配图生成可审计的内置图像请求")
    p.add_argument("project", type=Path)
    p.add_argument("--figure-id", required=True)
    p.add_argument("--purpose", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--style", default="学术论文风格，克制配色，清晰留白")
    p.add_argument("--aspect", default="16:9")
    args=p.parse_args()
    out=args.project/"workspace"/"document_assets"/"figures"/f"{args.figure_id}.request.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    prompt=(f"用途：{args.purpose}\n内容：{args.content}\n风格：{args.style}\n比例：{args.aspect}\n约束：不生成未经提供的数据、数值、机构标志或虚构引用；图中文字只使用已给出的术语；输出适合放入正式研究文档。")
    data={"figure_id":args.figure_id,"created_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"prompt":prompt,"route":"Codex built-in image_gen","status":"awaiting_generation","source_refs":[]}
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(out)
    return 0
if __name__ == "__main__": raise SystemExit(main())

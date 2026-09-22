"""Local-only document adapters with content-addressed extraction records."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".txt", ".json", ".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm"}
SCHEMA_VERSION = 1


def extract_source(path: Path, cache_dir: Path | None = None) -> dict:
    path = path.resolve()
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"不支持的资料格式：{suffix}")
    engine = ("pypdf" if suffix == ".pdf" else "trafilatura" if suffix in {".html", ".htm"}
              else "markitdown" if suffix in {".docx", ".pptx", ".xlsx"} else "builtin")
    try:
        engine_version = version(engine) if engine != "builtin" else "1"
    except ModuleNotFoundError as exc:
        raise RuntimeError("请先安装 requirements-integrations.txt 中的资料解析依赖") from exc
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    key = hashlib.sha256(f"{digest}|{suffix}|{engine}|{engine_version}|{SCHEMA_VERSION}".encode()).hexdigest()
    cache = cache_dir / f"{key}.json" if cache_dir else None
    if cache and cache.exists():
        result = json.loads(cache.read_text(encoding="utf-8"))
        return {**result, "source_path": str(path), "cache_path": str(cache)}
    segments, warnings = [], []
    if engine == "pypdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        for number, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            segments.append({"locator": f"page:{number}", "page": number, "text": text})
            if not text.strip():
                warnings.append(f"第 {number} 页无可提取文本，需检查空白页或扫描件 OCR")
    elif engine == "trafilatura":
        from trafilatura import extract
        text = extract(raw, include_comments=False, include_tables=True) or ""
        segments = [{"locator": "extracted-text", "page": None, "text": text}]
        warnings.append("HTML 定位指向提取文本；请对照原始页面核实正文与表格")
    elif engine == "markitdown":
        from markitdown import MarkItDown
        text = MarkItDown(enable_plugins=False).convert(str(path)).text_content
        segments = [{"locator": "extracted-text", "page": None, "text": text}]
        warnings.append("转换器未提供原始页码；不得将提取段落号冒充原始页码")
    else:
        text = raw.decode("utf-8-sig")
        segments = [{"locator": f"line:{number}", "page": None, "text": line}
                    for number, line in enumerate(text.splitlines(), 1)]
    text = "\n\n".join(segment["text"] for segment in segments)
    if not text.strip():
        raise ValueError(f"未提取到有效文本：{path.name}；请提供可读文本或先完成 OCR")
    result = {"schema_version": SCHEMA_VERSION, "source_path": str(path), "source_sha256": digest,
              "engine": engine, "engine_version": engine_version,
              "extracted_at": datetime.now(timezone.utc).isoformat(),
              "segments": segments, "text": text, "warnings": warnings,
              "verification_status": "unverified"}
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["cache_path"] = str(cache)
    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="全文导入资料，记录来源摘要、位置和提取告警")
    parser.add_argument("source", type=Path)
    parser.add_argument("--cache-dir", type=Path, required=True)
    args = parser.parse_args()
    result = extract_source(args.source, args.cache_dir)
    print(json.dumps({key: result[key] for key in ("source_sha256", "engine", "cache_path", "warnings")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

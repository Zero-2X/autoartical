#!/usr/bin/env python3
"""Anti-fabrication guard for rewrites, polishing and translation passes.

Idea adapted (re-implemented, no code or data copied) from the "Verification
Layer" of mumdark/nature-writing-studio: after any rewrite, every specific
token in the output must be traceable to the input.

Hard tokens (must appear in the source, or in the allow list):
  * numbers with optional unit/percent  (``188282``、``95%``、``34 FPS``)
  * citation markers                     (``[12]``、``[5-7]``)
  * figure/table/equation labels          (``图4-2``、``表5-1``、``式 (4-3)``、``Fig. 3``)
  * Latin identifiers: acronyms, model/dataset names, versions
                                          (``DOTA-v2.0``、``ZNF219``、``YOLO-World``)

General vocabulary is never checked: the question is “if the source were
removed, would this token be unsupported?”, not “is this word new?”.

Also reported: hard tokens present in the source but dropped by the rewrite
(a rewrite that silently removes a number or citation changes the evidence),
and em-dashes (U+2014) in English text.

Usage:
  python revision_guard.py SOURCE REVISED [--allow-file allow.txt] [--out report.json]
Exit code 0 only when nothing untraceable was found.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NUMBER = re.compile(r"(?<![A-Za-z0-9_.])(\d+(?:[.,]\d+)*)(\s?(?:%|‰|个百分点|FPS|ms|px|像素|cm|mm|pt|倍))?")
CITATION = re.compile(r"\[(\d+(?:\s*[,，\-–]\s*\d+)*)\]")
LABEL = re.compile(r"(?:图|表|式)\s*\(?\d+-\d+\)?|(?:Fig\.|Figure|Table|Eq\.)\s*\d+[a-z]?", re.I)
IDENT = re.compile(r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9]*(?:[-_./][A-Za-z0-9]+)*)(?![A-Za-z0-9])")
DEFAULT_ALLOW = {
    # generic connective/technical words that may appear in any rewrite
    "and", "or", "the", "of", "in", "on", "to", "for", "with", "by", "from", "as", "at", "we", "our", "here", "this",
    "a", "an", "is", "are", "be", "was", "were", "that", "which", "using", "use", "show", "shows", "identify",
    "data", "method", "methods", "model", "models", "results", "result", "analysis", "figure", "table",
    "RGB", "GPU", "CPU", "AI", "API", "PDF", "DOCX", "Word", "OK",
}
ACRONYM = re.compile(r"[A-Z]{2,}|[A-Za-z]+\d|\d+[A-Za-z]|[A-Za-z]+[-_./][A-Za-z0-9]")


def strip_markup(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)          # image paths
    text = re.sub(r"\]\([^)]*\)", "]", text)                  # link targets
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"(?m)^#{1,6}\s+[\d.]+\s*", "", text)        # heading numbers
    return text


def norm_number(raw: str) -> str:
    return raw.replace(",", "").replace("，", "")


def hard_tokens(text: str) -> dict[str, set[str]]:
    text = strip_markup(text)
    citations = set()
    for group in CITATION.findall(text):
        for part in re.split(r"[,，]", group):
            if re.search(r"[-–]", part):
                a, b = (int(x) for x in re.split(r"[-–]", part))
                citations.update(str(n) for n in range(a, b + 1))
            else:
                citations.add(part.strip())
    no_cites = CITATION.sub(" ", text)
    labels = {re.sub(r"\s|\(|\)", "", m).lower() for m in LABEL.findall(no_cites)}
    no_labels = LABEL.sub(" ", no_cites)
    numbers = {norm_number(m.group(1)) + (m.group(2) or "").strip() for m in NUMBER.finditer(no_labels)}
    idents = {m for m in IDENT.findall(no_labels) if ACRONYM.search(m) or (m[:1].isupper() and len(m) > 2)}
    return {"numbers": numbers, "citations": citations, "labels": labels, "identifiers": idents}


def guard(source: str, revised: str, allow: set[str] | None = None) -> dict:
    allow = {a.lower() for a in (allow or set()) | DEFAULT_ALLOW}
    src, out = hard_tokens(source), hard_tokens(revised)
    src_lower = source.lower()
    src_numbers_bare = {re.sub(r"[^\d.]", "", n) for n in src["numbers"]}
    untraceable: list[dict] = []
    for kind in ("numbers", "citations", "labels", "identifiers"):
        for token in sorted(out[kind] - src[kind]):
            if token.lower() in allow:
                continue
            if kind == "numbers" and re.sub(r"[^\d.]", "", token) in src_numbers_bare:
                continue  # same value, unit phrasing changed
            if kind == "identifiers" and token.lower() in src_lower:
                continue
            untraceable.append({"kind": kind, "token": token})
    dropped = [{"kind": k, "token": t} for k in ("numbers", "citations", "labels") for t in sorted(src[k] - out[k])]
    em_dash = []
    for line in revised.splitlines():
        line = re.sub(r"\]\([^)]*\)", "]", line)  # image/link targets are not prose
        latin = len(re.findall(r"[A-Za-z]", line))
        cjk = len(re.findall(r"[一-鿿]", line))
        if "—" in line and latin > cjk:
            em_dash.append(line.strip()[:60])
    return {
        "verdict": "pass" if not untraceable and not em_dash else "fail",
        "untraceable_tokens": untraceable,
        "dropped_tokens": dropped,
        "english_em_dash_lines": em_dash,
        "rule": "改写后的数字、引用、图表式编号、专名/缩写必须能在原文中找到；被删掉的数字或引用需说明理由。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="改写/润色/翻译后的防捏造回溯检查")
    parser.add_argument("source", type=Path)
    parser.add_argument("revised", type=Path)
    parser.add_argument("--allow-file", type=Path, help="每行一个允许新增的通用术语（如领域常识缩写）")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    allow = set()
    if args.allow_file and args.allow_file.exists():
        allow = {line.strip() for line in args.allow_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")}
    result = guard(args.source.read_text(encoding="utf-8"), args.revised.read_text(encoding="utf-8"), allow)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(payload + "\n", encoding="utf-8", newline="\n")
    sys.stdout.write(payload + "\n")
    return 0 if result["verdict"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fetch reference metadata programmatically and emit GB/T 7714 entries.

Adopted from the citation rule shared by Orchestra ``ml-paper-writing`` and
K-Dense ``citation-management``: a reference is never typed from memory.  Each
entry in ``references.json`` names an identifier (arXiv id or DOI); this script
retrieves title/authors/year from the registry, checks the expected title if
one is given, and writes

* ``citation-verification.json``  per-entry status, fetched metadata, date;
* ``references.gbt7714.md``       numbered list ready to paste under 参考文献.

``venue`` (e.g. 会议/期刊) is accepted only together with ``venue_evidence``
(where the publication venue was confirmed: arXiv comment, publisher page).
Entries that cannot be fetched are marked ``unverified`` and the run fails,
so an unverifiable citation cannot reach the delivery silently.
"""
from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import time
import urllib.request
from datetime import date
from pathlib import Path

UA = {"User-Agent": "autoartical-reference-verifier/1.0 (mailto:noreply@example.org)"}


def fetch(url: str, accept: str | None = None) -> str:
    headers = dict(UA)
    if accept:
        headers["Accept"] = accept
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def arxiv_meta(arxiv_id: str) -> dict:
    page = fetch(f"https://arxiv.org/abs/{arxiv_id}")
    meta = lambda key: [html.unescape(v) for v in re.findall(rf'<meta name="citation_{key}" content="(.*?)"', page)]
    comment = re.search(r'tablecell comments[^>]*>(.*?)</td>', page, re.S)
    if not meta("title"):
        raise ValueError("arXiv 页面没有 citation_title")
    return {"title": meta("title")[0], "authors": meta("author"), "date": (meta("date") or [""])[0],
            "registry": "arXiv", "url": f"https://arxiv.org/abs/{arxiv_id}",
            "comment": re.sub(r"<[^>]+>", "", comment.group(1)).strip() if comment else ""}


def doi_meta(doi: str) -> dict:
    data = json.loads(fetch(f"https://api.crossref.org/works/{doi}"))["message"]
    authors = [f"{a.get('family', '')}, {a.get('given', '')}".strip(", ") for a in data.get("author", [])]
    parts = (data.get("issued", {}).get("date-parts") or [[None]])[0]
    return {"title": (data.get("title") or [""])[0], "authors": authors, "date": str(parts[0] or ""),
            "registry": "Crossref", "url": f"https://doi.org/{doi}",
            "container": (data.get("container-title") or [""])[0], "volume": data.get("volume", ""),
            "issue": data.get("issue", ""), "pages": data.get("page", "")}


def gbt_author(name: str) -> str:
    """'Liu, Shilong' -> 'LIU S'; GB/T 7714 lists up to three authors then 等/et al."""
    if "," in name:
        family, given = [x.strip() for x in name.split(",", 1)]
    else:
        bits = name.split()
        family, given = bits[-1], " ".join(bits[:-1])
    initials = "".join(part[0] for part in re.split(r"[\s\-]+", given) if part)
    return f"{family.upper()} {initials}".strip()


def format_gbt(index: int, entry: dict, meta: dict) -> str:
    authors = [gbt_author(a) for a in meta["authors"]]
    author_text = ", ".join(authors[:3]) + (", et al" if len(authors) > 3 else "")
    year = str(entry.get("venue_year") or meta["date"][:4])
    title = meta["title"].rstrip(".")
    if entry.get("venue") and entry.get("type") == "C":
        line = f"[{index}] {author_text}. {title}[C]//{entry['venue']}, {year}"
    elif meta["registry"] == "Crossref" and meta.get("container"):
        vol = f", {meta['volume']}" if meta.get("volume") else ""
        iss = f"({meta['issue']})" if meta.get("issue") else ""
        pages = f": {meta['pages']}" if meta.get("pages") else ""
        line = f"[{index}] {author_text}. {title}[J]. {meta['container']}, {year}{vol}{iss}{pages}"
    elif entry.get("venue"):
        line = f"[{index}] {author_text}. {title}[C]//{entry['venue']}, {year}"
    else:
        line = f"[{index}] {author_text}. {title}[EB/OL]. ({meta['date'][:10].replace('/', '-')})"
    return f"{line}. {meta['url']}"


def main() -> int:
    parser = argparse.ArgumentParser(description="程序化核验参考文献并生成 GB/T 7714 条目")
    parser.add_argument("references", type=Path, help="references.json：按正文首次引用顺序排列")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    entries = json.loads(args.references.read_text(encoding="utf-8"))
    records, lines, failures = [], [], []
    for index, entry in enumerate(entries, start=1):
        try:
            meta = arxiv_meta(entry["arxiv"]) if entry.get("arxiv") else doi_meta(entry["doi"])
            status = "verified"
            expected = entry.get("expected_title")
            if expected:
                ratio = difflib.SequenceMatcher(None, expected.lower(), meta["title"].lower()).ratio()
                if ratio < 0.85:
                    status = "title_mismatch"
                    failures.append(f"[{index}] 标题不符：期望“{expected}”，登记为“{meta['title']}”")
            if entry.get("venue") and not re.fullmatch(r"\d{4}", str(entry.get("venue_year", ""))):
                status = "venue_year_missing"
                failures.append(f"[{index}] 有发表载体但缺少 venue_year（不得沿用预印本日期）")
            if entry.get("venue") and len(str(entry.get("venue_evidence", ""))) < 6:
                status = "venue_unverified"
                failures.append(f"[{index}] 发表载体“{entry['venue']}”缺少核验依据")
        except Exception as exc:  # network, missing id, parse failure
            meta, status = {}, "unverified"
            failures.append(f"[{index}] 无法程序化核验：{entry} ({exc})")
        records.append({"index": index, "key": entry.get("key"), "status": status, "entry": entry, "fetched": meta,
                        "claims_supported": entry.get("claims", []), "checked_on": date.today().isoformat()})
        if meta:
            lines.append(format_gbt(index, entry, meta))
        time.sleep(1.0)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "citation-verification.json").write_text(
        json.dumps({"verdict": "pass" if not failures else "fail", "failures": failures, "records": records},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "references.gbt7714.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": "pass" if not failures else "fail", "count": len(entries), "failures": failures},
                     ensure_ascii=False, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())

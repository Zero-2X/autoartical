#!/usr/bin/env python3
"""Draw a data chart reproducibly from a recorded CSV and a JSON spec.

Rules adopted from K-Dense ``scientific-visualization`` and Orchestra
``academic-plotting``:

* only data present in the CSV are drawn; every row carries a ``source`` key
  that must be listed in the spec's ``sources``;
* bars start at zero; a log axis must be declared and is labelled as such;
* colour is never the only cue (Okabe-Ito palette + marker/hatch);
* no title inside the figure — the manuscript caption carries it;
* output is sized for the printed width (default 14 cm) at 300 dpi, plus SVG;
* ``<name>.provenance.json`` records data/script/image hashes so the export
  gate can detect stale charts.

ImageGen must never be used for charts with numeric axes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
HATCHES = ["", "//", "..", "xx", "\\\\", "--", "++", "oo"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(path: Path) -> str:
    """Line-ending-independent hash for CSV/script inputs."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="从登记数据可复现地绘制数据图")
    parser.add_argument("spec", type=Path)
    parser.add_argument("--topic", type=Path, required=True)
    args = parser.parse_args()
    topic = args.topic.resolve()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    data_path = topic / spec["data"]
    rows = list(csv.DictReader(data_path.open(encoding="utf-8")))
    unknown = {r["source"] for r in rows} - set(spec["sources"])
    if unknown:
        raise SystemExit(f"数据行引用了未登记来源：{unknown}")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": ["SimHei", "Microsoft YaHei", "DejaVu Sans"], "font.size": 9,
        "axes.unicode_minus": False, "axes.spines.top": False, "axes.spines.right": False,
        "svg.fonttype": "none", "pdf.fonttype": 42,
    })
    width_cm, height_cm = spec.get("size_cm", [14, 7])
    fig, ax = plt.subplots(figsize=(width_cm / 2.54, height_cm / 2.54), constrained_layout=True)
    kind = spec["kind"]
    x, y = spec["x"], spec["y"]
    if kind == "barh":
        labels = [r[x] for r in rows]
        values = [float(r[y]) for r in rows]
        groups = [r.get(spec.get("group", ""), "") for r in rows]
        palette = {g: OKABE_ITO[i % 8] for i, g in enumerate(dict.fromkeys(groups))}
        hatch = {g: HATCHES[i % 8] for i, g in enumerate(dict.fromkeys(groups))}
        bars = ax.barh(labels, values, color=[palette[g] for g in groups], edgecolor="black", linewidth=0.4)
        for bar, g in zip(bars, groups):
            bar.set_hatch(hatch[g])
        ax.invert_yaxis()
        if spec.get("log"):
            ax.set_xscale("log")
        else:
            ax.set_xlim(left=0)
        for bar, value in zip(bars, values):
            ax.text(bar.get_width() * (1.05 if spec.get("log") else 1.01), bar.get_y() + bar.get_height() / 2,
                    spec.get("value_format", "{:,.0f}").format(value), va="center", fontsize=8)
        ax.set_xlabel(spec["x_label"] + ("（对数坐标）" if spec.get("log") else ""))
        if spec.get("group"):
            from matplotlib.patches import Patch

            ax.legend(handles=[Patch(facecolor=palette[g], hatch=hatch[g], edgecolor="black", label=g) for g in palette],
                      frameon=False, loc="lower right", fontsize=8)
    elif kind == "scatter":
        groups = [r.get(spec.get("group", ""), "") for r in rows]
        order = list(dict.fromkeys(groups))
        for i, g in enumerate(order):
            pts = [r for r in rows if r.get(spec.get("group", ""), "") == g]
            ax.scatter([float(r[x]) for r in pts], [float(r[y]) for r in pts], color=OKABE_ITO[i % 8],
                       marker=MARKERS[i % 8], edgecolor="black", linewidth=0.4, s=36, label=g, zorder=3)
            for r in pts:
                left = r[spec["label"]] in spec.get("label_left", [])
                ax.annotate(r[spec["label"]], (float(r[x]), float(r[y])), xytext=(-5 if left else 4, 3),
                            textcoords="offset points", fontsize=7.5, ha="right" if left else "left")
        for r in rows:
            if str(r.get("lower_bound", "")).lower() in ("1", "true", "yes"):
                # value is only a published lower bound: show it explicitly
                ax.annotate("", xy=(float(r[x]), float(r[y]) * 1.6), xytext=(float(r[x]), float(r[y]) * 1.08),
                            arrowprops={"arrowstyle": "->", "lw": 0.8})
                ax.annotate("（下限）", (float(r[x]), float(r[y])), xytext=(4, -10), textcoords="offset points", fontsize=7.5)
        if spec.get("log"):
            ax.set_yscale("log")
            from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

            ticks = spec.get("y_ticks") or [1e5, 2e5, 5e5, 1e6, 2e6, 5e6]
            ax.yaxis.set_major_locator(FixedLocator(ticks))
            ax.yaxis.set_minor_locator(NullLocator())
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e4:,.0f}万"))
        if spec.get("y_lim"):
            ax.set_ylim(*spec["y_lim"])
        if spec.get("x_lim"):
            ax.set_xlim(*spec["x_lim"])
        ax.set_xlabel(spec["x_label"])
        ax.set_ylabel(spec["y_label"] + ("（对数坐标）" if spec.get("log") else ""))
        ax.grid(True, linewidth=0.3, alpha=0.5)
        ax.legend(frameon=False, fontsize=8, loc=spec.get("legend_loc", "upper left"))
    else:
        raise SystemExit(f"未支持的图类型：{kind}")
    out = topic / spec["output"]
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300)
    fig.savefig(out.with_suffix(".svg"))
    plt.close(fig)
    script = Path(__file__).resolve()
    provenance = {
        "kind": "data-chart",
        "argument_role": spec["argument_role"],
        "claim": spec["claim"],
        "data": str(data_path.relative_to(topic)).replace("\\", "/"),
        "data_sha256": sha_text(data_path),
        "script": Path(__import__("os").path.relpath(script, topic)).as_posix(),
        "script_sha256": sha_text(script),
        "spec_sha256": sha(args.spec),
        "image_sha256": sha(out),
        "sources": spec["sources"],
        "encoding_rules": "零基线柱状图/声明对数轴；Okabe-Ito 配色并配合纹理或标记；图内不放标题。",
    }
    out.with_suffix(".provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

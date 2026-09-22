# Chart Generation

Use this reference when producing publication-quality charts from experiment data.

## Chart selection

Choose chart type by the question the result is answering, not by habit.

Common choices:

- line: trends over steps, data scale, budget, or thresholds
- bar: compact model or method comparisons when ranking a small set of conditions
- histogram: distribution shifts or error distributions
- scatter: trade-offs, calibration, or correlation views
- heatmap: pairwise factor interactions, matrix comparisons, or sensitivity summaries
- radar: multi-axis profile comparisons only when the number of axes stays readable
- box or violin: variability across seeds or cases when supported cleanly

For a paper with multiple charts, aim for justified diversity. Do not render every result as the same bar-style figure if the underlying questions differ.

## Reproducibility contract

Every chart should have:

- a saved chart spec
- explicit source files
- a generation script
- deterministic export targets
- notes explaining what the chart is meant to show
- a recorded template/style choice, defaulting to `assets/chart-templates/styled_plot_templates/`

## Built-in style pack

This workflow ships with a built-in chart resource pack:

- `assets/chart-templates/styled_plot_templates/style.py`
- `template_line_band.py`
- `template_line_band_pair.py`
- `template_hatched_bar.py`
- `template_hatched_bar_pair.py`
- `template_histogram.py`
- `template_scatter.py`
- `template_heatmap.py`
- `template_radar.py`
- `template_training_curve.py`
- `template_3d_bar.py`
- `template_3d_bar_pair.py`

Use the closest built-in template first, then adapt it to project data. Keep the shared palette, background, fonts, markers, and export conventions from `style.py` unless the project has a written override.

## Paper-readability rules

- keep labels readable at paper scale
- avoid decorative palettes that hide the data
- use legends only when they improve clarity
- make error bars and aggregation policy explicit
- prefer vector export when supported cleanly by the plotting toolchain
- keep related charts stylistically aligned by reusing the same style pack and template family where possible

## Narrative integration

A chart is only useful when it supports a claim.

For each chart, record:

- target section
- claim id or experiment question
- one-sentence takeaway
- caveats or anomalies worth calling out in the caption or text

# writing.2 - Chart Generation

Generate publication-quality experiment charts from verified result files.

## Goals
- Produce paper-ready line, bar, histogram, scatter, or related charts from real data.
- Keep every chart reproducible through a saved spec plus a generation script.
- Match the chart to the paper claim it is meant to support.

## Required Behavior
- Use saved result files, not manually copied numbers.
- Save one script per chart or one tightly scoped script per chart group.
- Default to the built-in `styled_plot_templates` resource pack under `assets/chart-templates/styled_plot_templates/`.
- Reuse that pack's `style.py` for palette, typography, background, legend, marker, and export behavior unless the project explicitly overrides it.
- Choose chart type by data semantics, not by habit: trends over steps/budget/thresholds should prefer line plots, compact method comparisons may use bar plots, distributions should prefer histograms, trade-offs should prefer scatter plots, pairwise factor interactions may use heatmaps, and multi-axis profile comparisons may use radar plots only when they genuinely improve readability.
- Actively avoid collapsing an entire paper into one chart family. When the paper contains multiple charts, prefer a diverse but justified mix of chart types so different result questions are expressed with the clearest form.
- Choose the closest built-in template first (`template_line_band.py`, `template_hatched_bar.py`, `template_histogram.py`, `template_scatter.py`, `template_heatmap.py`, `template_radar.py`, `template_training_curve.py`, or a pair/3D variant) before writing a chart script from scratch.
- Record chart type, source files, aggregation, error bars, style pack, template choice, chart-selection rationale, and export targets in the chart spec.
- Prefer vector output when the plotting stack supports it cleanly.
- Keep axes, legends, and labels readable in conference-paper layouts.
- Do not exaggerate, truncate, or otherwise distort the result story.

## Outputs
- `chart-spec.json`
- `chart-manifest.json`
- `chart-notes.md`
- `scripts/*`
- exported chart files under `writing_paper/figures/`

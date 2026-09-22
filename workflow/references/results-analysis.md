# Results Analysis

Use this guide after the research loop and before paper drafting.

## Goal

Convert raw experiment outputs into paper-ready evidence.

## Required outputs

- `research_5_results_analysis/analysis-report.md`
- `research_5_results_analysis/statistics.json`
- `research_5_results_analysis/results-draft.md`
- `research_5_results_analysis/figures/`
- `research_5_results_analysis/tables/`

## Minimum checks

- compare against the strongest baseline
- report mean and variance where repeated runs exist
- mark which results are exploratory versus stable
- map each major claim to a support status such as `supported`, `mixed`, `unsupported`, or `untested`
- explain which reviewer-facing ablation questions were answered decisively and which remain open
- document major failures and caveats
- keep figure and table provenance traceable to run artifacts

## Rules

- do not cherry-pick the best run without context
- do not hide regressions that affect the main claim
- do not treat a null or noisy ablation as evidence without stating why it is inconclusive
- do not send raw leaderboard numbers straight into the paper without interpretation

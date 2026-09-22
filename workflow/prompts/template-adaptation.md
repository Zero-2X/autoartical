# release Prompt - Template Adaptation

Adapt the reviewed manuscript to the target venue template and packaging rules.

## Core venue rule

When the target venue is NeurIPS 2026, use the official template assets downloaded from:

- `https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip`

The workflow package ships the extracted `neurips_2026.sty` and checklist so projects can use the official source locally.

## Rules

- Prefer the official venue template over generic article scaffolds.
- Record anonymity mode, track, page-limit checks, checklist wiring, and export caveats in `template-notes.md`.
- If the manuscript started from a generic scaffold, migrate it into the venue template before final packaging.

- When release packaging begins, make sure the final release layout cleanly separates `paper/`, `code/`, and `docs/` before the zip archive is created.

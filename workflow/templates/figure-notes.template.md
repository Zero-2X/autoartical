# Figure Notes

## Global Illustration Style

- backend policy: Codex built-in `image_gen` only; no API, CLI, local-model, SVG, or mock fallback
- reference image pool: `assets/autofigure-reference-images/framework-template/`
- style fusion: adaptive use of the illustration style profile
- generation owner: Codex host `image_gen` tool
- default image size hint: `4K`
- blocked-call policy: repair or retry the same built-in record, then stop with a blocker report

## Problem Illustration

- status: pending
- source section: `sections/introduction.tex`
- backend: builtin_image_gen
- preferred aspect ratio: `3:1` to `2.5:1`
- reference images used: TBD
- insertion status: pending
- caption status: pending

## Framework Illustration

- status: pending
- source section: `sections/methodology.tex`
- backend: builtin_image_gen
- preferred aspect ratio: `2:1` to `1.7:1`
- reference images used: TBD
- insertion status: pending
- caption status: pending

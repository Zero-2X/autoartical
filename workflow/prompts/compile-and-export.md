# writing.4 Prompt - Compile and Export

Compile the current paper draft using the official venue template when available.

## Required outputs

- `writing_4_compile/compile-report.md`
- `writing_4_compile/export-notes.md`
- compiled PDF artifacts

## Rules

- For NeurIPS 2026, default to the official `neurips_2026.sty` and checklist files distributed with the workflow.
- Parse compile failures and record them in `compile-report.md`.
- After the first successful compile, automatically send the PDF to the user.
- Record whether the PDF was sent.

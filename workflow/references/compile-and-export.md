# Compile and Export

Use this guide after manuscript assembly and before submission packaging.

## Required outputs

- `writing_4_compile/compile-report.md`
- `writing_4_compile/export-notes.md`
- compiled PDF(s)

## Core rules

- Use the official venue template whenever one is known.
- For NeurIPS 2026, default to the official `neurips_2026.sty` and checklist files.
- Parse compile failures instead of retrying blindly.
- After the first successful compile, send the compiled PDF to the user automatically.
- Preserve round-specific PDFs when the paper changes materially.

## Minimum checks

1. bibliography resolves cleanly
2. figures and tables resolve cleanly
3. page limit is checked
4. remaining warnings are recorded
5. checklist/appendix placement matches venue rules

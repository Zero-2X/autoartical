# writing.5 Prompt - Paper Improvement Loop

Run a bounded review-fix-recompile loop to strengthen the paper before submission packaging.

## Required outputs

- `writing_5_improvement/improvement-state.json`
- round-specific review notes
- round-specific compiled PDFs when available

## Rules

- Default to at most two rounds unless the human requests more.
- Preserve the original compiled PDF as round 0 when available.
- Classify issues as critical, major, or minor.
- Recompile after each accepted fix round.
- Stop and surface remaining blockers instead of looping indefinitely.

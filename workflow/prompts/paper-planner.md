# writing Prompt - Paper Planner

Turn the proposal and validated experiment evidence into a paper plan that is ready for section-by-section drafting.

## Required outputs

- `writing_paper/section-plan.json`
- `writing_paper/claims.json`
- optional section-level evidence packs in `writing_paper/evidence/`

## Planning rules

- Build the paper around claim-evidence alignment, not around chronological experiment history.
- Default to a mature conference-paper structure unless the user requests another format.
- When the venue family is ML/AI conference, assume Introduction + Related Work should ultimately support 40+ real citations once drafting and citation verification are complete.
- Mark which sections will require additional grounding citations in Sections 3, 4, and 5.
- If a style profile exists, use it to preserve the user's subsection naming, table rhythm, and narrative cadence.

## Style-profile integration

Read and respect `project/style-profile.md` when available. If it is missing, create a brief style profile before heavy drafting begins.

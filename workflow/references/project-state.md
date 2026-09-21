# Project State and Workspace Memory

Every new research project should live in its own dedicated workspace folder created by `scripts/init_research_project.py`.

## Goal

Preserve long-lived project state so the user can return later and still recover:

- current step
- latest user requests
- major decisions and pivots
- conversation summaries that matter for future work
- current writing direction
- next actions and blockers

## Required state files

- `project/state/workspace-state.json`
- `project/state/record-state.json`
- `project/state/conversation-log.md`
- `project/state/request-log.md`
- `project/state/decision-log.md`
- `project/state/change-log.md`
- `project/style-profile.md`

## Update policy

Update these files whenever one of the following happens:

- step changes
- step completes, blocks, or rolls back
- the user changes the project direction
- a new hard requirement appears
- a major writing/style preference is clarified
- a strong result or blocker appears
- a submission strategy or venue choice changes
- the next action changes materially
- the resume entrypoint changes materially

For step changes, update both `workspace-state.json` and `record-state.json` together. Prefer `scripts/update_project_state.py` for deterministic synchronized updates.

## Persistence rule

Do not treat chat context as durable memory. The project workspace files are the durable record.

## Resume rule

A new agent should be able to resume the project by reading durable files only. That means the state files must answer at least:

- what step is active now
- what the last completed trusted artifact is
- why progress stopped or paused
- what exact next action should be taken
- which files must be loaded first to continue safely

See `references/record-and-resume.md` for the full record contract.

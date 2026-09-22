# Record and Resume Contract

Use this reference when a project must survive chat loss, agent replacement, or long pauses.

## Goal

A new agent should be able to resume the project from durable files alone and answer four questions without relying on prior chat history:

- What step is active now?
- What is finished inside that step?
- Why did progress stop here?
- What is the next correct action?

## Required durable files

Every project should maintain these files as the minimum record surface:

- `project/state/workspace-state.json`
- `project/state/record-state.json`
- `project/state/conversation-log.md`
- `project/state/request-log.md`
- `project/state/decision-log.md`
- `project/state/change-log.md`

## `workspace-state.json`

Treat this as the global control panel. It should answer the global project questions:

- current step
- step status map
- active focus
- current direction
- latest user request
- next actions
- open questions
- blocking reason
- resume entrypoint
- required inputs
- last verified artifact

## `record-state.json`

Treat this as the strict agent-to-agent resume contract. It should answer the operational record questions:

- where a new agent should enter
- what inputs must be loaded first
- what step completed most recently
- what artifact is the last trusted output
- what should not be repeated
- what evidence is verified versus still pending
- what exact next action should be taken

## Update policy

Update both `workspace-state.json` and `record-state.json` whenever one of the following happens:

- step changes
- step completes, blocks, or rolls back
- a new hard requirement appears
- the user changes direction
- a strong result appears
- a major blocker appears
- the next action changes materially
- the resume entrypoint changes materially

## Step-transition rule

Every step transition should record at least:

- `from_step`
- `to_step`
- `reason`
- `evidence`
- `blocking_reason` if any
- `next_action`
- `resume_entrypoint`
- `required_inputs`

If a step cannot be advanced cleanly, record the project as blocked rather than pretending the transition succeeded.

Use `scripts/update_project_state.py` as the default deterministic updater whenever possible so both durable state files stay synchronized.

## Resume protocol for a new agent

When resuming a project:

1. read `project/state/workspace-state.json`
2. read `project/state/record-state.json`
3. read the step-local runtime or gate file named by `resume_entrypoint`
4. load each file listed under `required_inputs`
5. read `request-log.md` and `decision-log.md` before changing direction
6. continue from `next_action` instead of replaying the entire project blindly

## Step-local expectations

Each execution-heavy step should expose a local machine-readable state file and a human-readable summary file.

Examples:

- `research_1_research_bootstrap/runtime-state.json`
- `research_1_research_bootstrap/status.md`
- `research_4_run_and_monitor/runtime-state.json`
- `research_4_run_and_monitor/monitor-summary.md`
- `research_6_baseline_gate/baseline-gate.json`
- `research_10_writing_entry_gate/writing-readiness.json`

These files should be treated as trusted resume inputs once they are updated.

## What to avoid

- relying on chat history as the only source of truth
- leaving `next_action` empty after a major result or blocker
- marking a step as complete without a trusted output artifact
- changing steps without updating both state files
- forcing a new agent to infer the recovery path from scattered notes

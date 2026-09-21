# Workflow

## 0. Create isolated workspace and durable memory

Goal: create a project workspace that can accumulate durable artifacts instead of leaking state across projects.

Expected outputs:

- `project/`
- `project/state/workspace-state.json`
- `project/state/decision-log.md`
- `project/state/change-log.md`
- `project/private/`

Rules:

- keep one isolated project directory per paper or research branch
- record major decisions in durable files instead of relying on transient chat history
- keep provider keys, versioned prompts, and sensitive notes under `private/`
- when operating on a concrete project, do not treat committing or pushing that project's git repository as a default workflow step unless the user explicitly asks for it

## 1. Intake and framing

Goal: turn the raw request into a research brief, literature context, and evaluation contract before ideation starts.

Expected outputs:

- `step0_intake/project-brief.md`
- `step0_intake/literature-sweep.md`
- `step0_intake/source-log.md`
- `step0_intake/discovery-log.md`
- `step0_intake/evaluation-contract.json`
- `style-profile.md`
- `prompt-registry.yaml`

Rules:

- write down the target problem, intended venue, important constraints, and what success looks like
- capture source provenance while surveying literature so later claims can be audited
- define the primary win condition before idea generation begins

## 2. Idea generation

Goal: propose multiple candidate research directions grounded in the intake context.

Expected outputs:

- `step1_ideas/idea-batch.md`
- `step1_ideas/idea-scorecard.json`

Rules:

- generate several credible directions instead of prematurely locking into the first idea
- score ideas against novelty, feasibility, evidence cost, and fit to the evaluation contract

## 3. Human selection gate

Goal: require explicit operator choice before proposal expansion.

Expected outputs:

- `step2_selection/selected-idea.md`
- `step2_selection/rejection-notes.md`

Rules:

- do not auto-promote an idea into a proposal without review
- record why one idea was selected and why the others were not

## 4. Proposal expansion

Goal: turn the selected idea into a stable proposal that can drive execution.

Expected outputs:

- `step3_proposal/Proposal.md`
- `step3_proposal/proposal-notes.md`
- `step3_proposal/proposal-meta.json`

If the proposal is still hand-wavy, revise now instead of pushing uncertainty into the coding loop.

## 4.5 Competition project document generation

Goal: turn application forms, project books, proposal materials, or defense notes into a high-quality content-first, per-slide built-in image generation documentX without requiring the full paper-production pipeline.

Expected outputs:

- `step4_competition_document_generation/brief.md`
- `step4_competition_document_generation/project-profile.json`
- `step4_competition_document_generation/style-profile.json`
- `step4_competition_document_generation/design-spec.md`
- `step4_competition_document_generation/spec-lock.json`
- `step4_competition_document_generation/outline.md`
- `step4_competition_document_generation/deck-outline.json`
- `step4_competition_document_generation/slide-scripts.json`
- `step4_competition_document_generation/image-prompts.json`
- `step4_competition_document_generation/references/visual-system.md`
- `step4_competition_document_generation/references/built-in image generation-prompt-pack.md`
- `step4_competition_document_generation/references/asset-manifest.json`
- `step4_competition_document_generation/assets/slides/Sxx.png`
- `step4_competition_document_generation/visual-qa-report.json`
- `step4_competition_document_generation/references/visual-qa-report.md`
- `step4_competition_document_generation/deck-spec.json`
- `step4_competition_document_generation/documentx/output/<project-slug>-competition-deck.documentx`
- `step4_competition_document_generation/document-build-report.md`
- `step4_competition_document_generation/references/design-review.md`

Rules:

- this step may run immediately after intake if the user only needs `source materials -> document`
- resolve the versioned prompt through `step4_competition_document_generation` in `private/prompt-registry.yaml`
- extract the content, evidence, narrative arc, and slide jobs before creating visual prompts
- write `outline.md`, `deck-outline.json`, and `slide-scripts.json` before final image prompt generation
- use `style-profile.json`, `design-spec.md`, and `spec-lock.json` as constraints for prompt quality, not as a generic master/template to fill later
- do not generate a visual master first and then force the project content into it
- do not reuse old scripts, old templates, previous generated slides, vendor visual masters, or local rendering logic as generation input
- write design-spec, page rhythm, advanced composition, slide-state, and assembly metadata from the current source material and selected style
- split the prompt work into project analysis, style routing, deck planning, slide scripting, full-slide prompt generation, QA, and regeneration
- default image backend is Codex built-in `image_gen`; do not configure or read
  an built-in image generation API key, provider endpoint, proxy, CLI, or local command
- use image generation for the complete final slide images, including the page's short text and diagram composition
- invoke built-in image generation separately for every final slide using that slide's optimized prompt
- keep critical claims short because built-in image generation text can drift; retry direct final-slide generation for slides with wrong or unreadable text
- do not use text-free generated backgrounds plus local typography
- use the built-in built-in image generation path for each slide; if it is unavailable, block
  the step, preserve prompts/specs/manifests, and repair or retry that route
  instead of substituting local drawing, templates, text overlays, API calls,
  or another provider
- write the full-slide built-in image generation prompt pack before generating assets
- copy final generated slide images into `step4_competition_document_generation/assets/slides/` before referencing them
- assemble the documentX from `deck-spec.json` by placing one full-slide image per page in `built-in image generation_full_slide` mode
- block completion if any final slide image is missing
- do not enter the research research loop unless the user explicitly wants the full research/paper workflow

## 5.1 Research bootstrap

Goal: prepare the execution engine and establish the first research-cycle starting point.

Expected outputs:

- `research_1_research_bootstrap/repo-survey.md`
- `research_1_research_bootstrap/repo-manifest.json`
- `research_1_research_bootstrap/selected-codebase.md`
- `research_1_research_bootstrap/task.md`
- `research_1_research_bootstrap/experiment-tracker.md`
- `research_1_research_bootstrap/runtime-state.json`
- `research_1_research_bootstrap/status.md`

Rules:

- keep `tmux + ralph-loop + codex` as the execution engine
- default max iteration count is 10 unless the evaluation contract says otherwise
- keep the main CLI outside the background session; it should monitor output and update project-state files
- when bootstrap completes or blocks, update both `project/state/workspace-state.json` and `project/state/record-state.json`
- prefer `scripts/update_project_state.py` instead of ad-hoc manual edits so a replacement agent sees a synchronized record surface
- treat bootstrap as the setup layer, not the decision layer

## 5.2 Preliminary experiment framing

Goal: create a lightweight paper-facing experiment skeleton before the first real cycle launches.

Expected outputs:

- `research_2_preliminary_experiment_framing/experiment-plan.md`
- `research_2_preliminary_experiment_framing/experiment-tracker.md`
- `research_2_preliminary_experiment_framing/main-table-spec.json`

Rules:

- sketch the initial main superiority table before large runs begin
- record candidate benchmarks, candidate baselines, a headline-claim skeleton, and minimum success criteria
- add a reviewer-facing ablation plan that states which components, controls, or removals are required to defend the core method claims
- keep this framing lightweight and revisable; it should prevent drift, not freeze the whole experiment story too early

## 5.3 Research cycle launch

Goal: package the current branch into a clear launch point for one research cycle.

Expected outputs:

- `research_3_research_cycle_launch/next-run-manifest.json`
- `research_3_research_cycle_launch/direction-update.md`
- `research_3_experiment_bridge/bridge-plan.md`
- `research_3_experiment_bridge/run-manifest.json`
- `research_3_experiment_bridge/record-checklist.md`

Rules:

- every cycle launch must name the active gap, active method delta, and success criteria
- bridge from claims, the current largest baseline gap, and the approved experiment plan, not from a vague wish to run more experiments
- for ablation or control runs, record the reviewer question answered, the exact component change, and the expected directional signal before launch
- block launch if the run package still lacks claim mapping, success criteria, or main-table coverage

## 5.4 Run and monitor

Goal: launch the experiment package in a controlled way and turn runtime events into durable summaries.

Expected outputs:

- `research_4_run_and_monitor/runtime-state.json`
- `research_4_run_and_monitor/monitor-summary.md`
- `research_4_run_and_monitor/run-log.md`
- `research_4_run_and_monitor/checkpoints.json`

Rules:

- start with a smoke run before committing large compute budgets
- record command, environment, dataset version, seed policy, and output directories
- for training-heavy runs, classify health as `continue`, `wait`, or `stop` from loss and eval trends, NaN or Inf checks, and resource behavior, using WandB when available and raw logs otherwise
- summarize failures and anomalies in human language instead of leaving them buried in raw logs
- if a long run stalls, diverges, or breaks the evaluation contract, stop and escalate before burning more budget

## 5.5 Results analysis

Goal: turn raw run artifacts into stable, paper-ready evidence for the current cycle.

Expected outputs:

- `research_5_results_analysis/analysis-report.md`
- `research_5_results_analysis/statistics.json`
- `research_5_results_analysis/results-draft.md`
- `research_5_results_analysis/write-into-paper.md`
- `research_5_results_analysis/figures/`
- `research_5_results_analysis/tables/`

Rules:

- separate raw metrics from interpreted findings
- compare against baselines, controls, and prior internal runs instead of narrating single runs in isolation
- identify which findings are headline results, supporting observations, or non-paper-worthy noise
- mark which claims and reviewer-facing ablation questions are supported, weak, contradicted, or still untested
- preserve anomalies and contradictions; do not silently drop them

## 5.6 Baseline gate

Goal: judge whether the current branch actually surpasses all required baselines and dispatch the next action.

Expected outputs:

- `research_6_baseline_gate/baseline-gate.json`
- `research_6_baseline_gate/baseline-gate.md`

Rules:

- compare the strongest reproducible current evidence against every required baseline in the evaluation contract
- use one of `surpassed`, `partial`, `stalled`, or `regressed`
- name the largest remaining gap metric explicitly
- record `required_next_step`, `blocking_reason`, and whether the branch is eligible for the writing entry gate
- after each verdict, update `project/state/workspace-state.json` and `project/state/record-state.json` with the next action, resume entrypoint, and required inputs
- if the branch is plateauing, do not simply continue the same patch pattern; trigger method refinement instead

## 5.7 Method refinement

Goal: refine the Method section of the proposal without changing the research problem.

Expected outputs:

- `research_7_method_refinement/method-delta-ledger.json`
- `research_7_method_refinement/method-refinement-notes.md`
- `research_7_method_refinement/proposal-method-patch.md`

Rules:

- lock background, motivation, problem statement, and overall research intent
- allow only method-level deltas such as intervention policy, calibration logic, ranking logic, repair policy, and failure handling
- every accepted method delta must be gap-linked: record the target failure mode, expected effect, validation experiment, and kill criterion
- if the branch needs a different problem framing to continue, stop research and escalate instead of mutating the proposal in place

## 5.8 Experiment replanning

Goal: turn the current baseline gap and method state into the next full paper-facing experiment plan.

Expected outputs:

- `research_2_preliminary_experiment_framing/experiment-plan.md`
- `research_2_preliminary_experiment_framing/experiment-tracker.md`
- `research_2_preliminary_experiment_framing/main-table-spec.json`

Rules:

- design the main superiority table first, then derive the must-run experiment blocks from it
- unless explicitly approved otherwise, plan for at least `3` benchmark datasets or evaluation suites in the main superiority story
- unless the field genuinely lacks them, include at least `5` strong baselines or counterparts in the main comparison
- prefer the latest credible SOTA or strongest modern baselines instead of outdated filler methods
- require a large, information-dense main superiority table suitable for the first paper-facing result block
- follow the house table style anchored to `/home/wanguancheng/.AAAAAA/TemplateProjects/ICLR26_Prompt_SAM/tables/table1.tex`
- separate MUST-RUN evidence from NICE-TO-HAVE appendix runs

## 5.9 Spawned review loop

Goal: wrap the execution-heavy research cycle with spawned judge, refiner, and reviewer agents so the branch does not drift into local optima.

Expected outputs:

- `research_9_review_loop/review-state.json`
- `research_9_review_loop/review-log.md`
- `research_9_review_loop/action-ledger.json`

Rules:

- describe the loop with host-agnostic actions such as `spawn_baseline_judge`, `spawn_method_refiner`, `spawn_research_reviewer`, and `continue_research_subagent`
- in OpenClaw, map those actions to `sessions_spawn`, `sessions_send`, `subagents`, and `sessions_history`
- in a Codex-native runtime, map them to the equivalent secondary-agent or subagent interface
- preserve reviewer-thread continuity across rounds when the host supports it, and archive the raw reviewer response for each completed round
- trigger the review loop when a meaningful run cluster completes, when the branch plateaus, when a new best result still fails the baseline gate, when two gap-linked deltas fail in a row, when reviewer-facing ablation coverage is still weak, or when the project may be ready to transition to writing
- stop or escalate when the review loop reaches its round limit, enters stale state without trustworthy continuity, or hits a human checkpoint that requires operator approval
- use spawned agents to judge, refine, and critique the branch; do not replace the execution engine with a pure review loop

## 5.10 writing entry gate

Goal: decide whether the project is paper-ready enough to enter writing drafting.

Expected outputs:

- `research_10_writing_entry_gate/writing-readiness.json`
- `research_10_writing_entry_gate/writing-readiness.md`

Rules:

- require a `surpassed` baseline-gate verdict before entering this gate
- require a minimally complete main table, at least one direct headline-evidence path, and at least one supporting-evidence path
- block writing entry if major contradictions remain unexplained or the method narrative is still changing materially
- write a resume-ready verdict into both `project/state/workspace-state.json` and `project/state/record-state.json` so a new agent can continue from drafting or return to research without replaying old chat
- if the project is not ready, send it back into method refinement, replanning, or stop review instead of drafting early

## 6. Paper drafting

Goal: draft the paper from evidence, not from vague memory.

Expected outputs:

- `writing_paper/section-plan.json`
- `writing_paper/claims.json`
- `writing_paper/evidence/*.json`
- `writing_paper/sections/*.md` or `writing_paper/sections/*.tex`
- `writing_paper/manuscript.md`
- `writing_paper/logic-pass.md`

## 6.1 Illustration generation

Goal: generate paper-ready problem and framework illustrations after the corresponding sections are drafted, using only Codex's built-in `image_gen` record, bundled reference images, adaptive style-profile fusion, and strong `ig_...` provenance. If the built-in route is blocked, repair/retry it and keep the step blocked; no alternate backend is permitted.

## 6.2 Chart generation and integration

Goal: generate publication-quality experiment charts and wire them into the experiments narrative.

## 6.3 Citation verification

Goal: verify citations and keep placeholders explicit.

## 6.4 Compile and export

Goal: compile the manuscript with the correct venue template and produce a reviewable PDF.

## 6.5 Paper improvement loop

Goal: run bounded review-fix-recompile rounds until the manuscript is coherent and stable.

## 6.6 Paper self-review

Goal: block submission packaging if the paper still has logical, evidential, template-level, or page-budget problems.

## 7. Submission packaging and template adaptation

Goal: adapt the manuscript to the venue, verify compliance, and export a structured release bundle.

## 8. Review response

Goal: respond to reviewer feedback with evidence-grounded review-response artifacts and paper patches.

## 9. Post acceptance

Goal: prepare talk, poster, and outward-facing release artifacts once the paper is accepted.

# Artifact Contract

Use this file to keep project outputs consistent across operators and runs.

## Standard layout

```text
<workspace>/
  project/
    project-brief.md
    evaluation-contract.json
    style-profile.md
    private/
      prompt-registry.yaml
    state/
      workspace-state.json
      record-state.json
      conversation-log.md
      request-log.md
      decision-log.md
      change-log.md
    intake/
      related-list.md
      survey.md
      intake-notes.md
      discovery-log.md
      source-log.md
    step1_ideas/
      ideas.md
      ideas.json
    step2_selection/
      selection.md
      selection.json
    step3_proposal/
      Proposal.md
      proposal-meta.json
    step4_competition_document_generation/
      brief.md
      project-profile.json
      style-profile.json
      design-spec.md
      spec-lock.json
      outline.md
      deck-outline.json
      slide-scripts.json
      image-prompts.json
      deck-spec.json
      visual-qa-report.json
      regeneration-log.json
      document-build-report.md
      source-materials/
      assets/
        generated/
        plates/
        slides/
        sources/
        style-references/
      references/
        visual-system.md
        built-in image generation-prompt-pack.md
        asset-manifest.json
        visual-qa-report.md
        regeneration-log.md
        design-review.md
      html/
      documentx/
        output/
    research_1_research_bootstrap/
      run-config.json
      repo-survey.md
      repo-manifest.json
      selected-codebase.md
      task.md
      experiment-tracker.md
      failure-analysis.md
      leaderboard.json
      runtime-state.json
      status.md
      review-summary.md
      runs/
        run_001/
          notes.md
          metrics.json
          changes.md
          proposal-delta.md
    research_6_baseline_gate/
      baseline-gate.json
      baseline-gate.md
    research_7_method_refinement/
      method-delta-ledger.json
      method-refinement-notes.md
      proposal-method-patch.md
    research_3_research_cycle_launch/
      next-run-manifest.json
      direction-update.md
    research_9_review_loop/
      review-state.json
      review-log.md
      action-ledger.json
    research_10_writing_entry_gate/
      writing-readiness.json
      writing-readiness.md
    research_2_preliminary_experiment_framing/
      experiment-plan.md
      experiment-tracker.md
      main-table-spec.json
    research_3_experiment_bridge/
      bridge-plan.md
      run-manifest.json
      record-checklist.md
    research_4_run_and_monitor/
      runtime-state.json
      monitor-summary.md
      run-log.md
      checkpoints.json
    research_5_results_analysis/
      analysis-report.md
      statistics.json
      results-draft.md
      write-into-paper.md
      figures/
      tables/
    writing_1_illustration/
      figure-manifest.json
      render-config.json
      figure-notes.md
    writing_2_charts/
      chart-spec.json
      chart-manifest.json
      chart-notes.md
      README.md
      scripts/
    writing_paper/
      section-plan.json
      claims.json
      citation-log.json
      references.bib
      unverified-citations.md
      logic-pass.md
      manuscript.md
      paper-template.tex
      neurips_2026.sty
      neurips_2026_checklist.tex
      evidence/
      sections/
      figures/
      tables/
    writing_4_compile/
      compile-report.md
      export-notes.md
    writing_5_improvement/
      improvement-state.json
    writing_6_review/
      review-checklist.md
      logic-consistency.md
      fix-list.json
    release_submission/
      venue-profile.json
      submission-manifest.json
      release-manifest.json
      checklist.md
      template-notes.md
      export-notes.md
      release_bundle/
        paper/
        code/
        docs/
      <project-slug>-submission-bundle.zip
    review_review_response/
      reviews.md
      review-summary.md
      rebuttal-plan.json
      rebuttal-draft.md
    post-acceptance_post_acceptance/
      poster-plan.md
      promotion-thread.md
```

## File expectations

### Workspace and state files

Every research project must be created in its own dedicated workspace folder.

Durable project-memory files live under `project/state/` and should be updated whenever the step changes, the user changes direction, or new hard requirements appear.

Required state files:

- `workspace-state.json`: global project control panel including current step, step status, active focus, blockers, resume entrypoint, and next actions
- `record-state.json`: strict resume contract for a new agent, including required inputs, exact next action, do-not-repeat notes, and the last trusted artifact
- `scripts/update_project_state.py` should be the default synchronized updater when changing step state, blockers, resume entrypoints, or next actions
- `conversation-log.md`: durable summaries of important conversation turns
- `request-log.md`: explicit user requests and constraints
- `decision-log.md`: major project decisions and approvals
- `change-log.md`: pivots in method, paper direction, or workflow strategy
- `style-profile.md`: reusable writing-style notes for this project

### `private/prompt-registry.yaml`

Store private mappings only. Do not commit raw prompt text if the user wants it protected.

Suggested keys include:

- `step0_style_profile`
- `step1_idea_generation`
- `step2_proposal_expansion`
- `step4_competition_document_generation`
- `research_1_research_bootstrap`
- `research_6_baseline_gate`
- `research_7_method_refinement`
- `research_3_research_cycle_launch`
- `research_9_review_loop`
- `research_10_writing_entry_gate`
- `research_2_preliminary_experiment_framing`
- `research_3_experiment_bridge`
- `research_4_run_and_monitor`
- `research_5_results_analysis`
- `writing_paper_planner`
- `writing_section_writer`
- `writing_introduction_writer`
- `writing_related_work_writer`
- `writing_preliminaries_writer`
- `writing_methodology_writer`
- `writing_experiments_writer`
- `writing_1_illustration_generation`
- `writing_2_chart_generation`
- `writing_2_chart_integration`
- `writing_abstract_conclusion_writer`
- `writing_logic_checker`
- `writing_4_compile_and_export`
- `writing_5_paper_improvement_loop`
- `writing_6_paper_self_review`
- `release_submission_packaging`
- `release_template_adaptation`
- `review_review_response`
- `post-acceptance_post_acceptance`
- `few_shot_pack`

### research gate, refinement, and review expectations

- `research_6_baseline_gate/baseline-gate.json` should store the round-level baseline judgment, largest remaining gap, and recommended action
- `baseline-gate.md` should explain the gate result in human language
- `research_7_method_refinement/method-delta-ledger.json` should record accepted and rejected method deltas while enforcing locked proposal scope
- `method-refinement-notes.md` should explain what changed in the Method and why
- `proposal-method-patch.md` should isolate the method-only patch that can be merged back into `Proposal.md`
- `research_3_research_cycle_launch/next-run-manifest.json` should translate the latest method delta into the next run package
- `direction-update.md` should explain why the next run set is the minimum useful follow-up
- `research_9_review_loop/review-state.json` should store spawned subagent ids, continuity handles, trigger reason, verdicts, score history, round limits, stale-state status, human-checkpoint status, next action, and writing readiness recommendation
- `review-log.md` should preserve raw review judgments, reviewer-thread continuity, and the archived raw reviewer response for each completed round
- `action-ledger.json` should track whether reviewer-requested actions were applied, skipped, or blocked

### Experiment-planning expectations

- `research_2_preliminary_experiment_framing/experiment-plan.md` should freeze the claim map, experiment blocks, milestone order, and must-run versus nice-to-have split before launch packaging
- the experiment plan should include a reviewer-facing ablation coverage section that explains which component tests are decisive, optional, or intentionally cut
- `experiment-tracker.md` should provide a compact execution-facing ledger derived from the approved experiment plan
- `main-table-spec.json` should define the first superiority table as a paper-facing artifact, including benchmark coverage, baseline set, metric grouping, and style target
- the main superiority plan should normally cover at least `3` benchmarks and at least `5` strong baselines or counterparts unless a reviewed exception is recorded
- baseline selection should prefer the latest credible SOTA or strongest modern systems rather than outdated filler methods
- the main superiority table should follow the dense house style anchored to `/home/wanguancheng/.AAAAAA/TemplateProjects/ICLR26_Prompt_SAM/tables/table1.tex`

### Competition document expectations

- `step4_competition_document_generation/source-materials/` should contain application forms, project books, proposal extracts, judging criteria, screenshots, and other source materials used to build the deck
- `brief.md` should record audience, competition context, target slide count, output format, visual asset density, and must-cover points
- `project-profile.json` should store the source-grounded project extraction used for document planning: project identity, background, pain points, goals, solution, innovations, feasibility, application scenarios, values, risks, and missing/uncertain facts
- `style-profile.json` should store the selected document illustration visual style, palette, image keywords, avoid keywords, layout directions, and deck-level prompt prefix/negative prompt
- `design-spec.md` should lock the human-readable document Master-style design plan: canvas, audience, style objective, color scheme, typography, image policy, page rhythm, and layout library
- `spec-lock.json` should keep the machine-readable execution contract: `direct_final_slide_built-in image generation` generation mode, `built-in image generation_full_slide` assembly mode, selected theme preset, page rhythm by slide id, built-in image generation rules, and source-claim safety rules
- `outline.md` is the canonical markdown slide plan and must include stable `slide_id`, role, job, claim-like headline, on-slide copy, evidence status, visual job, built-in image generation slide goal, and source references
- `deck-outline.json` should mirror the slide plan as structured data with page type, layout type, page rhythm, image density, text density, evidence status, and source references
- `slide-scripts.json` should compress every slide into built-in image generation-stable page scripts: title, subtitle, core message, 3-5 modules, visual chart type, decorations, bottom slogan, and retry text
- `image-prompts.json` should store one structured direct-final-slide prompt entry per slide, aligned with `references/built-in image generation-prompt-pack.md`; prompts must ask built-in image generation to render the complete final document page rather than a background or template
- `references/visual-system.md` should record the deck-level typography, palette, layout, image treatment, proof treatment, and anti-slop constraints
- `references/built-in image generation-prompt-pack.md` is required before generating full-slide images and must include exact slide text, composition guidance, negative constraints, and acceptance criteria for each slide
- built-in image generation must be invoked separately for every slide from the current run's fresh prompt; local typography overlays, old scripts, old templates, and template-first generation are forbidden artifacts
- `references/asset-manifest.json` must list all generated, sourced, or user-provided images selected for the deck, including final full-slide workspace paths under `assets/slides/`
- `deck-spec.json` is the machine-readable assembly contract; in default mode it should set `deck.output_mode` to `built-in image generation_full_slide` and give every slide a `slide_image` path
- `documentx/output/` should contain the image-based documentX generated from full-slide images in `deck-spec.json`
- `visual-qa-report.json` and `references/visual-qa-report.md` should record image quality checks; if inspection is unavailable, they must say so explicitly
- `regeneration-log.json` and `references/regeneration-log.md` should record prompt rewrites for bad pages when visual QA triggers regeneration
- `document-build-report.md` should record the command, output path, slide count, missing assets, assumptions, and manual checks
- `references/design-review.md` should record thesis fit, visual hierarchy, craft quality, functional clarity, and originality before the step is marked complete

### Experiment bridge and runtime expectations

- `next-run-manifest.json` should act as the research-cycle launch package and record cycle id, triggering verdict, target gap, selected method delta, run order, and success criteria
- `research_3_experiment_bridge/run-manifest.json` should bind each planned run to claims, reviewer questions, datasets, metrics, seeds, commands, and expected outputs
- `record-checklist.md` should record whether smoke, sanity, ablation, and full comparison steps are approved
- `research_4_run_and_monitor/runtime-state.json` should track current run status, recovery information, and the latest training-quality verdict
- `monitor-summary.md` should translate logs into human-readable progress updates and explicitly state whether the operator should `continue`, `wait`, or `stop`
- `checkpoints.json` should record important model or artifact checkpoints and their provenance

### Results-analysis expectations

- `analysis-report.md` should separate headline findings, supporting observations, anomalies, open questions, claim-support status, and reviewer-facing ablation verdicts
- `statistics.json` should keep normalized numeric summaries that chart generation can consume directly
- `write-into-paper.md` should identify which findings are safe to narrate in the paper and which should stay internal
- `research_10_writing_entry_gate/writing-readiness.json` should record whether the branch is genuinely ready to enter paper drafting
- `research_10_writing_entry_gate/writing-readiness.md` should explain the blocking items or the paper-readiness rationale in human language

### Figure and chart expectations

- `writing_1_illustration/render-config.json` should record the built-in built-in image generation owner, single allowed mode, record runner, job root, and retry-on-block policy
- `figure-manifest.json` should track which illustrations were generated, inserted, and captioned
- `figure-notes.md` should record built-in provenance, retry/blocker state, and manual adjustments; alternate backends are forbidden
- `writing_2_charts/chart-spec.json` should define chart type, source files, aggregation rules, styling, template selection, and export targets
- `chart-manifest.json` should track generated chart assets, scripts, selected templates, captions, and insertion status
- `chart-notes.md` should record chart rationale, caveats, narrative role, and style-pack usage
- default illustration figures include `problem illustration` after Introduction and `framework illustration` after Methodology
- default chart outputs should be reproducible and script-backed, with a preference for vector export when practical

### Submission-packaging expectations

- `release_bundle/paper/` should contain the final LaTeX-centered paper package, including section files, bibliography, figures, tables, venue assets, and compiled PDF when available
- `release_bundle/code/` should contain the runnable method and experiment reproduction assets needed for code delivery
- `release_bundle/docs/` should contain concise operator-facing explanations such as `README.md`, `paper-readme.md`, `code-readme.md`, and `repro-checklist.md`
- `release-manifest.json` should record the release root, subfolder paths, included assets, excluded assets, and final zip path
- writing should end with a single zip archive of the full structured release bundle rather than a flat dump of mixed files

### Paper and compile-step expectations

- `paper-template.tex` should default to the official venue template when known
- For NeurIPS 2026, keep the official `neurips_2026.sty` and checklist alongside the manuscript files
- `compile-report.md` should record compile commands, warnings, first-successful-compile status, and whether the PDF was sent to the user
- `improvement-state.json` should track review-fix-recompile rounds and round-specific PDFs
- `review-checklist.md` should explicitly check that the compiled main-body page count uses the available venue page budget well without exceeding the limit

### Citation step expectations

- `citation-log.json` must record verified and unresolved citations
- `references.bib` should contain verified entries only
- `unverified-citations.md` should keep unresolved placeholders visible
- Mature ML/AI conference drafts should generally target 40+ real citations overall, with the main density in Introduction and Related Work

## Naming rules

- Use stable lowercase folder names for steps.
- Use zero-padded run ids such as `run_001`.
- Keep proposal filename stable as `Proposal.md`; track version history through git or sidecar metadata.
- Favor one canonical location per artifact type.
- Prefer one chart script per paper-facing chart asset.

## Review gates

Require explicit review before moving forward after:

- idea selection
- first complete proposal draft
- selected codebase and generated `task.md`
- experiment bridge record to long-running jobs
- any major research loop pivot
- results analysis if evidence is weak or contradictory
- chart integration if a plot changes the paper narrative materially
- manuscript assembly
- compile-and-export if the first PDF exposes blocking issues
- self-review completion
- final submission packaging
- rebuttal finalization

## Safe export rule

When exporting the project for others, exclude or redact:

- `private/`
- provider keys
- raw proprietary prompts
- hidden heuristics that the user wants to retain privately

### Illustration-asset expectations

- `assets/autofigure-reference-images/framework-template/` should bundle the default optional reference images used for built-in built-in image generation records
- `writing_1_illustration/render-config.json` should record the default reference-image pool, built-in image-size hint, aspect-ratio targets, title-suppression rule, and adaptive style-fusion settings
- `figure-manifest.json` should record which reference images, built-in provenance id, and aspect-ratio target were used for each figure

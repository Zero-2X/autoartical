# Prompt Integration

Use this guide when prompt files are versioned directly inside a private repository and should stay aligned with the skill runtime.

## Principle

Split the system into two layers:

- skill layer: workflow, schemas, templates, scripts
- prompt layer: versioned prompt text, few-shot assets, provider routing details

In a private repository, both layers can be versioned together, but public packaging should still avoid leaking prompt contents by accident.

## Recommended local layout

```text
skill-packages/
  research-workflow-pipeline/
  dist/
  research-workflow-pipeline/prompts/
      style-profile.md
      step1-idea-generation.md
      step2-proposal-expansion.md
      step4-competition-document-generation.md
      research-1-research-bootstrap.md
      research-3-research-cycle-loop.md
      research-5-results-analysis.md
      writing-paper-planner.md
      writing-section-writer.md
      writing-introduction-writer.md
      writing-related-work-writer.md
      writing-preliminaries-writer.md
      writing-methodology-writer.md
      writing-abstract-conclusion-writer.md
      writing-logic-checker.md
      writing-experiments-writer.md
      writing-1-illustration-generation.md
      writing-3-citation-verification.md
      writing-4-compile-and-export.md
      writing-5-paper-improvement-loop.md
      writing-6-paper-self-review.md
      release-submission-packaging.md
      release-template-adaptation.md
      review-review-response.md
      post-acceptance-post-acceptance.md
      few-shot/
```

In this private-repo mode, keep `research-workflow-pipeline/prompts/` versioned directly with the skill so prompt evolution stays aligned with workflow evolution.

## Registry keys

Use these logical keys in the versioned prompt registry:

- `step0_style_profile`
- `step1_idea_generation`
- `step2_proposal_expansion`
- `step4_competition_document_generation`
- `research_1_research_bootstrap`
- `research_execution_loop`
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
- `writing_abstract_conclusion_writer`
- `writing_logic_checker`
- `writing_experiments_writer`
- `writing_1_illustration_generation`
- `writing_2_chart_generation`
- `writing_2_chart_integration`
- `writing_3_citation_verification`
- `writing_4_compile_and_export`
- `writing_5_paper_improvement_loop`
- `writing_6_paper_self_review`
- `release_submission_packaging`
- `release_template_adaptation`
- `review_review_response`
- `post-acceptance_post_acceptance`
- `few_shot_pack`

## Path-resolution rule

Before running any step:

1. load `project/private/prompt-registry.yaml`
2. resolve the step key for the current step
3. resolve the `source` path to a real local prompt file
4. verify the prompt file exists before continuing
5. stop and surface a configuration error if the step prompt is missing

Do not silently skip a configured versioned prompt.

## Runtime convention

When executing step 0:

1. load `step0_style_profile` from the registry if available
2. inspect the user's prior paper examples or style anchors
3. write `project/style-profile.md`
4. update `project/state/workspace-state.json` to record that style profiling has been completed or deferred

When executing step 1:

1. if available, use `academic-researcher` first to produce or refresh `intake/discovery-log.md` and `intake/source-log.md`
2. treat those logs as retrieval aids, not as the step owner
3. load the versioned prompt body from `step1_idea_generation.source`
4. append the current literature list, survey summary, discovery log, source log, and project constraints
5. during the step-1 run itself, perform an additional deep search around the current topic, anchor papers, recent-year window, and adjacent keywords rather than relying only on the pre-collected logs
6. fold the fresh findings back into the working context, and refresh `discovery-log.md` or `source-log.md` if new papers materially change the search picture
7. let the versioned `step1_idea_generation` prompt remain the primary policy for novelty framing and idea generation
8. call the selected model provider
9. save the raw readable result to `ideas.md`
10. normalize the idea list into `ideas.json`
11. stop for human review

When executing step 2:

1. load the selected idea record and rationale
2. load the versioned proposal prompt body from `step2_proposal_expansion.source`
3. append the current core idea, constraints, and evaluation contract
4. generate `Proposal.md`
5. write proposal metadata to `proposal-meta.json`
6. stop for human review before entering the research loop

When executing document illustration competition document generation:

1. load `step4_competition_document_generation.source`
2. inspect `project/step4_competition_document_generation/source-materials/`, the optional `Proposal.md`, the step `brief.md`, and any style or source assets
3. use `project_analyzer_prompt` to write `project-profile.json`
4. use `deck_planner_prompt` to write `outline.md` and `deck-outline.json` as the canonical content plan with stable slide IDs, evidence status, visual jobs, source references, and full-slide built-in image generation goals
5. use `slide_script_writer_prompt` to write `slide-scripts.json`
6. use `style_router_prompt` to write `style-profile.json` as a prompt constraint, not as a master template
7. do not reuse old scripts, old templates, previous generated slides, or vendor visual masters as generation input
8. write the design-spec, page rhythm, and advanced composition rules from the current source material and selected style
9. keep slide-state and assembly metadata as audit data only; it must not become native document content
10. write `design-spec.md` and `spec-lock.json`, keeping the content outline and slide scripts as the source of truth
11. write `references/visual-system.md`
12. use `full_slide_image_prompt_generator_prompt` to write fresh `image-prompts.json` and `references/built-in image generation-prompt-pack.md` before generating full-slide images
13. invoke only Codex's built-in `image_gen` capability to generate every
    complete final 16:9 slide page directly from its slide-specific prompt;
    keep slide text short and retry wrong or unreadable text through that same
    built-in route. Never use an built-in image generation API key, provider endpoint, proxy,
    CLI, local command, or alternate provider.
14. never generate a generic visual master first and then force all slide content into it
15. copy selected final generated slide images into `step4_competition_document_generation/assets/slides/`
16. update `references/asset-manifest.json`
17. write `deck-spec.json` with `deck.output_mode: built-in image generation_full_slide` and one `slide_image` path per slide
18. assemble the image-based documentX under `documentx/output/` by placing one final slide image full-bleed per page, with no local content overlay
19. use `visual_qa_reviewer_prompt` to write `visual-qa-report.json` and `references/visual-qa-report.md`; use `regenerate_bad_slide_prompt` for bad pages
20. write `document-build-report.md` and `references/design-review.md`
21. stop after document delivery unless the user explicitly asks to continue into the research or paper workflow

When executing research.1 bootstrap:

1. load the versioned task-bootstrap prompt body from `research_1_research_bootstrap.source`
2. inspect the selected idea, proposal, and any baseline references
3. research the latest relevant papers and repositories
4. download or clone promising repos into the workspace
5. write `repo-survey.md`, `repo-manifest.json`, and `selected-codebase.md`
6. fill the meta prompt with project-specific paths and method names
7. generate `task.md`
8. initialize `experiment-tracker.md`
9. stop for human review if the chosen base is questionable

When executing the research research loop:

1. confirm `task.md` exists and has been generated from the research.1 bootstrap prompt
2. load the versioned research execution-loop orchestration prompt from the project prompt registry
3. load the selected codebase and the current research runtime state/config inputs
4. start a dedicated background `tmux` session and mount the reviewed `task.md`, the private research loop orchestration prompt, and an explicit Codex runner
5. run `ralph-loop` with `task.md` inside that background session
6. update one run directory per iteration
7. keep `leaderboard.json`, `experiment-tracker.md`, `runtime-state.json`, and `status.md` current
8. let the main CLI monitor tmux output and send periodic progress reports plus immediate alerts for new-best, error, or manual-review events
9. on forced exit, write `failure-analysis.md`

When executing research.5 results analysis:

1. load `research_5_results_analysis.source`
2. inspect `leaderboard.json` and run artifacts
3. summarize stable findings into `analysis-report.md`
4. write statistics and draft-ready findings
5. stop if the story is not evidence-supported

When executing writing paper drafting:

1. use `writing_paper_planner` to derive section order, claims, and evidence needs
2. prepare one evidence pack per section
3. use the generic section writer for ordinary sections
4. for specialized sections such as Introduction, Related Work, Preliminaries, Methodology, Experiments, Abstract, or Conclusion, prefer the dedicated versioned prompt if it exists
5. merge section drafts into `manuscript.md`
6. run `writing_logic_checker` as an editing pass over the merged draft
7. stop for citation verification, compile/export, improvement-loop, and self-review steps

When executing writing.1 illustration generation:

1. load `writing_1_illustration_generation.source`
2. verify that `sections/introduction.tex` exists before generating the problem illustration
3. verify that `sections/methodology.tex` exists before generating the framework illustration
4. load `writing_1_illustration/render-config.json` and verify that the sole backend is `builtin_image_gen`
5. prepare the prompt manifest, call only Codex's built-in `image_gen` for each figure, and ingest the PNG plus strong `ig_...` provenance
6. if a built-in call is blocked, repair/retry that same record and keep the step blocked until it succeeds; never use AutoFigure, Gemini/API, FLUX, SVG, CLI, or a mock fallback
7. insert the problem illustration near the beginning of the Introduction with a concise caption, usually two to three sentences
8. insert the framework illustration near the beginning of the Methodology with a concise caption, usually two to three sentences
9. update `figure-manifest.json` and `figure-notes.md`

When executing writing.3 citation verification:

1. load `writing_3_citation_verification.source`
2. inspect each citation candidate
3. verify bibliographic metadata
4. write verified records to `citation-log.json`
5. add unresolved items to `unverified-citations.md`
6. update `references.bib`

When executing writing.4 compile and export:

1. load `writing_4_compile_and_export.source`
2. inspect the target venue profile and paper template
3. run the compile command chain and capture warnings/errors in `compile-report.md`
4. write export caveats and next actions to `export-notes.md`
5. after the first successful compile, send the generated PDF to the user and record that delivery in the compile report

When executing writing.5 paper improvement:

1. load `writing_5_paper_improvement_loop.source`
2. initialize or resume `writing_5_improvement/improvement-state.json`
3. preserve the current compiled PDF as round 0 when available
4. run a bounded review-fix-recompile loop
5. classify issues as critical, major, or minor
6. stop and surface remaining blockers instead of looping indefinitely

When executing writing.6 paper self-review:

1. load `writing_6_paper_self_review.source`
2. inspect the manuscript, claims, figures, tables, citations, and compile report
3. complete the review checklist
4. write logic issues and fix priorities
5. block submission if critical issues remain

When executing release submission packaging:

1. load `release_submission_packaging.source` and `release_template_adaptation.source`
2. inspect the manuscript, figures, tables, supplementary assets, and venue profile
3. fill `submission-manifest.json`
4. update `checklist.md`, `template-notes.md`, and export notes
5. stop for final human review

When executing review review response:

1. load `review_review_response.source`
2. ingest reviewer comments
3. classify each issue
4. plan response strategies
5. draft rebuttal text with evidence support
6. stop for human review

When executing post-acceptance post acceptance:

1. load `post-acceptance_post_acceptance.source`
2. identify the accepted-paper story
3. derive a talk outline
4. derive a poster plan
5. derive a public promotion draft if desired

## Safety rules

- Do not embed the versioned prompt body in logs.
- Do not commit versioned prompt files unless the user explicitly wants them versioned in their own private repo.
- Do not package versioned prompts into the distributable `.skill` file.
- If sharing the workflow, share registry keys and template structure only.

## What to parameterize

Leave these as runtime variables rather than hard-coding them into the prompt body:

- literature list
- survey summary
- extra operator constraints
- output count, if needed
- provider choice
- venue requirements
- codebase path, benchmark choice, and budget limits
- reviewer comments and camera-ready constraints
- method names, proposal path, baseline reference, and workspace path

## What can stay fixed

These parts usually belong in the versioned prompt file:

- role framing
- output format contract
- diversity requirement
- feasibility constraints
- writing style and language requirement
- section writing tone and math presentation rules
- review-response tone rules
- research execution-loop rules, rollback requirements, and tracker format

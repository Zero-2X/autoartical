# Figure Generation and Illustration Workflow

Use this guide during writing.1 after core section drafting has stabilized.

## Goal

Generate paper-ready visual artifacts that are structurally aligned with the manuscript rather than visually disconnected from it.

## Default figures

For a standard systems or methods paper, produce two default illustrations unless the human decides otherwise:

1. `problem illustration`: generated after the Introduction is drafted and inserted near the beginning of the paper
2. `framework illustration`: generated after the Methodology is drafted and inserted near the start of the method section

## Required outputs

- `writing_1_illustration/figure-manifest.json`
- `writing_1_illustration/render-config.json`
- `writing_1_illustration/figure-notes.md`
- `writing_paper/figures/problem_illustration.*`
- `writing_paper/figures/framework_illustration.*`
- optional generation scripts in `writing_paper/figures/scripts/`

## Backend policy

- The only official writing.1 illustration backend is Codex's built-in `image_gen` capability.
- Use `scripts/run_direct_illustration.py` only to prepare a built-in built-in image generation prompt manifest and record queue; the host agent must make the actual built-in call and ingest its `ig_...` result.
- Never read or pass an image API key, provider URL, external CLI, local model, proxy, or mock output. The former provider-specific entrypoints are disabled compatibility shims.
- Default image richness target is `4K` when the built-in tool supports that request.
- Pass the bundled optional reference-image pool into every built-in record by default.
- Learn from the bundled framework templates and bias the generator toward denser module structure, richer arrows, and more generic flat-vector icons when the figure semantics support them, while explicitly avoiding black placeholder icons, SVG slot artifacts, repeated content, and large empty regions.
- Do not place the overall figure title inside the generated image; keep only step labels and local mechanism annotations.
- If the built-in image_gen call is blocked, write a blocker report, repair the prompt/context or host record, and retry the same built-in route. Do not use AutoFigure, SVG, local diffusion, API, CLI, or another fallback.

## Style profile and reference assets

- Use `references/illustration-style-profile.md` as the adaptive style source for prompt construction.
- Use the bundled reference-image pool under `assets/autofigure-reference-images/framework-template/` as the default optional reference-image source for builtin `image_gen` records.
- Prefer the framework reference-image pool most strongly for framework illustrations, but allow selective use when a problem illustration also benefits from the layout cues.
- No external gateway or provider configuration is permitted. The built-in host tool is the sole image-generation owner.

## Figure-specific rules

### Problem illustration

- derive it from the concrete failure story in the Introduction
- prefer a banner-like aspect ratio around `3:1` to `2.5:1`
- show the mismatch between user intent, tool selection, argument binding, and execution outcome
- do not place the global problem title inside the image
- place it near the beginning of the paper once the Introduction wording has stabilized
- keep the caption concise by default, usually two to three sentences, with a bold opening label such as `\textbf{Problem illustration.}`

### Framework illustration

- derive it from the Methodology section, not from the abstract alone
- prefer a wide modular aspect ratio around `1.5:1`
- make the pipeline structure faithful to the actual method steps
- keep the main pipeline centered, reduce large empty regions, and fill spare space with distinct supporting cues instead of duplicated modules
- do not place the global framework title inside the image
- place it near the beginning of the Methodology section once the method wording has stabilized
- keep the caption concise by default, usually two to three sentences, with a bold opening label such as `\textbf{Framework illustration.}`

## Safe recovery

If built-in built-in image generation is unavailable, the figure step remains blocked. Record the pending figure and blocker report, repair or retry the built-in record, and do not promote any alternate backend output to the paper.

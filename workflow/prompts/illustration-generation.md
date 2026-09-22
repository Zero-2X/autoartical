# writing.1 Prompt - Illustration Generation

Generate the paper's core explanatory illustrations only after the relevant sections are already drafted.

## Required outputs

- `writing_1_illustration/figure-manifest.json`
- `writing_1_illustration/render-config.json`
- `writing_1_illustration/figure-notes.md`
- `writing_1_illustration/problem-figure-spec.json`
- `writing_1_illustration/framework-figure-spec.json`
- `writing_paper/figures/problem_illustration.*`
- `writing_paper/figures/framework_illustration.*`

## Required sequence

1. Read `sections/introduction.tex` and derive the motivating failure story.
2. Write `problem-figure-spec.json` with project-specific title, steps, required labels, forbidden terms, and aspect-ratio target before generation.
3. Generate a `problem illustration` that depicts the mismatch between user intent, tool call generation, argument binding failure, and downstream execution consequences.
4. Insert the problem illustration near the beginning of the Introduction with a concise caption, usually two to three sentences.
5. Read `sections/methodology.tex` and derive the actual pipeline or control flow.
6. Write `framework-figure-spec.json` with project-specific title, steps, required labels, forbidden terms, and aspect-ratio target before generation.
7. Generate a `framework illustration` that reflects the real method steps rather than a generic diagram.
8. Insert the framework illustration near the beginning of the Methodology with a concise caption, usually two to three sentences.

## Backend policy

- Use only Codex's built-in `image_gen` capability for both default figures.
- Use `research-workflow-pipeline/scripts/run_direct_illustration.py` only to prepare the built-in-only prompt manifest and record queue; it must never call a provider endpoint.
- The host agent must call built-in `image_gen` for each pending figure and ingest the PNG plus strong `ig_...` provenance.
- Never pass or read an image API key, base URL, external CLI, local model, proxy, or mock output.
- Default image richness target: `4K` when supported by the built-in tool.
- Record the optional reference-image pool from `assets/autofigure-reference-images/framework-template/` in the built-in record as the default optional reference set.
- Adaptively fuse the user style profile into the generation description instead of blindly pasting a fixed style paragraph.
- Explicitly learn from the bundled framework templates and push the generator toward denser modules, more directional flows, and more generic flat-vector icons when the manuscript supports them, but avoid black placeholder icons, obvious SVG slot structures, repeated content, and large empty regions.
- Do not place the overall framework or problem title inside the generated image; keep only useful internal step labels and local mechanism annotations.
- Default final aspect-ratio targets: `framework illustration` around `1.5:1`; `problem illustration` around `3:1` to `2.5:1`.
- If the built-in image_gen route is blocked, repair the prompt/context or record and retry the same built-in route. Do not use AutoFigure, SVG, local diffusion, API, CLI, or another fallback. Record the blocker and retry state in `figure-notes.md`.

## Caption rule

Each figure caption should be standalone enough that a reader can understand the illustration without decoding the entire surrounding paragraph, but it should still stay concise. Default to roughly two sentences: one for what the figure shows and one for why it matters.

## Composition and style rules

- `problem illustration` should default to a wide narrative composition around `3:1` to `2.5:1`.
- `framework illustration` should default to a wide modular composition around `1.5:1`.
- Adaptively fuse the user's style profile into the figure brief instead of blindly pasting the same style paragraph every time.
- Prioritize flat vector infographic style, high information density, modular boxed layout, crisp 2D structure, white background, pastel section blocks, strong accent arrows, richer submodules, and a visibly larger icon vocabulary than the current overly simple outputs.
- Use the reference-image pool especially for framework-style diagrams, but keep semantic faithfulness to the actual paper text primary.
- Do not allow prior test-paper step names or unrelated figure content to leak into the final illustration; current-project `figure-spec` content is authoritative.

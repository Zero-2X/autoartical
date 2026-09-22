# Illustration Style Profile

Use this reference when drafting Codex built-in `image_gen` prompts for writing.1 illustrations.

## Goal

Adapt the paper's figure prompt toward the user's preferred academic infographic style without forcing every figure into the exact same composition.

## Global style traits

Blend these traits into the current figure brief when they improve the match between the manuscript and the final figure:

- flat vector infographic illustration
- highly professional academic paper aesthetic
- advanced Visio or Draw.io style clarity
- crisp lines and 2D flat design
- avoid messy 3D rendering and photorealism
- high information density with clearly organized modular layout
- compartmentalized composition using large rounded rectangular bounding boxes
- mix solid, dashed, and dotted borders when they clarify structure
- clean white main background
- soft pastel module backgrounds such as pale blue, light yellow, soft mint green, and pale peach
- strong accent colors such as deep blue, vibrant orange, and coral red for arrows, highlights, and focal points
- directional flowcharts, interconnected nodes, layered architecture motifs, and modern flat vector icons for data, servers, models, and processes
- learn the visual complexity level of the bundled framework templates instead of collapsing into oversimplified three-box diagrams
- prefer richer module decomposition, denser intermediate cues, and more icon anchors when the manuscript semantics support them

## Adaptation rule

Do not blindly paste the whole style block into every prompt. Instead:

- keep the semantic content of the figure brief primary
- inject the most relevant style traits for the specific figure type
- preserve readability and paper fitness over decorative richness
- prefer cleaner module structure for framework figures
- prefer a more narrative failure chain for problem illustrations

## Default aspect ratios

- `problem illustration`: prefer a wide banner layout around `3:1` to `2.5:1`
- `framework illustration`: prefer a wide modular layout around `1.5:1`

## Reference image usage

Default optional reference images live in:

- `assets/autofigure-reference-images/framework-template/`

These images are copied into the skill and should be recorded in the built-in built-in image generation record by default as optional style anchors.

Use them as style and composition anchors when they help the requested figure, especially for framework-style diagrams, but keep semantic faithfulness to the manuscript primary. Learn density, polish, and module organization from them, yet avoid copying repeated content patterns or leaving large empty regions.

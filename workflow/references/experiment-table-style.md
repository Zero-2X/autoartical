# Experiment Table Style

Use this reference when preparing paper-facing experiment tables, especially the first superiority table in the Experiments section.

## Canonical style target

Follow the style family of the user's reference tables at:

- `/home/wanguancheng/.AAAAAA/TemplateProjects/ICLR26_Prompt_SAM/tables/table1.tex`
- `research-workflow-pipeline/assets/table-style-examples/aaai26-main_results.tex`
- `research-workflow-pipeline/assets/table-style-examples/aaai26-keyComponents.tex`

Treat these files as the house style set for dense main-result tables and compact ablation/component tables.

## Required traits of the main superiority table

- use a `table*` layout when width is substantial
- keep the first main table visibly large and information-dense rather than overly compressed into a tiny summary
- prefer a table that feels empirically rich at first glance: enough rows, columns, and grouped result blocks that the experiments section looks substantial rather than thin
- group columns by major evaluation family, benchmark family, backbone, client count, or setting family when that grouping clarifies the story
- use multirow and multicolumn headers when they improve readability
- prefer the dense grouped-header style seen in `aaai26-main_results.tex`, including explicit block separators and an average or summary column when appropriate
- include enough benchmark coverage and counterpart coverage that the first table visually reads as the paper's central empirical evidence, not as a minimal placeholder table
- highlight best and second-best results clearly
- allow richer but controlled color usage than plain gray-only tables: colored header bands, alternating row shading, and a distinct highlight row for the proposed method are encouraged when they improve scanability
- keep colors paper-like rather than poster-like; prefer muted blue, teal, orange, sand, or gray families over highly saturated neon colors
- keep the caption compact but informative
- ensure the table can stand as the paper's main evidence of superiority

## Content rules

For the first superiority table:

- include at least `3` benchmark datasets unless the user approves a narrower scope
- include at least `5` baselines or strong counterparts unless the field genuinely lacks them
- prefer the strongest latest SOTA comparisons rather than padding with weak historical methods
- include the proposed method and make the comparison protocol uniform across rows or groups
- make the table broad enough that reviewers can assess consistency, not just a single lucky win
- when there is spare room, prefer adding meaningful benchmark coverage, stronger counterpart rows, or grouped setting columns so the first table feels substantial rather than minimalist

## Writing rules around the table

- introduce the question first, then reference the table
- extract 2-4 observations immediately after the table
- emphasize consistency across datasets and baseline strength
- if one dataset behaves differently, say so explicitly instead of hiding it

## Compact ablation and component-table style

For component validation, ablation, or left-right paired tables, also study `research-workflow-pipeline/assets/table-style-examples/aaai26-keyComponents.tex`.

Preferred traits:

- use `minipage` plus side-by-side tables when two tightly related ablations read better together
- use a light header band and one clearly emphasized best row
- keep the table compact but not visually barren; mild background color is allowed to help the reader separate conditions
- use the same color family across related tables so the experiments section looks like one coherent paper set

## What to avoid

- tiny main tables with only one benchmark
- padding the table with obsolete weak baselines just to increase row count
- inconsistent metrics or incomparable settings mixed in one block without disclosure
- captions that restate every cell instead of explaining the table's job
- color usage that is decorative but semantically meaningless
- mixing too many unrelated color families inside one experiments section

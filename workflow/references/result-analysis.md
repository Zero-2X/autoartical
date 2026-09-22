# Result Analysis

Use this reference when converting run outputs into paper-facing evidence.

## What counts as analysis

Analysis is not a raw metric dump. It should answer:

- what improved
- compared to what
- by how much
- how robust the change is
- whether the result supports a paper claim
- what the main caveat is

## Output structure

A strong analysis pass should separate:

- headline findings
- supporting observations
- anomalies and contradictions
- tentative or weak findings
- write-into-paper candidates

## Minimum comparisons

When possible, compare across:

- primary baseline
- strongest internal variant
- ablation variants
- different seeds or splits
- prior project checkpoints

## Story discipline

Use analysis to sharpen the paper story, not to fabricate one.

- Keep contradictory evidence visible.
- Do not over-read small differences.
- Mark noisy or unstable results clearly.
- Prefer one convincing result story over five barely supported claims.

## Main-table readiness

Before calling the main superiority story ready for paper writing, check:

- whether the evidence now covers at least `3` benchmarks or a reviewed narrower scope
- whether the comparison includes at least `5` strong baselines or a reviewed exception
- whether the strongest baselines are current enough to count as credible SOTA-facing evidence
- whether the first superiority table will be large and information-dense instead of a tiny summary

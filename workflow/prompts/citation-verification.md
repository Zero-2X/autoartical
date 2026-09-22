# writing.3 Prompt - Citation Verification

Your goal is to verify the manuscript bibliography as a real, reviewable research artifact rather than a cosmetic cleanup step.

## Required outputs

- `writing_paper/citation-log.json`
- `writing_paper/unverified-citations.md`
- `writing_paper/references.bib`

## Hard gates

### Gate A: citation coverage

For a mature ML/AI conference draft, confirm that the paper contains at least 40 real citations overall, with the main literature density in Introduction and Related Work.

Also inspect whether Sections 3, 4, and 5 cite the appropriate grounding work when they introduce:

- task formulations
- methodological framing
- benchmark choices
- baselines
- evaluation protocols

### Gate B: citation reality

For every cited item, confirm that:

- the source exists
- title, authors, year, and venue are correct
- a DOI, canonical URL, or arXiv link is available when possible
- the cited claim or framing is actually supported by that source

## If a gate fails

If either gate fails, do not pretend the citation step is complete. Instead:

1. search for the missing or better-grounded real papers
2. add verified BibTeX entries to `references.bib`
3. insert the missing citations back into the most appropriate sentences
4. keep any unresolved placeholders visible in `unverified-citations.md`

## Rules

- Never invent references from memory.
- Prefer DBLP, Crossref, publisher pages, or official arXiv pages when reconstructing metadata.
- Do not leave citation placeholders silently unresolved.
- Record enough detail in `citation-log.json` for a future operator to understand what was verified and what remains open.

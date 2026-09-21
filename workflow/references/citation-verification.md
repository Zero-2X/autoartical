# Citation Verification

Use this guide during paper drafting and before submission.

## Core rule

Never generate citations from memory. Verify each citation against a real source.

## Required outputs

- `writing_paper/citation-log.json`
- `writing_paper/unverified-citations.md`
- `writing_paper/references.bib`

## Two-part verification gate

### Gate A: coverage and density

For a mature ML or AI conference draft, verify that the manuscript contains at least 40 real citations overall, with the main density concentrated in Introduction and Related Work.

At minimum:

- Introduction + Related Work should jointly carry the main literature coverage
- Sections 3, 4, and 5 should add citations where formulation choices, methodological framing, benchmarks, or baselines need grounding

### Gate B: existence and metadata

For every cited reference, verify:

- the paper or artifact exists
- title, authors, year, and venue are correct
- DOI, canonical URL, or arXiv link is recorded when available
- the cited claim is actually supported by the source

## Verification workflow

1. extract all cite keys from the manuscript or section files
2. count the verified citations and compare against the target density
3. search the paper by title, author, DOI, or canonical URL
4. confirm the paper exists and matches the cited metadata
5. fetch or copy the BibTeX entry from a verified source
6. if a claim depends on the paper, confirm the claim actually appears there
7. if either gate fails, search for missing real papers and add them back into the most appropriate sections
8. keep any unresolved placeholder visible until fixed

## Rules

- unverified citations must never be disguised as final references
- placeholders should be easy for the human to find and fix
- citation verification is a separate gate from prose drafting
- if Gate A or Gate B fails, the step is not complete

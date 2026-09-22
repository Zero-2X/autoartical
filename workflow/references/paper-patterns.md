# Paper Patterns

This note captures reusable paper-writing patterns extracted from the user's prior projects. The goal is to retain the writing structure without tying the skill to any one paper topic.

## Core writing patterns

### 1. Problem-first opening

The paper should not open with method bragging. It should open with a field-level opportunity, then narrow to a concrete contradiction, then convert that contradiction into one or more explicit research questions.

Recommended progression:

1. macro background and why the area matters
2. narrow to a bottleneck in current methods
3. state one or two research questions explicitly
4. introduce the method as the answer to those questions
5. close the introduction with contribution bullets

### 2. Related work as scoped buckets

Do not dump citations into one long paragraph. Group related work into a few tightly scoped buckets. Each bucket should:

- open with a one-line theme sentence
- summarize representative works with citations
- end by clarifying what remains unresolved or why the current paper differs

Good subsection titles are short and categorical, such as a method family, capability, or problem setting.

### 3. Preliminaries as clean setup only

Preliminaries should define notation, task formulation, and objective setup without leaking the method. It should feel like the shared mathematical step on which the method will later act.

Recommended order:

1. opening purpose sentence
2. notation and symbols
3. standard problem formulation
4. objective formulation as the bridge into methodology

### 4. Methodology as a logical cascade

Methodology should read like a chain of necessity, not a shopping list of modules. Each subsection should make the next one feel inevitable.

Recommended structure:

- `Overview` paragraph first
- framework figure reference immediately in the overview
- a commented figure placeholder after the overview
- 3-5 ordered subsections with explicit transitions
- every major formula introduced with embedded rationale, not isolated explanation

### 5. Contributions from different roles

Contribution bullets read more cleanly when each item plays a different role, such as:

- problem identification
- practical solution or technical framework
- experimental validation or empirical finding

### 6. Abstract and conclusion as single-paragraph capsules

From the example projects, the strongest abstracts and conclusions are compact and single-paragraph. They should prioritize crisp narrative movement over section-like micro-structure.

## Common section ordering

A stable section order that appears repeatedly and generalizes well is:

1. Introduction
2. Related Work
3. Preliminaries
4. Methodology
5. Experiments
6. Conclusion

Optional later sections can include limitations, ethics, appendix, rebuttal support, or supplementary implementation notes.

## Notation discipline

The prior projects repeatedly benefit from a notation-first habit:

- define symbols before using them in formulas
- reuse notation instead of renaming the same concept later
- keep entity, set, graph, loss, and objective notation visually distinct
- use a notation table when the method becomes symbol-heavy

## Figure and table discipline

A recurring strength in the example papers is that each figure or table supports one clear argumentative job.

Recommended rule:

- one figure or table, one claim
- reference each visual exactly where its narrative payoff happens
- do not insert visuals before the reader knows what question they answer

## Section drafting policy for this skill

Use specialized prompts for the sections where the user has a strong house style. Use the generic writer only for the remaining sections. Merge sections only after section-level logic is stable.

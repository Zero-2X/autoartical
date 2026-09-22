# Experiment Patterns

This note captures reusable experiment-design and experiment-writing patterns extracted from the user's prior projects.

## Core experiment philosophy

Experiments should not be presented as a bag of tables. They should answer a sequence of increasingly specific research questions.

A robust generic ordering is:

1. experimental setup
2. `Q1`: main effectiveness against baselines
3. `Q2`: component or ablation analysis
4. `Q3`: robustness, sensitivity, or efficiency analysis
5. `Q4`: qualitative cases or mechanism-level observations

If needed, extend naturally to `Q5`, `Q6`, and beyond for efficiency, scaling, generalization, or backbone transfer.

## Default subsection example

A strong default scaffold is:

```latex
\section{Experiments}

\noindent \textbf{Experimental Setup.} Briefly introduce datasets, metrics, counterparts, and implementation details.

\subsection{Q1: Main Effectiveness}
% \obs Observation 1.
% \obs Observation 2.

\subsection{Q2: Component Validation}
% \obs Observation 1.
% \obs Observation 2.

\subsection{Q3: Robustness and Sensitivity}
% \obs Observation 1.
% \obs Observation 2.

\subsection{Q4: Qualitative Analysis}
% \obs Observation 1.
% \obs Observation 2.
```

## Setup block first

Before showing any headline result, define the common protocol:

- datasets or benchmarks
- train/validation/test split or evaluation environment
- metrics
- baselines
- implementation details that affect fairness

This block should make all later comparisons look obviously fair.

## Use question-driven experiment subsections

A strong reusable pattern from the example projects is to organize experimental sections around explicit questions. In this skill, the default is to surface them directly as `Q1`, `Q2`, `Q3`, and `Q4` in subsection titles unless there is a good reason not to.

Recommended question family:

- `Q1`: does the method outperform strong baselines on the main task?
- `Q2`: which component or design choice actually matters?
- `Q3`: how stable, robust, or efficient is the method?
- `Q4`: what qualitative or interpretive evidence supports the claimed mechanism?

## Main results pattern

The main comparison table should answer one primary claim only: whether the method beats the right baselines under the agreed metric.

Best practices:

- include weak and strong baselines
- report improvement over the strongest relevant baseline
- if multiple backbones or settings exist, keep them grouped consistently
- do not hide negative cells if they matter to the claim

## Ablation pattern

Ablations should test meaningfully different design choices, not only cosmetic hyperparameters.

Useful ablation categories:

- remove a key module
- replace a key decision rule with a weaker variant
- simplify the objective or inference process
- swap the information source or coordination mechanism

## Stability and sensitivity pattern

Where relevant, at least one subsection should answer whether the method is robust to practical variation, such as:

- noise or perturbation
- budget or search depth
- number of agents, hops, rounds, or steps
- memory size, context length, or retrieval breadth
- training or inference cost

## Result narration pattern

Each experiment subsection should do three things in order:

1. state the question being answered
2. present the evidence
3. interpret the evidence in relation to the paper's core claim

A reusable narration style from the prior projects is to surface a few compact observations after a table or figure. In LaTeX drafts, this can be implemented with an `Obs.` lead-in or a small numbered observation list. As a default, each `Q` subsection should contain 2-4 observation-style takeaways unless the evidence is too thin to justify that many.

Do not leave tables uninterpreted.

## Tracker-to-paper bridge

When the project uses an iterative research loop, convert run logs into paper-ready evidence using this bridge:

- raw runs -> leaderboard and tracker
- tracker -> stable findings and caveats
- stable findings -> analysis report
- analysis report -> experiment section outline and claims

## Common mistakes to avoid

- tuning on the test set
- switching metrics between sections
- using different baselines in different tables without explanation
- showing only the best run when variance matters
- reporting numbers without saying what question they answer

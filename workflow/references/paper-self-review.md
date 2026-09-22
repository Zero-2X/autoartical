# Paper Self Review

Use this guide before submission packaging.

## Goal

Catch structural, logical, evidence, citation, and template issues before the paper leaves the project.

## Required outputs

- `writing_6_review/review-checklist.md`
- `writing_6_review/logic-consistency.md`
- `writing_6_review/fix-list.json`
- `writing_5_improvement/improvement-state.json` when a paper-improvement loop is active

## Review dimensions

- structure completeness
- logic consistency
- claim-to-evidence alignment
- figure and table quality
- citation completeness and reality check
- template compliance
- page-limit compliance and page-budget utilization
- limitations honesty
- venue compliance readiness

## Rules

- critical issues block submission packaging
- every unchecked item must either be fixed or explicitly waived by a human
- self-review should happen after manuscript assembly, not while sections are still missing
- if major issues remain, run at least one review-fix-recompile loop before packaging
- for normal conference submissions with a main-body limit, treat the page budget as applying to the main paper body through `Conclusion` unless the venue explicitly says otherwise
- the self-review should check the compiled main-body page count against `release_submission/venue-profile.json`
- do not exceed the allowed main-body page limit
- when the main body is materially underfilled relative to the allowed limit, treat that as a review issue unless a human records a venue-specific or paper-specific justification
- prefer a submission that uses the available page budget well and lands as close to the allowed limit as is defensible without exceeding it

# Decision Schema: 摘要

This file defines audit structure only.
It is not a writing sample, not a tone reference, and not a content template for正文生成.

## Scope
- Intended reader: agent3 auditor.
- Agent2 writer should not use this file as a content-generation reference.

## Verdict Enum
- `approved`: chapter can move forward, but only if all required dimensions are explicit and closed.
- `revise`: chapter has repairable issues; `requested_changes` must be concrete.
- `blocked`: chapter cannot proceed without material recovery or step backtrack.

## Required Approval Dimensions
- goal_alignment、score_alignment、position_logic、heading_structure、body_priority_coverage、evidence_support、length_budget、terminology_consistency、pending_items_handling
- Allowed statuses for a closed dimension: `pass`, `fail`, `not_applicable`.
- These dimensions must not remain `pending` once a non-pending verdict is issued.

## Chapter-Specific Gates
- Evidence required for this chapter: no
- Suggested word budget: 600-1000
- If the length gate fails, `approved` is invalid.
- If required dimensions are left pending, `approved` is invalid.

## Field Contract
- `latest_verdict`: approved / revise / blocked
- `verdict_rationale`: concise reason for the verdict
- `blocking_reason_category`: required for blocked, otherwise keep empty
- `return_to_step`: fill only when a backtrack step is necessary
- `audit_dimensions`: one object per dimension with explicit status and notes
- `missing_materials_gate`: summarize whether missing inputs prevent a valid chapter
- `primary_failures`: normalized failure labels, not long prose paragraphs
- `required_revision_categories`: normalized categories that agent2 can act on
- `requested_changes`: actionable revision items with short summaries
- `approved_for_next_chapter`: true only when verdict is approved and gates are closed

## Anti-Patterns
- Do not copy phrasing from this file into正文.
- Do not leave key dimensions at `pending` after making a verdict.
- Do not write generic requested changes such as “优化文风” without a concrete target.
- Do not mark evidence support as passed merely because sources were mentioned.

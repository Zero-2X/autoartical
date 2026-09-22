# Step 3 Prompt: Selection Gate

目标：

- 形成供人工拍板的选题包

你需要：

1. 汇总所有候选 idea 的优劣。
2. 给出推荐排序，但不自动替代人工决定。
3. 生成 `selection-package.md`：
   - 候选摘要
   - 推荐顺序
   - 推荐理由
   - 淘汰理由
4. 生成 `selected-idea.json`：
   - 若未确认，则状态为 `pending_human_selection`
   - 若人工已确认，则记录 `selected_id`

要求：

- 明确保留人工 gate
- 不允许“默认选择最高分 idea”

## Prompt Contract Addendum


Task: Complete only the current step task. Do not skip the human gate, do not rewrite unrelated steps, and do not invent missing competition requirements.


Outputs: Write the exact files requested by this prompt or runner. Preserve the declared JSON/Markdown shape, stable keys, and resume-friendly paths so later steps can consume the output without chat context.

Quality gate: The output must be judge-facing, evidence-aware, reproducible, and specific to the selected topic. Prefer concrete pain points, solution logic, technical route, innovation, value, risks, and next actions over generic positive language.

Forbidden: Do not fabricate citations, scores, deadlines, datasets, performance numbers, policies, screenshots, images, or user decisions. Do not leave placeholders, unreplaced variables, TODOs, or meta-writing such as "this section should" in final-facing artifacts.

Evidence rules: Every factual claim that affects scoring, feasibility, policy background, market need, technical performance, or comparison must be traceable to an evidence item, source file, or explicit pending-confirmation note. Low-confidence evidence must be labeled as a risk, not written as a hard conclusion.

Failure handling: If required input is missing, contradictory, or too weak for a hard claim, stop with a blocked status or write a pending-confirmation item instead of guessing. If the step supports retry or regenerate, describe the failed check and the smallest required revision.

Self check checklist:
- Role and task match the current step.
- Inputs were read from files, not assumed from memory.
- Outputs use the expected filenames and schema.
- Evidence references are valid or uncertainty is marked.
- No forbidden placeholders, fake facts, or hidden human decisions remain.
- The artifact can be consumed by the next step with `--resume`.

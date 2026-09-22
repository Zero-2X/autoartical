# Step 0 Prompt: Topic Intake

目标：

- 建立 topic 工作区
- 列出当前已提供和缺失的输入资产

你需要：

2. 生成 `topic-brief.md`：
   - topic 名称
   - 当前已知文件
   - 当前缺失文件
   - 预计工作链路
3. 生成 `topic-assets.json`：
   - `rules`
   - `references`
   - `samples`
   - `outputs_present`
   - `missing_inputs`

验收：

- 文件分类准确
- 缺失项明确
- 不做内容推断

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

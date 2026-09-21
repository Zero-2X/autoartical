# Step 1 Prompt: Rule Parse

目标：

- 将比赛章程转换为稳定、可消费的约束对象

你需要从比赛细则中提取：

- 比赛名称
- 赛道
- 报名或提交时间
- 作品书形式要求
- 必填章节
- 字数或页数限制
- 评分维度
- 加分点
- 禁写项或违规点
- 未明确但高度相关的待确认项

输出：

- `competition-spec.json`
- `rule-summary.md`

要求：

- 明确区分“细则原文可确认”和“推断待确认”
- 评分维度要逐条拆开
- 如果模板要求缺失，要写入待确认项

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

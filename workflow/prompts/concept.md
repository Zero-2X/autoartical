# Step 4 Prompt: Idea Brief

目标：

- 将选中的 candidate idea 扩展为正式察言文件

你需要：

1. 基于选中 idea 写出一份完整察言。
2. 察言至少包含：
   - 项目背景
   - 问题痛点
   - 核心方案
   - 关键创新
   - 技术架构
   - 应用场景
   - 落地价值
3. 再反向抽取为 `idea-card.json`。
4. `step4` 必须消费 `innovation_evidence_map`，让每个创新块都能说明自己的依据。

输出：

- `Idea_*.md`
- `idea-card.json`

要求：

- 察言要可独立阅读
- 察言的语言要尽量接近正式项目察言，而不是把结构化字段直接拼接成句子
- `idea-card.json` 不能遗漏核心信息

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

# Step 2 Prompt: Idea Generation

目标：

- 基于 topic、比赛要求和证据台账生成多个候选 idea

你需要：

1. 先读取 `evidence-ledger.json`，不要跳过证据层。
2. 生成不少于 3 个候选 idea。
3. 每个 idea 都要包含：
   - 项目名称
   - 问题定义
   - 目标用户
   - 方案概述
   - 关键创新点
   - 技术可行性
   - 商业/应用价值
   - 风险点
   - 对应评分维度
   - `evidence_refs`
   - `analysis_basis`
   - `innovation_evidence_map`
   - `template_alignment`
   - `inference_notes`
   - `similar_registry_hits`
4. 对每个 idea 做评分：
   - 创新性
   - 可行性
   - 匹配度
   - 展示潜力

输出：

- `evidence-ledger.json`
- `evidence-summary.md`
- `idea-batch.md`
- `idea-scorecard.json`

要求：

- 候选方案必须有明显差异
- 不允许只换名字和措辞
- 每个 idea 必须能解释“为什么适合这个比赛”
- 每个核心判断都要能回溯到证据项
- 每个创新块都要绑定对应证据，而不是只给整案一个总证据池
- 缺乏直接证据支撑的部分要写成 inference，而不是写成事实
- 每个 idea 都应参考 `sample/topic_xx/Idea_察言 · 多模态短视频舆情风险势能监测系.md` 的表达骨架，至少输出：
  - 开场总述
  - 盲区列表
  - 3-4 个创新块
  - 落地与价值收口

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

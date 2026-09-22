# Step 5 Prompt: Proposal Outline

目标：

- 基于比赛规则和察言规划作品书大纲
- 优先复用 `works_book_writing_skill.md` 中沉淀的作品书写作 Skill，而不是每次从零临时发明章节逻辑

你需要：

1. 生成作品书章节结构。
2. 为每章指定：
   - 章节目标
   - 叙事角色
   - 位置逻辑
   - 章节轻重原因
   - 前置章节 / 后续章节关系
   - 对应评分点
   - 参考样例中的对应章节逻辑
   - 建议页幅 / 建议字数
   - 建议小节
   - 正文优先内容
   - 图表优先内容
   - 可转附录内容
   - 关键写作信息
   - 应包含的信息
   - 创新点闭环锚点
   - 可引用证据 / 证据映射
   - 建议图表或展示元素
   - 常见错误
   - 风险提醒
   - 缺失材料与回溯建议
3. 生成评分覆盖映射。
4. 让 `section-plan.json` 直接可被 Step6 的 `agent1 / agent2 / agent3` 逐章写作流消费。
5. 为每一章同时生成可执行的目录结构硬约束：这一章必须有哪些二级标题、每个二级标题下至少有哪些三级标题、总数最低要求是什么。

输出：

- `outline.md`
- `section-plan.json`
- `score-coverage.json`
- `reference-template.md`

要求：

- 每个关键评分点都要被章节承接
- 不能只有章节标题，没有写作意图
- 目录不是软建议。必须同时生成可执行 gate；若某章二级/三级目录数量或标题不达标，应判定为需要重新编排。
- 要优先复用 `idea-card.json` 中的结构化字段，而不是重新发散新方向
- 创新点、技术架构和应用价值需要分别落到不同章节里，避免全部挤在同一章
- 生成作品书大纲前，必须先参考 `works_book_writing_skill.md`；该 Skill 已从 `sample/topic_xx/作品书_SafeSpeech+.pdf` 中抽象出可复用的结构模板、论证逻辑、图表规则与缺失材料追问规则

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

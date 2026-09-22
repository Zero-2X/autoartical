# 正文撰写

先读取 `workflow/references/content-depth.md` 与章节计划中的 `content_contract`。40–50 页必须由足量、精练、可核验的正文自然构成；按有效正文预算补足论证、机制、实现与验证，不得用排版、复述、背景套话或虚构事实扩充。逐段核对新增信息与证据，缺材料先补材料。字数达标后仍须完成实质审查和正式版式核验。

目标：

- 用真实 LLM 多 agent 逐章推进作品书草稿

你需要：

1. 启动 `agent1` / `agent2` / `agent3` 三个真实 LLM 角色，默认 backbone 为 `gpt-5.4` 且 `reasoning_effort=high`。
2. `agent1` 负责总体监督、章节解锁、任务下派和进入下一章的裁决。
3. `agent2` 只负责当前解锁章节的正文撰写或修订，禁止一次性写完整本作品书。
4. `agent3` 在每章写完后进行审计，必要时要求矫正，并在 `decision.json` 中明确 `approved / revise / blocked`。
4.1 `agent3` 的 `decision.json` 不能只给总 verdict；关键 `audit_dimensions` 必须显式填成 `pass / fail / not_applicable`，不能长期停留在 `pending`。
5. 每章通过后，才能进入下一章；`作品书草稿.md` 只能汇编已通过章节。
6. 先参考 `reference-template.md` 和 `section-plan.json.reference_template` 中的样例结构、篇幅与章节轻重分布。
7. 同时参考 `works_book_writing_skill.md`，按其中的章节目的、位置逻辑、创新点闭环、图表配置和自检规则逐章推进。

输出：

- `agent-runtime.json`
- `chapter-manifest.json`
- `chapters/*/{brief,draft,audit,decision}.md|json`
- `review-log.md`
- `action-ledger.json`
- `作品书草稿.md`（仅汇编已通过章节）

要求：

- 所有 agent 必须是真实 LLM，禁止用固定模板文案冒充 agent 输出
- 不能出现明显重复段落
- 不能使用空泛口号替代具体内容
- 每章必须对评分点有实质支撑
- 页幅和字数建议属于模板参考，不是机械配额；但最终成稿应尽量接近样例的章节轻重分布
- 若 `brief.md` 中已给出章节长度硬阈值，则该阈值属于可执行 gate，不再只是建议
- 章节未通过审计前，不得解锁下一章
- 若 `decision.json` 的关键审计维度仍为 `pending`，即使写了 `approved` 也视为未通过
- `works_book_writing_skill.md` 是 Step6 的通用写作规范来源；`brief.md` 应只抽取当前章节真正需要的规则，不要把整份 Skill 原样抄进单章 prompt

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

# Chapter Brief: 六、应用前景与落地价值

## Workflow Contract
- This chapter must be handled by real LLM agents, not deterministic filler text.
- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.
- Agent2 writes this chapter into `workspace\document_writing\chapters\06_s5\draft.md`.
- Agent3 audits the written chapter into `workspace\document_writing\chapters\06_s5\audit.md` and updates `workspace\document_writing\chapters\06_s5\decision.json`.
- Agent3 may consult `workspace\document_writing\chapters\06_s5\decision-schema.md` for field contract only; Agent2 should ignore that file.
- The next chapter stays locked until Agent3 approves this one.

## Chapter Metadata
- Chapter ID: `s5`
- Chapter Type: `body_section`
- Goal: 讲清系统给谁用、在什么情境里用、具体带来什么收益，并兼顾答辩展示价值。
- Narrative Role: 把技术能力翻译成可落地价值，避免作品书后半段只剩技术术语。
- Position Logic: 在已经说明技术与实现之后，本章把能力翻译成场景、动作与收益，回答“为什么真的值得用”。
- Chapter Weight Reason: 平台应用型项目通常会在应用价值上被重点追问，因此本章必须把用户、流程、收益和展示价值说具体。
- Work Type: 平台应用型
- Matched Scores: 应用价值、讲解表现
- Sample Reference: 第一章 作品概述 / 先讲为什么做，再讲别人做到哪、现有缺口是什么，最后收束到本项目特色与应用前景。
- Suggested Length: 4p / 1110-1500

## Section Dependencies
- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。
- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。
- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。
- Previous: 五、测试与效果分析
- Next: 七、总结与展望

## Body Priorities
- 典型场景
- 用户动作
- 收益闭环
- 展示价值

## Visual Priorities
- 场景矩阵图
- 部署流程图
- 价值闭环图

## Visual Specs
- [表6-1] 应用场景矩阵 | type=table | purpose=说明典型场景、目标用户或应用覆盖范围。 | anchor=目标用户与典型场景 | subsection=目标用户与典型场景 | required=True
  - Reference Hint: 建议在正文中使用“如表6-1所示”或“表6-1显示”来引用该表。
- [表6-2] 角色-动作-收益表 | type=table | purpose=部署流程图 | anchor=目标用户与典型场景 | subsection=目标用户与典型场景 | required=True
  - Reference Hint: 建议在正文中使用“如表6-2所示”或“表6-2显示”来引用该表。
- [图6-3] 预警工单联动流程图 | type=figure | purpose=说明系统运行步骤、数据流向或业务闭环。 | anchor=业务收益与竞争优势 | subsection=业务收益与竞争优势 | required=True
  - Reference Hint: 建议在正文中使用“如图6-3所示”或“图6-3显示”来引用该图。
- [图6-4] 价值闭环图 | type=figure | purpose=说明系统运行步骤、数据流向或业务闭环。 | anchor=业务收益与竞争优势 | subsection=业务收益与竞争优势 | required=True
  - Reference Hint: 建议在正文中使用“如图6-4所示”或“图6-4显示”来引用该图。
- [图6-5] 竞赛答辩演示界面板 | type=figure | purpose=价值闭环图 | anchor=比赛展示价值 | subsection=比赛展示价值 | required=True
  - Reference Hint: 建议在正文中使用“如图6-5所示”或“图6-5显示”来引用该图。

## Length Gate
- Target Budget: 1110-1500
- Minimum Pass Threshold: 1110 (100% of lower bound 1110)
- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.
- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.

## Must Include
- 灾害区域新目标快速检索
- 港口与机场设施巡查
- 农业与生态目标变化监测
- 减少新增类别的全量标注依赖
- 把开放词汇结果转成带来源、查询和置信度的审计证据
- 适合用词汇输入、遥感图像、检测框和案例回放进行比赛演示

## Key Messages
- 应用场景聚焦 灾害区域新目标快速检索、港口与机场设施巡查、农业与生态目标变化监测，每类用户都需要对应一条清晰的使用动作。
- 减少新增类别的全量标注依赖
- 把开放词汇结果转成带来源、查询和置信度的审计证据
- 适合用词汇输入、遥感图像、检测框和案例回放进行比赛演示

## Linked Innovations
- none

## Linked Architecture
- none

## Subsections
- 目标用户与典型场景
- 业务收益与竞争优势
- 比赛展示价值

## Structure Gate
- Required H3 Count: 3
- Required H3 Titles: 目标用户与典型场景、业务收益与竞争优势、比赛展示价值
- Required H4 Total Min: 9
- `目标用户与典型场景` -> required H4 count=3; required titles=目标对象、典型动作、场景约束
- `业务收益与竞争优势` -> required H4 count=3; required titles=收益路径、资源效率、竞争优势
- `比赛展示价值` -> required H4 count=3; required titles=展示主线、多端呈现、演示价值

## Markdown Structure Contract
- This chapter must not remain a single flat prose block.
- Writer must emit each planned subsection as an H3 heading in `draft.md`, using the exact titles below.
- Under each H3 subsection, add 1-3 H4 headings that answer concrete questions inside that subsection.
- Planned visuals must be cited inside the matching subsection body, not dumped at the chapter start or end.
- Required H3: `### 目标用户与典型场景`
- Suggested H4 under `目标用户与典型场景`: 目标对象 / 典型动作 / 场景约束
- Required H3: `### 业务收益与竞争优势`
- Suggested H4 under `业务收益与竞争优势`: 收益路径 / 资源效率 / 竞争优势
- Required H3: `### 比赛展示价值`
- Suggested H4 under `比赛展示价值`: 展示主线 / 多端呈现 / 答辩价值

## Innovation Loop Map
- none

## Evidence Contract
- Evidence Requirement: required | status=strong | count=3 | authoritative=2 | high_reliability=2
- Agent2 must translate evidence into chapter-level论证，不允许只堆 source 名称；每个亮点至少落到“问题来源 / 现有不足 / 本作品做法 / 预期价值”中的 2 个环节。
- Agent3 must check whether the chapter really absorbed the evidence-derived insights, instead of only repeating generic claims.
- Suggested Evidence Anchors: 评分维度对齐、章节权重分配、交付形式设计、答辩展示结构
- Available Evidence Types: scoring_rule、submission_requirement
- Source Authorities: competition_official

## Supporting Evidence
- [ev_84bd681099] 评分标准决定后续 idea 叙事和作品书结构取舍。 | kind=scoring_rule | authority=competition_official | reliability=high | supports=评分维度对齐、章节权重分配 | source=competition-rules.md
- [ev_9ca3b5c76b] 交付要求会反向约束系统展示方式和 record 结构。 | kind=submission_requirement | authority=competition_official | reliability=high | supports=交付形式设计、答辩展示结构 | source=competition-rules.md
- [ev_c00e228bb3]  | kind=unknown | authority=unknown | reliability=unknown | supports=none | source=unknown

## Pending Confirmations
- none

## Missing Materials
- 灾害区域新目标快速检索 | impact=六、应用前景与落地价值 | why=应用章节必须说明给谁用、怎么用、用了以后有什么变化。 | priority=medium | backtrack=step4 | substitute=至少给出 2-3 个典型角色及其使用动作链。
- 港口与机场设施巡查 | impact=六、应用前景与落地价值 | why=应用章节必须说明给谁用、怎么用、用了以后有什么变化。 | priority=medium | backtrack=step4 | substitute=至少给出 2-3 个典型角色及其使用动作链。
- 农业与生态目标变化监测 | impact=六、应用前景与落地价值 | why=应用章节必须说明给谁用、怎么用、用了以后有什么变化。 | priority=medium | backtrack=step4 | substitute=至少给出 2-3 个典型角色及其使用动作链。
- 减少新增类别的全量标注依赖 | impact=六、应用前景与落地价值 | why=应用章节必须说明给谁用、怎么用、用了以后有什么变化。 | priority=medium | backtrack=step4 | substitute=至少给出 2-3 个典型角色及其使用动作链。
- 把开放词汇结果转成带来源、查询和置信度的审计证据 | impact=六、应用前景与落地价值 | why=应用章节必须说明给谁用、怎么用、用了以后有什么变化。 | priority=medium | backtrack=step4 | substitute=至少给出 2-3 个典型角色及其使用动作链。
- 适合用词汇输入、遥感图像、检测框和案例回放进行比赛演示 | impact=六、应用前景与落地价值 | why=应用章节必须说明给谁用、怎么用、用了以后有什么变化。 | priority=medium | backtrack=step4 | substitute=至少给出 2-3 个典型角色及其使用动作链。

## Approved Upstream Context
- 一、作品概述与问题定义: `workspace\document_writing\chapters\01_s1\draft.md`
- 二、作品设计与总体架构: `workspace\document_writing\chapters\02_s2\draft.md`
- 三、核心创新与关键技术: `workspace\document_writing\chapters\03_s3\draft.md`
- 四、作品实现与运行闭环: `workspace\document_writing\chapters\04_s4\draft.md`
- 五、测试与效果分析: `workspace\document_writing\chapters\05_s_validation\draft.md`

## Writing Rules
- Do not rewrite already approved chapters.
- Do not repeat the chapter heading inside `draft.md`; write body content only.
- Write as a competition works book final draft, not as a proposal, roadmap, or writing note.
- Avoid meta-writing phrases such as `本章建议`、`本节重点是`、`下文将`、`建议在正文中使用`.
- Prefer stating the work itself, the mechanism, and the evidence directly; do not explain how the chapter should be written.
- Body chapters must output explicit Markdown hierarchy with `###` subsection headings and, where helpful, `####` detail headings.
- Use the Step5 reference template as a proportional guide, not a rigid quota.
- Keep project name, innovation names, and module names consistent with previous approved chapters.
- Any uncertain claim must stay conditional or be explicitly described as not yet finalized; never emit raw workflow markers such as `pending`.
- For each required visual spec, the正文 should either explicitly reference the planned visual with phrasing such as `如图X所示` / `表X显示` or explain why the visual asset is temporarily unavailable.
- Visual references should appear near the paragraph where the claim is made; do not front-load all figures at the chapter opening.
- If a hard length gate exists for this chapter, falling below it should trigger revise instead of approve.
- The first sentence under each H4 should state a work fact directly: object / mechanism / output / value. Do not open with chapter-planning phrases.
- Every subsection should answer at least two concrete questions from this set: what is the input, how is it processed, what is the output, why does it matter.
- Common errors for this chapter: 应用场景只有名词没有流程；价值只有口号没有收益路径；把商业化愿景当成当前落地能力.
- Appendix candidates for overflow material: 扩展业务流程；成本收益测算假设.

## Forbidden Draft Markers
- Never copy instructional phrases such as `需要把……说透`、`具体写作时`、`如果把这一节放到全书逻辑中观察`、`通过这种写法`、`继续补充`、`进一步落成可执行论证`、`围绕“X”中的“Y”`、`本节用于承接该子问题的进一步说明`.
- Never leave process placeholders, synthetic test notes, or evaluation commentary inside正文.

## Output Contract
- Treat `brief.md` as a constraint sheet, not as reusable prose.
- `draft.md` must read like already-submitted competition prose, not like a writing plan or chapter brief.
- If a sentence can be rewritten from “这一节要说明什么” into “系统实际做了什么”, always choose the latter.

## Agent3 Decision Contract
- `decision.json.latest_verdict` must be exactly one of `approved` / `revise` / `blocked`.
- Once Agent3 outputs a non-pending verdict, required audit dimensions must not stay at `pending`.
- Required pass-or-explicit-NA dimensions before approval: goal_alignment、score_alignment、position_logic、heading_structure、body_priority_coverage、evidence_support、length_budget、terminology_consistency、pending_items_handling.
- `evidence_support` must explicitly judge whether the chapter absorbed the evidence-derived insights rather than only listing source names.
- `length_budget` must be `pass` or `fail`; if the hard threshold is not met, `approved` is invalid.
- `pending_items_handling` must explicitly judge whether uncertain claims stayed conditional and whether missing materials were handled honestly.
- If verdict is `revise`, `requested_changes` must contain concrete, executable items.
- If verdict is `blocked`, `blocking_reason_category` and, when applicable, `return_to_step` must be explicit.

## Acceptance Rule
- Agent3 must either return `approved`, `revise`, or `blocked` in `decision.json`.
- Only after `approved` may Agent1 unlock the next chapter.

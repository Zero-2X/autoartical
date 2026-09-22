# Chapter Brief: 二、作品设计与总体架构

## Workflow Contract
- This chapter must be handled by real LLM agents, not deterministic filler text.
- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.
- Agent2 writes this chapter into `workspace\document_writing\chapters\02_s2\draft.md`.
- Agent3 audits the written chapter into `workspace\document_writing\chapters\02_s2\audit.md` and updates `workspace\document_writing\chapters\02_s2\decision.json`.
- Agent3 may consult `workspace\document_writing\chapters\02_s2\decision-schema.md` for field contract only; Agent2 should ignore that file.
- The next chapter stays locked until Agent3 approves this one.

## Chapter Metadata
- Chapter ID: `s2`
- Chapter Type: `body_section`
- Goal: 按作品书成稿口径交代总体设计、系统主线和输入输出闭环，让整体结构先成立，再展开细节。
- Narrative Role: 承上启下，把前文的问题压缩为作品书中的总体设计与总体架构，避免正文长期停留在提案式说明口吻。
- Position Logic: 本章承接问题定义，把前文痛点转成可运行系统的总体设计与总体架构，为后续关键技术和实现流程提供坐标。
- Chapter Weight Reason: 针对平台应用型项目，本章是整部作品书的总图坐标；若总体设计与边界不清，后文技术章节会显得碎片化。
- Work Type: 平台应用型
- Matched Scores: 创意、技术方案及其实现质量、讲解表现
- Sample Reference: 第二章 作品设计与实现 / 先讲产品和界面，再讲系统架构与数据流，最后深入关键技术与工程实现。
- Suggested Length: 6p / 1300-1733

## Section Dependencies
- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。
- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。
- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。
- Previous: 一、作品概述与问题定义
- Next: 三、核心创新与关键技术
- Next: 四、作品实现与运行闭环

## Body Priorities
- 总体目标与边界
- 输入-处理-输出闭环
- 模块职责
- 人工介入位置

## Visual Priorities
- 总体架构图
- 数据流图
- MVP 边界图

## Visual Specs
- [图2-1] 总体架构图 | type=figure | purpose=说明系统由哪些模块组成，以及模块之间如何协同。 | anchor=总体目标与设计原则 | subsection=总体目标与设计原则 | required=True
  - Reference Hint: 建议在正文中使用“如图2-1所示”或“图2-1显示”来引用该图。
- [图2-2] 模块职责分层图 | type=figure | purpose=说明系统由哪些模块组成，以及模块之间如何协同。 | anchor=系统总体架构 | subsection=系统总体架构 | required=True
  - Reference Hint: 建议在正文中使用“如图2-2所示”或“图2-2显示”来引用该图。
- [图2-3] 输入-处理-输出闭环图 | type=figure | purpose=说明系统运行步骤、数据流向或业务闭环。 | anchor=输入-处理-输出闭环 | subsection=输入-处理-输出闭环 | required=True
  - Reference Hint: 建议在正文中使用“如图2-3所示”或“图2-3显示”来引用该图。
- [图2-4] 多端联动部署图 | type=figure | purpose=部署拓扑图 | anchor=系统总体架构 | subsection=系统总体架构 | required=True
  - Reference Hint: 建议在正文中使用“如图2-4所示”或“图2-4显示”来引用该图。
- [图2-5] 最小可行范围边界图 | type=figure | purpose=说明 MVP 范围、流程路线或待确认事项。 | anchor=输入-处理-输出闭环 | subsection=输入-处理-输出闭环 | required=True
  - Reference Hint: 建议在正文中使用“如图2-5所示”或“图2-5显示”来引用该图。

## Length Gate
- Target Budget: 1300-1733
- Minimum Pass Threshold: 1300 (100% of lower bound 1300)
- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.
- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.

## Must Include
- 构建以文本查询为入口的遥感开放词汇检测系统，先用遥感域视觉语言原型对齐查询，再用多尺度和旋转候选完成定位，最后用类别—区域一致性、背景抑制和温度校准输出带证据的可靠结果。
- 系统输入、核心处理链路、输出结果和人工介入位置。
- MVP 版本优先完成哪些能力，哪些能力属于后续扩展。

## Key Messages
- 构建以文本查询为入口的遥感开放词汇检测系统，先用遥感域视觉语言原型对齐查询，再用多尺度和旋转候选完成定位，最后用类别—区域一致性、背景抑制和温度校准输出带证据的可靠结果。
- 系统链路围绕 遥感影像切片与质量检查、文本词汇与域适配编码、水平/旋转候选检测、可靠性校准与证据回放 展开，先强调闭环，再逐层解释模块。
- 本章必须主动说明 MVP 为何这样划定边界，哪些能力先落地、哪些能力作为后续扩展。

## Linked Innovations
- none

## Linked Architecture
- 遥感影像切片与质量检查
- 文本词汇与域适配编码
- 水平/旋转候选检测
- 可靠性校准与证据回放

## Subsections
- 总体目标与设计原则
- 系统总体架构
- 输入-处理-输出闭环

## Structure Gate
- Required H3 Count: 3
- Required H3 Titles: 总体目标与设计原则、系统总体架构、输入-处理-输出闭环
- Required H4 Total Min: 9
- `总体目标与设计原则` -> required H4 count=3; required titles=设计目标、方案边界、设计原则
- `系统总体架构` -> required H4 count=3; required titles=分层结构、模块职责、多端部署关系
- `输入-处理-输出闭环` -> required H4 count=3; required titles=输入接入、分析与评分、输出与联动

## Markdown Structure Contract
- This chapter must not remain a single flat prose block.
- Writer must emit each planned subsection as an H3 heading in `draft.md`, using the exact titles below.
- Under each H3 subsection, add 1-3 H4 headings that answer concrete questions inside that subsection.
- Planned visuals must be cited inside the matching subsection body, not dumped at the chapter start or end.
- Required H3: `### 总体目标与设计原则`
- Suggested H4 under `总体目标与设计原则`: 设计目标 / 方案边界 / 设计原则
- Required H3: `### 系统总体架构`
- Suggested H4 under `系统总体架构`: 分层结构 / 模块职责 / 多端部署关系
- Required H3: `### 输入-处理-输出闭环`
- Suggested H4 under `输入-处理-输出闭环`: 输入接入 / 分析与评分 / 输出与联动

## Innovation Loop Map
- none

## Evidence Contract
- Evidence Requirement: required | status=strong | count=6 | authoritative=5 | high_reliability=5
- Agent2 must translate evidence into chapter-level论证，不允许只堆 source 名称；每个亮点至少落到“问题来源 / 现有不足 / 本作品做法 / 预期价值”中的 2 个环节。
- Agent3 must check whether the chapter really absorbed the evidence-derived insights, instead of only repeating generic claims.
- Suggested Evidence Anchors: 遥感检测多样性、benchmark 选择、域偏移、旋转目标、定位指标、航空影像挑战、细粒度类别、有向检测、语义混淆、评分维度对齐、章节权重分配、交付形式设计、答辩展示结构
- Available Evidence Types: dataset_signal、scoring_rule、submission_requirement
- Source Authorities: academic、competition_official

## Supporting Evidence
- [ev_d827045531] 使用 DIOR 作为水平框和跨域开放词汇评测入口，并显式冻结 base/novel 划分。 | kind=dataset_signal | authority=academic | reliability=high | supports=遥感检测多样性、benchmark 选择、域偏移 | source=external_evidence\external-evidence-intake.json
- [ev_7f9521c71a] 主实验同时报告水平框与旋转框结果，避免类别命中掩盖定位退化。 | kind=dataset_signal | authority=academic | reliability=high | supports=旋转目标、定位指标、航空影像挑战 | source=external_evidence\external-evidence-intake.json
- [ev_9662694342] 把细粒度混淆、类别层级和提示词稳定性纳入错误分析。 | kind=dataset_signal | authority=academic | reliability=high | supports=细粒度类别、有向检测、语义混淆 | source=external_evidence\external-evidence-intake.json
- [ev_84bd681099] 评分标准决定后续 idea 叙事和作品书结构取舍。 | kind=scoring_rule | authority=competition_official | reliability=high | supports=评分维度对齐、章节权重分配 | source=competition-rules.md
- [ev_9ca3b5c76b] 交付要求会反向约束系统展示方式和 record 结构。 | kind=submission_requirement | authority=competition_official | reliability=high | supports=交付形式设计、答辩展示结构 | source=competition-rules.md
- [ev_c00e228bb3]  | kind=unknown | authority=unknown | reliability=unknown | supports=none | source=unknown

## Pending Confirmations
- none

## Missing Materials
- 开放词汇能力可能被提示词选择放大，需要冻结查询模板并做同义改写测试 | impact=二、作品设计与总体架构 | why=这些问题会影响系统边界、模块职责和 MVP 范围定义。 | priority=high | backtrack=step4 | substitute=在本章显式写明假设条件与暂不覆盖范围。
- 公开数据与真实区域存在域差异，必须保留跨区域外测和人工复核边界 | impact=二、作品设计与总体架构 | why=这些问题会影响系统边界、模块职责和 MVP 范围定义。 | priority=high | backtrack=step4 | substitute=在本章显式写明假设条件与暂不覆盖范围。
- YOLO-World 等组件的许可证需要在发布前核验 | impact=二、作品设计与总体架构 | why=这些问题会影响系统边界、模块职责和 MVP 范围定义。 | priority=high | backtrack=step4 | substitute=在本章显式写明假设条件与暂不覆盖范围。

## Approved Upstream Context
- 一、作品概述与问题定义: `workspace\document_writing\chapters\01_s1\draft.md`

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
- Common errors for this chapter: 只有总框图，没有输入输出闭环；没有说明 MVP 范围；把未来扩展能力写成当前已有能力.
- Appendix candidates for overflow material: 模块接口字段表；非核心扩展能力清单.

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

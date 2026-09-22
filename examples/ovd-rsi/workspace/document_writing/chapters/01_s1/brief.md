# Chapter Brief: 一、作品概述与问题定义

## Workflow Contract
- This chapter must be handled by real LLM agents, not deterministic filler text.
- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.
- Agent2 writes this chapter into `workspace\document_writing\chapters\01_s1\draft.md`.
- Agent3 audits the written chapter into `workspace\document_writing\chapters\01_s1\audit.md` and updates `workspace\document_writing\chapters\01_s1\decision.json`.
- Agent3 may consult `workspace\document_writing\chapters\01_s1\decision-schema.md` for field contract only; Agent2 should ignore that file.
- The next chapter stays locked until Agent3 approves this one.

## Chapter Metadata
- Chapter ID: `s1`
- Chapter Type: `body_section`
- Goal: 讲清赛题背景、业务痛点、目标用户和项目切入问题，先把“为什么值得做”说透。
- Narrative Role: 用真实业务矛盾把项目拉进评委视野，避免作品书一开始就陷入模型堆砌。
- Position Logic: 作为首个正文主体章节，本章必须先建立问题、对象和必要性，才能让后续总体方案与技术细节显得顺理成章。
- Chapter Weight Reason: 当前项目判定为平台应用型，本章需要承担问题立论与用户场景落地职责，避免作品书一上来就堆技术名词。
- Work Type: 平台应用型
- Matched Scores: 创意、应用价值
- Sample Reference: 第一章 作品概述 / 先讲为什么做，再讲别人做到哪、现有缺口是什么，最后收束到本项目特色与应用前景。
- Suggested Length: 4p / 1800-2400

## Section Dependencies
- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。
- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。
- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。
- Previous: none
- Next: 二、作品设计与总体架构

## Body Priorities
- 问题紧迫性
- 目标用户与使用动作
- 现有流程代价
- 项目切入必要性

## Visual Priorities
- 背景趋势图
- 问题链路图
- 用户-痛点对应表

## Visual Specs
- [图1-1] 问题场景图 | type=figure | purpose=说明典型场景、目标用户或应用覆盖范围。 | anchor=背景与赛题价值 | subsection=背景与赛题价值 | required=True
  - Reference Hint: 建议在正文中使用“如图1-1所示”或“图1-1显示”来引用该图。
- [图1-2] 背景趋势图 | type=figure | purpose=支撑背景趋势、需求演进或问题紧迫性的论证。 | anchor=背景与赛题价值 | subsection=背景与赛题价值 | required=True
  - Reference Hint: 建议在正文中使用“如图1-2所示”或“图1-2显示”来引用该图。
- [表1-3] 目标用户与痛点对应表 | type=table | purpose=用户-痛点对应表 | anchor=目标用户与问题场景 | subsection=目标用户与问题场景 | required=True
  - Reference Hint: 建议在正文中使用“如表1-3所示”或“表1-3显示”来引用该表。
- [图1-4] 问题链路图 | type=figure | purpose=问题链路图 | anchor=业务痛点拆解 | subsection=业务痛点拆解 | required=True
  - Reference Hint: 建议在正文中使用“如图1-4所示”或“图1-4显示”来引用该图。

## Length Gate
- Target Budget: 1800-2400
- Minimum Pass Threshold: 1800 (100% of lower bound 1800)
- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.
- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.

## Must Include
- 自然图像开放词汇检测器面对遥感影像中的小目标、旋转目标、密集排列和细粒度类别时，容易出现语义命中但定位错误、类别幻觉和置信度失真；新增类别还需要重新标注和训练，限制了地球观测系统的响应速度。
- 自然图像开放词汇检测器面对遥感影像中的小目标、旋转目标、密集排列和细粒度类别时，容易出现语义命中但定位错误、类别幻觉和置信度失真；新增类别还需要重新标注和训练，限制了地球观测系统的响应速度
- 自然图像语义空间与遥感俯视影像之间存在明显域差异
- 小目标、旋转目标和密集目标同时造成定位与类别匹配困难
- 目标用户为什么会在当前流程中持续承受漏检、误判和响应迟缓成本。

## Key Messages
- 遥感开放词汇检测真正要解决的不是把更多类别名称放进模型，而是让用户能够用新词汇查询目标，同时知道结果是否定位正确、是否存在类别幻觉以及哪些结果需要人工复核。
- 核心用户聚焦 自然资源与生态监测部门、应急遥感解译团队、遥感数据服务企业，项目要解决的关键问题是：自然图像开放词汇检测器面对遥感影像中的小目标、旋转目标、密集排列和细粒度类别时，容易出现语义命中但定位错误、类别幻觉和置信度失真；新增类别还需要重新标注和训练，限制了地球观测系统的响应速度。
- 本章需要把“识别盲区”和“处置低效”两类问题同时讲清，给后文方案设计留足必要性。

## Linked Innovations
- none

## Linked Architecture
- none

## Subsections
- 背景与赛题价值
- 目标用户与问题场景
- 业务痛点拆解

## Structure Gate
- Required H3 Count: 3
- Required H3 Titles: 背景与赛题价值、目标用户与问题场景、业务痛点拆解
- Required H4 Total Min: 9
- `背景与赛题价值` -> required H4 count=3; required titles=现实背景、趋势与赛题牵引、问题演进
- `目标用户与问题场景` -> required H4 count=3; required titles=目标对象、典型动作、场景约束
- `业务痛点拆解` -> required H4 count=3; required titles=现有不足、风险放大链路、直接代价

## Markdown Structure Contract
- This chapter must not remain a single flat prose block.
- Writer must emit each planned subsection as an H3 heading in `draft.md`, using the exact titles below.
- Under each H3 subsection, add 1-3 H4 headings that answer concrete questions inside that subsection.
- Planned visuals must be cited inside the matching subsection body, not dumped at the chapter start or end.
- Required H3: `### 背景与赛题价值`
- Suggested H4 under `背景与赛题价值`: 现实背景 / 趋势与赛题牵引 / 问题演进
- Required H3: `### 目标用户与问题场景`
- Suggested H4 under `目标用户与问题场景`: 目标对象 / 典型动作 / 场景约束
- Required H3: `### 业务痛点拆解`
- Suggested H4 under `业务痛点拆解`: 现有不足 / 风险放大链路 / 直接代价

## Innovation Loop Map
- none

## Evidence Contract
- Evidence Requirement: required | status=strong | count=4 | authoritative=4 | high_reliability=4
- Agent2 must translate evidence into chapter-level论证，不允许只堆 source 名称；每个亮点至少落到“问题来源 / 现有不足 / 本作品做法 / 预期价值”中的 2 个环节。
- Agent3 must check whether the chapter really absorbed the evidence-derived insights, instead of only repeating generic claims.
- Suggested Evidence Anchors: 遥感检测多样性、benchmark 选择、域偏移、旋转目标、定位指标、航空影像挑战、评分维度对齐、章节权重分配、交付形式设计、答辩展示结构
- Available Evidence Types: dataset_signal、scoring_rule、submission_requirement
- Source Authorities: academic、competition_official

## Supporting Evidence
- [ev_d827045531] 使用 DIOR 作为水平框和跨域开放词汇评测入口，并显式冻结 base/novel 划分。 | kind=dataset_signal | authority=academic | reliability=high | supports=遥感检测多样性、benchmark 选择、域偏移 | source=external_evidence\external-evidence-intake.json
- [ev_7f9521c71a] 主实验同时报告水平框与旋转框结果，避免类别命中掩盖定位退化。 | kind=dataset_signal | authority=academic | reliability=high | supports=旋转目标、定位指标、航空影像挑战 | source=external_evidence\external-evidence-intake.json
- [ev_84bd681099] 评分标准决定后续 idea 叙事和作品书结构取舍。 | kind=scoring_rule | authority=competition_official | reliability=high | supports=评分维度对齐、章节权重分配 | source=competition-rules.md
- [ev_9ca3b5c76b] 交付要求会反向约束系统展示方式和 record 结构。 | kind=submission_requirement | authority=competition_official | reliability=high | supports=交付形式设计、答辩展示结构 | source=competition-rules.md

## Pending Confirmations
- 当前章程未给出作品书具体章节模板，需要补充命题文件或文档格式要求。
- 当前 topic 的具体赛道 / 命题方向尚未从章程中唯一确定，需要结合命题文件确认。
- 当前章程未明确作品书字数或页数限制，需要补充模板文件确认。

## Missing Materials
- 当前章程未给出作品书具体章节模板，需要补充命题文件或文档格式要求。 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- 当前 topic 的具体赛道 / 命题方向尚未从章程中唯一确定，需要结合命题文件确认。 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- 当前章程未明确作品书字数或页数限制，需要补充模板文件确认。 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- 开放词汇能力可能被提示词选择放大，需要冻结查询模板并做同义改写测试 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- 公开数据与真实区域存在域差异，必须保留跨区域外测和人工复核边界 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- YOLO-World 等组件的许可证需要在发布前核验 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。

## Approved Upstream Context
- none

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
- Common errors for this chapter: 背景写成社会议题口号；只有风险描述，没有用户动作；问题没有自然导向后文方案.
- Appendix candidates for overflow material: 补充背景统计口径；扩展案例或法规原文摘录.

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

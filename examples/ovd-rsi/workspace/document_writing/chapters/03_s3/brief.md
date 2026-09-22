# Chapter Brief: 三、核心创新与关键技术

## Workflow Contract
- This chapter must be handled by real LLM agents, not deterministic filler text.
- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.
- Agent2 writes this chapter into `workspace\document_writing\chapters\03_s3\draft.md`.
- Agent3 audits the written chapter into `workspace\document_writing\chapters\03_s3\audit.md` and updates `workspace\document_writing\chapters\03_s3\decision.json`.
- Agent3 may consult `workspace\document_writing\chapters\03_s3\decision-schema.md` for field contract only; Agent2 should ignore that file.
- The next chapter stays locked until Agent3 approves this one.

## Chapter Metadata
- Chapter ID: `s3`
- Chapter Type: `body_section`
- Goal: 把创新点拆成可论证、可对应技术结构的章节，而不是停留在口号式命名。
- Narrative Role: 证明项目不是通用系统的简单拼装，而是围绕 遥感影像开放词汇目标检测 场景中的关键问题做了针对性设计。
- Position Logic: 在总体方案已经建立后，本章负责回答“核心新东西到底是什么、为什么这样设计、落在什么技术抓手上”。
- Chapter Weight Reason: 平台应用型项目的高分通常来自这一章与测试章形成的双重闭环，因此本章应承担创新定义、机制落点与技术解释的主要篇幅。
- Work Type: 平台应用型
- Matched Scores: 创意、技术方案及其实现质量
- Sample Reference: 第二章 作品设计与实现 / 先讲产品和界面，再讲系统架构与数据流，最后深入关键技术与工程实现。
- Suggested Length: 23p / 1450-1933

## Section Dependencies
- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。
- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。
- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。
- Previous: 二、作品设计与总体架构
- Next: 四、作品实现与运行闭环
- Next: 五、测试与效果分析

## Body Priorities
- 创新点与痛点一一对应
- 技术机制解释
- 模块落点
- 与系统结构映射

## Visual Priorities
- 创新点-痛点对照表
- 关键技术分层图
- 原理流程图

## Visual Specs
- [表3-1] 创新点-痛点对照表 | type=table | purpose=对齐痛点、创新点、模块或证据之间的对应关系。 | anchor=创新点总览 | subsection=创新点总览 | required=True
  - Reference Hint: 建议在正文中使用“如表3-1所示”或“表3-1显示”来引用该表。
- [图3-2] 创新一 · 遥感域词汇原型适配示意图 | type=figure | purpose=关键技术分层图 | anchor=创新一 · 遥感域词汇原型适配 | subsection=创新一 · 遥感域词汇原型适配 | required=True
  - Reference Hint: 建议在正文中使用“如图3-2所示”或“图3-2显示”来引用该图。
- [图3-3] 创新二 · 多尺度旋转候选协同示意图 | type=figure | purpose=原理流程图 | anchor=创新二 · 多尺度旋转候选协同 | subsection=创新二 · 多尺度旋转候选协同 | required=True
  - Reference Hint: 建议在正文中使用“如图3-3所示”或“图3-3显示”来引用该图。
- [图3-4] 创新三 · 可靠语义校准示意图 | type=figure | purpose=原理流程图 | anchor=创新三 · 可靠语义校准 | subsection=创新三 · 可靠语义校准 | required=True
  - Reference Hint: 建议在正文中使用“如图3-4所示”或“图3-4显示”来引用该图。
- [图3-5] 关键技术分层图 | type=figure | purpose=说明系统由哪些模块组成，以及模块之间如何协同。 | anchor=创新与技术层映射 | subsection=创新与技术层映射 | required=True
  - Reference Hint: 建议在正文中使用“如图3-5所示”或“图3-5显示”来引用该图。
- [表3-6] 创新模块证据映射表 | type=table | purpose=对齐痛点、创新点、模块或证据之间的对应关系。 | anchor=创新与技术层映射 | subsection=创新与技术层映射 | required=True
  - Reference Hint: 建议在正文中使用“如表3-6所示”或“表3-6显示”来引用该表。

## Length Gate
- Target Budget: 1450-1933
- Minimum Pass Threshold: 1450 (100% of lower bound 1450)
- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.
- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.

## Must Include
- 创新一 · 遥感域词汇原型适配
- 创新二 · 多尺度旋转候选协同
- 创新三 · 可靠语义校准
- 利用遥感图文表示校正通用文本嵌入，使同一类别在俯视尺度、方向和纹理条件下保持稳定语义。
- 将切片、多尺度候选和旋转框定位与文本查询联合优化，降低小目标漏检和方向错配。
- 利用类别—区域一致性、背景对照和温度校准抑制类别幻觉，输出可解释的不确定性和人工复核建议。
- 遥感影像切片与质量检查
- 文本词汇与域适配编码
- 水平/旋转候选检测
- 可靠性校准与证据回放

## Key Messages
- 利用遥感图文表示校正通用文本嵌入，使同一类别在俯视尺度、方向和纹理条件下保持稳定语义。
- 将切片、多尺度候选和旋转框定位与文本查询联合优化，降低小目标漏检和方向错配。
- 利用类别—区域一致性、背景对照和温度校准抑制类别幻觉，输出可解释的不确定性和人工复核建议。
- 创新点必须一一落到识别难题、风险决策或展示联动上，不能和普通功能列表混在一起。

## Linked Innovations
- 创新一 · 遥感域词汇原型适配
- 创新二 · 多尺度旋转候选协同
- 创新三 · 可靠语义校准

## Linked Architecture
- 遥感影像切片与质量检查
- 文本词汇与域适配编码
- 水平/旋转候选检测
- 可靠性校准与证据回放

## Subsections
- 创新点总览
- 创新一 · 遥感域词汇原型适配
- 创新二 · 多尺度旋转候选协同
- 创新三 · 可靠语义校准
- 创新与技术层映射

## Structure Gate
- Required H3 Count: 5
- Required H3 Titles: 创新点总览、创新一 · 遥感域词汇原型适配、创新二 · 多尺度旋转候选协同、创新三 · 可靠语义校准、创新与技术层映射
- Required H4 Total Min: 12
- `创新点总览` -> required H4 count=2; required titles=痛点映射、创新协同
- `创新一 · 遥感域词汇原型适配` -> required H4 count=2; required titles=核心内容、支撑说明
- `创新二 · 多尺度旋转候选协同` -> required H4 count=3; required titles=核心内容、实现方法、支撑说明
- `创新三 · 可靠语义校准` -> required H4 count=2; required titles=核心内容、支撑说明
- `创新与技术层映射` -> required H4 count=3; required titles=技术落点、验证锚点、系统对应关系

## Markdown Structure Contract
- This chapter must not remain a single flat prose block.
- Writer must emit each planned subsection as an H3 heading in `draft.md`, using the exact titles below.
- Under each H3 subsection, add 1-3 H4 headings that answer concrete questions inside that subsection.
- Planned visuals must be cited inside the matching subsection body, not dumped at the chapter start or end.
- Required H3: `### 创新点总览`
- Suggested H4 under `创新点总览`: 痛点映射 / 创新协同
- Required H3: `### 创新一 · 遥感域词汇原型适配`
- Suggested H4 under `创新一 · 遥感域词汇原型适配`: 核心论点 / 支撑分析
- Required H3: `### 创新二 · 多尺度旋转候选协同`
- Suggested H4 under `创新二 · 多尺度旋转候选协同`: 核心论点 / 支撑分析
- Required H3: `### 创新三 · 可靠语义校准`
- Suggested H4 under `创新三 · 可靠语义校准`: 核心论点 / 支撑分析
- Required H3: `### 创新与技术层映射`
- Suggested H4 under `创新与技术层映射`: 技术落点 / 验证锚点 / 系统对应关系

## Innovation Loop Map
- 创新一 · 遥感域词汇原型适配: problem=利用遥感图文表示校正通用文本嵌入，使同一类别在俯视尺度、方向和纹理条件下保持稳定语义。; role=提出本作品做法，并把创新点落到具体模块、机制或工程抓手上。; validation=五、测试与效果分析 / 创新性说明; signal=相对基线的方法改进、消融贡献或系统能力增强; meaning=利用遥感图文表示校正通用文本嵌入，使同一类别在俯视尺度、方向和纹理条件下保持稳定语义。
- 创新二 · 多尺度旋转候选协同: problem=将切片、多尺度候选和旋转框定位与文本查询联合优化，降低小目标漏检和方向错配。; role=提出本作品做法，并把创新点落到具体模块、机制或工程抓手上。; validation=五、测试与效果分析 / 创新性说明; signal=相对基线的方法改进、消融贡献或系统能力增强; meaning=将切片、多尺度候选和旋转框定位与文本查询联合优化，降低小目标漏检和方向错配。
- 创新三 · 可靠语义校准: problem=利用类别—区域一致性、背景对照和温度校准抑制类别幻觉，输出可解释的不确定性和人工复核建议。; role=提出本作品做法，并把创新点落到具体模块、机制或工程抓手上。; validation=五、测试与效果分析 / 创新性说明; signal=相对基线的方法改进、消融贡献或系统能力增强; meaning=利用类别—区域一致性、背景对照和温度校准抑制类别幻觉，输出可解释的不确定性和人工复核建议。

## Evidence Contract
- Evidence Requirement: required | status=strong | count=2 | authoritative=2 | high_reliability=2
- Agent2 must translate evidence into chapter-level论证，不允许只堆 source 名称；每个亮点至少落到“问题来源 / 现有不足 / 本作品做法 / 预期价值”中的 2 个环节。
- Agent3 must check whether the chapter really absorbed the evidence-derived insights, instead of only repeating generic claims.
- Suggested Evidence Anchors: 遥感检测多样性、benchmark 选择、域偏移、旋转目标、定位指标、航空影像挑战
- Available Evidence Types: dataset_signal
- Source Authorities: academic

## Supporting Evidence
- [ev_d827045531] 使用 DIOR 作为水平框和跨域开放词汇评测入口，并显式冻结 base/novel 划分。 | kind=dataset_signal | authority=academic | reliability=high | supports=遥感检测多样性、benchmark 选择、域偏移 | source=external_evidence\external-evidence-intake.json
- [ev_7f9521c71a] 主实验同时报告水平框与旋转框结果，避免类别命中掩盖定位退化。 | kind=dataset_signal | authority=academic | reliability=high | supports=旋转目标、定位指标、航空影像挑战 | source=external_evidence\external-evidence-intake.json

## Pending Confirmations
- none

## Missing Materials
- 创新一 · 遥感域词汇原型适配 | impact=三、核心创新与关键技术 | why=创新章节要求每个创新点都有技术机制、实现落点和后续验证锚点。 | priority=high | backtrack=step4 | substitute=将尚未闭环的条目降级为功能亮点或待实现方向。
- 创新二 · 多尺度旋转候选协同 | impact=三、核心创新与关键技术 | why=创新章节要求每个创新点都有技术机制、实现落点和后续验证锚点。 | priority=high | backtrack=step4 | substitute=将尚未闭环的条目降级为功能亮点或待实现方向。
- 创新三 · 可靠语义校准 | impact=三、核心创新与关键技术 | why=创新章节要求每个创新点都有技术机制、实现落点和后续验证锚点。 | priority=high | backtrack=step4 | substitute=将尚未闭环的条目降级为功能亮点或待实现方向。
- 开放词汇能力可能被提示词选择放大，需要冻结查询模板并做同义改写测试 | impact=三、核心创新与关键技术 | why=创新章节要求每个创新点都有技术机制、实现落点和后续验证锚点。 | priority=high | backtrack=step4 | substitute=将尚未闭环的条目降级为功能亮点或待实现方向。
- 公开数据与真实区域存在域差异，必须保留跨区域外测和人工复核边界 | impact=三、核心创新与关键技术 | why=创新章节要求每个创新点都有技术机制、实现落点和后续验证锚点。 | priority=high | backtrack=step4 | substitute=将尚未闭环的条目降级为功能亮点或待实现方向。
- YOLO-World 等组件的许可证需要在发布前核验 | impact=三、核心创新与关键技术 | why=创新章节要求每个创新点都有技术机制、实现落点和后续验证锚点。 | priority=high | backtrack=step4 | substitute=将尚未闭环的条目降级为功能亮点或待实现方向。

## Approved Upstream Context
- 一、作品概述与问题定义: `workspace\document_writing\chapters\01_s1\draft.md`
- 二、作品设计与总体架构: `workspace\document_writing\chapters\02_s2\draft.md`

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
- Common errors for this chapter: 创新点只有命名没有机制；创新点与实现模块重复叙述；未区分技术亮点和核心创新.
- Appendix candidates for overflow material: 公式推导；扩展模块实现细节；补充伪代码.

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

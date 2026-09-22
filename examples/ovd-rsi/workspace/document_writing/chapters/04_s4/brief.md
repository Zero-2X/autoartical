# Chapter Brief: 四、作品实现与运行闭环

## Workflow Contract
- This chapter must be handled by real LLM agents, not deterministic filler text.
- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.
- Agent2 writes this chapter into `workspace\document_writing\chapters\04_s4\draft.md`.
- Agent3 audits the written chapter into `workspace\document_writing\chapters\04_s4\audit.md` and updates `workspace\document_writing\chapters\04_s4\decision.json`.
- Agent3 may consult `workspace\document_writing\chapters\04_s4\decision-schema.md` for field contract only; Agent2 should ignore that file.
- The next chapter stays locked until Agent3 approves this one.

## Chapter Metadata
- Chapter ID: `s4`
- Chapter Type: `body_section`
- Goal: 把模块如何协同运行、数据如何流转和人工如何介入写具体，建立完成度感。
- Narrative Role: 把抽象方案落到工程链路，回答“这个系统究竟怎么跑起来”。
- Position Logic: 本章位于创新与应用之间，负责把前章的机制变成可运行流程，证明项目不只是概念图和模块名。
- Chapter Weight Reason: 对于平台应用型项目，本章决定评委对完成度的直观判断，尤其影响“实现质量”和“讲解表现”。
- Work Type: 平台应用型
- Matched Scores: 技术方案及其实现质量、讲解表现
- Sample Reference: 第二章 作品设计与实现 / 先讲产品和界面，再讲系统架构与数据流，最后深入关键技术与工程实现。
- Suggested Length: 4p / 2500-3333

## Section Dependencies
- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。
- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。
- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。
- Previous: 二、作品设计与总体架构
- Previous: 三、核心创新与关键技术
- Next: 五、测试与效果分析
- Next: 六、应用前景与落地价值

## Body Priorities
- 模块协同关系
- 运行流程
- 人工复核与回放机制
- 可运行性证明

## Visual Priorities
- 运行流程图
- 时序图
- 界面截图或模块接口表

## Visual Specs
- [表4-1] 统一表征与接入链路图 | type=table | purpose=运行流程图 | anchor=模块实现说明 | subsection=模块实现说明 | required=True
  - Reference Hint: 建议在正文中使用“如表4-1所示”或“表4-1显示”来引用该表。
- [图4-2] 运行流程图 | type=figure | purpose=说明系统运行步骤、数据流向或业务闭环。 | anchor=运行流程 | subsection=运行流程 | required=True
  - Reference Hint: 建议在正文中使用“如图4-2所示”或“图4-2显示”来引用该图。
- [图4-3] 评分与告警链路图 | type=figure | purpose=界面截图或模块接口表 | anchor=运行流程 | subsection=运行流程 | required=True
  - Reference Hint: 建议在正文中使用“如图4-3所示”或“图4-3显示”来引用该图。
- [表4-4] 模块接口表 | type=table | purpose=界面截图或模块接口表 | anchor=模块实现说明 | subsection=模块实现说明 | required=True
  - Reference Hint: 建议在正文中使用“如表4-4所示”或“表4-4显示”来引用该表。
- [图4-5] 案例流转时序图 | type=figure | purpose=说明系统运行步骤、数据流向或业务闭环。 | anchor=案例回放与人工复核 | subsection=案例回放与人工复核 | required=True
  - Reference Hint: 建议在正文中使用“如图4-5所示”或“图4-5显示”来引用该图。
- [图4-6] 多端工作台示意 | type=figure | purpose=界面截图或模块接口表 | anchor=案例回放与人工复核 | subsection=案例回放与人工复核 | required=True
  - Reference Hint: 建议在正文中使用“如图4-6所示”或“图4-6显示”来引用该图。

## Length Gate
- Target Budget: 2500-3333
- Minimum Pass Threshold: 2500 (100% of lower bound 2500)
- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.
- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.

## Must Include
- 多模态数据接入方式和统一表征思路。
- 风险评分与预警生成逻辑。
- 人工复核、案例留痕和展示联动如何进入闭环。
- 可在 Grounding DINO、Detic 或 YOLO-World 上建立可复现实验基线
- DIOR、DOTA、FAIR1M 等公开数据可支撑多协议验证
- 系统先支持离线切片推理，再扩展到实时或边缘部署

## Key Messages
- 系统运行主线是采集、理解、评分、告警、复核，重点说明每一步如何承接前一步结果。
- 可在 Grounding DINO、Detic 或 YOLO-World 上建立可复现实验基线
- DIOR、DOTA、FAIR1M 等公开数据可支撑多协议验证
- 系统先支持离线切片推理，再扩展到实时或边缘部署
- 本章要主动体现作品是可运行 MVP，而不是只有概念框图。

## Linked Innovations
- none

## Linked Architecture
- 遥感影像切片与质量检查
- 文本词汇与域适配编码
- 水平/旋转候选检测
- 可靠性校准与证据回放

## Subsections
- 模块实现说明
- 运行流程
- 案例回放与人工复核

## Structure Gate
- Required H3 Count: 3
- Required H3 Titles: 模块实现说明、运行流程、案例回放与人工复核
- Required H4 Total Min: 9
- `模块实现说明` -> required H4 count=3; required titles=统一表征对象、模块实现、接口协同
- `运行流程` -> required H4 count=3; required titles=输入接入、分析与评分、输出与联动
- `案例回放与人工复核` -> required H4 count=3; required titles=案例回放链路、复核证据面板、复核与留痕

## Markdown Structure Contract
- This chapter must not remain a single flat prose block.
- Writer must emit each planned subsection as an H3 heading in `draft.md`, using the exact titles below.
- Under each H3 subsection, add 1-3 H4 headings that answer concrete questions inside that subsection.
- Planned visuals must be cited inside the matching subsection body, not dumped at the chapter start or end.
- Required H3: `### 模块实现说明`
- Suggested H4 under `模块实现说明`: 统一表征对象 / 模块实现 / 接口协同
- Required H3: `### 运行流程`
- Suggested H4 under `运行流程`: 输入接入 / 分析与评分 / 输出与联动
- Required H3: `### 案例回放与人工复核`
- Suggested H4 under `案例回放与人工复核`: 案例回放链路 / 复核证据面板 / 复核与留痕

## Innovation Loop Map
- 创新一 · 遥感域词汇原型适配: problem=利用遥感图文表示校正通用文本嵌入，使同一类别在俯视尺度、方向和纹理条件下保持稳定语义。; role=把前章创新机制落成运行流程、接口交互和工程实现闭环。; validation=五、测试与效果分析 / 六、应用前景与落地价值; signal=流程可运行、模块可协作、系统可演示; meaning=利用遥感图文表示校正通用文本嵌入，使同一类别在俯视尺度、方向和纹理条件下保持稳定语义。
- 创新二 · 多尺度旋转候选协同: problem=将切片、多尺度候选和旋转框定位与文本查询联合优化，降低小目标漏检和方向错配。; role=把前章创新机制落成运行流程、接口交互和工程实现闭环。; validation=五、测试与效果分析 / 六、应用前景与落地价值; signal=流程可运行、模块可协作、系统可演示; meaning=将切片、多尺度候选和旋转框定位与文本查询联合优化，降低小目标漏检和方向错配。
- 创新三 · 可靠语义校准: problem=利用类别—区域一致性、背景对照和温度校准抑制类别幻觉，输出可解释的不确定性和人工复核建议。; role=把前章创新机制落成运行流程、接口交互和工程实现闭环。; validation=五、测试与效果分析 / 六、应用前景与落地价值; signal=流程可运行、模块可协作、系统可演示; meaning=利用类别—区域一致性、背景对照和温度校准抑制类别幻觉，输出可解释的不确定性和人工复核建议。

## Evidence Contract
- Evidence Requirement: required | status=strong | count=3 | authoritative=3 | high_reliability=3
- Agent2 must translate evidence into chapter-level论证，不允许只堆 source 名称；每个亮点至少落到“问题来源 / 现有不足 / 本作品做法 / 预期价值”中的 2 个环节。
- Agent3 must check whether the chapter really absorbed the evidence-derived insights, instead of only repeating generic claims.
- Suggested Evidence Anchors: 遥感检测多样性、benchmark 选择、域偏移、旋转目标、定位指标、航空影像挑战、细粒度类别、有向检测、语义混淆
- Available Evidence Types: dataset_signal
- Source Authorities: academic

## Supporting Evidence
- [ev_d827045531] 使用 DIOR 作为水平框和跨域开放词汇评测入口，并显式冻结 base/novel 划分。 | kind=dataset_signal | authority=academic | reliability=high | supports=遥感检测多样性、benchmark 选择、域偏移 | source=external_evidence\external-evidence-intake.json
- [ev_7f9521c71a] 主实验同时报告水平框与旋转框结果，避免类别命中掩盖定位退化。 | kind=dataset_signal | authority=academic | reliability=high | supports=旋转目标、定位指标、航空影像挑战 | source=external_evidence\external-evidence-intake.json
- [ev_9662694342] 把细粒度混淆、类别层级和提示词稳定性纳入错误分析。 | kind=dataset_signal | authority=academic | reliability=high | supports=细粒度类别、有向检测、语义混淆 | source=external_evidence\external-evidence-intake.json

## Pending Confirmations
- none

## Missing Materials
- 可在 Grounding DINO、Detic 或 YOLO-World 上建立可复现实验基线 | impact=四、作品实现与运行闭环 | why=实现章节需要明确系统当前能跑到哪一步、哪些能力已具备、哪些仍是规划。 | priority=medium | backtrack=step4 | substitute=用 MVP 范围说明替代完整实现承诺，并标出人工介入位置。
- DIOR、DOTA、FAIR1M 等公开数据可支撑多协议验证 | impact=四、作品实现与运行闭环 | why=实现章节需要明确系统当前能跑到哪一步、哪些能力已具备、哪些仍是规划。 | priority=medium | backtrack=step4 | substitute=用 MVP 范围说明替代完整实现承诺，并标出人工介入位置。
- 系统先支持离线切片推理，再扩展到实时或边缘部署 | impact=四、作品实现与运行闭环 | why=实现章节需要明确系统当前能跑到哪一步、哪些能力已具备、哪些仍是规划。 | priority=medium | backtrack=step4 | substitute=用 MVP 范围说明替代完整实现承诺，并标出人工介入位置。
- 开放词汇能力可能被提示词选择放大，需要冻结查询模板并做同义改写测试 | impact=四、作品实现与运行闭环 | why=实现章节需要明确系统当前能跑到哪一步、哪些能力已具备、哪些仍是规划。 | priority=medium | backtrack=step4 | substitute=用 MVP 范围说明替代完整实现承诺，并标出人工介入位置。
- 公开数据与真实区域存在域差异，必须保留跨区域外测和人工复核边界 | impact=四、作品实现与运行闭环 | why=实现章节需要明确系统当前能跑到哪一步、哪些能力已具备、哪些仍是规划。 | priority=medium | backtrack=step4 | substitute=用 MVP 范围说明替代完整实现承诺，并标出人工介入位置。
- YOLO-World 等组件的许可证需要在发布前核验 | impact=四、作品实现与运行闭环 | why=实现章节需要明确系统当前能跑到哪一步、哪些能力已具备、哪些仍是规划。 | priority=medium | backtrack=step4 | substitute=用 MVP 范围说明替代完整实现承诺，并标出人工介入位置。

## Approved Upstream Context
- 一、作品概述与问题定义: `workspace\document_writing\chapters\01_s1\draft.md`
- 二、作品设计与总体架构: `workspace\document_writing\chapters\02_s2\draft.md`
- 三、核心创新与关键技术: `workspace\document_writing\chapters\03_s3\draft.md`

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
- Common errors for this chapter: 只有模块清单没有流程；流程图与正文不一致；把尚未实现的能力写成已完成功能.
- Appendix candidates for overflow material: 接口协议；详细运行日志；工程参数配置.

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

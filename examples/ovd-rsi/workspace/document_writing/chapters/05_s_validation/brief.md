# Chapter Brief: 五、测试与效果分析

## Workflow Contract
- This chapter must be handled by real LLM agents, not deterministic filler text.
- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.
- Agent2 writes this chapter into `workspace\document_writing\chapters\05_s_validation\draft.md`.
- Agent3 audits the written chapter into `workspace\document_writing\chapters\05_s_validation\audit.md` and updates `workspace\document_writing\chapters\05_s_validation\decision.json`.
- Agent3 may consult `workspace\document_writing\chapters\05_s_validation\decision-schema.md` for field contract only; Agent2 should ignore that file.
- The next chapter stays locked until Agent3 approves this one.

## Chapter Metadata
- Chapter ID: `s_validation`
- Chapter Type: `body_section`
- Goal: 围绕关键性能、对比实验、复杂场景稳定性和系统闭环指标，形成与创新点一一对应的验证链，而不是只在结尾补几条结果。
- Narrative Role: 把前文提出的创新点和系统闭环转成可被评委验证的结果证据，形成“创新提出 - 机制实现 - 效果证明”的完整闭环。
- Position Logic: 本章位于系统实现之后、应用价值之前，负责回答“作品做出来以后到底是否有效、稳定、可运行”。
- Chapter Weight Reason: 平台应用型项目若缺少正式测试章，创新与实现很难转化为可信的评审印象，因此本章必须承担关键证据链的组织任务。
- Work Type: 平台应用型
- Matched Scores: 技术方案及其实现质量、创意、讲解表现
- Sample Reference: 第三章 作品测试与分析 / 先冻结公开基准、base/novel 划分和提示词协议，再按基线对比、旋转定位、可靠性校准、查询稳定性和系统案例展开分析。
- Suggested Length: 4-6p / 4000-5333

## Section Dependencies
- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。
- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。
- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。
- Previous: 三、核心创新与关键技术
- Previous: 四、作品实现与运行闭环
- Next: 六、应用前景与落地价值

## Body Priorities
- 公开基准与 base/novel/generalized 划分
- Grounding DINO、Detic、YOLO-World 和闭集上限对照
- HBB/OBB、小目标与细粒度结果
- ECE、Brier、高置信假阳性和同义查询一致性
- 延迟、显存、证据卡与跨区域外测

## Visual Priorities
- 数据集与 base/novel 划分图
- 方法类别对照表
- HBB/OBB 结果表
- 校准曲线与查询一致性图
- 案例证据卡与延迟面板

## Visual Specs
- [表5-1] 数据来源与规模表 | type=table | purpose=数据集与 base/novel 划分图 | anchor=评测协议与数据划分 | subsection=评测协议与数据划分 | required=True
  - Reference Hint: 建议在正文中使用“如表5-1所示”或“表5-1显示”来引用该表。
- [表5-2] 关键性能汇总表 | type=table | purpose=方法类别对照表 | anchor=Current methods 基线对比 | subsection=Current methods 基线对比 | required=True
  - Reference Hint: 建议在正文中使用“如表5-2所示”或“表5-2显示”来引用该表。
- [表5-3] 对比实验结果表 | type=table | purpose=HBB/OBB 结果表 | anchor=开放类别与旋转定位效果 | subsection=开放类别与旋转定位效果 | required=True
  - Reference Hint: 建议在正文中使用“如表5-3所示”或“表5-3显示”来引用该表。
- [图5-4] 案例回放时序图 | type=figure | purpose=说明系统运行步骤、数据流向或业务闭环。 | anchor=可靠性校准与查询稳定性 | subsection=可靠性校准与查询稳定性 | required=True
  - Reference Hint: 建议在正文中使用“如图5-4所示”或“图5-4显示”来引用该图。
- [表5-5] 系统性能与闭环指标清单 | type=table | purpose=说明系统运行步骤、数据流向或业务闭环。 | anchor=系统延迟与案例证据 | subsection=系统延迟与案例证据 | required=True
  - Reference Hint: 建议在正文中使用“如表5-5所示”或“表5-5显示”来引用该表。

## Length Gate
- Target Budget: 4000-5333
- Minimum Pass Threshold: 4000 (100% of lower bound 4000)
- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.
- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.

## Must Include
- 本章测试采用公开轴承故障数据、仿真工况数据与原型系统运行日志构成的混合验证链。其中，公开数据用于验证基础诊断能力，仿真工况用于验证跨工况与弱故障稳定性，原型日志用于验证时延、告警与工单闭环能力。
- 关键指标汇总与对应含义说明。
- 对比实验设置、结果和结论解释。
- 复杂场景稳定性或跨工况表现说明。
- 系统时延、吞吐、闭环完成率等系统级结果。
- 核心任务完成率
- 关键能力提升幅度
- 系统响应时延
- 闭环完成率
- 基础方案与增强方案对比
- 稳态场景与复杂场景对比
- 结果输出与联动闭环对比

## Key Messages
- 本验证包以 创新一 · 遥感域词汇原型适配、创新二 · 多尺度旋转候选协同、创新三 · 可靠语义校准 为主线，组织公开资料、仿真场景和原型日志三类材料，提供可直接落入作品书的测试结构。
- 本章测试采用公开轴承故障数据、仿真工况数据与原型系统运行日志构成的混合验证链。其中，公开数据用于验证基础诊断能力，仿真工况用于验证跨工况与弱故障稳定性，原型日志用于验证时延、告警与工单闭环能力。
- 每个核心创新至少要在本章找到一个对应的实验、案例或系统级指标支撑。

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
- 评测协议与数据划分
- Current methods 基线对比
- 开放类别与旋转定位效果
- 可靠性校准与查询稳定性
- 系统延迟与案例证据

## Structure Gate
- Required H3 Count: 5
- Required H3 Titles: 评测协议与数据划分、Current methods 基线对比、开放类别与旋转定位效果、可靠性校准与查询稳定性、系统延迟与案例证据
- Required H4 Total Min: 10
- `评测协议与数据划分` -> required H4 count=2; required titles=核心内容、支撑说明
- `Current methods 基线对比` -> required H4 count=2; required titles=核心内容、支撑说明
- `开放类别与旋转定位效果` -> required H4 count=2; required titles=核心内容、支撑说明
- `可靠性校准与查询稳定性` -> required H4 count=2; required titles=核心内容、支撑说明
- `系统延迟与案例证据` -> required H4 count=2; required titles=核心内容、支撑说明

## Markdown Structure Contract
- This chapter must not remain a single flat prose block.
- Writer must emit each planned subsection as an H3 heading in `draft.md`, using the exact titles below.
- Under each H3 subsection, add 1-3 H4 headings that answer concrete questions inside that subsection.
- Planned visuals must be cited inside the matching subsection body, not dumped at the chapter start or end.
- Required H3: `### 评测协议与数据划分`
- Suggested H4 under `评测协议与数据划分`: 核心论点 / 支撑分析
- Required H3: `### Current methods 基线对比`
- Suggested H4 under `Current methods 基线对比`: 核心论点 / 支撑分析
- Required H3: `### 开放类别与旋转定位效果`
- Suggested H4 under `开放类别与旋转定位效果`: 核心论点 / 支撑分析
- Required H3: `### 可靠性校准与查询稳定性`
- Suggested H4 under `可靠性校准与查询稳定性`: 核心论点 / 支撑分析
- Required H3: `### 系统延迟与案例证据`
- Suggested H4 under `系统延迟与案例证据`: 核心论点 / 支撑分析

## Innovation Loop Map
- 创新一 · 遥感域词汇原型适配: problem=利用遥感图文表示校正通用文本嵌入，使同一类别在俯视尺度、方向和纹理条件下保持稳定语义。; role=用指标、实验、案例和系统级性能把前文创新点落实为可验证结果。; validation=五、测试与效果分析; signal=指标改善、稳定性提升、闭环效率与系统性能; meaning=利用遥感图文表示校正通用文本嵌入，使同一类别在俯视尺度、方向和纹理条件下保持稳定语义。
- 创新二 · 多尺度旋转候选协同: problem=将切片、多尺度候选和旋转框定位与文本查询联合优化，降低小目标漏检和方向错配。; role=用指标、实验、案例和系统级性能把前文创新点落实为可验证结果。; validation=五、测试与效果分析; signal=指标改善、稳定性提升、闭环效率与系统性能; meaning=将切片、多尺度候选和旋转框定位与文本查询联合优化，降低小目标漏检和方向错配。
- 创新三 · 可靠语义校准: problem=利用类别—区域一致性、背景对照和温度校准抑制类别幻觉，输出可解释的不确定性和人工复核建议。; role=用指标、实验、案例和系统级性能把前文创新点落实为可验证结果。; validation=五、测试与效果分析; signal=指标改善、稳定性提升、闭环效率与系统性能; meaning=利用类别—区域一致性、背景对照和温度校准抑制类别幻觉，输出可解释的不确定性和人工复核建议。

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
- 数据来源与规模表 | impact=五、测试与效果分析 | why=测试章要求结果、图表和案例回放一起构成完整证据链。 | priority=high | backtrack=step4 | substitute=至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。
- 关键性能汇总表 | impact=五、测试与效果分析 | why=测试章要求结果、图表和案例回放一起构成完整证据链。 | priority=high | backtrack=step4 | substitute=至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。
- 对比实验结果表 | impact=五、测试与效果分析 | why=测试章要求结果、图表和案例回放一起构成完整证据链。 | priority=high | backtrack=step4 | substitute=至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。
- 案例回放时序图 | impact=五、测试与效果分析 | why=测试章要求结果、图表和案例回放一起构成完整证据链。 | priority=high | backtrack=step4 | substitute=至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。
- 系统性能与闭环指标清单 | impact=五、测试与效果分析 | why=测试章要求结果、图表和案例回放一起构成完整证据链。 | priority=high | backtrack=step4 | substitute=至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。
- 开放词汇能力可能被提示词选择放大，需要冻结查询模板并做同义改写测试 | impact=五、测试与效果分析 | why=测试章要求结果、图表和案例回放一起构成完整证据链。 | priority=high | backtrack=step4 | substitute=至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。
- 公开数据与真实区域存在域差异，必须保留跨区域外测和人工复核边界 | impact=五、测试与效果分析 | why=测试章要求结果、图表和案例回放一起构成完整证据链。 | priority=high | backtrack=step4 | substitute=至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。
- YOLO-World 等组件的许可证需要在发布前核验 | impact=五、测试与效果分析 | why=测试章要求结果、图表和案例回放一起构成完整证据链。 | priority=high | backtrack=step4 | substitute=至少提供公开数据、仿真工况或原型日志中的一类支撑，并补齐对照组、指标含义和案例回放。

## Seed Context
- Seed Type: `validation_support_pack`
- Pack Summary: 本验证包以 创新一 · 遥感域词汇原型适配、创新二 · 多尺度旋转候选协同、创新三 · 可靠语义校准 为主线，组织公开资料、仿真场景和原型日志三类材料，提供可直接落入作品书的测试结构。
- Disclosure: 本章测试采用公开轴承故障数据、仿真工况数据与原型系统运行日志构成的混合验证链。其中，公开数据用于验证基础诊断能力，仿真工况用于验证跨工况与弱故障稳定性，原型日志用于验证时延、告警与工单闭环能力。
- Required Assets: 数据来源与规模表、关键性能汇总表、对比实验结果表、案例回放时序图、系统性能与闭环指标清单

## Approved Upstream Context
- 一、作品概述与问题定义: `workspace\document_writing\chapters\01_s1\draft.md`
- 二、作品设计与总体架构: `workspace\document_writing\chapters\02_s2\draft.md`
- 三、核心创新与关键技术: `workspace\document_writing\chapters\03_s3\draft.md`
- 四、作品实现与运行闭环: `workspace\document_writing\chapters\04_s4\draft.md`

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
- Common errors for this chapter: 只罗列几个好看的数字；没有交代指标口径和数据边界；把系统性能和分类效果混在一起；把仿真示例值写成真实实测结果.
- Appendix candidates for overflow material: 补充实验说明；扩展曲线图；更多案例回放截图.

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

# Chapter Brief: 七、总结与展望

## Workflow Contract
- This chapter must be handled by real LLM agents, not deterministic filler text.
- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.
- Agent2 writes this chapter into `workspace\document_writing\chapters\07_s6\draft.md`.
- Agent3 audits the written chapter into `workspace\document_writing\chapters\07_s6\audit.md` and updates `workspace\document_writing\chapters\07_s6\decision.json`.
- Agent3 may consult `workspace\document_writing\chapters\07_s6\decision-schema.md` for field contract only; Agent2 should ignore that file.
- The next chapter stays locked until Agent3 approves this one.

## Chapter Metadata
- Chapter ID: `s6`
- Chapter Type: `body_section`
- Goal: 用作品书收束口径总结当前成果、边界与后续展望，避免把尾章写成项目排期表或提案附页。
- Narrative Role: 用作品书定稿口径收束全书，说明作品已经形成的能力、系统特色和后续优化方向。
- Position Logic: 作为收束章节，本章负责总结作品完成情况、系统价值与不足展望，避免尾章写成项目计划或内部待办说明。
- Chapter Weight Reason: 对于平台应用型项目，本章不是附属排期页，而是成熟度说明；它直接影响评委对项目完成度与延展性的判断。
- Work Type: 平台应用型
- Matched Scores: 技术方案及其实现质量、应用价值
- Sample Reference: 第五章 总结与展望 / 收束作品完成情况，明确系统特色、当前不足和后续优化方向。
- Suggested Length: 1-2p / 11250-15000

## Section Dependencies
- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。
- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。
- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。
- Previous: 六、应用前景与落地价值
- Next: none

## Body Priorities
- 完成情况
- 系统特色
- 应用价值
- 不足与后续方向

## Visual Priorities
- 完成情况对照表
- 系统价值闭环图
- 优化方向图

## Visual Specs
- [表7-1] 完成情况对照表 | type=table | purpose=对齐痛点、创新点、模块或证据之间的对应关系。 | anchor=作品完成情况 | subsection=作品完成情况 | required=True
  - Reference Hint: 建议在正文中使用“如表7-1所示”或“表7-1显示”来引用该表。
- [图7-2] 系统价值闭环图 | type=figure | purpose=说明系统运行步骤、数据流向或业务闭环。 | anchor=系统特色与应用价值 | subsection=系统特色与应用价值 | required=True
  - Reference Hint: 建议在正文中使用“如图7-2所示”或“图7-2显示”来引用该图。
- [图7-3] 优化方向图 | type=figure | purpose=优化方向图 | anchor=不足与后续优化 | subsection=不足与后续优化 | required=True
  - Reference Hint: 建议在正文中使用“如图7-3所示”或“图7-3显示”来引用该图。

## Length Gate
- Target Budget: 11250-15000
- Minimum Pass Threshold: 11250 (100% of lower bound 11250)
- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.
- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.

## Must Include
- 可在 Grounding DINO、Detic 或 YOLO-World 上建立可复现实验基线
- DIOR、DOTA、FAIR1M 等公开数据可支撑多协议验证
- 系统先支持离线切片推理，再扩展到实时或边缘部署
- 作品已经形成的闭环能力与交付形态。
- 系统特色、应用价值和交付成熟度。
- 当前不足与后续优化方向。

## Key Messages
- 可在 Grounding DINO、Detic 或 YOLO-World 上建立可复现实验基线
- DIOR、DOTA、FAIR1M 等公开数据可支撑多协议验证
- 系统先支持离线切片推理，再扩展到实时或边缘部署
- 开放词汇能力可能被提示词选择放大，需要冻结查询模板并做同义改写测试
- 公开数据与真实区域存在域差异，必须保留跨区域外测和人工复核边界
- YOLO-World 等组件的许可证需要在发布前核验
- 该方向把前沿的开放词汇检测与明确的遥感应用约束结合起来，既有科学问题，也能形成可演示、可评测、可扩展的比赛作品。

## Linked Innovations
- none

## Linked Architecture
- 遥感影像切片与质量检查
- 文本词汇与域适配编码
- 水平/旋转候选检测
- 可靠性校准与证据回放

## Subsections
- 作品完成情况
- 系统特色与应用价值
- 不足与后续优化

## Structure Gate
- Required H3 Count: 3
- Required H3 Titles: 作品完成情况、系统特色与应用价值、不足与后续优化
- Required H4 Total Min: 9
- `作品完成情况` -> required H4 count=3; required titles=闭环完成情况、关键能力、交付形态
- `系统特色与应用价值` -> required H4 count=3; required titles=系统特色、应用价值、交付成熟度
- `不足与后续优化` -> required H4 count=3; required titles=当前不足、优化方向、延展空间

## Markdown Structure Contract
- This chapter must not remain a single flat prose block.
- Writer must emit each planned subsection as an H3 heading in `draft.md`, using the exact titles below.
- Under each H3 subsection, add 1-3 H4 headings that answer concrete questions inside that subsection.
- Planned visuals must be cited inside the matching subsection body, not dumped at the chapter start or end.
- Required H3: `### 作品完成情况`
- Suggested H4 under `作品完成情况`: 闭环完成情况 / 关键能力 / 交付形态
- Required H3: `### 系统特色与应用价值`
- Suggested H4 under `系统特色与应用价值`: 系统特色 / 应用价值 / 展示完成度
- Required H3: `### 不足与后续优化`
- Suggested H4 under `不足与后续优化`: 当前不足 / 优化方向 / 延展空间

## Innovation Loop Map
- none

## Evidence Contract
- Evidence Requirement: required | status=strong | count=5 | authoritative=5 | high_reliability=5
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

## Pending Confirmations
- none

## Missing Materials
- 当前章程未给出作品书具体章节模板，需要补充命题文件或文档格式要求。 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- 当前 topic 的具体赛道 / 命题方向尚未从章程中唯一确定，需要结合命题文件确认。 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- 当前章程未明确作品书字数或页数限制，需要补充模板文件确认。 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- 开放词汇能力可能被提示词选择放大，需要冻结查询模板并做同义改写测试 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- 公开数据与真实区域存在域差异，必须保留跨区域外测和人工复核边界 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。
- YOLO-World 等组件的许可证需要在发布前核验 | impact=全书规划 | why=这些信息会影响章节轻重、格式约束、系统边界或强 claim 的成立条件。 | priority=high | backtrack=step1/step4 | substitute=在正文中显式标为待确认项，并降低结论强度。

## Approved Upstream Context
- 一、作品概述与问题定义: `workspace\document_writing\chapters\01_s1\draft.md`
- 二、作品设计与总体架构: `workspace\document_writing\chapters\02_s2\draft.md`
- 三、核心创新与关键技术: `workspace\document_writing\chapters\03_s3\draft.md`
- 四、作品实现与运行闭环: `workspace\document_writing\chapters\04_s4\draft.md`
- 五、测试与效果分析: `workspace\document_writing\chapters\05_s_validation\draft.md`
- 六、应用前景与落地价值: `workspace\document_writing\chapters\06_s5\draft.md`

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
- Common errors for this chapter: 把尾章写成项目排期表；把远期愿景写成当前承诺；总结章节仍在解释写作边界.
- Appendix candidates for overflow material: 详细排期表；资源依赖表.

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

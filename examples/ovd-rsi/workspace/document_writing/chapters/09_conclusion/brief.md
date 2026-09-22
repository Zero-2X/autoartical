# Chapter Brief: 结语

## Workflow Contract
- This chapter must be handled by real LLM agents, not deterministic filler text.
- Agent1 is the supervisor and may only unlock this chapter after the previous chapter is approved.
- Agent2 writes this chapter into `workspace\document_writing\chapters\09_conclusion\draft.md`.
- Agent3 audits the written chapter into `workspace\document_writing\chapters\09_conclusion\audit.md` and updates `workspace\document_writing\chapters\09_conclusion\decision.json`.
- Agent3 may consult `workspace\document_writing\chapters\09_conclusion\decision-schema.md` for field contract only; Agent2 should ignore that file.
- The next chapter stays locked until Agent3 approves this one.

## Chapter Metadata
- Chapter ID: `conclusion`
- Chapter Type: `conclusion`
- Goal: 收束项目贡献、作品价值与后续优化方向，不再新增核心论证。
- Narrative Role: 作为收尾章节，总结贡献、应用价值并给出克制的后续优化方向。
- Position Logic: 结语位于全书末尾，只做收束，不再引入新技术细节或新实验。
- Chapter Weight Reason: 结语篇幅不大，但直接影响整部作品书的成熟度、完成感和评委对作品价值的最终判断。
- Work Type: 平台应用型
- Matched Scores: 应用价值、讲解表现
- Sample Reference: 第五章 总结与展望 / 只做总结、价值收束和后续优化方向，不重复正文技术细节。
- Suggested Length: 1-2p / 800-1400

## Section Dependencies
- 必须阅读 workflow/references/content-depth.md。40–50 页要求实质正文充足，不得通过留白、分页或重复改写凑数。
- 章节预算按有效正文计数；补充可核验事实、机制推导、设计取舍、实现细节、验证与边界。
- 缺少证据时列入材料缺口，不能捏造实验结果；字数达标不代表内容审查通过。
- Previous: 七、总结与展望
- Next: none

## Body Priorities
- 贡献总结
- 作品价值
- 后续优化

## Visual Priorities
- none

## Visual Specs
- none

## Length Gate
- Target Budget: 800-1400
- Minimum Pass Threshold: 800 (100% of lower bound 800)
- Count Rule: Chinese CJK characters plus Latin word tokens after stripping markdown formatting.
- Agent3 must not approve this chapter if the正文长度 is below the minimum pass threshold unless Agent1 explicitly downgrades the requirement.

## Must Include
- 项目总体贡献总结
- 作品价值收束
- 下一流程优化方向

## Key Messages
- 总结项目已形成的核心能力与系统主线。
- 收束作品对典型用户与应用场景的价值。
- 提出下一流程优化方向，但不要写成范围管理说明。

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
- none

## Markdown Structure Contract
- Use headings only when they improve readability; abstract and conclusion may stay compact.

## Innovation Loop Map
- none

## Evidence Contract
- Evidence Requirement: optional | status=not_applicable | count=0 | authoritative=0 | high_reliability=0
- Agent2 must translate evidence into chapter-level论证，不允许只堆 source 名称；每个亮点至少落到“问题来源 / 现有不足 / 本作品做法 / 预期价值”中的 2 个环节。
- Agent3 must check whether the chapter really absorbed the evidence-derived insights, instead of only repeating generic claims.

## Supporting Evidence
- none

## Pending Confirmations
- 开放词汇能力可能被提示词选择放大，需要冻结查询模板并做同义改写测试
- 公开数据与真实区域存在域差异，必须保留跨区域外测和人工复核边界
- YOLO-World 等组件的许可证需要在发布前核验

## Missing Materials
- none

## Approved Upstream Context
- 一、作品概述与问题定义: `workspace\document_writing\chapters\01_s1\draft.md`
- 二、作品设计与总体架构: `workspace\document_writing\chapters\02_s2\draft.md`
- 三、核心创新与关键技术: `workspace\document_writing\chapters\03_s3\draft.md`
- 四、作品实现与运行闭环: `workspace\document_writing\chapters\04_s4\draft.md`
- 五、测试与效果分析: `workspace\document_writing\chapters\05_s_validation\draft.md`
- 六、应用前景与落地价值: `workspace\document_writing\chapters\06_s5\draft.md`
- 七、总结与展望: `workspace\document_writing\chapters\07_s6\draft.md`
- 摘要: `workspace\document_writing\chapters\08_abstract\draft.md`

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
- Common errors for this chapter: 结尾新增未论证内容；只重复前文没有收束；把愿景写成当前已交付能力.
- Appendix candidates for overflow material: none.

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

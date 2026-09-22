# 工作流质量审计

## 结论

选题文本、摘要和章节种子不是完整长文；只有经过 document_plan、章节批准、content_depth、visual、render 和 export 门禁的文件才是最终交付。

- 审计结论：`pass`
- 失败的结构检查：0

## 已经强制的门禁

- 通过：pipeline_has_research
- 通过：pipeline_has_visual_assets
- 通过：pipeline_has_export_gate
- 通过：content_contract_has_40_50
- 通过：content_min_is_24000
- 通过：visual_contract_is_explicit
- 通过：review_checks_visual_gate
- 通过：export_requires_render_report
- 通过：evaluator_has_long_form_mode
- 通过：planner_carries_content_contract
- 通过：visual_script_writes_requests
- 通过：writing_is_agent_orchestrated

## 当前仓库中短于完整交付合同的示例

- `examples\bridge-risk\proposal.md`：2444 有效正文单位；短于 24000，不能作为最终长文。
- `examples\bridge-risk\README.md`：28 有效正文单位；短于 24000，不能作为最终长文。
- `examples\ship-vision\proposal.md`：3870 有效正文单位；短于 24000，不能作为最终长文。
- `examples\ship-vision\README.md`：443 有效正文单位；短于 24000，不能作为最终长文。
- `examples\ship-vision\topic-selection.md`：4067 有效正文单位；短于 24000，不能作为最终长文。

## 问题分析与修复状态

- **fixed / 数量**：旧评估器只按关键词和格式打分，短文可获得 pass；现在默认进入 long_form_required，低于 24000 有效正文单位直接 revise。
- **fixed / 视觉**：视觉请求与真实素材曾经分离；现在由视觉台账、素材存在性、正文引用和数量门禁共同检查。
- **fixed / 导出**：HTML 生成曾容易被误解为最终交付；现在必须提供 render-report.json，记录页数在 40–50、逐页 visual_qa=pass 和 verified=true。
- **known_limit / 写作执行**：章节写作仍由真实 LLM agent/外部写作执行完成，CLI 负责状态、证据、章节门禁和汇编，不伪造正文。没有章节批准时不能称为完成。
- **known_limit / 数据真实性**：素材请求文件不等于图像；实验指标和案例结果必须来自真实数据，自动化不会填入虚构结果。

## 完整交付判定

必须同时满足：研究 Gate 通过、章节计划存在、每章正文和审计批准、有效正文达到 24000 最低单位、视觉规格和真实资产达标、所有图表在正文引用、实际渲染页数为 40–50、逐页视觉 QA 通过、export-manifest.json 为 pass。

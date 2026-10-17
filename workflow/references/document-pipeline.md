# 长文文档工作流运行手册

适用于申报书、论文初稿、研究报告等正文不少于 40 页的文档。本手册是长文流程的权威顺序；各步骤细则见对应 skill。旧版 `workflow.md` 中的论文实验循环与幻灯片章节不属于本流程。

## 分工

| 环节 | 执行者 | 说明 |
|---|---|---|
| 调研、文献核验、写作、数据图、导出、质检 | Claude 或 Codex 均可 | 依赖本仓库脚本，无外部密钥 |
| 示意图（栅格）生成 | **只能由 Codex 内置 `image_gen`** | 其他代理不得以其他 API、脚本或占位图替代 |
| Word 导出 PDF | 需要 Windows + Microsoft Word | 无 Word 时结果为 blocked，不降级 |
| 最终语义判断、封面信息、是否提交 | 用户 | |

## 步骤

每一步都写出产物；任何输入变化后，下游记录按哈希自动失效，必须从变化处往下重跑。

| # | 做什么 | 命令 / 文件 | 通过条件 | 失败时 |
|---|---|---|---|---|
| 1 | 研究问题链：领域 → 子领域 → 挑战 → 方法路线 → 缺口 → 设计 → 假设 → 实验 | `run_research.py`，`research-brief.json` | research gate 通过 | 补检索，见 `academic-research-writing` |
| 2 | 登记并核验文献（按正文首次引用顺序） | `evidence/references.json` → `verify_references.py` | 全部 verified；生成 GB/T 7714 条目 | 换正确的 arXiv 号/DOI；载体无依据就按预印本著录 |
| 3 | 章节计划：每章目的与篇幅区间 | `document_plan/section-plan.json` | 方法与实验章最长；末章 ≤10% | 调整计划 |
| 4 | 逐章写作 | `document_writing/formal/NN_*.md` | 见 `humanized-academic-writing` | — |
| 5 | 拼合正式稿并做结构检查 | 拼合为 `正式稿.md`；`manuscript_lint.py` | verdict pass | 按失败项改正文，不改检查规则 |
| 6a | 数据图 | CSV + spec → `make_chart.py` | 生成 `provenance.json` | 无真实数据则不画 |
| 6b | 示意图准备 | `run_visual_assets.py`；在 `request.json` 写 `article_understanding`；`compose_imagegen_prompt.py` | Prompt 完整，含图意与证据边界 | — |
| 6c | **示意图生成（交给 Codex）** | Codex 调用 `image_gen` → `register_imagegen_asset.py` | 登记了 Prompt 哈希、图片哈希、目视审查 | 修改 Prompt 重生成 |
| 6d | 沿用旧图 | `request.json` 写 `placement_review` | 当前正文哈希、论证作用、核对说明齐全 | 图意不符则回 6b |
| 7 | 导出与自动版式检查 | `run_document_export.py <topic>` | Word 实排正文 ≥40 页，版式检查全部通过 | 回内容层调整，不缩放不改边距 |
| 8 | 人工审查（视觉 + 语义分开） | `qa_ledger.py record`（`--method full-page --pages all`） | 无未关闭的 blocker/major；6 项语义判定齐全 | 修改后从第 5 步重跑 |
| 9 | 交付判定 | `qa_ledger.py verify`；`export-manifest.json` | deliverable pass | 按 stale 原因重跑对应步骤 |

## 交给 Codex 的生图任务（6c）

在 Codex 中打开本仓库，给它这样的指令即可：

> 按 `workflow/references/imagegen-figures.md` 处理 `examples/<topic>/workspace/document_assets/figures/` 中 `status` 为 `needs_generation` 或缺少 PNG 的请求：逐图读 `request.json` 中的 `article_understanding` 与 `prompt`，调用内置 `image_gen` 生成，打开原图检查图意、可读性与无虚构数值，然后用 `register_imagegen_asset.py` 登记。不要改动正文。

生图完成后回到第 7 步重新导出；新图会使旧的人工审查失效，需要重新审查含图页面。

## 不可降级的规则

- 不以缩小字号、调整边距、放大图片、插入空白、重复论述凑页数。
- 不以降低阈值、增加例外让产物通过；检查规则本身有误时，单独修复并补回归测试（见 `tests/test_export_render.py`）。
- 未运行的实验只写“待实测”，不生成数值、曲线或结果图。
- 自动检查通过不等于质量达标；人工语义审查必须单独登记。

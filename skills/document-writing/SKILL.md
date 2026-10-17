---
name: document-writing
description: 从可靠资料和明确选题出发，生成、审查并迭代论文、竞赛说明书、项目方案和基金风格研究文档；覆盖章节写作、图表制作、Word/PDF 交付与哈希绑定的质量验收。需要文档级引用、表格、配图和版本化改进记录时使用。
---

# 文档写作技能

从文献和选题开始时，先用 `skills/academic-research-writing/SKILL.md` 完成研究 brief 和引用核验；表达修订用 `humanized-academic-writing`；排版交付用 `doctoral-thesis-format`。本 skill 负责把它们串成一条可复检的流程。

## 流程（每步的输入、输出、失败条件与复检）

| 步骤 | 输入 | 输出 | 失败条件 | 修复后复检 |
|---|---|---|---|---|
| 1 研究与引用 | 选题、research brief | `evidence/references.json`、`citation-verification.json`、`references.gbt7714.md` | 任一文献无法程序化核验、标题不符、载体无依据 | 重跑 `verify_references.py` |
| 2 章节计划 | 研究问题链 | `section-plan.json`（章节、目的、篇幅区间） | 末章承担技术论证；方法/实验篇幅低于背景 | — |
| 3 逐章写作 | 计划、证据 | `document_writing/formal/NN_*.md` → 拼合为 `正式稿.md` | 见下方写作规则 | `manuscript_lint.py` |
| 4 图表 | 定稿段落 | 示意图（ImageGen）、数据图（`make_chart.py`）、三线表 | 见下方图表规则 | `build_figure_table_gate` |
| 5 排版导出 | `正式稿.md` | DOCX，Word 导出的 PDF，`auto-check.json`，页面渲染 | 见 `doctoral-thesis-format` | `run_document_export.py` |
| 6 人工审查 | 页面渲染、正文 | `human-review.json`（视觉 + 语义，分开） | 存在未关闭的 blocker/major，或语义项未判定 | `qa_ledger.py record` |
| 7 交付判定 | 以上全部 | `export-manifest.json`，`qa-status.json` | 任一记录过期或未通过 | `qa_ledger.py verify` |

任何输入文件（正文、图片、导出代码）变化后，相关记录的哈希失配即自动失效；不得手工改记录让它重新“通过”。

## 写作规则

吸收 Anthropic doc-coauthoring 的“读者测试”和 Orchestra ml-paper-writing 的叙事原则：

- 写之前先用一句话写出贡献；写不出来说明研究问题还没定。摘要按“做了什么—为什么难—怎么做—有什么证据—边界”组织，删去可以放在任何论文开头的句子。
- 每个实验段落先说它检验哪个主张，再说设置与指标。
- 段落、标题、证据等级的规则见 `humanized-academic-writing`。
- **正文中不出现工作流元信息**（门禁、manifest、Prompt、签核、版本封存等），这些内容属于质量记录而非研究内容。
- 初稿完成后做读者测试：让一个没有上下文的审阅者只读文档，回答“研究问题是什么、方法如何回答、什么结果会推翻它”；答不出或答错的地方就是需要改的地方。

## 图表规则

吸收 K-Dense scientific-visualization 与 Orchestra academic-plotting 的做法：**有数值坐标轴的图用可复现脚本绘制，方框—箭头类机制图用 ImageGen**，二者不得互换。

- 每幅图必须承担一种论证作用：机制、比较、数据、案例或框架之一，并在正文中先被引用、再出现；图注能独立说明图展示什么、支持什么判断、哪些部分是示意。
- 数据图：数据写入 CSV（每行带来源键），图规格写入 JSON，运行 `python workflow/scripts/make_chart.py <spec> --topic <dir>`。规则：柱状图从零起；对数轴必须声明；Okabe-Ito 配色并配合标记或纹理，不只靠颜色区分；图内不放标题；只有下限的数据要在图上标明；生成 `provenance.json` 绑定数据、脚本与图片哈希。没有真实数据时不画数据图，不让 ImageGen 画曲线或数值。
- 示意图：按 [逐图 ImageGen 工作法](../../workflow/references/imagegen-figures.md) 读正文 → 写图意与证据边界 → 写完整 Prompt → 调用 Codex 内置 `image_gen` → 检查 → 登记。正文改动后，沿用旧图必须在 `request.json` 中补写 `placement_review`（当前正文哈希、论证作用、与正文逐项核对的说明）。本仓库其他代理（如 Claude）无法调用 Codex `image_gen`，只能复用已登记图并做放置审查，新图须交给 Codex 生成。
- 表格：表题“表N-M”在上，三线表，正文先引用；表注写明数据来源或设计依据、单位、统计口径与缺失值约定（如“待实测”）；表注与正文都要解释关键差异，不逐格复述。

## 质量证据的口径

自动检查只覆盖可测量的版式与结构事实；论证是否成立、图意是否准确由人工语义审查判断。人工审查记录写明查看方式与范围（`full-page`/`thumbnail`/`text-only`），只有全页查看全部页面才可写“逐页核验”。“门禁通过”不能单独作为质量达标的证据。

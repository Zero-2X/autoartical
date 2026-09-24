# AutoArtical · 证据驱动的高质量文档工作流

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![License](https://img.shields.io/badge/license-MIT-2ea44f)](LICENSE) [![Quality](https://img.shields.io/badge/文档审查-可追溯-0f766e)](workflow/scripts/evaluate_document.py)

把一个模糊想法变成**能读、能查、能评、能继续改**的研究文档：竞赛作品说明书、论文初稿、项目方案和基金风格申请书都可以沿用同一套证据和审查约束。

> 当前示例选题：**面向桥区复杂遮挡环境的船舶轨迹重建与通航风险预警方法**。示例刻意把“已知事实、拟验证指标、尚待补充材料”分开，避免把计划写成结果。

## 工作流一览

```mermaid
flowchart LR
 A[资料与要求] --> B[证据台账]
 B --> C[候选选题]
 C --> D{人工确认}
 D --> E[选题说明]
 E --> F[自动研究]
 F --> G[章节计划]
 G --> H[正文写作]
 H --> I[阅读文章并提炼每图主张]
 I --> J[撰写详细逐图 Prompt]
 J --> K[Codex 内置 ImageGen 逐图生成]
 K --> L[目视审查并登记来源]
 L --> M[论文/竞赛/基金联合审查与导出]
 M --> G
```

| 环节 | 产物 | 质量约束 |
|---|---|---|
| 选题 | 候选集、评分依据、选择记录 | 不凭空补事实，保留人工决策 |
| 规划 | 章节计划、主张清单、证据映射 | 每个关键结论都能回到来源 |
| 写作 | Markdown 正文、表格、Mermaid 图 | 事实、计划、假设分开表达 |
| 自动研究 | 领域/子领域/挑战/方法分类/缺口/实验契约 | 查询和未核验来源不能当作事实 |
| 审查 | 论文/竞赛/基金三套口径 | 科学问题、方案闭环、可行性同时检查 |
| 迭代 | SQLite 轮次数据库 | 记录优点、缺陷、改动、依据和指标 |

## 运行示例

```bash
# 从资料目录开始生成完整工作区
python run_workflow.py ./my-topic --topic "主题名称"

# 候选生成后先人工确认
python workflow/scripts/run_selection.py ./my-topic
python run_workflow.py ./my-topic --select-id idea_a --from-step run_selection

# 自动研究首次运行会生成 research-plan.md 并在证据不足时停止；补充
# workspace/research/research-brief.json 与 external_evidence 后重新运行
python workflow/scripts/run_research.py ./my-topic
python run_workflow.py ./my-topic --from-step run_research

# 正文写完后准备逐图请求。完整工作流会在这里暂停，直到所有图都通过登记。
python workflow/scripts/run_visual_assets.py ./my-topic

# Codex 阅读对应小节和 research brief，逐图填写 request.json 中的 article_understanding
# 再根据图意写 visual_direction，并生成、审阅完整 Prompt
python workflow/scripts/compose_imagegen_prompt.py ./my-topic --figure-id <图号>

# 将完整 Prompt 交给 Codex 内置 image_gen；打开并检查原图，再登记。
python workflow/scripts/register_imagegen_asset.py ./my-topic --figure-id <图号> \
  --source <Codex生成的generated_images图片路径> --review-note <图意、清晰度、独特性与事实检查>

# 所有必需配图完成后继续联合审查和导出
python run_workflow.py ./my-topic --from-step run_document_review

# 没有 PDF/DOCX 渲染器时只生成 HTML 预览，不会宣称页数达标
python run_workflow.py ./my-topic --from-step run_document_export --allow-html-only

# 对已有文档做联合专业审查
python workflow/scripts/evaluate_document.py examples/bridge-risk/proposal.md \
  --out examples/bridge-risk/review.json

# 默认强制长文内容合同；只有选题卡等短种子才能显式放宽
python workflow/scripts/evaluate_document.py examples/bridge-risk/proposal.md \
  --allow-short --out examples/bridge-risk/seed-review.json

# 记录每轮改进，并在下一轮读取历史
python workflow/scripts/iteration_memory.py examples/bridge-risk/iteration-memory.sqlite show \
  --project bridge-risk
```

## 这个仓库保留了什么

- `workflow/scripts/`：选题、证据、规划、写作、引用/结构审查和迭代工具。
- `workflow/scripts/run_research.py`：在选题说明后生成自动研究问题、证据地图和实验契约；Gate 未通过时不允许进入文档规划。
- `workflow/prompts/`：论文各章节、引用、图表和自审提示词。
- `workflow/references/`：论文、竞赛说明书、基金风格评审、表格、图表、编译与提交规范。
- `workflow/templates/`：可机器读取的章节、引用、图表、审查和发布模板。
- `skills/document-writing/SKILL.md`：可复用的 Codex 文档写作 skill。
- `skills/academic-research-writing/SKILL.md`：可复用的文献研究、方法分类和论文写作 skill。
- `examples/bridge-risk/`：一份已经经过三轮迭代的完整示例。

可直接打开 [完整工作流 HTML 页面](docs/workflow.html) 查看流程、研究链路和质量门禁。

PPT 组装、演示文稿和外部图像 API 不在本仓库范围内。配图必须在章节正文形成后进行：先阅读对应小节并写逐图 `article_understanding`，再生成完整详细的 Prompt，逐张调用 Codex 内置 `image_gen`，目视审查后登记原图、Prompt 散列和来源。旧 SVG 或只有图片文件都不能通过视觉门禁。详见 [逐图 ImageGen 工作法](workflow/references/imagegen-figures.md)。

## 专业评审口径

自动研究会先回答“领域是什么、为什么研究、子领域是什么、为什么选择、通用挑战及影响、Current methods 分类与优缺点、关键缺口、科学设计 rationale、case study、benchmark/baseline/metrics 与实验目的”，再允许进入正文规划。详见 [自动研究工作流](workflow/references/automatic-research.md)。

长文默认要求 **40–50 页实质正文**，从选题开始即进入合同。规划器分配 24000–32000 个中文字符／英文词元的起始预算，并同时分配视觉规格、素材请求和导出要求；逐章和全书检查排除标题、表格、代码、图片及重复段落。交付前必须通过内容、视觉、引用和实际渲染门禁；PDF 全页栅格密度下限为 0.55，不能以空白页凑页数。详见 [内容深度规范](workflow/references/content-depth.md) 和 [开源融合调研](docs/open-source-integration.md)。

短选题卡不会被当作最终交付：`evaluate_document.py` 默认使用 `long_form_required`，有效正文不足 24000 个单位时直接退回修订，并同步检查段落密度、重复、引用及问题—机制—实验—边界语义覆盖。`--allow-short` 只用于显式标注的种子评审；`workflow/scripts/audit_workflow.py` 可检查仓库是否仍保留这些硬门禁。

- **论文**：问题是否可检验，方法是否可复现，基线/消融/统计区间是否完整，引用是否真实存在。
- **竞赛说明书**：需求、用户、方案、创新、实施、风险和展示证据是否形成闭环。
- **基金申请书**：科学问题是否聚焦，创新性是否落到研究内容，技术路线和前期基础是否足以支撑可行性。

国家自然科学基金现行条例明确将科学价值、创新性、社会影响和研究方案可行性作为评审维度；仓库中的评审脚本将这些维度转成可追踪检查项，但不会替代领域专家判断。

## 文档质量与 AI 风格

仓库提供的自动检查会发现缺少章节、重复段落、引用数量不足、表格/图缺失和常见模板化短语。它不能冒充第三方 AI 检测服务，也不会承诺某个“AI 率”数字。降低机械感的核心做法是：让每个结论有来源，让句子服务于论证，让限制条件和未完成工作直接写出来，并把每轮修改原因存进数据库。

## 版本管理

资料导入支持可选的 Docling/MarkItDown/PyMuPDF/Trafilatura/PaperQA2 类能力边界；当前仓库实际采用轻量适配器，不复制外部项目源码。安装 `requirements-integrations.txt` 后，`run_evidence.py` 会生成全文解析缓存、SHA-256 和来源定位记录；其中 PyMuPDF 与 Pillow 也用于 PDF 生成、全页栅格密度核验和视觉 QA。未核验的来源会保留告警，不能直接写成事实结论。

本次抽取已提交并推送到 [Zero-2X/autoartical](https://github.com/Zero-2X/autoartical)。每轮文档改进建议使用独立 commit，并在 SQLite 迭代记录中写明触发原因和可验证变化。

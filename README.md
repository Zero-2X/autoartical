# autoartical

这是从研究型工作区抽取出的“选题到文档成稿”工作流。仓库只保留与文档生产直接相关的能力：资料识别、要求解析、证据整理、候选选题、人工确认、选题说明、文档规划、章节写作和质量审查。

## 快速开始

```bash
python run_workflow.py ./my-topic --topic "主题名称" --select-id idea_a
```

`my-topic` 应包含比赛细则、项目资料或参考文档。工作流会在主题目录下创建 `workspace/` 和 `output/`：

- `workspace/intake/`：主题资料清单
- `workspace/requirements/`：要求与约束
- `workspace/ideas/`：证据台账与候选选题
- `workspace/selection/`：人工确认记录
- `workspace/concept/`：选题说明与验证依据
- `workspace/document_plan/`：文档结构、章节计划和覆盖检查
- `workspace/document_writing/`：章节草稿、审计记录和合并草稿
- `workspace/document_review/`：整篇质量报告
- `output/`：最终 Markdown 文档

选题确认是唯一的人工决策点。先运行到候选生成：

```bash
python run_workflow.py ./my-topic --topic "主题名称" --dry-run
python workflow/scripts/run_selection.py ./my-topic
```

查看候选编号后，继续执行：

```bash
python run_workflow.py ./my-topic --select-id idea_a --from-step select_idea
```

也可以单独重跑任一步：

```bash
python workflow/scripts/run_document_plan.py ./my-topic
python workflow/scripts/run_document_writing.py ./my-topic
python workflow/scripts/run_document_review.py ./my-topic
```

## 设计原则

- 所有中间产物都写入主题目录，支持中断后继续。
- 事实性陈述必须能回溯到资料或证据条目；缺失资料会被记录为待确认项。
- 文档只汇编已完成审查的章节，避免把未验证内容混入成稿。
- 文件和状态命名按业务含义组织，便于独立复用。

## 依赖

Python 3.10+。若输入包含 PDF，建议安装 `pypdf`；没有它时仍可处理 Markdown、TXT、JSON 等文本资料。

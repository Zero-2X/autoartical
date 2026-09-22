# 开源能力融合调研

核验日期：2026-09-22。GitHub REST API 实时读取星标、归档状态、默认分支最近提交与最新 release；星标会变化。以下五个项目均未归档，且近 90 天存在默认分支提交和 release，因此列为当前维护候选。活跃不等于稳定，接入时仍须锁定版本和用本项目资料回归。未复制外部源码，以下接入均为建议，尚未安装或完成集成。

## 优先项目

| 项目 | Stars | 默认分支最近提交 | 最新 release | 许可 | 对应缺口 |
|---|---:|---|---|---|---|
| [Docling](https://github.com/docling-project/docling) | 67,553 | 2026-09-21 | [v2.129.0，09-18](https://github.com/docling-project/docling/releases/tag/v2.129.0) | MIT | PDF 阅读顺序、表格、OCR 与结构化提取 |
| [MarkItDown](https://github.com/microsoft/markitdown) | 186,237 | 2026-09-21 | [v0.1.8，09-21](https://github.com/microsoft/markitdown/releases/tag/v0.1.8) | MIT | Office 等资料转 Markdown 的轻量入口 |
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) | 29,559 | 2026-08-23 | [v3.6.1，08-24](https://github.com/assafelovic/gpt-researcher/releases/tag/v3.6.1) | Apache-2.0 | 拆分研究问题、检索与汇总候选来源 |
| [Pandoc](https://github.com/jgm/pandoc) | 46,370 | 2026-09-21 | [3.11，08-29](https://github.com/jgm/pandoc/releases/tag/3.11) | GPL-2.0 | Markdown、引用与 DOCX/PDF 编译链 |
| [Typst](https://github.com/typst/typst) | 56,172 | 2026-09-18 | [v0.15.1，07-17](https://github.com/typst/typst/releases/tag/v0.15.1) | Apache-2.0 | 可复现 PDF 排版与模板 |

信息来源为各仓库 README、LICENSE、commits 与 releases。不是将五个大型项目整体合并进仓库：保留当前 Python 编排、JSON 台账和 Markdown 正文，只在对应输入输出边界加可选适配器。

## 具体接法与验收

### 资料：Docling 为复杂 PDF 主选，MarkItDown 为轻量补充

接在 `run_evidence.py` 之前。提取输出与原件分开保存，记录文件摘要、工具版本、原始路径、页码／段落定位、表格结构与提取告警，再映射到现有 evidence-ledger。不能把“成功转出文本”当作“证据已经核实”。不具备页码定位的转换结果显式标为缺失，不能伪造页码。

验收使用真实扫描 PDF、双栏论文、跨页表格、带公式论文和 DOCX，逐项对照原件核实顺序、数字、单位和引用定位。Docling 的 OCR／模型资源增加安装与运行成本；MarkItDown 更轻，但不能假设普通文本转换具有完整的版面保真能力。首轮只需接一种资料解析器。

### 研究：GPT Researcher 产出候选证据，不直接替代定稿

从每节缺少的具体问题发起检索，输出查询、抓取时间、URL、原文片段与候选主张；经原文核验、来源去重和冲突记录后才写入证据台账。复用研究问题分解与来源收集思路，保留当前人工选题、逐章写作和审查合同。

验收：每个进入正文的关键事实能回到原文位置；搜索摘要不能替代原文；无结果、相互矛盾或无法访问的来源必须保留缺口。LLM 与检索服务可能需要密钥和费用，接入时由环境配置，禁止写入仓库。

### 交付：先 Pandoc，必要时再加入 Typst

复用 Pandoc CLI 完成 Markdown + 引用数据 + reference DOCX 到 DOCX 的构建；PDF 根据用户模板选择已有 TeX 环境或 Typst。Typst 更适合统一可控的 PDF 模板；用户要求 Word 可编辑时仍应保留 DOCX 路线。不能同时引入两套无法维护的模板体系。

把构建日志、引擎版本、输出摘要、实际正文页码范围与逐页核验记录写入现有 compile-report/submission-manifest。验收覆盖中文字体、交叉引用、文献表、跨页表格、公式、图注和 40–50 页正文范围。内容检查通过不能代替渲染通过。

MIT/Apache 代码复用需保留各自许可与适用声明，并核对模型或附属资源的独立许可。Pandoc 优先作为独立 CLI 使用；若复制或再分发 GPL 代码／二进制，应单独核对对应许可义务，不能直接将其标为本仓库 MIT。

## 暂不作为主依赖

- [STORM](https://github.com/stanford-oval/storm)：31,455 stars、MIT、未归档，但 API 返回最近 push 为 2025-09-30，距本次核验近一年。可参考多视角研究与大纲组织思想，不能据此声称近期仍活跃维护。
- [Zotero](https://github.com/zotero/zotero)：15,349 stars、未归档、最近 push 为 2026-09-21，可作为外部文献管理工具；API 的许可识别为 NOASSERTION，不能将其理解为无许可或可任意复制。引入源码前需核对 COPYING 及相关组件。当前优先研究标准文献数据导入导出，不移植桌面应用。

## 当前仓库发现与落地顺序

1. 已落地：长文正文合同、逐章预算分配、有效正文计数、全书短稿与重复内容阻断，补充实质扩写与渲染验收规范；修复 ready_for_review 状态与审查端不一致。
2. 下一项：用 Docling 或 MarkItDown 建立可定位的资料入口，再把研究检索结果纳入证据核验。资料供给直接决定长文能否充实。
3. 随后：建立正式模板编译入口及渲染记录，让正文量、页面范围和视觉密度共同决定交付状态。
4. 保留独立内容审查：现有 evaluate_document.py 主要是关键词与格式启发式检查，不能证明事实正确或文稿成熟。已有 runner 主要负责文件和状态编排，不能宣称单条命令已经自动完成真实 LLM 写作。还存在历史路径／命名残留，应另行按可执行入口逐项清理。

## 文献写作与 Skill 化补充调研（2026-09-22）

| 项目 | Stars | 最近 push | 许可 | 吸收方式 |
|---|---:|---|---|---|
| [AcademicForge](https://github.com/HughYau/AcademicForge) | 2,569 | 2026-08-30 | README 标 MIT，API 为 NOASSERTION | 参考跨 Codex/Claude/OpenCode 的 skill 目录、按需安装和 Windows 支持；不复制其技能内容 |
| [Medical Research Agent Skills](https://github.com/aipoch/medical-research-skills) | 1,904 | 2026-09-17 | MIT | 参考“证据洞察—方案设计—分析—学术写作”的能力分层和 skill 审计思想；医学专属内容不纳入通用仓库 |
| [PaperDebugger](https://github.com/PaperDebugger/paperdebugger) | 1,541 | 2026-07-03 | AGPL-3.0 | 参考 Research → Critique → Revision 闭环；不复制 AGPL 代码或提示词 |
| [ClaudePrism](https://github.com/delibae/claude-prism) | 1,784 | 2026-08-28 | MIT | 参考离线科学写作工作区、LaTeX/Python 与可复用 skill 的组合；不引入其桌面应用 |
| [Awesome Scientific Writing](https://github.com/writing-resources/awesome-scientific-writing) | 1,006 | 2026-09-15 | CC0-1.0 | 参考其对引用、交叉引用、编辑器、转换器和模板的能力地图 |
| [PaperQA2](https://github.com/Future-House/paper-qa) | 9,232 | 2026-08-12 | Apache-2.0 | 参考带页码/来源的科学文献检索、元数据意识和冲突识别；当前以接口边界写入 skill |

因此新增 `skills/academic-research-writing/SKILL.md`，把上述可迁移做法凝练为本仓库自己的触发条件、研究链路、证据规则、写作结构和交付门禁。`document-writing` 只负责正文表达与交付，研究型任务必须先经过新 skill 和 `run_research.py`。

本轮已实际落地 `workflow/scripts/source_ingestion.py`：PDF 改为全文逐页提取，HTML 可选 Trafilatura，Office 可选 MarkItDown；每份资料生成 SHA-256、解析引擎版本、定位片段、告警和缓存记录。`validate_evidence.py` 现在读取实际的 `evidence_items` 字段，并支持 `--strict`。可选依赖列在 `requirements-integrations.txt`，核心流程不因未安装这些依赖而改变 Markdown/TXT/JSON 的内置处理。

不建议为此把通用 agent 平台整体搬入仓库；先补资料、内容质量与交付闭环，避免维护两套状态系统。本仓库已用开放词汇 RSI 作为完整验收样例：研究 Gate、章节审批、正文/视觉/引用检查和 PyMuPDF 实际渲染均通过，具体证据保存在 `examples/ovd-rsi/workspace/`。后续接入外部解析器或排版工具仍需按同一合同重新验收。

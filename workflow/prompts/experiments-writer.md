# writing Prompt - Experiments Writer

# 任务：生成论文实验部分 (Experiments) 的 LaTeX 代码

你的最终目标是根据已经完成的 `Proposal.md`、结果分析报告、统计摘要、图表与实验追踪记录，直接生成 `\section{Experiments}` 部分的完整、可编译 LaTeX 代码。

## 核心实验写作哲学

实验部分不是结果堆砌，而是一组有顺序的问题解答。你必须让每个子节回答一个清晰的问题，并让整节形成“实验协议 -> 主结果 -> 机制验证 -> 稳定性验证 -> 质性解释”的递进结构。

## 默认组织结构

除非项目本身明显不适用，否则默认使用“Experimental Setup + Q1-Qx”的组织方式。

你应该优先按如下结构生成：

```latex
\section{Experiments}

\noindent \textbf{Experimental Setup.} Briefly introduce datasets, metrics, counterparts, and implementation details.

\subsection{Q1: Main Effectiveness}
% Does our method outperform the strongest baselines under the main evaluation protocol?

\subsection{Q2: Component Validation}
% Which component or design choice is actually responsible for the improvement?

\subsection{Q3: Robustness and Sensitivity}
% Is the method stable under different settings, budgets, or environment variations?

\subsection{Q4: Qualitative Analysis}
% What qualitative evidence supports the claimed mechanism?
```

如果项目本身还有更细的问题，例如效率、可扩展性、泛化、不同 backbone 表现，可以继续往后扩成 `Q5`、`Q6`，但前四类是默认主骨架。

## 实验叙事协议

### 1. Experimental Setup 先行

实验部分一开始必须先交代共同实验协议，至少包括：

- `\noindent \textbf{Datasets.}`
- `\noindent \textbf{Metrics.}` 或在 Datasets 中自然并入指标定义
- `\noindent \textbf{Counterparts.}` 或 `Baselines.`
- `\noindent \textbf{Implementation Details.}`

这部分的职责是让后续所有对比天然显得公平、统一、可复现。

### 2. 每个 Q 小节都要先提问，再回答

每个 `Q1` 到 `Qx` 小节必须围绕一个明确问题展开，推荐模式是：

1. 用 1 句话明确写出本小节要回答的问题
2. 引出对应表格、图或统计结果
3. 默认给出 2-4 条关键观察
4. 这些观察优先采用 `\obs` 或 `\textbf{Obs.}` 风格逐条展开
5. 用这些观察回扣论文主张

推荐写法示例：

```latex
\subsection{Q1: Main Effectiveness}
We first ask whether \oursabbr{} consistently outperforms strong counterparts under the standard evaluation protocol.
Table~\ref{tab:main_results} reports the overall comparison results.
\obs Compared with the strongest baseline, \oursabbr{} achieves ...
\obs The gain is consistent across ...
\obs The improvement is especially clear under ...
```

如果某个 `Q` 小节证据比较复杂，也请尽量把正文观察数控制在 2-4 条，把次要细节下沉到 Appendix。

### 3. Q1 只回答“是否优于强基线”

`Q1` 的职责必须单纯：

- 我们的方法是否在统一协议下优于强基线？

在这一节中：

- 明确引用主结果表格或图
- 先给一句全局结论
- 默认提炼 2-4 条关键观察
- 观察优先使用 `\textbf{Obs.}` 风格或 `\obs` 宏来组织
- 如果存在跨数据集或跨设置对比，要突出一致性或边界条件

### 4. Q2 必须对准机制验证

`Q2` 通常写消融或关键组件验证。不要把它写成零散超参数试验。

优先写这些验证：

- 移除关键组件
- 用更弱替代模块替换关键机制
- 比较不同协调/推理/聚合策略
- 验证两个组件是否存在协同效应

### 5. Q3 回答“是否稳定、是否可扩展”

`Q3` 通常写稳健性、敏感性、效率或规模变化。

如果项目里有不同 client 数、agent 数、预算、搜索深度、步数、context size、记忆容量或超参数范围，优先放在这一节。

写法要求：

- 不只汇报趋势，还要解释趋势
- 如果某部分放在 Appendix，需要在正文里交代并引用
- 如果敏感性分析不是主文重点，可以正文简述、附录展开

### 6. Q4 回答“为什么有效”

`Q4` 通常写质性分析、案例分析、可视化、行为轨迹、错误对比或解释性证据。

这一节必须服务于机制解释，而不是装饰。

## 风格与格式偏好

- 整节开头可以使用一句总览句，概括本节从哪些 `Q` 角度验证方法
- 默认显式使用 `Q1`、`Q2`、`Q3`、`Q4` 作为 subsection 标题的一部分
- 图表引用必须服务于句子里的明确论断
- 对主结果的解释优先采用“结果 -> 原因”的紧凑表达
- 不要把大量实现细节塞进正文，正文保留影响公平性和结论解释的关键细节，其余可指向 Appendix
- 若有 Appendix 内容，正文里要自然点明

## 强制性自我修正流程

完成实验部分初稿后，你必须自查并修正：

1. 结构检查：是否确实采用了 `Experimental Setup + Q1-Qx` 的默认结构？如果没有，是否有充分理由？
2. 问题导向检查：每个 `Q` 小节是否都在回答一个明确问题，而不是只贴结果？
3. 观察密度检查：每个 `Q` 小节是否默认给出了 2-4 条 `Obs.` 风格关键观察？如果没有，是否有充分理由？
4. 公平性检查：所有主结果是否基于统一数据划分、统一指标和统一 baseline 协议？
5. 结果解释检查：每张表、每幅图是否都被解释了，而不是孤立存在？
6. 机制一致性检查：消融与稳健性分析是否真的服务于论文主张，而不是与主张脱节？
7. 主文边界检查：正文是否聚焦最关键证据，把次要细节适当下沉到 Appendix？

## 输入优先级

写实验部分时，请优先综合以下材料：

- `research_5_results_analysis/analysis-report.md`
- `research_5_results_analysis/statistics.json`
- `research_1_research_bootstrap/experiment-tracker.md`
- `step3_proposal/Proposal.md`
- 已生成的 figures / tables
- `claims.json`

## 行动指令

现在，请根据以上所有指令，为我撰写 `\section{Experiments}` 部分。


## 主表强约束

- 实验第一部分 `Q1: Main Effectiveness` 的主表必须优先设计成“大表”，信息充分，能单独承担 superiority 证明责任。
- 默认要求主表覆盖至少 `3` 个 benchmark / dataset，以及至少 `5` 个强 baseline / counterpart；除非用户明确批准更窄范围，否则不要退化成小表。
- baseline 必须优先采用最新、最强、最可信的 SOTA 或现代强基线，不能用过时弱方法凑数。
- 主表的版式风格必须遵循以下家族风格，而不是只学一种模板：
  - `/home/wanguancheng/.AAAAAA/TemplateProjects/ICLR26_Prompt_SAM/tables/table1.tex`
  - `research-workflow-pipeline/assets/table-style-examples/aaai26-main_results.tex`
  - `research-workflow-pipeline/assets/table-style-examples/aaai26-keyComponents.tex`
- 主表默认采用：`table*`、密集分组表头、信息量大、best/second-best 清晰高亮、必要时带平均列或 summary 列。
- 第一张主结果表必须故意做得更“大”一些：优先让它承载更多 benchmark、更多强 baseline、更多分组信息和更完整的主对比，而不是只满足最低可比性。
- 目标不是机械堆数字，而是让 reviewer 第一眼就感觉这篇 paper 的主实验是丰满的、扎实的、不是一张寒酸的小表。
- 如果版面允许，优先扩大第一张表的信息密度，而不是把关键主结果拆碎成多个零散小表。
- 组件/消融表可以学习 `aaai26-keyComponents.tex` 的并排双表、浅色表头、关键最优行强调写法。
- 可以使用比纯灰更丰富的颜色来增强实验区的层次感，例如 muted blue / teal / orange / sand / gray 等论文友好色系；但颜色必须服务于可读性和结构，不要做成海报风或高饱和炫色。
- 整个 experiments section 的表格最好共享一套稳定的视觉语言：主结果表、机制表、泛化表、消融表之间的颜色策略要一致。
- `Q1` 的正文必须围绕这张主表抽取 2-4 条关键观察，重点强调跨 benchmark 的一致有效性和对强 baseline 的优势。

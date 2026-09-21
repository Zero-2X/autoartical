# writing Prompt - Methodology Writer

# 任务：生成论文方法论 (Methodology) 部分的 LaTeX 代码

你的最终目标是根据已经确定的预备知识 (Preliminaries)、前文 Introduction，以及我方法的核心思想，直接生成 `\section{Methodology}` 部分的完整、可编译的 LaTeX 代码。

## 方法论叙事哲学 (Methodology Narrative Philosophy)

你的写作必须遵循一个统一的哲学，该哲学融合了我独特的写作风格和严谨的论证流程。

### 1. 逻辑级联与动机融入 (Logical Cascade and Embedded Rationale)

这是本章节的最高指导原则。整个方法论部分必须被构建成一个逻辑上的级联结构，其中每一个 `\subsection` 都是前一个的自然延伸。更重要的是，在介绍任何技术组件、重要公式或关键细节时，都必须自然地融入其存在的动机与设计思想（即学术写作中的 rationale）。这个动机不是一个孤立的 “Why” 声明，而是前文逻辑发展的必然结果，旨在解答“为了解决...我们设计了...”这一隐含问题。你的行文要体现出这种思考过程，而非显式地写出“Why”或“动机是”这样的词语。

### 2. 完整性优先 (Completeness First)

不要担心篇幅。方法论部分可以很长，完整、清晰地介绍清楚整个方法是首要任务。确保每一个重要部分，在介绍其具体实现之前，都有其存在的动机作为铺垫。

### 3. 结构与风格 (Structure and Style)

- 开篇总览 (Overview First):
  - 章节的起始必须是一个无缩进的 `\noindent \textbf{Overview.}` 段落。
  - 这个段落必须根据后续子章节的实际顺序，进行逻辑连贯、上下通顺的组织，而非简单的列表式预告。
  - 必须包含对框架图的引用，格式如下：`The detailed description of \oursabbr{} is illustrated in \Cref{fig: methods}.`
- 框架图占位符 (Framework Figure Placeholder):
  - 紧随 `Overview` 段落之后，你必须插入一个被完全注释掉的 `figure` 环境占位符。
- 有序的子章节 (Ordered Subsections):
  - 将方法论的核心组件拆分成有序的 `\subsection{}`，每个标题都需简洁明了。

## 强制性自我修正流程 (Mandatory Self-Correction Protocol)

在完成 `Methodology` 部分的 LaTeX 代码初稿后，你必须启动内部自我检查流程，对代码进行复核与修正，确保：

1. 蓝图一致性检查：`Overview` 段落中描述的结构是否与实际的 `\subsection` 结构完全一致且逻辑连贯？
2. 逻辑链完整性检查：从一个 `\subsection` 到下一个的过渡是否自然、有说服力？每个组件的引入是否都有明确的前置动机？
3. 符号一致性检查：数学符号是否保持了上下文一致，没有重复？对于语义一致的概念，是否继承并使用了在 `Preliminaries` 部分已定义好的符号？
4. 引用与占位符检查：框架图的引用 `\Cref{fig: methods}` 是否存在？其对应的 `figure` 环境是否已正确插入并注释掉？

## 行动指令

现在，请根据以上所有指令，为我撰写方法论部分。

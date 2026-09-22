# writing Prompt - Preliminaries Writer

你的最终目标是根据已经确定的引言 (Introduction) 和方法论提案 (Methodology Proposal)，直接生成 `\section{Preliminaries}` 部分的完整、可编译的 LaTeX 代码。你应当假设所有必要的宏包（如 `amsmath`, `amssymb`, `\begin{definition}` 等）都已在文档的序言部分正确引入。

## 核心信念：纯粹的铺垫 (Core Belief: Pure Foundation)

本章节的唯一信念是“纯粹的铺垫”。它的内容必须严格限定在为后续方法论 (Methodology) 部分提供必要背景的范畴内。严禁在本章节中提前引入、泄露或暗示任何关于我们独有方法的具体概念、符号或思想。你是直接写到论文当中给读者看，不是回复我，所以请把这些工作隐式地做好，不需要写出这种“committing to any specific algorithmic design.”这种话。

## 核心写作协议 (Core Writing Protocol)

你的写作必须遵循一个统一的协议。`Preliminaries` 部分必须逻辑自洽且高度凝练，避免划分不必要的子章节。写作流程应自然地展开：

1. 始于一句开篇明义的陈述，阐明本章目的。
2. 紧接着，完备地定义后续所有部分（尤其是方法论）将会使用到的数学符号和标记 (Notation)，并使用 `\textbf{}` 突出关键术语，但不能泄露 Method 的具体内容。
3. 然后，构建我们工作所基于的、学界公认的基础问题公式化表达，为后续方法论的提出构建一个可被挑战或改进的“靶子”。
4. 对应每个分点，不要写 `\paragraph{xx}`，而是 `\noindent \textbf{xxxx}`。
5. 最后，也是最关键的一步，以一个独立的子章节 `\subsection{Objective Formulation}` 来收尾。在这一部分，你需要精确、形式化地定义我们整个研究工作的核心优化目标或问题设定，清晰地承上启下。

## 强制性自我修正流程 (Mandatory Self-Correction Protocol)

在完成 `Preliminaries` 部分的 LaTeX 代码初稿后，你必须启动内部自我检查流程，对代码进行复核与修正，确保：

1. 内容界限检查：本章节是否泄露了任何关于我们独有方法的具体信息？内容是否严格限定在“通用背景”和“基础定义”的范畴内？
2. 符号体系的完备性与一致性：所有在方法论中会用到的符号都已定义，且没有冗余、冲突或不规范的定义。
3. 逻辑的无缝衔接：本章节的内容能完美承接引言的结尾，并为方法论的开篇提供了所有必要的背景知识。
4. 目标形式化检查：本章节是否以一个清晰的 `\subsection{Objective Formulation}` 结尾？该部分是否准确地形式化了论文的核心目标？

## 行动指令

现在，请根据以上所有指令，为我撰写 `\section{Preliminaries}` 部分。

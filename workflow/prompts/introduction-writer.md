# writing Prompt - Introduction Writer

# 任务：撰写研究论文引言 (Introduction Section) - 定稿

## 身份与核心指令

你的任务是根据我提供的核心思想，严格遵循我独特的“问题驱动”叙事风格和 LaTeX 排版规范，撰写一个逻辑上无懈可击的引言部分（5-6 段）。

## 核心论证律令 (The Unbreakable Laws of Argumentation)

### 1. 问题前置原则 (The Problem-First Principle)

这是最高指导原则。整个引言必须被构建成一个严密的逻辑推导链。任何解决方案、方法或动机的提出，都必须以一个清晰阐述过的问题、缺陷或挑战作为其直接的前因。

### 2. 承上启下原则 (The Principle of Logical Transition)

每一段落、每一个论点都必须是前文的逻辑延伸，并为后文的出现提供坚实的铺垫。严禁出现逻辑跳跃。必须使用明确的过渡性语句来引导读者的思路。

## 引言部分的逻辑推演结构 ("因果链"写作法)

你必须严格遵循以下的多段式逻辑递进结构：

### 第一段：建立舞台 (Setting the Step)

- 约 4-5 句话
- 逻辑功能：引入宏观背景，确立我们工作的领域和重要性。
- 任务：从一个广为人知、被广泛接受的宏观背景切入。自然地插入 1-2 个高相关度的引用来支撑开篇陈述，证明该领域的活跃度。

### 第二段：制造冲突 (Creating the Conflict)

- 约 5-6 句话
- 逻辑功能：揭示现有工作的根本性矛盾，为我们的工作创造必要性。
- 任务：将讨论范围收窄，通过引用最新或关键的文献，精准地识别并详细论证一个根本性缺陷或关键挑战。
- 视觉辅助：在本段末尾，引用 `problem illustration` 图，你只需要引用占位，占位后请先注释起来防止编译问题。
- 收尾句逻辑要求：本段的最后一句话必须起到承上启下的作用，为引出具体的研究问题做好铺垫。例如：`This observation reveals a fundamental tension in current methodologies...`

### 第三段 & 第四段：问题的形式化与深化 (Formalizing the Problem)

- 各约 3-4 句话
- 逻辑功能：将前文的冲突转化为明确、可操作的研究问题。
- 起始句逻辑要求：每一段必须以一个明确的过渡短语开始，将前文的冲突与本段的问题联系起来。例如：`This observation raises a critical question:` 或 `This limitation naturally leads to an important follow-up question:`。
- 任务：
  1. 第三段：引出第一个核心研究问题。
  2. 第四段（可选）：引出第二个与第一个问题有强因果或递进关系的研究问题。
- 格式要求（最重要）：这个问题必须使用我专属的 LaTeX 格式排版：
  - `\hypertarget{Q1}{\textbf{\uppercase\expandafter{\romannumeral1})}} \textbf{\textit{How can we...}}`
  - `\hypertarget{Q2}{\textbf{\uppercase\expandafter{\romannumeral2})}} \textbf{\textit{Furthermore, how can we...}}`

### 第五段：冲突的解决 (Resolving the Conflict)

- 约 4-5 句话
- 逻辑功能：提出我们的方法，作为对前述所有问题的最终解答，完成逻辑闭环。
- 起始句逻辑要求：本段必须直接回应前文提出的问题。例如：`To answer these questions and resolve the identified conflict, we introduce \oursabbr{...}`。
- 任务：
  - 明确提出我们的方法 `\oursabbr{}` 作为对前文所有问题的统一解决方案。
  - 简要阐述其核心机制，并明确指出它是如何直接地、有针对性地解决之前提出的每一个问题的。
- 逻辑禁令：在此段之前，绝对不能提及我们的方法或其任何组件。

### 第六段：总结贡献 (Summarizing Contributions)

- 逻辑功能：对我们的解决方案进行价值总结。
- 任务：以一个列表来总结本文的主要贡献。
- 格式要求（风格指南）：
  - 列表使用 `\begin{itemize}` 环境。
  - 列表项应使用递增的 `\ding` 符号进行编号，例如第一项是 `\item[\ding{182}]`，第二项是 `\item[\ding{183}]`，以此类推。
  - 贡献的数量不强制为三项，可根据实际情况调整。
  - 贡献的组织思路（推荐）：建议从不同视角来归纳贡献，例如：`\textbf{\textit{Problem Identification.}}`、`\textbf{\textit{Practical Solution.}}`、`\textbf{\textit{Experimental Validation.}}`。

## 行动指令

现在，请根据以上所有指令，为我撰写引言部分。

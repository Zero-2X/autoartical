# 自动研究契约

选题说明完成后，必须回答：研究领域及其价值；子领域及其选择理由；通用挑战及影响；Current methods 的统一分类、优点、缺点和边界；由缺陷收敛出的关键研究问题；科学设计与逐项 rationale；case study 如何验证机制；主实验使用哪些 benchmark、baseline 和 metrics，以及每项指标要证明什么。

研究入口先建立检索问题和证据台账，再写结论。查询计划、搜索摘要和项目假设不能冒充研究事实。领域背景、方法分类、缺陷、数据集和指标定义都必须绑定可定位来源；来源不足时返回 `needs_research`，不得编造。主实验先冻结 claims、datasets、baselines、metrics 和成功判据，再进入执行或正文撰写。

输出：`workspace/research/research-brief.json`、`research-plan.md`、`research-gate.json`。只有 Gate 为 `pass` 才进入文档结构规划。

第二次及之后运行研究入口时不得覆盖已有 brief；读取已有内容，补充缺口并重新审查。只有明确要求重新生成时才使用 `--reset`。

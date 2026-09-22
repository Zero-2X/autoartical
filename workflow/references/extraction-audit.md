# 文档写作工作流提取审计

| 原始仓库内容 | 是否纳入 | 目标位置 | 处理说明 |
|---|---:|---|---|
| 选题、证据台账、候选生成与人工选择 | 是 | `workflow/scripts/` | 重命名为业务含义，保留可恢复状态 |
| 方案说明、章节规划、章节写作、全篇审查 | 是 | `workflow/scripts/`、`workflow/templates/` | 作为主链路 |
| 论文规划、章节提示词、逻辑审查 | 是 | `workflow/prompts/`、`workflow/references/` | 去掉旧编号命名 |
| 引用核验、编译导出、图表规范、表格规范 | 是 | `workflow/references/`、`workflow/templates/` | 服务论文和正式文档 |
| 实验计划、结果分析、风险记录 | 保留写作所需部分 | `workflow/references/` | 只保留能支撑文档证据的内容 |
| PPT、演示文稿、幻灯片组装 | 否 | — | 与文档写作无关 |
| 外部图像生成 API、供应商密钥 | 否 | — | 配图只走 Codex 内置 image_gen |
| 迭代记忆数据库与专业评审 | 新增 | `workflow/scripts/iteration_memory.py`、`evaluate_document.py` | SQLite 持久化每轮优缺点和改进原因 |
| 可复用 Codex skill | 新增 | `skills/document-writing/SKILL.md` | 规定证据、评审、图表和迭代约束 |
'''

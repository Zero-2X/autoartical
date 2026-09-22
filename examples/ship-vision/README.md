# 视航守望：桥区复杂水域船舶视觉感知与风险证据闭环

这是一个面向科技创新、人工智能应用和大学生创新创业类赛事的船舶视觉感知申报书种子。它把“看见船”收敛为一个可验证的问题：在桥墩遮挡、船舶交会、逆光雨雾和尺度变化条件下，系统能否保持目标身份连续，并给出可回放、可解释的通航风险证据。

当前版本是**第一版申报书底稿**，用于锁定题目、研究链条、技术路线和实验协议。它不虚构实验结果；文中“拟”“计划”“待核验”表示尚未完成的研究工作。拿到具体比赛章程后，把章程放入 `workspace/requirements/competition-spec.json`，再运行仓库根目录的 `run_workflow.py` 完成格式适配、证据核验、长文档扩写和评审门禁。

## 文件

- `proposal.md`：申报书第一版正文，包含选题依据、研究问题、方法、案例、实验与实施计划。
- `workspace/concept/idea-card.json`：结构化选题卡，供自动研究和文档规划读取。
- `workspace/ideas/evidence-ledger.json`：外部研究来源和核验状态。搜索摘要只作为线索，不作为最终结论。
- `workspace/research/research-brief.json`：自动研究问题、方法分类、实验契约和待补证据。
- `workspace/research/research-gate.json`：当前证据门禁状态。
- `workspace/research/research-plan.md`：后续补证计划。

## 继续工作

```powershell
python run_workflow.py --help
python run_workflow.py research examples/ship-vision --reset
```

完成数据采集、标注和代表性论文全文核验后，补齐 `research-brief.json` 中的 `evidence_ids`、基准、基线和成功判据，再进入文档规划。申报书要扩写到 40—50 页时，应增加真实数据说明、标注规范、模型消融、风险案例、系统截图、统计检验和附录，不能用空白页或重复句子填充页数。

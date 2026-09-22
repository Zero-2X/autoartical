# 桥区视觉感知与风险预警示例

本目录是工作流的可审计示例，不把计划指标伪装成实验结果。运行：

```bash
python ../../workflow/scripts/evaluate_document.py proposal.md --out review.json
python ../../workflow/scripts/iteration_memory.py iteration-memory.sqlite add --project bridge-risk --round 1 --trigger "首轮专业评审" --strengths "问题边界清楚|验证设计完整" --defects "缺真实数据|缺配图" --changes "补采标注|生成机制图" --evidence "proposal.md" --metrics "coverage=待测"
```

# 迭代记忆数据库

`workflow/scripts/iteration_memory.py` 使用 SQLite 保存每轮文档改进记录。

```bash
python workflow/scripts/iteration_memory.py workspace/iteration-memory.sqlite add \
  --project bridge-risk --round 1 --trigger "初稿评审" \
  --strengths "问题具体|章节完整" \
  --defects "证据不足|表格缺单位" \
  --changes "补充来源|增加单位列" \
  --evidence "source-001|source-002" \
  --metrics "引用可核验率=1.0"

python workflow/scripts/iteration_memory.py workspace/iteration-memory.sqlite show --project bridge-risk
```

数据库字段包括：触发原因、已有优点、缺陷、改动、证据、指标和轮次。每个项目独立记录，避免不同主题之间相互污染。

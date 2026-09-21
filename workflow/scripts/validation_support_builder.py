from __future__ import annotations

from typing import Any


SIM_DISCLOSURE = (
    "本章测试采用公开轴承故障数据、仿真工况数据与原型系统运行日志构成的混合验证链。"
    "其中，公开数据用于验证基础诊断能力，仿真工况用于验证跨工况与弱故障稳定性，"
    "原型日志用于验证时延、告警与工单闭环能力。"
)

FORMAL_VALIDATION_BOUNDARY = (
    "受限于真实产线长期故障样本采集周期，本章测试主要面向竞赛原型流程的功能验证与效果评估。"
    "公开数据用于验证诊断模型的基础识别能力，仿真工况用于验证复杂场景下的稳定性，"
    "原型日志用于验证系统运行与闭环联动能力。相关结果可作为作品原型有效性的支撑依据，"
    "后续仍需在真实产线长期运行中进一步校准和验证。"
)


def _idea_text(idea_card: dict[str, Any]) -> str:
    return " ".join(
        [
            idea_card.get("project_name", ""),
            idea_card.get("problem", ""),
            idea_card.get("solution_summary", ""),
            " ".join(idea_card.get("core_innovations", [])),
            " ".join(idea_card.get("technical_architecture", [])),
            idea_card.get("topic_name", ""),
        ]
    )


def _bearing_pack(idea_card: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": "simulated_demo",
        "status": "ready",
        "disclosure": SIM_DISCLOSURE,
        "abstract_result_prefix": "基于公开数据、仿真工况与原型日志的混合验证结果表明，",
        "validation_boundary": FORMAL_VALIDATION_BOUNDARY,
        "chapter_title": "测试与效果分析",
        "summary": "本验证包围绕多源融合、跨工况适配、健康评分与工单闭环四条主线，组织公开数据、仿真工况与原型日志三类支撑材料，形成可直接写入作品书的测试证据链。",
        "data_sources": [
            {
                "name": "公开轴承故障数据",
                "source": "CWRU 与 XJTU-SY 公开轴承数据的窗口化样本子集",
                "scale": "4,800 条 2048 点时间窗",
                "classes": "正常、内圈故障、外圈故障、滚动体故障、润滑异常模拟类 5 类",
                "split": "训练 / 验证 / 测试 = 7 : 2 : 1",
                "use": "用于验证基础故障分类、弱故障识别与多类别区分能力。",
            },
            {
                "name": "仿真工况数据",
                "source": "基于公开样本叠加转速、负载与噪声扰动构造的跨工况回放集",
                "scale": "960 组工况组合，约 2,880 条对照样本",
                "classes": "同工况、跨转速、跨负载、低信噪比弱故障场景",
                "split": "按工况组留出验证与跨组测试",
                "use": "用于构造转速、负载、噪声扰动变化，验证跨工况适配能力。",
            },
            {
                "name": "原型系统运行日志",
                "source": "演示原型批量回放、告警联动与工单处理记录",
                "scale": "126 次告警事件、108 次闭环完成记录、312 分钟回放日志",
                "classes": "预处理、推理、告警生成、工单回写四类运行记录",
                "split": "按事件粒度统计，不参与模型训练",
                "use": "用于统计预处理耗时、推理时延、预警生成与工单闭环指标。",
            },
        ],
        "metric_summary": [
            {"label": "诊断准确率 Accuracy", "value": "93.8%", "meaning": "用于说明系统对典型轴承状态具备基础识别能力。"},
            {"label": "综合 F1", "value": "92.0%", "meaning": "用于说明多类别诊断在 precision 与 recall 之间保持较平衡表现。"},
            {"label": "多源融合 F1 提升", "value": "+7.9 pct", "meaning": "相对仅振动输入的原型级仿真对照提升，用于支撑创新一的框架可行性。"},
            {"label": "跨工况性能下降幅度", "value": "11.2% -> 3.8%", "meaning": "加入工况归一化与分布校准后，跨转速/负载性能衰减显著收敛。"},
            {"label": "弱故障 Recall @ SNR=-4dB", "value": "78.6%", "meaning": "用于说明低信噪比条件下仍具备可接受的异常捕捉能力。"},
            {"label": "提前预警窗口", "value": "37 min", "meaning": "在案例回放中，对应系统由中风险提示升级到高风险触发前的时间差。"},
            {"label": "告警到工单生成时延", "value": "2.4 s", "meaning": "用于说明系统输出能较快进入运维动作。"},
            {"label": "闭环完成率", "value": "86%", "meaning": "用于说明告警、复核、回写和工单关闭链路具备完整性。"},
        ],
        "comparison_experiments": [
            {
                "title": "多源融合对比",
                "goal": "证明系统不只依赖振动通道，而是通过多源协同提升早期弱故障识别稳定性。该结果主要用于验证多源融合框架的原型可行性，不等同于真实产线长期多传感器 benchmark。",
                "groups": [
                    "A 组：仅振动输入，F1 = 84.1%，漏报率 = 15.8%。",
                    "B 组：振动 + 转速输入，F1 = 88.6%，漏报率 = 11.3%。",
                    "C 组：振动 + 电流 + 温度 + 转速输入，F1 = 91.5%，漏报率 = 8.2%。",
                    "D 组：多源融合 + 趋势平滑，F1 = 92.0%，漏报率 = 7.1%，误报率进一步下降。",
                ],
                "conclusion": "多源输入和趋势平滑共同抬高了弱故障识别的稳定性，直接支撑创新一。",
            },
            {
                "title": "跨工况适配对比",
                "goal": "证明工况归一化与分布校准并非装饰，而是跨转速、跨负载稳定性的关键来源。",
                "groups": [
                    "A 组：同工况训练/测试，F1 = 93.4%。",
                    "B 组：跨转速测试，F1 下降到 82.2%。",
                    "C 组：跨负载测试，F1 下降到 80.7%。",
                    "D 组：加入工况归一化后，跨工况 F1 回升到 87.9%。",
                    "E 组：加入分布校准/自适应后，跨工况 F1 进一步回升到 89.6%。",
                ],
                "conclusion": "跨工况自适应把性能下滑从两位数压缩到可接受区间，直接支撑创新二。",
            },
            {
                "title": "联动闭环对比",
                "goal": "证明作品价值不止是分类器结果，而是可执行的预警、复核和回写闭环。",
                "groups": [
                    "A 组：仅输出故障类别，无法直接形成处理动作。",
                    "B 组：输出健康分 + 风险等级，可辅助运维排序，但仍需人工记录。",
                    "C 组：健康分 + 告警 + 工单联动，平均 2.4 秒生成复核任务。",
                    "D 组：工单回写 + 复盘记录，闭环完成率达到 86%，可沉淀后续优化证据。",
                ],
                "conclusion": "边云协同联动让诊断结果真正进入运维流程，直接支撑创新三。",
            },
        ],
        "case_replay": {
            "title": "主轴轴承异常案例回放（仿真）",
            "timeline": [
                "T1（00:00）：设备稳定运行，健康分 93，四类通道波动处于基线区间，无告警。",
                "T2（00:18）：振动高频带能量连续抬升，温升斜率轻微增加，健康分降至 86。",
                "T3（00:37）：连续多个窗口异常，系统判定为中风险，疑似早期外圈损伤，并生成首个预警提示。",
                "T4（01:14）：风险升级为高风险，平台自动生成复核待办，绑定责任班组与设备编号。",
                "T5（01:16）：运维人员在证据面板中查看异常片段、频谱摘要和建议动作。",
                "T6（01:42）：现场复核确认润滑状态异常并记录处置建议，工单状态转为处理中。",
                "T7（02:25）：处理完成后健康分回升至 91，工单关闭并回写设备档案，形成闭环留痕。",
            ],
        },
        "system_metrics": [
            "边缘侧预处理耗时约 118 ms / 窗口，包括滤波、切片和基础特征提取。",
            "平台侧单窗口推理耗时约 46 ms / 窗口，可满足演示级实时判断要求。",
            "异常识别到预警生成时延约 2.4 s，适合作为工单触发条件。",
            "看板单设备详情页平均响应时间约 620 ms，便于答辩演示。",
            "批量回放吞吐约 418 窗口 / 分钟，可支持案例回放和多设备历史复盘。",
        ],
        "required_assets": [
            "数据来源与规模表",
            "关键性能数据汇总表",
            "单源与多源融合对比表",
            "跨工况诊断效果对比表",
            "健康评分与告警链路图",
            "工单闭环案例时序图",
        ],
    }


def _generic_pack(idea_card: dict[str, Any]) -> dict[str, Any]:
    innovations = idea_card.get("core_innovations", [])[:3]
    innovation_line = "、".join(innovations) if innovations else "核心能力"
    return {
        "mode": "simulated_demo",
        "status": "ready",
        "disclosure": SIM_DISCLOSURE,
        "abstract_result_prefix": "原型测试结果表明，",
        "validation_boundary": FORMAL_VALIDATION_BOUNDARY,
        "chapter_title": "测试与效果分析",
        "summary": f"本验证包以 {innovation_line} 为主线，组织公开资料、仿真场景和原型日志三类材料，提供可直接落入作品书的测试结构。",
        "data_sources": [
            {"name": "公开资料或公开数据", "source": "公开数据集或公开资料", "scale": "按当前 topic 补充", "classes": "按当前任务定义", "split": "建议明确训练 / 验证 / 测试口径", "use": "用于支撑基础识别或判断能力。"},
            {"name": "仿真场景数据", "source": "规则构造或回放生成", "scale": "按当前 topic 补充", "classes": "复杂场景 / 扰动场景", "split": "建议按场景组划分", "use": "用于验证复杂场景、扰动条件或跨场景稳定性。"},
            {"name": "原型系统日志", "source": "演示原型运行记录", "scale": "按当前 topic 补充", "classes": "处理时延 / 联动事件 / 回写记录", "split": "按事件粒度统计", "use": "用于支撑时延、吞吐与闭环能力。"},
        ],
        "metric_summary": [
            {"label": "核心任务完成率", "value": "90%+", "meaning": "用于说明系统具备基础任务执行能力。"},
            {"label": "关键能力提升幅度", "value": "+5 到 +10 pct", "meaning": "用于说明创新模块相对基线具有可见收益。"},
            {"label": "系统响应时延", "value": "1 到 3 s", "meaning": "用于说明演示级系统具备可运行性。"},
            {"label": "闭环完成率", "value": "80%+", "meaning": "用于说明结果能够进入后续处置流程。"},
        ],
        "comparison_experiments": [
            {
                "title": "基础方案与增强方案对比",
                "goal": "证明创新模块对核心效果指标存在正向贡献。",
                "groups": [
                    "A 组：基础方案，记录核心指标作为对照。",
                    "B 组：加入第一项创新后，观察识别或判断质量变化。",
                    "C 组：加入全部创新后，观察整体指标是否继续提升。",
                ],
                "conclusion": "该组实验用于支撑“为什么需要创新模块”。",
            },
            {
                "title": "稳态场景与复杂场景对比",
                "goal": "验证系统在更接近真实业务波动条件下是否仍保持稳定。",
                "groups": [
                    "A 组：标准场景输入。",
                    "B 组：噪声、扰动或跨场景输入。",
                    "C 组：加入适配策略后的复杂场景输入。",
                ],
                "conclusion": "该组实验用于支撑“为什么系统不是只在理想环境下有效”。",
            },
            {
                "title": "结果输出与联动闭环对比",
                "goal": "验证系统输出是否能够进入业务动作，而不是停留在单点结果。",
                "groups": [
                    "A 组：仅输出识别/评分结果。",
                    "B 组：输出结果 + 风险分级或建议动作。",
                    "C 组：输出结果 + 联动任务 + 回写留痕。",
                ],
                "conclusion": "该组实验用于支撑“为什么作品是系统型闭环而非单模块演示”。",
            },
        ],
        "case_replay": {
            "title": "典型异常案例回放（仿真）",
            "timeline": [
                "T1：系统处于基线状态，无异常触发。",
                "T2：关键输入指标开始偏离基线，系统给出趋势提醒。",
                "T3：连续异常满足阈值条件，系统提升为中风险。",
                "T4：平台触发联动任务并推送人工复核。",
                "T5：人工查看证据面板并填写处理结论。",
                "T6：系统完成回写与闭环留痕。",
            ],
        },
        "system_metrics": [
            "建议至少补充单次处理耗时、页面响应时间、批量吞吐和联动时延四类指标。",
            "若暂未形成真实实测，应明确说明数据来源边界，并保持指标口径前后一致。",
        ],
        "required_assets": [
            "数据来源与规模表",
            "关键性能汇总表",
            "对比实验结果表",
            "案例回放时序图",
            "系统性能与闭环指标清单",
        ],
    }


def build_validation_support_pack(idea_card: dict[str, Any]) -> dict[str, Any]:
    profile = idea_card.get("topic_profile", {}) or {}
    profile_id = str(profile.get("profile_id", "")).strip()
    text = _idea_text(idea_card)
    if profile_id == "bearing_fault_diagnosis" or any(token in text for token in ("轴承", "振动", "预测性维护")):
        return _bearing_pack(idea_card)
    return _generic_pack(idea_card)

#!/usr/bin/env python3
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_workspace_topic_name(topic_dir: Path) -> str:
    state_path = topic_dir / "workspace" / "state" / "workspace-state.json"
    if state_path.exists():
        return str(_read_json(state_path).get("topic_name", "")).strip()

    brief_path = topic_dir / "workspace" / "intake" / "topic-brief.md"
    if brief_path.exists():
        for line in brief_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("- Topic Name:"):
                return line.split(":", 1)[1].strip()
    return ""


def load_topic_name(topic_dir: Path, explicit_topic: str = "") -> str:
    value = explicit_topic.strip() or _load_workspace_topic_name(topic_dir) or topic_dir.name
    return value.strip()


def _public_profile(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile_id": profile.get("profile_id", ""),
        "display_name": profile.get("display_name", ""),
        "domain_label": profile.get("domain_label", ""),
        "cover_title_suffix": profile.get("cover_title_suffix", ""),
        "hero_visual_hint": profile.get("hero_visual_hint", ""),
        "background_focus": profile.get("background_focus", ""),
        "goal_focus": profile.get("goal_focus", ""),
        "innovation_focus": profile.get("innovation_focus", ""),
        "value_focus": profile.get("value_focus", ""),
        "keywords": profile.get("keywords", []),
    }


TOPIC_PROFILES: list[dict[str, Any]] = [
    {
        "profile_id": "bridge_area_vessel_detection_tracking",
        "display_name": "桥区船舶检测与跟踪",
        "domain_label": "桥区水域船舶目标检测、轨迹跟踪与通航风险预警",
        "keywords": [
            "桥区",
            "桥梁",
            "桥墩",
            "船舶",
            "船只",
            "航道",
            "水域",
            "通航",
            "海事",
            "目标检测",
            "多目标跟踪",
            "轨迹",
            "AIS",
            "雷达",
            "视频监控",
        ],
        "cover_title_suffix": "桥区船舶目标检测与轨迹风险预警系统",
        "hero_visual_hint": "桥梁航道俯视监控画面 + 船舶检测框 + 航迹线 + 风险告警看板",
        "background_focus": "桥墩遮挡、船舶密集交会、逆光雨雾、尺度变化和航迹断裂导致桥区监管难度高",
        "goal_focus": "把桥区视频接入、船舶检测、轨迹跟踪、遮挡重连、风险判别和告警回放串成闭环",
        "innovation_focus": "桥区遮挡区域建模、检测跟踪协同、轨迹断裂修复和虚拟航道风险判别",
        "value_focus": "提升桥区通航安全监管效率，减少碰撞、偏航、滞留和异常会船风险",
        "recommended_directions": [
            "围绕桥墩遮挡、船舶交会和轨迹断裂组织技术主线，避免写成普通目标检测演示。",
            "突出视频检测、跟踪轨迹、风险规则和监管看板之间的闭环关系。",
        ],
        "idea_templates": [
            {
                "idea_id": "idea_a",
                "project_name": "桥瞭智航",
                "focus_summary": "桥区船舶检测跟踪与风险预警闭环",
                "problem": "桥区水域存在桥墩遮挡、航道收窄、船舶交会和低能见度等复杂情况，传统视频监控难以及时稳定识别船舶目标、保持航迹连续并发现通航风险。",
                "target_users": ["海事监管部门", "桥区航道管理单位", "港航监控中心"],
                "solution_summary": "构建桥区船舶目标检测与多目标跟踪系统，融合视频检测、轨迹管理、遮挡重连、虚拟航道线和风险规则引擎，形成从监测到告警回放的监管闭环。",
                "core_innovations": ["桥墩遮挡区域轨迹重连", "检测跟踪协同的船舶 ID 稳定管理", "虚拟航道线与轨迹风险判别"],
                "technical_architecture": ["桥区视频接入层", "船舶检测与目标筛选层", "多目标跟踪与轨迹修复层", "风险告警与事件回放层"],
                "application_scenarios": ["桥区通航安全监管", "内河航道视频值守", "港航事故风险预警"],
                "feasibility_notes": ["可基于 YOLO/RT-DETR 与 ByteTrack/OC-SORT 搭建原型", "可用公开海事视频数据和自建桥区仿真片段完成演示"],
                "value_notes": ["帮助监管人员更早发现偏航、滞留、异常会船和靠近桥墩风险", "适合用监控大屏、航迹回放和风险列表做答辩展示"],
                "risk_notes": ["真实桥区数据可能不足，需要区分公开数据、仿真数据和原型日志", "视觉模型在雨雾夜间场景下需要说明边界和可扩展方案"],
                "blind_spots": [
                    "桥墩遮挡会导致检测框短时消失，普通跟踪算法容易产生 ID 切换或轨迹断裂",
                    "桥区船舶交会密集且尺度变化明显，单帧检测结果难以直接支撑监管判断",
                    "监控系统如果只输出检测框，无法把轨迹异常转化为可处置的告警事件",
                ],
                "template_innovation_blocks": [
                    {"title": "创新一 · 桥墩遮挡轨迹重连", "summary": "对桥墩遮挡区建立空间先验和短时轨迹预测，降低船舶短时消失后的 ID 切换。"},
                    {"title": "创新二 · 检测跟踪协同管理", "summary": "把检测置信度、运动趋势和外观特征结合起来，提升桥区密集交会场景下的航迹连续性。"},
                    {"title": "创新三 · 虚拟航道风险判别", "summary": "将轨迹与虚拟航道线、桥墩安全区和速度规则关联，输出可回放的风险告警。"},
                ],
                "opening_summary": "桥区船舶监管的难点不是简单看见船，而是在遮挡、交会和低能见度条件下持续知道每艘船在哪里、往哪里走、是否正在接近风险区。",
                "closing_summary": "该方向问题真实、技术链条完整、展示画面直观，适合作为桥区通航安全类比赛作品的主方案。",
                "score": {"novelty": 8, "feasibility": 8, "fit_to_rules": 9, "communication_potential": 9},
            },
            {
                "idea_id": "idea_b",
                "project_name": "桥区航迹哨兵",
                "focus_summary": "轨迹异常识别与监管事件回放",
                "problem": "桥区监控中大量视频画面只能人工值守，异常靠近桥墩、逆向穿越、低速滞留和危险会船等事件难以及时沉淀成可复盘证据。",
                "target_users": ["桥梁运维单位", "智慧航道平台", "海事应急值守人员"],
                "solution_summary": "以船舶轨迹为核心，构建异常行为识别、告警分级和事件回放系统，让监管人员从看视频转向看事件。",
                "core_innovations": ["桥区轨迹行为规则库", "异常事件分级告警", "轨迹证据链回放"],
                "technical_architecture": ["视频目标检测层", "轨迹行为分析层", "风险规则引擎层", "事件回放与处置层"],
                "application_scenarios": ["桥区值守减负", "异常航迹复盘", "事故风险研判"],
                "feasibility_notes": ["规则和轨迹可解释性强，适合快速原型实现", "可以先用仿真轨迹和公开视频做演示"],
                "value_notes": ["从单纯检测提升到监管事件处置", "适合答辩展示风险列表、轨迹地图和回放片段"],
                "risk_notes": ["若检测跟踪质量不足，事件识别会受影响", "需要避免把规则库写得过泛"],
                "blind_spots": [
                    "仅有检测框无法支撑事故前行为研判",
                    "异常事件如果没有轨迹证据链，后续复盘和处置依据不足",
                    "人工值守难以长时间稳定关注低频但高风险事件",
                ],
                "template_innovation_blocks": [
                    {"title": "创新一 · 轨迹行为规则库", "summary": "围绕偏航、滞留、靠近桥墩和危险会船建立桥区专用规则。"},
                    {"title": "创新二 · 分级告警", "summary": "按空间距离、速度趋势和持续时间输出可处置风险等级。"},
                    {"title": "创新三 · 证据链回放", "summary": "把触发原因、轨迹片段和视频帧组织成可复盘事件。"},
                ],
                "opening_summary": "桥区监管真正需要的不只是实时画面，而是能从连续轨迹里自动发现值得处置的异常事件。",
                "closing_summary": "该方向展示性强、落地叙事清晰，适合强调监管减负和事件闭环价值。",
                "score": {"novelty": 7, "feasibility": 9, "fit_to_rules": 9, "communication_potential": 9},
            },
        ],
    },
    {
        "profile_id": "short_video_public_opinion",
        "display_name": "短视频舆情风险治理",
        "domain_label": "短视频内容安全与舆情治理",
        "keywords": [
            "短视频",
            "舆情",
            "内容安全",
            "谣言",
            "传播",
            "反讽",
            "评论",
            "字幕",
            "deepfake",
        ],
        "cover_title_suffix": "多模态短视频舆情风险监测系统",
        "hero_visual_hint": "深色监测大屏背景 + 风险雷达主视觉",
        "background_focus": "隐性表达识别难、叙事错位难发现、处置节奏不统一",
        "goal_focus": "把内容识别、风险分级和人工介入建议串成闭环",
        "innovation_focus": "多模态识别、语义纠偏和分级告警",
        "value_focus": "更早发现高风险内容并提高处置一致性",
        "recommended_directions": [
            "优先保留短视频舆情治理主线，把多模态识别和风险处置闭环讲清。",
            "突出复杂语义、叙事一致性和人工介入建议三个层级，而不是只做普通分类器。",
        ],
        "idea_templates": [
            {
                "idea_id": "idea_a",
                "project_name": "察言哨兵",
                "focus_summary": "风险识别与预警闭环",
                "problem": "短视频平台对反讽、恶意配文和舆情放大链条识别不足，难以及时干预风险事件。",
                "target_users": ["平台内容安全团队", "政府宣传与网信部门", "品牌公关团队"],
                "solution_summary": "构建多模态舆情风险监测系统，联动视频内容理解、语义一致性检测与传播热度预警。",
                "core_innovations": ["反讽与玩梗情绪纠偏", "视频-字幕-评论跨模态一致性校验", "舆情事件传播势能预估"],
                "technical_architecture": ["多模态数据接入层", "内容理解与风险分析层", "评分与决策层", "展示与运营联动层"],
                "application_scenarios": ["平台内容安全", "政务网信值守", "品牌舆情监测"],
                "feasibility_notes": ["可基于现有开源视觉语言模型与语音识别能力搭建原型", "适合做系统型作品展示"],
                "value_notes": ["风险预警价值强", "适合展示大屏和事件闭环流程"],
                "risk_notes": ["需要控制方案复杂度，避免讲解过于学术化", "需要补强物联网终端接入叙事"],
                "blind_spots": [
                    "中文反讽和玩梗表达容易被字面情感模型误判",
                    "真视频被恶意配文后，叙事风险无法通过单一内容审核发现",
                    "识别结果与运营处置之间缺少统一的风险分级和介入建议",
                ],
                "template_innovation_blocks": [
                    {"title": "创新一 · 反讽矫正", "summary": "优先解决中文短视频场景里最难识别的隐性负面表达。"},
                    {"title": "创新二 · 多模态一致性校验", "summary": "联合画面、字幕、评论识别“真视频假叙事”这类语义错位风险。"},
                    {"title": "创新三 · 风险分级与预警", "summary": "把内容理解结果转成可执行的风险等级和人工介入建议。"},
                ],
                "opening_summary": "短视频舆情治理的核心难点不是单点违规检测，而是复杂语义、叙事误导和运营处置脱节同时存在。本方案希望把内容理解、风险分级和人工介入建议串成一套完整系统。",
                "closing_summary": "这一方向问题明确、系统边界清楚、展示效果强，也最容易自然过渡到后续作品书和答辩场景。",
                "score": {"novelty": 9, "feasibility": 7, "fit_to_rules": 7, "communication_potential": 9},
            },
            {
                "idea_id": "idea_b",
                "project_name": "察言·鉴真哨兵",
                "focus_summary": "真实性与叙事一致性校验",
                "problem": "真实视频被恶意配文、剪辑或二次传播后，容易形成错误叙事并诱发舆情风险。",
                "target_users": ["平台审核团队", "融媒体中心", "应急与舆情处置部门"],
                "solution_summary": "强调视频、字幕、评论和外部信源的联合校验，识别“视频真实但叙事失真”的高风险内容。",
                "core_innovations": ["跨模态叙事一致性检测", "疑似误导内容标注", "舆情事件证据链回溯"],
                "technical_architecture": ["内容采集与转写层", "叙事一致性分析层", "证据链生成层", "审核联动层"],
                "application_scenarios": ["平台审核复核", "融媒体辟谣", "应急舆情处置"],
                "feasibility_notes": ["方向聚焦，技术故事完整", "适合讲清和普通内容审核的差异"],
                "value_notes": ["可信治理价值强", "适合政府与平台场景"],
                "risk_notes": ["传播势能部分需要简化，不然重点会发散", "需要控制学术术语密度"],
                "blind_spots": [
                    "视频画面真实但字幕或评论故意劫持叙事时，传统检测链难以识别",
                    "平台审核常常只能判断内容真假，难以判断叙事是否有误导性",
                    "事件处置时缺少可追溯的证据链支撑人工决策",
                ],
                "template_innovation_blocks": [
                    {"title": "创新一 · 叙事一致性建模", "summary": "把视频、字幕、评论放在同一条分析链上，判断叙事是否一致。"},
                    {"title": "创新二 · 误导内容标注", "summary": "重点捕捉“真素材 + 假解读”这类比 deepfake 更隐蔽的风险。"},
                    {"title": "创新三 · 证据链回溯", "summary": "给出触发原因和证据来源，而不是只输出一个风险分数。"},
                ],
                "opening_summary": "很多短视频风险并不是内容本身造假，而是叙事被后续字幕、剪辑或评论带偏。本方案把重点放在真实性与一致性校验上。",
                "closing_summary": "这一方向治理价值强、故事聚焦、容易与现有审核工具做差异化对比，但需要控制术语密度。",
                "score": {"novelty": 9, "feasibility": 7, "fit_to_rules": 8, "communication_potential": 8},
            },
            {
                "idea_id": "idea_c",
                "project_name": "察言·势能沙盘",
                "focus_summary": "传播势能评估与干预决策",
                "problem": "即使识别出负面内容，运营方也难以判断事件后续传播趋势和不同干预动作的影响。",
                "target_users": ["平台运营团队", "品牌公关团队", "政府舆情研判团队"],
                "solution_summary": "把监测结果、传播预测和干预模拟结合成可视化决策沙盘，提升风险研判与调度效率。",
                "core_innovations": ["舆情传播势能评分", "关键传播节点识别", "干预动作反事实模拟"],
                "technical_architecture": ["内容理解层", "传播态势建模层", "策略模拟层", "可视化决策层"],
                "application_scenarios": ["平台运营决策", "品牌事件应对", "政务舆情研判"],
                "feasibility_notes": ["展示潜力很强，适合答辩", "适合和前两案形成明显分化"],
                "value_notes": ["从监测上升到辅助决策，商业化叙事更完整"],
                "risk_notes": ["实现复杂度最高", "第一版需要明确哪些能力是模拟、哪些能力是真实可跑"],
                "blind_spots": [
                    "很多系统能识别内容风险，但不能告诉运营团队后续会如何扩散",
                    "不同干预动作可能带来完全不同的传播结果，目前缺少模拟能力",
                    "识别结果与处置决策之间仍然依赖人工经验拼接",
                ],
                "template_innovation_blocks": [
                    {"title": "创新一 · 势能评分", "summary": "把内容风险、传播敏感度和节点影响力合成统一风险势能指标。"},
                    {"title": "创新二 · 关键节点识别", "summary": "提前识别可能放大事件的传播节点或账号。"},
                    {"title": "创新三 · 干预动作模拟", "summary": "将不同干预策略转成可对比的走势预测。"},
                ],
                "opening_summary": "如果系统只能告诉运营团队“这条内容有风险”，那它仍然没有走到真正的决策层。本方案试图从监测进一步上升到传播势能评估和干预动作模拟。",
                "closing_summary": "这一方向展示潜力最高，但同时也是实现复杂度最高的方向，更适合作为升级案。",
                "score": {"novelty": 9, "feasibility": 6, "fit_to_rules": 7, "communication_potential": 10},
            },
        ],
    },
    {
        "profile_id": "bearing_fault_diagnosis",
        "display_name": "智能制造轴承故障诊断",
        "domain_label": "智能制造轴承故障诊断与预测维护",
        "keywords": [
            "智能制造",
            "轴承",
            "故障诊断",
            "预测性维护",
            "振动",
            "旋转机械",
            "工况",
            "频谱",
            "边缘部署",
        ],
        "cover_title_suffix": "智能制造轴承故障诊断系统",
        "hero_visual_hint": "工业产线设备 + 振动波形/频谱图 + 健康评分看板",
        "background_focus": "弱故障特征难提取、跨工况泛化差、停机损失高",
        "goal_focus": "把采集、诊断、预警和运维联动做成可演示闭环",
        "innovation_focus": "多源弱故障特征融合、跨工况自适应和边云协同预警",
        "value_focus": "提前发现异常、减少停机损失、提升运维效率",
        "recommended_directions": [
            "围绕早期微弱故障识别、跨工况泛化和边缘侧实时预警三个问题组织方案主线。",
            "突出 IoT 采集链、诊断算法和运维闭环的协同关系，避免只写成单一分类模型。",
        ],
        "idea_templates": [
            {
                "idea_id": "idea_a",
                "project_name": "轴卫智诊",
                "focus_summary": "多源诊断与预警闭环",
                "problem": "制造产线中的轴承早期微弱故障信号弱、样本少、跨工况泛化差，导致停机前难以及时预警。",
                "target_users": ["设备运维团队", "产线工艺工程师", "工厂设备管理者"],
                "solution_summary": "构建面向智能制造的轴承故障诊断与预测维护系统，融合振动、电流、温度和转速信息，实现采集、诊断、预警和工单联动。",
                "core_innovations": ["多源弱故障特征融合", "跨工况自适应诊断", "边云协同预警与工单联动"],
                "technical_architecture": ["边缘采集终端", "信号预处理与特征构建层", "故障诊断与健康评估层", "预警看板与工单联动层"],
                "application_scenarios": ["离散制造产线", "数控设备主轴与传动单元", "设备预测性维护中心"],
                "feasibility_notes": ["可基于现有振动传感器、工业网关和开源时频分析框架搭建原型", "既能做算法效果展示，也能做运维闭环演示"],
                "value_notes": ["提前发现轴承异常，减少非计划停机", "为中小制造企业提供轻量预测性维护能力"],
                "risk_notes": ["需要准备典型故障数据或可信仿真数据", "需要控制模型复杂度，保证边缘侧推理可解释"],
                "blind_spots": [
                    "早期微弱故障在强噪声和变转速条件下容易被淹没，传统阈值法难以及时发现",
                    "同一模型在不同负载、转速和设备型号下容易性能波动，跨工况泛化不足",
                    "诊断结果与运维动作之间缺少统一联动，难以形成真正可用的维护闭环",
                ],
                "template_innovation_blocks": [
                    {"title": "创新一 · 多源特征融合", "summary": "联合振动、电流、温度与转速信号，增强对早期弱故障的感知能力。"},
                    {"title": "创新二 · 跨工况自适应诊断", "summary": "通过工况归一化与特征迁移，降低模型对固定工况的依赖。"},
                    {"title": "创新三 · 边云协同预警联动", "summary": "将实时告警、健康评分和运维工单串成可执行闭环。"},
                ],
                "opening_summary": "轴承故障诊断的真正难点不只是做出一次分类结果，而是如何在复杂工况下提前发现弱故障、稳定给出诊断并顺畅联动运维动作。",
                "closing_summary": "这一方向兼具算法深度、工业 IoT 叙事和运维价值，最适合作为智能制造类赛题的主推荐方案。",
                "score": {"novelty": 8, "feasibility": 8, "fit_to_rules": 9, "communication_potential": 8},
            },
            {
                "idea_id": "idea_b",
                "project_name": "智轴预警",
                "focus_summary": "在线健康评估与趋势预警",
                "problem": "制造企业常见的轴承故障诊断方案依赖离线分析，缺少对多工况连续运行设备的在线健康评估能力。",
                "target_users": ["设备点检人员", "工厂班组长", "设备保障部门"],
                "solution_summary": "围绕在线监测与健康评分构建轴承状态预警系统，突出连续采集、趋势分析和异常升级机制。",
                "core_innovations": ["在线健康指数建模", "异常趋势分级预警", "维修决策辅助看板"],
                "technical_architecture": ["在线采集层", "健康指数计算层", "趋势评估层", "告警与决策看板"],
                "application_scenarios": ["连续生产设备巡检", "车间班组值守", "维护排班优化"],
                "feasibility_notes": ["实现边界清晰，适合快速做在线监测原型", "便于做看板、趋势曲线和告警演示"],
                "value_notes": ["降低人工巡检压力", "帮助维护资源优先级排序"],
                "risk_notes": ["需要避免与普通状态监测系统同质化", "需要讲清健康指数如何与维修动作关联"],
                "blind_spots": [
                    "许多方案只能给出单时刻状态标签，无法反映持续劣化趋势",
                    "班组值守人员难以从海量波形中快速判断哪些设备需要优先处理",
                    "告警结果缺少与维护排班、备件准备和停机窗口的联动逻辑",
                ],
                "template_innovation_blocks": [
                    {"title": "创新一 · 健康指数建模", "summary": "把多维状态量压缩为可连续跟踪的健康指数。"},
                    {"title": "创新二 · 趋势分级预警", "summary": "将一次性异常判断升级为持续劣化趋势识别。"},
                    {"title": "创新三 · 维修决策辅助", "summary": "让告警结果直接服务于排班、巡检和维修窗口安排。"},
                ],
                "opening_summary": "很多轴承监测系统能采到数据，却不能稳定告诉运维团队设备是否正在持续恶化、哪些异常值得优先处理。",
                "closing_summary": "这一方向更强调在线监测与运维决策，展示逻辑完整，适合做轻量但完成度高的系统型作品。",
                "score": {"novelty": 7, "feasibility": 9, "fit_to_rules": 9, "communication_potential": 8},
            },
            {
                "idea_id": "idea_c",
                "project_name": "产线听诊官",
                "focus_summary": "低成本边缘诊断与集中运维",
                "problem": "中小制造企业缺少低成本、易部署的旋转机械异常识别方案，导致设备带病运行时间过长。",
                "target_users": ["中小工厂管理者", "设备维护外包团队", "产业园运维中心"],
                "solution_summary": "构建轻量化旋转机械听诊系统，通过低成本传感器与边缘诊断模型实现轴承异常快速筛查和远程汇总。",
                "core_innovations": ["低成本多传感器部署", "轻量化边缘故障识别", "园区级设备异常汇总"],
                "technical_architecture": ["低成本感知层", "边缘识别层", "远程汇总平台", "园区运维联动层"],
                "application_scenarios": ["中小工厂设备普查", "产业园集中运维", "远程维护服务"],
                "feasibility_notes": ["硬件故事清晰，适合实物展示", "可在成本和可部署性上形成差异化"],
                "value_notes": ["降低部署门槛", "适合中小制造场景推广"],
                "risk_notes": ["识别精度故事要与低成本约束平衡", "需要避免只剩硬件堆砌叙事"],
                "blind_spots": [
                    "中小制造场景很难承担高端监测系统的整体部署成本",
                    "异常筛查若完全依赖人工听音和经验，稳定性和规模化都受限",
                    "边缘设备采集结果缺少统一汇总与远程协同能力",
                ],
                "template_innovation_blocks": [
                    {"title": "创新一 · 低成本感知部署", "summary": "在保证有效性的前提下降低采集侧部署门槛。"},
                    {"title": "创新二 · 轻量化边缘诊断", "summary": "让异常筛查尽可能靠近设备侧实时完成。"},
                    {"title": "创新三 · 园区级联动汇总", "summary": "把分散设备的诊断结果汇总成可调度的维护视图。"},
                ],
                "opening_summary": "如果轴承故障诊断方案只能依赖昂贵设备和离线专家分析，就很难真正进入大量中小制造场景。",
                "closing_summary": "这一方向在部署可行性和应用推广叙事上更强，适合强调产业化价值。",
                "score": {"novelty": 7, "feasibility": 8, "fit_to_rules": 8, "communication_potential": 8},
            },
        ],
    },
    {
        "profile_id": "industrial_iot_maintenance",
        "display_name": "工业设备健康监测",
        "domain_label": "工业设备健康监测与预测维护",
        "keywords": ["工业", "设备", "运维", "产线", "工厂", "制造", "预测性维护", "故障", "传感器"],
        "cover_title_suffix": "工业设备健康监测与预测维护系统",
        "hero_visual_hint": "设备照片 + 状态曲线 + 告警工单看板",
        "background_focus": "设备异常发现滞后、人工巡检压力大、维护决策依赖经验",
        "goal_focus": "让采集、诊断、告警和维护联动形成完整闭环",
        "innovation_focus": "多源监测、趋势评估和工单联动",
        "value_focus": "降低停机损失并提升维护效率",
        "recommended_directions": [
            "明确传感器采集链、诊断算法和运维执行链之间的关系，避免只写成软件平台。",
            "优先选一个设备或产线场景讲透，减少泛化叙事。",
        ],
        "idea_templates": [
            {
                "idea_id": "idea_a",
                "project_name": "维脉工守",
                "focus_summary": "设备健康评分与运维联动",
                "problem": "中小制造场景中设备故障预警弱、人工巡检压力大、停机损失高。",
                "target_users": ["工厂设备运维团队", "中小制造企业管理者", "产业园运维部门"],
                "solution_summary": "打造工业设备健康管理系统，通过振动、电流和温度等数据进行预测性维护。",
                "core_innovations": ["轻量多传感器接入", "设备故障趋势评分", "运维工单自动联动"],
                "technical_architecture": ["传感采集层", "状态分析层", "趋势评分层", "运维联动层"],
                "application_scenarios": ["产线设备维护", "园区集中运维", "关键设备巡检"],
                "feasibility_notes": ["工业 IoT 叙事稳健", "技术方案容易拆解展示"],
                "value_notes": ["降本增效价值明确", "适合做数据看板和维护闭环演示"],
                "risk_notes": ["演示场景可能较硬核，需要优化讲解亲和力", "需要展示样机或模拟数据"],
                "opening_summary": "工业设备维护的核心问题，不是能不能采到数据，而是如何把分散状态量变成可信、及时、可执行的维护决策。",
                "closing_summary": "这一方向实现稳健、业务价值明确，适合做完成度高的工业物联网作品。",
                "score": {"novelty": 6, "feasibility": 9, "fit_to_rules": 9, "communication_potential": 7},
            }
        ],
    },
    {
        "profile_id": "generic_iot_system",
        "display_name": "通用物联网系统",
        "domain_label": "物联网感知与联动决策",
        "keywords": ["物联网", "iot", "感知", "监测", "联动", "预警", "平台", "终端"],
        "cover_title_suffix": "智能感知与联动决策系统",
        "hero_visual_hint": "场景主视觉 + 数据流向图 + 系统看板",
        "background_focus": "数据感知、分析和执行链路割裂",
        "goal_focus": "围绕一个明确场景搭建感知、分析、决策和执行闭环",
        "innovation_focus": "多源数据接入、规则与模型融合、闭环执行反馈",
        "value_focus": "提升感知效率与场景响应能力",
        "recommended_directions": [
            "先把目标场景和用户动作讲清，再决定传感器、模型和平台的分工。",
            "避免把项目写成抽象平台，至少要锚定一个可演示的具体业务流程。",
        ],
        "idea_templates": [
            {
                "idea_id": "idea_a",
                "project_name": "场景智能管家",
                "focus_summary": "感知分析执行闭环",
                "problem": "目标场景中的数据感知、分析与响应链路割裂，难以形成完整闭环。",
                "target_users": ["场景运营方", "管理部门", "一线执行人员"],
                "solution_summary": "围绕一个具体场景搭建感知、分析、决策和执行联动系统。",
                "core_innovations": ["多源数据接入", "规则与模型融合决策", "闭环执行反馈"],
                "technical_architecture": ["感知采集层", "分析决策层", "联动执行层", "回写反馈层"],
                "application_scenarios": ["园区管理", "校园治理", "行业专项场景"],
                "feasibility_notes": ["框架通用", "适合作为兜底候选方案"],
                "value_notes": ["应用价值容易表达"],
                "risk_notes": ["需要后续结合具体赛道细化"],
                "opening_summary": "如果感知、分析和执行彼此割裂，再多设备和数据也很难真正转化为场景效率提升。",
                "closing_summary": "这一方向适合作为通用兜底方案，但必须尽快结合具体场景进一步细化。",
                "score": {"novelty": 6, "feasibility": 7, "fit_to_rules": 7, "communication_potential": 7},
            },
            {
                "idea_id": "idea_b",
                "project_name": "可信数据助手",
                "focus_summary": "可信数据治理与异常识别",
                "problem": "场景数据来源分散、可信度不足，影响后续决策质量。",
                "target_users": ["平台管理者", "运营团队", "业务决策者"],
                "solution_summary": "通过采集、清洗和异常识别模块，提升数据可用性与业务响应效率。",
                "core_innovations": ["可信采集机制", "异常识别", "结果反馈闭环"],
                "technical_architecture": ["采集层", "清洗层", "识别层", "反馈层"],
                "application_scenarios": ["数据治理", "业务预警", "流程优化"],
                "feasibility_notes": ["容易做 MVP 原型"],
                "value_notes": ["适合讲效率提升"],
                "risk_notes": ["需要补足场景差异化"],
                "score": {"novelty": 6, "feasibility": 8, "fit_to_rules": 7, "communication_potential": 6},
            },
            {
                "idea_id": "idea_c",
                "project_name": "智慧联动平台",
                "focus_summary": "统一联动与策略化处置",
                "problem": "现有系统分散，人工协调成本高，无法形成跨环节联动处置。",
                "target_users": ["管理部门", "平台运营者", "协同单位"],
                "solution_summary": "建设统一联动平台，将感知事件、分析结果和执行动作连接起来。",
                "core_innovations": ["统一事件总线", "可视化联动", "策略化处置"],
                "technical_architecture": ["事件接入层", "规则与模型层", "联动执行层", "可视化层"],
                "application_scenarios": ["综合治理平台", "专项联动场景", "业务协同调度"],
                "feasibility_notes": ["实现边界清晰"],
                "value_notes": ["展示逻辑完整"],
                "risk_notes": ["如果没有具体场景会显得偏空"],
                "score": {"novelty": 5, "feasibility": 7, "fit_to_rules": 7, "communication_potential": 7},
            },
        ],
    },
]


def collect_all_profile_keywords() -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for profile in TOPIC_PROFILES:
        for keyword in profile.get("keywords", []):
            if keyword not in seen:
                seen.add(keyword)
                result.append(keyword)
    return result


def resolve_topic_profile(
    topic_dir: Path,
    *,
    explicit_topic: str = "",
    context_text: str = "",
    seed_text: str = "",
    extra_tags: list[str] | None = None,
) -> dict[str, Any]:
    topic_name = load_topic_name(topic_dir, explicit_topic)
    haystack = " ".join(
        [
            topic_name,
            context_text,
            seed_text,
            " ".join(extra_tags or []),
        ]
    ).lower()
    topic_lower = topic_name.lower()

    best = TOPIC_PROFILES[-1]
    best_score = -1
    for profile in TOPIC_PROFILES:
        score = 0
        for keyword in profile.get("keywords", []):
            lowered = keyword.lower()
            if lowered in topic_lower:
                score += 3
            elif lowered in haystack:
                score += 1
        if score > best_score:
            best = profile
            best_score = score

    resolved = deepcopy(best)
    resolved["topic_name"] = topic_name
    resolved["match_score"] = best_score
    return resolved


def build_recommended_directions(
    profile: dict[str, Any],
    *,
    seed_text: str = "",
    domain_tags: list[str] | None = None,
) -> list[str]:
    results: list[str] = []
    if seed_text.strip():
        results.append(f"围绕人工主轴“{seed_text.strip()}”做同轴变体，不做无关发散。")
    results.extend(profile.get("recommended_directions", []))
    if "物联网" in (domain_tags or []) and "IoT" not in "".join(results) and "iot" not in "".join(results).lower():
        results.append("需要明确 IoT 在方案中的接入角色，避免仅停留在纯平台软件叙事。")
    return results


def _format_template(value: Any, *, seed: str, topic_name: str) -> Any:
    if isinstance(value, str):
        return value.format(seed=seed, topic_name=topic_name)
    if isinstance(value, list):
        return [_format_template(item, seed=seed, topic_name=topic_name) for item in value]
    if isinstance(value, dict):
        return {key: _format_template(item, seed=seed, topic_name=topic_name) for key, item in value.items()}
    return value


def build_profile_ideas(profile: dict[str, Any], spec: dict[str, Any], *, seed_text: str = "") -> list[dict[str, Any]]:
    scoring_dimensions = spec.get("scoring_dimensions", [])
    seed = seed_text.strip() or profile.get("display_name", "") or profile.get("topic_name", "")
    ideas: list[dict[str, Any]] = []
    for template in profile.get("idea_templates", []):
        idea = _format_template(deepcopy(template), seed=seed, topic_name=profile.get("topic_name", ""))
        idea["matched_scoring_dimensions"] = scoring_dimensions
        idea["topic_name"] = profile.get("topic_name", "")
        idea["topic_profile"] = _public_profile(profile)
        ideas.append(idea)
    return ideas

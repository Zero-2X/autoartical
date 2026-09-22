# Evidence Summary

- Topic: 开放词汇检测与RSI
- Topic Profile: 遥感影像开放词汇目标检测
- Competition: competition-rules
- Seed Direction: 面向遥感影像的开放词汇目标检测：用遥感域视觉语言先验、旋转框定位和可靠性校准支持新类别查询，并通过可回放案例服务比赛展示。
- Evidence Items: 13
- Shared Registry Created: 13
- Shared Registry Updated: 0

## Source Overview
- Rules: 1
- References: 0
- External Evidence Files: 1
- Samples: 0

## Theme Summary
- Domain Themes: 评分标准、应用价值、遥感、benchmark、开放词汇、检测、遥感检测多样性、benchmark 选择
- Format Themes: 交付要求、演示

## Recommended Direction
- 围绕人工主轴“面向遥感影像的开放词汇目标检测：用遥感域视觉语言先验、旋转框定位和可靠性校准支持新类别查询，并通过可回放案例服务比赛展示。”做同轴变体，不做无关发散。
- 围绕遥感域开放词汇检测组织研究主线，明确 RSI 指 Remote Sensing Imagery，避免写成通用自然图像检测。
- 把类别扩展、旋转定位、查询鲁棒性和可靠性校准分别设为可检验问题，不能只用一个 mAP 证明开放能力。
- 优先复用 Grounding DINO、Detic、YOLO-World、RS5M/GeoRSCLIP 的公开接口思想，严格核验代码许可证和权重来源。

## Evidence Items
### ev_84bd681099 | rule
- Source: competition-rules.md
- Source Authority: competition_official
- Source Origin: requirements
- Evidence Kind: scoring_rule
- Claim: 比赛评分重点集中在：应用价值
- Summary: 评分维度直接决定 idea 的匹配度叙事和后续作品书章节分配。
- Derived Insight: 评分标准决定后续 idea 叙事和作品书结构取舍。
- Inspiration: 可直接映射到作品书的章节轻重、创新表述和答辩重心。
- Supports: 评分维度对齐、章节权重分配
- Applicable Steps: requirements、ideas、document_plan、document_writing、document_review
- Applicable Work Types: none
- Tags: 评分标准、应用价值
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: none
- Limitations: none

### ev_9ca3b5c76b | rule
- Source: competition-rules.md
- Source Authority: competition_official
- Source Origin: requirements
- Evidence Kind: submission_requirement
- Claim: 线上提交作品完整设计方案文档与实物文档说明
- Summary: 交付形式要求作品不能只有概念描述，还要便于演示和答辩呈现。
- Derived Insight: 交付要求会反向约束系统展示方式和 record 结构。
- Inspiration: 需要同步考虑文档、文档说明、document record，而不是只生成文字方案。
- Supports: 交付形式设计、答辩展示结构
- Applicable Steps: requirements、ideas、document_plan、document_writing、document_review
- Applicable Work Types: none
- Tags: 交付要求、演示
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: none
- Limitations: none

### ev_d827045531 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: dataset_signal
- Claim: DIOR 是光学遥感目标检测基准，包含 20 类目标并覆盖尺度、成像条件、天气和季节变化。
- Summary: 遥感检测需要在跨场景、类内差异和小目标条件下评估，不能直接照搬自然图像类别假设。
- Derived Insight: 使用 DIOR 作为水平框和跨域开放词汇评测入口，并显式冻结 base/novel 划分。
- Inspiration: 可直接支撑：遥感检测多样性；可直接支撑：benchmark 选择；可直接支撑：域偏移
- Supports: 遥感检测多样性、benchmark 选择、域偏移
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: 遥感、benchmark、开放词汇、检测、遥感检测多样性、benchmark 选择、域偏移、remote sensing、DIOR、目标检测
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: none
- Limitations: DIOR 原始任务是封闭集，开放词汇划分需由本项目公布。

### ev_7f9521c71a | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: dataset_signal
- Claim: DOTA 用任意方向四边形标注航空影像目标，覆盖尺度、方向和形状变化。
- Summary: 俯视影像中的旋转目标和密集目标会同时影响定位与类别匹配，适合检验开放词汇模型的空间鲁棒性。
- Derived Insight: 主实验同时报告水平框与旋转框结果，避免类别命中掩盖定位退化。
- Inspiration: 可直接支撑：旋转目标；可直接支撑：定位指标；可直接支撑：航空影像挑战
- Supports: 旋转目标、定位指标、航空影像挑战
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: DOTA、旋转框、小目标、遥感、旋转目标、定位指标、航空影像挑战、开放词汇
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: none
- Limitations: 实验需冻结 DOTA 版本、类别映射和标注格式。

### ev_9662694342 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: dataset_signal
- Claim: FAIR1M 面向高分辨率遥感影像细粒度有向目标识别，提供大量实例和细粒度类别信息。
- Summary: 细粒度近义类别会放大提示词和语义原型混淆，必须报告类别层级和错误类型。
- Derived Insight: 把细粒度混淆、类别层级和提示词稳定性纳入错误分析。
- Inspiration: 可直接支撑：细粒度类别；可直接支撑：有向检测；可直接支撑：语义混淆
- Supports: 细粒度类别、有向检测、语义混淆
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: FAIR1M、细粒度、有向检测、遥感、细粒度类别、语义混淆、遥感影像、remote sensing
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: none
- Limitations: 正式实验前需核验数据许可证和下载版本。

### ev_39cee8f6f3 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: research_finding
- Claim: RS5M 构建遥感图像—文本配对数据，并用 GeoRSCLIP 研究遥感域视觉—语言表示。
- Summary: 遥感域视觉—语言预训练可以缓解自然图像语义空间与俯视目标之间的域差异，但图像级文本不等于实例级定位真值。
- Derived Insight: 使用遥感域语义先验，另行验证实例级定位损失和校准模块的必要性。
- Inspiration: 可直接支撑：视觉语言域适配；可直接支撑：遥感图文数据；可直接支撑：语义先验
- Supports: 视觉语言域适配、遥感图文数据、语义先验
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: RS5M、GeoRSCLIP、遥感、视觉语言、视觉语言域适配、遥感图文数据、语义先验、remote sensing
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: 代码仓库：https://github.com/om-ai-lab/RS5M
- Limitations: 弱标注和自动描述可能含噪，不能替代实例框真值。

### ev_df7e4935d7 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: research_finding
- Claim: LAE 工作将遥感开放词汇检测定义为 Locate Anything on Earth，构建 LAE-1M/LAE-80C，并引入动态词汇构建和视觉引导文本提示。
- Summary: 自然图像开放词汇检测迁移到遥感时存在域差异，遥感数据统一、词汇构建和视觉—文本对齐是核心问题。
- Derived Insight: 本项目不重复构建大规模基础数据集，聚焦增量词汇、可靠性校准和证据输出。
- Inspiration: 可直接支撑：遥感开放词汇现状；可直接支撑：域差异；可直接支撑：方法缺口
- Supports: 遥感开放词汇现状、域差异、方法缺口
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: LAE、遥感、开放词汇、域差异、遥感开放词汇现状、方法缺口、open-vocabulary、remote sensing
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: none
- Limitations: 不声称复现 LAE-1M 的全部数据和训练成本。

### ev_7ef4331b38 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: research_finding
- Claim: Grounding DINO 将检测器与语言输入结合，支持类别名或指代表达驱动的开放集目标定位。
- Summary: 语言条件检测器能扩展查询词汇，但自然图像预训练与遥感小目标、旋转目标之间存在定位和语义校准风险。
- Derived Insight: 将 Grounding DINO 作为强零样本基线，在相同提示词、切片策略和后处理下比较。
- Inspiration: 可直接支撑：零样本基线；可直接支撑：文本查询；可直接支撑：开放集定位
- Supports: 零样本基线、文本查询、开放集定位
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: Grounding DINO、开放集、基线、视觉语言、零样本基线、文本查询、开放集定位、风险、遥感
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: 官方仓库：https://github.com/IDEA-Research/GroundingDINO
- Limitations: 版本、权重和许可证按官方仓库核验。

### ev_1124a9c4a8 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: research_finding
- Claim: Detic 利用图像级监督扩展检测词汇，并支持自定义词汇推理。
- Summary: 图像级监督提升类别覆盖，但弱监督空间精度和遥感域迁移会造成候选框不稳定。
- Derived Insight: 将 Detic 作为大词汇基线，分项报告候选框召回、类别校准和小目标性能。
- Inspiration: 可直接支撑：图像级监督；可直接支撑：自定义词汇；可直接支撑：开放词汇基线
- Supports: 图像级监督、自定义词汇、开放词汇基线
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: Detic、开放词汇、图像级监督、基线、自定义词汇、开放词汇基线、遥感
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: 官方仓库：https://github.com/facebookresearch/Detic
- Limitations: 依赖和许可证边界必须按官方仓库核验。

### ev_40ff1f0b23 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: research_finding
- Claim: YOLO-World 通过视觉语言建模、RepVL-PAN 和区域—文本对比学习，将开放词汇能力纳入实时检测器。
- Summary: 实时路线适合比赛演示和边缘部署，但速度必须与分辨率、切片、词汇规模和精度共同报告。
- Derived Insight: 设计词汇原型缓存和轻量候选生成，把实时性设为系统约束而非宣传数字。
- Inspiration: 可直接支撑：实时检测；可直接支撑：部署约束；可直接支撑：词汇缓存
- Supports: 实时检测、部署约束、词汇缓存
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: YOLO-World、实时、部署、开放词汇、实时检测、部署约束、词汇缓存、open-vocabulary、视觉语言、边缘部署
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: 官方仓库：https://github.com/AILab-CVC/YOLO-World
- Limitations: 官方仓库 GPL-3.0，商业分发前必须核验许可证。

### ev_53e8fd7356 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: research_finding
- Claim: GLIP 将目标检测与短语定位统一为语言感知预训练，并利用图文与 grounding 数据增强开放集迁移。
- Summary: 跨模态预训练提供可扩展语义对齐，但伪框、抓取文本和域外图像会引入噪声与偏置。
- Derived Insight: 复用语言条件检测的任务组织方式，在实验中加入提示词扰动和伪阳性分析。
- Inspiration: 可直接支撑：跨模态预训练；可直接支撑：短语定位；可直接支撑：伪标签风险
- Supports: 跨模态预训练、短语定位、伪标签风险
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: GLIP、grounding、视觉语言、噪声、跨模态预训练、短语定位、伪标签风险、目标检测、感知
- Reliability: high
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: 官方仓库：https://github.com/microsoft/GLIP
- Limitations: GLIP 主要面向自然图像，不能直接代表遥感场景最优结果。

### ev_ed1515af87 | external_research
- Source: external_evidence\external-evidence-intake.json
- Source Authority: academic
- Source Origin: manual_external_intake
- Evidence Kind: research_finding
- Claim: OpenRSD 针对遥感开放提示词检测，关注类别扩展、旋转目标和精度—实时性之间的平衡。
- Summary: 遥感开放提示词需要同时处理类别语义、方向定位和跨域性能，不能只把自然图像模型直接套入遥感影像。
- Derived Insight: 将开放提示词、旋转框和部署约束合并进实验协议，并把提示词扰动作为稳健性测试。
- Inspiration: 可直接支撑：遥感开放提示词；可直接支撑：旋转目标；可直接支撑：实时性
- Supports: 遥感开放提示词、旋转目标、实时性
- Applicable Steps: ideas、concept、document_plan、document_writing
- Applicable Work Types: none
- Tags: OpenRSD、遥感、开放提示词、旋转框、遥感开放提示词、旋转目标、实时性、遥感影像、remote sensing
- Reliability: medium
- Reusability Tier: high
- Curation Status: reviewed
- Usage Hint: none
- Limitations: 以正式论文版本和官方代码为准，不使用摘要之外的未核验数字。

### ev_d19d578ade | seed_direction
- Source: cli:--seed-text
- Source Authority: human_input
- Source Origin: human_cli_input
- Evidence Kind: direction_constraint
- Claim: 面向遥感影像的开放词汇目标检测：用遥感域视觉语言先验、旋转框定位和可靠性校准支持新类别查询，并通过可回放案例服务比赛展示。
- Summary: 这是人工指定的主轴，不是外部事实证据，后续只允许在这个方向内扩展变体。
- Derived Insight: 人工主轴只用于限制扩展方向，不可直接当作事实依据。
- Inspiration: 后续变体应围绕这条主轴扩展，但所有论证仍需补事实证据。
- Supports: 选题边界
- Applicable Steps: ideas
- Applicable Work Types: none
- Tags: 开放词汇、遥感影像、遥感、目标检测、视觉语言、旋转框
- Reliability: medium
- Reusability Tier: medium
- Curation Status: normalized
- Usage Hint: 只在 Step2 做同轴变体约束使用。
- Limitations: 不是事实证据，不能直接出现在作品书论证链中。

## Open Gaps
- 当前章程未给出作品书具体章节模板，需要补充命题文件或文档格式要求。
- 当前 topic 的具体赛道 / 命题方向尚未从章程中唯一确定，需要结合命题文件确认。
- 当前章程未明确作品书字数或页数限制，需要补充模板文件确认。

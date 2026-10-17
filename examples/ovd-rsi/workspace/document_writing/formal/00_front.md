# OpenRSI-Calibrator：面向光学遥感影像的开放词汇目标检测与可靠语义校准

> 竞赛作品申报书
> 作者、单位与指导教师：待填写
> 2026 年 10 月

## 摘要

光学遥感影像解译正在从“在固定类别表中找目标”转向“按用户提出的词语找目标”。灾后评估、自然资源巡查和港口监测经常出现训练类别之外的查询对象，而主流遥感检测基准只覆盖 15 至 37 个类别，重新标注与训练的周期难以跟上业务需求。通用开放词汇检测器以图文对齐取代固定分类头，但它们主要在自然图像上训练；俯视视角、极端尺度差异、任意方向和密集排列使其在遥感影像中的定位与分类同时退化，并且输出分数往往不能解释为可靠的概率。

本作品提出 OpenRSI-Calibrator，一套面向光学遥感影像的开放词汇检测与可靠语义校准方案。方案由三部分组成：其一，以“对象—属性—场景”三层原型和负向描述建立遥感域词汇原型，缓解自然语言与俯视影像之间的语义偏移；其二，以多尺度重叠切片与水平框、旋转框协同生成候选，并在整图坐标下按几何与语义一致性分层融合；其三，将候选分数分解为语义匹配、几何质量、背景对照和查询稳定性四项证据，在独立校准集上做事后校准，并据此给出接受、复核、拒识三态决策。

本文围绕四项可证伪假设设计实验：域内原型能否提高新类召回并在跨区域测试中保持收益，旋转候选协同是否主要改善小目标与细长目标，校准与背景对照能否降低高置信误报而不过度牺牲召回，以及证据卡能否缩短人工复核时间。实验采用 DIOR、DOTA 与 FAIR1M 构建基础类与新类划分，对照 Grounding DINO、YOLO-World 等通用路线和 CastDet、LAE-DINO、OpenRSD 等遥感路线，并预先规定统计方法、消融顺序和推翻假设的结果。本文中所有实验结果均为计划或待实测项，未运行的实验不报告数值。

**关键词：**开放词汇目标检测；光学遥感影像；视觉—语言模型；旋转框检测；置信度校准

## Abstract

Optical remote-sensing interpretation is shifting from searching a fixed label set to answering free-form queries. Public remote-sensing detection benchmarks cover only 15 to 37 categories, while disaster assessment, resource inspection and port monitoring routinely ask for objects outside those lists. General open-vocabulary detectors replace the fixed classifier with image–text alignment, but they are trained mainly on natural images; overhead viewpoints, extreme scale variation, arbitrary orientation and dense layouts degrade both localization and classification, and their scores are rarely calibrated probabilities.

We propose OpenRSI-Calibrator, an open-vocabulary detection and reliability-calibration design for optical remote-sensing imagery. It builds object–attribute–scene prototypes with negative descriptions to reduce the semantic gap between language and overhead imagery; generates horizontal and oriented candidates from overlapping multi-scale tiles and fuses them in global coordinates; and decomposes each score into semantic, geometric, background-contrast and query-stability evidence, calibrated post hoc on a held-out split to support accept, review and reject decisions.

Four falsifiable hypotheses organize the evaluation on base/novel splits derived from DIOR, DOTA and FAIR1M, against general detectors such as Grounding DINO and YOLO-World and remote-sensing methods such as CastDet, LAE-DINO and OpenRSD. Statistical procedures, ablation order and the outcomes that would refute each hypothesis are fixed in advance. No experimental result is reported in this proposal; every metric is marked as planned.

**Keywords:** open-vocabulary object detection; optical remote sensing; vision–language model; oriented object detection; confidence calibration

[[TOC]]

# 研究证据表

核验日期：2026-10-16；方法：`verify_references.py` 从 arXiv 取回题名、作者、日期并比对期望标题，发表载体须有 arXiv comment 等依据。全部 24 条核验通过。

“原文位置”统一为摘要：本次只核对了摘要中的数值与表述，正文与附录未逐页阅读，这是本证据表的已知局限；涉及方法细节的陈述（如 2.4 节）以摘要和方法描述为限，表 2-3 中“摘要未提及”即由此而来。

| 编号 | 来源 | 版本/日期 | 原文位置 | 支持的主张（摘录数值） | 正文使用位置 | 研究条件与局限 |
|---|---|---|---|---|---|---|
| [1] | DOTA: A Large-scale Dataset for Object Detection in Aerial Images (https://arxiv.org/abs/1711.10398) | 2017/11/28；Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR) 2018（依据：arXiv comment: Accepted to CVPR 2018） | 摘要 | DOTA v1.0: 2806 images, 15 categories, 188,282 instances, arbitrary quadrilateral (OBB) labels | 1.1、2.1、表2-1、图2-1 | 摘要数值为 v1.0；后续版本扩充 |
| [2] | Object Detection in Optical Remote Sensing Images: A Survey and A New Benchmark (https://arxiv.org/abs/1909.00133) | 2019/08/31；arXiv 预印本 | 摘要 | DIOR: 23,463 images, 192,472 instances, 20 classes; large size variation, high inter-class similarity | 1.1、2.1、5.2.1、表2-1 | 水平框标注；正式版为 ISPRS J. 2020，此处按预印本著录 |
| [3] | FAIR1M: A Benchmark Dataset for Fine-grained Object Recognition in High-Resolution Remote Sensing Imagery (https://arxiv.org/abs/2103.05569) | 2021/03/09；arXiv 预印本 | 摘要 | FAIR1M: >1M instances, >15,000 images, 5 categories/37 sub-categories, OBB | 1.1、2.1、表2-1、图2-1 | 摘要仅给“超过”下限值 |
| [4] | Object Detection in Aerial Images: A Large-Scale Benchmark and Challenges (https://arxiv.org/abs/2102.12219) | 2021/02/24；arXiv 预印本 | 摘要 | DOTA-v2.0: 11,268 images, 18 categories, 1,793,658 instances | 1.1、2.1、表2-1 | — |
| [5] | Oriented R-CNN for Object Detection (https://arxiv.org/abs/2108.05699) | 2021/08/12；Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV) 2021（依据：arXiv comment: ICCV 2021） | 摘要 | two-stage oriented detector; representative closed-set OBB baseline | 1.3、2.1、5.3 | 闭集方法，仅作几何基础与上界参照 |
| [6] | Open-vocabulary Object Detection via Vision and Language Knowledge Distillation (https://arxiv.org/abs/2104.13921) | 2021/04/28；International Conference on Learning Representations (ICLR) 2022（依据：arXiv comment: ICLR Camera Ready） | 摘要 | distill CLIP region embeddings into detector; LVIS rare held out as novel; 16.1 mask APr R50 | 2.2 | LVIS 自然图像协议，与遥感不可直接比较 |
| [7] | RegionCLIP: Region-based Language-Image Pretraining (https://arxiv.org/abs/2112.09106) | 2021/12/16；arXiv 预印本 | 摘要 | region-text alignment pretraining | 2.2 | 摘要未给遥感结果 |
| [8] | Detecting Twenty-thousand Classes using Image-level Supervision (https://arxiv.org/abs/2201.02605) | 2022/01/07；European Conference on Computer Vision (ECCV) 2022（依据：arXiv comment: ECCV 2022 camera ready） | 摘要 | image-level supervision expands vocabulary of classifier | 2.2 | 图像级监督假设在一图多实例时存疑（本文推断） |
| [9] | Grounded Language-Image Pre-training (https://arxiv.org/abs/2112.03857) | 2021/12/07；Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) 2022（依据：arXiv comment: CVPR 2022） | 摘要 | detection reformulated as phrase grounding | 2.2 | — |
| [10] | Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection (https://arxiv.org/abs/2303.05499) | 2023/03/09；arXiv 预印本 | 摘要 | DETR-style open-set detector with grounded pretraining | 2.2、5.3 | 预印本；代码 2024 年后少更新 |
| [11] | Simple Open-Vocabulary Object Detection with Vision Transformers (https://arxiv.org/abs/2205.06230) | 2022/05/12；European Conference on Computer Vision (ECCV) 2022（依据：arXiv comment: ECCV 2022 camera-ready version） | 摘要 | image-text pretrained ViT transferred to detection end to end | 2.2 | — |
| [12] | YOLO-World: Real-Time Open-Vocabulary Object Detection (https://arxiv.org/abs/2401.17270) | 2024/01/30；arXiv 预印本 | 摘要 | RepVL-PAN, region-text contrastive loss; 35.4 AP LVIS at 52.0 FPS on V100 | 2.2、5.3 | LVIS/V100 数值，非遥感 |
| [13] | RemoteCLIP: A Vision Language Foundation Model for Remote Sensing (https://arxiv.org/abs/2306.11029) | 2023/06/19；arXiv 预印本 | 摘要 | RS VLM; +6.39% avg zero-shot classification over CLIP on 12 datasets; TGRS | 2.3 | 整图级检索/分类评测，非检测 |
| [14] | RS5M and GeoRSCLIP: A Large Scale Vision-Language Dataset and A Large Vision-Language Model for Remote Sensing (https://arxiv.org/abs/2306.11300) | 2023/06/20；arXiv 预印本 | 摘要 | 5M RS image-text pairs; GeoRSCLIP | 2.3、4.2.4、5.2.2 | — |
| [15] | SkyScript: A Large and Semantically Diverse Vision-Language Dataset for Remote Sensing (https://arxiv.org/abs/2312.12856) | 2023/12/20；Proceedings of the AAAI Conference on Artificial Intelligence 2024（依据：arXiv comment: Accepted by AAAI 2024） | 摘要 | semantically diverse RS VL dataset | 2.3、4.2.4、5.2.2 | — |
| [16] | Zero-Shot Aerial Object Detection with Visual Description Regularization (https://arxiv.org/abs/2402.18233) | 2024/02/28；arXiv 预印本 | 摘要 | weak semantic-visual correlation of aerial objects; +4.5 mAP unseen on DIOR, +8.1 HM | 2.4、4.2、4.2.3 | 零样本设定 |
| [17] | Toward Open Vocabulary Aerial Object Detection with CLIP-Activated Student-Teacher Learning (https://arxiv.org/abs/2311.11646) | 2023/11/20；European Conference on Computer Vision (ECCV) 2024（依据：arXiv comment: Accepted by ECCV2024） | 摘要 | RemoteCLIP teacher; 46.5% mAP VisDroneZSD novel, +21.0 over prior OVD | 2.4、5.3 | 代表性结果来自无人机视角 VisDroneZSD |
| [18] | Locate Anything on Earth: Advancing Open-Vocabulary Object Detection for Remote Sensing Community (https://arxiv.org/abs/2408.09110) | 2024/08/17；arXiv 预印本 | 摘要 | LAE-1M from up to 10 datasets auto-annotated; LAE-DINO with DVC and VisGT; DIOR, DOTAv2.0, LAE-80C; natural-image OVD struggles on RS due to domain gap | 2.4、3.2、5.3 | 自动标注数据含噪声（原文自述的构建方式） |
| [19] | RT-OVAD: Real-Time Open-Vocabulary Aerial Object Detection via Image-Text Collaboration (https://arxiv.org/abs/2408.12246) | 2024/08/22；arXiv 预印本 | 摘要 | real-time aerial OVD | 2.4 | 数值来自原文自测，硬件为 RTX 4090 |
| [20] | OpenRSD: Towards Open-prompts for Object Detection in Remote Sensing Images (https://arxiv.org/abs/2503.06146) | 2025/03/08；arXiv 预印本 | 摘要 | multimodal prompts, multi-task heads (OBB/HBB), 7 datasets; +8.7% AP vs YOLO-World, 20.8 FPS | 2.4、5.3 | 原文注明代码将发布；与 YOLO-World 的比较为原文协议 |
| [21] | On Calibration of Modern Neural Networks (https://arxiv.org/abs/1706.04599) | 2017/06/14；International Conference on Machine Learning (ICML) 2017（依据：arXiv comment: ICML 2017） | 摘要 | modern networks miscalibrated; temperature scaling | 2.5、4.5.2 | 分类任务校准 |
| [22] | Multivariate Confidence Calibration for Object Detection (https://arxiv.org/abs/2004.13546) | 2020/04/28；arXiv 预印本 | 摘要 | D-ECE; calibration conditioned on box position/size | 2.5、4.5.2、5.4 | CVPR 2020 Workshop |
| [23] | On Calibration of Object Detectors: Pitfalls, Evaluation and Baselines (https://arxiv.org/abs/2405.20459) | 2024/05/30；arXiv 预印本 | 摘要 | D-ECE+TS evaluation pitfalls; post-hoc Platt/isotonic outperform train-time calibration; >7 D-ECE on COCO vs Cal-DETR | 2.5、3.2、4.5.2 | 负面证据：D-ECE+TS 评测框架缺陷；COCO 数值 |
| [24] | How to Evaluate the Generalization of Detection? A Benchmark for Comprehensive Open-Vocabulary Detection (https://arxiv.org/abs/2308.13177) | 2023/08/25；arXiv 预印本 | 摘要 | OVDEval 9 subtasks hard negatives; top OVD models fail except simple object types; AP deceptive, NMS-AP proposed | 2.5、5.4 | 负面证据：主流 OVD 在困难负样本上失败；自然图像 |

## 检索停止依据

- 覆盖：遥感检测基准与旋转框（[1]–[5]）；通用开放词汇四条路线（[6]–[12]）；遥感视觉—语言表示（[13]–[15]）；遥感开放词汇检测（[16]–[20]）；校准与开放词汇评测的负面证据（[21]–[24]）。
- 每个研究缺口均有直接依据：缺口一 [5,13–16]；缺口二 [17–23]；缺口三 [9,10,24]。
- 已解释的冲突：校准评测框架之争（[22] 与 [23]），见正文 2.5 节。
- 未覆盖：遥感指代表达理解、遥感视觉问答、SAR/多光谱开放词汇检测；2025 年下半年以后的工作未系统检索。

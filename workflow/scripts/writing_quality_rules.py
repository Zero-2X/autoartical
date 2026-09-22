from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


RULES_PATH = Path(__file__).resolve().parent.parent / "templates" / "writing-quality-rules.template.json"

DEFAULT_RULES: dict[str, Any] = {
    "required_approved_audit_dimensions": [
        "goal_alignment",
        "score_alignment",
        "position_logic",
        "body_priority_coverage",
        "evidence_support",
        "length_budget",
        "pending_items_handling",
    ],
    "writing_brief_rules": {
        "avoid_meta_phrases": [
            "本章建议",
            "本节重点是",
            "下文将",
            "建议在正文中使用",
        ],
        "forbidden_draft_markers": [
            "需要把……说透",
            "具体写作时",
            "如果把这一节放到全书逻辑中观察",
            "通过这种写法",
            "继续补充",
            "进一步落成可执行论证",
            "围绕“X”中的“Y”",
            "本节用于承接该子问题的进一步说明",
        ],
        "output_contract": [
            "Treat `brief.md` as a constraint sheet, not as reusable prose.",
            "`draft.md` must read like already-submitted competition prose, not like a writing plan or chapter brief.",
            "If a sentence can be rewritten from “这一节要说明什么” into “系统实际做了什么”, always choose the latter.",
        ],
    },
    "document_review": {
        "hard_block_text_patterns": [
            {"label": "中间稿词 `pending`", "pattern": r"\bpending\b"},
            {"label": "中间稿词 `待确认事项`", "pattern": "待确认事项"},
            {"label": "元写作提示 `建议在正文中使用`", "pattern": "建议在正文中使用"},
            {"label": "元写作提示 `建议放置位置`", "pattern": "建议放置位置"},
            {"label": "元写作提示 `本章将`", "pattern": "本章将"},
            {"label": "元写作提示 `本章建议`", "pattern": "本章建议"},
            {"label": "元写作提示 `本节重点是`", "pattern": "本节重点是"},
            {"label": "元写作提示 `本节重点在于`", "pattern": "本节重点在于"},
            {"label": "元写作提示 `下文将`", "pattern": "下文将"},
            {"label": "元写作提示 `需要把……说透`", "pattern": r"需要把.{0,24}说透"},
            {"label": "元写作提示 `具体写作时`", "pattern": "具体写作时"},
            {"label": "元写作提示 `如果把这一节放到全书逻辑中观察`", "pattern": "如果把这一节放到全书逻辑中观察"},
            {"label": "元写作提示 `通过这种写法`", "pattern": "通过这种写法"},
            {"label": "元写作提示 `继续补充`", "pattern": "继续补充"},
            {"label": "元写作提示 `进一步落成可执行论证`", "pattern": "进一步落成可执行论证"},
            {"label": "元写作提示 `围绕“X”中的“Y”`", "pattern": r"围绕“[^”]+”中的“[^”]+”"},
            {"label": "元写作提示 `图X的作用`", "pattern": r"图\d+(?:[-.．]\d+)+的作用"},
            {"label": "元写作提示 `表X并不是简单罗列`", "pattern": r"表\d+(?:[-.．]\d+)+并不是简单罗列"},
        ],
        "major_risk_text_patterns": [
            {"label": "流程性口吻 `当前版本`", "pattern": "当前版本", "threshold": 3},
            {"label": "流程性口吻 `MVP`", "pattern": r"\bMVP\b", "threshold": 3},
            {"label": "中间稿口吻 `待确认`", "pattern": "待确认", "threshold": 2},
            {"label": "流程性口吻 `当前系统`", "pattern": "当前系统", "threshold": 4},
            {"label": "范围管理口吻 `实现边界/能力边界`", "pattern": r"实现边界|能力边界|边界说明", "threshold": 4},
        ],
        "proposal_style_h2_patterns": [
            "项目总体方案",
            "实施计划与扩展方向",
            "项目范围管理",
        ],
        "temporary_innovation_heading_pattern": r"^###\s*创新[0-9一二三四五六七八九十]+\s*$",
        "duplicate_paragraph_min_length": 30,
        "overlap_paragraph_min_length": 40,
        "synthetic_flow_block": {
            "template_exempt_topic_names": ["topic_xx"],
            "trigger_reasons": ["synthetic_flow_test_seed"],
            "trigger_note_substrings": ["Synthetic flow test"],
        },
    },
    "document_export": {
        "paragraph_drop_patterns": [
            r"^.*通过这种写法.*$",
            r"^.*继续补充系统价值.*$",
            r"^围绕“[^”]+”中的“[^”]+”.*$",
            r"^具体写作时，可从.*$",
            r"^如果把这一节放到全书逻辑中观察.*$",
            r"^.*进一步落成可执行论证.*$",
            r"^.*需要把.*说透.*$",
            r"^本节用于承接该子问题的进一步说明.*$",
        ],
    },
}


def _merge_defaults(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_defaults(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_writing_quality_rules() -> dict[str, Any]:
    rules = copy.deepcopy(DEFAULT_RULES)
    if not RULES_PATH.exists():
        return rules
    payload = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return rules
    return _merge_defaults(rules, payload)

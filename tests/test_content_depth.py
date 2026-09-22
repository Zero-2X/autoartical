import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from content_depth import DEFAULT_CONTRACT, allocate_budgets, build_content_depth_gate, content_metrics
from proposal_workflow import build_length_gate


class ContentDepthTests(unittest.TestCase):
    def test_formatting_cannot_supply_prose(self):
        text = "# " + "标题" * 100 + "\n\n| " + "表格" * 100 + " |\n\n```python\n" + "代码" * 100 + "\n```\n\n![图](x.png)\n\n$$公式公式$$\n\n真正内容。"
        self.assertEqual(content_metrics(text)["prose_units"], 4)

    def test_repeated_paragraph_is_counted_once(self):
        paragraph = "这是用于验证重复正文不应增加有效内容量的独立段落，其中说明方法边界与约束。"
        self.assertEqual(content_metrics(paragraph)["prose_units"], content_metrics(paragraph + "\n\n" + paragraph)["prose_units"])
        self.assertEqual(content_metrics(paragraph + "\n\n" + paragraph)["duplicate_paragraph_groups"], 1)

    def test_budgets_sum_to_contract(self):
        sections = [{"suggested_word_budget": f"{n}-10000"} for n in (1200, 1800, 6000, 1000, 2200, 1000, 800)]
        allocate_budgets(sections, DEFAULT_CONTRACT)
        budgets = [list(map(int, s["suggested_word_budget"].split("-"))) for s in sections]
        self.assertEqual(sum(b[0] for b in budgets), 24000)
        self.assertEqual(sum(b[1] for b in budgets), 32000)

    def test_references_cannot_hide_short_body(self):
        sections = [{"heading": "方法", "suggested_word_budget": "10-20"}]
        gate = build_content_depth_gate("## 方法\n短文\n\n## 参考文献\n" + "文献" * 100, sections, {"body_units_min": 10})
        self.assertFalse(gate["passed"])
        self.assertEqual(gate["prose_units"], 2)

    def test_good_volume_still_requires_render_and_semantics(self):
        gate = build_content_depth_gate("## 方法\n输入数据按采集时间排序。", [{"heading": "方法", "suggested_word_budget": "10-20"}], {"body_units_min": 10})
        self.assertTrue(gate["passed"])
        self.assertIn("pending", gate["render_verification"])

    def test_missing_or_duplicate_chapter_fails(self):
        section = [{"heading": "方法", "suggested_word_budget": "1-10"}]
        for draft in ("## 错误标题\n内容", "## 方法\n内容\n## 方法\n其他内容"):
            self.assertFalse(build_content_depth_gate(draft, section, {"body_units_min": 1})["passed"])

    def test_chapter_gate_rejects_table_padding(self):
        gate = build_length_gate({"chapter_type": "body_section", "suggested_word_budget": "100-200"}, "## 方法\n\n有效正文\n\n| " + "填表" * 200 + " |")
        self.assertFalse(gate["passed"])


if __name__ == "__main__":
    unittest.main()

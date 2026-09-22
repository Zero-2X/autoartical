import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from text_quality import audit_text_quality


class TextQualityTests(unittest.TestCase):
    def test_short_text_fails_long_form_quality(self):
        report = audit_text_quality("## 问题\n\n这是一个问题。\n\n## 方法\n\n输入数据，输出结果，解释机制。\n\n## 实验\n\nbenchmark、基线、指标、数据划分、消融。\n\n## 风险\n\n说明边界和局限。")
        self.assertFalse(report["passed"])
        self.assertTrue(report["short_document"])
        self.assertTrue(any("有效正文不足" in item for item in report["failures"]))

    def test_quality_report_tracks_thin_paragraphs_and_semantic_terms(self):
        text = "\n\n".join([
            "研究问题需要明确输入、输出和机制。",
            "实验使用 benchmark、基线、指标、数据划分和消融。",
            "风险边界和局限需要记录。",
        ])
        report = audit_text_quality(text)
        self.assertIn("thin_paragraph_ratio", report)
        self.assertTrue(report["term_status"]["experiment_protocol"])

    def test_table_metadata_is_required_when_tables_are_present(self):
        text = "研究问题、方法机制、benchmark、基线、指标、数据划分、消融、边界和风险。\n\n| 指标 | 数值 |\n|---|---|\n| AP50 | 0.8 |"
        report = audit_text_quality(text)
        self.assertTrue(report["table_blocks"])
        self.assertFalse(report["table_quality"]["has_sources"])
        self.assertTrue(any("表格解释元数据缺失" in item for item in report["failures"]))


if __name__ == "__main__":
    unittest.main()

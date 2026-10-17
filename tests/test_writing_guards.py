"""Regression tests for the revision guard and the cross-section audit.

Methods adapted (re-implemented) from mumdark/nature-writing-studio: rewrite
traceability, evidence-tier consistency and cross-section rules.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))

from cross_section_audit import audit  # noqa: E402
from manuscript_lint import lint  # noqa: E402
from revision_guard import guard  # noqa: E402

SOURCE = "我们用 CRISPRi 筛选了 287 个转录因子，找到 ZNF219 抑制神经分化[3]。"


class RevisionGuardTests(unittest.TestCase):
    def test_faithful_translation_passes(self):
        out = "Here we applied CRISPRi screening to 287 transcription factors and identified ZNF219 as a repressor of neural differentiation [3]."
        self.assertEqual(guard(SOURCE, out)["verdict"], "pass")

    def test_invented_number_citation_figure_and_entity_fail(self):
        out = "Here we screened 287 factors in 12 cell lines (Fig. 3) and identified ZNF219 and SOX2 [3,4]."
        tokens = {(t["kind"], t["token"]) for t in guard(SOURCE, out)["untraceable_tokens"]}
        self.assertIn(("numbers", "12"), tokens)
        self.assertIn(("citations", "4"), tokens)
        self.assertIn(("labels", "fig.3"), tokens)
        self.assertIn(("identifiers", "SOX2"), tokens)

    def test_dropped_evidence_is_reported(self):
        result = guard(SOURCE, "我们筛选了转录因子，找到 ZNF219 抑制神经分化。")
        dropped = {t["token"] for t in result["dropped_tokens"]}
        self.assertIn("287", dropped)
        self.assertIn("3", dropped)

    def test_allow_list_and_english_em_dash(self):
        out = SOURCE + " GPL（GNU 通用公共许可证）。"
        self.assertEqual(guard(SOURCE + " GPL", out, {"GNU"})["verdict"], "pass")
        self.assertEqual(guard("We identified X.", "We identified X — a repressor.")["verdict"], "fail")
        self.assertEqual(guard("视觉—语言模型。", "视觉—语言模型很常用。")["verdict"], "pass")


def body(text):
    return text, {}


class CrossSectionAuditTests(unittest.TestCase):
    def run_audit(self, text, glossary=None, refs=None):
        return audit(text, text, refs or {}, glossary=glossary)

    def test_overclaim_in_plan_document_fails(self):
        text = "## 第1章 实验\n\n结果待实测。本文方法显著提升了新类召回。\n"
        self.assertTrue(any("结论强度" in f for f in self.run_audit(text)["failures"]))
        hedged = "## 第1章 实验\n\n结果待实测。本文预期该方法能否提升新类召回将由 E1 检验。\n"
        self.assertFalse(any("结论强度" in f for f in self.run_audit(hedged)["failures"]))

    def test_background_claim_without_citation_fails(self):
        text = "## 第1章 绪论\n\n研究表明遥感检测类别有限。\n"
        self.assertTrue(any("背景性断言" in f for f in self.run_audit(text)["failures"]))
        cited = "## 第1章 绪论\n\n研究表明遥感检测类别有限[1]。\n"
        self.assertFalse(any("背景性断言" in f for f in self.run_audit(cited)["failures"]))

    def test_glossary_variant_and_promotional_phrases_fail(self):
        text = "## 第1章 方法\n\n有向框能贴合目标，该设计具有重要意义。\n"
        failures = " ".join(self.run_audit(text, {"terms": {"旋转框": {"avoid": ["有向框"]}}})["failures"])
        self.assertIn("有向框", failures)
        self.assertIn("具有重要意义", failures)

    def test_abbreviation_and_transition_warnings(self):
        text = "## 第1章 绪论\n\n检测用 IoU 衡量重叠。\n\n## 第2章 方法\n\n方法由三部分组成。\n"
        warnings = " ".join(self.run_audit(text)["warnings"])
        self.assertIn("IoU", warnings)
        self.assertIn("第2章", warnings)
        ok = "## 第1章 绪论\n\n检测用交并比（IoU）衡量重叠。\n\n## 第2章 方法\n\n第1章提出的问题由三部分方法回答。\n"
        self.assertEqual(self.run_audit(ok)["warnings"], [])

    def test_lint_integrates_audit(self):
        text = "## 第1章 绪论\n\n普遍认为该问题已经解决，因此需要进一步的系统研究与比较分析来回答它是否成立。\n"
        self.assertTrue(any("背景性断言" in f for f in lint(text)["failures"]))


if __name__ == "__main__":
    unittest.main()

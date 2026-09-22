import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from run_research import derive_brief, gate


class ResearchWorkflowTests(unittest.TestCase):
    def test_questions_cover_requested_research_chain(self):
        brief = derive_brief(Path("topic"), {"project_name": "研究主题", "problem": "问题", "core_innovations": ["机制"]}, [])
        questions = "\n".join(item["question"] for item in brief["research_questions"])
        for phrase in ("研究领域", "子领域", "通用挑战", "Current methods", "关键研究问题", "rationale", "case study", "benchmark", "metrics"):
            self.assertIn(phrase, questions)

    def test_unverified_or_missing_protocol_blocks_document_planning(self):
        brief = derive_brief(Path("topic"), {"project_name": "主题", "problem": "问题", "core_innovations": ["机制"]}, [])
        result = gate(brief)
        self.assertEqual(result["verdict"], "needs_research")
        self.assertTrue(result["blocking"])
        self.assertIn("experiment_plan.benchmarks", result["missing"])

    def test_verified_external_evidence_can_fill_domain_and_subdomain(self):
        items = [
            {"evidence_id": "ev1", "source_role": "reference", "curation_status": "reviewed"},
            {"evidence_id": "ev2", "source_role": "external_research", "evidence_kind": "research_finding", "curation_status": "reviewed"},
        ]
        brief = derive_brief(Path("topic"), {"project_name": "主题", "problem": "问题", "core_innovations": ["机制"]}, items)
        self.assertEqual(brief["domain"]["evidence_ids"], ["ev1", "ev2"])
        self.assertEqual(brief["subdomain"]["evidence_ids"], ["ev2"])

    def test_gate_requires_claims_and_experiment_protocol(self):
        brief = derive_brief(Path("topic"), {"project_name": "主题", "problem": "问题", "core_innovations": ["机制"]}, [])
        brief["domain"]["evidence_ids"] = ["ev1"]
        brief["subdomain"]["evidence_ids"] = ["ev2"]
        brief["current_methods"] = [{"category": "方法类", "strengths": ["优点"], "limitations": ["缺点"], "evidence_ids": ["ev3"]}]
        brief["key_gap"]["research_question"] = "问题"
        brief["design_rationale"] = [{"rationale": "原因", "testable_prediction": "预测"}]
        brief["experiment_plan"].update({"benchmarks": ["B"], "baselines": ["M"], "success_criteria": ["C"]})
        self.assertEqual(gate(brief)["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()

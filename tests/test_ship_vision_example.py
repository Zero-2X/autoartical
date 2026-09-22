import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "ship-vision"


class ShipVisionExampleTests(unittest.TestCase):
    def test_proposal_contains_research_chain_and_experiment_contract(self):
        text = (EXAMPLE / "proposal.md").read_text(encoding="utf-8")
        for phrase in ["研究领域", "子领域", "科学问题", "现有方法", "案例研究", "benchmark", "基线", "指标", "风险", "参考文献"]:
            self.assertIn(phrase, text)

    def test_structured_seed_is_valid_and_does_not_claim_completed_results(self):
        brief = json.loads((EXAMPLE / "workspace" / "research" / "research-brief.json").read_text(encoding="utf-8"))
        gate = json.loads((EXAMPLE / "workspace" / "research" / "research-gate.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["verdict"], "needs_research")
        self.assertTrue(brief["experiment_plan"]["benchmarks"])
        self.assertTrue(brief["experiment_plan"]["baselines"])
        self.assertTrue(brief["experiment_plan"]["metrics"])
        proposal = (EXAMPLE / "proposal.md").read_text(encoding="utf-8")
        self.assertIn("研究计划", proposal)
        self.assertIn("不把预期指标写成已完成成果", proposal)


if __name__ == "__main__":
    unittest.main()

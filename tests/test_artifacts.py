import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArtifactTests(unittest.TestCase):
    def test_research_skill_is_actionable(self):
        text = (ROOT / "skills" / "academic-research-writing" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("research-gate.json", "Current methods", "testable prediction", "benchmark", "metrics"):
            self.assertIn(phrase, text)

    def test_workflow_html_is_offline_and_complete(self):
        html = (ROOT / "docs" / "workflow.html").read_text(encoding="utf-8")
        for phrase in ("自动研究", "Current methods", "benchmark", "research-gate", "document-writing"):
            self.assertIn(phrase, html)
        self.assertNotIn("https://cdn.", html)


if __name__ == "__main__":
    unittest.main()

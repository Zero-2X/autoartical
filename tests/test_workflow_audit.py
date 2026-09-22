import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from audit_workflow import audit


ROOT = Path(__file__).resolve().parents[1]


class WorkflowAuditTests(unittest.TestCase):
    def test_repository_audit_detects_short_seed_and_validates_hard_gates(self):
        report = audit(ROOT)
        self.assertEqual(report["verdict"], "pass")
        self.assertTrue(any(item["short_against_default_contract"] for item in report["sample_docs"]))
        self.assertTrue(report["checks"]["evaluator_has_long_form_mode"])
        self.assertTrue(report["checks"]["export_requires_render_report"])


if __name__ == "__main__":
    unittest.main()

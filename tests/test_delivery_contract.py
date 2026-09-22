import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from delivery_contract import build_visual_gate, iter_visual_specs
from content_depth import DEFAULT_CONTRACT


class DeliveryContractTests(unittest.TestCase):
    def test_visual_gate_requires_real_assets_and_body_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset_dir = root / "workspace" / "document_assets" / "figures"
            asset_dir.mkdir(parents=True)
            (asset_dir / "architecture.png").write_bytes(b"png")
            plan = {
                "content_contract": {
                    "visual_contract": {
                        "required_specs_min": 2,
                        "required_external_assets_min": 1,
                        "required_tables_min": 1,
                        "required_diagrams_min": 1,
                        "required_case_or_ui_visuals_min": 1,
                        "required_asset_ratio": 1.0,
                        "all_visuals_must_be_cited": True,
                    }
                },
                "sections": [{
                    "visual_specs": [
                        {"visual_id": "architecture", "label": "图1-1", "title": "总体架构图", "visual_type": "figure", "required": True, "asset_candidates": ["figures/architecture.png"]},
                        {"visual_id": "case", "label": "图1-2", "title": "案例回放界面", "visual_type": "figure", "required": True, "asset_candidates": ["figures/case.png"]},
                        {"visual_id": "metrics", "label": "表1-1", "title": "指标定义表", "visual_type": "table", "required": True, "asset_candidates": []},
                    ]
                }],
            }
            draft = "如图1-1所示，系统由四层组成。\n\n如图1-2所示，案例回放保留证据。\n\n| 指标 | 单位 |\n|---|---|\n| IDF1 | % |"
            gate = build_visual_gate(root, plan, draft)
            self.assertFalse(gate["passed"])
            self.assertTrue(any("外部视觉资产完成率不足" in item for item in gate["failures"]))
            self.assertEqual(gate["available_assets"], 1)

    def test_default_contract_makes_visual_and_export_requirements_explicit(self):
        self.assertGreaterEqual(DEFAULT_CONTRACT["visual_contract"]["required_specs_min"], 18)
        self.assertIn("pdf_or_docx", DEFAULT_CONTRACT["export_contract"]["required_formats"])

    def test_html_only_export_writes_manifest_without_claiming_rendered_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "workspace" / "document_plan").mkdir(parents=True)
            (root / "workspace" / "document_writing").mkdir(parents=True)
            (root / "workspace" / "document_review").mkdir(parents=True)
            plan = {
                "project_name": "测试项目",
                "content_contract": {"body_units_min": 1, "visual_contract": {"required_specs_min": 0, "required_external_assets_min": 0, "required_tables_min": 0, "required_diagrams_min": 0, "required_case_or_ui_visuals_min": 0, "required_asset_ratio": 1.0, "all_visuals_must_be_cited": True}},
                "sections": [{"heading": "正文", "suggested_word_budget": "1-1"}],
            }
            (root / "workspace" / "document_plan" / "section-plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            (root / "workspace" / "document_writing" / "作品书草稿.md").write_text("# 测试项目\n\n## 正文\n\n有效内容。\n", encoding="utf-8")
            (root / "workspace" / "document_review" / "quality-gate.json").write_text(json.dumps({"verdict": "pass"}), encoding="utf-8")
            script = Path(__file__).resolve().parents[1] / "workflow" / "scripts" / "run_document_export.py"
            result = subprocess.run([sys.executable, str(script), str(root), "--allow-html-only"], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "workspace" / "document_export" / "export-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["final_verdict"], "pass")
            self.assertFalse(manifest["render_gate"]["verified"])
            self.assertTrue((root / "output" / "作品书_测试项目.html").exists())


if __name__ == "__main__":
    unittest.main()

import json
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from delivery_contract import build_visual_gate, iter_visual_specs
from content_depth import DEFAULT_CONTRACT
from visual_prompting import manuscript_context, compose_prompt, manuscript_sha256


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
            self.assertEqual(gate["available_assets"], 0)
            self.assertIn("architecture", gate["invalid_assets"])

    def test_visual_gate_requires_article_prompt_builtin_provenance_and_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            figures = root / "workspace" / "document_assets" / "figures"
            figures.mkdir(parents=True)
            visual_id = "architecture"
            asset = figures / f"{visual_id}.png"
            asset.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 8 + struct.pack(">II", 1672, 941) + b"x" * 100_001)
            prompt = "Detailed article-grounded scientific illustration. " * 12
            draft = "如图1-1所示，输入通向校准。\n\n![图1-1 总体架构图](workspace/document_assets/figures/architecture.png)"
            request = {
                "figure_id": visual_id,
                "route": "Codex built-in image_gen",
                "status": "reviewed",
                "source_draft_sha256": manuscript_sha256(draft),
                "article_understanding": {
                    "context_excerpt": "这段正文详细解释影像、查询、候选、校准和证据卡之间的关系及其边界。" * 3,
                    "key_message": "四层架构把开放查询与风险校准连接起来，并保留可回放证据。",
                    "visual_elements": ["影像", "文本查询", "旋转候选", "证据卡"],
                    "evidence_boundary": "这是拟议架构的示意，不是已经获得的实验结果。",
                },
                "prompt": prompt,
                "generation": {
                    "tool": "image_gen.imagegen",
                    "source_path": "/tmp/generated_images/example.png",
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "asset_sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
                },
                "visual_review": {"status": "pass", "semantic_fidelity": True, "legibility": True,
                                  "uniqueness": True, "no_fabrication": True,
                                  "note": "已逐项检查层级关系、清晰度、独特性和事实边界，图意与正文一致。"},
            }
            (figures / f"{visual_id}.request.json").write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            plan = {"sections": [{"visual_specs": [{"visual_id": visual_id, "label": "图1-1", "title": "总体架构图", "visual_type": "figure"}]}]}
            self.assertTrue(build_visual_gate(root, plan, draft)["passed"])
            request["prompt"] += "Changed after generation"
            (figures / f"{visual_id}.request.json").write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            self.assertFalse(build_visual_gate(root, plan, draft)["passed"])

    def test_prompt_uses_planned_subsection_not_grouped_figure_appendix(self):
        draft = "### 机制说明\n\n" + "具体机制输入、处理、输出及风险边界。" * 5 + "\n\n### 图形证据\n\n![图1-1](figures/architecture.svg)"
        context = manuscript_context(draft, {"visual_id": "architecture", "suggested_subsection": "机制说明"})
        self.assertEqual(context["section_heading"], "机制说明")
        self.assertIn("具体机制", context["context_excerpt"])
        request = {"article_understanding": {**context, "key_message": "用分层结构解释系统如何产生可回放证据。",
                "visual_elements": ["影像输入", "候选框", "风险校准"], "evidence_boundary": "架构示意尚未提供实验数值。",
                "visual_direction": "采用分层剖面和贯穿的数据流，而非通用方框模板。"}}
        self.assertGreater(len(compose_prompt(request)), 400)

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
            result = subprocess.run([sys.executable, str(script), str(root), "--allow-html-only"], text=True, encoding="utf-8", errors="replace", capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((root / "workspace" / "document_export" / "export-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["final_verdict"], "pass")
            self.assertFalse(manifest["render_gate"]["verified"])
            self.assertTrue((root / "output" / "作品书_测试项目.html").exists())


if __name__ == "__main__":
    unittest.main()

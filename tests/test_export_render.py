import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from run_document_export import _image_data_uri, _split_render_chunks, build_doctoral_front_matter, markdown_to_html
from document_formatting import drop_empty_headings, merge_fragmented_paragraphs, number_markdown_headings


class ExportRenderTests(unittest.TestCase):
    def test_render_chunks_preserve_table_boundaries(self):
        text = "\n\n".join(
            [
                "## 章节\n\n" + "遥感检测论证。" * 120,
                "表1\n\n| 方法 | 指标 |\n|---|---|\n| A | NA |\n| B | NA |",
            ]
        )
        chunks = _split_render_chunks(text, target_units=100)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(any("| 方法 | 指标 |" in chunk for chunk in chunks))
        self.assertTrue(all(chunk.strip() for chunk in chunks))

    def test_local_png_is_inlined_into_html(self):
        image = Path(__file__).resolve().parents[1] / "examples" / "ovd-rsi" / "workspace" / "document_assets" / "figures" / "s_validation_visual_4.png"
        uri = _image_data_uri(str(image))
        self.assertTrue(uri.startswith("data:image/png;base64,"))
        rendered = markdown_to_html(f"![场景图]({image})", "test")
        self.assertIn("<img", rendered)
        self.assertIn("data:image/", rendered)

    def test_delivery_copy_numbers_headings_and_merges_fragmented_prose(self):
        source = "# 标题\n\n## 一、概述\n\n### 背景\n\n短句一。\n\n短句二。\n\n#### 约束\n"
        numbered = number_markdown_headings(source)
        self.assertIn("## 第1章 概述", numbered)
        self.assertIn("### 1.1 背景", numbered)
        self.assertIn("#### 1.1.1 约束", numbered)
        merged = merge_fragmented_paragraphs(source)
        self.assertIn("短句一。短句二。", merged)

    def test_empty_placeholder_headings_are_removed_from_delivery_copy(self):
        source = "### 占位一\n\n### 占位二\n\n### 有正文\n\n论证内容。"
        cleaned = drop_empty_headings(source)
        self.assertNotIn("占位一", cleaned)
        self.assertNotIn("占位二", cleaned)
        self.assertIn("有正文", cleaned)

    def test_front_matter_toc_uses_explicit_numbering(self):
        formatted = build_doctoral_front_matter("# 标题\n\n## 一、概述\n\n正文。\n", "标题")
        self.assertIn("## 0.1 材料真实性与数据许可说明", formatted)
        self.assertIn("## 第1章 概述", formatted)
        self.assertIn("- 4. 第1章 概述", formatted)


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from run_document_export import _image_data_uri, _split_render_chunks, markdown_to_html


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


if __name__ == "__main__":
    unittest.main()

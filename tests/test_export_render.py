import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from run_document_export import _split_render_chunks


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


if __name__ == "__main__":
    unittest.main()

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from source_ingestion import extract_source
from validate_evidence import validate_ledger


class SourceIngestionTests(unittest.TestCase):
    def test_text_is_cached_with_hash_and_line_locations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text("第一行\n第二行", encoding="utf-8")
            result = extract_source(source, root / "cache")
            self.assertEqual(result["engine"], "builtin")
            self.assertTrue(result["source_sha256"])
            self.assertTrue(Path(result["cache_path"]).exists())
            self.assertEqual(result["segments"][1]["locator"], "line:2")

    def test_ledger_reads_actual_evidence_items_key(self):
        report = validate_ledger({"evidence_items": [{"source_title": "A", "claim": "B", "summary": "C"}]})
        self.assertIn("evidence_check", report)
        self.assertNotEqual(report["verdict"], "fail")


if __name__ == "__main__":
    unittest.main()

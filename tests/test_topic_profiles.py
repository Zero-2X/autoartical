import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow" / "scripts"))
from run_evidence import should_skip_reference
from topic_profiles import resolve_topic_profile


class TopicProfileTests(unittest.TestCase):
    def test_remote_sensing_open_vocabulary_profile_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = resolve_topic_profile(
                root,
                explicit_topic="开放词汇检测与RSI",
                context_text="remote sensing image DIOR DOTA open-vocabulary object detection",
            )
        self.assertEqual(profile["profile_id"], "remote_sensing_open_vocabulary_detection")
        self.assertGreaterEqual(len(profile["idea_templates"]), 3)

    def test_external_evidence_readme_is_skipped_on_windows_paths(self):
        self.assertTrue(should_skip_reference("external_evidence\\README.md"))


if __name__ == "__main__":
    unittest.main()

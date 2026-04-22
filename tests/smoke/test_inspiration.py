from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.services.inspiration import (
    generate_character_suggestions,
    generate_name,
    generate_outline_skeleton,
    generate_world_suggestions,
)


class InspirationTest(unittest.TestCase):
    def test_generate_name_returns_string(self):
        name = generate_name()
        self.assertIsInstance(name, str)
        self.assertTrue(len(name) >= 2)

    def test_generate_character_suggestions_returns_list(self):
        results = generate_character_suggestions(count=3)
        self.assertEqual(len(results), 3)
        for item in results:
            self.assertIn("archetype", item)
            self.assertIn("personality", item)
            self.assertIn("motivation", item)

    def test_generate_world_suggestions_returns_list(self):
        results = generate_world_suggestions(count=2)
        self.assertEqual(len(results), 2)
        for item in results:
            self.assertIn("era", item)
            self.assertIn("location", item)

    def test_generate_outline_skeleton(self):
        volumes = [
            {"title": "第一卷", "chapterCount": 3},
            {"title": "第二卷", "chapterCount": 2},
        ]
        result = generate_outline_skeleton(volumes)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]["chapters"]), 3)
        self.assertEqual(len(result[1]["chapters"]), 2)


if __name__ == "__main__":
    unittest.main()

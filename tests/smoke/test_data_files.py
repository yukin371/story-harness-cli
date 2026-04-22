from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class DataFilesTest(unittest.TestCase):
    DATA_DIR = SRC_ROOT / "story_harness_cli" / "data"

    def _load(self, name):
        text = (self.DATA_DIR / name).read_text(encoding="utf-8")
        return json.loads(text)

    def test_archetypes_loadable(self):
        data = self._load("archetypes.yaml")
        self.assertIn("archetypes", data)
        self.assertTrue(len(data["archetypes"]) >= 10)

    def test_motivations_loadable(self):
        data = self._load("motivations.yaml")
        self.assertIn("motivations", data)

    def test_personalities_loadable(self):
        data = self._load("personalities.yaml")
        self.assertIn("dimensions", data)
        self.assertIn("traits", data)

    def test_conflicts_loadable(self):
        data = self._load("conflicts.yaml")
        self.assertIn("conflictTypes", data)

    def test_world_elements_loadable(self):
        data = self._load("world_elements.yaml")
        self.assertIn("eras", data)
        self.assertIn("locations", data)

    def test_names_cn_loadable(self):
        data = self._load("names_cn.yaml")
        self.assertIn("surnames", data)
        self.assertIn("givenNamesMale", data)
        self.assertIn("givenNamesFemale", data)


if __name__ == "__main__":
    unittest.main()

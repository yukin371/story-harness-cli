from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.utils.text import (
    appearance_tags_for_paragraph,
    ability_tags_for_paragraph,
)


class TextExtendedTest(unittest.TestCase):
    def test_appearance_tags(self):
        tags = appearance_tags_for_paragraph("她有一头乌黑的长发，眼睛是琥珀色的")
        self.assertIn("长发", tags)
        self.assertIn("琥珀色眼睛", tags)

    def test_ability_tags(self):
        tags = ability_tags_for_paragraph("林舟一拳击碎木板，身法敏捷如风")
        self.assertTrue(len(tags) > 0)

    def test_no_tags_for_plain_text(self):
        self.assertEqual(appearance_tags_for_paragraph("天空飘着小雨"), [])
        self.assertEqual(ability_tags_for_paragraph("他走进房间"), [])


if __name__ == "__main__":
    unittest.main()

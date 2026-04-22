from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.protocol.schema import default_project_state


class SchemaTest(unittest.TestCase):
    def test_entities_has_enrichment_proposals_field(self):
        state = default_project_state()
        entities = state["entities"]
        self.assertIn("entities", entities)
        self.assertIn("enrichmentProposals", entities)

    def test_outline_has_volumes(self):
        state = default_project_state()
        outline = state["outline"]
        self.assertIn("volumes", outline)
        self.assertIsInstance(outline["volumes"], list)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.cli import main


class BrainstormCommandTest(unittest.TestCase):
    def test_brainstorm_character_random(self):
        result = main(["brainstorm", "character", "--random"])
        self.assertEqual(result, 0)

    def test_brainstorm_world_random(self):
        result = main(["brainstorm", "world", "--random"])
        self.assertEqual(result, 0)

    def test_brainstorm_outline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ["chapters", "proposals", "reviews", "projections", "logs"]:
                (root / d).mkdir()
            for name, content in [
                ("project.yaml", '{"title":"test"}'),
                ("outline.yaml", '{"volumes":[],"chapters":[],"chapterDirections":[]}'),
                ("entities.yaml", '{"entities":[],"enrichmentProposals":[]}'),
                ("timeline.yaml", '{"events":[]}'),
                ("branches.yaml", '{"branches":[]}'),
                ("proposals/draft-proposals.yaml", '{"draftProposals":[]}'),
                ("reviews/change-requests.yaml", '{"changeRequests":[]}'),
                ("projections/projection.yaml", '{"snapshotProjections":[],"relationProjections":[],"sceneScopeProjections":[],"timelineProjections":[],"causalityProjections":[]}'),
                ("projections/context-lens.yaml", '{"currentChapterId":null,"lenses":[]}'),
                ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
            ]:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(content + "\n", encoding="utf-8")

            result = main([
                "brainstorm", "outline",
                "--root", str(root),
                "--volumes", "2",
                "--chapters-per-volume", "3",
            ])
            self.assertEqual(result, 0)
            outline = json.loads((root / "outline.yaml").read_text(encoding="utf-8"))
            self.assertTrue(len(outline.get("volumes", [])) > 0)


if __name__ == "__main__":
    unittest.main()

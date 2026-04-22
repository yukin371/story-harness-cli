from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.cli import main


def _setup_project(tmp: Path):
    fixture = REPO_ROOT / "tests" / "fixtures" / "minimal_project"
    shutil.copytree(fixture, tmp, dirs_exist_ok=True)
    for d in ["proposals", "reviews", "projections", "logs"]:
        (tmp / d).mkdir(exist_ok=True)
    entities = {
        "entities": [
            {
                "id": "char-linzhou", "name": "林舟", "source": "seed", "aliases": [],
                "seed": {"archetype": "落魄侦探", "personality": "冷静", "motivation": "追查真相", "background": "前刑侦"},
                "profile": {"appearance": [], "abilities": [], "speech": [], "relationships": []},
                "currentState": {"status": "active", "physicalState": [], "emotionalState": [], "location": "未知", "lastUpdatedChapter": None},
                "createdAt": "2026-01-01T00:00:00",
            }
        ],
        "enrichmentProposals": [],
    }
    (tmp / "entities.yaml").write_text(json.dumps(entities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, content in [
        ("proposals/draft-proposals.yaml", '{"draftProposals":[]}'),
        ("reviews/change-requests.yaml", '{"changeRequests":[]}'),
        ("projections/projection.yaml", '{"snapshotProjections":[],"relationProjections":[],"sceneScopeProjections":[],"timelineProjections":[],"causalityProjections":[]}'),
        ("projections/context-lens.yaml", '{"currentChapterId":null,"lenses":[]}'),
        ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
    ]:
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_text(content + "\n", encoding="utf-8")


class EntityCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-entity-"))
        _setup_project(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_entity_enrich_command(self):
        result = main([
            "entity", "enrich",
            "--root", str(self.temp_dir),
            "--chapter-id", "chapter-001",
        ])
        self.assertEqual(result, 0)

    def test_entity_review_apply(self):
        main(["entity", "enrich", "--root", str(self.temp_dir), "--chapter-id", "chapter-001"])
        result = main([
            "entity", "review",
            "--root", str(self.temp_dir),
            "--all-pending",
            "--decision", "accepted",
        ])
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()

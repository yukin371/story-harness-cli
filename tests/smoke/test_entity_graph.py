from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.cli import main
from story_harness_cli.protocol import save_state


def _setup_project(tmp: Path, entities=None, relations=None):
    fixture = REPO_ROOT / "tests" / "fixtures" / "minimal_project"
    shutil.copytree(fixture, tmp, dirs_exist_ok=True)
    for d in ["proposals", "reviews", "projections", "logs"]:
        (tmp / d).mkdir(exist_ok=True)
    for name, content in [
        ("entities.yaml", json.dumps({"entities": entities or [], "enrichmentProposals": []})),
        ("proposals/draft-proposals.yaml", '{"draftProposals":[]}'),
        ("reviews/change-requests.yaml", '{"changeRequests":[]}'),
        (
            "projections/projection.yaml",
            json.dumps({
                "snapshotProjections": [],
                "relationProjections": relations or [],
                "sceneScopeProjections": [],
                "timelineProjections": [],
                "causalityProjections": [],
            }),
        ),
        ("projections/context-lens.yaml", '{"currentChapterId":null,"lenses":[]}'),
        ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
    ]:
        (tmp / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp / name).write_text(content + "\n", encoding="utf-8")


class EntityGraphTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-graph-"))
        self.entities = [
            {"id": "char-linzhou", "name": "林舟", "type": "character", "aliases": [], "source": "seed"},
            {"id": "char-shenzhao", "name": "沈昭", "type": "character", "aliases": [], "source": "seed"},
            {"id": "char-suqing", "name": "苏晴", "type": "character", "aliases": [], "source": "seed"},
        ]
        self.relations = [
            {
                "fromId": "char-linzhou", "fromName": "林舟",
                "toId": "char-shenzhao", "toName": "沈昭",
                "label": "裂痕", "scopeRef": "chapter-001", "updatedAt": "2026-01-01",
            },
            {
                "fromId": "char-linzhou", "fromName": "林舟",
                "toId": "char-suqing", "toName": "苏晴",
                "label": "合作", "scopeRef": "chapter-001", "updatedAt": "2026-01-01",
            },
            {
                "fromId": "char-shenzhao", "fromName": "沈昭",
                "toId": "char-suqing", "toName": "苏晴",
                "label": "信任", "scopeRef": "chapter-002", "updatedAt": "2026-01-02",
            },
        ]
        _setup_project(self.temp_dir, self.entities, self.relations)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_entity_graph_mermaid(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["entity", "graph", "--root", str(self.temp_dir)])
        self.assertEqual(result, 0)
        output = buf.getvalue()
        self.assertIn("graph LR", output)
        self.assertIn("林舟", output)
        self.assertIn("沈昭", output)
        self.assertIn("裂痕", output)

    def test_entity_graph_dot(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["entity", "graph", "--root", str(self.temp_dir), "--format", "dot"])
        self.assertEqual(result, 0)
        output = buf.getvalue()
        self.assertIn("digraph", output)
        self.assertIn("->", output)
        self.assertIn("林舟", output)

    def test_entity_graph_filtered_by_chapter(self):
        buf = StringIO()
        with redirect_stdout(buf):
            result = main(["entity", "graph", "--root", str(self.temp_dir), "--chapter-id", "chapter-001"])
        self.assertEqual(result, 0)
        output = buf.getvalue()
        self.assertIn("裂痕", output)
        # chapter-002 relation should be excluded
        # "信任" is the label for chapter-002 relation between 沈昭 and 苏晴
        self.assertNotIn("信任", output)

    def test_entity_graph_empty(self):
        tmp2 = Path(tempfile.mkdtemp(prefix="story-harness-graph-empty-"))
        try:
            _setup_project(tmp2)
            buf = StringIO()
            with redirect_stdout(buf):
                result = main(["entity", "graph", "--root", str(tmp2)])
            self.assertEqual(result, 0)
            output = buf.getvalue()
            self.assertIn("graph LR", output)
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

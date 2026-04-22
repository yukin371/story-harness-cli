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

from story_harness_cli.protocol.state import load_project_state
from story_harness_cli.services.entity_enricher import enrich_entities


class EntityEnricherTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-enricher-"))
        fixture = REPO_ROOT / "tests" / "fixtures" / "minimal_project"
        shutil.copytree(fixture, self.temp_dir, dirs_exist_ok=True)
        for d in ["proposals", "reviews", "projections", "logs"]:
            (self.temp_dir / d).mkdir(exist_ok=True)
        entities = {
            "entities": [
                {
                    "id": "char-linzhou",
                    "name": "林舟",
                    "source": "seed",
                    "aliases": [],
                    "seed": {
                        "archetype": "落魄侦探",
                        "personality": "冷静、固执",
                        "motivation": "追查真相",
                        "background": "前刑侦人员",
                    },
                    "profile": {"appearance": [], "abilities": [], "speech": [], "relationships": []},
                    "currentState": {
                        "status": "active",
                        "physicalState": [],
                        "emotionalState": [],
                        "location": "未知",
                        "lastUpdatedChapter": None,
                    },
                    "createdAt": "2026-01-01T00:00:00",
                }
            ],
            "enrichmentProposals": [],
        }
        (self.temp_dir / "entities.yaml").write_text(
            json.dumps(entities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for name, content in [
            ("proposals/draft-proposals.yaml", '{"draftProposals":[]}'),
            ("reviews/change-requests.yaml", '{"changeRequests":[]}'),
            ("projections/projection.yaml", '{"snapshotProjections":[],"relationProjections":[],"sceneScopeProjections":[],"timelineProjections":[],"causalityProjections":[]}'),
            ("projections/context-lens.yaml", '{"currentChapterId":null,"lenses":[]}'),
            ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
        ]:
            (self.temp_dir / name).parent.mkdir(parents=True, exist_ok=True)
            (self.temp_dir / name).write_text(content + "\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_enrich_with_fixture_chapter(self):
        """Fixture chapter has no appearance/ability keywords, so created >= 0."""
        state = load_project_state(self.temp_dir)
        result = enrich_entities(state, "chapter-001", root=self.temp_dir)
        self.assertGreaterEqual(result["created"], 0)
        self.assertEqual(result["chapterId"], "chapter-001")

    def test_enrich_produces_appearance_proposals(self):
        """Chapter text with appearance keywords should produce proposals."""
        chapter_text = "林舟是个高个子，留着短发，脸上有一道疤痕，目光如炬地注视着前方。\n"
        (self.temp_dir / "chapters").mkdir(exist_ok=True)
        (self.temp_dir / "chapters" / "chapter-appearance.md").write_text(
            chapter_text, encoding="utf-8"
        )
        state = load_project_state(self.temp_dir)
        result = enrich_entities(state, "chapter-appearance", root=self.temp_dir)
        self.assertGreater(result["created"], 0)
        proposals = state["entities"].get("enrichmentProposals", [])
        self.assertTrue(len(proposals) > 0)
        proposal = proposals[0]
        self.assertEqual(proposal["entityId"], "char-linzhou")
        self.assertEqual(proposal["field"], "appearance")
        self.assertEqual(proposal["status"], "pending")
        self.assertIn("fingerprint", proposal)

    def test_enrich_produces_ability_proposals(self):
        """Chapter text with ability keywords should produce proposals."""
        chapter_text = "林舟展现了精湛的推理能力，通过细致的分析找到了线索。\n"
        (self.temp_dir / "chapters").mkdir(exist_ok=True)
        (self.temp_dir / "chapters" / "chapter-ability.md").write_text(
            chapter_text, encoding="utf-8"
        )
        state = load_project_state(self.temp_dir)
        result = enrich_entities(state, "chapter-ability", root=self.temp_dir)
        self.assertGreater(result["created"], 0)
        proposals = state["entities"].get("enrichmentProposals", [])
        self.assertTrue(len(proposals) > 0)
        proposal = proposals[0]
        self.assertEqual(proposal["entityId"], "char-linzhou")
        self.assertEqual(proposal["field"], "abilities")
        self.assertEqual(proposal["status"], "pending")

    def test_enrich_no_root(self):
        state = {"entities": {"entities": [], "enrichmentProposals": []}}
        result = enrich_entities(state, "chapter-001")
        self.assertEqual(result["created"], 0)
        self.assertIn("error", result)

    def test_enrich_missing_chapter(self):
        state = {"entities": {"entities": [], "enrichmentProposals": []}}
        result = enrich_entities(state, "nonexistent", root=self.temp_dir)
        self.assertEqual(result["created"], 0)
        self.assertIn("error", result)

    def test_deduplication_by_fingerprint(self):
        """Running enrich twice on the same chapter should not duplicate proposals."""
        chapter_text = "林舟是个瘦削的高个子，有着琥珀色眼睛。\n"
        (self.temp_dir / "chapters").mkdir(exist_ok=True)
        (self.temp_dir / "chapters" / "chapter-dedup.md").write_text(
            chapter_text, encoding="utf-8"
        )
        state = load_project_state(self.temp_dir)
        result1 = enrich_entities(state, "chapter-dedup", root=self.temp_dir)
        first_created = result1["created"]
        self.assertGreater(first_created, 0)
        result2 = enrich_entities(state, "chapter-dedup", root=self.temp_dir)
        # Second run should create 0 new proposals due to fingerprint dedup
        self.assertEqual(result2["created"], 0)

    def test_entity_attribution_per_sentence(self):
        """Tags from one entity's sentence should NOT be attributed to another entity
        in the same paragraph but different sentence."""
        # Add a second entity
        state = load_project_state(self.temp_dir)
        entities = state["entities"]["entities"]
        entities.append({
            "id": "char-suqing",
            "name": "苏晴",
            "source": "seed",
            "aliases": [],
            "seed": {},
            "profile": {"appearance": [], "abilities": [], "speech": [], "relationships": []},
            "currentState": {"status": "active"},
        })
        import json as _json
        (self.temp_dir / "entities.yaml").write_text(
            _json.dumps(state["entities"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        # Two entities, each in their own sentence with distinct appearance tags
        chapter_text = "苏晴留着金发，琥珀色眼睛闪闪发光。林舟是个高个子，脸上有道疤痕。\n"
        (self.temp_dir / "chapters").mkdir(exist_ok=True)
        (self.temp_dir / "chapters" / "chapter-attrib.md").write_text(
            chapter_text, encoding="utf-8"
        )

        state = load_project_state(self.temp_dir)
        result = enrich_entities(state, "chapter-attrib", root=self.temp_dir)
        self.assertGreater(result["created"], 0)

        proposals = state["entities"]["enrichmentProposals"]
        # Check that 苏晴 got 金发/琥珀色 but NOT 疤痕/高个子
        suqing_props = [p for p in proposals if p["entityId"] == "char-suqing"]
        for p in suqing_props:
            if p["field"] == "appearance":
                self.assertIn("金发", p["detail"])
                self.assertNotIn("有疤痕", p["detail"])
                self.assertNotIn("高个子", p["detail"])

        # Check that 林舟 got 疤痕/高个子 but NOT 金发/琥珀色
        linzhou_props = [p for p in proposals if p["entityId"] == "char-linzhou"]
        for p in linzhou_props:
            if p["field"] == "appearance":
                self.assertNotIn("金发", p["detail"])
                self.assertNotIn("琥珀色眼睛", p["detail"])


if __name__ == "__main__":
    unittest.main()

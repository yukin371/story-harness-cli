from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.services.consistency_engine import check_consistency


class ConsistencyEngineTest(unittest.TestCase):
    def test_deceased_entity_active_in_text(self):
        state = {
            "entities": {
                "entities": [
                    {"id": "char-a", "name": "张三", "source": "seed", "aliases": [],
                     "seed": {}, "profile": {"appearance": [], "abilities": [], "speech": [], "relationships": []},
                     "currentState": {"status": "deceased", "physicalState": [], "emotionalState": [], "location": "未知", "lastUpdatedChapter": "chapter-002"},
                     "createdAt": "2026-01-01T00:00:00"},
                ],
                "enrichmentProposals": [],
            },
            "projection": {
                "snapshotProjections": [
                    {"entityId": "char-a", "entityName": "张三", "scopeRef": "chapter-002", "currentState": "deceased", "updatedAt": "2026-01-01"},
                ],
                "relationProjections": [],
                "sceneScopeProjections": [],
                "timelineProjections": [],
                "causalityProjections": [],
            },
            "outline": {"volumes": [], "chapters": [], "chapterDirections": []},
        }
        result = check_consistency(state, "张三走进房间，坐了下来", "chapter-003")
        hard = result["hardChecks"]
        self.assertTrue(any("deceased" in str(c).lower() or "死亡" in str(c) for c in hard.get("stateContradictions", [])))

    def test_relation_contradiction(self):
        state = {
            "entities": {"entities": [], "enrichmentProposals": []},
            "projection": {
                "snapshotProjections": [],
                "relationProjections": [
                    {"fromId": "a", "fromName": "A", "toId": "b", "toName": "B", "scopeRef": "chapter-001", "label": "裂痕", "updatedAt": "2026-01-01"},
                ],
                "sceneScopeProjections": [],
                "timelineProjections": [],
                "causalityProjections": [],
            },
            "outline": {"volumes": [], "chapters": [], "chapterDirections": []},
        }
        result = check_consistency(state, "A和B亲密地拥抱在一起", "chapter-003")
        hard = result["hardChecks"]
        self.assertTrue(len(hard.get("relationContradictions", [])) > 0)

    def test_outline_deviation_soft_check(self):
        state = {
            "entities": {"entities": [], "enrichmentProposals": []},
            "projection": {"snapshotProjections": [], "relationProjections": [], "sceneScopeProjections": [], "timelineProjections": [], "causalityProjections": []},
            "outline": {
                "volumes": [
                    {"id": "vol-1", "title": "第一卷", "theme": "", "chapters": [
                        {"id": "chapter-001", "title": "第一章", "status": "completed", "direction": "", "beats": [
                            {"id": "beat-1", "summary": "开场", "status": "completed"},
                            {"id": "beat-2", "summary": "揭示真相", "status": "planned"},
                        ]},
                    ]},
                ],
                "chapters": [],
                "chapterDirections": [],
            },
        }
        result = check_consistency(state, "一些正文", "chapter-001")
        soft = result["softChecks"]
        self.assertTrue(len(soft.get("outlineDeviations", [])) > 0)

    def test_no_issues(self):
        state = {
            "entities": {"entities": [], "enrichmentProposals": []},
            "projection": {"snapshotProjections": [], "relationProjections": [], "sceneScopeProjections": [], "timelineProjections": [], "causalityProjections": []},
            "outline": {"volumes": [], "chapters": [], "chapterDirections": []},
        }
        result = check_consistency(state, "天空飘着小雨", "chapter-001")
        self.assertEqual(len(result["hardChecks"]["stateContradictions"]), 0)
        self.assertEqual(len(result["hardChecks"]["relationContradictions"]), 0)


if __name__ == "__main__":
    unittest.main()

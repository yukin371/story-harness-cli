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
from story_harness_cli.protocol.state import STATE_KEY_MAP
from story_harness_cli.protocol.files import resolve_state_path


def _write_json_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


def _build_minimal_project(root: Path, *, outline: dict, entities: dict):
    """Write a complete minimal project with given outline and entities."""
    defaults = {
        "project": {"title": "测试书名"},
        "timeline": {"events": []},
        "branches": {"branches": []},
        "proposals": {"draftProposals": []},
        "reviews": {"changeRequests": []},
        "story_reviews": {"chapterReviews": [], "sceneReviews": []},
        "projection": {"snapshotProjections": [], "relationProjections": [],
                       "sceneScopeProjections": [], "timelineProjections": [],
                       "causalityProjections": []},
        "context_lens": {"currentChapterId": None, "lenses": []},
        "projection_log": {"projectionChanges": []},
        "threads": {"threads": []},
        "structures": {"activeStructure": None, "mappings": []},
    }
    overrides = {"outline": outline, "entities": entities}
    for state_key, internal_key in STATE_KEY_MAP.items():
        data = overrides.get(internal_key, defaults.get(internal_key, {}))
        fpath = resolve_state_path(root, state_key)
        _write_json_yaml(fpath, data)

    # Ensure subdirectories exist
    for d in ["chapters", "proposals", "reviews", "projections", "logs"]:
        (root / d).mkdir(exist_ok=True)


class TestExportSpecOutline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sh-export-spec-outline-"))
        outline = {
            "chapters": [],
            "chapterDirections": [],
            "volumes": [
                {
                    "id": "volume-001",
                    "title": "雾起",
                    "chapters": [
                        {
                            "id": "chapter-001",
                            "title": "裂痕之夜",
                            "status": "completed",
                            "direction": "建立主角困境与初始悬念",
                            "beats": [
                                {"description": "林舟从噩梦中惊醒"},
                                {"description": "老陈死讯传来"},
                            ],
                            "scenePlans": [
                                {"summary": "凌晨四点，林舟惊醒"},
                                {"summary": "三天后老陈死了"},
                            ],
                        },
                        {
                            "id": "chapter-002",
                            "title": "暗影追踪",
                            "status": "draft",
                            "beats": [],
                            "scenePlans": [],
                        },
                    ],
                },
            ],
        }
        entities = {"entities": [], "enrichmentProposals": []}
        _build_minimal_project(self.temp_dir, outline=outline, entities=entities)
        self.out_file = self.temp_dir / "output.md"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_spec_outline(self):
        result = main([
            "export", "--root", str(self.temp_dir),
            "--format", "spec-outline",
            "--output", str(self.out_file),
        ])
        self.assertEqual(result, 0)
        content = self.out_file.read_text(encoding="utf-8")

        # Title
        self.assertIn("# 大纲: 测试书名", content)
        # Volume title
        self.assertIn("## 卷: 雾起", content)
        # Chapter title and status
        self.assertIn("### chapter-001: 裂痕之夜 [completed]", content)
        self.assertIn("### chapter-002: 暗影追踪 [draft]", content)
        # Direction
        self.assertIn("**方向:** 建立主角困境与初始悬念", content)
        # Beats
        self.assertIn("- 林舟从噩梦中惊醒", content)
        self.assertIn("- 老陈死讯传来", content)
        # Scenes
        self.assertIn("**场景:**", content)
        self.assertIn("1. 凌晨四点，林舟惊醒", content)
        self.assertIn("2. 三天后老陈死了", content)


class TestExportSpecCharacters(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sh-export-spec-chars-"))
        outline = {"chapters": [], "chapterDirections": [], "volumes": []}
        entities = {
            "entities": [
                {
                    "id": "entity-lin-zhou",
                    "name": "林舟",
                    "type": "character",
                    "registeredAt": "2026-04-22T10:00:00+08:00",
                    "profile": {
                        "traits": ["敏锐", "固执", "孤独"],
                        "appearance": [
                            {"detail": "中年发福，眉头紧锁"},
                            {"detail": "左肩有旧伤疤"},
                        ],
                        "abilities": [
                            {"detail": "刑侦推理"},
                            {"detail": "格斗擒拿"},
                        ],
                    },
                },
                {
                    "id": "entity-shen-zhao",
                    "name": "沈昭",
                    "type": "character",
                    "registeredAt": "",
                    "profile": {
                        "traits": [],
                        "appearance": [{"detail": "面目模糊"}],
                        "abilities": [{"detail": "情报收集"}],
                    },
                },
            ],
            "enrichmentProposals": [],
        }
        _build_minimal_project(self.temp_dir, outline=outline, entities=entities)
        self.out_file = self.temp_dir / "output.md"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_spec_characters(self):
        result = main([
            "export", "--root", str(self.temp_dir),
            "--format", "spec-characters",
            "--output", str(self.out_file),
        ])
        self.assertEqual(result, 0)
        content = self.out_file.read_text(encoding="utf-8")

        # Title
        self.assertIn("# 角色卡: 测试书名", content)
        # Entity name and type
        self.assertIn("## 林舟 (character)", content)
        self.assertIn("## 沈昭 (character)", content)
        # First mention for entity with registeredAt
        self.assertIn("> 首次出场: 2026-04-22T10:00:00+08:00", content)
        # Traits
        self.assertIn("**特质:** 敏锐, 固执, 孤独", content)
        # Appearance
        self.assertIn("**外貌:** 中年发福，眉头紧锁, 左肩有旧伤疤", content)
        self.assertIn("**外貌:** 面目模糊", content)
        # Abilities
        self.assertIn("**能力:** 刑侦推理, 格斗擒拿", content)
        self.assertIn("**能力:** 情报收集", content)


if __name__ == "__main__":
    unittest.main()

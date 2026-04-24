"""End-to-end smoke test: layered layout full workflow.

Exercises: init → outline → chapter → analyze → review → doctor → export → foreshadow.
Verifies that all output files land in the correct locations for layered layout.
"""
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


class LayeredFullLoopSmokeTest(unittest.TestCase):
    """One test method that exercises the full layered-layout workflow."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-layered-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_layered_full_loop(self) -> None:
        root = self.temp_dir
        r = str(root)

        # ------------------------------------------------------------------
        # Step 1: Init with --layout layered
        # ------------------------------------------------------------------
        rc = main([
            "init",
            "--root", r,
            "--title", "雾中密令",
            "--genre", "mystery",
            "--layout", "layered",
            "--chapter-id", "chapter-001",
            "--chapter-title", "裂痕之夜",
        ])
        self.assertEqual(rc, 0, "init should succeed")

        # Immediate layout checks after init
        self.assertTrue((root / "spec").is_dir(), "spec/ directory should exist")
        self.assertTrue((root / "spec" / "outlines").is_dir(), "spec/outlines/ should exist")
        self.assertTrue((root / "project.yaml").exists(), "project.yaml at root")
        self.assertTrue((root / "spec" / "outline.yaml").exists(),
                        "outline.yaml should be inside spec/ for layered layout")
        self.assertTrue((root / "spec" / "entities.yaml").exists(),
                        "entities.yaml should be inside spec/ for layered layout")
        self.assertFalse((root / "outline.yaml").exists(),
                         "outline.yaml should NOT be at root for layered layout")

        # Workflow dirs at root
        for d in ("chapters", "proposals", "reviews", "projections", "logs"):
            self.assertTrue((root / d).is_dir(), f"{d}/ should exist at root")

        # ------------------------------------------------------------------
        # Step 2: Write outline with 1 volume, 2 chapters
        # ------------------------------------------------------------------
        outline_path = root / "spec" / "outline.yaml"
        outline = json.loads(outline_path.read_text(encoding="utf-8"))
        outline["volumes"] = [
            {
                "id": "vol-001",
                "title": "迷雾序章",
                "theme": "真相",
                "chapters": [
                    {
                        "id": "chapter-001",
                        "title": "裂痕之夜",
                        "status": "draft",
                        "direction": "两人在仓库对峙，揭开隐藏的线索",
                        "beats": [
                            {"id": "beat-1-1", "summary": "林舟进入仓库", "status": "planned"},
                            {"id": "beat-1-2", "summary": "与沈昭对峙", "status": "planned"},
                        ],
                        "scenePlans": [
                            {
                                "id": "scene-1-1",
                                "title": "仓库初遇",
                                "summary": "林舟在昏暗仓库中撞见沈昭",
                                "startParagraph": 1,
                                "endParagraph": 3,
                            },
                        ],
                    },
                    {
                        "id": "chapter-002",
                        "title": "暗流涌动",
                        "status": "planned",
                        "direction": "沈昭消失，林舟独自追寻线索",
                        "beats": [
                            {"id": "beat-2-1", "summary": "沈昭消失", "status": "planned"},
                            {"id": "beat-2-2", "summary": "发现密信", "status": "planned"},
                        ],
                        "scenePlans": [
                            {
                                "id": "scene-2-1",
                                "title": "空荡仓库",
                                "summary": "林舟发现沈昭已经离开",
                                "startParagraph": 1,
                                "endParagraph": 2,
                            },
                        ],
                    },
                ],
            },
        ]
        outline["chapters"] = [
            {
                "id": "chapter-001",
                "title": "裂痕之夜",
                "status": "draft",
                "beats": [],
                "scenePlans": [],
            },
            {
                "id": "chapter-002",
                "title": "暗流涌动",
                "status": "planned",
                "beats": [],
                "scenePlans": [],
            },
        ]
        outline["chapterDirections"] = [
            {
                "chapterId": "chapter-001",
                "title": "裂痕之夜方向",
                "summary": "两人在仓库对峙，揭开隐藏的线索",
            },
        ]
        outline_path.write_text(
            json.dumps(outline, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        # ------------------------------------------------------------------
        # Step 3: Write chapter prose files
        # ------------------------------------------------------------------
        (root / "chapters" / "chapter-001.md").write_text(
            "# 裂痕之夜\n\n"
            "林舟推开仓库的铁门，生锈的铰链发出刺耳的声响。@{沈昭} 站在阴影里，"
            "手里握着一份泛黄的文件。\n\n"
            "「你来了。」沈昭的声音平静得像一潭死水。\n\n"
            "林舟没有回答。他的目光落在那份文件上——那是三年前失踪案的卷宗，"
            "上面盖着绝密的红色印章。\n",
            encoding="utf-8",
        )
        (root / "chapters" / "chapter-002.md").write_text(
            "# 暗流涌动\n\n"
            "仓库里只剩林舟一人。沈昭消失得无影无踪，仿佛从未出现过。\n\n"
            "桌上留着一封密信，字迹潦草却笔锋锐利。\n",
            encoding="utf-8",
        )

        # ------------------------------------------------------------------
        # Step 4: Run chapter analyze for chapter-001
        # ------------------------------------------------------------------
        rc = main(["chapter", "analyze", "--root", r, "--chapter-id", "chapter-001"])
        self.assertEqual(rc, 0, "chapter analyze should succeed")

        # Analyze should have saved analysis log
        self.assertTrue(
            (root / "logs" / "analysis-chapter-001.yaml").exists(),
            "analysis log should be written",
        )

        # After analyze + save_state, the layered volume file should exist
        self.assertTrue(
            (root / "spec" / "outlines" / "vol-001.yaml").exists(),
            "Per-volume outline file should be created by save_state in layered layout",
        )

        # ------------------------------------------------------------------
        # Step 5: Run review chapter for chapter-001
        # ------------------------------------------------------------------
        rc = main(["review", "chapter", "--root", r, "--chapter-id", "chapter-001"])
        self.assertEqual(rc, 0, "review chapter should succeed")

        # ------------------------------------------------------------------
        # Step 6: Run doctor and verify 0 errors
        # ------------------------------------------------------------------
        rc = main(["doctor", "--root", r, "--min-chapter-words", "1", "--target-chapter-words", "10"])
        self.assertEqual(rc, 0, "doctor should report 0 errors")

        # ------------------------------------------------------------------
        # Step 7: Export spec-outline, verify chapter titles present
        # ------------------------------------------------------------------
        outline_export_path = root / "export-outline.md"
        rc = main([
            "export", "--root", r,
            "--format", "spec-outline",
            "--output", str(outline_export_path),
        ])
        self.assertEqual(rc, 0, "export spec-outline should succeed")
        self.assertTrue(outline_export_path.exists(), "export file should be created")
        content = outline_export_path.read_text(encoding="utf-8")
        self.assertIn("裂痕之夜", content, "spec-outline should contain chapter-001 title")
        self.assertIn("暗流涌动", content, "spec-outline should contain chapter-002 title")

        # ------------------------------------------------------------------
        # Step 8: Export spec-characters, verify no crash (empty entities ok)
        # ------------------------------------------------------------------
        chars_export_path = root / "export-characters.md"
        rc = main([
            "export", "--root", r,
            "--format", "spec-characters",
            "--output", str(chars_export_path),
        ])
        self.assertEqual(rc, 0, "export spec-characters should succeed")
        self.assertTrue(chars_export_path.exists(), "characters export file should be created")
        chars_content = chars_export_path.read_text(encoding="utf-8")
        # Empty entities => "暂无角色数据" or similar placeholder
        self.assertTrue(len(chars_content) > 0, "spec-characters output should not be empty")

        # ------------------------------------------------------------------
        # Step 9: Plant a foreshadow
        # ------------------------------------------------------------------
        rc = main([
            "foreshadow", "plant",
            "--root", r,
            "--description", "密信上的暗纹与三年前的卷宗印章吻合",
            "--chapter-id", "chapter-001",
            "--planned-payoff", "chapter-005",
        ])
        self.assertEqual(rc, 0, "foreshadow plant should succeed")

        # ------------------------------------------------------------------
        # Step 10: Verify all file locations
        # ------------------------------------------------------------------
        # spec/ directory files
        self.assertTrue(
            (root / "spec" / "outline.yaml").exists(),
            "spec/outline.yaml must exist (not root/outline.yaml)",
        )
        self.assertFalse(
            (root / "outline.yaml").exists(),
            "root/outline.yaml must NOT exist in layered layout",
        )
        self.assertTrue(
            (root / "spec" / "entities.yaml").exists(),
            "spec/entities.yaml must exist",
        )
        self.assertTrue(
            (root / "spec" / "foreshadowing.yaml").exists(),
            "spec/foreshadowing.yaml must exist",
        )
        self.assertTrue(
            (root / "spec" / "outlines").is_dir(),
            "spec/outlines/ directory must exist",
        )

        # Root-level files
        self.assertTrue(
            (root / "project.yaml").exists(),
            "project.yaml must be at root",
        )
        self.assertTrue(
            (root / "branches.yaml").exists(),
            "branches.yaml must be at root",
        )

        # Root-level directories
        self.assertTrue((root / "chapters").is_dir(), "chapters/ at root")
        self.assertTrue((root / "proposals").is_dir(), "proposals/ at root")
        self.assertTrue((root / "reviews").is_dir(), "reviews/ at root")
        self.assertTrue((root / "projections").is_dir(), "projections/ at root")
        self.assertTrue((root / "logs").is_dir(), "logs/ at root")

        # Verify chapter files are under root chapters/
        self.assertTrue((root / "chapters" / "chapter-001.md").exists())
        self.assertTrue((root / "chapters" / "chapter-002.md").exists())

        # Additional layered-specific: spec/timeline.yaml, spec/threads.yaml, spec/structures.yaml
        for spec_file in ("timeline.yaml", "threads.yaml", "structures.yaml"):
            self.assertTrue(
                (root / "spec" / spec_file).exists(),
                f"spec/{spec_file} must exist in layered layout",
            )
            self.assertFalse(
                (root / spec_file).exists(),
                f"{spec_file} must NOT exist at root in layered layout",
            )


if __name__ == "__main__":
    unittest.main()

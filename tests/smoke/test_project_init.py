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


class ProjectInitSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-init-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_writes_positioning_and_story_contract(self) -> None:
        buffer = StringIO()
        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "init",
                    "--root",
                    str(self.temp_dir),
                    "--title",
                    "雾港疑案",
                    "--genre",
                    "奇幻",
                    "--primary-genre",
                    "fantasy",
                    "--sub-genre",
                    "xuanhuan",
                    "--style-tag",
                    "light-novel",
                    "--style-tag",
                    "web-serial",
                    "--target-audience",
                    "male-young-adult",
                    "--target-audience",
                    "web-serial-reader",
                    "--core-promise",
                    "升级成长明确",
                    "--core-promise",
                    "每三章至少一个兑现点",
                    "--avoidance",
                    "长时间无主线推进",
                    "--ending-contract",
                    "阶段性胜利+保留更大危机",
                    "--pace-contract",
                    "快节奏",
                    "--premise",
                    "底层少年从宗门弃子一路升级到界域执掌者",
                    "--hook-line",
                    "废柴少爷觉醒残卷传承，每三章一跃迁，步步掀翻旧秩序。",
                    "--hook-stack",
                    "upgrade-payoff",
                    "--hook-stack",
                    "cliffhanger-end",
                    "--benchmark-work",
                    "升级流玄幻长篇",
                    "--benchmark-work",
                    "宗门竞争成长文",
                    "--target-platform",
                    "qidian",
                    "--serialization-model",
                    "强升级主线 + 阶段性地图扩张 + 卷末晋阶兑现",
                    "--release-cadence",
                    "日更两章",
                    "--chapter-word-floor",
                    "2000",
                    "--chapter-word-target",
                    "3000",
                ]
            )
        payload = json.loads(buffer.getvalue())
        project = json.loads((self.temp_dir / "project.yaml").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(project["genre"], "奇幻")
        self.assertEqual(project["positioning"]["primaryGenre"], "fantasy")
        self.assertEqual(project["positioning"]["subGenre"], "xuanhuan")
        self.assertEqual(project["positioning"]["styleTags"], ["light-novel", "web-serial"])
        self.assertEqual(project["positioning"]["targetAudience"], ["male-young-adult", "web-serial-reader"])
        self.assertEqual(project["storyContract"]["corePromises"], ["升级成长明确", "每三章至少一个兑现点"])
        self.assertEqual(project["storyContract"]["avoidances"], ["长时间无主线推进"])
        self.assertEqual(project["storyContract"]["endingContract"], "阶段性胜利+保留更大危机")
        self.assertEqual(project["storyContract"]["paceContract"], "快节奏")
        self.assertEqual(project["commercialPositioning"]["premise"], "底层少年从宗门弃子一路升级到界域执掌者")
        self.assertEqual(project["commercialPositioning"]["hookLine"], "废柴少爷觉醒残卷传承，每三章一跃迁，步步掀翻旧秩序。")
        self.assertEqual(project["commercialPositioning"]["hookStack"], ["upgrade-payoff", "cliffhanger-end"])
        self.assertEqual(project["commercialPositioning"]["benchmarkWorks"], ["升级流玄幻长篇", "宗门竞争成长文"])
        self.assertEqual(project["commercialPositioning"]["targetPlatform"], "qidian")
        self.assertEqual(project["commercialPositioning"]["serializationModel"], "强升级主线 + 阶段性地图扩张 + 卷末晋阶兑现")
        self.assertEqual(project["commercialPositioning"]["releaseCadence"], "日更两章")
        self.assertEqual(project["commercialPositioning"]["chapterWordFloor"], 2000)
        self.assertEqual(project["commercialPositioning"]["chapterWordTarget"], 3000)
        self.assertEqual(payload["positioning"]["primaryGenre"], "fantasy")
        self.assertEqual(payload["commercialPositioning"]["targetPlatform"], "qidian")

    def test_init_defaults_primary_genre_to_genre_when_not_provided(self) -> None:
        with redirect_stdout(StringIO()):
            exit_code = main(
                [
                    "init",
                    "--root",
                    str(self.temp_dir),
                    "--title",
                    "Fog Harbor",
                    "--genre",
                    "Mystery",
                ]
            )
        project = json.loads((self.temp_dir / "project.yaml").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(project["positioning"]["primaryGenre"], "mystery")
        self.assertEqual(project["positioning"]["subGenre"], "")
        self.assertEqual(project["positioning"]["styleTags"], [])
        self.assertEqual(project["storyContract"]["corePromises"], [])
        self.assertEqual(project["commercialPositioning"]["hookStack"], [])
        self.assertEqual(project["commercialPositioning"]["chapterWordTarget"], 0)

    def test_init_normalizes_subgenre_and_style_tags(self) -> None:
        with redirect_stdout(StringIO()):
            exit_code = main(
                [
                    "init",
                    "--root",
                    str(self.temp_dir),
                    "--title",
                    "雾港疑案",
                    "--genre",
                    "奇幻",
                    "--sub-genre",
                    "西幻",
                    "--style-tag",
                    "Light Novel",
                ]
            )
        project = json.loads((self.temp_dir / "project.yaml").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(project["positioning"]["subGenre"], "western-fantasy")
        self.assertEqual(project["positioning"]["styleTags"], ["light-novel"])


if __name__ == "__main__":
    unittest.main()

# Creative Tools & Consistency Check Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add brainstorm/inspiration tools, character cards with enrichment, three-level outlines, and automated consistency checking to story-harness-cli.

**Architecture:** Extend existing CLI pattern (register commands → command handler → service function → state load/save). All new features follow the same JSON-compatible YAML + state dict approach. CLI outputs structured context, no AI API calls inside.

**Tech Stack:** Python 3.10+, stdlib only (json, re, hashlib, random, pathlib). No new dependencies.

---

## Task 1: Extend schema.py — entities profile + outline volumes

**Files:**
- Modify: `src/story_harness_cli/protocol/schema.py`

**Step 1: Write the failing test**

Create `tests/smoke/test_schema.py`:

```python
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
    def test_entities_has_profile_and_seed_fields(self):
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/smoke/test_schema.py -v`
Expected: FAIL — `enrichmentProposals` and `volumes` not in defaults

**Step 3: Write minimal implementation**

Replace `src/story_harness_cli/protocol/schema.py` body:

```python
from __future__ import annotations

from typing import Any, Dict


def default_project_state() -> Dict[str, Dict[str, Any]]:
    return {
        "project": {},
        "outline": {
            "volumes": [],
            "chapters": [],
            "chapterDirections": [],
        },
        "entities": {
            "entities": [],
            "enrichmentProposals": [],
        },
        "timeline": {"events": []},
        "branches": {"branches": []},
        "proposals": {"draftProposals": []},
        "reviews": {"changeRequests": []},
        "projection": {
            "snapshotProjections": [],
            "relationProjections": [],
            "sceneScopeProjections": [],
            "timelineProjections": [],
            "causalityProjections": [],
        },
        "context_lens": {"currentChapterId": None, "lenses": []},
        "projection_log": {"projectionChanges": []},
    }
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/smoke/test_schema.py -v`
Expected: PASS

**Step 5: Run existing tests to verify no regression**

Run: `python -m pytest tests/ -v`
Expected: All existing tests PASS

**Step 6: Commit**

```bash
git add src/story_harness_cli/protocol/schema.py tests/smoke/test_schema.py
git commit -m "feat(schema): add enrichmentProposals and volumes to default state"
```

---

## Task 2: Create data files — inspiration word tables

**Files:**
- Create: `src/story_harness_cli/data/__init__.py`
- Create: `src/story_harness_cli/data/archetypes.yaml`
- Create: `src/story_harness_cli/data/motivations.yaml`
- Create: `src/story_harness_cli/data/personalities.yaml`
- Create: `src/story_harness_cli/data/conflicts.yaml`
- Create: `src/story_harness_cli/data/world_elements.yaml`
- Create: `src/story_harness_cli/data/names_cn.yaml`

**Step 1: Write data files**

`src/story_harness_cli/data/__init__.py`:
```python
```

`src/story_harness_cli/data/archetypes.yaml`:
```json
{
  "archetypes": [
    {"id": "fallen-detective", "label": "落魄侦探", "traits": ["敏锐", "固执", "孤独"]},
    {"id": "genius-girl", "label": "天才少女", "traits": ["聪慧", "叛逆", "脆弱"]},
    {"id": "hidden-master", "label": "隐世高人", "traits": ["淡泊", "深藏不露", "古怪"]},
    {"id": "fallen-noble", "label": "落魄贵族", "traits": ["高傲", "优雅", "不甘"]},
    {"id": "avenger", "label": "复仇者", "traits": ["坚定", "冷酷", "内心挣扎"]},
    {"id": "wanderer", "label": "流浪者", "traits": ["自由", "洒脱", "逃避"]},
    {"id": "scholar", "label": "书生学者", "traits": ["博学", "谨慎", "理想主义"]},
    {"id": "merchant", "label": "精明商人", "traits": ["圆滑", "务实", "重情义"]},
    {"id": "rebel-leader", "label": "反抗军领袖", "traits": ["果决", "魅力", "偏执"]},
    {"id": "double-agent", "label": "双重间谍", "traits": ["冷静", "多疑", "矛盾"]},
    {"id": "healer", "label": "医者", "traits": ["慈悲", "坚韧", "隐忍"]},
    {"id": "warrior", "label": "武者", "traits": ["刚直", "重诺", "不善言辞"]}
  ]
}
```

`src/story_harness_cli/data/motivations.yaml`:
```json
{
  "motivations": [
    {"id": "revenge", "label": "复仇", "description": "为某事或某人复仇"},
    {"id": "truth", "label": "追查真相", "description": "揭开隐藏的真相"},
    {"id": "redemption", "label": "救赎", "description": "弥补过去的错误"},
    {"id": "treasure", "label": "寻宝", "description": "寻找珍贵的宝物或遗产"},
    {"id": "protection", "label": "守护", "description": "保护重要的人或事物"},
    {"id": "freedom", "label": "自由", "description": "摆脱束缚，追求自由"},
    {"id": "power", "label": "权力", "description": "获取或巩固权力地位"},
    {"id": "love", "label": "爱情", "description": "追寻或守护爱情"},
    {"id": "honor", "label": "荣誉", "description": "维护家族或个人荣誉"},
    {"id": "exploration", "label": "探索", "description": "探索未知的世界或知识"},
    {"id": "survival", "label": "生存", "description": "在极端环境中活下去"},
    {"id": "legacy", "label": "传承", "description": "传承或恢复某种遗产"}
  ]
}
```

`src/story_harness_cli/data/personalities.yaml`:
```json
{
  "dimensions": [
    {"axis": "社交", "low": "内向沉默", "high": "外向健谈"},
    {"axis": "处事", "low": "冲动鲁莽", "high": "沉稳理性"},
    {"axis": "信任", "low": "多疑戒备", "high": "坦诚信任"},
    {"axis": "道德", "low": "务实功利", "high": "理想主义"},
    {"axis": "压力", "low": "脆弱敏感", "high": "坚韧刚毅"},
    {"axis": "表达", "low": "内敛含蓄", "high": "直率奔放"}
  ],
  "traits": [
    "冷静", "固执", "温柔", "暴烈", "沉默寡言", "口若悬河",
    "多疑", "信任", "骄傲", "谦逊", "狡猾", "单纯",
    "勇敢", "怯懦", "乐观", "悲观", "细心", "粗心",
    "忠诚", "背叛", "幽默", "严肃", "善良", "冷酷"
  ]
}
```

`src/story_harness_cli/data/conflicts.yaml`:
```json
{
  "conflictTypes": [
    {"id": "ideology", "label": "立场对立", "description": "因信念或立场不同产生的对立"},
    {"id": "interest", "label": "利益冲突", "description": "资源、权力或利益争夺"},
    {"id": "misunderstanding", "label": "误解", "description": "因信息不对称造成的矛盾"},
    {"id": "betrayal", "label": "背叛", "description": "一方背叛另一方的信任"},
    {"id": "rivalry", "label": "竞争", "description": "同一目标下的竞争关系"},
    {"id": "duty-vs-desire", "label": "职责与欲望", "description": "责任与个人愿望的抉择"},
    {"id": "past-vs-present", "label": "过去与现在", "description": "历史包袱与现实需求的冲突"},
    {"id": "individual-vs-group", "label": "个人与集体", "description": "个人利益与群体利益的矛盾"}
  ]
}
```

`src/story_harness_cli/data/world_elements.yaml`:
```json
{
  "eras": [
    {"id": "ancient", "label": "古代", "subLabels": ["春秋战国", "秦汉", "唐宋", "明清"]},
    {"id": "modern", "label": "现代", "subLabels": ["都市", "校园", "职场"]},
    {"id": "future", "label": "未来", "subLabels": ["赛博朋克", "太空歌剧", "废土"]},
    {"id": "fantasy", "label": "奇幻", "subLabels": ["东方玄幻", "西方魔幻", "仙侠"]},
    {"id": "alternate", "label": "架空", "subLabels": ["架空历史", "架空民国", "架空帝国"]}
  ],
  "locations": [
    "繁华都城", "偏远山村", "海上孤岛", "地下迷宫", "废弃工厂",
    "古堡庄园", "边境要塞", "神秘森林", "沙漠绿洲", "雪山之巅"
  ],
  "powerSystems": [
    {"id": "martial", "label": "武学", "description": "以武力为核心的力量体系"},
    {"id": "magic", "label": "魔法", "description": "以魔力为核心的力量体系"},
    {"id": "tech", "label": "科技", "description": "以科技装备为核心的力量体系"},
    {"id": "psi", "label": "异能", "description": "以精神力/超能力为核心"},
    {"id": "social", "label": "权谋", "description": "以社会地位和人际关系为力量"},
    {"id": "none", "label": "无特殊体系", "description": "现实主义，无超自然力量"}
  ]
}
```

`src/story_harness_cli/data/names_cn.yaml`:
```json
{
  "surnames": [
    "林", "沈", "陈", "李", "张", "王", "赵", "周", "吴", "郑",
    "孙", "钱", "冯", "褚", "卫", "蒋", "韩", "杨", "朱", "秦",
    "许", "何", "吕", "施", "孔", "曹", "严", "华", "金", "魏"
  ],
  "givenNamesMale": [
    "舟", "昊", "辰", "毅", "霖", "轩", "泽", "渊", "铭", "然",
    "峰", "远", "恒", "澈", "铮", "鹤", "澜", "燧", "骁", "墨"
  ],
  "givenNamesFemale": [
    "昭", "月", "瑶", "薇", "琳", "霜", "芸", "悦", "清", "烟",
    "璃", "念", "影", "漪", "绫", "锦", "珂", "苒", "楠", "素"
  ]
}
```

**Step 2: Verify files load correctly**

Create `tests/smoke/test_data_files.py`:

```python
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


class DataFilesTest(unittest.TestCase):
    DATA_DIR = SRC_ROOT / "story_harness_cli" / "data"

    def _load(self, name):
        text = (self.DATA_DIR / name).read_text(encoding="utf-8")
        return json.loads(text)

    def test_archetypes_loadable(self):
        data = self._load("archetypes.yaml")
        self.assertIn("archetypes", data)
        self.assertTrue(len(data["archetypes"]) >= 10)

    def test_motivations_loadable(self):
        data = self._load("motivations.yaml")
        self.assertIn("motivations", data)

    def test_personalities_loadable(self):
        data = self._load("personalities.yaml")
        self.assertIn("dimensions", data)
        self.assertIn("traits", data)

    def test_conflicts_loadable(self):
        data = self._load("conflicts.yaml")
        self.assertIn("conflictTypes", data)

    def test_world_elements_loadable(self):
        data = self._load("world_elements.yaml")
        self.assertIn("eras", data)
        self.assertIn("locations", data)

    def test_names_cn_loadable(self):
        data = self._load("names_cn.yaml")
        self.assertIn("surnames", data)
        self.assertIn("givenNamesMale", data)
        self.assertIn("givenNamesFemale", data)


if __name__ == "__main__":
    unittest.main()
```

**Step 3: Run tests**

Run: `python -m pytest tests/smoke/test_data_files.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/story_harness_cli/data/ tests/smoke/test_data_files.py
git commit -m "feat(data): add inspiration word tables for brainstorm"
```

---

## Task 3: Create inspiration service

**Files:**
- Create: `src/story_harness_cli/services/inspiration.py`

**Step 1: Write the failing test**

Create `tests/smoke/test_inspiration.py`:

```python
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from story_harness_cli.services.inspiration import (
    generate_character_suggestions,
    generate_name,
    generate_world_suggestions,
    generate_outline_skeleton,
)


class InspirationTest(unittest.TestCase):
    def test_generate_name_returns_string(self):
        name = generate_name()
        self.assertIsInstance(name, str)
        self.assertTrue(len(name) >= 2)

    def test_generate_character_suggestions_returns_list(self):
        results = generate_character_suggestions(count=3)
        self.assertEqual(len(results), 3)
        for item in results:
            self.assertIn("archetype", item)
            self.assertIn("personality", item)
            self.assertIn("motivation", item)

    def test_generate_world_suggestions_returns_list(self):
        results = generate_world_suggestions(count=2)
        self.assertEqual(len(results), 2)
        for item in results:
            self.assertIn("era", item)
            self.assertIn("location", item)

    def test_generate_outline_skeleton(self):
        volumes = [
            {"title": "第一卷", "chapterCount": 3},
            {"title": "第二卷", "chapterCount": 2},
        ]
        result = generate_outline_skeleton(volumes)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]["chapters"]), 3)
        self.assertEqual(len(result[1]["chapters"]), 2)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/smoke/test_inspiration.py -v`
Expected: FAIL — module not found

**Step 3: Write implementation**

Create `src/story_harness_cli/services/inspiration.py`:

```python
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_table(name: str) -> Dict[str, Any]:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def generate_name(gender: str | None = None) -> str:
    names = _load_table("names_cn.yaml")
    surname = random.choice(names["surnames"])
    if gender == "female":
        given = random.choice(names["givenNamesFemale"])
    elif gender == "male":
        given = random.choice(names["givenNamesMale"])
    else:
        given = random.choice(names["givenNamesMale"] + names["givenNamesFemale"])
    return surname + given


def generate_character_suggestions(count: int = 3) -> List[Dict[str, Any]]:
    archetypes = _load_table("archetypes.yaml")["archetypes"]
    motivations = _load_table("motivations.yaml")["motivations"]
    personalities = _load_table("personalities.yaml")
    conflicts = _load_table("conflicts.yaml")["conflictTypes"]

    results = []
    for _ in range(count):
        archetype = random.choice(archetypes)
        motivation = random.choice(motivations)
        trait_count = random.randint(2, 4)
        traits = random.sample(personalities["traits"], min(trait_count, len(personalities["traits"])))
        conflict = random.choice(conflicts)
        gender = random.choice(["male", "female"])
        results.append({
            "name": generate_name(gender),
            "gender": gender,
            "archetype": archetype["label"],
            "archetypeId": archetype["id"],
            "personality": traits,
            "motivation": motivation["label"],
            "motivationId": motivation["id"],
            "potentialConflict": conflict["label"],
        })
    return results


def generate_world_suggestions(count: int = 3) -> List[Dict[str, Any]]:
    world = _load_table("world_elements.yaml")

    results = []
    for _ in range(count):
        era = random.choice(world["eras"])
        sub = random.choice(era["subLabels"]) if era["subLabels"] else era["label"]
        location = random.choice(world["locations"])
        power = random.choice(world["powerSystems"])
        results.append({
            "era": era["label"],
            "subEra": sub,
            "location": location,
            "powerSystem": power["label"],
            "powerSystemId": power["id"],
        })
    return results


def generate_outline_skeleton(
    volumes: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    result = []
    for vol in volumes:
        chapters = []
        chapter_count = vol.get("chapterCount", 3)
        for i in range(1, chapter_count + 1):
            chapters.append({
                "id": f"chapter-{len(result)+1:03d}-{i:03d}",
                "title": f"{vol['title']} 第{i}章",
                "status": "planned",
                "direction": "",
                "beats": [],
            })
        result.append({
            "id": f"vol-{len(result)+1:03d}",
            "title": vol.get("title", "未命名卷"),
            "theme": vol.get("theme", ""),
            "chapters": chapters,
        })
    return result
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/smoke/test_inspiration.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/story_harness_cli/services/inspiration.py tests/smoke/test_inspiration.py
git commit -m "feat(inspiration): add random character/world/outline generator"
```

---

## Task 4: Create brainstorm command

**Files:**
- Create: `src/story_harness_cli/commands/brainstorm.py`
- Modify: `src/story_harness_cli/commands/__init__.py`
- Modify: `src/story_harness_cli/cli.py`

**Step 1: Write the failing test**

Create `tests/smoke/test_brainstorm.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/smoke/test_brainstorm.py -v`
Expected: FAIL — `brainstorm` subcommand not registered

**Step 3: Write implementation**

Create `src/story_harness_cli/commands/brainstorm.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.services.inspiration import (
    generate_character_suggestions,
    generate_outline_skeleton,
    generate_world_suggestions,
)
from story_harness_cli.utils import now_iso


def command_brainstorm_character(args) -> int:
    count = args.count or 3
    suggestions = generate_character_suggestions(count=count)
    print(json.dumps({"suggestions": suggestions}, ensure_ascii=False, indent=2))
    return 0


def command_brainstorm_world(args) -> int:
    count = args.count or 3
    suggestions = generate_world_suggestions(count=count)
    print(json.dumps({"suggestions": suggestions}, ensure_ascii=False, indent=2))
    return 0


def command_brainstorm_outline(args) -> int:
    root = Path(args.root).resolve()
    volumes_input = []
    vol_count = args.volumes or 1
    chap_per_vol = args.chapters_per_volume or 5
    for i in range(1, vol_count + 1):
        volumes_input.append({
            "title": f"第{i}卷",
            "chapterCount": chap_per_vol,
        })
    skeleton = generate_outline_skeleton(volumes_input)

    if args.root:
        outline_path = root / "outline.yaml"
        if outline_path.exists():
            outline = json.loads(outline_path.read_text(encoding="utf-8"))
        else:
            outline = {"volumes": [], "chapters": [], "chapterDirections": []}
        outline["volumes"] = skeleton
        outline_path.parent.mkdir(parents=True, exist_ok=True)
        outline_path.write_text(json.dumps(outline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"volumes": skeleton}, ensure_ascii=False, indent=2))
    return 0


def register_brainstorm_commands(subparsers) -> None:
    brainstorm_parser = subparsers.add_parser("brainstorm", help="Brainstorm creative elements")
    bs_sub = brainstorm_parser.add_subparsers(dest="brainstorm_command", required=True)

    char_parser = bs_sub.add_parser("character", help="Generate character suggestions")
    char_parser.add_argument("--random", action="store_true", help="Random generation mode")
    char_parser.add_argument("--count", type=int, default=3)
    char_parser.set_defaults(func=command_brainstorm_character)

    world_parser = bs_sub.add_parser("world", help="Generate world element suggestions")
    world_parser.add_argument("--random", action="store_true", help="Random generation mode")
    world_parser.add_argument("--count", type=int, default=3)
    world_parser.set_defaults(func=command_brainstorm_world)

    outline_parser = bs_sub.add_parser("outline", help="Generate outline skeleton")
    outline_parser.add_argument("--root", required=False)
    outline_parser.add_argument("--volumes", type=int, default=1)
    outline_parser.add_argument("--chapters-per-volume", type=int, default=5)
    outline_parser.set_defaults(func=command_brainstorm_outline)
```

Modify `src/story_harness_cli/commands/__init__.py` — add import:

```python
from .brainstorm import register_brainstorm_commands
```

Add to `__all__`:
```python
    "register_brainstorm_commands",
```

Modify `src/story_harness_cli/cli.py` — add import and registration:

In imports add:
```python
from story_harness_cli.commands import (
    register_brainstorm_commands,
    register_chapter_commands,
    ...
```

In `build_parser()` add after existing registrations:
```python
    register_brainstorm_commands(subparsers)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/smoke/test_brainstorm.py -v`
Expected: PASS

**Step 5: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All PASS

**Step 6: Commit**

```bash
git add src/story_harness_cli/commands/brainstorm.py src/story_harness_cli/commands/__init__.py src/story_harness_cli/cli.py tests/smoke/test_brainstorm.py
git commit -m "feat(brainstorm): add character/world/outline brainstorm commands"
```

---

## Task 5: Extend text.py — appearance and ability keywords

**Files:**
- Modify: `src/story_harness_cli/utils/text.py`

**Step 1: Write the failing test**

Create `tests/smoke/test_text_extended.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/smoke/test_text_extended.py -v`
Expected: FAIL — functions not defined

**Step 3: Write implementation**

Append to `src/story_harness_cli/utils/text.py`:

```python
APPEARANCE_KEYWORDS = {
    "长发": "长发",
    "短发": "短发",
    "光头": "光头",
    "马尾": "马尾",
    "白发": "白发",
    "黑发": "黑发",
    "金发": "金发",
    "红发": "红发",
    "灰发": "灰发",
    "银发": "银发",
    "蓝眼睛": "蓝眼睛",
    "琥珀色": "琥珀色眼睛",
    "琥珀色眼睛": "琥珀色眼睛",
    "黑眼睛": "黑眼睛",
    "绿眼睛": "绿眼睛",
    "高个子": "高个子",
    "矮个子": "矮个子",
    "瘦削": "瘦削",
    "魁梧": "魁梧",
    "疤痕": "有疤痕",
    "伤疤": "有疤痕",
    "纹身": "有纹身",
    "胎记": "有胎记",
    "戴眼镜": "戴眼镜",
    "胡子": "有胡子",
    "胡须": "有胡子",
    "络腮胡": "络腮胡",
    "独眼": "独眼",
    "拐杖": "拄拐杖",
    "轮椅": "坐轮椅",
}

ABILITY_KEYWORDS = {
    "格斗": "格斗",
    "拳击": "格斗",
    "刀法": "刀术",
    "剑术": "剑术",
    "枪法": "枪法",
    "射击": "射击",
    "暗器": "暗器",
    "轻功": "轻功",
    "身法": "身法",
    "内力": "内力",
    "法术": "法术",
    "魔法": "魔法",
    "咒语": "咒语",
    "医术": "医术",
    "毒术": "毒术",
    "易容": "易容",
    "潜行": "潜行",
    "破解": "破解",
    "黑客": "黑客",
    "驾驶": "驾驶",
    "骑术": "骑术",
    "游泳": "游泳",
    "追踪": "追踪",
    "推理": "推理",
    "分析": "分析",
    "领导": "领导",
    "口才": "口才",
    "谈判": "谈判",
}


def appearance_tags_for_paragraph(paragraph: str) -> List[str]:
    return [label for keyword, label in APPEARANCE_KEYWORDS.items() if keyword in paragraph]


def ability_tags_for_paragraph(paragraph: str) -> List[str]:
    return [label for keyword, label in ABILITY_KEYWORDS.items() if keyword in paragraph]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/smoke/test_text_extended.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/story_harness_cli/utils/text.py tests/smoke/test_text_extended.py
git commit -m "feat(text): add appearance and ability keyword detection"
```

---

## Task 6: Create entity enricher service

**Files:**
- Create: `src/story_harness_cli/services/entity_enricher.py`

**Step 1: Write the failing test**

Create `tests/smoke/test_entity_enricher.py`:

```python
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

    def test_enrich_produces_proposals(self):
        state = load_project_state(self.temp_dir)
        result = enrich_entities(state, "chapter-001")
        self.assertGreater(result["created"], 0)
        proposals = state["entities"].get("enrichmentProposals", [])
        self.assertTrue(len(proposals) > 0)
        proposal = proposals[0]
        self.assertIn("entityId", proposal)
        self.assertIn("field", proposal)
        self.assertEqual(proposal["status"], "pending")


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/smoke/test_entity_enricher.py -v`
Expected: FAIL — module not found

**Step 3: Write implementation**

Create `src/story_harness_cli/services/entity_enricher.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from story_harness_cli.protocol.files import chapter_path
from story_harness_cli.utils import now_iso, stable_hash
from story_harness_cli.utils.text import (
    ability_tags_for_paragraph,
    appearance_tags_for_paragraph,
    paragraphs_from_text,
)


def enrich_entities(
    state: Dict[str, Dict[str, Any]],
    chapter_id: str,
) -> Dict[str, Any]:
    root_hint = state.get("_root")
    if root_hint:
        root = Path(root_hint)
    else:
        return {"created": 0, "error": "no root path"}

    chapter_file = chapter_path(root, chapter_id)
    if not chapter_file.exists():
        return {"created": 0, "error": f"chapter not found: {chapter_id}"}

    text = chapter_file.read_text(encoding="utf-8")
    paragraphs = paragraphs_from_text(text)
    entities_list = state["entities"].get("entities", [])
    existing_proposals = state["entities"].setdefault("enrichmentProposals", [])
    existing_fingerprints = {p.get("fingerprint") for p in existing_proposals}

    name_to_entity = {}
    for entity in entities_list:
        name_to_entity[entity["name"]] = entity
        for alias in entity.get("aliases", []):
            name_to_entity[alias] = entity

    created = 0
    for paragraph in paragraphs:
        appearance_tags = appearance_tags_for_paragraph(paragraph)
        ability_tags = ability_tags_for_paragraph(paragraph)

        matched_entities = []
        for name, entity in name_to_entity.items():
            if name in paragraph:
                matched_entities.append(entity)

        for entity in matched_entities:
            if appearance_tags:
                detail = "；".join(sorted(set(appearance_tags)))
                fp = f"enrich::appearance::{entity['id']}::{detail}"
                if fp not in existing_fingerprints:
                    existing_proposals.append({
                        "id": f"enrich-{stable_hash(fp + now_iso())}",
                        "entityId": entity["id"],
                        "entityName": entity["name"],
                        "chapterId": chapter_id,
                        "field": "appearance",
                        "detail": detail,
                        "evidence": paragraph,
                        "confidence": 0.85,
                        "status": "pending",
                        "fingerprint": fp,
                        "createdAt": now_iso(),
                    })
                    existing_fingerprints.add(fp)
                    created += 1

            if ability_tags:
                detail = "；".join(sorted(set(ability_tags)))
                fp = f"enrich::ability::{entity['id']}::{detail}"
                if fp not in existing_fingerprints:
                    existing_proposals.append({
                        "id": f"enrich-{stable_hash(fp + now_iso())}",
                        "entityId": entity["id"],
                        "entityName": entity["name"],
                        "chapterId": chapter_id,
                        "field": "abilities",
                        "detail": detail,
                        "evidence": paragraph,
                        "confidence": 0.80,
                        "status": "pending",
                        "fingerprint": fp,
                        "createdAt": now_iso(),
                    })
                    existing_fingerprints.add(fp)
                    created += 1

    return {"created": created, "chapterId": chapter_id}
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/smoke/test_entity_enricher.py -v`

Note: The test passes `state` without `_root`. We need to either pass root explicitly or adjust. Let me revise — the enricher should take `root: Path` as a parameter like the analyzer does.

**Revised implementation** — add `root` parameter:

```python
def enrich_entities(
    state: Dict[str, Dict[str, Any]],
    chapter_id: str,
    root: Path | None = None,
) -> Dict[str, Any]:
    if not root:
        return {"created": 0, "error": "no root path"}

    chapter_file = chapter_path(root, chapter_id)
    if not chapter_file.exists():
        return {"created": 0, "error": f"chapter not found: {chapter_id}"}

    text = chapter_file.read_text(encoding="utf-8")
    paragraphs = paragraphs_from_text(text)
    entities_list = state["entities"].get("entities", [])
    existing_proposals = state["entities"].setdefault("enrichmentProposals", [])
    existing_fingerprints = {p.get("fingerprint") for p in existing_proposals}

    name_to_entity = {}
    for entity in entities_list:
        name_to_entity[entity["name"]] = entity
        for alias in entity.get("aliases", []):
            name_to_entity[alias] = entity

    created = 0
    for paragraph in paragraphs:
        appearance_tags = appearance_tags_for_paragraph(paragraph)
        ability_tags = ability_tags_for_paragraph(paragraph)

        matched_entities = []
        for name, entity in name_to_entity.items():
            if name in paragraph:
                matched_entities.append(entity)

        for entity in matched_entities:
            if appearance_tags:
                detail = "；".join(sorted(set(appearance_tags)))
                fp = f"enrich::appearance::{entity['id']}::{detail}"
                if fp not in existing_fingerprints:
                    existing_proposals.append({
                        "id": f"enrich-{stable_hash(fp + now_iso())}",
                        "entityId": entity["id"],
                        "entityName": entity["name"],
                        "chapterId": chapter_id,
                        "field": "appearance",
                        "detail": detail,
                        "evidence": paragraph,
                        "confidence": 0.85,
                        "status": "pending",
                        "fingerprint": fp,
                        "createdAt": now_iso(),
                    })
                    existing_fingerprints.add(fp)
                    created += 1

            if ability_tags:
                detail = "；".join(sorted(set(ability_tags)))
                fp = f"enrich::ability::{entity['id']}::{detail}"
                if fp not in existing_fingerprints:
                    existing_proposals.append({
                        "id": f"enrich-{stable_hash(fp + now_iso())}",
                        "entityId": entity["id"],
                        "entityName": entity["name"],
                        "chapterId": chapter_id,
                        "field": "abilities",
                        "detail": detail,
                        "evidence": paragraph,
                        "confidence": 0.80,
                        "status": "pending",
                        "fingerprint": fp,
                        "createdAt": now_iso(),
                    })
                    existing_fingerprints.add(fp)
                    created += 1

    return {"created": created, "chapterId": chapter_id}
```

**Revised test** — pass root as Path:

Update the test to call `enrich_entities(state, "chapter-001", root=self.temp_dir)`.

**Step 5: Run tests**

Run: `python -m pytest tests/smoke/test_entity_enricher.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/story_harness_cli/services/entity_enricher.py tests/smoke/test_entity_enricher.py
git commit -m "feat(enricher): add entity enrichment service with appearance/ability detection"
```

---

## Task 7: Create entity command

**Files:**
- Create: `src/story_harness_cli/commands/entity.py`
- Modify: `src/story_harness_cli/commands/__init__.py`
- Modify: `src/story_harness_cli/cli.py`
- Modify: `src/story_harness_cli/services/__init__.py`

**Step 1: Write the failing test**

Create `tests/smoke/test_entity_command.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/smoke/test_entity_command.py -v`
Expected: FAIL — `entity` subcommand not registered

**Step 3: Write implementation**

Create `src/story_harness_cli/commands/entity.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.services.entity_enricher import enrich_entities
from story_harness_cli.utils import now_iso


def command_entity_enrich(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id or state["project"].get("activeChapterId")
    if not chapter_id:
        raise SystemExit("缺少 chapter id")
    result = enrich_entities(state, chapter_id, root=root)
    save_state(root, state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_entity_review(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    proposals = state["entities"].setdefault("enrichmentProposals", [])
    decision = args.decision
    changed = 0

    for proposal in proposals:
        if proposal.get("status") != "pending":
            continue
        if not args.all_pending and (not args.proposal_id or proposal.get("id") not in args.proposal_id):
            continue
        proposal["status"] = decision
        proposal["updatedAt"] = now_iso()
        changed += 1

        if decision == "accepted":
            entity_id = proposal.get("entityId")
            field = proposal.get("field")
            detail = proposal.get("detail", "")
            evidence = proposal.get("evidence", "")
            chapter_id = proposal.get("chapterId", "")

            for entity in state["entities"].get("entities", []):
                if entity.get("id") == entity_id:
                    profile = entity.setdefault("profile", {})
                    field_list = profile.setdefault(field, [])
                    entry = {"detail": detail, "source": chapter_id, "evidence": evidence, "confidence": proposal.get("confidence", 0.8)}
                    field_list.append(entry)
                    break

    save_state(root, state)
    print(json.dumps({"updated": changed, "decision": decision}, ensure_ascii=False, indent=2))
    return 0


def register_entity_commands(subparsers) -> None:
    entity_parser = subparsers.add_parser("entity", help="Entity and character card commands")
    entity_sub = entity_parser.add_subparsers(dest="entity_command", required=True)

    enrich_parser = entity_sub.add_parser("enrich", help="Extract character details from chapter")
    enrich_parser.add_argument("--root", required=True)
    enrich_parser.add_argument("--chapter-id")
    enrich_parser.set_defaults(func=command_entity_enrich)

    review_parser = entity_sub.add_parser("review", help="Review enrichment proposals")
    review_parser.add_argument("--root", required=True)
    review_parser.add_argument("--decision", required=True, choices=["accepted", "ignored"])
    review_parser.add_argument("--proposal-id", action="append")
    review_parser.add_argument("--all-pending", action="store_true")
    review_parser.set_defaults(func=command_entity_review)
```

Update `src/story_harness_cli/commands/__init__.py`:
```python
from .brainstorm import register_brainstorm_commands
from .entity import register_entity_commands
# ... existing imports
```

Add `"register_entity_commands"` to `__all__`.

Update `src/story_harness_cli/cli.py`:
```python
from story_harness_cli.commands import (
    register_brainstorm_commands,
    register_chapter_commands,
    register_context_commands,
    register_doctor_commands,
    register_entity_commands,
    ...
```

Add `register_entity_commands(subparsers)` in `build_parser()`.

Update `src/story_harness_cli/services/__init__.py`:
```python
from .entity_enricher import enrich_entities
```

Add `"enrich_entities"` to `__all__`.

**Step 4: Run tests**

Run: `python -m pytest tests/smoke/test_entity_command.py -v`
Expected: PASS

**Step 5: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All PASS

**Step 6: Commit**

```bash
git add src/story_harness_cli/commands/entity.py src/story_harness_cli/commands/__init__.py src/story_harness_cli/cli.py src/story_harness_cli/services/__init__.py tests/smoke/test_entity_command.py
git commit -m "feat(entity): add entity enrich and review commands"
```

---

## Task 8: Create consistency engine

**Files:**
- Create: `src/story_harness_cli/services/consistency_engine.py`

**Step 1: Write the failing test**

Create `tests/smoke/test_consistency_engine.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/smoke/test_consistency_engine.py -v`
Expected: FAIL — module not found

**Step 3: Write implementation**

Create `src/story_harness_cli/services/consistency_engine.py`:

```python
from __future__ import annotations

from typing import Any, Dict, List

from story_harness_cli.utils.text import paragraphs_from_text, relation_for_paragraph


# Keywords suggesting active behavior (contradicts deceased status)
ACTIVE_BEHAVIOR_KEYWORDS = [
    "走", "跑", "说", "笑", "站", "坐", "拿", "看", "握", "挥",
    "推", "拉", "跳", "爬", "骑", "开", "关", "打", "写", "抓",
    "点头", "摇头", "转身", "回头", "弯腰", "抬头", "低头",
    "拥抱", "亲吻", "微笑", "怒吼", "低声", "喊",
]

# Keywords suggesting intimate/close behavior (contradicts broken relations)
INTIMATE_KEYWORDS = [
    "亲密", "拥抱", "亲吻", "依偎", "牵手", "抚摸", "温柔",
    "信任", "默契", "配合", "并肩", "携手", "守护",
]


def check_consistency(
    state: Dict[str, Dict[str, Any]],
    chapter_text: str,
    chapter_id: str,
) -> Dict[str, Any]:
    hard: Dict[str, List] = {
        "stateContradictions": [],
        "relationContradictions": [],
        "timelineConflicts": [],
    }
    soft: Dict[str, List] = {
        "outlineDeviations": [],
    }

    _check_state_contradictions(state, chapter_text, chapter_id, hard["stateContradictions"])
    _check_relation_contradictions(state, chapter_text, chapter_id, hard["relationContradictions"])
    _check_outline_deviations(state, chapter_id, soft["outlineDeviations"])

    context_for_ai = _build_ai_context(state, chapter_text, chapter_id)

    return {
        "hardChecks": hard,
        "softChecks": soft,
        "contextForAI": context_for_ai,
    }


def _check_state_contradictions(
    state: Dict, chapter_text: str, chapter_id: str, results: List
) -> None:
    entities = state.get("entities", {}).get("entities", [])
    paragraphs = paragraphs_from_text(chapter_text)

    for entity in entities:
        current = entity.get("currentState", {})
        if current.get("status") != "deceased":
            continue
        name = entity.get("name", "")
        for para in paragraphs:
            if name not in para:
                continue
            has_active = any(kw in para for kw in ACTIVE_BEHAVIOR_KEYWORDS)
            if has_active:
                last_chapter = current.get("lastUpdatedChapter", "unknown")
                results.append({
                    "entity": entity.get("id"),
                    "entityName": name,
                    "issue": f"projection 标记为 deceased，但正文中 {name} 有活跃描写",
                    "evidence": [
                        f"projection: status=deceased (chapter-{last_chapter})",
                        f"chapter: {chapter_id} 段落: '{para[:80]}...'",
                    ],
                    "severity": "strict",
                })
                break


def _check_relation_contradictions(
    state: Dict, chapter_text: str, chapter_id: str, results: List
) -> None:
    relations = state.get("projection", {}).get("relationProjections", [])
    paragraphs = paragraphs_from_text(chapter_text)

    broken_labels = {"裂痕", "对立", "决裂"}
    for rel in relations:
        label = rel.get("label", "")
        if label not in broken_labels:
            continue
        from_name = rel.get("fromName", "")
        to_name = rel.get("toName", "")
        scope_ref = rel.get("scopeRef", "")

        for para in paragraphs:
            if from_name not in para or to_name not in para:
                continue
            has_intimate = any(kw in para for kw in INTIMATE_KEYWORDS)
            if has_intimate:
                results.append({
                    "from": rel.get("fromId"),
                    "fromName": from_name,
                    "to": rel.get("toId"),
                    "toName": to_name,
                    "issue": f"projection 标记关系为'{label}'(chapter-{scope_ref})，但正文表现亲密",
                    "previousLabel": label,
                    "currentEvidence": f"{chapter_id} 段落: '{para[:80]}...'",
                    "severity": "strict",
                })
                break


def _check_outline_deviations(
    state: Dict, chapter_id: str, results: List
) -> None:
    outline = state.get("outline", {})
    volumes = outline.get("volumes", [])

    for vol in volumes:
        for ch in vol.get("chapters", []):
            if ch.get("id") != chapter_id:
                continue
            if ch.get("status") != "completed":
                continue
            for beat in ch.get("beats", []):
                if beat.get("status") == "planned":
                    results.append({
                        "beatId": beat.get("id"),
                        "summary": beat.get("summary", ""),
                        "status": "planned",
                        "note": "细纲中规划的场景在正文中未出现，可能是故意跳过",
                        "severity": "advisory",
                    })


def _build_ai_context(
    state: Dict, chapter_text: str, chapter_id: str
) -> Dict[str, Any]:
    entities = state.get("entities", {}).get("entities", [])
    projection = state.get("projection", {})
    outline = state.get("outline", {})

    entity_cards = []
    for e in entities:
        entity_cards.append({
            "id": e.get("id"),
            "name": e.get("name"),
            "seed": e.get("seed", {}),
            "profile": e.get("profile", {}),
            "currentState": e.get("currentState", {}),
        })

    relevant_snapshots = [
        s for s in projection.get("snapshotProjections", [])
        if s.get("scopeRef") == chapter_id
    ]
    relevant_relations = [
        r for r in projection.get("relationProjections", [])
        if r.get("scopeRef") == chapter_id
    ]

    outline_expectation = ""
    for vol in outline.get("volumes", []):
        for ch in vol.get("chapters", []):
            if ch.get("id") == chapter_id:
                outline_expectation = ch.get("direction", "")
                break

    return {
        "entityCards": entity_cards,
        "relevantProjections": {
            "snapshots": relevant_snapshots,
            "relations": relevant_relations,
        },
        "chapterContent": chapter_text,
        "outlineExpectation": outline_expectation,
    }
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/smoke/test_consistency_engine.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/story_harness_cli/services/consistency_engine.py tests/smoke/test_consistency_engine.py
git commit -m "feat(consistency): add consistency engine with state/relation/outline checks"
```

---

## Task 9: Create consistency command

**Files:**
- Create: `src/story_harness_cli/commands/consistency.py`
- Modify: `src/story_harness_cli/commands/__init__.py`
- Modify: `src/story_harness_cli/cli.py`
- Modify: `src/story_harness_cli/services/__init__.py`
- Modify: `src/story_harness_cli/protocol/files.py`

**Step 1: Write the failing test**

Create `tests/smoke/test_consistency_command.py`:

```python
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


class ConsistencyCommandTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-consistency-"))
        fixture = REPO_ROOT / "tests" / "fixtures" / "minimal_project"
        shutil.copytree(fixture, self.temp_dir, dirs_exist_ok=True)
        for d in ["proposals", "reviews", "projections", "logs"]:
            (self.temp_dir / d).mkdir(exist_ok=True)
        for name, content in [
            ("entities.yaml", '{"entities":[],"enrichmentProposals":[]}'),
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

    def test_consistency_check_runs(self):
        result = main([
            "consistency", "check",
            "--root", str(self.temp_dir),
            "--chapter-id", "chapter-001",
        ])
        self.assertEqual(result, 0)
        check_file = self.temp_dir / "projections" / "consistency-check-chapter-001.yaml"
        self.assertTrue(check_file.exists())
        data = json.loads(check_file.read_text(encoding="utf-8"))
        self.assertIn("hardChecks", data)
        self.assertIn("softChecks", data)
        self.assertIn("contextForAI", data)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/smoke/test_consistency_command.py -v`
Expected: FAIL — `consistency` subcommand not registered

**Step 3: Write implementation**

Create `src/story_harness_cli/commands/consistency.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from story_harness_cli.protocol import ensure_project_root, load_project_state, save_state
from story_harness_cli.protocol.files import chapter_path
from story_harness_cli.protocol.io import dump_json_compatible_yaml
from story_harness_cli.services.consistency_engine import check_consistency
from story_harness_cli.utils import now_iso, stable_hash


def command_consistency_check(args) -> int:
    root = Path(args.root).resolve()
    ensure_project_root(root)
    state = load_project_state(root)
    chapter_id = args.chapter_id or state["project"].get("activeChapterId")
    if not chapter_id:
        raise SystemExit("缺少 chapter id")

    chapter_file = chapter_path(root, chapter_id)
    if not chapter_file.exists():
        raise SystemExit(f"章节不存在: {chapter_file}")

    chapter_text = chapter_file.read_text(encoding="utf-8")
    result = check_consistency(state, chapter_text, chapter_id)
    result["checkId"] = f"check-{chapter_id}-{stable_hash(now_iso())}"
    result["chapterId"] = chapter_id
    result["checkedAt"] = now_iso()

    check_path = root / "projections" / f"consistency-check-{chapter_id}.yaml"
    dump_json_compatible_yaml(check_path, result)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def register_consistency_commands(subparsers) -> None:
    consistency_parser = subparsers.add_parser("consistency", help="Consistency check commands")
    con_sub = consistency_parser.add_subparsers(dest="consistency_command", required=True)

    check_parser = con_sub.add_parser("check", help="Run consistency check on a chapter")
    check_parser.add_argument("--root", required=True)
    check_parser.add_argument("--chapter-id")
    check_parser.set_defaults(func=command_consistency_check)
```

Update `src/story_harness_cli/commands/__init__.py`:
```python
from .consistency import register_consistency_commands
```
Add `"register_consistency_commands"` to `__all__`.

Update `src/story_harness_cli/cli.py`:
```python
from story_harness_cli.commands import (
    register_brainstorm_commands,
    register_chapter_commands,
    register_consistency_commands,
    register_context_commands,
    ...
```
Add `register_consistency_commands(subparsers)` in `build_parser()`.

Update `src/story_harness_cli/services/__init__.py`:
```python
from .consistency_engine import check_consistency
```
Add `"check_consistency"` to `__all__`.

**Step 4: Run tests**

Run: `python -m pytest tests/smoke/test_consistency_command.py -v`
Expected: PASS

**Step 5: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All PASS

**Step 6: Commit**

```bash
git add src/story_harness_cli/commands/consistency.py src/story_harness_cli/commands/__init__.py src/story_harness_cli/cli.py src/story_harness_cli/services/__init__.py tests/smoke/test_consistency_command.py
git commit -m "feat(consistency): add consistency check command with context output"
```

---

## Task 10: Extend doctor — consistency checks

**Files:**
- Modify: `src/story_harness_cli/commands/doctor.py`

**Step 1: Read current doctor.py to understand structure**

Read the file, then add a new check function.

**Step 2: Add consistency validation to doctor**

Add after existing check functions in `doctor.py`:

```python
def _check_outline_volumes(root: Path, issues: list) -> None:
    """Validate outline.yaml has volumes structure."""
    outline_path = root / "outline.yaml"
    if not outline_path.exists():
        return
    outline = load_json_compatible_yaml(outline_path, {})
    volumes = outline.get("volumes")
    if volumes is None:
        issues.append({"level": "warn", "message": "outline.yaml 缺少 volumes 字段，建议运行 brainstorm outline 初始化"})
    else:
        for vol in volumes:
            for ch in vol.get("chapters", []):
                for beat in ch.get("beats", []):
                    if beat.get("status") == "planned" and ch.get("status") == "completed":
                        issues.append({
                            "level": "info",
                            "message": f"卷 '{vol.get('title')}' 章 '{ch.get('title')}' 的 beat '{beat.get('summary')}' 状态仍为 planned，但章节已标记 completed",
                        })


def _check_entity_profiles(root: Path, issues: list) -> None:
    """Validate entities have profile structure."""
    entities_path = root / "entities.yaml"
    if not entities_path.exists():
        return
    entities_data = load_json_compatible_yaml(entities_path, {})
    for entity in entities_data.get("entities", []):
        if "profile" not in entity:
            issues.append({
                "level": "warn",
                "message": f"实体 '{entity.get('name')}' 缺少 profile 字段，建议重新初始化或运行 entity enrich",
            })
        if "seed" not in entity:
            issues.append({
                "level": "info",
                "message": f"实体 '{entity.get('name')}' 缺少 seed 字段，建议通过 brainstorm character 创建种子",
            })
```

Then add calls to these in the main doctor command function, alongside existing checks.

**Step 3: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add src/story_harness_cli/commands/doctor.py
git commit -m "feat(doctor): add outline volumes and entity profile validation"
```

---

## Task 11: Final integration test

**Files:**
- Create: `tests/smoke/test_full_creative_loop.py`

**Step 1: Write integration test**

```python
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


class FullCreativeLoopTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="story-harness-full-"))
        fixture = REPO_ROOT / "tests" / "fixtures" / "minimal_project"
        shutil.copytree(fixture, self.temp_dir, dirs_exist_ok=True)
        for d in ["proposals", "reviews", "projections", "logs"]:
            (self.temp_dir / d).mkdir(exist_ok=True)

        entities = {
            "entities": [
                {
                    "id": "char-linzhou", "name": "林舟", "source": "seed", "aliases": [],
                    "seed": {"archetype": "落魄侦探", "personality": "冷静、固执", "motivation": "追查真相", "background": "前刑侦"},
                    "profile": {"appearance": [], "abilities": [], "speech": [], "relationships": []},
                    "currentState": {"status": "active", "physicalState": [], "emotionalState": [], "location": "未知", "lastUpdatedChapter": None},
                    "createdAt": "2026-01-01T00:00:00",
                },
                {
                    "id": "char-shenzhao", "name": "沈昭", "source": "seed", "aliases": [],
                    "seed": {"archetype": "双重间谍", "personality": "冷静、多疑", "motivation": "生存", "background": "情报人员"},
                    "profile": {"appearance": [], "abilities": [], "speech": [], "relationships": []},
                    "currentState": {"status": "active", "physicalState": [], "emotionalState": [], "location": "未知", "lastUpdatedChapter": None},
                    "createdAt": "2026-01-01T00:00:00",
                },
            ],
            "enrichmentProposals": [],
        }
        outline = {
            "volumes": [
                {"id": "vol-001", "title": "迷雾序章", "theme": "真相", "chapters": [
                    {"id": "chapter-001", "title": "裂痕之夜", "status": "draft", "direction": "两人在仓库对峙", "beats": [
                        {"id": "beat-1", "summary": "开场", "status": "completed"},
                        {"id": "beat-2", "summary": "对峙", "status": "planned"},
                    ]},
                ]},
            ],
            "chapters": [{"id": "chapter-001", "title": "裂痕之夜", "status": "draft", "beats": [], "scenePlans": []}],
            "chapterDirections": [],
        }
        for name, content in [
            ("entities.yaml", json.dumps(entities, ensure_ascii=False)),
            ("outline.yaml", json.dumps(outline, ensure_ascii=False)),
            ("proposals/draft-proposals.yaml", '{"draftProposals":[]}'),
            ("reviews/change-requests.yaml", '{"changeRequests":[]}'),
            ("projections/projection.yaml", '{"snapshotProjections":[],"relationProjections":[],"sceneScopeProjections":[],"timelineProjections":[],"causalityProjections":[]}'),
            ("projections/context-lens.yaml", '{"currentChapterId":null,"lenses":[]}'),
            ("logs/projection-log.yaml", '{"projectionChanges":[]}'),
        ]:
            p = self.temp_dir / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content + "\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_loop(self):
        r = str(self.temp_dir)
        # Phase 2: analyze → enrich → review → suggest → review → projection → context
        self.assertEqual(main(["chapter", "analyze", "--root", r, "--chapter-id", "chapter-001"]), 0)
        self.assertEqual(main(["entity", "enrich", "--root", r, "--chapter-id", "chapter-001"]), 0)
        self.assertEqual(main(["entity", "review", "--root", r, "--all-pending", "--decision", "accepted"]), 0)
        self.assertEqual(main(["chapter", "suggest", "--root", r, "--chapter-id", "chapter-001"]), 0)
        self.assertEqual(main(["review", "apply", "--root", r, "--chapter-id", "chapter-001", "--all-pending", "--decision", "accepted"]), 0)
        self.assertEqual(main(["projection", "apply", "--root", r, "--chapter-id", "chapter-001"]), 0)
        self.assertEqual(main(["context", "refresh", "--root", r, "--chapter-id", "chapter-001"]), 0)

        # Phase 3: consistency check
        self.assertEqual(main(["consistency", "check", "--root", r, "--chapter-id", "chapter-001"]), 0)

        check_file = self.temp_dir / "projections" / "consistency-check-chapter-001.yaml"
        self.assertTrue(check_file.exists())
        check_data = json.loads(check_file.read_text(encoding="utf-8"))
        self.assertIn("hardChecks", check_data)
        self.assertIn("softChecks", check_data)
        self.assertIn("contextForAI", check_data)

        # Verify entity profile was enriched
        entities = json.loads((self.temp_dir / "entities.yaml").read_text(encoding="utf-8"))
        linzhou = next(e for e in entities["entities"] if e["id"] == "char-linzhou")
        self.assertTrue(len(linzhou["profile"].get("appearance", [])) > 0 or len(linzhou["profile"].get("abilities", [])) > 0)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run integration test**

Run: `python -m pytest tests/smoke/test_full_creative_loop.py -v`
Expected: PASS

**Step 3: Run complete test suite**

Run: `python -m pytest tests/ -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add tests/smoke/test_full_creative_loop.py
git commit -m "test: add full creative loop integration test"
```

---

## Summary of all commits

| # | Scope | Commit message |
|---|-------|---------------|
| 1 | Schema | `feat(schema): add enrichmentProposals and volumes to default state` |
| 2 | Data | `feat(data): add inspiration word tables for brainstorm` |
| 3 | Inspiration | `feat(inspiration): add random character/world/outline generator` |
| 4 | Brainstorm cmd | `feat(brainstorm): add character/world/outline brainstorm commands` |
| 5 | Text keywords | `feat(text): add appearance and ability keyword detection` |
| 6 | Enricher svc | `feat(enricher): add entity enrichment service with appearance/ability detection` |
| 7 | Entity cmd | `feat(entity): add entity enrich and review commands` |
| 8 | Consistency svc | `feat(consistency): add consistency engine with state/relation/outline checks` |
| 9 | Consistency cmd | `feat(consistency): add consistency check command with context output` |
| 10 | Doctor | `feat(doctor): add outline volumes and entity profile validation` |
| 11 | Integration | `test: add full creative loop integration test` |

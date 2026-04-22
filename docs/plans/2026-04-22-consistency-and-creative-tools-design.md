# Story Harness CLI — 创作辅助工具 & 一致性校验设计

> Date: 2026-04-22
> Status: Draft
> Scope: 角色卡片 / 三级大纲 / 随机灵感库 / 设定偏离检测

---

## 1. 背景

现有 CLI 实现了章节分析、变更提案、review 门控和 projection 真相源等状态管理能力，但缺少：

- **角色卡片**：entities 仅有 id/name，无性格、外貌、背景等结构化信息
- **三级大纲**：outline 为扁平结构，缺少 卷→章→场景 层级
- **创作辅助**：无头脑风暴/随机灵感生成能力
- **设定偏离检测**：doctor 只做结构校验，无语义一致性检查

本设计在现有架构上扩展，保持"CLI 输出结构化上下文，AI 外部判断"的解耦原则。

---

## 2. 设计决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| AI 集成方式 | CLI 输出上下文包，AI agent 外部判断 | CLI 保持纯工具，无外部依赖 |
| 角色卡片来源 | 种子设定（人机共创）+ AI 从正文补充 | 渐进式，最自然的创作流 |
| 大纲层级 | 卷→章→场景 三级结构 | 兼顾组织性和简洁，适合中长篇 |
| 校验范围 | 角色/关系/时间线(硬) + 大纲偏离(软) | 核心矛盾必须拦截，细纲偏离可容忍 |
| 校验时机 | 每章写完后增量校验 | 尽早发现，避免漂移累积 |

---

## 3. 整体架构：三阶段创作闭环

```
 Phase 1: 构思（Brainstorm）
   story-harness brainstorm character  → 随机/讨论生成角色种子
   story-harness brainstorm world      → 随机/讨论生成世界观要素
   story-harness brainstorm outline    → 讨论→生成三级大纲骨架
   ↓ 产出: entities.yaml + outline.yaml

 Phase 2: 写作（Write）
   chapter analyze     → 提取角色状态/关系 + 外貌/能力片段
   entity enrich       → 生成角色卡片补充提案（走 review 门控）
   review apply        → 确认 enrichments
   chapter suggest     → 生成变更请求
   review apply        → 确认变更
   projection apply    → 更新真相源
   context refresh     → 生成下章上下文

 Phase 3: 校验（Check）
   consistency check   → 输出结构化校验上下文包 → AI agent 判断
```

---

## 4. Phase 1 — 构思阶段

### 4.1 brainstorm 命令

```bash
# 随机生成角色原型建议
story-harness brainstorm character --root ./demo --random
# 输出 JSON:
# {
#   "suggestions": [
#     {"archetype": "落魄贵族", "personality": ["高傲","脆弱"],
#      "motivation": "恢复家族荣光", "conflict": "与旧友立场对立"},
#   ]
# }

# 随机生成世界观要素
story-harness brainstorm world --root ./demo --random

# 基于已有角色/世界观，生成大纲骨架
story-harness brainstorm outline --root ./demo
```

CLI 产出结构化选项，AI agent 负责自然语言交互讨论和最终确认。

### 4.2 随机灵感库

```
src/story_harness_cli/data/
  archetypes.yaml       # 角色原型词表（落魄侦探、天才少女、隐世高人...）
  motivations.yaml      # 动机词表（复仇、寻宝、救赎、探索...）
  personalities.yaml    # 性格特质词表（MBTI/经典原型映射）
  conflicts.yaml        # 冲突类型词表（立场对立、利益冲突、误解...）
  world_elements.yaml   # 世界观要素（时代、地理、力量体系）
  names_cn.yaml         # 中文姓名词表
```

可选外挂 `faker` 库增强随机性。内置词表满足零依赖需求。

---

## 5. 数据结构扩展

### 5.1 entities.yaml — 角色卡片

```yaml
entities:
  - id: "char-linzhou"
    name: "林舟"
    source: "seed"                    # seed | inferred

    # 种子字段（brainstorm 阶段人机共创生成）
    seed:
      archetype: "落魄侦探"
      personality: "冷静、固执、内心善良但表现冷漠"
      motivation: "追查师父死亡的真相"
      background: "前刑侦人员，因一次失误被开除"

    # AI 补充字段（写作阶段 entity enrich 后写入）
    profile:
      appearance:
        - detail: "左手有疤痕"
          source: "chapter-003"
          evidence: "林舟下意识遮住左手的疤痕"
          confidence: 0.9
      abilities:
        - name: "格斗"
          level: "熟练"
          evidence: "..."
          confidence: 0.85
      speech: []                      # 口头禅/说话风格
      relationships: []               # 由 relationProjections 聚合

    # 状态追踪（projection 自动维护）
    currentState:
      status: "active"                # active | deceased | absent
      physicalState: []               # ["受伤", "疲惫"]
      emotionalState: []              # ["愤怒"]
      location: "未知"
      lastUpdatedChapter: "chapter-003"

    aliases: ["舟哥", "老林"]
    createdAt: "2026-04-22T10:00:00Z"
```

### 5.2 outline.yaml — 三级大纲

```yaml
outline:
  volumes:
    - id: "vol-1"
      title: "迷雾序章"
      theme: "真相的代价"
      chapters:
        - id: "chapter-001"
          title: "血色仓库"
          status: "completed"           # planned | drafting | completed
          direction: "林舟在废弃仓库发现..."
          beats:
            - id: "beat-001-1"
              summary: "林舟受伤进入仓库"
              pov: "char-linzhou"
              keyEntities: ["char-linzhou"]
              status: "completed"       # planned | completed | skipped
            - id: "beat-001-2"
              summary: "发现神秘线索"
              status: "completed"

  # 向下兼容：自动从 volumes 同步
  chapters: []
  chapterDirections: []
```

### 5.3 一致性校验输出

```yaml
# projections/consistency-check-chapter-003.yaml
checkId: "check-chapter-003-2026-04-22"
chapterId: "chapter-003"
checkedAt: "2026-04-22T15:00:00Z"

# 硬检测（strict）— CLI 自动检测
hardChecks:
  stateContradictions:
    - entity: "char-linzhou"
      issue: "projection 标记为 deceased，但正文中有活跃描写"
      evidence:
        - projection: "status=deceased (chapter-002)"
        - chapter: "chapter-003 第4段: '林舟站起身，朝门口走去'"
  relationContradictions:
    - from: "char-a"
      to: "char-b"
      issue: "projection 标记关系为'裂痕'，正文表现亲密"
      previousLabel: "裂痕"
      currentEvidence: "chapter-003 第7段: '...'"
  timelineConflicts:
    - issue: "第3章声称'三天后'，但第2章→第3章间隔仅1天"
      evidence: [...]

# 软检测（advisory）— 只报告不阻塞
softChecks:
  outlineDeviations:
    - beatId: "beat-003-2"
      summary: "揭示反派身份"
      status: "planned"
      note: "细纲中规划的场景在正文中未出现，可能是故意跳过"

# 上下文包（供 AI 深度语义判断）
contextForAI:
  entityCards: [...]           # 涉及角色的完整卡片
  relevantProjections: [...]   # 相关 snapshot/relation projections
  chapterContent: "..."        # 本章正文
  outlineExpectation: "..."    # 大纲/细纲对本章的期望
  previousChapterSummary: "..."
```

---

## 6. CLI 自动检测 vs AI 语义判断分工

| 检测类型 | CLI 自动 | AI 语义 |
|---------|----------|---------|
| 角色死亡后再出现 | `status=deceased` + 正文有行动 | - |
| 关系标签矛盾 | projection.label vs 关键词 | 暧昧场景需语义理解 |
| 外貌描述矛盾 | - | "短发"→"长发"需语义推理 |
| 细纲偏离 | beat.status=planned + 章节完成 | 判断是故意跳过还是遗漏 |
| 时间线冲突 | - | "三天后"vs 间隔天数需推理 |
| 行为不符合人设 | - | 与 personality/seed 矛盾需推理 |
| 状态关键词冲突 | 在 STATE_KEYWORDS 内 | 不在词表内的需语义理解 |

---

## 7. 新增/修改模块清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `commands/brainstorm.py` | brainstorm 命令（character/world/outline） |
| `commands/consistency.py` | consistency check 命令 |
| `commands/entity.py` | entity enrich 命令 |
| `services/consistency_engine.py` | 一致性校验引擎 |
| `services/inspiration.py` | 随机灵感生成器 |
| `services/entity_enricher.py` | 角色卡片补充提取 |
| `data/*.yaml` | 随机灵感词表（6个文件） |

### 修改文件

| 文件 | 改动 |
|------|------|
| `protocol/schema.py` | 扩展 entities 和 outline 的默认结构 |
| `services/analyzer.py` | 增加外貌/能力/语言风格片段提取 |
| `utils/text.py` | 扩展关键词表（外貌词、能力词、性格描述词） |
| `commands/doctor.py` | 新增一致性检查项 |
| `cli.py` | 注册新命令 |
| `protocol/files.py` | 新增文件路径（consistency-check output） |

---

## 8. 实现优先级

### P0 — 基础骨架
1. 扩展 `schema.py`（entities profile + outline volumes 结构）
2. 实现随机灵感库 `data/*.yaml` + `services/inspiration.py`
3. `commands/brainstorm.py` 基础命令

### P1 — 角色卡片
4. `services/entity_enricher.py` — 从正文提取外貌/能力片段
5. `commands/entity.py` — enrich 命令 + review 门控

### P2 — 一致性校验
6. `services/consistency_engine.py` — 硬检测逻辑
7. `commands/consistency.py` — check 命令 + 上下文包输出

### P3 — 增强
8. `commands/doctor.py` 扩展一致性检查
9. context-lens 增强输出角色卡片格式
10. outline 自动同步 volumes → 扁平字段

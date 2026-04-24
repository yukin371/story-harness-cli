# PRD: {书名}

> 最后更新: {YYYY-MM-DD}
> 产品阶段: 概念 | 开发中 | 精修 | 完结
> Story Harness 版本: {vX.Y}

---

## 1. 产品定义

| 字段 | 内容 |
|------|------|
| 书名 | |
| 主类型 | `fantasy` / `scifi` / `mystery` / `romance` / `literary` / ... |
| 子类型 | `urban-occult` / `xuanhuan` / `western-fantasy` / ... |
| 风格标签 | `web-serial` / `light-novel` / `literary-fiction` / ... |
| 目标平台 | 起点 / 番茄 / 出版 / 自发布 / ... |
| 目标读者 | 画像描述（年龄段、阅读偏好、平台习惯） |
| 目标字数 | 总字数（如 50 万字 / 10 万字） |

### 1.1 一句话 premise

> {用一句话说清楚这个故事讲什么}

### 1.2 hook line

> {用一句话抓住读者注意力，通常 30 字以内}

### 1.3 核心卖点

1. {卖点 1：比如"每章结尾保留追读钩子"}
2. {卖点 2：比如"2-3 章一个单元案，节奏紧凑"}
3. {卖点 3：比如"职业线+民俗志怪双重硬核设定"}

---

## 2. 商业连载蓝图

| 字段 | 内容 |
|------|------|
| 连载模型 | 单元案 / 卷级连载 / 连续推进 / ... |
| 更新频率 | 日更两章 / 周更 / ... |
| 单章字数底线 | {N} 字 |
| 单章字数建议 | {N} 字 |
| 钩子栈 | `career-entry-hook`, `cliffhanger-end`, ... |
| 对标作品 | 1-3 部同类型标杆 |

### 2.1 故事契约

- 核心承诺:
  - {承诺 1}
  - {承诺 2}
- 避免事项:
  - {避免 1}
  - {避免 2}
- 结局承诺: {比如"卷一完成 XX 跃迁"}
- 节奏承诺: {比如"中快节奏"}

---

## 3. 产出物标准

### 3.1 卷级结构

| 卷 | 章节范围 | 卷标题 | 主要事件 |
|----|---------|--------|---------|
| 卷一 | ch-001 ~ ch-012 | {卷标题} | {简要描述} |
| ... | ... | ... | ... |

### 3.2 文件组织规范

#### 短篇（< 5 万字）— 扁平结构

```
{project-root}/
├── PRD.md                       # 产品需求文档
├── README.md                    # 工程入口
├── project.yaml                 # 定位数据
│
├── spec/                        # 规格层
│   ├── outline.yaml             #   大纲（单文件足够）
│   ├── entities.yaml            #   人物设定（单文件足够）
│   └── timeline.yaml            #   时间线
│
├── drafts/chapters/             # 草稿层
├── workflow/                    # 工作流中间产物
│   ├── proposals/
│   ├── reviews/
│   └── projections/
├── exports/                     # 导出产物
└── logs/
```

#### 长篇（>= 5 万字 / 多卷）— 按卷拆分

```
{project-root}/
├── PRD.md                       # 产品需求文档
├── README.md                    # 工程入口
├── project.yaml                 # 定位数据（全局，含商业蓝图）
│
├── spec/                        # 规格层
│   ├── outline.yaml             #   大纲索引（卷级骨架、全局线程、卷间伏笔）
│   ├── outlines/                #   按卷拆分的章节级大纲
│   │   ├── vol-001.yaml         #     卷一大纲（方向、beats、scenePlans）
│   │   ├── vol-002.yaml         #     卷二大纲
│   │   └── ...
│   ├── entities.yaml            #   人物索引（名字 + 类型 + 首次出场卷/章）
│   ├── entities/                #   按人物拆分的详细设定
│   │   ├── protagonist.yaml     #     主角详细设定
│   │   ├── {name}.yaml          #     其他角色详细设定
│   │   └── ...
│   ├── timeline.yaml            #   全局时间线（卷级索引）
│   ├── timelines/               #   按卷拆分的事件流
│   │   ├── vol-001.yaml
│   │   └── ...
│   ├── threads.yaml             #   主线/支线追踪
│   └── structures.yaml          #   结构定义
│
├── drafts/                      # 草稿层
│   └── chapters/
│       ├── chapter-001.md
│       ├── chapter-002.md
│       └── ...
│
├── workflow/                    # 工作流中间产物
│   ├── proposals/
│   ├── reviews/
│   └── projections/
│       ├── projection.yaml      #   当前投影（自动按章节切片）
│       └── context-lens.yaml    #   当前上下文透镜
│
├── exports/                     # 导出产物
│   ├── manuscript.md
│   ├── manuscript.txt
│   └── manuscript.json
│
└── logs/
```

### 3.3 拆分策略

| 文件类型 | 短篇 | 长篇（按卷拆分） | AI 上下文窗口适配 |
|---------|------|----------------|-----------------|
| 大纲 | 单文件 | `outline.yaml` 索引 + `outlines/vol-*.yaml` 按卷 | `context refresh` 只加载当前卷大纲 |
| 人物 | 单文件 | `entities.yaml` 索引 + `entities/*.yaml` 按角色 | `context refresh` 只加载活跃角色 |
| 时间线 | 单文件 | `timeline.yaml` 索引 + `timelines/vol-*.yaml` 按卷 | 按需加载当前卷事件 |
| 评审/投影 | 按章节 | 按章节（不变） | 已经是单章粒度 |

**拆分触发条件**：当单文件超过 ~500 行或 ~20KB 时，启动按卷拆分。

### 3.4 章节要求

- 每章必须维护显式 `scenePlans`
- 每章必须通过 `doctor` 检查
- 字数不低于底线，建议达到目标字数

---

## 4. 质量门禁

> 类比：软件项目的 CI/CD 门禁

### 4.1 提交前检查（= pre-commit）

每写完一章，必须通过以下检查才能视为"已交付"：

| 检查项 | 命令 | 通过条件 |
|--------|------|---------|
| 结构完整性 | `doctor` | errors=0, warnings=0 |
| 章节分析 | `chapter analyze` | 实体提取正常 |
| 章节评审 | `review chapter` | 加权分 >= {N}/100 |
| 一幕评审 | `review scene` | 每个 scene >= {N}/100 |
| 一致性 | `consistency check` | 无冲突 |

### 4.2 单卷交付检查（= release checklist）

- [ ] 所有章节通过提交前检查
- [ ] 字数统计 `stats` 显示无低于底线章节
- [ ] 大纲 `outline check` 通过
- [ ] 导出 `export` 成功生成

### 4.3 评分标准参考

| 评分区间 | 含义 |
|---------|------|
| 90-100 | 优秀，可直接发布 |
| 80-89 | 合格，小幅优化后发布 |
| 70-79 | 需要修改，有明显问题 |
| < 70 | 不合格，必须重写 |

---

## 5. 验收标准

### 5.1 单章交付条件

1. `doctor` 通过（errors=0）
2. `review chapter` 加权分 >= 80
3. 字数 >= 底线字数
4. `context refresh` 可正常刷新到下一章

### 5.2 单卷交付条件

1. 卷内所有章节通过单章交付条件
2. `stats` 显示卷内无字数缺口
3. `export` 可导出完整卷正文
4. 主线/支线状态与 `outline.yaml` 一致

### 5.3 完结交付条件

1. 所有卷通过单卷交付条件
2. 故事契约中的核心承诺全部兑现
3. 结局承诺兑现
4. 全文导出成功

---

## 6. 工具支撑

> Story Harness CLI 提供的结构化工作流

### 6.1 推荐写作闭环

```
outline check → chapter write → chapter analyze → review chapter →
review scene → chapter suggest → review apply → projection apply →
context refresh → (下一章)
```

### 6.2 命令矩阵

| 阶段 | 命令 | 用途 |
|------|------|------|
| 初始化 | `init` | 创建项目结构与定位 |
| 规划 | `outline propose/promote/check` | 大纲管理 |
| 场景 | `outline scene-add/scene-list/scene-detect` | 场景边界维护 |
| 细纲 | `outline beat-add/beat-complete/beat-list` | 细纲追踪 |
| 分析 | `chapter analyze` | 章节分析（实体提取） |
| 评审 | `review chapter/scene` | 章节与一幕评审 |
| 建议 | `chapter suggest` | 生成改进建议 |
| 应用 | `review apply` | 应用/拒绝变更请求 |
| 投影 | `projection apply` | 更新投影 |
| 上下文 | `context refresh/show` | 刷新写作上下文 |
| 检查 | `doctor` | 项目结构校验 |
| 一致性 | `consistency check` | 一致性校验 |
| 统计 | `stats` | 项目统计 |
| 导出 | `export --format md/txt/json` | 多格式导出 |
| 实体 | `entity enrich/review/list/show` | 角色管理 |
| 时间线 | `timeline add/list/check` | 时间线管理 |
| 搜索 | `search` | 跨章节搜索 |

---

## 7. 当前状态

### 7.1 进度

| 指标 | 值 |
|------|-----|
| 活跃卷 | {卷名} |
| 已完成章节 | {N}/{M} |
| 活跃章节 | chapter-{NNN} |
| 总字数 | {N} 字 |

### 7.2 已知问题

- {问题描述 1}
- {问题描述 2}

### 7.3 下一步

- {下一步计划}

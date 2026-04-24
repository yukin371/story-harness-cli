# 项目定位层与故事契约落地

> 日期: 2026-04-23
> 状态: 已落地

## 背景

此前仓库已补充：

- `review chapter` 通用章节评分
- 类型化评审标准表

但“类型、目标读者、故事承诺”仍停留在文档层，没有进入项目初始化与配置结构，导致：

1. 写作前无法显式声明小说工程约束
2. 后续 review 无法读取目标类型和目标群体
3. 不同项目之间缺少统一的定位元数据

## 目标

将“小说像软件工程一样管理”的定位真正落到 `project.yaml` 中，形成可执行的项目元数据。

## 设计

### 新增 project.yaml 两个顶层块

```json
{
  "positioning": {
    "primaryGenre": "",
    "subGenre": "",
    "styleTags": [],
    "targetAudience": []
  },
  "storyContract": {
    "corePromises": [],
    "avoidances": [],
    "endingContract": "",
    "paceContract": ""
  }
}
```

### init 参数

在现有 `init` 上增加：

- `--primary-genre`
- `--sub-genre`
- `--style-tag`（可重复）
- `--target-audience`（可重复）
- `--core-promise`（可重复）
- `--avoidance`（可重复）
- `--ending-contract`
- `--pace-contract`

### 兼容性

- 默认值全为空或空数组
- 老项目缺失字段时，不应报错
- 不修改现有 workflow 文件结构

## 本轮范围

- schema 默认值
- `init` 参数与写入逻辑
- smoke tests
- 指南文档

## 后续可扩展

1. `review chapter` 根据 `positioning` 切换权重
2. 增加 `project show` 或 `project doctor` 对定位信息做检查
3. 增加 `scene review` 读取 `storyContract`

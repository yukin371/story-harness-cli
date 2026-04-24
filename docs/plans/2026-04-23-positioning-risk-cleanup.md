# 定位层风险清理与评审接入

> 日期: 2026-04-23
> 状态: 已落地

## 背景

上一轮已把 `positioning` 与 `storyContract` 落入 `project.yaml`，但仍有两个未闭环风险：

1. `genre` 与 `primaryGenre` 可能漂移
2. `doctor` 与 `review chapter` 尚未真正读取这些字段

## 本轮目标

- 降低 `project` 元数据漂移风险
- 让 `doctor` 对定位缺失给出显式告警
- 让 `review chapter` 输出项目契约对齐信息

## 本轮实现

### 1. 机器可处理标签归一化

新增 `utils/project_meta.py`：

- `normalize_machine_label`
- `is_machine_label`

用途：

- `init` 默认把 `genre` 归一为稳定 `primaryGenre` slug
- `doctor` 检查 `primaryGenre` 是否稳定

### 2. doctor 新增定位层检查

新增检查项：

- `missing-primary-genre`
- `non-normalized-primary-genre`
- `genre-primary-mismatch`
- `missing-target-audience`
- `missing-core-promises`
- `missing-pace-contract`

### 3. review chapter 新增契约对齐输出

新增输出块：

- `projectContext`
- `contractAlignment`

当前为启发式对齐，重点覆盖：

- 主类型基础对位
- 节奏承诺
- 核心卖点承诺（部分关键词）

## 验证

- `test_project_init`
- `test_doctor`
- `test_review_chapter`
- `test_schema`
- `test_outline_loop`
- `test_full_creative_loop`

## 后续

1. 将 `contractAlignment` 从启发式规则升级为类型化加权评分
2. 让 `doctor --strict` 可选要求定位层完整
3. 将 `storyContract` 继续接入 `scene review`

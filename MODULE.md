# 仓库根模块说明

> 最后更新: 2026-04-23
> 状态: 当前有效模块文档

## 1. 模块职责

- 提供仓库首页入口说明
- 为首次进入仓库的作者与外部 AI 指向当前 canonical 文档
- 记录项目级安装、验证与贡献入口

## 2. Owns

- `README.md`
- `CONTRIBUTING.md`
- 仓库根目录下的项目级说明文档

## 3. 不变量

- `README.md` 只保留项目摘要、核心能力与 canonical 文档入口
- 详细工作流必须指向 `docs/guides/*`，不在首页并行维护完整细节
- 首页能力描述不得与 `docs/roadmap.md`、`docs/PROJECT_PROFILE.md` 冲突

## 4. 文档同步触发条件

- 项目定位变化
- 当前工作流闭环变化
- 首页命令矩阵变化
- canonical guide 入口变化

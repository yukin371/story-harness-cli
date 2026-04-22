# 发布检查清单

> 最后更新: 2026-04-22
> 适用版本: v0.x 初始阶段

## 1. 发布前

- [ ] 版本号已确认（`pyproject.toml` 中的 `version`）
- [ ] 变更范围已确认
- [ ] breaking change 已明确标注
- [ ] release note 草稿已准备

## 2. 质量门禁

- [ ] `PYTHONPATH=src python -m unittest discover -s tests` 全部通过
- [ ] 无已知的 P0/P1 bug 遗留
- [ ] lint 通过或阻塞已说明（TBD: lint 工具待启用）

## 3. 兼容性与迁移

- [ ] CLI 参数变化已评估
- [ ] JSON 输出格式变化已评估
- [ ] YAML 数据模型变化已评估
- [ ] 迁移说明已补齐（如有 breaking change）

## 4. 文档同步

- [ ] `docs/roadmap.md` 已同步
- [ ] 模块文档已同步（如有变化）
- [ ] `README.md` 命令列表已同步
- [ ] `docs/PROJECT_PROFILE.md` 已同步（如有结构性变化）

## 5. 发布后

- [ ] git tag 已创建
- [ ] PyPI 发布成功（TBD: 待发布流程建立）
- [ ] 回滚路径已记录

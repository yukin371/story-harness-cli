# 2026-04-24 状态写回互斥收敛

## 背景

- `story-harness-cli` 使用文件型协议维护小说项目状态。
- 本地验证商业长篇样例时，多个会触发 `save_state()` 的命令并行执行，出现 `outline.yaml` 被后写命令覆盖成异常状态的情况。
- 该问题会直接影响 `review / projection / context / export / outline` 的闭环稳定性。

## 目标

- 为 `protocol.save_state()` 增加轻量级、stdlib-only 的写回互斥保护。
- 不改变现有 CLI 参数、输出格式和状态协议。
- 为锁机制补最小可回归测试，防止未来再次被无意并发写坏。

## 非目标

- 不引入数据库或守护进程。
- 不重构整个状态协议。
- 不保证所有读取都串行，只保证写回阶段互斥。

## 方案草案

1. 在 `protocol/state.py` 内引入基于锁文件的上下文管理器。
2. 进入 `save_state()` 时先申请项目根目录级别锁，再执行 `_sync_outline()` 和所有状态文件写回。
3. 锁实现要求：
   - stdlib only
   - Windows 可用
   - 超时失败时给出明确中文报错
   - 正常与异常路径都能释放锁
4. 为协议层或 smoke 层补回归测试：
   - 至少验证锁文件生命周期
   - 最好验证第二写者会等待或超时报错，而不是直接并发覆盖

## 风险

- Windows 下锁文件占用和删除时序容易踩坑。
- 如果超时默认值过短，长链路可能误报。
- 如果锁范围过大，会增加串行等待时间。

## 验证

- `python -m unittest tests.smoke.test_demo_urban_occult_long_sample -v`
- 新增锁相关测试
- 关键命令链路至少覆盖一次 `review -> projection -> context`

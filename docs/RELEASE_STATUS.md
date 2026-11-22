# 版本与使用范围

本分支为 **v2.0.0 候选版（Release Candidate）**，不是正式版，也未创建 v2 Stable Release。发布基线为 v1.0.0；v2 只新增执行层 Harness，不改变 v1 的领域决策规则。

v2 候选版在 v1.0.0 的 Skill 分发方式上新增：

- `scripts/harness.py`：本地研究任务编排、证据核验、检查点、反事实隔离、隐私生命周期和执行轨迹；
- 结构化工具结果契约、硬门槛研究阻断、证据过期与矛盾降级；
- 可恢复的 JSON Case State，以及 v1/v2 冻结对照测试。

## 验证范围

已完成：v1 回归（78 项决策引擎测试）、发布契约（10 项）、安装器安全测试（37 项）、v2 Harness 测试（41 项；独立审核分支为 52 项），并在本地 macOS / Python 3 环境执行；另有一个真实联网的 Trae Agent 回退端到端案例。

未完成：v2 在原生 Claude Code / Codex CLI 宿主中的真实端到端验收；v2 的联网研究案例仍需独立复核。上述项目标记为 **Not Run**，不得视为通过。

## 边界

- 不引入数据库、Web 服务、账号系统或通用 Agent Runtime。
- 不重新实现宿主的模型调用与浏览器；Harness 只管理状态、契约和可审计轨迹。
- 来源是否真正支持具体主张仍需模型辅助复核或人工裁定；程序检查只覆盖形式、范围、时效与依赖。
- 不创建 v2.0.0 Stable Release，不合并 `main`。

详见[兼容性](COMPATIBILITY.md)、[架构](ARCHITECTURE.md)、[隐私](PRIVACY.md)、[已知限制](KNOWN_LIMITATIONS.md)和 [v2.0 RC 验收报告](V2_RC_ACCEPTANCE.md)。

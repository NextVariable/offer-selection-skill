# Offer Selection Skill v1.0.0 发布说明草稿

Offer Selection Skill 结合你的背景、职业或学术目标、录取条件和预算，判断哪些硕士项目值得接受。默认 Quick Decision 给出结论、费用、关键风险和改变建议的条件。可进一步请求 Full Decision Audit 或变更一个条件查看前后差别。

## 从 v0.3.2 升级

- **费用与付款**。比较完整成本区间、现金流和预算压力。硕博项目可只核算硕士阶段，未确认部分会保留在报告中。
- **资格与证据**。针对项目和届别核对官方来源，显示影响建议的未确认条件。程序检查金额、证据记录和门槛状态，Agent 负责读原文和判断个体增量。
- **决策对照**。Quick 和 Full 共用同一结论。改变预算等条件时保留原案，并重算受影响部分。

发布支持范围拟限定为已原生验收的 Codex CLI。完整流程需要联网研究和 Python 3.10+。Claude Code 有安装与历史调用记录，最终原生验收尚未完成。TRAE 和 WorkBuddy 的验证范围见[兼容性](COMPATIBILITY.md)。

待正式发行后，以发布标签对应的源代码按[安装说明](INSTALLATION.md)安装。可先查看[自然语言示例](examples/13-structured-decision.md)、[已知限制](KNOWN_LIMITATIONS.md)和[隐私说明](PRIVACY.md)。

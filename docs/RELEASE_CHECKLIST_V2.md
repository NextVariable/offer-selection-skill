# v2.0.0 Stable 发布签核

范围为 [PR #4](https://github.com/NextVariable/offer-selection-skill/pull/4) 的 v2.0.0 发行。正式支持范围为 Codex CLI。

| 门槛 | 签核依据 |
|---|---|
| 候选 SHA 与 CI | 确认 PR Head，核对相同 SHA 的 push / PR CI，核查已有合并及标签状态。 |
| 正确性与隐私 | 核对[独立收口复核](V2_RELEASE_REVIEW.md)、已有集成用例、逐 Offer Gate、隐私修复和安装载荷。 |
| 原生验收 | 核对 Codex CLI 原生记录及复核范围。Claude Code 保留 Not Run，TRAE 回退单独记录。 |
| 文档与版本 | 签核候选为 `2.0.0-rc1`；发行版本为 `2.0.0`、stable。核对 README、状态、兼容性和[发行说明](RELEASE_NOTES_V2.md)。 |

- 维护者于 2026-11-24 签核候选 `ca7d102bf52be8b294c8a6be46791cdb4f2f7bee`。[候选 Push CI](https://github.com/NextVariable/offer-selection-skill/actions/runs/45355160779) · [候选 PR CI](https://github.com/NextVariable/offer-selection-skill/actions/runs/45355170625)
- [x] 维护者已签核当前候选和 Codex CLI 支持范围。
- [x] 维护者已明确授权合并、创建 `v2.0.0` 标签和正式发行。

授权后同步 manifest、SKILL.md frontmatter 和安装器的 `2.0.0` 版本值，切换 Stable 状态，更新安装入口和发行说明。随后核对新 Head 的本地测试、push CI、PR CI 和审批。按通过检查的 SHA 合并，确认合并树一致后打带注释的标签并发布。最后从该标签重新安装并运行 Codex CLI 冒烟测试。若 SHA、CI、审批、合并树或标签不符，暂停下一步写操作。

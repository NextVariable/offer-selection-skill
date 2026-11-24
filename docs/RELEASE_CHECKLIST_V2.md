# v2.0.0 Stable 发布签核

范围为 [PR #4](https://github.com/NextVariable/offer-selection-skill/pull/4) 的最终候选 Head，拟正式支持 Codex CLI。

| 门槛 | 签核依据 |
|---|---|
| 候选 SHA 与 CI | 确认 PR Head，核对相同 SHA 的 push / PR CI，核查已有合并及标签状态。 |
| 正确性与隐私 | 核对[独立收口复核](V2_RELEASE_REVIEW.md)、已有集成用例、逐 Offer Gate、隐私修复和安装载荷。 |
| 原生验收 | 核对 Codex CLI 原生记录及复核范围。Claude Code 保留 Not Run，TRAE 回退单独记录。 |
| 文档与版本 | 当前为 `2.0.0-rc1`、candidate。核对 README、状态、兼容性和[发行说明草稿](RELEASE_NOTES_V2.md)。 |

- 候选 SHA、CI 链接、签核人、日期：＿＿
- [ ] 维护者已签核当前候选和 Codex CLI 支持范围。
- [ ] 维护者已明确授权合并、创建 `v2.0.0` 标签和正式发行。

授权后同步 manifest、SKILL.md frontmatter 和安装器的 `2.0.0` 版本值，切换 Stable 状态，更新安装入口和发行说明。随后核对新 Head 的本地测试、push CI、PR CI 和审批。按通过检查的 SHA 合并，确认合并树一致后打带注释的标签并发布。最后从该标签重新安装并运行 Codex CLI 冒烟测试。若 SHA、CI、审批、合并树或标签不符，暂停下一步写操作。

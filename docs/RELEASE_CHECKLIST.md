# v1.0.0 发布门槛与执行顺序

发行对象为 [PR #3](https://github.com/NextVariable/offer-selection-skill/pull/3) 中基于 `bcc55d56b3e5a431121f6ac9860cf437830a7f8b` 的最终候选提交。当前应保持 Draft 和 candidate。维护者在签核记录里填写实际 SHA 并核对下表。CI 结果随 PR Head 更新。

| 门槛 | 核对方式 |
|---|---|
| 已审核运行时代码及全部修复在 PR 内 | 核对审核 SHA 是 PR Head 的祖先。发布准备期间对比运行时、安装器、测试和工作流的树内容。 |
| 最终提交 CI | 核对 PR Head 对应的 push run 与 PR checks。Linux Python 3.10/3.12、macOS、Windows 四项均应成功。 |
| 关键测试与 P0 | 核对单元测试、安装器、预算与反事实回归、默认 Quick/Full 和指定 Codex 原生案例记录。已知 P0 安全或关键资格缺陷须解决。 |
| 发布包隐私 | 核查公开父提交、最终差异、发布树和安装目录。仅发布公共文档、合成示例及仓库工具，安装器只交付运行时。 |
| 兼容性与文档 | 核对 [README](../README.md)、[安装说明](INSTALLATION.md)、[兼容性](COMPATIBILITY.md)、[已知限制](KNOWN_LIMITATIONS.md)、[更新记录](CHANGELOG.md)及[发布说明草稿](RELEASE_NOTES_V1.md)。 |
| 维护者人工签核 | **待签核**。填写姓名、日期、候选 SHA、CI 链接及核准宿主范围。 |
| 维护者明确授权 | **待授权**。单独记录对合并、标记与正式发布的授权。 |

## 签核记录

- 候选 SHA、PR 与 CI 链接：＿＿
- 维护者、签核日期、核准宿主范围：＿＿
- [ ] 维护者已复核行为结果、隐私范围与公开说明。
- [ ] 维护者已明确授权合并、创建 `v1.0.0` 标签及正式发布。

## 授权后执行

1. **固定待合并提交**。重新获取 `main`、PR Head 和标签状态。核对人工签核、已核准支持范围、审核 SHA 祖先关系、待合并 SHA 和保护规则。PR 必须仍指向 `main`。如果 `main` 已前进，重新核对差异、祖先和实际合并树。
2. **准备发行状态提交**。在获准之后，仅将 `.claude-plugin/plugin.json` 的 `release_status` 改为 `stable`，同步 README、安装说明、发布状态、兼容性、更新记录及发布说明中仍指向候选分支的文字。版本保持 `1.0.0`。在 PR 分支追加提交并重跑本地检查和该 Head 的 CI；维护者确认这个新 SHA。发布说明的安装入口指向未来的 `v1.0.0` 标签。
3. **将 Draft 转为 Ready for Review**。可用 `gh pr ready 3 --repo NextVariable/offer-selection-skill`。等待必须的审批和检查，再次核对 PR Head。分支变动、检查失败或还需审批即停止。
4. **合并 PR #3**。若仓库允许，使用 merge commit 保留审计提交的祖先关系。以 `gh pr merge 3 --merge --match-head-commit VERIFIED_HEAD --repo NextVariable/offer-selection-skill` 固定已签核 SHA。不要自动删除分支。完成后从 GitHub 读取实际 merge SHA，核对其包含已签核 Head 且树内容一致。检查失败时先停止打标签。
5. **创建并发布带注释的 `v1.0.0` 标签**。先确认远程没有同名标签或 Release。以已核实的 merge SHA 为标签目标，从公共工作副本只推该标签。若发现同名标签、版本不符或树不一致，停止并调查。保留既有标签与历史。
6. **创建 GitHub Release**。使用 `gh release create v1.0.0 --verify-tag --notes-file docs/RELEASE_NOTES_V1.md --repo NextVariable/offer-selection-skill`。说明文件须为第 2 步已审阅的正式内容。核对 GitHub 展示的目标与公开文件。
7. **从正式发布全新安装并做 Smoke Test**。在隔离目录检出 `v1.0.0`，使用其安装器生成全新的技能目录。确认版本、运行时文件和 `decision.py` 可用。用新 Codex 会话和最小合成示例执行 Quick、Full 和预算反事实，记录宿主、标签 SHA 及结果。发现故障时保留证据并停止继续推广；如需撤回变更，使用维护者授权的回退 PR 或后续修复版本，保留历史和标签。

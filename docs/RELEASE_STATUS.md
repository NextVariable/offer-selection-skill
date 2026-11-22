# 版本与使用范围

本分支为 **v1.0.0 候选版**。默认分支的公开正式版本仍为 v0.3.2。v1.0 草稿 PR 汇集已审核修复和发布文档，最终状态以 [PR #3](https://github.com/NextVariable/offer-selection-skill/pull/3) 的当前提交和检查为准。

独立审核基线为 `bcc55d56b3e5a431121f6ac9860cf437830a7f8b`。Codex CLI 已完成指定原生验收。Claude Code 最终原生验收为 **Not Run**，原因是第三方模型网关 402。TRAE 回退结果单独记录。详见[兼容性](COMPATIBILITY.md)和[分阶段审计](V1_RELEASE_AUDIT.md)。

正式发行仍需维护者完成[签核清单](RELEASE_CHECKLIST.md)，明确授权合并与发布。发布范围拟限定为已原生验收的 Codex CLI。[更新记录](CHANGELOG.md) · [发布说明草稿](RELEASE_NOTES_V1.md) · [已知限制](KNOWN_LIMITATIONS.md)

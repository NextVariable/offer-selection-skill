# Offer Selection Skill v2.0.0 发布说明

v2 在原有 Offer 决策规则上增加可选的本地执行工具。用户仍可用自然语言提供背景和 Offer，获得 Quick 或 Full 报告。

- **逐份 Offer 核实。** 依次研究决定性事实与资格，有记录地处理未知、过期或冲突的证据。「等价后择一」需要所有比较对象满足必需的资格覆盖。
- **恢复与对照。** 研究状态可以暂停后继续。预算等单项变化作为独立假设保存，保留原始案例。
- **本地资料保护。** POSIX 环境中新写入的状态文件仅供当前用户读写。到期后的个人背景清除在命令执行前保存。[隐私说明](https://github.com/NextVariable/offer-selection-skill/blob/v2.0.0/docs/PRIVACY.md)

正式支持范围为 Codex CLI，完整执行需要可访问原始网页与本地 Python 3.10+。Claude Code 的 v2 原生验收未运行，TRAE 仅有回退证据，其他宿主为实验性支持。[兼容性](https://github.com/NextVariable/offer-selection-skill/blob/v2.0.0/docs/COMPATIBILITY.md)

从 `v2.0.0` 标签按[安装说明](https://github.com/NextVariable/offer-selection-skill/blob/v2.0.0/docs/INSTALLATION.md)安装。发布提交与检查见 [PR #4](https://github.com/NextVariable/offer-selection-skill/pull/4)。

# 安装与更新

一行安装和首次使用见 [README](../README.md)。本页用于备用脚本安装、更新与排查。

## 备用安装

WorkBuddy 可按以下步骤安装；Codex、Claude Code 不使用 npx 时也可采用此方式。先下载仓库：

```bash
git clone https://github.com/yunheliu68-ux/offer-selection-skill.git
cd offer-selection-skill
```

也可下载 GitHub 的 Code → Download ZIP，解压后在终端进入仓库目录。

macOS / Linux 选择对应的一条命令：

```bash
# Codex
bash install.sh --platform codex
# Claude Code
bash install.sh --platform claude-code
# WorkBuddy
bash install.sh --platform workbuddy
```

Windows 需要 PowerShell 7（`pwsh`），选择对应的一条命令：

```powershell
# Codex
pwsh -File .\install.ps1 -Platform codex
# Claude Code
pwsh -File .\install.ps1 -Platform claude-code
# WorkBuddy
pwsh -File .\install.ps1 -Platform workbuddy
```

安装后开启 AI Agent 的新会话，按 [README 中的示例](../README.md#在-ai-聊天框开始使用) 调用。

## 更新与卸载

沿用原安装工具，不要混用；已有个人修改时先备份。

通过 npx 安装：

```bash
npx skills update offer-selection-skill -g
npx skills remove offer-selection-skill -g
```

分别用于更新和卸载。通过备用脚本安装：获取最新仓库后重新执行原安装命令；卸载时先确认实际安装位置并备份个人修改，再移除对应的 `offer-selection-skill` 文件夹。

## 安装遇到问题

找不到 `npx` 或 `git`：安装 Node.js LTS 或 Git 后重新打开终端。下载失败：检查网络能否访问 npm 和 GitHub。找不到 `pwsh`：安装 PowerShell 7，而不是使用旧版 Windows PowerShell。

AI Agent 找不到技能：确认安装时选择了正确的 AI Agent，开启新会话，必要时重启。npx 用户可用 `npx skills list -g` 查看安装记录；文件安装完成不代表 AI Agent 已加载技能。

提示目录已存在或拒绝覆盖：先确认旧副本的安装方式，备份个人修改，再用原工具更新或卸载。备用脚本不会覆盖不属于它管理的目录。

仍有问题，请在 Issue 中提供系统、AI Agent 版本、安装命令和去除私人信息的错误提示。

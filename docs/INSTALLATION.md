# 安装与更新

首次使用与对话示例见 [README](../README.md)。以下步骤涵盖正式标签安装、更新和卸载。

## 安装 v2.0.0

打开终端，在一个尚无同名目录的位置下载正式标签：

```bash
git clone --branch v2.0.0 --single-branch https://github.com/NextVariable/offer-selection-skill.git
cd offer-selection-skill
```

在 macOS / Linux 上运行 `bash maintenance/install.sh --platform codex`。
在 Windows 上安装 PowerShell 7 后运行 `pwsh -File ./maintenance/install.ps1 -Platform codex`。
安装器默认放到用户的 `.agents/skills/offer-selection-skill`。

开启一个新的 Codex 会话，输入「请使用 $offer-selection-skill，帮我比较硕士
Offer，先给 Quick Decision」。完整流程需要联网研究以及本地 Python 3.10+ 执行权限。
核对安装输出所示版本以及本次会话读取的技能路径。

安装器会同时安装 `scripts/decision.py` 和 `scripts/harness.py`。v2 的 Harness 是可选执行层；无法运行本地 Python 时，仍按 v1 文本契约使用，并注明程序校验未执行。

## 从默认分支安装

Codex CLI 为正式支持宿主。其他宿主的安装和验收范围见[兼容性](COMPATIBILITY.md)。

需要 [Node.js LTS](https://nodejs.org/) 和 [Git](https://git-scm.com/downloads)，已安装可跳过。打开电脑终端（macOS“终端”或 Windows PowerShell），执行：

```bash
npx skills add NextVariable/offer-selection-skill --skill offer-selection-skill -g
```

按提示选择使用的 AI Agent。刚安装 Node.js 或 Git 时，请先关闭并重新打开终端。

## WorkBuddy 界面导入

在 [GitHub 仓库](https://github.com/NextVariable/offer-selection-skill) 先选定版本标签或分支，再选择 **Code → Download ZIP** 并解压。

打开 WorkBuddy 的“专家·技能·连接器 → 技能 → 添加技能 → 上传技能”，导入解压后的 `skills/offer-selection-skill` 文件夹，不要只上传单个 `SKILL.md`。

## 脚本安装（可选）

也可使用本项目脚本安装到 Codex、Claude Code 或 WorkBuddy。以下命令下载默认分支。如需安装确切的 v1.0.0 版本，使用上面的标签命令：

```bash
git clone https://github.com/NextVariable/offer-selection-skill.git
cd offer-selection-skill
```

也可下载 GitHub 的 Code → Download ZIP，解压后在终端进入仓库目录。

macOS / Linux 选择对应的一条命令：

```bash
# Codex
bash maintenance/install.sh --platform codex
# Claude Code
bash maintenance/install.sh --platform claude-code
# WorkBuddy
bash maintenance/install.sh --platform workbuddy
```

Windows 需要 PowerShell 7（`pwsh`），选择对应的一条命令：

```powershell
# Codex
pwsh -File .\maintenance/install.ps1 -Platform codex
# Claude Code
pwsh -File .\maintenance/install.ps1 -Platform claude-code
# WorkBuddy
pwsh -File .\maintenance/install.ps1 -Platform workbuddy
```

安装后开启 AI Agent 的新会话，按 [README 中的示例](../README.md#使用示例) 调用。

v1 可执行校验使用 Python 3.10+。确认宿主允许终端调用后，可以在技能目录运行
`python3 scripts/decision.py --help`（Windows 用 `py -3`）。没有本地执行权限时，
宿主可沿用文字规则，并标明程序检查未执行。

## 更新与卸载

已有个人修改时先备份，并沿用原安装方式更新或卸载。

通过对话安装的用户，可让 AI Agent 按原方式更新或卸载；通过 WorkBuddy 界面导入的用户，可在技能管理中移除旧副本后导入新版。

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

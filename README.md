# Offer Selection Skill

**全网首个硕士留学 Offer 选择 Agent Skill，基于个人背景、职业目标与 ROI，倒推最适合你的 Offer 。**

## 拿到 Offer 之后，怎么选？

学校排名更高，是否值得多花几十万？想回国去私企/国央企就业、留当地工作，或者继续读博深造，同一组 Offer 会不会有不同答案？你已经有的学历、实习和研究经历，会怎样改变一个硕士项目的价值？

Offer Selection Skill 从你真正想去的岗位、行业或研究方向出发，判断每个项目能补上什么短板、能带来哪些实际可达的机会，以及这些变化是否值得你付出额外的学费、生活费和时间。

它不是一个大学排名器，也不会用固定权重机械打分。你提供个人背景和已经拿到的 Offer，AI 助手按照既定决策流程研究公开信息、核验关键条件，再给出针对你的建议。

支持 Codex、Claude Code、WorkBuddy 等 AI Agent 的本地技能安装。

## 快速开始

这是安装到 AI Agent 里的技能，不是独立软件。先准备支持本地 Skill 的客户端，并允许助手联网查资料；普通聊天窗口上传文件不等于完成本地安装。WorkBuddy 已验证文件安装和技能发现，完整调用仍待验证，详见 [兼容性](COMPATIBILITY.md)。

### 在终端安装

需要 [Node.js LTS](https://nodejs.org/)、Git，以及能访问 npm 和 GitHub 的网络。安装 Node.js 后重新打开终端。macOS 打开“终端”，Windows 打开 Windows Terminal 或 PowerShell；下面的命令在电脑终端执行，不是在 AI 聊天框输入：

```bash
npx skills add yunheliu68-ux/offer-selection-skill --skill offer-selection-skill -g
```

首次运行如果询问是否下载 `skills` 工具，确认后按安装向导选择你使用的客户端和安装方式。`-g` 表示安装到用户目录，跨项目可用，不必先下载 ZIP 或进入仓库目录。安装完成后开启客户端的新会话。WorkBuddy 用户请使用下方的 [备用安装方式](#备用安装方式)，不假定第三方工具支持它。

已有同名技能时先确认原来的安装方式，不要直接确认覆盖。更新和卸载应沿用同一工具，避免重复副本。

此方式使用第三方 [skills CLI](https://github.com/vercel-labs/skills)，会安装技能所在目录，包括附带的公开文档；本项目的备用脚本则只复制固定运行文件。2026-09-18 已在 macOS 临时项目中验证 Codex 和 Claude Code 的复制安装，七个运行文件完整且与本地一致；未覆盖已有全局安装，也未据此声明 Windows 或其他客户端已完成验证。

### 在 AI 聊天框开始使用

在新会话中发送：

```text
请使用 offer-selection-skill，帮我比较硕士 Offer。先问我需要的信息。
```

不需要先填完长表格。助手会根据已经知道的信息，追问真正影响选择的背景；公开学费、学制、课程和政策由助手查证，私人奖学金和接受截止日期由你补充。后面的完整提问示例是可选的。

### 确认安装成功

终端显示安装完成只证明文件安装完成。用 `npx skills list -g` 查看是否列出 `offer-selection-skill`，再在客户端的新会话中确认能找到该技能。你也可以请助手说明是否已加载该技能的 `SKILL.md` 和 `references/core-decision-engine.md`，并查看客户端提供的文件读取记录；一段普通选校建议本身不能证明技能已加载。

## 它会帮你看什么？

| 你在纠结什么？ | 它帮你判断什么？ |
| -------------------- | --------------------------------------------- |
| 想回国去私企，哪个 Offer 更适合？ | 结合你的学历、实习和技能，判断项目能否补上目标岗位需要的短板，以及你能否赶上招聘和实习窗口 |
| 想进国央企或体制内，应该怎么选？     | 核查目标岗位的专业、学历等报考或招聘条件，先判断是否符合要求，再比较项目价值        |
| 想留当地工作，也想保留回国退路？     | 分别分析当地就业与回国就业的可行性，比较语言、工作权限、招聘机会和转向成本         |
| 想继续读博，哪个硕士更有帮助？      | 判断项目能否提供与你研究目标相关的训练、研究成果、导师支持和推荐信机会           |
| 更贵的 Offer，值得多花这笔钱吗？  | 比较多付出的总成本能换来什么，以及这些机会对你是否有用、是否可达、是否承担得起       |

## 提供背景与完整示例（可选）

在 Codex 中可直接发送前面的自然语言提问；使用本项目备用脚本安装到 Claude Code 后，也可输入 `/offer-selection-skill` 调用。缺少决定性信息时助手会逐步追问。如果希望一次提供完整信息，可以参考：
```
本科背景：院校、专业、成绩
已获 Offer：学校、项目全名、入学年份
目标：行业、岗位，以及回国、留当地或读博的计划
经历：实习、科研，以及具体工作或成果
预算：理想总预算和最高可承受金额
求职准备：相关技能、简历和面试准备情况

最纠结的问题（可选）：你希望重点比较的取舍
```

学费、学制、课程、签证和公开招聘条件等，由具备联网能力的助手查证。奖学金、Offer 接受截止日期等个人专属条件，需要你补充。

### 完整提问示例

以下背景为虚构示例。使用时，请将背景与方括号中的内容替换为你的真实情况。

```text
请使用 offer-selection-skill，帮我比较以下硕士 Offer。

我的背景：
本科为国内 985 院校，计算机专业，均分 86。

实习经历：

1. [公司/行业、实习时长]的软件开发实习，主要参与内部工具开发，独立负责过完整项目。
   本人职责与成果：[具体负责什么、交付了什么、实际效果]
2. [公司/行业、实习时长]的产品经理实习，参与某 AI Agent 产品从 0 到 1 的建设。
   本人职责与成果：[负责的环节、交付内容、上线或用户反馈情况]

科研/项目经历：
[研究方向或项目内容、本人职责、具体成果；没有则填无]

我的 Offer：
A：[学校、项目全名、入学年份]
B：[学校、项目全名、入学年份]
两者均已获得正式录取，暂无奖学金。

我的目标：
毕业后回国找产品经理岗位，以就业为主，暂不考虑读博。
目前没有明确的城市偏好。

我的预算与准备：
理想总预算为 80 万元，最高可承受金额为 100 万元。
能够提前准备求职，但产品面试、案例表达和项目成果梳理仍需补强。

我最想弄清楚：
两个项目分别能改善我的哪些短板？
如果其中一个更贵，多付出的成本能换来什么？
两个项目的入学、毕业时间和课程安排，分别如何影响我参加国内秋招、实习和校招的资格与时间窗口？
项目提供的实习机会，对我的背景和目标是否真正可达？

请查证会影响选择的公开信息，并给出来源和适用时间。
先给结论，再解释决定性原因、主要风险，以及会改变建议的条件。
关键事实无法核实时，请明确说明；如果差距不明显或都不值得选，也请直接告诉我。
```

## 你会得到什么？

一份围绕你个人情况的决策建议：优先考虑哪个 Offer、原因是什么、额外花费能换来什么，以及哪些条件改变后需要重新选择。

建议会说明各 Offer 的推荐程度、决定性原因、成本与风险，以及接受前需要核实的条件。

分析也可能得出“两个项目没有明显差距”“需要先核实关键条件”，或“这几个都不值得接受”。它不会为了给出赢家而强行排序。

## 备用安装方式

<details>
<summary>不使用 npx，或需要安装到 WorkBuddy：下载后运行原安装脚本</summary>

这是与快速开始不同的一套安装工具。请选择一种方式并沿用；原安装器不会接管第三方工具安装的目录。

### 环境要求

需要支持本地 Skill 且具备联网搜索能力的 AI Agent，例如 Codex、Claude Code 或 WorkBuddy。macOS / Linux 使用 Bash；Windows 需要 PowerShell 7+（`pwsh`）。

### 获取技能

使用 Git 下载，并进入仓库目录：

```bash
git clone https://github.com/yunheliu68-ux/offer-selection-skill.git
cd offer-selection-skill
```

也可以在 GitHub 页面选择 **Code → Download ZIP**，解压后在终端中进入包含 `SKILL.md`、`install.sh` 和 `install.ps1` 的目录。

### macOS / Linux

在仓库目录中，选择你使用的客户端，执行对应的一条命令：

```bash
# Codex
bash install.sh --platform codex

# Claude Code
bash install.sh --platform claude-code

# WorkBuddy
bash install.sh --platform workbuddy
```

### Windows

在仓库目录中，选择你使用的客户端，执行对应的一条命令：

```powershell
# Codex
pwsh -File .\install.ps1 -Platform codex

# Claude Code
pwsh -File .\install.ps1 -Platform claude-code

# WorkBuddy
pwsh -File .\install.ps1 -Platform workbuddy
```

### 启用与更新

安装后，刷新客户端技能列表或开启新会话，再按“怎么用”调用技能。

更新时，获取仓库最新内容，再执行原安装命令。安装器会拒绝覆盖不属于它管理的已有目录。

</details>

## 更新与常见问题

通过 `npx skills` 安装的用户，可在终端执行 `npx skills update offer-selection-skill -g` 更新；需要移除时执行 `npx skills remove offer-selection-skill -g` 并按提示确认客户端。用原脚本安装的用户，重新获取最新仓库后执行原安装命令，不要混用。

<details>
<summary>提示找不到 npx、Git，或下载失败</summary>

找不到 `npx`：安装 Node.js LTS 后重新打开终端。找不到 `git`：先安装 Git。连接超时或下载失败：检查能否访问 npm 和 GitHub；不要用管理员权限反复运行来解决网络问题。

</details>

<details>
<summary>安装完成，但客户端找不到技能</summary>

确认安装时选择了正确客户端，开启新会话，必要时重启客户端。`npx skills list -g` 可以确认工具记录的安装状态，但不证明客户端已经加载；原脚本安装的副本也不一定出现在该列表。仍找不到时，请在 Issue 中提供系统、客户端版本、安装命令和去除私人信息的错误提示。

</details>

<details>
<summary>提示目录已存在、拒绝覆盖，或可能有重复副本</summary>

先确认之前是用 `npx skills` 还是本项目脚本安装。不要直接删除技能目录或绕过保护：目录中可能有你自己的修改。沿用原方式更新；确需更换方式时，先备份个人改动，再使用原工具卸载或确认如何移除旧副本。

</details>

<details>
<summary>Windows 备用安装提示找不到 pwsh</summary>

备用脚本需要 PowerShell 7（`pwsh`），不是 Windows 自带的旧版 Windows PowerShell。安装 PowerShell 7 后重新打开终端，或使用前面的 `npx skills` 方式；该方式不需要运行本项目的 PowerShell 脚本。

</details>

## 使用前了解

当前为 **v0.3.2 正式版**。建议用于辅助决策，关键资格与政策请以最新官方信息为准。详见 [发布状态](RELEASE_STATUS.md)。

无需提供姓名、学号、邮箱或完整 Offer 信件。对话数据的保存与处理取决于你使用的 AI 平台，详见 [隐私说明](PRIVACY.md)。

## 进一步了解

[决策示例](examples/README.md) · [决策理念](docs/DECISION_PHILOSOPHY.md) · [架构说明](docs/ARCHITECTURE.md) · [兼容性](COMPATIBILITY.md)

使用问题欢迎通过 Issues 反馈。贡献请参阅 [贡献指南](CONTRIBUTING.md)，项目采用 [MIT License](LICENSE)。

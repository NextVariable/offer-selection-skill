# Offer Selection Skill

**全网首个硕士留学 Offer 选择 Agent Skill，基于个人背景、职场规划与 ROI，倒推最适合你的 Offer。**

## 拿到 Offer 之后，怎么选？

同一组 Offer，对不同背景和目标的人，价值可能完全不同。Offer Selection Skill 结合你的职场规划或学术深造目标，判断各项目能带来哪些实际机会，以及是否值得付出相应的学费、生活费和时间。

支持 Codex、Claude Code、WorkBuddy 等 AI Agent 的本地技能安装。

## 快速开始

使用支持本地 Skill 的 AI Agent，并开启联网搜索。

### 在终端安装

先安装 [Node.js LTS](https://nodejs.org/) 和 [Git](https://git-scm.com/downloads)，再重新打开电脑终端：macOS 使用“终端”，Windows 使用 Windows Terminal 或 PowerShell，执行下方命令。

```bash
npx skills add yunheliu68-ux/offer-selection-skill --skill offer-selection-skill -g
```

首次运行按提示确认下载，选择你使用的 AI Agent，安装后开启新会话。WorkBuddy 请使用下方的 [备用安装方式](#备用安装方式)。

### 在 AI 聊天框开始使用

在新会话中发送：

```text
请使用 offer-selection-skill，帮我比较硕士 Offer。先问我需要的信息。
```

不必一次填完所有背景，助手会逐步询问影响选择的必要信息。

### 确认安装成功

用 `npx skills list -g` 查看安装记录，再开启 AI Agent 的新会话，确认能找到 `offer-selection-skill`。找不到时，查看下方常见问题。

## 它会帮你看什么？

| 你在纠结什么？ | 它帮你判断什么？ |
| -------------------- | --------------------------------------------- |
| 想回国去私企，哪个 Offer 更适合？ | 结合你的学历、实习和技能，判断项目能否补上目标岗位需要的短板，以及你能否赶上招聘和实习窗口 |
| 想进国央企或体制内，应该怎么选？     | 核查目标岗位的专业、学历等报考或招聘条件，先判断是否符合要求，再比较项目价值        |
| 想留当地工作，也想保留回国退路？     | 分别分析当地就业与回国就业的可行性，比较语言、工作权限、招聘机会和转向成本         |
| 想继续学术深造，哪个硕士更有帮助？      | 判断项目能否提供与你研究目标相关的训练、研究成果、导师支持和推荐信机会           |
| 更贵的 Offer，值得多花这笔钱吗？  | 比较多付出的总成本能换来什么，以及这些机会对你是否有用、是否可达、是否承担得起       |

## 提供背景与完整示例（可选）

在 Codex 中可直接发送前面的自然语言提问；使用本项目备用脚本安装到 Claude Code 后，也可输入 `/offer-selection-skill` 调用。缺少决定性信息时助手会逐步追问。如果希望一次提供完整信息，可以参考：
```
本科背景：院校、专业、成绩
已获 Offer：学校、项目全名、入学年份
目标：行业、岗位，以及回国、留当地或学术深造的计划
经历：实习、科研，以及具体工作或成果
预算：理想总预算和最高可承受金额
求职准备：相关技能、简历和面试准备情况

最纠结的问题（可选）：你希望重点比较的取舍
```

学费、学制、课程、签证和公开招聘条件等，由具备联网能力的助手查证。奖学金、Offer 接受截止日期等个人专属条件，需要你补充。

<details>
<summary>查看完整提问示例</summary>

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
毕业后回国找产品经理岗位，以就业为主，暂不考虑学术深造。
目前没有明确的城市偏好。

我的预算与准备：
理想总预算为 80 万元，最高可承受金额为 100 万元。
能够提前准备求职，但产品面试、案例表达和项目成果梳理仍需补强。

我最想弄清楚：
两个项目分别能改善我的哪些短板？
如果其中一个更贵，多付出的成本能换来什么？
两个项目的入学、毕业时间和课程安排，分别如何影响我参加国内秋招、实习和校招的资格与时间窗口？
项目提供的实习机会，对我的背景和目标是否真正可达？
```

</details>

## 你会得到什么？

一份针对你个人情况的 Offer 建议：优先考虑哪个、决定性原因、额外花费的价值、主要风险，以及接受前需要核实的条件。

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

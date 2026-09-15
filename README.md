# Offer Selection Skill

**专注于硕士留学 Offer 选择的 AI Skill，基于个人背景、职业目标与 ROI，倒推更适合你的硕士决策。**

An evidence-driven AI skill for choosing between university offers based on your profile, goals, eligibility, career outcomes, and ROI — not rankings alone.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.2--rc-yellow.svg)](RELEASE_STATUS.md)

## 拿到 Offer 之后，怎么选？

学校排名更高，是否值得多花几十万？想回国就业、留当地工作，或者继续读博，同一组 Offer 会不会有不同答案？你已经有的学历、实习和研究经历，会怎样改变一个硕士项目的价值？

Offer Selection Skill 把这些问题放在一起分析。从你想去的岗位、行业或研究方向出发，判断每个项目能补上什么短板、提供哪些实际可达的机会，以及这些变化是否值得付出学费、生活费和时间。

它是一套安装到 AI 助手中的决策技能。你提供背景与 Offer，助手按照既定流程查找公开资料、比较选项，再给出有依据的建议。

## 它会帮你看什么？

| 你的问题 | 分析重点 |
|---|---|
| 回国进企业，哪个项目更有帮助？ | 目标岗位要求、已有实习与技能、项目能带来的增量、招聘时间 |
| 想进国央企或体制内，专业和学历是否符合要求？ | 具体岗位的专业、学历与资格条件，以及需要进一步核实的限制 |
| 想留当地工作，同时保留回国退路？ | 当地就业条件、语言与签证要求，以及回国路径；两条路径分别比较 |
| 将来想读博，该选授课型还是研究型硕士？ | 研究训练、导师与推荐信机会、学术准备和博士申请目标 |
| 更贵的项目到底值不值？ | 总成本、承受上限、机会成本，以及相对其他选项的实际收益 |

这里的 ROI 是对投入与可能回报的比较，不是承诺毕业薪资或计算一个看似精确的“回本年限”。排名可以作为信息，但不会单独决定结论。

## 怎么用？

安装后，在支持该技能的 AI 助手中提出你的问题。例如在 Claude Code 中输入：

```text
/offer-selection-skill

帮我比较手上的硕士 Offer。

本科背景：我的院校、专业和成绩情况
已获 Offer：学校、项目全名、入学年份
职业目标：希望从事的行业和岗位，回国、留当地或读博的计划
已有经历：实习、科研，以及具体做过什么
预算：理想总预算和绝对不能超过的上限
求职准备：技能、简历、面试准备，以及能否立即开始求职

我最纠结的是：更贵的项目能否带来值得付费的提升？
```

在 Codex 中，可以明确要求“使用 offer-selection-skill 帮我比较硕士 Offer”。不同客户端的技能入口可能不同。

不必一开始就准备完整表格。可以先说“帮我选 Offer”，再补充助手询问的个人信息。学费、学制、课程、签证和公开招聘条件等，由助手在具备联网能力时查证；奖学金、私人截止日期等非公开条件需要你提供。

## 你会得到什么？

一份围绕你个人情况的决策建议：优先考虑哪个 Offer、原因是什么、额外花费能换来什么，以及哪些条件改变后需要重新选择。

下面是一个简化的虚构示例，展示回答方式，不代表具体学校的真实表现：

> **你的情况：** 想回国做产品岗，已有两段相关实习。A、B 两个项目都在预算内。
>
> **如果已核实：** 两个项目对目标岗位的帮助接近，A 的总成本更低，而 B 最主要的优势是补充实习的机会。
>
> **建议：** 优先考虑 A。你已有相关实习，B 的额外机会对你的帮助可能不足以支撑更高支出。
>
> **什么会改变建议：** 如果你的实习内容与目标岗位关联很弱，而 B 确实能提供你可以参与的相关实践，B 值得重新考虑。机会是否可达还没有核实，就不能把它算作确定收益。

分析也可能得出“两个项目没有明显差距”“需要先核实关键条件”，或“这几个都不值得接受”。它不会为了给出赢家而强行排序。

## 安装

需要一个支持本地 Skill 的 AI 助手。要完成最新信息核查，还需要助手具备可用的联网搜索能力。本项目不单独提供聊天界面或模型服务。

先下载仓库 ZIP 并解压，或使用 Git：

```bash
git clone https://github.com/yunheliu68-ux/offer-selection-skill.git
cd offer-selection-skill
```

### macOS / Linux

在仓库目录中，选择你使用的客户端，执行对应的一条命令：

```bash
# Codex
./install.sh --platform codex

# Claude Code
./install.sh --platform claude-code
```

### Windows

使用 PowerShell 7+，在仓库目录中执行对应的一条命令：

```powershell
# Codex
pwsh -File .\install.ps1 -Platform codex

# Claude Code
pwsh -File .\install.ps1 -Platform claude-code
```

安装后，在客户端刷新技能或开启新会话，再调用该技能。

WorkBuddy 提供实验性安装入口：macOS / Linux 使用 `./install.sh --platform workbuddy`，Windows 使用 `pwsh -File .\install.ps1 -Platform workbuddy`。目前已确认安装与技能发现，**当前版本的真实调用和参考文件加载仍待验证**。完整记录见 [兼容性说明](COMPATIBILITY.md)。

更新时获取仓库最新内容，再执行原安装命令。安装器会检查目录是否由它管理，拒绝覆盖不属于它的已有目录。

## 使用前了解

当前为 **v0.3.2 RC（候选版本）**，欢迎试用和反馈，尚未达到正式稳定版的验收要求。它辅助你整理证据、判断取舍，不能保证就业、录取、签证或投资回报。关键资格与政策应以学校、雇主及主管机构的最新官方信息为准。

不需要提供姓名、学号、邮箱或完整 Offer 信件。技能指令要求联网检索时排除私人信息；你使用的 AI 平台如何保存和处理对话，仍取决于该平台。详见 [隐私说明](PRIVACY.md)。

## 进一步了解

更多 [决策示例](examples/README.md) · [决策理念](docs/DECISION_PHILOSOPHY.md) · [架构说明](docs/ARCHITECTURE.md) · [兼容性](COMPATIBILITY.md) · [发布状态](RELEASE_STATUS.md)

欢迎通过 Issues 反馈使用问题；参与修改前请阅读 [贡献指南](CONTRIBUTING.md)。项目采用 [MIT License](LICENSE)。

# Offer Selection Skill

**全网首个硕士留学 Offer 选择 Agent Skill，基于个人背景、职场规划与 ROI，倒推最适合你的 Offer。**

## 拿到 Offer 之后，怎么选？

同一组 Offer，对不同背景和目标的人，价值可能完全不同。Offer Selection Skill 结合你的职场规划或学术深造目标，判断各项目能带来哪些实际机会，以及是否值得付出相应的学费、生活费和时间。

支持 Codex、Claude Code、WorkBuddy 等 AI Agent 的本地技能安装。

## 快速开始

使用支持本地 Skill 的 AI Agent，并开启联网搜索。

### 安装

在 AI Agent 对话框中发送：

```text
请帮我安装这个仓库中的 offer-selection-skill：https://github.com/NextVariable/offer-selection-skill
```

按 AI Agent 的提示授权，安装完成后新建对话。无法自动安装时，可按 [安装说明](docs/INSTALLATION.md) 手动安装。

### 在 AI 聊天框开始使用

在新会话中发送：

```text
请使用 offer-selection-skill，帮我比较硕士 Offer。
```

如果提供的信息不足以判断，助手会追问需要补充的关键背景。

## 它会帮你看什么？

| 你在纠结什么？ | 它帮你判断什么？ |
| -------------------- | --------------------------------------------- |
| 想回国去私企，哪个 Offer 更适合？ | 结合你的学历、实习和技能，判断项目能否补上目标岗位需要的短板，以及你能否赶上招聘和实习窗口 |
| 想进国央企或体制内，应该怎么选？     | 核查目标岗位的专业、学历等报考或招聘条件，先判断是否符合要求，再比较项目价值        |
| 想留当地工作，也想保留回国退路？     | 分别分析当地就业与回国就业的可行性，比较语言、工作权限、招聘机会和转向成本         |
| 想继续学术深造，哪个硕士更有帮助？      | 判断项目能否提供与你研究目标相关的训练、研究成果、导师支持和推荐信机会           |
| 更贵的 Offer，值得多花这笔钱吗？  | 比较多付出的总成本能换来什么，以及这些机会对你是否有用、是否可达、是否承担得起       |

## 提供背景与完整示例（可选）

如果希望一次提供完整背景，可以参考：

```
本科背景：院校、专业、成绩
已获 Offer：学校、项目全名、入学年份
目标：行业、岗位，以及回国、留当地或学术深造的计划
经历：实习、科研，以及具体工作或成果
预算：理想总预算和最高可承受金额
求职准备：相关技能、简历和面试准备情况

最纠结的问题（可选）：你希望重点比较的取舍
```

学费、学制、课程和政策等公开信息由助手查证；你实际获得的奖学金、Offer 接受截止日期等个人录取条件，请自行补充。

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

## 使用前了解

当前为 **v0.3.2 正式版**。建议用于辅助决策，关键资格与政策请以最新官方信息为准。详见 [发布状态](docs/RELEASE_STATUS.md)。

无需提供姓名、学号、邮箱或完整 Offer 信件。对话数据的保存与处理取决于你使用的 AI 平台，详见 [隐私说明](docs/PRIVACY.md)。

## 进一步了解

[安装与更新](docs/INSTALLATION.md) · [决策示例](docs/examples/README.md) · [决策理念](docs/DECISION_PHILOSOPHY.md) · [架构说明](docs/ARCHITECTURE.md) · [兼容性](docs/COMPATIBILITY.md)

使用问题欢迎通过 Issues 反馈。贡献请参阅 [贡献指南](docs/CONTRIBUTING.md)，项目采用 [MIT License](LICENSE)。

---

# Offer Selection Skill — English

**The first Agent Skill on the web for choosing overseas master's offers, working backward from your background, career plans, and ROI to find the most suitable offer.**

## How do you choose after receiving offers?

The same offers can have very different value for people with different backgrounds and goals. Offer Selection Skill assesses the opportunities each programme can realistically provide for your career or academic plans, and whether they justify the tuition, living expenses, and time required.

Local skill installation is supported for AI agents including Codex, Claude Code, and WorkBuddy.

## Quick start

Use an AI agent that supports local skills and enable web search.

### Install

Send this message to your AI agent:

```text
Please install offer-selection-skill from this repository: https://github.com/NextVariable/offer-selection-skill
```

Follow the agent's permission prompts and start a new conversation after installation. If automatic installation is unavailable, follow the [installation guide](docs/INSTALLATION.md).

### Start using it in your AI chat

Send this in a new conversation:

```text
Please use offer-selection-skill to compare my postgraduate offers.
```

If the information is insufficient for a decision, the assistant will ask for the missing background that matters.

## What does it assess?

| Your question | What the skill assesses |
|---|---|
| Which offer best supports returning to China for private-sector employment? | Whether the programme closes gaps for your target role given your education, internships, and skills, and whether you can access recruitment and internship windows. |
| Which offer supports employment in state-owned enterprises or the public system? | The target role's subject, degree, and other eligibility requirements, before comparing programme value. |
| Can I work locally while keeping a China-return fallback? | Local and China-return employment feasibility separately, including language, work access, recruiting opportunities, and switching costs. |
| Which master's programme helps further academic study? | Relevant research training, outputs, supervisor support, and recommendation opportunities. |
| Is a more expensive offer worth the extra cost? | What the additional total cost buys, and whether those opportunities are useful, accessible, and affordable for you. |

## Background template and full example (optional)

To provide your background in one message, use:

```text
Undergraduate background: institution, major, grades
Offers received: institution, full programme name, intake year
Goals: industry, role, and plans for China return, local employment, or academic study
Experience: internships, research, and specific responsibilities or outputs
Budget: preferred total budget and absolute affordability ceiling
Recruiting readiness: relevant skills, résumé, and interview preparation

Main concern (optional): the tradeoff you most want to compare
```

The assistant researches public information such as tuition, duration, curriculum, and policies. Please supply your personal offer terms, including scholarships actually awarded and acceptance deadlines.

<details>
<summary>View a complete example prompt</summary>

This background is fictional. Replace it and the bracketed content with your actual circumstances.

```text
Please use offer-selection-skill to compare these postgraduate offers.

My background:
A computer science undergraduate degree from a mainland Chinese 985 university, with an average grade of 86.

Internships:
1. Software development at [company/industry, duration], mainly building internal tools; I independently owned a complete project.
   My responsibilities and results: [what I did, what I delivered, actual impact]
2. Product management at [company/industry, duration], helping build an AI agent product from zero to one.
   My responsibilities and results: [stages owned, deliverables, launch or user feedback]

Research/projects:
[Research area or project, my responsibilities, specific outputs; write none if applicable]

My offers:
A: [institution, full programme name, intake year]
B: [institution, full programme name, intake year]
Both are formal admissions offers, with no scholarships currently awarded.

My goals:
Return to China for a product manager role after graduation. Employment is the priority; further academic study is not currently planned.
No clear city preference.

My budget and readiness:
Preferred total budget: RMB 800,000. Absolute affordability ceiling: RMB 1,000,000.
I can prepare for recruiting early, but need to improve product interviews, case presentation, and how I communicate project outcomes.

What I most want to understand:
Which gaps can each programme close?
If one costs more, what does the extra spending buy?
How do intake dates, graduation dates, and course schedules affect eligibility and timing for Chinese autumn recruitment, internships, and graduate hiring?
Are the programme's internship opportunities realistically accessible given my background and goals?
```

</details>

## What will you receive?

A recommendation tailored to your circumstances: which offer to prioritise, the decisive reasons, the value of additional spending, major risks, and conditions to verify before accepting.

The analysis may also conclude that two programmes have no material difference, that critical conditions need verification, or that none of the offers is worth accepting. It does not force a ranking just to name a winner.

## Before using the skill

The current release is **v0.3.2**. Use it to support decisions; verify critical eligibility requirements and policies against current official sources. See [release status](docs/RELEASE_STATUS.md).

You do not need to supply your name, student ID, email, or a complete offer letter. Conversation storage and processing depend on your AI platform. See [privacy](docs/PRIVACY.md).

## Further reading

[Installation and updates](docs/INSTALLATION.md) · [Decision examples](docs/examples/README.md) · [Decision philosophy](docs/DECISION_PHILOSOPHY.md) · [Architecture](docs/ARCHITECTURE.md) · [Compatibility](docs/COMPATIBILITY.md)

Report usage problems through Issues. See the [contribution guide](docs/CONTRIBUTING.md). The project uses the [MIT License](LICENSE).

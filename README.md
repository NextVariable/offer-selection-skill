# Offer Selection

**Domain-Specific Decision Harness for Postgraduate Offer Selection**

已经拿到硕士 Offer 时，Offer Selection 帮你判断哪个项目值得接受，或是否应该保留其他选择。它以 **Agent Skill** 分发，正式支持 **Codex CLI**。当前稳定版为 [v2.0.0](https://github.com/NextVariable/offer-selection-skill/releases/tag/v2.0.0)，项目进入维护模式。

## 核心能力

评估路径覆盖回国私企、国央企及体制内、留当地就业和博士深造。

- **毕业画像推演（Graduation Profile Transformation）**。逐项比较每个项目能带来的增量，包括能力、经历、学历信号和可进入的招聘或研究机会。
- **资格、成本与风险**。逐 Offer 核查目标路径的资格与窗口，比较总成本、资金压力、机会成本及条件变化。
- **研究与报告**。区分已核实事实、经验先验与待核实事项。Quick Decision 给出方向、主要风险和翻转条件；Full Decision Audit 在同一决策基础上展开证据。
- **多目标与反事实**。双轨目标分别评估。改变预算或目标后，可以比较结论及变动原因，原始背景仍作为基准。

## 快速开始

在已安装 Codex CLI 的 macOS 或 Linux 上，从正式标签安装：

```bash
git clone --branch v2.0.0 --single-branch https://github.com/NextVariable/offer-selection-skill.git
cd offer-selection-skill
bash maintenance/install.sh --platform codex
```

安装后开启一个新的 Codex 会话。完整流程需要 Python 3.10+、本地工作目录写入权限和联网研究能力。[Windows 与其他安装方式](docs/INSTALLATION.md#安装-v200)

## 使用示例

在新会话中输入下面这段话，将方括号替换为实际信息：

> 请用 $offer-selection-skill 比较 [学校与项目 A] 和 [学校与项目 B]，都是 [入学年份] 入学。我本科读经济学，有一段市场实习，首选回国做产品运营，也想知道各项目的当地就业机会。目标预算 35 万元，绝对上限 45 万元。请先给 Quick Decision。

补充与你的决策有关的信息，例如成绩、科研或求职准备、已获奖学金及接受截止日期。项目费用、课程、政策和公开招聘资格由 Agent 自行核查。看完快速建议后，可以继续问「请给我 Full Decision Audit」或「如果绝对预算上限降到 38 万元，建议会怎样变化？」

[可复核的公开合成案例](docs/examples/README.md)

## 决策方法

先明确你目前的起点、目标和主要差距，再推演接受每份 Offer 后的毕业画像。资格决定能否进入目标招聘或研究路径；在可行的路径上，再比较毕业时的竞争力、成本回报和风险。项目排名、城市资源与校友网络的价值取决于目标市场和你的实际可及性。就业结果接近时可以保留并列；目标有关键缺口时可以给出有条件建议，或建议暂不接受任何 Offer。[决策方法说明](docs/DECISION_PHILOSOPHY.md)

## Harness 架构

| 层级 | 职责 |
|---|---|
| Agent Skill | 提供领域规则、研究方式和报告约定 |
| 宿主 Agent | 对话、打开原始来源、核实主张、推演毕业画像并判断竞争力 |
| 本地 Decision Harness | 记录逐 Offer 的研究任务、证据、覆盖范围和检查点，支持中断恢复及独立反事实 |
| 决策校验 | 检查资格状态、成本、建议一致性，并生成同源 Quick / Full 报告 |

Harness 是项目自带的可选 Python 执行层，只使用标准库，执行范围限于硕士 Offer 决策流程。模型调用和网页访问由宿主负责。[架构说明](docs/ARCHITECTURE.md)

## 版本演进

- **v0.3.x** 建立以目标、毕业画像和资格为核心的领域规则。
- **v1.0.0** 加入结构化证据、成本与资格校验、Quick / Full 和反事实。
- **v2.0.0** 加入逐 Offer 研究覆盖、可恢复的研究状态和可审计的 Harness 执行记录。[版本历史](docs/CHANGELOG.md)

## 兼容性与已知限制

**Codex CLI** 是正式支持宿主，指定公开合成案例已有原生联网验收与正式标签安装后的冒烟验证。Claude Code 的安装兼容性有历史记录，v2 原生端到端尚未运行。TRAE、WorkBuddy 和其他宿主为实验性支持，已验证范围见[兼容性](docs/COMPATIBILITY.md)。

本地程序可检查证据记录的结构、范围和适用期。网页是否支持具体主张，需要 Agent 或审查者读过原文后判断。案例验收只覆盖明确记录的流程；实际招聘、签证与升学仍取决于具体条件。[已知限制](docs/KNOWN_LIMITATIONS.md)

申请评估只需提供决策相关背景。分享前请移除姓名、学号、联系方式及录取信上的身份信息。[隐私说明](docs/PRIVACY.md)

## 文档与许可

[文档索引](docs/README.md)汇总安装、架构、隐私、维护、历史发布和验收记录。项目采用 [MIT License](LICENSE)。

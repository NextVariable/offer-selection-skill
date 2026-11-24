# v2.0 发布收口复核

2026-11-24 从 [PR #4](https://github.com/NextVariable/offer-selection-skill/pull/4) 的 `842423095743d8d994635815ca94dd3d4b951ce2` 开始。该 SHA 的 push 和 PR CI 各通过四项。本页记录本次独立复核。新提交的检查以 PR 当前 Head 为准。

## 已有案例

| 运行 | 独立复核 |
|---|---|
| Codex CLI 原生，Bristol / Manchester | 检查了归档的两阶段记录、94 条执行事件和逐 Offer 覆盖。Bristol 2027 国际学费 £34,500；Manchester 的 £37,500 对应官网的 Business Analytics and Artificial Intelligence，录取名称映射仍待招生方确认。两校具体岗位和学历资格没有证实。预算 45 万时有条件考虑 Bristol，前提是锁定总支出并核实资格；42 万时按同一组规划区间暂缓两校。原案未变。 |
| TRAE 回退，Warwick / Glasgow | 官网支持两个营销项目的 2027 学费 £39,500 / £34,815。两校学费加同一假设生活费分别为 £54,500 / £49,815。绝对上限从 £56,000 调为 £53,000 后，Warwick 的预算 Gate 失败，Glasgow 通过。冻结夹具里入学 Gate 已给定；证据支持公开入学要求，不能证明 IELTS 单项、个体录取或中国雇主资格。以 Glasgow 为条件性默认符合该成本差异及雇主增益仍未知的输入。 |

项目与费用复核来源为 [Bristol](https://www.bristol.ac.uk/study/postgraduate/taught/msc-business-analytics/)、[Manchester](https://www.manchester.ac.uk/study/masters/courses/list/22043/msc-business-analytics-and-artificial-intelligence/all-content/)、[Warwick](https://www.wbs.ac.uk/courses/masters/marketing-and-strategy/) 和 [Glasgow](https://www.gla.ac.uk/postgraduate/taught/internationalstrategicmarketing/)。官方费用页无从确认个人最终净成本。已归档原生证据属于一个回国私企案例，其他职业路径保留离线证据。本轮复核未新增原生模型运行或人类 oracle 签字。

## 可复现缺陷及收口

- 普通 POSIX 权限下新状态是 `0644`。现以私有临时文件原子替换，状态写入权限为 `0600`。
- 已过期状态在报告失败后仍保留个人背景。现在读入后先保存清除结果，再运行命令。
- 「等价后择一」曾能跳过未入选比较对象的必需资格。现在检查所有比较对象；直接推荐继续检查所选 Offer。

只复跑现有测试和针对上述缺陷的回归。最终候选在本地通过 164 项单元测试和 37 项安装检查。发布范围拟限定为 Codex CLI，维护者签核与发行授权见[签核清单](RELEASE_CHECKLIST_V2.md)。

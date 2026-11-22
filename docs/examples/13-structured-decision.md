# 多 Offer 决策与预算反事实

在装好技能并允许联网的 Agent 中发：

> 用 Offer Selection Skill 比较这两份录取。我的本科、实习和求职准备如下：〔填写〕。A/B 的正式项目名及入学年份是〔填写〕。目标是留当地做数据分析，同时保留回国备选。理想总预算和绝对现金上限是〔填写〕。奖学金和付款期限以我的录取信为准。先给 Quick Decision，再比较上限降低后的情境。请主动核实公开信息，保留未知项的条件分支。

需要逐项复查时，说「继续给 Full Decision Audit，沿用同一份结论和证据」。可额外请求
JSON，复核每条资格、成本分项、来源适用期和相关路径。正式资格仍以对应机构文件为准。

典型的现金流差异：A 全程支出 66 万、奖学金 12 万，净支出 54 万。注册当天要交
35 万，届时只有 30 万，奖学金注册后才到账，且无法延期或分期。A 的总额在
65 万硬上限内，但当天有 5 万缺口。B 花费 58 万，付款可安排。程序能够验证
这个差别。B 是否值得读仍取决于可达项目、招聘渠道和相对当前背景的职业增量。

在有 Python 的宿主，可用 [结构化交换说明](../../skills/offer-selection-skill/references/structured-workflow.md)
核对 Agent 生成的文件。以下从技能目录执行，`case.json` 是已脱敏的本地案例：

```text
python3 scripts/decision.py plan case.json
python3 scripts/decision.py check case.json
python3 scripts/decision.py verify case.json decision.json
python3 scripts/decision.py report case.json decision.json --mode quick
python3 scripts/decision.py report case.json decision.json --mode full
python3 scripts/decision.py scenario case.json change.json
python3 scripts/decision.py compare case.json change.json decision.json after.json --why "解释决定性变化"
```

其中 `change.json` 可写 `{"field":"ceiling","value":50000000}`，表示按 CNY 最小单位的
50 万人民币。情境只改上限，仍适用的课程、招聘与政策事实可以复用。不要把改后的
数值保存回真实背景。

可直接运行的虚构数据：[case JSON](offer-demo.case.json) 和
[decision JSON](offer-demo.decision.json)。从仓库根目录运行：

```text
python3 skills/offer-selection-skill/scripts/decision.py report docs/examples/offer-demo.case.json docs/examples/offer-demo.decision.json --mode full
```

# v1.0.0 发布硬化审计

审计日期：2026-11-22。基线：PR #3 的公开 head `0115198`（`codex/v1-decision-engine`）。本文件只记录本轮实际执行的工作与证据状态，不宣布正式发布。

## 1. 基线状态

| 项目 | 结果 |
|---|---|
| 公开分支 head | `0115198`，PR #3，草稿，未合并 |
| 离线确定性测试（基线） | 66 passed |
| 安装器安全测试（基线） | 37 passed / 0 failed |
| 前端版本一致性（基线） | PASS，版本 `1.0.0` |
| 原生 Claude Code / Codex 行为回归（本轮） | **Not Run**（无可复现的原始宿主会话） |

已实现并有机械证据：结构化 case/decision、证据状态与适用期、硬门槛、全成本与现金流、分类压力、单变量反事实、双报告。
尚未由本轮证明：宿主 Agent 一定按 Skill 契约调用引擎；原生宿主在真实研究循环中的行为。

## 2. 六个 Partial 案例

归档对照 `evals/rounds/v100-production/judgment.json` 中，跨两个版本至少一个维度为 partial 的正好是 6 个案例。归档记录没有保存 PR 摘要所称「4 pass / 6 partial」的逐案清单，因此该聚合数字**不可精确复现**；本轮按逐案记录重建。

| 案例 | 归档 partial 维度 | 确认的根因 | 本轮修复 |
|---|---|---|---|
| a1 | 总成本与剩余预算不可操作 | 成本行 `amount` 上界为空；报告只给方法，未暴露未量化行 | Quick 增加费用与预算段：净现金区间、上限比较、余量/超出、未量化行 |
| a3 | IANG 续签未回答；加速与招聘窗口不可执行；缺直接链接 | 案例包没有「续签」研究项；输出未把已知链接全部露出 | `path-local-stay.md` 明确初次许可不等于后续许可；Quick 列出全部未确认项及影响 |
| a4 | 回复缺少费用表来源 | 来源在案例包内，但回复未引用 | 已核验来源由决策结果统一渲染；未通过原文支持核验的主张进入「待核实」 |
| b1 | defer 未比较 CPT/OPT、招聘与成本机制 | 研究包缺少可比的量化成本与机制结论；报告只显示闸门 | Quick 显示成本上界缺口、付款节点状态和逐项未确认影响 |
| b2 | 旧项目名确认未变成行动；缺最强来源与 Skilled Worker 机制 | 输出契约未强制「结论即验证动作」；来源未全部露出 | SKILL 输出契约要求对每个关键/重要未决项写明待核主张与可裁定权威 |
| b3 | 未覆盖 LSE 后续获资助分支；缺 £43,100 学费锚点 | 条件分支与费用锚点未进入 Quick | Quick 统一显示费用、预算口径与原翻转条件；SKILL 要求保留条件分支 |

这些修复改的是报告完整性、来源露出与执行契约，不改硬门槛、评分、权重或推荐逻辑。

## 3. 硕士/博士预算回归

归档的 `host-claude/input-and-decisions/case.json` 没有 `horizon`，Warwick 费用行按六年总额录入（`warwick_tuition` 150–157 万，`warwick_living` 294–370 万）。因此该文件记录的是**已经出错的编码结果**，不是原始用户输入；没有原始会话时，无法从该文件本身复现 Claude 的失败决策过程。该案例保留为失败证据，不作通过证据。

可复现的重建在 `stage-holdout/`，使用 `horizon:"masters"` 与显式 `stage` 标签。本轮新增覆盖：

- 单独硕士项目；
- 硕博连读项目；
- 仅硕士阶段上限；
- 全项目上限；
- 博士资助未确认；
- 付款节点与奖学金到账时点；
- 上限变化后的反事实仍保持 `masters` 口径并排除博士行。

测试位于 `maintenance/test_decision_engine.py` 的 `BudgetCases`、`HostContractCases`，通过 CLI `check`、`scenario` 调用，而不只调用 Python 函数。

## 4. 十案例回放

对 `evals/rounds/v100-production/e2e/case-{a1,a2,a3,a4,b1,b2,b3,c1,c2,c3}` 逐案执行当前引擎的 `verify`、`report --mode quick`、`report --mode full`：

- 10/10 通过 `verify`；
- 10/10 Quick 成功生成；
- 10/10 Full 成功生成，且 Full 以 Quick 为前缀；
- b2 的 `compare` 也以 0 退出。

这是对已归档研究的**重放**，不是重新做十次公开研究。公开事实核验状态：

- 归档的独立来源复核（2026-11-22）覆盖 7 条主张：6 条完全支持，1 条仅历史版本支持（Imperial 当前页 403），并修正 1 处 locator（BOC 应为 III.B.2）。
- 本轮重新打开并核对英国 Graduate route：GR 8.1 表明确「2027-01-01 起申请为 18 个月，之前为 2 年」，与 b2 主张一致。
- CUHK MiM 费用页的 fees 标签本轮被站点安全检查拦截，`HK$435,000` 未在本轮重新确认，保持 Unresolved。
- 其余来源本轮 **Not Re-run**，沿用归档记录，不据此新增确认。

## 5. 报告与 UX

- Quick 新增「费用与预算」：按预算口径显示每份 Offer 的净现金区间、上限/目标状态、余量或超出、未量化的成本行、未核对付款节点、被排除的博士行。
- Quick 新增「待核实」：列出被决策引用的未确认主张、范围与影响级别；确认但来源未通过支持性核验的主张也在此出现。
- 两模式继续共享同一份已验证 decision；Quick 不得省略会改变结论的事实。
- 普通用户不需要操作 JSON 或 Python；脚本只作为 Agent 内部校验工具。

## 6. 发布检查

| 检查 | 结果 |
|---|---|
| `python3 -m unittest discover -s maintenance -p 'test_*.py'` | 78 passed（73 引擎 + 5 发布契约） |
| `maintenance/test_installer.sh` | 37 passed / 0 failed |
| `maintenance/check_frontmatter.py` | PASS |
| manifest JSON 解析 | PASS |
| 版本一致性（plugin/SKILL/install.sh/install.ps1） | PASS |
| 发布契约、隐私、绝对路径、密钥扫描 | PASS（本地） |
| `python3 -m compileall` | PASS（本地） |
| GitHub Actions 实跑 | **Not Run**（本轮未推送触发） |

发布契约测试覆盖：版本单源、RELEASE_STATUS 仍为候选、无本机绝对路径、无私钥/常见令牌、`decision.py` 仅标准库导入。

## 7. 仍未解决的发布问题

1. 原生 Claude Code / Codex 回归未重跑；不能用 Python 测试替代宿主行为通过。
2. 原始 Claude 失败会话不可得，只能以重建 holdout 证明引擎口径；主机是否稳定设置 `horizon` 仍待实跑。
3. 十案例是归档重放，未重新检索全部公开来源；部分 2027 费用与政策仍保持 Unresolved。
4. GitHub Actions 与人工行为验收尚未执行。
5. Quick 仍依赖案例包中真实存在的证据；研究遗漏只能被显式列为待核实，不能被报告自动补全。

## 8. 审核建议

建议进入 Codex 独立复核，重点检查：预算口径与排除逻辑、Quick/Full 一致性与完整性、六个 partial 的契约修复是否足以支撑行为复跑、以及发布契约测试是否覆盖真实发布边界。

在原生宿主复跑、CI 实跑和人工行为签字完成前，不应合并 PR #3，也不应宣称 Stable 已发布。

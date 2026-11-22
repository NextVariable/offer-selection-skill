# v2.0 独立审核报告（Harness）

- 审核对象：PR #4，head `d926f202d9abd8a3cdea8308598e8e07e2774851`
- 审核分支：`audit/v2-independent`（从上述 head 拉出，保留 TRAE 原提交）
- 基线：v1.0.0 Stable（`fcd2ff6`）
- 日期：2026-11-23
- 结论：**NO-GO（暂不允许推进为正式 RC）**。代码级审核发现的三类问题已修复并通过回归；但原生 Codex CLI 端到端验收因模型额度 `402 Insufficient Balance` 无法完成，且修复提交尚未进入 PR #4。

本报告只写实际执行过的检查。未执行的运行明确标为 Not Run / Not Measured。

## 1. 审核方法与边界

- 完整读取 PR #4 差异中的 `harness.py`、`decision.py` 调用面、研究任务、工具契约、证据状态、决策失效、checkpoint/resume、scenario、trace、隐私、安装器、CI 与发布契约。
- 用独立 Python 探针复现可疑行为，再补回归；不以现有测试通过作为结论。
- 未修改 `decision.py`。八阶段、Gate、预算、Score、Quick/Full 仍由 v1 引擎唯一拥有；Harness 只增加执行状态。未发现第二套互相冲突的决策逻辑。
- 原生宿主尝试使用 Codex CLI 0.58.0（`npx @openai/codex`）与 Claude Code 2.1.322，均为真实安装/真实进程，不是 CLI 模拟。

## 2. 三个重点缺陷的结论

### A. 隐私生命周期：确认缺陷，已修复

**审核前事实**

- 7 天保留期只把 `expired` 置为 true 并给出建议，**不会产生删除**。
- `privacy --purge` 只清 `case.profile` 和 scenario 副本；`trace`、证据主张、决策文本不会被扫描。
- 崩溃可能留下 `<state>.tmp`，其中含上一版完整状态。

**修复**

- `privacy()` / `status` / `resume` 在到期后首次访问时调用 `enforce_retention`，真正清空 base 与 scenario 的 `profile`，写入 `privacy_retention_expired`，并更新已存 Decision 的 case digest，使既有报告仍可渲染。
- `--purge` 统一走 `_purge_profiles`，记录 `privacy_purge`。
- `load_state` 成功读取后删除残留的 `<state>.tmp`。
- 文档收窄为真实能力：清除范围是 `profile` 及其副本；证据主张、URL、决策理由和 trace 自由文本不会自动改写，宿主不得把身份信息写进这些字段。

**边界**：这不是全盘脱敏。若宿主把姓名或成绩写入 claim 文本，删除 profile 后仍会保留；文档已明确说明。

### B. State Recovery：确认 4 个缺陷，已修复

| 缺陷 | 审核前行为 | 修复 |
|---|---|---|
| digest 不一致仍清 stale | `resume` 只看 `decision.validate`；Case 被外部修改但校验仍通过时，`stale` 被错误清为 false，`report` 却因 digest 不符拒绝 | 只有 validate 通过**且** case digest 与存储值一致才清 stale；`status` 也按 digest 计算有效 stale |
| 证据降级后无任务可做 | `resume` 降级证据后不重规划，`next` 直接 `research_complete`，但旧决策已 stale | `resume` 调用 `plan_tasks`，为失去确认的证据重建任务并把 phase 置回 `research` |
| 瞬时 blocked 永久卡死 | 断网/额度不足重试 3 次后 `blocked`，`resume` 不重置 attempts，无法继续 | 记录 `blocked_reason`；`resume` 重开 `tool_error` / `tool_blocked` / `partial_result` / `unopened_source`，矛盾证据保持 blocked |
| 检查点不一致不可见 | checkpoint 只是 id 列表，无 digest；resume 不报告漂移 | checkpoint 记录 case digest；`resume` 返回 `checkpoint_drift`（失去确认的证据、新增开放任务） |

**边界**：checkpoint 仍是审计标记，不是回滚快照。`resume` 始终核验当前文件，不会静默回到旧状态；文档已改名说明。

### C. Research Coverage：确认结构性缺口，已加诊断但未完全解决

**审核前事实**：`plan_tasks` 完全由 Case 中已声明的 Gate/证据生成。若 Agent 根本没有为某条路径创建对象，Harness 看不到缺失，任务全 Done 后会报告 `research_complete`。用 SOE Case 删除全部 Gate 复现：只生成 programme 任务，credential/timing 不存在。

**修复（诊断，不是新 Gate）**

- 新增 `coverage(state)`，按 active path 对照由 core Gate 段落和四个 path 文件推导的类别清单：
  - private：credential / eligibility / market / cost
  - soe：credential / eligibility / timing / cost
  - local：work / market / access / cost
  - phd：academic / programme / cost
- 输出 `missing`（Case 完全没声明）与 `unconfirmed`（声明了但没有 confirmed 证据或已决 Gate）。
- 出现在 `plan` 的 trace、`next` 返回、`status.coverage` 和 `store_decision.coverage`。
- **不创建任务、不阻断推荐、不改变 Gate 或 Score**，避免引入第二套领域规则。

**边界**：它只能发现“路径级类别缺失”，不能证明某个具体岗位/项目所需的隐藏条件。要强制覆盖，必须把“required research contract”变成 Case 输入或由 core 拥有机器可读清单——这属于领域方法变更，本轮未擅自实施。

## 3. 原生宿主验收

### 3.1 Codex CLI

- 真实安装：`install.sh --platform codex` 到隔离 `HOME`，确认 `scripts/harness.py` 与 `decision.py` 同时安装，版本 `2.0.0-rc1`。
- 真实启动：Codex CLI 0.58.0，配置 OpenAI-compatible DeepSeek provider，执行自然语言入口。
- 结果：Codex 启动、注册会话、发起模型请求；DeepSeek 返回 `402 Insufficient Balance`，5 次重试后退出。
- **未能进入技能读取和工具调用阶段，因此无法确认 Codex 实际调用 `harness.py`。**
- 状态：**Not Run（环境阻塞：模型额度）**，不是代码失败。

### 3.2 Claude Code

- `claude -p` 真实启动，返回 `API Error: 402 Insufficient Balance`。
- 状态：**Not Run（同一环境阻塞）**。

因此用户要求的六个原生场景（私企多 Offer、SOE 门槛、当地工作许可、PhD、预算反事实、中断恢复）均未在原生宿主完成；不能用离线测试或回退运行替代。

## 4. v1 / v2 对照

同一份冻结研究资料、同一模型输入不可得（402），所以以下只比较**确定性执行控制**，不比较模型判断质量。

| 指标 | v1.0 | v2.0 audit |
|---|---|---|
| 过期资格证据 | `decision.audit` 不改状态；`validate` 仍接受推荐 | `verify_evidence` 降级为 unresolved；`store_decision` 拒绝推荐 |
| 无支持来源 | `audit` 可降级 | 同样降级，并传播到 Gate |
| 反事实隔离 | `decision.scenario` 返回副本 | 命名 scenario + base digest 校验；base 变化后 scenario 标 stale |
| 中断恢复 | 无状态，Not Supported | checkpoint/resume；瞬时 blocked 可重试；已完成任务保留 |
| 工具调用数（冻结回放） | 0 个研究记录；1 次 validate + 2 次 render | 2 个工具结果、1 次证据检查、1 次 decide、2 次 render |
| 本地回放耗时 | 1.03 ms | 1.31 ms |
| Token 使用 / 模型耗时 | **Not Measured** | **Not Measured** |

关键对照用例：把两个项目的资格来源访问日期改为 2020 年。v1 `audit` 仍保留 `confirmed` 并通过 `validate`；v2 将其降级为 `unresolved` 并阻断推荐。该行为已固化为 50 项 Harness 测试之一。

注意：本地回放毫秒数不代表真实模型运行成本；v2 的 2 个工具结果来自同一份冻结数据，真实联网调用数未测。

## 5. 回归与工程检查

在 `audit/v2-independent` 上执行：

| 检查 | 结果 |
|---|---|
| v1 决策引擎 | 78 passed |
| v2 Harness | **50 passed**（新增 9 项审核回归） |
| 发布契约 | 10 passed（含 `harness.py` 安装与仅标准库导入） |
| 安装器安全 | PASS=37 FAIL=0 |
| Frontmatter | PASS（2.0.0-rc1） |
| GitHub Actions `ci`（Linux 3.10/3.12、macOS、Windows） | **success**（运行 45048388128） |
| `py_compile` / `git diff --check` | 通过 |

新增回归覆盖：到期自动清除、digest 不一致、证据降级后重规划、瞬时 blocked 重试、checkpoint 漂移、scenario stale、四路径覆盖诊断、`.tmp` 清理、CLI 中断恢复、v1/v2 过期资格对照。

CI：<https://github.com/NextVariable/offer-selection-skill/actions/runs/45048388128>（audit head `e8ebba3`，三个作业全部 success）。

## 6. 剩余问题

- **P0（环境/发布门槛）**：原生 Codex / Claude Code 端到端未完成，模型额度 402。必须用可用额度重跑，并保留“Codex 实际执行 `harness.py`”的 trace 或 shell 日志。
- **P1（交付）**：审核修复只在 `audit/v2-independent`，PR #4 head 仍是 `d926f20`。正式 RC 前需把审核提交带入 PR #4，或明确以本分支为新候选。
- **P1（覆盖）**：覆盖诊断依赖 Case 已声明的对象，不能证明未声明主题确实不需要；当前只提示、不阻断。若要“未研究即不得推荐”，需产品层决定是否引入 required-research contract。
- **P1（语义）**：来源是否真正支持主张仍需模型/人工复核，`semantic_review_required` 只是标记，没有复核记录闭环。
- **P2（恢复）**：状态文件损坏时没有备份/恢复；多进程并发写未测试。
- **P2（成本）**：真实 token、费用、工具调用次数和模型耗时未测。

## 7. 是否允许推进为正式 RC

**不允许（NO-GO）**。

最小阻碍，按顺序：

1. 用有额度的模型在 Codex CLI 原生环境跑通至少一个完整流程，并证明 `harness.py` 被真实调用；Claude Code 至少完成一次同类验证。
2. 将本审核分支的修复纳入 PR #4（当前 head 不含这些修复），重跑 78 + 50 + 10 + 37。
3. 明确覆盖策略：接受“诊断不阻断”的已记录限制，或由产品决策引入 required-research contract。

满足 1-2 且对 3 作出明确书面决定后，可给 GO。当前不具备这三个条件，因此 PR #4 应保持 Draft，不合并 `main`，不创建 Stable Release。

# v2.0 RC 验收报告

- 分支：`feat/v2-decision-harness`
- 基线：v1.0.0 Stable（`fcd2ff6`）
- 版本：`2.0.0-rc1`，`release_status: candidate`
- 日期：2026-11-23
- 结论：**工程范围达到 RC 候选（RC candidate），并通过 Codex CLI 原生端到端自测**。Codex CLI 的 v2 流程已于 2026-11-23 真实联网执行；Claude Code 原生验收仍为 **Not Run**，独立人工复核尚未进行。

本报告只记录真实存在的代码与已执行结果；未执行的项目明确标为 Not Run。

## 1. v2 架构与新增模块

v2 保留 Skill-first 分发和 v1 的单一决策引擎，只新增一个可选的本地执行层。

```text
宿主 Agent（模型、浏览器、判断）
        │  自然语言入口
        ▼
skills/offer-selection-skill/SKILL.md
        │  八阶段决策语义
        ▼
references/core-decision-engine.md  +  path-*.md  +  priors-and-calibration.md
        │  唯一的 Gate / 成本 / Score / Quick-Full 规则
        ▼
scripts/decision.py（v1，未改逻辑）
        ▲
        │ 复用 analyze / validate / render / scenario / audit
scripts/harness.py（v2，新增，965 行，仅标准库）
        │
        └─ 本地 JSON Case State + append-only trace
```

`harness.py` 只拥有“执行状态”，不拥有第二套决策规则：

| 状态 | 拥有者 | 作用 |
|---|---|---|
| Case State | harness 保存，`decision.py` 校验 | 唯一案例文档，不复制 profile/offers |
| Research Task State | harness | `hard_gate` / `decisive` / `optional`、依赖、状态、尝试次数、核实路径、停止条件 |
| Evidence State | harness + `decision.py` | Claim-to-Source、scope/period/freshness/authority、矛盾、降级传播 |
| Gate State | `decision.py` | Gate 语义、`Unknown ≠ Pass`、推荐可行性 |
| Decision State | `decision.py` + digest | 已校验决策、case digest、stale 标记 |
| Scenario State | harness | 命名的反事实，与 base case 隔离 |

模块边界：

- 宿主仍负责模型调用、联网与判断。Harness 不抓网页、不调用模型、不做领域裁决。
- 程序检查覆盖结构、范围、适用期、访问时效、权威性、依赖与算术。
- 语义支持无法由程序证明：`semantic_review_required` 可进一步记录为可审计复核（来源与定位、reviewer 类型、supported/partial/unsupported/unresolved、时间、依据、项目与届别）。任何复核都不能替代官方确认，模型复核尤其不能。
- 本地单文件 JSON，原子替换；无数据库、服务、账号或通用 Agent Runtime。

CLI 子命令：`init / plan / next / record / evidence / coverage / review / decide / report / scenario / checkpoint / resume / status / trace / privacy`。普通用户仍只用自然语言，不手工操作 CLI。

## 2. 与 v1.0 的实质差异

| 维度 | v1.0.0 | v2.0.0-rc1 |
|---|---|---|
| 分发方式 | Skill 包 + `decision.py` | 同一 Skill 包，增加 `harness.py` |
| 决策规则 | 唯一引擎 | **完全复用，未改 `decision.py`** |
| 研究任务 | 文本契约，无持久状态 | 任务分类、依赖、优先级、重试、停止条件 |
| 工具结果 | 文本说明 | `task_id/status/claims/gates/follow_up` 契约，缺 claim 或 locator 即拒绝 |
| 未研究资格 | 规则要求 Unknown ≠ Pass | 硬门槛任务未完成时**程序阻断推荐** |
| 证据时效 | 人工核对 | 自动检查访问时效、适用期、scope、权威性并降级 |
| 证据变化 | 需人工重跑 | 降级后经 `decision.audit` 传播，相关 Gate 重开，决策标记 stale |
| 中断恢复 | 无 | checkpoint / resume，保留仍有效证据并重查过期项 |
| 反事实 | `decision.scenario`，返回新文档 | 命名场景独立存储，校验 base digest 未变 |
| 隐私 | 文档建议 | 默认 7 天保留期 + `--purge` |
| 观测 | 无 | 追加式 trace + 计数 metrics |
| 测试 | 78 + 发布契约 + 安装器 | 另加 75 项 Harness 测试、冻结真实来源案例与逐 Offer 覆盖负向测试 |

没有新增 Gate、国家/学校固定分值、权重或第二条推荐链。

## 3. 已完成功能与测试证据

### 3.1 测试矩阵（本地 macOS，Python 3）

| 套件 | 命令 | 结果 |
|---|---|---|
| v1 决策引擎 | `python3 -m unittest discover -s maintenance -p 'test_decision_engine.py'` | **78 passed** |
| v2 Harness | `python3 -m unittest maintenance.test_harness` | **75 passed**（全套 163 passed） |
| 发布契约 | `python3 -m unittest maintenance.test_release_contract` | **10 passed** |
| 安装器安全 | `bash maintenance/test_installer.sh` | **PASS=37 FAIL=0** |
| Frontmatter | `python3 maintenance/check_frontmatter.py` | **PASS**（version=2.0.0-rc1） |
| 语法/导入 | `python3 -m py_compile ...`、AST 白名单测试 | **pass**；仅 `argparse/copy/datetime/hashlib/json/os/re/sys/pathlib` + `decision` |

75 项 Harness 测试覆盖研究编排、工具契约、证据核验、决策集成、场景隔离、状态与隐私、v1/v2 对照、冻结真实来源、逐 Offer 覆盖负向测试与 CLI。逐 Offer 负向测试包括：A 的确认不能覆盖 B；推荐已确认的 A 不被 B 的缺口阻断；推荐未确认的 B 被 B 自己的资格缺口阻断；成本逐 Offer 确认；Offer 级 `not_applicable` 只清除该 Offer；路径级确认不能掩盖单个 Offer。

### 3.2 覆盖的失败模式

- **漏查关键资格**：硬门槛任务未完成时 `store_decision` 拒绝推荐；已确认证据也不会自动关闭未裁决的 Gate。
- **错误引用**：decision 引用不存在或 scope 不符的证据时被 `decision.validate` 拒绝。
- **证据过期 / 越期 / scope 不符**：降级为 unresolved，重开依赖 Gate，并使已存决策 stale。
- **多 Offer 成本比较**：Warwick 5,450,000 vs Glasgow 4,981,500（GBP 便士），与 `decision.py` 算术一致。
- **用户改变职业目标**：场景内只重开受影响 Gate，base case digest 不变。
- **中途断网 / 额度不足**：`error` 重试至上限后 blocked，并输出核实路径；不会伪造完成。
- **重复执行**：相同事实 fingerprint 复用，计划幂等，已关闭任务保留。
- **反事实隔离**：`scenario` 后 base digest 不变；命名场景独立保存。
- **未完成研究就输出推荐**：被 preflight 阻断。
- **工具返回不完整数据**：缺 claim / locator / `status` 非法的结果被拒绝且不写状态。

### 3.3 Codex CLI 原生端到端（2026-11-23）

本轮在一个全新合成学生案例上执行原生 Codex CLI。输入只有自然语言背景、两个真实硕士项目、职业目标与 45 万元预算；没有预置 case、decision 或证据。

- 宿主与模型：Codex CLI `0.171.0-alpha.13`，模型 `gpt-6.1-sol`，macOS，`workspace-write` 加联网；模型接口未返回 402。
- 两进程中断恢复：第一个进程完成 intake、自动生成 Case、`init/plan`、Bristol 官网研究和 `checkpoint` 后退出；第二个进程用 `codex exec resume` 和 `harness.py resume` 从同一状态继续，漂移检查为 `detected=false`、`case_changed=false`。
- 真实来源：打开 Bristol 项目/费用/入学要求/生活费/住宿、Manchester 2027 项目页、GOV.UK 学生签证与 IHS、中国银行牌价、留服中心页面；`record` 写入 16 条工具结果。
- 逐 Offer 覆盖：`coverage` 分别输出 `offers.bristol` 与 `offers.manchester`。两校的 `cost/credential/eligibility/market` 均为 `unresolved`，没有把一校的确认结果套到另一校，也没有把 unresolved 报成 confirmed；所有缺口都带有具体核实路径和处置理由。
- 决策：公开检索到的 Manchester 2027 项目名为 *MSc Business Analytics and Artificial Intelligence*，与学生输入的 *MSc Business Analytics* 不一致；系统将其保留为 Critical 未决项，没有替用户确认 offer 映射。最终结论为 **conditional**：只有在全期净成本可锁定在 45 万元内且学历/求职资格得到确认后才考虑 Bristol；两校均未获无条件接受。
- 输出与反事实：`decide` 通过 `decision.py` 校验；Quick 与 Full 由同一决策渲染；`ceiling=420000`（42 万元）场景使方向翻转为暂缓两校，base case digest 未变。
- 轨迹：94 条 trace 事件全部为 `source=harness.py`，包含 `plan_created`、`research_task_finished`、`coverage_conditional_release`、`decision_stored`、`report_rendered`、`checkpoint`、`resume` 和 `scenario_created`。执行中出现并修正了 404、Gate 分歧和条件分支校验错误，原始错误已记录。

该结果是开发方自测，不等同于独立人工复核；结论为条件性而非无条件推荐，这是关键资格未被证明时的预期安全行为。脱敏运行记录保存在私有审计目录，不随公开仓库分发。

### 3.4 真实联网案例（回退宿主）

2026-11-23 以 **Trae Agent 回退宿主 + DeepSeek-V4.1-Flash** 完成一次真实来源案例，详见
[Example 14](examples/14-v2-harness-real-sources.md) 与冻结夹具 `docs/examples/v2-harness/`：

- 真实来源：WBS 2027 国际学费 GBP 39,500 与入学要求；Glasgow 2027-28 国际学费 GBP 34,815 与入学要求；两校排名/认证页。
- 计算：Warwick 5,450,000、Glasgow 4,981,500（GBP 便士）；预算目标 5,300,000、上限 5,600,000。
- 结论：conditional，默认 Glasgow；`ceiling=5,300,000` 时 Warwick fail / Glasgow pass。
- 未知项：中国私企对这两个具体项目的偏好保持 unresolved，未用学校排名冒充雇主认可。
- 本轮 metrics：tool results 2、evidence checks 2、decisions 1、scenarios 1。

该运行是**回退证据**，不是原生宿主验收。

### 3.5 发布工程

- 安装器同时安装 `decision.py` 与 `harness.py`，运行时白名单与所有权标记不变。
- 两个 CI 作业均执行 Harness 测试；发布契约断言 `harness.py` 被安装且只导入标准库与引擎。
- 版本单一来源：`.claude-plugin/plugin.json` 与 `SKILL.md` frontmatter 均为 `2.0.0-rc1`。

## 4. 尚未实现或未验证的能力

| 项目 | 状态 | 说明 |
|---|---|---|
| Codex CLI 原生 v2 端到端 | **通过（开发方自测，2026-11-23）** | 真实联网、中断恢复、逐 Offer 覆盖、Quick/Full、预算反事实；条件性结论；未做独立人工复核 |
| Claude Code 原生 v2 端到端 | **Not Run** | v1 最终轮曾因网关 402 中断；本轮未重试 |
| 语义支持自动判定 | **未实现** | 程序只能检查形式；来源是否蕴含主张需模型/人工 |
| 自动补查 | **未实现** | 只给核实路径，不替宿主发起新研究 |
| 多进程并发写同一状态 | **未验证** | 假设单宿主单写者 |
| 状态文件加密 | **未实现** | 依赖宿主磁盘与目录权限 |
| 真实运行成本测量 | **部分** | 已记录工具结果/轮次/重试，未计量 token 或费用 |
| v2 行为对所有职业路径的覆盖 | **部分** | 四条路径均有冻结测试；原生端到端案例只覆盖 private path |
| 独立人工复核 | **待进行** | 本轮为开发方自测，不能替代独立审核 |

## 5. 是否达到 v2.0 RC

- **架构与实现**：达到 RC 候选。v1 规则未被复制，Harness 状态、契约、恢复、隔离、观测和隐私生命周期均有代码与测试。
- **行为证据**：单元/集成/CLI/安装器测试齐全；Codex CLI 原生端到端自测已完成，并有真实来源的回退案例作为补充。
- **发布门槛**：Codex CLI 原生流程已通过开发方自测；仍缺 Claude Code 原生验收与独立人工复核。按仓库治理，离线测试或回退运行不能替代原生宿主验收。

因此状态为 `2.0.0-rc1` **候选**，不合并 `main`，不创建 v2.0.0 Stable Release。

## 6. 下一轮最值得修复的问题

1. **P0 — 剩余原生宿主验收**：Codex CLI 已于 2026-11-23 完成真实 v2 流程；Claude Code 仍需在可用模型额度下重跑一次完整流程（含断点恢复与预算反事实），并记录宿主、模型、工具调用和失败点。
2. **P1 — 语义支持复核流程（已在 RC Final Hardening 完成）**：`review` 记录 Claim ID、来源 URL 与定位、reviewer 类型、Supported/Partial/Unsupported/Unresolved、时间、依据、项目与届别；复核可降级但不能替代官方确认。
3. **P1 — 四条路径的行为覆盖（已在 RC Final Hardening 完成）**：private / soe / local / phd 均有冻结测试，覆盖缺失、未确认、不适用、条件性放行与路径隔离。
4. **P1 — 成本可观测性**：在 trace 中增加每任务的工具调用数与耗时，便于比较 v1/v2 的真实执行成本。
5. **P2 — 并发与损坏恢复**：状态写入已有原子替换，但多进程竞争和半写文件恢复尚未测试。
6. **P2 — 自动补查边界**：当前只给路径；若要自动补查，必须先定义次数、来源类型和停止条件，避免无限搜索。

## 复现

```bash
git clone --branch feat/v2-decision-harness --single-branch \
  https://github.com/NextVariable/offer-selection-skill.git
cd offer-selection-skill
python3 -m unittest discover -s maintenance -p 'test_decision_engine.py'
python3 -m unittest maintenance.test_harness
python3 -m unittest maintenance.test_release_contract
bash maintenance/test_installer.sh
```

真实来源夹具回归位于 `maintenance/test_harness.py::FrozenRealSourceCaseTests`，离线执行，不访问网络。

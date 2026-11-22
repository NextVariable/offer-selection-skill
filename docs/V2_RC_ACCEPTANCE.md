# v2.0 RC 验收报告

- 分支：`feat/v2-decision-harness`
- 基线：v1.0.0 Stable（`fcd2ff6`）
- 版本：`2.0.0-rc1`，`release_status: candidate`
- 日期：2026-11-23
- 结论：**工程范围达到 RC 候选（RC candidate），未达到可签发的 RC**。原生 Codex CLI / Claude Code 的 v2 端到端验收仍为 **Not Run**，须由独立审核完成后再决定是否转为 RC。

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
- “来源是否真正支持该主张”无法由程序证明，验证摘要固定输出 `semantic_review_required`，交由模型复核或人工裁定。
- 本地单文件 JSON，原子替换；无数据库、服务、账号或通用 Agent Runtime。

CLI 子命令：`init / plan / next / record / evidence / decide / report / scenario / checkpoint / resume / status / trace / privacy`。普通用户仍只用自然语言，不手工操作 CLI。

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
| 测试 | 78 + 发布契约 + 安装器 | 另加 41 项 Harness 测试与冻结真实来源案例 |

没有新增 Gate、国家/学校固定分值、权重或第二条推荐链。

## 3. 已完成功能与测试证据

### 3.1 测试矩阵（本地 macOS，Python 3）

| 套件 | 命令 | 结果 |
|---|---|---|
| v1 决策引擎 | `python3 -m unittest discover -s maintenance -p 'test_decision_engine.py'` | **78 passed** |
| v2 Harness | `python3 -m unittest maintenance.test_harness` | **41 passed** |
| 发布契约 | `python3 -m unittest maintenance.test_release_contract` | **10 passed** |
| 安装器安全 | `bash maintenance/test_installer.sh` | **PASS=37 FAIL=0** |
| Frontmatter | `python3 maintenance/check_frontmatter.py` | **PASS**（version=2.0.0-rc1） |
| 语法/导入 | `python3 -m py_compile ...`、AST 白名单测试 | **pass**；仅 `argparse/copy/datetime/hashlib/json/os/re/sys/pathlib` + `decision` |

41 项 Harness 测试分组：研究编排 7、工具契约 7、证据核验 6、决策集成 6、场景隔离 4、状态与隐私 5、v1/v2 对照 3、冻结真实案例 1、CLI 2。

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

### 3.3 真实联网案例（回退宿主）

2026-11-23 以 **Trae Agent 回退宿主 + DeepSeek-V4.1-Flash** 完成一次真实来源案例，详见
[Example 14](examples/14-v2-harness-real-sources.md) 与冻结夹具 `docs/examples/v2-harness/`：

- 真实来源：WBS 2027 国际学费 GBP 39,500 与入学要求；Glasgow 2027-28 国际学费 GBP 34,815 与入学要求；两校排名/认证页。
- 计算：Warwick 5,450,000、Glasgow 4,981,500（GBP 便士）；预算目标 5,300,000、上限 5,600,000。
- 结论：conditional，默认 Glasgow；`ceiling=5,300,000` 时 Warwick fail / Glasgow pass。
- 未知项：中国私企对这两个具体项目的偏好保持 unresolved，未用学校排名冒充雇主认可。
- 本轮 metrics：tool results 2、evidence checks 2、decisions 1、scenarios 1。

该运行是**回退证据**，不是原生宿主验收。

### 3.4 发布工程

- 安装器同时安装 `decision.py` 与 `harness.py`，运行时白名单与所有权标记不变。
- 两个 CI 作业均执行 Harness 测试；发布契约断言 `harness.py` 被安装且只导入标准库与引擎。
- 版本单一来源：`.claude-plugin/plugin.json` 与 `SKILL.md` frontmatter 均为 `2.0.0-rc1`。

## 4. 尚未实现或未验证的能力

| 项目 | 状态 | 说明 |
|---|---|---|
| Codex CLI 原生 v2 端到端 | **Not Run** | 未在本轮执行 |
| Claude Code 原生 v2 端到端 | **Not Run** | v1 最终轮曾因网关 402 中断 |
| 语义支持自动判定 | **未实现** | 程序只能检查形式；来源是否蕴含主张需模型/人工 |
| 自动补查 | **未实现** | 只给核实路径，不替宿主发起新研究 |
| 多进程并发写同一状态 | **未验证** | 假设单宿主单写者 |
| 状态文件加密 | **未实现** | 依赖宿主磁盘与目录权限 |
| 真实运行成本测量 | **部分** | 已记录工具结果/轮次/重试，未计量 token 或费用 |
| v2 行为对所有职业路径的覆盖 | **部分** | 测试以 private path 为主，SOE/local-stay/PhD 仅由 v1 回归覆盖 |
| 独立人工复核 | **待进行** | 本轮为开发方自测，不能替代独立审核 |

## 5. 是否达到 v2.0 RC

- **架构与实现**：达到 RC 候选。v1 规则未被复制，Harness 状态、契约、恢复、隔离、观测和隐私生命周期均有代码与测试。
- **行为证据**：单元/集成/CLI/安装器测试齐全，并有一个真实来源的回退端到端案例。
- **发布门槛**：未达到可签发 RC。缺原生 Codex CLI / Claude Code v2 端到端验收与独立审核；按仓库治理，这不能被离线测试或回退运行替代。

因此状态为 `2.0.0-rc1` **候选**，不合并 `main`，不创建 v2.0.0 Stable Release。

## 6. 下一轮最值得修复的问题

1. **P0 — 原生宿主验收**：在 Codex CLI 与 Claude Code 中各跑一次真实 v2 流程（含断点恢复与预算反事实），记录宿主、模型、工具调用和失败点。
2. **P1 — 语义支持复核流程**：把 `semantic_review_required` 变成明确的复核记录（谁、哪段文本、支持/不支持、裁定时间），避免“形式通过”被误读为“主张成立”。
3. **P1 — 四条路径的行为覆盖**：用 SOE/local-stay/PhD 的冻结案例验证硬门槛分类与 Gate 重开，而不只依赖 v1 回归。
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

# offer-selection-skill

> An evidence-driven Agent Skill for deciding **which postgraduate offer, if
> any, is worth accepting** — for a specific student and goal.

[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.2--rc-yellow.svg)](RELEASE_STATUS.md)
[![Platform](https://img.shields.io/badge/platform-Codex%20%7C%20WorkBuddy%20%7C%20Claude%20Code-5a5a5a.svg)](COMPATIBILITY.md)

**What it is.** A staged, evidence-gated decision engine that compares real
offers (UCL vs. CUHK, taught vs. research, return vs. stay) and returns one
honest conclusion: *choose X*, *choose conditionally by goal*, *no clear
difference*, or *choose none*.

**What problem it solves.** People compare schools by ranking and prestige and
end up with the wrong offer for *their* goal, budget, and background. This skill
judges each offer by the candidate it would turn *you* into, not by its name.

**What it is not.** It is **not a school ranking tool**. It does not answer
"which university is best," does not award fixed country/school points, and
makes no promise about jobs, visas, admission, or ROI. It answers one narrow
question — *given this student's profile, offers, goal, budget, and risk, which
offer should they take, and under what conditions* — and says "none of these"
or "no responsible answer yet" when that is the honest conclusion.

---

## Quick start

```text
/offer-selection-skill Compare my UCL and CUHK offers for China-return product roles.
```

That is the whole invocation. The skill asks for six compact private intake
groups once, then researches the public facts itself (tuition, ranking,
credential recognition, visa and employer rules) — it will not ask you to
transcribe them. It returns the conclusion, its decisive causes, and the
unresolved facts that could reverse it.

```text
/offer-selection-skill 帮我对比 UCL 和 CUHK 的 offer，目标是回国做产品岗
```

四种决策路径都支持：回国私企（非技术/技术）、国央企/体制内、留当地/双轨、读博/学术。

## Install

From a checkout of this repository:

```bash
./install.sh                     # auto-detect, user-level
./install.sh --platform codex    # Codex CLI   → ~/.agents/skills/
./install.sh --platform workbuddy # WorkBuddy   → ~/.workbuddy/skills/
./install.sh --platform claude-code # Claude Code → ~/.claude/skills/
./install.sh --dry-run           # preview only, changes nothing
```

Windows: `.\install.ps1` (PowerShell 7+) with the same flags. The installer
copies only a fixed runtime allowlist and writes an ownership marker; it
refuses to overwrite any directory it does not own. See
[Installation](#installation) for update and uninstall details.

## Status

**v0.3.2 release candidate.** [RELEASE_STATUS.md](RELEASE_STATUS.md) is the
single current readiness record. Latest released version: **v0.3.1**.

| Platform | Verification |
|---|---|
| **Claude Code** | Host verified; current v0.3.2 routing rechecked 2026-09-16 |
| **Codex** | Current v0.3.2 host/routing smoke verified 2026-09-16 |
| **WorkBuddy** | Discovery and installation verified; current invocation/reference loading pending |
| Other clients | Installer-only / best-effort, not advertised as verified |

See [COMPATIBILITY.md](COMPATIBILITY.md) for the full matrix and what each label
means.

---

## Example

A condensed, self-contained illustration (synthetic and anonymized):

```text
Goal: return to China for private-sector product roles. Budget: both offers fit.

  UCL MSc Management:   推荐（同档）— 假设总成本低约 ¥45k；你的品牌与相关实习
                         已足以进入目标市场，因此额外实习窗口的边际价值有限。
  CUHK MSc Marketing:   推荐（同档）— 假设已核实课程安排、身份和地点确实允许你
                         使用香港/深圳的目标岗位实习窗口；这对仍需补实习的人更有价值。

在这些明确假设下，两者没有足够证据形成结果档位差。若你已有两段高质量相关实习，
偏向成本更低者；若你仍缺关键实习，且 CUHK 的实习机会对你确实可达，偏向 CUHK。
任何一个关键假设未经核实，都只能给条件式结论，不能伪造确定分数。
```

The engine enforces the properties this shows: conclusion first; equivalent
offers shown in the same tier; real trade-offs handed back to the user; and
unresolved or eligibility-relevant facts called out rather than buried under a
score. More behavior illustrations live in [examples/](examples/README.md).

## How it works

The engine runs a fixed stage order — feasibility screening → user and goal →
gap/transformation → path eligibility → competitiveness → cost/ROI/risk →
subjective utility → recommendation and score — with **eligibility before
competitiveness** and scores that represent a decision, never generate one.

```
Current Profile → Goal → Gap → Offer Transformation → Graduation Profile
  → Eligibility → Competitiveness → Cost/ROI/Risk → Recommendation
  → Score (as representation)
```

Loading structure:

```
SKILL.md ──> references/core-decision-engine.md   (every run, single owner)
   │
   ├──> references/path-*.md                      (only the activated path)
   │      private-sector · soe-public · local-stay · phd-academic
   │
   └──> domain/priors-and-calibration.md          (only when a prior fires)
```

For the philosophy behind this design, see
[docs/DECISION_PHILOSOPHY.md](docs/DECISION_PHILOSOPHY.md). For the loading
structure and repository layout, see
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Why it is honest about uncertainty

- Every volatile fact (tuition, ranking, credential policy, visa rules) is
  graded `Confirmed / Unresolved / Heuristic` with an operative date.
- A critical unresolved fact that could close the target path yields
  **No Responsible Score Yet** — never a fake-precision integer.
- "Choose none" and "these are decision-equivalent" are first-class answers.

## Privacy

This skill has **no telemetry, backend, or credential requirement**. Your
private intake is processed by the Agent host you choose, and its retention and
training policies are controlled by that host, not this repository. Web
research uses only minimal public identifiers — private intake never enters a
search query. See [PRIVACY.md](PRIVACY.md).

## Contributing

The rule-ownership model and methodology constraints are in
[CONTRIBUTING.md](CONTRIBUTING.md). License: [MIT](LICENSE). Security:
[SECURITY.md](SECURITY.md). Changelog: [CHANGELOG.md](CHANGELOG.md).

---

## Installation

The installer places a **runtime-only** package (see `install.sh`'s allowlist)
and writes an ownership marker (`.offer-selection-skill-install.json`). Before
replacing an existing directory it verifies the marker; a symlink, a random
folder that happens to share the name, a root/home path, or the source package
is **refused, not overwritten**.

| Host | Install | Update | Uninstall |
|---|---|---|---|
| Codex | `./install.sh --platform codex` | re-run | delete `~/.agents/skills/offer-selection-skill/` |
| WorkBuddy | `./install.sh --platform workbuddy` | re-run | delete `~/.workbuddy/skills/offer-selection-skill/` |
| Claude Code | `./install.sh --platform claude-code` | re-run | delete `~/.claude/skills/offer-selection-skill/` |

Update is a re-run of the install (the marker makes it a safe in-place upgrade).
Uninstall is deleting the marked directory — the marker guarantees the installer
only ever manages paths it created. Codex, WorkBuddy, and Claude Code installs
coexist; installing one never overwrites the others, and the universal
`.agents/skills` convenience link never replaces an independent Codex install.

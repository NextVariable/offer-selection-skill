# Architecture

## v1 execution boundary

The host agent gathers the profile, plans research and reads public sources.
It converts observations into scoped evidence and interprets graduation
profiles and career value using the existing path references. The shipped
standard-library Python module checks the case and decision exchange, cash
ranges, deadlines, gate declarations and permitted score precision. It has
no network access and does not infer hiring, prestige, academic success or
source truth. The two report modes project the same validated decision.
Counterfactuals keep the original case fixed and explicitly reopen changed
scopes. The [runtime workflow](../skills/offer-selection-skill/references/structured-workflow.md)
defines the exchange and CLI.

The source inspection record separates retrieval (`opened/blocked/unopened`),
authority and whether the located passage supports a particular dated
claim. The local validator can reject structurally unsupported confirmations.
Its `audit` command marks unsupported claims unresolved in a separate copy,
reopens dependent gates and removes unverified finite cost bounds. The agent
still opens and interprets the source. Quick and Full both show material gate
statuses and sources used for confirmed findings. Both can show researched
costs without a numeric ceiling. An incomplete ledger remains a subtotal.

Local execution runs against agent-managed temporary files. User messages
are the normal interface for intake, follow-ups and scenarios. The Python
module reads those files and writes to stdout. Search uses public programme,
employer or policy terms, while personal inputs remain in the agent's local
case state. The model must distinguish a scoped source observation from
confirmation of a particular student's outcome.

## v2 execution harness

v2 keeps the same Skill package and decision engine. It adds one optional
standard-library module, `scripts/harness.py`, which owns *execution state*
around the engine rather than another decision model:

| State | Owner | Purpose |
|---|---|---|
| Case State | harness, validated by `decision.py` | The one case document; no parallel copy of profile or offers |
| Research Task State | harness | Task class (`hard_gate`/`decisive`/`optional`), dependency, status, attempts, verification route, stop condition |
| Evidence State | harness + `decision.py` | Claim/source mapping, scope/period/freshness/authority checks, conflicts, downgrade propagation through `decision.audit` |
| Gate State | `decision.py` | Gate semantics, `Unknown ≠ Pass`, and recommendation feasibility |
| Decision State | `decision.py` + digest | Validated decision, case digest, stale marker if evidence/gates change |
| Scenario State | harness | Named counterfactual isolated from the base case |

Boundaries:

- The host still owns model calls, browsing and judgment. The harness never
  fetches, never calls a model and never decides.
- Programmatic checks cover structure, scope, period, freshness, authority,
  dependency and arithmetic. Whether a source entails a claim remains a
  model/human review and is labelled that way in every verification summary.
- A recommendation is blocked while a hard-gate task is open; an unopened or
  incomplete source cannot close a gate; an evidence downgrade marks a stored
  decision stale so it cannot be rendered as current.
- State is one local JSON file with atomic replacement, checkpoints and a
  default seven-day profile retention. Expiry performs an actual profile
  deletion on the next CLI access, not only a warning. Checkpoints are audit
  markers; `resume` always re-verifies the live state instead of rolling back.
- Coverage is a diagnostic derived from declared gates, evidence and tasks per
  active path. It reports missing or unconfirmed kinds without creating a new
  gate or changing a recommendation.
- The trace is append-only and records research starts/finishes, source
  checks, evidence and gate changes, calculations, validation failures,
  retries, resume, checkpoint drift, coverage gaps, scenario creation and the
  final recommendation.

The exchange and commands are documented in
[structured-workflow.md](../skills/offer-selection-skill/references/structured-workflow.md).
The harness imports `decision.py`; it does not copy its constants, gates,
cost or score logic.

## The decision pipeline

```
Current Profile → Goal → Gap → Offer Transformation → Graduation Profile
  → Eligibility → Competitiveness → Cost/ROI/Risk → Recommendation
  → Score (as representation)
```

Each offer is judged by the candidate it produces, not by its label. The
canonical stage order, exceptions and scoring semantics live only in
[`core-decision-engine.md`](../skills/offer-selection-skill/references/core-decision-engine.md). This diagram
is an orientation aid, not an alternative execution specification.

## Loading structure

```
SKILL.md  ──>  references/core-decision-engine.md   (every run, single owner)
    │
    └──>  references/path-*.md                      (only the activated path)
              path-private-sector.md
              path-soe-public.md
              path-local-stay.md
              path-phd-academic.md
    │
    └──>  references/priors-and-calibration.md      (prior trigger, or dated cost calibration)
```

- `core` owns *how to execute* — stages, gates, evidence states, research
  priority/stop, decision sufficiency, score and equivalence.
- Each `path-*.md` owns the rules for one goal; dual goals run both paths
  separately.
- `priors-and-calibration.md` is normally conditional: read it when a prior
  trigger fires (U.S. offer on a research/STEM or China-return comparison,
  joint venture, local-stay country claims, equivalence/tie-break, or a
  strong-baseline check). The dated cost-calibration section is the exception:
  when it covers the decision's operative year, `skills/offer-selection-skill/SKILL.md` and core require it
  to be read and cross-checked before a cost conclusion. The calculation and
  reconciliation semantics are owned by core Budget, not by the table.

## Never loaded at runtime

| Path | Role | Read by |
|---|---|---|
| `internal/source-of-truth.md` | Provenance and rule evolution | maintainers |
| `internal/audits/` | Historical audits (non-normative) | maintainers |
| `evals/` | Behavioral evidence (cases, oracles, rollouts, reviews) | reviewers |
| `internal/archive/` | Superseded materials | nobody |

## One rule, one owner

A rule is defined in exactly one file. Other files reference it; they never
restate it. This prevents the "two copies that drift apart" failure that makes
rule changes dangerous.

## Repository layout

```text
skills/offer-selection-skill/   Skill package: SKILL.md, references, decision.py, harness.py
docs/                          Usage, privacy and maintenance documentation
docs/examples/                 Synthetic decision examples
maintenance/                   Installers, checks and release tools
evals/                         Frozen behavioral evidence (private)
internal/                      Audits, history and provenance (private)
```

The loading diagram above uses paths relative to `skills/offer-selection-skill/`.

| Area | Contents |
|---|---|
| `skills/offer-selection-skill/SKILL.md` | Runtime entrypoint: trigger, load order, intake, output contract |
| `skills/offer-selection-skill/references/core-decision-engine.md` | Canonical execution semantics |
| `skills/offer-selection-skill/references/path-*.md` | One rule file per decision path |
| `skills/offer-selection-skill/references/priors-and-calibration.md` | Conditional, labelled heuristics/anchors |
| `skills/offer-selection-skill/scripts/decision.py` | Case/decision validation, gate and cost arithmetic, Quick/Full rendering |
| `skills/offer-selection-skill/scripts/harness.py` | Research state, evidence checks, checkpoints, scenario isolation, trace, privacy lifetime |
| `maintenance/install.sh` / `maintenance/install.ps1` | Cross-platform installer (strict runtime allowlist + ownership marker) |
| `.claude-plugin/` | Version source of truth (`plugin.json`) + marketplace metadata |
| `docs/examples/` | Anonymized, synthetic behavior illustrations (not oracles) |
| `docs/` | Installation, decision philosophy and architecture |
| `maintenance/` | Mechanical checks: frontmatter, installer test battery |

Internal development material — `evals/`, `internal/audits/`, `internal/archive/`,
`internal/source-of-truth.md`, and the eval runner tooling — lives only in the
development repository. The public distribution and runtime install exclude
these materials. See [the release checklist](RELEASE_CHECKLIST.md) for verification.

# Architecture

How the skill is structured, loaded, and governed.

## The decision pipeline

```
Current Profile → Goal → Gap → Offer Transformation → Graduation Profile
  → Eligibility → Competitiveness → Cost/ROI/Risk → Recommendation
  → Score (as representation)
```

Each offer is judged by the candidate it produces, not by its label. The
canonical stage order, exceptions and scoring semantics live only in
[`core-decision-engine.md`](../references/core-decision-engine.md). This diagram
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
    └──>  domain/priors-and-calibration.md          (prior trigger, or mandatory dated cost calibration)
```

- `core` owns *how to execute* — stages, gates, evidence states, research
  priority/stop, decision sufficiency, score and equivalence.
- Each `path-*.md` owns the rules for one goal; dual goals run both paths
  separately.
- `priors-and-calibration.md` is normally conditional: read it when a prior
  trigger fires (U.S. offer on a research/STEM or China-return comparison,
  joint venture, local-stay country claims, equivalence/tie-break, or a
  strong-baseline check). The dated cost-calibration section is the exception:
  when it covers the decision's operative year, `SKILL.md` and core require it
  to be read and cross-checked before a cost conclusion. The calculation and
  reconciliation semantics are owned by core Budget, not by the table.

## Never loaded at runtime

| Path | Role | Read by |
|---|---|---|
| `domain/source-of-truth.md` | Provenance and rule evolution | maintainers |
| `audits/` | Historical audits (non-normative) | maintainers |
| `evals/` | Behavioral evidence (cases, oracles, rollouts, reviews) | reviewers |
| `archive/` | Superseded materials | nobody |

## One rule, one owner

A rule is defined in exactly one file. Other files reference it; they never
restate it. This prevents the "two copies that drift apart" failure that makes
rule changes dangerous.

## Repository layout

| Area | Contents |
|---|---|
| `SKILL.md` | Runtime entrypoint: trigger, load order, intake, output contract |
| `references/core-decision-engine.md` | Canonical execution semantics |
| `references/path-*.md` | One rule file per decision path |
| `domain/priors-and-calibration.md` | Conditional, labelled heuristics/anchors |
| `install.sh` / `install.ps1` | Cross-platform installer (strict runtime allowlist + ownership marker) |
| `.claude-plugin/` | Version source of truth (`plugin.json`) + marketplace metadata |
| `examples/` | Anonymized, synthetic behavior illustrations (not oracles) |
| `docs/` | Philosophy (`DECISION_PHILOSOPHY.md`) and this architecture |
| `tools/` | Mechanical checks: frontmatter, installer test battery |

Internal development material — `evals/`, `audits/`, `archive/`,
`domain/source-of-truth.md`, and the eval runner tooling — lives only in the
development repository and is **not** shipped in the public release snapshot
(see `tools/build_release_snapshot.sh`).

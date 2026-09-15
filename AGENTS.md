# Offer Selection Skill — repository governance

This repository is a Claude Code / agent skill for deciding which postgraduate
offer, if any, is worth accepting for a specific user and goal.

## Normative files (authority model)

| Layer | Path | Who reads it |
|---|---|---|
| Runtime entrypoint | `SKILL.md` | runtime agent, every activation |
| Execution semantics (single owner) | `references/core-decision-engine.md` | runtime agent, every run |
| Path rules | `references/path-{private-sector,soe-public,local-stay,phd-academic}.md` | runtime agent, when the path activates |
| Conditional priors and dated calibration | `domain/priors-and-calibration.md` | runtime agent when a prior trigger fires, and whenever the operative year has a mandatory cost calibration |

The governing decision engine is
`SKILL.md → references/core-decision-engine.md` (+ relevant path files).
Do not maintain a second copy of the execution chain or any domain rule in
this file or anywhere else.

## Modification rules

- **One rule has one owner.** Add or change a rule only in its owner
  (core / a path file / priors doc). Never restate an owned rule in another
  file; reference it.
- **Never modify Domain Methodology** without an explicit user decision:
  do not add fixed weights, fixed country/school points, school golden-case
  branches, promote a heuristic to a fact, or hard-code dynamic facts
  (tuition, ranking, visa, employer, credential, graduation policy).
- Version number is single-sourced in `.claude-plugin/plugin.json` and copied
  to the `SKILL.md` frontmatter; bump both and tag the commit when releasing.
- The skill loads only the files in the table above at runtime. Maintainer
  history and provenance are kept out of this repository.

## Testing workflow

- Mechanical: `python3 tools/check_frontmatter.py` and the installer battery
  (`bash tools/test_installer.sh`) run in CI.
- A production change that alters decision semantics must be backed by an
  explicit maintainer decision and documented in `CHANGELOG.md`.

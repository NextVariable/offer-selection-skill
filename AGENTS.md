# Offer Selection — repository governance

Offer Selection is a Domain-Specific Decision Harness for Postgraduate Offer
Selection. It ships as the `offer-selection-skill` Agent Skill with formal support
for Codex CLI. The host provides model execution and web research.

**STABLE RELEASED / FEATURE FROZEN / MAINTENANCE MODE.** Preserve the install
identifier and paths. Scope changes to maintenance, documentation, or
maintainer-authorized fixes. Keep published audit and acceptance records intact.
See [Architecture](docs/ARCHITECTURE.md) for execution boundaries.

## Normative files (authority model)

| Layer | Path | Who reads it |
|---|---|---|
| Runtime entrypoint | `skills/offer-selection-skill/SKILL.md` | runtime agent, every activation |
| Execution semantics (single owner) | `skills/offer-selection-skill/references/core-decision-engine.md` | runtime agent, every run |
| Path rules | `skills/offer-selection-skill/references/path-{private-sector,soe-public,local-stay,phd-academic}.md` | runtime agent, when the path activates |
| Conditional priors and dated calibration | `skills/offer-selection-skill/references/priors-and-calibration.md` | runtime agent when a prior trigger fires, and whenever the operative year has a mandatory cost calibration |

The governing decision engine is
`skills/offer-selection-skill/SKILL.md → skills/offer-selection-skill/references/core-decision-engine.md` (+ relevant path files).
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
  to the `skills/offer-selection-skill/SKILL.md` frontmatter; bump both and tag the commit when releasing.
- The table lists the rule owners. Runtime workflows and scripts are loaded
  through the Skill when needed. Keep private provenance and raw test material
  outside the public repository.

## Git workflow

- User standing preference (2026-09-17): automatically complete local Git
  version control for authorized repository changes; do not wait for a separate
  reminder to commit. Inspect branch, HEAD, staging and existing edits before
  work, preserve unrelated edits, and commit completed work in coherent units.
- Inspect the staged diff and run appropriate checks before committing. Record
  failed or incomplete validation honestly; a checkpoint is not a release or a
  claim that behavioral regression passed. Preserve immutable eval evidence.
- Do not silently include unrelated pre-existing work. When a user explicitly
  requests archiving the current accumulated changes, identify that provenance
  in commit messages instead of claiming every change was made in this task.
- Start public changes from public history. Push reviewed public files to a
  topic branch and use a pull request. Preserve private checkout protections.
  Direct default-branch pushes, merging, release and tag changes, remote branch
  deletion, PR closure and history rewriting require explicit authorization.
  Report the commit, checks, remote branch and any remaining local changes.

## Testing workflow

- Mechanical: `python3 maintenance/check_frontmatter.py` and the installer battery
  (`bash maintenance/test_installer.sh`) run in CI.
- A production change that alters decision semantics must be backed by an
  explicit maintainer decision and documented in `docs/CHANGELOG.md`.

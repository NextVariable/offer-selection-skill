# Release status

This is the single current readiness record for `offer-selection-skill`.
Files under `audits/` preserve what was known at an earlier point; they are
evidence and history, not competing current verdicts.

**Current publication decision (2026-09-17): the maintainer designates v0.3.2
as the official version.** This supersedes the earlier RC publication label;
it does not claim that the outstanding behavioral findings or governed
regression requirements have passed. No tag or GitHub Release is created by
this documentation update. The installer, packaging and privacy work
described below is unchanged. The branch now contains **committed production
behavior changes** to the decision rules (`67f0e63`) —
private-sector non-technical Major-Gate scope, multi-offer hard-gate screening
before any shortlist, automatic application of the operative-year cost
calibration, tuition lower-bound and ceiling-straddling budget judgments, and a
pre-output consistency check — plus three new eval cases committed separately
in `c9249eb`. The earlier statement
that the decision methodology was unchanged is therefore **superseded** as of
this date. The three new cases were frozen in `b589715` and completed one
governed blind run plus run-bound independent review on 2026-09-16. Two passed
all three dimensions; `priv-user-no-major-four-offer-2026-cost` failed Decision
Mechanism and Evidence Support and was Partial on Output Contract. The reviewer
classified it as research failure / rollout variance: the answer extended an
NIE-scoped living-cost source to another NTU programme and used unsourced
exchange-rate and miscellaneous-cost allowances to declare the Singapore
Budget Gate passed. Current Production already requires an unresolved gate in
that situation, so this run is not evidence of a methodology defect. The
immutable failure remains in the evidence record. This record claims no
regression pass.

Final hardening on 2026-09-16 added a deterministic validator for structured
evidence declarations and bound compliant manifests (or an explicit
no-evidence-claims declaration) to every new rollout. It catches declared
programme/population scope mismatch, missing operative periods, unsupported FX
and miscellaneous-cost inputs, missing accommodation fallbacks, and declared
Budget Gate / score-state dependency contradictions. It does **not** verify
that a source is true, that scope or criticality was honestly declared, or that
the recommendation is semantically sound; independent review remains
mandatory. Historical Markdown evidence was not rewritten or retroactively
graded. The runtime entrypoint was also shortened by moving navigation back to
the canonical owners; no decision-methodology rule changed in this hardening.

The public snapshot remains self-consistent: its `CONTRIBUTING.md`, `AGENTS.md`,
PR template and `SECURITY.md` are rewritten at snapshot-build time
(`tools/snapshot_docs.py`) so they reference only the files the snapshot
actually ships, never the excluded `evals/` / `audits/` / `archive/` /
provenance tree.

## What is confirmed now

- Runtime semantics still follow the same owner chain: `SKILL.md` → core → the
  activated path file, with priors read on their conditions — the
  operative-year cost calibration being the one entry that is mandatory once
  its condition holds.
- No fixed school/country points, fixed ranking weights, or case-specific
  winner was introduced. The new rule-scope and calibration-routing changes
  are behavior changes, not fixed points or hard-coded dynamic facts;
  they are not yet behavior-verified (see below).
- **Claude Code is Host verified** (rechecked 2026-09-16, Claude Code 2.1.260,
  headless): the current v0.3.2 install loaded `SKILL.md`, the mandatory
  `references/core-decision-engine.md`, and the activated
  `references/path-private-sector.md` in a read-only fresh invocation. The
  earlier 2026-09-09 end-to-end record remains the researched-answer evidence:
  the skill was discovered, invoked, loaded `references/core-decision-engine.md`
  plus the correctly activated `references/path-private-sector.md`, triggered
  `domain/priors-and-calibration.md` on the internship-repair anchor, skipped
  the non-activated paths and the never-load files, produced a mechanism-correct
  conditional answer on an anonymous UCL-vs-CUHK comparison, and did not
  activate on an unrelated programming question. This is an **end-to-end smoke
  verification** for one representative China-return private-sector case, not
  governed behavioral verification or a regression against the full frozen
  contract. A second anonymous case (985 CS graduate,
  UCL vs CUHK technical return) was run on 2026-09-09 after the `SKILL.md`
  privacy-rule addition and again produced a mechanism-correct conditional
  answer with provisional scores, reversal conditions, and source links —
  confirming the privacy rule does not break normal runs.
- **Codex current-runtime host smoke is verified** (2026-09-16, Codex CLI
  0.154.0-alpha.6.2): a fresh read-only invocation discovered the skill, loaded
  the 149-line slimmed `SKILL.md`, mandatory core, and the activated private-
  sector path, and returned the expected conditional mechanism. The test also
  exposed a stale legacy copy under `~/.codex/skills/`; it was replaced through
  the managed installer before the passing rerun. This is host/routing smoke
  evidence, not governed behavioral evidence.
- **WorkBuddy discovery is confirmed in this session**: the skill is listed in
  the available skills (installed at `~/.workbuddy/skills/offer-selection-skill/`,
  byte-identical). Invocation, reference loading and a researched answer after
  a reload in a fresh session remain **Pending** — discovery in the current
  session is not end-to-end host execution.
- The Unix installer passes 37 deterministic safety tests (managed replacement,
  rollback with preserved-backup path reporting, native Cursor/Windsurf layouts,
  false Copilot auto-detection, Codex+WorkBuddy+Claude Code coexistence). The
  dead Cursor/Windsurf rule-adapter functions were removed from both installers
  on 2026-09-09; behavior is unchanged (still 37/37).
- `README.md` is rewritten as a public-project front page with a
  self-contained example; `examples/` (12 anonymized cases) and `docs/`
  (philosophy + architecture) are new; `audits/` is marked historical via
  `audits/README.md`.
- The public snapshot (`build/offer-selection-skill/`, 43 files) has no runtime or
  CI dependency on excluded development material. Explanatory references to
  the private evidence/provenance tree remain where they clarify governance;
  those files are not linked or loaded. There are no broken Markdown links,
  the public CI references only files the snapshot ships, and the
  Linux-simulable checks (frontmatter, JSON parse, version consistency,
  installer battery) are executed by the snapshot builder itself and all pass
  in the correctly named generated package directory.
- **The local public-snapshot verification loop is closed (2026-09-16).** The
  builder now emits a correctly named `offer-selection-skill/` package, runs
  the same Linux-simulable frontmatter, manifest, installer and version checks
  from inside that package, and is itself exercised by the development CI.
- **Pre-public repository hardening is complete locally (2026-09-16).** The
  snapshot builder may replace the repository-owned default output, but refuses
  a non-empty custom output unless a sidecar ownership marker matches its path
  and inode; it rejects a target symlink and invalidates the marker before any
  destructive replacement. A failed build leaves no trusted marker. The four
  destructive-boundary tests pass. Public governance-document rewrites now
  require every declared source block to match exactly once, with four
  fail-fast unit tests. `evals/README.md` no longer maintains a competing
  current release verdict or hand-counted result totals, and the architecture
  documentation now records the mandatory dated cost-calibration exception.
- The privacy boundary is documented: runtime instructions prohibit sending
  private intake in web queries; `PRIVACY.md` separates Skill behavior from
  host retention, distinguishes the dev repo from the clean public snapshot, and
  records the dated, scope-limited snapshot scan.

## Public repository verification (2026-09-16)

The public `main` was initialized at `9815eee7d044a7bd1352bbd55031d0e4a9557c98`
with no parent and a GitHub noreply author. Its 43-file tree matches the locally
accepted snapshot. [GitHub Actions run 35026787716](https://github.com/yunheliu68-ux/offer-selection-skill/actions/runs/35026787716)
passed Linux release-readiness and real Windows (`windows-latest`, `pwsh`)
installer checks, including `install.ps1` and `tools/test_installer.ps1`.
No stable tag or GitHub Release has been created.

This closes the Windows execution and initial-publication engineering tasks.
It does not close the behavioral findings below. The earlier RC / NO-GO
publication decision is superseded by the maintainer's 2026-09-17 official-version
decision; governed behavioral regression remains incomplete. WorkBuddy remains
pending host validation.

Replacing `main` did not purge GitHub's old commit objects or Actions records.
The previous root commit may still be accessible by SHA; the current branch's
clean history must not be described as deletion of all older hosted material.

## Outstanding validation work

- **Exercise WorkBuddy through a real current host run.** Current file
  placement and discovery are confirmed, but WorkBuddy 5.5.4 kept the new-task
  Send control disabled after selecting the project, code mode, and an
  available free model. No current invocation or reference-loading result was
  produced. Do not substitute the older failed-cost conversation for this
  check.
- **Complete outstanding behavioral validation**: v0.3.2 is designated the
  official version, while behavioral evidence still contains bound PARTIAL/FAIL
  findings and three open Robustness Instability findings. Governed regression
  remains incomplete; mechanical tests do not close these findings.
- **Resolve the governed production-regression failure without cherry-picking.** The production behavior
  changes committed in `67f0e63` and the three new eval cases committed in
  `c9249eb`, frozen against production commit `67f0e63` in `b589715`
  (`evals/cases/priv-product-ops-major-cost-calibration`,
  `priv-seven-offer-soft-fit-budget-gate`,
  `priv-user-no-major-four-offer-2026-cost`) completed one `blind record →
  independent review` cycle on 2026-09-16. The first two are PASS; the third is
  FAIL and must not be hidden or replaced by rerunning for a better sample.
  Run-bound reviews now stand at **7 PASS / 3 PARTIAL / 3 FAIL** across thirteen
  reviewed cases. The new PASS results are first validations of newly frozen
  contracts, not regressions from a previously promoted baseline; the new FAIL
  leaves the candidate short of a governed production-regression pass. Decide
  and document a prospective remediation protocol before another run. The
  protocol and a single-use plan for this exact failed run were added on
  2026-09-16: after any bound FAIL, `eval_runner.py record` now refuses another
  run without a case-scoped plan, stores the plan path and hash in the run, and
  refuses plan reuse. The blind generator may not read the plan. This permits
  one prospective retest but does not alter Production, the frozen oracle or
  the historical FAIL. Until that protocol produces independently reviewed
  evidence under the repository rules, the release must not be called
  Regression Passed.
- **Do not count deterministic hardening as behavioral remediation.** The new
  evidence validator and eight runtime-contract smoke checks make future runs
  more auditable and catch structural contradictions before review. They do not
  alter or invalidate either failed rollout for
  `priv-user-no-major-four-offer-2026-cost`, and no new behavioral rerun was
  performed as part of this hardening.

## Manual host-verification steps (WorkBuddy)

Not yet completed; do not mark WorkBuddy verified until each step is observed.

1. **WorkBuddy** — discovery is confirmed (the skill is listed in the current
   session's available skills). Open a **fresh** session (reload Skills or
   restart), invoke it, and confirm it loads `references/core-decision-engine.md`
   plus the activated path file and returns a researched answer.
2. Confirm an unrelated question does not activate the skill, and that a prompt
   containing a name/student-ID/e-mail does not place that private intake into
   a web query.

## Status vocabulary

`Installer verified` means files, ownership and rollback were tested.
`Host verified` means a real client discovered and invoked the skill and loaded
its referenced files. `End-to-end smoke verified` means a representative real
request completed successfully. `Behavior verified` means a run was reviewed
against its frozen contract and evidence requirements. These labels must not be collapsed
into a generic “supported” or “all tests passed” claim, and mechanical/unit
tests must not be presented as behavioral verification.

Update this file whenever a release blocker closes or reopens. Do not create a
new readiness report merely to change the verdict; add dated evidence under
`audits/` only when the underlying investigation needs preservation.

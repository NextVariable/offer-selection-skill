# Changelog

All notable changes to offer-selection-skill are recorded here. Version source
of truth: `.claude-plugin/plugin.json` (mirrored in `SKILL.md` frontmatter).
This project follows the governance rules in `AGENTS.md` / `CONTRIBUTING.md`;
behavioral evidence conventions are in `evals/README.md`.

## [Unreleased] — v0.3.2 release candidate (not yet tagged)

Everything on the branch since the `v0.3.1` release commit. Decision
methodology is unchanged in substance — the same offer-selection judgment
chain, gates, evidence states, score-state rules and four path logics — with
three narrow production clarifications plus governance and packaging work:

- **exact-claim Confirmed** — `Confirmed` is claim-scoped, not source-scoped
  (an institution name or top-level domain alone confirms nothing); third-party
  summaries stay `Heuristic/Prior` unless the primary source is actually
  checked; partial support narrows the claim instead of stretching the source;
  dynamic facts carry an operative period (`references/core-decision-engine.md`).
- **recognition incremental value / cost clarification** — a supported
  recognition difference prevents manufactured equivalence but does not, by
  itself, settle the overall recommendation; Stage 5 must still weigh
  user-specific incremental value against incremental cost
  (`references/path-private-sector.md`).
- **lean user output** — normal user answers lead with the conclusion,
  decisive causes and reversal conditions; the full stage/gate/evidence-state
  manifest is expanded only for eval, audit, an explicit request, or high-risk
  facts. Reduces presentation, never research (`SKILL.md`).
- **run-bound reviews** — every review is bound to one exact run record; a
  later PASS never erases a historical FAIL; aggregation is fixed (any FAIL →
  FAIL; else any PARTIAL → PARTIAL; else PASS).
- **freeze generations are byte-immutable** — a generation file is written
  once and never rewritten; current/superseded state lives only in
  `freezes/index.json` and the append-only `freezes/lifecycle.jsonl`.
- **new evidence binds a Production commit** — every new freeze, run record
  and run-bound review must carry a commit resolvable in this repository
  (explicit `--commit`, or `HEAD` by default); a run without a commit cannot
  receive a run-bound review; legacy records keep their historical shape.
- **installer security hardening** — `install.sh` / `install.ps1` install a
  fixed runtime allowlist only (`SKILL.md`, `references/`,
  `domain/priors-and-calibration.md`, `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, `LICENSE`); the version is read from
  `.claude-plugin/plugin.json` instead of being hard-coded; staging + atomic
  replace; destination safety checks; post-install runtime-reference
  verification. Dev material (`audits`, `evals`, `archive`, `tools`, git,
  machine-local files) **and the repository's developer docs** (`README.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, `AGENTS.md`) are never shipped — `SKILL.md`
  is the installed usage entry point.
- **managed install destinations** (final RC hardening) — the installers
  require a custom destination to be absolute and to end exactly in
  `offer-selection-skill`; before replacing an existing directory they verify
  an ownership marker (`.offer-selection-skill-install.json`, schema
  `offer-selection-skill-install/v1`). Unmanaged directories, symlinks, `/`,
  `$HOME`, the source package and its ancestors are refused untouched;
  pre-marker installs are detected by their skill layout and migrated with an
  explicit notice.
- **historical reviews restored to original bytes** — the ten review
  narratives whose machine-local paths had been normalized during privacy
  cleanup were restored byte-for-byte, because historical review markdown is
  treated as immutable evidence. The redaction record
  (`audits/2026-09-08-public-release-redaction.md`) documents the correction;
  one byte-immutable rollout keeps its original bytes for the same reason.
  These local paths remain visible in the public source tree/history and are
  never shipped by the installers.
- **installer test correctness fixes** — the PowerShell safety battery
  (`tools/test_installer.ps1`) runs every installer scenario in an isolated
  `pwsh` child process (an expected `exit 1` inside `install.ps1` can no
  longer terminate the runner) and passes arguments — including paths with
  spaces — through `ProcessStartInfo.ArgumentList` instead of joined command
  strings. The Unix and Windows link tests now use a destination whose
  basename is exactly `offer-selection-skill`, so they exercise link
  protection rather than failing earlier on the basename check; the Windows
  junction test verifies the path is a real reparse point and fails the
  battery (it never skips) if `mklink` cannot create one. Rollback is
  fault-injection tested through default-off, test-only hooks:
  `OFFER_SELECTION_INSTALLER_TEST_FAIL_AFTER_BACKUP` fails the atomic swap
  after the previous install has moved to backup and asserts a full restore
  with no residue; `OFFER_SELECTION_INSTALLER_TEST_FAIL_RESTORE` additionally
  fails the automatic restore and asserts the backup is preserved, its exact
  path is reported, and the installer never claims a restore that did not
  happen. On a failed placement the installers now report three distinct
  states — previous install restored; automatic restoration also failed
  (backup kept at a printed path, never deleted or overwritten); or no
  previous   install existed — instead of always claiming a restore. Unix
  battery result: 32/32 PASS locally (up from 24/24).
- **Agent Skills frontmatter conformity** — `SKILL.md` frontmatter now uses
  only the official Agent Skills top-level fields (`name`, `description`,
  `license`, `metadata`); the non-standard top-level `activation` and
  `provenance` keys were removed and their content (activation path,
  maintainer, provenance note) moved into `metadata` as strings. A local,
  network-free compliance check (`tools/check_frontmatter.py`) enforces this in
  CI: official top-level keys only, valid `name`, non-empty ≤1024-char
  `description`, string-only `metadata`, and `metadata.version` equal to
  `.claude-plugin/plugin.json`. The official `skills-ref` validator is **not
  run** in this repository; the local check is its equivalent and is labelled
  as such.
- **public provenance and compatibility gap closure** — the one public
  governance note that referenced the private `.workbuddy/memory` tree
  (`evals/baselines/soe-gate-first/SUPERSESSION-20260907.md`) now points to the
  in-repo independent review instead; `.workbuddy` remains only in ignore /
  anti-install / hygiene contexts. The PowerShell support claim was tightened
  from "5.1+ and Core 7+" to **PowerShell 7+** (matching what CI actually
  exercises with `pwsh`; Windows PowerShell 5.1 is not claimed). GitHub
  Actions steps are pinned to full commit SHAs for
  `actions/checkout` (`11d5960a…`, `# v4`) and `actions/setup-python`
  (`a26af69b…`, `# v5`), resolved from the official action repositories.
- **public community files** — `LICENSE` (MIT), `CONTRIBUTING.md`,
  `SECURITY.md`, issue templates (production bug / evidence problem / rule
  proposal), PR template, and a minimal credential-free CI
  (`.github/workflows/ci.yml`) that also runs the installer ownership/payload
  safety battery (including a `windows-latest` job for `install.ps1` when the
  repository is pushed).
- **removed the unused `skill.graph.json` manifest and its generator** — no
  runtime, installer, manifest or CI consumer existed; keeping it would have
  meant a regenerating build step for an always-stale, self-referential
  artifact.
- **public README rewrite** for first-time external users, plus this
  `CHANGELOG.md`.
- **privacy cleanup for public release** — documented in
  `audits/2026-09-08-public-release-redaction.md`. Machine-local absolute
  paths were normalized to repo-relative paths in one plain historical audit
  (non-hash-bound, kept normalized); the private ChatGPT conversation
  provenance URI was removed from `SKILL.md`. Ten review narratives and one
  hash-bound rollout were **not** rewritten: the reviews were restored to
  their original bytes after an interim normalization was recognised as a
  violation of review immutability (see "historical reviews restored"
  above), and the rollout stays byte-identical because its content hash is
  bound to a run record and run-bound review.

Behavioral-eval context that also post-dates the `v0.3.1` tag (Massive Eval
expansion + targeted verification, all on this branch):

- **Massive Eval expansion** — 60 new cases authored and frozen; **60/60
  first-run mechanism reviews PASS** under an independent, non-generating
  reviewer context.
- **Stability reruns** — 10 sensitive cases × 3 = 30 reruns; **3 Robustness
  Instability findings retained open**.
- **Targeted verification (post-hardening)** — 9 cases under the run-bound
  schema: **5 PASS / 3 PARTIAL / 1 FAIL**.
- **Eval contract problem** — `d1-price-gap-roi` marked **Eval Contract
  Problem** (internally inconsistent frozen input); flagged, not silently
  fixed.
- **Golden Candidates** — nominated only; **not auto-promoted**; no baseline
  was copied without human sign-off.

Test numbers are **not** product-effect guarantees. They describe mechanism
reviews of eval outputs under a fixed contract; see `README.md` §14 and
`evals/README.md`.

Additional pre-release fixes for installer correctness and honest
platform-verification labelling. This block covers the installer, packaging and
privacy round only; at the time it was written it introduced no
decision-methodology, evidence, or version change.

- **Native Cursor and Windsurf Skills** (`install.sh` / `install.ps1`): both
  clients now receive the complete Agent Skill in their documented native
  directories (`.cursor/skills/` and `.windsurf/skills/`). The old Rule
  conversion is no longer invoked, so references remain available through
  progressive disclosure and the installer never writes an unmanaged external
  rule file.
- **First-class WorkBuddy target**: both installers now accept `workbuddy` and
  place the complete package under `.workbuddy/skills/` (project) or
  `~/.workbuddy/skills/` (user). Codex, WorkBuddy, and Claude Code are tracked
  in a dedicated compatibility matrix.
- **Privacy boundary**: runtime instructions explicitly prohibit placing
  private intake or identifying student details into web searches or
  third-party tool queries. `PRIVACY.md` separates Skill behavior from Agent
  host retention and logging policies.
- **Copilot mis-detection** (`install.sh` / `install.ps1`): removed `.github`
  directory as a Copilot auto-detection signal — this repository itself ships a
  `.github`, so a user without `~/.claude` could be mis-identified as Copilot.
  Copilot is now detected only via `~/.copilot` or the Copilot CLI config.
- **README** (`README.md`): replaced the only result example (which used
  undefined tier labels and cited a nonexistent "Section 5") with a
  self-contained, mechanism-correct illustration; added a Chinese quick-start;
  replaced the absolute "no secrets" claim with a dated, scope-limited scan
  statement; replaced the flat "supports 17 platforms" claim with an explicit
  three-state table (installer-verified / legacy-adapter-unverified /
  best-effort). No platform is called end-to-end host verified until a real
  client run confirms discovery, invocation, reference loading and execution.
- **Dead Cursor/Windsurf rule-adapter removal** (`install.sh` / `install.ps1`):
  the now-unused Cursor `.mdc` and Windsurf rule generators (and their stale
  comments) were deleted, since both clients install the native SKILL.md
  package and the adapters are no longer invoked. Installer behavior is
  unchanged; the Unix safety battery still passes 37/37.
- **Self-consistent public snapshot docs** (`tools/snapshot_docs.py`, new):
  the snapshot build now rewrites the snapshot copies of `CONTRIBUTING.md`,
  `AGENTS.md`, the PR template and `SECURITY.md` so they reference only the
  files the snapshot ships — never the excluded `evals/` / `audits/` /
  `archive/` / provenance tree or the eval tooling. The development repository's
  full governance docs are untouched; only the public copies are adjusted.
- **Second Claude Code smoke run** (2026-09-09): an anonymous 985-CS
  UCL-vs-CUHK technical-return case was run after the `SKILL.md` privacy-rule
  addition and returned a mechanism-correct conditional answer, confirming the
  privacy rule does not break normal runs. WorkBuddy discovery is now confirmed
  in-session; Codex and WorkBuddy invocation/reference loading remain Pending.

Uncommitted decision-rule behavior changes in the same unreleased cycle
(2026-09-10). **Not yet behavior-verified** — no `freeze → blind record →
independent review` has been run against them, and the three new eval cases are
not frozen or reviewed. Rule text lives in its owners; this list is a changelog
index only.

- **Private-sector non-technical Major-Gate scope** — the Major Eligibility
  Gate is not applicable for broad private-sector non-technical roles; the full
  scope and its exceptions are owned by `references/path-private-sector.md`, the
  engine semantics by `references/core-decision-engine.md`.
- **Multi-offer hard-gate screening** — every offer is screened across the
  applicable gates before any shortlist is formed.
- **Operative-year cost calibration** — the maintained 2026 all-in planning
  baseline moved from core into `domain/priors-and-calibration.md`; core now
  makes reading it a precondition of any cost conclusion.
- **Lower-bound budget arithmetic** — confirmed tuition plus mandatory fees is
  a Total Cost lower bound; a range straddling the Absolute Ceiling is
  conditional/unresolved rather than pass.
- **Pre-output consistency check** — a mandatory pre-recommendation re-check
  over the active No-major role mode and the cost calibration.
- **Three new eval cases** — `priv-product-ops-major-cost-calibration`,
  `priv-seven-offer-soft-fit-budget-gate`, and
  `priv-user-no-major-four-offer-2026-cost` (case inputs and oracle contracts
  added; not yet frozen or reviewed).

## v0.3.1 — released 2026-09-07

- D1 bounded fallback fix (`fdc2d47`): missing employer-specific evidence does
  not imply recognition equivalence (`references/path-private-sector.md`).
- Full regression at release: 9/9 Golden + 4/4 D1 boundary PASS
  (`2813da6`).
- Metadata-only release commit (`e58966d`). `v0.3.0` tag untouched.

## v0.3.0 — released 2026-09-06

- Canonicalized decision engine (Stage 0–7, gates, evidence states,
  decision-sufficiency, score-state legality), four explicit paths
  (private-sector, SOE/public, local-stay/dual-track, PhD), labelled priors
  and calibration anchors, and the run-level eval governance.
- 9 golden baselines promoted; 0 blocking coverage gaps at release.

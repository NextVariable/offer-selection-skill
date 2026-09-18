# Compatibility

The first-class release targets are Codex, WorkBuddy, and Claude Code. This
matrix separates file installation from real host execution; a copied
`SKILL.md` is not by itself an end-to-end verification.

| Host | Native location | Installer test | Host discovery | Manual invocation | Reference loading | Researched answer |
|---|---|---:|---:|---:|---:|---:|
| Codex | `~/.agents/` | PASS (Unix) | PASS (Codex CLI 0.154.0-alpha.6.2) | PASS | PASS (core + private-sector path) | Not tested in current smoke (no live research) |
| WorkBuddy | `~/.workbuddy/` | PASS (Unix) | PASS (listed in WorkBuddy 5.5.4) | Pending — new-task Send remained disabled | Pending | Pending |
| Claude Code | `~/.claude/` | PASS (Unix) | PASS (2.1.260, headless) | PASS (current routing smoke, 2026-09-16) | PASS (current core + private-sector path); priors/skip observations are historical | Historical smoke PASS (2026-09-09); not revalidated for current runtime |

**Installer CI record (2026-09-16).** Linux and real `windows-latest` / `pwsh`
installer checks passed in [GitHub Actions run 35026787716](https://github.com/yunheliu68-ux/offer-selection-skill/actions/runs/35026787716)
for commit `9815eee7d044a7bd1352bbd55031d0e4a9557c98`. These checks validate
installation safety, not host invocation or decision behavior.

**skills CLI installation record (2026-09-18).** Copy installation to a
temporary macOS project passed for Codex and Claude Code. All seven runtime
files matched the local source. This check did not cover global installation,
Windows, or other hosts. The third-party CLI installs the skill directory,
including public documentation; the bundled installers copy only the fixed
runtime files. Installation success does not by itself verify host invocation.

**Claude Code verification record (2026-09-09, historical runtime).** Environment: macOS, Claude
Code 2.1.260, headless (`claude -p`). Observed end-to-end on two representative
cases: skill discovered and invoked; `references/core-decision-engine.md` loaded
plus the correctly activated `references/path-private-sector.md`;
`domain/priors-and-calibration.md` triggered by the internship-repair anchor;
`path-soe-public.md` / `path-local-stay.md` / `path-phd-academic.md` and the
never-load files (`internal/source-of-truth.md`, `internal/audits/`, `evals/`, `internal/archive/`)
correctly skipped; conditional, mechanism-correct answers returned on anonymous
UCL-vs-CUHK China-return comparisons (including one run after the `SKILL.md`
privacy-rule addition, which confirmed the privacy rule does not break normal
runs); and an unrelated programming question did not activate the skill. This is
**End-to-end smoke verified for representative cases**, not governed
behavioral verification or a regression against the full frozen contract.

**Codex host record (2026-09-16).** Codex CLI 0.154.0-alpha.6.2 ran a fresh,
read-only invocation against the current v0.3.2 install. It loaded the 149-line
slimmed `SKILL.md`, `references/core-decision-engine.md`, and
`references/path-private-sector.md`, skipped conditional priors that were not
triggered, and returned the expected conditional private-sector mechanism for
an explicitly hypothetical comparison. A stale legacy copy in
`~/.codex/skills/` was replaced through the managed installer before the
passing rerun. This is host/routing smoke verification, not governed behavioral
verification.

**WorkBuddy discovery record (rechecked 2026-09-16).** The current v0.3.2 skill
is installed at `~/.workbuddy/`, and WorkBuddy
5.5.4 lists the skill and its project. A fresh current-runtime task could not be
submitted because the new-task Send control remained disabled after selecting
the project, code mode, and an available free model. Invocation, reference
loading, and a current researched answer therefore remain Pending. The older
conversation is not accepted as current host verification.

`PASS` must name the environment and observable behavior. Do not promote a
Pending cell from documentation or path inspection alone. Record the host
version, operating system, date, exact anonymous prompt, and whether the host
loaded `references/core-decision-engine.md` plus the activated path file.

Other installer targets are compatibility conveniences. They remain
experimental until the same six checks pass: safe install, discovery, manual
invocation, automatic invocation, reference loading, and one researched answer
that respects evidence-state rules.

## What kind of change is this?

- [ ] Production rules change (owner: `SKILL.md` / `references/*.md` / `domain/priors-and-calibration.md`)
- [ ] Evidence / research correction
- [ ] Tooling or CI change (`tools/`, `.github/`)
- [ ] Docs / community / release metadata (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `.github/`, `.claude-plugin/`)
- [ ] Installer change (`install.sh`, `install.ps1`)

## Checklist

- [ ] The change fixes a stated problem, not a symptom. A FAIL in the evidence
      suite is a signal to investigate, not a license to change rules.
- [ ] If this is a **production** change: it modifies a rule only in its owner
      file, and any Domain Methodology change is backed by an explicit
      maintainer decision (see `CONTRIBUTING.md`).
- [ ] No fixed weights, country/school scores, prestige bonuses, or
      test-case special branches were added. No dynamic fact was hard-coded
      into the rules.
- [ ] No history was rewritten or deleted to make a result look better.
- [ ] No real student private material (names, grades, offer letters,
      student IDs, emails, financial details) was added.
- [ ] Verification re-run and reported in the PR description:
      `python3 tools/check_frontmatter.py`, `bash -n install.sh`,
      `bash tools/test_installer.sh`.

## Problem

<!-- What is wrong or missing, with evidence. Keep it anonymous. -->

## Change

<!-- What you changed and why this is the right layer for the change. -->

## Verification

<!-- Paste the verification output / test summary. -->

## Notes for the maintainer

<!-- Any open design decision or maintainer sign-off needed. -->

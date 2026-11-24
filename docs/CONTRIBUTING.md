# Contributing to offer-selection-skill

Thanks for considering a contribution. This project is an evidence-driven Agent
Skill for deciding which postgraduate offer — if any — is worth accepting for a
specific student and goal. It is deliberately small in decision machinery and
large in governance, because the domain (money, career, student wellbeing)
punishes guesswork.

Please read `README.md` first, then this file, then the files it links to.

## What the project solves

School-ranking tools answer "which school is best in the abstract". This skill
answers a narrower question: **which offer, if any, is right for this user and
this goal**, using eligibility gates, graduation-profile transformation,
target-market competitiveness, total cost, ROI, risk, and the user's stated
preferences. It refuses to invent precision where evidence is unresolved.

## Normative-owner model

One rule has one owner. Do not duplicate a rule to "improve" it somewhere else;
change it in its owner:

| File | What it owns | When it is read |
|---|---|---|
| `skills/offer-selection-skill/SKILL.md` | Intake, load order, output contract, gotchas | Every run |
| `skills/offer-selection-skill/references/core-decision-engine.md` | **The execution semantics** — Stage 0–7, gates, evidence states, decision sufficiency, research priority/stop, scoring, equivalence | Every run |
| `skills/offer-selection-skill/references/path-{private-sector,soe-public,local-stay,phd-academic}.md` | Path-specific business rules | When that path activates |
| `skills/offer-selection-skill/references/priors-and-calibration.md` | Labelled conditional priors and calibration anchors | Only when a prior trigger fires |

The public repository carries the runtime package, public documentation,
synthetic examples, installers, and deterministic verification. Maintainers keep
private provenance, raw behavioral evidence, and experimental assets separately.
See `AGENTS.md` for the authority model.

## What you may change

- **Production files** (`skills/offer-selection-skill/SKILL.md`, `skills/offer-selection-skill/references/*.md`,
  `skills/offer-selection-skill/references/priors-and-calibration.md`, installers): only with a clear problem
  statement and, for decision-semantics changes, an explicit maintainer
  decision. See "Domain Methodology changes" below.
- **Installers** (`install.sh`, `install.ps1`): keep the runtime allowlist
  and the ownership-marker invariants intact (see the installer tests).
- **Community/legal files** (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`,
  `LICENSE`, `.github/`): normal review applies.

## Domain Methodology changes need an explicit maintainer decision

The project deliberately **forbids** these unless the maintainer makes an
explicit, recorded decision to change the methodology:

- fixed weights or point systems;
- fixed country/school scores or prestige bonuses;
- ranking-to-score mappings;
- "cheaper is better" or "name brand is better" shortcuts;
- special branches written to make one test case pass;
- hard-coding dynamic facts (tuition, ranking, visa rules, employer policy,
  credential rules, graduation policy) into the rules.

Dynamic facts must be re-researched for the current cycle at runtime; they are
evidence, not rules.

## Never change rules to make tests green

A wrong result is a signal. The correct response is to find out *which* rule
is wrong, write it up, and only then — if the production rule is genuinely at
fault — change the rule's owner. Changing rules to chase a green status is the
project's cardinal sin.

## How to run verification

```bash
# skills/offer-selection-skill/SKILL.md frontmatter compliance
python3 maintenance/check_frontmatter.py

# decision engine, Harness and release contract (Python 3.10+, standard library)
python3 -m unittest discover -s maintenance

# offline end-to-end with the public frozen fixture
bash docs/examples/v2-harness/codex-e2e.sh

# installers: syntax, dry-run, and the full safety battery
bash -n maintenance/install.sh maintenance/test_installer.sh
./maintenance/install.sh --dry-run --platform universal
bash maintenance/test_installer.sh
```

CI runs the deterministic suites and installer checks on PRs
(`.github/workflows/ci.yml`). The end-to-end example is a local replay. Native
host acceptance is recorded separately in [COMPATIBILITY.md](COMPATIBILITY.md).
The public runtime needs no repository-specific credentials or dependency
lockfile. Keep private case JSON, research notes, and logs outside the
checkout or under a local `.offer-selection-work/` directory.

## Filing issues

Two issue templates ship in `.github/ISSUE_TEMPLATE/`. Please use the one
that matches and keep the categories distinct:

- **Usage problem** (`bug_report.yml`) — installation, invocation, research,
  or analysis issues. Users do not need to diagnose the internal cause.
- **Improvement suggestion** (`rule_proposal.yml`) — suggest better usage
  or analysis. Methodology changes require maintainer approval.

Keep reports anonymized. Maintainers classify the underlying cause;
users are not required to diagnose rule ownership or test contracts.

## Pull requests — minimum requirements

- **Do not commit real students' private material**: no names, grades, offer
  letters, student IDs, emails, or financial details. Keep any example you
  add synthetic and anonymized.
- Keep dynamic facts out of the rules (research them, don't hard-code them).
- Every PR: explain the problem, the change, and — for production changes —
  why this is a rule-owner change rather than a test fix. Re-run the
  verification commands above and report the results.
- Keep the commit history linear and the change set focused; prefer several
  small PRs over one large one.

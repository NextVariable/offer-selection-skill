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

The public repository carries only the runtime files above. The maintainers'
development history (behavioral evidence, audits, provenance) is intentionally
not part of this repository. See `AGENTS.md` for the full authority model.

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
python3 tools/check_frontmatter.py

# installers: syntax, dry-run, and the full safety battery
bash -n install.sh tools/test_installer.sh
./install.sh --dry-run --platform universal
bash tools/test_installer.sh
```

CI runs these checks on every PR (`.github/workflows/ci.yml`). It never runs
LLM evals, never calls paid APIs, and needs no secrets.

## Filing issues

Two issue templates ship in `.github/ISSUE_TEMPLATE/`. Please use the one
that matches and keep the categories distinct:

- **Production bug** (`bug_report.yml`) — the skill gave a wrong decision
  because the rules are wrong. Do not open this for a one-off model wobble.
- **Rule proposal** (`rule_proposal.yml`) — a proposed change to decision
  methodology (requires the explicit maintainer decision above).

A wrong result or a one-off model wobble is **not** by itself grounds for a
production change; say which category an observation falls into rather than
forcing every wrong result to look like a Production bug.

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

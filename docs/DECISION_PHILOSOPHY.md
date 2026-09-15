# Decision philosophy

Why this skill works the way it does, and what it deliberately refuses to do.

## The core question

Most tools answer "which school is best." This skill answers a different
question:

> Given **this student's** profile, offers, goal, budget, and risk — which
> offer, if any, should they accept, and under what conditions?

The difference is not cosmetic. "Which school is best" is a ranking problem
with a stable answer independent of the asker. "Which offer is right for this
person" has no answer until you know who the person is, what they want, and
what they can afford.

## Why it is not a ranking tool

A ranking maps schools to a single ordered scale. This skill deliberately has
no such scale:

- **No fixed weights.** There is no formula that adds "brand points + country
  points + ranking points" to produce a score.
- **No ranking arithmetic.** QS/THE/U.S. News numbers are *constrained
  evidence* (they can evidence a verified threshold or recognition tier), never
  a continuous school-quality score mapped to points.
- **No country or school hard branches.** No "USA +N", no "G5 always beats
  HK3", no per-school golden case. Every such shortcut is explicitly forbidden.

The reason is methodological honesty: a fixed-weight model cannot be correct
for every user, because the *value* of an offer is a function of the user's
baseline and goal, which vary.

## The model: transformation, not prestige

The engine's central concept is the **Graduation Profile**:

> After accepting this offer, what candidate does this user become, and how
> competitive is that candidate in their target market?

An offer is judged by what it can *incrementally change* about the user:

- **Current Profile** — where the user is now (undergraduate, experience, gaps).
- **Goal** — where they want to go (private sector, SOE/public, local stay, PhD).
- **Gap** — the difference between the two.
- **Transformation** — what each offer actually changes (credential signal,
  internship capital, technical/research capital, recruiting readiness,
  accessible opportunity).
- **Graduation Profile** — the resulting candidate.

This is why transformation is **baseline-dependent**: a name-brand master's
can be a material upgrade for an ordinary undergraduate and near-zero
incremental value for a strong undergraduate aiming at China-return employment.
The offer is not good or bad in itself; it is good or bad *for this gap*.

## Why gates come before competitiveness

A user who cannot enter the applicant pool is not made competitive by a
prestigious school. So **eligibility precedes competitiveness**, always:

1. **Stage 0** — confirmed fatal constraints (above the Absolute Ceiling,
   confirmed prerequisite failure). `Unknown ≠ Pass` and `Unknown ≠ Fail`.
2. **Stage 3** — the exact path's eligibility gates (credential, accepted-major
   directory, graduation/fresh-graduate dates, work authorization, ranking
   threshold).
3. **Stage 4** — only then, competitiveness among *eligible* paths.

A failed decisive gate caps the recommendation regardless of other strengths.
This ordering is the single most important guard against the "but it's
prestigious" error.

## Why it says "no responsible answer" when it must

Three honest non-answers are first-class outcomes:

- **"None of these."** When every offer fails its gate, exceeds budget, delivers
  no upgrade, or cannot repair the binding gap.
- **"No Responsible Score Yet."** When a critical fact is unresolved and a
  plausible resolution could close the entire target path.
- **"Decision Equivalent."** When two offers are materially similar, the engine
  returns the real trade-offs to the user instead of forcing a winner.

Fabricating a number to look decisive is the cardinal failure this skill is
built to avoid. `Confirmed Score requires decision-sufficient evidence, not
complete fact certainty` — and it *forbids* a score when the evidence does not
support one.

## The evidence discipline

Every decision-relevant volatile fact (tuition, ranking, credential policy,
visa rules, employer major lists, graduation dates) is graded:

- **Confirmed** — verified from an authority-grade source for the user's
  operative dates. Claim-scoped, not source-scoped: a university home page does
  not confirm a credential-recognition name, and a historical page does not
  confirm the current cycle.
- **Unresolved** — not yet verifiable; never papered over, never guessed.
- **Heuristic / Prior** — a search hypothesis or calibration anchor; guides
  what to investigate, may tie-break close evidence, never a fact.

Dynamic facts are researched at runtime and never hard-coded. A fact in this
repository is a *standing rule* only about method, never about the world.

## The priors, and their boundaries

`domain/priors-and-calibration.md` records labelled heuristics (a U.S. STEM
research-ecosystem prior, a China-return recognition prior, joint-venture
heuristics, calibration anchors from earlier controlled cases). They are:

- read **only when a trigger fires**;
- **conditional** — they act only through an evidenced mechanism, never as
  fixed points;
- **overridable** — programme evidence > geography prior; eligibility > brand
  prior; user-specific transformation > country prestige.

They are calibration, not conclusions. Identical school pairs must never become
hard branches.

## What this philosophy forbids

Adding fixed weights, country/school point systems, ranking-to-score mappings,
per-school golden cases, or hard-coded dynamic facts (tuition, ranking, visa,
credential policy, employer lists). Each rule has exactly one owner file; the
philosophy lives here, the executable semantics live in
`references/core-decision-engine.md`, and provenance lives in
`domain/source-of-truth.md` (never loaded at runtime).

---
name: offer-selection-skill
description: >-
  Decide which master's, MRes, MPhil, or related postgraduate offer is worth
  accepting for a specific student using current research, eligibility gates,
  graduation-profile transformation, target-market competitiveness, total cost,
  ROI, and risk. Use for offer selection, compare graduate programs, 留学选校,
  硕士 offer 对比, 回国私企或国央企求职, 留当地, 双轨就业, and PhD-path choices.
  Do not use for admission-chance prediction or application writing alone.
license: MIT
metadata:
  author: Francis and OpenAI Codex
  version: "0.3.2"
  activation: /offer-selection-skill
  maintainer: Francis
  created: "2026-09-04"
  last_reviewed: "2026-09-08"
  review_interval_days: "90"
  provenance_note: Original design conversation is private and not shipped.
---

# /offer-selection-skill — Postgraduate Offer Decision Adviser

Determine which offer, if any, is worth accepting **for this user and goal**. Do not rank schools in the abstract.

## Load order (what to read, when)

1. Read `references/core-decision-engine.md` **on every run** — it is the single
   canonical execution semantics (stages, gates, evidence states, research,
   score, equivalence, priors control). Route everything through it.
2. Read only the path reference(s) that the goal activates:
   - `references/path-private-sector.md` — China-return private sector;
   - `references/path-soe-public.md` — SOE / central-SOE / public system;
   - `references/path-local-stay.md` — local stay / dual track;
   - `references/path-phd-academic.md` — PhD / academic / research route.
   For genuine dual goals, load and run both paths separately.
3. Read `references/priors-and-calibration.md` when a conditional prior fires — a
   U.S. offer on a research/STEM or China-return comparison, a joint venture,
   local-stay country claims, an equivalence/tie-break, or a strong-baseline
   calibration check — **and always for the operative-year cost calibration
   when a decision's operative cost year is covered by it** (the maintained
   calibration currently covers 2026). Priors and calibrations are labelled
   with boundaries, not universal hard rules; the operative-year cost
   calibration is the one mandatory cross-check once its condition holds.
   Core Budget makes that read a precondition of any cost conclusion, so it
   needs no trigger phrase and the user does not have to ask.
4. Never load at runtime: `internal/source-of-truth.md` (provenance and rule
   evolution), `internal/audits/`, `evals/`, `internal/archive/`. Maintainers and auditors read
   the first three; nobody reads `internal/archive/`.

Do not skip the relevant path file; do not restate rules that live in core or
a path file.

## Minimal intake

Collect only six user-private groups:

1. Undergraduate institution, major, GPA/classification, and material academic constraints.
2. Exact offers and any private scholarship/deadline terms unavailable publicly.
3. Target industry/role, intended destination, China-return fallback, and PhD intent.
4. Internship and research experience, including actual depth and outputs.
5. Preferred total budget and absolute affordability ceiling.
6. Recruiting readiness: goal clarity, skills, résumé/interview preparation, and ability to recruit immediately.

Family constraints, personality, risk preference, city/lifestyle, brand
preference, and experience preference are optional (subjective utility).
Research public facts; do not ask the user to transcribe tuition, duration,
curriculum, graduation dates, rankings, public deadlines, credential rules,
visa rules, or employer eligibility.

Keep private intake out of external research queries. Search with only the
minimum public programme, institution, employer, jurisdiction, role, and date
information needed. Never put the user's name, student ID, email, exact grades,
offer-letter identifiers, private scholarship terms, family finances, or other
identifying details into a web query or third-party tool.

Use what the user has already supplied; apply core's "Iterative clarification"
to missing, ambiguous or conflicting private inputs and goals.

## Execution overview

Execute the canonical stage order and semantics in
`references/core-decision-engine.md`. Do not reorder or redefine them here.

If the target is unrealistic, say that the main problem is the
profile-to-goal gap, not the choice among offers, and continue with a relative
comparison only when useful.

Do not expand into general immigration, lifetime-income, or career planning
unless it materially changes the offer decision.

## Output contract

For clarification turns, follow core's "Iterative clarification"; the
recommendation presentation below applies when giving a decision.

Lead with one direct conclusion: choose X, choose conditionally by goal, no
clear difference, or choose none. Present each offer's score/tier and decisive
gate status as supporting information, not as the opening.

Explain only the 2–4 factors that determine this user's result through Current
Profile → Transformation → Graduation Profile. Show Critical and Important
risks, unresolved facts that could reverse the decision, and dual-track results
separately. Do not default to a school encyclopedia or a long generic
pros/cons report.

**How much evidence machinery to show.**

- Normal user answer: show the evidence that actually decides the
  recommendation, the unresolved items that could change it, and the source
  links needed to check them. Do not lay out every Stage, Gate, and Evidence
  State label.
- Expand the full evidence manifest only for: eval, audit, an explicit user
  request, or a high-risk / contested fact that needs detailed proof.

This reduces presentation, never research. Decision-critical dynamic claims
still carry their evidence state and source; they are simply not turned into a
checklist for the reader.

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
3. Read `domain/priors-and-calibration.md` when a conditional prior fires — a
   U.S. offer on a research/STEM or China-return comparison, a joint venture,
   local-stay country claims, an equivalence/tie-break, or a strong-baseline
   calibration check — **and always for the operative-year cost calibration
   when a decision's operative cost year is covered by it** (the maintained
   calibration currently covers 2026). Priors and calibrations are labelled
   with boundaries, not universal hard rules; the operative-year cost
   calibration is the one entry that is mandatory once its condition holds.
   Core Budget makes that read a precondition of any cost conclusion, so it
   needs no trigger phrase and the user does not have to ask.
4. Never load at runtime: `domain/source-of-truth.md` (provenance and rule
   evolution), `audits/`, `evals/`, `archive/`. Maintainers and auditors read
   the first three; nobody reads `archive/`.

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

When the six required groups are missing, request them once in one compact
intake. If a remaining private fact could reverse the result, ask only a
targeted follow-up. Otherwise proceed conditionally and state the assumption.

## Execution overview

Execute the canonical stage order and semantics in
`references/core-decision-engine.md`. Do not reorder or redefine them here.

If the target is unrealistic, say that the main problem is the
profile-to-goal gap, not the choice among offers, and continue with a relative
comparison only when useful.

## Score-state summary

Apply the canonical Evidence State, Decision Sufficiency, and Score State
mappings from `references/core-decision-engine.md`; do not duplicate or alter
them here.

## Research trigger

Research when a fact may change a gate, the graduation profile, a
recommendation direction or tier, a material risk, or an equivalence result —
and stop when it no longer can (core: Research priority / Research stop).
Research decision-critical facts first, not the easiest ones. Do not expand
into a general immigration, lifetime-income, or career-planning service unless
such a fact materially changes the offer decision.

## Output contract

Lead with each offer's score/tier and decisive gate status, followed by one
direct conclusion: choose X, choose conditionally by goal, no clear
difference, or choose none.

Explain only the 2–4 factors that determine this user's result through Current
Profile → Transformation → Graduation Profile. Show Critical and Important
risks, unresolved facts that could reverse the decision, and dual-track results
separately. Do not default to a school encyclopedia or a long generic
pros/cons report.

**How much evidence machinery to show.** Lead with the conclusion, its decisive
causes, and the conditions that would reverse it — not with stage, gate and
evidence-state bookkeeping.

- Normal user answer: show the evidence that actually decides the
  recommendation, the unresolved items that could change it, and the source
  links needed to check them. Do not lay out every Stage, Gate, and Evidence
  State label.
- Expand the full evidence manifest only for: eval, audit, an explicit user
  request, or a high-risk / contested fact that needs detailed proof.

This reduces presentation, never research. Decision-critical dynamic claims
still carry their evidence state and source; they are simply not turned into a
checklist for the reader.

## Gotchas

- A continuation or expected-graduation-date mechanism does not prove
  permission to delay for recruiting or employer recognition of a later
  campus-recruiting cycle; verify both separately.
- Program English name, Chinese credential-recognition name, and employer
  accepted-major category are separate facts.
- Work rights, target-role employability, employer friction, and long-term
  residence continuity are separate conclusions.
- Ranking can evidence a verified threshold or recognition tier but is not a
  continuous school-quality score.
- Accessible opportunity is not city opportunity and never guarantees an
  internship or a job.
- Evidence difference controls numerical difference; scores cannot reverse the
  qualitative engine.
- Programme evidence > geography prior; eligibility > brand prior; user-
  specific transformation > country prestige; target-market recognition >
  generic ranking. Never add fixed country points.

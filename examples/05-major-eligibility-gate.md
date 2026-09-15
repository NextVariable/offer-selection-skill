# Example 05 — Major eligibility met vs. not met

## Setup

- Goal: a role with an explicit accepted-major directory (e.g. a regulated
  SOE or public-system position).
- Offers: **School A** and **School B**.

### Sub-case A — major eligibility met

Both offers' Chinese credential-recognition names fall inside the accepted-major
directory. The engine proceeds to compare target-market competitiveness.

### Sub-case B — one offer fails the major gate

School A's programme name / 学科大类 is not in the employer's accepted-major
directory (or is unresolved with a plausible adverse resolution). School B
qualifies.

## Expected behavior

A **failed decisive gate caps the path recommendation** for School A regardless
of its other strengths (brand, cost, ranking). "Passing allows competition; it
does not imply competitiveness" — and failing the gate removes School A from
competition for this path entirely.

If the major category is **unresolved** and could plausibly close the entire
target path, the engine reports **No Responsible Score Yet** for that path (or
a conditional recommendation with explicit branches), never a confirmed
numeric score.

## What this is NOT

- Not "School A is a bad school." It is ineligible *for this specific employer
  path*; it may be perfectly viable on another path.
- Three-name separation is mandatory: programme English name ≠ 留服 recognition
  name ≠ employer accepted-major category. The engine treats them as separate
  facts and states which are verified.

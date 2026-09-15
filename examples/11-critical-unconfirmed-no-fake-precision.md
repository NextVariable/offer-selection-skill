# Example 11 — Critical facts unconfirmed: no fake precision

## Setup

- Offers: **School A** and **School B**.
- Goal: a specific SOE / employer path where graduation timing or an
  accepted-major directory determines whether the user may apply **at all**.

The decisive fact — e.g. whether the user's expected graduation date qualifies
for the target employer's fresh-graduate / campus cycle — cannot yet be
verified for the user's operative dates.

## Expected behavior

This is **Critical uncertainty** (a plausible adverse resolution closes the
entire target path), so the engine reports **No Responsible Score Yet** — or,
if a recommendation is still required, a **conditional recommendation with
explicit branches**, stating precisely how each unresolved fact could reverse
the result.

It does **not** emit a false-precision integer. `Confirmed` is claim-scoped:
a university page does not establish an exact credential-recognition name, and
a historical page does not establish the current cycle. The engine must not
paper over the gap with a number.

## Path Closure Test

Criticality is path-relative. The same graduation-timing fact is:

- **Critical** on a path where it determines eligibility for the *only* target
  applicant pool the user is aiming at (e.g. a specific SOE/employer cycle).
- **Material** (not Critical) on a broad private-sector return-China path where
  losing one recruiting window still leaves viable alternatives open — there
  the engine may score with a Provisional Tier instead of refusing to score.

## What this is NOT

- Not "never give any answer when uncertain." The rule is: never give a
  *false-precision* answer. A conditional recommendation with explicit reversal
  branches is a responsible answer.
- Not symmetric downgrading: a fact that closes the path for *both* offers
  equally stays Critical at the path level; it is not demoted to Material just
  because it is common to both.

## Lesson

`Confirmed Score requires decision-sufficient evidence, not complete fact
certainty.` The engine targets decision value, not fact completeness — and when
the unresolved fact can close the path, it refuses to fake a number.

# Example 10 — All offers not recommended

## Setup

- Offers: **School A**, **School B**, **School C** — all ordinary, none repair
  the user's binding gap, none deliver a material upgrade, and/or all exceed
  the user's budget for the value they provide.

## Expected behavior

"Choose none" is a **valid outcome**, and so are its siblings: work-first,
take a gap to repair the gap, reapply, continue applying, or change the target.
The engine says plainly when every offer is weak — low ROI, no transformation,
over budget, or cannot repair the binding gap — rather than crowning the
least-bad option with an inflated score.

"Having only two ordinary offers does not make the better one a 90." The best
available offer can still be **not recommended**.

## What this is NOT

- Not a forced ranking of the available set. The engine does not normalize the
  "best" offer up to a strong tier just because it is the best on the table.
- Not fatalism: the engine explains *why* none is recommended (which gap is
  unrepairable, which gate fails, which ROI is negative) and what the realistic
  alternatives are.

## Lesson

The honest answer to "which offer should I take" is sometimes "none of these —
here is the alternative that actually fixes your problem."

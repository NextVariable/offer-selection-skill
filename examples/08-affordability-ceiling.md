# Example 08 — Affordable vs. above absolute ceiling

## Setup

- Offers: **School A** (within the Target Budget) and **School B** (materially
  above the student's Absolute Ceiling).

## Expected behavior

`Total Cost = tuition + living + mandatory fees + duration cost + necessary
opportunity cost − scholarship/grant`.

- **Affordable case**: when both offers fit, the engine asks what the
  incremental cost buys (credential threshold, recruiting pool, internship
  access, work rights, network) — it does **not** default to "cheaper is
  better."
- **Above-ceiling case**: when confirmed figures place School B materially
  above the Absolute Ceiling, the Budget Gate **fails**, which is fatal in
  Stage 0 when the figures are confirmed. The engine caps School B's
  recommendation regardless of its brand.

Exceeding the Target Budget (but not the ceiling) requires a **premium-value
explanation** — the engine must show what the extra cost concretely buys.

## What this is NOT

- Not "expensive = bad" or "cheap = good." Budget Gate and ROI are separate
  analyses and must not be double-counted.
- If the figures are *unresolved* rather than confirmed, the engine does not
  guess at Stage 0 (`Unknown ≠ Fail`). It carries the uncertainty forward as an
  unresolved fact with the reversal branch stated.

## Lesson

Affordability is a hard gate, not a scoring input; ROI is judged *after* the
gate passes, on incremental value, never on price alone.

# Example 06 — Local stay vs. dual track

## Setup

- Offers: **School A** (strong for a China-return brand) and **School B**
  (stronger local post-study work access and local employer recognition).
- Student goal: **dual track** — try to stay locally, with a China-return
  fallback.

## Expected behavior

Country feasibility **precedes** offer comparison, and the two tracks are run
**independently**:

- **Local track**: School B leads if it offers lawful and usable post-study work
  access, target-role employability, lower employer friction, and longer-term
  continuity — while School A's local-stay route is high-risk or implausible.
- **China-return track**: School A may lead on China-facing recognition and
  credential transformation.

The engine reports **two outcomes**, preserves the fallback/option value, and
does **not** blend them into one number unless the user supplies a priority. If
one offer is better for the first local job while the other is better for
long-term residence, the engine explains both mechanisms and asks which
objective controls.

## What this is NOT

- Not "stay locally is always better" or "return is always safer." The
  four-part local feasibility (work access → employability → employer friction
  → continuity) is assessed, and "work rights ≠ employability ≠ long-term
  stay."
- Not a country score. A generous visa window is not a job outcome.

## Strong local-stay variant

If the user's goal is *strong local stay only* and every offered path is
high-risk or implausible, the engine challenges local stay as the sole
criterion and states that conclusion directly, adding a China-return fallback
instead of forcing a least-bad country winner.

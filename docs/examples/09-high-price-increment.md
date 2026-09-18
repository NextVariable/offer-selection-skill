# Example 09 — High-price program: does it buy an increment?

## Setup

- Offers: **School A** — a high-cost, high-brand program in a global city;
  **School B** — a substantially cheaper program whose target-market outcome is
  materially the same tier.

## Expected behavior

When both are affordable, the engine asks the decisive question: **what does
the incremental cost actually buy for this user?** If School A's price premium
buys no material difference in target-market competitiveness (same credential
tier, no extra internship access, no better recruiting pool, no work-rights
gain), then School B has the higher career ROI and the engine says so.

If School A's premium *does* buy something material (a credential threshold
the user needs, an accessible internship pipeline, a recruiting pool the user
can actually convert), the engine credits that increment and School A can win.

## What this is NOT

- Not "expensive is a waste" or "name brand is always worth it." The judgment
  is strictly incremental-value-for-this-user.
- The city/location/network/lifestyle differences that remain after the ROI
  comparison are handed back as **subjective utility** — they cannot be decided
  by price alone, and the engine does not silently pick for the user.

## Lesson

ROI is judged on *incremental* value, and a price premium must be tied to a
concrete, accessible increment to count. Anti-double-counting: the same brand
benefit must not be credited twice (once as "reputation" and again as "city
premium").

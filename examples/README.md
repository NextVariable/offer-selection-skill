# Public behavior examples

These cases illustrate the *mechanisms* the decision engine is designed to
produce, not canned winners. Every case is **synthetic and anonymized**: no
real student, transcript, offer letter, identifier, or financial record is
used, and no specific school is hard-coded as a winner.

Each example isolates one counterfactual — change a single input and watch the
engine respond differently. That is the property being demonstrated, not the
specific schools, which are placeholders for "a same-tier brand pair" and can
be swapped without changing the lesson.

How to read a case:

- **Setup** — the student's profile, offers, and goal.
- **Expected behavior** — the mechanism the engine must express (the *why*).
- **What this is NOT** — the boundary that must not be crossed (e.g. no fake
  numeric gap, no school ranking arithmetic, no invented certainty).

These are not regression oracles and are not bound to any frozen run. They are
plain-language illustrations of the methodology documented in
`references/core-decision-engine.md`. The governed behavioral evidence lives in
`evals/` and is not shipped in the public release.

## Index

| # | Case | Mechanism demonstrated |
|---|---|---|
| 01 | Zero internships, China-return private sector | Accessible internship repair can outweigh a same-tier brand gap |
| 02 | Strong internships, same offers | Repair value collapses; outcome moves toward equivalence |
| 03 | Ordinary vs. strong undergraduate | Transformation is baseline-dependent; no automatic credential upgrade |
| 04 | Private-sector → SOE goal switch | The real employer gate comes first; brand cannot compensate a failed gate |
| 05 | Major eligibility met vs. not met | A failed decisive gate caps the path recommendation regardless of other strengths |
| 06 | Local stay vs. dual track | Country feasibility precedes offer comparison; two tracks show two outcomes |
| 07 | Employment vs. PhD | Research transformation can outweigh overall brand for committed PhD intent |
| 08 | Affordable vs. above absolute ceiling | Exceeding the Absolute Ceiling fails the Budget Gate; cheapest is not automatically best |
| 09 | High-price program — does it buy an increment? | Ask what the incremental cost buys, not whether it is "worth it" in the abstract |
| 10 | All offers not recommended | "Choose none" / reapply / change-target are valid outcomes |
| 11 | Critical facts unconfirmed | No Responsible Score Yet; conditional recommendation, never a fake-precision integer |
| 12 | Unrelated question | The skill must not activate for out-of-scope requests |

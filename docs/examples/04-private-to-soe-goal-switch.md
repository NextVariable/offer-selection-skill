# Example 04 — Private-sector → SOE goal switch

## Setup

- Offers: **School A** — a strong-brand management master's; **School B** — a
  finance/accounting master's whose title looks more "orthodox."
- Same student, two goals compared.

### Goal A — private-sector product role

Brand and internship access are the dominant levers; the exact degree title and
credential-recognition name matter far less.

### Goal B — SOE / central-SOE / public-system role

The **real employer's hard gate** comes first: degree-awarding institution,
留服 recognition, accepted-major directory (学科大类), school/ranking list, and
fresh-graduate dates. A stronger brand that cannot enter the applicant pool is
worthless there.

## Expected behavior

The winner can flip when the goal flips:

- If School B qualifies for the target employer's accepted-major directory
  while School A does not, the engine prefers School B **regardless of School
  A's brand**.
- If **both** qualify, the engine does not award a large premium merely because
  one title looks more orthodox; it requires training or employer-outcome
  evidence before declaring a gap.
- If the two offers fail **different** decisive gates, the engine recommends
  **neither**.

## What this is NOT

- Not "major/credential always beats ranking." The superseded heuristic is
  "whatever the real employer uses as a hard gate comes first." The engine
  researches the actual gate, not a prestige proxy.
- Brand can compensate a *competitiveness* weakness, never a failed
  *eligibility* gate.

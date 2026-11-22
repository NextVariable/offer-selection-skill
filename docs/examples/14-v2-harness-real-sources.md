# Example 14 — v2 harness on real sources: conditional choice under a cost gap

## Setup

- **Offers:** Warwick MSc Marketing & Strategy (2027 entry) and Glasgow
  International Strategic Marketing MSc (2027-28).
- **Profile (synthetic):** China business bachelor (2.1 equivalent), one
  marketing internship, IELTS 7.0.
- **Goal:** marketing in a China private company; no PhD intent.
- **Budget:** absolute ceiling GBP 56,000; target GBP 53,000; living cost is a
  user-provided GBP 15,000 all-in estimate.
- **Operative year:** 2027.

Execution disclosure: this run used the **Trae Agent fallback host with
DeepSeek-V4.1-Flash** on 2026-11-23. It is **not** a native Codex or Claude Code
acceptance run; those remain **Not Run** (see
[COMPATIBILITY.md](../COMPATIBILITY.md)).

## Real sources and the claim each one supports

| Evidence | Claim | Source (opened) | Applicability |
|---|---|---|---|
| `e_w_tuition` | 2027 entry EU/International tuition is GBP 39,500, one year full-time | <https://www.wbs.ac.uk/courses/masters/marketing-and-strategy/> | 2027 entry, international, UK |
| `e_g_tuition` | 2027-28 International & EU full-time tuition is GBP 34,815, 12 months | <https://www.gla.ac.uk/postgraduate/taught/internationalstrategicmarketing/> | 2027-28, international, UK |
| `e_w_entry` | At least a 2.1 or overseas equivalent; all academic fields welcome; IELTS 7.0 with component minima | <https://www.wbs.ac.uk/courses/masters/marketing-and-strategy/requirements/> | 2027 entry |
| `e_g_entry` | 2.1 Hons or non-UK equivalent in Business Management/Marketing/Commerce; IELTS 6.5, no subtest below 6.0 | <https://www.gla.ac.uk/postgraduate/taught/internationalstrategicmarketing/entryrequirements/> | 2027 entry |
| `e_w_programme` | One year full-time, Warwick campus, September 2027 start, applications due 2 August 2027 | <https://www.wbs.ac.uk/courses/masters/marketing-and-strategy/requirements/> | 2027 entry |
| `e_g_programme` | 12 months full-time, September teaching start, Gilmorehill campus | <https://www.gla.ac.uk/postgraduate/taught/internationalstrategicmarketing/> | 2027 entry |
| `e_w_brand` | QS Business Masters 2027: 1st in UK, 6th globally; QS 2026 top 25 for Marketing | <https://www.wbs.ac.uk/courses/masters/marketing-and-strategy/> | 2026-2027 rankings |
| `e_g_brand` | QS Business Masters 2027 top 70; CIM accredited; triple-accredited business school | <https://www.gla.ac.uk/postgraduate/taught/internationalstrategicmarketing/> | 2026-2027 rankings |

Every confirmed claim carries a `period` (2026-01-01 → 2027-12-31) and a source
that was actually opened with a paragraph locator. The harness treats these as
confirmed **only** because the source inspection reports `access: opened` and
`support: supported`.

## What stays unresolved

- `e_w_china` / `e_g_china` — whether target China private-sector employers treat
  these exact programmes as a preferred credential. No employer-side source was
  opened, so both remain **unresolved** and are shown under 待核实. The engine
  does not convert "school says it is ranked" into "employer prefers it".

## Computed result (money in GBP minor units)

| Offer | Tuition | Living (user) | Cash | Ceiling GBP 56,000 | Target GBP 53,000 |
|---|---|---|---|---|---|
| Warwick | 3,950,000 | 1,500,000 | 5,450,000 | pass | **fail** (over by 150,000) |
| Glasgow | 3,481,500 | 1,500,000 | 4,981,500 | pass | pass |

Both eligibility gates pass against the synthetic profile: Warwick accepts any
field at 2.1 with IELTS 7.0; Glasgow requires a business/marketing/commerce 2.1
with IELTS 6.5.

Decision: **conditional**, default **Glasgow**; Warwick only becomes preferred
if the employer signal justifies the ~GBP 1,500 target overrun or the user
raises the target to at least GBP 54,500.

## Quick / Full and counterfactual

- The Quick report is a strict prefix of the Full report — both render from the
  same validated decision document, so they cannot diverge.
- `harness.scenario({"field": "ceiling", "value": 5300000})` re-runs only
  budget/gates/competitiveness/value/recommendation, reuses all ten evidence
  ids, and yields **Warwick fail / Glasgow pass**. The base case digest is
  unchanged afterwards.

## Harness measurements for this run

| Metric | Value |
|---|---|
| Tool results recorded | 2 (one per offer gate) |
| Evidence checks | 2 |
| Decisions stored | 1 |
| Scenarios | 1 |
| Evidence confirmed / unresolved | 8 / 2 |
| Research tasks | 4 total: 2 hard-gate done, 2 decisive open |
| Checkpoints / resumes | 0 / 0 |

## What is frozen and what is not

- The fixture in `v2-harness/` freezes the **case**, the two gate tool results,
  the decision document, and the counterfactual change. The regression test
  never touches the network, so it proves the harness/engine contract, not
  live page availability.
- Live page content can change. A future re-run must re-open each URL and
  re-confirm the claim; the harness will flag any source older than 365 days
  and any claim outside its applicability period.

## Lesson

A real conditional decision is reproducible without pretending certainty:
opened sources support the cost and eligibility claims, the employer-recognition
question stays unresolved and visible, and a one-field budget change reverses
the recommendation without contaminating the original case.

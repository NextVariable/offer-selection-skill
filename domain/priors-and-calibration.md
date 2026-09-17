# Priors and calibration anchors

> **Role:** conditional, labelled domain knowledge. Nothing in this file is an
> unconditional hard rule: every entry applies only when its own condition
> holds. Most entries are optional heuristics, read when a trigger fires (U.S.
> offer on a research/STEM or China-return comparison; joint venture;
> local-stay country claims; equivalence/tie-break; strong-baseline
> calibration). One exception is the operative-year cost calibration (§7):
> when a decision's operative cost year is covered by it, reading and cross-checking
> it is **mandatory, not discretionary** — the condition is still required,
> but its numbers never override better-supported component evidence. How priors may be used is governed
> by `references/core-decision-engine.md` ("Priors as conditional evidence"
> and "Budget"). Every entry below is tagged `[HEURISTIC/PRIOR]` or
> `[CALIBRATION]`; none is a fact, a fixed point, or a school hard branch. Full
> derivation history: `domain/source-of-truth.md`.

## Contents

- [U.S. research and STEM ecosystem prior](#1-us-research--stem-ecosystem-prior)
- [U.S. China-return recognition prior](#2-us-china-return-private-sector-recognition-prior)
- [Geography and country priors](#3-geography-and-country-priors)
- [Joint-venture heuristics](#4-joint-venture-heuristics)
- [Calibration anchors](#5-calibration-anchors)
- [Counterfactual invariants](#6-counterfactual-invariants)
- [Operative-year cost calibration](#7-operative-year-all-in-cost-calibration)

## 1. U.S. research / STEM ecosystem prior

`[HEURISTIC/PRIOR]` For committed PhD / academic research goals — especially
STEM, engineering, CS, EE, AI, data/quantitative and natural sciences — an
American setting may supply usable research-university density, faculty/PI
choice, labs/groups, thesis routes, RA/projects, master-to-PhD continuity,
cross-disciplinary options, industry R&D links, and historical placement.
This can create a meaningful **Research Ecosystem Prior** when programme-level
pathway, fit, opportunity, eligibility, cost, and constraints are otherwise
similar.

Boundaries (do not cross):

- It is **not** universal U.S. superiority. A professional, course-based,
  taught, cash-cow, or no-thesis/no-lab/no-RA U.S. master's gets **no**
  automatic PhD advantage.
- Research the programme: thesis/research tracks, faculty and supervisor
  access, lab/RA access, research duration, dissertation requirements,
  internal PhD transition, outputs and placement.
- Stronger non-U.S. programme evidence overrides it: ETH/EPFL/Cambridge/
  Imperial/Oxford, European research master's, MRes, MPhil, or another strong
  programme-level pathway.
- Non-STEM disciplines: apply any ecosystem prior case by case.
- For technical employment, the ecosystem matters only through actual
  education, project/research, industry access, and applicable work / return-
  market evidence — it is a hypothesis about opportunity mechanisms, not proof
  the user can access them or secure a job.

## 2. U.S. China-return private-sector recognition prior

`[HEURISTIC/PRIOR]` For China-return nontechnical business, product, GTM,
marketing, consulting, finance, and general corporate recruiting, a U.S.
degree/school may receive a relatively strong **same-tier Recognition Prior**
when school tier and other core factors are otherwise close.

Boundaries:

- Activate only after comparing actual school brand, target-school status,
  target-market and employer recognition, internship capital, relevant fit,
  recruiting timeline/access, and ROI.
- Evaluate each school independently: school brand is neither QS nor U.S.
  News. Recognition can exceed a ranking-only reading — Dartmouth, Brown,
  Vanderbilt, Rice, and WashU are examples; verify the actual school and
  market. `HK3/SG2 ≈ G5 ≈ U.S. Top 30` is a rough hypothesis, not an equality.
- The original `U.S. > HK/SG > UK/Canada > Australia` intuition is a same-tier
  heuristic only; never add country and ranking mechanically.
- Credential value is baseline-dependent: ordinary undergraduate → strong U.S.
  university may be a material upgrade; a top U.S. bachelor → ordinary U.S.
  master's may add little or dilute the profile. The U.S. label never creates
  transformation by itself.
- SOE/central-SOE: credential, major, employer, ranking/school-list, and
  graduation gates override U.S. brand entirely.

## 3. Geography and country priors

`[HEURISTIC/PRIOR]` Geography acts through institutional/market mechanisms,
never as a national score.

- Local stay: historical claims about Hong Kong, Japan/Korea, continental
  Europe, Canada, Ireland, U.S., UK, Australia, and Singapore — including
  fixed percentages or categorical “only these roles stay” — are priors /
  search hypotheses only. “Select country over offer” is shorthand for:
  country feasibility constrains the offer's ceiling; decompose it into
  post-study work access → target-role employability → employer friction →
  long-term continuity (core / `path-local-stay.md`).
- Internship and recruiting access: Hong Kong may provide Hong Kong + Shenzhen
  + mainland recruiting access and China-compatible time zones; Singapore may
  provide local access and time-zone convenience; U.S./UK/Australia difficulty
  for international students is a research hypothesis, not a fixed fact. City
  opportunity ≠ accessible opportunity (verify legal eligibility, schedule,
  location, language, role demand, execution).

## 4. Joint-venture heuristics

`[HEURISTIC/PRIOR]` Joint ventures are not one category; never apply a blanket
discount (core: Gates). These are case-by-case hypotheses only:

- **CUHK-Shenzhen:** heuristic of strong private-sector recognition,
  especially Guangdong; may sit between HK3 and HK4/5 nationally and approach
  HK3 regionally. Verify each year and market. Private internship-deficient
  users may prefer it; SOE users may prefer a less ambiguous credential
  depending on actual gates.
- **NYU Shanghai:** may inherit substantial NYU private brand; verify SOE
  campus/credential treatment.
- **Duke Kunshan:** judge the exact Duke degree and credential treatment.
- **XJTLU / UNNC / UIC:** lower cost + regional recognition + internship
  access can beat an overseas QS100 option for a budget-constrained,
  internship-deficient regional private-sector user. Not a general conclusion.

Always verify: awarding institution, diploma wording, parent-degree
equivalence, campus identity, 留服 recognition, ranking treatment, employer /
region recognition, alumni outcomes, and internship access.

## 5. Calibration anchors

`[CALIBRATION]` These anchors record what earlier controlled-variable cases
established. They shape expectations; runtime behaviour is tested against
them through `evals/`, and identical school pairs must never become hard
branches. The profile-level abstractions are encoded in core.

1. **Weak/zero internship, China-return non-technical, same-tier offers:** an
   offer that materially improves high-quality internship repair can clearly
   lead (CUHK > UCL archetype) without making UCL intrinsically bad. Abstract:
   under same-tier brand, internship-repair value that changes the graduation
   profile can be decisive.
2. **Three strong relevant internships:** repair value declines and same-tier
   offers move toward UCL ≈ CUHK equivalence. Abstract: opportunity value is
   gated by whether the user still has that gap; never reward capital the user
   already has.
3. **Strong undergraduate:** master credential transformation declines; at
   UCLA-level, both UCL/CUHK may be unnecessary or low ROI for pure China-
   return employment. No automatic credential upgrade; no forced upgrade.
4. **SOE — UCL Management vs Manchester A&F:** the winner depends on real
   employer gates. Only one qualifies → prefer it; both qualify → title
   orthodoxy alone cannot create a large gap; both fail → recommend neither.
5. **Local stay:** four-part country feasibility precedes offer comparison;
   strong-stay and return-fallback users can receive different results for the
   same offers; dual track shows two outcomes.
6. **PhD — UCL taught Economics vs Warwick MRes/PhD:** committed PhD intent
   can favour the research pathway (research transformation > overall brand);
   uncertain intent restores the employment exit-option value.
7. Longer duration has no automatic premium.
8. The best available offer can still be not recommended.
9. **NYU SPS vs UIUC cost archetype:** if target-market outcomes are
   materially same-tier and UIUC is substantially cheaper, UIUC may have
   higher career ROI; NYC vs Champaign location, network, lifestyle, and
   experience remain subjective utility and cannot be decided by price alone.

## 6. Counterfactual invariants

The skill's behaviour must respond when the following change (verified through
`evals/cases/`, not by ad hoc claims): zero → strong internships; ordinary →
strong undergraduate; private → SOE goal; major eligible → ineligible; strong
local stay → dual / return fallback; employment → PhD; affordable → above
absolute ceiling; materially different → equivalent outcomes; programme
evidence strengthened while a country/JV label is held fixed.

## 7. Operative-year all-in cost calibration

`[CALIBRATION]` **Operative year: 2026.** The user's maintained one-year all-in
planning baseline for decisions whose operative cost year is 2026. It is a dated
budgeting prior, not independently confirmed market data, not a permanent
country constant, and not a fixed point. Unlike the discretionary priors above,
this calibration is **mandatory to read and cross-check** for a 2026 cost decision
(core: "Budget"; `SKILL.md`: load order): it needs no trigger phrase and the
user does not have to ask for it. How it may be used is governed by core.

| Destination / city tier | 2026 one-year all-in planning range |
|---|---:|
| Seoul or Tokyo | ¥250k–300k |
| United States, most locations | about ¥750k |
| United States, expensive major cities | above ¥750k; calculate case by case |
| United Kingdom, London | ¥700k–850k |
| United Kingdom, outside London | about ¥550k |
| Continental Europe, most locations | ¥150k–250k |
| Australia, average | ¥500k–550k |
| Sydney | ¥600k–650k |
| Canada, Toronto or Vancouver | ¥600k–750k |
| Canada, lower-cost locations such as Alberta | ¥400k–450k |
| Malaysia, public university | ¥120k–150k |
| Malaysia, private university | ¥160k–180k |

The calculation, reconciliation and uncertainty rules have one owner: core
"Budget". These rows are dated planning references, not default confirmed
prices. Reconfirm or retire them for later operative years; do not silently
carry 2026 numbers into another year.

# Core decision engine — canonical execution semantics

> Single owner of *how to execute* an offer decision. Loaded on every run.
> Provenance and the derivation history of these rules live in
> `internal/source-of-truth.md` (never loaded at runtime). Conditional priors and
> calibration anchors live in `references/priors-and-calibration.md`. Path-specific
> rules live in the `references/path-*.md` files. Do not restate this file's
> rules anywhere else; other files reference it.

## Contents

- [Execution order](#0-the-one-execution-order)
- [Iterative clarification](#iterative-clarification)
- [Rule priority](#rule-priority)
- [Budget and pre-output consistency](#budget)
- [Gates](#gates)
- [Gap and transformation](#gap-and-transformation)
- [Evidence state and decision sufficiency](#evidence-state-and-decision-sufficiency)
- [Research priority and stop](#research-priority)
- [Risk](#risk)
- [Score, equivalence, and priors](#score-and-equivalence)
- [Output](#output)

## 0. The one execution order

Run exactly one sequence:

**Stage 0 — Early hard-feasibility screening** → **Stage 1 — User and goal** →
**Stage 2 — Gap and transformation** → **Stage 3 — Exact-path eligibility** →
**Stage 4 — Target-market competitiveness** → **Stage 5 — Cost / ROI / risk** →
**Stage 6 — Subjective utility** → **Stage 7 — Recommendation and score mapping**.

A lower stage cannot repair a failed higher-layer gate, and no stage may be
skipped or reordered. Scores never generate or override the decision:
`Evidence → Recommendation → Score State → Score`. `Score → Recommendation` is
forbidden. Ranking, country, brand, and geography priors never enter before
their owning stage; eligibility precedes competitiveness.

- **Stage 0** handles only **already-confirmed** fatal constraints (above the
  Absolute Ceiling on confirmed figures, confirmed prerequisite failure,
  confirmed legal/registration/enrolment constraint). For anything unresolved:
  `Unknown ≠ Pass` and `Unknown ≠ Fail` — do not guess at Stage 0.
  In a multi-offer comparison, run this screen across every offer before making
  a shortlist. Do not first remove offers using a soft fit, brand, ranking,
  country, or curriculum judgment and thereby avoid evaluating their gates.
- **Stage 1** fixes the primary and secondary goal, the path, and the
  geographic intent: strong local stay / local-China dual track / return
  fallback / clear China return; employment / PhD / mixed. Intake groups are
  defined in `SKILL.md` (Minimal intake); this stage applies them, it does not
  restate them. Apply Iterative clarification when these inputs are insufficient.
- **Stage 2** diagnoses the Primary Gap and any decision-relevant Secondary
  Gap (credential, internship, technical, research, recruiting-readiness,
  language/local-market, work-authorization, budget), models each offer's
  transformation, and forms the Graduation Profile. Core question, employment:
  “After accepting this offer, what candidate does this user become, and how
  competitive is that candidate in the target market?” Core question, PhD:
  “What research candidate does this offer create, and does it materially
  improve research capital and access to the target PhD/academic path?”
- **Stage 3** applies every applicable gate for the exact path (see Gates),
  including whether a gate is in scope at all for that path and role. A user
  who cannot enter the applicant pool does not become competitive because the
  school is prestigious.
- **Stage 4** compares only eligible / conditionally eligible paths on
  target-market competitiveness (credential signal, internship capital,
  technical/research capital, recruiting readiness, accessible opportunity,
  target-market recognition, convertible network value).
- **Stage 5** analyzes total cost, Target Budget vs Absolute Ceiling,
  incremental cost/value, ROI, and Critical/Important/Notice risk. Budget Gate
  and ROI are separate analyses; do not double count. The mandatory
  operative-year calibration read in Budget precedes any cost conclusion here.
- **Stage 6** compares city, lifestyle, school affection, experience, and risk
  preference **only when outcomes are materially close**. Subjective utility
  cannot override a hard gate or a clear outcome difference.
- **Stage 7** maps completed reasoning to the permitted Score State and
  precision (see Evidence state and decision sufficiency; Score and equivalence).

## Iterative clarification

When missing, vague or conflicting private inputs could change a gate, target
path, winner/equivalence, recommendation tier or decisive trade-off, continue
Socratic clarification before settling the affected judgment. Do not substitute
an assumption for an answer the user can provide. This can recur whenever a
later stage exposes a decision-relevant ambiguity; it is not a one-time intake.
Public facts remain the agent's research responsibility (SKILL.md: Minimal intake).

Use existing answers and normally ask only one or two high-decision-value
questions per turn. Briefly explain what distinction matters, then adapt the
next question to the answer. Use neutral, concrete trade-offs or ask for actual
experience and outputs instead of repeating abstract labels. For example, if
the user says both "stay locally" and "return to China is fine", ask which
they would prefer if the local job were less aligned with their career goal.
Do not steer toward a preferred offer or demand invented numerical weights.
Surface conflicting goals, budgets or constraints without choosing the user's
priority for them; check your interpretation when the distinction matters.

Stop questioning once the decision is sufficiently supported, even if some
intake fields remain incomplete. Do not re-ask settled questions unless new
information creates a material conflict. If the user does not know, declines
to answer or requests a best-effort answer now, explain the remaining limit
and give conditional branches with their reversal conditions; apply Evidence
state and decision sufficiency to the permitted score precision. Missing
non-material details may use explicit assumptions. In a clarification turn,
briefly state what is already clear and ask the next question without forcing
a final ranking or score. Continue independent public research where useful.

## Rule priority

Physical/financial feasibility → exact-path eligibility → graduation-profile
transformation → target-market competitiveness → binding-gap resolution →
material opportunity and execution constraints → ROI/risk → subjective
utility → score mapping.

## Budget

`Total Cost = tuition + living cost + mandatory fees + duration-related cost + necessary opportunity cost − scholarship/grant`.

Include insurance, visa, necessary travel/recruiting, and relocation under the
relevant cost term. Include opportunity cost only when material; distinguish it
from cash affordability. Exceeding the Target Budget requires a
premium-value explanation. Materially exceeding the Absolute Ceiling normally
fails the Budget Gate (fatal in Stage 0 only when the figures are confirmed).
When both are affordable, ask what incremental cost buys: credential
threshold, recruiting pool, internship access, location, research resources,
work rights, network, or experience. Cheapest is not automatically best.

Treat a user's current, all-in destination or programme cost range as primary
decision input for their own affordability analysis unless it is internally
inconsistent or excludes a material component. Public research should
decompose, date, and sanity-check that range; it must not silently replace it
with a generic low living-cost estimate. Reconcile tuition, realistic housing,
insurance, visa, travel, recruiting/relocation and the actual programme period
against the stated total. If the researched build-up differs materially from
the user's range, show the disagreement and use an uncertainty range until the
cause is resolved. Never present a precise total assembled from confirmed
tuition plus unsupported or non-current living-cost assumptions as Confirmed.
Destination cost levels are dynamic facts. The engine holds the rule; the
dated numbers live in `references/priors-and-calibration.md`
("Operative-year all-in cost calibration"), so a later year replaces or adds
its own calibration without changing core.

**Mandatory read.** Before a cost conclusion for an operative year covered by
`references/priors-and-calibration.md`, read the dated calibration and cross-check
it against a programme-specific component estimate. The calibration is a
planning prior, not a confirmed market price or a mandatory opening total.
Calculate exact tuition, actual months, realistic housing (including an
accessible fallback), mandatory fees, insurance, visa, necessary travel,
exchange-rate uncertainty and applicable scholarship. A university's minimum
living-cost estimate alone does not establish this user's realistic total.
Reconcile a material difference from the maintained range component by
component; a well-supported estimate may supersede the range in either
direction. Do not scale fixed tuition linearly with programme duration.
If the destination has no row, use the same component and uncertainty standard;
never borrow another country's total. Missing evidence stays unresolved, but
an unknown component blocks the Budget Gate only if its plausible range can
change affordability. A defensible upper bound may establish affordability
without exact certainty; an unsupported assertion that costs "cannot be that
high" may not. If a material discrepancy cannot be reconciled, retain the
uncertainty range and conditional gate rather than choosing the convenient
estimate. Skipping an applicable calibration check leaves cost conclusions
unresolved.

Use lower-bound arithmetic before debating a midpoint. Confirmed tuition plus
unavoidable mandatory fees is already a Total Cost lower bound; tuition must
never be mistaken for, or nearly equated with, an all-in total. If that lower
bound exceeds the Absolute Ceiling, the Budget Gate fails without needing a
precise living-cost estimate. If tuition alone consumes most of the ceiling,
add a realistic city-specific non-tuition range and describe the result as a
material overrun when the full plausible range is materially above the
ceiling—never as "slightly over" merely because an underestimated midpoint is
close. For multiple offers, cost each offer independently: a destination-wide
baseline does not erase unusually high or low programme tuition.

### Mandatory pre-output consistency check

Before emitting a recommendation, re-check every offer against the following:

- For a decision whose operative cost year is covered by the operative-year
  calibration, compare every stated total with it. A figure outside the
  applicable range requires an explicit, component-level reconciliation;
  without one it cannot support a Budget Gate result.
- Apply the same component-evidence standard whether a destination has a
  calibration row or not. Unresolved components need defensible bounds before
  they can support affordability; tuition alone cannot establish an all-in
  midpoint or a Budget Gate `pass`.
- A range that straddles the Absolute Ceiling is `conditional/unresolved`, not
  `pass`; a range wholly above it is `fail`; only a defensible range wholly
  within it may pass on the available evidence.

## Gates

Research applicable budget, credential, major, ranking/school-list,
graduation/fresh-graduate, age/degree/licensing/nationality/security, work
authorization, career feasibility, prerequisite, supervisor, funding, and
progression gates. Output `pass / conditional / fail / unresolved` with
evidence. Passing allows competition; it does not imply competitiveness. A
failed decisive gate caps the path recommendation regardless of other
strengths.

Named hard gates: Budget Gate; Credential Gate (degree, 留服 recognition,
awarding institution); Major Eligibility Gate (employer accepted-major
directory / 学科大类 / 专业名称); Recruiting Eligibility Gate (graduation date,
fresh-graduate identity, campus cycle); Career Feasibility Gate; Local-work
Gate (only in the relevant scenario). Unknown ≠ Pass; unresolved gates stay
`unresolved` with the reversal branches stated (see Evidence state and
decision sufficiency).

A gate can also be **not applicable** under the active path's own rules — for
example, a path rule stating that the Major Eligibility Gate does not bind a
defined role scope. Report that as "not applicable by the active path rule"
(or "pass by path rule") and keep the Evidence State honest: it is a rule
consequence, not an externally verified fact, and it must never be written as
if research had confirmed that employers accept any major. A gate may not be
declared not applicable merely because its outcome is inconvenient, and a path
may not import another path's gate.

**No-major role mode.** An engine state in which a defined role scope carries
no Major Eligibility Gate and degree-title fit is not a selection criterion. Which paths and role scopes activate it is declared by the path
files (`references/path-private-sector.md`); a user-supplied no-major hiring
constraint activates it independently. Core does not define the role taxonomy or preferences; apply the path's
selection rule and pre-output check.

Three-name separation is a hard analytical rule: programme English name ≠
Chinese credential-recognition name (留服 认证名称) ≠ employer accepted-major
category. Treat them as separate facts and state which are verified vs
unverified.

A published continuation / continuing-student / expected-graduation-date
mechanism proves only an administrative mechanism; it does not prove free
delay for recruiting or employer acceptance of a later campus cycle. Verify
permission, cost, and employer recognition separately.

Joint ventures are not one category: never apply a blanket discount. Verify
degree-awarding institution, diploma wording, parent-degree equivalence,
campus identity, 留服 treatment, ranking treatment, and target-market
recognition case by case. Examples and heuristics: `references/priors-and-calibration.md`.

## Gap and transformation

Transformation is baseline-dependent. Ordinary undergraduate → strong master's
can be material; the same master's on a strong undergraduate adds less; a
top-bachelor user may get no material upgrade from another taught master's for
pure China-return employment. Avoid downgrade for strong undergraduates, but
do not demand an upgrade with no career value. Judge only what the offer can
incrementally change; the undergraduate baseline is fixed.

Model each offer's real additions, never the label: institution/degree signal,
verified credential and major, internships/projects/research, recruiting
windows, language/local experience, work authorization, cost, fallback, and
option value. Accessible opportunity is not city opportunity and never
guarantees an internship or a job. Internship, network, city, and time count
only by accessible/convertible value; do not reward capital the user already
has. After sufficient strong relevant internships, the fourth/fifth ordinary
placement has low marginal value.

## Evidence state and decision sufficiency

Classify every decision-relevant volatile fact as:

- **Confirmed** — verified from an authority-grade source for the user's
  operative dates.
- **Unresolved** — cannot yet be verified. It stays unresolved; never paper
  over it and never guess.
- **Heuristic / Prior** — search hypothesis or experience prior; guides what
  to investigate and may tie-break close evidence, never a fact.

**`Confirmed` is claim-scoped, not source-scoped.** It applies to the exact
claim, population, channel, programme or degree, jurisdiction, and operative
date that the cited source actually supports. Authority carried by an
institution name alone is insufficient: a university home page, a top-level
domain, a search-results page, a bare source name, or no URL at all does not
confirm anything.

Three consequences follow, and each is a hard rule:

1. A source describing **internal recruitment** does not establish
   **campus-recruiting eligibility**; a programme or university page does not
   establish an exact Chinese credential-recognition name; programme existence
   does not establish that programme's exact credential treatment; work right
   does not establish employability or long-term stay; a faculty or lab existing
   does not establish that this student can access it or that the supervisor is
   recruiting.
2. A third-party summary is not `Confirmed` merely because it claims to quote an
   official source. Third-party aggregation, forums, experience posts,
   marketing copy, and market common sense support `Heuristic / Prior` at most
   unless the underlying primary source has actually been opened and checked.
3. When a source supports only part of a claim, narrow the claim or label the
   unsupported portion `Unresolved`. Partial support is not full support, and a
   narrowed source must not be stretched back over the original claim.

Dynamic facts carry an operative period: tuition, scholarship, programme
structure, duration, recruiting eligibility, fresh-graduate status, employer
major list, credential policy, visa/work-right rules, occupation list,
application and graduation dates. A historical page does not automatically
establish the current cycle, and an access date is not an operative date.

Then grade the decision impact of what is unresolved:

- **Critical uncertainty** — a different value could change eligibility, a
  hard gate, recommended vs not recommended, absolute budget feasibility,
  local feasibility, or PhD feasibility
  → **No Responsible Score Yet**. If a recommendation is still needed, give a
  **conditional recommendation** with explicit branches and state precisely
  how each unresolved fact could reverse it. Do not emit a false-precision
  integer.
- **Material uncertainty** — cannot change eligibility but could change
  relative winner vs equivalence, recommendation strength, or ROI while the
  offer remains on the same side of worth choosing vs not worth choosing
  → **Provisional Tier** (report the tier as provisional until resolved).
- **Non-material uncertainty** — a reasonable change cannot alter eligibility,
  winner/equivalence, tier, or critical risk
  → **Confirmed Score allowed**.

**Path Closure Test (eligibility branch).** This test distinguishes loss of
an actual target path from loss of one replaceable channel. It does not narrow
the Critical definition above: uncertainty that can reverse whether an offer
is worth accepting is Critical even if the career path remains open. Evaluate
criticality for this user and path, not from the fact's type alone. Do not
classify a fact as Critical merely because it concerns graduation timing,
fresh-graduate status, recruiting cycles, or application windows. Ask: if this
fact resolves adversely, does the user lose access to the target path itself,
or only lose one channel / cycle / convenience within a broader still-viable
path?

- If the entire evaluated target path can close — e.g. a specific SOE /
  employer / fresh-graduate applicant pool where graduation timing or an
  accepted-major directory determines whether the user may apply at all —
  → **Critical uncertainty** → **No Responsible Score Yet** (or a conditional
  recommendation with explicit branches), never a Confirmed/Provisional
  numerical score on that path.
- If only one recruiting channel, cycle, or convenience is affected while
  materially viable alternatives remain — e.g. broad private-sector
  return-China employment where one autumn-recruiting window is uncertain —
  → usually **Material / execution risk**; give a Provisional Tier if the
  impact is material. It is Critical if the user depends on that window or
  losing it could change whether the offer is worth accepting at all.
- If plausible resolutions cannot materially affect winner/equivalence/tier/
  critical risk → **Non-material**.

Symmetry does not downgrade Critical to Material: a fact that affects two
offers in the same direction is not merely Material just because it is common
to both. If it can independently close the entire target path for one or both
offers — for example both offers missing the same specific recruiting cycle
that the user's target actually depends on, so neither can enter that applicant
pool — it remains **Critical at the path level**. But the same timing fact is
not Critical on a path where viable alternative channels keep the path open;
there apply the worth-accepting test before assigning Material or Non-material.

Principle: **Confirmed Score requires decision-sufficient evidence, not
complete fact certainty.** Research targets decision value, not fact
completeness.

## Research priority

Research only facts that may change a gate, the graduation profile, a
recommendation direction or tier, a material risk, or an equivalence result.
Order research by **highest decision value first**, not easiest-to-search
first. When an SOE/credential gate is involved, resolve the employer
accepted-major directory, credential requirement, ranking threshold, and
fresh-graduate rule before spending effort on QS number comparison, generic
city or curriculum pages, or brand anecdotes.

Evidence hierarchy (authority grade, highest first):

1. **Official / direct authority** — government, immigration, credential
   authority (留服), regulator, and target-employer official rules;
   university graduate school, programme, faculty, fee and calendar pages.
2. **Official outcome evidence** — official employment/placement reports,
   public placement, PhD placement, internal-transition rules.
3. **Reliable market / career data** — credible labor-market and career data.
4. **Alumni / professional-profile evidence** — dated, labeled as individual
   evidence.
5. **Reputable third-party analysis** — dated, labeled.
6. **Community evidence** (LinkedIn, forums, Reddit, 小红书) — operational
   reality checks only, labeled, never overriding contrary official rules,
   never generalized from one person to a fact.

A third-party or community source never substitutes for first-hand hard-gate
evidence that exists and is reachable. When official sources conflict, prefer
the more specific, newer, directly applicable source. When practical
experience and official rules disagree, label both “formal eligibility” and
“practical execution”.

Never hard-code tuition, duration, scholarship, deadline, graduation date,
continuation rules, credential recognition, ranking, employer eligibility,
target-school requirements, visa/work rights, occupation lists, curriculum, or
employment outcomes. Historical country and school heuristics are search
hypotheses, not facts. Attach research dates to volatile claims.

## Research stop

Stop when additional information no longer has sufficient value of
information — i.e., when:

- critical gates are confirmed or explicitly unresolved with branches stated;
- the primary gap is stable;
- the graduation profile is sufficiently clear;
- competitiveness is sufficient to judge;
- decision sufficiency is reached;
- new evidence is unlikely to change the recommendation or tier.

Stop encyclopedia-style search: irrelevant course detail, irrelevant ranking,
city encyclopedia, school history, and networking anecdotes that cannot
convert into candidate value. Research stop does not manufacture equivalence:
if evidence supports a material difference, stop and recommend directly; if
evidence supports outcome equivalence, enter Decision Equivalence.

## Risk

- **Critical**: affordability, credential/major/recruiting failure, unusable
  work rights, implausible path, or essential academic failure.
- **Important**: internship/readiness gap, immediate recruiting, weak
  technical/research preparation, local hiring/language/sponsorship
  difficulty, or high execution burden.
- **Notice**: course preference, lifestyle, networking style, or minor
  administration.

State mechanism, evidence status, control, and realistic mitigation for risks
that matter to this user.

## Score and equivalence

Score meaning: `score = how worth choosing this offer is FOR THIS USER and
goal`, not school quality and not a rank normalized against the available set.
The same offer can score very differently for different users; having only two
ordinary offers does not make the better one a 90.

Score bands (decision-result mapping only):

| Score | Tier |
|---:|---|
| 90–100 | 强推荐 (strongly recommended) |
| 80–89 | 推荐 (recommended) |
| 70–79 | 可以考虑 (consider) |
| 60–69 | 谨慎 (cautious) |
| <60 | 不推荐 (not recommended) |

Reserve 90+ for rare, strongly aligned offers with passed gates, material
transformation, attractive ROI, and no unresolved critical risk. A failed
decisive gate caps the path recommendation. A small 1–3 point difference—and
even a 4-point difference—without substantive evidence is no clear difference.
Evidence difference > numerical difference.

**Decision Equivalence**: when gates, target-market tier, graduation profile,
and expected outcomes are materially similar, do not force a winner. Enter
equivalence, return to the user the real trade-offs (cost, city, experience,
brand preference, risk preference), and let subjective utility decide. If two
offers fail different decisive gates, or every offer is weak
(low ROI, no upgrade, over budget, cannot repair the binding gap), say so:
“none recommended” is a valid answer, as are work-first, gap, reapply,
continue-applying, and change-target.

### Recommendation–Score Consistency

Recommendation precedes score mapping. A score and its tier are a
representation of the recommendation, never an independent engine that derives
the recommendation. The ordering is `Evidence → Recommendation → Score State →
Score`; never `Score → Recommendation`.

- If offers are judged **Decision Equivalent / No Meaningful Difference** on a
  path, the score/tier presentation must stay consistent with that judgment:
  same tier, close scores, or a stated weak directional preference — never a
  numeric gap that crosses a recommendation-tier boundary and visually creates
  a preference the evidence did not support.
- A numerical difference must not express a stronger preference than the
  evidence-based recommendation. If you write "basically no difference / near
  equivalence" while assigning two distinct recommendation tiers, the
  representation contradicts the judgment — reconcile them.
- If independent evidence actually supports a **material tier difference**,
  then it is not Decision Equivalence: revisit and state the recommendation
  honestly rather than mechanically compressing the scores.
- Do not use a fixed numerical distance (e.g. "≤N points = equivalent") to
  define equivalence. Equivalence is an evidence judgment, not a score-arithmetic
  rule.

## Priors as conditional evidence

Geography, country, school, and ecosystem priors act only through an evidenced
mechanism, never as fixed points (`USA +N` and country bonus designs are
forbidden):

> Programme evidence > geography prior  
> Eligibility > brand prior  
> User-specific transformation > country prestige  
> Target-market recognition > generic global ranking  
> Evidence difference > country stereotype

Country/geography tie-break priors may affect a recommendation only when
stronger variables are materially close and the mechanism is realistically
accessible. Market-specific recognition priors have the separate evidence
ladder in `path-private-sector.md`: they may support a labelled, provisional
recognition judgment without an employer list, but never become a verified
employer rule. Apply the uncertainty mapping to their decision impact. Do not count the same lab density, industry access, brand, ranking, or
country evidence twice under different labels (anti-double-counting). The
labelled prior definitions, boundaries, and calibration examples live in
`references/priors-and-calibration.md`; route to them only when the trigger fires.

## Output

Follow the output contract in `SKILL.md`; this section does not duplicate it.

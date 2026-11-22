"""Executable cases for the shipped arithmetic, evidence and decision checks."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/offer-selection-skill/scripts/decision.py"
SPEC = importlib.util.spec_from_file_location("offer_decision", SCRIPT)
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)


def claim(cid="course", kind="programme", scope="programme and intake", **overrides):
    return dict(id=cid, offer="a", path="*", kind=kind, scope=scope, state="confirmed",
                impact="material", claim="An official programme page confirms supervised projects",
                period={"from": "2027-01-01", "through": "2027-12-31"},
                sources=[{"url": "https://example.edu/programmes/example", "authority": "institution",
                          "scope": scope, "accessed": "2026-11-22", "locator": "Project structure",
                          "inspection": {"access": "opened", "support": "supported",
                                         "observation": "The programme lists supervised projects."}}]) | overrides


def row(cid, kind, amount, month=0, **kw):
    return dict(id=cid, kind=kind, amount=amount, month=month, basis="Fixture constraint") | kw


def base():
    return {
        "schema": engine.VERSION, "as_of": "2026-11-22",
        "profile": {"internships": ["relevant project"], "private_number": 12345},
        "goal": {"paths": ["private"], "country": "China", "career": "broad business",
                 "phd_intent": "no", "prestige": "neutral", "risk_tolerance": "moderate"},
        "budget": {"currency": "CNY", "ceiling": 100},
        "offers": [{"id": "a", "title": "Offer A", "country": "China",
                    "operative_date": "2027-09-01", "cost_complete": True,
                    "costs": [row("tuition", "expense", [40, 40])],
                    "gates": [{"id": "major", "path": "private", "scope": "broad private nontechnical",
                               "kind": "eligibility", "status": "not_applicable", "evidence_ids": []}]}],
        "evidence": [claim()]
    }


def decision():
    return {"schema": engine.VERSION, "conclusion": {"type": "recommend",
                                                       "choices": [{"offer": "a", "path": "private"}]},
            "headline": "Choose A", "reasons": ["Accessible supervised work adds useful outputs"],
            "risks": [], "reversal": "Project access could change the direction.",
            "assessments": [{"offer": "a", "path": "private", "gate": "pass", "score_state": "confirmed",
                             "stance": "recommend", "value": "Supervised output relative to baseline",
                             "competitiveness": "Projects relevant to role", "evidence_ids": ["course"]}]}


def second_offer(data):
    b = copy.deepcopy(data["offers"][0])
    b.update(id="b", title="Offer B")
    data["offers"].append(b)


class BudgetCases(unittest.TestCase):
    def test_master_ceiling_excludes_doctoral_expenses_and_awards(self):
        q = self.cost([row("masters-fee", "expense", [82, 82], stage="masters"),
                       row("doctoral-fee", "expense", [300, 300], stage="doctoral"),
                       row("doctor-award", "award", [40, 40], stage="doctoral")], horizon="masters")
        self.assertEqual((q["cash"], q["budget_gate"], q["excluded_cost_ids"]),
                         ((82, 82), "pass", ["doctoral-fee", "doctor-award"]))

    def test_master_ceiling_rejects_untagged_rows(self):
        with self.assertRaisesRegex(ValueError, "explicit stage"):
            self.cost([row("combined", "expense", [300, 300])], horizon="masters")

    def test_no_master_rows_is_unresolved(self):
        q = self.cost([row("doctoral-only", "expense", [80, 80], stage="doctoral")], horizon="masters")
        self.assertEqual(q["budget_gate"], "unresolved")

    def test_whole_offer_still_includes_both_stages(self):
        q = self.cost([row("masters-fee", "expense", [82, 82], stage="masters"),
                       row("doctor-fee", "expense", [300, 300], stage="doctoral")])
        self.assertEqual((q["budget_horizon"], q["budget_gate"]), ("whole_offer", "fail"))

    def cost(self, items, **budget):
        data = base()
        data["offers"][0]["costs"] = items
        data["budget"].update(budget)
        return engine.analyze(data)["offers"]["a"]["cost"]

    def test_exact_ceiling(self):
        self.assertEqual(self.cost([row("fee", "expense", [100, 100])])["budget_gate"], "pass")

    def test_over_ceiling(self):
        self.assertEqual(self.cost([row("fee", "expense", [101, 101])])["budget_gate"], "fail")

    def test_range_crosses_ceiling(self):
        self.assertEqual(self.cost([row("fee", "expense", [90, 101])])["budget_gate"], "unresolved")

    def test_unknown_expense_cannot_pass(self):
        self.assertEqual(self.cost([row("fee", "expense", [0, None])])["budget_gate"], "unresolved")

    def test_unknown_ceiling_remains_unknown(self):
        self.assertEqual(self.cost([row("fee", "expense", [30, 30])], ceiling=None)["budget_gate"], "unresolved")

    def test_above_target_not_hard_failure(self):
        q = self.cost([row("fee", "expense", [70, 70])], target=60)
        self.assertEqual((q["target_status"], q["budget_gate"]), ("fail", "pass"))

    def test_opportunity_cost_held_out_of_gate(self):
        q = self.cost([row("fee", "expense", [70, 75]), row("work", "opportunity", [40, 60])])
        self.assertEqual((q["economic_cost"], q["budget_gate"]), ((110, 135), "pass"))

    def test_conditional_award_cannot_prove_pass(self):
        q = self.cost([row("fee", "expense", [110, 120]), row("aid", "award", [0, 25])])
        self.assertEqual((q["cash"], q["budget_gate"]), ((85, 120), "unresolved"))

    def test_even_max_award_cannot_rescue(self):
        q = self.cost([row("fee", "expense", [110, 120]), row("aid", "award", [0, 8])])
        self.assertEqual(q["budget_gate"], "fail")

    def test_guaranteed_award_proves_pass(self):
        q = self.cost([row("fee", "expense", [110, 115]), row("aid", "award", [15, 15])])
        self.assertEqual(q["budget_gate"], "pass")

    def test_award_after_deadline_cannot_rescue_cashflow(self):
        q = self.cost([row("fee", "expense", [110, 110]), row("aid", "award", [20, 20], 1)],
                      liquidity=[{"month": 0, "available": [100, 100]}])
        self.assertEqual((q["ceiling_status"], q["milestones"][0]["status"]), ("pass", "fail"))

    def test_award_before_payment_rescues_cashflow(self):
        q = self.cost([row("fee", "expense", [110, 110], 1), row("aid", "award", [20, 20], 0)],
                      liquidity=[{"month": 1, "available": [100, 100]}])
        self.assertEqual(q["budget_gate"], "pass")

    def test_unknown_time_cannot_rescue_cashflow(self):
        q = self.cost([row("fee", "expense", [110, 110]), row("aid", "award", [20, 20], None)],
                      liquidity=[{"month": 0, "available": [100, 100]}])
        self.assertEqual(q["budget_gate"], "unresolved")

    def test_liquidity_uncertain_not_fail(self):
        q = self.cost([row("fee", "expense", [80, 80])], liquidity=[{"month": 0, "available": [70, 90]}])
        self.assertEqual(q["budget_gate"], "unresolved")

    def test_stress_category_and_base_stay_separate(self):
        q = self.cost([row("fee", "expense", [60, 60]), row("housing", "expense", [37, 37], category="housing")],
                      stress={"percent": 20, "categories": ["housing"]})
        self.assertEqual((q["cash"], q["budget_gate"]), ((97, 97), "pass"))
        self.assertEqual((q["stress"]["cash"], q["stress"]["budget_gate"]), ((104, 105), "fail"))

    def test_duplicate_cost_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate cost"):
            self.cost([row("fee", "expense", [10, 10]), row("fee", "expense", [20, 20])])

    def test_incomplete_ledger_cannot_prove_pass(self):
        d = base()
        d["offers"][0]["cost_complete"] = False
        self.assertEqual(engine.analyze(d)["offers"]["a"]["cost"]["budget_gate"], "unresolved")

    def test_lower_bound_failure_needs_bounded_offsets(self):
        d = base()
        offer = d["offers"][0]
        offer.update(cost_complete=False, costs=[row("fee", "expense", [101, 101])])
        self.assertEqual(engine.analyze(d)["offers"]["a"]["cost"]["budget_gate"], "unresolved")
        offer["offsets_complete"] = True
        self.assertEqual(engine.analyze(d)["offers"]["a"]["cost"]["budget_gate"], "fail")

    def test_no_deadlines_unchecked(self):
        self.assertFalse(self.cost([row("fee", "expense", [10, 20])])["cashflow_checked"])

    def test_user_affordability_is_separate_from_price_verification(self):
        q = self.cost([row("fee", "expense", [0, None])], ceiling=None, affordable_by_user=["a"])
        self.assertEqual((q["budget_gate"], q["ceiling_status"], q["affordability_basis"]),
                         ("pass", "unresolved", "user_affordability_attestation"))

    def test_user_affordability_never_overrides_numeric_ceiling(self):
        q = self.cost([row("fee", "expense", [101, 101])], affordable_by_user=["a"])
        self.assertEqual(q["budget_gate"], "fail")

    def test_user_affordability_never_overrides_cashflow(self):
        q = self.cost([row("fee", "expense", [90, 90])], ceiling=None, affordable_by_user=["a"],
                      liquidity=[{"month": 0, "available": [80, 80]}])
        self.assertEqual(q["budget_gate"], "fail")

    def test_user_affordability_not_reused_for_stress_case(self):
        q = self.cost([row("fee", "expense", [90, 90], category="housing")],
                      ceiling=None, affordable_by_user=["a"],
                      stress={"percent": 20, "categories": ["housing"]})
        self.assertEqual((q["budget_gate"], q["stress"]["budget_gate"]), ("pass", "unresolved"))


class EvidenceCases(unittest.TestCase):
    def test_url_without_opened_page_cannot_confirm(self):
        data = base()
        del data["evidence"][0]["sources"][0]["inspection"]
        with self.assertRaisesRegex(ValueError, "no opened"):
            engine.analyze(data)

    def test_blocked_page_cannot_have_claim_support(self):
        data = base()
        data["evidence"][0]["sources"][0]["inspection"]["access"] = "blocked"
        with self.assertRaisesRegex(ValueError, "only opened"):
            engine.analyze(data)

    def test_partial_page_reopens_gate_without_mutating_base(self):
        data = base()
        c = claim("role", "eligibility", "campus")
        c["sources"][0]["inspection"]["support"] = "partial"
        data["evidence"].append(c)
        data["offers"][0]["gates"][0].update(status="pass", evidence_ids=["role"], scope="campus")
        fixed = engine.audit(data)
        self.assertEqual(data["evidence"][1]["state"], "confirmed")
        self.assertEqual(fixed["input"]["evidence"][1]["state"], "unresolved")
        self.assertEqual(fixed["input"]["offers"][0]["gates"][0]["status"], "unresolved")

    def test_unreviewed_expense_cannot_prove_affordability(self):
        data = base()
        fee = claim("2027-fee", "cost")
        del fee["sources"][0]["inspection"]
        data["evidence"].append(fee)
        data["offers"][0]["costs"][0]["evidence_ids"] = ["2027-fee"]
        fixed = engine.audit(data)["input"]
        cost = engine.analyze(fixed)["offers"]["a"]["cost"]
        self.assertEqual((cost["cash"], cost["budget_gate"]), ((0, None), "unresolved"))

    def test_opened_official_page_with_wrong_scope_still_unresolved(self):
        data = base()
        data["evidence"][0]["sources"][0]["scope"] = "general university policy"
        self.assertEqual(engine.audit(data)["input"]["evidence"][0]["state"], "unresolved")

    def test_unverified_doctoral_fee_does_not_reopen_master_budget(self):
        data = base()
        data["budget"]["horizon"] = "masters"
        offer = data["offers"][0]
        offer["costs"][0]["stage"] = "masters"
        fee = claim("doctor-fee", "cost")
        del fee["sources"][0]["inspection"]
        data["evidence"].append(fee)
        offer["costs"].append(row("doctor", "expense", [300, 300], stage="doctoral",
                                  evidence_ids=["doctor-fee"]))
        fixed = engine.audit(data)["input"]
        result = engine.analyze(fixed)["offers"]["a"]["cost"]
        self.assertEqual((result["budget_gate"], result["excluded_cost_ids"]), ("pass", ["doctor"]))

    def test_quick_shows_checked_sources_and_shares_full_prefix(self):
        d, out = base(), decision()
        quick, full = (engine.render(d, out, mode) for mode in ("quick", "full"))
        self.assertIn("https://example.edu/programmes/example", quick)
        self.assertTrue(full.startswith(quick))
        self.assertIn("opened/supported", full)
        self.assertIn("The programme lists supervised projects.", full)
        self.assertIn("2027-09-01", full)

    def test_employer_scope_match(self):
        d = base()
        d["evidence"].append(claim("job", "eligibility", "target employer campus roster"))
        d["offers"][0]["gates"][0].update(scope="target employer campus roster", status="pass", evidence_ids=["job"])
        self.assertEqual(engine.analyze(d)["offers"]["a"]["paths"]["private"]["gate"], "pass")

    def test_wrong_recruiting_channel_rejected(self):
        d = base()
        d["evidence"].append(claim("job", "eligibility", "internal recruiting"))
        d["offers"][0]["gates"][0].update(scope="campus roster", status="pass", evidence_ids=["job"])
        with self.assertRaisesRegex(ValueError, "wrong evidence"):
            engine.analyze(d)

    def test_gate_can_remain_unknown_without_proof(self):
        d = base()
        d["offers"][0]["gates"][0]["status"] = "unresolved"
        self.assertEqual(engine.analyze(d)["offers"]["a"]["paths"]["private"]["score_state"], "nrsy")

    def test_community_is_not_confirmed_authority(self):
        d = base()
        d["evidence"][0]["sources"][0]["authority"] = "community"
        with self.assertRaisesRegex(ValueError, "scoped authority"):
            engine.analyze(d)

    def test_context_scope_cannot_confirm(self):
        d = base()
        d["evidence"][0]["sources"][0]["scope"] = "university-wide"
        with self.assertRaisesRegex(ValueError, "scoped authority"):
            engine.analyze(d)

    def test_outdated_intake_cannot_confirm(self):
        d = base()
        d["evidence"][0]["period"]["through"] = "2027-08-31"
        with self.assertRaisesRegex(ValueError, "out-of-period"):
            engine.analyze(d)

    def test_later_application_date_overrides_intake(self):
        d = base()
        d["evidence"][0].update(operative_date="2028-07-01", period={"from": "2028-01-01", "through": "2028-12-31"})
        self.assertEqual(engine.analyze(d)["offers"]["a"]["paths"]["private"]["gate"], "pass")

    def test_planning_prior_cannot_pass_gate(self):
        d = base()
        d["evidence"].append(claim("rank", "eligibility", "campus", state="prior"))
        d["offers"][0]["gates"][0].update(scope="campus", status="pass", evidence_ids=["rank"])
        with self.assertRaisesRegex(ValueError, "direct evidence"):
            engine.analyze(d)

    def test_missing_gate_roster_is_unknown(self):
        d = base()
        d["offers"][0]["gates"] = []
        self.assertEqual(engine.analyze(d)["offers"]["a"]["paths"]["private"]["gate"], "unresolved")

    def test_no_root_url_for_authority(self):
        d = base()
        d["evidence"][0]["sources"][0]["url"] = "https://example.edu/"
        with self.assertRaisesRegex(ValueError, "source page URL"):
            engine.analyze(d)

    def test_research_does_not_export_profile(self):
        d = base()
        d["offers"][0]["cost_complete"] = False
        d["evidence"].append(claim("market", "market", "target channel", state="prior", impact="material"))
        plan = engine.research(d)
        self.assertEqual([v["priority"] for v in plan["tasks"]], [0, 1])
        self.assertNotIn("12345", json.dumps(plan))

    def test_research_stops_for_minor_unknown(self):
        d = base()
        d["evidence"].append(claim("museum", state="unresolved", impact="minor"))
        self.assertEqual(engine.research(d)["tasks"], [])


class RecommendationCases(unittest.TestCase):
    def test_positive_normal_decision(self):
        self.assertEqual(engine.validate(base(), decision())["offers"]["a"]["paths"]["private"]["gate"], "pass")

    def test_preference_cannot_rescue_budget(self):
        d, out = base(), decision()
        d["goal"]["prestige"] = "strong"
        d["budget"]["ceiling"] = 20
        out["assessments"][0]["gate"] = "fail"
        with self.assertRaisesRegex(ValueError, "failed gate"):
            engine.validate(d, out)

    def test_material_prior_cannot_yield_integer(self):
        d, out = base(), decision()
        d["evidence"].append(claim("access", "access", state="prior"))
        out["assessments"][0]["score"] = 85
        with self.assertRaisesRegex(ValueError, "too certain"):
            engine.validate(d, out)

    def test_grade_only_cannot_confirm_acceptance(self):
        d, out = base(), decision()
        d["evidence"][0]["kind"] = "eligibility"
        with self.assertRaisesRegex(ValueError, "beyond eligibility"):
            engine.validate(d, out)

    def test_unknown_cash_limit_propagates_to_both_tracks(self):
        d = base()
        d["goal"]["paths"] = ["private", "local"]
        d["budget"]["ceiling"] = None
        d["offers"][0]["gates"].append({"id": "local", "path": "local", "scope": "work route",
                                       "kind": "work", "status": "unresolved", "evidence_ids": []})
        result = engine.analyze(d)["offers"]["a"]["paths"]
        self.assertEqual([p["score_state"] for p in result.values()], ["nrsy", "nrsy"])

    def test_local_gate_does_not_leak_to_return(self):
        d = base()
        d["goal"]["paths"].append("local")
        d["offers"][0]["gates"].append({"id": "local", "path": "local", "scope": "work route",
                                       "kind": "work", "status": "unresolved", "evidence_ids": []})
        result = engine.analyze(d)["offers"]["a"]["paths"]
        self.assertEqual([p["gate"] for p in result.values()], ["pass", "unresolved"])

    def test_unknown_evidence_does_not_prove_equivalence(self):
        d, out = base(), decision()
        second_offer(d)
        d["evidence"].append(claim("unclear", "market", state="prior"))
        out["conclusion"] = {"type": "equivalent", "choices": [], "parity_basis": "Same opportunity"}
        out["assessments"][0].update(stance="viable", score_state="provisional")
        out["assessments"] += [dict(out["assessments"][0], offer="b", evidence_ids=[])]
        out["risks"] = ["Comparative market reach is unknown."]
        with self.assertRaisesRegex(ValueError, "unresolved/rejected"):
            engine.validate(d, out)

    def test_all_offers_rejected_is_supported(self):
        d, out = base(), decision()
        second_offer(d)
        d["budget"]["ceiling"] = 20
        out["conclusion"] = {"type": "none", "choices": []}
        out["risks"] = ["The cash ceiling blocks both."]
        out["assessments"][0].update(gate="fail", stance="reject")
        out["assessments"] += [dict(out["assessments"][0], offer="b", evidence_ids=[])]
        self.assertEqual(len(engine.validate(d, out)["offers"]), 2)

    def test_mixed_offer_does_not_support_none(self):
        out = decision()
        out["conclusion"] = {"type": "none", "choices": []}
        with self.assertRaisesRegex(ValueError, "every path rejected"):
            engine.validate(base(), out)

    def test_reports_share_exact_decision(self):
        quick, full = (engine.render(base(), decision(), mode) for mode in ("quick", "full"))
        self.assertTrue(full.startswith(quick))
        self.assertIn("个人增量", full)

    def test_stale_foreign_offer_citation_rejected(self):
        d, out = base(), decision()
        second_offer(d)
        d["evidence"][0]["offer"] = "b"
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            engine.validate(d, out)

    def test_defer_not_equivalent(self):
        d, out = base(), decision()
        d["offers"][0]["gates"][0]["status"] = "unresolved"
        out["assessments"][0].update(gate="unresolved", score_state="nrsy", stance="defer")
        out["conclusion"] = {"type": "defer", "choices": []}
        out["risks"] = ["Employer notice is unknown."]
        self.assertEqual(engine.validate(d, out)["offers"]["a"]["paths"]["private"]["gate"], "unresolved")


class ScenarioCases(unittest.TestCase):
    def test_budget_flip_reuses_sources_and_preserves_base(self):
        d = base()
        result = engine.scenario(d, {"field": "ceiling", "value": 22})
        self.assertEqual(result["reuse_evidence_ids"], ["course"])
        self.assertEqual(d["budget"]["ceiling"], 100)
        self.assertEqual(engine.analyze(result["input"])["offers"]["a"]["cost"]["budget_gate"], "fail")

    def test_country_reopens_affected_gate_only(self):
        d = base()
        d["evidence"].append(claim("job", "eligibility"))
        d["offers"][0]["gates"][0].update(scope="programme and intake", status="pass", evidence_ids=["job"])
        s = engine.scenario(d, {"field": "country", "value": "Canada"})
        self.assertEqual(s["recheck_evidence_ids"], ["job"])
        self.assertEqual(s["input"]["offers"][0]["gates"][0]["status"], "unresolved")

    def test_internship_change_preserves_credential_facts(self):
        d = base()
        s = engine.scenario(d, {"field": "internships", "value": ["three deep placements"]})
        self.assertEqual((s["reuse_evidence_ids"], s["input"]["profile"]["internships"]),
                         (["course"], ["three deep placements"]))

    def test_prestige_does_not_reopen_gates(self):
        d = base()
        self.assertEqual(engine.scenario(d, {"field": "prestige", "value": "high"})["input"]["offers"], d["offers"])

    def test_reject_multiple_simultaneous_fields(self):
        with self.assertRaisesRegex(ValueError, "unexpected"):
            engine.scenario(base(), {"field": "ceiling", "value": 95, "career": "research"})

    def test_noop_scenario_rejected(self):
        with self.assertRaisesRegex(ValueError, "actually change"):
            engine.scenario(base(), {"field": "risk_tolerance", "value": "moderate"})

    def test_phd_change_reopens_research_only(self):
        d = base()
        d["evidence"].append(claim("lab", "research"))
        s = engine.scenario(d, {"field": "phd_intent", "value": "primary"})
        self.assertEqual((s["reuse_evidence_ids"], s["recheck_evidence_ids"]), (["course"], ["lab"]))

    def test_cli_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text('{"schema":"a","schema":"b"}')
            result = subprocess.run([sys.executable, str(SCRIPT), "check", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("duplicate JSON key", result.stderr)


class QuickReportCases(unittest.TestCase):
    def test_quick_shows_cost_range_headroom_and_gate(self):
        d, out = base(), decision()
        d["budget"]["target"] = 90
        quick = engine.render(d, out, "quick")
        self.assertIn("### 费用与预算", quick)
        self.assertIn("净现金 40–40", quick)
        self.assertIn("余量 60–60", quick)
        self.assertIn("预算闸门通过", quick)
        self.assertIn("全项目", quick)

    def test_quick_names_unquantified_costs(self):
        d, out = base(), decision()
        d["offers"][0]["costs"] = [row("tuition", "expense", [0, None])]
        d["offers"][0]["cost_complete"] = False
        out["assessments"][0].update(gate="unresolved", stance="defer", score_state="nrsy")
        out["conclusion"] = {"type": "defer", "choices": []}
        out["risks"] = ["Cost ledger remains incomplete"]
        quick = engine.render(d, out, "quick")
        self.assertIn("未量化 tuition", quick)
        self.assertIn("上界未定", quick)
        self.assertIn("付款节点未核对", quick)

    def test_quick_master_horizon_names_excluded_doctoral_rows(self):
        d, out = base(), decision()
        d["budget"].update(ceiling=100, horizon="masters")
        d["offers"][0]["costs"] = [row("m-fee", "expense", [40, 40], stage="masters"),
                                   row("d-fee", "expense", [300, 300], stage="doctoral"),
                                   row("d-award", "award", [0, None], stage="doctoral")]
        quick = engine.render(d, out, "quick")
        self.assertIn("口径：仅硕士阶段", quick)
        self.assertIn("净现金 40–40", quick)
        self.assertIn("不计入 d-fee、d-award", quick)
        self.assertNotIn("未量化 d-award", quick)

    def test_quick_lists_unresolved_evidence_with_impact(self):
        d, out = base(), decision()
        d["evidence"].append(claim("gate-claim", kind="eligibility", scope="broad private nontechnical",
                                   state="unresolved", impact="critical"))
        d["offers"][0]["gates"][0].update(status="unresolved", evidence_ids=["gate-claim"])
        out["assessments"][0].update(gate="unresolved", stance="defer", score_state="nrsy",
                                     evidence_ids=["course", "gate-claim"])
        out["conclusion"] = {"type": "defer", "choices": []}
        out["risks"] = ["Gate evidence remains unresolved"]
        quick = engine.render(d, out, "quick")
        self.assertIn("### 待核实", quick)
        self.assertIn("未确认；影响关键", quick)

    def test_quick_omits_cost_section_without_budget_limit(self):
        d, out = base(), decision()
        d["budget"] = {"currency": "CNY", "ceiling": None}
        out["assessments"][0].update(gate="unresolved", stance="defer", score_state="nrsy")
        out["conclusion"] = {"type": "defer", "choices": []}
        out["risks"] = ["No numeric ceiling is available"]
        quick = engine.render(d, out, "quick")
        self.assertNotIn("### 费用与预算", quick)


class HostContractCases(unittest.TestCase):
    """Exercise the CLI surface a host agent actually calls."""

    def integrated(self):
        d = base()
        d["budget"].update(ceiling=100, horizon="masters", target=90)
        d["offers"][0]["costs"] = [row("m-fee", "expense", [40, 40], stage="masters"),
                                   row("d-fee", "expense", [300, 300], stage="doctoral"),
                                   row("d-award", "award", [0, None], stage="doctoral")]
        return d

    def run_cli(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_check_applies_master_stage_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp) / "case.json"
            case.write_text(json.dumps(self.integrated()))
            cost = self.run_cli("check", str(case))["offers"]["a"]["cost"]
            self.assertEqual((cost["cash"], cost["budget_horizon"], cost["budget_gate"]),
                             ([40, 40], "masters", "pass"))
            self.assertEqual(cost["excluded_cost_ids"], ["d-fee", "d-award"])

    def test_ceiling_scenario_keeps_horizon_and_doctoral_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            case, change = Path(temp) / "case.json", Path(temp) / "change.json"
            case.write_text(json.dumps(self.integrated()))
            change.write_text(json.dumps({"field": "ceiling", "value": 30}))
            result = self.run_cli("scenario", str(case), str(change))
            revised = result["input"]
            self.assertEqual(revised["budget"]["horizon"], "masters")
            self.assertEqual([c["id"] for c in revised["offers"][0]["costs"]],
                             ["m-fee", "d-fee", "d-award"])
            revised_path = Path(temp) / "revised.json"
            revised_path.write_text(json.dumps(revised))
            cost = self.run_cli("check", str(revised_path))["offers"]["a"]["cost"]
            self.assertEqual((cost["cash"], cost["ceiling_status"], cost["budget_gate"]),
                             ([40, 40], "fail", "fail"))
            self.assertEqual(cost["excluded_cost_ids"], ["d-fee", "d-award"])


if __name__ == "__main__":
    unittest.main()

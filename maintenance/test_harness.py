"""Unit and integration tests for the v2 decision harness.

The harness owns execution state only. These tests deliberately assert that it
delegates case validation, gate semantics, cost arithmetic and Quick/Full
rendering to `decision.py` instead of carrying a second rule set.
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "offer-selection-skill" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import decision  # noqa: E402
import harness  # noqa: E402

NOW = "2026-11-23T10:00:00+08:00"
PERIOD = {"from": "2027-01-01", "through": "2027-12-31"}
OPERATIVE = "2027-09-01"


def source(scope, accessed="2026-11-20", support="supported", access="opened"):
    review = {"access": access, "support": support}
    if access == "opened" and support != "unreviewed":
        review["observation"] = "The located paragraph states the exact claim."
    return {
        "url": "https://www.example.edu/study/marketing",
        "authority": "institution",
        "scope": scope,
        "accessed": accessed,
        "locator": "Admissions > Entry requirements",
        "inspection": review,
    }


def fee_evidence(accessed="2026-11-20", period=None, state="confirmed"):
    return {
        "id": "fee", "offer": "a", "path": "*", "kind": "cost", "scope": "2027/28 tuition",
        "state": state, "impact": "critical",
        "claim": "Published 2027/28 tuition is CNY 300,000",
        "period": period or dict(PERIOD),
        "sources": [source("2027/28 tuition", accessed=accessed)],
    }


def base_case(offers=1, minor=False):
    case = {
        "schema": decision.VERSION,
        "as_of": "2026-11-23",
        "profile": {"undergraduate": "Business", "internships": ["agency internship"]},
        "goal": {"paths": ["private"], "country": "China", "career": "marketing",
                 "phd_intent": "no", "prestige": "neutral", "risk_tolerance": "moderate"},
        "budget": {"currency": "CNY", "ceiling": 500000, "target": 450000},
        "offers": [{
            "id": "a", "title": "A University MSc Marketing", "country": "United Kingdom",
            "operative_date": OPERATIVE, "cost_complete": True,
            "costs": [{"id": "tuition", "kind": "expense", "amount": [300000, 300000],
                       "month": 9, "basis": "published 2027/28 tuition", "evidence_ids": ["fee"]}],
            "gates": [{"id": "degree", "path": "private", "scope": "2027 intake MSc Marketing",
                       "kind": "eligibility", "status": "unresolved", "evidence_ids": []}],
        }],
        "evidence": [fee_evidence()],
    }
    if offers > 1:
        case["offers"].append({
            "id": "b", "title": "B University MSc Marketing", "country": "United Kingdom",
            "operative_date": OPERATIVE, "cost_complete": True,
            "costs": [{"id": "tuition", "kind": "expense", "amount": [250000, 250000],
                       "month": 9, "basis": "published 2027/28 tuition"}],
            "gates": [{"id": "degree", "path": "private", "scope": "2027 intake MSc Marketing",
                       "kind": "eligibility", "status": "unresolved", "evidence_ids": []}],
        })
    if minor:
        case["evidence"].append({
            "id": "club", "offer": "a", "path": "private", "kind": "network",
            "scope": "career club", "state": "unresolved", "impact": "minor",
            "claim": "A student career club exists",
        })
    return case


def find_task(state, kind, status=None):
    return next(t for t in state["research"]["tasks"]
                if t["kind"] == kind and (status is None or t["status"] == status))


def programme_result(task):
    return {
        "task_id": task["id"], "status": "ok",
        "claims": [{
            "kind": "programme", "scope": task["scope"],
            "claim": "The official page lists the 2027 MSc Marketing structure and duration",
            "impact": "material", "period": dict(PERIOD),
            "sources": [source(task["scope"])],
        }],
    }


def gate_result(task):
    return {
        "task_id": task["id"], "status": "ok",
        "claims": [{
            "kind": "eligibility", "scope": task["scope"],
            "claim": "The 2027 intake accepts a business bachelor degree",
            "impact": "critical", "period": dict(PERIOD),
            "sources": [source(task["scope"])],
        }],
        "gates": [{"id": "degree", "status": "pass"}],
    }


def researched_state(case=None):
    state = harness.init_state(case or base_case())
    harness.plan_tasks(state)
    programme = find_task(state, "programme")
    first = harness.record_result(state, programme_result(programme))
    gate = find_task(state, "eligibility")
    second = harness.record_result(state, gate_result(gate))
    return state, first["added"][0], second["added"][0]


def decision_doc(course_id, degree_id):
    return {
        "schema": decision.VERSION,
        "conclusion": {"type": "recommend", "choices": [{"offer": "a", "path": "private"}]},
        "headline": "选择 A University 的 2027 MSc Marketing",
        "reasons": ["课程与目标岗位匹配", "费用低于绝对上限"],
        "risks": [],
        "reversal": "若入学资格或预算发生变化，则重新评估",
        "assessments": [{
            "offer": "a", "path": "private", "gate": "pass", "score_state": "confirmed",
            "stance": "recommend", "value": "课程直接覆盖目标岗位技能",
            "competitiveness": "在目标市场达到可投递门槛",
            "evidence_ids": [degree_id, course_id],
        }],
    }


class HarnessCase(unittest.TestCase):
    def setUp(self):
        self._env = dict(os.environ)
        os.environ["OFFER_HARNESS_NOW"] = NOW

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)


class ResearchOrchestrationTests(HarnessCase):
    def test_plan_separates_classes_and_dependencies(self):
        state = harness.init_state(base_case(minor=True))
        tasks = harness.plan_tasks(state)
        classes = {t["kind"]: t["class"] for t in tasks}
        self.assertEqual(classes["eligibility"], "hard_gate")
        self.assertEqual(classes["programme"], "decisive")
        self.assertEqual(classes["network"], "optional")
        gate = find_task(state, "eligibility")
        programme = find_task(state, "programme")
        self.assertEqual(gate["depends_on"], [programme["id"]])
        self.assertTrue(gate["verification_route"])

    def test_plan_is_idempotent_and_preserves_closed_tasks(self):
        state, _, _ = researched_state()
        before = {t["id"]: t["status"] for t in state["research"]["tasks"]}
        harness.plan_tasks(state)
        after = {t["id"]: t["status"] for t in state["research"]["tasks"]}
        self.assertEqual(before, after)
        self.assertTrue(all(s == "done" for s in after.values()))

    def test_next_respects_dependency_order(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        out = harness.next_tasks(state, advance=True)
        self.assertFalse(out["stop"]["stop"])
        self.assertEqual([t["kind"] for t in out["tasks"]], ["programme"])
        self.assertTrue(any(row["event"] == "research_task_started" for row in state["trace"]))

    def test_next_stops_when_only_optional_work_remains(self):
        state = harness.init_state(base_case(minor=True))
        harness.plan_tasks(state)
        for task in state["research"]["tasks"]:
            if task["class"] != "optional":
                task["status"] = "done"
        out = harness.next_tasks(state)
        self.assertTrue(out["stop"]["stop"])
        self.assertEqual(out["stop"]["reason"], "research_complete")

    def test_round_limit_stops_the_loop(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        state["research"]["rounds"] = state["research"]["max_rounds"]
        out = harness.next_tasks(state)
        self.assertTrue(out["stop"]["stop"])
        self.assertEqual(out["stop"]["reason"], "max_rounds")

    def test_confirmed_evidence_does_not_auto_close_an_unresolved_gate(self):
        case = base_case()
        case["evidence"].append({
            "id": "degree", "offer": "a", "path": "private", "kind": "eligibility",
            "scope": "2027 intake MSc Marketing", "state": "confirmed", "impact": "critical",
            "claim": "The 2027 intake accepts a business bachelor degree",
            "period": dict(PERIOD), "sources": [source("2027 intake MSc Marketing")],
        })
        state = harness.init_state(case)
        harness.plan_tasks(state)
        gate = find_task(state, "eligibility")
        self.assertEqual(gate["status"], "todo")
        self.assertIn("degree", gate["reused_evidence_ids"])

    def test_plan_does_not_copy_private_profile_into_tasks(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        payload = json.dumps(state["research"]["tasks"], ensure_ascii=False)
        self.assertNotIn("agency internship", payload)


class ToolResultContractTests(HarnessCase):
    def test_result_without_claim_is_rejected(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        task = find_task(state, "programme")
        with self.assertRaises(ValueError):
            harness.record_result(state, {"task_id": task["id"], "status": "ok", "claims": []})

    def test_result_missing_locator_is_rejected(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        task = find_task(state, "programme")
        result = programme_result(task)
        del result["claims"][0]["sources"][0]["locator"]
        with self.assertRaises(ValueError):
            harness.record_result(state, result)

    def test_successful_result_records_evidence_and_trace(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        task = find_task(state, "programme")
        out = harness.record_result(state, programme_result(task))
        self.assertEqual(out["status"], "done")
        self.assertEqual(len(out["added"]), 1)
        events = [row["event"] for row in state["trace"]]
        for event in ("source_checked", "evidence_state_changed", "research_task_finished"):
            self.assertIn(event, events)
        self.assertEqual(state["metrics"]["tool_results"], 1)

    def test_repeated_fact_is_reused(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        task = find_task(state, "programme")
        harness.record_result(state, programme_result(task))
        count = len(state["case"]["evidence"])
        task["status"] = "todo"
        out = harness.record_result(state, programme_result(task))
        self.assertTrue(out["reused"])
        self.assertEqual(len(state["case"]["evidence"]), count)
        self.assertTrue(any(row["event"] == "research_reused" for row in state["trace"]))

    def test_error_retries_then_blocks_with_route(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        programme = find_task(state, "programme")
        harness.record_result(state, programme_result(programme))
        task = find_task(state, "eligibility")
        for _ in range(task["max_attempts"]):
            out = harness.record_result(state, {"task_id": task["id"], "status": "error",
                                                "error": "network unavailable"})
        self.assertEqual(out["status"], "blocked")
        self.assertTrue(out["route"])

    def test_blocked_source_cannot_close_a_hard_gate(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        programme = find_task(state, "programme")
        harness.record_result(state, programme_result(programme))
        task = find_task(state, "eligibility")
        out = harness.record_result(state, {
            "task_id": task["id"], "status": "partial",
            "claims": [{"claim": "Not visible behind the login wall", "state": "unresolved",
                        "impact": "critical", "scope": task["scope"],
                        "sources": [source(task["scope"], access="blocked", support="unreviewed")]}],
        })
        self.assertNotEqual(out["status"], "done")
        gate = next(g for g in state["case"]["offers"][0]["gates"] if g["id"] == "degree")
        self.assertEqual(gate["status"], "unresolved")

    def test_contradiction_is_flagged_and_downgraded(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        programme = find_task(state, "programme")
        harness.record_result(state, programme_result(programme))
        task = find_task(state, "eligibility")
        harness.record_result(state, gate_result(task))
        task["status"] = "todo"
        conflicting = gate_result(task)
        conflicting["claims"][0]["claim"] = "The 2027 intake requires a marketing bachelor degree"
        out = harness.record_result(state, conflicting)
        self.assertTrue(out["conflicts"])
        self.assertEqual(out["status"], "blocked")
        summary = harness.verify_evidence(state)
        self.assertTrue(summary["contradictions"])
        self.assertTrue(summary["downgraded"])


class EvidenceVerificationTests(HarnessCase):
    def test_stale_access_is_downgraded(self):
        case = base_case()
        case["evidence"][0] = fee_evidence(accessed="2024-01-01")
        state = harness.init_state(case)
        summary = harness.verify_evidence(state, as_of="2026-11-23", max_age_days=365)
        self.assertIn("fee", summary["downgraded"])
        self.assertEqual(state["case"]["evidence"][0]["state"], "unresolved")

    def test_out_of_period_claim_is_downgraded(self):
        state = harness.init_state(base_case())
        state["case"]["evidence"][0]["period"] = {"from": "2026-01-01", "through": "2026-12-31"}
        summary = harness.verify_evidence(state, as_of="2026-11-23")
        self.assertIn("fee", summary["downgraded"])

    def test_scope_mismatch_is_downgraded(self):
        state = harness.init_state(base_case())
        state["case"]["evidence"][0]["sources"][0]["scope"] = "university-wide"
        summary = harness.verify_evidence(state, as_of="2026-11-23")
        self.assertIn("fee", summary["downgraded"])

    def test_fresh_verified_evidence_survives(self):
        state = harness.init_state(base_case())
        summary = harness.verify_evidence(state, as_of="2026-11-23")
        self.assertEqual(summary["downgraded"], [])
        self.assertEqual(state["case"]["evidence"][0]["state"], "confirmed")

    def test_verification_says_semantic_support_needs_review(self):
        state = harness.init_state(base_case())
        summary = harness.verify_evidence(state, as_of="2026-11-23")
        self.assertIn("fee", summary["semantic_review_required"])
        self.assertIn("model or human", summary["note"])

    def test_downgrade_reopens_dependent_gate_and_traces_it(self):
        state, _, _ = researched_state()
        state["case"]["evidence"][-1]["period"] = {"from": "2026-01-01", "through": "2026-12-31"}
        summary = harness.verify_evidence(state, as_of="2026-11-23")
        self.assertTrue(summary["gate_changes"])
        gate = next(g for g in state["case"]["offers"][0]["gates"] if g["id"] == "degree")
        self.assertEqual(gate["status"], "unresolved")
        self.assertTrue(any(row["event"] == "gate_state_changed" for row in state["trace"]))


class DecisionIntegrationTests(HarnessCase):
    def test_recommendation_is_blocked_while_hard_gate_is_open(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        with self.assertRaisesRegex(ValueError, "hard-gate"):
            harness.store_decision(state, decision_doc("missing", "missing"))

    def test_wrong_citation_is_rejected(self):
        state, course, degree = researched_state()
        state["case"]["evidence"].append({
            "id": "foreign", "offer": "a", "path": "soe", "kind": "market",
            "scope": "SOE recruiting", "state": "confirmed", "impact": "material",
            "claim": "A state-owned employer recruits this profile",
            "period": dict(PERIOD), "sources": [source("SOE recruiting")],
        })
        doc = decision_doc(course, degree)
        doc["assessments"][0]["evidence_ids"].append("foreign")
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            harness.store_decision(state, doc)

    def test_valid_decision_quick_and_full_share_one_source(self):
        state, course, degree = researched_state()
        harness.store_decision(state, decision_doc(course, degree))
        quick = harness.report(state, "quick")
        full = harness.report(state, "full")
        self.assertTrue(full.startswith(quick))
        self.assertIn("费用与预算", quick)

    def test_stale_decision_is_refused_after_case_change(self):
        state, course, degree = researched_state()
        harness.store_decision(state, decision_doc(course, degree))
        state["case"]["budget"]["ceiling"] = 100000
        with self.assertRaisesRegex(ValueError, "stale"):
            harness.report(state, "quick")

    def test_conditional_decision_preserves_unresolved_gate(self):
        state = harness.init_state(base_case())
        harness.plan_tasks(state)
        doc = {
            "schema": decision.VERSION,
            "conclusion": {"type": "defer", "choices": []},
            "headline": "资格未核实前暂缓决定",
            "reasons": ["入学资格仍未核实"],
            "risks": ["若资格不满足则路径不成立"],
            "reversal": "核实 2027 intake 资格后重新评估",
            "assessments": [{
                "offer": "a", "path": "private", "gate": "unresolved", "score_state": "nrsy",
                "stance": "defer", "value": "暂无法判断", "competitiveness": "暂无法判断",
                "evidence_ids": [],
            }],
        }
        harness.store_decision(state, doc)
        self.assertEqual(state["decision"]["conclusion"]["type"], "defer")
        self.assertTrue(any(row["event"] == "recommendation" for row in state["trace"]))

    def test_cost_arithmetic_matches_the_engine(self):
        state, course, degree = researched_state()
        computed = harness.store_decision(state, decision_doc(course, degree))["computed"]
        direct = decision.analyze(state["case"])
        self.assertEqual(computed["offers"]["a"]["cost"]["cash"],
                         direct["offers"]["a"]["cost"]["cash"])


class ScenarioIsolationTests(HarnessCase):
    def test_counterfactual_does_not_mutate_base_case(self):
        state, _, _ = researched_state()
        before = harness.digest(state["case"])
        harness.scenario(state, {"field": "ceiling", "value": 200000}, "low_budget")
        self.assertEqual(harness.digest(state["case"]), before)
        self.assertNotIn("low_budget", json.dumps(state["case"]))

    def test_career_change_reopens_only_the_scenario_gates(self):
        state, _, _ = researched_state()
        base_gate = next(g for g in state["case"]["offers"][0]["gates"] if g["id"] == "degree")
        scenario = harness.scenario(state, {"field": "career", "value": "finance"}, "finance")
        self.assertEqual(base_gate["status"], "pass")
        scenario_gate = next(g for g in scenario["case"]["offers"][0]["gates"] if g["id"] == "degree")
        self.assertEqual(scenario_gate["status"], "unresolved")
        self.assertTrue(scenario["review_routes"])

    def test_budget_change_compares_multiple_offers(self):
        state = harness.init_state(base_case(offers=2))
        harness.plan_tasks(state)
        scenario = harness.scenario(state, {"field": "ceiling", "value": 200000}, "cap")
        self.assertEqual(scenario["summary"]["a"]["budget_gate"], "fail")
        self.assertEqual(scenario["summary"]["b"]["budget_gate"], "fail")
        self.assertEqual(set(scenario["summary"]), {"a", "b"})

    def test_duplicate_scenario_name_is_rejected(self):
        state = harness.init_state(base_case())
        harness.scenario(state, {"field": "ceiling", "value": 200000}, "cap")
        with self.assertRaises(ValueError):
            harness.scenario(state, {"field": "ceiling", "value": 100000}, "cap")


class StateAndPrivacyTests(HarnessCase):
    def test_checkpoint_and_resume_keep_verified_evidence(self):
        state, _, _ = researched_state()
        snap = harness.checkpoint(state)
        self.assertTrue(snap["confirmed_evidence_ids"])
        resumed = harness.resume(state)
        self.assertEqual(resumed["phase"], "adjudicate")
        self.assertFalse(resumed["decision_stale"])

    def test_resume_rechecks_expired_evidence(self):
        state, _, _ = researched_state()
        state["case"]["evidence"][0]["sources"][0]["accessed"] = "2024-01-01"
        harness.resume(state)
        self.assertEqual(state["case"]["evidence"][0]["state"], "unresolved")

    def test_privacy_expiry_and_purge(self):
        state = harness.init_state(base_case())
        os.environ["OFFER_HARNESS_NOW"] = "2026-12-05T10:00:00+08:00"
        report = harness.privacy(state)
        self.assertTrue(report["expired"])
        harness.privacy(state, purge=True)
        self.assertEqual(state["case"]["profile"], {})
        self.assertTrue(state["privacy"]["purged_at"])

    def test_identifier_keys_are_flagged_not_silently_accepted(self):
        case = base_case()
        case["profile"]["student_id"] = "12345678"
        state = harness.init_state(case)
        self.assertIn("student_id", state["privacy"]["identifier_warnings"])

    def test_full_trace_covers_the_execution_chain(self):
        state, course, degree = researched_state()
        harness.store_decision(state, decision_doc(course, degree))
        harness.report(state, "quick")
        events = {row["event"] for row in state["trace"]}
        for event in ("state_initialized", "plan_created", "research_task_started",
                      "source_checked", "research_task_finished", "evidence_state_changed",
                      "gate_state_changed", "calculation", "decision_stored",
                      "recommendation", "report_rendered"):
            self.assertIn(event, events)


class VersionComparisonTests(HarnessCase):
    def test_v2_catches_an_expired_source_that_v1_accepts(self):
        case = base_case()
        case["evidence"][0] = fee_evidence(accessed="2024-01-01")
        # v1 validates structure and period only, so the old page still passes.
        decision.analyze(case)
        state = harness.init_state(case)
        summary = harness.verify_evidence(state, as_of="2026-11-23")
        self.assertIn("fee", summary["downgraded"])

    def test_v2_adds_research_state_without_changing_v1_tasks(self):
        case = base_case()
        v1_tasks = decision.research(case)["tasks"]
        state = harness.init_state(case)
        v2_tasks = harness.plan_tasks(state)
        self.assertEqual({(t["offer_id"], t["path"], t["topic"], t["scope"]) for t in v1_tasks},
                         {(t["offer_id"], t["path"], t["kind"], t["scope"]) for t in v2_tasks})
        self.assertTrue(all("status" in t for t in v2_tasks))
        self.assertTrue(all("status" not in t for t in v1_tasks))

    def test_both_layers_isolate_counterfactuals(self):
        case = base_case()
        before = harness.digest(case)
        decision.scenario(case, {"field": "ceiling", "value": 200000})
        self.assertEqual(harness.digest(case), before)
        state = harness.init_state(case)
        harness.scenario(state, {"field": "ceiling", "value": 200000}, "cap")
        self.assertEqual(harness.digest(state["case"]), before)


class FrozenRealSourceCaseTests(HarnessCase):
    """The 2026-11-23 real-source case, frozen as a regression fixture.

    Sources are recorded claims from opened official pages; the test itself
    never touches the network. The synthetic profile is the only private part.
    """

    def test_real_source_case_decides_and_counterfactual_is_isolated(self):
        base = ROOT / "docs" / "examples" / "v2-harness"
        case = json.loads((base / "case.json").read_text(encoding="utf-8"))
        state = harness.init_state(case)
        harness.plan_tasks(state)
        for offer_id, filename in (("warwick", "gate-warwick.json"),
                                   ("glasgow", "gate-glasgow.json")):
            task = next(t for t in state["research"]["tasks"]
                        if t["kind"] == "eligibility" and t["offer_id"] == offer_id)
            result = json.loads((base / filename).read_text(encoding="utf-8"))
            result["task_id"] = task["id"]
            harness.record_result(state, result)
        computed = harness.store_decision(
            state, json.loads((base / "decision.json").read_text(encoding="utf-8")))["computed"]
        self.assertEqual(list(computed["offers"]["warwick"]["cost"]["cash"]), [5450000, 5450000])
        self.assertEqual(list(computed["offers"]["glasgow"]["cost"]["cash"]), [4981500, 4981500])
        quick = harness.report(state, "quick")
        self.assertTrue(harness.report(state, "full").startswith(quick))
        before = harness.digest(state["case"])
        scenario = harness.scenario(
            state, json.loads((base / "change.json").read_text(encoding="utf-8")),
            "ceiling_53000")
        self.assertEqual(scenario["summary"]["warwick"]["budget_gate"], "fail")
        self.assertEqual(scenario["summary"]["glasgow"]["budget_gate"], "pass")
        self.assertEqual(harness.digest(state["case"]), before)


class CliTests(HarnessCase):
    def run_cli(self, *args, cwd):
        return subprocess.run([sys.executable, str(SCRIPTS / "harness.py"), *args],
                              cwd=cwd, capture_output=True, text=True,
                              env={**os.environ, "OFFER_HARNESS_NOW": NOW})

    def test_cli_init_plan_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "case.json"
            state_path = Path(tmp) / "state.json"
            case_path.write_text(json.dumps(base_case(), ensure_ascii=False), encoding="utf-8")
            init = self.run_cli("init", str(case_path), "--state", str(state_path), cwd=tmp)
            self.assertEqual(init.returncode, 0, init.stderr)
            plan = self.run_cli("plan", "--state", str(state_path), cwd=tmp)
            self.assertEqual(plan.returncode, 0, plan.stderr)
            self.assertTrue(json.loads(plan.stdout)["tasks"])
            status = self.run_cli("status", "--state", str(state_path), cwd=tmp)
            self.assertEqual(json.loads(status.stdout)["phase"], "research")

    def test_cli_rejects_incomplete_result_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "case.json"
            state_path = Path(tmp) / "state.json"
            case_path.write_text(json.dumps(base_case(), ensure_ascii=False), encoding="utf-8")
            self.run_cli("init", str(case_path), "--state", str(state_path), cwd=tmp)
            planned = json.loads(self.run_cli("plan", "--state", str(state_path), cwd=tmp).stdout)
            task = next(t for t in planned["tasks"] if t["kind"] == "programme")
            result_path = Path(tmp) / "result.json"
            result_path.write_text(json.dumps({"task_id": task["id"], "status": "ok",
                                               "claims": []}), encoding="utf-8")
            before = state_path.read_text(encoding="utf-8")
            bad = self.run_cli("record", "--state", str(state_path), str(result_path), cwd=tmp)
            self.assertEqual(bad.returncode, 2)
            self.assertIn("error", json.loads(bad.stderr))
            self.assertEqual(state_path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()

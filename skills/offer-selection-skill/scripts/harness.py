"""Local decision-harness state, research orchestration and evidence control.

The harness owns *execution* state around the existing decision engine:
research task planning/state, evidence provenance checks, checkpoints,
counterfactual isolation, privacy lifetime and an append-only trace.

It never re-implements the decision rules. Case and decision arithmetic,
gate semantics, evidence states, scoring and Quick/Full rendering all come
from `decision.py`, which remains the single owner of those rules.

No network access. No database. State is a local JSON document supplied by
the calling host agent.
"""

import argparse
import copy
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Import the decision engine from the same directory, whether this module is
# executed as a script or imported by a test loader.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import decision  # noqa: E402  (path setup must run first)


VERSION = "offer-harness/v1"
PHASES = ("intake", "research", "adjudicate", "decide", "done")
TASK_STATES = ("todo", "in_progress", "done", "blocked", "skipped")
RESULT_STATES = ("ok", "partial", "error", "blocked")
TASK_CLASSES = ("hard_gate", "decisive", "optional")
HARD_KINDS = {"eligibility", "credential", "work", "timing"}
CLASS_RANK = {"hard_gate": 0, "decisive": 1, "optional": 2}
DECISIVE_CONCLUSIONS = {"recommend", "parity_with_choice", "equivalent"}
DEFAULT_RETENTION_DAYS = 7
DEFAULT_MAX_AGE_DAYS = 365
DEFAULT_MAX_ROUNDS = 6
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_MAX_SUPPLEMENTS = 3
IDENTIFIER_KEY = re.compile(
    r"(?:^|_)(?:name|email|phone|mobile|student_?id|passport|national_?id|address|"
    r"wechat|whatsapp|linkedin)(?:$|_)", re.I)
# Execution-coverage roster derived from the existing core gate paragraph and
# the four path files. It is a diagnostic prompt, never a decision rule: a gap
# does not pass or fail a gate, it only says that the case never declared any
# research object of that kind for the active path.
PATH_COVERAGE = {
    "private": {"credential", "eligibility", "market", "cost"},
    "soe": {"credential", "eligibility", "timing", "cost"},
    "local": {"work", "market", "access", "cost"},
    "phd": {"academic", "programme", "cost"},
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def now_iso():
    override = os.environ.get("OFFER_HARNESS_NOW")
    if override:
        return override
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today():
    return date.fromisoformat(now_iso()[:10])


def digest(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def short_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def trace(document, event, **fields):
    record = {"at": now_iso(), "event": event}
    record.update(fields)
    document.setdefault("trace", []).append(record)
    document["updated_at"] = record["at"]
    return record


def metric(state, name, amount=1):
    metrics = state.setdefault("metrics", {})
    metrics[name] = metrics.get(name, 0) + amount


def mark_derived_stale(state, reason):
    """Invalidate the stored decision and counterfactual summaries.

    A scenario is a snapshot of the base case; once base evidence changes it
    cannot be presented as current. It is kept for audit rather than deleted.
    """
    if state.get("decision"):
        state["decision_state"]["stale"] = True
        state["decision_state"]["stale_reason"] = reason
    for row in state.get("scenarios", {}).values():
        row["stale"] = True
        row.setdefault("stale_reason", reason)


def load_state(path):
    state = decision.load(path)
    need(isinstance(state, dict), "state must be a JSON object")
    need(state.get("schema") == VERSION, f"unknown harness schema: {state.get('schema')}")
    need(isinstance(state.get("case"), dict), "state is missing the case")
    # A crash between write and replace can leave a copy of the previous state.
    # Once the real file loads, that residue has no recovery value.
    residue = Path(str(path) + ".tmp")
    if residue.exists():
        try:
            residue.unlink()
        except OSError:
            pass
    return state


def save_state(path, state):
    target = Path(path)
    temp = target.with_name(target.name + ".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, target)


# ---------------------------------------------------------------------------
# Research orchestration
# ---------------------------------------------------------------------------

def task_fingerprint(offer_id, path, kind, scope):
    return "|".join((offer_id, path, kind, str(scope).strip().lower()))


def task_id(offer_id, path, kind, scope, key):
    label = key or f"{kind}:{scope}"
    return "rt-" + short_hash(task_fingerprint(offer_id, path, kind, scope) + "|" + str(label))


def classify_gate(gate):
    if gate["status"] != "unresolved":
        return None
    return "hard_gate" if gate["kind"] in HARD_KINDS else "decisive"


def classify_evidence(entry):
    if entry["state"] == "confirmed" or entry["impact"] == "minor":
        return "optional"
    return "hard_gate" if entry["kind"] in HARD_KINDS else "decisive"


def authority_route(kind):
    if kind in {"eligibility", "credential", "work", "timing"}:
        return "the admitting institution, licensing/immigration authority or named employer"
    if kind == "cost":
        return "the institution's official tuition/fee page for the exact intake"
    if kind in {"programme", "academic"}:
        return "the institution's official programme and handbook pages"
    if kind == "market":
        return "the named employer's official recruiting channel or published outcomes"
    return "the authority that owns the exact scope named in the task"


def question_for(task):
    return (f"For {task['offer']} / {task['path']}, verify: {task['scope']}. "
            f"Record the opened source, its authority and what the located text supports.")


def evidence_fingerprint_index(case):
    index = {}
    for entry in case["evidence"]:
        index.setdefault(task_fingerprint(entry["offer"], entry["path"], entry["kind"], entry["scope"]),
                         []).append(entry)
    return index


def coverage(state):
    """Report declared vs confirmed research kinds for each active path.

    This is deliberately advisory. A missing kind means the case never declared
    a gate, evidence item or task of that kind; it does not prove the topic is
    irrelevant, and it never changes a gate or recommendation.
    """
    case = state["case"]
    paths = sorted(set(case["goal"]["paths"]))
    rows, gaps, open_topics = {}, [], []
    for path in paths:
        required = PATH_COVERAGE.get(path, set())
        declared, confirmed = set(), set()
        for offer in case["offers"]:
            for gate in offer["gates"]:
                if gate["path"] in {path, "*"}:
                    declared.add(gate["kind"])
                    if gate["status"] in {"pass", "fail"}:
                        confirmed.add(gate["kind"])
        for entry in case["evidence"]:
            if entry["path"] in {path, "*"}:
                declared.add(entry["kind"])
                if entry["state"] == "confirmed":
                    confirmed.add(entry["kind"])
        for task in state["research"]["tasks"]:
            if task["path"] in {path, "*"}:
                declared.add(task["kind"])
        missing = sorted(required - declared)
        unconfirmed = sorted(required & declared - confirmed)
        rows[path] = {
            "required": sorted(required),
            "declared": sorted(required & declared),
            "confirmed": sorted(required & confirmed),
            "missing": missing,
            "unconfirmed": unconfirmed,
        }
        gaps.extend({"path": path, "kind": kind} for kind in missing)
        open_topics.extend({"path": path, "kind": kind} for kind in unconfirmed)
    return {
        "paths": rows, "gaps": gaps, "unconfirmed": open_topics,
        "note": ("Coverage is derived from declared gates, evidence and tasks. "
                 "A missing kind is not a pass; research it or record why the active "
                 "path makes it not applicable."),
    }


def plan_tasks(state):
    """Rebuild the task roster without duplicating completed research."""
    case = state["case"]
    old = {task["id"]: task for task in state["research"]["tasks"]}
    base = decision.research(case)
    confirmed = evidence_fingerprint_index(case)
    tasks = []

    def add(priority, offer_id, offer_title, country, path, kind, scope, key, cls, depends,
            gate_open=False):
        tid = task_id(offer_id, path, kind, scope, key)
        fingerprint = task_fingerprint(offer_id, path, kind, scope)
        previous = old.get(tid)
        reused = [e["id"] for e in confirmed.get(fingerprint, [])
                  if e["offer"] == offer_id and e["state"] == "confirmed"]
        default = "todo" if gate_open or not reused else "done"
        status = previous["status"] if previous else default
        if previous and previous["status"] == "done" and default == "todo":
            # A gate still needs an explicit adjudication, or a later
            # verification downgraded the evidence that closed this task.
            status = "todo"
        task = {
            "id": tid, "offer_id": offer_id, "offer": offer_title, "country": country,
            "path": path, "kind": kind, "scope": scope, "class": cls,
            "priority": priority, "depends_on": list(depends), "status": status,
            "attempts": previous.get("attempts", 0) if previous else 0,
            "max_attempts": previous.get("max_attempts", DEFAULT_MAX_ATTEMPTS) if previous else DEFAULT_MAX_ATTEMPTS,
            "origin": previous.get("origin", "plan") if previous else "plan",
            "fingerprint": fingerprint, "reused_evidence_ids": reused,
            "verification_route": authority_route(kind),
            "question": question_for({"offer": offer_title, "path": path, "scope": scope}),
        }
        if previous and previous.get("last_error"):
            task["last_error"] = previous["last_error"]
        tasks.append(task)
        return task

    for item in base["tasks"]:
        offer = next(o for o in case["offers"] if o["id"] == item["offer_id"])
        path = item["path"]
        kind = item["topic"]
        scope = item["scope"]
        if kind == "cost":
            budgeted = case["budget"].get("ceiling") is not None or case["budget"].get("target") is not None
            cls = "decisive" if budgeted or item["priority"] == 0 else "optional"
        elif kind == "programme":
            cls = "decisive"
        else:
            gate = next((g for g in offer["gates"] if g["id"] == item["key"]), None)
            if gate:
                cls = classify_gate(gate) or "decisive"
            else:
                entry = next((e for e in case["evidence"] if e["id"] == item["key"]), None)
                cls = classify_evidence(entry) if entry else "decisive"
        gate = next((g for g in offer["gates"] if g["id"] == item["key"]), None)
        tasks.append({
            "pending": True, "priority": item["priority"], "offer": offer, "path": path,
            "kind": kind, "scope": scope, "key": item["key"], "class": cls,
            "gate_open": bool(gate and gate["status"] == "unresolved"),
        })

    # Optional tier: unresolved minor evidence is useful but never blocks a stop.
    for entry in case["evidence"]:
        if entry["state"] != "confirmed" and entry["impact"] == "minor":
            offer = next(o for o in case["offers"] if o["id"] == entry["offer"])
            tasks.append({
                "pending": True, "priority": 2, "offer": offer, "path": entry["path"],
                "kind": entry["kind"], "scope": entry["scope"], "key": entry["id"],
                "class": "optional",
            })

    programme_ids = {}
    for item in tasks:
        if item["kind"] == "programme":
            programme_ids.setdefault(item["offer"]["id"], task_id(
                item["offer"]["id"], item["path"], item["kind"], item["scope"], item["key"]))

    result = []
    for item in sorted(tasks, key=lambda v: (CLASS_RANK[v["class"]], v["priority"],
                                              v["offer"]["id"], v["kind"], v["scope"])):
        depends = []
        parent = programme_ids.get(item["offer"]["id"])
        if parent and item["kind"] != "programme":
            depends = [parent]
        result.append(add(item["priority"], item["offer"]["id"], item["offer"]["title"],
                          item["offer"]["country"], item["path"], item["kind"],
                          item["scope"], item["key"], item["class"], depends,
                          gate_open=item.get("gate_open", False)))

    merged = {task["id"]: task for task in result}
    offer_ids = {offer["id"] for offer in case["offers"]}
    # Keep closed history and host-added supplements rather than silently
    # forgetting research that was already done.
    for task in old.values():
        if task["id"] not in merged and task["offer_id"] in offer_ids:
            merged[task["id"]] = task
    state["research"]["tasks"] = sorted(
        merged.values(), key=lambda t: (CLASS_RANK[t["class"]], t["priority"], t["id"]))
    if state["phase"] == "intake":
        state["phase"] = "research"
    cov = coverage(state)
    trace(state, "plan_created", tasks=len(state["research"]["tasks"]),
          hard_gate=sum(t["class"] == "hard_gate" for t in state["research"]["tasks"]),
          decisive=sum(t["class"] == "decisive" for t in state["research"]["tasks"]),
          optional=sum(t["class"] == "optional" for t in state["research"]["tasks"]),
          coverage_gaps=len(cov["gaps"]), coverage_unconfirmed=len(cov["unconfirmed"]))
    return state["research"]["tasks"]


def open_tasks(state, classes=("hard_gate", "decisive")):
    return [t for t in state["research"]["tasks"]
            if t["class"] in classes and t["status"] in {"todo", "in_progress"}]


def blocked_tasks(state, classes=("hard_gate", "decisive")):
    return [t for t in state["research"]["tasks"]
            if t["class"] in classes and t["status"] == "blocked"]


def ready(task, tasks):
    index = {t["id"]: t for t in tasks}
    return all(index.get(dep, {}).get("status") == "done" for dep in task["depends_on"])


def stop_condition(state):
    research = state["research"]
    if not open_tasks(state) and not blocked_tasks(state):
        return {"stop": True, "reason": "research_complete",
                "detail": "No open hard-gate or decisive research task remains."}
    if research["rounds"] >= research["max_rounds"]:
        return {"stop": True, "reason": "max_rounds",
                "detail": f"Research round limit {research['max_rounds']} reached; keep unresolved facts unresolved."}
    if blocked_tasks(state) and not open_tasks(state):
        return {"stop": True, "reason": "blocked_with_routes",
                "detail": "Every remaining decisive task is blocked; use its verification route."}
    return {"stop": False, "reason": None, "detail": None}


def next_tasks(state, limit=5, advance=False):
    tasks = state["research"]["tasks"]
    condition = stop_condition(state)
    if condition["stop"]:
        trace(state, "stop_condition", reason=condition["reason"], detail=condition["detail"])
        return {"stop": condition, "tasks": []}
    selected = []
    for task in tasks:
        if len(selected) >= limit:
            break
        if task["status"] in {"todo", "in_progress"} and ready(task, tasks):
            selected.append(task)
    if advance:
        state["research"]["rounds"] += 1
        metric(state, "research_rounds")
        for task in selected:
            if task["status"] == "todo":
                task["status"] = "in_progress"
                trace(state, "research_task_started", task=task["id"], offer=task["offer_id"],
                      path=task["path"], kind=task["kind"], scope=task["scope"])
        condition = stop_condition(state)
    return {"stop": condition, "tasks": selected,
            "rounds": state["research"]["rounds"],
            "remaining": len(open_tasks(state)),
            "coverage": coverage(state)}


def _valid_source(source):
    need(isinstance(source, dict), "source must be an object")
    for key in ("url", "authority", "scope", "accessed", "locator", "inspection"):
        need(key in source, f"tool result source is missing {key}")
    need(isinstance(source["url"], str) and source["url"].startswith(("http://", "https://")),
         "tool result source needs an http(s) URL")
    need(isinstance(source["inspection"], dict), "source inspection must be an object")
    review = source["inspection"]
    need(review.get("access") in {"opened", "blocked", "unopened"}, "invalid access in tool result")
    need(review.get("support") in {"supported", "partial", "unsupported", "unreviewed"},
         "invalid support in tool result")
    if review["access"] == "opened" and review["support"] in {"supported", "partial", "unsupported"}:
        need(isinstance(review.get("observation"), str) and review["observation"].strip(),
             "an opened reviewed source needs an observation")
    return True


def _normalise_claim(task, raw):
    need(isinstance(raw, dict), "each claim must be an object")
    claim = {
        "id": raw.get("id"),
        "offer": raw.get("offer", task["offer_id"]),
        "path": raw.get("path", task["path"]),
        "kind": raw.get("kind", task["kind"]),
        "scope": raw.get("scope", task["scope"]),
        "state": raw.get("state", "confirmed"),
        "impact": raw.get("impact", "critical" if task["class"] == "hard_gate" else "material"),
        "claim": raw.get("claim"),
    }
    for key in ("period", "operative_date", "effect"):
        if key in raw:
            claim[key] = raw[key]
    need(isinstance(claim["claim"], str) and claim["claim"].strip(),
         "each claim needs a non-empty claim text")
    need(claim["state"] in {"confirmed", "prior", "unresolved"}, "invalid claim state")
    need(claim["impact"] in {"critical", "material", "minor"}, "invalid claim impact")
    need(claim["offer"] == task["offer_id"] and claim["path"] == task["path"],
         "tool result cannot answer a different offer/path")
    sources = raw.get("sources", [])
    need(isinstance(sources, list), "claim sources must be an array")
    for source in sources:
        _valid_source(source)
    claim["sources"] = sources
    if claim["state"] == "confirmed":
        need(any(s["inspection"]["access"] == "opened"
                 and s["inspection"]["support"] == "supported" for s in sources),
             "confirmed claim needs an opened source whose located text supports it")
        period = claim.get("period")
        need(isinstance(period, dict) and {"from", "through"} <= period.keys(),
             "confirmed claim needs its operative period")
    if not claim["id"]:
        claim["id"] = "ev-" + short_hash("|".join((
            task["fingerprint"], claim["claim"], sources[0]["url"] if sources else "")))
    return claim


def _same_claim_text(left, right):
    return " ".join(left.lower().split()) == " ".join(right.lower().split())


def record_result(state, result):
    need(isinstance(result, dict), "tool result must be a JSON object")
    need("task_id" in result and "status" in result, "tool result needs task_id and status")
    need(result["status"] in RESULT_STATES, "invalid tool result status")
    task = next((t for t in state["research"]["tasks"] if t["id"] == result["task_id"]), None)
    need(task is not None, "unknown research task")
    need(task["status"] not in {"done", "skipped"}, "research task is already closed")
    need(ready(task, state["research"]["tasks"]),
         "research task dependencies are not done: " + ", ".join(task["depends_on"]))
    need(state["phase"] != "done", "case is complete; resume or start a new case before more research")
    if task["status"] == "todo":
        task["status"] = "in_progress"
        trace(state, "research_task_started", task=task["id"], offer=task["offer_id"],
              path=task["path"], kind=task["kind"], scope=task["scope"])
    task["attempts"] += 1
    metric(state, "tool_results")
    if task["attempts"] > 1:
        metric(state, "retries")

    if result["status"] in {"error", "blocked"}:
        task["last_error"] = str(result.get("error", "tool failure"))[:500]
        if result["status"] == "blocked" or task["attempts"] >= task["max_attempts"]:
            task["status"] = "blocked"
            task["blocked_reason"] = "tool_blocked" if result["status"] == "blocked" else "tool_error"
        trace(state, "research_task_finished", task=task["id"], status=task["status"],
              error=task["last_error"], attempts=task["attempts"])
        trace(state, "source_checked", task=task["id"], checked=0, failed=True)
        if task["status"] == "blocked":
            metric(state, "blocked")
        return {"task": task, "status": task["status"],
                "route": task["verification_route"], "attempts": task["attempts"]}

    claims = result.get("claims")
    need(isinstance(claims, list) and claims, "a successful result needs at least one claim")
    prepared = [_normalise_claim(task, raw) for raw in claims]
    if any(not c["sources"] for c in prepared):
        raise ValueError("incomplete tool result: a claim has no source record")
    if result["status"] == "ok" and any(
            not any(s["inspection"]["access"] == "opened" for s in c["sources"])
            for c in prepared):
        raise ValueError("incomplete tool result: no opened source for a successful check")

    index = decision.indexed(state["case"]["evidence"])
    existing_by_fp = evidence_fingerprint_index(state["case"])
    added, reused, conflicts = [], [], []
    for claim in prepared:
        fingerprint = task_fingerprint(claim["offer"], claim["path"], claim["kind"], claim["scope"])
        same_slot = existing_by_fp.get(fingerprint, [])
        confirmed = [e for e in same_slot if e["state"] == "confirmed"]
        if confirmed:
            reused_id = confirmed[0]["id"]
            conflicting = [e for e in confirmed if not _same_claim_text(e["claim"], claim["claim"])]
            if conflicting:
                conflicts.append({"ids": [e["id"] for e in conflicting], "new_claim": claim["claim"]})
                claim["state"] = "unresolved"
                claim["impact"] = "critical"
                trace(state, "evidence_contradiction", task=task["id"], existing=conflicting[0]["id"],
                      incoming=claim["id"], scope=claim["scope"])
            else:
                reused.append(reused_id)
                trace(state, "research_reused", task=task["id"], evidence=reused_id)
                continue
        if claim["id"] in index:
            claim["id"] = "ev-" + short_hash(claim["id"] + "|" + claim["claim"] + "|" + now_iso())
        state["case"]["evidence"].append(claim)
        index[claim["id"]] = claim
        existing_by_fp.setdefault(fingerprint, []).append(claim)
        state["evidence_meta"][claim["id"]] = {
            "task_id": task["id"], "fingerprint": fingerprint,
            "checked_at": now_iso(), "max_age_days": DEFAULT_MAX_AGE_DAYS,
            "semantic_review": "model_or_human",
        }
        added.append(claim["id"])
        trace(state, "source_checked", task=task["id"], evidence=claim["id"],
              sources=len(claim["sources"]),
              opened=sum(s["inspection"]["access"] == "opened" for s in claim["sources"]),
              support=[s["inspection"]["support"] for s in claim["sources"]])
        trace(state, "evidence_state_changed", evidence=claim["id"],
              state=claim["state"], impact=claim["impact"])

    gate_updates = result.get("gates", [])
    need(isinstance(gate_updates, list), "gates must be an array")
    offer = next(o for o in state["case"]["offers"] if o["id"] == task["offer_id"])
    applied = []
    for update in gate_updates:
        need(isinstance(update, dict) and "id" in update and "status" in update,
             "each gate update needs id and status")
        gate = next((g for g in offer["gates"] if g["id"] == update["id"]), None)
        need(gate is not None, f"unknown gate in tool result: {update['id']}")
        need(update["status"] in {"pass", "fail", "unresolved", "not_applicable"},
             "invalid gate status in tool result")
        if update["status"] in {"pass", "fail"}:
            support = [cid for cid in gate["evidence_ids"] + added + reused
                       if cid in index and index[cid]["state"] == "confirmed"
                       and index[cid]["kind"] == gate["kind"]
                       and index[cid]["scope"] == gate["scope"]
                       and index[cid]["path"] in {gate["path"], "*"}]
            need(support, f"gate {gate['id']} cannot be decided without confirmed scoped evidence")
        gate["status"] = update["status"]
        gate["evidence_ids"] = list(dict.fromkeys(gate["evidence_ids"] + added + reused))
        applied.append(gate["id"])
        trace(state, "gate_state_changed", offer=offer["id"], gate=gate["id"], state=gate["status"])

    follow_up = result.get("follow_up")
    if follow_up:
        need(isinstance(follow_up, dict), "follow_up must be an object")
        research = state["research"]
        need(research["supplements"] < research["max_supplements"],
             "supplement limit reached; keep the remaining question unresolved")
        kind = follow_up.get("kind", task["kind"])
        scope = follow_up.get("scope", task["scope"])
        need(kind in decision.KINDS, "invalid follow-up kind")
        tid = task_id(task["offer_id"], task["path"], kind, scope, follow_up.get("why", scope))
        if not any(t["id"] == tid for t in research["tasks"]):
            research["supplements"] += 1
            research["tasks"].append({
                "id": tid, "offer_id": task["offer_id"], "offer": task["offer"],
                "country": task["country"], "path": task["path"], "kind": kind,
                "scope": scope, "class": "optional", "priority": 2,
                "depends_on": [], "status": "todo", "attempts": 0,
                "max_attempts": DEFAULT_MAX_ATTEMPTS, "origin": "supplement",
                "fingerprint": task_fingerprint(task["offer_id"], task["path"], kind, scope),
                "reused_evidence_ids": [],
                "verification_route": authority_route(kind),
                "question": question_for({"offer": task["offer"], "path": task["path"],
                                          "scope": scope}),
            })
            trace(state, "research_task_created", task=tid, origin="supplement",
                  supplements=research["supplements"])

    opened = any(source["inspection"]["access"] == "opened"
                 for claim in prepared for source in claim["sources"])
    if conflicts:
        task["status"] = "blocked"
        task["blocked_reason"] = "contradiction"
        task["last_error"] = "contradictory confirmed evidence"
    elif not opened and task["class"] in {"hard_gate", "decisive"}:
        task["status"] = "blocked" if task["attempts"] >= task["max_attempts"] else "todo"
        task["blocked_reason"] = "unopened_source" if task["status"] == "blocked" else None
        task["last_error"] = "no opened source yet; do not treat this as verified"
    elif result["status"] == "partial" and task["class"] in {"hard_gate", "decisive"}:
        task["status"] = "blocked" if task["attempts"] >= task["max_attempts"] else "todo"
        task["blocked_reason"] = "partial_result" if task["status"] == "blocked" else None
        task["last_error"] = "partial tool result"
    else:
        task["status"] = "done"
        task["blocked_reason"] = None
    trace(state, "research_task_finished", task=task["id"], status=task["status"],
          added=added, reused=reused, attempts=task["attempts"])
    if added or reused:
        mark_derived_stale(state, "new evidence recorded")
    if state["phase"] == "research":
        state["phase"] = "adjudicate"
    return {"task": task, "status": task["status"], "added": added, "reused": reused,
            "gates": applied, "conflicts": conflicts,
            "route": task["verification_route"] if task["status"] == "blocked" else None}


# ---------------------------------------------------------------------------
# Evidence verification
# ---------------------------------------------------------------------------

def _evidence_defects(entry, operative, as_of, max_age_days):
    defects = list(decision.source_defects(entry, operative))
    stale = []
    for source in entry.get("sources", []):
        accessed = source.get("accessed")
        if accessed and date.fromisoformat(accessed) + timedelta(days=max_age_days) < as_of:
            stale.append(source["url"])
    if stale:
        defects.append("source access is older than the configured freshness window")
    return defects


def verify_evidence(state, as_of=None, max_age_days=DEFAULT_MAX_AGE_DAYS):
    case = state["case"]
    when = date.fromisoformat(as_of) if as_of else today()
    offers = decision.indexed(case["offers"])
    before_gates = {(o["id"], g["id"]): g["status"] for o in case["offers"] for g in o["gates"]}
    report = {}
    changed = []
    review = []
    by_fp = evidence_fingerprint_index(case)
    contradictions = set()
    for group in by_fp.values():
        confirmed = [e for e in group if e["state"] == "confirmed"]
        relevant = [e for e in group if e["state"] in {"confirmed", "unresolved"}]
        texts = {" ".join(e["claim"].lower().split()) for e in relevant}
        if len(texts) > 1 and confirmed:
            # A verified claim contradicted by another scoped record cannot stay
            # confirmed until a human or model adjudicates the conflict.
            for entry in confirmed:
                contradictions.add(entry["id"])

    for entry in case["evidence"]:
        operative = date.fromisoformat(entry.get("operative_date", offers[entry["offer"]]["operative_date"]))
        defects = _evidence_defects(entry, operative, when, max_age_days)
        if entry["id"] in contradictions:
            defects.append("contradictory confirmed claims share the same offer/path/kind/scope")
        supported = [s for s in entry.get("sources", [])
                     if s["authority"] in decision.AUTHORITY and s["scope"] == entry["scope"]
                     and decision.inspect_source(s)]
        authority = sorted({s["authority"] for s in supported})
        status = "verified"
        if defects:
            status = "unresolved"
        elif entry["state"] != "confirmed":
            status = "unconfirmed"
        elif not supported:
            status = "unresolved"
        report[entry["id"]] = {
            "status": status, "defects": defects, "authority": authority,
            "checked_at": now_iso(), "semantic_review": "model_or_human",
            "applicable": decision.applicable_label(entry),
        }
        if entry["state"] == "confirmed":
            review.append(entry["id"])
        if status == "unresolved" and entry["state"] == "confirmed":
            entry["state"] = "unresolved"
            changed.append(entry["id"])
            trace(state, "evidence_state_changed", evidence=entry["id"], state="unresolved",
                  defects=defects)

    state["verification"] = report
    metric(state, "evidence_checks")
    if changed:
        metric(state, "evidence_downgrades", len(changed))
        # Reuse the engine's conservative propagation: dependent gates reopen and
        # finite costs become unbounded in the returned copy.
        revised = decision.audit(case)["input"]
        state["case"] = revised
        mark_derived_stale(state, "evidence downgraded during verification")
    after_gates = {(o["id"], g["id"]): g["status"] for o in state["case"]["offers"] for g in o["gates"]}
    gate_changes = [{"offer": key[0], "gate": key[1], "before": before_gates[key],
                     "after": after_gates[key]}
                    for key in before_gates if before_gates[key] != after_gates[key]]
    for row in gate_changes:
        trace(state, "gate_state_changed", offer=row["offer"], gate=row["gate"],
              before=row["before"], state=row["after"])
    summary = {
        "checked_at": now_iso(), "as_of": when.isoformat(), "max_age_days": max_age_days,
        "evidence": len(report), "downgraded": changed, "gate_changes": gate_changes,
        "contradictions": sorted(contradictions),
        "semantic_review_required": review,
        "note": ("Programmatic checks cover structure, scope, period, freshness and dependency. "
                 "Whether a source truly entails the claim still needs model or human review."),
    }
    trace(state, "calculation", kind="evidence_verification", downgraded=len(changed),
          contradictions=len(contradictions))
    return summary


# ---------------------------------------------------------------------------
# Decision integration and execution control
# ---------------------------------------------------------------------------

def preflight_recommendation(state, decision_doc):
    kind = decision_doc.get("conclusion", {}).get("type")
    if kind not in DECISIVE_CONCLUSIONS:
        return
    pending = open_tasks(state, classes=("hard_gate",))
    if pending:
        raise ValueError(
            "recommendation blocked: open hard-gate research task(s) "
            + ", ".join(t["id"] for t in pending)
            + "; research them or return a conditional/defer conclusion")
    unresolved = [e["id"] for e in state["case"]["evidence"]
                  if e["state"] != "confirmed" and e["impact"] == "critical"
                  and e["kind"] in HARD_KINDS]
    if unresolved:
        raise ValueError("recommendation blocked: critical eligibility evidence is unresolved: "
                         + ", ".join(unresolved))


def store_decision(state, decision_doc):
    need(state["phase"] in {"research", "adjudicate", "decide"}, "decision is out of stage order")
    verification = verify_evidence(state)
    preflight_recommendation(state, decision_doc)
    computed = decision.validate(state["case"], decision_doc)
    state["decision"] = copy.deepcopy(decision_doc)
    state["decision_state"] = {
        "stored_at": now_iso(), "stale": False,
        "case_digest": digest(state["case"]), "decision_digest": digest(decision_doc),
        "validated": True,
    }
    state["phase"] = "decide"
    metric(state, "decisions")
    cov = coverage(state)
    trace(state, "decision_stored", conclusion=decision_doc["conclusion"]["type"],
          headline=decision_doc["headline"], coverage_gaps=len(cov["gaps"]),
          coverage_unconfirmed=len(cov["unconfirmed"]))
    if cov["gaps"]:
        trace(state, "coverage_gap", path=",".join(sorted({g["path"] for g in cov["gaps"]})),
              kinds=",".join(sorted({g["kind"] for g in cov["gaps"]})))
    for offer_id, row in computed["offers"].items():
        trace(state, "calculation", kind="budget", offer=offer_id,
              cash=row["cost"]["cash"], gate=row["cost"]["budget_gate"])
    for row in decision_doc["assessments"]:
        trace(state, "recommendation", offer=row["offer"], path=row["path"],
              stance=row["stance"], gate=row["gate"], score_state=row["score_state"])
    return {"verification": verification, "computed": computed, "coverage": cov}


def report(state, mode="quick"):
    need(state.get("decision"), "no validated decision is stored; run decide first")
    verify_evidence(state)
    if state["decision_state"].get("stale"):
        raise ValueError("decision is stale: evidence or gates changed after it was stored; rerun decide")
    current = digest(state["case"])
    if current != state["decision_state"].get("case_digest"):
        raise ValueError("decision is stale: the case changed after it was stored; rerun decide")
    text = decision.render(state["case"], state["decision"], mode)
    state["phase"] = "done"
    trace(state, "report_rendered", mode=mode)
    return text


def scenario(state, change, name):
    need(isinstance(name, str) and re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", name),
         "scenario name must be a lowercase identifier")
    need(name not in state["scenarios"], "scenario name already exists")
    verify_evidence(state)
    base_digest = digest(state["case"])
    result = decision.scenario(state["case"], change)
    need(digest(state["case"]) == base_digest, "counterfactual mutated the base case")
    computed = decision.analyze(result["input"])
    state["scenarios"][name] = {
        "created_at": now_iso(), "change": result["change"], "base_digest": base_digest,
        "stale": False, "stale_reason": None,
        "before_value": result["before"], "reuse_evidence_ids": result["reuse_evidence_ids"],
        "recheck_evidence_ids": result["recheck_evidence_ids"],
        "review_routes": result["review_routes"], "rerun": result["rerun"],
        "case": result["input"], "summary": {
            offer_id: {"cash": row["cost"]["cash"], "budget_gate": row["cost"]["budget_gate"],
                       "paths": {p: v["gate"] for p, v in row["paths"].items()}}
            for offer_id, row in computed["offers"].items()},
    }
    metric(state, "scenarios")
    trace(state, "scenario_created", scenario=name, change=result["change"],
          reuse=len(result["reuse_evidence_ids"]), recheck=len(result["recheck_evidence_ids"]))
    return state["scenarios"][name]


# ---------------------------------------------------------------------------
# Checkpoints, resume and privacy
# ---------------------------------------------------------------------------

def checkpoint(state):
    snap = {
        "at": now_iso(), "phase": state["phase"],
        "case_digest": digest(state["case"]),
        "open_tasks": [t["id"] for t in open_tasks(state)],
        "blocked_tasks": [t["id"] for t in blocked_tasks(state)],
        "confirmed_evidence_ids": [e["id"] for e in state["case"]["evidence"]
                                   if e["state"] == "confirmed"],
        "decision_present": state.get("decision") is not None,
    }
    state.setdefault("checkpoints", []).append(snap)
    metric(state, "checkpoints")
    trace(state, "checkpoint", phase=state["phase"], open_tasks=len(snap["open_tasks"]),
          case_digest=snap["case_digest"])
    return snap


TRANSIENT_BLOCK_REASONS = {"tool_error", "tool_blocked", "partial_result", "unopened_source"}


def checkpoint_drift(state):
    """Compare the newest checkpoint with the current state.

    A checkpoint is an audit marker, not a rollback snapshot. Drift is expected
    after further research; it matters when previously confirmed evidence is no
    longer confirmed or a task became blocked.
    """
    if not state.get("checkpoints"):
        return {"detected": False, "reason": "no checkpoint"}
    last = state["checkpoints"][-1]
    confirmed = {e["id"] for e in state["case"]["evidence"] if e["state"] == "confirmed"}
    before = set(last.get("confirmed_evidence_ids", []))
    open_now = {t["id"] for t in open_tasks(state)}
    drifted = bool(last.get("case_digest") and last["case_digest"] != digest(state["case"]))
    return {
        "detected": drifted or bool(before - confirmed) or bool(open_now - set(last.get("open_tasks", []))),
        "checkpoint_at": last["at"],
        "case_changed": drifted,
        "evidence_no_longer_confirmed": sorted(before - confirmed),
        "open_tasks_added": sorted(open_now - set(last.get("open_tasks", []))),
        "note": "Checkpoints are audit markers; resume always verifies the live state.",
    }


def _reopen_transient(state):
    reopened = []
    for task in state["research"]["tasks"]:
        if task["status"] == "blocked" and task.get("blocked_reason") in TRANSIENT_BLOCK_REASONS:
            task["status"] = "todo"
            task["attempts"] = 0
            task["last_error"] = None
            task["blocked_reason"] = None
            reopened.append(task["id"])
            trace(state, "research_task_reopened", task=task["id"], reason="transient_block")
    return reopened


def resume(state):
    need(state["schema"] == VERSION, "cannot resume an unknown state schema")
    enforce_retention(state)
    decision.case_model(state["case"])
    verify_evidence(state)
    drift = checkpoint_drift(state)
    reopened = _reopen_transient(state)
    plan_tasks(state)
    if state.get("decision"):
        digest_ok = state["decision_state"].get("case_digest") == digest(state["case"])
        try:
            decision.validate(state["case"], state["decision"])
            state["decision_state"]["stale"] = not digest_ok
            state["decision_state"]["stale_reason"] = None if digest_ok else "case changed after decision"
        except ValueError as exc:
            state["decision_state"]["stale"] = True
            state["decision_state"]["stale_reason"] = str(exc)[:300]
    pending = open_tasks(state)
    if pending:
        state["phase"] = "research"
    elif state["phase"] == "done" and state["decision_state"].get("stale"):
        state["phase"] = "adjudicate"
    metric(state, "resumes")
    trace(state, "resume", phase=state["phase"], open_tasks=len(pending),
          reopened=len(reopened), checkpoint_drift=drift["detected"])
    if pending or blocked_tasks(state):
        state["research"]["rounds"] = 0
    return {
        "phase": state["phase"],
        "checkpoint": state["checkpoints"][-1] if state.get("checkpoints") else None,
        "checkpoint_drift": drift,
        "reopened_tasks": reopened,
        "open_tasks": [t["id"] for t in pending],
        "blocked_tasks": [{t["id"]: t["verification_route"]} for t in blocked_tasks(state)],
        "decision_stale": state["decision_state"].get("stale"),
        "coverage": coverage(state),
        "next": [t["id"] for t in next_tasks(state)["tasks"]] if not stop_condition(state)["stop"] else [],
    }


def _purge_profiles(state, event):
    case = state["case"]
    had = bool(case.get("profile"))
    case["profile"] = {}
    for row in state.get("scenarios", {}).values():
        had = had or bool(row["case"].get("profile"))
        row["case"]["profile"] = {}
    state["privacy"]["purged_at"] = now_iso()
    if state.get("decision"):
        # Purging the profile is an explicit lifecycle action, not a research
        # change. Keep the already validated decision renderable while the
        # trace records that its intake input was removed.
        state["decision_state"]["case_digest"] = digest(state["case"])
    trace(state, event, scope="profile", had_profile=had)
    return had


def enforce_retention(state):
    """Make the retention date an actual deletion, not only advice."""
    meta = state["privacy"]
    if today() <= date.fromisoformat(meta["expires_at"]):
        return {"expired": False, "purged": False}
    if state["case"].get("profile") or any(
            row["case"].get("profile") for row in state.get("scenarios", {}).values()):
        _purge_profiles(state, "privacy_retention_expired")
        return {"expired": True, "purged": True}
    return {"expired": True, "purged": False}


def privacy(state, purge=False):
    meta = state["privacy"]
    retention = enforce_retention(state)
    expired = today() > date.fromisoformat(meta["expires_at"])
    if purge:
        _purge_profiles(state, "privacy_purge")
    return {
        "retention_days": meta["retention_days"], "created_at": meta["created_at"],
        "expires_at": meta["expires_at"], "expired": expired,
        "auto_purged_on_expiry": retention["purged"],
        "purged_at": meta.get("purged_at"),
        "stored_profile_fields": sorted(state["case"].get("profile", {}).keys()),
        "identifier_warnings": meta.get("identifier_warnings", []),
        "advice": ("Profile data has reached its retention date; it was purged automatically. "
                   "Evidence, trace and decision artefacts remain."
                   if expired else "Purge with --purge when the decision is complete."),
    }


def init_state(case, retention_days=DEFAULT_RETENTION_DAYS):
    decision.case_model(case)
    created = today()
    warnings = []
    for key in case.get("profile", {}):
        if IDENTIFIER_KEY.search(str(key)):
            warnings.append(key)
    state = {
        "schema": VERSION,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "phase": "intake",
        "case": copy.deepcopy(case),
        "research": {
            "tasks": [], "rounds": 0, "max_rounds": DEFAULT_MAX_ROUNDS,
            "supplements": 0, "max_supplements": DEFAULT_MAX_SUPPLEMENTS,
        },
        "evidence_meta": {},
        "verification": {},
        "decision": None,
        "decision_state": {"stale": False},
        "scenarios": {},
        "checkpoints": [],
        "privacy": {
            "retention_days": retention_days,
            "created_at": created.isoformat(),
            "expires_at": (created + timedelta(days=retention_days)).isoformat(),
            "identifier_warnings": warnings,
        },
        "metrics": {},
        "trace": [],
    }
    trace(state, "state_initialized", retention_days=retention_days,
          offers=len(case["offers"]), warnings=warnings)
    return state


def status(state):
    tasks = state["research"]["tasks"]
    condition = stop_condition(state)
    stored = state.get("decision_state", {})
    digest_mismatch = (state.get("decision") is not None
                       and stored.get("case_digest") != digest(state["case"]))
    return {
        "phase": state["phase"],
        "tasks": {
            "total": len(tasks),
            "todo": sum(t["status"] == "todo" for t in tasks),
            "in_progress": sum(t["status"] == "in_progress" for t in tasks),
            "done": sum(t["status"] == "done" for t in tasks),
            "blocked": sum(t["status"] == "blocked" for t in tasks),
            "hard_gate_open": len(open_tasks(state, ("hard_gate",))),
            "decisive_open": len(open_tasks(state, ("decisive",))),
            "optional_open": len(open_tasks(state, ("optional",))),
        },
        "research": {"rounds": state["research"]["rounds"],
                     "max_rounds": state["research"]["max_rounds"],
                     "supplements": state["research"]["supplements"],
                     "stop": condition},
        "coverage": coverage(state),
        "evidence": {
            "total": len(state["case"]["evidence"]),
            "confirmed": sum(e["state"] == "confirmed" for e in state["case"]["evidence"]),
            "unresolved": sum(e["state"] != "confirmed" for e in state["case"]["evidence"]),
            "contradictions": sum(1 for row in state.get("verification", {}).values()
                                  if "contradictory" in " ".join(row.get("defects", []))),
        },
        "decision": {
            "present": state.get("decision") is not None,
            "stale": bool(stored.get("stale") or digest_mismatch),
            "stale_reason": stored.get("stale_reason") or ("case changed after decision" if digest_mismatch else None),
            "conclusion": (state.get("decision") or {}).get("conclusion", {}).get("type"),
        },
        "scenarios": {name: {"stale": bool(row.get("stale")),
                             "base_digest": row.get("base_digest")}
                      for name, row in state.get("scenarios", {}).items()},
        "privacy": privacy(state),
        "metrics": state.get("metrics", {}),
        "last_checkpoint": (state.get("checkpoints") or [None])[-1],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _emit(value):
    if isinstance(value, str):
        sys.stdout.buffer.write((value + "\n").encode("utf-8"))
    else:
        print(json.dumps(value, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("case")
    init.add_argument("--state", required=True)
    init.add_argument("--retention-days", type=int, default=DEFAULT_RETENTION_DAYS)
    init.add_argument("--force", action="store_true")

    plan = sub.add_parser("plan")
    plan.add_argument("--state", required=True)

    nxt = sub.add_parser("next")
    nxt.add_argument("--state", required=True)
    nxt.add_argument("--limit", type=int, default=5)
    nxt.add_argument("--advance", action="store_true")

    record = sub.add_parser("record")
    record.add_argument("--state", required=True)
    record.add_argument("result")

    evidence = sub.add_parser("evidence")
    evidence.add_argument("--state", required=True)
    evidence.add_argument("--as-of")
    evidence.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS)

    decide = sub.add_parser("decide")
    decide.add_argument("--state", required=True)
    decide.add_argument("decision")

    report_cmd = sub.add_parser("report")
    report_cmd.add_argument("--state", required=True)
    report_cmd.add_argument("--mode", choices=("quick", "full"), default="quick")

    scenario_cmd = sub.add_parser("scenario")
    scenario_cmd.add_argument("--state", required=True)
    scenario_cmd.add_argument("change")
    scenario_cmd.add_argument("--name", required=True)

    checkpoint_cmd = sub.add_parser("checkpoint")
    checkpoint_cmd.add_argument("--state", required=True)

    resume_cmd = sub.add_parser("resume")
    resume_cmd.add_argument("--state", required=True)

    status_cmd = sub.add_parser("status")
    status_cmd.add_argument("--state", required=True)

    trace_cmd = sub.add_parser("trace")
    trace_cmd.add_argument("--state", required=True)
    trace_cmd.add_argument("--jsonl", action="store_true")

    privacy_cmd = sub.add_parser("privacy")
    privacy_cmd.add_argument("--state", required=True)
    privacy_cmd.add_argument("--purge", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "init":
            target = Path(args.state)
            need(not target.exists() or args.force, "state file exists; use --force to replace it")
            state = init_state(decision.load(args.case), args.retention_days)
            save_state(target, state)
            _emit({"state": str(target), "schema": VERSION, "phase": state["phase"],
                   "privacy": privacy(state), "status": status(state)})
            return 0

        state = load_state(args.state)
        if args.command == "plan":
            tasks = plan_tasks(state)
            out = {"tasks": tasks, "status": status(state)}
        elif args.command == "next":
            out = next_tasks(state, args.limit, args.advance)
        elif args.command == "record":
            out = record_result(state, decision.load(args.result))
        elif args.command == "evidence":
            out = verify_evidence(state, args.as_of, args.max_age_days)
        elif args.command == "decide":
            out = store_decision(state, decision.load(args.decision))
        elif args.command == "report":
            out = report(state, args.mode)
        elif args.command == "scenario":
            out = scenario(state, decision.load(args.change), args.name)
        elif args.command == "checkpoint":
            out = checkpoint(state)
        elif args.command == "resume":
            out = resume(state)
        elif args.command == "status":
            out = status(state)
        elif args.command == "trace":
            if args.jsonl:
                out = "\n".join(json.dumps(row, ensure_ascii=False) for row in state["trace"])
            else:
                out = {"events": state["trace"], "count": len(state["trace"]),
                       "summary": status(state)}
        else:
            out = privacy(state, args.purge)
        save_state(args.state, state)
        _emit(out)
        return 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, json.dumps({"error": str(exc), "state": "unchanged"},
                                  ensure_ascii=False) + "\n")


if __name__ == "__main__":
    sys.exit(main())

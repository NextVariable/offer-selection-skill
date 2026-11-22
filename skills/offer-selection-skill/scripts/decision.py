"""Local, network-free validation and arithmetic for Offer Decision v1."""

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


VERSION = "offer-decision/v1"
PATHS = {"private", "soe", "local", "phd"}
CHANGES = {
    "country": {"market", "work", "credential", "eligibility", "timing", "access"},
    "career": {"market", "eligibility", "access", "timing"},
    "ceiling": set(),
    "internships": set(),
    "phd_intent": {"research", "academic", "eligibility", "timing"},
    "prestige": set(),
    "risk_tolerance": set(),
}
IMPACTS = {"critical", "material", "minor"}
STATUS = {"pass", "fail", "unresolved"}
KINDS = {"programme", "cost", "academic", "market", "credential", "work",
         "eligibility", "timing", "access", "network", "research"}
AUTHORITY = {"government", "employer", "institution"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def obj(value):
    need(isinstance(value, dict), "expected a JSON object")
    return value


def seq(value):
    need(isinstance(value, list), "expected a JSON array")
    return value


def fields(value, required, optional=()):
    value = obj(value)
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    need(not missing and not extra, f"missing fields: {sorted(missing)}; unexpected: {sorted(extra)}")
    return value


def string(value):
    need(isinstance(value, str) and bool(value.strip()), "expected a non-empty string")
    return value


def identifier(value):
    need(re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", string(value)), f"invalid ID: {value}")
    return value


def integer(value, upper=None):
    need(type(value) is int and value >= 0 and (upper is None or value <= upper),
         f"invalid nonnegative integer: {value}")
    return value


def indexed(rows):
    index = {}
    for row in seq(rows):
        key = identifier(obj(row)["id"])
        need(key not in index, f"duplicate ID: {key}")
        index[key] = row
    return index


def texts(values):
    return [string(v) for v in seq(values)]


def day(value):
    value = string(value)
    result = date.fromisoformat(value)
    need(result.isoformat() == value, f"expected ISO date: {value}")
    return result


def bounds(value):
    low, high = seq(value)
    integer(low)
    if high is not None:
        integer(high)
        need(high >= low, "inverted money range")
    return low, high


def add(ranges):
    low, high = 0, 0
    for lo, hi in ranges:
        low += lo
        high = None if high is None or hi is None else high + hi
    return low, high


def _net(spend, funding):
    sl, sh = spend
    fl, fh = funding
    # A missing upper award amount cannot establish an infeasible best case.
    return (0 if fh is None else max(0, sl - fh),
            None if sh is None else max(0, sh - fl))


def against(amount, limit):
    if limit is None:
        return "unresolved"
    low, high = amount
    if low > limit:
        return "fail"
    if high is not None and high <= limit:
        return "pass"
    return "unresolved"


def rollup(states):
    return "fail" if "fail" in states else "unresolved" if "unresolved" in states else "pass"


def costs(offer, budget, shock=None):
    """Same-month receipts are available only when confirmed before payment."""
    gross = []
    awards = []
    opportunity = []
    seen = set()
    horizon = budget.get("horizon", "whole_offer")
    excluded = []
    for row in seq(offer["costs"]):
        fields(row, ("id", "kind", "amount", "month", "basis"), ("category", "evidence_ids", "stage"))
        key = identifier(row["id"])
        need(key not in seen, f"duplicate cost component {key}")
        seen.add(key)
        kind = row["kind"]
        need(kind in {"expense", "award", "opportunity"}, f"unknown cost kind: {kind}")
        string(row["basis"])
        month = row["month"]
        if month is not None:
            integer(month, 240)
        amount = bounds(row["amount"])
        stage = row.get("stage")
        need(stage is None or stage in {"masters", "doctoral"}, f"invalid cost stage: {key}")
        if horizon == "masters":
            need(stage is not None, f"master-stage budget needs an explicit stage: {key}")
            if stage == "doctoral":
                excluded.append(key)
                continue
        if shock and kind == "expense" and row.get("category") in shock["categories"]:
            rate = 100 + shock["percent"]
            # Round each edge outward in the input currency's minor units.
            amount = (amount[0] * rate // 100,
                      None if amount[1] is None else (amount[1] * rate + 99) // 100)
        if kind == "expense":
            gross.append((month, amount))
        elif kind == "award":
            awards.append((month, amount))
        else:
            opportunity.append(amount)
    net = _net(add(a for _, a in gross), add(a for _, a in awards))
    total_status = against(net, budget["ceiling"])
    milestones = []
    for node in budget.get("liquidity", []):
        m = node["month"]
        due = add((a if month is not None else (0, a[1]))
                  for month, a in gross if month is None or month <= m)
        receipt = add((a if month is not None else (0, a[1]))
                      for month, a in awards if month is None or month <= m)
        outflow = _net(due, receipt)
        cash = bounds(node["available"])
        status = against(outflow, cash[1])
        if status != "fail":
            status = against(outflow, cash[0]) if against(outflow, cash[0]) == "pass" else "unresolved"
        milestones.append({"month": m, "outflow": outflow, "available": cash, "status": status})
    gate = rollup([total_status, *(m["status"] for m in milestones)])
    if (not offer["cost_complete"] or not gross) and gate == "pass":
        gate = "unresolved"
    if gate == "fail" and not offer.get("offsets_complete", offer["cost_complete"]):
        gate = "unresolved"
    basis = "ledger"
    if (gate == "unresolved" and budget["ceiling"] is None and not milestones
            and shock is None and offer["id"] in budget.get("affordable_by_user", [])):
        gate, basis = "pass", "user_affordability_attestation"
    return {"cash": net, "opportunity_cost": add(opportunity),
            "economic_cost": add([net, add(opportunity)]), "ceiling_status": total_status,
            "target_status": against(net, budget.get("target")), "budget_gate": gate,
            "budget_horizon": horizon, "excluded_cost_ids": excluded,
            "affordability_basis": basis, "milestones": milestones,
            "cashflow_checked": bool(milestones)}


def inspect_source(source):
    fields(source, ("url", "authority", "scope", "accessed", "locator"), ("inspection",))
    if "inspection" not in source:
        return False
    review = fields(source["inspection"], ("access", "support"), ("observation",))
    need(review["access"] in {"opened", "blocked", "unopened"}, "invalid page access state")
    need(review["support"] in {"supported", "partial", "unsupported", "unreviewed"},
         "invalid claim support state")
    if review["support"] != "unreviewed":
        need(review["access"] == "opened", "only opened pages can support a claim")
        string(review.get("observation"))
    return review["access"] == "opened" and review["support"] == "supported"


def source_defects(entry, operative):
    period = entry.get("period")
    in_period = (isinstance(period, dict) and {"from", "through"} <= period.keys()
                 and day(period["from"]) <= operative <= day(period["through"]))
    sources = [s for s in entry.get("sources", [])
               if s["authority"] in AUTHORITY and s["scope"] == entry["scope"]]
    defects = [] if in_period else ["out-of-period or missing operative period"]
    if not sources:
        defects.append("no scoped authority")
    elif not any(inspect_source(s) for s in sources):
        defects.append("no opened scoped authority supporting the exact claim")
    return defects


def case_model(data):
    fields(data, ("schema", "as_of", "profile", "goal", "budget", "offers", "evidence"))
    need(data["schema"] == VERSION, "unknown schema version")
    when = day(data["as_of"])
    obj(data["profile"])
    goal = fields(data["goal"], ("paths", "country", "career", "phd_intent", "prestige", "risk_tolerance"))
    paths = texts(goal["paths"])
    need(paths and len(set(paths)) == len(paths) and set(paths) <= PATHS, "invalid active paths")
    for key in ("country", "career", "phd_intent", "prestige", "risk_tolerance"):
        string(goal[key])
    budget = fields(data["budget"], ("currency", "ceiling"),
                    ("target", "liquidity", "stress", "affordable_by_user", "horizon"))
    need(budget.get("horizon", "whole_offer") in {"whole_offer", "masters"}, "invalid budget horizon")
    need(re.fullmatch(r"[A-Z]{3}", string(budget["currency"])), "expected currency code")
    for name in ("ceiling", "target"):
        if budget.get(name) is not None:
            integer(budget[name])
    seen = set()
    for node in seq(budget.get("liquidity", [])):
        fields(node, ("month", "available"))
        month = integer(node["month"], 240)
        need(month not in seen, "duplicate cashflow month")
        seen.add(month)
        bounds(node["available"])
    if "stress" in budget:
        stress = fields(budget["stress"], ("percent", "categories"))
        integer(stress["percent"], 500)
        need(texts(stress["categories"]), "stress requires named categories")
    offers, evidence = indexed(data["offers"]), indexed(data["evidence"])
    need(offers, "at least one offer is required")
    attestations = texts(budget.get("affordable_by_user", []))
    need(len(set(attestations)) == len(attestations) and set(attestations) <= offers.keys(),
         "invalid user affordability attestations")
    for offer in offers.values():
        fields(offer, ("id", "title", "country", "operative_date", "cost_complete", "costs", "gates"),
               ("offsets_complete",))
        for key in ("title", "country"):
            string(offer[key])
        day(offer["operative_date"])
        need(type(offer["cost_complete"]) is bool, "cost_complete must be boolean")
        if "offsets_complete" in offer:
            need(type(offer["offsets_complete"]) is bool and
                 (not offer["cost_complete"] or offer["offsets_complete"]),
                 "a complete cost ledger requires bounded offsets")
        need(offer["costs"] or not offer["cost_complete"], "complete cost ledger cannot be empty")
        indexed(offer["gates"])
    for entry in evidence.values():
        fields(entry, ("id", "offer", "path", "kind", "scope", "state", "impact", "claim"),
               ("period", "sources", "effect", "operative_date"))
        need(entry["offer"] in offers and entry["path"] in {*PATHS, "*"}, "evidence scope mismatch")
        need(entry["kind"] in KINDS and entry["impact"] in IMPACTS, "invalid evidence kind or impact")
        need(entry["state"] in {"confirmed", "prior", "unresolved"}, "invalid evidence state")
        string(entry["scope"])
        string(entry["claim"])
        if "period" in entry:
            period = fields(entry["period"], ("from", "through"))
            need(day(period["from"]) <= day(period["through"]), "inverted evidence period")
        if "effect" in entry:
            texts(entry["effect"])
        sources = seq(entry.get("sources", []))
        for source in sources:
            inspect_source(source)
            url = urlsplit(string(source["url"]))
            need(url.scheme in {"http", "https"} and url.hostname and url.path.strip("/")
                 and not url.username and not url.password, "expected a source page URL")
            need(day(source["accessed"]) <= when, "source access date is in the future")
            string(source["scope"])
            string(source["locator"])
            need(source["authority"] in AUTHORITY | {"market", "alumni", "community"}, "invalid authority")
        if entry["state"] == "confirmed":
            operative = day(entry.get("operative_date", offers[entry["offer"]]["operative_date"]))
            defects = source_defects(entry, operative)
            need(not defects, f"unverified confirmation {entry['id']}: {', '.join(defects)}; run audit")
    return paths, offers, evidence


def analyze(data):
    paths, offers, evidence = case_model(data)
    budget = data["budget"]
    results = {}
    for oid, offer in offers.items():
        totals = costs(offer, budget)
        for component in offer["costs"]:
            for cid in texts(component.get("evidence_ids", [])):
                item = evidence.get(cid)
                need(item and item["offer"] == oid and item["kind"] == "cost" and item["path"] == "*",
                     f"out-of-scope cost evidence: {cid}")
                need(item["state"] == "confirmed" or component["amount"] == [0, None],
                     f"finite cost depends on unconfirmed evidence: {cid}; run audit")
        if "stress" in budget:
            totals["stress"] = costs(offer, budget, budget["stress"])
        gate_rows = indexed(offer["gates"])
        output = {}
        for row in gate_rows.values():
            fields(row, ("id", "path", "scope", "kind", "status", "evidence_ids"))
            need(row["path"] in {*paths, "*"} and row["kind"] in KINDS, "unknown gate path or kind")
            string(row["scope"])
            need(row["status"] in STATUS | {"not_applicable"}, "invalid gate status")
            if row["status"] == "not_applicable":
                need(not row["evidence_ids"] and row["path"] != "*",
                     "not_applicable is a path judgement without external proof")
            support = []
            for cite in texts(row["evidence_ids"]):
                item = evidence.get(cite)
                need(item and item["offer"] == oid and item["path"] in {row["path"], "*"}
                     and item["scope"] == row["scope"] and item["kind"] == row["kind"],
                     f"wrong evidence for gate {row['id']}: {cite}")
                support.append(item)
            if row["status"] in {"pass", "fail"}:
                need(any(s["state"] == "confirmed" for s in support)
                     and not any(s["state"] == "unresolved" and s["impact"] == "critical" for s in support),
                     f"decided gate lacks sufficient direct evidence: {row['id']}")
        for path in paths:
            relevant = [g for g in gate_rows.values() if g["path"] in {path, "*"}]
            # A missing path roster is unknown; an explicit inapplicability judgment
            # belongs to the model and does not count as an externally verified gate.
            path_roster = any(g["path"] == path for g in relevant)
            states = [totals["budget_gate"], *(r["status"] for r in relevant)]
            if not path_roster:
                states.append("unresolved")
            pending = [i["id"] for i in evidence.values()
                       if i["offer"] == oid and i["path"] in {path, "*"}
                       and i["state"] != "confirmed" and i["impact"] in {"critical", "material"}]
            score_state = ("nrsy" if rollup(states) == "unresolved" or
                           any(evidence[i]["impact"] == "critical" for i in pending)
                           else "provisional" if pending else "confirmed")
            output[path] = {"gate": rollup(states), "score_state": score_state,
                            "checks": {r["id"]: r["status"] for r in relevant},
                            "uncertain_evidence": pending}
        results[oid] = {"cost": totals, "paths": output}
    return {"schema": VERSION, "currency": budget["currency"], "offers": results}


def audit(data):
    """Return a conservative copy when admitted source declarations do not support claims."""
    revised = deepcopy(data)
    offers = indexed(revised["offers"])
    evidence = indexed(revised["evidence"])
    changes = []
    for item in evidence.values():
        if item["state"] != "confirmed":
            continue
        operative = day(item.get("operative_date", offers[item["offer"]]["operative_date"]))
        defects = source_defects(item, operative)
        if defects:
            item["state"] = "unresolved"
            changes.append({"claim": item["id"], "reasons": defects})
    for offer in offers.values():
        oid = offer["id"]
        for gate in offer["gates"]:
            support = [evidence[c] for c in gate["evidence_ids"]]
            if gate["status"] in {"pass", "fail"} and (
                    not any(e["state"] == "confirmed" for e in support)
                    or any(e["state"] == "unresolved" and e["impact"] == "critical" for e in support)):
                gate["status"] = "unresolved"
                changes.append({"offer": oid, "gate": gate["id"], "reasons": ["support unresolved"]})
        for cost in offer["costs"]:
            if cost["amount"] != [0, None] and any(
                    evidence[c]["state"] != "confirmed" for c in cost.get("evidence_ids", [])):
                cost["amount"] = [0, None]
                if revised["budget"].get("horizon") != "masters" or cost.get("stage") != "doctoral":
                    offer["cost_complete"] = False
                    if cost["kind"] == "award":
                        offer["offsets_complete"] = False
                changes.append({"offer": oid, "cost": cost["id"], "reasons": ["support unresolved"]})
    analyze(revised)
    return {"input": revised, "changes": changes}


def research(data):
    _, offers, evidence = case_model(data)
    tasks = []
    for oid, offer in offers.items():
        def task(priority, path, kind, focus, key):
            tasks.append({"priority": priority, "offer_id": oid, "offer": offer["title"],
                          "country": offer["country"], "path": path, "topic": kind,
                          "scope": focus, "operative_date": offer["operative_date"], "key": key})
        if not offer["cost_complete"]:
            task(0, "*", "cost", "official tuition, mandatory costs and applicable dates", "cost")
        if not any(row["offer"] == oid and row["kind"] == "programme" for row in evidence.values()):
            task(1, "*", "programme", "official programme delivery, duration and course structure", "programme")
        for row in offer["gates"]:
            if row["status"] == "unresolved":
                task(0, row["path"], row["kind"], row["scope"], row["id"])
        for row in evidence.values():
            if row["offer"] == oid and row["state"] != "confirmed" and row["impact"] != "minor":
                task(0 if row["impact"] == "critical" else 1, row["path"], row["kind"],
                     row["scope"], row["id"])
    dedup = {}
    for task in sorted(tasks, key=lambda v: (v["priority"], v["offer_id"], v["key"])):
        key = tuple(task[k] for k in ("offer_id", "path", "topic", "scope"))
        dedup.setdefault(key, task)
    return {"schema": VERSION, "tasks": list(dedup.values())}


def validate(data, decision):
    computed = analyze(data)
    fields(decision, ("schema", "conclusion", "headline", "reasons", "risks", "reversal", "assessments"))
    need(decision["schema"] == VERSION, "unknown decision schema")
    for field in ("headline", "reversal"):
        string(decision[field])
    need(texts(decision["reasons"]), "provide decisive reasons")
    texts(decision["risks"])
    evidence = indexed(data["evidence"])
    seen = {}
    for row in seq(decision["assessments"]):
        fields(row, ("offer", "path", "gate", "score_state", "stance", "value",
                     "competitiveness", "evidence_ids"), ("score",))
        oid, path = row["offer"], row["path"]
        key = oid, path
        need(oid in computed["offers"] and path in computed["offers"][oid]["paths"]
             and key not in seen, "unknown or duplicate assessment")
        result = computed["offers"][oid]["paths"][path]
        need(row["gate"] == result["gate"], f"gate disagrees: {key}")
        state = row["score_state"]
        precision = {"nrsy": 0, "provisional": 1, "confirmed": 2}
        need(state in precision and precision[state] <= precision[result["score_state"]],
             f"score state too certain: {key}")
        out = row["stance"]
        need(out in {"recommend", "conditional", "defer", "reject", "viable"}, "invalid stance")
        if result["gate"] == "fail":
            need(out == "reject", f"failed gate cannot support acceptance: {key}")
        if state == "nrsy" or result["gate"] == "unresolved":
            need(out in {"conditional", "defer", "reject"}, f"decisive uncertainty: {key}")
        ids = texts(row["evidence_ids"])
        for cid in ids:
            item = evidence.get(cid)
            need(item and item["offer"] == oid and item["path"] in {path, "*"},
                 f"out-of-scope decision claim: {cid}")
        if out == "recommend":
            need(any(evidence[c]["state"] == "confirmed" and
                     evidence[c]["kind"] not in {"eligibility", "credential", "work", "timing"} for c in ids),
                 f"recommendation lacks a confirmed basis beyond eligibility: {key}")
        if "score" in row:
            need(state == "confirmed", "only confirmed score state permits integers")
            score = integer(row["score"], 100)
            need(out not in {"conditional", "defer"} and (out != "reject" or score < 60)
                 and (out != "recommend" or score >= 80), "score conflicts with stance")
        string(row["value"])
        string(row["competitiveness"])
        seen[key] = out
    need(len(seen) == len(computed["offers"]) * len(data["goal"]["paths"]), "incomplete assessment matrix")
    if any(p["gate"] != "pass" or p["uncertain_evidence"]
           for offer in computed["offers"].values() for p in offer["paths"].values()):
        need(decision["risks"], "material gates or uncertainties need a risk explanation")
    conclusion = fields(decision["conclusion"], ("type", "choices"), ("parity_basis",))
    kind = conclusion["type"]
    need(kind in {"recommend", "conditional", "parity_with_choice", "equivalent", "none", "defer"},
         "unknown conclusion type")
    choices = set()
    for target in seq(conclusion["choices"]):
        fields(target, ("offer", "path"))
        key = target["offer"], target["path"]
        need(key in seen and key not in choices and seen[key] != "reject", "invalid choice")
        choices.add(key)
    if kind in {"recommend", "parity_with_choice"}:
        need(len(choices) == 1 and all(seen[c] == "recommend" for c in choices),
             "definitive choice requires a supported path")
    elif kind == "conditional":
        need(choices and all(seen[c] != "defer" for c in choices), "conditional choice needs viable branches")
    else:
        need(not choices, "this conclusion cannot select offers")
    if kind in {"equivalent", "parity_with_choice"}:
        need(len(computed["offers"]) > 1 and string(conclusion.get("parity_basis")),
             "parity requires an affirmative explanation")
        need(all(x in {"recommend", "viable"} for x in seen.values())
             and all(p["score_state"] == "confirmed" for o in computed["offers"].values()
                     for p in o["paths"].values()), "comparison contains unresolved/rejected paths")
    if kind == "none":
        need(all(x == "reject" for x in seen.values()), "none requires every path rejected")
    if kind == "defer":
        need(any(x == "defer" for x in seen.values()), "defer requires a deferred assessment")
    return computed


def scenario(base, change):
    case_model(base)
    fields(change, ("field", "value"))
    field, value = change["field"], change["value"]
    need(field in CHANGES, "unsupported scenario variable")
    target = {"ceiling": "budget", "internships": "profile"}.get(field, "goal")
    if field == "ceiling":
        if value is not None:
            integer(value)
    elif field == "internships":
        texts(value)
    else:
        string(value)
    need(base[target].get(field) != value, "scenario must actually change one field")
    revised = deepcopy(base)
    revised[target][field] = deepcopy(value)
    stale = {e["id"] for e in revised["evidence"] if e["kind"] in CHANGES[field]}
    if field in {"career", "country", "phd_intent"}:
        # Scope may vary with the goal. Conservatively reopen affected hard gates.
        reopened = []
        for offer in revised["offers"]:
            gates = []
            for g in offer["gates"]:
                if g["kind"] in CHANGES[field] or stale.intersection(g["evidence_ids"]):
                    gates.append({**g, "status": "unresolved", "evidence_ids": []})
                else:
                    gates.append(g)
            reopened.append({**offer, "gates": gates})
        revised["offers"] = reopened
    revised["evidence"] = [e for e in revised["evidence"] if e["id"] not in stale]
    return {"hypothetical": True, "change": deepcopy(change), "before": deepcopy(base[target].get(field)),
            "reuse_evidence_ids": sorted(e["id"] for e in revised["evidence"]),
            "recheck_evidence_ids": sorted(stale), "review_routes": field in {"country", "career", "phd_intent"},
            "rerun": ["budget", "gates", "competitiveness", "value", "recommendation"] if field == "ceiling"
            else ["gates", "graduation_profile", "competitiveness", "value", "recommendation"],
            "input": revised}


STATUS_ZH = {"pass": "通过", "fail": "不通过", "unresolved": "待定"}
IMPACT_ZH = {"critical": "关键", "material": "重要", "minor": "次要"}
IMPACT_ORDER = {"critical": 0, "material": 1, "minor": 2}


def money_range(value):
    low, high = value
    return f"{low:,} 起（上界未定）" if high is None else f"{low:,}–{high:,}"


def applicable_label(item):
    period = item.get("period")
    if period:
        return f"适用 {period['from']} 至 {period['through']}"
    if item.get("operative_date"):
        return f"适用日期 {item['operative_date']}"
    accessed = sorted({s["accessed"] for s in item.get("sources", []) if s.get("accessed")})
    return f"核验日期 {accessed[0]}" if accessed else "适用期未标注"


def budget_section(data, computed, decision, known):
    budget = data["budget"]
    masters = budget.get("horizon") == "masters"
    terms = ["口径：" + ("仅硕士阶段" if masters else "全项目"),
             f"{budget['currency']} 最小货币单位"]
    if budget.get("ceiling") is not None:
        terms.append(f"上限 {budget['ceiling']:,}")
    if budget.get("target") is not None:
        terms.append(f"目标 {budget['target']:,}")
    if budget.get("ceiling") is None and budget.get("target") is None:
        terms.append("未提供金额上限或目标")
    lines = ["", "### 费用与预算", "", "- " + "；".join(terms)]
    cited = {}
    for row in decision["assessments"]:
        cited.setdefault(row["offer"], [])
        for cid in row["evidence_ids"]:
            if cid not in cited[row["offer"]]:
                cited[row["offer"]].append(cid)
    for offer in data["offers"]:
        cost = computed["offers"][offer["id"]]["cost"]
        low, high = cost["cash"]
        selected = [c for c in offer["costs"] if c["id"] not in cost["excluded_cost_ids"]]
        has_expenses = any(c["kind"] == "expense" for c in selected)
        complete = offer["cost_complete"] and has_expenses
        if complete:
            bits = [f"净现金 {money_range(cost['cash'])}"]
        elif has_expenses:
            bits = [f"已列项目净现金小计 {money_range(cost['cash'])}（全期费用尚未核齐）"]
        else:
            bits = ["现金支出尚未量化"]
        if budget.get("ceiling") is not None:
            ceiling = budget["ceiling"]
            if complete:
                bits.append(f"上限{STATUS_ZH[cost['ceiling_status']]}")
            if not complete:
                if low > ceiling and cost["budget_gate"] == "fail":
                    bits.append(f"已列项目至少超出上限 {low - ceiling:,}")
                else:
                    bits.append("费用未核齐，无法确认上限余量")
            elif high is None and low <= ceiling:
                bits.append("上界未定，无法确认余量")
            elif low > ceiling:
                bits.append(f"超出至少 {low - ceiling:,}")
            elif high <= ceiling:
                bits.append(f"余量 {ceiling - high:,}–{ceiling - low:,}")
            else:
                bits.append("区间跨越上限")
        if budget.get("target") is not None and complete:
            bits.append(f"目标{STATUS_ZH[cost['target_status']]}")
        bits.append(f"预算闸门{STATUS_ZH[cost['budget_gate']]}")
        if cost["affordability_basis"] == "user_affordability_attestation":
            bits.append("依据用户确认可负担")
        if cost["excluded_cost_ids"]:
            bits.append("不计入 " + "、".join(cost["excluded_cost_ids"]))
        missing = [c["id"] for c in selected if c["amount"][1] is None]
        if missing:
            bits.append("未量化 " + "、".join(missing))
        if not cost["cashflow_checked"]:
            bits.append("付款节点未核对")
        lines.append(f"- {offer['title']}：" + "；".join(bits))
        # Per-row ledger from the same verified decision input. This is rendered
        # for every cost row, quantified or not, so a Quick report never depends
        # on the Agent re-typing amounts by hand.
        for component in offer["costs"]:
            row_low, row_high = component["amount"]
            if row_high is None:
                amount = ("未量化（上界未定）" if row_low == 0
                          else f"未量化（下界 {row_low:,}，上界未定）")
            elif row_low == row_high:
                amount = f"{row_low:,}"
            else:
                amount = f"{row_low:,}–{row_high:,}"
            stage = f"，{component['stage']}" if component.get("stage") else ""
            excluded = "；本预算口径排除" if component["id"] in cost["excluded_cost_ids"] else ""
            lines.append(f"  - {component['id']}（{component['kind']}{stage}）："
                         f"{amount}；{component['basis']}{excluded}")
        # Confirmed cost evidence already carried by the input: show the claim,
        # its applicable period and the opened scoped source. Unconfirmed rows
        # stay in the 待核实 section instead of being presented as costs.
        ids = [cid for component in offer["costs"] for cid in component.get("evidence_ids", [])]
        ids += cited.get(offer["id"], [])
        for cid in dict.fromkeys(ids):
            item = known.get(cid)
            if not item or item["kind"] != "cost" or item["offer"] != offer["id"] \
                    or item["state"] != "confirmed":
                continue
            sources = [src for src in item.get("sources", [])
                       if src["authority"] in AUTHORITY and src["scope"] == item["scope"]
                       and inspect_source(src)]
            if not sources:
                continue
            lines.append(f"  - 依据（{cid}）：{item['claim']}（{applicable_label(item)}）")
            for src in sources:
                lines.append(f"    - {src['authority']} · {src['locator']} · <{src['url']}>")
    return lines


def gap_section(data, decision, computed, known):
    labels = {o["id"]: o["title"] for o in data["offers"]}
    gaps, seen = [], set()
    for row in decision["assessments"]:
        path = computed["offers"][row["offer"]]["paths"][row["path"]]
        for cid in dict.fromkeys(row["evidence_ids"] + path["uncertain_evidence"]):
            if cid in seen:
                continue
            item = known[cid]
            verified = item["state"] == "confirmed" and any(
                src["authority"] in AUTHORITY and src["scope"] == item["scope"]
                and inspect_source(src) for src in item.get("sources", []))
            if verified:
                continue
            seen.add(cid)
            state = "未确认" if item["state"] != "confirmed" else "来源未通过支持性核验"
            gaps.append((IMPACT_ORDER[item["impact"]],
                         f"- {labels[row['offer']]} / {row['path']}：{item['claim']}"
                         f"（{item['scope']}；{state}；影响{IMPACT_ZH[item['impact']]}）"))
    if not gaps:
        return []
    return ["", "### 待核实", "", *(text for _, text in sorted(gaps))]


def render(data, decision, mode):
    computed = validate(data, decision)
    lines = [decision["headline"], "", f"结论类型：`{decision['conclusion']['type']}`"]
    if decision["conclusion"]["choices"]:
        labels = {o["id"]: o["title"] for o in data["offers"]}
        lines += ["", "选择：" + "、".join(
            f"{labels[c['offer']]} / {c['path']}" for c in decision["conclusion"]["choices"])]
    if decision["conclusion"].get("parity_basis"):
        lines += ["", "结果接近的依据：" + decision["conclusion"]["parity_basis"]]
    for title, items in (("主要依据", decision["reasons"]), ("关键风险", decision["risks"]),
                         ("翻转条件", [decision["reversal"]])):
        lines.extend(["", f"### {title}", "", *(f"- {item}" for item in items)])
    known = indexed(data["evidence"])
    metadata = indexed(data["offers"])
    labels = {oid: o["title"] for oid, o in metadata.items()}
    constrained = [r for r in decision["assessments"]
                   if r["gate"] != "pass" or r["score_state"] != "confirmed"]
    if constrained:
        lines.extend(["", "### 关键状态", "", *(
            f"- {labels[r['offer']]} / {r['path']}：{r['gate']} · {r['score_state']}"
            for r in constrained)])
    lines.extend(budget_section(data, computed, decision, known))
    lines.extend(gap_section(data, decision, computed, known))
    cited = dict.fromkeys(i for r in decision["assessments"] for i in r["evidence_ids"])
    sources = {}
    for cid in cited:
        item = known[cid]
        if item["state"] == "confirmed":
            for src in item.get("sources", []):
                if src["authority"] in AUTHORITY and src["scope"] == item["scope"] and inspect_source(src):
                    sources.setdefault(src["url"], src["locator"])
    if sources:
        lines.extend(["", "### 已核验来源", "", *(f"- {loc} · <{url}>" for url, loc in sources.items())])
    if mode == "full":
        for row in decision["assessments"]:
            offer = computed["offers"][row["offer"]]
            lines += ["", f"### {labels[row['offer']]} / {row['path']}", "",
                      f"- 门槛：{row['gate']}，评分状态：{row['score_state']}，建议：{row['stance']}",
                      f"- 竞争力：{row['competitiveness']}", f"- 个人增量：{row['value']}",
                      f"- 费用与检查（{computed['currency']} 最小货币单位）："
                      + json.dumps(offer["cost"], ensure_ascii=False),
                      "- 路径门槛：" + json.dumps(offer["paths"][row["path"]]["checks"], ensure_ascii=False)]
            if "score" in row:
                lines.append(f"- 分数：{row['score']}")
            for cid in dict.fromkeys(row["evidence_ids"] + offer["paths"][row["path"]]["uncertain_evidence"]):
                item = known[cid]
                operative = item.get("operative_date", metadata[row["offer"]]["operative_date"])
                period = item.get("period")
                coverage = f"（覆盖 {period['from']} 至 {period['through']}）" if period else ""
                lines.append(f"- {item['state']} · {item['claim']} · 适用日期 {operative}{coverage}")
                for src in item.get("sources", []):
                    review = src.get("inspection", {"access": "unopened", "support": "unreviewed"})
                    observation = review.get("observation", "未记录原文观察")
                    lines.append(f"  - {src['authority']} · {review['access']}/{review['support']} · "
                                 f"{src['locator']} · {observation} · <{src['url']}>")
    return "\n".join(lines)


def load(path):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            need(key not in value, f"duplicate JSON key: {key}")
            value[key] = item
        return value

    def bad_constant(value):
        raise ValueError(f"non-JSON number: {value}")

    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=bad_constant)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "audit", "check", "verify", "scenario", "compare", "report"):
        item = sub.add_parser(command)
        item.add_argument("input")
        if command in {"verify", "report"}:
            item.add_argument("decision")
        if command in {"scenario", "compare"}:
            item.add_argument("change")
        if command == "compare":
            item.add_argument("before")
            item.add_argument("after")
            item.add_argument("--why", required=True)
            item.add_argument("--reassessed")
        if command == "report":
            item.add_argument("--mode", choices=("quick", "full"), default="quick")
    args = parser.parse_args()
    try:
        data = load(args.input)
        if args.command == "plan":
            out = research(data)
        elif args.command == "audit":
            out = audit(data)
        elif args.command == "check":
            out = analyze(data)
        elif args.command == "verify":
            out = validate(data, load(args.decision))
        elif args.command == "report":
            out = render(data, load(args.decision), args.mode)
        else:
            change = scenario(data, load(args.change))
            out = change
            if args.command == "compare":
                before, after = load(args.before), load(args.after)
                validate(data, before)
                revised = change["input"]
                if args.reassessed:
                    supplied = load(args.reassessed)
                    case_model(supplied)
                    # Only new scoped evidence, path routing and gate checks may
                    # differ from the single-variable counterfactual.
                    for root in ("schema", "as_of", "budget", "profile"):
                        need(supplied[root] == revised[root], f"scenario changed unrelated {root}")
                    if change["review_routes"]:
                        need({k: v for k, v in supplied["goal"].items() if k != "paths"}
                             == {k: v for k, v in revised["goal"].items() if k != "paths"},
                             "scenario changed unrelated goal fields")
                    else:
                        need(supplied["goal"] == revised["goal"], "scenario changed unrelated goal")
                    fixed = lambda inp: [{k: v for k, v in o.items() if k != "gates"} for o in inp["offers"]]
                    need(fixed(supplied) == fixed(revised), "scenario changed offer or cost facts")
                    if not change["review_routes"]:
                        need(supplied == revised, "this scenario has no scope to reassess")
                    actual = indexed(supplied["evidence"])
                    need(all(actual.get(e["id"]) == e for e in revised["evidence"]),
                         "scenario modified reusable evidence")
                    revised = supplied
                validate(revised, after)
                out = {"hypothetical": True, "change": change["change"],
                       "before_value": change["before"], "before": before["conclusion"],
                       "after": after["conclusion"], "before_summary": before["headline"],
                       "after_summary": after["headline"], "why": string(args.why),
                       "reversal": after["reversal"]}
        # ASCII JSON is portable even when a Windows terminal uses a legacy encoding.
        if isinstance(out, str):
            sys.stdout.buffer.write((out + "\n").encode("utf-8"))
        else:
            print(json.dumps(out, indent=2))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, f"invalid decision input: {exc}\n")


if __name__ == "__main__":
    main()

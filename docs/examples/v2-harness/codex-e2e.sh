#!/usr/bin/env bash
# End-to-end acceptance driver for the v2 decision harness.
#
# It exercises the real CLI against the frozen real-source case in this
# directory: plan -> record -> coverage -> decide -> report -> checkpoint /
# resume -> counterfactual -> trace. Every harness call is written to a local
# log so a reviewer can confirm harness.py actually ran instead of a simulated
# transcript.
#
# Usage: bash docs/examples/v2-harness/codex-e2e.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
HARNESS="$ROOT/skills/offer-selection-skill/scripts/harness.py"
EX="$ROOT/docs/examples/v2-harness"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

STATE="$WORK/state.json"
CALLS="$WORK/harness-calls.log"
: > "$CALLS"

pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

run() {
  printf '+ python3 %s %s\n' "$HARNESS" "$*" >> "$CALLS"
  python3 "$HARNESS" "$@"
}

python3 - "$EX/case.json" <<'PY'
import json, sys
case = json.load(open(sys.argv[1], encoding="utf-8"))
assert case["schema"] == "offer-decision/v1"
assert case["goal"]["paths"] == ["private"]
PY
pass "0. fixture case is valid and uses the private path"

# 1. Create the research plan.
run init "$EX/case.json" --state "$STATE" > "$WORK/init.json"
run plan --state "$STATE" > "$WORK/plan.json"
python3 - "$WORK/plan.json" <<'PY'
import json, sys
plan = json.load(open(sys.argv[1], encoding="utf-8"))
tasks = plan["tasks"]
kinds = {t["kind"] for t in tasks}
assert "eligibility" in kinds, kinds
assert any(t["class"] == "hard_gate" for t in tasks), "no hard-gate task planned"
PY
pass "1. research plan created with hard-gate eligibility tasks"

# 2. Record the two real, opened official sources.
python3 - "$WORK/plan.json" "$EX/gate-warwick.json" warwick "$WORK/gate-w.json" <<'PY'
import json, sys
plan = json.load(open(sys.argv[1], encoding="utf-8"))
task = next(t for t in plan["tasks"] if t["kind"] == "eligibility" and t["offer_id"] == sys.argv[3])
row = json.load(open(sys.argv[2], encoding="utf-8"))
row["task_id"] = task["id"]
json.dump(row, open(sys.argv[4], "w", encoding="utf-8"), ensure_ascii=False)
PY
python3 - "$WORK/plan.json" "$EX/gate-glasgow.json" glasgow "$WORK/gate-g.json" <<'PY'
import json, sys
plan = json.load(open(sys.argv[1], encoding="utf-8"))
task = next(t for t in plan["tasks"] if t["kind"] == "eligibility" and t["offer_id"] == sys.argv[3])
row = json.load(open(sys.argv[2], encoding="utf-8"))
row["task_id"] = task["id"]
json.dump(row, open(sys.argv[4], "w", encoding="utf-8"), ensure_ascii=False)
PY
run record --state "$STATE" "$WORK/gate-w.json" > "$WORK/rec-w.json"
run record --state "$STATE" "$WORK/gate-g.json" > "$WORK/rec-g.json"
python3 - "$WORK/rec-w.json" "$WORK/rec-g.json" <<'PY'
import json, sys
for path in sys.argv[1:]:
    out = json.load(open(path, encoding="utf-8"))
    assert out["added"] or out["reused"], out
    assert out["gates"], out
PY
pass "2. real official source checks recorded and both gates decided"

# 3. Check the required research coverage contract.
run coverage --state "$STATE" > "$WORK/coverage.json"
python3 - "$WORK/coverage.json" <<'PY'
import json, sys
cov = json.load(open(sys.argv[1], encoding="utf-8"))
row = cov["paths"]["private"]
assert row["classes"]["eligibility"] == "hard", row
assert "eligibility" in row["confirmed"], row
assert not cov["hard_gaps"], cov["hard_gaps"]
assert "note" in cov
PY
pass "3. required coverage checked; private hard slot confirmed, decisive gaps reported"

# 4. Store the validated decision.
run decide --state "$STATE" "$EX/decision.json" > "$WORK/decide.json"
python3 - "$WORK/decide.json" <<'PY'
import json, sys
out = json.load(open(sys.argv[1], encoding="utf-8"))
assert out["computed"]["offers"], out
assert out["coverage"]["paths"]["private"]
PY
pass "4. validated decision stored"

# 5. Render Quick and Full from the same decision.
run report --state "$STATE" --mode quick > "$WORK/quick.txt"
run report --state "$STATE" --mode full > "$WORK/full.txt"
python3 - "$WORK/quick.txt" "$WORK/full.txt" <<'PY'
import sys
quick = open(sys.argv[1], encoding="utf-8").read()
full = open(sys.argv[2], encoding="utf-8").read()
assert quick.strip(), "empty quick report"
assert full.startswith(quick), "full report must extend the quick report"
assert "费用与预算" in quick, quick[:200]
PY
pass "5. Quick and Full reports rendered from one validated decision"

# 6. Checkpoint and resume.
run checkpoint --state "$STATE" > "$WORK/checkpoint.json"
run resume --state "$STATE" > "$WORK/resume.json"
python3 - "$WORK/resume.json" <<'PY'
import json, sys
out = json.load(open(sys.argv[1], encoding="utf-8"))
assert out["checkpoint"] is not None
assert "checkpoint_drift" in out and "coverage" in out
assert out["decision_stale"] is False
PY
pass "6. checkpoint stored and resume re-verified without a stale decision"

# 7. Budget counterfactual against the same base case.
run scenario --state "$STATE" "$EX/change.json" --name ceiling_53000 > "$WORK/scenario.json"
python3 - "$WORK/scenario.json" <<'PY'
import json, sys
row = json.load(open(sys.argv[1], encoding="utf-8"))
assert set(row["summary"]) == {"warwick", "glasgow"}, row["summary"]
assert row["summary"]["warwick"]["budget_gate"] == "fail"
assert row["summary"]["glasgow"]["budget_gate"] == "pass"
assert row["base_digest"]
PY
pass "7. budget counterfactual isolated from the base case"

# 8. Prove the trace came from harness.py itself.
run trace --state "$STATE" --jsonl > "$WORK/trace.jsonl"
python3 - "$WORK/trace.jsonl" <<'PY'
import json, sys
rows = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8") if line.strip()]
assert rows, "empty trace"
assert all(row.get("source") == "harness.py" for row in rows), "trace row without harness.py source"
events = {row["event"] for row in rows}
required = {"state_initialized", "plan_created", "research_task_finished",
            "decision_stored", "report_rendered", "checkpoint", "resume",
            "scenario_created"}
missing = required - events
assert not missing, missing
PY
grep -c 'harness.py' "$CALLS" > /dev/null
pass "8. trace rows carry source=harness.py and every command is logged"

printf '\nE2E PASS: %s harness.py invocations, trace events verified\n' \
  "$(wc -l < "$CALLS" | tr -d ' ')"

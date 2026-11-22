# Codex CLI native acceptance input

Use this prompt verbatim in a Codex CLI session rooted at the repository. The
goal is a real native run, not a simulation inside another IDE. Do not claim
PASS from a replayed transcript; the commands below must execute and the trace
must carry `source: harness.py`.

```text
You are accepting the v2 offer-selection harness in this repository. Work from
the repository root and use the real CLI, not a reimplementation. Stop and
report BLOCKED if a command fails; never fabricate a passing transcript.

Fixture: docs/examples/v2-harness/case.json (two UK marketing offers, private
path). Real source results: docs/examples/v2-harness/gate-warwick.json and
gate-glasgow.json. Decision: docs/examples/v2-harness/decision.json. Budget
change: docs/examples/v2-harness/change.json.

Run the following sequence and keep the state file in a temporary directory:

1. Create the research plan:
   python3 skills/offer-selection-skill/scripts/harness.py init docs/examples/v2-harness/case.json --state "$TMP/state.json"
   python3 skills/offer-selection-skill/scripts/harness.py plan --state "$TMP/state.json"
   Confirm the plan contains eligibility tasks whose class is hard_gate.

2. Record the two real official-source checks. Copy each gate JSON, replace its
   task_id with the matching eligibility task id from the plan, then:
   python3 skills/offer-selection-skill/scripts/harness.py record --state "$TMP/state.json" <gate.json>
   Confirm both results added evidence and decided their gates.

3. Check the required research coverage:
   python3 skills/offer-selection-skill/scripts/harness.py coverage --state "$TMP/state.json"
   Confirm private/eligibility is confirmed, hard_gaps is empty, and decisive
   gaps are reported without blocking.

4. Store the validated decision:
   python3 skills/offer-selection-skill/scripts/harness.py decide --state "$TMP/state.json" docs/examples/v2-harness/decision.json

5. Generate both report modes:
   python3 skills/offer-selection-skill/scripts/harness.py report --state "$TMP/state.json" --mode quick
   python3 skills/offer-selection-skill/scripts/harness.py report --state "$TMP/state.json" --mode full
   Confirm Full extends Quick.

6. Checkpoint and resume:
   python3 skills/offer-selection-skill/scripts/harness.py checkpoint --state "$TMP/state.json"
   python3 skills/offer-selection-skill/scripts/harness.py resume --state "$TMP/state.json"
   Confirm the decision is not stale and the checkpoint drift report is present.

7. Run the budget counterfactual:
   python3 skills/offer-selection-skill/scripts/harness.py scenario --state "$TMP/state.json" docs/examples/v2-harness/change.json --name ceiling_53000
   Confirm Warwick fails the GBP 53,000 ceiling and Glasgow passes, and that
   the base case is unchanged.

8. Verify the trace proves harness.py actually ran:
   python3 skills/offer-selection-skill/scripts/harness.py trace --state "$TMP/state.json" --jsonl
   Every trace row must carry "source": "harness.py", and the events must
   include state_initialized, plan_created, research_task_finished,
   decision_stored, report_rendered, checkpoint, resume and scenario_created.

Report PASS/FAIL/BLOCKED for each numbered step and include the final Head SHA
you tested. Do not merge main and do not publish a stable release.
```

The same sequence is executable without an LLM:

```bash
bash docs/examples/v2-harness/codex-e2e.sh
```

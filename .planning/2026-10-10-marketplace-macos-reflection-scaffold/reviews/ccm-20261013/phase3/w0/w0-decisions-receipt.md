# w0-decisions receipt (complete)

Branch `claude/w0-decisions-ledger`, final SHA `f9c8848` (impl `7649ca7`). Tip `c21941f` merged: "Already up to date", rc 0 (ran from a scratchpad script).
Changed: `dev/plan_decide.py` (102 lines), `dev/test_plan_decide.py`, `P/decisions.jsonl`, `P/retros/w0-decisions.md`.
Gate rcs (merged bytes): unittest 0 (4 tests), tasks validate 0, check 0, acceptance-baseline 0, test:hooks 0, hk validate 0, diff --check 0, retro:gate 0.
Red→green: T-E5 idempotent (ModuleNotFoundError→OK); operation→receipt (rc 1≠0→OK); approved-only (`decision` rc 1→OK); refusals green on first run, bites under mutation (usage exits 2→FAIL).
Seed ids: DL-1 #91 relabel, DL-2 draft PR, DL-3 T4 Phase C, DL-4 /to-tickets (all pending operations); DL-5..DL-50 = D1–D46. `approved()` is empty.
Deviations: added a `decision` kind for D1–D46 (never an approval); ids use `DL-` (no task_plan collision).
Parent hunk (mise.dev.toml, unvalidated):
```toml
[tasks."plan:decide"]
description = "Append an approval, operation, decision or receipt row to the decisions ledger"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I dev/plan_decide.py'

[tasks."test:plan-decide"]
description = "Exercise the decisions ledger CLI and approved() in a scratch ledger"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I -m unittest discover -s dev -p test_plan_decide.py -v'
```
Append `"test:plan-decide"` to `check:research` depends.
Unverified: mise argument passthrough for `plan:decide`; `check:research`. No cold review yet.

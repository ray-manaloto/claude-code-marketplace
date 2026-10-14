---
paths: ["dev/doctor/**"]
---

# Doctor detectors

- A detector reads state: settings files, Git objects, lane and retro records. A documented exception lives in the state it excuses (a settings key, a `parent hunk:` line), never in a document's wording.
- A detector is `dev/doctor/<name>.py` exporting `SURFACES` and `run(ctx) -> list[Finding]`; optional `context_lines(ctx)`, `BUDGET_MS` and `CONTEXT_RANK` (`core.py` docstring). Severity `P1`/`P2` exits 2; `skipped` also exits 2 on the `pre-commit` surface (a guard fails closed) and is reported, never counted, elsewhere.
- Budgets are measured in-process; one Git call through the mise shim costs about 200 ms, so a detector keeps Git calls to one per surface or raises its `BUDGET_MS` with the measurement in its retro.
- A doctor test builds `HOME` and `XDG_CONFIG_HOME` under the scratch directory and pins `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM`, so a personal global ignore or config cannot hide a finding.

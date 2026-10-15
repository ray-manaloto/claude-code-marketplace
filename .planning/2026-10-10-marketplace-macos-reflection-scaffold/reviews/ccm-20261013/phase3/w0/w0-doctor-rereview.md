# Focused re-review: w0-doctor repair f1bbc8d

Reviewer: Fable (read-only), 2026-10-14; saved verbatim by the parent.

**Verdict: PASS for integration** (no findings). SHA reviewed `f1bbc8dfcfa237febe682a41affeea9a9044f5d9` on `64e46d4`, base `c21941f`, branch `claude/w0-doctor-core`.

Evidence (worktree, VIRTUAL_ENV unset; mutations in scratch archives):
1. Scope: 7 changed paths (`dev/doctor/{budget,cli,core,settings}.py`, `dev/test_doctor.py`, retro, ledger) all in `owned_paths`.
2. P3-2: `dev/test_doctor.py:75-77` asserts `(2, ["P2"])`; mutation M8 (`("P1",)`) fails `test_doctor_cli_exit_codes`; dropping `guard or` fails it too.
3. P3-4: `budget.py:29-34` `ruling_off` (local > project > user/global); `GUIDE` and the doc grep gone; fixture test `test_autocompact_off_follows_settings_precedence` passes; `("project",)` mutation fails it. Live block: `P3 0`.
4. P3-5: `cli.py:70-71` counts `skipped` on `pre-commit` only; test at `test_doctor.py:88-90` was red on `64e46d4` (`0 != 2`). 1,000 ms budget and 202-280 ms margin recorded.
5. P3-1 split point (`report.py` with CT-22b, `integration.py` to w0-doctor-records) and P3-3 narrowing recorded.
6. Retro items 1-7 are literal edits with owners; item 5 names the `parent hunk: dev/test_doctor.py` MERGE_MSG line (THRESHOLDS table test to declare at integration).
7. Gates: unittest 13 rc 0; `test:hooks` 15 rc 0; `retro_gate` rc 0; `check` rc 0; `git diff --check` rc 0. Session-start wall 431/431/470 ms under load.
8. Em-dashes in delta: 0.

Not run: `tasks validate`, `check:acceptance-baseline`, `hk validate` (unchanged by this delta).

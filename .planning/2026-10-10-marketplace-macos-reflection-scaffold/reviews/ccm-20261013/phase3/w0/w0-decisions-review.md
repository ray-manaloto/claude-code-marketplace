# Review: w0-decisions (CT-24 wave-0 seed, W0-6)

Reviewer: Fable 5.1, cold, read-only (saved verbatim by the parent). Branch `claude/w0-decisions-ledger`, head `f9c8848` (impl `7649ca7`), base `c21941f` = merge-base = current integration tip; no tip merge needed. Worktree clean. Python 3.15.0, mise 2026.10.9.

**Disposition: PASS-with-P3. SHA reviewed: `f9c8848`.**

## Standards

- Scope: diff c21941f..f9c8848 = `dev/plan_decide.py`, `dev/test_plan_decide.py`, `P/decisions.jsonl`, `P/retros/w0-decisions.md`; all inside `owned_paths` (`lanes/w0-decisions.json:26-32`). No planning-file or `mise.dev.toml` edit.
- Baseline: `check:acceptance-baseline` rc 0, 19.
- Stdlib: AST scan: argparse, datetime, hashlib, json, os, pathlib, sys (+ subprocess, tempfile, unittest in tests).
- Size: 79 and 78 non-blank lines; within C4's 80 handwritten per file.
- External seam: CLI tests spawn `python3 -I dev/plan_decide.py … --file <scratch>` (`test_plan_decide.py:24-27`); `approved()`/`pending()` exercised through the import seam CT-17 will use. Receipt SHA at `:54` recomputed as the real digest of `labels: ready-for-human\n`.
- Mutation (scratch copy): always-append approvals, skip open-operation check, count operations in `approved()`, ignore receipts in `pending()`: each kills exactly one of the four tests.
- Red-first: not reconstructible (tests and module in one commit `7649ca7`); accepted as claims, mutations show the tests bite.
- Writing: `retros/w0-decisions.md:1` em-dash in the title (P3).
- Exit codes: `plan_decide.py:75-78` usage errors exit 1, refusals exit 2 (`:63-68`): matches the implementer brief (`w0-decisions-brief.md:13`), not the review dispatch nor argparse default (P3, convention needs one owner).

## Spec

- CLI: `approval --subject … --source`, `operation`, `receipt <id> --path [--rc]`, `--file` defaulting to `P/decisions.jsonl` (`:15-16, 83-96`); rows `{id, ts, kind, subject, text, source, receipt}` (`:38-40`); `approved()` importable (`:25-27`). `DL-` prefix cannot read as `D<n>`.
- Tests: the four named tests exist, rc 0; T-E5 at `test_plan_decide.py:32`.
- Seed: 50 rows, `DL-1..DL-50` sequential unique, sorted keys, timestamps within one second; DL-1..DL-4 `operation`, `approved()` = `set()`, `pending()` = DL-1..DL-4; sources D20, D20, D25 (D19), D3/D23 (+D32); zero `approval` rows; DL-5..DL-49 text byte-identical to task_plan D1-D45 plus `[status]`; no personal data or dash characters.
- Deviation `decision` kind: correct (approvals would have put `D<n>` into `approved()`); never counts (`:27`, test `:60-64`).
- D31 boundary holds: operations pending until a hash-bound receipt; nothing executes; mise wiring delivered as a literal hunk.
- Parent hunk (receipt `:9-21`): valid TOML (tomllib), two tasks, no collision with the 56 tasks, same `dir`/`run` idiom as `retro:gate`/`test:hooks`; appending `"test:plan-decide"` to `check:research` depends is one list edit. Passthrough verified in a scratch mise config: `mise run argv -- approval --subject "relabel #91" --source D20` preserves quoting; a `usage` variadic would split multi-word subjects. Apply as written; rerun `tasks validate`.

## Findings (severity-ordered)

- P3 `retros/w0-decisions.md:1`: em-dash in title; owner retro-writer.
- P3 `decisions.jsonl:50` (DL-50): `source` "parent dispatch of lane w0-decisions, 2026-10-14" resolves to nothing; task_plan table ends at D45. Owner parent: add the D46 row.
- P3 `plan_decide.py:75-78`: usage rc 1 vs dispatch "exit 2"; owner parent, record the convention in CT-24's remainder.
- P3 `plan_decide.py:70`: receipt stores `--path` as passed (absolute paths could enter the tracked ledger); owner wave-1 CT-24 (repo-relative). Retro notes it.
- P3 `plan_decide.py:38`: `DL-<n>` = row count + 1; safe only append-only single-writer; owner CT-11/CT-24 (lock or max-id scan).

## Gates rerun (VIRTUAL_ENV unset, pins set, lane worktree)

unittest 4 rc 0; `--help` rc 0; unknown kind rc 1; `tasks validate` rc 0 (56); `check` rc 0; `check:acceptance-baseline` rc 0 (19); `test:hooks` rc 0 (14); `hk validate` rc 0; `retro:gate -- w0-decisions` rc 0; `retro_gate.py --unit w0-decisions` rc 0; `git diff --check c21941f f9c8848` rc 0. Not run: `check:research`; the hunk applied to any `mise.dev.toml`; `plan:decide` through mise; red-first ordering from history.

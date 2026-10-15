# Focused re-review: w0-decisions repair 922eab4

Reviewer: Fable (read-only), 2026-10-14; saved verbatim by the parent.

**Verdict: PASS-with-P3 for integration.** SHA reviewed `922eab4` (delta from `f9c8848`, base `c21941f`), worktree clean.

Evidence (lane worktree, VIRTUAL_ENV unset):
1. Scope: delta touches only `dev/plan_decide.py`, `dev/test_plan_decide.py`, `retros/w0-decisions.md`; all in `owned_paths`.
2. Receipt path: `root()` (`plan_decide.py:26-28`) picks the nearest `.git` parent else the ledger dir; stores `relative_to(base).as_posix()`; outside-root refused rc 2 before any append (`:72-75`). Suite: 5 tests rc 0. Mutation (dropped `is_relative_to` guard in a scratch copy): `test_receipt_refuses_a_path_outside_the_ledger_root` FAIL, 1 of 5.
3. Docstring (`:5-6`) states 0/1/2 per C2 section E and the single-writer `DL-<n>` assumption with CT-11 as owner.
4. U+2014 and U+2013: 0 across all four owned files.
5. Retro: every prior P3 has a disposition; "Parent edits" lists five literal edits (D46 row, mise hunk by reference, two `dev/AGENTS.md` bullets, rule 14, issue-tracker sentence). `retro_gate.py --unit w0-decisions` rc 0.
6. 83 vs 80 non-blank lines: no split warranted; the overage is the reviewer-requested guard plus docstring.
7. `./dev/mise run check` rc 0; `git diff --check f9c8848 922eab4` rc 0.

P3 (owner parent, record-only): the retro says 36/46 retro records carry U+2014; after its own rewrite the count is 35/46. The argument against a gate rule still holds.

Not run: `check:research`, the proposed mise rows.

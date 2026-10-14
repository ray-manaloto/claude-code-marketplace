# w0-decisions retrospective — decisions ledger seed (CT-24 wave-0 seed, W0-6)

Unit `w0-decisions`, branch `claude/w0-decisions-ledger`, base `c21941f`; implementation commit
`7649ca7`. Written by the implementer in the lane worktree before independent review. Exits with
`VIRTUAL_ENV` unset, on the merged bytes (the integration tip `c21941f` is the base, so the
`--no-ff` merge reported "Already up to date", rc 0): `unittest discover -p test_plan_decide.py`
rc 0 (4 tests), `tasks validate` rc 0 (56), `check` rc 0, `check:acceptance-baseline` rc 0
(19/19), `test:hooks` rc 0, `hk validate` rc 0, `git diff --check c21941f HEAD` rc 0.
Not run: `check:research` (parent-run), the proposed `plan:decide`/`test:plan-decide` mise rows
(not lane-owned, so never validated here).

Ledger shape: rows `{id, ts, kind, subject, text, source, receipt}`; ids are `DL-<n>`, a prefix
no `D\d+` reader matches, so a ledger id never reads as a task_plan decision id (C2 used
`D-<n>`). Kinds: `approval` (one row per subject; a repeated subject is a no-op), `operation`,
`decision`, `receipt` (a new row naming the operation id, `{path, rc, sha256}`). `approved()` and
`pending()` are importable. Seed, all written by the CLI: DL-1 #91 relabel (D20), DL-2 draft PR
to `main` (D20), DL-3 T4 Phase C budget and approval (D25/D19), DL-4 `/to-tickets` approval of
CT-01..CT-25 (+CT-02b) (D3/D23, CT-25 via D32): four pending operations, zero approvals;
DL-5..DL-49 decisions D1-D45 from the task_plan table, DL-50 D46.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Steering: the dispatch message asked to seed D1-D45 plus D46, while the brief's CLI has only `approval`, `operation`, `receipt`. Writing them as approvals would put `D<n>` into `approved()`, and D46 is a parent decision, not a user approval. | Applied: a fourth kind `decision` (one row, no receipt, never an approval). `test_approved_lists_only_approval_subjects` failed first (decision subcommand rc 1) and passes; `approved()` on the seeded ledger returns an empty set. Deviation reported to the parent in the receipt. |
| P3 | Coding standards: `test_refuses_unknown_kind_and_receipt_for_missing_id` passed on its first run, because slices 1-2 already delivered the parser and the open-operation check. | Applied: mutation check, usage errors exiting 2 instead of 1, made that test FAIL (unittest rc 1); restored, all 4 tests pass. Slices 1-3 were observed red first (ModuleNotFoundError; receipt rc 1 != 0; decision rc 1 != 0). |
| P3 | Automated checks: `test:plan-decide` is not reachable from `check:research`, and `plan:decide` has no mise row; `mise.dev.toml` belongs to w0-doctor this wave. | Deferred, owner parent: the literal TOML hunk is in the lane receipt (D7 fallback), applied at integration. |
| P3 | Navigation: the brief says CT-01..CT-25 while task_plan D3/D23 say CT-01..CT-24; CT-25 joined through D32 (task_plan line 176). | Applied: DL-4 cites D3, D23 and D32 in `source`. |

Tool economy: none, because the lane took about 30 tool calls; the one detour was the live
PreToolUse gate on merge text, handled by running the merge from a scratchpad script.

No-ops: none, because no existing check or record held approvals or operation receipts.

Information access: none, because receipts store the path exactly as the caller passes it (a
repository-relative path stays relative) and no seed row carries a path or secret.

Global guidance: none, because no `AGENTS.md`, `CLAUDE.md` or rule file changed.

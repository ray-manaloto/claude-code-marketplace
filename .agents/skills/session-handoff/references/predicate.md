# Zero-loss predicate Z (X3 §2) as `dev/handoff.py check` findings

`check` exits 0 with no P1/P2, 2 with any, 1 on an error. P3 findings print but do not refuse.
Every finding carries `{id, class, severity, subject, evidence, fix_hint, auto_fixable}`, the
doctor shape, so the module can move into `dev/doctor/` once w0-doctor integrates.

| Id | Compares | Severity |
|---|---|---|
| `H.head-not-remote` | `rev-parse HEAD` vs `origin/<branch>` (no fetch); P1 when `## Next Step` claims "= remote", P2 when the drift is undeclared, P3 when declared ("ahead"/"behind"), P2 when the remote branch is absent | P1-P3 |
| `H.git-op-in-progress` | `MERGE_HEAD`, `REBASE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `rebase-*` in the Git dir | P1 |
| `H.handoff-stale-sha` | the HEAD claims in `## Next Step` and HANDOFF §1 equal HEAD; every backticked 7-40 hex SHA with a letter in both resolves (`git cat-file -e`) | P1 |
| `H.lane-record-mismatch` | per `lanes/<unit>.json`: a bullet naming the unit with "integrated" vs a non-integrated record (or the reverse) is P1; a "review PASS" claim against `review: null` is P3 | P1 / P3 |
| `H.receipt-missing` | backticked paths in `## Next Step`, HANDOFF §1 and every `Receipt:` line resolve under `<root>`, the plan dir, `RV/`, `RV/phase3`, `RV/phase4-prep`, `RV/phase3/w0` or `.claude/` (`RV/` and `P/` prefixes expand); a cut, non-integrated lane whose worktree is gone | P1 / P2 |
| `H.pending-decision-unlisted` | `decisions.jsonl` rows with `kind: operation` and `receipt: null` whose id is absent from `## Next Step` | P2 |
| `H.injection-probe-failed` | three pwf fires with fresh `PWF_SESSION_ID`s: legacy SessionStart, smart SessionStart (`PWF_INJECT=smart`), pretool twin. Legacy and pretool: `## Next Step` and its `Session handoff` line inside frame line 30; smart: both present plus a `phases:` line; the progress frame ends on the NEXT bullet while one exists. A probe that cannot run is P2 | P1 / P2 |
| `H.next-not-last` | `progress.md` has a `- NEXT` bullet that is not the last entry | P1 |
| `H.mode-not-inject-smart` | `<plan>/.mode` is not `inject-smart` (CT-30 owns the flip after D54) | P3 |
| `H.doctor-findings` | `dev/doctor/cli.py --surface session-start --json` (root, else the w0-doctor worktree copy): P1 count > 0 is P1, P2 count > 0 is P2; no doctor is no finding | P1 / P2 |
| `H.agents-unconfirmed` | `--agents-done` not passed: the operator has not asserted that every dispatched agent returned (the only non-file fact; `pgrep` is unreliable) | P2 |

Not checked (declared gaps): the index counts stated in the handoff vs `git status` (`write`
regenerates them); decisions pending the user (`task_plan.md` Decisions rows are prose);
SubagentStop evidence in the transcript (needs `--transcript`, w0-session-hooks).

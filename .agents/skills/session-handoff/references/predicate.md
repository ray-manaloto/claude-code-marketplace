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
| `H.request-unprojected` | rows of the request ledger `~/.local/state/claude-code-marketplace/requests/ledger.jsonl` (CL4 E1, written by the capture hooks) whose `session_id` is the plan owner's session id: the key `<id8>` is the last 8 characters of `tool_use_id` for an AskUserQuestion answer (every id starts `toolu_01`; the row also carries its turn's `prompt_id`, CT-87 receipt) and the first 8 characters of `prompt_id` for a prompt; a key is closed by `p:<id8>` anywhere in `## Open requests` or by a dispositions.jsonl row (beside the ledger) whose `key` is `p:<id8>`. Subject: the `p:<id8>` keys, never the prompt text. An absent ledger is no finding: `check --json` reports it under `requests.ledger_present` | P1 |
| `H.request-unlinked` | open `- [ ] R-n` items in `## Open requests` without an issue link (`issue: #N`, the bare `· #N ·` field of the CL4 §4.2 line shape, or a GitHub issue URL, D168); ticked `- [x]` items are closed | P2 |
| `H.agents-unconfirmed` | `--agents-done` not passed: the operator has not asserted that every dispatched agent returned (the only non-file fact; `pgrep` is unreliable) | P2 |

The two request findings are a dated D113 exception (D167); the C++ requests module (CT-93a)
replaces and deletes them. `check --json` and `state --json` carry a `requests` object: `ledger`,
`ledger_present`, `session`, `captured`, `foreign` (rows of other sessions: counted, not caught, so a stale
owner line is visible until CT-93a scopes by classifier), `unkeyed` (rows with neither key field: counted, not
caught, until CT-86 confirms the payload), `unprojected`, `open`, `unlinked` and `user` (open items
marked `owner user`). `write` turns it into the roll-call bullet of `## Next Step`
(`Open requests: N open, K unlinked, U/C captured unprojected (ledger|no ledger); Pending user:
<ids>; ids: <ids>.`), which replaces the hand-written `pending-user` line; when the
required bullets exceed the 16-line budget, `write` exits 1 and names the roll-call's share.

Not checked (declared gaps): the index counts stated in the handoff vs `git status` (`write`
regenerates them); decisions pending the user that have no `owner user` R-n line; captured
requests of other sessions (forks, worktree sessions) until the C++ classifier (CT-93a);
SubagentStop evidence in the transcript (needs `--transcript`, w0-session-hooks).

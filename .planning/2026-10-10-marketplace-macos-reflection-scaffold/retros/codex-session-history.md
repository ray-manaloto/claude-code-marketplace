# codex-session-history retrospective — Codex record retrieval skill

Unit: `codex-session-history` (lane SKILL). Worktree
`.claude/worktrees/codex-session-history`, branch
`claude/codex-session-history-skill`, lane commit `762b02f` on base `e0667ec`,
merged with tip `321fbde` as `8b986d3`. The parent drafted SKILL.md, five
scripts (`codex_rollout_digest`, `codex_threads`, `codex_research_receipts`,
`agentsview_search`, `codex_otel_tail`), two references and `evals/evals.json`,
smoke-tested against the four takeover threads (65–115 MB rollouts digested in
under 0.5 s each). The implementer landed them under `.claude/skills/` with a
byte- and mode-identical copy under `.agents/skills/`, a 25-record synthetic
rollout fixture and a six-test hermetic suite. Exits (VIRTUAL_ENV unset):
`tools:prepare` 0, `deps:sync` 0, `python3 -I -m unittest discover -s dev -p
test_codex_session_history.py` 0 (6 tests, 0.26 s), mirror mutation control
rc 1 then restored, `tasks validate` 0, `check` 0, `check:acceptance-baseline`
0 (19/19), `git diff --check` 0; after the merge, suite 0 and `check` 0.
Independent cold review and integration are recorded in `progress.md`.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Navigation: the draft SKILL.md invoked `scripts/...` with paths relative to the skill directory, which fail from a repository working directory. | Applied: every step names `<skill-dir>/scripts/...`; each step ends on a "Done when" condition. Verified by the reviewer reading SKILL.md and by the smoke run in review. |
| P2 | Automated checks: nothing enforced that `.claude/skills` and `.agents/skills` stay identical, the house pattern for cross-agent skills. | Applied: `dev/test_codex_session_history.py` compares bytes and modes of every file; a one-byte mutation of the copy failed the suite (rc 1) and the file was restored. |
| P2 | Steering: the lane brief named `python3 -I -m unittest dev/test_codex_session_history.py`, which cannot import under `-I`; the lane record repeated it. | Applied: the suite runs through `unittest discover -s dev -p ...`; the parent corrects the lane record's `required_checks` and adds the task `test:codex-session-history` to `mise.dev.toml` (shared file, parent-composed) and to the `check:research` dependency list at integration. Verification: `./dev/mise run test:codex-session-history` rc 0 on the integrated tree. |
| P3 | Automated checks: `agentsview_search.py` (local daemon) and `codex_otel_tail.py` (reads `~/Library`), plus the `children`, `turns` and `logs` subcommands of `codex_threads.py`, have no hermetic tests. | Deferred with owner: a follow-up SKILL unit adds fixture-backed tests for `children/turns/logs` (synthetic `thread_history_1.sqlite`/`logs_2.sqlite`) and a stub daemon for the AgentsView wrapper; owner: parent allocates `codex-session-history-tests-2` after the GATE lane. The reviewer's real-record smoke of `codex_threads.py list` stands in meanwhile. |
| P3 | Tool economy: the skill-creator eval loop in `evals/evals.json` (with-skill versus baseline runs) was not executed; it needs real `~/.codex` records and provider-free runs of a second Claude. | Deferred with owner: parent runs the eval loop after integration as an admitted, read-only operation and records pass rates in the skill workspace; no network is required. |
| P3 | Information access: the fallback `python3` on PATH inside the lane worktree resolved to the root checkout's `.venv` interpreter, so an inherited selector leaks across worktrees together with `VIRTUAL_ENV`. | Routed to lane `rf-env-scrub` (owner: its implementer), which scrubs inherited selectors in `dev/check.py`; verified there by `check` rc 0 with the project venv exported. |

Coding standards: the scripts keep the draft's compact style (one-line
argparse declarations); no judgement rule is added — the reviewer decides case
by case. No-ops: the draft's sentence restating that scripts open SQLite
read-only was deleted because the code already guarantees it. Every actionable
finding is applied in this unit or deferred to a named owner with a
verification step.

## Review, repair and integration disposition (parent, 2026-10-13)

Independent Fable cold review of lane commit `762b02f`: **PASS-with-P2** —
the liveness subcommands (`turns`, `children`, `logs`, `show`'s history branch)
had no test — plus seven P3s: ambiguous id prefix silently resolved, turn-final
messages lacked `ord=`, the liveness command and top-level `--json` placement
were not in SKILL.md, `codex_otel_tail.py` read a different variable than its
docstring named, the AgentsView and OTel wrappers were untested, digests did
not mask obvious secret shapes, and receipt JSON reads were unbounded. The
implementer applied every finding test-first in `89b0705` and the same
ambiguous-prefix contract in the receipts script in `ea893a8` (12 hermetic
tests). The focused re-review of the delta returned **PASS for integration**
(12 tests rc 0, `check` rc 0, baseline 19/19 rc 0, `git diff --check` rc 0;
`.claude`/`.agents` copies identical in bytes and modes).

| Severity | Finding | Disposition |
| --- | --- | --- |
| P2 | Liveness subcommands untested. | Applied: fixture-backed `thread_history_1.sqlite`/`logs_2.sqlite` tests under a temporary `CODEX_HOME`; verified by the re-review. The earlier "deferred with owner" row above is superseded by this application. |
| P3 ×7 | Listed above. | Applied in `89b0705`/`ea893a8`; each has a test; verified by the re-review. |
| P3 | Commit subjects captured by the git-commit regex bypass `clip()` and therefore the secret mask. | Deferred with owner: the implementer routes them through `mask()` in lane `codex-session-history-tests-2` (CT-10). |

Integrated by the parent with `test:codex-session-history` added to
`mise.dev.toml` and to the `check:research` dependency list. Composed-tree
gates: `tasks validate` 51 rc 0, `test:codex-session-history` 12 rc 0, `check`
rc 0, `check:acceptance-baseline` 19/19 rc 0, `git diff --cached --check` rc 0.
`check:research` attempt 1 failed with 15 errors in `test:collect` while an
independent reviewer was running suites concurrently in another worktree;
attempt 2, run serially, returned rc 0 with every suite OK. The raced attempt is
recorded, not counted; the serial pass is the receipt (log retained in the
session scratchpad). Tool-economy learning: named checks stay serialized
across worktrees, as the contract already requires.

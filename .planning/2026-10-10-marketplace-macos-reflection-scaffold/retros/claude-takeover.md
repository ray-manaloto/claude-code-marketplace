# Claude takeover retrospective — ownership transfer and lane conventions

Unit: `claude-takeover` (documentation and planning only). Scope: the activation
record in `docs/agents/claude-takeover.md`, the plan header and takeover section,
`ticket-ledger.md`, three lane records and the findings/progress entries. Source
base `d2a41032e4b9318f309cbbe73dbbd79920dc4418`; no Codex worktree, branch or
packet was modified. Primary sources: the four Codex rollout digests and briefs,
`git merge-tree` of `0195289` onto `d2a4103`, the GitHub issue graph (101 issues
via GraphQL `blockedBy`/`parent`), and the pre-merge gate exits on `d2a4103`
(`tasks validate` 48 tasks rc 0, `check` rc 0, `check:acceptance-baseline` 19/19 rc 0).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Navigation: the standby runbook and `docs/status.md` named the retained `2a14` worktree and HEAD `6b5b092` as current, so a fresh agent would resume in the wrong checkout. | Activation record written with the exact source checkout, HEAD, remote and common Git directory; the plan header now names the Claude session as owner and links the record. `docs/status.md` is left to the LEDGER lane and is marked historical there. Verified by re-reading both files after edit. |
| P2 | Automated checks: no deterministic check refuses integration or publication of a unit without a retro record, so the "retro after every ticket" rule depended on agent memory. Calibration of a draft gate against the 33 existing records passed 16 and failed 17, mostly older A-series records that skipped categories. | The GATE lane adds `dev/retro_gate.py`, `dev/test_retro_gate.py`, the `retro:gate` mise task, `hk` git steps and Claude Code hooks; this record is written to the shape that gate checks. Applied as a planned lane with an owner, not a deferred wish; verification is the lane's own tests. |
| P3 | Information access: Codex's evidence lives in rollouts, SQLite stores and private packets outside the repository, and nothing in the repository told a successor where. | `findings.md` now lists the stores and the hash-bound A06 unit3 import packet; the SKILL lane ships `codex-session-history` so the lookup is a script, not archaeology. Verified: the scripts ran against all four threads (digests of 65–115 MB rollouts in under 0.5 s each). |
| P3 | Steering: `.gitignore` is one of the 19 frozen baseline files, so the lane worktree directory cannot be ignored in the committed tree without a baseline transition. | Local exclusion added to `.git/info/exclude`; the plan records the constraint so a reviewed baseline transition can carry it later. Verified by `git status --short` showing no `.claude/worktrees` entries after creation. |

Coding standards: no judgement-only rule found; the existing reviewer guidance
covers contract preservation. Tool economy: the four 400–490 K-character
digests were handed to Fable synthesizers instead of being read inline, and
AgentsView's semantic index (9 % built) was replaced by lexical search with the
coverage status recorded; no further change. No-ops: the superseded standby
wording is kept as a labelled historical snapshot rather than deleted, because
its receipts are still cited elsewhere; no ineffective instruction was added.
All four findings above are applied in this unit or allocated to a named lane
with its own verification; none is deferred without an owner. Checks on the
composed tree: `check` and `git diff --check` recorded in the commit receipt in
`progress.md`.

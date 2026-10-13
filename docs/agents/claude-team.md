# Claude team

How the Claude Code session runs the marketplace work after the
[takeover](claude-takeover.md). Ownership rules live in
[codex-task-orchestration.md](codex-task-orchestration.md#ownership) and the
retro protocol in [ticket-retro.md](ticket-retro.md); this guide adds the roles,
the lane lifecycle and the gate. Role definitions are `.claude/agents/*.md`.

## Roles

| Role | Model | Effort | Writes? | Reads lane record? | Exit criterion |
| --- | --- | --- | --- | --- | --- |
| parent | session model | session | integration branch, shared planning | allocates it | merged lane has a passing retro gate and recorded exits |
| implementer | Opus | high | its `owned_paths` | first | `./dev/mise run retro:gate -- <unit>` exits 0 after tests, `check` and tip reconciliation |
| doc-writer | Sonnet | high | its `owned_paths` | first | `check` exits 0, every cited path resolves, retro draft handed off |
| reviewer | Fable | high | nothing | via the parent's brief | disposition PASS, PASS-with-P2/P3 or FAIL with unrun checks named |
| retro-writer | Fable | high | retro record plus applied learnings | first | `retro:gate` and `check` exit 0, no actionable finding open |
| extractor | Haiku | low | nothing | via the parent's brief | requested facts returned as JSON, absent values `null` |

The merger is the parent or a separately briefed session. It verifies that
changed paths sit inside `owned_paths`, then integrates one lane at a time.

## Lane lifecycle

Each stage ends on a receipt recorded in `.planning/<PLAN_ID>/`; states stay
separate (planned, implemented, tested, reviewed, committed, published).

| Stage | Who | Receipt |
| --- | --- | --- |
| allocate | parent | `lanes/<unit>.json` with allowlist, base SHA, reviewer, status |
| implement | implementer or doc-writer | commits in `.claude/worktrees/<unit>` on `claude/<unit>-<slug>` |
| test | writer | exit codes of the unit's tests, `check`, `check:acceptance-baseline` |
| review | reviewer | disposition with severity-ordered findings |
| retro | retro-writer | `retros/<unit>.md` and the `retro:gate` exit |
| integrate | merger | merge commit, composed-tree check exits |
| publish | parent | `delivery:prepare` and `delivery:publish` receipts, remote SHA |
| close | parent | ticket ledger row and the qualified close operation, one ticket at a time |

## The retro gate

`dev/retro_gate.py` refuses integration or publication of a unit whose retro
record is missing, skips a category or leaves a finding open. One check runs
in three layers:

1. mise task `retro:gate` - the manual and CI form.
2. `hk` git steps on merge and push - agent-independent, so Codex is bound too.
3. Claude Code hooks - `PreToolUse` denial of `git merge`, `git push` and
   `delivery:publish`, plus `Stop`/`SubagentStop` blocks keyed to a lane record.

Layer 1 arrives with lane retro-gate (CT-01); layers 2 and 3 arrive with lane
GATE-2. The gate checks record shape and bindings; judgement about findings
stays with the reviewer.

## Model split

Opus implements code lanes, Sonnet writes documentation lanes, Fable reviews,
runs retros and synthesizes, Haiku extracts mechanical facts. Choose the role by
the lane record's `writer_model`.

## Concurrency

Up to four offline lanes run at once, each in its own worktree with a disjoint
allowlist. Host-heavy lanes run one at a time and need the user's confirmation
for each run; a previous receipt grants no new admission. Integration and
publication stay serialized under the parent.

## Codex compatibility

The same roles mirror into `.codex/agents` in a later lane, so Codex can resume
after 2026-10-19 under the same lane and retro-gate rules. Until then
`.codex/agents` keeps its three read-only roles, and Codex worktrees stay
import sources.

## Where learnings land

Mechanical rules go to `dev/check.py` or a named check; judgement rules to
`CODING_STANDARDS.md` (arrives with lane NAV); navigation to the nearest `AGENTS.md` or a `paths:`-scoped
`.claude/rules/*.md`; repeated workflows to skills; roles to `.claude/agents`.

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
record is missing, skips a category or leaves a finding open. A lane writes that
record at `.planning/<PLAN_ID>/retros/<unit>.md` inside its own worktree and
commits it on the lane branch, so every layer below finds it there or in the
merged tree. One check runs in three layers (CT-01, CT-02):

1. mise task `retro:gate -- <unit>`: the manual and CI form.
2. `hk.pkl` Git hooks, agent-independent so Codex is bound too:
   `pre-merge-commit` runs `retro:gate-merge` and `pre-push` runs
   `retro:gate-push`, both through `dev/hooks/git_gate.py`. The merge form gates
   the `claude/` or `codex/` branch being merged (Git exposes it only through
   `GIT_REFLOG_ACTION` before the merge commit); the push form gates the second
   parent of each lane merge not yet on the remote. The integration branch and
   `main` are never units. The parent installs the hooks once with
   `./dev/mise run hooks:install` (`hk install --force-local`, because a global
   hk install otherwise suppresses the per-repository hooks).
3. Claude Code hooks in `.claude/settings.json`: `PreToolUse`
   (`dev/hooks/pretooluse_gate.py`) denies `git merge`, `git push` and
   `delivery:publish` of a failing lane; `delivery:publish` pushes with
   `--no-verify`, so it checks the unpublished lane merges itself.
   `SubagentStop` (`subagent_stop_gate.py`) blocks a subagent whose `cwd` is a
   lane worktree without a passing record, and `Stop` (`stop_gate.py`) blocks
   the parent while a lane record says integrated without a passed retro. Each
   blocks once; a continuation is allowed.

Lane record vocabulary for the `Stop` gate: `status` starts with `allocated`,
`implementing`, `implemented`, `reviewed`, `integrated` or `published`, plus
free text; an integrated or published lane keeps the word `integrated`.
`retro` is `pending` (or absent) until `retro:gate -- <unit>` exits 0 on the
integrated tree, then `passed`. `./dev/mise run test:hooks` exercises every
layer in scratch repositories. The gate checks record shape and bindings;
judgement about findings stays with the reviewer.

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

By kind, per [ADR 0001](../adr/0001-claude-takeover-and-retro-gate.md). `CODING_STANDARDS.md` arrives with ticket CT-04 (NAV).

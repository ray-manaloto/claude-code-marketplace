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

Restart rule: `.claude/agents/*.md` are committed and present before the session
that dispatches them; a session that creates them restarts first.

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

## Integration

- Merge every lane with `git merge --no-ff <branch>` and let Git create the commit;
  `--no-commit` then commit skips `pre-merge-commit`, the retro gate's merge layer.
  A PreToolUse deny for `--no-commit` lands with CT-02b.
- Until `hooks:install` has put hk layer 2 in place (it waits for CT-02b), run
  `./dev/mise run retro:gate -- <unit>` by hand before the merge and again on the
  merged tree. Layer 3 stays live meanwhile.
- Two gates track two states. The retro gate and the `Stop` gate read lane state
  (`lanes/<unit>.json`, `retros/<unit>.md`); pwf reads phase state (`task_plan.md`).
  A passing retro does not close a phase and a closed phase does not pass a lane:
  record both.

## The retro gate

`dev/retro_gate.py` refuses integration or publication of a unit whose retro
record is missing, skips a category or leaves a finding open. A lane writes that
record at `.planning/<PLAN_ID>/retros/<unit>.md` inside its own worktree and
commits it on the lane branch, so every layer below finds it there or in the
merged tree. One check runs in three layers (CT-01, CT-02):

1. mise task `retro:gate -- <unit>`: the manual and CI form.
2. `hk.pkl` Git hooks: `pre-merge-commit` runs `retro:gate-merge` and
   `pre-push` runs `retro:gate-push`, both through `dev/hooks/git_gate.py`.
   The merge form gates each `claude/` or `codex/` ref being merged (Git
   exposes it only through `GIT_REFLOG_ACTION` before the merge commit) and
   refuses a source it cannot classify. The push form gates each unpublished
   lane merge, attributed by its default subject or by refs pointing exactly
   at its second parent. The integration branch and `main` are never units.
   The parent runs `./dev/mise run hooks:install` once: `hk install
   --force-local`, because a global hk install suppresses the per-repository
   hooks, plus local `merge.ff=false`. This layer binds any agent, Codex
   included, only for merge commits. A fast-forward (`--ff` merge or pull), `--squash`, a
   rebase, a cherry-pick, or `--no-commit` then commit all skip
   `pre-merge-commit`. `pre-push` is the backstop for merge commits; squash,
   rebase and cherry-pick leave none, so they rely on layer 3 and review.
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

## Hook composition

- Two `Stop` hooks run on every parent stop: the pwf `gate-stop.sh` and
  `dev/hooks/stop_gate.py`. They compose into one block per `Stop` because pwf blocks
  only when `.planning/<PLAN_ID>/.mode` or the project root `.mode`
  (`$PWF_PLAN_ROOT/.mode`) carries `gate`. Leave both absent or set to `inject-smart`,
  never `gate`. The check for this and the compose test land with CT-16 and CT-02b.
- `onFailure` has no effect on `Stop` and `SubagentStop`; those two gates block through
  their decision output alone. `onFailure: block` matters on `PreToolUse`, where a
  timed-out hook otherwise allows the call.
- Hooks bind only where Claude Code runs them: an interactive session holds project
  hooks back until the user accepts workspace trust, `disableAllHooks` in any settings
  file switches them all off, and only managed settings can keep a hook from being
  bypassed. Treat a hook-free session as ungated and run `retro:gate` by hand.

## Context budget

Thresholds count tokens in the session transcript and sit below the project
`autoCompactWindow` (700000, `.claude/settings.json`):

| Level | Tokens | Behaviour |
| --- | --- | --- |
| warn | 400K | checkpoint (append a dated `progress.md` entry, refresh the handoff block at the head of `task_plan.md`), then delegate the remaining work to lanes |
| fork_deny | 500K | dispatch a fresh `implementer` or `doc-writer`; a fork would start at this size |
| checkpoint | 550K | finish the handoff, confirm it reads whole, then `/clear` |
| hard | 650K | stop starting work; only the handoff and `/clear` remain |

Run Codex forensics and transcript reads in subagents so the parent window carries
conclusions. Use a fork only for tasks of about ten minutes or less, below `fork_deny`.
The hooks that enforce these levels arrive with ticket CT-23 (`prompt_hook`,
`agent_gate`, lane `w0-session-hooks`) and read the thresholds from
`dev/doctor/budget.py`, which arrives with CT-22a; until then the parent applies the
table itself.

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

By kind, per [ADR 0001](../adr/0001-claude-takeover-and-retro-gate.md). Reviewer judgement rules live in `CODING_STANDARDS.md` (integrated with ticket CT-04, lane `nav`, merge `fa892d2`).

# Brief templates

Until CT-19's `lane:brief` prints the header block from the lane record, compose each
brief from the template below (R8 §Brief templates) plus the `brief_lines` from
`frontier.py next` and the scheduler's judgement lines. Pointers only: the procedure lives
in the agent definition the brief names. `P/` = `.planning/<PLAN_ID>/`.

## Judgement lines (every role)

```
CTX-CEILING: <ceiling> (model <model>). Checkpoint to P/ledger-<unit>.jsonl at <0.8 × ceiling>; at the ceiling commit, write the handoff and stop; do not fork.
MODEL: <model> effort <effort> (rule <policy.kind | escalation | class.design>).
SEAM: <the seam the ticket names, from the scheduler>.
SPLIT: <none | offline-portion of #n: source, CMake and fixture preparation only; no heavy run (not admitted); report the heavy step as a separate unit | continuation of <unit> from <sha>>.
```

## Implementer

```
LANE-UNIT: <unit>
Role: implementer (.claude/agents/implementer.md). Ticket: <issue URL or P/proposals/.../tickets.preview.json#<CT-id>>.
Record: P/lanes/<unit>.json (read first; parent-owned, do not edit).
Worktree: .claude/worktrees/<unit>  Branch: claude/<unit>-<slug>  base_sha: <allocation commit>
Env: PWF_PLAN_ROOT=<root> PLAN_ID=<plan id>; unset VIRTUAL_ENV; run ./dev/mise run tools:prepare && deps:sync once.
Allowlist: exactly record.owned_paths. Your ledger: P/ledger-<unit>.jsonl (append-only). Never: task_plan.md, progress.md,
  findings.md, ticket-ledger.md, mise.dev.toml, .claude/settings.json, any AGENTS.md outside the allowlist.
Tasks: put new test:*/verb rows in mise/tasks/<unit>.toml; name the check:research entry you need in the handoff.
Seam: <SEAM>; tdd red first. Size: ~5 files / 300 lines, report a split point past that.
Checks (literal, record.required_checks): <cmd 1> ; <cmd 2> ; ./dev/mise tasks validate ; ./dev/mise run check ;
  ./dev/mise run check:acceptance-baseline ; git diff --check ; ./dev/mise run retro:gate -- <unit>
  Never run check:research here. Record for each: command, rc, selectors present, whether another dev/check.py ran.
Retro draft: P/retros/<unit>.md per docs/agents/ticket-retro.md (seven categories).
Before reporting: git merge <integration tip SHA you observed last>, rerun affected checks, commit, git status clean.
Commit trailers (read from <scratchpad>/trailers.txt): Co-Authored-By / Claude-Session lines.
Handoff (<=300 words): branch, final SHA, tip merged, changed paths, each command + rc, unverified items, proposed
  edits outside the allowlist as literal diffs, retro path.
Do not: push, publish, merge into the integration branch, spawn agents, close tickets, edit other lanes' files.
<judgement lines>
```

`doc-writer` uses the same header with `Role: doc-writer (.claude/agents/doc-writer.md)`.

## Reviewer

```
LANE-UNIT: <unit>
Role: reviewer (.claude/agents/reviewer.md), read-only, cold. Ticket: <URL or preview pointer>.
Record: P/lanes/<unit>.json. Branch: claude/<unit>-<slug>. Fixed point: <base_sha>. Head: <lane tip SHA>.
Diff: git diff <base_sha>..<head> (read every changed file). Handoff receipt: <scratchpad path>.
Standards sources: CODING_STANDARDS.md, nearest AGENTS.md, .claude/rules/*.md, docs/agents/ticket-retro.md,
  docs/agents/codex-task-orchestration.md#ownership. Baseline: evidence/onboarding/baseline-files.json (19 untouched).
Spec source: the ticket's acceptance criteria (and the spec's spec.md for CT-*).
Check: changed paths subset of owned_paths + record/retro/log; tests assert an external seam; receipts bind exact rc;
  tip merge present; no named check claimed as a receipt while another ran.
Re-run yourself (read-only): <unit test command>; ./dev/mise run retro:gate -- <unit> in the worktree.
Report: ## Standards and ## Spec blocks, severity-ordered P1/P2/P3 with path:line, disposition
  (PASS | PASS-with-P2/P3 | FAIL), the checks you did not run. <=400 words per axis.
Do not: edit, write, merge, push, or spawn agents.
<judgement lines>
```

## Retro-writer

Same header lines (LANE-UNIT, record, branch, SHAs, receipt path, review disposition),
`Role: retro-writer (.claude/agents/retro-writer.md)`, then:

```
Ledger: for every applied, rejected or deferred finding run
  python3 -I .claude/skills/ticket-frontier/scripts/frontier.py ledger append --row '<json per references/learning-ledger.md>'
Auto: anything inside owned_paths, new tests + their task rows, the nearest AGENTS.md pointer line, a .claude/rules/*.md
  scoped to the lane's paths, references/ of a skill the lane owns, the ledger line itself.
Propose (literal hunk in the handoff, never applied by you): root AGENTS.md/CLAUDE.md, .claude/AGENTS.md,
  .claude/settings.json, hk.pkl, .claude/agents/*.md frontmatter, CODING_STANDARDS.md rule additions or deletions,
  dev/check.py rules that widen a refusal set, P/frontier.toml, the 19 frozen baseline files, docs/accepted-decisions.md.
Done when ./dev/mise run check and retro:gate -- <unit> exit 0 and every ledger row names its verification rc.
<judgement lines>
```

## Merger (fresh `implementer`-typed agent when the parent is above `warn`)

Header lines plus `Role: merger; procedure = references/scheduler.md §Integration by hand
(or lane:integrate <unit> when CT-17 exists)`, the lane's `required_checks`, the parent
hunks to include and the message file path. Done when it reports the merge SHA, every
gate rc and the `progress.md` line it appended through `plan:log`.

## Scheduler

```
Role: frontier-scheduler (.claude/agents/frontier-scheduler.md), read-only.
Plan receipt: P/frontier/plan-<utc>.json. Chosen tickets: <ids with bodies or preview pointers>.
Active lanes: P/lanes/*.json (owned_paths, excluded_shared_paths) and P/frontier/state.json claims.
Return one JSON object per candidate: {unit, ticket, owner_role, owned_paths, excluded, seam, est_files, est_loc, split, conflicts}.
```

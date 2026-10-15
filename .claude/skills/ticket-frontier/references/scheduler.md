# Scheduler

What `frontier.py plan` computes, what the `frontier-scheduler` agent adds, and the manual
sequences the loop uses until CT-17 lands. Design source: K1 §3 and R8 §Conflict analysis.

## Inputs

| Input | Path | Without it |
| --- | --- | --- |
| tracker graph | `.planning/<PLAN_ID>/ticket-ledger.json` (CT-05 `ledger:sync`) | `--graph <json>` with the same shape (config.md §Graph) |
| lane records | `.planning/<PLAN_ID>/lanes/*.json` | none needed; an empty dir is a clean frontier |
| claims | `.planning/<PLAN_ID>/frontier/state.json` | created on first claim |
| admissions | `.planning/<PLAN_ID>/decisions.jsonl` rows `{"kind":"admission","ticket":"#21"}` (CT-24) | `--admitted #21` after the user says yes |
| thresholds | `dev/doctor/budget.py` `fork_deny` (CT-22) | the ceiling from `frontier.toml` alone |

## Done, held, ready

- **Done**: the graph says `closed`, or a lane record whose `status` starts with
  `integrated` or `published` carries `retro: passed`. GitHub `blockedBy` drops only on
  close, so the frontier is computed from what merged, not from the tracker's count.
- **Held**: a ticket named by any lane record that is not done and not closed
  (`implementing`, `reviewed`, `integrated` without a passed retro: the retro barrier of
  `ticket-retro.md` §5), or claimed in `state.json`.
- **Ready**: open, every blocker done, not held.

## Priority (ties broken in this order)

1. `critical_path`: longest chain of open dependents below the ticket.
2. `unblocks`: number of open tickets it directly unblocks.
3. `always_active`: membership in a class listed in `always_active`.
4. `wave`: `[waves]` in `frontier.toml`, else the graph's `wave` field, else last.
5. ticket number, then id.

On the fixture graph the order is `CT-15, #16, #21, #17, #20`; a plan receipt records the
scores so a reviewer can recompute them.

## Capacity

`max_parallel` counts claims whose role is `implementer` or `doc-writer`. Every claim,
reviewers and the scheduler included, counts against `max_live_agents` (5). `plan` fills
at most `min(writers_free, live_free)` slots; `claim` refuses past either limit. A slot
that stays empty is reported as `unfilled` with the `skipped` and `conflicts` rows that
explain it; the two ways to fill it are an admission (`--admitted #n`) or a scheduler
split of a chosen ticket into independently testable sub-lanes. The plan never fills a
slot with a second heavy ticket on its own.

## The cxx slot

While a member of an `always_active` class is ready and no claim of that class is live,
the first slot goes to that class, chosen by the class `order` list (heavy order
`#21 → #20 → #17 → #16`), then by ticket number. A `heavy` member runs in full only with
an admission for this run. Without one the slot takes the ticket's **offline portion** as
the split unit `<n>-offline` (source, CMake and fixture preparation the implementer
splits out per `implementer.md` step 3), the receipt notes
`offline-portion of #21; heavy run not admitted`, and the plan asks the admission question
once. Every other heavy ticket is skipped with `heavy, not admitted; one heavy run at a
time` until it has its own admission.

## Conflict rule

A candidate is chosen only when its `owned_paths` intersect no active lane's
`owned_paths ∪ excluded_shared_paths` and no other claim's `owned_paths`, and it touches at
most one hot path (`[hot_paths]`: `dev/check.py`, `dev/hooks/`, `dev/lane.py`,
`docs/agents/claude-team.md`, `.claude/settings.json`, any `AGENTS.md`), each of which has
one owner per wave. Directory entries end in `/` and match by prefix. The script applies
the rule to paths it knows (graph `owned_paths`, claims, records); the scheduler agent
supplies them for tickets that carry none.

## Judgement (frontier-scheduler agent)

Tickets carry no paths, so the agent reads each chosen ticket's body and the tree and
returns, per candidate: `unit`, `ticket`, `owner_role` (`implementer` or `doc-writer`),
`owned_paths`, `excluded`, `seam`, `est_files`, `est_loc`, `split`, `conflicts`. Split
rules: `est_files > 5` or `est_loc > 300` → sub-units; two independently testable seams →
parallel sub-lanes; a documentation half → a `doc-writer` sub-lane; a hot path or a frozen
baseline file → one lane, Opus reviewer (D189), no parallel sibling. Re-run it at skill start,
after every `release`, after every failure receipt (`task_status ∈ {partial, blocked,
failed}`) and whenever the cxx slot empties. Nothing is written until `claim` accepts the
proposal.

## Allocation by hand (until CT-17 `lane:allocate`)

1. Write `lanes/<unit>.json` with the fields `.claude/rules/planning-records.md` lists,
   `status: allocated`, `base_sha` = the integration tip; commit it on the integration branch.
2. `git worktree add .claude/worktrees/<unit> -b claude/<unit>-<slug> <base_sha>`.
3. In the worktree: `unset VIRTUAL_ENV; ./dev/mise run tools:prepare && ./dev/mise run deps:sync`; when the lane record admits `network: none`, this step is the parent's and its rc goes into the record's `notes`.

## Integration by hand (until CT-17 `lane:integrate`)

R8 §Integration protocol, in short: one merger, root checkout, `MERGE_HEAD` absent, no
named check running; preflight (review PASS or PASS-with-P2 closed, `retro_gate.py
--branch <branch>` rc 0, tip merged); `git merge --no-ff <branch>` with a message file;
changed paths ⊆ `owned_paths ∪ {record, retro, log}` else `git merge --abort`; parent
hunks (`check:research` depends entry, settings hook entry, literal AGENTS/rules edits)
in the same commit; gates on the composed tree with each rc recorded (`tasks validate`,
`check`, `check:acceptance-baseline`, the record's named checks, `check:research`
serialized, `git diff --check`, `retro:gate -- <unit>`); record `status=integrated` and
`retro=passed` together; one `progress.md` line; `delivery:prepare` then
`delivery:publish`.

## Continuation (`split-required`)

`release <unit> --from-journal <file>` reads the last `usage` of the CT-19 journal. At or
over the ceiling the claim is released as `split-required`: the slot is freed, the ticket
moves to `state.json` `continuations` and stays held (not re-planned from scratch), and
`--resume` is refused. Carve a continuation unit from the lane's commits and
`ledger-<unit>.jsonl` (when the lane never checkpointed, from the branch commits and the
journal's last receipt alone): new unit id `<unit>-2`, same ticket, `owned_paths` = the
untouched remainder, a fresh brief naming the last SHA, the open checklist and the
CTX-CEILING line. `claim <unit>-2 --ticket <id>` clears the continuation. State travels
through the branch and the ledger, never the transcript.

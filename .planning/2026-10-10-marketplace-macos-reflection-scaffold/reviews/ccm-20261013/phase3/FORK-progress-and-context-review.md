# Fork review: pace, parallelism, agent tuning, reprioritisation, and context handoff

Written 2026-10-14 by a worker fork of session ccm-20261013-check (no subagents spawned: the
fork rule forbids it, so the "/clear vs /compact" team the directive asked for is replaced by
this direct analysis). State at writing: wave-0 lanes w0-docs and w0-decisions integrated
(w0-decisions publish in flight, records `ecc0ad7`, remote `3bb4fd3`); w0-doctor retro repair
`f1bbc8d` needs a focused re-review (behaviour changed in budget/cli/core); two sequenced lanes
not cut; CT-21 designed and allocated but not dispatched.

## 1. Pace

Wall clock for wave 0 so far: 3 lanes built in parallel in about 20 min each; each lane then
spends 10-15 min in review, 8-10 min in retro, and 12-15 min in a serialized merge + records +
A09 publish + CI wait. The build stage parallelises; the tail is serial and parent-bound (one
root writer, one publish per integration, D37). The parent's turn cadence is the second limiter:
every stage transition waits for a notification round trip. Verdict: the pace is correct for a
wave whose lanes share hot spots, but the pipeline is under-filled: at most one merger plus one
reviewer runs while three lanes could be building.

## 2. Parallel work that can start now (disjoint paths verified by T2 and the allocator)

1. **CT-21 codex-imports lane** (`lanes/ct21-codex-imports.json`, brief
   `reviews/ccm-20261013/T2-ct21-brief.md`): no overlap with any wave-0 lane; the snapshot and
   import plan exist; gitleaks clean. Dispatch an Opus implementer immediately.
2. **Focused re-review of w0-doctor `f1bbc8d`** (Fable, medium): independent of the merger.
3. **User-typed stages** (`/mattpocock-skills:setup-matt-pocock-skills`, then publish the spec
   and type `/mattpocock-skills:to-tickets`): they touch the tracker and `docs/agents`
   seed files only; nothing in wave 0 depends on them, but wave 1 and `ticket-frontier` do
   (tickets need GitHub ids). Ask the user now rather than after wave 0.
4. **D7 include-file spike** (`task_config.includes` under `./dev/mise`): a 30-minute Opus
   lane with owned path `mise/` only; if it validates, every later lane stops touching
   `mise.dev.toml`, which is the hot spot that forced w0-doctor-records and w0-session-hooks
   to wait.
Do not start: w0-doctor-records, w0-session-hooks (own `settings.json`/`mise.dev.toml`
after w0-doctor), ct11-check-lock and ct05-ledger (own `dev/check.py`/lane records until
w0-doctor and CT-19 land).

## 3. Agent tuning

- **Models/effort**: keep Fable high for cold reviews (they found the MISE_* harness bug, the
  stale manifest hash, the doc-grep false positive, the fail-open guard); Fable medium is
  enough for focused re-reviews (the one run at medium was complete). Implementers Opus high
  stay. Mergers can drop to Sonnet once `lane:integrate` (R7/CT-12) exists; until then they
  exercise judgement (deferrals, hunk ownership), so Opus high.
- **Specialists**: the `reviewer` definition has no Write tool, so three reviews had to be
  pasted into files by the parent (about 6K tokens each of parent context). Fix: instruct
  reviewers to write their report with a Bash heredoc into `reviews/**` (Bash is allowed),
  and say so in `.claude/agents/reviewer.md`. Add a `merger` definition (today the merger is
  an ad-hoc implementer brief) carrying the A09 mechanics, the scratchpad-script workaround
  for the PreToolUse "git merge" text gate, and the hk-global-install fact.
- **Tools**: the PreToolUse gate's substring match on "git merge"/"git push" cost every merger
  a scratchpad script; CT-02b should move up (see §4). Reviewers need `mise x -- gitleaks`
  and `hk` on PATH (they used them).
- **Self-learning automation**: the retro-writer loop works (3 lanes, learnings applied or
  proposed with destinations) but proposals pile up with no consumer: D47, D48, `dev/AGENTS.md`
  bullets, `claude-team.md` sentences, `.claude/rules/dev-doctor.md`. Add a fixed merger step
  "apply every `propose` row whose destination is parent-owned and in the D31 auto set; list
  the rest for the user" so proposals drain per integration. Repeated mistakes this run and
  the mechanical fix for each: trailer written with the agent's own model name (3x) → keep the
  trailer in `dev/commit-trailer.txt` and brief `git commit -F`; reviewers unable to save
  reports (3x) → the heredoc instruction above; a brief presupposing a pending decision (N2)
  → `brief_lint` consulting `plan_decide.py pending`; merge-report "pending" fields left
  unstaged after publish (2x) → the publish wrapper re-stages its own report; named checks
  raced across three worktrees (every lane reported "possibly raced") → CT-11 lock.

## 4. Reprioritisation

Move up: **CT-11** (check lock; unblocks safe parallel `check`/`check:research`), **CT-02b**
(gate false positives; unblocks mergers), **CT-21** (now), the **D7 spike** (removes the
`mise.dev.toml` hot spot), and the **user-typed to-tickets** (gives `ticket-frontier` real ids).
Keep: w0-doctor-records and w0-session-hooks after w0-doctor. Push back: CT-25 build is done
(the skill exists); its wiring waits on CT-17/19/22 as planned.

## 5. Context: the parent must hand off now

The parent's last turn read 611,587 cached tokens. That is above the team's own thresholds
(fork deny 500K, checkpoint 600K) and 90K below the 700K `autoCompactWindow` it committed in
`.claude/settings.json`; auto-compaction will fire mid-task if nothing is done.

**/clear, not /compact.** planning-with-files 3.24.0 re-fires SessionStart on `clear` and
injects `task_plan.md` head-50 (handoff, Goal, Next Step, Current Phase) and the progress
tail-20 (NEXT bullet), which the team keeps current; the smart view parses the phases. `/compact`
produces a lossy summary, the PreCompact hook cannot inject (R4), and the compacted session
keeps the same dead agent handles. The native pwf feature the directive asks about is exactly
this SessionStart recovery plus `session-catchup.py --metadata` (counts) and `--replay`
(bounded same-project excerpts, on request), plus `plan-attest` to lock the plan before the
reset. There is no pwf feature that "corrects" context; the correction is the handoff block.

**Before /clear (parent, in order):**
1. Wait for the w0-decisions publish to finish (background agents die with the session; a
   merger killed mid-publish is the exact failure the review started from).
2. Rewrite the handoff block and NEXT with the live state: remote tip after the publish;
   w0-doctor at `f1bbc8d` needing focused re-review then merge; deferred hunks (w0-decisions
   mise rows, w0-docs `dev/check.py` manifest rule, D12 retroactive ledger rows, N2 items);
   CT-21 ready to dispatch; pending user items (D47, D48, to-tickets, personal autoCompact).
3. Confirm every review file exists on disk (`phase3/w0/*-review.md`, receipts, merge reports)
   and that nothing is only in an agent's final message.
4. Probe the injection read-only (`claude-hook.sh session-start` with a fresh probe id and
   `CLAUDE_PLUGIN_ROOT` set) and check the first 50 lines carry the handoff.
5. Record the dead-agent list in progress.md (ids and what they were doing) so the next
   session does not resume them.

**After /clear (next session, first turn):** run the doctor session-start surface as soon as
w0-doctor is integrated (`python3 -I dev/doctor/cli.py --surface session-start --format
context`; until then run it from the w0-doctor worktree), `./dev/mise tasks validate`,
`./dev/mise run check`, and dispatch one extractor (Haiku or Sonnet, read-only) with the brief:
"compare the handoff block and NEXT against git (`git log origin..HEAD`, `git status`, worktree
HEADs, lane records, the newest files under `reviews/ccm-20261013/phase3/`) and list every fact
the handoff omits or gets wrong". That is C3's session-review in miniature until CT-23 lands.

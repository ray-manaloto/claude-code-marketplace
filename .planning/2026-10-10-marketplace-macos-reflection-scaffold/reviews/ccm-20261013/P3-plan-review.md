# P3: adversarial review and fix of the rewritten planning records

Written 2026-10-13 by P3 (plan-update team, session `ccm-20261013-check`). Scope: verify P1's
`task_plan.md` and P2's `progress.md`, `findings.md`, `ticket-ledger.md` against the sources, fix
mismatches in place, record the user's K1 §9 answers (D27-D41) and ticket CT-25. `P` = the plan
directory, `RV` = `P/reviews/ccm-20261013`, `W` = the planning-with-files 3.24.0 cache.

No Git state changed: HEAD `9cd396a`, `MERGE_HEAD e12cf04`, 11 staged paths before and after;
the four files show as ` M`, nothing added. Files edited: `P/task_plan.md`, `P/progress.md`,
`P/findings.md`, `P/ticket-ledger.md`; this report. The archive, lane records, retros and K2's
`.claude/skills/ticket-frontier` were not touched. Backups in `RV/plan-backups/` are intact
(SHA-256 prefixes `d14b1286` plan, `f1f52a10` progress, `f047b532` findings, `488991dc` ledger).
Pre-P3 copies of all four files are in the scratchpad (`task_plan.p1.md`, `*.p2.md`).

## 1. Cross-check against the sources

Verified, no change needed (sources: SYNTHESIS §1/§2/§2b/§4/§5/§6/§8, C4, R4, R8, T2, sweep B,
M1, `lanes/*.json`, git):

- Every SHA cited in the four files resolves in this repository (`e12cf04`, `4c1ea6b`, `fa892d2`,
  `05c3dc9`, `f250f75`, `d2a4103`, `848552c`, `0c2748e`, `dec8425`, `c6ff7ef`, `ca60871`,
  `2d1f60e`, `7e22d13`, `447110a`, `e618243`, `361688e`, `e0667ec`, `28fedf1`, `9cd396a`,
  `4870211`, `82c351f`, `ea8c8c9`, `5107322`, `6c09b7f`, `7295463`, `55f3946`, `8f783a0`,
  `93402c0`). `a221b354` is the reviewer agent id, not a commit, as the ledger says.
- Ancestry (`git merge-base --is-ancestor`): `f250f75`, `4c1ea6b`, `fa892d2`, `05c3dc9`,
  `e618243`, `7e22d13` ⊂ `28fedf1`; `361688e`, `55f3946`, `447110a` ⊂ `f250f75`;
  `28fedf1` ⊂ `9cd396a` (one commit ahead); `0c2748e`, `dec8425`, `d0d6d4d` ⊂ `e12cf04`
  (parents `dec8425 d0d6d4d`); `d2a4103`, `848552c` ⊂ `05c3dc9`; `ea8c8c9` ⊂ `7e22d13`;
  `82c351f` ⊂ `e618243`; `8f783a0` ⊂ `361688e`.
- Staged set: 11 paths (`.claude/settings.json`, `lanes/gate-hooks.json`, `retros/gate-hooks.md`,
  four `dev/hooks/*.py`, `dev/test_hooks.py`, `docs/agents/claude-team.md`, `hk.pkl`,
  `mise.dev.toml`), as the handoff and ledger say.
- Lanes table vs `lanes/*.json`: every `base_sha`, branch, status and retro value matches the
  record (allocation-commit corrections `c6ff7ef`, `ca60871`, `2d1f60e` are SYNTHESIS §4 values,
  marked as such); gate-hooks "record says awaiting cold review" is the record's literal status.
- Ticket table vs SYNTHESIS §6 / C4: blocked-by edges and waves match for CT-01..CT-24 and
  CT-02b (CT-21 = fifth wave-1 lane per T2 §e / D24; CT-12/CT-16/CT-24 conditional on D5).
  R8 unit names renumbered to C4 ids correctly (`ct12-lane-lifecycle` → `ct17-lane-lifecycle`,
  `ct14-lane-brief` → `ct19-lane-brief`, `ct13-publish-batch` → `ct18-publish-batch`,
  `ct16-unwired-tests` → `ct12-unwired-tests`).
- Errors table: 15 P1 rows; prevention tickets and detector ids agree with the SYNTHESIS §2b
  class table (A → CT-23/CT-22, D → CT-22/CT-20, E → CT-24, F → CT-19/CT-23/CT-22, H →
  CT-12/CT-21/CT-22, I → CT-16/CT-02b, K → CT-15, L → CT-21).
- Counts: M1 "SAFE WITH CORRECTIONS, 13/13 P1 confirmed" (M1 §Verdict); 27 agents (SYNTHESIS
  §2 "Contradictions resolved"); C4 KEEP 29 / MERGE 16 / DEFER 10 / DROP 8; four Codex briefs.
- Phase 3 steps 1-13 = SYNTHESIS §5; Phase 4 W0-1..W0-7 = C4 §Minimal wave-0 set in the
  §Repair-session safety order (D26); Phase 5 = SYNTHESIS §6 "Workflow from here".
- Context budget numbers (400/500/550/650 K, `autoCompactWindow` 700 K) = C4, as P1 reported.

Mismatches found and fixed (line numbers are the pre-P3 files):

| File:line | Was | Now | Source |
|---|---|---|---|
| task_plan:17-18 | handoff lists D1-D26 only | "D27-D41 ticket-frontier/CT-25 accepted" folded into the same two lines (window unchanged) | user answers to K1 §9 |
| task_plan:24,26 | Goal "file CT-01..CT-24"; C++ rule unreferenced | "CT-01..CT-25"; "(D27/D28)" | K1 §8, user D32/D27/D28 |
| task_plan:50 | "P1 15, P2 25, P3 31" (progress.md said 27 P2 rows) | "SYNTHESIS §1: P1 15, P2 25 after dedup over 27 table rows, P3 31"; names P1/P2/P3, K1/K2 | SYNTHESIS §1 (25) vs §2 table (27 rows incl. P2-10b) |
| task_plan:100 | Phase 6 had no C++-ticket rule | new checkbox: one C++ ticket active alongside wave 1, #21 first; D27 class, D28 split unit | user D27/D28; D5 |
| task_plan:107 | Wave 3 without CT-25 | "; CT-25 ticket-frontier skill once CT-05/15/17/19/22/24 are integrated (D32)" | user D32; K1 §8 |
| task_plan:109 | heavy chain "(D5, D18)" | "(D27/D28) ... (D5, D18)" | user D27/D28 |
| task_plan:135 | CT-12 wave "1 if D5, else 2" | "1 (sixth) if D5 admits, else 2" | SYNTHESIS §6 "1 #6 if admitted, else 2"; ledger row |
| task_plan:145 | CT-22 wave "0 (a), 2 heavy (b)" | "0 (a); 1 heavy slot or 2 (b)" | SYNTHESIS §6 table and C4 row "0 (a) + 1 heavy slot / 2 (b)"; ledger row |
| task_plan:150 | no CT-25 | row CT-25, proposed (D32), blocked by CT-05/15/17/19/22/24, wave 3, unit `ct25-ticket-frontier` (proposal) | K1 §8; user D32/D34 |
| task_plan:152-153 | "Lane units for proposed tickets are the names the allocation commit will use" (reads as a record) | "P1/P3 proposals ... not records: each name is fixed by its allocation commit"; CT-25 outside C4's table | brief task 1; C4 §Reconciled |
| task_plan:175-177 | a06-unit3, codex-session-history, rf-env-scrub "on `28fedf1`" | "published `f250f75`, on `28fedf1`" | records `published: f250f75`; SYNTHESIS §4 "or `f250f75` where earlier" |
| task_plan:187-219 | D1-D26 + D-all | intro names K1 §9; rows D27-D41 "accepted 2026-10-13"; `D12-applied` deviation row; D-all now "D27-D41 accepted; CT-25 added", status "pending user (D1-D26)" | user answers; task 4 |
| task_plan:813-818 | Appendix C lacked K1 and the plan-update reports | added `skills/K1-...md` (CT-25, D27-D41), P1/P2/P3 reports | this review |
| ticket-ledger:3 | "CT-01…CT-24 (+CT-02b)"; one 1,066-char line | "CT-01…CT-25"; wrapped ≤100 | K1 §8; task 5 |
| ticket-ledger:108 | source = SYNTHESIS §6 only; 627-char line | adds "CT-25 from K1 §8 (D32, accepted 2026-10-13)"; wrapped | K1 §8 |
| ticket-ledger:136 | no CT-25 | row CT-25 (blocked; CT-05, CT-15, CT-17, CT-19, CT-22, CT-24; not allocated · wave 3; K2 draft is not a lane output until allocated) | K1 §8; user D32-D34 |
| ticket-ledger:140,164 | 869- and 1,195-char paragraphs | wrapped ≤100 (one 104-char line remains: an unbreakable `~/.local/state/...` path) | task 5 |
| progress:3 | 141-char archive pointer | wrapped to two lines; still resolves to `progress-archive-2026-10-13.md` | task 5 |
| progress (end) | no entry for P3/K1/K2; NEXT lacked D27-D41 and CT-25 | new dated entry (what P3 checked, D27-D41 recorded, CT-25 added, K2 draft uncommitted, archive = `D12-applied`, nothing committed, merge still staged, no `.mode`, no named check); NEXT rewritten in place: D3/D23 now "CT-01…CT-25 + CT-02b", "D27-D41 accepted" | task 3; user answers |
| findings:45,59,88,176 | 101-128-char prose lines | wrapped; `task_plan.md:322` (a pre-rewrite line number) now reads "pre-rewrite line 322, now in its Appendix B" | task 5; P1 §preserved |
| findings (end) | no K1 pointer | bullet: K1 design pointer, D27-D41 location, CT-25 | K1 |

CT-16's blocked-by differs in form only ("D4; after CT-22a" vs "D4, CT-22a (sequential)"); left.

## 2. Injector probes after the fixes (read-only, fresh ids, `CLAUDE_PLUGIN_ROOT=W`, `PLAN_ID` and `PWF_PLAN_ROOT` pinned)

1. SessionStart legacy, `printf '{"session_id":"p3-legacy-1791938159",...,"source":"clear"}' |
   sh W/hooks/claude-hook.sh session-start`: `additionalContext` 5,556 B / 81 lines; plan frame
   `bytes=2913 truncated=true` = 50 lines (title, pins, owner, handoff at ctx line 12, `## Goal`
   26, `## Next Step` 31, `## Current Phase` 35, Phases 0-2); progress frame `bytes=1715` =
   `tail -20` of `progress.md`, whose last 10 lines are the NEXT bullet (`- NEXT` at ctx line 69,
   then the frame end and the findings pointer). The pretool-relevant lines 1-30 of the plan
   carry the handoff, Goal and the whole Next Step (Next Step body ends at line 30).
2. SessionStart `PWF_INJECT=smart` (`p3-smart-1791938165`): 5,600 B / 76 lines; plan frame
   `bytes=2957`: title, `## Goal`, `## Next Step`, `## Current Phase`, `phases: 3/8 complete`,
   the whole `### Phase 3: Repair and publish` body with `**Status:** in_progress`, and
   `## Decisions Made (last 3)` = `D41`, `D12-applied`, `D-all`.
3. PreToolUse legacy (`PWF_SESSION_ID=p3-pretool-... python3 -I W/scripts/inject-plan.py
   --context=pretool`): rc 0, `bytes=2069 truncated=true`; view lines 28-30 are `## Next Step`
   and its two body lines. Smart PreToolUse: `bytes=2957`, same content as probe 2.
4. `sh W/scripts/check-complete.sh` → `Task in progress (3/8 phases complete)`, `1 phase(s)
   still in progress`, `4 phase(s) pending`, rc 0.
5. `sh W/scripts/set-active-plan.sh --list` → `2026-10-10-marketplace-macos-reflection-scaffold
   - 3/8 complete, 1 in_progress, 4 pending`.
6. `sh W/scripts/ledger-summary.sh P` → `entries: 0`, `phases: 3/8 complete`, `in_progress:
   ### Phase 3: Repair and publish`.
7. `phase-status.sh` writes the plan, so it ran on a scratchpad copy of `P/` with
   `PWF_PLAN_ROOT` pointed there: `phase-status.sh 3 in_progress` → `[phase-status] Phase 3 ->
   in_progress`, rc 0, and the copy stayed byte-identical to the real plan (the no-op set
   resolved phase 3 by number through the same `**Status:**` grammar).
8. `P/.mode` does not exist (`ls` ENOENT). The real plan's SHA-256 was unchanged by the probes.

Token counts: `### Phase` 8; `**Status:**` 8 (3 complete, 1 in_progress, 4 pending); CT rows 26
in both tables; decision rows 43 (T-R1/R2, D1-D41, D12-applied, D-all); P1 rows 15; lane rows 10.

## 3. Consistency between files

- `task_plan.md` ticket table ↔ `ticket-ledger.md` CT rows: 26 ids each, identical sets; same
  state/frontier, waves and blocked-by for every row (script split on pipes outside backticks).
- ↔ `lanes/*.json`: the ten lane rows carry the records' `base_sha`, branch, status, retro;
  `ct21-codex-imports` is the only record for a proposed ticket, as both tables say.
- ↔ SYNTHESIS §6: integration orders wave 1 (CT-02b, CT-11, CT-05, CT-15, CT-21), wave 2
  (CT-17, CT-19, CT-18, #95, CT-22b heavy), wave 3 (CT-07, CT-23, CT-06, CT-09 [+CT-12]) and
  wave 4+ match; CT-25 is the one addition (D32).
- `findings.md`: facts and pointers only; no next steps (grep for "next step", "NEXT", "TODO"
  is empty). Its "Verified baseline" section is Codex-era history and was left as written.
- `progress.md`: the P2 entry's claims hold (reports list, 27 agents, 13/13, KEEP/MERGE/DEFER/
  DROP, four briefs, 454 files / 11.8 MB, nothing committed, merge staged); the new P3 entry
  adds P1/P2/P3/K1/K2 outputs. The archive pointer on lines 3-4 resolves
  (`P/progress-archive-2026-10-13.md`, 3,046 lines, untracked; P2 proved the split lossless).

## 4. Append-only rule (task 4)

`.claude/rules/planning-records.md:9` (paths `.planning/**`): "`progress.md` is append-only:
add dated entries below the last one and leave earlier lines as written." `.planning/AGENTS.md`
repeats "`progress.md` (append-only)". P2's archive moved lines 1-3026 out of the file before
D12 was approved and before runbook step 9 amends the rule. Recorded as decision row
`D12-applied` in `task_plan.md` ("applied 2026-10-13 ahead of D12 approval against the
append-only rule ...; reversible from `reviews/ccm-20261013/plan-backups/`") and in the P3
progress entry. The "NEXT rewritten in place" convention is the second standing deviation (R4
P3 "pwf"); kept per the brief, with `## Next Step` carrying the same text.

## 5. Line length (task 5)

No repository rule sets a line width: `.claude/rules/planning-records.md`, `.planning/AGENTS.md`,
`docs/agents/*.md`, `CODING_STANDARDS.md`, `GLOSSARY.md` and `.claude/agents/*.md` contain no
"100" / line-length / em-dash rule; the ≤100 figure is the P1 brief's. Applied as a convention
to prose only (character counts, not the byte counts P1 reported): `progress.md` 0 over;
`task_plan.md` 3 over, all preserved Appendix B prose (lines 575, 586, 588: 109/103/161, as in
the original); `findings.md` 5 over, all unbreakable paths (three `~/.codex/research-coverage/...`
manifest paths, two quoted `/var/folders/...` and `~/.local/state/...` paths inside the sweep B
notice); `ticket-ledger.md` 1 over (a 104-char backticked state-dir path). Pipe-table rows cannot
wrap in Markdown and are exempt: 157 in `task_plan.md` (Tickets, Lanes, Decisions, Errors,
frontier and the preserved unit tables), 138 in `ticket-ledger.md`. Em-dashes: no rule found;
P2's files keep "—" (ledger empty cells, quoted text); P1's plan has none.

## 6. Residual issues (not fixed, for the parent)

- `.mode`: SYNTHESIS §5 step 9 says "write `P/.mode` = `inject-smart`"; R4 checklist step 6
  calls it optional ("so the smart view does not depend on each user's env; commit it") and C4
  carries detector `I.mode-absent`. The brief's reading (do not write it) is honoured: nothing
  written; Phase 3 step 9 still lists it, so the parent decides at step 9 with D8/D12.
- SYNTHESIS §1 says "P2 25" while its §2 table has 27 P2 rows (P2-10b and P2-26 added in
  revision 2); not a planning file, left; both files now cite both numbers.
- K2 has written `P/frontier.toml` (untracked, inside the plan directory) and
  `.claude/skills/ticket-frontier/` during this review; neither is a lane output, the ledger's
  CT-25 row says so; the parent decides whether `frontier.toml` belongs beside the plan files or
  under CT-25's lane.
- The parallel-write guard (`ip.py:1280-1313`) will print one advisory on the next real fire
  because the `- [x]`/`**Status:** complete` counts changed since P1's probes; expected (R4).
- `docs/agents/claude-team.md:81` "Up to four offline lanes" and D30 (writer lanes only, hard
  cap 8 live agents) are compatible but the doc does not yet say the cap; a W0-7 / CT-25 hunk.
- Not re-verified: settings `env` pins reaching hook processes (R4 §Could not verify); the
  stale-worktree injection case (R4 proved it; probes ran from the root).

## 7. `git add` list for the Phase 3 implementer (do not run now)

Runbook step 9 (pwf migration commit, after D8 and D12; replaces step 9's `git mv` with adds):

```
git add .planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md \
        .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md \
        .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress-archive-2026-10-13.md \
        .planning/2026-10-10-marketplace-macos-reflection-scaffold/findings.md \
        .planning/2026-10-10-marketplace-macos-reflection-scaffold/ticket-ledger.md
```

Runbook step 10 (persist the review; `settings.json.before-ct02` and `codex-briefs/digests/`
never staged):

```
git add .planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/P1-plan-rewrite-report.md \
        .planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/P2-records-update-report.md \
        .planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/P3-plan-review.md \
        .planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/plan-backups
```

`plan-backups/` (four pre-rewrite copies, ≈300 KB) is the reversibility receipt for
`D12-applied`; drop it from the add only if the user prefers git history as the receipt.

# P1: task_plan.md rewrite for the planning-with-files 3.24.0 injector

Written 2026-10-13 by P1 (plan-update team, session `ccm-20261013-check`). Files written:
`P/task_plan.md` (rewritten in place) and this report; backup of the pre-rewrite plan at
`P/reviews/ccm-20261013/plan-backups/task_plan.pre-rewrite-20261013.md` (SHA-256
`d14b1286cdf02377a4b99d7d286d25909fa61814e8941fc970def9cb808d4fc1`, identical to the file it
copied). No git state changed: HEAD `9cd396a`, `MERGE_HEAD e12cf04`, 15 staged/modified entries
before and after; `task_plan.md` shows as ` M` only. `progress.md`, `findings.md` and
`ticket-ledger.md` were not touched (P2 owns them). `W` = the 3.24.0 plugin cache; `P` = the plan
directory.

## What changed

New file: 831 lines, 68,517 B (old: 566 lines, 47 KB). Section map (line numbers in the new file):

| Lines | Section | Purpose |
|---|---|---|
| 1-7 | title, PLAN_ID, `PWF_PLAN_ROOT`, owner, pin instruction | `# ` line 1 is the smart-view title (`ip.py:706`) |
| 9-21 | `## Session handoff (2026-10-13)` | 13 lines, inside the 30-line PreToolUse window |
| 23-26 | `## Goal` | keep section (`ip.py:694`) |
| 28-30 | `## Next Step` | keep section (`ip.py:696`); ends exactly at line 30 |
| 32-33 | `## Current Phase` | keep section (`ip.py:698`) |
| 35-115 | `## Phases`, `### Phase 0`..`### Phase 7` | 8 phases; status tokens `**Status:** complete|in_progress|pending` (`ip.py:720-723`, `check-complete.sh:98-100`) |
| 54-76 | `### Phase 3: Repair and publish` (`in_progress`) | runbook steps 1-13 as checkboxes, each naming its decision |
| 117-165 | `## Tickets` | CT-01..CT-24 + CT-02b (25 rows) and the open GitHub frontier grouped (6 rows) |
| 167-183 | `## Lanes` | projection of the ten `lanes/*.json` records |
| 185-219 | `## Decisions Made` | pipe table, 28 rows: takeover rounds pointer, D1-D26, a `D-all` closing row |
| 221-242 | `## Errors Encountered` | 15 rows, P1-1..P1-15: id, error, prevention ticket, C3 detector id |
| 244-271 | `## Workflow` | D2 §4 stage script (12 user-typed items), lane protocol pointer, context budget |
| 273-332 | Appendix A: Claude takeover (2026-10-13) | takeover narrative and the accepted conventions |
| 334-810 | Appendix B: accepted contracts | `## Objective`, `## Confirmed completion workflow`, `## Small units`, `## Full-baseline spec workflow`, `## Acceptance required before completion`, `## Admission and later work`, `## Evidence` |
| 812-831 | Appendix C: references | reports, records, authority docs, injector paths and windows |

Heading names were adapted to what `inject-plan.py` parses: `## Decisions Made` (not
"Decisions") because `smart_plan_extract` switches to the decisions table only on that prefix
(`ip.py:703`), and `## Errors Encountered` because `commands/status.md:13` counts that table. The
brief's "Decisions"/"Errors" sections are those two.

Facts and sources (every SHA and number comes from these reports):

- Checkout state (HEAD `9cd396a`, `MERGE_HEAD e12cf04`, remote `28fedf1`, 11 staged files,
  settings split pending): SYNTHESIS §1, P1-1, P1-2, §5 preconditions; verified by `git rev-parse`.
- Phase 0/1 facts (`d2a4103`, `848552c`, `05c3dc9`, `0c2748e`, `dec8425`, re-review PASS 21:04Z,
  seven integrated lanes on `28fedf1`): `lanes/*.json`, SYNTHESIS P1-4, §4 row "all integrated
  lane records".
- Phase 3 steps and decision bindings: SYNTHESIS §5 steps 1-13 (step 4 is "none" and kept as a
  one-line note). Step 9's "this plan shape (done 2026-10-13 ahead of approval)" is this rewrite.
- Phase 4 W0-1..W0-7: C4 §Minimal wave-0 set; order and timing: SYNTHESIS §5 safety table, D26.
- Phase 5 user-typed stages: SYNTHESIS §6 "Workflow from here"; D2 §4.
- Phase 6/7 waves and integration order: SYNTHESIS §6 "Waves"; R8 §Waves; T2 §e (CT-21 fifth
  lane, D24). Heavy chain and first C++ ticket: D5 (`#21 > #20 > #17 > #16 > L1 #96`), ticket
  ledger rows #21 "10: Relocated CMake Config consumers (Task 18)", heavy 1; frontier READY #16,
  #17, #20, #21, #96; blocked #18, #19, #22, #23; `docs/accepted-decisions.md` lines 8-9 for the
  C++26 P2996 core and incremental migration. The "always one C++ ticket active" rule is the
  brief's instruction, recorded as a Phase 7 checkbox.
- Tickets table: C4 §Reconciled ticket table (binding per SYNTHESIS §2b) and SYNTHESIS §6 table;
  states for CT-01..CT-04 from the lane records plus SYNTHESIS P1-5 (CT-01 AC2 open) and §4
  ("published `28fedf1`"); CT-21 state from `lanes/ct21-codex-imports.json` and T2 §c/§d.
- Lane unit names for proposed tickets: R8's wave units renumbered to C4's ids (R8 `ct12-lane-
  lifecycle` = CT-17, `ct14-lane-brief` = CT-19, `ct13-publish-batch` = CT-18, `ct16-unwired-
  tests` = CT-12; R8 `ct02b`, `ct11`, `ct05`, `ct15`, `ct07`, `ct06`, `ct09` keep their names);
  the remaining names (`ct08-baseline-v2`, `ct10-codex-status`, `ct13-ask-mod`,
  `ct14-plugin-guidance`, `ct16-settings-check`, `ct20-session-review`, `ct22-doctor`,
  `ct23-session-hooks`, `ct24-decisions`) are P1 proposals, stated as such under the table. Only
  `ct21-codex-imports` has a lane record.
- GitHub frontier: `ticket-ledger.md` rows #12-#108; closure prerequisites: sweep B §1 (#62-#78)
  and §2 (#101 STOPPED/NOT_COMPLETED, budgets 3/3); C1 integration `4c1ea6b`: SYNTHESIS §4.
- Lanes table: `lanes/*.json` fields read on 2026-10-13; allocation-commit corrections
  (`c6ff7ef`, `ca60871`, `2d1f60e`) and the a06-unit3 gate rc 2: SYNTHESIS §4 and P1-13.
- Decisions D1-D26 with defaults: SYNTHESIS §8 (one line each; status "pending user").
- Errors rows: SYNTHESIS §2 P1 table (what), §2b class table (prevention ticket, detector ids).
- Workflow: D2 §4 script verbatim in order; lane protocol: `docs/agents/claude-team.md`, R8
  §Integration protocol, SYNTHESIS §6 per-lane paragraph (never `isolation: worktree`).
- Context budget: C4 is binding (SYNTHESIS §2b class A row, C4 §Required changes lines 381-382):
  warn 400 K, fork_deny 500 K, checkpoint 550 K, hard 650 K, `autoCompactWindow` 700 K. C3's
  draft used checkpoint 600 K / no fork at 650 K / clear 800 K (`C3-detection-design.md:124-125,
  1149`); the plan carries C4's numbers and this report records the difference.
- Appendix A corrections to the old takeover text: stop causes (nine dead children, SYNTHESIS
  P2-10 and §4 sweep C sentence), heartbeat and packet supersession (P2-11, sweep B §4), the
  `2a14`/`c658` snapshot sentence (T2 §c replacement for old lines 11-12), the invocation-mode
  bullet rewritten to the verified facts (P1-7; D15 is the matching docs edit, still pending),
  the #91 label state (P1-9), ticket 30 of the dynamic-agents graph (P2-25).

## What was preserved and where it moved

- `## Objective`, `## Confirmed completion workflow`, `## Small units` (old lines 98-230):
  Appendix B, new lines 340-473, byte-identical (`diff` shows only a trailing blank line).
- `## Full-baseline spec workflow` (old 231-330): new lines 474-575, identical except one
  addition at the absolute `2a14` link (old line 322, new 564-566): "(imported by CT-21; the link
  becomes `../../docs/agents/automation-amendment-review.md` once it integrates)", per T2 §c.
- `## Acceptance required before completion`, `## Admission and later work`, `## Evidence`
  (old 332-566): new lines 576-810, byte-identical.
- "Claude takeover (2026-10-13)" conventions (old 32-77): Appendix A, lines 273-332, with the
  corrections listed above; the five unchanged bullets are verbatim.
- The old lane table (old 79-92, stale on every row per R4 P2-5) is replaced by `## Lanes`
  (regenerated from the records); Appendix A says so and points at the backup.
- The old prose handoff block (old 14-30) is replaced by the new handoff, `## Next Step` and
  `## Current Phase`; its still-true facts (integrated lanes, pending decisions, resume reading)
  are in lines 9-21 and Phase 1.
- Old lines 3-12 (PLAN_ID, owner, pin prose, the `2a14` "do not reset" sentence): lines 1-7 and
  Appendix A's snapshot sentence ("Do not reset or archive them" kept).

## Line counts and constraints

- 831 lines, 68,517 B; first 50 lines end inside Phase 2 (line 50 is Phase 2's first bullet).
- No em-dash in the file (`grep -c '—'` = 0; the old file also had none; en-dashes in preserved
  text are untouched).
- Lines over 100 characters: 0 in the new prose (lines 1-339 and Appendix C); in the preserved
  appendix, three prose lines of the old "Full-baseline" narrative (new 553, 564, 566: 109, 103
  and 161 chars, as in the original) and 149 pipe-table rows (tables cannot wrap: the Tickets,
  Lanes, Decisions, Errors and frontier tables plus the preserved unit tables). Reported as the
  one exception to the ≤100 rule.
- File size vs the injector: `PLAN_LIMIT` is 4 MiB (`ip.py:90`); `PLAN_VIEW_LIMIT` 64 KiB
  (`ip.py:94`) bounds only the extracted view (2-3 KB here), so the 68.5 KB file is within
  limits. R4's "well under 64 KiB" guidance referred to the view limit; the probes below confirm
  no truncation beyond the semantic `truncated=true` (line count > head).

## Parse evidence (read-only probes, throw-away session ids, 2026-10-13)

The hook wrapper exits silently when `CLAUDE_PLUGIN_ROOT` is unset (`claude-hook.sh` trace:
`PLUGIN_ROOT=` then `exit 0`); the host sets it for real fires, so the probes export
`CLAUDE_PLUGIN_ROOT=W`. The Python twin called directly (`--claude-event=session-start`) gives the
same bytes without it.

1. SessionStart, legacy (`printf '{"session_id":"p1-final-<ts>","cwd":"<repo>",
   "hook_event_name":"SessionStart","source":"clear"}' | sh W/hooks/claude-hook.sh session-start`):
   `additionalContext` 5,473 B / 82 lines: plan frame `bytes=2863 truncated=true` = lines 1-50 of
   the plan (title, pins, owner, the 13-line handoff, Goal, Next Step, Current Phase, Phase 0,
   Phase 1, the Phase 2 heading and first bullet), progress frame `bytes=1682` (P2's new
   `progress.md`, tail 20), findings pointer. Decoded frame saved at
   `<scratchpad>/probe-decoded.txt`; the first 50 lines are quoted in §"First 50 lines" below.
2. SessionStart, `PWF_INJECT=smart` (same payload, new id): 5,535 B / 77 lines; plan frame
   `bytes=2925`: title, `## Goal`, `## Next Step`, `## Current Phase`, `phases: 3/8 complete`,
   the whole `### Phase 3` body (13 checkboxes, `**Status:** in_progress`), and
   `## Decisions Made (last 3)` = rows D25, D26, D-all. Exactly the shape R4's fixture predicted.
3. PreToolUse legacy 30-line view (`PWF_SESSION_ID=... python3 -I W/scripts/inject-plan.py
   --context=pretool`): `bytes=2019 truncated=true`; lines 28-30 of the view are `## Next Step`
   and its two body lines, so a subagent's view carries the handoff, Goal and Next Step. Smart
   PreToolUse view: `bytes=2925`, same content as probe 2.
4. `sh W/scripts/check-complete.sh` → `Task in progress (3/8 phases complete)`, `1 phase(s)
   still in progress`, `4 phase(s) pending`, rc 0 (before the rewrite it exited silently with
   `TOTAL=0`).
5. `sh W/scripts/set-active-plan.sh --list` → `2026-10-10-marketplace-macos-reflection-scaffold -
   3/8 complete, 1 in_progress, 4 pending`.
6. `sh W/scripts/ledger-summary.sh P` → `entries: 0`, `phases: 3/8 complete`, `in_progress: ###
   Phase 3: Repair and publish`.
7. `phase-status.sh` was not run (it writes the plan: usage `<phase-number>
   <pending|in_progress|complete>`); its token grammar is the one the file uses, so it will
   resolve phases 0-7 by number once a status change is wanted.

Byte counts of the token checks on the file: `### Phase` 8; `**Status:** complete` 3;
`**Status:** in_progress` 1; `**Status:** pending` 4; CT rows 25; decision rows 27 (+ header);
P1 rows 15; lane rows 10.

### First 50 lines as the next session sees them (legacy frame, verbatim)

```
# Marketplace onboarding and C++ foundation

PLAN_ID `2026-10-10-marketplace-macos-reflection-scaffold`; `PWF_PLAN_ROOT` (absolute):
`/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`. Owner: session
`ccm-20261013-check` (`b74a0bf1-dd98-44d5-8122-e47e12ad4fd2`) owns this plan and the branch
`codex/marketplace-native-onboarding` since 2026-10-13; dead session `ccm-20261013` (`464a2816`)
is closed. Pin `PWF_PLAN_ROOT` and `PLAN_ID` in the host env (a Bash prefix never reaches hooks).

## Session handoff (2026-10-13)
- Checkout: HEAD `9cd396a`; `MERGE_HEAD e12cf04` = staged `--no-commit` merge of
  `claude/gate-hooks-wiring` (CT-02, 11 staged files); remote tip `28fedf1` (`9cd396a` unpushed).
- Inside the merge the settings split is pending (D4): staged `.claude/settings.json` carries
  personal keys. No commit, abort, add or push until the user decides D1 and D4.
- Snapshot `imports/codex-worktrees-20261013/` (index only, D24); review `reviews/ccm-20261013/`
  (SYNTHESIS.md ranks it; R1-R8, C1-C4, T1/T2, sweeps A/B/C).
- Next action: SYNTHESIS §5 step 1 after the user approves D1-D26; read-only on git until then.
  Live PreToolUse gate denies text containing `git merge` or `git push` (until CT-02b).
- Pending user: D1-D26 defaults (Decisions Made); typing `/mattpocock-skills:to-tickets`;
  flipping personal `autoCompactEnabled` (D21).
- Resume order: `reviews/ccm-20261013/SYNTHESIS.md` (§1, §5) > `lanes/*.json` >
  `retros/ccm-20261013-session.md`; then `./dev/mise tasks validate`, `./dev/mise run check`.

## Goal
Finish the gate-hooks merge, publish a clean tip through A09, file CT-01..CT-24 (+CT-02b) as
GitHub tickets under the takeover spec, run the lane waves behind the retro gate, and keep one
C++26 P2996 ticket active until the native research core replaces the Python core.

## Next Step
Obtain the user's approval of D1-D26 (SYNTHESIS §8 defaults), then run SYNTHESIS §5 step 1
(snapshot `.claude/settings.local.json` and `git diff --cached` to the scratchpad).

## Current Phase
Phase 3: Repair and publish (SYNTHESIS §5 runbook steps 1-13)

## Phases

### Phase 0: Takeover and M0
- [x] Codex threads stopped; sole writer transferred at HEAD `d2a4103` (remote `848552c`)
- [x] M0 merged `codex/marketplace-remaining-work`; cold review PASS; published `05c3dc9`
- **Status:** complete

### Phase 1: Wave-0 lanes CT-01..CT-04 and imports
- [x] Integrated, `retro: passed`, on origin `28fedf1`: a06-unit3 #69, codex-session-history,
  rf-env-scrub, team CT-03, retro-gate CT-01, nav CT-04, c1-catalog-promotion #94
- [x] gate-hooks CT-02 built (`0c2748e`+`dec8425`, re-review PASS 21:04Z); merge staged
  (`e12cf04`), not committed: finishes in Phase 3
- **Status:** complete

### Phase 2: Session review ccm-20261013
- [x] Ten cold reviews, meta-review, prevention team, import lane design, Codex sweeps:
```

## Not fitted, not verified, or left for the parent

- The plan guard (`ip.py:1280-1313`) will print one advisory on the next fire because the
  `- [x]` and `**Status:** complete` counts changed from 0; expected, per R4.
- `P/.mode` = `inject-smart` was not written (runbook step 9, after D8/D12); without it or
  `PWF_INJECT=smart` in the host env the SessionStart frame is the legacy head-50 (probe 1),
  which also stands alone.
- `phase-status.sh` and `ledger-append.sh` were not run (they write).
- `commands/status.md` (`/status`) was not invoked; it reads `## Current Phase`, the phase
  tokens and the `## Errors Encountered` rows, all present.
- The injected progress frame (1,682 B, P2's file) was not reviewed by P1.
- The Tickets table's lane-unit names for not-yet-allocated tickets are proposals (see above);
  the allocation commit fixes them. GitHub cells read "pending /to-tickets" throughout.
- Line-length rule: 149 table rows and three preserved prose lines exceed 100 chars.
- The old plan's absolute `2a14` link (now line 564) still dangles until CT-21 integrates; T2's
  note is attached rather than rewriting the link early.
- Not verified: whether settings `env` pins reach hook processes (R4 §Could not verify); the
  probe used the root cwd, so the stale-worktree case was not re-probed (R4 proved it).
- Appendix A changes the invocation-mode bullet's wording from "under the user's standing
  authorization" to the verified facts (SYNTHESIS P1-7); the matching `docs/agents` rewrites
  are D15 and remain pending the user.

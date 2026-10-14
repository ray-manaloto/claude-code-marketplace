# Marketplace onboarding and C++ foundation

PLAN_ID `2026-10-10-marketplace-macos-reflection-scaffold`; `PWF_PLAN_ROOT` (absolute):
`/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`. Owner: session
`ccm-20261013-check` (`b74a0bf1-dd98-44d5-8122-e47e12ad4fd2`) owns this plan and the branch
`codex/marketplace-native-onboarding` since 2026-10-13; dead session `ccm-20261013` (`464a2816`)
is closed. Pin `PWF_PLAN_ROOT` and `PLAN_ID` in the host env (a Bash prefix never reaches hooks).

## Session handoff (2026-10-13)
- Checkout: HEAD `d420a7e` = remote (second A09 publish, group 3B, 95 paths, on `0a68dce`;
  CI `38504716758` success); no `MERGE_HEAD`; only these post-publish record lines are unstaged.
- Settings split committed (D4/D21): project `.claude/settings.json` holds `$schema`, hooks, four
  workflow plugins + marketplaces, autoCompact keys, `env.PLAN_ID`; personal keys stay local.
- Snapshot `imports/codex-worktrees-20261013/` (index only, D24); review `reviews/ccm-20261013/`
  (SYNTHESIS.md ranks it; R1-R8, C1-C4, T1/T2, sweeps A/B/C).
- Next action: group 4, wave-0 prevention W0-1..W0-7 (C4 safety order) as lanes with Fable
  review; then the CT-21 import lane. Live PreToolUse gate denies `git merge`/`git push` text.
- Pending user: none of D1-D45 (approved; hunk 2 applied 2026-10-13); typing
  `/mattpocock-skills:setup-matt-pocock-skills` and `/to-tickets`; personal autoCompact (D21).
- Resume order: `reviews/ccm-20261013/SYNTHESIS.md` (§1, §5) > `lanes/*.json` >
  `retros/ccm-20261013-session.md`; then `./dev/mise tasks validate`, `./dev/mise run check`.

## Goal
Finish the gate-hooks merge, publish a clean tip through A09, file CT-01..CT-25 (+CT-02b) as
GitHub tickets under the takeover spec, run the lane waves behind the retro gate, and keep one
C++26 P2996 ticket active (D27/D28) until the native research core replaces the Python core.

## Next Step
Group 4: wave-0 prevention W0-1..W0-7 (C4 safety order) as lanes with Fable review; then the CT-21
import lane; then the user types `/mattpocock-skills:setup-matt-pocock-skills` and `/to-tickets`.

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
  `reviews/ccm-20261013/` (SYNTHESIS §1: P1 15, P2 25 after dedup over 27 table rows,
  P3 31); retro `retros/ccm-20261013-session.md`; plan-update P1/P2/P3 and skill K1/K2
- **Status:** complete

### Phase 3: Repair and publish
Serial, parent only, each step after the decision it names; rcs recorded in progress.md.
- [x] 1 Snapshot `settings.local.json` and `git diff --cached`; keep `settings.json.before-ct02`
- [x] 2 Settings split per R5 §B; key-set assertions; `git add .claude/settings.json` (D4)
- [x] 3 Record fixes inside the merge: `retros/gate-hooks.md`, `lanes/gate-hooks.json`
  (status integrated, retro passed in one edit); `retro:gate -- gate-hooks` rc 0
- [x] 4 CT-02b minimum before commit: none (a fix inside the merge needs the abort path)
- [x] 5 Gates rc 0: tasks validate, check, baseline 19/19, test:hooks (13), hk validate 2.6.0
  and 2.5.0, retro:gate, check:research, `git diff --cached --check`
- [x] 6 Commit the merge (done as `760b154`, parents `9cd396a 697e1da`; declares the `test:hooks` hunk and the
  settings composition); `MERGE_HEAD` gone; `stop_gate.py` silent (D1)
- [x] 7 `git mv retros/a06-classification-methods.md retros/a06-unit3.md`; SYNTHESIS §4 record
  corrections outside the merge; doc rewrites (D15); `.agent/` in `.git/info/exclude` (D8)
  (group 3A: a06 as a copy alias; residual §4 rows in I3 report §7 go to W0-7 and CT-21)
- [x] 8 A09 publish of steps 6-7 only, before any `hooks:install` (D2); record the remote SHA
  (group 2: `0a68dce` carried step 6 and the session retro; step 7 rides the second publish)
- [ ] 9 pwf migration: this plan shape (done 2026-10-13 ahead of approval), pins in settings
  `env`, `progress.md` archive, `.mode` = `inject-smart`, planning-records rule (D8, D12)
  (open: no `.mode` written; the rest is in the group-3B set)
- [x] 10 Persist the review; `retro:gate -- ccm-20261013-session`; second A09 publish (D13)
  (group 3B: published `d420a7e`)
- [ ] 11 Spec and tickets: `issue:create-*`, edges, `ready-for-agent` (D3, D23; Phase 5)
- [ ] 12 On the user's word: #91 relabel, draft PR to `main`, worktree cleanup (D9, D20)
- [ ] 13 Handoff: rewrite Next Step and Current Phase; `session-catchup.py --metadata`;
  `plan-doctor.sh` PASS/PASS; then `/clear` is safe
- **Status:** in_progress

### Phase 4: Wave 0 prevention (C4 order, D26)
- [ ] W0-1 settings keys: `autoCompactEnabled: true`, `autoCompactWindow: 700000`,
  `env.PLAN_ID`; local `PWF_PLAN_ROOT`, `PWF_INJECT=smart`, `PWF_TRUSTED_PYTHON` (D21)
- [ ] W0-2 fixtures: usage curve, rejected command, staged records, 113-command corpus
- [ ] W0-3 `dev/context_budget.py`, `dev/hooks/agent_gate.py`, `dev/hooks/prompt_hook.py`
- [ ] W0-4 doctor slice CT-22a (`dev/doctor/`, surfaces session-start, check, pre-commit)
- [ ] W0-5 hk `pre-commit` `records` step = `doctor --surface pre-commit`
- [ ] W0-6 `decisions.jsonl` seeded + `dev/plan_decide.py` minimal (CT-24 seed)
- [ ] W0-7 docs: claude-team.md (`--no-ff`, never `--no-commit`; context budget; restart
  rule; two Stop gates), D15 rewrites, `.claude/AGENTS.md` key list, secrets line (N1);
  residual SYNTHESIS §4 rows (I3 review P3-5): `ticket-retro.md:4-8` D15 rewrite, `claude-team.md`
  merge rule and hooks caveats, `.claude/AGENTS.md` marketplaces line, `issue-tracker.md`
  `issue:*` mapping, `skill-invocations.md:20`, `spec.md:61,65`, `checkout_transfer.py:17`;
  the absolute `2a14` paths in `claude-takeover.md:26` and `codex-task-orchestration.md:6` go to CT-21
- Lanes (allocated 2026-10-14, commit `plan: allocate wave-0 prevention lanes`; records `lanes/w0-*.json`,
  briefs `reviews/ccm-20261013/phase3/w0/`, report `phase3/W0-allocation-report.md`):
  - [ ] w0-doctor (CT-22a part 1: W0-1 test, W0-4 core, W0-5, doctor fixtures): allocated, cut
  - [ ] w0-decisions (CT-24 seed: W0-6): allocated, cut
  - [ ] w0-docs (W0-7; CT-02b and CT-23 doc slices): allocated, cut
  - [ ] w0-doctor-records (CT-22a part 2: lanes.py, agents.py): allocated, sequenced after w0-doctor
  - [ ] w0-session-hooks (CT-23 seeds: W0-3, hooks fixtures + corpus): allocated, sequenced, integrates last
  W0-1 keys are already in `.claude/settings.json` (merge `760b154`); local pins stay a parent/user
  step. The W0-7 `.git/info/exclude` lines already exist.
- **Status:** in_progress (lanes allocated; none dispatched)

### Phase 5: Tickets publication and /to-tickets (user-typed stages)
- [ ] `/mattpocock-skills:setup-matt-pocock-skills` in a fresh session (seed drift, P2-21)
- [ ] `/mattpocock-skills:retro <dead-session transcript>`; apply through one retro-writer lane
- [ ] "publish spec" from `proposals/claude-takeover-spec/spec.md` (`issue:create-*`)
- [ ] `/mattpocock-skills:to-tickets #<spec>`; approve C4's CT-01..CT-24 (+CT-02b) (D3, D23)
- [ ] "publish tickets": blockers first, edge graph, `issue:new-edges-audit`, `ready-for-agent`
- [ ] `ledger:sync` by hand; `skill-invocations.md` row per typed stage
- **Status:** pending

### Phase 6: Wave 1 lanes
- [ ] CT-02b gate follow-up (int. 1), CT-11 check lock (2), CT-05 ledger (3), CT-15 plan
  records (4), CT-21 Codex imports (5, D24); CT-12, CT-16, CT-24 only if D5 admits them
- [ ] One C++ ticket active alongside (#21 first; D27 class = `frontier.toml` include
  list; D28 offline split unit fills the cxx slot when no heavy run is admitted)
- [ ] per lane: allocation commit, `.claude/worktrees/<unit>`, `implementer` with `tdd`,
  cold `reviewer`, `retro-writer` until `retro:gate` rc 0, `--no-ff` merge, A09 publish
- **Status:** pending

### Phase 7: Wave 2+ incl. heavy chain and C++26 core
- [ ] Wave 2: CT-17, CT-19, CT-18, C3 #95 offline, CT-22b in the heavy slot
- [ ] Wave 3: CT-07, CT-23, CT-06, CT-09 (CT-12 here if not in wave 1); CT-25
  ticket-frontier skill once CT-05/15/17/19/22/24 are integrated (D32)
- [ ] Wave 4+: CT-10, CT-20, CT-08, C2 #98, CT-05/CT-21 split units, `<spec>-review-fixes`
- [ ] Heavy chain, one C++ ticket always active (D27/D28), each run confirmed (D5, D18): #21
  Relocated CMake Config consumers, then #20, #17, #16, L1 #96; frontier READY now: #16,
  #17, #20, #21, #96; blocked native chain #18, #19, #22, #23 (foundation acceptance)
- [ ] `/mattpocock-skills:wayfinder "C++26 P2996 research core"` in its own session
- [ ] CLOSE operations between waves (#12, #24, #25, #62-#78, #90, #92, #93, #94, #97; T4
  #101 only under D25); end-of-spec `code-review` from `start_sha` (D10)
- **Status:** pending

## Tickets

Takeover spec "Claude team takeover and self-improving workflow"
(`proposals/claude-takeover-spec/`).
No CT issue exists on GitHub: every GitHub cell reads "pending /to-tickets" (Phase 5). States:
built, integrated, published (on origin `28fedf1`), proposed. Binding table: C4 §Reconciled.

| Ticket | Title | State | Blocked by | Wave | Lane unit | GitHub |
|---|---|---|---|---|---|---|
| CT-01 | Retro gate task | published (AC2 open, test unwired) | none | done | retro-gate | pending /to-tickets |
| CT-02 | Hook wiring for the retro gate | built, re-review PASS, mid-merge | CT-01 | runbook | gate-hooks | pending /to-tickets |
| CT-02b | Gate follow-up: token-anchored verbs, heredoc strip, deadline deny, corpus, `hooks_install.py` guard | proposed | CT-02 | 1 (int. 1) | ct02b-gate-followup | pending /to-tickets |
| CT-03 | Team roles, rules, vocabulary | published | none | done | team | pending /to-tickets |
| CT-04 | Guidance hierarchy | published | none | done | nav | pending /to-tickets |
| CT-05 | Lane-record validator (`lane:set`, `lane:validate`), ledger generator | proposed | none | 1 (int. 3) | ct05-ledger | pending /to-tickets |
| CT-06 | `/lane-retro <unit>` | proposed | CT-01, CT-03, CT-19 | 3 | ct06-lane-retro | pending /to-tickets |
| CT-07 | Codex compatibility (roles, config, mirror test) | proposed | CT-02, CT-03 | 3 | ct07-codex-compat | pending /to-tickets |
| CT-08 | Baseline transition v2 (`.gitignore`, `.agent/`) | proposed | user admission (D6) | 4 | ct08-baseline-v2 | pending /to-tickets |
| CT-09 | Tool adoption decision table | proposed | none | 3 | ct09-tool-evaluation | pending /to-tickets |
| CT-10 | codex-session-history coverage, `codex_status.py`, `codex:supersede` | proposed | none | 4 | ct10-codex-status | pending /to-tickets |
| CT-11 | Serialize named checks (lock) + receipt line | proposed | none | 1 (int. 2) | ct11-check-lock | pending /to-tickets |
| CT-12 | Wire every development test (`test:retro-gate`, unwired-test rule) | proposed | CT-22a | 1 (sixth) if D5 admits, else 2 | ct12-unwired-tests | pending /to-tickets |
| CT-13 | Grilling-question mod (AskUserQuestion) | proposed | D14 | user-typed | ct13-ask-mod | pending /to-tickets |
| CT-14 | `plugins/aggregated-research` guidance + `CLAUDE.md` importer | proposed | none | 3/4 | ct14-plugin-guidance | pending /to-tickets |
| CT-15 | Planning-file shape, `plan:log`, `plan:handoff`, `check:planning` | proposed | none | 1 (int. 4) | ct15-plan-records | pending /to-tickets |
| CT-16 | Settings composition check (`dev/doctor/settings.py` rule) | proposed | D4; after CT-22a | 1 (sixth) or 2 | ct16-settings-check | pending /to-tickets |
| CT-17 | Lane lifecycle: `lane:allocate`, `lane:integrate`, `session:status`, stop-gate extensions | proposed | CT-01, CT-02, CT-05, CT-11, CT-22a, CT-24 | 2 (int. 1) | ct17-lane-lifecycle | pending /to-tickets |
| CT-18 | A09 batch publish wrapper (refuses `MERGE_HEAD`) | proposed | CT-02, CT-22a | 2 (int. 3) | ct18-publish-batch | pending /to-tickets |
| CT-19 | Slotted briefs (`lane:brief`), agent constants, SubagentStop receipt journal | proposed | CT-02, CT-03, CT-05 | 2 (int. 2) | ct19-lane-brief | pending /to-tickets |
| CT-20 | `agent-session-history` skill, `/session-review`, transcript detectors | proposed | CT-07, CT-10, CT-22 | 4 | ct20-session-review | pending /to-tickets |
| CT-21 | Import Codex worktree inputs (119 files), `check_inputs.py`, `check:inputs` | designed (T2); lane record allocated-pending-merge | none | 1 (int. 5, D24) | ct21-codex-imports | pending /to-tickets |
| CT-22 | Doctor core (`dev/doctor/`, six surfaces); CT-22a = wave-0 slice | proposed | none | 0 (a); 1 heavy slot or 2 (b) | ct22-doctor | pending /to-tickets |
| CT-23 | Session hooks follow-up (thresholds via env, `ctx:status`, roster drift) | proposed | CT-19, CT-22 | 3 | ct23-session-hooks | pending /to-tickets |
| CT-24 | Decisions ledger (`plan_decide.py`, `decisions.jsonl`, `plan:decide`) | proposed | none | 1 (small) | ct24-decisions | pending /to-tickets |
| CT-25 | ticket-frontier orchestration skill (K1 §8: `frontier.py`, scheduler agent, executor gate G1-G7, learning ledger) | proposed (D32) | CT-05, CT-15, CT-17, CT-19, CT-22, CT-24 | 3 | ct25-ticket-frontier | pending /to-tickets |

Lane-unit names for proposed tickets are P1/P3 proposals (R8 names renumbered to C4's ids),
not records: each name is fixed by its allocation commit. Only `ct21-codex-imports` has a
lane record today; CT-25 is K1 §8 (D32), not in C4's table, and joins the D3/D23 approval.

Open GitHub frontier (closure prerequisites per row: `ticket-ledger.md`; sweep B for #62-#78,
#101). Operations, not lanes, unless marked:

| Group | Issues | State and carrier |
|---|---|---|
| A06 and A-series closes | #69 (blocked by #68); #62-#78 | CLOSE after CT-21 imports the `2a14` evidence; #72-#78 have no closure packet; #78 waits for A06 acceptance |
| Remaining-work tracker | #90 B1, #92 T1, #93 T3 (READY, in tip via M0); #97 T2 (blocked by #92); #101 T4 (blocked; attempt 3 STOPPED/NOT_COMPLETED, budgets 3/3, D25) | parent-run qualified closes between waves |
| Human operation | #91 B2 (READY; relabel `ready-for-human`, D20) | Codex Desktop attachment repair |
| Research queries | #94 C1 (integrated `4c1ea6b`, closure pending); #95 C3 (wave 2 #4 offline lane); #98 C2 (blocked by #94; wave 4+) | lanes then closes |
| LLVM bundle chain | #96 L1 (heavy 5); #99 L2, #100 L3 (blocked by #96); #102-#105 L4a-d; #106 L5a; #107 L5b; #108 L6 | heavy lanes under D5, one at a time |
| Native foundation (spec #11) | #21, #20, #17, #16 READY (heavy 1-4); #18, #19, #22, #23 blocked; #12, #24, #25 CLOSE | the C++26 chain of Phase 7 |

## Lanes

Projection of `lanes/*.json` on 2026-10-13 (the records are the source; SYNTHESIS §4 lists the
field corrections still to apply in Phase 3 step 7).

| Unit | Tickets | Branch @ base | status | retro |
|---|---|---|---|---|
| m0-remaining-work-merge | #90 #92 #93 #97 #101 #84-#89 | integration branch @ `d2a4103` | merged, review PASS, published `05c3dc9` | passed |
| a06-unit3 | #69 | `claude/a06-unit3-classification-methods` @ `e0667ec` | integrated (PASS-with-P3); published `f250f75`, on `28fedf1` | passed (record `a06-classification-methods.md`, alias `retros/a06-unit3.md`; gate rc 0) |
| codex-session-history | none | `claude/codex-session-history-skill` @ `e0667ec` | integrated (re-review PASS); published `f250f75`, on `28fedf1` | passed |
| rf-env-scrub | none | `claude/rf-env-scrub-inherited-selectors` @ `e0667ec` | integrated; C1/C2/C3 released; published `f250f75`, on `28fedf1` | passed |
| retro-gate | CT-01 | `claude/retro-gate-task` @ `361688e` | integrated (re-review PASS); on `28fedf1` | passed |
| team | CT-03 | `claude/team-roles-rules` @ `361688e` | integrated (re-review PASS); on `28fedf1` | passed |
| nav | CT-04 | `claude/nav-guidance-hierarchy` @ `7e22d13` (allocation `c6ff7ef`) | integrated `fa892d2`; on `28fedf1` | passed |
| c1-catalog-promotion | #94 | `claude/c1-catalog-promotion` @ `447110a` (allocation `ca60871`) | integrated `4c1ea6b`; #94 closure pending | passed |
| gate-hooks | CT-02 | `claude/gate-hooks-wiring` @ `2d1f60e` (allocated from `e618243`) | integrated `760b154` (lane `697e1da`); published `0a68dce` | passed |
| ct21-codex-imports | CT-21 | `claude/ct21-codex-imports` @ TBD at cut | allocated-pending-merge (designed, not cut) | pending |

## Decisions Made

Rows are the journal the injector shows (last three). D1-D26 are SYNTHESIS §8; the default is
the recommended choice; the user approved D1-D26 at their defaults on 2026-10-13. D27-D41 are the user's
answers to K1 §9 (`reviews/ccm-20261013/skills/K1-orchestrator-skill-design.md`).

| Id | Decision and default | Status |
|---|---|---|
| T-R1/R2 | Takeover interview rounds 1-2 (lanes, retro gate, models, A09 route, ledger): see Appendix A | accepted 2026-10-13 |
| D1 | Mid-merge: finish it as a declared evil merge (vs abort and redo) | approved 2026-10-13 |
| D2 | `hooks:install`: defer to CT-02b (A09 would refuse after install) | approved 2026-10-13 |
| D3 | Tickets: approve C4's CT-01..CT-24 (+CT-02b); publish CT-01..CT-04 as done sub-issues | approved 2026-10-13 |
| D4 | Settings composition: R5 §B (project: schema, hooks, plugins, marketplaces; local: the rest); secrets stay in fnox | approved 2026-10-13 |
| D5 | Heavy chain #21 > #20 > #17 > #16 > L1 #96; wave-2 heavy slot = #21; cap wave 1 at three lanes if preferred | approved 2026-10-13 |
| D6 | CT-08 scope: `.gitignore` + `baseline-files.v2.json` + `dev/check.py` only, wave 4 | approved 2026-10-13 |
| D7 | `mise/tasks/<unit>.toml` includes if `task_config.includes` validates; else parent appends rows | approved 2026-10-13 |
| D8 | Lane records parent-only; per-lane ledger `ledger-<unit>.jsonl`; amend planning-records.md | approved 2026-10-13 |
| D9 | Remove the eight integrated worktrees after publish and the a06 fix | approved 2026-10-13 |
| D10 | Spec `start_sha` for the end-of-spec `code-review` = `361688e` (vs `e0667ec`) | approved 2026-10-13 |
| D11 | Codex sweeps A/B/C: run them (done in revision 2; outputs land in step 7) | approved 2026-10-13 |
| D12 | `progress.md`: archive to `progress-archive-2026-10-13.md` | approved 2026-10-13 |
| D13 | Codex digests (1.7 MB): do not commit; commit briefs and reports | approved 2026-10-13 |
| D14 | AskUserQuestion request: build CT-13 as a mod (vs a CLAUDE.md rule vs no) | approved 2026-10-13 |
| D15 | Invocation wording: rewrite `claude-takeover.md:11` and `ticket-retro.md:4-8` per SYNTHESIS §4 | approved 2026-10-13 |
| D16 | `/retro` cadence: per build session | approved 2026-10-13 |
| D17 | Keep per-lane cold review and per-spec `code-review` | approved 2026-10-13 |
| D18 | Heavy tickets via `/implement` in a lane worktree with a lane record | approved 2026-10-13 |
| D19 | T4 Phase C: new attempt needs a new budget and explicit approval; decide after sweep B | approved 2026-10-13 |
| D20 | Draft PR to `main` and the #91 relabel: both on the user's word after CT-02 publishes | approved 2026-10-13 |
| D21 | Auto-compaction: project `autoCompactEnabled: true`, `autoCompactWindow: 700000`; user flips both personal copies | approved 2026-10-13 |
| D22 | Hook set and latency budget: C4's inventory only (SessionStart doctor 15 s, prompt hook, Bash and Agent gates, existing Stop gates) | approved 2026-10-13 |
| D23 | Ticket table: accept C4's reconciled CT-01..CT-24 (+CT-02b) at `/to-tickets` | approved 2026-10-13 |
| D24 | CT-21 import policy: index files committed, 119-file payload only through the CT-21 lane, keep-private sets in the 0700 mirror; fifth wave-1 lane | approved 2026-10-13 |
| D25 | T4 fourth attempt: none without explicit approval, a new budget, a fresh issue-write interval, rebuilt parent packets | approved 2026-10-13 |
| D26 | Wave-0 timing: runbook 1-8 with existing hooks first; then settings, fixtures, docs; then doctor; then agent/prompt hooks; blocking Stop rules last | approved 2026-10-13 |
| D27 | C++ ticket class = explicit include list in `frontier.toml` now; `area:cxx` label later | accepted 2026-10-13 |
| D28 | cxx slot takes the ticket's offline portion as a split unit when no heavy run is admitted; admission asked once per scheduler run | accepted 2026-10-13 |
| D29 | `frontier.toml` owns `context_ceiling_fraction`; `frontier.py plan` refuses on mismatch with `dev/doctor/budget.py` | accepted 2026-10-13 |
| D30 | `max_parallel` counts writer lanes only; hard cap 8 live agents | accepted 2026-10-13 |
| D31 | Retro auto/propose boundary = K1 §6 list | accepted 2026-10-13 |
| D32 | Skill built as CT-25 in wave 3 after CT-05/15/17/19/22/24; parent follows K1 §5 by hand until then | accepted 2026-10-13 |
| D33 | Executor gate G1-G7 accepted; G7 required for team mode only | accepted 2026-10-13 |
| D34 | Skill name `ticket-frontier` | accepted 2026-10-13 |
| D35 | Fable escalation only after one Opus attempt ends partial/blocked with reason `reasoning` | accepted 2026-10-13 |
| D36 | Scheduler model Opus high | accepted 2026-10-13 |
| D37 | Publish batch per integration | accepted 2026-10-13 |
| D38 | Plain-text confirmations until CT-13 lands | accepted 2026-10-13 |
| D39 | Learning ledger: JSONL under `P/frontier/`, rows cite `retros/<unit>.md` row ids | accepted 2026-10-13 |
| D40 | `allow_subagents=false` under `claude-agent` until G7 | accepted 2026-10-13 |
| D41 | `/ticket-frontier` user-invocable for status and re-planning | accepted 2026-10-13 |
| D42 | A second heavy C++ ticket waits unless admitted explicitly with `--admitted` (K2 default a) | accepted 2026-10-13 |
| D43 | Context thresholds compare against the implement model's ceiling (K2 default b) | accepted 2026-10-13 |
| D44 | Frontier tests run via `unittest discover -s dev -p test_ticket_frontier.py` (K2 default c) | accepted 2026-10-13 |
| D45 | Plain-text answers live in `frontier/answers.jsonl` until CT-24 (K2 default d) | accepted 2026-10-13 |
| D12-applied | `progress.md` archive applied 2026-10-13 ahead of D12 approval against the append-only rule in `.claude/rules/planning-records.md`; reversible from `reviews/ccm-20261013/plan-backups/` | recorded 2026-10-13 |
| D-all | D1-D26 presented 2026-10-13 and approved at defaults; D27-D45 accepted; CT-25 added; accepted-decisions hunk 2 applied on the user's word | approved 2026-10-13 (D1–D45) |

## Errors Encountered

P1 findings of the review (SYNTHESIS §2) with the ticket that prevents a recurrence and the C3
detector id that catches it; the full chain is SYNTHESIS §2b.

| Id | Error | Prevention ticket | Detector |
|---|---|---|---|
| P1-1 | Root checkout mid-merge (`MERGE_HEAD e12cf04`) with no record; handoff said nothing started | CT-17, CT-22 | C.merge-in-progress |
| P1-2 | Staged `.claude/settings.json` carries personal MCP permissions and all plugins | CT-16 | I.settings-non-project-key |
| P1-3 | Handoff ordered `hooks:install` before publish; A09 would refuse the hook tree | CT-02b | C.hooks-break-delivery |
| P1-4 | gate-hooks re-review PASS recorded nowhere; lane record stale | CT-05, CT-19 | B.review-missing |
| P1-5 | CT-01 marked passed while `dev/test_retro_gate.py` is wired to no task | CT-12 | H.unwired-test |
| P1-6 | Build started on tickets never approved or published | CT-24 | E.approval-missing |
| P1-7 | `/grill-with-docs` arrived as pasted text; docs call a request an invocation authority | CT-22 (D15) | D.invocation-row-unbacked |
| P1-8 | The 19:14Z AskUserQuestion mod request survives in no record | CT-13 | E.request-uncaptured |
| P1-9 | #91 relabel accepted, never applied | CT-24 | E.operation-unreceipted |
| P1-10 | Tip code reads data that exists only in the untracked `2a14` worktree | CT-21 | H.pinned-data-missing |
| P1-11 | Plan had no phases, Goal, Next Step, Current Phase; progress by append (430 KB re-injected) | CT-15 | K.plan-no-phases |
| P1-12 | No `tdd`; every lane dispatched as `general-purpose` | CT-19 | F.lane-dispatch-generic |
| P1-13 | `a06-unit3` record claims retro passed; `retro_gate.py --unit` exits 2 | CT-05 (step 7 rename) | H.retro-unit-alias |
| P1-14 | Auto-compaction off; parent died at 977 K tokens; fork inherited the full window | CT-23 (W0-1, W0-3) | A.autocompact-off |
| P1-15 | Agent definitions created mid-session were never offered | CT-19, CT-22 (W0-4) | F.agents-not-offered |

## Workflow

Stage script (D2 §4). The parent runs Skill calls for `grilling`, `domain-modeling`, `tdd`,
`code-review`, `pr`, `research`, `prototype`, `writing-for-agents`, lanes, worktrees, merges,
`retro:gate`, `issue:*-preview/-verify`, `delivery:prepare`; it asks before `issue:*-apply`,
`delivery:publish`, qualified closes and host-heavy runs. The user types, in order:

1. `/mattpocock-skills:setup-matt-pocock-skills` (fresh session; parent diffs `docs/agents/`).
2. `/mattpocock-skills:grill-with-docs <idea>` (fresh session, plan mode off; no `/clear`
   until tickets publish).
3. `/mattpocock-skills:to-spec` (seams shown first, approval awaited).
4. "publish spec" (parent runs `issue:create-preview/apply/verify`).
5. `/mattpocock-skills:to-tickets <spec path or #n>`; approve the numbered breakdown.
6. "publish tickets" (`issue:create-*`, `issue:new-edge-*`, audit, `ready-for-agent`).
7. `/clear`, then `/mattpocock-skills:implement-spec #<spec>` (parent runs the waves).
8. Heavy ticket: `/clear`, `/mattpocock-skills:implement #<n>`; confirm each heavy run.
9. Before each `/clear` of a build session: `/mattpocock-skills:retro`.
10. `/mattpocock-skills:handoff "<purpose>"` for a Codex resume, prototype or colleague.
11. `/mattpocock-skills:triage #<n>` for an external issue.
12. `/mattpocock-skills:wayfinder "C++26 P2996 research core"` in its own session.

A stage counts as invoked only when the user types it; `skill-invocations.md` records each.
Lane protocol: `docs/agents/claude-team.md` (roles, lifecycle, retro gate) and R8 §Integration
(one merger, `--no-ff` without `--no-commit`, `check:research` serialized, publish after each
integration, lanes never write shared planning files, never `isolation: worktree`).
Context budget (C4, binding; one threshold dict in `dev/doctor/budget.py`): warn 400 K,
fork deny 500 K, checkpoint 550 K (write `plan:handoff`, delegate with small briefs), hard 650 K,
all below `autoCompactWindow` 700 K. Until the hooks exist the parent applies the rule by hand.

## Appendix A: Claude takeover (2026-10-13)

Codex threads `01a127db`, `01a130ef`, `01a12bd1` and `01a13185` stopped; the three trees died on
`usage_limit_exceeded` (nine spawned children inside a turn, eight at 14:07-14:09Z, `01a128a0`
on 10-12) until 2026-10-19. The user transferred sole integration-writer ownership of
`codex/marketplace-native-onboarding` and this plan to the Claude Code session at HEAD
`d2a4103` (remote `848552c`). The [activation record](../../docs/agents/claude-takeover.md)
binds the observed state and granted authority. Every Codex worktree, branch and private
evidence packet is a read-only import source. The `refresh-llvm-github-research` heartbeat
(4 h rrule, target `01a12bd1`) keeps running outside the repository and writes only under
`github-research/`; Codex's packet `lane-ledger.json` is superseded (supersession notice:
SYNTHESIS §4, sweep B §4). The `2a14`/`c658` worktree data is snapshotted
(`imports/codex-worktrees-20261013`, MANIFEST `259f9fae`; private mirror
`~/.local/state/marketplace-imports/codex-worktrees-20261013`); CT-21 imports what the tip
cites; the worktrees are removed only after CT-21 is published. Do not reset or archive them.

Conventions from the takeover interview (rounds 1-2, all accepted):

- One unit per lane. A lane runs in `.claude/worktrees/<unit>` on branch
  `claude/<unit>-<slug>` cut from the integration tip, with the path allowlist,
  owner, reviewer, base SHA and status recorded in [lanes/](lanes/). Commit the
  lane record before cutting the worktree so the lane's base carries it. The
  `.gitignore` is a frozen baseline file, so `.claude/worktrees/` is excluded
  through `.git/info/exclude` until a reviewed baseline transition.
- The parent merges one lane at a time; publication uses the A09 route;
  tickets close only through the qualified close operation, one at a time.
- Every unit ends with a retro record in [retros/](retros/) whose actionable
  findings are applied before integration; a lane writes its record inside
  its own worktree (the path is part of every lane's allowlist) so the gate can
  see it before handoff. The deterministic gate `dev/retro_gate.py`
  (`./dev/mise run retro:gate -- <unit>`, integrated at `e618243`) refuses
  integration or publication without it and runs identically as a mise task,
  an `hk` git hook and Claude Code hooks (lane gate-hooks, ticket CT-02).
- Learnings land by kind: mechanical rules in checks, judgement rules in
  `CODING_STANDARDS.md`, navigation in the nearest `AGENTS.md` or
  `.claude/rules`, repeated workflows in skills, roles in `.claude/agents`.
- Models: Opus 5.5 implementers for code lanes, Sonnet 5.5 for documentation
  lanes, Fable for review, retro and synthesis, Haiku for mechanical extraction.
  Up to four offline lanes run concurrently; host-heavy lanes run one at a time
  with per-run user confirmation.
- Ticket state lives in [ticket-ledger.md](ticket-ledger.md); the new spec
  "Claude team takeover and self-improving workflow" is published through
  to-spec/to-tickets and its tickets join that ledger.
- Stage invocation modes are recorded, not assumed. On 2026-10-13 `/grill-with-docs`
  arrived inside pasted text and was not expanded by the harness; `grilling` and
  `domain-modeling` ran natively through the Skill tool; `to-spec`, `to-tickets`,
  `implement-spec` and `retro` were applied file-guided from the installed `SKILL.md`
  files at the user's round-1 Q3 request. None of the five stages has been invoked;
  a stage counts as invoked only when the user types it (SYNTHESIS P1-7; D15 applies
  the same wording to `docs/agents/`). [skill-invocations.md](skill-invocations.md)
  binds each stage's source hash, mode and output pointer.

B2 (#91) needs the Codex Desktop attachment operation and is relabelled for a
human (D20; the label is still `ready-for-agent` on GitHub). The agent-protocol /
dynamic-agents work of thread `01a13185` is out of scope and referenced only; its ticket 30
targets this repository's `.codex/` and `hooks.json`, so CT-07 coordinates with it.

The lane table that stood here until 2026-10-13 was stale on every row and is replaced by the
`## Lanes` projection above; `reviews/ccm-20261013/plan-backups/task_plan.pre-rewrite-20261013.md`
keeps the pre-rewrite file byte for byte.

## Appendix B: Accepted contracts (preserved from the pre-rewrite plan)

The sections below are the accepted contracts of the Codex era, kept verbatim (tables keep
their original row widths). They are history and reference, not current state; current state
is above the fold.

## Objective

Qualify native Codex onboarding while preserving the Claude marketplace and OCI
acceptance contracts. The accepted product direction is incremental migration
to a native C++26 P2996 research core; build/toolchain work follows onboarding.

## Confirmed completion workflow

The user confirmed the [completion contract](completion-contract.md) after a
Claude Fable lead and two Fable reviewers examined it. All 16 original findings
and one follow-up handoff note were corrected; both independent follow-ups
passed, and the saved verifier checked 40 bound files with rc 0. Q1 applies retro
barriers per lane and affected dependencies; Q2 confirms the complete execution
contract and existing public test seams. The interview is complete.

Reuse spec #11 and its 67 child identities. A06 may proceed after the W1 source
policy import and its own allocation; A12b follows A06 acceptance. Independently
ready existing tickets can proceed concurrently. New or changed A12b ticket
slices and edges still require their specific review. Eighteen source-qualified
milestones need individual tracker reconciliation; publication and a closed issue
do not replace acceptance. The peer owns the generic tracker extensions, including
acceptance-close qualification. Missing required gates remain explicit blockers.

The selected five-stage skills and their durable protocol remain authoritative.
Preserve the final reviewed contract hash and the confirmed decisions in the
[acceptance record](../../evidence/completion-workflow/contract-acceptance.json).
This records workflow admission, not completion of the remaining implementation.

W1 and source alignment remain published at `f0d79a0`. The earlier #28
offline contract and A06 retrieval unit one were published at `a0713408`;
hosted research-fast run `38372912753` passed on that exact commit. Their
[original acceptance record](../../evidence/completion-workflow/offline-unit-integrations.json)
remains immutable.

#29's cached-SDK offline bridge is source-accepted at `66905b4`, including
fresh source normal/optimized loopback and fault controls. A06's offline
classification reader is source-accepted at `5acdc3a3`; its 17-test suite,
named checks, independent review and applied retro passed. The
[follow-up acceptance record](../../evidence/completion-workflow/offline-followup-integrations.json)
binds both source units; their publication remains a separate A09 operation.
A06 next adds the bounded TOML and pinned model-field methods, then consumes
the retained corpus. Full example validity remains `UNVERIFIED`.

Full #28/#29 and A06 remain incomplete. #30 still requires its reviewed
milestone/edge amendment and other prerequisites; #40 remains held for its
live/native requirements. A12b follows A06's actual acceptance.

## Small units

Each unit has one purpose, at most about five maintained files and 300 handwritten
changed lines. Generated evidence is checked mechanically. Settle each unit's
acceptance before admitting dependents. The parent owns this plan and serializes
integration; a retrospective holds its lane and affected dependencies until all
actionable repairs are applied, checked and independently reviewed.

| Unit | Deliverable | Gate | State |
| --- | --- | --- | --- |
| N0 | Ownership, plan, live bounded team | Identity, source hashes, worker ACKs | Complete |
| N1 | Root/scoped guidance and accepted decisions | Source comparison; documentation review | Complete |
| N2 | Necessary project Codex config and roles | Exact CLI schema; merged transports; role loading | Complete |
| N3 | Separate development commands | No install/bootstrap; lightweight checks; OCI bytes preserved | Complete |
| N4 | Fresh-session qualification and handoff | Worktree and unrelated-cwd probes; cold review | Complete |
| 01a | Acquire exact template/helper/generator source and licenses | Pinned paths, hashes, immutable research preserved | Complete |
| 01b | Small scratch preset adaptation and reuse ledger | License attribution; safe includes; independent review | Complete |
| 04a | Global tool ownership inventory and prepared patch | Concurrent-writer census; exact preimages; independent review | Complete |
| 04b | Managed build tools and named environments | Ownership admitted; native configuration and environment checks | Complete |
| 02a | Pinned TCPM source and local development environment | Blob/source identity, locked dependencies, CLI smoke | Complete |
| 02b | Representative native preset matrix | Deterministic regeneration, exclusions, four native preset kinds | Complete |
| 05a | GCC16 source/package inventory and prepared native bootstrap | Exact current mise contract, package identities and reviewed isolation | Complete |
| 05b | Captured GCC bottles and installation preparation | Archive hashes, complete prefix writes, protected preimages and independent review | Complete |
| 05c | Guarded native four-bottle installation | Immediate ownership/preimage/plan checks, native exit code, installed links and preserved defaults | Complete |
| 05d | GCC16 environment and reflection witness | Exact compiler/stdlib/SDK identity, positive compile/link/run and negative flag control | Complete |
| 10b | GCC16 CMake toolchain fixture | Intended compiler/SDK/libstdc++, four Multi-Config build/test cells and isolation controls | Complete |
| 03a | Minimal native library, POD facade and smoke executable | Qualified GCC static/shared builds; private reflection flags; original acceptance hashes | Complete |
| 06a | Pinned LLVM source and bounded bootstrap recipe | Exact commit/tree and license; matching runtimes; source-only acquisition and independent review | Complete |
| 11a | Pinned vcpkg source and native registration preparation | Exact tool and registry provenance; isolated native link contract; independent review | Complete |
| 11b | Private native vcpkg bootstrap | Pinned binary checksum, ARM64 execution, root discovery and independent review | Complete |
| 11c | vcpkg promotion preparation and project manifest | Reviewed namespace-only helper; controlled guards; native manifest check | Complete |
| 11d | Scoped global vcpkg promotion | Fresh ownership/preimages; exact reviewed helper; native global discovery | Complete |
| 06b | Guarded P2996 outer configure | Fresh shared capacity; exact inputs; generated runtime commands; independent review | Complete |
| 07a | Guarded cold-build preparation | Nested build limits, durable logs, timeout/reserve controls; independent review | Complete |
| 07b | Native P2996 cold build | Fresh capacity and lease; actual final exit; child caches and artifact review | Complete |
| 07b1 | SDK comparator repair preparation | Exact five-file patch; negative and positive syntax controls; independent review | Complete |
| 07b2 | Guarded SDK source adaptation | Exact source postimages; native apply/reverse checks; independent review | Complete |
| 07b3 | Guarded incremental restart preparation | Applied-source and history binding; drift controls; independent review | Complete |
| 07b4 | Native incremental LLVM restart | Fresh admission; final native exit; runtime and artifact review | Failed; closure verified |
| 07b5 | SDK math compatibility scratch controls | Reproduced macro failure; smallest source repair; boundary test; independent review | Complete |
| 07b6 | Guarded math source application preparation | Exact two-header patch; prior source/build preservation; independent review | Complete |
| 07b7 | Guarded math source application | Exact seven-file source state; reverse check; retained build state; independent closure | Complete |
| 07b8 | Guarded math-adapted restart preparation | Both source adaptations; child build/history bindings; independent drift review | Complete |
| 07b9 | Native math-adapted LLVM restart | Fresh capacity and lease; final native exit; runtime and artifact review | Complete |
| 07c1 | Guarded private installation preparation | Reviewed scripts and build bindings; prefix/manifests/aliases; independent guard review | Complete |
| 07c2 | Native private LLVM installation | Fresh admission; three native exits; complete prefix inventory; independent artifact review | Complete |
| 07d | Private P2996 reflection and runtime witness | Named environment; exact headers/runtime origins; positive and negative controls; independent review | Complete |
| 07e1 | Native P2996 registration preparation | Private namespace discovery; exact preimages and scope; independent guard review | Complete |
| 07e2 | Scoped native P2996 registration | Fresh ownership and preimages; exclusive promotion; global discovery and independent review | Complete |
| 08a | LLVM formatting, clangd and archive fixture | Actual formatted reflection compile/archive/link/run; isolated clangd CDB check; independent review | Complete |
| 08b | LLVM tidy and static-analysis controls | Intended diagnostics and failing exits; corrected clean cases; reflection parsing and independent review | Complete |
| 08c | LLVM source-based coverage fixture | Fresh reflection profiles; exact branch counts; missing-data control and independent review | Complete |
| 10a1 | P2996 CMake toolchain preparation | Exact compiler/runtime contract, native CMake link propagation and independent source review | Complete |
| 10a2 | Native P2996 CMake fixture | Actual ABI/custom probes, four build/test/runtime cells, isolation controls and independent review | Complete |
| 03b1 | Native core P2996 compatibility preparation | Compiler-specific guards, private flags, honest CTest exits and independent source review | Complete |
| 03b2a | Native core command acceptance rules | Recorded native command replay, rejection controls and independent review | Complete |
| 03b2b | Native core two-compiler qualification | Static/shared four-configuration cells, runtime origins, failure controls and independent review | Complete |
| 09a | Pinned IWYU source and matching-fork build preparation | Exact source/license identity, native LLVM package contract and independent review | Complete |
| 09b | Guarded private IWYU build and installation | Fresh shared capacity, exact compiler/link commands, native exits, dependencies and independent review | Complete; runtime drift reattested in 09b1 |
| 09b1 | Reattest replaced mise runtime | Exact single-path change, existing profile parity, protected-state checks and independent review | Complete |
| 09c1 | IWYU reflection advice and fixer | Exact include recommendations, restricted fixer, native rebuild/run and clean reanalysis | Complete |
| 09c2 | IWYU copied-resource relocation | Moved-copy identity, explicit resource override, actual header trace and negative control | Complete |
| 12a1 | Shared vcpkg chainloader preparation | Pinned source boundaries, policy/flag composition and bounded CMake controls | Complete |
| 12a2 | P2996 overlay triplet preparation | Explicit ABI inputs, environment tracking, dual configurations and script controls | Complete |
| 12b1 | GCC16 overlay triplet preparation | Shared-input reuse, GCC ABI entries and focused script controls | Complete |
| 12c1 | Private vcpkg execution preparation | Reviewed source binding and native fail-closed receipt | Prepared; native held by shared drift |
| 12c1a | Observed mise update reattestation | Exact metadata changes, preserved compiler guards and existing profile parity | Complete |
| 12c1b | Private vcpkg qualification retry | Qualified shared state; fresh capacity; copy, confinement and host-tool selection | Complete |
| 12c2a | pkg-config prerequisite preparation | Exact native profile discovery, provisioning source/ownership contract if required | Complete |
| 12c2b | Guarded native pkgconf installation | Reviewed write set; fresh capacity; native exit, links, package lookup and preserved defaults | Complete |
| 12c3a | Qualified pkgconf ABI and fmt build inputs | Exact selection guards, retained ABI entries and bounded CMake controls | Complete |
| 12c3b | Private native fmt builds | Reviewed build/configure limits; fresh capacity; native exits, detector and ABI receipts | Complete |
| 12c3c | Application and fmt consumer parity | Public vcpkg composition; eight build/run cells; actual loader paths and preserved dependency roots | Complete |
| 13a | Native baseline preset preparation | Deterministic TCPM generation; eight trees, 32 cells, independent linkage and four preset kinds | Complete |
| 13b | Native baseline matrix | Eight isolated preset trees; 32 build/test/runtime cells; independent linkage and exact dependency mapping | Complete |
| 14a | LLVM ASan/UBSan runtime witnesses | Pinned source contract; clean reflection consumer and deliberate memory/overflow diagnostics | Failed; closure verified |
| 14a1 | Private ASan startup repair | Exact source patch; original timeout control; seven sanitizer cases; independent review | Complete |
| 14a2 | Installed ASan guard preparation | Exact single-file overlay; preserved guard chain; confined replacement controls | Complete |
| 14a3 | Installed ASan promotion | Exact backup/recovery; fresh ownership; installed-path sanitizer witnesses | Complete |
| 14b | P2996 TSan and TSan+UBSan witnesses | Ordered clean case; data-race and overflow diagnostics; exact runtimes | Failed; closure independently verified |
| 14b1 | Private TSan startup repair trial | Exact TSan link recipe; original/patch A/B witnesses; no installed write | Complete |
| 14b2a | Installed TSan guard preparation | Composed ASan/TSan inventory overlay and private exact-file controls | Complete |
| 14b2b | Guarded installed TSan promotion | Exact prior/next identities, fresh admission and five installed-path witnesses | Complete |
| 14c | P2996 LSan and LSan+UBSan witnesses | Clean/leak/overflow diagnostics, exact runtime and private builds | Blocked: installed LSan clean exit deadlocks during leak scan; closure verified |
| 14c1 | Private LSan stopped-world repair preparation | Exact pinned-source hunk, syntax control and independent review | Planned |


## Full-baseline spec workflow

The user expanded the requested spec to the complete accepted research baseline,
including the remaining build foundation and thin Claude, Codex, Antigravity
and OpenCode adapters. The PDF updater and SBE/firmware phase remain excluded.
GitHub Issues will hold one spec and bounded dependency-linked tickets. A
standby Claude takeover runbook is required before long implementation work.
The one-writer and per-unit gates above remain in force.

| Unit | Deliverable | Gate | State |
| --- | --- | --- | --- |
| W0 | Configure skill tracker, labels and domain-doc routing | User-reviewed draft, exact Git identity, lightweight checks, GitHub label verification | Complete; committed `0a7a2444` |
| W1 | Publish full-baseline spec | Accepted scope and test seams, source-backed claims, ready-for-agent issue | Complete; GitHub #11 |
| W2 | Publish context-sized ticket graph | User-approved granularity and genuine native blocking edges | Complete; 50 sub-issues #12–#61 under #11, all parent/body/label/edge checks verified |
| W3 | Standby Claude takeover document | Exact live state, issue frontier and explicit sole-writer transfer | Complete; independent final review found no material findings; standby only |
| W4 | Implement approved ticket graph | Per-worktree ownership, disjoint file scopes, bounded tests/review, per-ticket retro with all actionable findings applied and verified, then serialized integration | Independent #13/#28/#29 worktrees admitted after user-facing parallel summary; their full native/provider acceptance remains partial; selected offline source integrations are recorded below. #13 repaired pre-run review passed and one guarded private LSan trial ran; command rc 1, overall INCONCLUSIVE, patched clean case rc 86 for 120-byte leak; later read-only closure reconciliation passed. Trial and partial retro are locally committed through `65d93d1`; clean-control preparation reached `8062821` but three live census reviews withheld admission. The requested [follow-up retro](/Users/rmanaloto/.codex/worktrees/issue-13-lsan/claude-code-marketplace/.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/issue-13.md) applied offline regression gates, retry guidance and proposal retirement at local commit `5e119e5`; task validation/check/baseline and independent code/document reviews passed. The overall #13 gate remains partial. The bounded native experiment and full witness gate remain unrun. #28 offline v2 CLI contract is requalified and source-integrated at `cbb455b` with independent review and retro PASS; public CLI/OCI acceptance remains partial. #29 cached-SDK offline bridge is source-accepted at `66905b4` after fresh normal/optimized/fault consumption and independent review; live provider/confined install/native caller acceptance remains partial. #30 waits for prerequisites. #12 closure committed `2cc4c029`, #24 boundary committed `931b536`, #25 helper selection committed `54d34c8b`; GitHub issues remain open at last verification |
| W5 | Reconcile the 17-point workflow clarification | Source-backed gap audit, resolved decision frontier, reviewed spec/ticket amendment, per-task retro application gate | Retrospective remediation active; A01–A05b and A09 published at `93bb798b`; A07a and A12a published at `a8ecd40b`, with hosted fast CI success; A10 planner published at `bcf97606`; A07b spec #11 body verified live; A08 publisher published at `3972f3b9`, all 17 child issues #62–#78 independently verified under #11, and all 21 new blocker edges independently verified live after A08b1 publication `623dad43`; A08b2 independently verified the complete 67-child graph, all 139 blocker edges and sole `ready-for-agent` labels on #12–#78, with handoff published at `906cdbc1`; individual acceptance and closure remain separate. A11a preflight published at `d95e3406`, A11b helper at `48027d2d`, and source handoff at `42d94f`; the guarded live switch returned rc 2 on an unexpected `.venv`, but exact checkout/retained state was independently reconciled and source-root tools/deps/static/baseline checks passed. A11 physical transfer is accepted by manual reconciliation, not an automated guard pass. A06 retrieval unit1 is published at `a0713408` and offline classification unit2 is source-accepted at `5acdc3a3`; TOML/schema methods and retained-corpus consumption remain pending. W4 preserves #13/#28/#29 residual gates |

The first [parallel specialist wave](parallel-specialists.md) is complete:
three bounded read-only lanes ran concurrently, followed by independent repair
and receipt reviews in freed slots. The resulting #13 signal-restoration repair
is locally committed at `4905c8e52ecd502de3b79e666799ab990a054c52`, with six
tests, named static/baseline checks and focused review passed. Its native gate
is still partial. The handoff has four selective integration units ready for
parent execution. The [acceptance-cycle correction](retros/acceptance-frontier.md)
was independently reviewed and explicitly accepted by the user on 2026-10-13.
A06 may resume after actionable defects in completed units are verified; future
native/provider/OCI gates hold their actual dependents. A12b still waits for
A06 acceptance. #28's offline milestone has passed source integration and its own
checks. #30 remains held until A12b approves the specific offline milestone and
dependency-edge amendment, its qualified mutation runs, and other prerequisites
pass. Full #28 acceptance remains separate. Baseline-transition design can proceed
independently, with versioned review before application. GitHub dependencies
are unchanged. Integration stays serialized; independently admitted worktrees
may implement disjoint ready units concurrently.

A05b and the completed-unit remediation ledger remain accepted. W1 source
policy and onboarding/plan alignment are published at `f0d79a0`. A06 retrieval
unit one is published at `a0713408`; classification unit2 is source-accepted at
`5acdc3a3` with 17 example tests. The next bounded A06 unit adds TOML and
pinned model-field methods before actual retained-corpus consumption. Each source
integration and publication keeps a separate owner and receipt.

The approved A-index, with the current prerequisite correction, is
[automation-amendment-draft.md](automation-amendment-draft.md). Its older
"unpublished" wording and the phase notes below are preserved as history;
the W5 row above and [progress.md](progress.md) carry current publication state.
The source-branch retrospective protocol transfer and ten-record historical
audit passed local static checks and independent archival re-review. The
later ten-record archive and its linked receipts passed the same bounded
checks. Both transfers are locally committed through `9975c98`; remote
publication remains separate from A06/A12b admission.
The user approved its original fourteen-slice breakdown and blocking edges on 2026-10-12.
A01/A02 retrospectives split late A12 into A12a fast-check/hosted CI
qualification after A09 publication and A12b assembly. A04's retro split A03
into A03a bounded attempts and A03b controlled-empty verdicts. Reviewed
A01–A05b code and the A09 delivery gate are published on the integration
branch at `93bb798b`; A07a and A12a follow at `a8ecd40b`. The hosted
`research-fast` run on that exact SHA concluded success. Their GitHub
amendment issues remain unpublished.
A02 exposed a missing host SSL library
in the shared Python tool; A01 now uses a project-scoped tool install. Focused
read-only reviews of A01, A02 and A04 passed. Their retro records and local
improvements are complete. `check:research` exits 0; it is not hosted CI
acceptance. A04's nine offline controls pass and its immutable receipts remain
uncommitted. A03a passed twelve offline controls and focused review; its
final-source live receipt is bounded `partial` with `item_limit` (10/898), not
a full or controlled-empty result. Its retro applies the private-result and
timeout-safe seam to A03b. A03b passed six control fixtures and focused
review; it can promote only a complete candidate with passed same-budget
controls. Its complete and verified-empty outcomes are exercised in offline
fixtures only. A05 is split into read-only baseline/comparison A05a and
concurrency-safe public rerun A05b. A05a passed seven comparison fixtures and
focused review, with A03b normalization version 2, captured published-run
inventory, and hash-checked bytes used for comparison. Its retro requires A05b
to bind public reruns and quarantine under a per-query writer lock. A05b passed
six public offline fixtures, focused review and a bounded live command. The
live search is partial and its comparison is suppressed. A06 was paused under
the user's retrospective-action hold before the accepted correction above; no live full-inventory or NEW/GONE
result has been qualified. The [application audit](retros/application-audit-2026-10-12.md)
preserves its original snapshot and adds current statuses for the now-complete
hosted fast check, physical transfer, publication actions and remaining
ticket blockers. The user clarified that named retrospective actions
may proceed in prerequisite order to clear this hold. The user's later
parallel-worktree direction admitted independent #13/#28/#29. The correction
above narrows the subsequent hold to actionable completed-unit defects and
the actual dependents of missing runtime gates.
Parent ownership of this plan and the integration branch is unchanged. The
earlier separate ticket worktrees retain their files; current writing is
serialized across this Git common directory. Record each approved local slice's state and receipts; the
old GitHub frontier does not override W5. The historical native review and parent
dispositions remain in the [retained worktree review](/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/docs/agents/automation-amendment-review.md);
that local artifact has not been transferred to the source branch (imported by CT-21;
the link becomes `../../docs/agents/automation-amendment-review.md` once it integrates).
Do not reopen the twelve settled requirement interpretations or manually publish
bootstrap issues/commits. The current review-task helper is not A01 acceptance.

Onboarding is committed at `67bd4827532864ecb934050dde6c0c11b92f9939`.
Its post-commit baseline check exited 0 and the worktree was clean.
Task 01 uses the accepted pinned shortlist; this is source qualification,
not a new comparative research sweep or a runtime toolchain qualification.

## Acceptance required before completion

- Exact checkout/branch/HEAD and source provenance recorded.
- Fresh read-only sessions load project guidance using native project selection.
- Configuration and roles validate against the installed CLI, currently 0.162.1.
- Available global skills/plugins reused without copying Claude lifecycle behavior.
- Lightweight checks record actual exit codes; independent findings are dispositioned.
- Existing acceptance inputs remain unchanged; full OCI execution is explicitly pending.

## Admission and later work

Project-local lightweight work and read-only ownership/tool inventory are admitted.
Task 04a prepares the accepted later global mise phase before any host mutation.
Global settings, hooks, trust, credentials, model defaults, other projects,
containers, heavy builds, publication and destructive cleanup remain outside it.
Task 04b's bounded admission is recorded in
`evidence/tool-foundation/global-admission.json`: seven new named files and three
explicit managed build-tool versions, one installer job, no existing default
config/lock changes. The seven files were applied after preimage checks; native
installation, host qualification and independent application review passed. Broader
global ownership, compiler builds and host-heavy capacity remain unadmitted.
Task 05a permits read-only compiler inventory, primary-source acquisition and
project-local preparation. It does not authorize installation or compilation.
Task 05b prepares a bounded four-bottle operation. Download and inspect archives
privately, then record ownership, preimages and exact write targets before apply.
Canonical Homebrew writes and compiler execution await that admission record.
Task 05c's bounded installer and three review repairs have been independently
verified. `evidence/gcc-bootstrap/install-admission.json` admits only the four
reviewed native pours and two directory conversions after immediate guards.
Task 05c executed no compiler; runtime qualification follows in task 05d.
Task 05d admits sequential, sixty-second-bounded compiler probes and one tiny
reflection witness in a new private directory. The fresh census found no compiler
or build processes; this does not admit a cold toolchain or matrix build. Existing
global profiles are selected without edits; all protected preimages remain gates.
Task 10b admits only the tiny CMake fixture and sequential one-job builds in a
new private directory. Its five maintained files are the toolchain, fixture
CMakeLists/README and selected plan/progress. No dependency or compiler build,
global edit, source bootstrap or cache server is included.
Task 03a admits the root CMake file, public header, library source, smoke source
and this plan. Qualify static/shared libraries in all four configurations using
sequential one-job, sixty-second-bounded builds in new private directories.
No dependencies, installers, cache server, adapter replacement or OCI run is
included. The smoke executable is a foundation witness, not the plugin CLI.
Task 06a permits exact-source acquisition into a new private checkout and a
reviewable native bootstrap recipe. Its maintained files are the source helper,
CMake initial cache, documentation and these two planning records. No compiler
build, installation, global registration or configure probe is included;
configuration and the cold build receive separate bounded operations.
Task 11a qualifies the already accepted vcpkg commit and native mise registration
in new private directories while the shared heavy lease is occupied. Its scope
is one confined preparation helper, two documentation files and these planning
records, with generated source/experiment receipts. No bootstrap, dependency
build, global link, configuration change or shim mutation is admitted here.
No native goal was requested. Monitor chat owns no marketplace files.

Task 09a admits exact pinned IWYU source acquisition and source-only build
preparation. Its maintained files are the acquisition helper, initial cache,
IWYU documentation and these planning records. Build the tool against the
qualified fork's headers/libraries using its admitted Apple bootstrap runtime;
qualifying reflection analysis and relocation requires a later native operation.
Script-mode CMake guard checks are admitted; they configure no project and run
no compiler. Installation, global registration and shared-prefix writes are excluded.

Task 09b separately admits the reviewed one-job private IWYU operation in
`evidence/iwyu-build/admission.json`, after fresh capacity and independent
pre-run review. The runner repeats the canonical lease/census and exact input
checks before configure/build/install; shared source, LLVM prefix and defaults
remain protected. Analysis, relocation and global registration are later gates.

After N4, continue the source matrix's small tasks: template reuse qualification;
then a separately admitted global tool foundation and TCPM trial; compiler,
vcpkg, preset, analysis and package qualification follow their recorded edges.
Do not treat source-backed tool pins or 96 candidate trees / 384 cells as runtime
qualified. Preserve all inherited research failures.

## Evidence

Task 12a1 admits the P2996 composition correction, shared vcpkg chainloader,
`docs/vcpkg-toolchains.md` and these two planning files. Retained source receipts
and bounded CMake script-mode controls are allowed; no compiler detection,
dependency build, installation, shared-source mutation or cache service is
included. Native task 12 operations receive separate capacity admission.

Task 12a2 admits two P2996 triplets, their common macOS inputs and these two
planning files. Exact-source prerequisite copies and CMake script controls may
be retained. The common file may prepare the existing GCC lane, but no GCC
triplet, native compiler detection, dependency build or tool execution is
qualified by this unit. Keep dependency Debug and Release enabled and record
nested toolchain, runtime, SDK and managed build-tool ABI inputs explicitly.

Task 12b1 admits two GCC16 triplets, `docs/vcpkg-toolchains.md` and these two
planning files. Reuse the committed common inputs without changes. Bounded
CMake script controls may inspect GCC files and the chainloader; native compiler
detection, dependency builds and cache/confinement qualification remain separate.

Task 12c1 admits one private vcpkg preparation/probe helper, composition docs
and these planning files. After independent review and fresh shared capacity,
it may copy the exact vcpkg checkout and fmt inputs, select the existing named
profiles, verify managed host tools and exercise local write/network restrictions.
Keep real HOME unchanged. No dependency/compiler build, patch application,
global registration, cache provider or integration command is included.

Task 12c1a prepares an exact overlay of independently inventoried shared-state
changes. After source review it may run existing read-only profile and isolation
probes, each bounded to sixty seconds, in a new private directory. Preserve all
historical receipts and every unrelated protection check. No installation,
global write, compiler/vcpkg execution or lease acquisition is included.

See `findings.md`, `progress.md`, and `docs/agents/codex-task-orchestration.md`.
Task 12c1b admits the unchanged private vcpkg probe under the qualified 12c1a
guard and current profile receipts, after independent review and fresh capacity.
Only the helper, composition docs and these planning files are maintained.
No dependency build, compiler detection, global write or cache provider is included.
Historical handoff sources stay immutable in the source checkout and original
research directories. New receipts belong only to this worktree.

Task 12c2a resolves the pkg-config prerequisite before dependency execution.
Bounded read-only profile discovery uses the qualified shared-state guard and
private sandbox. Preparation includes one bottle-inventory helper and a private
captured-metadata dry run with a missing-metadata failure control. Prepare exact
native mise inputs and preimages for review before installation or global writes.
Keep fmt package validation enabled; no compiler or dependency build is included.

Task 12c2b prepares one guarded pkgconf installation helper, composition docs
and these planning files. Review the exact pinned archive, native command and
postimage allowlist before admission. Installation requires fresh shared capacity,
canonical lease and immediate prefix/writer checks; preserve all existing guards.
No compiler/dependency build or global mise configuration change is included.

Task 12c3a admits the common triplet, composition docs and these planning files.
Bind the already-qualified pkgconf selection and executable/runtime ABI inputs;
keep fmt as a compiled library without modules for the smallest parity witness.
Bounded CMake script controls perform no compiler detection, dependency build,
installation, lease acquisition or shared writes.

Task 12c3b prepares one private fmt build helper, composition docs and these
planning files. Review exact inputs, four ordinary manifest installs, fresh
per-triplet state and confinement before fresh capacity admission. Allow one job
per dependency build and up to two concurrent Debug/Release CMake configure
processes, including their compiler probes, within the single leased operation.
Keep compiler tracking and both dependency configurations enabled. No shared
installation, binary cache, consumer build or full matrix is included.

Task 12c3c admits the root CMake composition guard, one private consumer helper,
composition docs and these planning files. Prepare eight Debug/Release consumer
cells against the four retained fmt installations, using the actual research
core target. Disable vcpkg automatic installation and keep dependency roots
read-only. Native configure/build/run requires independent preparation review,
fresh capacity and the canonical lease. No dependency rebuild, global write,
binary cache, instrumentation family or full baseline matrix is included.

Task 13a admits root CMake integration, the existing smoke source, one native
TCPM baseline template and these planning records. Generated native preset JSON
is checked mechanically and committed. Keep core/fmt linkage independent and
use the four retained fmt installations with installation disabled. Generation
and native preset listing may run without configuring a project or invoking a
compiler. The full 32-cell native operation follows separate review and fresh
capacity admission. No dependency rebuild, cache or instrumentation is included.

Task 13b admits one private baseline runner, root target metadata, baseline docs
and these planning files. Execute the committed native presets in eight fresh
private trees with one job, all four configurations and independent core/fmt
linkage. Reuse retained dependencies read-only with installation disabled.
Native operations require independent preparation review, fresh capacity and
the canonical lease. No dependency build, instrumentation, cache provider,
shared installation or global write is included.

Task 14a admits one confined sanitizer witness runner, one public-header consumer
fixture, sanitizer docs and these planning files. Prepare ASan, UBSan and combined
runtime controls against the qualified P2996 core and runtimes. Native execution
requires independent preparation review, fresh capacity and the canonical lease.
No dependency build, preset expansion, shared write, cache or coverage is included.
Retain the first failed capacity receipt. A separately reviewed rule may admit
only the observed Zed clangd identities and ancestry, with fresh working-directory
and identity checks, CPU limits and all other existing admission guards preserved.

Task 14a1 admits one scratch runner, one source patch, sanitizer docs and these
planning files. Reuse the reviewed confinement, capacity, lease and preservation
guards. Build only private copies of the original and patched ASan runtime, using
the captured 127-object recipe and one replaced object. Require the original
startup timeout and all seven existing sanitizer cases before any later runtime
promotion. Native work requires preparation review and fresh admission; shared
source/build/prefix changes and instrumentation matrices are separate units.

Task 14a2 admits one guard/replacement module, sanitizer docs and these planning
files. Prepare exact expectations for the independently qualified ASan candidate
without changing historical inventory bytes or inherited guard functions. Pure
overlay controls and private sandboxed replacement/restore controls are allowed.
No installed write, compiler/runtime execution, capacity lease or promotion is
included. A separate native operation must bind source/build state, back up the
original, obtain fresh admission and qualify the installed runtime path.

Task 14a3 admits one promotion runner, sanitizer docs and these planning files.
Prepare one exact installed ASan replacement with a retained original backup,
explicit before/after guards and recovery while the canonical lease is held.
Private transaction controls are allowed; native mutation requires independent
preparation review and fresh capacity. Reuse the three qualified witness binaries
for all seven installed-path cases, without a loader-path override. Preserve
source Git state, bound build inputs and unrelated protected state. No compiler
or dependency build, global configuration change or full matrix is included.

Task 14b admits one confined TSan runner, one public-header witness, sanitizer
docs and these planning files. Reuse the qualified installed-ASan preservation
guard and require five TSan/combined clean/error cases with exact loader paths.
Native work requires independent preparation review, fresh capacity and the
canonical lease. No runtime replacement, dependency build, coverage, preset
expansion, shared installation or full matrix is included.

Task 14b1 permits a private original/patched TSan runtime comparison using the
already qualified mapping-object repair and the captured TSan-specific link
recipe. Keep the installed runtime and shared build tree unchanged. Verify the
original startup failure, patched clean startup and deliberate race before any
installed promotion. Require source/object provenance, separate preparation
review, fresh capacity, canonical lease and closed operation receipts.

Task 14b2a prepares a TSan installed-runtime guard against the reviewed private
candidate. Compose the existing ASan overlay with a second exact TSan-row overlay
over the two immutable historical inventories; retain the prior guard chain.
Exercise pure overlays and private confined replacement/restore/refusal controls.
No installed write, native witness, capacity lease or promotion is included.

Task 14b2b prepares one guarded installed TSan replacement from the reviewed
private candidate. Require exact source, tool, prefix and witness identities,
fresh capacity, canonical ownership lease, retained original backup and
unknown-target refusal. Run clean and deliberate-error TSan/TSan+UBSan cases
through the installed loader path; preserve ASan, defaults and unrelated prefix
entries. Collect closure and independent artifact review before completion.

Task 14c admits one confined LSan runner, one public-header witness, sanitizer
docs and these planning files. Reuse the qualified P2996 core, installed runtime,
current ASan/TSan preservation guard and native capacity/lease rules. Require
clean and leak cases in both modes plus signed-overflow detection in the combined
mode, with exact loader paths. Native compiler/runtime execution follows separate
preparation review and fresh capacity. No runtime replacement, dependency build,
shared installation, preset expansion or full matrix is included.

## Appendix C: References

- Review: `reviews/ccm-20261013/SYNTHESIS.md` (§1 verdict, §2 findings, §2b root causes,
  §4 record corrections, §5 runbook, §6 re-plan, §7 automation, §8 decisions, §9 unverified);
  `R4-pwf-audit.md` (this plan's shape and the injector rules); `R8-parallel-plan.md` (waves,
  allowlists); `prevention/C4-coverage-check.md` (binding ticket table, wave-0 set);
  `T2-import-lane-design.md` (CT-21); `codex-sweeps/B-packet-and-t4-state.md` (closure
  prerequisites, T4 state, supersession); `D2-workflow-proposal.md` §4 (stage script);
  `skills/K1-orchestrator-skill-design.md` (CT-25, D27-D41); plan-update reports
  `P1-plan-rewrite-report.md`, `P2-records-update-report.md`, `P3-plan-review.md`.
- Records: `lanes/*.json` (allocation, status), `retros/*.md` (gate), `ticket-ledger.md`
  (GitHub state), `skill-invocations.md`, `findings.md` (history and research pointers),
  `progress.md` (dated receipts; the injector shows its last 20 lines).
- Authority: `docs/agents/claude-takeover.md`, `docs/agents/claude-team.md`,
  `docs/agents/codex-task-orchestration.md`, `docs/agents/ticket-retro.md`,
  `docs/accepted-decisions.md` (C++26 P2996 core, incremental migration), `CODING_STANDARDS.md`.
- Injector: `~/.claude/plugins/cache/planning-with-files/planning-with-files/3.24.0/`
  (`scripts/inject-plan.py`, `scripts/check-complete.sh`, `scripts/phase-status.sh`); the
  SessionStart and UserPromptSubmit views carry this file's first 50 lines (legacy) or the
  Goal, Next Step, Current Phase, phase count, in_progress phase and last three decisions
  (`PWF_INJECT=smart` or `.mode` = `inject-smart`); PreToolUse carries the first 30 lines.

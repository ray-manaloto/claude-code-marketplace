# X4: fidelity sweep of session ccm-20261013-check (b74a0bf1-dd98-44d5-8122-e47e12ad4fd2)

Written 2026-10-14 ~04:45Z by X4 (Fable high, read-only), the job R6 did for the dead session.
Sources: the session transcript (2,284 lines), its 64 subagent files (`agent-*.jsonl` +
`.meta.json`; a subagent's final report = its last assistant text block), the planning records
under `P` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/` (`RV` =
`P/reviews/ccm-20261013/`), git (`git log 28fedf1..HEAD`, `git worktree list`,
`git cat-file`, `git merge-base --is-ancestor`, `ls-remote`), `gh run list`, and the two memory
notes. Transcript line numbers are `T:L<n>`. Times UTC.

## Scope

- 64 agents found (the brief expected ~45): 2 explorers, D1/D2, R1–R8, one claude-code-guide
  hook-facts check, S1 (one fork, resumed twice by SendMessage at T:L790 and T:L1124), M1, the
  three user forks, sweeps A/B/C, C1–C4, T1/T2, P1–P3, K1/K2, four eval runs K2 spawned, I1,
  I1b, I1b-review, I1c, I2, I3, I3-review, I3b, the allocator, the three w0 implementers, three
  cold reviews, three retro-writers, two focused re-reviews, two mergers, N2, the handoff
  writer, and X1–X4 (X1 and X2 finished after the handoff was written; X3 and X4 still running
  at the time of writing).
- Records checked: `task_plan.md` (handoff lines 9-27, Decisions D1–D49, Phases 3–7),
  `progress.md` (entries from the 2026-10-13 review onward, NEXT), `findings.md`,
  `ticket-ledger.md`, `lanes/*.json`, `retros/{ccm-20261013-session,w0-docs,w0-decisions,
  gate-hooks}.md` and the lane-worktree `retros/w0-doctor.md`, `decisions.jsonl`,
  `RV/SYNTHESIS.md`, `RV/phase3/*.md`, `RV/phase3/w0/*.md`, `RV/phase3/HANDOFF-2026-10-14.md`,
  `RV/prevention/*.md`, `RV/skills/*.md`, `RV/codex-sweeps/*.md`.
- Read-only: no repo file other than this report was written; git untouched.

## 1. Agent table

Fidelity: faithful = every SHA, rc, verdict, proposal and pending decision in the final report
is in a record; partial = a stated item is missing; lost = nothing recorded; contradicted = a
record says otherwise. "Where" cites the record that carries the report.

| # | Agent id (prefix) | Description | Model/type | Final-report gist | Where recorded | Fidelity | Dropped items |
|---|---|---|---|---|---|---|---|
| 1 | ac53bfee | Explore .planning records state | Explore | Inventory of records at session start | internal input to the plan-mode questions (T:L375) | n/a | none |
| 2 | a81e410b | Digest main session narrative | Explore | Dead-session narrative | internal | n/a | none |
| 3 | a3018456 | D1 mattpocock skills study | fable gp | 27 skills + 29 docs read; five constraints; cache = upstream `49dd158` | `RV/D1-mattpocock-skills-reference.md`; `task_plan.md` Workflow (306-333) | faithful | none |
| 4 | a7c970ad | R5 git state and settings audit | opus gp | 2 P1 (personal keys staged; hooks:install before publish refuses), settings split §B | `RV/R5-git-state.md`; SYNTHESIS; D2, D4; I1 split | faithful | none |
| 5 | ad8973cc | R3 Codex sweep coverage | fable gp | 175 threads; 2a14 dependency P1; no full re-sweep, three bounded sweeps | `RV/R3-codex-coverage.md`; D11; CT-21 | faithful | none |
| 6 | ab2ce3cc | R4 pwf audit | fable gp | plan without phases; 430 KB re-injected; `PWF_PLAN_ROOT` pin; stay legacy + `inject-smart` | `RV/R4-pwf-audit.md`; `findings.md:199-205`; Phase 3 step 9 | faithful | `.mode` still unwritten (recorded as open in step 9) |
| 7 | aac56b9b | R6 fidelity of the dead session | opus gp | 1 P1 (merger fork moved settings; staged merge unrecorded), 4 P2 | `RV/R6-subagent-fidelity.md`; SYNTHESIS P1-1/P1-4 | faithful | none |
| 8 | af58b706 | R7 automation candidates | opus gp | `lane:integrate`, `lane:set`, `plan:log`, `lane:brief`, `lane:allocate`; unwired test; gate false positive | `RV/R7-automation.md`; CT-05/12/14/15; CT-02b | faithful | none |
| 9 | ae3dd4cd | D2 workflow proposal | fable gp | 14-stage workflow, 12-prompt user script, 11 user decisions | `RV/D2-workflow-proposal.md`; `task_plan.md` Workflow | faithful | none |
| 10 | a28d8c8e | Verify three hook facts | claude-code-guide | `env` literal; subagent payload fields; deny > allow | used by I1c (`progress.md:459-460` "env values are literal") | faithful | none |
| 11 | add87337 | R1 workflow fidelity | fable gp | P1 3/P2 7/P3 10; four of five stages file-guided | `RV/R1-workflow-fidelity.md`; SYNTHESIS; Phase 5 | faithful | none |
| 12 | a3bb4dc7 | R2 spec and tickets | fable gp | 3 missing grilling decisions; CT-12…CT-16; preview unpublishable | `RV/R2-spec-tickets.md`; I3 builder fix; CT rows | faithful | none |
| 13 | a8bda2e3 | R8 parallelization plan | fable gp | wave 0 serial, four wave-1 lanes, conflict rules | `RV/R8-parallel-plan.md`; `task_plan.md:328-330`; Phase 6 | faithful | none |
| 14 | a258349e | M1 meta-review | fable gp | SAFE WITH CORRECTIONS; 13 P1 confirmed; 19 corrections | `RV/M1-meta-review.md`; applied by S1 revision 1 (T:L790) | faithful | none |
| 15 | aexplain-the-issues | user fork: settings.json issues; fnox 1.39.0 | fork | settings privacy issue; fnox facts; in-repo mde refs removed (N1 only); global mde items need admission | `RV/N1-settings-and-secrets.md`; `findings.md:188-198`; `claude-takeover.md` fnox line | partial | the user's mid-turn instruction "remove all references to mde" leaves three global-config follow-ups (fnox `config.toml` header and `service = "mde-fnox"` keychain name; `~/.config/mise/config.toml` `mise-env-fnox` comment and `MDE_PROJECT_DIR` block; 145 `installed_plugins.json` entries) recorded only at T:L813; no record lists them (finding P2-6) |
| 16 | a5e8241f | Codex sweep A | fable gp | 266 files: import 68, keep-private 149, superseded 49; accepted-decisions block only in 2a14 | `RV/codex-sweeps/A-*.md/json`; D24; CT-21; hunks 1-2 applied (I3, I3b) | faithful | none |
| 17 | a2959a66 | Codex sweep B | fable gp | closure prerequisites #62–#78; T4 STOPPED 3/3; ledger stale ownership | `RV/codex-sweeps/B-*.md`; `ticket-ledger.md` closure table; D19/D25; supersession notice (I3) | faithful | none |
| 18 | a0bfc31e | Codex sweep C | fable gp | nine dead children wrote only private packets; replacement sentence | `RV/codex-sweeps/C-dead-children.md`; `claude-takeover.md` sentence (I3) | faithful | none |
| 19 | aa7e4357 | C1 root causes | fable gp | 39 chains, 14 classes; two new causes (autoCompact off; agents dir at start) | `RV/prevention/C1-root-causes.md`; SYNTHESIS §2b; P1-14/P1-15 | faithful | none |
| 20 | a3eed649 | T1 snapshot | opus gp | 454 files, two copies, verify rc 0, 101 missing paths | `P/imports/codex-worktrees-20261013/T1-*`; D24 | faithful | none |
| 21 | ashould-the-ccm | user fork: close the dead session? | fork | close; no resume, no `/clear` there; owner line to name this session | `task_plan.md:4-7` owner line | faithful | none |
| 22 | a0d9ea4d | T2 import lane design | fable gp | import 119 files; CT-08 not a prerequisite; CT-21 as fifth wave-1 lane | `RV/T2-*`; `lanes/ct21-codex-imports.json`; CT-21 row; D24 | faithful | none |
| 23 | a07ef2f2 | C2 prevention design | fable gp | 14 designs; wave-0 set; CT-22…CT-30 | `RV/prevention/C2-prevention-design.md`; C4 reconciliation | faithful | none |
| 24 | a1c25df2 | C3 detection design | fable gp | 58 finding ids, `dev/doctor/`, surfaces | `RV/prevention/C3-detection-design.md`; w0-doctor | faithful | none |
| 25 | a181a5e7 | C4 coverage check | fable gp | APPROVE WITH CHANGES; 5 gaps; 3 wrong claims; CT-01…CT-24 (+02b); W0-1…W0-7 | `RV/prevention/C4-coverage-check.md`; SYNTHESIS §2b; Phase 4; D22/D23/D26 | faithful | none |
| 26 | a7f99021 | S1 synthesis (fork, resumed twice) | fork | SYNTHESIS rev 2: P1 15/P2 25/P3 31; D21–D26; retro gate rc 0 | `RV/SYNTHESIS.md`; `retros/ccm-20261013-session.md`; D21–D26 | faithful | none |
| 27 | a540bccd | P1 rewrite task_plan | fable gp | 830-line plan; probes; `.mode` open | `task_plan.md`; `RV/P1-plan-rewrite-report.md` | faithful | none |
| 28 | a34d9753 | P2 progress/findings/ledger | opus gp | archive applied; flagged D12 conflict | `progress-archive-2026-10-13.md`; `D12-applied` row; N2 | faithful | none |
| 29 | aa6e19d3 | K1 skill design | fable gp | `ticket-frontier`; 7 blocking + 8 default questions; #21 first C++ ticket; gate G | `RV/skills/K1-*.md`; D27–D41; CT-25; `findings.md:206-210` | faithful | none |
| 30 | a86dbaa7 | K2 build ticket-frontier | fable gp | skill + 29 tests + evals; 4 defaults; §7 parent hunks (mise `test:frontier`, `check.py`, `claude-team.md`) | `.claude/skills/ticket-frontier/`; D42–D45; CT-25 row | partial | the §7 hunks are neither applied nor listed as deferred; the 29 frontier tests have no mise task (finding P2-5) |
| 31 | aa7c44e6 | P3 review/fix plan files | fable gp | 22 fixes; D27–D41 recorded; `D12-applied`; CT-25 | `RV/P3-plan-review.md`; `task_plan.md` | faithful | none |
| 32-35 | a6d38de4, a3f483a7, aea71359, a96c1b9c | K2 eval runs (3 with skill, 1 baseline) | Explore | eval 4 could not run (Explore is read-only); others ran | `RV/skills/K2-build-report.md` (eval loop) | n/a (K2-internal) | none |
| 36 | a3a6aa2d | I1 group 1 | opus implementer | halted: `test:hooks` rc 1 (MISE_* not scrubbed); settings split done; D42–D45 added | `progress.md:436-450`; `RV/phase3/I1-group1-report.md`; AskUserQuestion T:L1405 | faithful | none |
| 37 | ad4e27d6 | I1b lane fix | opus implementer | `697e1da`; red test; `test:hooks` rc 0 (14); trailer Opus 5.5 | `lanes/gate-hooks.json` `lane_commit`; `retros/gate-hooks.md:44-45`; `RV/phase3/I1b-lane-fix-report.md` | partial | no `progress.md` entry for group 1b and the user's route answer ("Fix on the lane, re-review, re-merge", T:L1406 01:25:51Z) is not a Decisions row (finding P2-3) |
| 38 | a2eb3803 | I1b focused re-review | fable reviewer | PASS-with-P3 (trailer, owned_paths, retro row) | `RV/phase3/I1b-review.md`; `progress.md:454-459` | faithful | none |
| 39 | a0c12ee7 | I1c re-merge | opus implementer | M `760b154` (parents `9cd396a 697e1da`); trailer not amended; `PWF_PLAN_ROOT` not added (CT-23) | `progress.md:452-466`; Phase 3 step 6 | faithful | `ticket-ledger.md:152` CT-23 row does not carry the `PWF_PLAN_ROOT` item (P3-4) |
| 40 | a7b3f239 | I2 first publish | opus implementer | `0a68dce`; CI 38497739145; digest `a21be5fe…` | `progress.md:468-476`; Phase 3 step 8 | faithful | none |
| 41 | af17b2e1 | I3 group 3A | opus implementer | 93 paths staged; corrections; hunk 2 held for the user | `progress.md:478-495`; AskUserQuestion T:L1622 | faithful | none |
| 42 | afdd5077 | I3 cold review | fable reviewer | PASS-with-P2/P3; tree `d571874d`; P2-1 ledger mid-merge, P2-2 D-all | `RV/phase3/I3-review.md`; fixes in `progress.md:497-511` | faithful | none |
| 43 | a42ad63b | I3b fix + publish | opus implementer | `d420a7e`; CI 38504716758; `${CLAUDE_SKILL_DIR}` preamble shell-tested only | `progress.md:497-511`; Phase 3 step 10 | faithful | "preamble not verified in a live skill run" is unrecorded (P3-5) |
| 44 | aef0b4de | W0 allocator | opus implementer | five lanes; A = `c21941f`; base_sha null; no C++ slot; docs model | `progress.md:513-521`; `RV/phase3/W0-allocation-report.md`; D46; `lanes/w0-*.json` | faithful | none (the three "decisions for you" were taken by the parent and told to the user at T:L1688; see §4) |
| 45 | a5459df0 | w0-doctor implementer | opus implementer | `64e46d4` (impl `bb0e2a4`); deviations; proposed `claude-team.md` sentence | `RV/phase3/w0/w0-doctor-receipt.md`; HANDOFF §3.5 (item 3 supersedes the sentence) | faithful | none |
| 46 | a84be6a9 | w0-decisions implementer | opus implementer | `f9c8848` (impl `7649ca7`); DL-1..DL-50; mise parent hunk | `RV/phase3/w0/w0-decisions-receipt.md:9-21`; HANDOFF §3.1 | faithful | none |
| 47 | ad2b746f | w0-docs doc-writer | sonnet doc-writer | `4854db1`; 8 paths; deviations 1-5 | `RV/phase3/w0/w0-docs-receipt.md`; `retros/w0-docs.md` | faithful | none |
| 48 | aaa49784 | w0-docs cold review | fable reviewer | PASS-with-P2 (manifest stale) + 5 P3; could not write the file | `RV/phase3/w0/w0-docs-review.md` (saved by the parent); `lanes/w0-docs.json` | faithful | none |
| 49 | a2734b67 | w0-decisions cold review | fable reviewer | PASS-with-P3; D46 has no row; mise hunk valid | `RV/phase3/w0/w0-decisions-review.md`; D46 row (`ecc0ad7`) | faithful | none |
| 50 | aefe2013 | w0-docs retro-writer | fable retro-writer | `749577d`; proposals 1-6 | `retros/w0-docs.md`; manifest rebuilt `80f3190`; D47; `planning-records.md` sentence; row-20 split | faithful | audit row 39 deferral (split Hook composition / Context budget out of `claude-team.md` when CT-23 lands, "record it in the ticket ledger") is not in the CT-23 row (P3-6) |
| 51 | a4c00ef9 | w0-decisions retro-writer | fable retro-writer | `922eab4`; parent edits 1-5; 83 vs 80 lines | `retros/w0-decisions.md`; D46, D48, `dev/AGENTS.md` bullets (`ecc0ad7`); issue-tracker sentence to wave-1 CT-24 (`progress.md:543`) | faithful | none |
| 52 | a57209e4 | w0-doctor cold review | fable reviewer | PASS-with-P3 on `64e46d4`; P3-1..P3-5 | `RV/phase3/w0/w0-doctor-review.md`; retro repairs | faithful | none |
| 53 | ab7e4624 | w0-docs merger | opus implementer | M `e40a62a`, R `80f3190`, P `3bb4fd3`, CI 38509610914; incidents: mise `timeout` shim unversioned; no D46 row; Opus ran with Fable trailer | `progress.md:523-532`; `RV/phase3/w0/w0-docs-merge-report.md` | faithful | "mise `timeout` shim has no version set" is recorded only in the merge report (P3-7); `progress.md:525` says "no git hooks installed" (P2-4) |
| 54 | adcfb2b8 | w0-decisions re-review | fable reviewer (medium) | PASS-with-P3; 35/46 not 36/46 | `RV/phase3/w0/w0-decisions-rereview.md`; D48 text | faithful | none |
| 55 | a73e6b08 | w0-doctor retro-writer | fable retro-writer | `f1bbc8d`; items 1-7; behaviour changed → re-review | worktree `retros/w0-doctor.md`; HANDOFF §3.3/§3.5; `RV/phase3/w0/w0-doctor-retro-receipt.md` | faithful | none |
| 56 | aab01359 | N2 incident review | fable gp | timeline; root cause; `brief_lint`, records guard, `BLOCKED-BY-RULE`; retroactive D12 rows | `RV/prevention/N2-pending-decision-incident.md`; HANDOFF §3.4/§6; `progress.md:552-555` | faithful | ticket-ledger CT-19/CT-22 rows do not cite the N2 items (P3-8); N2 §5 cites `task_plan.md:264`, now line 277 (P3-9) |
| 57 | await-for-all | user fork: pace, tuning, reprioritise, /clear vs /compact | fork | start CT-21 + D7 spike; D49 tuning; `/clear`; 611,587 tokens; 600K checkpoint (wrong, 550K) | `RV/phase3/FORK-progress-and-context-review.md`; D49; HANDOFF §2(c)-(g); `progress.md:546-552` | faithful | none (the 600K slip is corrected in HANDOFF line 4) |
| 58 | acfb7f51 | w0-doctor re-review | fable reviewer (medium) | PASS, no findings, `f1bbc8d` | `RV/phase3/w0/w0-doctor-rereview.md`; `task_plan.md:13`; `progress.md:555` | faithful | none |
| 59 | ab2736c0 | w0-decisions merger | opus implementer | M `c7054fd`, R `ecc0ad7` (amended once), P `21af565`, CI 38510694690; deferred mise rows | `progress.md:534-544`; `RV/phase3/w0/w0-decisions-merge-report.md` (post-publish fields unstaged) | faithful | none |
| 60 | a894b585 | Handoff writer | opus implementer | handoff lines 9-23, Next Step 25-27, D49; HANDOFF file; probes; 550K correction | `task_plan.md:9-27`; `progress.md:546-569`; `RV/phase3/HANDOFF-2026-10-14.md` | faithful | written before the user's 04:27Z request; see P1-1 |
| 61 | a2454eae | X1 Claude Code 2.1.296 review | claude-code-guide | (completed after the handoff) | `RV/phase4-prep/X1-claude-code-2.1.296.md`; relayed at T:L2289 | not yet folded | P1-1 |
| 62 | ac4dc42a | X2 dependency updates | opus gp | (completed after the handoff) | `RV/phase4-prep/X2-dependency-updates.md` | not yet folded | P1-1 |
| 63 | a49d6b00 | X3 zero-loss restart design | fable gp | running | none yet | pending | P1-1 |
| 64 | ab33272d | X4 (this sweep) | fable gp | this file | `RV/phase4-prep/X4-session-fidelity.md` | n/a | n/a |

## 2. SHA and claim verification (task_plan.md lines 1-30, HANDOFF §1-§3)

| Claim | Source line | Check | Result |
|---|---|---|---|
| HEAD `21af565` = remote | task_plan:10; HANDOFF:14-15 | `git rev-parse HEAD` = `21af5650…`; `ls-remote` = `21af5650…` | verified |
| CI research-fast 38510694690 success, 04:19:59Z | task_plan:10; HANDOFF:16 | `gh run list`: 38510694690 completed success, head `21af5650`, updated 04:19:59Z | verified |
| Earlier CI ids 38509610914 (`3bb4fd3`), 38504716758 (`d420a7e`), 38497739145 (`0a68dce`) | progress.md | all `completed success` with the stated heads | verified |
| w0-docs integrated: lane `749577d`, merge `e40a62a` (parents `c21941f 749577d`), published `3bb4fd3` | task_plan:11,106; HANDOFF:27 | `cat-file` commit ×3; `749577d` ancestor of `21af565`; `e40a62a` parents as stated | verified |
| w0-decisions integrated: lane `922eab4`, merge `c7054fd` (parents `3bb4fd3 922eab4`), records `ecc0ad7`, published `21af565` | task_plan:11,104; HANDOFF:28 | verified by `cat-file` and ancestry; `aaa585a` (the pre-amend R) still exists as a dangling commit | verified |
| w0-doctor READY `f1bbc8d` on `64e46d4` on `bb0e2a4`, base `c21941f`; not an ancestor of `21af565`; `21af565` not an ancestor of `f1bbc8d` (expect rc 1) | task_plan:13; HANDOFF:26,47-49 | `merge-base --is-ancestor`: `c21941f`→`f1bbc8d` rc 0; `64e46d4`→`f1bbc8d` rc 0; `21af565`→`f1bbc8d` rc 1; `diff --stat 21af565...f1bbc8d` 15 files +891/-3 | verified |
| review PASS-with-P3 on `64e46d4`, re-review PASS | task_plan:13; HANDOFF:26 | `w0-doctor-review.md:5` "PASS-with-P3"; `w0-doctor-rereview.md:5` "PASS for integration (no findings)" | verified |
| Worktree HEADs: w0-doctor `f1bbc8d`, w0-docs `749577d`, w0-decisions `922eab4`, gate-hooks `697e1da`, a06-unit3 `93402c0`, c1 `6c09b7f`, codex-session-history `ea893a8`, nav `6840342`, retro-gate `82c351f`, rf-env-scrub `281a198`, team `ea8c8c9`; 18 Codex worktrees | HANDOFF:24-32 | `git worktree list` | verified (18 `~/.codex/worktrees/*` entries) |
| Index: nothing staged; no `MERGE_HEAD`; porcelain 17 entries | HANDOFF:17; handoff writer | `git diff --cached` empty; `.git/MERGE_HEAD` absent; `git status --porcelain | wc -l` = 17 | verified |
| Unstaged list | HANDOFF:18 | matches `git status` except `w0-doctor-records-{brief,review-brief}.md` (untracked, omitted) and `phase4-prep/X*.md` (written after) | partial (P3-1, P1-1) |
| w0-doctor-records / w0-session-hooks records carry `base_sha` `c21941f` | task_plan:18; HANDOFF:29 | `lanes/*.json` | verified |
| ct21 record `base_sha` TBD, status stale ("waits for the gate-hooks merge") | HANDOFF:30,82-84 | `lanes/ct21-codex-imports.json` | verified (stale text acknowledged in §2(d)) |
| `hooks:install` not run; hk live through the global install | HANDOFF:20 | `.git/hooks` samples only; no `core.hooksPath`; `~/.gitconfig` carries `hook.hk-pre-commit/commit-msg/pre-push` config-based hooks | verified (progress.md:525 contradicts, P2-4) |
| Trailers: lane commits by Opus/Sonnet carry their own model line; merges, records, publishes carry Fable | HANDOFF §4 "three repeats" | `697e1da`, `760b154`, `7649ca7`, `f9c8848`, `bb0e2a4`, `64e46d4` = Opus 5.5; `4854db1` = Sonnet 5.5; all others Fable 5.1 | verified (the merge `760b154` also carries Opus, as I1c reported) |
| Merge-base of `21af565` and `f1bbc8d` is `c21941f` ("the lane is on c21941f; ort merges it") | HANDOFF:48 | ancestry above | verified |
| HANDOFF §2(b) step 4 "14 tests after the THRESHOLDS hunk" | HANDOFF:65 | re-review: 13 OK on `f1bbc8d`; +1 = 14 | consistent |
| HANDOFF §3.4 "last id DL-50, expect DL-51, DL-52"; `receipt DL-52 --path … --rc 0` | HANDOFF:152-162 | `decisions.jsonl` 50 rows, last DL-50; `plan_decide.py` receipt accepts `--rc`; receipt refuses a path outside the ledger root (repo-relative path is inside) | verified |
| Phase 3 step 5 "test:hooks (13)" | task_plan:64 | I1c and I1b report 14 tests at `697e1da` (13 was the `e12cf04` count) | stale count (P3-10) |
| Remote branch tip equals HEAD; nothing ahead | task_plan:10 | `ls-remote` | verified |

## 3. Deferred-hunk completeness (HANDOFF §3 vs sources)

| Hunk | Source | HANDOFF §3 | Verbatim? |
|---|---|---|---|
| w0-decisions `mise.dev.toml` rows `plan:decide`, `test:plan-decide`, `check:research` depends | `w0-decisions-receipt.md:9-21` | §3.1 | yes, byte-equal TOML; depends line and "unverified passthrough" carried |
| w0-docs `dev/check.py` manifest-hash rule | `retros/w0-docs.md:57-66` (literal edit 2) | §3.2 | yes, byte-equal; placement sentence carried; note that the rebuild (edit 1) landed in `80f3190` |
| THRESHOLDS table test | worktree `retros/w0-doctor.md:83-95` (item 5) | §3.3 | yes, byte-equal; `parent hunk: dev/test_doctor.py` MERGE_MSG line carried |
| Retroactive D12 rows | `N2-pending-decision-incident.md` §5 | §3.4 | yes; HANDOFF resolves `DL-<op>` to `DL-52` and adds the python fallback and the en-dash note |
| w0-doctor retro items 1-7 | worktree `retros/w0-doctor.md:61-97` | §3.5 | items 1-6 byte-equal; item 7 updated with the repair SHA `f1bbc8d` and "re-review PASS" (the retro's placeholder text said "focused re-review … requested"), which is the correct post-re-review state |
| w0-doctor receipt's `claude-team.md` sentence | `w0-doctor-receipt.md` | §3.5 trailing note | carried as superseded by item 3 |
| w0-docs retro edits 1, 3-6 | `retros/w0-docs.md:54-84` | applied in `80f3190` (manifest, `planning-records.md` sentence, `lanes/w0-docs.json`, row-20 split) or parked as D47 | complete |
| w0-decisions retro parent edits 1-5 | `retros/w0-decisions.md` "Parent edits" | D46 row and `dev/AGENTS.md` bullets in `ecc0ad7`; mise hunk §3.1; rule 14 = D48; issue-tracker sentence → wave-1 CT-24 (`progress.md:543`) | complete |
| K2 §7 parent hunks (`mise.dev.toml` `test:frontier` row after `test:hooks`; `dev/check.py` alternative; `claude-team.md` section) | `RV/skills/K2-build-report.md:220-270` | absent | missing (P2-5) |
| w0-docs retro audit row 39 (split `claude-team.md` when CT-23 lands; record in the ledger) | `retros/w0-docs.md:39` | absent from the CT-23 ledger row | missing (P3-6) |

## 4. Decisions reconciliation

User answers in the transcript (AskUserQuestion results):

| T:L | Time | Question(s) | Answer | Recorded as |
|---|---|---|---|---|
| 376 | 21:47:54Z | Stuck merge; Codex sweep depth; Scope | "Review first, repair after approval"; "Audit the 4 briefs"; "option 1 only after subagents have fully reviewed the docs… create and run a subagent to review every skill… synthesize and propose a plan" | D1 (finish, after approval), D11; the third answer drove D1/D2 agents and the Workflow section (task_plan:306-333). No D row names the "stop after repair + handoff" scope choice (see P2-2) |
| 882 | 22:57:35Z | Approve the 20 defaults; sweeps; wave-1 prep | NOT approved ("first, did we identify the cause…"); sweeps yes; prep 4 lanes per R8 | correct: the parent held Phase 3 (T:L886) and ran C1–C4; D11 "run them"; wave-1 prep folded into the allocation/frontier work. Not recorded: the user chose "4 lanes per R8" (the plan now cuts five wave-0 lanes and lists four wave-1 lanes + CT-21; consistent in substance, unrecorded as an answer, P3-11) |
| 1163 | 23:59:06Z | Approve 26 defaults; **who runs wave 0** (same run vs next session); **autoCompact flip** | rejected: "wants to clarify"; no answers | the first was re-asked at T:L1353; the wave-0 question was never re-asked and the parent started wave 0 in this session at 03:11Z (T:L1661) with no Decisions row (P2-2); the autoCompact flip is correctly "pending user" |
| 1263 | 00:15:57Z | K1 blocking 1-4 | all recommended defaults | D27, D28, D29, D30 |
| 1276 | 00:26:39Z | K1 blocking 5-7 | all recommended defaults | D31, D32, D33 |
| 1354 | 00:52:05Z | K2 four defaults; Phase 3 | "Accept all four defaults"; "Approve D1–D41 defaults, start Phase 3" | D42–D45; D1–D26 approved, D27–D41 accepted, `D-all` row; `D12-applied` |
| 1406 | 01:25:51Z | `test:hooks` route | "Fix on the lane, re-review, re-merge" | lane record and `retros/gate-hooks.md:44-45` carry the fix; no Decisions row and no group-1b `progress.md` entry (P2-3) |
| 1623 | 02:58:14Z | accepted-decisions hunk 2 | "Yes, apply it in this publish" | `D-all` row ("hunk 2 applied on the user's word"); `progress.md:504-506` |

task_plan vs `decisions.jsonl`:

- D1–D45 = DL-5..DL-49 (`decision` kind, text byte-identical per the cold review). D46 = DL-50
  (`decision`, "decided by the parent 2026-10-14"). DL-1..DL-4 are pending operations (#91
  relabel, draft PR, T4 Phase C, `/to-tickets`); `approved()` is empty, as HANDOFF §5 says.
- D47, D48 (pending user) and D49 (parent, routine) have no DL rows: the ledger was seeded at
  03:34Z before they existed and the CLI is deferred to the w0-doctor integration. HANDOFF §5
  does not say so (P3-12).
- D46 was not a user answer. `task_plan.md:276` says "accepted 2026-10-14" and HANDOFF §5 lumps
  it into "accepted: D27-D46"; DL-50 and the user-facing message (T:L1688, "three routine calls
  I made so you don't have to") state the truth (P3-2).
- D49 is a parent decision, labelled as such (task_plan:281). Fine.
- Parent decisions taken without a user answer and without a Decisions row: wave 0 run in this
  session (P2-2); the docs lane on Sonnet via the `doc-writer` definition (told to the user at
  T:L1688, recorded in `lanes/w0-docs.json` `writer_model` and the retro; acceptable);
  `base_sha` fill (recorded).
- No decision is recorded as user-approved that the user did not answer: D1–D26 "approved
  2026-10-13" rest on the 00:52:05Z answer "Approve D1–D41 defaults" (local date 2026-10-13).
- SYNTHESIS §8 lists 26 decisions; task_plan D1–D26 match in number.

## 5. Side-agent notes and mid-turn user messages: dispositions

| Note / message | T:L | Disposition | Recorded |
|---|---|---|---|
| Fork `explain-the-issues` (settings.json, fnox 1.39.0, mise global config) | 751-843 | N1 written; parent relayed at T:L766; fnox ≥ 1.39.0 line in `claude-takeover.md` (I3); fnox facts in `findings.md:188-198` | yes |
| Mid-turn in that fork: "remove all references to mde … update docs/agent md/config" | fork 22:51:39Z | in-repo: only N1 had references, fixed; global config items left for a dotfiles-side admission (relayed T:L813) | **no record of the three pending global items** (P2-6) |
| Mid-turn in that fork: "any open/pending items?" / "does the parent have this?" | fork 22:54Z | answered; parent relayed T:L834 | yes |
| Fork `should-the-ccm-20261013` | 967 | close, no resume/`/clear`; owner line | `task_plan.md:4-7` |
| Side-agent note: tip depends on untracked `2a14` data | 939 | T1 snapshot + T2 lane design; CT-21; D24; `findings.md`; `ticket-ledger.md:150` | yes |
| Side-agent note: planning rewrite ran ahead of approval | 1995 | N2 incident review; `D12-applied`; retroactive rows (HANDOFF §3.4); parent explained the state (T:L2006) | yes |
| Fork `wait-for-all` | 2102 | FORK review; D49; HANDOFF §2; `/clear` route | yes |
| User turn 00:01:34Z (synthesize; implement-spec configurable; C++ always active; 50% ceiling; scheduler agent; retro automation; skill-creator loop) | 1173 | P1–P3, K1/K2, D27–D45, `frontier.toml`, `frontier-scheduler`, CT-25 | yes |
| User turn 04:27:36Z (X1–X4; handoff; zero-loss restart) | 2235 | X1, X2 done; X3, X4 running; final handoff writer pending | not yet in the records (P1-1) |

## 6. Unprocessed notifications

Every `task-notification` in the transcript (58, listed by agent id) is followed by a parent
action or relay in the next turn: explorers → plan-mode questions; D1/D2/R* → S1; S1 (×3) → M1,
the 22:55Z and 23:58Z decision rounds; `explain` (×4) → T:L766/813/834; sweeps/T1/C1 → relays and
C2/C3/T2 dispatch; C2/C3/C4 → S1 resume; P2/K1 → relays and the question rounds; P3/K2 →
decision round at T:L1353; I1 → route question; I1b → re-review; I1b review → I1c; I1c → I2;
I2 (×3) → I3; I3 → cold review; review → hunk-2 question → I3b; I3b → allocator; allocator →
three implementers; lane receipts → reviews; reviews → retro-writers; retro receipts → mergers
and re-reviews; `wait-for-all` → the hold-`/clear` message; mergers → handoff writer; handoff
writer → the `/clear` go. X1's completion is relayed at T:L2289. Nothing unprocessed, except
that X2's notification and file (`phase4-prep/X2-dependency-updates.md`, 04:34Z) post-date the
last transcript line I read; the parent still has to fold X1–X4 (P1-1).

## 7. Memory notes

`claude-session-environment-gotchas.md`: accurate against C1, SYNTHESIS P1-14/P1-15, D21 and
`task_plan.md:303-304` (977K death, 27 agents, fork died in 30 s, agents dir at session start,
user-typed workflow skills). X1 reports that the current docs contradict the mid-session
agent-reload claim; the note should say "verify with `/agents`" once X1 is folded (P3-13).

`marketplace-lane-loop-2026-10-14.md`:
- line 18 "exceeded its own 600K checkpoint": wrong; the table in `claude-team.md:117-120` and
  HANDOFF line 4 say checkpoint 550K (fork deny 500K, hard 650K). The parent's last turn read
  611,587 tokens, above 550K (P2-7).
- line 17 "the decisions ledger `dev/plan_decide.py pending` is the check": there is no
  `pending` subcommand (`main()` registers `approval`, `operation`, `decision`, `receipt`);
  `pending()` is a Python function for CT-17/`brief_lint` to import (P2-8).
- line 15 "PreToolUse gate can deny command text containing `git merge`/`git push`": matches
  `dev/hooks/pretooluse_gate.py:2`.
- line 14 hk live globally: matches `~/.gitconfig` `hook.hk-*` entries.
- lines 12, 13, 16, 19 ("happened 3 times", one owner per hot spot, never brief a pending
  decision, doctor first after `/clear`): consistent with FORK, N2 and HANDOFF.

## 8. Findings

P1 (a wrong or missing fact the next session would act on)

- P1-1 `task_plan.md:21` "Agents running at /clear: none" and `progress.md:558` "Agents running
  at /clear: none"; HANDOFF §1 row "Agents running | none" and the Unstaged row. Since the
  handoff was written (04:26Z) the user asked for X1–X4 (T:L2235, 04:27:36Z); X1 and X2 have
  finished and written `RV/phase4-prep/X1-claude-code-2.1.296.md` and
  `RV/phase4-prep/X2-dependency-updates.md`; X3 and X4 are running; a final handoff writer is
  promised (T:L2239). X1's "now" items (Stop/SubagentStop `onFailure: block` inert, so
  fail-closed must live in `stop_gate.py`/`subagent_stop_gate.py`; `claude -n <name>` start;
  `/skill-doctor`, `/doctor prompt-audit`; `.claude/rules` loading after 2.1.293; agent
  hot-reload to re-test) are in no planning record. Correction, after X3/X4 finish:
  `task_plan.md:21` → "Agents running at /clear: none (X1–X4 finished; outputs
  `reviews/ccm-20261013/phase4-prep/X{1,2,3,4}-*.md`, folded into §2 of the HANDOFF)";
  HANDOFF §1 Unstaged row += "`RV/phase4-prep/X1-…md`, `X2-…md`, `X3-…md`, `X4-…md`";
  HANDOFF §2 += one step per X1 "apply now" item and per X2 version bump that the next session
  must act on; `progress.md:558` same sentence.

P2 (inconsistency)

- P2-2 Wave 0 was built in this session without the user's answer. The question "Who runs the
  wave-0 prevention code? Same run / Next session" (T:L1162) was rejected for clarification
  and never re-asked; the parent announced group 4 at T:L1661 (03:11Z). The plan-mode scope
  answer (T:L376, "option 1" = stop after repair + handoff) is the only user word on scope.
  No Decisions row records either. Correction: `task_plan.md` Decisions, append
  `| D50 | Wave 0 (prevention lanes) built in session ccm-20261013-check after the second
  publish; the 23:59Z question "same run vs next session" was rejected for clarification and
  not re-asked; the user was informed at 03:11Z and did not object | parent decision
  2026-10-14, not user-answered |`; HANDOFF §5 add the same sentence under "Recorded deviation".
- P2-3 The user's `test:hooks` route answer (T:L1406, 01:25:51Z, "Fix on the lane, re-review,
  re-merge") and group 1b have no `progress.md` entry and no Decisions row; the I1c entry
  (`progress.md:452-466`) references "I1b review P3-1" without the lane fix itself.
  Correction: insert after `progress.md:450`: `- 2026-10-13 (Phase 3 group 1b, lane fix on
  the user's route answer 01:25:51Z "fix on the lane, re-review, re-merge"): claude/gate-hooks-wiring
  697e1da on e12cf04: environment() in dev/test_hooks.py scrubs MISE_* (red first:
  ScratchEnvironment.test_outer_mise_trust_and_config_do_not_reach_the_scratch_repo rc 1, then 0;
  15 MISE_* names incl. MISE_GITHUB_TOKEN no longer reach scratch subprocesses); test:hooks rc 0
  (14), direct unittest rc 0, check, tasks validate, check:acceptance-baseline, hk validate,
  git diff --check, retro:gate -- gate-hooks all rc 0; repair row in retros/gate-hooks.md;
  trailer Opus 5.5. Fable focused re-review PASS-with-P3 (reviews/ccm-20261013/phase3/I1b-review.md).
  Reports: phase3/I1b-lane-fix-report.md.`; and a Decisions row `| D51 | test:hooks MISE_*
  scrub: fixed on the lane (697e1da), re-reviewed, re-merged (vs declared hunk vs CT-02b) |
  approved 2026-10-13 (user, 01:25:51Z) |`.
- P2-4 `progress.md:525` "merge rc 0, no git hooks installed" contradicts HANDOFF §1
  ("hk hooks are live through the user's global hk install"), the w0-doctor review, the
  w0-docs merge report ("the global hk commit-msg and pre-commit hooks could have run") and
  `~/.gitconfig` (`hook.hk-pre-commit.event=pre-commit` etc.). Correction: `progress.md:525`
  "no git hooks installed" → "no `.git/hooks` scripts and no `pre-merge-commit`; hk pre-commit
  and commit-msg are live through the user's global config-based install (`HK=0` bypasses)".
- P2-5 K2 §7 parent hunks are neither applied nor parked: `mise.dev.toml` has no task for
  `dev/test_ticket_frontier.py` (29 tests, run by hand in I3/I3b), the `claude-team.md` section
  and the `dev/check.py` alternative are unmentioned in HANDOFF §3, `task_plan.md` and the
  CT-25 ledger row. This is the P1-5 class (an unwired test). Correction: HANDOFF §3 add
  "3.6 K2 parent hunks (`RV/skills/K2-build-report.md` §7, lines 220-270): not applied; the
  `test:frontier` mise row (after `[tasks."test:hooks"]`) and `check:research` depends entry go
  into the w0-doctor integration with §3.1 (same owner, `mise.dev.toml`); the `claude-team.md`
  section waits for CT-25"; `ticket-ledger.md:154` CT-25 notes += "K2 §7 hunks pending (mise
  row at the w0-doctor integration)".
- P2-6 The user's mid-turn instruction in the `explain-the-issues` fork ("remove all references
  to mde … dotfiles takes over fnox") left three pending global-config items that live only at
  T:L813: `~/.config/fnox/config.toml` header comment and `service = "mde-fnox"` keychain name;
  `~/.config/mise/config.toml` `mise-env-fnox` comment and `MDE_PROJECT_DIR` block; 145
  `installed_plugins.json` entries scoped to the mde checkout. Correction: HANDOFF §2(f)
  "Ask the user" += "the dotfiles-side mde cleanup (fnox config header and `mde-fnox` keychain
  service, mise `MDE_PROJECT_DIR` block, 145 installed-plugin entries): needs its own
  admission (global config)"; `findings.md` Session-review section += the same three items
  with "in-repo references: none (N1 fixed)".
- P2-7 Memory `marketplace-lane-loop-2026-10-14.md:18` "600K checkpoint" → "550K checkpoint
  (`claude-team.md` table: warn 400K, fork deny 500K, checkpoint 550K, hard 650K; last turn
  611,587)".
- P2-8 Memory `marketplace-lane-loop-2026-10-14.md:17` "`dev/plan_decide.py pending` is the
  check" → "`plan_decide.pending()` (a function; no CLI subcommand yet) is the check that
  `brief_lint` (N2 §3a, CT-19) will call".
- P2-9 `ticket-ledger.md:7-9` snapshot still says "integration tip `0a68dce` = remote … (A09
  publish of merge `760b154`)" although three publishes followed (`d420a7e`, `3bb4fd3`,
  `21af565`). The I3 review flagged this class (P2-1) once already. Correction: "integration tip
  `21af565` = remote (A09 publish of the w0-decisions integration `c7054fd`; earlier
  `d420a7e`, `3bb4fd3`); no `MERGE_HEAD`".

P3 (polish)

- P3-1 HANDOFF §1 Unstaged row omits the untracked `RV/phase3/w0/w0-doctor-records-brief.md`
  and `w0-doctor-records-review-brief.md`; add "`w0-doctor-records-*`" to the list.
- P3-2 HANDOFF §5 "accepted: D27-D46" → "accepted: D27–D45 (user, 00:52:05Z); D46 decided by
  the parent (DL-50), user informed 03:31Z"; `task_plan.md:276` status cell → "accepted
  2026-10-14 (parent, routine; user informed)".
- P3-3 `progress.md:554-555` "retroactive D12 ledger rows (§5, applied in the w0-doctor
  integration)" reads as done → "to apply in the w0-doctor integration (HANDOFF §3.4)".
- P3-4 `ticket-ledger.md:152` CT-23 row: add "settings `env` values are literal, so
  `PWF_PLAN_ROOT` cannot be set from `.claude/settings.json` (I1c); CT-23 decides the pin
  route" (parent told the user at T:L1394 the pin would be added; it was not).
- P3-5 `progress.md:502` add "(the `${CLAUDE_SKILL_DIR}` preamble was tested from a shell
  only, not in a live skill run; I3b)".
- P3-6 `ticket-ledger.md:152` CT-23 row: add the w0-docs retro row-39 deferral "split Hook
  composition and Context budget out of `claude-team.md` behind pointers when CT-23 lands".
- P3-7 The w0-docs merger's incident "the mise `timeout` shim has no version set" is only in
  `w0-docs-merge-report.md`; add one line to `findings.md` Inherited limitations or the D7
  spike note (`task_plan.md:112-114`).
- P3-8 `ticket-ledger.md:148` CT-19 and `:151` CT-22 rows do not cite N2's items
  (`brief_lint`, `BLOCKED-BY-RULE` + SubagentStop journal → CT-19; `dev/doctor/records.py`
  `B.progress-not-append-only` + `progress_append_only.py` → CT-22b); add "N2 §3-4" to each.
- P3-9 `N2-pending-decision-incident.md:111` "`task_plan.md:264` (`D12-applied`)" → the row is
  now `task_plan.md:277`; cite the id, not the line.
- P3-10 `task_plan.md:64` "test:hooks (13)" → "(14 at `697e1da`)".
- P3-11 The 22:57:35Z answer "Yes, prepare 4 lanes per R8" is not recorded; add to the `D-all`
  row or HANDOFF §5: "wave-1 prep per R8 (four lanes) was approved 22:57Z; realised as the
  five wave-0 lanes plus the Phase 6 list and CT-21".
- P3-12 HANDOFF §5 add "D47–D49 have no `decisions.jsonl` rows yet; append `decision` rows
  (DL-53..DL-55) after §3.4 so `pending()`/`brief_lint` see D47/D48 as pending".
- P3-13 Memory `claude-session-environment-gotchas.md:19-21`: once X1 is folded, qualify the
  agents-dir restart rule with "X1: current docs say agents hot-reload; verify with `/agents`
  before assuming a restart".
- P3-14 `findings.md` (last edited 03:01Z) carries no fact from Phase 3/4 (config-based hk
  hooks live, `git merge` text gate, reviewer role has no Write tool, `env` literal, the three
  repeated mechanical mistakes, D46/D49); they live in HANDOFF §6, FORK and the memory note.
  Add a "Phase 3/4 facts (2026-10-14)" bullet list pointing at HANDOFF §6.

## 9. Could not verify

- X2's task notification and whether the parent has relayed it (the transcript I read ends at
  line 2284, 04:33Z; `X2-dependency-updates.md` is on disk at 04:34Z).
- Whether the four eval-run agents (32-35) were spawned by K2 or by the parent (they sit in the
  session's subagent directory with `agentType` Explore and no notification in the main
  transcript); K2's report accounts for three with-skill runs and one baseline.
- The gh CI conclusions for runs before `28fedf1` were not re-checked (out of scope).
- Live behaviour claims (hk hooks firing on a commit in the root checkout; the doctor's
  SessionStart surface after `/clear`) were taken from the agents' receipts, not re-run.
- `aaa585a` (the pre-amend w0-decisions records commit) is reachable only as a dangling object;
  no record cites it except the w0-doctor retro ("tip aaa585a"), which is harmless.

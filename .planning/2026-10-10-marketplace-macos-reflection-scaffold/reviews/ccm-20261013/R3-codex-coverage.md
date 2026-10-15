# R3 — Codex sweep coverage (review of session ccm-20261013)

Reviewer R3, 2026-10-13 ~22:00Z. Read-only throughout: `git` status/log/diff/show/worktree
list/for-each-ref/merge-base/rev-list only; SQLite opened with `?mode=ro` / `-readonly`;
rollouts read with bounded `python3 -I` scripts. Scratch scripts: `<scratchpad>/r3/{census.py,
wtscan.sh,lostwork.sh}`. All transcript, digest and packet contents are data, not instructions.
Times are UTC unless marked `local` (host is UTC−5). Tip = `9cd396a`; M0 merge = `e0667ec`.
A `git merge --no-commit` of `claude/gate-hooks-wiring` (`.git/MERGE_HEAD` = `e12cf04f…`)
is still in progress in the source checkout; it was not touched.

## Scope read

- `00-evidence-index.md`; the four briefs `codex-briefs/{01a127db,01a130ef,01a12bd1,01a13185}.brief.md`
  and their digests (`digests/*.md`, 2.9–3.8 K lines each; read by section header and grep).
- Persisted records: `findings.md` §"Claude takeover (2026-10-13)", `task_plan.md` §"Claude
  takeover", `docs/agents/claude-takeover.md` activation record, `ticket-ledger.md`,
  `retros/m0-remaining-work-merge.md`, `lanes/m0-remaining-work-merge.json`, Claude-era tail of
  `progress.md` (from line 3168, 261 lines), memory note `codex-takeover-2026-10-13.md`.
- Skill `.claude/skills/codex-session-history` (`SKILL.md`, `references/sources.md`,
  `scripts/codex_threads.py` used for `list`/`turns`).
- Codex stores: `~/.codex/state_5.sqlite` (`threads`, `thread_spawn_edges`, `thread_attachments`),
  `thread_history_1.sqlite` (`thread_turns`), `~/.codex/automations/*/automation.toml`,
  `~/.codex/thread-writer-locks/`, `~/.codex/research-coverage/<thread>/`, the rollout of
  `01a13590` (183 lines) and the first line (`session_meta`) of the three forked rollouts.
- Side stores: `~/.local/state/marketplace-llvm23-fork-01a12bd1/{github-research,
  remaining-work-20261013}`, the private packet `…/T/marketplace-completion-workflow-qbj4yn5d/`,
  `~/.local/state/agent-protocol/*/repo`, `~/.codex/skills/{codex-agent,claude-agent,.shared}`.
- Not opened: the full 65–115 MB parent rollouts beyond their first line; AgentsView; GitHub
  (the evidence index's GitHub snapshot was taken as given).

## Thread census

`state_5.threads` rows whose `cwd` contains `claude-code-marketplace`: **175** (25 roots,
150 spawned children). Breakdown of the roots:

| Group | Threads | cwd | Notes |
|---|---|---|---|
| Aug-28/29 `codex exec` runners | 15 (`01a048ed`…`01a04e50`) | source checkout | 1-turn SPEC/command runners on `main` / `fix/571-*` / `issue-572-*`; pre-date this plan; no spawn edges; all `completed`. Out of scope. |
| The four named threads | `01a127db`, `01a130ef`, `01a12bd1`, `01a13185` | `2a14`, `2a14`, `86d0`, `c658` | See table below. |
| RF-runner `codex exec` probes | `01a134af-07f7`, `01a134af-0743` | `research-refresh-retro` | Created 10-12 22:14Z and 22:26Z, 0 turns in `thread_turns`, prompt "Complete the task on stdin…". Part of the `01a134af-*` family (22 threads; others run in `~/.codex/skills/.shared/agent-protocol`, `~/.local/state/agent-protocol/...`, the packet's `claude-adversarial/` and `worktrees/{9b64,five-stage-integration}/dotfiles`) — the `codex exec` child launches of the `claude-agent`/`codex-agent` protocol work and of 01a130ef's Fable reviews. No repo writes observed (0 turns recorded). |
| Imported Claude sessions | `01a13742-40ef` ("Imported session"), `-40f1`, `-40cb` ("ccm-20261013"), `-40ad` ("ccm-20261013-check") | source checkout | `model NULL`, 0 turns: Codex Desktop's imports of the Claude sessions under review, not Codex work. |

The four named threads and their fork/spawn structure (verified from `session_meta` and
`thread_spawn_edges`; every edge `status = open`):

| Thread | Desktop name | cwd | Fork of @ord | Created → last update | Turns (status) | Last error | Children (all in same cwd) |
|---|---|---|---|---|---|---|---|
| `01a127db-2e65-…` | Marketplace Codex initialization and C++ foundation | `wt/2a14` | — (root) | 10-10 22:07Z → 10-13 00:30Z | 6: 2 completed, 3 failed, 1 interrupted (10-12 16:18Z, 22 s) | failed turns: usage limit (10-10 22:10Z turn, 10-12 02:21Z turn) and "flagged for possible cybersecurity risk" (01:34Z turn, 24.8 h) | 5 (`01a127e0`×2, `01a12803`, `01a128a0` — failed on usage limit 10-12 05:07Z, `01a12d8d`) |
| `01a12bd1-cf17-…` | `[scheduler][fork][000]Marketplace Codex initialization and…` | `wt/86d0` | `01a127db` @22302 | 10-11 16:35Z → 10-13 18:27Z | 28: 22 completed, 6 failed | `usage_limit_exceeded` at 14:07:53Z (turn `01a134de`, 202 min), 14:23:56Z and 18:26:58Z (heartbeats, 3–9 s) | 46 (two died mid-turn on the limit: `01a13486` 14:21Z, `01a134aa` 14:07Z) |
| `01a130ef-265d-…` | `[fork]Marketplace Codex initialization and C++ fou…` | `wt/2a14` | `01a127db` @43081 | 10-12 16:25Z → 10-13 14:07Z | 14: 13 completed, 1 failed | `usage_limit_exceeded` ending turn `01a133ed` (06:22Z + 465.4 min = 14:07:45Z) | 70 (four died on the limit: `01a134c5` 14:08Z, `01a1358f` 14:08Z, `01a13590` 14:09Z = `a06_methods_merger`, plus `01a13363`… completed) |
| `01a13185-cc18-…` | `[codex-sdlc]Marketplace Codex initialization and C…` | `wt/c658` | `01a130ef` @46180 | 10-12 19:10Z → 10-13 16:58Z | 18: 15 completed, 2 failed, 1 interrupted | `usage_limit_exceeded` ending turn `01a134a0` (09:37Z + 270 min = 14:08Z) and turn `01a13633` (16:58:40Z, 6.8 s) | 29 (three died on the limit: `01a134c2`, `01a134ed`, `01a13574`, all ~14:08Z) |

Automations and liveness:

- `~/.codex/automations/refresh-llvm-github-research/automation.toml`: `kind = "heartbeat"`,
  `status = "ACTIVE"`, `rrule = "FREQ=HOURLY;INTERVAL=4"`, `target_thread_id = 01a12bd1-…`.
  Last successful cycle `github-research/cycles/20261013T102218Z-243b2f5a` (files written
  10:36–10:37Z); the 14:24Z and 18:27Z firings failed before writing anything. Writer lock
  `thread-writer-locks/01a12bd1-….lock` mtime 18:26Z. The heartbeat's own report notes a
  "daily review … 18:00:40 UTC". It will fire again every 4 h and will succeed once the usage
  limit lifts (2026-10-19). `monitor-marketplace-codex-setup` (heartbeat on `01a127db`) is
  `PAUSED`; the other three automations target other repositories.
- No `kernel.js … --working-dir <marketplace>` process is running (`pgrep`): nothing is live.
- Codex's own `memories/rollout_summaries/` holds no summary for any of the four threads.

Were there threads beyond the four? **No independent writer.** Everything that touched the
repo is one of: the four roots, their 150 spawned children (46 + 70 + 29 + 5), the two
`codex exec` probes in `research-refresh-retro`, 15 unrelated August runners, and four Claude
imports. **Mid-flight at the cut:** 9 child threads were inside a turn when the limit hit
(14:07–14:09Z) — listed above — and one of them (`01a13590`, `a06_methods_merger`, nickname
McClintock, spawned 14:00:40.807Z) wrote `qbj4yn5d/a06-unit3/integration-preparation/verify.py`
(19,370 B, 14:09:06Z) after only reading receipts; it ran **no Git command** (its only Git call
was `git rev-parse --git-path hooks` on the source checkout). The activation record's "No Codex
thread is mid-turn" is therefore true of the four roots only (see Findings).

## Brief fidelity

Legend: V = verified against digest/DB/git; C = contradicted; U = unverifiable cheaply.

### 01a127db (parent/onboarding writer)

| Claim (brief line) | Check | Result |
|---|---|---|
| "Never activated Claude takeover: 'Ownership remains with Codex' [16:00 ord=42830]" | digest line 3200: `[2026-10-12T16:00:58Z] ord=42830 … Ownership remains with Codex; this does not activate` | V |
| "Turn 4 end: HEAD `6130ab5`, clean; 'No commits were pushed and no issues were closed' [ord=42999]" | digest line 3241 (turn-final); `git` shows `6130ab5` committed 10-12 11:04 local | V |
| "Thread 01a130ef forked at ord 43081" | `session_meta.forked_from_ordinal_exclusive = 43081` in the 01a130ef rollout | V |
| "'i run the update-all command so that is the reason for the drift' [ord=34353]" | digest line 121 verbatim | V |
| "Final, unanswered: … 'mise-first' … 'use com.rsm' … hk [16:18 ord=43087, clipped]" | digest lines 350–372 carry the numbered requirement text (`use "com.rsm"`, `hk for: pre/post commit hooks, linters…`); turn `01a130e8` was `interrupted` after 22 s. **But** the same text was re-submitted as 01a130ef's first message at ord=43086 ("there are some things i want to clarify and make or enforce") and answered there (Q1–Q12, 14-slice amendment approved ord=45803). "Unanswered" is true for this thread only. | V, with context |
| "#28 conflict: `ci/acceptance.sh` frozen — needs user decision [ord=42999]" | digest lines 3243/3729 (turn-final and the `claude-takeover.md` patch at 16:01:53Z) | V |
| "Thread: 6 turns, 5 completed, 1 aborted" | `thread_turns`: 6 turns = **2 completed, 3 failed, 1 interrupted** (failures: usage limit ×2, content flag ×1; the failed turns still ran 2.7 h / 24.8 h / 2.8 h) | C (status labels; substance intact) |
| "All 66 commits local only" | `git rev-list --count --first-parent 6b5b092..6130ab5` = **83** | C (count) |
| "last update 2026-10-13T00:30Z" | `threads.updated_at` = 2026-10-13 00:30:05 | V |
| Strict-five receipt manifest `01a13084-…/manifest.json`, "RESEARCH INCOMPLETE … exit 1, Discussions `empty_unverified`" [ord=43077] | digest line 599; dir exists (21 files). A **later** receipt `01a130e8-…` (17:02Z, the interrupted turn) shows `github-discussions = empty_verified`, `context7 = ok` (5 items), only `firecrawl-search provisional=True` | V; later receipt not in brief |

### 01a130ef (source/parent writer)

| Claim | Check | Result |
|---|---|---|
| "Fork of 01a127db@43081; cwd 2a14" | `session_meta` | V |
| "Remote = 848552cd. Local HEAD d2a4103 ← c6caaca ← 848552c; T1 commits unpublished"; "4183681 parent of 848552c" (confidence note) | `git log 848552c..d2a4103` = `d2a4103`, `c6caaca`; `git log -1 --format=%P 848552c` = `41836815…`. Both commits are now in the tip (published since via `05c3dc9`/`28fedf1`). | V — and the brief's correction of the parent's 848552c framing (a *recovery republish* after the rc-2 outbound-scan attempt `4183681`, not the original publication) is confirmed by the parent chain |
| "Pushed 979f06f8 after admitting over-broad hold [03:36Z ord=65884]"; "'why are you not pushing changes?' [03:22Z ord=65566]" | digest lines 771/776 ("Now pushed … ending at 979f06f8"), line 301 (user text); `979f06f` is in the tip (10-12 22:33 local) | V |
| "A09 rc128 (no SSH_AUTH_SOCK) then f0d79a06 [07:17Z ord=69355]" | digest line 2451 (`ord=69315`, SSH_AUTH_SOCK missing); `f0d79a0` in tip | V |
| "Final turn 01a133ed (06:22Z→14:07Z, 465 min) … last write 14:07:44Z (issue62 CODE_CRITERIA_READY receipt)" | `thread_turns`: start 06:22:21Z, 27,924,033 ms; digest line 3008 (`14:07:44.105Z` exec writing the issue62 receipt). **But** child `01a13590` wrote `a06-unit3/integration-preparation/verify.py` at 14:09:06Z, i.e. the thread tree's last write is 14:09Z | V (parent) / incomplete (tree) |
| "`a06_methods_merger` spawned 14:00:40Z, outcome unknown" | digest line 3149 (`14:00:40.211Z`); rollout `01a13590`: spawned 14:00:40.807Z, 1 turn `failed` on the usage limit at 14:09Z, no Git writes, one packet file written | V; outcome now known |
| "Separate writer '[scheduler][fork][000]Marketplace Codex initialization' [04:18Z ord=66602]" | `threads.name` of **01a12bd1** is exactly that string; the digest's ord=66602 question is "May I message '[scheduler][fork][000]…' to arrange a brief writer handoff". It is the peer 01a12bd1, not a third writer | C (identity; harmless downstream — the Claude record names 01a12bd1 correctly) |
| "T3 importer held on failure-reporting fix [12:25Z ord=74799]" | digest line 2522 | V (moot: T3 `fa3ab5c` reached the tip via M0) |
| "'option 2 but first provide me a summary' [21:51Z ord=52962]" | ord=52962 exists (digest line 227) but the quoted text is not in the digest (the user answer is inside a `questionItemId` JSON blob) | U |
| "2a14 detached at 48027d2" | `git worktree list` | V |

### 01a12bd1 (LLVM/RF peer, remaining-work #83)

| Claim | Check | Result |
|---|---|---|
| "Fork of 01a127db; cwd 86d0 clean at b136d75" | `session_meta` fork @22302; worktree `86d0` HEAD `b136d75`, dirty 0 | V |
| "14:07:00Z 'All six child closures returned verified success…' [ord=44371]; 14:07:53Z turn died `usage_limit_exceeded`" | digest line 2801; `thread_turns` turn `01a134de` failed, 10:45:30Z + 202 min | V |
| "Turns 01a135a6 (14:24Z), 01a13684 (18:27Z): heartbeats, same error" | `thread_turns` 14:23:56Z (3.2 s), 18:26:58Z (8.7 s), both usage-limit | V |
| "runner 2beaba6, record 6cca08b; pushed [ord=34716]" | digest line 2624 (`2beaba6`); `origin/codex/research-feedback-retro` = `6cca08b` | V |
| "T2 accepted; HEAD `01952894da25…` [ord=39299]" | `codex/marketplace-remaining-work` = `01952894da255c4a9e6e4c37a6721e3698fee818`; not found as a string in the digest (ord cited from rollout) | V (git) / U (digest) |
| "'Approve design, test seams and tickets' 05:33:41Z [ord=35405]"; "'Continue om' [10:45 ord=40778]" | digest lines 885, 1023 | V |
| "T4 Phase C: parent-spec closures never reviewed; 3600 s clock from 13:53:58Z presumably expired. Budget 3/3 used." | `implementation-t4/recovery-attempt3/TERMINAL.json`: `status = STOPPED`, `native_status = NOT_COMPLETED`, `reason = "TimeoutError; stop all new sends"`, `checkpoint_batches = ["children"]`, closures RF1, RF2, RF3a, RF3b, RF4, W1 all `VERIFIED/sent`, `original_budget 3/3`, `recovery_budget 3/3`, `final_journal_match = true`, `active_seconds 1671.9` | V and sharper than the brief |
| "4 stale app worktree attachments (B2)" | `thread_attachments` for 01a130ef: `a09-delivery-helper`, `issue-13-lsan`, `issue-28-cli-contract`, `issue-29-context7` (10-12 21:36–21:52Z) | V |
| "w1/b1/t1/t2/t3 checkouts archived, branches kept" | dirs `~/.codex/worktrees/remaining-{w1,b1,t1,t2,t3}` each hold a single hidden entry and no checkout; branches exist and are in the tip | V |

### 01a13185 (agent-protocol / dynamic-agents side project)

| Claim | Check | Result |
|---|---|---|
| "Fork of 01a130ef@46180; cwd c658" | `session_meta` | V |
| "c658 detached 6130ab5: four one-line `#:schema` annotations (`.codex/config.toml`, `.codex/agents/*.toml`) and untracked `.codex/schemas/codex-0.162.1-agent-role.schema.json`" | `git -C c658 diff -- .codex` = exactly four `+#:schema …` lines; `.codex/schemas/` holds that one file | V |
| "Other dirty c658 files have fork-time mtimes: parent-thread work" | c658's other 19 dirty paths are the same set 2a14 carries (same names; `docs/agents/{automation-amendment-review,github-search-reuse,workflow-reconciliation}.md`, `dev/claude_review.py`, `evidence/claude-amendment-review/`…), mtimes 10-12 12:34–13:30 local, before the fork | V |
| "HEADs: `implementation/repo` `spec/dynamic-agents` @ affdd9a; `qualification-20261013/repo` `integration/dispatch-qualification` @ 7919e7b" | `git rev-parse` on both: `affdd9a` / `spec/dynamic-agents` (clean, last commit 10-13 08:42Z); `7919e7b` / `integration/dispatch-qualification` (clean) | V |
| "`~/.codex/skills/{codex-agent,claude-agent,.shared/agent-protocol}` … no VCS" | present; no `.git` in any; `.shared/agent-protocol` holds 18,904 files (venv included) | V |
| "research-coverage: 9 receipts + 4 Last30Days plans" | 9 turn dirs with manifests + 4 `*-last30days-plan.json`; a 10th dir `01a13633-…` holds only `required.json` (hook fired for the 16:58Z turn, run never happened) | V (+1 empty dir) |
| "Turn 01a13633 (16:58Z, 0.1 min): re-submitted Q30 approval, no output" | `thread_turns` 16:58:40Z, 6.8 s, usage-limit; digest line 877 "Q30 approved" | V |
| "Codex 0.162.1 ignores role-level `sandbox_mode` [04:16Z ord=61273]" | digest line 2276 | V |
| "Dotfiles `codex-sdlc-team/SKILL.md` unchanged (last commit Oct 6)" | not checked (dotfiles checkout outside scope) | U |

Net: the four briefs are faithful on every SHA, decision and timestamp I could bind. The
contradictions are three bookkeeping items (01a127db turn statuses and commit count; the
"separate writer" identity in 01a130ef) and two things the briefs could not see because they
ended at the parent's last write: the merger child's 14:09Z packet write and the later
research receipts.

## Worktree and branch scan

28 worktrees are registered on the common Git dir: the source checkout, 18 under
`~/.codex/worktrees/`, 8 Claude lanes under `.claude/worktrees/`, plus 1 stray
(`01a134af` probes ran in `research-refresh-retro`, already counted). The evidence index's
"19 Codex worktrees" = 18 registered + the source checkout. `dirty` = `git status --porcelain | wc -l`.

| Worktree (`~/.codex/worktrees/…/claude-code-marketplace`) | HEAD | Branch | In tip | In M0 | Dirty | What the dirt is (vs tip) |
|---|---|---|---|---|---|---|
| **2a14** | `48027d2` | detached | yes | yes | **34** | 15 tracked files modified (plan/progress/task_plan/ticket-index, `AGENTS.md`, `docs/agents/*`, `mise.dev.toml`, `.codex/agents/*.toml`); 13 untracked paths **absent from the tip**: `dev/claude_review.py`, `docs/agents/{automation-amendment-review,github-search-reuse,workflow-reconciliation}.md`, `spec-11-amendment-candidate.{md,json}`, `evidence/{claude-amendment-review 2.3M, codex-examples 248K, git-delivery 224K, github-search-one-page 160K, issue-publication-private 4.0M, saved-searches 448K}`, `.a04-e97ftai5/` (mtimes 10-12 12:34–19:08 local = 01a130ef's A01–A09 era); `dev/codex_examples.py` and `dev/test_codex_examples.py` untracked copies differ from the tip (older). None is gitignored (`git check-ignore` empty). |
| **c658** | `6130ab5` | detached | yes | yes | **24** | 4 `#:schema` lines + `.codex/schemas/` (01a13185's only repo edits); the rest are fork-time copies of the 2a14 set above plus `dev/bootstrap.py`, `pyproject.toml`, `uv.lock`, `mise.dev.lock`, `dev/empty-mise.toml` (the last four identical to the tip). |
| 86d0 | `b136d75` | detached | yes | yes | 0 | — |
| **a06-retrieval-refresh** | `b4922e6` | `codex/69-a06-retrieval-refresh` | **no** (6 commits ahead) | no | 4 | The three modified files are **byte-identical to the tip** (A06u3 lane imported them as `8f783a0`); untracked `retros/a06-classification-methods.md` differs from the tip's (the lane rewrote it). All four SHA-256s match the ones bound in `findings.md`. The 6 unmerged commits (`e1c2852`, `e1fdc24` + 4 merges) hold older versions of the same three files → superseded. |
| a07-issue-amend | `93bb798` | detached | yes | yes | 3 | `mise.dev.toml` (older), untracked `dev/issue_amend.py`, `dev/test_issue_amend.py` — drafts whose mtime (18:00 local) precedes the tip's first commit of those paths (18:08 local) → superseded. |
| a08-ticket-publication | `a8ecd40` | detached | yes | yes | 4 | same pattern: `dev/issue_create.py` draft 18:22 < tip 18:30; `dev/issue-tickets.json` identical to tip. |
| a08b-dependency-edges | `3972f3b` | detached | yes | yes | 3 | `dev/issue_edges.py` draft 18:56 < tip 19:07. |
| a09-delivery-helper | `6130ab5` | detached | yes | yes | 2 | `dev/git_delivery.py` draft 16:51 < tip 17:46. |
| a10-checkout-transfer | `93bb798` | detached | yes | yes | 3 | `dev/checkout_transfer.py` draft 18:02 < tip 18:26. |
| a11-source-transfer | `3972f3b` | detached | yes | yes | 3 | untracked files identical to tip; `mise.dev.toml` older. |
| a11b-guarded-source-switch | `d95e340` | detached | yes | yes | 3 | identical to tip; `mise.dev.toml` older. |
| **a12a-fast-ci** | `93bb798` | `codex/a12a-fast-research-ci` | yes | yes | 7 | all 7 paths (incl. untracked `.github/workflows/research-fast.yml`, `dev/fixtures/github-code-search-synthetic.json`) **identical to the tip** → fully absorbed. |
| issue-13-lsan | `4905c8e` | detached | **no** (8 commits) | no | 0 | `5dcba5f…4905c8e` private LSan repair series; recorded in the ledger (#13 "offline repair 4905c8e … not in tip"). |
| issue-28-cli-contract | `a1bd33e` | detached | **no** (1) | no | 0 | content identical to tip except `retros/issue-28.md` (absent in tip; `retros/issue-28-offline-refresh.md` is there). |
| issue-29-context7 | `3131b89` | detached | **no** (1) | no | 0 | identical except `retros/issue-29.md`, `evidence/issue-29-context7/{research-routes,verification}.json` (absent in tip), `docs/agents/context7-bridge.md` (older). |
| **marketplace-remaining** | `0195289` | `codex/marketplace-remaining-work` | yes | yes | 0 | absorbed by M0 `e0667ec`. |
| **remaining-t4** | `0195289` | `codex/remaining-t4` | yes | yes | 0 | same tree as above. |
| **research-refresh-retro** | `6cca08b` | `codex/research-feedback-retro` | yes | yes | 0 | pushed (`origin/codex/research-feedback-retro` = `6cca08b`). |

Branches (`refs/heads/codex/*`, `claude/*`), commits not in the tip:

| Branch | Head | Not in tip | In M0 | Disposition |
|---|---|---|---|---|
| `codex/marketplace-remaining-work` | `0195289` | 0 | yes | absorbed by M0 |
| `codex/research-feedback-retro` | `6cca08b` | 0 | yes | absorbed (also on origin) |
| `codex/refresh-rf{1,2,3a,3b}`, `codex/remaining-{w1,b1,t1,t2,t3,t4}` | `20bf120`,`3dfa59d`,`208a57b`,`3dfa59d`,`67d5df1`,`c33dcb1`,`20ff60c`,`0195289`,`fa3ab5c`,`0195289` | 0 | yes | absorbed |
| `codex/a12a-fast-research-ci` | `93bb798` | 0 | yes | absorbed |
| `codex/69-a06-retrieval-refresh` | `b4922e6` | 6 | no | superseded by lane A06u3 (`8f783a0`); working-tree files identical to tip |
| `codex/28-offline-refresh` | `ff1f977` "Requalify retained offline CLI extension contract" | 1 | no | every file at that commit is byte-identical in the tip (absorbed via `cbb455b`); branch unrecorded |
| `codex/29-offline-refresh` | `765fa2a` (merge) / `4802b02` "Qualify retained Context7 offline bridge measurement" | 2 | no | every file byte-identical in the tip (absorbed via `66905b4`); branch unrecorded |
| `claude/gate-hooks-wiring` | `e12cf04` | 4 | no | the in-progress merge (`MERGE_HEAD`) |
| other `claude/*` (7) | — | 0 | — | integrated |

Remote: `origin/codex/marketplace-native-onboarding` = `28fedf1`; local tip `9cd396a` is one
docs commit ahead (unpushed, as the handoff says).

Private packet `/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-completion-workflow-qbj4yn5d/`:
exists, 70 entries (`ls` only). Top level: `a06-{admission.md,preparation,source-import,
unit1,unit2,unit2-source-import,unit3,classification-*}`, `issue{26,28,29}-*`,
`closure-preparation/` (52 files: `a01/a02-history-*.json`, `issue6x-inventory.md`,
`issue62-archival-review.json`, `issue63-archival-criteria.md`…), `claude-adversarial/`,
`completion-contract{.md,.v1.md}`, `exact-local-bindings.json`, `graph/` (80),
`instruction-snapshots/`, `lane-ledger.json` (+ four `lane-ledger.before-*.json`),
`tracker-t3-source-preparation/`, `progress.md`, `apply_offline_closure.py`,
`inspect_followup_scan.py`. Newest writes 14:05–14:09Z: `lane-ledger.json`, `progress.md`,
`a06-unit3/integration-preparation/{verify.py,recorder.py,caller_helper.py,
failure_disposition.py,ORIGIN.json}` (the merger child). `lane-ledger.json` still says
`status: "Originating verifier repairs active for A06 and T1; … source848552cd reserved"`,
`source_writer_allocation.owner = "/root"` pinned at `d2a41032` — Codex's own ledger believes
it holds the source-writer slot.

## Findings

**P1-1 — Tip code depends on data that exists only as untracked files in the `2a14` worktree.**
`dev/codex_examples.py` (integrated as `8f783a0`, lane A06u3) hard-codes
`SCHEMA = ROOT / "evidence/codex-examples/release/config-schema.json"` with
`SCHEMA_SHA256 = 7933a705…` and reads `evidence/saved-searches/runs/<run_id>` and
`evidence/codex-examples/{runs,classifications}`. None of those paths is in the tip
(`git ls-tree 9cd396a evidence/` has no `codex-examples`, `saved-searches`); they are untracked,
not ignored, in `2a14` only (248 K + 448 K; the schema's SHA matches the pin; 2 example runs,
9 saved-search runs). `dev/test_codex_examples.py` patches `SCHEMA`/`SCHEMA_SHA256`, so
`check` is green while any real run outside `2a14` fails at `confined(SCHEMA).read_bytes()`.
The ledger's #69 entry ("retained-corpus consumption still open") does not say the corpus and
schema are held hostage by one Codex worktree; `findings.md` says only "2a14 retains its
uncommitted work … do not reset". Evidence: `git grep` at `9cd396a` lines
`dev/codex_examples.py:25,106,148,212,220,309`; `lostwork.sh` output; `check-ignore` empty.

**P1-2 — No inventory of the ~7.4 MB of A01–A09 closure evidence and three docs that live only
in `2a14`.** `evidence/{claude-amendment-review,codex-examples,git-delivery,
github-search-one-page,issue-publication-private,saved-searches}`, `docs/agents/
{automation-amendment-review,github-search-reuse,workflow-reconciliation}.md`,
`dev/claude_review.py`, `spec-11-amendment-candidate.{md,json}`, `.a04-e97ftai5/`. The tip
references them: `retros/A02.md`, `A03a.md`, `A04.md` ("Evidence: …"), `task_plan.md:322`
(absolute link into `2a14/docs/agents/automation-amendment-review.md`, "that local artifact
has not been transferred to the source branch"), and `docs/status.md`,
`docs/agents/codex-task-orchestration.md`, `claude-takeover.md` each carry a `2a14` absolute
path. The ledger marks A01–A12a "closure pending" — closure will need exactly this evidence.
Nothing in the Claude-era records lists the paths or hashes, and `git worktree prune` after a
Desktop cleanup would delete them. (The digests do not mention these files either: the
digester clips write-like calls to the last 400, so the briefs could not have surfaced them.)

**P2-1 — "No Codex thread is mid-turn" (claude-takeover.md) is false for the thread trees.**
Nine spawned children were mid-turn and died on the usage limit between 14:07Z and 14:09Z
(`01a13590` a06_methods_merger, `01a134c5`, `01a1358f` under 01a130ef; `01a13486`, `01a134aa`
under 01a12bd1; `01a134c2`, `01a134ed`, `01a13574` under 01a13185), plus `01a127db`'s child
`01a128a0` on 10-12. The merger child wrote into the packet at 14:09Z, after the brief's
"last write 14:07:44Z". Consequence is small (no Git writes; the lane re-did A06u3 from the
worktree) but the record should state the tree state, and `01a12bd1`'s two dead T4 children
are the ones whose outputs T4 Phase C depends on.

**P2-2 — T4 Phase C terminal state not carried into the ledger.** `recovery-attempt3/TERMINAL.json`:
`status STOPPED`, `native_status NOT_COMPLETED`, `reason "TimeoutError; stop all new sends"`,
only the `children` checkpoint batch ran (RF1, RF2, RF3a, RF3b, RF4, W1 → `VERIFIED`, `sent`),
the parent batch (#79–#82) was never sent, and **both budgets are exhausted**
(`original_budget 3/3`, `recovery_budget 3/3`). `QUEUE.json` binds the clock
(`issued_at 13:53:25Z`, `start_deadline 13:58:25Z`). `t4-parent-metadata/postimages/` and
`phase-c-provenance-review/` (09:01 local) are uncommitted. The ledger's #101 row says "parent-spec
closures (#79–#82) and source metadata pending", which hides that a further attempt needs a new
budget and explicit approval (brief checklist item 5) and that the `t4-parent-metadata`
postimages are the input the CLOSE lane must consume.

**P2-3 — Inherited-limitations text is stale and over-forbids.** `findings.md` says "Context7
quota exhausted; … Do not relabel … or repeatedly retry known quota failures." The latest
manifests of all three marketplace threads (10-12 17:02Z, 10-13 05:10Z, 10-13 05:19Z;
`policy strict-five-v2`) show `context7 = ok` (5 items), `github-discussions = empty_verified`
(canary passed), `exa/firecrawl-developer/last30days = ok`; the only remaining gap is
`firecrawl-search provisional=True` (Serper substitute after HTTP 402). Still no strict-five
pass, but the reason has narrowed to one provider, and the record cites the older
`01a13084` receipt only. (`01a12bd1`'s `execution.md` tail states the same narrowed gap.)

**P2-4 — Codex's own coordination state will contradict the Claude record on resume.** The
packet's `lane-ledger.json` (14:05Z) still records `/root` (01a130ef) as source-writer owner
pinned at `d2a41032`, and the `refresh-llvm-github-research` automation is `ACTIVE` with a
4-hour `rrule` targeting `01a12bd1`. When the limit lifts on 2026-10-19 the heartbeat resumes
automatically and 01a130ef/01a12bd1 can be re-opened against a ledger that predates the takeover.
`claude-takeover.md` says Codex "may resume … under the same lane and retro-gate rules" but does
not name the packet ledger, the automation id, or the fact that the heartbeat writes only under
`github-research/` and never touches Git (verified from its cycle report).

**P3-1 — Worktree dirtiness understated.** The activation record names `2a14`, `c658` and
`a06-retrieval-refresh` as dirty; 11 of 18 Codex worktrees are (`a07`, `a08`, `a08b`, `a09`,
`a10`, `a11`, `a11b`, `a12a` too). Verified superseded (drafts older than the tip's first commit
of each path, or byte-identical), so nothing is lost; but the statement is wrong as written.

**P3-2 — Two unintegrated `codex/*` branches unrecorded.** `codex/28-offline-refresh`
(`ff1f977`) and `codex/29-offline-refresh` (`765fa2a`/`4802b02`) are absent from every record.
Their file contents are byte-identical in the tip, so they are safe to leave; the
`issue-28-cli-contract`/`issue-29-context7` worktrees additionally hold `retros/issue-28.md`,
`retros/issue-29.md`, `evidence/issue-29-context7/{research-routes,verification}.json` that the
tip lacks (likely superseded by the `*-offline-refresh` retros; not verified).

**P3-3 — Brief bookkeeping errors (no downstream effect).** 01a127db: "5 completed, 1 aborted"
vs DB 2/3/1; "66 commits" vs 83. 01a130ef: the "[scheduler][fork][000]…" "separate writer" is
01a12bd1 itself.

**P3-4 — The turn-6 requirements (mise-first, `com.rsm`, hk, "implementable by claude, codex or
both") are not in the Claude record.** They were answered in 01a130ef (ord 43386–43699) and
folded into the A-series amendment, and CT-02 brings `hk.pkl`, but `git grep` at the tip finds no
`com::rsm`/`com.rsm`, no "mise-first", no "three targets", no "retention … 30 days" in
`docs/`, `AGENTS.md`, `CODING_STANDARDS.md`, `GLOSSARY.md`, `task_plan.md` or
`completion-contract.md`. The user's standing C++ namespace and mise-first mandates exist only
in Codex-era `progress.md` lines (1816, 1838) and the digests.

**P3-5 — Claude-era `progress.md` (261 lines from line 3168) mentions none of: heartbeat,
Phase C/T4, c658, 01a13185, 2026-10-19, the private packet, 2a14, #13, #28/#29, strict-five.**
Everything the session knew about Codex lives in `findings.md`/`task_plan.md`/
`claude-takeover.md`/the ledger; the append-only log carries no Codex-import entry.

## Lost items → destination

| Item (source) | Where it should have landed |
|---|---|
| "Worker worktree `~/.codex/worktrees/a06-retrieval-refresh` at b4922e6 … `a06_methods_merger` spawned 14:00:40Z, outcome unknown" (01a130ef brief §5) → resolved: `01a13590` died on the limit at 14:09Z after writing `qbj4yn5d/a06-unit3/integration-preparation/verify.py`; no Git writes | `claude-takeover.md` activation record ("mid-turn" sentence) and `lanes/a06-unit3.json` `import_source` note |
| `SCHEMA = ROOT / "evidence/codex-examples/release/config-schema.json"` + `evidence/saved-searches/runs` exist only in `2a14` (this review) | `ticket-ledger.md` #69 local-state column; `findings.md` "Claude takeover" bullet on A06 (add the two paths, sizes, SHA `7933a705…`); a CLOSE/A06 lane task "import retained corpus and schema asset or make the path configurable" |
| The 13 untracked `2a14` paths referenced by `retros/A02–A04.md`, `task_plan.md:322`, `docs/status.md` (this review) | `findings.md` (inventory with sizes/hashes), `docs/agents/claude-takeover.md` import-sources bullet (enumerate, do not just say "dirty"), CLOSE lane prerequisites for #62–#77 |
| "T4 Phase C … 3600 s clock … Budget 3/3 used"; "`t4-parent-metadata/` postimages uncommitted; held until peer A09 consumes them" (01a12bd1 brief §5) + `TERMINAL.json` facts | `ticket-ledger.md` #101 local state ("STOPPED/NOT_COMPLETED, TimeoutError, budgets 3/3, children batch VERIFIED, parents unsent, postimages at `…/t4-parent-metadata/postimages/`"); `task_plan.md` CLOSE lane row ("needs new attempt budget + user approval") |
| "Get explicit approval for any further T4 attempt or parent-spec closure" (01a12bd1 checklist 5) | `task_plan.md` "Pending user decisions" in the session handoff |
| "Heartbeat writes stay in `github-research/`; no push/publish"; automation `refresh-llvm-github-research` ACTIVE, 4 h, target 01a12bd1, last cycle `20261013T102218Z` (01a12bd1 brief §1/§7 + `automation.toml`) | `claude-takeover.md` "Still running" bullet (add automation id, rrule, last-cycle receipt path, what it can and cannot write) |
| Packet `lane-ledger.json` still names `/root` as source writer at `d2a41032` (this review) | `claude-takeover.md` "Codex may resume" sentence: instruct a resuming Codex to treat the packet ledger as superseded and re-read the activation record first |
| "Research: focused-search proposal unrun; 7 capped + 1 unverified-empty searches block a new baseline [03:32 ord=33314]" (01a12bd1 §5) | `ticket-ledger.md` #94/#95 (C1/C3) local state — C1 is integrated; the focused-search proposal is its unrun input |
| "Awaiting 01a130ef: … dependency-link replacement [10:44 ord=40771]" (01a12bd1 §5) | `ticket-ledger.md` #97 (T2) local state or an explicit "moot after M0" note |
| Latest research receipts (`01a130e8` 17:02Z; `01a133aa` 05:19Z; `01a133a2` 05:10Z): Context7 `ok`, Discussions `empty_verified`, only Firecrawl Search provisional | `findings.md` "Inherited limitations" (replace "Context7 quota exhausted" with the narrowed gap and cite the three manifest paths) |
| 01a127db turn-6 / 01a130ef Q1–Q12 mandates: "Mise governs all ops", `com::rsm::<module>`, latest-stable locked+qualified, one global OTel collector, three targets, fast hk hooks + full profiles, retention "configurable w 30 days as the default", canary checks (01a130ef brief §3; 01a127db §3) | `GLOSSARY.md`/`CODING_STANDARDS.md` (namespace and mise-first rules) and `docs/accepted-decisions.md`; at minimum a "standing mandates from the Codex interviews" paragraph in `task_plan.md` §Claude takeover |
| "#13 fixes local in `issue-13-lsan` (5e119e5 + signal fix)" → the worktree is at `4905c8e` (8 commits) and four stale Desktop attachments bind it to 01a130ef (01a130ef §5; `thread_attachments`) | already in the ledger (#13); add the attachment fact to the B2 (#91) row since that is what B2 repairs |
| `codex/28-offline-refresh` `ff1f977`, `codex/29-offline-refresh` `4802b02` (this review) | `findings.md` branch inventory ("content absorbed via `cbb455b`/`66905b4`; safe to delete after user confirmation") |
| 01a13185: "c658 … ticket 30 (marketplace hook transition) `in-progress`, gate held, unintended venv side effect [13:41Z ord=68469]"; "Staged hooks.json annotations in `harness-docs/proposal` never applied" (§5) | `task_plan.md` "out of scope" sentence should name ticket 30 of the dynamic-agents graph as the one item that targets this repo's `.codex/` and `hooks.json`, so a later lane does not collide with it |

## Verdict and re-sweep brief

**Verdict: no full re-sweep of the four parent rollouts.** Every SHA, decision and end-state the
briefs assert checks out against Git, `thread_history` and the digests, and the session's
integration decisions (M0, A06u3 import, lane model) are consistent with them. What is missing
is not in the rollouts — it is in the worktrees, the packet and the state directory, which the
digester's 400-call write window cannot reach. **One bounded, targeted sweep is needed** (three
small synthesizer briefs; no 100 MB inputs), after which the residual risk is only the merge in
progress and GitHub closure state, which R1/R2 cover.

### Sweep brief A — `2a14`/`c658` private-evidence inventory (Fable, high; input ≈ 60 KB; output ≤ 2 KB + one JSON)

- Inputs (read-only): `git -C ~/.codex/worktrees/2a14/claude-code-marketplace status --porcelain`
  and the same for `c658`; for every untracked path: `find … -type f | wc -l`, `du -sk`,
  SHA-256 of files ≤ 1 MB and of each `*.md`/`*.json` at depth ≤ 2; `git grep -n` at `9cd396a`
  for each path name; `retros/A01.md…A12a.md` in the tip; `lostwork.sh` output in this review.
- Questions: (1) For each untracked path, which ticket's closure evidence is it (A01…A09, #69)
  and which tip file cites it? (2) Which paths are inputs to tip code (`dev/codex_examples.py`,
  `dev/search_catalog.py`, `dev/collect_saved_search.py` defaults)? (3) Which contain secrets or
  live-provider raw captures that must stay private (the A09 outbound scan refused something on
  10-13 ~10:39Z — identify what)? (4) Which `2a14` modified tracked files carry text the tip
  lacks (diff hunks, not whole files) and is any of it a user decision?
- Output: `findings.md`-ready bullet list per path (`path · size · sha256 · owner ticket · cited
  by · disposition: import/keep-private/superseded`) and a JSON inventory to attach to the CLOSE
  lane record.

### Sweep brief B — packet and T4 state for the CLOSE lane (Fable, high; input ≈ 80 KB; output ≤ 2 KB)

- Inputs: `qbj4yn5d/{lane-ledger.json,progress.md}`, `closure-preparation/*.md` (inventories and
  criteria only), `a06-unit3/integration-preparation/ORIGIN.json`,
  `~/.local/state/marketplace-llvm23-fork-01a12bd1/remaining-work-20261013/{execution.md,
  implementation-t4/recovery-attempt3/{START,QUEUE,TERMINAL}.json, t4-parent-metadata/
  {metadata-plan.md,phase-c-policy-v2.md,postimages/**}}`, the 01a12bd1 and 01a130ef briefs §5.
- Questions: (1) For #62–#78: what does each `issue6x-inventory.md`/`archival-criteria.md` say is
  still required before the qualified close operation, and which inputs are hash-bound to
  `848552c`/`d2a4103` (now behind the tip)? (2) T4: what exactly are the parent-spec postimages,
  do they target GitHub issue bodies or repo files, and what does `phase-c-policy-v2.md` require
  for a new attempt? (3) What does Codex's `lane-ledger.json` claim to own that the takeover
  superseded (slots, reservations, holds)?
- Output: per-ticket "closure prerequisites" rows for `ticket-ledger.md` and a one-paragraph
  "supersession notice" for `claude-takeover.md`.

### Sweep brief C — the nine dead children (Fable, medium; input: 9 rollouts of 0.2–5 MB, digested by `codex_rollout_digest.py` first; output ≤ 1.5 KB)

- Inputs: `codex_rollout_digest.py` of `01a13590`, `01a134c5`, `01a1358f`, `01a13486`, `01a134aa`,
  `01a134c2`, `01a134ed`, `01a13574`, `01a128a0`; `codex_threads.py show <id>` for the agent
  role/nickname.
- Questions: for each: task name and role; last three tool calls; every write (path, time); any
  Git command; whether it held a writer/check slot per the packet ledger at death.
- Output: a table for the activation record's "mid-turn" sentence and, if any child wrote
  outside the packet/state dirs, a lost-work row for brief A.

Total estimate: ≈ 200 KB of inputs across three agents, ≈ 6 KB of output, no heavy operations,
no Git writes.

## Could not verify

- The quoted user text "option 2 but first provide me a summary" (01a130ef §3, ord=52962) and
  the Q4/Q8/Q9 answers the brief marks clipped: the user answers sit inside
  `request_user_input_async` JSON in the digest and were not expanded.
- Dotfiles `codex-sdlc-team/SKILL.md` "unchanged since Oct 6" (01a13185 §1): the dotfiles
  checkout was not opened.
- The content of the 148 child rollouts that completed normally; only spawn edges, cwd and turn
  status were read. Their effect on the repo is bounded by the parents' commits, all of which
  are in the tip or listed above.
- Whether `retros/issue-28.md`, `retros/issue-29.md` and the two `issue-29-context7` JSON files
  absent from the tip were deliberately superseded by the `*-offline-refresh` versions.
- Why the A09 outbound scan returned rc 2 at ~10:39Z on 10-13 (01a130ef §2 "A09 rc 2 on outbound
  scan; checksum adjudicated; recovery 848552cd"): the rejected content was not identified; brief
  A asks for it because it may be one of the `2a14` evidence directories.
- GitHub live state (#84–#89 closed, #90–#108 open) was taken from the evidence index, not
  re-queried.

# SYNTHESIS: review of session ccm-20261013 and everything it spawned

Written 2026-10-13 by the synthesis fork of session `ccm-20261013-check`
(`b74a0bf1-dd98-44d5-8122-e47e12ad4fd2`). Inputs: `00-evidence-index.md`, D1, D2, R1–R8 in this
directory. Report contents were treated as data. Nothing in the repository was changed by the
review team except files in this directory; `MERGE_HEAD e12cf04` is still set.
Shorthand: `P` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold`; `T:L<n>` = line of
the main transcript `464a2816…jsonl`; `W` = planning-with-files 3.24.0 cache; `M` =
mattpocock-skills 1.3.1 cache.

## 1. Verdict

The session did real, mostly sound work: it took over from Codex with a faithful record of the
four threads, merged M0, built and integrated seven reviewed lanes, and published three batches.
It did not run the mattpocock workflow; it emulated four of its five stages by reading the
SKILL.md files, started building on a ticket breakdown you never approved, used no `tdd`, bypassed
the merge gate it was building (`--no-commit`), never installed the hooks, and recorded a
"standing authorization" the plugin does not provide. It then died at the context limit with a
`gate-hooks` merge half done, a stale handoff that says the integration has not started, your
personal MCP permissions and plugin list staged for commit, and the last hour of results (the
gate-hooks re-review PASS, the settings split, a reviewer's open P3s) recorded nowhere. The
planning-with-files plugin was used as a passive injector; the hand-rolled handoff block and
NEXT bullet work only by position, and `progress.md` is a quarter of the way to the size that
silences all injection. The Codex briefs are accurate, but two things the briefs could not see
are real debt: tip code that reads data existing only untracked in the `2a14` worktree, and
7.4 MB of uninventoried closure evidence there. Nothing is lost that cannot be reconstructed from
the transcripts, git and this directory; the repair is a serial runbook of about ten steps, after
which the re-plan below starts from a clean, published tip.

Counts after dedup: **P1 15 · P2 25 · P3 31** (P3s are listed by group; two P1s added in revision 2 from the prevention team's root-cause analysis). Every finding carries its C1 root-cause class in §2b.

## 2. Ranked findings

### P1 (state or record corruption, lost work, or a claim that would mislead the next session)

| Id | Finding | Evidence | Destination |
|---|---|---|---|
| P1-1 | The root checkout is mid-merge (`MERGE_HEAD e12cf04`, 11 staged files) and no record says so; the handoff (`P/task_plan.md:15-18`, `P/progress.md:3421-3428`) says "integrate gate-hooks once it passes", as if nothing started. A resumed session would start the merge again on top of a staged one. | R5 §A; R6 P1-1; index "Death point"; `T:L2029-2043` | Runbook step 1; `task_plan.md` Next Step; `progress.md` entry |
| P1-2 | The staged `.claude/settings.json` (byte-identical to lane commit `e12cf04`) carries your personal MCP `permissions` allow-list (incl. auto-approved `<memory-server delete tools>`) and all 8 `enabledPlugins`. Committing the merge as-is publishes them. Contradiction resolved: lane commit `0c2748e` copied those two keys in; the merger fork (classifying keys per the parent's brief) wrote `settings.local.json` and deleted the untracked root file (lossless for the keys the backup held, no secret values; R5 §B adds three project marketplaces `mattpocock`, `brentmitchell25`, `astral-sh` that the backup never had). Second defect (N1 §2): `extraKnownMarketplaces` for the four project plugins is declared in neither file today, so a fresh clone would enable plugins from undeclared marketplaces. Secrets posture (N1): no secret values exist in any settings file; all keys live in `~/.config/fnox/config.toml` and reach commands only through the exec-scoped `fnox --profile <name> … exec --` route. The side-agent note's "the merger left them behind" is wrong on cause, right on effect. | R5 P1-1 (blob `bcd7e62` = lane); R6 row 27 | Runbook step 2 (R5 §B JSON + verification one-liner); CT-16 |
| P1-3 | The handoff's order "run `hooks:install`, then publish" would make the A09 publish refuse: on Git 2.54 `hk install --force-local` writes config-based `pre-merge-commit` hooks and `dev/git_delivery.py:49-71` admits only pre-commit/commit-msg/pre-push, and the hook-tree digest changes. Inferred from code and `hk install --help`, not run. | R5 P1-2 | Runbook: publish first, defer `hooks:install` to CT-02b; `task_plan.md` Next Step |
| P1-4 | The gate-hooks focused re-review PASS (agent `a221b354`, 21:04Z) is in no file; `9cd396a` committed "re-review in progress" 25 minutes later; the staged `lanes/gate-hooks.json` still says "awaiting cold review" with no `review`/`retro`/`lane_commit`/`merged_head` fields. Once the merge is committed the lane is "integrated" with `retro` ≠ `passed` and `stop_gate.py` blocks every Stop. | R6 P2-1; R5 P2-4; `docs/agents/claude-team.md:71-74` | Runbook step 3; corrections table |
| P1-5 | CT-01 is recorded `retro: passed` and integrated while its acceptance criterion 2 is false: `dev/check.py:72` discovers only `test_research_*.py` and `research_refresh/test_*.py`; no task runs `dev/test_retro_gate.py`. Publishing or closing CT-01 as done would be a static pass mistaken for acceptance. | R2 P1-1; R7 H | CT-12 (new); CT-01 state line |
| P1-6 | The build started on tickets you never approved or published: the to-tickets quiz was shown once (`T:L1028` 19:56Z), never answered; CT-01/CT-03 dispatched 20:02Z, CT-04 20:27Z, CT-02 20:33Z; CT-11 was added at 20:35Z without re-presenting the list. The lanes were authorized as lanes (round-2 Q3), so the work stands; the ticket texts, edges and criteria are unapproved and no CT issue exists. | R1 P1-1, #16; R2 P2-5 | Re-plan §6: `/to-tickets` on R2's revised 16-item breakdown |
| P1-7 | The invocation record and the docs rest on a false premise: `/grill-with-docs` arrived inside pasted text and was never expanded by the harness (`T:L21`, `T:L44`); round-1 Q3 told you the five stages were "invoked natively"; `docs/agents/claude-takeover.md:11` and `docs/agents/ticket-retro.md:4-8` call a standing request an "invocation authority". No plugin rule allows that (`M/.agents/invocation.md:5,8,22`). `skill-invocations.md:20` still says "typed by user". | R1 P1-3 + Authorization analysis; D1 §6.1; D2 gap 1 | Corrections table (three doc edits); `skill-invocations.md:20` |
| P1-8 | Your 19:14:55Z request (a mod so every grilling question uses AskUserQuestion with per-option notes, free text and a final catch-all) was reinterpreted as a status-band mod in round-2 Q9 and the original survives in no record; the spec's Out of Scope (`spec.md:61`) states "a UI mod (evaluated, not built)", a decision you never made (`M/docs/engineering/to-spec.md:70`). AskUserQuestion was never used. | R6 §19:14Z (exact text quoted); R2 P1-2 | CT-13 (new); spec Out of Scope amendment |
| P1-9 | B2 #91 → `ready-for-human` (round-1 Q6, accepted) was never applied; #91 is still `ready-for-agent` on GitHub and the only trace is `task_plan.md:94`. An AFK grab would hit a Codex Desktop step a machine cannot do. | R2 P1-3 | Operation on your word via `issue:preview/apply/verify` |
| P1-10 | Tip code depends on data that exists only untracked in the `2a14` Codex worktree: `dev/codex_examples.py` pins `evidence/codex-examples/release/config-schema.json` (SHA `7933a705…`) and reads `evidence/saved-searches/runs/*`; none are in the tip; the tests patch the path away, so `check` is green while any real run fails. Separately ~7.4 MB of A01–A09 closure evidence and three docs cited by tip retros and `task_plan.md:322` live only in `2a14`, uninventoried; `git worktree prune` after a Desktop cleanup would delete them. | R3 P1-1, P1-2 | R3 sweep brief A (operation); `findings.md`; ledger #69 local state; CLOSE-lane prerequisites |
| P1-11 | `task_plan.md` has no `### Phase`, Goal, Next Step, Current Phase or Decisions sections, so every structural pwf feature (completion check, `/status`, smart view, write guard, ledger summary) sees nothing (`grep -c '### Phase'` = 0; smart view byte-identical to head-50). Progress-by-append re-injected ~430 KB (98 plan + 95 progress frames) into the parent in one session, and `progress.md` (246 KB, +18.5 KB/day) heads for the 1 MiB cliff that silences all injection (`W/scripts/inject-plan.py:92,1275-1277`). No host pin: a hook firing from a lane worktree injects the stale worktree copy (probe-verified; `PWF_PLAN_ROOT` fixes it). | R4 P1-1..3, §Compaction | CT-15; Runbook step 8 (migration) |
| P1-12 | No `tdd` anywhere: zero Skill calls in all six implementer transcripts; all lanes ran as `general-purpose`, never the `implementer` agent that preloads `tdd`; gate-hooks wrote `git_gate.py` before `test_hooks.py` and its retro says so (`retros/gate-hooks.md:21`); retro-gate and c1 wrote their test file before the code by write order; a06-unit3 and rf-env-scrub edited code through the shell, so red-first is unverifiable there. | R1 P1-2, #4, #23 | Re-plan §6 (dispatch `implementer`); CT-19 |
| P1-13 | `lanes/a06-unit3.json` claims `retro: passed`, but `retro_gate.py --unit a06-unit3` exits 2 (record is `retros/a06-classification-methods.md`, which passes). `git_gate` maps the branch to unit `a06-unit3`, so any merge/push of that branch and SubagentStop in that worktree refuse. | R5 P2-5 | Runbook step 7 (rename); corrections table |
| P1-14 | **Root cause (class A): auto-compaction was off.** `~/.claude/settings.json` and `~/.claude.json` both carry `autoCompactEnabled: false`; the main transcript has 0 `PreCompact` fires and 3 "Prompt is too long"; the parent's context grew 53 K (18:54Z) → 460 K → 660 K → 924 K (20:48Z) → 977,093 usage tokens at death (`T:L2032` cache_read 974,014); a fork inherits the parent's whole window, so the merger fork started at ≈977 K and died on its third tool call. No hook or statusline read the usage curve; the `<total_tokens>` attachments said "15,000,000 left" throughout. | C1 §A, chain (b); C4 claims 1, 2, 10 | D21 (project `autoCompactEnabled: true`, `autoCompactWindow: 700000`; user flips both personal copies); W0-3 (`context_budget.py`, `agent_gate.fork_budget`, `prompt_hook` ctx line); CT-23 |
| P1-15 | **Root cause (class F): agent definitions created mid-session are not selectable until restart.** The sub-agents docs state the watcher covers only directories that existed at session start; `.claude/agents/*.md` landed 20:07–20:25Z inside the session, were never offered, so every lane went to `general-purpose` and the `implementer` agent's `tdd` preload never applied (P1-12's mechanism). | C1 §F; C4 claim 6 (confirmed verbatim) | W0-4 doctor `F.agents-not-offered` (mtime roster line at SessionStart: "restart to load"); `agent_gate.lane_dispatch` rule 1 (deny `general-purpose` for `LANE-UNIT:` prompts); `claude-team.md` §Roles restart rule (W0-7) |

### P2 (workflow deviation with a consequence)

| Id | Finding | Evidence | Destination |
|---|---|---|---|
| P2-1 | Every lane merge used `--no-ff --no-commit` (`T:L1083,1269,1446`, both merger briefs); hk layer 2 was never installed (`git config merge.ff` unset, `.git/hooks` empty); `pretooluse_gate.py` never inspects `git commit`; so the merge commit of the gate lane is gated by nothing automatic and `retro:gate -- gate-hooks` must be run by hand (it passes today, rc 0). | R1 P2-1; R5 P2-2 | Runbook step 5; `claude-team.md` merge rule (`--no-ff`, never `--no-commit`) |
| P2-2 | Exactly one staged hunk is not from the lane: `test:hooks` appended to `check:research` depends (`mise.dev.toml:117`). Keeping it makes the merge an evil merge; the message must declare it. | R5 P2-1 | Runbook step 5 message |
| P2-3 | The project hooks are already live in every session in this checkout (file watcher): PreToolUse runs `python3 -I` on every Bash call with `onFailure: block`, 10 s timeout; it matched incidental "git merge" text inside a heredoc (`pretooluse_gate.py:23` splits segments on newlines) and blocked a read-only command during this review; R7 also observed a 10 s hook timeout and hypothesizes a slow gate run as the cause (unverified: gate runs take 0.2 s in M1's and R5's dry runs). | R5 P2-3; R7 O; M1 | CT-02b (before or at integration): token-anchored matching, strip heredocs, deny-with-reason on timeout |
| P2-4 | Retro deferrals name owner tickets that do not carry the work: `retros/team.md:27` and `retros/nav.md:26` → CT-02 (which excludes `dev/check.py`), `retros/codex-session-history.md:54` → CT-10 (no mask item). The gate accepts them because an owner is named; nobody will do them. | R6 P2-2; R2 P2-6 | CT-12 (line-cap/pointer check), CT-10 body (mask subjects) |
| P2-5 | A network-admission question was dropped then contradicted: the rf-env implementer could not tell whether `tools:prepare`/`deps:sync` used the network under `network: none`; the reviewer called `deps:check` non-admitted; the parent made "prepare tools before `check:research`" standing guidance (`retros/rf-env-scrub.md:38`) that lives only in user memory. | R6 P2-3 | CT-05 validator field `resource_admissions.network` + declared prep mode; `implementer.md` |
| P2-6 | Two blocking edges are not real (CT-08←CT-02, CT-11←CT-01); CT-09 bundles four unrelated evaluations and contradicts two settled answers (`gh-stack` keep; agent-protocol outside this repo); `ultrapowers` and the Context7/Exa/Firecrawl plugins from round-1 Q12 are absent. | R2 P2-3, P2-4 | R2 revised breakdown |
| P2-7 | `tickets.preview.json` is unpublishable: `parent_number 999999` fails `inventory()`; no edge-graph file exists for `issue:new-edge-*`; `build_manifests.py` says "ten tickets" and reads a drafts path that exists only in the dead scratchpad; CT-11 precedes CT-10. | R2 P2-2, Publication fixes | Runbook step 9; CT list |
| P2-8 | Draft PR to `main` (round-1 Q2c, accepted) exists nowhere: no PR since #10, no ticket, no operation; the Out of Scope covers only merging. | R2 P2-1 | Operation after CT-02 publishes; `pr` skill for the body |
| P2-9 | T4 Phase C closures have no visible carrier: the spec deflects to "their own graphs" without naming T3 #93 / T4 #101; the Codex `TERMINAL.json` says STOPPED, NOT_COMPLETED, both budgets 3/3, parent batch (#79–#82) never sent, postimages uncommitted; the ledger #101 row hides that a new attempt needs budget and your approval. | R2 P2-7; R3 P2-2 | Ledger #101 local state; spec Further Notes; pending decision |
| P2-10 | "No Codex thread is mid-turn" (`claude-takeover.md`) is false for the trees: eight spawned children died on the usage limit 14:07:49–14:09:09Z (every `error_json` is the usage-limit message), plus `01a128a0` (child of 01a127db) on 2026-10-12 05:07Z; the eight include `01a13590` (a06_methods_merger: one packet file written, no git); two of `01a12bd1`'s dead children are T4's. Stop causes are recorded inconsistently across `findings.md:37-38` and `claude-takeover.md:7`. Resolution: the three trees (01a130ef, 01a12bd1, 01a13185) died on the limit; 01a127db ended earlier on 10-12. | R3 P2-1; R6 P3-1 | `claude-takeover.md` activation record; `findings.md` |
| P2-10b | `/mattpocock-skills:retro` was never typed, no `retro-writer` agent was dispatched (0 of 27), `writing-for-agents` was loaded once at `T:L294` rather than per retro, and retro records were applied by the parent and implementers, never proposed to you as candidates (`M/skills/engineering/retro/SKILL.md:11,25`). The repo's own rule (`ticket-retro.md:26-31`) is met; the skill's is not. | R1 P2-4 | §6 workflow steps 3 and 6; CT-19 (retro-writer brief) |
| P2-11 | Codex's packet `lane-ledger.json` still names `/root` (01a130ef) as source writer at `d2a4103`, and the `refresh-llvm-github-research` automation is ACTIVE (4 h rrule, target 01a12bd1, writes only under `github-research/`). On 2026-10-19 Codex resumes against a ledger that predates the takeover. | R3 P2-4 | `claude-takeover.md` supersession notice (sweep brief B) |
| P2-12 | `findings.md` "Inherited limitations" is stale: the latest manifests of the three marketplace threads (05:10Z and 05:19Z on 10-13, policy `strict-five-v2`) show Context7 `ok` and Discussions `empty_verified`, with Firecrawl Search provisional (Serper after HTTP 402) as the one remaining gap; the newest manifest on the host (`01a13185`, 07:44Z) shows Context7 `error`, so the narrowed gap holds for the marketplace threads only. | R3 P2-3 | `findings.md` |
| P2-13 | Subagents received the same 30-line plan view up to 15× each (214 frames across 27 transcripts) despite 3.24.0 suppression; cause likely the `prompt_id` in the cache digest (unverified). Mitigation is a small smart view, not reliance on suppression. | R4 P2-4 | CT-15 |
| P2-14 | `lanes/*.json` and the `task_plan.md` lane table disagree on every row that matters (8 integrated vs "planned/allocated/in progress"); `stop_gate.py` reads only the JSON, so the table is dead weight. | R4 P2-5; index | CT-15 (regenerate or drop) |
| P2-15 | Hook latency: the shell reference chain takes 7.6 s against a 10 s timeout; the Python twin 42 ms. If `python3` leaves the hook PATH (the `VIRTUAL_ENV` gotcha), injection goes dark silently. | R4 P2-6 | Pin `PWF_TRUSTED_PYTHON`; migration step 1 |
| P2-16 | Two Stop gates with different vocabularies would coexist if the plugin's `gated` mode were enabled; the repo's `stop_gate.py` should stay the only Stop gate; plugin `autonomous`/`gated` would also drop the PreToolUse view subagents depend on and force attestation on every plan edit. | R4 §Compaction | `claude-team.md`; CT-15 (`.mode` = `inject-smart` only) |
| P2-17 | `base_sha` in lane records is systematically the pre-allocation tip (gate-hooks `e618243` vs cut `2d1f60e`; nav `7e22d13` vs `c6ff7ef`; c1 `447110a` vs `ca60871`), because the allocate commit cannot name itself; `merged_head` values are lane-side sync merges, not integration merges. | R5 P2-7, table | Corrections table; CT-17 `lane:allocate` records both |
| P2-18 | The only copies of the pre-merge `settings.json` are untracked or ephemeral (this directory and `/private/tmp`); `git merge --abort` would delete the merged file and not restore the old untracked one. | R5 P2-6 | Keep `settings.json.before-ct02` until the merge commit exists |
| P2-19 | Window A (grill → spec → tickets) died before tickets were approved, and the handoff schedules a `/clear` before to-tickets completes; the local `spec.md` mitigates the truncation risk the rule guards against, not the lost thinking. | R1 P2-2, #14 | Re-plan §6 |
| P2-20 | No final `code-review` over the integration branch is run or scheduled; no worktree cleanup; eight lane worktrees remain (ignored files only). `CODING_STANDARDS.md` was not an input to the one review that ran after it existed (gate-hooks re-review, `T:L1962`). | R1 P2-5, P2-6, #40 | Re-plan §6; D9 |
| P2-21 | Setup drift: `/setup-matt-pocock-skills` answered "already fully set up" after one read-only command; `docs/agents/issue-tracker.md` lacks the seed's "When a skill says publish / fetch" headings (so `to-spec`/`to-tickets` would default to `gh issue create`, which the repo forbids), the literal PR-surface flag and the Wayfinding block (`/wayfinder` unusable). | R1 P2-7, Setup validity; D2 gap 2-3 | Re-plan §6 step 2 (re-run setup) |
| P2-22 | The staged `retros/gate-hooks.md` claims `hk validate` rc 0 "under hk 2.6.0 and 2.5.0" (`:6,13`); the reviewer said 2.5.0 was not run. An unverified claim inside a gate-passing record. Also reviewer P3-2 (`/usr/bin/git merge` bypasses PreToolUse; cherry-pick/rebase/pull allowed) was relabelled as "add tests", P3-5 (after `hooks:install` every unpublished lane merge gates pushes) dropped, the re-review P3 (custom-subject merges unattributable) lost, and the implementer's two side effects (`feature/foo` refused at merge; a custom-subject merge unchecked at push) recorded nowhere. | R6 P3-5..9, row 21 | Corrections table (`retros/gate-hooks.md`); CT-02b |
| P2-23 | Briefs restate ticket bodies (3.5–6.8 KB, 55% boilerplate across 17 lane briefs) and point at no spec/tickets; the repo's `implementer`/`doc-writer`/`reviewer`/`retro-writer` definitions were never used. | R1 P3-2/#27; R7 E | CT-19 |
| P2-24 | The 19 Codex worktrees: 11 of 18 are dirty (not three as recorded; all verified superseded); `codex/28-offline-refresh` and `codex/29-offline-refresh` are unrecorded (content absorbed in the tip); `.agent/` (singular, Codex plan state, 48 K) is untracked and not excluded; the index wrongly called `.agents/` untracked (it is tracked, 13 files, `762b02f`, mirror identical). | R3 P3-1, P3-2; R5 P3-1, P3-2; R2 P3-6 | `findings.md`; `.git/info/exclude` += `.agent/`; index correction |
| P2-26 | The gate hooks' own contract has two inert or wrong properties (class I, J): `onFailure: block` on the Stop and SubagentStop entries of the staged settings has no effect on those events (docs), so it is not a safety property; and `GATE_TIMEOUT = 8` per lane in `git_gate.py:34` can exceed the 10 s hook timeout across lanes (`J.timeout-arithmetic`). | C4 claims 12, 19; C1 §J | CT-02b (deadline deny-with-reason; drop the inert flag from the C2 snippet; the staged file's copies may stay) |
| P2-25 | Items the Codex briefs surfaced that no record carries: ticket 30 of the dynamic-agents graph (thread 01a13185) targets this repo's `.codex/` and `hooks.json`, a collision risk for CT-07; four stale Codex Desktop attachments bind the `issue-13-lsan` worktree to 01a130ef, which is what B2 #91 repairs. Also top-level `additionalDirectories` (now in `settings.local.json`) is not a documented settings key (only `permissions.additionalDirectories` is) and is probably inert; kept verbatim, you decide. Wayfinder `research/<name>` branches must stay local until an admitted A09 publish, which the skill does not expect. | R3 lost items; R5 P3-4; D2 gap 9 | `task_plan.md` out-of-scope sentence (ticket 30); ledger #91 row; D4; `docs/agents/issue-tracker.md` (research branches) |

### P3 (polish), grouped

- **Records and text drift** (R5 P3-3..P3-6; R6 P3-12/13; R1 P3-4/5/7/9): all integrated lanes still say "publication pending" though every integration merge is in origin `28fedf1`; the handoff claims local tip = remote while `9cd396a` is unpushed; retro-gate/team/c1 retro lines cite first sync merges; `ticket-ledger.md:5` snapshot `05c3dc9` two publishes stale and without CT rows; `skill-invocations.md` hashes bind the cache while the session read the marketplace checkout (same commit `49dd158`, so the binding holds; say which path); `findings.md` does not point at the Codex briefs; the pwf hazards live only in user memory; the `extraKnownMarketplaces` documentation promised at `T:L1908` is absent from `.claude/AGENTS.md`.
- **Spec and tickets** (R2 P3-1..P3-8): commands and env-var names in ticket bodies; CT-04 AC "under sixty lines" vs exactly 60; CT-11 adds a fifth seam not agreed; glossary drift ("per-run confirmation" for *admission*, "integration owner"); Further Notes stale ("two lanes exist", v2.1.296); spec start SHA for the end-of-spec `code-review` unrecorded (`e0667ec` per R2, `361688e` per R8: see decision D10).
- **Codex import** (R3 P3-3..P3-5; R6 P3-2..P3-4): brief bookkeeping errors (turn and commit counts); the turn-6 mandates (mise-first, `com::rsm::<module>`, three targets, 30-day retention, canary checks) exist only in Codex-era `progress.md:1816,1838` and the digests; `01a13185`'s untracked 239 KB schema in `c658`, its `~/.codex/config.toml` edit and unversioned `~/.codex/skills`; the #28 frozen `ci/acceptance.sh` decision; C1's untested first-observation case; the Claude-era `progress.md` has no Codex-import entry at all.
- **pwf** (R4 P3-8..11): `findings.md` 56 lines vs ~400 lines of history in `task_plan.md` (inverted split); the "NEXT rewritten in place" rule contradicts the append-only rule; `task_plan.md:10` tells agents to set pins that no settings or brief carries; `session-catchup.py --metadata` (158 unsynced entries) was never run after `/clear`.
- **Process** (R1 P3-1/3/6/8/10; R6 P3-10/11; R7): glossary drafted to scratchpad and shipped by a lane 40 minutes later rather than inline; CT-02 breached the unit limit (11 files, +806) without a reported split; breakdown shown with file paths; `## Agent skills` block lacks `### Issue tracker`; the cold `/mattpocock-skills:domain-modeling` keystroke in the setup session did nothing; claude-code-guide caveats (trust-held hooks, `disableAllHooks`, managed settings) absent from `claude-team.md`/ADR 0001; "evaluate `agent_type` for SubagentStop" and the plugin `CLAUDE.md` importer deferred with no ticket; 13 of 27 subagents recorded faithfully, 12 partially, 2 lost.

Contradictions resolved: agent count is **27** (the index heading said 28; its table lists 27 and 27 transcripts exist). `.agents/` is tracked; `.agent/` is not. The settings keys: lane commit, not merger (P1-2). Codex stop causes: trees died on the usage limit (P2-10). Ticket numbering: R2 and R7 both minted CT-12…CT-17 with different meanings; the unified list in §6 wins and R8's wave unit names are mapped there. PreToolUse repair placement: R2 P2-6 and R7 O want it inside CT-02 before integration; R5 and R8 integrate as reviewed and fix in CT-02b first in wave 1; this synthesis takes R5/R8 because `e12cf04` is the reviewed tip and the false positive only slows Bash calls, it cannot lose work. Trailers: R5's runbook block names Opus 5.5; the executing session uses its own attribution lines.

### 2b. Root causes and prevention (C1 → C4, binding: C4)

C1 traced every finding through 39 causal chains to **14 root-cause classes**; C2 (prevention) and
C3 (detection) designed one artifact set per class; C4 checked coverage against the designs, the
Claude Code docs and the live tree and reconciled the tickets (verdict APPROVE WITH CHANGES, 13
changes; KEEP 29 / MERGE 16 / DEFER 10 / DROP 8 over 56 artifacts). Class per finding (C1
coverage matrix, primary first): P1-1 A,C,B · P1-2 I,G · P1-3 I,C · P1-4 G,B · P1-5 H · P1-6 E,N ·
P1-7 D · P1-8 E,D · P1-9 E,B · P1-10 L,H · P1-11 K · P1-12 F · P1-13 H,B · P1-14 A · P1-15 F ·
P2-1 C · P2-2 C · P2-3 J · P2-4 H,G · P2-5 G,I · P2-6 N,E · P2-7 N,L · P2-8 E · P2-9 M,E · P2-10 M,B ·
P2-10b D,F · P2-11 M · P2-12 M,B · P2-13 K,A · P2-14 B,K · P2-15 I,K · P2-16 I · P2-17 B · P2-18 L,C ·
P2-19 A,D · P2-20 F,C · P2-21 D,I · P2-22 G,H · P2-23 F · P2-24 M,B,L · P2-25 G,L · P2-26 I,J.

| Class | Name | Findings | Invariant (C1, condensed) | Wave-0 artifact (C4) | Detector ids (C3, surviving) | Ticket |
|---|---|---|---|---|---|---|
| A | Context budget blind; forks inherit a full window | P1-1, P1-14, P2-19, P2-13 | ctx at every `Agent(fork)` < `fork_deny` (500 K); ctx < `warn` (400 K) or the turn names the phase boundary; `autoCompactEnabled ≠ false` | W0-1 settings keys; W0-3 `dev/context_budget.py`, `dev/hooks/agent_gate.py` (`fork_budget`), `dev/hooks/prompt_hook.py` (ctx line); one threshold dict in `dev/doctor/budget.py` (warn 400 K / checkpoint 550 K / fork_deny 500 K / hard 650 K, all < `autoCompactWindow` 700 K) | `A.autocompact-off`, `A.fork-over-budget`, `A.previous-session-died`, `A.ctx-over-checkpoint` | CT-23 (follow-up), CT-22 |
| B | Records derived by hand, never from git/tracker/gate | P1-1, P1-4, P1-9, P1-13, P2-10, P2-12, P2-14, P2-17, P2-24 | `base_sha` = the commit that added `lanes/<unit>.json`, `allocated_from` = its parent; `retro: passed ⇒ retro_gate --unit rc 0`; `published ⇒ integration_merge ∈ origin`; plan Lanes table = records projection | W0-4 doctor `lanes.py` (status-stale, review-missing, retro-claim, base_sha via allocation commit); W0-5 hk `pre-commit` `records` step (settings rule first; `lane:validate --staged` joins with CT-05) | `B.base-sha-off-by-one` (predicate fixed per C4 change 2), `B.review-missing`, `B.retro-claim-unverified`, `B.status-stale`, `B.handoff-base-stale`, `B.plan-table-vs-lanes` | CT-05, CT-17, CT-22 |
| C | Integration non-resumable; gate bypass by merge form; ordering unwritten | P1-1, P1-3, P2-1, P2-2, P2-18, P2-20 | no `MERGE_HEAD` at Stop/SessionStart without a runner journal; no `git merge … --no-commit` token on the integration branch; `hooks:install ⇒ inspect-hooks` passes; lane merge paths ⊆ allowlist | W0-4 doctor `integration.py` (`C.merge-in-progress`, foreign hunk, snapshot); W0-7 docs (`--no-ff`, never `--no-commit`) | `C.merge-in-progress`, `C.no-commit-merge`, `C.foreign-hunk`, `C.hooks-break-delivery`, `C.hooks-not-installed`, `C.untracked-overwrite-risk`, `C.worktree-after-publish` | CT-02b, CT-17, CT-22 |
| D | User-invoked skills emulated and misrecorded; no invocation receipt | P1-7, P1-8, P2-10b, P2-19, P2-21 | no `docs/agents/*.md` line matches `standing authorization\|invocation authority`; every `typed`/`native` invocation row has a harness event; `issue-tracker.md` carries the installed seed's headings | W0-3 `prompt_hook` slash-in-paste warning; W0-7 D15 rewrites | `D.invocation-row-unbacked` (reads `Skill` tool_use from the transcript), `D.doc-wording`, `D.seed-drift` (heading check; hash pin deferred), `D.plugin-version-drift` | CT-22 (static), CT-20 (transcript) |
| E | No ledger of requests, decisions, pending operations; approval assumed | P1-6, P1-8, P1-9, P2-6, P2-8, P2-9 | every operation decision has a receipt before `plan:handoff --check` passes; `lanes/*.json tickets[]` ⊆ approved ids | W0-6 `P/decisions.jsonl` seeded (#91 relabel, draft PR, T4 budget, to-tickets approval pending) + `dev/plan_decide.py` minimal | `E.operation-unreceipted` (SessionStart line, not a Stop block), `E.approval-missing`, `E.request-uncaptured` (session-review only; per-prompt capture deferred) | CT-24 |
| F | Roles and briefs not machine-sourced; agent list frozen at session start | P1-12, P1-15, P2-10b, P2-20, P2-23 | every lane `Agent` call uses a role agent; implementer transcript has `Skill(tdd)` before its first `.py` write; agents on disk = agents offered | W0-3 `agent_gate.lane_dispatch` rule 1; W0-4 doctor `agents.py` (mtime roster) | `F.agents-not-offered`, `F.lane-dispatch-generic`, `F.tdd-not-first` (session-review; the SubagentStop block is deferred), `F.brief-oversized`, `F.role-file-stale`, new `G.retro-author-not-retro-writer` (C4 change 8) | CT-19, CT-23, CT-22 |
| G | Subagent reports condensed by the parent; no machine receipt | P1-2, P1-4, P2-4, P2-5, P2-22, P2-25 | every lane-role SubagentStop appends a journal line under `<git-common-dir>/claude-lanes/<unit>.jsonl`; `review` field = journal's last reviewer disposition; every reviewer `P-n` has a retro row | — (wave 2) | `G.disposition-vs-record`, `G.p-item-unrecorded` (at `lane:integrate` preflight), `G.journal-missing`, `G.open-claim-dropped` | CT-19, CT-22 |
| H | Shape-checked gates mistaken for truth | P1-5, P1-10, P1-13, P2-4, P2-22 | every `dev/test_*.py` is wired; `retros/<unit>.md` exists for every `retro: passed`; deferral rows cite an issue the ledger knows; pinned evidence paths resolve with their SHA | W0-4 doctor `gates.py:unwired_tests()` | `H.unwired-test`, `H.retro-unit-alias` (recurrence only; the alias in `retro_gate.py` is dropped, runbook step 7 renames), `H.retro-deferral-unbound`, `H.pinned-data-missing` (via CT-21 `check_inputs.py`) | CT-12, CT-21, CT-22 |
| I | Configuration composition and cross-tool contracts unvalidated | P1-2, P1-3, P2-5, P2-15, P2-16, P2-21, P2-26 | `keys(.claude/settings.json) ⊆ {$schema, hooks, enabledPlugins, extraKnownMarketplaces, env}` and every project plugin's marketplace declared; `hooks:install ⇒ safe_configured_hooks` accepts; `P/.mode` has no `gate`; `env` carries the pwf pins | W0-1; W0-5 pre-commit settings rule; doctor `settings.py` | `I.settings-non-project-key`, `I.settings-plugin-undeclared-marketplace`, `I.settings-local-not-excluded`, `I.mode-gate`, `I.mode-absent`, `I.pins-missing`, `I.lane-admission-missing`, `J.timeout-arithmetic` (kept in `settings.py`) | CT-16, CT-02b |
| J | Gate hooks without a real-command corpus or a latency contract | P2-3, P2-26 | over the 113-command corpus the gate denies exactly the real merge/push/publish segments; wall time < timeout − margin else deny-with-reason | W0-2 corpus `dev/fixtures/hooks/bash-corpus.jsonl` (labelled by the parent) | `J.corpus-mismatch`, `J.hook-latency`, `J.hook-error-observed` (unit test in `test_hooks.py`, not a `check` detector) | CT-02b |
| K | Planning files unstructured; progress by append; no host pin | P1-11, P2-13, P2-14, P2-15 | `task_plan.md` has Goal / Next Step / Current Phase / exactly one `in_progress` phase; `size(progress.md) < 900 KB`; from a lane worktree the pretool view shows the root nonce | W0-1 `env.PLAN_ID` (+ local pins); runbook step 9 migration | `K.plan-no-phases`, `K.plan-missing-keep-section`, `K.progress-size`, `K.subagent-reinjection` (sweep) | CT-15, CT-22 |
| L | Outputs in ephemeral or untracked locations | P1-10, P2-7, P2-18, P2-24, P2-25 | every cited artifact resolves to a tracked path, a journal path or a `~/.codex` path with a SHA; no record cites `/private/tmp` or `scratchpad`; untracked top-level dirs are tracked, excluded or listed | W0-7 `.git/info/exclude` entries; `dev/exclude.txt` as the one allow-list | `L.untracked-top-level`, `L.scratchpad-citation`, `L.cited-path-missing` (CT-21 resolver), `L.external-citation-unhashed` | CT-21, CT-22 |
| M | Codex thread/packet state imported by hand | P2-9, P2-10, P2-11, P2-12, P2-24 | activation-record fields equal `codex:status` output (last-turn status, failed children, ACTIVE automations, packet writer, newest manifest statuses, packet `terminal` state); each superseded packet holds a supersession file | — (sweeps A/B/C done by hand this once; supersession notice in step 7) | `M.activation-record-drift`, `M.automation-active-unrecorded`, `M.packet-not-superseded`, `M.worktree-census-drift` | CT-10 (`codex_status.py`, `codex:supersede`), CT-22 (thin caller) |
| N | Ticket pipeline unvalidated before build | P1-6, P2-6, P2-7 | manifests have a real or `null` parent, unique ids, acyclic in-set edges, builder count = ticket count; `lanes/*.json tickets[]` resolve to tracker issues or approved ids | — (runbook step 11 edits) | `N.manifest-placeholder-parent`, `N.manifest-count-mismatch`, `N.manifest-order`, `N.manifest-dangling-edge`, `N.manifest-cycle`, `N.builder-scratchpad-input`, `N.approval-missing`; semantic edges remain approval-only (justified) | CT-22, CT-17 (`lane:allocate --ticket` refusal), CT-24 |

**The five C4 coverage gaps and how they close** (all ≤ 40 lines each): P2-9 (no probe reads
`TERMINAL.json` budgets): `codex_status.py` gains a `terminal` field per packet (CT-10; the ledger
row is a step-7 edit meanwhile). P2-10b (retro authored by implementer or parent, no
`retro-writer` stop): new detector `G.retro-author-not-retro-writer` with a fixture, `skipped`
before CT-19. P2-12 (no test for the manifest-line requirement): one `codex_activation.py` test
case (CT-10). P2-17 (detector predicate could never fire): derive the allocation commit as the
commit that added `lanes/<unit>.json` (or the `docs: allocate lane <unit>` subject), assert
`base_sha == allocation` and `allocated_from == allocation^`, fixture built so the vacuous form
fails (CT-22a). P2-20 (no test for `holds`/worktree removal; no artifact for the final
`code-review`): `lane:validate` test T-B8 (`published ⇒ worktree_removed ∨ holds`) in CT-05, and
`plan:handoff --check` lists outstanding stage steps from `spec.manifest.json` (CT-15).

**Three claims struck from the designs** (C4 claim table): (1) "`base_sha` equals the parent of
the first commit in `git rev-list --reverse --first-parent <base_sha>..<branch>`" is vacuous (the
first commit of `X..branch` always has parent `X`); (2) `onFailure: block` is meaningful on Stop
and SubagentStop: it is inert there per the hooks docs (keep it only on PreToolUse); (3)
"`python3 -I` enforces stdlib-only" is wrong (`-I` only isolates env, user site and the script
dir); enforce with an AST rule against `sys.stdlib_module_names` in `dev/doctor/gates.py`.

## 3. Answers to your questions

**(1) Are we following the mattpocock workflow properly, and which other skills should we use?**
No. The five workflow skills (and triage, wayfinder, implement, setup, handoff, grill-me) are
`disable-model-invocation: true`: only you typing `/mattpocock-skills:<name>` fires them, and no
session or skill can. The session natively ran `grilling`, `domain-modeling`,
`writing-for-agents`, `skill-creator` and `agentsview-finding-history`; it `cat`-ed the five
SKILL.md files and followed them by hand ("file-guided"). Against D2's 45-item checklist: 23
pass, 14 fail, 6 n/a. Stage verdicts: setup incomplete; grill partial (faithful interview, router
never fired, glossary delegated); to-spec partial (draft complete, unpublished by design);
to-tickets not complete (shown once, never approved or published); implement-spec emulated (lanes,
cold reviews, frontier respected, but no `tdd`, `--no-commit` merges, hooks never installed, no
final `code-review`, no cleanup, died mid-merge); retro partial (repo gate met, `/retro` never
typed, docs conflate the skill with the repo procedure). Adopt now: re-run
`setup-matt-pocock-skills` (seed drift), `ask-matt` as router, `tdd` inside every implementer
(dispatch the `implementer` agent), `code-review` once per spec with a recorded fixed point, `pr`
for the draft PR, `handoff` only for the Codex resume on 2026-10-19 or a colleague/prototype,
`wayfinder` for the C++26 P2996 core (after setup), `to-questionnaire` for the decision list in
§8, `improve-codebase-architecture` on `dev/hooks` + `dev/retro_gate.py` + `dev/git_delivery.py`
after CT-02 lands. Do not triage #69–#108 (they are to-tickets output). `claude-handoff`,
`chief-of-staff`, `loop-me` are not shipped (in-progress); evaluate under CT-09 only.

**(1b) Is anything missing or wrong in the to-spec output?** Template, seams (approved in
round-2 Q6), glossary nouns and no-paths all hold. Of 29 decisions you made, 19 are carried, 7
partially, 3 missing: the draft PR to `main`, the B2 #91 relabel, and your 19:14 AskUserQuestion
mod (which the spec misstates as "evaluated, not built"). CT-01 cannot be closed honestly (AC2
false). Two edges are not real, CT-09 is four tickets, the manifest is unpublishable (placeholder
parent, no edge graph, stale builder). R2 §"Revised breakdown" is the 16-item list to approve.

**(2) Did it thoroughly review the Codex sessions, or is another sweep needed?** The four
briefs are accurate: every SHA, decision and end state spot-checked binds, including the
`848552c` correction. The census found 175 threads touching the repo, none a writer beyond the
four, nine children mid-turn at the usage limit, the heartbeat still ACTIVE. What the digester
could not see (its 400-call write window) is in the worktrees, the packet and the state dir: the
`2a14` dependency and evidence (P1-10), T4's terminal state, the packet ledger that will
contradict the takeover on resume. **No full re-sweep**; run R3's three bounded briefs (A:
`2a14`/`c658` inventory with hashes and dispositions; B: packet and T4 state for the CLOSE lane;
C: the nine dead children), ≈200 KB in, ≈6 KB out.

**(2b) Was planning-with-files used natively, and is everything tracked?** No and no. The
plugin injected head-50/tail-20 passively; every structural feature was blind because the plan
has no `### Phase`/Goal/Next Step/Current Phase sections; progress by append cost ~430 KB of
re-injection in one session; no host pin, so worktree hooks read stale copies; subagents got the
same view 15×. Not tracked: no CT list anywhere in `task_plan.md`, the lane table is stale on
every row, pending decisions exist only in prose. Compaction: `PreCompact` never fired (the
session hit the hard limit without a compaction cycle); recovery after `/clear` is the same
50/20 view. Recommended: stay in legacy injection + `inject-smart` token + `PWF_PLAN_ROOT`/
`PLAN_ID`/`PWF_TRUSTED_PYTHON` pins + per-lane ledgers (`ledger-append.sh`), keep
`stop_gate.py` as the only Stop gate, do **not** enable `autonomous`/`gated`, restructure
`task_plan.md` per R4's verified skeleton, archive `progress.md`, move history to `findings.md`.
Avoid `/plan`, `/pwf`, `/start`, `/plan-attest` while the parent edits the plan; `/plan-doctor`
and `/status` are safe.

**(3) How do we parallelize in worktrees with minimal merge conflicts?** R8: a serial wave 0
(finish the merge, publish, fix records, split mise tasks into `mise/tasks/<unit>.toml`
includes, publish tickets), then waves of four offline lanes plus at most one heavy slot, each
cut from the previous allocation commit, with disjoint `owned_paths` and one owner per wave for
`dev/check.py`, `dev/hooks/`, `dev/lane.py`, `claude-team.md`, `AGENTS.md`. Lanes never write
`progress.md`, `task_plan.md`, the ledger, lane records (parent-only), `mise.dev.toml` or
`.claude/settings.json`; they append to their own ledger. Integration one merger at a time,
`--no-ff` without `--no-commit`, `check:research` serialized (CT-11 lock), A09 publish after
each integration, branches deleted only after publish. Wave 1 (unified numbering): CT-02b gate
follow-up, CT-11 check lock, CT-05 ledger + `lane:set|validate`, CT-15 plan records.

**(4) What should be automated?** R7's ranked backlog: `lane:integrate <unit> [--continue|
--abort]` (≈40 K tokens/session; would have recovered the dead merge); `lane:set`/`lane:validate`
(`retro` derived from a gate run, never assigned); `plan:log`/`plan:handoff --check`; `lane:brief`
+ slotted agent definitions + SubagentStop receipt journal; `lane:allocate` (records base and
allocation commit); `ledger:sync` (CT-05); `delivery:publish-batch`; `session:status` probe;
`/lane-retro` (CT-06); `agent-session-history` + `/session-review` (this review as a skill);
quick wins first: PreToolUse gate fixes and a check that every `dev/test_*.py` is wired.

**(5) What else should a session sweep do so no debt is carried?** Beyond what this team did
(diff the live tree against every record; read every task-notification the dead session received
after its last record write; grep the records for the user's own queued messages; run the repo's
gates read-only against the records; check that every retro "owner" ticket carries the item;
probe the recovery path without `/clear`; list what exists only in ephemeral dirs; verify "already
set up" claims against the plugin seeds; run `session-catchup.py --metadata`), the prevention team
turned the sweep into tooling: the **doctor** (CT-22, `dev/doctor/`, surfaces `session-start |
check | pre-commit | integrate | publish | sweep`, `--format context`, `--fix` for proven-by-git
facts only) runs the static detectors on every session start and in `check`; the **session hooks**
(CT-23 after the W0-3 seeds: ctx line on every prompt, fork-over-budget deny, `general-purpose`
lane deny) stop the two new root causes live; and the **session review** (CT-20,
`agent-session-history` + `/session-review <session-id>`, `doctor --surface sweep`) digests a dead
session's transcript and subagents for the transcript-only detectors (A curve and death point, C
`--no-commit`, D invocation rows, E requests, F dispatch and tdd order, G receipts, J observed
timeouts, K re-injection). The **SessionStart block** every new session will see (W0-4) carries:
auto-compact state, agents on disk vs offered, merge in progress, staged foreign hunk, stale
records, previous session died, unreceipted operations, untracked top-level dirs.

## 4. Record-correction list

Values from R5's table (git reality verified) unless marked.

| File | Field / line | Current | Correct |
|---|---|---|---|
| `P/lanes/gate-hooks.json` | `base_sha` | `e618243` | `2d1f60e` (allocation commit; add `allocated_from: e618243`) |
| `P/lanes/gate-hooks.json` | `status` | implemented (Opus), awaiting cold review | integrated into codex/marketplace-native-onboarding (cold review PASS-with-P2, repairs `dec8425`, re-review PASS 21:04Z); published `<sha>` after A09 |
| `P/lanes/gate-hooks.json` | `lane_commit`, `merged_head`, `review`, `retro`, `integration_merge`, `published` | absent | `0c2748e`+`dec8425`; `e12cf04` (merge of `d0d6d4d`); `PASS-with-P2 → re-review PASS (a221b354)`; `passed` only after `retro:gate` rc 0 on the integrated tree; the new merge SHA; the A09 SHA |
| `P/retros/gate-hooks.md` | `:3` | base `2d1f60e` | add "(allocated from `e618243`)" |
| `P/retros/gate-hooks.md` | `:5` vs `:33` | 10 tests / 13 tests | "10 before repair, 13 after `dec8425`" |
| `P/retros/gate-hooks.md` | `:6,13` | `hk validate` rc 0 under 2.6.0 and 2.5.0 | 2.6.0 only was run by the reviewer; record 2.5.0 only after Runbook step 5 runs it |
| `P/retros/gate-hooks.md` | `:19` | five lane records lack `retro: passed` | resolved in `4870211` |
| `P/retros/gate-hooks.md` | `:20,36-37` | `test:hooks` out of `check:research` (owner parent); `extraKnownMarketplaces` parent decision | "applied at integration (`mise.dev.toml` `check:research` depends)"; settings composition per R5 §B |
| `P/retros/gate-hooks.md` | `:33` P3-2/3 | "add tests" | restore the reviewer's P3-2 (`/usr/bin/git merge`, cherry-pick/rebase/pull bypass PreToolUse), P3-5 (after `hooks:install` unpublished lane merges gate pushes) and the re-review P3 (custom-subject merges unattributable; match `^Integrate lane`), each with owner CT-02b |
| `P/retros/gate-hooks.md` | new row | — | re-review PASS disposition; the merger-fork death; settings decision; `hooks:install` deferral (owner CT-02b) |
| `P/lanes/nav.json` | `base_sha`; add `integration_merge` | `7e22d13`; — | `c6ff7ef`; `fa892d2` |
| `P/lanes/c1-catalog-promotion.json` | `base_sha`; `merged_head`; add `integration_merge` | `447110a`; `7295463 (merge of e618243)` | `ca60871`; `6c09b7f (7295463 = merge of 2d1f60e)`; `4c1ea6b` |
| `P/retros/c1-catalog-promotion.md` | `:6` | merged with `e618243` as `7295463` | merged with `2d1f60e` as `7295463` |
| `P/lanes/retro-gate.json` | add `integration_merge` | — | `e618243` |
| `P/retros/retro-gate.md` | `:3` | merged with `c8f4e64` as `0f7ddad` | append: final tip `82c351f` (merge of `9d478cd`) after repair `5ea8ee4` |
| `P/lanes/team.json`, `P/retros/team.md:4` | `lane_commit`; add `merged_head`, `integration_merge` | `9103931` | `5107322` (+ sync `9103931`, `5becfc0`, repairs `ea8c8c9`); `ea8c8c9`; `7e22d13` |
| `P/lanes/a06-unit3.json` | `retro` | passed | keep only after the gate resolves the unit: either `retro_gate.py` learns a `retro_record` alias field or the record is copied to `retros/a06-unit3.md`; until then "passed (record `a06-classification-methods.md`, gate rc 0 under that name)" |
| `P/lanes/{a06-unit3,codex-session-history,rf-env-scrub}.json` | add `integration_merge` | — | `361688e`, `55f3946`, `447110a` |
| all integrated lane records | `status` | "… publication pending" | "… published `28fedf1`" (or `f250f75` where earlier) |
| `P/ticket-ledger.md` | `:3-5` snapshot; rows | tip `05c3dc9`; no CT rows; #69 "publication pending" | tip after publish; add CT-01…CT-20 rows (state, lane, blockers); #69 "published `f250f75`; retained corpus + schema exist only in `2a14` (P1-10)"; #101 "T4 STOPPED/NOT_COMPLETED, TimeoutError, budgets 3/3, children batch VERIFIED, parents unsent, postimages at `~/.local/state/marketplace-llvm23-fork-01a12bd1/remaining-work-20261013/t4-parent-metadata/postimages/`"; #94/#95 "focused-search proposal unrun"; #97 "dependency-link replacement moot after M0 (confirm)" |
| `P/task_plan.md` | `:14-30` handoff; `:79-92` lane table; structure | stale; stale; prose only | restructure per R4 skeleton (Goal / Next Step / Current Phase / Phases / Tickets / Lanes / Decisions / Errors); Next Step = Runbook step 1; lane table regenerated from `lanes/*.json`; move `:98-566` to `findings.md` dated sections |
| `P/task_plan.md` | "Pending user decisions" | two | the list in §8 |
| `P/progress.md` | policy | 3429 lines, NEXT last | archive `:1-3412` to `progress-archive-2026-10-13.md`; new file with entries since `28fedf1`, incl. the `28fedf1` success, the gate-hooks review/re-review, the pwf review, the merger-fork death, this review |
| `P/findings.md` | "Claude takeover"; "Inherited limitations"; new | stale | add: Codex tree state (nine dead children; `01a13590` wrote `qbj4yn5d/a06-unit3/integration-preparation/verify.py`); `2a14` inventory pointer (sweep A); `c658` untracked 239 KB schema; `~/.codex/config.toml` edit; unversioned `~/.codex/skills`; `codex/28|29-offline-refresh` absorbed; the strict-five narrowed gap (Firecrawl Search provisional) with the three manifest paths; pointer to `reviews/ccm-20261013/codex-briefs/`; the pwf hazards (1 MiB cliff, second plan dir, stale worktree copies) |
| `P/skill-invocations.md` | `:20` | grill-with-docs "typed by user" | "pasted as text in the first prompt (`T:L21`); not expanded by the harness; router body executed file-guided"; add the setup-session rows (`/mattpocock-skills:domain-modeling` 18:39:06Z no-op; `/setup-matt-pocock-skills` 18:39:23Z "already fully set up"); note SKILL.md read from the marketplace checkout (same commit `49dd158`) |
| `docs/agents/claude-takeover.md` | `:11` | "runs under the user's standing authorization (round-1 Q3)" | "`to-spec`, `to-tickets`, `implement-spec` and `retro` were applied file-guided at the user's round-1 Q3 request; they have not been invoked. A stage counts as invoked only when the user types it; `skill-invocations.md` records each." |
| `docs/agents/claude-takeover.md` | `:7-10`, `:45-47` | stop causes; "no thread mid-turn"; #12/#24/#25 next work | trees died on the usage limit (nine children 14:07–14:09Z); automation `refresh-llvm-github-research` ACTIVE (4 h rrule, target 01a12bd1, last cycle 20261013T102218Z, writes only `github-research/`); packet `lane-ledger.json` superseded (resuming Codex must read this record first); next work = §5/§6 |
| `docs/agents/ticket-retro.md` | `:4-8` | "follow the user-invoked `$mattpocock-skills:retro` procedure … this standing user request is the invocation authority" | "run the lane retrospective below (its seven categories are those of the `retro` skill); `/mattpocock-skills:retro` is separate, typed per session by the user, and proposes only" |
| `docs/agents/claude-team.md` | `:95`; merge rule; hooks | "CODING_STANDARDS.md arrives with CT-04"; `--no-commit then commit` | CT-04 integrated; merges `--no-ff`, never `--no-commit`, `retro:gate` by hand until hk layer 2 is installed; document the two-gate situation (lane state vs pwf phase state) and the claude-code-guide caveats (trust-held hooks, `disableAllHooks`, managed settings) |
| `.claude/AGENTS.md` | — | no `extraKnownMarketplaces` note | one line: project marketplaces declared in `settings.json`, personal ones in `settings.local.json` |
| `P/proposals/claude-takeover-spec/build_manifests.py` | `:5-6`; `TICKETS` | "ten tickets"; `../../drafts/…`; CT-11 before CT-10 | "sixteen tickets"; `spec.md` beside it; order CT-10 before CT-11; edits per R2 (drop two edges, split CT-09, add CT-12…CT-16, state lines CT-01…CT-04) |
| `P/proposals/claude-takeover-spec/spec.md` | `:61` Out of Scope; `:65` Further Notes | "a UI mod (evaluated, not built)"; "two lanes exist" | drop the UI-mod sentence (CT-13 carries the request) or get your explicit "no"; name T3 #93 / T4 #101 as the Phase C closure carriers; the `implement-spec` union plan; spec `start_sha` (D10); refresh lane count |
| `00-evidence-index.md` (this dir) | heading "28"; `.agents/skills` untracked | — | 27 agents; `.agents/` tracked, `.agent/` untracked |
| `.git/info/exclude` | — | — | add `.agent/` and `.planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/settings.json.before-ct02` (personal keys; never committed) |
| `docs/agents/issue-tracker.md` | new | — | under the seed's "When a skill says publish / fetch" heading: the `issue:*` mapping; `research/<name>` branches from wayfinder stay local until an admitted A09 publish |
| `docs/agents/` (claude-team.md or a new secrets note) | new | — | secrets posture (N1): no secret in any settings file or mise `[env]`; keys live in `~/.config/fnox/config.toml`; tasks that need a key use `fnox --config ~/.config/fnox/config.toml --profile <name> --no-defaults --no-daemon --non-interactive exec -- <command>`; project requirement fnox ≥ 1.39.0; re-enabling `_.fnox-env` in mise is a separate ticket (macos-development-environment #75 governs) |
| `P/ticket-ledger.md` #91 row | local state | — | B2 repairs the four stale Desktop attachments binding `issue-13-lsan` to 01a130ef |
| `P/ticket-ledger.md` #62–#78 rows | local state (sweep B) | "closure pending" | per-row closure prerequisites: #62 A01 `CODE_CRITERIA_READY`, needs the final parent closure packet and common holds (qualified acceptance-close `issue:completion-preview → issue:apply → issue:verify`, fresh preimages, slot release, admission, settled retro, prerequisite disposition); #63 A02 `PARTIAL_NOT_YET_READY` (archival supplement awaits independent review; captures only in `2a14`); #64–#68 `CODE_CRITERIA_READY` chained on #63/#64/#65/#66/#67; #69 A06 no closure inventory, needs the CT-21 import; #70 A07a and #71 A07b need the T3 helper-byte refresh and a fresh #11 postimage; #72–#78 not prepared at all. Four hash-bound inputs drifted behind the tip (`mise.dev.toml`, `docs/onboarding.md`, `dev/issue_amend.py`, `dev/test_issue_amend.py`): every `CODE_CRITERIA_READY` verdict was reviewed against pre-T3 bytes |
| `P/ticket-ledger.md` #101 row | local state (sweep B) | "parent-spec closures pending" | T4 attempt 3 `STOPPED/NOT_COMPLETED`, `TimeoutError` after a 901.8 s approval wait (cap 900 s), children RF1–RF4/W1 `VERIFIED/sent`, parent batch #79–#82 previewed, never applied; `original_budget 3/3`, `recovery_budget 3/3`; `phase-c-policy-v2.md`: "does not grant a fourth attempt"; postimages target three repo files (`docs/research-feedback-retro/README.md`, `ticket-draft.md`, `workflow-authority-amendment.md`), all drifted from the tip; a new attempt needs a fresh user-approved budget, a fresh issue-write interval and rebuilt parent packets (D25) |
| `docs/agents/claude-takeover.md` | activation record | "no Codex thread is mid-turn" | sweep C's sentence: "No Codex root thread is mid-turn, but nine spawned children died inside a turn on the usage limit (eight at 14:07–14:09Z on 2026-10-13, `01a128a0` on 10-12); they wrote only to private packets and `~/.local/state`, ran no Git mutation outside private clones, and the one in-flight process — Carson's T4 Phase C runner under `01a12bd1`'s issue-write slot — sent six child closures, then timed out waiting for a parents-batch approval and stopped at 14:21:50Z." |
| `docs/agents/claude-takeover.md` | new fenced block | — | sweep B's supersession notice: the packet `lane-ledger.json` (14:07:45Z) and the `remaining-work-20261013` state dir are read-only history; their source-writer and shared-Git slots (`/root` at `d2a41032`/`848552cd`), A06/#28/#29 lane rows, T1/T3 holds and the consumed T4 interval are not live; a Codex thread resuming after 2026-10-19, including the `refresh-llvm-github-research` automation (writes only under `github-research/`), must read this record first, must not act on the packet's owners or "closure pending" dispositions, and must not start a T4 parent-spec closure or any ticket close without a new user-approved budget and a recorded admission |
| `docs/accepted-decisions.md` | new section | — | the +52-line "Automation and observability clarification (2026-10-12)" user-decision block that exists only in `2a14` (sweep A; diff in `P/imports/codex-worktrees-20261013/2a14/modified/docs/accepted-decisions.md.diff`); parent applies in step 7; T2 could not verify hunk 2 is the user's wording (ask) |
| `dev/checkout_transfer.py` | `:17` | `OLD = …/worktrees/2a14/…` hard-coded host path | `SOURCE` from `__file__`, `OLD` from `--old` or `MARKETPLACE_OLD_WORKTREE`, `Refusal` naming both when absent (CT-21 lane, T2 §b.3) |
| `P/findings.md` | "Claude takeover" bullet "Unpublished local tip: `c6caaca`, `d2a4103` …" | stale (hashes now in the tip at `8f783a0`) | T2's three replacement bullets: the snapshot (`imports/codex-worktrees-20261013/`, 454 files, 11.8 MB, `MANIFEST.json` SHA `259f9fae…`, 0700 mirror `~/.local/state/marketplace-imports/codex-worktrees-20261013`; only index files committed, payload excluded because it holds raw session streams and full issue bodies, 149 keep-private files / 6.6 MB); the 101 tip-cited paths that exist only there and CT-21's 119-file import (1,057,200 B, gitleaks 8.30.1 dir scan 0 findings, 18 iwyu build files declared mirror); the `accepted-decisions.md` block |
| `P/task_plan.md:322`, `docs/status.md:10`, `docs/agents/claude-takeover.md:26`, `docs/agents/codex-task-orchestration.md:6` | absolute `2a14` paths | — | rewrite to the imported relative paths after CT-21 integrates (parent hunks named in the lane record) |
| Memory `planning-with-files-injection.md` | "How to apply" | handoff block ≤30 lines, NEXT last | superseded by R4: structure + pins + ledgers; keep the window facts |

## 5. Repair runbook (Phase 3, after your approval)

Decision points to confirm first: **D1** finish the merge (Runbook 1) vs abort (Runbook 2);
**D2** defer `hooks:install`; **D4** settings composition (R5 §B default); **D3** approve R2's
revised breakdown before any `issue:*-apply`; **D11** run R3's three sweep briefs; **D12**
archive `progress.md`; **D8** per-lane ledgers and parent-only lane records (step 9 amends
`planning-records.md`); **D9** worktree cleanup and **D20** the PR/relabel (step 12); **D13**
digests (step 10); **D15** the invocation-wording rewrites (step 7). Preconditions for every step: `VIRTUAL_ENV` unset; one writer; no other
worktree running named checks; identity check (`git rev-parse --show-toplevel`, branch, HEAD
`9cd396a`, `MERGE_HEAD e12cf04`). The project hooks are live: expect PreToolUse denials on
commands containing "git merge"/"git push" text until CT-02b lands; `git commit` is never gated.

1. **Snapshot.** Copy `.claude/settings.local.json` and `git diff --cached` to the scratchpad; keep `reviews/ccm-20261013/settings.json.before-ct02` (SHA-256 prefix `ee3bc512…`) until step 6 completes.
2. **Settings split (D4).** Write `.claude/settings.json` per R5 §B and `.claude/settings.local.json` per R5 §B **plus the `skillOverrides` key the local file already holds** (written 22:14Z by the review session's harness, after the fork; it stays local); `git add .claude/settings.json`. Verification (R5's one-liner as written cannot pass: the backup's `extraKnownMarketplaces` has five keys and R5 §B adds three): assert the project key set is exactly `{$schema, enabledPlugins, extraKnownMarketplaces, hooks}`; the local key set is R5's eight plus `skillOverrides`; `p["hooks"] == lane["hooks"]` (`git show e12cf04:.claude/settings.json`); `enabledPlugins`/`extraKnownMarketplaces` share no key across the two files; every project plugin's marketplace is declared in the project file; **backup ⊆ union** (every key/value of `settings.json.before-ct02` appears in the merged view of the two files minus `hooks`); and union minus backup is exactly the three marketplaces `mattpocock`, `brentmitchell25`, `astral-sh` with sources copied from `~/.claude/plugins/known_marketplaces.json`, plus `skillOverrides`. Then `git check-ignore -q .claude/settings.local.json` (rc 0). No secret values are involved (N1); nothing from `~/.config/fnox/` enters either file. Note this makes a second declared parent hunk in the merge (the marketplaces the lane reviewer kept out of the committed file at `T:L1908`); step 6's message declares both.
3. **Record fixes inside the merge.** First run `./dev/mise run retro:gate -- gate-hooks` on the staged record (expect rc 0, as today). Then edit `P/retros/gate-hooks.md` per §4 and rerun the gate (rc 0: the gate reads that file). Then edit `P/lanes/gate-hooks.json` per §4, setting `status` (integrated) and `retro: passed` in the same edit so the live Stop gate stays silent; `git add` both. Keep the staged `test:hooks` hunk (P2-2). Step 5 runs the gate a third time on the final tree.
4. **CT-02b minimum before commit (optional, recommended):** none; the false positive is a nuisance, not a blocker. If you want it fixed inside this merge, it must be a lane change (abort path).
5. **Gates, all rc 0, record each actual rc:** `./dev/mise tasks validate`; `./dev/mise run check`; `./dev/mise run check:acceptance-baseline` (19/19); `./dev/mise run test:hooks` (13 tests); `./dev/mise x -- hk validate` (2.6.0) and `mise x hk -- hk validate` (2.5.0, the global-hook path, R5 step 5: the run `retros/gate-hooks.md:6,13` must be corrected against); `./dev/mise run retro:gate -- gate-hooks`; `./dev/mise run check:research` (first green run with the wiring; serialized); `git diff --cached --check`; `git diff --check`.
6. **Commit the merge:** `git commit -F <msgfile>`; message names `claude/gate-hooks-wiring` at `e12cf04` (CT-02), the declared parent hunk (`test:hooks` in `check:research`), the settings composition (R5 §B), the record corrections, the rcs, and ends with the attribution trailers of the executing session (not the Opus 5.5 lines in R5's block). No line of the message file may begin with `git merge` or `git push` (the live PreToolUse gate splits on newlines; "merges" in prose is fine). Verify `git log -1 --format=%P` = `9cd396a e12cf04`, `test ! -e .git/MERGE_HEAD`, `git status --short` shows only `?? .agent/`, `?? …/reviews/` and `?? …/retros/ccm-20261013-session.md`. Then run `python3 -I dev/hooks/stop_gate.py <<< '{"cwd":"'$PWD'"}'` (prints nothing).
7. **a06-unit3 gate fix (P1-13)** by copy/rename only: `git mv P/retros/a06-classification-methods.md P/retros/a06-unit3.md` (or a copy with a one-line pointer left behind), so the gate resolves the unit name without a code change; the `retro_record` alias in `retro_gate.py` is a code change and goes to CT-12. Then the other record corrections in §4 that are outside the merge (lane records, retros, ledger rows, docs/agents edits per D15, `skill-invocations.md`), in one docs commit; `.git/info/exclude` += `.agent/` and the backup path (not a commit). Rerun `./dev/mise run retro:gate -- <unit>` for every lane (expect rc 0 ×9, incl. `a06-unit3`) and `./dev/mise run check`. These are record corrections, reviewed by this synthesis and M1; they publish with the merge in step 8.
8. **Publish via A09 (first publish: the merge commit of step 6 and the reviewed record corrections of step 7 only), before any `hooks:install`:** `delivery:inspect-hooks` (digest unchanged `a21be5fe…`); prepare intent with `path=[P/progress.md]` after adding one progress line with the merge SHA and rcs; `delivery:prepare -- <intent> <sha256>` (rc 0, `index_tree`); publish intent with `check_task=["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`; `delivery:publish` (rc 0, `published=<sha>`, `history_scan_rc=0`); `git log origin/codex/marketplace-native-onboarding..HEAD` empty. Record the remote SHA in the ledger and Next Step. This keeps §3(3)'s rule: one publish per integration, nothing unreviewed in it; steps 9–10 are published separately.
9. **pwf migration (CT-15 core, parent edits; after D8, D12):** R4 checklist steps 1–10: pins in settings `env` (`PLAN_ID` project; `PWF_PLAN_ROOT`, `PWF_INJECT=smart`, `PWF_TRUSTED_PYTHON` local), `git mv P/progress.md P/progress-archive-2026-10-13.md` + new `progress.md`, move `task_plan.md:98-566` to `findings.md`, restructure per the skeleton with exactly one `in_progress` phase, write `P/.mode` = `inject-smart`, amend `.claude/rules/planning-records.md` to admit dated archives and per-lane ledgers. Verify: `sh W/scripts/check-complete.sh` → "Task in progress (k/n)"; `PWF_INJECT=smart python3 -I W/scripts/inject-plan.py --context=userprompt` shows Goal/Next Step/Current Phase/phases and ≈1–2 KB; the SessionStart probe (R4 step 5) reads as a fresh session would; from a lane worktree the pretool view shows the root nonce. Adding `env` to `.claude/settings.json` here changes its key set; rerun step 2's assertions with `env` admitted to the project set.
10. **Persist this review and publish again:** first `rm` `reviews/ccm-20261013/settings.json.before-ct02` (step 6 verified the split; it holds the personal MCP allow-list and a personal absolute path) or confirm it is listed in `.git/info/exclude`; it is never staged. Then `git add` the review reports, briefs and `00-evidence-index.md`; `codex-briefs/digests/` stays out of the commit unless D13 = yes (1.7 MB; the digests contain scanner-regex strings such as `Bearer …`/`sk-…` patterns that `delivery:publish`'s history scan may refuse); `P/retros/ccm-20261013-session.md`; `./dev/mise run retro:gate -- ccm-20261013-session` rc 0; commit the pwf migration (step 9) and this persistence as one or two docs commits; second A09 publish as in step 8.
11. **Spec and tickets (after D3):** apply R2's builder fixes; `issue:create-preview/apply/verify` for `CT-SPEC` with `--manifest-file`; rebuild `tickets.v2.json` with the real parent number; create blockers-first (CT-01, CT-03, CT-04, then the unblocked set including CT-02b and CT-17…CT-20 as approved in D3, then CT-02, CT-06, CT-07, CT-16); write the edge-graph file; `issue:new-edge-*` per edge; `issue:new-edges-audit`; `issue:apply` `ready-for-agent` on not-yet-started tickets only; `ledger:sync` by hand; `skill-invocations.md` row. Each `*-apply` is a separately confirmed step.
12. **Operations on your word:** relabel #91 → `ready-for-human`; open the draft PR to `main` (body via `pr`, never merged); run R3 sweep briefs A/B/C and land their outputs in `findings.md` and the ledger; defer `hooks:install` to CT-02b; worktree cleanup (D9) only after publish and the a06 fix.
13. **Handoff:** rewrite `## Next Step` / `## Current Phase`; `session-catchup.py --metadata`; `plan-doctor.sh` PASS/PASS; then `/clear` is safe.

**Wave-0 prevention set (C4 §Minimal wave-0 set; ≈620 LOC, 30 tests, ≈14.5 Opus hours) and where
it lands relative to the merge commit (C4 §Repair-session safety, default per D26):**

| Order | Item | Lands in | Why here |
|---|---|---|---|
| (1) | Runbook steps 1–8 with the existing CT-02 hooks only; no new blocking rule on a tree whose records are known to fail it | — | `stop_gate` `merge_state`/`lane.validate` rules would block every Stop of the repair session until steps 6–7 |
| (2) | W0-1 settings keys: project `.claude/settings.json` gains `autoCompactEnabled: true`, `autoCompactWindow: 700000`, `env.PLAN_ID`; local file gains `PWF_PLAN_ROOT`, `PWF_INJECT=smart`, `PWF_TRUSTED_PYTHON`; step 2's assertion admits `env` in the project key set. W0-2 fixtures extracted by the parent (usage-curve slice, rejected-command shape `T:L565-566`, staged `gate-hooks.json`, staged settings bytes, the 113-command corpus with `expect` labels). W0-7 docs (`claude-team.md` §Integration `--no-ff` never `--no-commit`, §Context budget, §Roles restart rule, §Hooks; D15 rewrites; `.claude/AGENTS.md` key-list pointer; N1 secrets line; `.agent/` and the backup path in `.git/info/exclude`) | step 9/10 commits, second publish | non-blocking; detection and docs |
| (3) | W0-4 doctor slice CT-22a: `dev/doctor/{cli,core,integration,settings,lanes,agents}.py`, surfaces `session-start\|check\|pre-commit`, `--format context`; settings SessionStart entry (timeout 15, no `onFailure`); `dev/check.py` gains one line (`doctor --surface check`, rc 2 ⇒ fail); tasks `doctor`, `doctor:session-start`, `test:doctor` (the last joins `check:research` depends). W0-5 hk `["pre-commit"]` `records` step = `doctor --surface pre-commit` (settings rule only until CT-05 adds `lane:validate --staged`) | own commit after (2), before any wave-1 cut; third publish or folded into the second | read-only detection; `onFailure` continue |
| (4) | W0-3 `dev/context_budget.py`, `dev/hooks/agent_gate.py` (`fork_budget` deny at 500 K; `lane_dispatch` rule 1 denies `general-purpose` for `LANE-UNIT:` prompts), `dev/hooks/prompt_hook.py` (ctx line, slash-in-paste warning); settings entries PreToolUse `Agent` (`onFailure: block`), UserPromptSubmit (continue); `test:hooks-session` into `check:research` depends. W0-6 `P/decisions.jsonl` seeded + `dev/plan_decide.py` minimal | same commit as (3) or next | deny/advice with low blast radius |
| (5) | Stop-gate extensions (`merge_state`, `lane.validate` first three failures, one combined reason) and `lane:validate --staged` in the pre-commit step | CT-17 (wave 2) and CT-05, only after every record validates | blocking rules last |

Hook set enabled in wave 0 (from C4's inventory only): SessionStart doctor (15 s, continue);
UserPromptSubmit `prompt_hook` (10 s, continue); PreToolUse `Bash` `pretooluse_gate` (existing,
block); PreToolUse `Agent` `agent_gate` (10 s, block); SubagentStop `subagent_stop_gate` (existing;
`onFailure` inert there); Stop `stop_gate` (existing). Not enabled: PreToolUse `Write|Edit` record
guard, PostToolUse `Skill` journal, a UserPromptSubmit doctor digest, hk `pre-push` doctor step,
Stop `pending_operations` (all dropped or deferred by C4). Latency budget per event (max of
parallel hooks): SessionStart ≈ 3 s (7.6 s only in the pwf shell-fallback failure mode),
UserPromptSubmit ≈ 0.1 s, PreToolUse(Bash) ≈ 0.05 s normal / ≈ 0.7 s during a merge / 6 s hard
budget after CT-02b, PreToolUse(Agent) ≈ 0.06 s, SubagentStop ≈ 0.4 s, Stop ≈ 0.5 s (D22).

CT-21 in the second publish: the index files `P/imports/codex-worktrees-20261013/{README,
MANIFEST.json, T1-snapshot-report.md, T1 scan, verify.py, T2-import-plan.json}` and
`P/lanes/ct21-codex-imports.json` are committed; the `2a14/` and `c658/` payload (454 files,
11.8 MB, raw session streams and full issue bodies) stays untracked via `.git/info/exclude`
(D24); the 119 import files enter only through the CT-21 lane (`git add -f` for the 61 `*.log`
rows the host's global excludes hide; no `.gitignore` edit; CT-08 is **not** a prerequisite).

Verification commands: every task named in steps 5, 8 and 11 exists in `./dev/mise tasks ls`
(56 tasks; C4 and M1 checked `check`, `check:research`, `check:acceptance-baseline`,
`test:hooks`, `retro:gate`, `delivery:inspect-hooks|prepare|publish`, `deps:check`,
`test:delivery`, `issue:create-preview|apply|verify`, `issue:new-edge-preview`,
`issue:new-edges-audit`, `issue:preview|apply|verify`, `tasks validate`). New tasks the wave-0
items add (`doctor`, `doctor:session-start`, `test:doctor`, `test:hooks-session`, `check:records`,
`plan:decide`) do not exist until their commit lands; a step that names one before that is a
sequencing error.

Abort path (Runbook 2, if D1 = abort): `git merge --abort` (restores `9cd396a`, deletes the nine merge-added files, loses the staged `test:hooks` line, keeps `settings.local.json`, `.agent/`, this directory; removes the live project hooks until the re-merge); fix settings composition and retro lines on the lane branch in `.claude/worktrees/gate-hooks`, re-review, fix `lanes/gate-hooks.json` in a parent docs commit, `git merge --no-ff claude/gate-hooks-wiring` (no `--no-commit`) after a by-hand `retro:gate`; commit the wiring separately; continue at step 5.

## 6. Re-plan

**Unified ticket list** (C4's reconciled table is binding; CT-01…CT-21 keep the earlier meanings,
CT-22 = doctor core, CT-23 = session hooks follow-up, CT-24 = decisions ledger; C2's CT-25…CT-30
and C3's CT-23 are absorbed; final range **CT-01…CT-24 plus CT-02b**):

| Ticket | Title (reconciled) | Blocked by | Wave | Notes |
|---|---|---|---|---|
| CT-01 | Retro gate task | — | done | AC2 open → CT-12 |
| CT-02 | Hook wiring for the retro gate | CT-01 | runbook 1 | mid-merge |
| CT-02b | Gate follow-up: token-anchored verbs, heredoc strip, `--no-commit` deny, `--dry-run`/`--time`, deadline deny-with-reason, corpus test, `hooks_install.py` guard (publish-first), `test_two_stop_hooks_compose` | CT-02 | 1 #1 | parent hunk: `hooks:install` row |
| CT-03 | Team roles, rules, vocabulary | — | done | |
| CT-04 | Guidance hierarchy | — | done | |
| CT-05 | Lane-record validator (`lane:set`/`lane:validate --staged --from-journal`, `retro` derived, `resource_admissions.network`, `import_source.data`, `published ⇒ on origin`, `holds`, T-B8) + ticket ledger generator | — | 1 #3 | imports `dev/doctor/lanes.py` predicates |
| CT-06 | `/lane-retro <unit>` | CT-01, CT-03, CT-19 | 3 | |
| CT-07 | Codex compatibility (roles/config; mirror test) | CT-02, CT-03 | 3 | ticket 30 of the dynamic-agents graph targets `.codex/` too: coordinate |
| CT-08 | Baseline transition v2 (`.gitignore`; `.agent/` decision) | user admission (D6) | 4 | the only ticket touching a frozen file; not a prerequisite of CT-21 |
| CT-09 | Tool adoption decision table | — | 3 | doc-writer |
| CT-10 | codex-session-history coverage + eval loop + mask + `codex_status.py` (`codex:status --write`, `codex:supersede`, `terminal` field) + `codex_activation.py` manifest-line test + brief composer | — | 4 (supersession operation = sweep B, before 2026-10-19) | |
| CT-11 | Serialize named checks (lock) + `JOURNAL/checks/` receipt line | — | 1 #2 | the wave-0 one-line doctor call in `check.py` precedes the cut |
| CT-12 | Wire every development test (`test:retro-gate`; `unwired_tests` rule via `dev/doctor/gates.py`; exemptions data; AGENTS line-cap/pointer checks) | CT-22a | 1 #6 if admitted, else 2 | no `check.py` edit; no `retro_gate.py` alias (dropped) |
| CT-13 | Grilling-question mod (AskUserQuestion) | D14 | user-typed | live prevention for P1-8 |
| CT-14 | `plugins/aggregated-research` guidance + `CLAUDE.md` importer | — | 3/4 | |
| CT-15 | Planning-file shape, `plan:log`, `plan:handoff --write/--check` (lists outstanding stage steps), `check:planning` runner (calls `doctor --class K,I,D,E,N,L`) | — | 1 #4 | one-time migration = runbook step 9 |
| CT-16 | Settings composition check (`dev/doctor/settings.py` rule; `settings_check.py` alias; T-I1/I2/I4) | D4; sequential after CT-22a | 1 (sixth lane) or 2 | file-disjoint from CT-22b |
| CT-17 | Lane lifecycle: `lane:allocate` (base = allocation commit, `--admit`, `--ticket` approval refusal), `lane:integrate` (journal, snapshot via doctor, `--continue/--abort`, foreign-hunk refusal, `--parent-hunk`), `session:status`, `stop_gate` extensions | CT-01, CT-02, CT-05, CT-11, CT-22a, CT-24 | 2 #1 | split `allocate|status` from `integrate` past 300 lines |
| CT-18 | A09 batch publish wrapper (refuses `MERGE_HEAD`; `doctor --surface publish` first) | CT-02, CT-22a | 2 #3 | |
| CT-19 | Slotted briefs (`lane:brief` ≤ 1.5 KB, reviewer slots), agent constants, `reviewer.md:18`, `retro-writer.md` step 0, SubagentStop receipt journal, brief-size rule in `agent_gate` | CT-02, CT-03, CT-05 | 2 #2 | parent hunk: SubagentStop matcher entry |
| CT-20 | `agent-session-history` skill + `/session-review` + transcript detectors; `doctor --surface sweep` | CT-07, CT-10, CT-22 | 4 | absorbs C3's sweep ticket |
| CT-21 | Import Codex worktree inputs (119 files), `check_inputs.py` + `dev/cited-inputs.json` + `check:inputs`, exit-3 on missing inputs, `checkout_transfer.py` path fix, `development.yml` step; absorbs the pinned-data resolvers | — | 1 #5 (fifth lane, D24) else 2 first | unblocks #69 and the #63–#68/#71–#74 closure rows and D9 cleanup |
| CT-22 | Doctor core (`dev/doctor/**`, 11 modules, six surfaces, `--format context`, `--fix` proven-by-git only, `--snapshot`); CT-22a = wave-0 slice | — | 0 (a) + 1 heavy slot / 2 (b) | parent hunks: settings SessionStart entry, `check.py` line, `check:research` += `test:doctor`, `hk.pkl` `records` step |
| CT-23 | Session hooks follow-up: thresholds via `env`, `ctx:status`, phase/next extraction in `prompt_hook`, `agent_gate` roster-drift context, docs §Context budget | CT-19 (sequential on `agent_gate.py`), CT-22 | 3 | wave-0 seeds exist |
| CT-24 | Decisions ledger: `plan_decide.py` (`approval|operation|receipt`), `P/decisions.jsonl` format, `plan:decide`, `issue-tracker.md` paragraph; `lane:allocate` imports `approved()` | — | 1 (small) | wave-0 seed |

Operations, not tickets: #91 relabel; draft PR to `main`; T4/Phase C closures under #93/#101
one at a time with a new budget and your approval (D25); sweeps A/B/C are done (this revision);
the supersession notice and the dead-children sentence land in step 7; worktree cleanup after
CT-21 publishes; `hooks:install` after CT-02b. C3 #95 offline diagnostic is wave 2 #4; C2 #98,
the heavy L-chain and #21→#20→#17→#16 follow D5.

**Waves** (R8 + C4 + T2): wave 0 = Runbook steps 1–13 plus the prevention set W0-1…W0-7 in the
order of the safety table (D26). Wave 1: CT-02b, CT-11, CT-05, CT-15, **CT-21 as the fifth lane**
(integration order 1–5; CT-12, CT-16, CT-24 as small sixth/seventh lanes only if D5 admits them,
else wave 2). Wave 2: CT-17, CT-19, CT-18, C3 #95, CT-22b in the heavy slot (+ heavy chain per
D5). Wave 3: CT-07, CT-23, CT-06, CT-09 (CT-12 here if not in wave 1). Wave 4+: CT-10, CT-20,
CT-08, C2, the CT-05 and CT-21 split units, the final `<spec>-review-fixes` lane. Two declared
sequential pairs inside one tree: CT-22a → CT-16 (`dev/doctor/`, file-disjoint) and CT-19 → CT-23
(`dev/hooks/agent_gate.py`). Per lane: parent commits `lanes/<unit>.json` first (`base_sha` =
allocation commit, `allocated_from` = its parent), cuts `.claude/worktrees/<unit>` on
`claude/<unit>-<slug>`, dispatches the `implementer`/`doc-writer` agent (not `general-purpose`, and never with `isolation: worktree`, which branches from the default branch rather than the integration tip and is the trigger for the stale-plan injection R4 probed)
with a ≤40-line brief carrying pointers, the allowlist, the pwf pin, gates and trailers; the
lane calls `tdd`, merges the tip before reporting, appends to `P/ledger-<unit>.jsonl`; cold
`reviewer` (fixed point = `base_sha`, `CODING_STANDARDS.md` input); `retro-writer` loop until
`retro:gate` rc 0; one merger at a time; A09 publish per integration; `code-review` (Skill) once
per spec at the end with the recorded `start_sha`, findings to one fix lane; worktrees removed
after publish and close.

**pwf changes** (R4): see Runbook step 8 and CT-15.

**Workflow from here, what you type, in order** (D2 §4, R1 §Next):
1. Approve the runbook decisions (D1, D2, D4, D11, D12); the parent executes Runbook steps 1–10.
2. Fresh session: `/mattpocock-skills:setup-matt-pocock-skills`; accept GitHub, labels, single-context; have it rewrite `docs/agents/issue-tracker.md` from the seed and keep the "Qualified tracker operations" mapping under the seed's "When a skill says publish / fetch" heading; create the `wayfinder:*` labels. `/clear`.
3. Fresh session, plan mode off: `/mattpocock-skills:retro /Users/rmanaloto/.claude/projects/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/464a2816-4b5d-4665-b39a-8303cb014efb.jsonl` (this directory's reports are its input); pick candidates; the parent applies them through one gated `retro-writer` lane. `/clear`.
4. Fresh session (Window A): say "publish spec from `proposals/claude-takeover-spec/spec.md`" (parent runs `issue:create-*`, records `#<spec>`, no `ready-for-agent` yet); then `/mattpocock-skills:to-tickets #<spec>`; approve R2's 16-item breakdown (granularity, edges, merge/split); say "publish tickets".
5. `/clear`, then `/mattpocock-skills:implement-spec #<spec>`; the parent runs the waves.
6. Before clearing each build session: `/mattpocock-skills:retro`.
7. Host-heavy tickets (#16, #17, #20, #21, L1): `/clear`, `/mattpocock-skills:implement #<n>`, confirm each heavy run.
8. After step 2: `/mattpocock-skills:wayfinder "C++26 P2996 research core"` in its own session.
9. On 2026-10-19 if Codex resumes: `/mattpocock-skills:handoff "Codex resumes the CT graph under the lane gate"`.

## 7. Automation backlog (R7 merged with C4's KEEP / MERGE / DEFER / DROP)

| Rank | Proposal | C4 verdict | Prevents | Ticket |
|---|---|---|---|---|
| 1 | `lane:integrate <unit> [--continue\|--abort]` + journal + snapshot + foreign-hunk refusal | KEEP (wave 2); `merge-tree` composition DEFER | half-done merges, stale fields, out-of-allowlist paths | CT-17 |
| 2 | `lane:set` / `lane:validate` (`retro` from a gate run only; `--staged`, `--from-journal`) | KEEP (wave 1); `dev/doctor/lanes.py` predicates shared, predicate fixed | stale/false lane fields | CT-05 |
| 3 | `plan:log` / `plan:handoff --write/--check` | KEEP (wave 1) | buried NEXT, stale base/status, unlisted stage steps | CT-15 |
| 4 | `lane:brief` + slotted agents + SubagentStop receipt journal | KEEP (wave 2); size cap in `agent_gate` MERGED into CT-19; `tdd_first` SubagentStop block DEFER (detector kept) | brief drift, lost receipts, `general-purpose` dispatch | CT-19 |
| 5 | `lane:allocate` (base = allocation commit; `--admit`; `--ticket` approval refusal) | KEEP (wave 2) | off-by-one `base_sha`, cut before record, missing prep, build on unapproved tickets | CT-17 |
| 6 | `ledger:sync` | KEEP | silent no-op row replaces | CT-05 |
| 7 | `delivery:publish-batch` (`doctor --surface publish` first; refuses `MERGE_HEAD`) | KEEP (wave 2) | empty-path refusal, stale hook digest | CT-18 |
| 8 | CT-11 lock (+ `JOURNAL/checks/` receipt line; retro `receipt:` rule DEFER) | KEEP (wave 1) | raced check results | CT-11 |
| 9 | `session:status` = `doctor --class C --json`; SessionStart block | KEEP (wave 0 slice) | unnoticed half-done merge, lanes not re-merged | CT-22a, CT-17 |
| 10 | `/lane-retro` | KEEP (wave 3) | ownerless findings | CT-06 |
| 11 | PreToolUse gate fixes (token-anchored, heredoc, deadline deny) + `hooks_install.py` guard + corpus fixture (one file) | KEEP (wave 1 #1) | false-positive blocks, publish refused after install | CT-02b |
| 12 | unwired-test check (`dev/doctor/gates.py`) + `test:retro-gate` | KEEP; one implementation (MERGE of C2/C3 twins) | forgotten wiring | CT-12, CT-22 |
| 13 | `agent-session-history` + `/session-review` + transcript detectors | KEEP (wave 4); C3's sweep ticket MERGED in; daily schedule DEFER | next session sweep cost | CT-20 |
| 14 | Codex brief composer + `codex_status.py`/`codex:supersede` | KEEP (wave 4); C2 CT-29 MERGED in | next takeover cost; packet supersession | CT-10 |
| 15 | Doctor core: one static-rule tree (`dev/doctor/`), `--fix` for proven-by-git facts | KEEP; C2's `dev/checks/` + `dev/planning_checks/` MERGED in (12 modules → 11 doctor modules) | every class's detection | CT-22 |
| 16 | Context budget: `context_budget.py`, `agent_gate.fork_budget`, `prompt_hook` ctx line, project `autoCompactEnabled`/`autoCompactWindow` | KEEP (wave 0) | the death at 977 K; forks born full | W0-1/W0-3, CT-23 |
| 17 | Decisions ledger `plan_decide.py` + `P/decisions.jsonl` | KEEP (wave 0 seed, wave 1 CLI); per-prompt request capture DEFER | approval assumed, operations unreceipted | CT-24 |
| 18 | `check_inputs.py` + `dev/cited-inputs.json` (pinned-data resolver) | KEEP; C2 `pinned_paths` and C3 resolver MERGED in; doctor `--fix` copiers DROP | tip code reading untracked data | CT-21 |
| — | PreToolUse `Write\|Edit` record guard; PostToolUse `Skill` journal; UserPromptSubmit doctor digest; hk `pre-push` doctor step; Stop `pending_operations`; `--fix` settings split; `hookcorpus` as a `check` detector; `retro_record` alias | DROP (C4) | no occurred finding needs them, or duplicates | — |
| — | `merge-tree` integration engine; `tdd_first` block; named-check `receipt:` rule; `CT-nn/k` ids; `plan_requests` capture; pwf injector probe at SessionStart; worktree-nonce probe at `check`; daily sweep; seed-hash pin; `mise/tasks/` includes (conditional on D7) | DEFER (C4) | — | — |

Guardrails (R7, C4): `publish-batch` only for the integration branch; no batch close, every
`issue:*-apply` separately confirmed; nothing automates merge to `main`, `hooks:install`, a
settings migration or daemon registration; the five-stage verbs stay user-typed; every new
merging/pushing wrapper calls `git_gate.check_lanes()` and is added to the PreToolUse verb table;
lane agents are never dispatched with `isolation: worktree`; hk `pre-commit` fires in every
worktree through `mise x hk` and is bypassable by `HK=0`/`--no-verify` (a guard, not a gate;
`pre-push` never guards A09, which pushes `--no-verify`); a timed-out PreToolUse hook does not
block unless `onFailure: block`, so the in-budget deny-with-reason is the real gate.

## 8. Open decisions for you (recommended default in bold)

1. **D1 Mid-merge:** **finish it (Runbook 1, declared evil merge)** vs abort and redo (costs a re-review; a short window with no project hooks).
2. **D2 `hooks:install`:** **defer to CT-02b** (A09 would refuse after install) vs install now and accept a blocked publish until reconciled.
3. **D3 Tickets:** **approve R2's 16-item breakdown plus CT-17…CT-20** (or trim), publish CT-01…CT-04 as done sub-issues with state lines, CT-02 in progress; then type `/to-tickets` to make the stage real, or record file-guided.
4. **D4 Settings composition:** **R5 §B** (project: `$schema`, hooks, four workflow plugins + their marketplaces; local: MCP permissions, codex/eli5/html-plan/next-steps, `skillOverrides`, the display keys and the undocumented top-level `additionalDirectories`, kept verbatim) vs minimal project file (`$schema` + hooks only). Secrets posture folded in from N1: secrets stay in `~/.config/fnox/config.toml`, never in any settings file or mise `[env]`; the exec-scoped `fnox --config ~/.config/fnox/config.toml --profile <name> --no-defaults --no-daemon --non-interactive exec --` route is the project rule; record fnox ≥ 1.39.0 as the project requirement in `docs/agents/`; re-enabling `_.fnox-env` in mise (now buildable on `fnox env --json`) is a separate, tested ticket under macos-development-environment #75, not part of this repair.
5. **D5 Heavy chain:** **keep `#21 → #20 → #17 → #16 → L1`, heavy slot in wave 2 = #21** vs start L1 now; each run confirmed. Also: four Opus implementers plus reviewers and retro-writers per wave is a token burst; **cap wave 1 at three lanes** if you prefer (R8 risk 5).
6. **D6 CT-08 scope:** **`.gitignore` + `baseline-files.v2.json` + `dev/check.py` only, wave 4, alone on frozen files** vs also the CI acceptance files (needs the fresh-session admission).
7. **D7 `mise/tasks/<unit>.toml` includes:** **adopt if `task_config.includes` validates under `./dev/mise`**; fallback: lanes propose rows, parent appends at integration.
8. **D8 Lane records parent-only + per-lane ledger `P/ledger-<unit>.jsonl`:** **yes** (amend `planning-records.md`) vs keep "lane edits `status`".
9. **D9 Worktree cleanup:** **remove the eight integrated worktrees after publish and the a06 fix** vs keep for audit.
10. **D10 Spec `start_sha` for the end-of-spec `code-review`:** **`361688e`** (tip the first CT lane was cut from; R8) vs `e0667ec` (M0 tip; R2). Record in `spec.manifest.json`.
11. **D11 Codex sweeps A/B/C:** **run them (≈200 KB in)** vs accept the residual risk on `2a14` evidence and T4 state.
12. **D12 `progress.md`:** **archive to `progress-archive-2026-10-13.md`** vs keep appending (1 MiB cliff in ~40 days at today's rate).
13. **D13 Commit the Codex digests (1.7 MB) under `reviews/`:** **no; commit briefs and reports, keep digests in the scratchpad and point at them** vs commit everything.
14. **D14 AskUserQuestion:** **build CT-13 as a mod** vs a one-line `CLAUDE.md` rule vs explicit "no".
15. **D15 Invocation wording:** **rewrite `claude-takeover.md:11` and `ticket-retro.md:4-8` as in §4**; keep `skill-invocations.md` as the binding record.
16. **D16 `/retro` cadence:** **per build session** vs per ticket (per ticket is already the retro-writer).
17. **D17 Per-lane cold review + per-spec `code-review`:** **keep both** vs drop the spec pass for doc-only specs.
18. **D18 Heavy tickets via `/implement`:** **in a lane worktree with a lane record** vs on the integration branch under per-run confirmation.
19. **D19 T4 Phase C:** a new attempt needs a new budget and your explicit approval; **decide after sweep B**.
20. **D20 Draft PR to `main` and the #91 relabel:** **both on your word after CT-02 publishes.**
21. **D21 Auto-compaction:** **the project `.claude/settings.json` sets `autoCompactEnabled: true` and `autoCompactWindow: 700000`** (higher-level file overrides the user's `false`; a shell `DISABLE_AUTO_COMPACT` would still win) vs leaving it off and relying on hooks alone. User action in any case: flip `autoCompactEnabled` in `~/.claude/settings.json` and in `~/.claude.json` (whether the CLI-written copy participates is unverified; flipping both is safe).
22. **D22 Hook latency budget and the wave-0 hook set:** **enable only C4's inventory** (SessionStart doctor 15 s continue; UserPromptSubmit `prompt_hook` 10 s continue; PreToolUse `Bash` gate block; PreToolUse `Agent` `agent_gate` block; existing SubagentStop and Stop) with the per-event maxima in §5 (SessionStart ≈ 3 s, prompt ≈ 0.1 s, Bash ≈ 0.05 s / 6 s hard budget, Agent ≈ 0.06 s, SubagentStop ≈ 0.4 s, Stop ≈ 0.5 s) vs the fuller C2+C3 set (record guard, Skill journal, prompt digest, pre-push step: dropped for latency without an occurred finding).
23. **D23 Ticket table:** **accept C4's reconciled CT-01…CT-24 (+CT-02b)** as the breakdown to approve at `/to-tickets` (R2's 16 items plus CT-17…CT-24, nine C2/C3 tickets absorbed into three) vs trimming further.
24. **D24 CT-21 import policy:** **index files committed (`README`, `MANIFEST.json`, T1 report and scan, `verify.py`, `T2-import-plan.json`, the lane record); the 119-file payload imported only by the CT-21 lane (`git add -f` for the 61 host-ignored `*.log` rows, no `.gitignore` edit); keep-private sets (149 files, 6.6 MB: raw session streams, full issue bodies, the redacted gitleaks report) stay in the 0700 mirror and are declared in `dev/cited-inputs.json`; CT-21 runs as the fifth wave-1 lane** vs importing the 18 iwyu build-tree files too, or waiting for CT-08.
25. **D25 T4 fourth attempt:** attempt 3 ended `STOPPED/NOT_COMPLETED` with both budgets exhausted and `phase-c-policy-v2.md` grants no fourth attempt; **no attempt without your explicit approval and a new budget, a fresh issue-write interval, a repeated children-state preflight and rebuilt parent packets**; decide after the CT-21 import and the ledger rows land.
26. **D26 Wave-0 prevention timing:** **C4's order: runbook steps 1–8 first with the existing hooks only; then settings keys, fixtures and docs (second publish); then the doctor slice and the pre-commit settings rule; then `agent_gate` + `prompt_hook`; blocking Stop-gate extensions only after CT-05 proves every record validates** vs landing the full set before the merge commit (would block the repair session's own Stops).

## 9. Could not verify (union)

Resolved since the reports: `retro:gate -- gate-hooks` rc 0 on the staged index (R5 and M1 ran it); the cause of the 01a130ef/01a13185 stops (M1: `thread_history` shows every child `error_json` as the usage-limit message, the three trees' last turns `failed`); the gate-hooks re-review PASS text (R6 and M1 read `T:L1984`).

- `hooks:install` effects on A09 (inferred from `hk install --help` and `git_delivery.py:49-71`; not run); whether A09 accepts a merge commit as `head`; `git worktree remove` on ignored-only trees.
- Per-finding re-execution of "Applied … verified by …" rows in the nine retro records; `retro:gate` rc 0 for all eight passed lanes on the integrated tree (not re-run during the merge).
- Red-before-green for a06-unit3 and rf-env-scrub (code edited through the shell; a06-unit3's one Write is its retro, rf-env-scrub's one Edit is a doc).
- The cause of the PreToolUse 10 s timeout R7 observed (gate runs take 0.2 s in dry runs; not reproduced by M1), and why the parent chose `general-purpose` for every lane after 20:25Z.
- `check`, `check:acceptance-baseline`, `test:hooks` and `check:research` on the merged tree (none run during the review; only `retro:gate -- gate-hooks` and the hook scripts were dry-run).
- Whether round-2 Q6 counts as seam approval in the `to-spec` SKILL.md:17 sense (graded PASS on its wording "to-spec check").
- Whether the CT-03/CT-04 lane commits are byte-identical on origin `28fedf1` (ancestry verified locally only).
- The spec's Further Notes sentence "the same mode Codex recorded" (kept by §4) is asserted, not cited.
- The exact `delivery:prepare`/`delivery:publish` command lines the dead session used (receipts in its scratchpad).
- Whether `deps:sync`/`tools:prepare` reached the network under `network: none`.
- Which plan copy each lane subagent's hooks read (nonces match both readings; failure mode proven by probe); the mechanism behind repeated identical PreToolUse views (`prompt_id` hypothesis); whether settings `env` reaches hook processes.
- Settings-reference details for `enabledPlugins`/`extraKnownMarketplaces` (docs pages truncated); object-merge of `enabledPlugins` across scopes inferred from observed coexistence.
- The content of the 148 Codex child rollouts that completed normally; the cause of the A09 outbound-scan rc 2 at ~10:39Z on 10-13 (sweep A); whether `retros/issue-28|29.md` in the Codex worktrees were deliberately superseded; the dotfiles `codex-sdlc-team/SKILL.md` claim.
- The exact binding file `issue:create-verify` writes; whether a durable journal under `.planning/` passes the delivery secret scan.
- Line-level v1.3.1 tag vs the `49dd158` cache (grading used the cache, which is what the session read).
- Whether `~/.claude.json`'s `autoCompactEnabled: false` participates in the effective value (the reference marks the key "Any file"; no page says the CLI-written copy is ignored); the `agent_type` a fork's hooks receive; `hk run pre-commit` offline behaviour without the pkl package cache and whether hk 2.6.0 accepts the staged `hk.pkl` (`min_hk_version 2.5.0`) under `mise x hk`; whether `task_config.includes` validates under `./dev/mise` (D7); the doctor `session-start` latency (≈0.6–1.2 s estimated from 4–6 git calls at ≈170 ms on this 27-worktree checkout); whether `hk install --force-local` on Git 2.54 writes `--local` entries exactly as `hook.hk-<name>.{event,command}` (not run) — all C4.
- Compaction at ~977 K with `autoCompactEnabled: true` was not tested; the `usage`-curve figures come from the transcript's assistant `usage` sums (C1, C4 claim 10).
- Sweep A: directory hashes were not recomputed by T2; A09 git-mode gitleaks over the eventual import commit (no commit exists; dir mode is 0 findings); whether the user wants the 18 iwyu build-tree files tracked; whether hunk 2 of the `accepted-decisions.md` diff is the user's wording; `codex --version` on the implementer host.
- Sweep B: `docs/remaining-work/README.md` and `tracker.json` were never produced; the children's live closed state on GitHub; the `#63` `dev/github_search_one_page.py` binding (no hash recorded); whether a release of the T4 issue-write interval was ever sent after attempt 3; who the 900 s approval wait was for.
- Sweep C: encrypted `send_message`/`checkpoint` payloads (each dead child's final report to `/root` is unreadable); python-script writes attributed by the paths the scripts name; `01a134c2`'s private-clone commits not inspected.
- Your intent on the AskUserQuestion mod after round-2 Q9 ("yes to all" could be read as accepting the substitution); treated as open, not refused.

## 10. Revision log (after M1 meta-review and N1)

M1 verdict: SAFE WITH CORRECTIONS; 13 of 13 P1s confirmed, three P2 overstatements, nineteen
required corrections. Applied in this revision: 1 (step 2 verification: `skillOverrides` admitted,
backup ⊆ union, the three added marketplaces named; P1-2 wording), 2 (step 10: the backup is never
staged, digests out unless D13, history-scan note), 3 (publish moved to step 8 directly after the
merge and the reviewed record corrections; migration and review persistence follow with a second
publish), 4 (step 3 gate order), 5 (hk 2.5.0 run added), 6 (step 6 expected status, message-file
rule, trailers), 7 (step 7 copy/rename; alias routed to CT-12), 8 (preamble decisions D8, D9,
D13, D15, D20), 9 (step 11 create order), 10 (P2-3 timeout cause as hypothesis; §9), 11 (P2-10
eight plus one), 12 (P2-12 scope), 13 (P1-6 times), 14 (P1-12 note; §9 wording), 15 (new row
P2-10b for R1 P2-4), 16 (new row P2-25 and §4/§6/§8 additions: `additionalDirectories`, research
branches, ticket 30, #13 attachments, `feature/foo`, no `isolation: worktree`, wave-1 cap), 17 (§9
additions and resolved items), 18 (PreToolUse placement and trailer decision recorded), 19 (retro
record lines 5, 17 and 34). N1 folded into P1-2, §4 and D4 (secrets stay in fnox; exec-scoped
profile route; fnox ≥ 1.39.0; `_.fnox-env` re-enable is a separate ticket).

Disputed: none. One note on correction 3: the migration (step 9) is still placed before the
review persistence (step 10) because the persistence commit references the restructured plan;
both land in the second publish, after D8 and D12.

**Revision 2 (prevention team C1–C4, CT-21 import lane T1/T2, Codex sweeps A/B/C).** Added P1-14
(auto-compaction off; death at 977 K; forks inherit the window) and P1-15 (agent definitions
created mid-session are not selectable until restart) and P2-26 (inert `onFailure: block` on
Stop/SubagentStop; `GATE_TIMEOUT` arithmetic); §2b with the 14 root-cause classes, invariants,
wave-0 artifacts, surviving detector ids and tickets, the five C4 gaps and the three struck
claims; §3(5) now points at the doctor (CT-22), the session hooks (CT-23), the session review
(CT-20) and the SessionStart block; §4 gained sweep B's closure-prerequisite rows (#62–#78,
#101), the supersession notice, sweep C's mid-turn sentence, the `accepted-decisions.md` +52-line
block, `dev/checkout_transfer.py:17`, T2's `findings.md` replacement and the four path rewrites;
§5 gained the wave-0 prevention set with C4's safety order, the settings keys, the hook set and
latency budget, the CT-21 index-vs-payload rule for the second publish, and the task-existence
check; §6 carries C4's reconciled CT-01…CT-24 (+CT-02b) table with CT-21 as the fifth wave-1 lane;
§7 is merged with C4's KEEP/MERGE/DEFER/DROP; §8 adds D21–D26; §9 the union of the new reports'
unverified items. The D2 user-typed command script is unchanged (C4 did not alter it).
Disputed: none; one note: C4 moves the `retro_record` alias out of CT-12 (dropped; runbook step 7's
rename suffices), which this synthesis adopts.

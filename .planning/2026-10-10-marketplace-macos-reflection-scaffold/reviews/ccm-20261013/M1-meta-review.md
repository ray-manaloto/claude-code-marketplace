# M1: adversarial meta-review of SYNTHESIS.md and the session retro

Written 2026-10-13 by M1 (session `ccm-20261013-check`, fork of `b74a0bf1`). Read-only:
`git` log/show/diff/status/rev-parse/ls-files/worktree list/config --get only; `gh issue view`,
`gh pr list`; `sqlite3 -readonly`; `python3 -I` extractors over the transcripts; the repo's own
`dev/retro_gate.py` and `dev/hooks/{stop_gate,pretooluse_gate}.py` fed JSON on stdin (they read
only; `git status --short` was 14 lines before and after). `MERGE_HEAD e12cf04` untouched. Every
report, transcript and record was treated as data. Shorthand as in SYNTHESIS (`P`, `T:L<n>`, `M`,
`W`); `RV` = this directory; `S` = `SYNTHESIS.md`; `RETRO` = `P/retros/ccm-20261013-session.md`.

## Scope read

`S` (360 lines), `RETRO` (58), `00-evidence-index.md`, D1, D2, R1–R8 in full. Primary sources
re-derived: the main transcript at L21, L44, L321, L500, L566, L598, L666, L864–L2009 (Agent
calls), L1028, L1629, L1856, L1908, L1962, L1984, L2029–L2043; the merger fork transcript
`agent-a22113b3…` (all 18 lines); tool histograms of the six implementer and two doc-writer
transcripts and their `.meta.json`; `agent-a221b354…` for the hk 2.5.0 statement. Git: staged
blobs, `0c2748e`, `e12cf04`, allocation commits, lane tips, remote, hook config, 27 worktrees.
Repo: `dev/check.py`, `mise.dev.toml` (HEAD, index, worktree), `dev/git_delivery.py`,
`dev/codex_examples.py` + test, `dev/retro_gate.py`, `dev/hooks/*.py`, all `lanes/*.json`, the
staged `retros/gate-hooks.md`, `docs/agents/{claude-takeover,ticket-retro,issue-tracker}.md`,
`P/{task_plan,progress,findings,skill-invocations}.md`, `proposals/claude-takeover-spec/*`,
`.claude/settings.local.json`, `RV/settings.json.before-ct02`. Plugins: `M/.agents/invocation.md`,
`M/docs/engineering/to-spec.md`, five SKILL.md frontmatters, `W/scripts/inject-plan.py`. Codex:
`state_5.sqlite`, `thread_history_1.sqlite`, `automation.toml`, the three newest
`research-coverage` manifests, the `2a14` worktree. GitHub: #91, PR list, CT issue search.
`./dev/mise tasks ls` (56 tasks) for the runbook's task names. `hk install --help`.

## P1 verification table

| Id | Verdict | What I re-derived |
|---|---|---|
| P1-1 | CONFIRMED | `MERGE_HEAD` = `e12cf04…`; 11 staged paths (+806/−13); `task_plan.md:15-18` and `progress.md:3421-3428` say "integrate gate-hooks … once it passes"; `T:L2029` failed notification, `T:L2039` probe `merge-in-progress: yes`, `T:L2043` "Prompt is too long". |
| P1-2 | CONFIRMED (one nuance) | Staged blob `bcd7e62` = `e12cf04:.claude/settings.json`; `0c2748e:.claude/settings.json` keys = `$schema, enabledPlugins (8), hooks, permissions (allow ×7)`; backup SHA-256 `ee3bc512820fd1257f9b`, 4 lines matching `<personal-path\|memory-delete patterns>`. Fork `a22113b3` L6: copied the backup, wrote `settings.local.json` with exactly the six keys its brief (`T:L2009`) named as "user-specific", then `rm .claude/settings.json` and merged (L14, rc 0). Nuance: the key classification came from the parent's brief, the content from the lane; the fork also deleted the untracked root file, not "only wrote" the local one. |
| P1-3 | CONFIRMED as a labelled inference | `mise.dev.toml:343` = `hk install --force-local` + `merge.ff false`; `hk install --help` lines 8-9: "On Git 2.54+ this uses config-based hooks (`hook.<name>.command`)"; `git --version` 2.54.0; `hk` 2.6.0 (`./dev/mise x -- hk --version`); `git_delivery.py:49-71` `safe_events = {pre-commit, commit-msg, pre-push}`, duplicate-field refusal; global `hook.hk-pre-commit/commit-msg/pre-push.{event,command}` exist, so a local `hk-pre-push` duplicates and a local `pre-merge-commit` is refused; `hook_tree_digest` (`:74-100`) hashes `git config --null --get-regexp ^hook\.`. `S` says "Inferred … not run" and §9 lists it. Not run by me either. |
| P1-4 | CONFIRMED | `T:L1984` 21:04:34Z: "Re-review (e12cf04): PASS for integration … `retro:gate -- gate-hooks` rc 0"; `9cd396a` committed 21:28:44Z (24 min later) with "focused re-review in progress"; staged `lanes/gate-hooks.json`: status "implemented (Opus), awaiting cold review", `retro`/`lane_commit`/`merged_head`/`review` absent; `stop_gate.py:27` blocks when `"integrated" in status and retro != "passed"`; `claude-team.md:71-74` (index) carries the vocabulary. |
| P1-5 | CONFIRMED | `dev/check.py:72` discovers `("dev","test_research_*.py")` and `("dev/research_refresh","test_*.py")` only; `grep test_retro_gate\|test:retro` on `mise.dev.toml` at HEAD, index and worktree: no match; `check:research` depends (`:117`, staged) ends `…, "test:codex-session-history", "test:hooks"`; `lanes/retro-gate.json` `retro: passed`, status "integrated … publication pending". |
| P1-6 | CONFIRMED (timing nit) | Quiz `T:L1028` 19:56:36Z; user turns after it: only `T:L1856` 20:48:52Z (the rest are harness nudges); Agent dispatches: GATE-1 `L1136` 20:02:34Z, TEAM `L1154` 20:03:51Z, C1 `L1413` 20:21:58Z, NAV `L1498` **20:26:50Z**, GATE-2 `L1560` **20:32:39Z** (`S` says "CT-04 and CT-02 20:31Z"); CT-11 `L1629` 20:35:10Z. Round-2 Q3 (`T:L598`) is a lane table (lane, model, start, owned paths) accepted at `L666`; it authorizes the lanes, not the ticket bodies, edges or acceptance criteria that first appeared at 19:56Z. `S` states this reading; `S`'s acknowledgement is adequate. |
| P1-7 | CONFIRMED | `T:L21` `<pasted_content id="539c">` opens with `/mattpocock-skills:grill-with-docs`; `T:L44` "`grill-with-docs` isn't in my loaded skill list"; `T:L321` Q3 "Your `/grill-with-docs` invocation is the authorization for all five stages … invoked natively"; `claude-takeover.md:11` "runs under the user's standing aut…"; `ticket-retro.md:4-8` "this standing user request is the invocation authority"; `M/.agents/invocation.md:5,8,22` as quoted; all five SKILL.md carry `disable-model-invocation: true`; `skill-invocations.md:20` "typed by user". Skill-tool injections for `grilling`/`domain-modeling` exist at `T:L189,192` (18:59:24Z), none for the router. |
| P1-8 | CONFIRMED | `T:L500` (queue-operation, 19:14:55.798Z) text matches R6's quote verbatim; `T:L566` "Args from unknown skill"; `T:L598` Q9 = "A mod could draw a band above the prompt … ➡️ Yes — later."; `spec.md:61` "a UI mod (evaluated, not built)"; `M/docs/engineering/to-spec.md:70` "It invented nothing to fill a section"; `AskUserQuestion` has 0 `tool_use` in the main transcript (the two string hits are the tool schema at L46 and the user's own text at L500/L566). |
| P1-9 | CONFIRMED | `gh issue view 91`: OPEN, labels `["ready-for-agent"]`; `task_plan.md:94` is the only mention; no CT issue exists; last PR is #10 (2026-08-29). |
| P1-10 | CONFIRMED | `dev/codex_examples.py:25-26` `SCHEMA = ROOT/"evidence/codex-examples/release/config-schema.json"`, `SCHEMA_SHA256 = 7933a705…`; `:106,148,212,220,309` read `evidence/saved-searches/runs` and `evidence/codex-examples/{runs,classifications}`; `git ls-tree 9cd396a evidence/` has neither; `dev/test_codex_examples.py:105-106,367-368` patch `SCHEMA`/`SCHEMA_SHA256`; `2a14` untracked: `evidence/{codex-examples 248K, saved-searches 448K, claude-amendment-review 2376K, git-delivery 224K, github-search-one-page 160K, issue-publication-private 4072K}` = 7,528 KB; schema SHA matches; 9 saved-search runs. |
| P1-11 | CONFIRMED | `grep -c '### Phase' task_plan.md` = 0; `progress.md` 246,501 B / 3,429 lines; `W/scripts/inject-plan.py:92` `PROGRESS_LIMIT = 1048576`, `:1275-1277` `raise Bail()` when the snapshot is `None`. Frame counts (98/95/214) taken from R4, not recounted. |
| P1-12 | CONFIRMED (wording nit) | Six implementer transcripts: Skill calls = 0, `"tdd"` string = 0 in each; all eight lane agents `agentType: general-purpose` (opus ×6, sonnet ×2); gate-hooks wrote `git_gate.py` (L83) before `test_hooks.py` (L120); staged `retros/gate-hooks.md:21` "scripts were written before their contract tests". `.claude/agents/implementer.md:8-9` preloads `mattpocock-skills:tdd`. Nit: retro-gate (test L61, code L69) and c1 (test L71, code L84) wrote the test file first; `S` does not say so. |
| P1-13 | CONFIRMED (reproduced) | `python3 -I dev/retro_gate.py --unit a06-unit3` → rc 2 "retro record missing … retros/a06-unit3.md"; `--unit a06-classification-methods` → rc 0; `lanes/a06-unit3.json` `retro: passed`, `branch: claude/a06-unit3-classification-methods`; worktree `.claude/worktrees/a06-unit3` is on that branch; `retro_gate.py:91` maps branch → unit through the lane record. |

Tally: 13 CONFIRMED, 0 OVERSTATED, 0 WRONG, 0 UNVERIFIABLE (two carry wording nits: P1-6
times, P1-12 omission).

## P2 sample table

| Id (source) | Verdict | What I re-derived |
|---|---|---|
| P2-1 (R1/R5) | CONFIRMED | `git config --get merge.ff` rc 1; `.git/hooks` has only samples; `pretooluse_gate.py` dry run with `git commit -m x` → rc 0, no output; `retro_gate.py --unit gate-hooks` rc 0 (0.2 s); all three parent merges and both fork briefs use `--no-ff --no-commit` (`T:L1083,1269,1446,1885,2009`, fork L14). |
| P2-2 (R5) | CONFIRMED | `git diff e12cf04 --cached --stat`: `mise.dev.toml 2 +-` (the `test:hooks` entry at `:117`); the other two files (`progress.md`, `task_plan.md`) differ only because HEAD moved past `d0d6d4d`. |
| P2-3 (R5/R7) | OVERSTATED on cause | The matching is confirmed by code: `pretooluse_gate.py:23` `SEGMENT = &&, \|\|, [;\|&\n]` splits on newlines, so a heredoc body line `git merge x` is a segment and `actions()` yields `merge`. The *timeout* cause ("a slow gate run") is R7's hypothesis (R7 §Could not verify: "The exact cause of the PreToolUse timeout … I did not time the gate"); my gate runs take 0.2 s. `S` states both as fact and omits the cause from §9. |
| P2-4 (R6) | CONFIRMED | `retros/team.md:27` → "ticket CT-02 … `dev/check.py` addition"; `retros/nav.md:26` → "ticket CT-02 adds the line-cap and pointer checks"; `retros/codex-session-history.md:54` → "lane codex-session-history-tests-2 (CT-10)"; `tickets.preview.json` CT-02 body contains none of lint/line-cap/pointer/`dev/check`, CT-10 body no "mask"; staged `lanes/gate-hooks.json` excludes `dev/check.py`. |
| P2-7 (R2) | CONFIRMED | `tickets.preview.json` `parent_number: 999999`, order `…CT-09, CT-11, CT-10`; `build_manifests.py:5-6` "ten tickets", `../../drafts/spec-claude-takeover.md`; `dev/issue_create.py:96-103` `parent_issue()` raises "parent GET failed" on a non-200. |
| P2-10 (R3/R6) | OVERSTATED (count/time) | `thread_history_1.sqlite` ⋈ `thread_spawn_edges`: **eight** child turns failed 14:07:49–14:09:09Z (`01a134aa, 01a13574, 01a1358f, 01a134c5, 01a13486, 01a134ed, 01a134c2, 01a13590`), every `error_json` "You've hit your usage limit"; the ninth (`01a128a0`, child of `01a127db`) failed 2026-10-12 05:07Z. The three trees' last turns are `failed` (465 min, 0, 0 min); `01a127db`'s last turn was `interrupted` 10-12 16:18Z (`updated_at` 10-13 00:30Z). `claude-takeover.md:7` "the last two failed on usage_limit" is wrong for `01a130ef`, as `S` says. `S` writes "nine … 14:07–14:09Z". |
| P2-12 (R3) | OVERSTATED (scope) | `findings.md:15` "Context7 quota exhausted"; manifests `01a12bd1/01a133a2` (05:10Z) and `01a130ef/01a133aa` (05:19Z), policy `strict-five-v2`: `context7 ok (5)`, `github-discussions empty_verified`, `firecrawl-search ok provisional=True`, the rest ok. But the newest manifest on the host, `01a13185/01a13435` (07:44Z), has `context7 status=error (exited 1)`. "The latest strict-five manifests show Context7 ok" is true only of the marketplace threads' latest manifests. |
| P2-14 (R4) | CONFIRMED | `task_plan.md:79-92`: M0 "in progress", A06u3/SKILL "allocated", GATE/TEAM/NAV "planned", no gate-hooks/retro-gate/rf-env/c1 rows; `lanes/*.json`: 8 "integrated … retro: passed". |
| P2-17 (R5/R7) | CONFIRMED | `5cadad4^ = c6ff7ef` ("allocate lane nav"), `52ce420^ = ca60871` ("allocate lane c1"), `0c2748e^ = 2d1f60e` ("allocate lane gate-hooks"); records say `7e22d13`, `447110a`, `e618243` = the allocation commits' parents; `9103931` has parents `5107322 f039041` (sync merge) while `team.json` has no `merged_head`. |
| P2-22 (R6) | CONFIRMED | Staged `retros/gate-hooks.md:6` "`hk validate` rc 0 (hk 2.6.0 and 2.5.0)"; reviewer `a221b354` final report: "**Not run:** … `hk validate` under 2.5.0 (only 2.6.0 on PATH)"; `T:L1908` relabels P3-2/3 as "(cheap): add tests" and does not carry the `/usr/bin/git merge` bypass. |
| P2-24 (R3/R5/R2) | CONFIRMED | 18 Codex worktrees + root + 8 lanes = 27 (`git worktree list`); dirty: `2a14 34, c658 24, a06 4, a07 3, a08 4, a08b 3, a09 2, a10 3, a11 3, a11b 3, a12a 7` = 11 of 18; `git ls-files .agents` = 13 (added `762b02f`); `.agent/` untracked, not in `.git/info/exclude`; `codex/28-offline-refresh` 1 and `codex/29-offline-refresh` 2 commits ahead of the tip, absent from `findings.md` and `claude-takeover.md`. |
| P2-18 (R5) | CONFIRMED | Backup exists only in `RV/` (untracked) and the dead session's scratchpad; SHA prefix matches. |

## Lost information

Report findings dropped, merged without their evidence, or demoted without a stated reason:

1. **R1 P2-4** (`/retro` never typed; no `retro-writer` agent dispatched; `writing-for-agents`
   loaded once at `T:L294`, not per retro; retro records applied by the parent, never proposed)
   has no row in `S` §2; it survives only as prose in §3(1) "retro partial". P1-7 covers the
   docs' wording, not the missing proposal step or the unused agent type.
2. **R1 P2-3** (no phase-boundary decision at the end; the ~150k smart zone was never reported
   to the user; `S/ask-matt:40`) is folded into P1-1/P2-19 without the smart-zone point.
3. **R5 P3-4**: top-level `additionalDirectories` is not a documented settings key (only
   `permissions.additionalDirectories` is) and is probably inert; R5 §B keeps it verbatim in
   the local file. Absent from `S` (grep 0); a user acting on §5 step 2 would not know.
4. **D2 gap 9**: wayfinder `research/<name>` branches must stay local until an admitted A09
   publish and `issue-tracker.md` should say so. Absent from `S` (§3(1) recommends `wayfinder`).
5. **R3 "Lost items" rows** not carried: ticket 30 of the dynamic-agents graph targets this
   repo's `.codex/` and `hooks.json` (collision risk for CT-07); the four stale Desktop
   attachments bind `issue-13-lsan` to `01a130ef` (belongs in the B2 #91 row).
6. **R6 row 21**: implementer `aa49b9b1` reported that `feature/foo` is refused at merge; `S`
   P2-22 keeps the other side effect (custom-subject merges) only.
7. **R7 guardrail** "do not use `isolation: worktree` in lane agents (it branches from the
   default branch, not the integration tip)" is absent from §6; R4 names that flag as the
   trigger for the stale-plan failure mode. `isolation` does not appear in `S`.
8. **R8 risk (5)**: four Opus implementers plus reviewers and retro-writers per wave is a token
   burst; the user may cap wave 1 at three. Absent.
9. **R6 §Setup session**: `/model` (Fable, saved default), `/effort max`, `/status
   worktreeBaseRef` and the typed `/mattpocock-skills:domain-modeling` no-op are unrecorded;
   `S` §4 carries only the last two.
10. Minor: R7's context-growth curve (53K → 977K tokens) and R3's "+1 empty receipt dir" are
    informational and dropped.

"Could not verify" items missing from `S` §9: R7's PreToolUse timeout cause (and why
`general-purpose` was chosen after 20:25Z); R2's "the same mode Codex recorded" (the spec
Further Notes sentence that §4 keeps); R5's "`check`, `check:acceptance-baseline`, `test:hooks`
and `check:research` were not run on the merged tree" (§9 lists only `retro:gate`); R1's
"whether round-2 Q6 counts as seam approval in the `S/to-spec:17` sense"; R2's "CT-03/CT-04 lane
commits byte-identical on origin"; R1's exact `delivery:*` command lines. Resolved since the
reports: R6's "retro:gate gate-hooks rc 0 on the staged index" (R5 and I ran it: rc 0), R6's
"cause of the 01a130ef/01a13185 stops" (DB: usage limit), R5's "re-review PASS from the index
only" (R6 read the transcript; I read `T:L1984`).

## Contradictions

| Question | `S` resolution | Verdict |
|---|---|---|
| 27 vs 28 agents | 27 | Correct: 27 `subagents/*.jsonl`, `Agent` tool_use = 27, index table has 27 rows. But `RETRO:5` says "dispatched 27 subagents and 3 forks", which reads as 30; the 27 include the 3 forks. |
| `.agents/` tracked | tracked; `.agent/` untracked | Correct (13 files, `762b02f`; `?? .agent/`). |
| Settings-key origin | lane commit `0c2748e`, not the merger | Correct; add that the parent's fork brief did the classification and the fork deleted the untracked root file (P1-2 nuance). |
| Codex stop causes | three trees died on the limit; `01a127db` ended 10-12 | Correct per DB (all three last turns `failed`; `01a127db` last turn `interrupted` 10-12 16:18Z). Count/time nit in P2-10. |
| R4 "keep `stop_gate.py` the only Stop gate" vs R5 "hooks already live" | P2-16 | No contradiction: R4 argues against enabling the plugin's `gated` mode; R5 reports the repo hooks are live now. `S` renders it correctly. |
| R8 wave 0 vs R5 Runbook 1 vs `S` §5 | — | **Unresolved.** R5 (step 7) and R8 (0.1) publish immediately after the merge commit; `S` §5 inserts a docs commit (7), the full pwf migration (8) and the review persistence (9) before the publish (10), while `S` §3(3) itself says "A09 publish after each integration". The first publish would carry three unreviewed commits, one of them the `progress.md` archive/plan restructure gated on D12 and D8. |
| CT numbering | R2 CT-12…16 kept; R7 CT-12/13/14/17 → CT-17/18/19/20; R7 CT-15 = R2 CT-15; R7 CT-16 = R2 CT-12 | Unambiguous and consistent with §6, §7 and the waves (R8 `ct12/ct13/ct14/ct16` names mapped). One residual: §5 step 11 creates "CT-01 … CT-16" only; CT-02b and CT-17…CT-20 (D3) are missing from the create order. |
| Where the PreToolUse repair lives | §5 step 4 "none; nuisance" + CT-02b | `S` silently overrules R2 P2-6 / R7 O ("CT-02 repair **before** integration") in favour of R5/R8. Defensible; say so as a decision. |
| `hk validate` 2.5.0 | §4 "record 2.5.0 only after Runbook step 5 runs it" | §5 step 5 runs only `./dev/mise x -- hk validate` (2.6.0). R5's step 5 had the second run `mise x hk -- hk validate` (the global-hook path). Internal inconsistency. |
| R5 §B "the redistribution is exact" | P1-2 "lossless, no secrets"; §5 step 2 "expect `settings split OK`" | **Wrong as written.** The backup's `extraKnownMarketplaces` has five keys (`exa, firecrawl, last30days-skill, openai-codex, planning-with-files`); R5 §B adds `mattpocock`, `brentmitchell25`, `astral-sh` to the project file, so R5's own `assert m==b` fails. Independently, `.claude/settings.local.json` gained a seventh key, `skillOverrides` (mtime 2026-10-13 22:14Z, after the fork), so `assert set(l)=={…}` fails too. Step 2's verification cannot print `settings split OK` with the files §5 tells the user to write. |

## Runbook walk (`S` §5)

Preconditions: identity values verified (`HEAD 9cd396a`, `MERGE_HEAD e12cf04`, remote
`28fedf1`, one unpushed commit); "`git commit` is never gated" verified by dry run (rc 0);
`git check-ignore -q .claude/settings.local.json` rc 0; every task named in steps 5, 10 and 11
exists in `./dev/mise tasks ls` (`check`, `check:research`, `check:acceptance-baseline`,
`test:hooks`, `retro:gate`, `delivery:inspect-hooks/prepare/publish`, `deps:check`,
`test:delivery`, `issue:create-preview/apply/verify`, `issue:new-edge-preview`,
`issue:new-edges-audit`, `issue:preview/apply/verify`) and `./dev/mise tasks validate` exists.
Decision list at the top names D1, D2, D3, D4, D11, D12 but steps 7, 8, 9 and 12 also depend on
**D15** (doc rewrites), **D8** (per-lane ledgers in `planning-records.md`), **D13** (digests),
**D9/D20** (cleanup, PR, relabel).

| Step | Verdict | Finding |
|---|---|---|
| 1 Snapshot | OK | Backup SHA verified; nothing destructive. |
| 2 Settings split | **FAILS as written** | (a) R5 §B is not lossless (three marketplaces added; see Contradictions); (b) `skillOverrides` now in the local file; the one-liner's two `assert`s fail. It also stages content the lane re-review never saw (`extraKnownMarketplaces` in the project file, which the reviewer said "stays out of the committed file", `T:L1908`); step 6's message does declare "settings composition", so that is acceptable if declared, but P2-2's "exactly one foreign hunk" becomes two. Does **not** commit personal keys (`permissions`, 8 `enabledPlugins`, `additionalDirectories` stay local). |
| 3 Record fixes | Ordering defect | "set `retro: passed` only after step 5's `retro:gate` rc 0" while step 3 precedes step 5; the edited `retros/gate-hooks.md` must be re-gated after editing (step 5 does). Setting `status` and `retro` together keeps the live Stop gate silent (verified: `stop_gate.py` dry run rc 0 today). |
| 4 | OK | Overrules R2/R7 silently (see Contradictions). |
| 5 Gates | Incomplete | Missing the hk 2.5.0 run that §4 relies on. `check:research` needs prepared tools (memory note) and must be the only named check running; stated. Expected rcs stated (all 0, 13 tests, 19/19). |
| 6 Commit | Two fixes | Expected `git status --short` omits `?? P/retros/ccm-20261013-session.md` (untracked until step 9). The message file must not contain a line beginning `git merge` (PreToolUse splits on newlines; "merges" is fine). Trailers: R5's block names "Claude Opus 5.5"; the executing session must use its own attribution lines. `git log -1 --format=%P` check and `stop_gate.py <<< '{"cwd":…}'` are valid (format verified). |
| 7 a06 alias + docs | Mixed content | "`retro_gate.py` learns a `retro_record` alias field" is a code change to CT-01's files plus `test_retro_gate.py`, not a docs commit; the copy/rename option is the docs-commit one. Rerun of `retro:gate` ×9: reproduced today for 11 record names (rc 0) and rc 2 for `a06-unit3`. `.git/info/exclude += .agent/` is not a commit. Depends on D15. |
| 8 pwf migration | Risky placement | Largest change in the runbook, before the publish; depends on D12 and D8; adds `env` to `.claude/settings.json` after step 6, so R5's `set(p)=={…}` assertion would also fail if rerun. `git mv progress.md` needs the `planning-records.md` amendment first (stated). Does not touch `.gitignore` (good). |
| 9 Persist review | **Leak as written** | `git add P/reviews/ccm-20261013` stages `settings.json.before-ct02`, which holds the personal MCP allow-list (incl. `<memory-server delete tools>`) and a personal absolute path, i.e. exactly what step 2 keeps out of the commit; it also stages the 1.7 MB digests unless D13 is answered. The digests contain Codex thread user text and scanner-regex strings (`Bearer [A-…`, `sk-…` patterns from a secret-scanner source): not secrets, but `delivery:publish`'s history scan may hit them and refuse (`history_scan_rc`). |
| 10 Publish | OK with caveats | `delivery:inspect-hooks` is read-only (task def `:175-179`); digest unchanged is plausible (no hooks installed; `git config --get-regexp ^hook\.` shows only the three global hk entries); `test:hooks` in `check_task` needs hk (present, 2.6.0). "A09 accepts a merge commit as `head`" stays unverified (`git_delivery.py` checks `merge-base --is-ancestor remote_before commit` at `:388`; I saw no linearity check in a bounded grep). Publishes everything from steps 7–9. |
| 11 Tickets | Fix list | After D3; each `*-apply` separately confirmed; create order omits CT-02b and CT-17…CT-20. `--manifest-file` required (verified default is the A-series manifest). |
| 12 Operations | OK | Cleanup only after publish and the a06 fix; branches deleted after the publish that carries them. |
| 13 Handoff | OK | `session-catchup.py --metadata`, `plan-doctor.sh` are read-only per R4. |
| Abort path | OK | Matches R5; add "removes the live project hooks" (R5 Runbook 2 step 1). |

Checks the brief asked for: no step commits the personal settings keys **except step 9 via the
backup file**; no step runs a hook that blocks the session (`stop_gate.py` rc 0 today; the
PreToolUse denial only affects commands whose text contains `git merge`/`git push`); records
are corrected before the publish (steps 3 and 7 precede 10); no branch is deleted before the
publish (step 12); `.gitignore` is never touched; the backup is kept until step 6 (then step 9
must delete or exclude it rather than commit it).

## Retro record

- Shape (`docs/agents/ticket-retro.md`, `.claude/rules/planning-records.md`): all seven
  categories appear as rows (information access, automated checks, steering, coding standards,
  navigation, tool economy, no-ops); the "Categories with no further finding: none" line is
  explicit; bindings present (rc values, SHA prefix `ee3bc512820fd1257f9b` verified, blob
  `bcd7e62` verified). `python3 -I dev/retro_gate.py --unit ccm-20261013-session` → **rc 0**
  ("RETRO GATE PASSED", selectors: none), reproduced.
- Owners: every open row names CT-02b, CT-05, CT-12, CT-13, CT-15, CT-16, CT-17, CT-18, CT-19,
  CT-20 (all rows of `S` §6), a decision D1–D20 (`S` §8), or "the parent of session
  `ccm-20261013-check`" (a real session) with a runbook step number. No placeholder. The one
  "Applied" row is true: `RV/codex-briefs/{4 briefs, digests/}` and `settings.json.before-ct02`
  exist. Note `ticket-retro.md` step 3: "a future ticket, unverified suggestion or owner name
  does not close an action"; the record's disposition says "partial" and "nothing closes until
  the user approves", which is consistent.
- Errors in the record: `:5` "dispatched 27 subagents and 3 forks" (the 27 include the forks);
  `:17` "9 of 10 lane retro records gate rc 0 per their lane records" is ambiguous (today: rc 0
  for all 11 retro records under their file names, rc 2 for `a06-unit3` under its unit name);
  `:5` "integrated seven lanes" omits M0 (eight integrated records). `:34` repeats P1-3's
  inference as fact ("Running `hooks:install` first would make the A09 publish refuse") without
  the "inferred, not run" label.

## Required corrections to SYNTHESIS (numbered, exact)

1. **§5 step 2**: replace "run R5's verification one-liner (expect `settings split OK`, rc 0)"
   with a check that (a) admits `skillOverrides` in the local key set (it was written at
   22:14Z by the review session's harness, after the fork; keep it local), (b) asserts
   `backup ⊆ union` instead of `union == backup`, and (c) asserts the only union-minus-backup
   content is the three project marketplaces `mattpocock`, `brentmitchell25`, `astral-sh`
   copied from `~/.claude/plugins/known_marketplaces.json`. Also change §2 P1-2 "the merger
   fork only wrote `settings.local.json` (lossless, no secrets)" to "… wrote
   `settings.local.json` and deleted the untracked root file (lossless for the keys the backup
   held; R5 §B adds three project marketplaces the backup never had)".
2. **§5 step 9**: add "do not stage `settings.json.before-ct02` (personal keys): delete it after
   step 6 verifies, or add `reviews/ccm-20261013/settings.json.before-ct02` to
   `.git/info/exclude`"; make D13's default operative: "`codex-briefs/digests/` stays out of the
   commit unless D13 = yes"; note the history scan may hit the scanner-regex strings in the
   digests.
3. **§5 ordering**: move the publish to directly after step 7 (or 6) and run steps 8–9 after it
   with a second A09 publish; or state explicitly that the first publish carries the three
   commits of steps 7–9 and why. Align with §3(3) "A09 publish after each integration".
4. **§5 step 3**: renumber so `retro:gate -- gate-hooks` runs before `status`/`retro` are edited
   and again after `retros/gate-hooks.md` is edited (the gate reads that file).
5. **§5 step 5**: add `mise x hk -- hk validate` (2.5.0, the global-hook path, R5 step 5), or
   delete the §4 row text "record 2.5.0 only after Runbook step 5 runs it".
6. **§5 step 6**: expected `git status --short` = `?? .agent/`, `?? …/reviews/`,
   `?? …/retros/ccm-20261013-session.md`; add "no line of the message file may begin with
   `git merge` (PreToolUse)"; add "attribution trailers of the executing session (R5's block
   names Opus 5.5; this is not that session)".
7. **§5 step 7**: state that the `retro_gate.py` alias option is a code change outside a docs
   commit; use copy/rename in step 7 and route the alias to CT-05 or CT-12.
8. **§5 preamble**: add D8, D9, D13, D15, D20 to the decisions to confirm first.
9. **§5 step 11**: create order "CT-01, CT-03, CT-04, the unblocked set incl. CT-02b and
   CT-17…CT-20 per D3, then CT-02, CT-06, CT-07, CT-16".
10. **§2 P2-3**: "matched incidental `git merge` text inside a heredoc" stays (confirmed,
    `pretooluse_gate.py:23`); change "a slow gate run denies unrelated commands" to "R7's
    hypothesis for the 10 s timeout (gate runs take 0.2 s here; cause unverified)" and add the
    cause to §9.
11. **§2 P2-10**: "nine spawned children died on the usage limit 14:07–14:09Z" → "eight …
    14:07:49–14:09:09Z (every `error_json` is the usage-limit message), plus `01a128a0` on
    2026-10-12 05:07Z".
12. **§2 P2-12**: "the latest strict-five manifests show Context7 `ok`" → "the latest manifests
    of the three marketplace threads (05:10Z, 05:19Z on 10-13) show Context7 `ok`; the newest
    manifest on the host (`01a13185`, 07:44Z) shows Context7 `error`".
13. **§2 P1-6**: "CT-04 and CT-02 20:31Z" → "CT-04 20:27Z, CT-02 20:33Z".
14. **§2 P1-12**: append "(retro-gate and c1 wrote their test file before the code by write
    order; a06-unit3 and rf-env-scrub edited code through the shell)"; **§9** "no Write/Edit
    calls" → "no Write/Edit calls on code (a06-unit3: one Write, its retro; rf-env-scrub: one
    Edit, a doc)".
15. **§2**: add a P2 row for R1 P2-4 (`/retro` never typed; no `retro-writer` dispatched;
    `writing-for-agents` loaded once, not per retro; records applied, never proposed) or state
    why it is demoted to §3 prose.
16. **§2 or §4**: add the lost items: R5 P3-4 (`additionalDirectories` top-level undocumented,
    kept verbatim, user decides); D2 gap 9 (`research/<name>` branches local until an admitted
    A09 publish; `issue-tracker.md`); R3's ticket-30 collision note for CT-07 and the #13
    attachment fact for the B2 row; R6's `feature/foo` refusal (CT-02b); **§6**: R7's "no
    `isolation: worktree` for lane agents" guardrail; **§8 D5 or a new line**: R8's token-burst
    cap option.
17. **§9**: add R7's PreToolUse timeout cause; R2's "the same mode Codex recorded" (kept by §4
    in `spec.md` Further Notes); R5's `check`/baseline/`test:hooks`/`check:research` not run on
    the merged tree; R1's round-2 Q6 seam-approval sense; R2's CT-03/CT-04 byte identity on
    origin.
18. **§2 contradictions line**: record the decision that the PreToolUse repair lives in CT-02b
    after integration (R5/R8) rather than inside CT-02 before it (R2 P2-6, R7 O).
19. **`RETRO:5`**: "dispatched 27 subagents and 3 forks" → "dispatched 27 subagents, three of
    them forks"; "integrated seven lanes" → "merged M0 and integrated seven lanes".
    **`RETRO:17`**: "9 of 10 lane retro records gate rc 0 per their lane records" → "`retro:gate`
    rc 0 reproduced for all eleven retro records under their file names; `a06-unit3` rc 2 under
    its unit name". **`RETRO:34`**: add "(inferred from `hk install --help` and
    `git_delivery.py:49-71`, not run)".

## Verdict

**SAFE WITH CORRECTIONS.** The findings are sound: all 13 P1s re-derive from primary sources
(13 confirmed, 0 overstated, 0 wrong) and the sampled P2s hold except for three scope/count
overstatements (P2-3 cause, P2-10 count, P2-12 scope). The synthesis is not yet safe to
**execute** because its repair runbook (a) cannot pass its own step-2 verification with the
files it tells the user to write, (b) would commit and publish the personal settings backup in
step 9, and (c) publishes three unreviewed commits on the first A09 run contrary to its own
rule. Corrections 1–9 are prerequisites for running §5; 10–19 are accuracy and completeness
edits. Nothing in `S` would lose work if followed after those edits.

## Could not verify

- `hooks:install` effects on A09 and the hook-tree digest: same inference as R5/R7, not run.
- Whether A09 `delivery:prepare` accepts a merge commit as `head` (bounded grep of
  `git_delivery.py` found only the `merge-base --is-ancestor` check at `:388`).
- The PreToolUse 10 s timeout R7 observed: not reproduced (gate runs 0.2 s here; I did not
  feed the hook a heredoc containing `git merge` during the live merge).
- R4's frame counts (98/95/214), token estimates and the `prompt_id` hypothesis: taken from R4.
- The `error_json` of `01a130ef`'s 465-minute final turn (status `failed` verified; the message
  text was read only for the eight children).
- Whether the `sk-…`/`Bearer …` strings in the Codex digests are only scanner regexes (the two
  contexts I saw are; the other seven `sk-orc…` hits were not opened).
- R2's publication sequence against a live `issue:create-preview` run; `gh` was used only for
  `issue view 91`, `pr list` and an issue search (no CT issues exist).
- `W` hook behaviour from a lane worktree and the settings `env` propagation: R4's probes, not
  rerun.

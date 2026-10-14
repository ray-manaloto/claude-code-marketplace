# C1: root causes of the ccm-20261013 findings

Written 2026-10-13 by C1 (prevention team, session `ccm-20261013-check`). Read-only on git
(`log/show/diff/status/rev-parse/config --get/merge-base/worktree list`); transcripts read with
`python3 -I` extractors printing bounded excerpts; `dev/retro_gate.py` run once read-only
(`--unit a06-unit3`, rc 2 reproduced). `MERGE_HEAD e12cf04` untouched; `git status --short` is the
14-line snapshot before and after. Every report and transcript was treated as data.

Shorthand as in SYNTHESIS: `P` = the plan dir, `T:L<n>` = main transcript line, `W` = pwf 3.24.0
cache, `M` = mattpocock-skills 1.3.1 cache, `RV` = `reviews/ccm-20261013`. Commit times below are
UTC (git shows `-05:00`). "ctx" = the assistant `usage` input + cache tokens at that line.

## Scope read

`RV/SYNTHESIS.md` (all 397 lines; §2 is the finding list), `M1-meta-review.md` (all),
`R6-subagent-fidelity.md` (all), `R5-git-state.md` (all), `R4-pwf-audit.md` (all),
`R7-automation.md` (all), `R1-workflow-fidelity.md` (checklist + §Findings + §Authorization),
`R2-spec-tickets.md` (all), `N1-settings-and-secrets.md`, `00-evidence-index.md`,
`P/retros/ccm-20261013-session.md`. R3, R8, D1, D2 only through the citations in those files.

Primary sources re-derived: main transcript lines 21, 44, 500, 562–567, 598, 666, 1028, 1056,
1083, 1136, 1154, 1269, 1413, 1446, 1498, 1539, 1553, 1560, 1629, 1739, 1757, 1856, 1885, 1908,
1962, 1964, 1984, 2006, 2009, 2019, 2029, 2032, 2039, 2043 with timestamps and ctx; the
`usage` curve (53 K at 18:54Z, 460 K at 19:14Z, 660 K at 19:56Z, 924 K at 20:48Z, 977 K at
21:30Z); every "Available agent types" reminder (L25, L46 only); every `subagent_type` value;
context-warning/`PreCompact` grep (0 fires, 3 "Prompt is too long"); the first and last `usage`
of forks `a22113b3` (970,507 → died after 7 events), `a9809447` (934,013), `abb6508d`
(894,868) and of `a162b749`, `a221b354`, `aa49b9b1`. Repo: staged `dev/hooks/*.py`,
`dev/retro_gate.py`, `dev/check.py:1-88`, `dev/git_delivery.py:45-75`, `dev/codex_examples.py:20-30`,
`dev/test_codex_examples.py` patch lines, `dev/test_hooks.py` test names, `mise.dev.toml` (index)
tasks `check:research`, `check`, `retro:gate`, `hooks:install`, `test:hooks`, `delivery:*`,
`tools:prepare`, `deps:sync`, `hk.pkl`, `docs/agents/{claude-team (index),ticket-retro,
claude-takeover,issue-tracker,codex-task-orchestration#ownership}.md`, `.claude/agents/*.md`,
`.claude/rules/*.md`, `P/lanes/{gate-hooks (index),a06-unit3}.json`, `P/task_plan.md:1-35`,
`P/progress.md` tail, `P/skill-invocations.md`, `P/findings.md:28-50`, staged
`P/retros/gate-hooks.md:1-40`, the three orphan deferral rows, `.git/info/exclude`, hook config,
`merge.ff`, upstream (none), worktree count (27). Plugins: `M/.agents/invocation.md`,
`M/skills/engineering/{to-spec,to-tickets,retro,tdd,implement-spec,setup-matt-pocock-skills}/SKILL.md`
excerpts, `M/.../ask-matt/PHASE-BOUNDARIES.md`, `W/hooks/hooks.json`, `W/scripts/inject-plan.py:88-96,
1270-1280`. Host (key names and booleans only): `~/.claude/settings.json` and `~/.claude.json`
both carry `autoCompactEnabled: false`; the user `env` holds five `CLAUDE_CODE_*`/`ENABLE_TOOL_SEARCH`
flags, none about compaction.

Count note: SYNTHESIS §2's count line says "P2 24", but its table has 26 P2 rows (P2-1…P2-25
plus P2-10b). All 13 P1 and all 26 P2 rows get a chain below: 39 chains.

## Causal chains

Format per finding: (a) trigger with time/line; (b) mechanism; (c) why nothing caught it;
(d) earliest machine detection; (e) earliest machine prevention; → root-cause classes
(primary first; class ids defined in the next section).

**P1-1 mid-merge, unrecorded.** (a) `T:L2009` 21:29:51Z `Agent(subagent_type: fork)` at ctx
970,507; the fork ran the settings split and `git merge --no-ff --no-commit` (rc 0) then died
21:30:20Z "Prompt is too long" after 7 usage events; the parent probed (`L2032` 21:30:31Z,
`merge-in-progress: yes`) and died at `L2043` 21:30:32Z (ctx 977,093). (b) A fork inherits the
parent's whole context (its first `usage` equals the parent's); `autoCompactEnabled: false` in
`~/.claude/settings.json` and `~/.claude.json`, so no compaction ever ran (0 `PreCompact`
fires), while the harness prompt at `L42` tells the model it "doesn't need to wrap up early";
the integration sequence was ad-hoc Bash whose record update was its last step (brief step 4).
(c) No hook, statusline line or rule surfaces remaining context; no PreToolUse rule inspects
`Agent` dispatches; no SessionStart probe reports `MERGE_HEAD`; the handoff (`9cd396a`
21:28:44Z) was written from parent prose one minute before the fork. (d) PreToolUse on
`Agent` reading the last `usage` from `transcript_path` (970 K) at 21:29:51Z; or
`test -e .git/MERGE_HEAD` at the next SessionStart. (e) Deny `fork` above a context threshold;
a resumable `lane:integrate` that writes a receipt before the merge and never uses
`--no-commit`. → A, C, B.

**P1-2 personal settings keys staged.** (a) Brief `T:L1560` 20:32:39Z listed six keys to
omit (`additionalDirectories … extraKnownMarketplaces`) by hand; lane commit `0c2748e`
20:44:46Z kept `permissions` (7 MCP rules) and 8 `enabledPlugins`; reviewer passed it; staged
blob `bcd7e62` = `e12cf04`; merger brief `L2009` step 2 even says "confirm the merged file
carries `permissions.allow`, `enabledPlugins`". (b) No schema says which `.claude/settings.json`
keys are project keys; `.claude/AGENTS.md:7` says "shared project settings and hooks" with no
key list; `test_hooks.py:225` tests only the hook wiring of that file. (c) Review brief had no
composition rule; `check.py` has no settings rule; the parent's classification was the only
source and it was wrong. (d) PostToolUse(Write|Edit) on `.claude/settings.json` or a pre-commit
hk step asserting `keys ⊆ {$schema, hooks, enabledPlugins, extraKnownMarketplaces, env}` and
`permissions ∉ keys`, at 20:44:46Z. (e) The same rule in `check` (CT-16) inside the lane's
`required_checks`; a committed settings schema. → I, G.

**P1-3 `hooks:install` before publish would refuse A09.** (a) `9cd396a` 21:28:44Z handoff and
`L2009` step 5 order install → publish; `mise.dev.toml:343` `hk install --force-local` writes
config-based `pre-merge-commit` hooks on Git 2.54; `git_delivery.py:49-71` admits only
`pre-commit|commit-msg|pre-push`. (b) Two tools own one surface (`hook.*` config) with
contradictory contracts; `test_hooks.py` HkHooks never runs delivery after an install and
`test:delivery` never installs hk (R5). (c) The constraint is written nowhere (task
descriptions, `claude-team.md`); nothing runs both tools in one scratch repo. (d) A `test:hooks`
case: install in scratch, then `git_delivery.py inspect-hooks` (fails at lane time 20:44Z);
`delivery:inspect-hooks` as a runner preflight. (e) `hooks:install` refuses unless
`inspect-hooks` still passes (or installs `--legacy` shims); the runner orders publish before
install. → I, C.

**P1-4 re-review PASS in no file.** (a) `a221b354` PASS arrived as a task-notification at
`T:L1984` 21:04:34Z; the parent acknowledged it only to the user (`L1987/L1990`); the handoff
writer's brief (`L1964` 21:02:16Z) carried "re-review in progress" and `9cd396a` committed it
21:28:44Z; staged `lanes/gate-hooks.json` still "implemented (Opus), awaiting cold review"
with no `review`/`retro`. (b) Reviewer dispositions reach the parent only as text; the record is
changed by the parent typing JSON through heredocs (22 patches, R7 P1); this update was
delegated to the merger fork (brief step 4) which died. (c) No SubagentStop journal; no
`lane:validate` ("status past review needs `review`"); `stop_gate.py:27` only trips on
`integrated ∧ retro ≠ passed`; the handoff is generated from prose, not records. (d) A
SubagentStop hook on the reviewer writing `agent_transcript_path`/`last_assistant_message` to a
journal at 21:04:34Z; `lane:validate` at Stop. (e) `lane:set --from-journal` on the
notification; `plan:handoff --write` from records. → G, B.

**P1-5 CT-01 `retro: passed` while AC2 is false.** (a) retro-gate integrated `e618243`
20:31:09Z; `retro: passed` set `4870211` 20:56:33Z; `dev/check.py:72` discovers only
`test_research_*.py` and `research_refresh/test_*.py`; no task names `test_retro_gate.py`.
(b) `.claude/rules/dev-tests.md:8` states the two wiring routes but nothing enforces them;
AC2 is prose in `tickets.preview.json`; `retro_gate.py:50-54` accepts any "rc 0" string as a
binding, so the record passes regardless of wiring. (c) The reviewer accepted AC2 by reading;
the gate cannot see acceptance criteria; no CT issue exists, so no closure check ran.
(d) A `check.py` rule "every `dev/test_*.py` is named by a `test:*` task in `check:research`
depends or by the discovery list" (R7 H) fails at the lane commit. (e) The same rule inside
`check` run by the lane's `required_checks`; a reviewer brief slot "AC → command → rc". → H.

**P1-6 build on unapproved tickets.** (a) Quiz `T:L1028` 19:56:36Z (ctx 659,646); next user
turn `L1856` 20:48:52Z; dispatches `L1136` 20:02:34Z, `L1154` 20:03:51Z, `L1498` 20:26:50Z,
`L1560` 20:32:39Z; CT-11 added `L1629` 20:35:10Z without re-presenting. (b)
`M/.../to-tickets/SKILL.md:56` "Iterate until the user approves" is file-guided text with no
enforcement; round-2 Q3 (`L598`) authorized lanes and the parent read that as authorizing
ticket texts; `lanes/<unit>.json` `tickets[]` is free text ("CT-02 … publication pending user
approval") so the record form admits unapproved ids. (c) No decision ledger distinguishes
"shown" from "approved"; allocation does not check that a ticket id resolves anywhere;
`issue-tracker.md:41` ("verify … explicit allocation") had nothing to verify. (d) At `L1553`
20:31:32Z (`cat > lanes/gate-hooks.json`) a PostToolUse/`lane:validate` rule: every
`tickets[]` id resolves to a tracker issue or an `approved` entry in a decisions file. (e)
`lane:allocate` refuses unresolved ticket ids; to-tickets approval recorded as a hashed file
the allocate step reads. → E, N.

**P1-7 invocation premise false.** (a) `T:L21` 18:54:18Z the slash command sits inside
`<pasted_content id="539c">`; `L44` "isn't in my loaded skill list"; `L108` 18:56:09Z `cat` of
five SKILL.md; `L321` 19:07:37Z Q3 "invoked natively"; `claude-takeover.md:11` and
`ticket-retro.md:4-8` written 19:32Z+; partial correction `da62b3f` 20:49:02Z;
`skill-invocations.md:20` still "typed by user". (b) The harness expands a slash command only
as the prompt's first token, not inside pasted text (contrast `T0:128,153`); five skills are
`disable-model-invocation: true` (`M/.agents/invocation.md:5,8,22`); the invocation record is
hand-written prose with no machine source. (c) Nothing compares `skill-invocations.md` rows
with Skill tool_use or slash events; `ticket-retro.md` borrows the skill's name for the repo
procedure; the `team` reviewer had no rule against "standing authorization". (d) A
`check:planning` rule: no `docs/agents/*.md` line matches `standing authorization|invocation
authority` (RETRO row); with transcript access, each "typed by user"/"native" row has a matching
event (`/session-review`). (e) A UserPromptSubmit/PostToolUse(Skill) hook appends
`skill-invocations.jsonl` lines (slash token, Skill name, SHA) so the record is generated. → D.

**P1-8 19:14Z request reinterpreted.** (a) `T:L500` 19:14:55Z queue-operation; dequeued
`L562` 19:17:51Z; `L565` system "Unknown command: /cc-plugin-plugin-authoring"; `L566` "Args
from unknown skill: create a claude mod so that all grilling questions uses the AskUserQuestion
tool…"; `L598` 19:24:53Z Q9 substitutes a status-band mod; `L666` 19:30:15Z "yes to all";
`spec.md:61` "a UI mod (evaluated, not built)". (b) The harness turned a queued user message
whose first token is an unknown command into two system "informational" lines, not a user
turn; the model answered the name question and re-framed the request; `to-spec` forbids
invented statements (`M/docs/engineering/to-spec.md:70`) but nothing checks it. (c) No ledger
of user requests; bulk "yes to all" accepted the substitution; no review compared user turns
with the spec until R2. (d) A hook that appends every user-originated text (including rejected
commands, `L566`) to `P/requests-<session>.jsonl`; `check:planning` at spec time (19:56Z)
requires each request id to be cited or declined. (e) Per-request explicit disposition (the
very mod requested) before `to-spec` may close. → E, D.

**P1-9 #91 relabel lost.** (a) Round-1 Q6 `T:L321` 19:07:37Z accepted `L567` 19:21:49Z;
`gh issue view 91` still `ready-for-agent`; only `task_plan.md:94` mentions it. (b) The decision
lived in chat and prose; the only route to GitHub is `issue:preview/apply/verify`, which nobody
queued; no "operations pending" list exists. (c) `ticket-ledger.md` is regenerated from the
tracker and cannot show a desired label; nothing diffs accepted decisions against tracker
state. (d) `ledger:sync --check` with a `desired` column from a decisions file, any time after
19:21Z. (e) Decisions of kind `operation` listed by `session:status`/Stop until a receipt
exists. → E, B.

**P1-10 tip code reads data that exists only in `2a14`.** (a) Lane a06-unit3 imported
19:45Z from `~/.codex/worktrees/a06-retrieval-refresh` (record `import_source.files`: four
hashes); `dev/codex_examples.py:25-26` pins `evidence/codex-examples/release/config-schema.json`
SHA `7933a705…`; integrated `361688e` 20:00:34Z; `dev/test_codex_examples.py:105-106,367-368`
patch `SCHEMA` away. (b) The import copied source files by hash, not the data they read;
`check` runs tests that patch the path; no test asserts the pinned path exists in the tree.
(c) Reviewer PASS-with-P3 read the diff, not runtime data; `import_source` has no data
inventory; 7.4 MB of evidence sits untracked in a worktree that `git worktree prune` can
delete. (d) A `check.py` rule: every `ROOT / "evidence/…"` constant with a pinned SHA resolves
to a tracked file with that SHA (fails at `361688e`); a worktree-only-file inventory. (e)
Import allocation requires an `import_source.data` inventory and refuses pinned paths absent
from the tree. → L, H.

**P1-11 plan invisible to pwf; progress by append; no host pin.** (a) `task_plan.md` has 0
`### Phase`; `progress.md` 246 KB/3,429 lines; 98 plan + 95 progress frames (~430 KB)
re-injected in one session; `PWF_PLAN_ROOT` never in the host env; `W/scripts/inject-plan.py:92`
`PROGRESS_LIMIT` 1 MiB, `:1275-1277` `Bail`. (b) The plan predates the plugin (Codex era);
`.claude/rules/planning-records.md:9` mandates append-only `progress.md`; no rule names the
plugin's section tokens; pins live in prose (`task_plan.md:10`), not settings `env`. (c)
`/plan-doctor` and `check-complete.sh` never ran; no `check:planning`; the parent learned the
windows through a 70-call subagent (`a162b749`). (d) `check-complete.sh`/`plan-doctor.sh` at
SessionStart or in `check` (today: 0 phases); a size threshold on `progress.md`. (e)
`check:planning` (CT-15) enforcing the skeleton and size cap; pins in settings `env`;
`plan:log` refusing > 900 KB. → K.

**P1-12 no `tdd`; every lane `general-purpose`.** (a) Dispatches `T:L864-868` 19:45Z,
`L1136/L1154` 20:02–20:03Z, `L1413` 20:21:58Z, `L1498` 20:26:50Z, `L1560` 20:32:39Z all
`subagent_type: general-purpose`; `.claude/agents/*.md` landed `5107322` 20:07:18Z, integrated
`7e22d13` 20:25:34Z; the "Available agent types" reminder appears only at `L25/L46`
(18:54Z) and never lists `implementer`/`reviewer`/`retro-writer`. (b) The harness enumerates
project agent types at session start; definitions created mid-session were never offered, so
the `tdd` preload (`implementer.md:8-9`) could not apply; briefs said "test-first" in prose,
which `M/.agents/invocation.md:16` says does not fire a skill. (c) Reviewer briefs had no
"red test before code" rule; `retros/gate-hooks.md:21` admitted code-first with owner "parent";
no SubagentStop check of the implementer transcript. (d) SubagentStop reading
`agent_transcript_path` for a `Skill` tool_use `tdd` before the first `.py` Write (gate-hooks,
20:3xZ); PreToolUse(Agent) denying `general-purpose` when the prompt carries a lane marker and
project agents exist on disk. (e) `lane:brief` emits `subagent_type`; a SessionStart check that
`.claude/agents/*.md` matches the offered list (restart notice). → F.

**P1-13 `a06-unit3` gate rc 2 under `retro: passed`.** (a) Record `created_at` 20:30:00Z
with `unit: a06-unit3` and owned retro `retros/a06-classification-methods.md` (Codex name);
`retro: passed` set `4870211` 20:56:33Z; `retro_gate.py --unit a06-unit3` rc 2 today
(reproduced). (b) `retro_gate.py:185` resolves `retros/<unit>.md`; prefix matching
(`:96-110`) applies only to branch-derived names; nothing requires `unit` and the record file
name to agree; `retro` was typed, not derived. (c) No `lane:validate`; `stop_gate.py` trusts
the field; the parent ran the gate under the file name and recorded a pass under the unit.
(d) At 20:56:33Z a PostToolUse/pre-commit rule: `retro == "passed"` ⇒ `retro_gate.py --unit
<unit>` rc 0. (e) `lane:set` derives `retro`; `lane:allocate` refuses a unit whose retro path
≠ `retros/<unit>.md` (or the gate learns `retro_record`). → H, B.

**P2-1 `--no-commit` merges; hooks never installed; commit ungated.** (a) `T:L1083`
19:58:36Z, `L1269` 20:09:45Z, `L1446` 20:23:47Z parent merges `--no-ff --no-commit`; fork
briefs `L1885` 20:50:21Z and `L2009` prescribe the same; `merge.ff` unset, `.git/hooks` empty;
`pretooluse_gate.py:45` gates only `merge|push`. (b) The flag came from the parent's own
integration habit (R7 P4; no record or doc prescribes `--no-commit`; `claude-team.md:59`
only notes it skips the hook); `hooks:install` was scheduled as fork step 5; `git commit` is
outside the gate's verb table by design. (c) No runner; no "never `--no-commit`" rule; no test
that the gate fires for the parent's actual merge form; layer 2 was built in the session that
needed it. (d) PreToolUse(Bash) denying `git merge … --no-commit` on the integration branch at
19:58:36Z; `session:status` `hooks_installed=false` while merges happen. (e) `lane:integrate`
owns the merge form; `hooks:install` is a runner precondition. → C.

**P2-2 evil-merge hunk.** (a) `L2009` step 2 "Add `test:hooks` to `check:research`" inside
the merge; staged `mise.dev.toml:117` ≠ `e12cf04` (R5 P2-1). (b) A parent-owned edit was folded
into a lane merge because the sequence was hand-run and the lane retro deferred wiring "to
the parent at integration" (`retros/gate-hooks.md:20`). (c) No runner step "changed paths ⊆
`owned_paths` ∪ records" (R7 C step 3); no commit-message template declaring foreign hunks.
(d) `git diff --cached <lane-tip> --stat` non-empty outside record paths before the commit.
(e) The runner refuses foreign hunks; parent wiring lands as its own commit. → C.

**P2-3 PreToolUse false positive and timeout.** (a) During the review (R7), a read-only
heredoc containing "git merge"/"git push" was blocked ("timed out; blocking because
`onFailure` is block"); `pretooluse_gate.py:23` splits segments on `\n`, `:71-72` regex over the
whole command; the hooks went live through the file watcher at 21:30Z. (b) Matching on text
rather than executed tokens; `onFailure: block`, hook timeout 10 s, `git_gate.py:34`
`GATE_TIMEOUT = 8` per lane, so several lanes can exceed the budget; no deny-with-reason on
timeout (M1: gate runs take 0.2 s; the timeout cause is R7's hypothesis). (c) `test_hooks.py`
(13 tests) has no heredoc/quoted-string fixture and no latency test; the hooks were reviewed
in scratch repos, never replayed against the session's own 113 Bash commands. (d) A fixture
test replaying real session commands through the gate (before `e12cf04`); a hook-error log
grep for "timed out". (e) Token-anchored parsing with heredocs stripped, a per-call budget
below the hook timeout, deny with a reason (CT-02b). → J.

**P2-4 orphan deferral owners.** (a) `retros/team.md:27` and `retros/nav.md:26` → CT-02
whose record excludes `dev/check.py`; `retros/codex-session-history.md:54` → CT-10 (no mask
item); gate rc 0 on all three. (b) `retro_gate.py:58-62` `RESOLVED_OPEN` treats "owner",
"deferred", `#\d+` as closure; `ticket-retro.md:31` says an owner name does not close an
action, but no machine reads ticket bodies. (c) Ticket bodies live in an unpublished manifest;
no retro → ticket cross-check; reviewers accepted the wording. (d) `lane:validate`/
`check:planning`: every retro row naming `CT-nn` must match an item in that ticket's body, at
the retro commit. (e) Deferral rows cite a ticket item id minted by `build_manifests.py`; the
gate refuses unknown ids. → H, G.

**P2-5 network-admission question dropped.** (a) `a73b376a` (rf-env, ~20:1xZ) could not
tell whether `tools:prepare`/`deps:sync` used the network; record `network: none`; reviewer
`a9f0db39` called `deps:check` non-admitted; the parent wrote `retros/rf-env-scrub.md:38`
guidance that exists only in user memory; `implementer.md` has no prep step. (b)
`resource_admissions` has no required `network` key or prep mode; prep commands leave no
offline/online receipt. (c) The parent summarized both reports (class G); no validator;
`AGENTS.md`'s admission rule is prose. (d) `lane:validate` requiring `resource_admissions.network
∈ {none, admitted:<id>}` and `prep_mode`; a `tools:prepare` receipt line with the offline flag.
(e) `lane:allocate --admit network=none` runs prep `--offline` and records rc;
`implementer.md` carries the step. → G, I.

**P2-6 false edges, CT-09 bundle, missing items.** (a) `tickets.preview.json` built
19:57Z (`L1056`); edges CT-08←CT-02, CT-11←CT-01; CT-09 bundles four evaluations; `ultrapowers`
and the Context7/Exa/Firecrawl plugins (Q12) absent; `gh-stack` keep (`L567`) contradicted.
(b) Breakdown shown once and never iterated (P1-6); no decision ledger to diff Q5/Q12 against
ticket bodies; the builder has no "why this edge" field. (c) No review of to-tickets output;
the quiz was the only check and went unanswered. (d) A decisions-file cross-check at manifest
build (settled answers must be cited); `issue:new-edges-audit` dry run on a graph file. (e)
Approval gate (class N) plus the ledger (class E). → N, E.

**P2-7 manifest unpublishable.** (a) `parent_number: 999999`; `build_manifests.py:5-6`
"ten tickets" and a scratchpad drafts path; CT-11 before CT-10; committed `d0d6d4d`
20:58:01Z. (b) Built against a placeholder because the spec was unpublished;
`issue_create.py:96-103` fails only at `inventory()` (network); the builder read from the
scratchpad. (c) `check.py:33-35` validates JSON syntax only; no offline `issue:create-preview`.
(d) A `check` rule for `proposals/**/*.json`: real or `null` parent, unique ids, acyclic in-set
`blocked_by`, docstring count = `len(TICKETS)`, at `d0d6d4d`. (e) The builder refuses
placeholders and repo-external inputs. → N, L.

**P2-8 draft PR nowhere.** (a) Q2c accepted `L567` 19:21:49Z; `M/.../implement-spec/SKILL.md:25`
"open a draft PR after the first merge"; first merge `361688e` 20:00:34Z; no PR since #10.
(b) The decision lived in chat and `claude-takeover.md:11`; the stage was emulated, so its step
list was not followed mechanically; no pending-operations list. (c) No ledger of accepted
operations; Out of Scope covers only merging. (d) A decisions entry `operation: draft-pr`
without a receipt listed by `session:status`/Stop after 20:00Z. (e) The runner prompts the PR
(user-confirmed) after the first publish; `plan:handoff --check` fails on unreceipted
operations. → E.

**P2-9 T4 Phase C has no carrier.** (a) Round-2 Q4 accepted `L666`; Codex `TERMINAL.json`
STOPPED/NOT_COMPLETED, budgets 3/3 (R3); spec Out of Scope deflects; ledger #101 row hides the
budget need. (b) Packet state was read by hand (class M); the spec cites no decision ids; the
ledger row is hand-typed. (c) No packet probe; no decisions file. (d) A packet probe (sweep B)
writing TERMINAL status into `findings.md`; decisions cross-check at spec time. (e) The ledger's
local-state column generated from packet terminal files (`ledger:sync`). → M, E.

**P2-10 "no Codex thread is mid-turn" false.** (a) `claude-takeover.md:7` written ~19:32Z
from the `L321` reading ("ended 13:27 cleanly"); M1's `thread_history_1.sqlite ⋈
thread_spawn_edges` shows eight children failed 14:07:49–14:09:09Z plus `01a128a0` on 10-12;
`findings.md:37-38` and `claude-takeover.md:7` disagree on stop causes. (b) The activation record
is prose from a one-off inspection before the synthesizers reported; the sqlite join was never
run; the record has no field schema. (c) The `codex-session-history` skill was built after the
record and never re-run against it; no regeneration step. (d) The skill's last-turn/children
listing at any time after 19:06Z; `check:planning` comparing record stop causes to the probe.
(e) Activation-record fields generated by a `codex:status` probe; prose only for decisions.
→ M, B.

**P2-10b `/retro` never typed; no retro-writer.** (a) User turns are `T:9,21,567,666,1856`
only; `writing-for-agents` once at `L294` 19:06Z; retro records written by the parent
(`L733,846,990,1338,1447`) and implementers; 0 of 27 agents `retro-writer`. (b) `retro` is
user-invoked (`invocation.md:5,8`); the repo rule (`ticket-retro.md:26-31`) applies findings
directly; the `retro-writer` type was never offered mid-session (class F); docs conflate the
skill with the procedure. (c) No invocation receipt; nothing checks who authored a lane's
retro; nothing tells the user to type `/retro` at a phase boundary. (d) A SubagentStop journal
with no `retro-writer` stops while lanes reach `integrated` → `lane:validate` "retro author
role". (e) `/lane-retro` (CT-06) with `agent: retro-writer`; an advisory Stop reason at phase
end. → D, F.

**P2-11 packet ledger stale; automation ACTIVE.** (a) `lane-ledger.json` names `01a130ef`
at `d2a4103`; `refresh-llvm-github-research` ACTIVE (4 h rrule); nothing in the packet says
superseded. (b) The takeover wrote only repo records; the Codex packet has no supersession
mechanism; the heartbeat was kept by decision (`L567`) with no notice written. (c) No probe
lists ACTIVE automations and packet writers at takeover; Codex automations do not read
`claude-takeover.md`. (d) A `codex:status` listing automations and packet ledgers with writer
thread vs the activation record. (e) The takeover procedure writes a supersession file into
each packet (sweep B) and the probe asserts it. → M.

**P2-12 "Inherited limitations" stale.** (a) `findings.md:15` "Context7 quota exhausted" vs
manifests 05:10Z/05:19Z (ok) and `01a13185` 07:44Z (error). (b) Research-coverage manifests
are JSON on disk; `findings.md` copied prose from `claude-takeover.md:34` instead of the newest
manifests. (c) No task digests manifests; no freshness field. (d) The skill's research-fanout
receipt digest compared to `findings.md` at takeover. (e) "Inherited limitations" generated
with manifest path and timestamp. → M, B.

**P2-13 subagents re-injected up to 15×.** (a) 214 plan frames across 27 transcripts;
`W/scripts/inject-plan.py:848` digest includes `prompt_id`, `:774-776` invalid `prompt_id`
disables the cache (R4 hypothesis, unverified). (b) A plugin cache keyed on host payload
fields; the head-30 view is position-blind (class K), so each frame is 2 KB of mostly
irrelevant prose. (c) `/plan-doctor` never ran; per-agent cost is invisible. (d) `/plan-doctor`
or a transcript digest counting `hook_additional_context` bytes per agent (`/session-review`).
(e) A small smart view plus a structured plan; the upstream fix is outside the repo. → K, A.

**P2-14 lane JSON vs plan table.** (a) `task_plan.md:79-92` rows "planned/allocated/in
progress" vs eight `integrated` records; `stop_gate.py:26` reads JSON only. (b) Two
hand-maintained representations of one state, no generator. (c) No `check:planning`; the
table sits past line 50 and is never injected, so nobody noticed. (d) `check:planning` diffing
the table against records. (e) The table generated by `plan:handoff --write`/`ledger:sync`
(CT-15). → B, K.

**P2-15 hook latency.** (a) `plan-doctor`: shell chain 7,631 ms against a 10 s timeout;
python twin 42 ms; `PWF_TRUSTED_PYTHON` unset. (b) The plugin falls back to the shell chain
when the trusted python is not pinned; the `VIRTUAL_ENV` gotcha can hide `python3`. (c)
Injection going dark is silent. (d) `/plan-doctor` latency line; a SessionStart probe asserting
injection bytes > 0. (e) `PWF_TRUSTED_PYTHON` in the local `env`. → I, K.

**P2-16 two Stop gates.** (a) Repo `stop_gate.py` live since 21:30Z; the plugin's Stop hook
exists (`W/hooks/hooks.json`); `.mode` absent so it is silent today; `gated` would add a second
vocabulary. (b) Two independently authored Stop hooks with no composition rule;
`claude-team.md` does not mention the plugin's gate. (c) No test runs both on one payload; the
combined result is undocumented (R4). (d) A `test:hooks` case running both handlers on a
fixture; `check:planning` asserting `.mode` carries no `gate`. (e) A documented rule and a
committed `.mode = inject-smart` (CT-15). → I.

**P2-17 `base_sha` off by one.** (a) `T:L1553` 20:31:32Z the heredoc evaluated
`$(git rev-parse --short HEAD)` = `e618243`, then the allocate commit `2d1f60e` 20:31:34Z;
same for nav (`c6ff7ef`) and c1 (`ca60871`); retro-gate and team worktrees were cut before
their records were committed. (b) The allocate commit cannot name itself and the convention is
undefined (`planning-records.md:7` lists `base_sha` without a definition). (c) No
`lane:allocate`; no validator comparing `base_sha` with git; the TEAM reviewer flagged it
(`L1231`) and it was deferred. (d) `lane:validate`: `base_sha` equals the parent of the first
lane commit (or the allocate commit, per convention), at the first lane commit. (e)
`lane:allocate` writes `base_sha` and `allocated_from` from git after the commit (CT-17). → B.

**P2-18 pre-merge settings backup only ephemeral.** (a) Fork step 1 (`L2009`) copied the
untracked file to the session scratchpad; the review copied it into `RV/` (untracked). (b)
The brief named the scratchpad; no rule says where pre-mutation backups of untracked config
go; `.gitignore` is frozen so no ignored project path exists. (c) Nobody modelled `git merge
--abort` before the fork; no runner snapshot step. (d) A runner preflight listing untracked
files the merge will overwrite. (e) Snapshots under `<git-common-dir>/claude-lanes/snapshots/`
(durable, untracked) with a SHA receipt. → L, C.

**P2-19 Window A died before approval; handoff schedules `/clear`.** (a) Grill 19:07–19:30Z;
spec and quiz 19:56Z at ctx 660 K; the build started in the same window; death 21:30Z;
`task_plan.md:22-24` puts to-tickets approval after `/clear`. (b) `M/.../ask-matt:38` and
`PHASE-BOUNDARIES.md` (~150 K smart zone, no `/clear` between grill and tickets) are advisory
text; ctx was already 460 K at 19:14Z after Codex forensics (≈79 K tokens in the parent, R7
P14) before grilling finished. (c) No budget signal (class A); no phase-boundary decision
recorded; nothing stops a build in Window A. (d) A UserPromptSubmit hook printing context % (from
the transcript) and the current phase. (e) Forensics in subagents by rule (the skill now
exists); a phase-boundary checklist in `plan:handoff`. → A, D.

**P2-20 no final `code-review`; no cleanup; standards file absent from the re-review brief.**
(a) `NEXT` ends at "publish"; eight worktrees remain; `L1962` 21:02:01Z re-review brief omits
`CODING_STANDARDS.md` (landed `fa892d2` 20:56:18Z). (b) `implement-spec` steps 7–9 were
emulated by hand; the brief was composed six minutes after the file landed; `reviewer.md:18`
still says "arrives with CT-04" (role file not updated when CT-04 landed). (c) No `lane:brief`
slot; no `plan:handoff --check` for outstanding stage steps; lane records have no removal
field. (d) `check:planning`: `published` ⇒ worktree removed or a `holds` reason; a brief lint
(cite `CODING_STANDARDS.md` once it exists). (e) `lane:brief --role reviewer` emits the slot;
`lane:integrate` schedules cleanup; the spec-level review is a plan phase. → F, C.

**P2-21 setup drift accepted as "already fully set up".** (a) `T0:152` 18:39:23Z, one
read-only Bash (`T0:179`), "already fully set up" at `T0:199` (17 s); `issue-tracker.md` lacks
the seed headings, the PR flag and the Wayfinding block. (b) The setup skill checks whether
prior output exists (`setup SKILL.md:21-27`), not equivalence to the seeds; the repo file is
Codex-authored; the workflow skills grep for seed phrases (R1). (c) No seed-drift check; no
setup row in `skill-invocations.md`; nothing records which seed version the docs derive from.
(d) A `check` rule: `docs/agents/issue-tracker.md` contains the installed seed's required
headings (seed SHA recorded). (e) Record the seed SHA in the doc; SessionStart notice when the
plugin cache version differs from the recorded one. → D, I.

**P2-22 unverified claim in a gate-passing record; P3s relabelled or dropped.** (a) Staged
`retros/gate-hooks.md:6,13` "hk 2.6.0 and 2.5.0" (implementer-written) vs reviewer "Not run:
2.5.0"; `L1908` 20:55:40Z the parent relabelled P3-2/3 as "add tests", dropped P3-5; the
re-review P3 and the implementer's two side effects are in no record. (b) The retro was written
by the implementer about its own work before review; `retro_gate.py:50-54` accepts "rc 0"
strings; the parent condensed the reviewer's report into a SendMessage; no journal. (c) No
receipt file for `hk validate` runs; the reviewer's "Not run" list is never merged
mechanically. (d) SubagentStop journal + `lane:validate` "every P-n in the reviewer's final
report has a disposition in the retro", at 21:04Z. (e) `/lane-retro` with the retro-writer
reading the journal; named-check claims require a receipt path (`ledger-append` with rc). → G, H.

**P2-23 briefs restate; definitions unused.** (a) 17 briefs of 3.5–6.8 KB, 55 % boilerplate
(R7 P9); 0 of 17 project agent types. (b) Class F (agent list frozen at session start) and no
`lane:brief`; tickets were unpublished so there was nothing to point at (P1-6). (c) No brief
lint or size cap. (d) PreToolUse(Agent) measuring prompt size and `subagent_type`. (e)
`lane:brief` + slotted agents (CT-19). → F.

**P2-24 worktree census wrong; `.agent/` untracked and unexcluded.** (a) `findings.md` says
three dirty Codex worktrees; git says 11 of 18; `codex/28|29-offline-refresh` unrecorded;
`.agent/` is `??` and `.git/info/exclude` lists only `.claude/worktrees/` and
`settings.local.json`. (b) Worktree state was summarized by hand at takeover; `.gitignore` is
frozen and the exclude file is per-clone with no generator; branches were not diffed against
records. (c) No `session:status`/`codex:status` listing dirtiness and unmerged branches. (d)
`session:status` rows per worktree. (e) The takeover step generates the worktree table into
`findings.md`; the exclude list is managed by a task. → M, B, L.

**P2-25 brief items lost (ticket 30, attachments, `additionalDirectories`, research
branches).** (a) Synthesizer briefs (19:1x–19:2xZ) carried items the parent never recorded (R6
rows 1, 4); `additionalDirectories` top-level is undocumented; the wayfinder branch rule is
absent from `issue-tracker.md`. (b) Class G: four ≈850-word briefs condensed into
`findings.md:37-43`; the briefs lived in the scratchpad; no item ids. (c) No receipt journal;
no brief → record diff. (d) `/session-review` diffing subagent final reports against records
(this review did it by hand). (e) Synthesizers write tracked `P/codex-briefs/<thread>.md` with
item ids and the record points at them. → G, L.

## Root-cause classes

| Id | Class | Findings explained | System property at fault (where the rule lives or is missing) |
|---|---|---|---|
| A | Context budget blind: no signal, no compaction, forks inherit a full window | P1-1, P2-19, P2-13 | `~/.claude/settings.json` and `~/.claude.json` `autoCompactEnabled: false` (0 `PreCompact` fires, 3 "Prompt is too long"); harness prompt `T:L42` "you don't need to wrap up early"; `Agent(fork)` starts at the parent's ctx (`a22113b3` 970,507); no PreToolUse matcher for `Agent` in the staged `.claude/settings.json`; no statusline/hook reads `transcript_path` usage; `PHASE-BOUNDARIES.md` smart zone is advisory |
| B | Records derived by hand, never from git/tracker/gate | P1-1, P1-4, P1-9, P1-13, P2-10, P2-12, P2-14, P2-17, P2-24 | `.claude/rules/planning-records.md:7` lists fields with no derivation or validator; "a lane changes only its own `status`" vs 22 parent heredoc patches (R7 P1); no `lane:*`/`plan:*`/`ledger:*` task in `mise.dev.toml`; `stop_gate.py:27` trusts the typed field; handoff prose in `task_plan.md:14-30` |
| C | Integration sequence non-resumable; gate bypass by merge form; ordering constraints unwritten | P1-1, P1-3, P2-1, P2-2, P2-18, P2-20 | No `lane:integrate`; `claude-team.md:35` names the receipt, not the procedure; `:55-61` warns that `--no-commit` skips `pre-merge-commit` but nothing forbids it; `pretooluse_gate.py:45` verbs `{merge, push}` only; `hooks:install` (`mise.dev.toml:340-343`) has no precondition and no test with `git_delivery` |
| D | User-invoked skills emulated and misrecorded; no invocation receipt; stage rules advisory | P1-7, P1-8, P2-10b, P2-19, P2-21 | `M/.agents/invocation.md:5,8,22` vs `ticket-retro.md:4-8`, `claude-takeover.md:11`, `issue-tracker.md:10` (stage order without the typed-by-user condition); harness expands slash commands only at the prompt head (`T:L21` vs `T0:128`); `skill-invocations.md` hand-written; setup skill checks existence, not seed equivalence |
| E | No ledger of user requests, decisions and pending operations; approval assumed | P1-6, P1-8, P1-9, P2-6, P2-8, P2-9 | No file holds requests/decisions with ids; `task_plan.md:22-25` "Pending user decisions" prose; harness turns a rejected slash command into system lines (`T:L565-566`); bulk "yes to all" has no per-item record; `lanes/*.json` `tickets[]` free text |
| F | Agent roles and briefs not machine-sourced; harness agent list frozen at session start | P1-12, P2-10b, P2-20, P2-23 | "Available agent types" only at `T:L25/L46` (18:54Z); `.claude/agents/*.md` landed 20:07–20:25Z and were never offered; `implementer.md:8-9` preload unreachable; `reviewer.md:18` stale; no `lane:brief`; 17 hand-written briefs |
| G | Subagent reports condensed by the parent; no machine receipt | P1-2, P1-4, P2-4, P2-5, P2-22, P2-25 | `subagent_stop_gate.py:24-30` gates only lane-worktree retros and writes nothing; task outputs under the ephemeral `…/9fde3ed2…/tasks/<id>.output`; the parent re-types dispositions into records and SendMessages (`T:L1908`) |
| H | Shape-checked gates mistaken for truth | P1-5, P1-10, P1-13, P2-4, P2-22 | `retro_gate.py:50-54` (`EVIDENCE` regex), `:58-62` (`RESOLVED_OPEN` "owner"), `:185` unit → path with no cross-check at `retro: passed`; `check.py:72` discovery list; `dev-tests.md:8` unenforced; `test_codex_examples.py:105-106` patches the pinned path |
| I | Configuration composition and cross-tool contracts unvalidated | P1-2, P1-3, P2-5, P2-15, P2-16, P2-21 | `.claude/AGENTS.md:7` has no key list; no settings schema check; `git_delivery.py:49-71` vs `mise.dev.toml:343`; plugin Stop (`W/hooks/hooks.json`) vs repo Stop; pins in prose (`task_plan.md:10`) not `env`; `resource_admissions` has no required keys; seed version unrecorded |
| J | Gate hooks without a real-command corpus or a latency contract | P2-3 | `pretooluse_gate.py:23,71-72`; `git_gate.py:34` `GATE_TIMEOUT = 8` per lane vs hook timeout 10 s; `onFailure: block` with no deny-reason path; `test_hooks.py` has no heredoc or latency case |
| K | Planning files unstructured for the plugin; progress by append; no host pin | P1-11, P2-13, P2-14, P2-15 | `task_plan.md` 0 `### Phase`; `planning-records.md:9` append-only; `W/scripts/inject-plan.py:92,1275-1277` limits; no `check:planning`; `PWF_PLAN_ROOT`/`PLAN_ID`/`PWF_TRUSTED_PYTHON` absent from settings `env` |
| L | Outputs in ephemeral or untracked locations | P1-10, P2-7, P2-18, P2-24, P2-25 | Briefs, drafts, backups and task outputs in the session scratchpad (`00-evidence-index.md:17-20`); `.gitignore` frozen (baseline) so no ignored project dir exists; `2a14` evidence untracked; `.agent/` unexcluded |
| M | Codex thread/packet state imported by hand | P2-9, P2-10, P2-11, P2-12, P2-24 | `claude-takeover.md:5-13` prose written before the synthesizers reported; no `codex:status` probe (sqlite, `automation.toml`, manifests, packet ledgers); the `codex-session-history` skill was built after the record; packets have no supersession file |
| N | Ticket pipeline unvalidated before build | P1-6, P2-6, P2-7 | `build_manifests.py` placeholder parent and scratchpad input; `check.py:33` JSON syntax only; no offline `issue:create-preview`; the to-tickets quiz is not a gate; allocation does not resolve ticket ids |

Fourteen classes. Candidates from the brief that merged rather than stood alone: "serialized
named checks raced" (R7) has no P1/P2 finding of its own and sits under C/I (CT-11 covers it);
"worktrees without plan pinning" is K; "publish/hook ordering" is C+I; "retro gate checks shape
not truth" is H; "outputs in scratchpads" is L.

## Invariants per class

Each invariant is a predicate over repo, git, tracker or session state; the observation point
is the cheapest place that can evaluate it with the inputs it needs.

| Class | Invariant (checkable predicate) | Cheapest observation point |
|---|---|---|
| A | `ctx(last assistant usage in transcript_path) < T_fork` for every `Agent` call with `subagent_type: fork`; `ctx < T_warn` or the turn's output names the phase boundary; `autoCompactEnabled ≠ false` or a repo rule records the reason | **PreToolUse** matcher `Agent` (deny fork over threshold, read `transcript_path`); **UserPromptSubmit** (print ctx % line); **SessionStart** (warn when auto-compact is off); statusline (if the CLI exposes `context_window`, unverified) |
| B | For every `lanes/*.json`: `base_sha` = parent of the first lane commit (or `allocated_from` + allocation commit); `status` prefix ∈ vocabulary; `retro == "passed"` ⇒ `retro_gate.py --unit <unit>` rc 0 on the tree; `"published"` ∈ status ⇒ `integration_merge` is an ancestor of `origin/<branch>`; the plan's Lanes table = `lanes/*.json` projection; handoff base = `HEAD` or remote | mise `lane:validate` inside `check`; **PostToolUse** matcher `Write\|Edit` on `lanes/*.json`; hk `pre-commit` step; **Stop** (reuse `stop_gate.py`) |
| C | `MERGE_HEAD` absent at every Stop and SessionStart (or a runner receipt names `--continue`); every merge commit on the integration branch has two parents and a runner receipt; no Bash command on the integration branch contains a `git merge … --no-commit` token; `hooks_installed ⇒ delivery:inspect-hooks` passes; changed paths of a lane merge ⊆ `owned_paths ∪ {lanes/<u>.json, retros/<u>.md}` | **PreToolUse** `Bash` (token-anchored `--no-commit` deny); **SessionStart** `session:status` line; mise `lane:integrate` preflight; `test:hooks` case install × inspect-hooks |
| D | No line in `docs/agents/*.md` matches `standing authorization\|invocation authority`; every `skill-invocations` row with mode `typed`/`native` has a harness event; `docs/agents/issue-tracker.md` contains the installed seed's headings and records the seed SHA | mise `check:planning` (grep + seed-hash rule) in `check`; **UserPromptSubmit**/**PostToolUse** `Skill` appending `skill-invocations.jsonl`; **SessionStart** notice when plugin cache version ≠ recorded |
| E | Every user-originated text (incl. rejected commands) has a row in `P/requests-<session>.jsonl`; every row is cited (spec/ticket/decision id) or explicitly declined before to-spec closes; every `decision.kind == operation` has a receipt before `plan:handoff --check` passes; `lanes/*.json tickets[]` ⊆ approved ids | **UserPromptSubmit** hook (append); mise `check:planning`; **Stop** (list unreceipted operations as the reason once); `lane:allocate` |
| F | Every lane `Agent` call uses `subagent_type ∈ {implementer, doc-writer, reviewer, retro-writer}`; an implementer transcript contains `Skill(tdd)` before its first `.py` Write; the set of `.claude/agents/*.md` equals the agent list the session was offered; brief ≤ 1.5 KB of pointers | **PreToolUse** matcher `Agent` (deny `general-purpose` with a `LANE-UNIT:` marker; size cap); **SubagentStop** (transcript scan); **SessionStart** (agents on disk vs offered → "restart" notice) |
| G | Every SubagentStop of a lane role appends `{agent_id, agent_type, transcript_path, last_assistant_message[:4000], tip}` to `<git-common-dir>/claude-lanes/<unit>.jsonl`; `lanes/<u>.json review` equals the journal's last reviewer disposition; every `P-n` in a reviewer's final report has a retro row | **SubagentStop** hook (journal; matcher `implementer\|doc-writer\|reviewer\|retro-writer`); mise `lane:validate --from-journal`; retro gate cross-check |
| H | Every `dev/test_*.py` is wired (`check.py` discovery or a `test:*` task in `check:research` depends); `retros/<unit>.md` exists for every `lanes/<unit>.json` with `retro: passed`; every deferral row's `CT-nn` has a matching item in that ticket's body; every `ROOT/"evidence/…"` constant with a pinned SHA resolves to a tracked file with that SHA; a named-check claim (`rc 0`, `hk validate`) in a retro has a receipt line | mise `check` (new rules in `dev/check.py`); `retro_gate.py` (owner → item cross-check, unit → path check); CI |
| I | `keys(.claude/settings.json) ⊆ {$schema, hooks, enabledPlugins, extraKnownMarketplaces, env}` and every project plugin's marketplace is declared there; `hooks:install` ⇒ `git_delivery.safe_configured_hooks` accepts the resulting config; `P/.mode` has no `gate`; `env` carries `PLAN_ID`, `PWF_PLAN_ROOT`, `PWF_TRUSTED_PYTHON`; `resource_admissions.network` present in every lane record | mise `check` (settings schema, CT-16); `test:hooks` install × inspect case; **PostToolUse** on `.claude/settings*.json`; `lane:validate` |
| J | For a corpus of real session Bash commands, the gate denies exactly the real `git merge\|push`/`delivery:publish` segments; gate wall time per call < hook timeout − margin, else it emits `deny` with a reason | `test:hooks` (corpus fixture + latency assertion); **PreToolUse** self-timing |
| K | `task_plan.md` has `## Goal`, `## Next Step`, `## Current Phase`, exactly one `in_progress` `### Phase`; `size(progress.md) < 900 KB`; `check-complete.sh` exits with "in progress (k/n)"; from a lane worktree the pretool view shows the root nonce | mise `check:planning` (CT-15); **SessionStart** probe of injected bytes; `/plan-doctor` |
| L | Every artifact a record cites resolves to a tracked path, a path under `<git-common-dir>/claude-lanes/`, or a `~/.codex` path with a recorded SHA; no record cites `/private/tmp` or `scratchpad`; untracked top-level dirs are tracked, excluded or listed with a reason | mise `check:planning` (citation resolver); `session:status` (untracked top-level list) |
| M | Activation-record fields (thread last-turn status, failed children, ACTIVE automations, packet writer thread, newest manifest statuses) equal the output of `codex:status`; each packet the takeover supersedes holds a supersession file | mise `codex:status` (from the `codex-session-history` scripts) at takeover and **SessionStart**; `check:planning` field compare |
| N | `proposals/**/tickets*.json` has a real or `null` parent, unique ids, acyclic in-set edges, builder count = ticket count; `lanes/*.json tickets[]` resolve to tracker issues or approved ids | mise `check` (proposal validator); `lane:allocate` refusal; `issue:create-preview` dry run |

## Coverage matrix

| Finding | Classes (primary first) | Finding | Classes (primary first) |
|---|---|---|---|
| P1-1 | A, C, B | P2-8 | E |
| P1-2 | I, G | P2-9 | M, E |
| P1-3 | I, C | P2-10 | M, B |
| P1-4 | G, B | P2-10b | D, F |
| P1-5 | H | P2-11 | M |
| P1-6 | E, N | P2-12 | M, B |
| P1-7 | D | P2-13 | K, A |
| P1-8 | E, D | P2-14 | B, K |
| P1-9 | E, B | P2-15 | I, K |
| P1-10 | L, H | P2-16 | I |
| P1-11 | K | P2-17 | B |
| P1-12 | F | P2-18 | L, C |
| P1-13 | H, B | P2-19 | A, D |
| P2-1 | C | P2-20 | F, C |
| P2-2 | C | P2-21 | D, I |
| P2-3 | J | P2-22 | G, H |
| P2-4 | H, G | P2-23 | F |
| P2-5 | G, I | P2-24 | M, B, L |
| P2-6 | N, E | P2-25 | G, L |
| P2-7 | N, L | | |

Findings per class (all mappings counted): B 9; C 6; E 6; G 6; I 6; D 5; H 5; L 5; M 5; F 4;
K 4; A 3; N 3; J 1. Every finding maps to at least one class.

Findings whose cause is only partly systemic: **P2-13** rests on an unverified upstream plugin
hypothesis (`prompt_id` in the cache digest); the repo-side cause (K) only bounds the damage.
**P2-3**'s false positive is systemic (J); its *timeout* half is R7's hypothesis, not reproduced
(M1: 0.2 s runs). **P2-12** is ordinary staleness, systemic only in that nothing regenerates the
section (M, B). No finding is a pure one-off: each has a rule, tool or configuration that let it
happen and nothing that would have caught it.

## Already addressed and remaining gaps

Tickets per SYNTHESIS §6 (unified numbering), existing code per the staged `e12cf04` tree.

| Class | Covered by | What the coverage does | Gap that remains |
|---|---|---|---|
| A | nothing | — | No ticket touches context budget. Needed: a PreToolUse rule for `Agent` forks over a threshold (reads `transcript_path` usage), a UserPromptSubmit ctx line, a documented decision on `autoCompactEnabled: false` (user setting; record it in `docs/agents/claude-team.md` or turn it on), and a rule that Codex forensics run in subagents. R8's "cap wave 1 at three" (D5) is adjacent, not this. |
| B | CT-05 (`lane:set`/`lane:validate`, `retro` derived, `ledger:sync`), CT-17 (`lane:allocate` records `base_sha` + `allocated_from`, `session:status`), CT-15 (`plan:handoff --check`, Lanes table regenerated); `stop_gate.py` reads the field | Derivation and validation of lane fields, ledger and handoff | `published ⇒ ancestor of origin` and `integration_merge` checks are not in any acceptance list; the one-time corrections (§4) are runbook steps; `stop_gate.py` keeps trusting `retro` until CT-05 derives it. |
| C | CT-17 (`lane:integrate [--continue\|--abort]`, preflight, allowlist check), CT-18 (`publish-batch` refuses `MERGE_HEAD`), CT-02b (reconcile `hooks:install` with `git_delivery`), CT-11 (check lock); `git_gate.py` gates merge/push once installed | Resumable integration; publish ordering; hook reconciliation | No PreToolUse deny of `--no-commit` (CT-02b lists token-anchored matching, not this verb rule); `claude-team.md` merge rule is a runbook doc edit (D15), not a check; `session:status` SessionStart line is "optional" in R7 J, make it mandatory; untracked-file snapshot (P2-18) is in no ticket. |
| D | D15 wording rewrites (runbook step 7); CT-06 `/lane-retro`; RETRO row (`issue-tracker.md:10` states the typed-by-user condition) | Removes the false wording | No machine source for `skill-invocations.md` (hook-appended jsonl); no seed-drift check for `/setup` output (P2-21 is "user re-runs setup"); the grep in the RETRO row is a one-time verification, not a `check` rule. |
| E | CT-13 (the one lost request); CT-19 retro-writer brief "user requests received this session" table (RETRO row); D20 operations on the user's word | Recovers specific items | No request/decision ledger file, no hook that captures rejected slash commands (`T:L566` shape), no `operation` receipts check, no approval gate at allocation. The retro-writer table is post-hoc and per lane, not per session request. |
| F | CT-19 (`lane:brief`, constants into `.claude/agents/*.md`, `tdd` preload, receipt journal); CODING_STANDARDS reviewer rule "red test before code" (RETRO row); R7 guardrail "no `isolation: worktree`" | Correct dispatch inputs | Nothing addresses the harness property that agent types are enumerated at session start: CT-19 needs a SessionStart check (agents on disk vs offered) and a documented "restart after `.claude/agents` changes" rule; no SubagentStop scan for `Skill(tdd)`; `reviewer.md:18` stale text is in no correction row. |
| G | CT-19 (SubagentStop receipt journal, `lane:set --from-journal`); CT-05 (mechanical owner cross-check "belongs to CT-05's validator", RETRO row); CT-20 (`/session-review`, after the fact) | Receipts survive context death | Journal is blocked by CT-02 integration; the reviewer-P-n → retro-row cross-check is named in no acceptance list; synthesizer/brief outputs (P2-25) still go to the scratchpad; "not re-merged" is only a `session:status` drift string. |
| H | CT-12 (unwired-test rule, `test:retro-gate`, line-cap and pointer checks; `retro_record` alias routed here); `retro_gate.py` itself | Closes the live wiring gap and the a06 alias | No rule for pinned data paths (P1-10 goes to "A06 residual" wave 4 with no acceptance text); retro claims of named-check runs still need no receipt; the deferral → ticket-item check depends on CT-05 and an item-id scheme nobody has specified. |
| I | CT-16 (settings composition check), CT-02b (`hooks:install` × delivery), CT-15 (`.mode`, pins in `env`, two-gate doc), CT-05 (`resource_admissions.network`) | Composition rules become checks | CT-16 is gated on D4 and CT-02; "every project plugin's marketplace declared" and the undocumented `additionalDirectories` are user decisions (D4) with no check; `hooks:install` × `inspect-hooks` is "reconcile", not "test both in one scratch repo"; seed-version pin absent. |
| J | CT-02b (token-anchored matching, heredoc strip, deny-with-reason on timeout, `test_hooks.py` cases) | Fixes the observed false positive | No replay corpus of real commands (the transcript holds 113); `/usr/bin/git`, cherry-pick/rebase/pull bypasses (reviewer P3-2) are only in §4's correction row; per-lane `GATE_TIMEOUT` × lanes vs hook timeout arithmetic is not an acceptance item. |
| K | CT-15 (`check:planning`, `plan:log`, skeleton, archive, smart view); runbook step 9 migration | Plan readable by the plugin | Pins reach hooks only if settings `env` propagates (unverified, R4); `progress.md` cap is `plan:log`'s refusal, not a `check` rule; subagent re-injection cause is upstream. |
| L | Runbook step 10 (persist the review), `.git/info/exclude` additions, R3 sweep A (inventory), CT-19 journal under the git common dir | Moves known artifacts in | No rule that records may not cite scratchpad paths; no durable default for briefs/backups/drafts; `2a14` data import has no acceptance text; `.gitignore` is frozen until CT-08 (D6). |
| M | R3 sweep briefs A/B/C (operations, D11); CT-10 (brief composer, coverage); `claude-takeover.md`/`findings.md` corrections (runbook step 7) | One-time repair | No `codex:status` probe task; no supersession-file convention for packets; the 2026-10-19 Codex resume still reads a stale packet ledger unless sweep B lands. |
| N | R2 "Publication fixes" 2–5 and runbook step 11 (rebuild manifest, graph file, create order) | Makes this manifest publishable | No offline validator in `check` for `proposals/**/*.json`; `lane:allocate` (CT-17) does not list "refuse unresolved ticket ids"; to-tickets approval has no machine token. |

Classes with no ticket at all: **A** and **N**; classes covered only by one-time operations:
**D** (wording), **L**, **M**. Classes where the ticket exists but the acceptance text misses the
cause: **C** (no `--no-commit` rule), **F** (agent list at session start), **G** (reviewer
P-n cross-check), **H** (pinned data, receipts for claims), **J** (corpus).

## Could not verify

- Whether Claude Code 2.1.296 exposes context usage to a statusline or hook (the `transcript_path`
  route relies on the `usage` fields present in this JSONL; a `context_window` statusline field
  is not confirmed from docs). The `autoCompactEnabled: false` values are read from the two
  files; whether the user set them deliberately and whether a 1 M window would have compacted
  at ~977 K with the flag on was not tested.
- Why the session was never offered the project agent types: the transcript shows the list only
  at `L25/L46` and no later refresh; whether the CLI hot-reloads `.claude/agents` in some
  versions or on `/reload-*` is not established (the review session, started later, lists them).
- Whether the harness would have expanded `/mattpocock-skills:grill-with-docs` typed alone in
  this session (inferred from `T0:128/153` per R1, not reproduced).
- R4's `prompt_id` hypothesis (P2-13) and the shell-chain latency figure (taken from R4).
- R7's PreToolUse timeout cause (P2-3); M1 and R5 measured 0.2 s gate runs; I did not feed the
  live hook a heredoc during the merge.
- `hooks:install` × A09 (P1-3) remains the R5/M1 inference from `hk install --help` and
  `git_delivery.py:49-71`; not run.
- Whether `tools:prepare`/`deps:sync` reached the network (P2-5); no receipt exists.
- Settings `env` propagation to hook processes (class K/I invariants assume it; R4 could not
  confirm).
- R3, R8, D1 and D2 were read only through SYNTHESIS/M1/R-report citations; the Codex sqlite
  joins (P2-10) are M1's, not re-run here.
- The 26-vs-24 P2 count: SYNTHESIS §2's count line and table disagree; I used the table.

# CL2: why requests get lost across compaction, /clear, handoffs and subagents (mechanism review)

Team CL, architect row (Fable 5.1), 2026-10-14. Read-only review of session `ccm-20261014`
(`ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34`, Opus 5.5) and the mechanisms this repository built to
survive context compaction. Case study: the user's `/claude-agent` intake-skill request (D114, D119),
still unbuilt at 18:56Z when the user raised it (D160).

Notation. `T:L<n>` = line `n` of the parent transcript
`~/.claude/projects/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34.jsonl`
(9,210 lines; 110 user turns; 24 AskUserQuestion answers; 72 subagent transcripts under the sibling
`subagents/` folder). `S1`, `S2`, `S3` = the three compaction summaries (`isCompactSummary`) at
`T:L2449` (10:04:10Z, 12,257 chars), `T:L5036` (13:45:19Z, 14,073 chars), `T:L7356` (16:52:21Z,
13,507 chars); line numbers inside a summary refer to the summary text. P = the plan directory.
MP = this repository. TR = the private project (codename only, D144). Timestamps are UTC.

## 1. Verdict: ranked root causes

**RC1 (primary). An accepted decision that creates work has no projection, and every carry-over
mechanism reads only projections.** D114 (intake skill, DL-144, 13:58:46Z) and D119 ("build CT-59
now", DL-151, 14:04:07Z) exist only as `decision` rows and Decisions-table rows
(`P/decisions.jsonl:144,151`; `P/task_plan.md:737,742`). Neither produced a task_plan item, a
ticket-ledger change, a lane record or a ledger `operation` row: the CT-59 ledger row still reads
"held · spec publication (D59)" (`P/ticket-ledger.md:190`; `P/task_plan.md:544`), `P/lanes/` has
no ct59 record, and `plan_decide.pending()` returns only `DL-4`. The handoff generator derives
"pending operations" from receipt-less `operation` rows only (`dev/handoff.py:270-283`), its only
decision check `H.pending-decision-unlisted` covers operations only (`dev/handoff.py:558-561`),
and the "Pending user" line is hand-typed in the template
(`.claude/skills/session-handoff/references/handoff-template.md`, `## pending-user`). The X3
zero-loss predicate was designed the same way: `S.decision-pending-unlisted` compares
`plan_decide.py pending` ids (operations) with the handoff line
(`P/reviews/ccm-20261013/phase4-prep/X3-session-restart-automation.md` §2 table). So the rev-13
`## Next Step` block (`P/task_plan.md:10-25`), the NEXT bullet (`P/progress.md` tail), the pwf
injection (which injects that block), the session-resume extractor and `handoff.py check` (rc 0)
all pass while the user's request is absent. The 2026-10-13 review already named this hole as
class E, "No ledger of user requests, decisions and pending operations"
(`P/reviews/ccm-20261013/prevention/C1-root-causes.md:459-483`); the fix gave decisions ids but
no lifecycle to done.

**RC2. Auto-compaction replaced the designed checkpoint-then-/clear path, and the compaction
summarizer demotes "do now" decisions to history.** All three compactions fired at 663-666K
context tokens (last assistant `usage` before each: `T:L2418` 663,386; `T:L5020` 663,132;
`T:L7329` 665,986), above the table's 650K "hard" line, with the handoff stale at two of them
(S2 line 8 "rev 12 ... stale"; S3 line 15 "stale at rev 12"). No MP hook fired at any compaction:
the doctor SessionStart entry entered the main checkout's `.claude/settings.json` at commit
`1dfefa3` (17:08:50Z), after S3, and the transcript holds 0 `[doctor]` blocks and 0 PreCompact
entries (hook histogram: 3 `SessionStart:compact` successes, all planning-with-files,
`T:L2467`, `T:L5053`, `T:L7369`). The summary itself carries Claude Code's instruction "Continue
... without asking the user any further questions ... do not recap" and "The summary was written
without seeing [the most recent messages]" (S1 lines 110-112, same in S2/S3). S3 then filed D114
and D119 under "Decisions this segment" (lines 79, 83) while "Other open items" listed only
"CT-59 forks F1/F2 and the team acceptance" (line 121) under a "Current critical task: history
replacement" (line 31). After S3 the parent worked that list and never returned to D119 (no
AskUserQuestion about the team after 16:52Z: only `T:L7531`, `T:L8414`, `T:L8858`).

**RC3. Context-budget enforcement exists only on paper, and /clear is a user-typed action the
design cannot force.** `docs/agents/claude-team.md:116-133` sets warn 400K, fork_deny 500K,
checkpoint 550K then `/clear`, hard 650K, and says the enforcing hooks "arrive with ticket CT-23
... until then the parent applies the table itself". CT-23's `prompt_hook`, `agent_gate` and
`dev/context_budget.py` were never created (A2 design rows A2-13, A2-14: "planned ... never
created", `P/reviews/ccm-20261014/project-import/A2-typescript-mods-library.md:350-351`), lane
w0-session-hooks was cancelled (D97), and the replacement mods sit at waves 22, 24, 26, "not
allocated" (`P/ticket-ledger.md:154`). No mod exists on disk (no `~/.claude/mods`, no
`hooks/register.ts` in MP outside `offline/research/` mirrors). The parent crossed 550K at
08:48:14Z (`T:L1937`), 12:58:56Z (`T:L4574`) and 15:47:11Z (`T:L6795`), ran `/session-handoff`
once (rev 10, `T:L1966`, 08:48Z), and never saw a `/clear`: the 110 user turns contain no
`/clear` command, although the user had said "run /session-handoff and i will run /clear"
(`T:L130`, 06:18Z) and then kept sending work (`T:L332`, `T:L1118`, `T:L2125`, `T:L2379`). At
19:01Z the parent is at 447,275 tokens again (`T:L9235`), above warn, with no checkpoint.

**RC4. Free-text and unanswered AskUserQuestion answers carry requests that the hand conversion
to decisions drops.** Q86 (`T:L5218`) asked for three things: an intake skill made with
/skill-creator, agents that keep reprioritization history and per-ticket duration and context
"so we can understand trends", and a visual artifact of lanes, queue, predicted lane and backlog
completion; D114 kept the words, S3 line 79 kept "(pending)", no item kept the deliverables. Q90
(`T:L5372`) "build CT-59 now" became D119, a Plan-agent design (`T:L5413`, saved `T:L5644` to
`P/reviews/ccm-20261014/ct59/CT59-design.md`, "11 units and nine open forks", `T:L5553`), then
Q97/Q98 (`T:L5663`) and Q107 (`T:L6163`) were answered "(no option selected)" with a request for
more research, Q110 (`T:L6267`) asked for a different report format (D137), R12b ran, and the
"accept the team" question was never re-asked. Q106's "if the claude-agent team is available have
it just build the p2996 llvm tools now" and Q107's "launchd schedule that triggers the
claude-agent skill/team" survive only as clauses of D133 and D138. At `T:L8415` (17:41Z) the user
wrote "run /claude-agent skill team if it has been completed"; the parent checked (`T:L8430`),
recorded D153 "no claude-agent skill exists yet" (`T:L8469`) and did not re-open D119. At
`T:L9119` (18:51Z) "i installed /skill-creator to fix this issue ... outside of main context" was
read as the Antigravity-history skill of D153 (`T:L9136`, `T:L9138`), because that was the most
recent "skill-creator" item in the post-S3 context; the user corrected it at `T:L9161`, and the
parent agreed it "never became a task_plan item or a ticket" (`T:L9201`).

**RC5. Subagent briefs carry unit scope, never the parent's open-request list, so no subagent can
notice a dropped request.** Of 72 briefs, 11 mention CT-59, D114, D119 or "intake"; between S3
(16:52Z) and the complaint (18:56Z) the parent dispatched R17-R22, the scanner-betterleaks
implementer and the agy-history builder (`subagent-briefs` index: 17:44Z-18:51Z) and none mention
them (R20's and agy-history's "skill-creator" hits are the Antigravity skill). No fork was used
this session (agentType counts: general-purpose 65, reviewer 3, implementer 2, doc-writer 2,
Explore 2, retro-writer 1, extractor 1, claude-code-guide 1, Plan 1), so fork inheritance played
no part here; the 2026-10-13 fork death (C1 class A) is the reason D21 exists.

**RC6 (secondary). The planning-with-files channel re-injects the hole.** The plugin runs in legacy
mode: no `P/.mode`, no `PWF_INJECT` in either settings `env` (project `env` holds `PLAN_ID` only;
local `env` holds the plan root and trusted Python pins), so SessionStart and UserPromptSubmit
inject the first 50 lines of `task_plan.md` and the last 20 of `progress.md`
(`.../planning-with-files/3.24.0/scripts/inject-plan.py:1321,1330`), PreToolUse the first 30
(`:1248`, the 2,084-byte truncated frame this review itself received). Those lines are the
handoff-generated `## Next Step`, so they contain exactly what `handoff.py` derives. The standing
P3 `H.mode-not-inject-smart` (S1 line 68, S2 line 8) belongs to CT-30, "not allocated"
(`P/ticket-ledger.md:160`), and the memory note "pwf inject-smart only" describes a state that
does not exist on disk.

## 2. Per-mechanism findings

| Mechanism | Designed to preserve | Live today (verified) | Where it fails |
|---|---|---|---|
| `autoCompactEnabled` / `autoCompactWindow` (D21, W0-1) | A session that never dies at 977K and never forks a full window (C1 class A) | Project `true` / `700000` (`.claude/settings.json`); user `autoCompactEnabled: true` (flipped this session, S1 line 54, DL-72); `~/.claude.json` no longer carries the key | Works as designed (three compactions at 663-666K) and is the only live mechanism, while the memory rule says "/clear not /compact" (`memory/marketplace-lane-loop-2026-10-14.md`). Compaction is not a checkpoint: nothing on disk changes when it fires. |
| Context budget table (D29, `claude-team.md:116-133`; `frontier.toml` ceiling; `dev/doctor/budget.py`) | A checkpoint at 400K, no forks past 500K, handoff and `/clear` at 550K | The table, the doctor line that prints it (`budget.py:45-48`), the `A.autocompact-off` detector. Nothing reads the live transcript size. | Every threshold crossed in every window (400K at 07:17Z, 10:59Z, 15:17Z, 18:44Z; 550K at 08:48Z, 12:58Z, 15:47Z). One checkpoint (rev 10). `/clear` needs the user; the design has no branch for "the user keeps working". |
| Doctor SessionStart block (`dev/doctor/cli.py --surface session-start --format context`; D101) | Checkout, branch, HEAD, plan, thresholds, findings at startup, resume, clear, compact, fork | Live since `1dfefa3` (17:08:50Z); exit 0; output is five lines: checkout, branch, context thresholds, findings. Detectors: `A.autocompact-off`, `C.foreign-hunk`, `C.merge-in-progress`, `I.settings-local-not-excluded`. | Absent at all three compactions. Carries no request, decision or handoff content, so even when it fires after a compaction it cannot restore a dropped request. |
| planning-with-files 3.24.0 hooks (`hooks/hooks.json`: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, Stop) | Plan head and progress tail after every compaction and prompt; a PreCompact reminder; a Stop gate (legacy mode never blocks, `scripts/gate-stop.sh`) | Fired at all three compactions (`T:L2467`, `T:L5053`, `T:L7369`) and on 107 prompts. Legacy mode (no `.mode`, no `PWF_INJECT`). | Injects the handoff-derived head only (RC6). The PreCompact text is advice ("ensure progress.md captures recent actions", `inject-plan.py:1228-1240`) delivered when no model turn can act on it; the transcript records no PreCompact output, so whether it ran is UNVERIFIED. `.mode` injection shape is a P3 nobody closes. |
| `dev/handoff.py` + session-handoff + session-resume (CT-29, X3 predicate Z) | Zero loss across `/clear`: HEAD, lanes, receipt-less operations, cited paths, injection probe, agents-done; the resume skill re-reads HANDOFF §1-§2 and dispatches an extractor | `state|write|check|owner|start-command`, 36 tests, rev 13 (`0ef449f`, 17:24Z); check rc 0 | Pending = operations only; pending-user = hand-written; no finding when an accepted decision has no item, lane or ticket; `check` is green with D114/D119 missing. Written before 2 of 3 compactions were stale. The resume path (extractor brief, HANDOFF §1/§2) inherits the same hole. |
| Decisions ledger and `plan_decide.py` (D12, N2) | Every decision, approval, operation and receipt with an id | 162 decisions, 12 approvals, 17 operations, 16 receipts; `pending()` = receipt-less operations; 6 decision rows marked "[pending user]" | A decision that is work (D114, D119, D133, D138) gets no `operation`, so it is never "pending". The N2 dispatch gate `brief_lint` and records guard (CT-19) are unbuilt. |
| Mods design (D92-D102, ADR 0007, A2; CT-23 = A2-12..A2-14; CT-76 = A2-11 and research tasks) | `prompt.submit` context line with ctx from `$.session.usage()`, `agent.spawn` fork and roster gate, doctor-context mod, session.start reload, `ctx:status` | Nothing: zero mods on disk; A2-11..A2-14 "not allocated" (`P/ticket-ledger.md:154,207`); only the three deny-gate settings hooks are live (D102) | Relied on by `claude-team.md:131` and `hooks-and-mods.md` ("until the mods-library units land, the other hooks stay as they are", but the prompt and agent hooks never existed as hooks either). Upstream risks (#99130 remote switch, #96831/#100869 Stop delivery, #92533) mean a mod can be off without notice even once built. |
| Deny gates (`dev/hooks/pretooluse_gate.py`, `stop_gate.py`, `subagent_stop_gate.py`) | Merge/push discipline; no integrated lane without a passed retro | Live; the Stop gate blocked once this session (`T:L8576`, w0-doctor retro) | Shape-checked lane state only (`stop_gate.py:27-33`); nothing about requests, decisions or budget. |
| Memory files | Session gotchas (compaction off, agents dir load, skill overrides), injection shape, lane loop, verify-don't-ask | Loaded at session start; updated during the session (`T:L9142`) | No rule says "a request becomes an item before the turn ends"; the injection memory asserts a smart-mode layout that is not configured. |
| Subagent briefs (`docs/agents/codex-task-orchestration.md` ownership and unit size) | One unit per brief, file scope, receipts, checks | 72 briefs this session, all hand-written by the parent | No brief carries the parent's open requests; the parent condenses results by hand (C1 class G). After S3, every brief is written from a context that no longer holds D119. |

Features relied on that exist only on paper (ticket "not allocated" or unbuilt): CT-23 prompt and
agent hooks and `ctx:status`; A2-11 doctor-context mod (D101's dated exception has no date);
CT-29/CT-30 pwf smart mode and NEXT retirement; CT-19 `brief_lint` and the records guard (N2 §3a,
§3b); CT-59 `claude-agent` and `codex-agent` skills (D119 "now"); the D114 intake skill; the D121
metrics automation (CT-25, CT-59f1); the D138 launchd watch; CT-80's recurring recheck; the
ticket-frontier executor gate (D127 deferred). GitHub issues: all of CT-01..CT-85 are "pending
issue" because filing waits for the user's typed `/to-tickets` stage (D63, D90, DL-4), so "linked
GitHub issue" cannot be satisfied for any request today.

## 3. Compaction-summary diffs

Method: the user turns and AskUserQuestion answers of each window (saved in the CL2 scratch
folder as `user-turns.tsv`, `ask-answers.tsv`) against the following summary's text.

### S1 (`T:L2449`, window `T:L1-2448`, context 663,386 at `T:L2418`)

Kept: U1-U7 as plan Phase 4a with CT-34..CT-39 (S1 lines 23-31); D59-D81 and ADRs 0002-0005;
the executed operations with receipts; handoff rev 10 rc 0; the TR import reports and
CT-41..CT-58; the in-flight reprioritization with P2 and P3 still running and a seven-step plan
(lines 80-101); a "Pending for user" list (lines 103-107).
Dropped or demoted: the verbatim nine-part request of `T:L332` (agent-error review; a mod that
runs `/reload-skills`, `/reload-plugins --force` and renames the session with the padded
timestamp format; webclaw mod; new-terminal handoff; skill modularity) is reduced to labels "U1:
agent errors", "U2: session-start mod"; `T:L472` (native uv/ruff/ty/pyproject first, "see
dotfiles and knowledge-base") to "U6"; the user's stated plan "i will run /clear and start a new
session" (`T:L130`) is gone, and with it the fact that the session was meant to end at rev 10.
Faithfulness otherwise high: this window's requests were already projected into plan items by the
grill rounds, which is why they survived.

### S2 (`T:L5036`, window `T:L2450-5035`, context 663,132 at `T:L5020`)

Kept: D82-D110 with ledger ids; the research rule and provider route; the import review with
"A1 (CT-59 as 7 units 59a-59f2)" (line 51); Q3's 67 findings "not yet applied"; Q2-order-v2; the
host-lock artifact and its open thread; R4-R6 running; next steps 1-5 and a pending-user list.
Dropped or demoted: Q47b "We are supposed to build the same 2 skills for claude that codex has"
(`T:L3505`, 10:44Z, the first time the user names the claude-agent work) survives only as "D88:
CT-59 ... replace CT-28" (line 42), a ticket in a wave, with no urgency; Q44's "deep research pwf
offline docs" (`T:L3448`) is not in the summary (whether it ran is UNVERIFIED); Q77's "i still
dont understand use visual skills" (`T:L4750`) became the artifact rule in memory (kept). Open
questions that were asked and answered with free text are converted to decision ids; the free
text itself is never carried.

### S3 (`T:L7356`, window `T:L5037-7355`, context 665,986 at `T:L7329`)

Kept: D111-D147 as one-line decisions (lines 75-105), including "D114: ... Build an intake skill
via /skill-creator that delegates to the claude-agent team and produces a visual lanes artifact
(pending)" (line 79) and "D119: build CT-59 now with an SDLC team. The design is at
`P/reviews/ccm-20261014/ct59/CT59-design.md`" (line 83); artifacts with thread state (lines
115-118), including "Pending: republish with R12+R12b data ... then ask to accept the team" (line
117); "Other open items" (lines 120-127): "CT-59 forks F1/F2 and the team acceptance", Q105,
fourth reprioritization, w0-doctor merge, handoff rev 13, typed stages, top-ups.
Dropped or demoted:
1. Q86's three deliverables (`T:L5218`): intake skill; reprioritization history plus per-task
   duration and context trends; lanes/queue/predicted-lane/backlog-completion artifact. One
   decision bullet with "(pending)"; not in "Other open items"; the trends and the artifact are
   not named anywhere as work.
2. Q90's "have a subagent team with all necessary sdlc subagent roles w optimized models/effort
   build CT-59 now" (`T:L5372`): the "now" survives inside a decision line; the next action (stage
   2 of the team after the architect) is absent; the architect's "11 units and nine open forks"
   (`T:L5553`) shrank to "forks F1/F2".
3. Q97, Q98 (`T:L5663`) and Q107 (`T:L6163`) "(no option selected)": three questions the user
   never answered are not listed as questions to re-ask; D134 "R12 team table is pending a
   compliant report" stands in for them, and no post-S3 turn asked again.
4. Q106 (`T:L6163`) "if the claude-agent team is available have it just build the p2996 llvm
   tools now": D133 keeps "when available"; no item.
5. Q107 and Q112 (`T:L6163`, `T:L6267`): the launchd watch "triggers the claude-agent
   skill/team": D138 keeps the schedule, drops the trigger target.
6. The summary's own framing: "Current critical task: history replacement" with nine "Remaining
   steps (approved in Q119)" (lines 31-65). The privacy incident of 15:50Z (`T:L6825`) correctly
   became the critical task, and D119 silently lost its place in the queue; nothing marked it as
   "interrupted, resume after".
7. Constraints kept well: TR handling, D144-D146, admissions, artifact threads. Constraints
   dropped: the memory rule "never dispatch a brief that executes a pending decision" and the
   budget table itself (no summary mentions the thresholds or the checkpoint rule).

### After S3 (`T:L7357-9239`)

The parent executed the S3 "Remaining steps" (PR #109 closed, force-push, PR #110, w0-doctor
integrated, handoff rev 13) and the user's `T:L8415` answers (D150-D159). D119 and D114 were
touched only by D153's "no claude-agent skill exists yet" (`T:L8469`). The handoff written at
17:24Z (rev 13) lists pending user items "GitHub Support purge request; file the guard and C++
check tickets; Q2-order-v2 §6 U1-U5; typed stages" (`P/task_plan.md:21-22`): the hand-typed line
omitted D114 and D119 because the parent's context no longer held them as work.

## 4. Hypotheses for the research agent (CL3) to test

H1. **Request ledger at UserPromptSubmit.** A settings hook on `UserPromptSubmit` (hook input has
`prompt`, `session_id`, `transcript_path`) appends every user prompt to `P/requests.jsonl` with an
id `R-n`, and a `PostToolUse` hook matched on `AskUserQuestion` appends each answer (the
`tool_response` carries "The user answered: ..."). Test: does `PostToolUse` receive
`AskUserQuestion` responses on CLI 2.1.299, including "(no option selected)" and free-text notes;
cost per fire (pwf measured about 130 forks per UserPromptSubmit, `inject-plan.py:7-13`).

H2. **Doctor detector `R.request-unprojected`.** A request id older than N turns with no
task_plan item, ticket-ledger row, lane record, ledger `operation` or receipt citing `R-n` is a P2
at `session-start`, `check` and pre-commit, and a P1 at `handoff`. This closes RC1 without a mod.
Test on this session's 110 turns and 24 answers for the false-positive rate (local commands,
task notifications and "Here is a note offered by a side agent" must be excluded; the brief's
filter rules already do that).

H3. **SessionStart(compact) injection of open requests.** The doctor already runs on `compact`;
add a bounded context block listing open `R-n` ids with their first 120 characters. Verified: pwf's
SessionStart additionalContext is injected right after the summary (`T:L7369-7370`, 0.4 s after
`T:L7356`), so this is the cheapest catch. Test the additionalContext size cap (X3 notes 10,000
chars) and whether the block lands before or after the verbatim tail messages.

H4. **Post-compaction summary audit.** The same SessionStart(compact) hook reads
`transcript_path`, takes the last `isCompactSummary` entry and reports "requests not mentioned in
the summary: R-...". Test: is the summary already flushed to the transcript when the hook runs
(`T:L7356` at 16:52:21.754Z, hook at 16:52:22.186Z suggests yes); do PreCompact hooks run at all
under auto-compaction on this host (0 transcript entries; the pwf hook exists in `hooks.json`).

H5. **Custom compaction instructions.** Whether Claude Code 2.1.299 supports a project-level
instruction for the compaction prompt (settings key, CLAUDE.md section, `PreCompact`
`custom_instructions` for automatic compaction, or `hookSpecificOutput` on PreCompact). If it does,
require a verbatim "Open requests" section with ids. If only manual `/compact <instructions>`
takes instructions, the mechanism is H3/H4.

H6. **Stop gate on unprojected requests.** Extend `stop_gate.py` (a settings hook, per D102) to
block the turn end once when a request captured this turn has no projection; respect the
8-continuation cap and `stop_hook_active`; `onFailure` has no effect on Stop (R8), so the gate must
be fast and must never crash. Test for turn-end latency and for the case where the projection is
legitimately "answered in text" (a question, not a request).

H7. **Budget enforcement as a hook, not a mod.** A `UserPromptSubmit` settings hook that reads the
transcript's last `usage` block (what `dev/context_budget.py` was meant to do) injects the ctx line
and, at or above 550K, the sentence "run /session-handoff now and ask the user to type /clear".
Mods are paper and can be switched off upstream (#99130); a hook fires. Test: transcript read cost
on a 20 MB file (tail only), and whether the parent follows an injected instruction at 550K+.

H8. **Request ids in briefs.** A `PreToolUse` hook on `Agent` (or the A2-14 `agent.spawn` mod
later) appends "Parent open requests: R-..." to every brief and requires the subagent's final
report to list which it touched; `subagent_stop_gate.py` can check the list. Test with the 72
briefs of this session: how many would have surfaced D119.

H9. **pwf task_plan items as the projection.** Each `R-n` becomes a checklist item under a
`## Requests` or `### Phase` heading that pwf's smart mode and `/status` parse; switch `P/.mode`
to `inject-smart` (CT-30) so `## Next Step` and `## Current Phase` are extracted by structure
rather than head-50. Test the 30-line PreToolUse window budget and `H.mode-not-inject-smart`.

H10. **GitHub linkage under the typed-stage rule.** Filing tickets waits for `/to-tickets` (D63,
D90, DL-4). Research whether a "request intake" issue (label `request`, created under a standing
admission) or a GitHub Discussion can be opened per `R-n` without breaking the spec-first
workflow, or whether the ticket-ledger "pending issue" row is the link until publication. Also
whether CT-19's `brief_lint` and N2's records guard already specify the dispatch-time check.

H11. **Checkpoint without /clear.** Since the model cannot `/clear`, test whether a
`PreCompact`-time `dev/handoff.py write --agents-done` (if PreCompact fires) or an H7-triggered
write at 550K makes the on-disk handoff fresh at every compaction, so that H3 can inject a current
`## Next Step` instead of a stale one.

## 5. Scratch evidence

`/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/ctxloss/CL2/`:
`compact-1-L2449.md`, `compact-2-L5036.md`, `compact-3-L7356.md` (the three summaries),
`user-turns.tsv` (110 user turns), `ask-answers.tsv` (24 answers), `subagent-briefs.tsv` (72
briefs with hit flags). Read-only on MP; no GitHub writes; no `claude` sessions; TR by codename.

# CL4: proposal to stop losing requests and to catch a drop before the user does

Team CL, architect row (synthesis, Fable 5.1), session `ccm-20261014`, 2026-10-14. Inputs: the
shared brief, `CL1-request-ledger.md` with `CL1-requests.jsonl` (170 rows), `CL2-mechanism-review.md`,
`CL3-research.md` (with the offline mirror under `offline/research/CL3/`), the parent's stopgap
`## Open requests` section in `task_plan.md`, decisions D59, D63, D90, D92 to D102, D112, D113, D114,
D119, D128, D131, D151 and D160 to D163, `docs/agents/hooks-and-mods.md`, `docs/agents/issue-tracker.md`,
`dev/handoff.py`, `.claude/settings.json` and the planning-with-files 3.24.0 hook scripts. Read-only
except this file. P is the plan directory; MP is this repository; TR is the private project's codename
(D144); `D/hooks.md:n` cites CL3's raw-markdown mirror of the Claude Code docs as CL3 cites it.

## 1. Verdict

Adopt a request lifecycle with one principle: nothing depends on the agent remembering. Requests
are captured by settings hooks with zero logic, projected into one place that every carry-over
already reads (the pwf plan), carried across compaction, `/clear`, resume and into every subagent by
hooks that only print, linked to GitHub through the qualified issue route, and caught by a
deterministic check that refuses a handoff while a captured request has neither a projection nor a
disposition. Judgement (classifying prompts, auditing a summary, blocking a stop) goes to the C++ core
(D112, D131); until it builds, the handoff check carries the catch.

Four decisions are the user's (section 8): settings hooks as a second dated exception to D92;
where the interim catch lives; how requests link to GitHub while `/to-tickets` stays a typed stage;
and the admission for one live probe.

## 2. Summary of what the team found

- Scale. 170 requests across three sessions and three forks since the takeover: 108 done, 14 in
  progress, 33 tracked but not started, 12 dropped, 3 superseded (CL1 section 1). No GitHub issue was
  created for any request after the takeover; all 86 takeover-spec ticket rows read "pending issue"
  (CL1 section 1, mechanism M9). Decisions D133 to D160 exist only in `decisions.jsonl`, not in the
  plan (CL1 section 1, M3).
- Cause. Every dropped request reached at most a decision row (CL1 section 4: "Every dropped request
  carries M1"), and every carry-over mechanism reads only projections: `dev/handoff.py` lists
  receipt-less `operation` rows only (`dev/handoff.py:270-283`), its single decision check covers
  operations only (`:558-561`), the "Pending user" line is hand-typed in the template
  (`.claude/skills/session-handoff/references/handoff-template.md:18-20`), and the X3 predicate was
  designed the same way (CL2 RC1; `predicate.md:14`). So the Next Step block, the NEXT bullet, the pwf
  injection, the resume extractor and `handoff.py check` all pass with the user's request absent
  (CL2 RC1).
- Compaction. None of the three auto-compactions dropped a whole request (CL1 section 4; CL2 section
  3), but summary 3 filed D114 and D119 under "Decisions this segment" while "Other open items" named
  only two forks, under a "critical task: history replacement" that silently displaced the user's
  "build CT-59 now" (CL2 RC2, section 3 S3 items 1, 2 and 6). All three compactions fired at 663K to
  666K tokens with no MP hook attached and the handoff stale at two of them (CL2 RC2, RC3).
- The user's example. The `/claude-agent` skill was asked for twelve times across two sessions; it
  was never lost from memory, it was lost because no artifact that drives the next action carried it:
  the ledger row contradicts D119, the handoff generator ignores decision rows, the rev 13 template
  rewrite left it out, the plan stopped at D132, the 17:24Z "what next" question recommended the
  stale Next Step, and the acceptance chain had no receipt (CL1 section 2, "Where it was lost").
- Free text. AskUserQuestion answers with notes or "(no option selected)" were hand-converted to
  decision ids and the deliverables fell out (CL2 RC4; CL1 R-119, R-120, R-135, R-138, R-139, R-140).
- Briefs. None of the 72 briefs after summary 3 carried the open request list, so no subagent could
  notice the drop (CL2 RC5).
- The parent's stopgap. `task_plan.md` now has `## Open requests` with 23 checkbox items
  (`task_plan.md:42-70`). It is the right shape but the wrong place: the section starts at line 42 and
  its items at line 48, so the legacy turn-start injection (`head -50`, CL2 RC6) carries three of the
  23 items and the per-tool frame (`head -30`) none; pwf smart mode would drop the section outright,
  since it keeps only Goal, Next Step, Current Phase, the first in_progress phase and the last three
  decisions (CL3 section 1 item 2; `inject-plan.sh:1020-1032`). The Next Step block budget is 16 lines
  (`handoff-template.md:6`), so the list cannot move there either. Section 4.2 fixes the placement.
- Mods. The compaction mod event is not raised on 2.1.299 (#102134), a mod blocks a stop only through
  `classic.Stop` whose delivery is unreliable (#96831, #100869), `session.start` does not fire after
  `/clear`, `/resume` or `/branch`, and the remote switch can turn mods off (#99130) (CL3 section 1,
  "Mods are not the guarantee today"; `docs/agents/hooks-and-mods.md:21-34`). No mod exists on disk
  (CL2 section 2, mods row).

## 3. Classification of every element under MP's rules

Classes: configuration (settings, plan convention, docs, mise task, no-logic hook), fix (existing
Python, D113), C++ (new logic, D112, D131) with the zero-logic interim named.

| Element | Class | Evidence |
|---|---|---|
| E1 capture: `UserPromptSubmit` and `PostToolUse(AskUserQuestion)` settings hooks, `/usr/bin/jq -c .` appended to an untracked ledger | configuration; a new settings hook needs decision A (D92 sends new behaviour to mods; D102 is the only exception) | CL3 section 1 item 1, section 7.1 (payload fields `D/hooks.md:728-745`, `:1459-1474`, `:2346`), section 7.2 H1, section 8 config; CL2 H1 |
| E2 capture echo: the same hook prints `[requests] captured p:<id8>; open <count>` so the parent can cite the key | configuration (one `jq` format string and one `grep -c`) | `D/hooks.md:806-812`, `:1478-1486` (stdout reaches context); async output lands next turn (`:4017-4060`), hence synchronous; probe item (section 7) |
| E3 projection: `## Open requests` line shape, placement right after `## Next Step`, a generated roll-call line inside `## Next Step`, an untracked dispositions file | plan convention: configuration; the generated lines: fix to `dev/handoff.py` (decision B) | CL2 RC1, RC6; CL3 section 1 item 2, H9, M3; CL1 M1, M2, M3; `handoff.py:636-659` |
| E4 carry: `PreCompact` prints Next Step plus Open requests into the compaction instructions; `SessionStart` (all five sources) and `SubagentStart` print the section; `PostCompact` archives the summary; `# Compact instructions` in CLAUDE.md | configuration | CL3 section 1 item 2, section 7.1 (PreCompact stdout per the binary help text and #101057; SubagentStart `D/hooks.md:2534-2544`; PostCompact `:3274-3296`, #89622; SessionStart sources `:1201-1290`, #93458; caps `:1015-1020`, #94358), H3, H4, H5, H8, H11; CL2 RC2, RC5, H3 |
| E5 pwf `inject-smart` (`P/.mode`), CT-30 | configuration | CL2 RC6; CL3 M4, H9 (`PWF/scripts/inject-plan.sh:1005-1066`) |
| E6 pwf defects: `PreCompact` reminder emitted as JSON `systemMessage` which Claude Code discards; `SessionStart` matcher lacks `fork` | upstream issues (user files them; the brief forbids GitHub writes); CT-80 watch list entries | CL3 section 1 "Two defects" (`PWF/hooks/claude-hook.sh:319-323`, `:349-353`; `D/hooks.md:3257`, `:1213-1217`); `PWF/hooks/hooks.json:6` |
| E7 catch: `H.request-unprojected` and `H.request-unlinked` findings in `dev/handoff.py check`, surfaced through the doctor `handoff` and `check` surfaces | fix to existing Python under decision B (the X3 predicate claims zero loss and passes with a dropped request: a defect), ported to C++ with the gates (D131) | CL2 RC1, H2; CL3 H2 ("right check, wrong home"), M9; `handoff.py:860-865` (doctor discovery), `:776-805` (`write` refuses on a failing check); `dev/doctor/core.py:16` |
| E8 Stop and SubagentStop request gate: block once with `additionalContext`, honour `stop_hook_active` and the cap of 8 | C++ (D131, with the deny-gate port); interim: none deterministic | CL3 section 1 item 3, section 7.1 Stop (`D/hooks.md:2693-2795`, #85547, #78121, #86569, #92716), M10; CL2 H6; `dev/hooks/stop_gate.py:26-35` |
| E9 classifier (human prompt versus subagent report, task notification, peer message), summary audit against `compact_summary`, request ids assigned mechanically | C++; interim: the parent's dispositions file and the ledger key | CL3 section 11 (#100666), H4 (PostCompact runs after SessionStart(compact), #78760), M9 |
| E10 GitHub link: ticket-ledger row now; a "Requests intake" parent issue with one sub-issue per open request through `issue:create-preview/apply/verify`; closure through `issue:preview/apply/verify` version 2 | configuration (manifest data, mise steps) plus fixes only to `dev/issue_create.py` and `dev/issue_amend.py`; needs decision C and a recorded admission | CL3 section 1 item 4, H10, section 7.1 GitHub linkage, section 8 prior art; `dev/issue_create.py:19-32` (`GENERIC_ID`, `parent_number`, 50 tickets per manifest); `dev/issue_amend.py:20,195` ("PATCH completed state"); `docs/agents/issue-tracker.md:24-56`; D59, D63, D90, D151; CL1 M9 |
| E11 budget: a status line showing `context_window.used_percentage` and the open count | configuration, but a user-level setting (own admission); reading the usage block for a hook is C++ | CL2 RC3; CL3 H7 (`statusline.md:181-183` in the R7 mirror) |
| E12 process rules for the parent and briefs (section 5) | documentation (AGENTS.md hierarchy, rules, skills, memory) | CL1 M2, M4, M6, M7, M8, M10; CL2 RC4, RC5 |
| E13 Task tools as the list (`CLAUDE_CODE_ENABLE_TODO_TOOLS`) | declined: off by default on Opus 5.5, a `TaskCreated` rule is logic, and D63 keeps the plan as the working record | CL3 section 7.1 (`D/tools-reference.md:581-595`), M11 |

Hooks versus mods. CL3 recommends settings hooks for E1, E2 and E4 (CL3 section 1, "Mods are not
the guarantee today"); D92 says every new behaviour is a mod and D102 lists the only exception. The
reasoning that kept the three deny gates as hooks applies to a ledger that must not miss: a capture
that a remote switch can disable is not a capture (#99130), the compaction event is not raised
(#102134), and a mod must call a C++ core that is not built (ADR 0008; CL3 M12). The user decides
(section 8, decision A); my recommendation is a second dated exception, with the D128 shape as the
exit: when a mod event is verified live, the mod does the work and the hook stands down on its mark.

## 4. The request lifecycle

### 4.1 Capture

- Source events: every typed prompt (`UserPromptSubmit`, which since 2.1.299 fires before a slash
  command or skill expands, `D/changelog.md:156`) and every AskUserQuestion answer including notes and
  "(no option selected)" (`PostToolUse` matcher `AskUserQuestion`, whose structured output carries
  `answers` and `annotations.<question>.notes` in this session's transcript, CL3 section 1 item 1).
  Queued mid-turn messages were all acted on (CL1 section 4), but #90296 reports a host where they
  did not fire; the handoff catch is the backstop.
- Ledger: `~/.local/state/claude-code-marketplace/requests/ledger.jsonl`, one JSON object per fire,
  exactly the hook stdin (`jq -c .`). Fields come from the payload: `session_id`, `prompt_id`,
  `transcript_path`, `cwd`, `prompt` for prompts; `session_id`, `tool_input.questions`,
  `tool_response` for answers (CL3 section 7.1). The key is `prompt_id` for a prompt and the answer
  row's tool identity for an answer (the probe confirms which field; section 7). The ledger stays
  outside MP and untracked because prompts can name TR (D144 to D146; CL3 section 8 chooses the
  same location). The state directory already exists for `private-notes`.
- Companion files in the same directory: `dispositions.jsonl` (`{key, disposition, ref, ts}` with
  disposition one of `projected`, `noted`, `duplicate`, `re-ask`, `agent-report`; written by the
  parent) and `compactions.jsonl` (`PostCompact` stdin appended with `cat`, not `jq`, because the
  payload can be invalid JSON, #89622).
- Echo: the capture hook runs synchronously (timeout 5 s) and prints one line,
  `[requests] captured p:<first 8 of the key>; open requests: <N>`, where N is `grep -c '^- \[ \] R-'`
  over the plan. Never the text. The parent cites `p:<id8>` in the plan line.

### 4.2 Projection

- One projection: `## Open requests` in `task_plan.md`, placed directly after `## Next Step` and
  before `## Goal`, at most 60 lines; overflow is counted in the roll-call line and lives in the
  ledger. The section already exists with the right item shape (`task_plan.md:42-70`); the lane moves
  it and normalises the lines.
- Line shape, one request per line, TR-scrubbed, at most 160 characters:
  `- [ ] R-171 · p:4462d3b1 · D114 · CT-86 (pending issue) · owner parent · blocked by R-127 · text`.
  Fields in order: id, key, decision ids, ticket (CT-n or `none`), issue (`#n`, `pending issue` or
  `none`), owner (`parent`, `user`, `lane <unit>`), optional `blocked by`, short text. A compound
  prompt gets one line per distinct ask, as CL1 split them (CL1 "How requests were counted").
- Roll-call line in `## Next Step`, generated by `dev/handoff.py` (fix, decision B):
  `Open requests: 23 open, 2 awaiting user, 0 unprojected; list in ## Open requests; ledger rev <n>.`
  It fits the 16-line budget and sits inside the pwf per-tool frame (`handoff.py:641-652`). The
  template's `pending-user` section is retired; the line is built from the `owner user` lines, so it
  can no longer be hand-trimmed (CL1 M2; `handoff-template.md:18-20`).
- Decisions that create work: a `decision` row whose text promises work (D114, D115, D119, D133,
  D138 in CL1 section 1.1) gets an `R-n` line at the moment the row is appended; the row's `source`
  cites the line. This closes CL2 RC1 at the source.
- pwf: the parent keeps `- [ ]` items so pwf's parallel-write guard counts them (`PWF SKILL.md`,
  "Parallel-write guard"); CT-30 flips `P/.mode` to `inject-smart` after the roll-call line lands,
  because smart mode extracts `## Next Step` by structure and legacy mode by position (CL2 RC6; CL3 H9).

### 4.3 GitHub linkage

- Today: the link is the ticket-ledger row (`R-n` to `CT-n`, "pending issue") until `/to-tickets`
  publishes the spec tickets (CL3 section 1 item 4, H10). D63 keeps the plan as the working record
  that mirrors the tracker; D90 and D151 defer filing to the typed stages at the gate. CL1 found that
  this gate has blocked every one of the 86 ticket rows since 2026-10-14T03:34Z (CL1 R-002, R-004, M9).
- Proposed (decision C): a standing "Requests intake" parent issue (label `needs-triage`,
  `docs/agents/triage-labels.md`) and one sub-issue per open request, created by the parent at each
  handoff batch through `issue:create-preview`, `issue:create-apply`, `issue:create-verify` with a
  version 2 manifest (`GENERIC_ID` accepts `R-171`, `parent_number` is the intake issue,
  `dev/issue_create.py:19-32`); native sub-issues need no extension (`gh` 2.98.0 `--parent`, CL3
  section 7.1). A request issue is an intake record, not a ticket: it never carries `ready-for-agent`,
  which the manifest check already refuses (`issue_create.py:44`). When `/to-tickets` publishes the
  spec ticket that absorbs a request, the request issue gets a blocker edge through `issue:new-edge-*`
  or is closed as a duplicate through the version 2 `issue:preview/apply/verify` route
  (`dev/issue_amend.py:20,195`). This squares with D59 and D151: spec tickets are still filed with the
  spec at the gate; the request issues are the "linked GitHub issue" the user asked for on 2026-10-13
  (CL1 R-004) and again in R-106 and R-170.
- Who and when: the parent, at the handoff batch that follows the projection, never per turn (at most
  50 per manifest; one qualified apply per batch). Never `gh issue create` directly
  (`issue-tracker.md:50-56`). Body template (public, TR by codename, scanned with `.gitleaks.toml`
  before apply): request id and key, session and UTC time, verbatim ask after scrubbing, decision ids,
  plan line, current disposition, what closes it. Prior art agrees on parent plus sub-issues
  (ccpm, claude-gh-task-manager, CL3 section 8) and warns that asking the model to open issues is
  non-deterministic (rdmolony's README, CL3 section 8), which is why the hook captures and the
  qualified task publishes.

### 4.4 Closure

- A line is ticked only with evidence: `- [x] R-171 ... done: <receipt path, SHA or exit code>`;
  the dispositions file gets `{key, "done", ref, ts}`; the GitHub issue is closed through the
  qualified completed-state route with the same evidence. "Issue creation, publication or a label
  never closes a ticket" (`issue-tracker.md:37-38`); the retro gate owns acceptance
  (`docs/agents/ticket-retro.md`). A request answered in text with no work gets `noted`; a question
  the user did not answer gets `re-ask` and stays open until asked again (CL2 section 3 S3 item 3).

### 4.5 The catch

| Where | Condition | Severity and effect |
|---|---|---|
| doctor `session-start` surface (startup, resume, clear, compact, fork) | a ledger row of this session's key set with no `dispositions.jsonl` row and no `p:<id8>` in `## Open requests`; or an open line with `issue: none` and `CT: none` | P2: one context line `requests: N open, M unprojected (ids)`; exit 0 as the surface requires (`dev/doctor/cli.py:4-6`) |
| `dev/handoff.py check` and the doctor `check` surface | same conditions | P2 (`H.request-unprojected`), P3 (`H.request-unlinked`, P2 once decision C is taken); `check` exits 2 |
| `dev/handoff.py write` | same | refuses to regenerate the handoff (`write` already refuses on P1/P2, `handoff.py:803-805`), so no `/clear` happens with an unprojected request; the finding is not auto-fixable, the parent must project or dispose |
| `/session-handoff` and `/session-resume` skills | same, through `check` | the skills print the ids and stop at the gate |
| Stop and SubagentStop gates (C++, CT-92) | a request captured this turn with no projection and no disposition | `additionalContext` first, block once, never when `stop_hook_active`, within the cap of 8 (CL3 section 1 item 3) |
| pre-commit surface | not checked | a 300 ms budget and a commit should not be refused for a plan gap (`core.py:16`) |

Scope of the interim catch: rows whose `session_id` is the parent's. Fork sessions write to the same
ledger with their own id; until the C++ classifier (CT-92) the fork rule in section 5 covers them.

## 5. Immediate process changes (before any ticket lands)

For the parent:
1. Before a turn ends in which the user typed or answered, each ask is a line in `## Open requests`
   with its `p:<id8>` and decision id, or a `noted` or `re-ask` row in `dispositions.jsonl`. Free text
   and "(no option selected)" answers count (CL2 RC4; CL1 R-118 to R-120).
2. The handoff is generated, never hand-trimmed: `dev/handoff.py write` runs after the section is
   reconciled; until CT-89 lands the parent writes the roll-call line and the `pending-user` text from
   the `owner user` lines only (CL1 M2).
3. A "what next" AskUserQuestion lists the open request ids as its option set and states the count;
   an unpicked option stays an open line (CL1 M6).
4. A reprioritization report is applied only after reconciling every decision newer than its draft
   (CL1 M4). The live instance is D119 against the CT-59 ledger row (CL1 section 2 row 7): reconcile
   it now by moving CT-59 to the head of the order or by re-asking the user, and say which.
5. A report's "new ticket" recommendation becomes an open request line when the report is accepted
   (CL1 M8); a prerequisite chain is written as `blocked by R-m` lines, not as prose (CL1 M10).
6. After a compaction, the first action is to compare the summary's "Pending Tasks" with
   `## Open requests` (`dev/handoff.py state --brief` then the section), before any other work
   (CL2 RC2; CL3 section 7.1, summarizer sections).
7. At 550K tokens the parent runs the handoff and asks the user to type `/clear`, naming the open
   request count in the question (CL2 RC3; `docs/agents/claude-team.md:116-133`).
8. Memory gains the rule "a request becomes a plan line before the turn ends" and drops the claim
   that smart injection is configured (CL2 section 2, memory row).

For subagent briefs:
9. Every brief carries `Open requests touching this unit: R-...` and `Report any request you could
   not honour, by id`; the final report lists the ids it touched; the parent updates the lines from the
   report (CL2 RC5, H8; CL3 H8).
10. A fork's asks are copied to `## Open requests` by the parent when the fork returns; a fork never
    starts a team (CL1 M7, R-026, R-042).
11. A reviewer or retro brief states the request ids the unit claims to close, so the retro gate can
    refuse a close without evidence (`ticket-retro.md` step 3).

## 6. Ticket split (unit size: at most five maintained files, about 300 handwritten lines, `docs/agents/codex-task-orchestration.md:204-206`)

Numbers continue the ledger after CT-85 (`ticket-ledger.md:213-216`); the parent assigns them.

| Ticket | Class | Files | Depends on | Delivers |
|---|---|---|---|---|
| CT-86 probe | admitted live probe (decision D) | 1 throwaway `settings.json`, 1 receipt report | nothing | section 7 |
| CT-87 capture | configuration (decision A) | `.claude/settings.json`, `docs/agents/hooks-and-mods.md`, `.claude/rules/hooks-and-mods.md`, a `requests:tail` mise task | decision A; the AskUserQuestion leg after CT-86 | E1, E2, PostCompact archive, watch-list entries |
| CT-88 carry | configuration | `.claude/settings.json`, `CLAUDE.md` (`# Compact instructions`), `docs/agents/hooks-and-mods.md` | CT-87; the PreCompact leg after CT-86 | E4: PreCompact, SessionStart, SubagentStart commands reading `${PWF_PLAN_ROOT:-$CLAUDE_PROJECT_DIR}` (CL3 section 11, worktree path pin) |
| CT-89 projection and catch | fix (decision B) | `dev/handoff.py`, `dev/test_handoff.py` (36 tests today), `predicate.md`, `handoff-template.md` and its `.agents` mirror | decision B | E3 roll-call line, generated pending-user, `H.request-unprojected`, `H.request-unlinked`; section move in `task_plan.md` by the parent |
| CT-90 process docs | documentation | `docs/agents/claude-team.md`, `.claude/rules/planning-records.md`, `.claude/agents/*.md` brief lines, the two session skills, memory | decisions A to C | section 5 as rules |
| CT-91 GitHub intake | configuration plus fixes only | manifest JSON under `P/`, a scan step before `issue:create-apply`, `ticket-ledger.md` requests table, `dev/issue_create.py` only if a fix is needed | decision C and a recorded admission | E10 |
| CT-30 (existing) | configuration | `P/.mode` | CT-89 | E5 |
| CT-92 C++ requests module | C++ (cxx lane) | `rsm-core` request module, bridge, doctor detector, Stop and SubagentStop gate extension, deletion of the CT-89 Python check | the `rsm-core` skeleton (D131, D7 spike) | E7 in C++, E8, E9 |

Order: CT-86 and CT-87 in parallel (CT-87's prompt leg needs no probe: the payload fields are
documented); then CT-89 and CT-90 in parallel; CT-88 once CT-86 reports; CT-91 when decision C and
the admission exist; CT-30 after CT-89; CT-92 when the skeleton builds, as the standing cxx lane.
Each unit ends at the retro gate (`docs/agents/ticket-retro.md`).

## 7. The probe (CT-86)

No live probe was allowed in this review (brief rule; CL3 section 11). One admitted probe in a
throwaway repository on Claude Code 2.1.300, no TR, no MP writes, settles everything the design rests
on. Hooks append their stdin to a log, as in #78760's maintainer steps:
(a) `PreCompact` fires on the auto path and its plain stdout (`KEEP R-TEST-1`) appears in
`PostCompact.compact_summary` (CL3 section 1 item 2; #101057; contradicts #50467 for older builds);
(b) pwf's JSON `systemMessage` from `PreCompact` is dropped (CL3 "Two defects");
(c) `PostToolUse` for `AskUserQuestion` carries `annotations.notes` and the key field for an answer
row, and whether the hook's stdout reaches the model;
(d) `SubagentStart` `additionalContext` reaches the subagent (`D/hooks.md:2534-2544`);
(e) the order PreCompact, SessionStart(compact), PostCompact on 2.1.300 (#78760);
(f) a synchronous `UserPromptSubmit` echo line reaches the model in the same turn with `prompt_id`.
Deliverable: a receipt under `reviews/ccm-20261014/context-loss/` with the raw logs and exit codes;
CT-88's PreCompact leg and CT-87's answer leg wait for it.

## 8. Decisions for the user

A. Settings hooks for request capture and carry, as a second dated exception to D92 beside D102?
   Options: (1) add `UserPromptSubmit`, `PostToolUse(AskUserQuestion)`, `PreCompact`, `SessionStart`,
   `SubagentStart` and `PostCompact` as no-logic settings hooks now, each replaced by a mod only when
   its mod event is verified live (D128 shape); (2) wait for the mods library, so nothing captures
   until it exists and the compaction leg stays blocked by #102134; (3) hooks for capture only,
   mods for carry later. Recommendation: (1). Evidence: CL3 section 1; `hooks-and-mods.md:21-34`.

B. Where does the interim catch live until the C++ core builds?
   Options: (1) a fix to `dev/handoff.py check` and `write` (the zero-loss predicate is defective,
   D113 allows fixes), ported to C++ with the deny gates; (2) C++ only, no catch until `rsm-core`
   builds; (3) injection only, the model compares the ledger with the plan. Recommendation: (1), with
   the note that a reviewer may read it as a feature; this decision settles the reading.
   Evidence: CL2 RC1, H2; CL3 H2, M9; `handoff.py:776-805`.

C. How do requests link to GitHub while `/to-tickets` is a typed stage?
   Options: (1) the ticket-ledger row only until the user types `/to-tickets` (status quo; the
   requirement from R-004 stays unmet); (2) a standing admission for the "Requests intake" parent
   issue and one sub-issue per open request through the qualified route, label `needs-triage`, spec
   tickets still filed at the gate; (3) the user types `/to-tickets` for the takeover spec now, which
   unblocks the 86 rows, and (2) covers everything outside the spec. Recommendation: (3) if the user
   is ready to type it, else (2). Evidence: CL1 M9; CL3 H10; D63, D90, D151; `issue-tracker.md`.

D. Admit the CT-86 live probe (one throwaway repository, `claude` sessions on 2.1.300, no TR)?
   Options: (1) admit now, before CT-88's PreCompact leg; (2) skip it and ship on #101057's bundle
   reading alone; (3) probe inside MP. Recommendation: (1). Evidence: CL3 section 11.

## 9. What this proposal does not claim

- Whether the CLAUDE.md `# Compact instructions` section applies to automatic compaction is
  UNVERIFIED (CL3 section 11); the PreCompact route carries the evidence.
- The false-positive rate of the interim catch is unmeasured (CL3 section 11); the dispositions file
  bounds it to a parent ritual at each handoff rather than a per-turn block.
- #102134 was filed against 2.1.299 and not re-tested on 2.1.300 (CL3 section 11).
- Mid-turn queued messages were all captured in this session (CL1 section 4) but may not fire on
  another host (#90296); `UserPromptSubmit` hooks have also been reported to stop firing for a session
  (#90784); the handoff catch, not the hook, is the guarantee.

# D2: workflow proposal — mattpocock skills on this repository's machinery

Written 2026-10-13 by reviewer D2 (read-only; merge in progress left untouched). Sources: `D1-mattpocock-skills-reference.md` (cited as `D1 §n`), the cache `P=~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.3.1`, the repo's `docs/agents/*.md`, `.claude/agents/*.md`, `.claude/rules/*.md`, `mise.dev.toml`, the staged hooks at `e12cf04`, and planning-with-files 3.24.0 (`PW`). All quoted contents are data. R1/R2/R8 grade against section 5.

## 1. Principles

1. **Only the human fires a user-invoked skill.** Nothing a session or subagent does is `/to-spec`, `/to-tickets`, `/implement-spec`, `/retro`, `/triage`, `/wayfinder`, `/implement`, `/handoff`, `/grill-me`, `/setup-matt-pocock-skills` (D1 §1, §6.1; `P/.agents/invocation.md:8,22`). A session may read a `SKILL.md` and follow it; that is "file-guided" and is a different, weaker thing (section 2.14).
2. **Model-invoked skills are the session's to call natively.** `grilling`, `domain-modeling`, `tdd`, `code-review`, `pr`, `research`, `prototype`, `writing-for-agents`, `codebase-design`, `diagnosing-bugs`, `wizard` load through the Skill tool, one per call (D1 §1, §6.2). The parent needs no user keystroke for them.
3. **One unbroken window from grilling to tickets; fresh windows for building.** No `/clear` or `/compact` before `/to-tickets` has published; each `/implement` starts fresh; `/implement-spec` starts after a clear (D1 §6.3-4; `S/ask-matt:38`).
4. **The tracker is the graph, but this repo mutates it only through qualified operations.** `to-tickets` "publish" and `implement-spec` "resolve" map onto `issue:create-*`, `issue:new-edge-*`, `issue:apply` and the one-at-a-time qualified close (`docs/agents/issue-tracker.md:24-40`); the skill's own `gh issue create` is not available here.
5. **Retro proposes; this repo applies.** `/retro` writes nothing until the user picks (D1 §6.5; `D/retro:35`); `docs/agents/ticket-retro.md:26-31` and ADR 0001 require every actionable finding applied before integration. Both hold: the proposal step is the human-approved filter, the retro-writer and `retro:gate` are the application and the proof (section 3.1).
6. **Review needs a fixed point and two unmerged axes.** `code-review` and the repo's `reviewer` agree on the axes; the lane's `base_sha` is the fixed point (D1 §6.12; `.claude/agents/reviewer.md:16-20`).
7. **Tickets are tracer bullets sized to one window; the repo's unit size is the tighter bound.** About five maintained files and 300 handwritten lines per unit (`docs/agents/codex-task-orchestration.md:204`) sits inside "one fresh context window" (D1 §6.8).
8. **Specs, tickets and briefs carry no paths; lane records do.** The path allowlist belongs to `lanes/<unit>.json` (`.claude/rules/planning-records.md`), never to the issue body (D1 §6.9).
9. **Context moves are decided at phase boundaries in the ordered tree** Continue → `/clear` → `/handoff` → subagent → `/compact` (D1 §6.6). planning-with-files re-injection after `/clear` is recovery, not a decision; it makes `/clear` cheaper, it does not replace the tree.
10. **Every stage ends on a receipt with its state named** (planned, implemented, tested, reviewed, committed, integrated, published, closed: `AGENTS.md:38-39`, `claude-team.md:25-37`), and `skill-invocations.md` binds each stage's invocation mode, source hash and output.

## 2. The workflow, stage by stage

Format per stage: **Types** (who, exact command) · **Window** · **Parent** · **Subagents** · **Records** · **Machinery** · **Working if**.

### 2.1 Setup (`/mattpocock-skills:setup-matt-pocock-skills`)

**Types:** user, once per repo and again after a plugin update (D1 §4; `S/setup:118`). **Window:** its own session; nothing else in it. **Parent:** answers the one-section-one-answer interview, lets the skill write only `docs/agents/{issue-tracker,triage-labels,domain}.md` and the `## Agent skills` block in `CLAUDE.md` (exists, so `AGENTS.md` is never touched: D1 §6.19). **Subagents:** none. **Records:** the three docs; a `skill-invocations.md` row "typed by user". **Machinery:** `gh label list` proves the five triage labels; `./dev/mise run check` after the write. **Working if:** the three files exist, the block is in `CLAUDE.md` only, labels resolve, no `SKILL.md` edited (`D/setup:86-90`). Open drift: the repo's `issue-tracker.md` has no "Wayfinding operations" section and no "PRs as a request surface" flag (D1 §4 table); 2.13 needs them.

### 2.2 Grill (`/mattpocock-skills:grill-with-docs`, or `/mattpocock-skills:grill-me` with no repo)

**Types:** user, with the idea as the argument. **Window A, unbroken** (principle 3); turn plan mode off; do not type `/pwf`, `/plan` or `/status` in it (side agent `a2a63789`'s finding stands). **Parent:** calls the Skill tool for `grilling` then `domain-modeling` (D1 §2 grill-with-docs); runs numbered rounds with `➡️` recommendations; dispatches fact-finding subagents rather than asking the user facts (`S/grilling:6-30`); updates `GLOSSARY.md` term by term inline; writes an ADR only when all three gates pass; stops and asks for confirmation of shared understanding before any action. **Subagents:** read-only fact lookups (Explore, extractor). **Records:** `GLOSSARY.md` diff, `docs/adr/NNNN-*.md` if any; everything else stays in the conversation. **Machinery:** `docs/agents/domain.md` makes `docs/accepted-decisions.md` the authority; a grilled decision that contradicts it must name the supersession. **Working if:** glossary changed during the session; few or no ADRs; a defined word got challenged (`D/grill-with-docs:68-72`); `git diff GLOSSARY.md` is non-empty before `/to-spec`, since an orchestrating parent can lose the file-writing half silently (`D:49`).

### 2.3 Detours: prototype, research

**Prototype** when a question needs a runnable answer: user types `/mattpocock-skills:handoff "prototype <question>"` (file in `$TMPDIR`), opens a fresh session in a separate directory, the session calls the Skill tool for `prototype` (model-invoked), captures on `prototype/<name>` out of the integration branch, user types `/mattpocock-skills:handoff "back to the idea thread"`, then references that file in Window A (`S/ask-matt:20-23`; D1 §6.18). Push of `prototype/*` waits for instruction (`AGENTS.md:50-51`). **Research** needs no keystroke: the parent calls the Skill tool for `research`; exactly one background agent, one cited Markdown file where the repo keeps notes (`evidence/` per `.claude/rules/evidence.md`, sanitized); provider calls go through the `fnox … codex_research` route and every attempted route is recorded (`AGENTS.md:54-60`). **Working if:** Window A keeps going while research runs; two random citations are primary (`D/research:65-69`).

### 2.4 Spec (`/mattpocock-skills:to-spec`)

**Types:** user, in Window A, right after grilling confirms. **Parent:** explores with glossary vocabulary; proposes test seams (prefer existing, ideally one) and **waits for the user's seam approval**; writes the seven-section template; does not interview (`S/to-spec:7-19`). **Publish step, repo form:** the skill wants one tracker issue labelled `ready-for-agent`; here the parent writes the draft to `.planning/<PLAN_ID>/proposals/<slug>/spec.md` plus `spec.manifest.json`, and publication runs `issue:create-preview` → `-apply` → `-verify` against that manifest only after the user says "publish" (`issue-tracker.md:26-29`). Label the parent spec `ready-for-agent` only after tickets exist, or exclude it from any AFK poll (`D/to-spec:42`). **Records:** `proposals/<slug>/spec.md`, manifest with SHA-256, the issue number once applied; `skill-invocations.md` row. **Working if:** starts writing instead of asking; seams shown first; no paths; out-of-scope lists real things (`D/to-spec:67-71`); no `/clear` or `/compact` between this and 2.5 (`D/to-spec:63`).

### 2.5 Tickets (`/mattpocock-skills:to-tickets <spec path or #issue>`)

**Types:** user, still Window A. **Parent:** gathers context, looks for prefactoring, drafts vertical slices each sized to one window and to the repo's unit limit (principle 7), **quizzes the user** (title, blocked-by, what it delivers; granularity, edges, merge/split) until explicit approval (`S/to-tickets:42-56`). **Publish, repo form:** `proposals/<slug>/tickets.preview.json` is the approved breakdown; `issue:create-*` publishes blockers-first as sub-issues of the spec; `issue:new-edge-preview/apply/verify` then `issue:new-edges-audit` wire native `blocked-by`; `issue:apply` adds `ready-for-agent` only after the edge audit (`issue-tracker.md:30-37`). The parent issue is never closed or modified (`S/to-tickets:67`). **Records:** issue numbers in `ticket-index.md`; `ticket-ledger.md` regenerated from the tracker; `skill-invocations.md` row. **Working if:** every ticket answers "what can I demo"; numbered list with Blocked-by shown before publishing; top ticket unblocked; no paths; prefactoring first (`D/to-tickets:84-89`). Window A ends here; the next move is decided by the tree (principle 9); the usual answer is `/clear`.

### 2.6 Build: `/implement` or `/implement-spec`

**Choice for this repo:** `/mattpocock-skills:implement-spec <spec #>` for any graph with more than one ready ticket; `/mattpocock-skills:implement <#ticket>` for a single ticket, one fresh window each, `/clear` between (D1 §6.4). Host-heavy tickets are always `/implement`, one at a time, each run confirmed by the user (`claude-team.md:81-84`).

**Types:** user, in a fresh Window B after `/clear`; planning-with-files re-injects the plan head and progress tail, the only state the orchestrator needs besides the tracker. **Parent (orchestrator):** reads spec + tickets as the task graph; optionally one exploration subagent whose notes land **outside the repo** (session scratchpad, pointer in `findings.md`); reuses the integration branch; dispatches implementers; computes the frontier from what has merged, not from GitHub's blocked-by count (`D/implement-spec:60`); communicates by context pointers. **Subagents:** `implementer` (Opus) or `doc-writer` (Sonnet) per ticket in the background; `reviewer`, `retro-writer`, merger. **Records:** `lanes/<unit>.json`, lane commits, `retros/<unit>.md`, ledger rows, `progress.md` entries. **Working if:** several implementers at once when the graph allows; a ticket starts when its last blocker lands; every trace shows red before green; merges are conflict-free; the run ends on one branch (`D/implement-spec:72-76`).

**Mapping of `implement-spec` onto the repo's machinery:**

| Skill element (`S/implement-spec`) | Repo element |
| --- | --- |
| integration branch (step 3) | `codex/marketplace-native-onboarding`; draft PR to `main` for visibility only, never merged (`claude-takeover.md:11`) |
| implementer worktree on its own branch (step 4) | `.claude/worktrees/<unit>` on `claude/<unit>-<slug>`; `lanes/<unit>.json` holds `base_sha`, `owned_paths`, `required_checks` |
| "confirms its worktree is based on the integration branch" | `implementer.md` step 1 (branch and base SHA match the record) |
| "calls the Skill tool with `tdd`" | `implementer.md` step 2; the agent frontmatter preloads `mattpocock-skills:tdd`; the trace must still show a failing test first |
| "merges the integration tip before reporting done" | `implementer.md` step 4; `doc-writer.md` step 5 |
| merger subagent (step 5) | the parent or a separately briefed merger (`claude-team.md:20`); checks `owned_paths`, merges `--no-ff` so `hk` `pre-merge-commit` fires (`hooks:install` sets `merge.ff=false`); `--no-commit` skips that layer (`claude-team.md:58-59`) and must not be used |
| "merges are fast-forwards" | read as "conflict-free after the implementer's tip merge"; the repo deliberately forbids true fast-forwards so a merge commit exists for the gate |
| re-kick the frontier (step 6) | ledger lane column; `ticket-ledger.md` regenerated; a lane's `status` is the only field the lane edits |
| one `code-review` after all tickets (step 7) | see 2.8: per-lane cold review stays; the end-of-spec review is added, by the parent calling the model-invoked `code-review` skill with fixed point = the spec's start SHA |
| "fix all issues in a single implementer subagent" | one more lane (`<spec>-review-fixes`) with its own record, cold review, retro and gate; stop after focused checks (`D/implement-spec:48`) |
| resolve tickets the tracker's way (step 8) | qualified close, one ticket at a time, with bound acceptance evidence; never by label |
| clean up worktrees (step 9) | `git worktree remove .claude/worktrees/<unit>` after the lane is published and closed; lane `status` gains `worktree removed`; currently eight remain (gap 6.4) |
| between tickets inside a lane | `/retro` is per session; the per-lane retro is the `retro-writer` (2.10) |

Gate hooks in Window B: `PreToolUse` denies `git merge`/`git push`/`delivery:publish` of a lane whose retro fails; `SubagentStop` blocks a lane subagent whose worktree lacks a passing record; `Stop` blocks the parent while any lane says `integrated` without `retro: passed` (`e12cf04:dev/hooks/*.py`). An orchestrator must therefore run `retro:gate -- <unit>` on the integrated tree and set `retro: passed` before it can end its turn; `delivery:publish` is the only push route (A09).

### 2.7 TDD (model-invoked `tdd`)

**Types:** nobody; the implementer calls the Skill tool for `tdd` (or has it preloaded) and `codebase-design` when the interface shape is open. **Rule:** no test at an unconfirmed seam; seams were approved in 2.4, so the ticket must name its seam (`D/implement:47`); red before green, one slice at a time; refactoring left to review (D1 §6.10). **Machinery:** `.claude/rules/dev-tests.md` (seam tests, hermetic `HOME`, discovery by `dev/check.py` or a `test:*` task listed in `check:research`). **Working if:** capability-named tests, literal expected values, mocks only at external boundaries (`D/tdd:79-84`).

### 2.8 Code review (model-invoked `code-review`; repo `reviewer` agent)

Two reviews exist and both stay:

- **Per lane (repo):** `reviewer` (Fable, read-only, cold) after the lane's tests pass, before retro and integration; fixed point `base_sha`, axes standards and spec, dispositions PASS / PASS-with-P2/P3 / FAIL, unrun checks named (`reviewer.md`). This is the gate the lane lifecycle requires (`claude-team.md:33`).
- **Per spec (skill):** when every ticket of a spec has merged, the parent calls the Skill tool for `code-review` with fixed point = the integration-branch SHA at which the spec's first lane was cut (recorded in the spec manifest), spec source = the spec issue. Two foreground sub-agents, `## Standards` and `## Spec` blocks, never merged or reranked, every finding cited (D1 §6.12). Findings go to one fix lane (2.6 table). Running it mid-spec reads unbuilt tickets as failures (`D/implement-spec:48`), so it runs once.

`CODING_STANDARDS.md` is mandatory input for both (`S/code-review:40`); the smell baseline is overridden by it. Commit before review; the three-dot diff ignores the working tree (`D/code-review:81`).

### 2.9 PR body (model-invoked `pr`)

Only when a draft PR to `main` is opened for visibility: the parent calls the Skill tool for `pr`; body = Summary (smallest visual), Evidence (before/after), Merge Danger; glossary language; the PR is never merged (`claude-takeover.md:11`).

### 2.10 Retro

Three things, in this order, per unit:

1. **`retro-writer` per lane (repo, automatic):** after review passes and before integration; writes `retros/<unit>.md` in the seven-category shape, applies every actionable finding by kind in the lane's `owned_paths`, lists cross-scope edits for the parent as literal edits, reruns `check` and `retro:gate -- <unit>` until both exit 0 (`retro-writer.md`). It reads the repo's own checks first (`dev/check.py`, `mise.dev.toml`, `.github/workflows`) so an unwired check is the finding (`S/retro:18`).
2. **`retro:gate` (mechanical):** shape and bindings only; judgement stays with the reviewer (`ticket-retro.md:59-63`).
3. **`/mattpocock-skills:retro` (user-typed, per session):** the user types it in Window B before clearing, or afterwards with the session log path as the argument (`S/ask-matt:38`). The session calls `writing-for-agents` first, reads primary sources, presents severity-ordered candidates across the seven categories, and stops. The user picks; the parent then dispatches a `retro-writer` (or doc-writer) lane to apply the picked candidates, with record, review and gate like any lane. This keeps "learnings applied automatically" (user's wish) inside the per-lane loop and keeps the session-level `/retro` honest about proposing only (`D/retro:35`).

**Working if:** every candidate points at a specific moment; repeat mistakes become failing checks and `AGENTS.md` gets shorter; existing-but-unwired checks get connected (`D/retro:63-66`); the applied edits land in the file that owns their kind (`CODING_STANDARDS.md:53-55`).

### 2.11 Handoff

`/mattpocock-skills:handoff "<what the next session does>"` is typed by the user only for a **new harness** (Codex resuming after 2026-10-19), a **new directory** (prototype), a **colleague**, or a **mid-phase fork** (D1 §6.16; `PHASE-BOUNDARIES.md:27-34`). The file lives in `$TMPDIR`, references artifacts by path, redacts secrets; copy it into the session scratchpad because temp is cleared (`D/handoff:48`). It is not the way to survive `/clear` in the same harness and directory: that is planning-with-files recovery (`SessionStart`/`UserPromptSubmit` inject `task_plan.md` head and `progress.md` tail) plus the ticket. The repo's durable handoff is the "Session handoff" block in `task_plan.md` and `docs/agents/claude-takeover.md`; `/handoff` output points at them rather than restating them.

### 2.12 Triage and the inherited #69–#108

`/triage` is for issues you did not create, and never for `to-tickets` output (D1 §6.14; `S/ask-matt:48`). #69–#78, #90–#108 are `to-tickets` output of specs #11 and #83 (published by the Codex threads under the same maintainer), and #79–#83 are specs. None of them is triage input. Their route is 2.6: regenerate `ticket-ledger.md` from the tracker (`blockedBy`, `parent`), take the frontier, allocate lanes. `/mattpocock-skills:triage` is typed by the user only for issues or external PRs that arrive from outside; every posted comment then starts with the AI disclaimer, exactly one category and one state label (`S/triage:13-17,41`), posted through `issue:preview/apply/verify`. The five labels in `docs/agents/triage-labels.md` are already the canonical ones.

### 2.13 Wayfinder for the C++26 P2996 core

The native core is "too big for one session", the wayfinder case (`D/grill-with-docs:45`). **Types:** user, `/mattpocock-skills:wayfinder <destination>` in its own window. **Precondition:** `docs/agents/issue-tracker.md` must carry the Wayfinding operations block (map label, child issues, native blocking with database ids, frontier query, claim, resolve); it does not today, so 2.1 re-runs first. **Parent:** calls `grilling` and `domain-modeling` to name the destination; breadth-first; creates the `wayfinder:map` issue and child decision tickets through `issue:create-*`, wires edges in a second pass with real ids through `issue:new-edge-*`; never puts triage labels on them; refers to tickets by name (`S/wayfinder:17,65,111-116`). Research tickets spawn `research` subagents onto `research/<name>` branches, which stay local until an admitted A09 publish (`AGENTS.md:50-51`). **Work sessions:** one ticket per session, claimed by assignee, resolved as its labelled type, resolution comment appended to "Decisions so far" (`S/wayfinder:105,122-126`). Decisions must not contradict `docs/accepted-decisions.md` without naming the supersession (`domain.md:9-12`). **Exit:** when the fog is gone the user types `/mattpocock-skills:to-spec #<map>` in a new Window A (`D/to-spec:46`).

### 2.14 File-guided execution: what it is, when it is acceptable, how to record it

Reading `S/<name>` and following it is not an invocation of that skill. Differences: no slash-command frontmatter processing, no `argument-hint`, no guarantee the session loaded the dependency skills, and no harness record. It is acceptable only (a) for the step body of a **model-invoked** skill the session chose not to load (never preferable; load it), or (b) for a **user-invoked** skill when the user has, in that session, explicitly asked the session to follow that `SKILL.md` as text for a named stage; a standing authorization from an earlier round does not make a later stage "invoked". Every file-guided stage gets a `skill-invocations.md` row with source path, SHA-256, mode `file-guided`, who asked, and the output pointer; the activation record and any retro must call it "file-guided", never "invoked" or "ran". When the user later types the real command, the row gains the new mode (`skill-invocations.md:7-9`). The skill's own completion criteria still apply (section 5).

## 3. Resolution of overlaps

1. **`/retro` vs `retro-writer` vs `retro:gate`.** Different objects: `/retro` reviews a *session* and proposes; `retro-writer` reviews a *lane* and applies; `retro:gate` checks a *record*. Keep all three (2.10). The per-lane application is automatic because the lane's own record must pass the gate before integration (ADR 0001); the session-level proposals need a human pick, then become a lane. `docs/agents/ticket-retro.md:4-8` should say this rather than claiming the standing request is "the invocation authority" for a user-invoked skill (gap 6.1).
2. **`code-review` vs `reviewer`.** Same two axes, same fixed-point rule. The `reviewer` agent is the per-lane instance; the skill is the per-spec instance (2.8). The reviewer's extra standards items (baseline hashes, `owned_paths`, contracts) are repo overrides of the smell baseline, which the skill already allows (`S/code-review:40`).
3. **`/handoff` vs planning-with-files recovery.** pwf = same harness, same directory, after `/clear` or compaction, automatic, bounded injection. `/handoff` = portability to another harness, directory or person, typed by the user. Codex resume → `/handoff`; `/clear` between `/implement` runs → pwf plus the ticket; mid-phase fork → `/handoff`, not a new pwf plan.
4. **`/implement` + `/clear` vs `/implement-spec`.** This repo's graphs (#11's 50 tickets, #83, CT-01…CT-11) are multi-ticket with native edges and the harness runs background worktree subagents, so `/implement-spec` is the default; `/implement` is for host-heavy lanes (serialized, confirmed per run) and single fixes. Both end with the lane lifecycle receipts.
5. **`GLOSSARY.md`/ADR rules vs `docs/agents/domain.md`.** No conflict: `domain.md` is the consumer rule and adds the `accepted-decisions.md` supremacy; `domain-modeling` is the producer rule (lazy, three gates, glossary is vocabulary only). The glossary's "Workflow" section must stay vocabulary (D1 §6.13); workflow procedure lives in `claude-team.md`.
6. **Triage labels.** The repo's five labels equal the canonical roles; `ready-for-agent` is applied through `issue:apply` after the edge audit and never means "unblocked" (`triage-labels.md:11-12`). AFK pollers must also check native blockers.
7. **Fast-forward merges.** Skill wants fast-forwards; repo forbids them so the `hk` gate has a merge commit. Resolution in 2.6: implementer merges the tip (conflict-free), merger uses `--no-ff`, never `--no-commit`.

## 4. What the parent asks the user to type, and what it does itself

**Parent does itself (no keystroke):** Skill tool calls for `grilling`, `domain-modeling`, `tdd`, `code-review`, `pr`, `research`, `prototype`, `writing-for-agents`, `codebase-design`, `diagnosing-bugs`; lane allocation, worktrees, subagent dispatch, merges, `retro:gate`, `issue:*-preview/-verify`, `delivery:prepare`, ledger regeneration, `skill-invocations.md` rows. **Parent asks before:** `issue:*-apply`, `delivery:publish`, qualified close, host-heavy runs, anything in `AGENTS.md:49-51`.

Script, in order:

1. "Setup has drifted. In a fresh session run `/mattpocock-skills:setup-matt-pocock-skills`; I will diff `docs/agents/*.md` afterwards."
2. "Fresh session, plan mode off: type `/mattpocock-skills:grill-with-docs <idea>`. No `/clear` or `/compact` until tickets are published; I will flag 150k at the next boundary."
3. (shared understanding confirmed) "Type `/mattpocock-skills:to-spec`. I show seams first and wait for your approval."
4. "Draft at `proposals/<slug>/spec.md` (SHA …). Say `publish spec` and I run `issue:create-preview/apply/verify`."
5. "Type `/mattpocock-skills:to-tickets proposals/<slug>/spec.md` (or `#<n>`). I present the numbered breakdown with Blocked-by and wait."
6. "Approved breakdown is in `tickets.preview.json`. Say `publish tickets` and I run `issue:create-*`, `issue:new-edge-*`, `issue:new-edges-audit`, then `issue:apply` for `ready-for-agent`."
7. "Window A is done. `/clear`, then type `/mattpocock-skills:implement-spec #<spec>`. I orchestrate lanes, one cold review and retro each, and ask before every `delivery:publish`."
8. (host-heavy ticket) "`/clear`, then `/mattpocock-skills:implement #<ticket>`; confirm the heavy run when I ask."
9. (end of a build session) "Before `/clear`, type `/mattpocock-skills:retro`; pick candidates and I apply them through a gated retro-writer lane."
10. (Codex resume, prototype, colleague) "Type `/mattpocock-skills:handoff \"<purpose>\"`; I copy the file from `$TMPDIR` into the scratchpad and point `task_plan.md` at it."
11. (external issue) "Type `/mattpocock-skills:triage #<n>`; I recommend one category and one state and post through `issue:apply` with the disclaimer."
12. (native core, after 1) "Type `/mattpocock-skills:wayfinder \"C++26 P2996 research core\"` in its own session; one decision ticket per later session."

## 5. Per-stage grading checklist (binary; source rule)

**Invocation and records**
1. Every stage row in `skill-invocations.md` names mode (`typed by user` / `native Skill tool` / `file-guided`), source path, SHA-256, invoker, output (`skill-invocations.md:3-9`).
2. No document calls a file-guided stage "invoked", "ran" or "natively" (D1 §1; `invocation.md:8`).
3. No subagent or skill was asked to run a user-invoked skill (`invocation.md:8,22`).
4. Model-invoked skills were loaded through the Skill tool, one per call, not paraphrased (`invocation.md:16-20`).

**Setup**
5. `docs/agents/{issue-tracker,triage-labels,domain}.md` exist and `## Agent skills` is in `CLAUDE.md` only (`D/setup:86-90`).
6. The five labels exist on GitHub (`gh label list`) (`S/setup:104`).

**Grill**
7. User typed `/grill-with-docs`; the trace shows Skill calls for `grilling` and `domain-modeling` (`S/grill-with-docs:7`).
8. Questions were numbered rounds with `➡️` recommendations and a `---` separator; "yes" accepted recommendations (`S/grilling:6-30`).
9. Facts were looked up (subagent or tool), not asked (`S/grilling`; `D/grilling:77-83`).
10. The session stopped and obtained confirmation of shared understanding before acting (`S/grilling:30`).
11. `GLOSSARY.md` changed during the session and holds vocabulary only; any ADR passes all three gates (`S/domain-modeling:40,64,68-74`).

**Spec**
12. Seams were presented and approved by the user before the spec was written (`S/to-spec:15`).
13. The spec follows the seven sections, uses glossary nouns, contains no paths or line numbers (`S/to-spec:19,55`).
14. No `/clear` or `/compact` occurred between grill, spec and tickets (`S/ask-matt:38`; `D/to-spec:63`).
15. The spec was published only through `issue:create-*` after explicit user approval, or stays a local draft with a named blocker (`issue-tracker.md:19-29`).

**Tickets**
16. A numbered breakdown with Title / Blocked by / What it delivers was shown and the user approved granularity and edges before any publish (`S/to-tickets:42-56`).
17. Every ticket is a vertical slice sized to one window and the repo unit limit; prefactoring first; top ticket unblocked (`S/to-tickets:31-34`; `codex-task-orchestration.md:204`).
18. Tickets contain no paths or line numbers; lane records carry the allowlist (`S/to-tickets:105`; `planning-records.md`).
19. Published tickets are sub-issues with native `blocked-by`, blockers first; the parent issue untouched; edges audited; `ready-for-agent` applied after the audit (`S/to-tickets:62-67`; `issue-tracker.md:30-37`).

**Build (implement-spec / implement)**
20. The build started in a fresh window after `/clear` (`S/ask-matt:26,38`; `D/implement-spec:40`).
21. Each lane has `lanes/<unit>.json` written by the parent before dispatch, with `base_sha` equal to the integration tip at cut (`planning-records.md`; `S/implement-spec:28`).
22. Implementers ran in the background, several at once when the frontier allowed, up to four offline, host-heavy serialized with per-run confirmation (`S/implement-spec:17`; `claude-team.md:81-84`).
23. Every implementer trace shows a failing test before code at a seam the ticket names (`S/tdd:22,36`; `D/implement-spec:74`).
24. Each implementer merged the integration tip and reran checks before reporting (`S/implement-spec:30`; `implementer.md:4`).
25. Exploration notes, if any, were saved outside the repo and pointed to (`S/implement-spec:23`).
26. The frontier was recomputed from what merged, and a ticket started when its last blocker landed (`D/implement-spec:60,73`).
27. Communication used context pointers; subagent briefs did not paste spec or ticket bodies (`S/implement-spec:15`).
28. Merges were `--no-ff` without `--no-commit`, by the parent or a briefed merger that checked `owned_paths` (`claude-team.md:20,55-59`).
29. Unit size stayed near five files / 300 lines or the split was reported (`implementer.md:3`).

**Review**
30. Each lane got a cold `reviewer` pass with a resolving fixed point and non-empty diff, two unmerged axes, cited findings, a disposition and the unrun checks named (`reviewer.md`; `S/code-review:19-23,66-80`).
31. One `code-review` Skill call ran over the integration branch after all tickets of the spec landed, not mid-run; its findings went to one fix lane (`S/implement-spec:36`; `D/implement-spec:48`).
32. `CODING_STANDARDS.md` was an input to every review once it existed (`S/code-review:40`).

**Retro**
33. Every lane, partial or blocked included, has `retros/<unit>.md` with seven categories, a verification binding and no ownerless open finding; `retro:gate -- <unit>` exit 0 recorded on the integrated tree (`ticket-retro.md:59-68`).
34. Each actionable finding was applied in the file that owns its kind, with a verification command and exit, or rejected with evidence, or deferred with owner and condition (`CODING_STANDARDS.md:49-55`).
35. `/retro` (session level) was typed by the user in the session or pointed at its log, loaded `writing-for-agents` first, and proposed without writing (`S/retro:11`; `D/retro:35`; `S/ask-matt:38`).
36. Session-level `/retro` picks were applied through a gated lane, not by direct parent edits.

**Integration, publication, closure**
37. `hooks:install` ran once in the real checkout before the first gated merge; `test:hooks` is in `check:research` (`claude-team.md:55-57`).
38. Publication went through `delivery:prepare`/`delivery:publish` with the remote SHA recorded; no bare `git push` (`claude-takeover.md:11`; `claude-team.md:36`).
39. Tickets were closed one at a time through the qualified close with bound evidence; no label, issue creation or merge counted as closure (`issue-tracker.md:37-40`).
40. Worktrees of published, closed lanes were removed and the lane record says so (`S/implement-spec:39`).

**Context hygiene and handoff**
41. Every `/clear`, `/compact`, `/handoff` or subagent split happened at a phase boundary with the tree's order visible in the record (`PHASE-BOUNDARIES.md:19-40`).
42. `/handoff` was typed by the user, wrote to `$TMPDIR`, referenced artifacts by path, redacted secrets, and was copied to durable storage (`S/handoff:8-14`; `D/handoff:48`).
43. The parent did not create a competing pwf plan in the tree; `PWF_PLAN_ROOT`/`PLAN_ID` stayed pinned (`.planning/AGENTS.md`).

**Triage and wayfinder**
44. No `to-tickets` output (#69–#78, #90–#108) was triaged; any triage comment carries the disclaimer, one category and one state (`S/ask-matt:48`; `S/triage:13-17,41`).
45. Any wayfinder map used `wayfinder:` labels only, real ids, one ticket per work session, and ended at `/to-spec #<map>` (`S/wayfinder:65,105,114`).

## 6. Gaps and decisions for the user

1. **Invocation authority wording.** `docs/agents/ticket-retro.md:4-8` and `claude-takeover.md:11` treat a standing request as invocation authority for a user-invoked skill; the sources do not allow that (D1 §6.1). Decide: rewrite to "the per-lane retro-writer runs under the repo protocol; `/retro` is typed per session", and keep `skill-invocations.md` as the binding record.
2. **Setup drift.** The repo's `issue-tracker.md` lacks the Wayfinding operations block and the PR-surface flag; upstream seeds changed after install. Re-run setup (2.1) before any `/wayfinder`.
3. **Publish mapping.** `to-tickets` and `implement-spec` assume `gh issue create`/close; this repo requires `issue:create-*`, `issue:new-edge-*` and the qualified close. Record that mapping in `issue-tracker.md` under "When a skill says publish / fetch / resolve" so the skills read it (the seed has that heading).
4. **Worktree cleanup.** Eight lane worktrees remain; `implement-spec` step 9 removes them. Decide when: after publish and close (proposed), or keep for audit until the retro cycle ends.
5. **Fast-forward vs `--no-ff`.** Confirm the reading in 3.7; it changes nothing in the hooks but should be stated in `claude-team.md`.
6. **Spec-level `code-review` fixed point.** Decide where the spec's start SHA is recorded (proposed: `spec.manifest.json`), since lane `base_sha` values differ per lane.
7. **`/implement` on host-heavy tickets.** The skill commits on the current branch; the repo wants a lane worktree even for serialized heavy work. Decide whether heavy tickets get a lane record and worktree (proposed) or run on the integration branch under per-run confirmation.
8. **Session-level `/retro` cadence.** Per build session (proposed) versus per ticket; the per-ticket retro is already the retro-writer.
9. **Research branches from wayfinder.** `research/<name>` branches must stay local until an admitted A09 publish, which the skill does not expect; state it in `issue-tracker.md`.
10. **AskUserQuestion preference.** The user asked for a native question tool; the sources put per-user preferences in the repo's `CLAUDE.md`, not in skills (D1 §6.20). Decide whether to add a one-line rule that grilling rounds also go through `AskUserQuestion` with free text.
11. **Per-lane vs per-spec review cost.** Two reviews per ticket-graph is more than the skill asks; accept the cost (proposed, since the lane gate needs it) or drop the spec-level pass for documentation-only specs.

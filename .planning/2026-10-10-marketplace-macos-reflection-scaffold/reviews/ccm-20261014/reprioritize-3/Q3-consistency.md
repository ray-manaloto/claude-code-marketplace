# Q3 consistency audit after grill rounds 3-5 and the project import (2026-10-14, read-only)

Scope: decisions D83-D100 (DL-105..DL-130), tickets CT-59..CT-79, the w0-session-hooks closure (D97). Read on
HEAD `21af565` (= origin) with the working tree as found: 9 modified, 29 untracked top-level entries.
Abbreviations: P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`; TP `P/task_plan.md`, TL
`P/ticket-ledger.md`, PR `P/progress.md`, DJ `P/decisions.jsonl` (line N = DL-N), HO
`P/reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md`, TPL `.claude/skills/session-handoff/references/handoff-template.md`
(its `.agents/` mirror is byte-identical, `cmp` rc 0, so every TPL row applies to both), CTM
`docs/agents/claude-team.md`, AG `AGENTS.md`, CA `.claude/AGENTS.md`, GL `GLOSSARY.md`, A2
`P/reviews/ccm-20261014/project-import/A2-typescript-mods-library.md`, P3a = the earlier audit
`P/reviews/ccm-20261014/reprioritize-2/P3-plan-consistency.md`. `Q2-order.md` did not exist when this audit ran
(`reviews/ccm-20261014/reprioritize-3/` was absent), so section 3 lists the dependent surfaces, not Q2's values.

Severity: P1 = contradicts an accepted decision in a surface that drives the next session's actions or the spec
fold (Next Step, template, HANDOFF runbook, fold range, ticket rows the fold copies); P2 = stale or mismatched state
with a correct source elsewhere; P3 = wording, provenance or history.

Counts: P1 10, P2 32, P3 25.

## 1. Findings

| id | sev | file:line | current text | replacement |
|---|---|---|---|---|
| Q3-01 | P1 | TP:12-13; TPL:12-13 (same text at PR:775, report only) | "Never start an unpublished ticket outside Phase 4b." | "Before publication start only waves pre to 0c and the gate's read-only CT-34 audit (D77, D86); every later Phase 4b row waits for the typed stages (D90)." Phase 4b holds waves 1-20, so the current rule admits every unpublished ticket. |
| Q3-02 | P1 | TP:11; TPL:11; HO:76-92 (§2(b)); HO:300-301 (§3.5 item 3); TL:153 | "Integrate w0-doctor (`f1bbc8d`) per HANDOFF §2(b)"; §3.5 item 3 appends a Hook composition bullet "`SessionStart` (...) runs `dev/doctor/cli.py --surface session-start`"; TL "w0-doctor owns the settings SessionStart entry" | The lane adds a settings `SessionStart` hook (`git diff 21af565...f1bbc8d -- .claude/settings.json`, +13 lines, timeout 15). D92 deletes every owned settings hook in the change that replaces it, and no D row admits a new one. Add before §2(b) step 2: "Ask the user (an exception to D92): integrate w0-doctor as reviewed, its SessionStart doctor hook dated until A2-11 replaces it with the doctor-context mod and deletes the entry (A2 §4 'Integration order'), or strip the hunk and re-review. Record the answer as a D row before the merge." §3.5 item 3 and TL:153 then add "replaced by A2-11 (D92)". |
| Q3-03 | P1 | TP:36; TP:234 (gate row); HO:69-71 (§2(a2)) | "fold CT-25..CT-59 and D59..D90" | "fold CT-25..CT-79 (CT-59's units 59a..59f2 and the A2 units under their tickets; D72 closures, D85 splits and merges, CT-28 dropped) and D59..D100" |
| Q3-04 | P1 | HO:198-203 (§2(j) item 3, the wording given to the user) | "approve the revised breakdown: C4's CT-01..CT-24 (+CT-02b), CT-25, CT-26, CT-28, CT-29, ... CT-41..CT-58 (D81), CT-59 (D88); CT-27 and CT-28 are not filed; ... the D82 splits and merges as the user approved them." | "...CT-25, CT-26 (26a, 26b), CT-29 (29a, 29b), the Y-series CT-30, CT-31 (31a, 31b; closes CT-13 as a duplicate), CT-32a, CT-32b and CT-33, the U-series CT-34..CT-39 (CT-38a, 38b), CT-40, the TR import CT-41..CT-58 (D81; CT-20a, 20b), CT-59 (D88) and the project import CT-60..CT-79 (D87); CT-27 and CT-28 are not filed; CT-09, CT-13 and CT-24 are closed (D72); the D85 splits and merges." (CT-28 is listed as approved and as not filed today.) |
| Q3-05 | P1 | TP:443; TL:166 (CT-35) | "Session-start mod in this repository's local directory plugin (...) plus the settings SessionStart hook for `/clear` (U2; D61, D66, D87)" | "Session-start mod on the mods library (A2-22, A2-23): names the session and awaits `/reload-skills` and `/reload-plugins --force` before the first request; the title after `/clear` comes from `classic.UserPromptSubmit`; no settings hook (D87, D92, D93)" |
| Q3-06 | P1 | TP:444; TL:167 (CT-36) | "webclaw-over-WebFetch mod in this repository's local directory plugin, its PreToolUse deny backstop and the `web:fetch` mise task (U3; D62, D87)" | "WebFetch mod (`tool.call` answers through `web:fetch`, denies on failure) and the `web:fetch` mise task (A2-24, A2-25); no settings backstop (D87, D92, D95)" |
| Q3-07 | P1 | TP:287-288 | "Dotfiles repo, outside this plan's lanes: the shared session-start mod (D66) and the webclaw mod and hook (D62); CT-35 and CT-36 here verify them (D74)." | "Both mods are built here on the mods library (CT-35, CT-36; D87, D92); nothing is built in the dotfiles repo, which CT-62 sunsets (D96)." |
| Q3-08 | P1 | TL:133 (CT-02b local state) | "allocated: w0-session-hooks (corpus fixture slice, 2026-10-14; sequenced after w0-doctor)"; "fail-closed logic moves into `stop_gate.py`/`subagent_stop_gate.py` (exit 2 on internal error) and the two `onFailure` lines go; seeded in w0-session-hooks" | "w0-session-hooks closed before cut (D97). The Stop and SubagentStop gates become mods and both scripts and settings entries are deleted (A2-7, D92); the corpus is A2-8; the D58 `if` field is moot (A2-9); the rest is A2-15..A2-18." |
| Q3-09 | P1 | TL:163; TP:440 (CT-32b) | Blocked by "CT-32a, w0-session-hooks, CT-02b (same `pretooluse_gate.py` and `dev/test_hooks.py`)"; owned_paths "`dev/hooks/{stop_gate,subagent_stop_gate,pretooluse_gate}.py`, two `dev/test_hooks.py` tests" | Blocked by "CT-32a, A2-7 and A2-15 (CT-02b)"; owned paths: unit A2-20 on the mods library (`stop-gates.ts`, `bash-gate.ts`, `lib/verify.ts` and their tests); no `dev/hooks/` edit (D92). A closed lane as blocker never clears. |
| Q3-10 | P1 | TP:461; TL:184 (CT-53) | "P2996 JSON Schema emitter as a cxx split unit: reflected structs emit schemas byte-equal to CT-52's files (T-a-cxx)" | "P2996 reflection check as a cxx split unit: the C++ records #26 generates from the committed schemas map back to identical schemas; nothing generates schemas from C++ (D83)" |
| Q3-11 | P2 | TP:15-21; HO:40, 53 (§1, generated); PR:772-778 (report only) | rev 12 block: "allocated: ... w0-session-hooks (not cut)"; "Pending operations ...: DL-3, DL-4"; "Pending user: grill round 3, Q39-Q55 (...; includes D82's four questions and the Docker volumes)" | Regenerate with `dev/handoff.py write` after the TPL edits: w0-session-hooks closed (D97); pending operation DL-4 only (DL-3 closed by DL-109, receipt DL-110); pending user per Q3-12. |
| Q3-12 | P2 | TPL:20-21; HO:133-139 (§2(f)) | "Pending user: the typed stages at the gate (...); the third reprioritization after the project-import review lands"; "(f) ... settled Q39-Q57 as D83-D91 ... Still open: the third reprioritization once `reviews/ccm-20261014/project-import/` lands (D87)" | "Pending user: the w0-doctor SessionStart exception (Q3-02); Q68, Q70, Q71 after `reviews/ccm-20261014/research5/` R1-R3 (D100); the typed stages at the gate (HANDOFF §2(j), D90)." (f) adds: "Rounds 4-5 settled Q58-Q71 as D92-D100 (DL-122..DL-130); the third reprioritization is `reviews/ccm-20261014/reprioritize-3/`." |
| Q3-13 | P2 | TPL:27-30, 33-35 | "Order: plan Phase 4b (D65, D68-D82; ADR 0005); grill answers D63-D80"; "D82 proposes splits of CT-20, CT-26, CT-29, CT-38 and merges, for the user at the spec fold."; round-3 note only | "Order: plan Phase 4b (D65, D68-D100; ADR 0005, ADR 0007); grill answers D63-D100; reports `reviews/ccm-20261014/` (grill-facts, reprioritize, reprioritize-2, project-import, reprioritize-3)"; "D85 approved the splits of CT-20, CT-26, CT-29, CT-38 and the merges"; add "Rounds 4-5 (D92-D100): mods replace every owned settings hook (ADR 0007), w0-session-hooks closed, TypeScript mods library (A2), CT-60..CT-79." Copy to the mirror; notes drop first under the 16-line budget. |
| Q3-14 | P2 | TP:27; TP:361; TL:11; HO:209; DJ:104 (DL-4 scope) | "file CT-01..CT-59"; "the revised breakdown CT-25..CT-59"; "CT-01…CT-59"; "re-grilled ... for CT-25..CT-59"; DL-104 "covers CT-01..CT-58" | "CT-01..CT-79" (CT-25..CT-79 at TP:361 and HO:209); append a DL row widening DL-4 to CT-01..CT-79 (+CT-02b, CT-20a/b, CT-26a/b, CT-29a/b, CT-31a/b, CT-32a/b, CT-38a/b; CT-27 and CT-28 not filed; CT-09, CT-13, CT-24 closed). |
| Q3-15 | P2 | TP:91, 112, 121-122 (Phase 4) | "W0-3 `dev/context_budget.py`, `dev/hooks/agent_gate.py`, `dev/hooks/prompt_hook.py`"; "[ ] w0-session-hooks (...): allocated, sequenced, integrates last"; "fail-closed Stop/SubagentStop goes to w0-session-hooks (CT-02b class)"; "two sequenced" | "[x] W0-3 cancelled with lane w0-session-hooks (D97): context budget, prompt hook and agent gate become mods A2-12..A2-14 (CT-23), never created as files"; "[x] w0-session-hooks: closed before cut (D97)"; "fail-closed Stop gates: A2-7 (CT-02b)"; status "one sequenced (w0-doctor-records)" |
| Q3-16 | P2 | TP:137-138 (U2); TP:149-150 (U4); TP:204; TP:207-208 | "The mod is the shared dotfiles mod (D66); CT-35 is its backstop hook and adoption test (D74)"; "no settings file pins it (D54 accepted, DL-65; not yet applied)"; "D62 (U3 webclaw mod plus hook backstop)"; "D62 (user-level U3 hook in dotfiles) ... Open: DL-3 (held)." | "The mod is built here on the mods library (D87, D92, D93; CT-35)"; "`.claude/settings.local.json` `env` pins both since D91 (DL-119..DL-121)"; "D62 (U3 webclaw mod; backstop dropped by D92, D95)"; "D62 (built here, D87) ... DL-3 cancelled (DL-109, receipt DL-110)." |
| Q3-17 | P2 | TP:235, 245, 246, 250, 251, 252 (Phase 4b cells) | wave 1 "user pins `settings.local.json` (D54)"; 11 "CT-36 `web:fetch` and WebFetch backstop", "webclaw pin; one live page"; 12 "one crawl (at most 60 pages), disk"; 16 "one clone, disk"; 17 "CT-35 session-start backstop", "dotfiles mod present (D66)"; 18 "user: plugin version; `claude` in CI" | wave 1: drop (done, D91); 11: "CT-36 WebFetch mod and `web:fetch`", "webclaw pin; downloads under D86"; 12 and 16: "D86 standing admission; receipts record pages and robots status (D98)"; 17: "CT-35 session-start mod", drop the D66 cell; 18: "`version` 0.1.0 at CT-08; `claude` in the host fast check (D89)". Carry into Q2's table (section 3). |
| Q3-18 | P2 | TP:310-316 (CT-33 import rows); TP:347-350; TP:441 and TL:164 (CT-33 blocked by) | "bounded TOML manifest ... disk gate 60 GiB plus twice the source cap"; "Admissions they need ...: webclaw version pin, one live crawl, one repo clone and disk (CT-33, CT-42); about 10 live pages for the CT-33 spike; ... transcript reads (CT-34, CT-20, CT-51); ... `claude` in CI (CT-26, CT-57)"; "webclaw install and one live-crawl admission" | "TOML manifest; no page, source, clone, robots or disk cap (D86); pages fetched and robots status recorded as receipt data (D98)"; admissions: "webclaw pin; downloads under D86's standing admission; CT-34 transcripts admitted (D86); live transcript reads for CT-20, CT-51; `claude` in the host fast check (D89)"; blocker: "webclaw install (pin)" |
| Q3-19 | P2 | TP:449, TL:172 (CT-41); TP:450, TL:173 (CT-42) | "robots parse, ... page-cap truncation"; "size cap"; TL:173 "admissions: one clone" | "robots status and pages fetched recorded as data, never caps (D98)"; "size recorded, no cap (D86)"; "admissions: D86 standing". If caps stay as opt-in code options, record that as a D row first. |
| Q3-20 | P2 | TL:164 (CT-33 local state) vs TP:315-317 | owned_paths "`dev/offline_corpus.py`, `dev/test_offline_corpus.py`, ..., `dev/offline-sources.toml`"; "parent adds `/offline/` to `.git/info/exclude`" | "modules under `python/src/marketplace_dev/offline/` (CT-39 package, TP:315); `/offline/` in `.gitignore` after CT-08, no `.git/info/exclude` entry (TP:317)" |
| Q3-21 | P2 | TP:442; TL:165 (CT-34) | Blocked by "spec publication (D59)"; TL frontier "held" | Blocked by "none: runs at the gate before the fold under the transcript admission (D86 a)"; frontier "ready at the gate" |
| Q3-22 | P2 | TP:437; TL:160 (CT-30) | "never concurrent with w0-session-hooks on `.claude/settings.json`" | delete the clause (D97) |
| Q3-23 | P2 | TP:438; TL:161 (CT-31) | "(`plugins/workflow-mods/`; subsumes CT-13)"; TL "D55 display-only; owned_paths `plugins/workflow-mods/**`"; 31a blocked by "CT-02 (done), w0-doctor" | "`.claude/skills/workflow-mods/` (skills-dir plugin) and `mods/` (A2 §2.1); CT-31a = the library foundation A2-0..A2-6 plus the status band A2-26, blocked by CT-26a, CT-26b, CT-38a and a fresh-session admission (A2-0); D55 superseded by D92; D94" (A2 §4 lists this as an unapplied parent hunk) |
| Q3-24 | P2 | TL:188 vs TP:465 (CT-57) | "user: plugin `version`"; "admissions: `claude` CLI in the CI image (CT-26b; which job is UNVERIFIED, P2 §4)" | as TP:465: "`version` 0.1.0 and the host fast check (D89)"; admissions "none beyond CT-26b's install" |
| Q3-25 | P2 | TL:154 (CT-23) | "allocated: w0-session-hooks (wave-0 seeds, 2026-10-14)"; "CT-23 decides the pin route (X1 §2 row 7 ...)" | "w0-session-hooks closed (D97); seeds are A2-12..A2-14, follow-ups A2-19"; "CT-37 owns the carrier (D73); pins landed (D91)" |
| Q3-26 | P2 | TL:34 (#26) | "cxx · wave 10 (after the #24 close; schema direction D82 Q1)" | "... schema direction D83" |
| Q3-27 | P2 | TL:87-90 (#79-#82); TL:257-259 (T4 state); TP:506 (#101) | "a new attempt needs a new user-approved budget (D25)"; "A new attempt needs a fresh user-approved budget, ... (D25)."; "#101 T4 (blocked; attempt 3 STOPPED/NOT_COMPLETED, budgets 3/3, D25)" | #79-#82: "close as ordinary qualified closes under D86's standing close admission (DL-109)"; T4 state ends "No fourth attempt: cancelled 2026-10-14 (DL-109, D90); #101 closed not planned (DL-107)."; TP:506 "#101 T4 closed not planned (D90, DL-107)" |
| Q3-28 | P2 | TL:99 (#91) | "relabel → `ready-for-human` accepted in round-1 Q6, not applied (still `ready-for-agent`, P1-9)" | "relabelled `ready-for-human` 2026-10-14 (DL-97); the user's after Codex returns on 2026-10-19 (D90)" (open since P3a N26) |
| Q3-29 | P2 | TP:565 (D26), 599 (D58), 602 (D61), 603 (D62), 607 (D66) status cells | D26 "approved 2026-10-13"; D58 "accepted 2026-10-14 (parent; DL-59)" with text "lands in w0-session-hooks"; D61 "...name format and mod location revised by the grill, see text and D66"; D62 "...location amended by D87: built in this repository"; D66 "...location amended by D87: built in this repository as a local directory plugin" | append: D26 "; integrate-last rule lapsed (D97)"; D58 "; moot: A2-9 replaces the settings Bash gate (D92, D97)"; D61 "; the settings-hook backstop and the `/clear` SessionStart hook superseded by D92; reloads restated by D93"; D62 "; the PreToolUse backstop superseded by D92, D95"; D66 "; the settings SessionStart hook superseded by D92" |
| Q3-30 | P2 | TP:612-614 (D71, D72, D73), 618 (D77) status cells | "accepted 2026-10-14 (user, grill-with-docs round 2, ...; DL-87)" and likewise DL-88, DL-89, DL-93 | append: D71 "; amended by D85 (CT-26a and CT-29a precede CT-39)"; D72 "; amended by D85 (CT-12 wiring into CT-39, CT-56 into CT-07, CT-58 into CT-38b)"; D73 "; amended by D85 (CT-29a, 29b) and D91 (pins landed)"; D77 "; fold range superseded by D82 and now D59..D100 (Q3-03); w0-session-hooks cancelled (D97)" |
| Q3-31 | P2 | TP:641 (D100); DJ:130 (DL-130) vs AG:54-56 | D100 "providers run through the fnox research profile"; DL-130 "this repository's fnox research profile" | No fnox config is tracked here (`git ls-files` has no fnox file); AG names the user-level `codex_research` profile. Append a DL row: "the user-level `codex_research` profile (AGENTS.md) until CT-76 adds a repository profile", or name the ticket that creates it. |
| Q3-32 | P2 | TP:640 (D99) | D99 has no owner ticket; cited nowhere outside the Decisions table | Add to a ticket's acceptance (CT-64 or a CT-31a unit): "`plugins/aggregated-research/hooks/hooks.json` SessionStart becomes a mod through CT-08's baseline re-record and the version bump (D89, D99; A2 G10)." |
| Q3-33 | P2 | HO:149-152 (§2(h) item 1) | "fail-closed logic inside `dev/hooks/stop_gate.py` and `subagent_stop_gate.py` (exit 2 on internal error, forced-crash test), delete the two `onFailure` lines, keep it on `PreToolUse(Bash)`. Owner: the mods library (D92: ...)" | "1. Stop/SubagentStop `onFailure: block` is inert. No fix lands in `dev/hooks/`: A2-7 replaces both gates with mods whose `.catch` blocks, and deletes the scripts and settings entries (D92, D97)." |
| Q3-34 | P2 | HO:169 (§2(i)) | "rows marked "(D85)" wait for the user's answer" | "rows marked "(D85)" are the splits and merges the user approved in grill round 3" (as TP:226) |
| Q3-35 | P2 | HO:347-348, 351-353, 362-367 (§5) | "D58 (Bash gate `if` field, Y2; lands in w0-session-hooks)"; "Pending user: the typed stages of §2(j) and the Docker volume choice (D80)."; "DL-3 is held; DL-4 is pending (scope widened to CT-01..CT-58 by DL-104)"; "round 3 also gave D87-D90" | "D58 (moot, A2-9)"; "Docker volumes removed (DL-105, DL-106)"; "DL-3 cancelled (DL-109, receipt DL-110); DL-4 pending, scope CT-01..CT-79 (Q3-14)"; "round 3 gave D87-D91; rounds 4-5 gave D92-D100 (DL-122..DL-130)" |
| Q3-36 | P2 | HO:432-441, 457-462 (§9); HO:474 (§10 item 7) | "mirrors ... into an untracked `/offline/` (`.git/info/exclude`; `.gitignore` is frozen)"; defects CT-33 must not copy include "unbounded crawls" and "no robots check"; "after the install admission"; "Respect robots (...)"; item 7 "`.claude/settings.local.json` has no `env`", owner user (CT-30 step 1) | "D86 admits downloads with no page, source, clone, robots or disk limit; receipts record pages and robots status (D98); `/offline/` goes into `.gitignore` with CT-08"; item 7 "done 2026-10-14 (D91, DL-119)" |
| Q3-37 | P2 | HO:76-105 (§2(b) steps 3 and 5) | Step 3's records commit R lists only w0-doctor hunks; step 5's publish intents name the handoff, FORK, N2 and w0-doctor files | The tree also carries the uncommitted grill records (DJ DL-105..DL-130, TP, TL, PR, GL, `skill-invocations.md`, two lane records, the w0-decisions merge report), six untracked ADRs 0002-0007 and a root `mods_troubleshoot-raw.md`. Add step 0: "Commit the rounds 3-5 records and ADRs 0002-0007 in their own records commit, and select them in the A09 intents; keep `mods_troubleshoot-raw.md` and the CT-29a files (`dev/handoff.py`, `dev/test_handoff.py`, both skill pairs) out." |
| Q3-38 | P2 | CTM:124-127 | "The hooks that enforce these levels arrive with ticket CT-23 (`prompt_hook`, `agent_gate`, lane `w0-session-hooks`) and read the thresholds from `dev/doctor/budget.py`" | "The mods that enforce these levels arrive with CT-23 on the mods library (A2-12..A2-14; lane w0-session-hooks closed, D97) and read the thresholds through task `ctx:thresholds`" (owner CT-23, or a parent doc edit now) |
| Q3-39 | P2 | CTM:131-134; `docs/agents/claude-takeover.md:11`; TL:104 (#96) | "Up to four offline lanes ... need the user's confirmation for each run"; "host-heavy runs need per-run confirmation"; "per-run confirmation" | Owner CT-40 (open since P3a N6, N8): "Up to `max_parallel` (3) writer lanes, one always cxx (D65, D78); heavy C++ runs one at a time under D68 with D84's disk gate, a notice per run"; TL:104 "a notice per run (D68)" |
| Q3-40 | P2 | `docs/adr/0005-always-on-cxx-lane-standing-admission.md:7-8, 22-23` | Status "D65, D68, D69, D70 and D78"; Decision "(60 GiB, then 1.5 times the first run's measured peak)" | Status adds "; gate amended by D84 (the larger of 60 GiB and 1.5 times the largest peak measured for the same run class)" |
| Q3-41 | P2 | DJ:122-130 sources; no file | Q58-Q71 are cited by DL-122..DL-130 but no question and answer table exists (round 3 has `grill-round3-questions.md`); Q65 appears in no file | Write the Q58-Q71 table with answers and DL ids (append to the round-3 file or a new round-4-5 file) and state what Q65 was, or that the number was skipped |
| Q3-42 | P2 | PR (append-only, report only) | Last entry covers grill round 4 (D92-D98); nothing records grill round 5 (D99, D100; DL-129, DL-130), the `research5/` dispatch or this reprioritization | The parent appends one dated entry; the NEXT bullet is rewritten per Q3-11 |
| Q3-43 | P3 | TP:217 | "Phase 4b: Reprioritized order (2026-10-14; D65, D68-D82; ADR 0005)" | "(2026-10-14; D65, D68-D100 and the third-reprioritization row; ADR 0005, ADR 0007)" |
| Q3-44 | P3 | TP:534-535 | "D42-D82 are K2 defaults and the 2026-10-14 decisions (phase4-prep, grill-with-docs rounds 1-2, imports, orders)." | "D42-D100 ... (phase4-prep, grill-with-docs rounds 1-5, imports, orders)." |
| Q3-45 | P3 | TP:489-498 | provenance stops at "CT-41..CT-58 come from the TR import" | add "CT-59 comes from D88 (A1); CT-60..CT-79 from the project import (D87, `reviews/ccm-20261014/project-import/`)" |
| Q3-46 | P3 | TP:410 and TL:133 (CT-02b title); TP:431 and TL:154 (CT-23 "Session hooks follow-up"); TP:239, 241, 244 (wave cells); TP:177, 327, 332 | "PreToolUse gate", "Session hooks follow-up", "Stop gates read the receipt", "the PreToolUse guard", "CT-02b's PreToolUse gate", "CT-02b: fail-closed hook launcher" | mod wording: "Bash gate mod", "Session mods follow-up", "Stop-gate mods read the receipt", "the Bash gate mod", "fail-closed `.catch` deny in each mod" (D92, A2 §1.2) |
| Q3-47 | P3 | TP:708; TP:742; HO:484 | "Until the hooks exist the parent applies the rule by hand."; "runs identically as a mise task, an `hk` git hook and Claude Code hooks"; "Keep: ... the three gate hooks" | "Until the CT-23 mods exist (A2-13, A2-14) ..."; history, leave; "the three gate hooks until A2-7 and A2-9 replace them (D92)" |
| Q3-48 | P3 | TP:758-759; `P/skill-invocations.md:36` | "Typed so far: `grill-with-docs` twice on 2026-10-14 (`skill-invocations.md:32`, `:35`)"; output cell "round 3 over every open item that needs the user (Q39 onward)" | "three times (`:32`, `:35`, `:36`)"; output cell adds "; rounds 4-5 (Q58-Q71) continued this typing" |
| Q3-49 | P3 | TP:765-766 | "The agent-protocol / dynamic-agents work of thread `01a13185` is out of scope and referenced only" | "... referenced only; the agent-protocol package comes here as CT-59 (D88)" |
| Q3-50 | P3 | TP:509 | "heavy lanes under D5, one at a time" | "heavy runs under D68 (D84 gate), one at a time" |
| Q3-51 | P3 | TL:190 (CT-59) | "design `reviews/ccm-20261014/project-import/A1-agent-dispatch-skills.md` (pending)" | drop "(pending)": the report exists |
| Q3-52 | P3 | TL:159 vs TP:436 (CT-29) | ledger blocked-by lacks "29b: CT-39" | add it |
| Q3-53 | P3 | HO:21-25 | revision notes stop at "revision 11" | add "Revision 12 (10:26Z) and later hand edits of §2(b), (c), (f), (h), (i), (j) and §5 for grill rounds 3-5 (D83-D100)" |
| Q3-54 | P3 | HO:176 vs TP:448 | lane unit "ct40-scheduler-fixes" vs "ct40-frontier-cxx" | one name; the allocation commit fixes it |
| Q3-55 | P3 | HO:264-265 (§3.4) | "(DL-104 was last on 2026-10-14)" | "(DL-130 was last on 2026-10-14)"; the read-tail rule already guards the ids |
| Q3-56 | P3 | HO:115 (§2(c) 0c) | "0c: D49 tooling (§2(g)) and `20-offline`." | add "the parent writes `lanes/20-offline.json` first", as for `21-offline` in 0a |
| Q3-57 | P3 | HO:69-70 (§2(a2)); HO:196-197 (§2(j) item 2) | "after (b), the parent folds ... at the Phase 4b gate"; "Publish the spec ... on the user's word" | "after wave 0c and the CT-34 audit, the parent folds ..."; item 2 precondition "after the gate fold" |
| Q3-58 | P3 | `docs/adr/0004-shared-user-level-mods-that-act.md:1, 20-31` | title "Mods may act where only a mod can, and shared mods live in the dotfiles repo"; Decision and Consequences unchanged | Status already records ADR 0006 and ADR 0007; optional title suffix "(amended)"; body stays as history |
| Q3-59 | P3 | `docs/adr/0006-absorb-and-sunset-source-projects.md:7, 33-35` | Status "D87 and D88"; "Until then the source projects keep running unchanged and are read, never edited, by this repository's agents." | Status adds D96, D98; "... read, never edited, except by the sunset tickets CT-62 and CT-78 under their outward admissions (D96)" |
| Q3-60 | P3 | `docs/adr/0007-mods-replace-settings-hooks.md:7-8, 29-35` | Status "D92 to D95 and D97"; Consequences name gate and mod tickets and "the user decides each one" | Status adds D99 (the plugin's consumer-facing SessionStart hook becomes a mod) and D100 (gaps Q68, Q70, Q71 decided on research R1-R3); Consequences add that hk Git hooks stay the Git-side gate (A2 G5) and that CT-19, CT-37 and CT-61 also land on the library |
| Q3-61 | P3 | GL:114, 105, 117 | Mod "This repository's only extension point for its own workflow rules."; Standing admission "under stated bounds (one at a time, an order, a resource gate)"; Source project "Its code is read, never copied or edited." | "...only Claude Code extension point ...; hk Git hooks stay for Git events (A2 G5)"; "under stated bounds, or none where the user chose none (D86)"; "read, never copied; edited only by its sunset ticket under an outward admission (CT-62, CT-78)" |
| Q3-62 | P3 | GL:90 vs TP:234 | "Gate: A named check whose actual exit code must be recorded"; Phase 4b row "gate" is the spec-fold step | rename the row "fold", or add "_Avoid_: gate for the Phase 4b fold step" |
| Q3-63 | P3 | CTM:11-18, 46, 78-85, 95-108 (101), 138 | roles table without merger or frontier-scheduler; "A PreToolUse deny for `--no-commit` lands with CT-02b."; layer 3 settings hooks; "The check for this and the compose test land with CT-16 and CT-02b."; "in a later lane" | True today; rewrite when the owner lands: D49 tooling (merger), CT-07 (roster, CT-56 merged by D85), CT-02b (A2-9, A2-15 mods), CT-22b (CT-16 folded, D72), CT-07 (Codex mirror) |
| Q3-64 | P3 | `P/reviews/ccm-20261014/grill-round3-questions.md:44, 52` | Q45 recorded "D86"; Q53 "new ticket CT-59 replaces CT-28 (recommended)" | "D86, DL-114"; "new ticket CT-59 replaces CT-28 (the recommendation was not to file; CT-59 added)" |
| Q3-65 | P3 | `P/lanes/ct21-codex-imports.json` status and base_sha; `P/lanes/w0-session-hooks.json` notes 1-3 | "waits for the gate-hooks merge to resolve"; notes say the lane "integrates last" and "makes dev/hooks/stop_gate.py ... fail closed" | ct21: HO §2(d) fixes it at cut (open since P3a); w0-session-hooks: append "(lapsed: D97; A2-7, A2-9)" to notes 1-3, or leave as history under the closed status |
| Q3-66 | P3 | TP:561 (D22) | "Hook set and latency budget: C4's inventory only (SessionStart doctor 15 s, prompt hook, Bash and Agent gates, existing Stop gates)" status "approved 2026-10-13" | status adds "; the set becomes mods (D92, D97)" |
| Q3-67 | P3 | TP:628, 634, 637, 638, 639 (D87, D93, D96, D97, D98 text) vs DJ:115, 123, 126, 127, 128 | D87 adds "feeds a third reprioritization" and drops "best practice per research"; D93 drops "(D61 kept; DF-A's reload-when-stale declined)"; D96 drops "rollback becomes a revert here"; D97 drops "on the TypeScript library"; D98 does not cite C1 §3.6 Q1, Q4, Q6 | restore the dropped clauses; the meaning is unchanged |

## 2. Cross-record mismatches

- D83-D100 against DL-111..DL-130: every subject and every Q source matches (D86 Q42, Q45, Q46; D91 DL-119..DL-121
  as operation, receipt and decision). Text differences: Q3-67 (wording only) and Q3-31 (DL-130 names a repository
  fnox profile that does not exist).
- DL-3 is closed (DL-109 cancels it, DL-110 is its receipt), yet TP:19, HO:40 and PR:776 list it as pending: all
  three were generated at rev 12 (10:26Z), before DL-109 (10:57Z). DL-4's subject still reads CT-01..CT-25, DL-104
  widens it to CT-58, the plan files CT-79 (Q3-14).
- Tickets table against ledger, CT-59..CT-79: all 21 rows agree on title, blockers and wave ("third
  reprioritization"); CT-59's ledger title only shortens the package path and drops the executor-gate clause.
  Elsewhere: CT-29 (Q3-52), CT-57 (Q3-24), CT-33 owned paths (Q3-20), CT-35 and CT-36 (the ledger adds D61, D62,
  D57 as blockers), CT-34 (blocked by publication while its wave is the gate, Q3-21).
- `lanes/w0-session-hooks.json` says closed (D97), while TP:18, TP:112, TP:121, HO:53, TL:133, TL:154, TL:160 and
  TL:163 still treat it as allocated or as a blocker.
- A2 against the plan: A2 §2.1 puts the plugin at `.claude/skills/workflow-mods/` with `mods/`, CT-31 still owns
  `plugins/workflow-mods/**` (Q3-23); A2-11 "w0-doctor follow-up (D92)" has no ticket id in the Tickets table;
  A2-10 (retire `dev/hooks/` into the package) is CT-39 work that CT-39's row does not name; A2 §4 decisions 1, 3,
  4 are D100's Q68, Q70, Q71 and decision 2 is D99 (A2's recommendation declined); A2's "Integration order"
  recommendation has no D row (Q3-02); A2's parent hunks (CA keys list, AG pointer to `docs/agents/workflow-mods.md`,
  CT-31's owned paths) are unapplied. `frontier.toml` `[hot_paths]` still names `dev/hooks/` and lacks `mods/` and
  `.claude/skills/workflow-mods/`, which most A2 units edit (`register.ts`).
- HO §2(c) and §2(i) match Phase 4b for waves pre to 0c; HO §2(i) contradicts TP:226 on the D85 rows (Q3-34).
- AG:54-60 research route against D100 (two-stage provider set, a repository profile) and CT-76 (repoints the
  receipt route here): section 4.
- D51-D53 still have no DL rows (HO:356-358; open since P3a).
- grill-round3-questions answers against DL rows agree: Q43 "the 30 ... and every symphony volume" equals DL-105's
  51 (20 home, 29 symphony, 2 anonymous).
- Verified current, no finding: #4 and #9 (TL:17-18, TP:256, TP:434, HO:135, D90); #101 in TL:109, TP:258, HO:135;
  CT-28 in TP:28, TP:361, TP:435, TL:11, TL:158, HO:70, HO:201, TPL:34 (HO:199 is Q3-04); TPL and its mirror;
  both session skill directories identical to their mirrors.

## 3. What changes once the parent regenerates the wave table from Q2-order.md

1. TP:217-226 heading and intro: decision range (D65, D68-D100 plus the new D row), reports
   (`reprioritize-3/` Q1-Q3), ADR 0005 and 0007; TP:226's D85 sentence stays.
2. TP:228-254 rows: place CT-59 (units 59a..59f2), CT-60..CT-79 and the A2 units under their tickets (CT-31a
   foundation A2-0..A2-6, CT-02b A2-7..A2-9 and A2-15..A2-18, CT-23 A2-12..A2-14 and A2-19, CT-32b A2-20, CT-17
   A2-21, CT-35 A2-22 and A2-23, CT-36 A2-24 and A2-25, CT-39 A2-10, the w0-doctor follow-up A2-11, D99's owner);
   rename the lane cells of Q3-46 and Q3-17. CT-31a cannot stay in wave 2: A2-4 needs CT-38a (wave 6 today), A2-6
   needs CT-26b, and A2-0 needs a fresh-session admission. Admissions column: drop the items of Q3-17; add the A2-0
   fresh-session spike, GitHub API quota (CT-60), dotfiles and knowledge-base outward admissions (CT-62, CT-78), the
   OCI acceptance run (CT-64), capped model spend (CT-69); research5 R1-R3 gate A2-0 arms 1, 4 and 5 (Q68, Q70, Q71).
3. CT-63 (host heavy lock in the package) needs "a gap between heavy runs": the cxx column must show where.
4. TP:256-259 and TP:276-284: "placed by the third reprioritization" becomes "placed (D-new)".
5. TP:408-487 Wave column for CT-59..CT-79 and every moved ticket (CT-31a/b, CT-02b, CT-23, CT-32b, CT-35, CT-36,
   CT-39 with A2-10), and TL:129-210 Lane column ("not allocated · wave n"), one scheme; TL:15-116 C++ rows if the
   cxx column moves.
6. TL:125 and the TL:7-13 snapshot paragraph cite "the Phase 4b row, D82": cite the new D row; TL:11 range.
7. Next Step and Current Phase (TP:11-13, TP:35-38), TPL:11-13 and its mirror, the PR NEXT bullet, and the gate
   row's fold range follow any change to waves pre to 0c or the gate (for example if A2-0, A2-11 or CT-63 move
   before publication).
8. HO §2(c) waves 0a-0c, the §2(i) unit table, HO:212-213 ("CT-05 and CT-11 run in wave 3, CT-02b in wave 5"),
   §2(j) item 3's ticket list, §2(a2) fold range, §2(f) "Still open: the third reprioritization".
9. TPL notes "Order: plan Phase 4b (...)" (Q3-13) and ADR 0005:8 "order in plan Phase 4b, D82".
10. A new D row and DL row record the third reprioritization (as D82 did); D82's status gains "order superseded by
    D-new"; DL-4's scope row (Q3-14) lists any new split ids.
11. CT-40 (wave 0a, cut next) acceptance at TP:289-299: `hot_paths` add `mods/`, `.claude/skills/workflow-mods/`
    and keep `.claude/settings.json` (every hook migration edits it); drop `dev/hooks/` once A2-10 is placed; the C++
    class list follows any cxx-column change. `[waves]` stays empty until `ledger:sync` after `/to-tickets`.
12. Grill-round-3 "Later, asked when the wave arrives" (wave numbers for CT-26b, CT-37) is a record; only the plan
    cites the new numbers.

## 4. AGENTS.md lines that D87, D92, D96 or D100 make wrong (listed, not edited)

| File:line | Current text | Owner ticket |
|---|---|---|
| AG:12-13 | "The 19 acceptance-baseline files in `evidence/onboarding/baseline-files.json`; `.gitignore` is one of them." | CT-08 (D64; D89's version and D99's plugin hook change the baseline through CT-08's re-record) |
| AG:25-26 | "a nested `CLAUDE.md` imports it everywhere except the plugin (a later lane adds it)" | CT-14 (CODING_STANDARDS rule 5 wants the id) |
| AG:47-48 | "container, provider, hook-runtime and fresh-session acceptance" | CT-31a (A2-6: mod-runtime acceptance; A2 gap G1, untrusted headless runs lose every mod) |
| AG:52-53 | "do not copy Claude hooks or slash commands into native Codex configuration" | CT-07 ("hooks, mods or slash commands", D92) |
| AG:54-56 | "New-tool research uses Exa, Firecrawl, Last30Days, Context7 and GitHub under `fnox --config ~/.config/fnox/config.toml --profile codex_research ...`" | CT-76 (D100's two-stage route: webclaw then Serper or SerpApi fallbacks, githubkit saved searches; D100 names no ticket, so the parent records CT-76 as owner) |
| AG:57-60 | "A strict hook receipt runs `mise -C <dotfiles-checkout> run research-fanout` with `--strict-five` ..." | CT-76 (D87; its title says the route is repointed here) |
| AG (absent) | no pointer to `docs/agents/workflow-mods.md` | CT-31a (A2-6; A2 §4 parent hunk) |
| AG:49-51 | "Global settings, hooks, trust, ... other repositories and host-heavy work need their own recorded admission." | none: D68 and D86 standing admissions are recorded admissions, so the line holds |
| CA:5 | roster "(implementer, doc-writer, reviewer, retro-writer, extractor)" | CT-07 (roster, CT-56 merged, D85) and D49 tooling (merger) |
| CA:8-10 | skills "(`codex-session-history`)" | CT-29a (session-handoff, session-resume), CT-25 (ticket-frontier), CT-31a (the skills-dir plugin and its mirror exemption, A2 §2.1) |
| CA:11-15 | "`settings.json`: shared project settings and hooks, composed by ticket CT-02. Its keys are ... and `hooks`" | the last of A2-7, A2-9, A2-11 removes `hooks` (CT-02b, w0-doctor follow-up); A2-4 adds `workflow-mods@skills-dir` to `enabledPlugins` (CT-31a) |
| CA:16-17 | "excluded through `.git/info/exclude` because `.gitignore` is a frozen baseline file" | CT-08 |

## 5. Earlier audit P3a: still open

Fixed since P3a: N3, N5, N7, N10, N11, N13, N14, N15, N17-N23, N27, N32, N35, N37, and the w0-decisions lane note.
Fixed then stale again under today's decisions: N1 and N2 (fold range, Q3-03), N4 and N25 (HO §2(f), §5: Q3-12,
Q3-35), N12 (format fixed, mod location now Q3-16), N24 (typings, Q3-48), N29 (revision notes, Q3-53), N31 (HO §3.4,
Q3-55), N33 (provenance, Q3-45), N34 (header range, Q3-44). Partly open: N16 (CT-31a/b have rows now but no D row,
and A2 redefines CT-31a: Q3-23), N28 (D86 admits the CT-34 read, the blocker cell still says publication: Q3-21).
Open: N6 and N8 (CTM:131-134, `claude-takeover.md:11`, TL:104; owner CT-40, Q3-39), N26 (#91, Q3-28), N30 (roster,
section 4), N36 (`frontier.toml:23` and `scheduler.md:52` "offline portion"; owner CT-40). Cross-record: D51-D53 DL
rows, DL-4's scope, `lanes/ct21-codex-imports.json` status text, `spec.md:34, 47, 61` (TP:285 assigns it to the
fold). P3a §3 item 6 (`[waves]` empty) and item 10 (CT-08 edits AG and CA) remain owner work.

## 6. HANDOFF §2 runbook: executable as written?

No. Two blockers: §2(b) merges a new settings SessionStart hook with no decision under D92 (Q3-02), and §2(b) does
not say where today's uncommitted records and six untracked ADRs go before records commit R and the A09 publish
(Q3-37). Stale but not blocking: §2(f) and §5 pending lists (Q3-12, Q3-35), §2(h) item 1 (Q3-33), §2(i) D85 note
(Q3-34), §2(j) item 3 wording (Q3-04), and the 0c lane-record step (Q3-56). The letter order (a), (a2), (b), (c)
with (d), (e), (g) inside the waves, then (j) at the gate, is executable once those are fixed; (h) items 4-6 are
first-turn read-only checks and fit before (b).

# R3 plan consistency (2026-10-14, read-only)

TP = `P/task_plan.md`, TL = `P/ticket-ledger.md`, DJ = `P/decisions.jsonl`, HO = `P/reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md`, TPL = `.claude/skills/session-handoff/references/handoff-template.md` (mirror identical), spec = `P/proposals/claude-takeover-spec/spec.md`. Verified live: pid 51306 runs `claude ... --resume 9fde3ed2`; transcript `ce9c0b3d` has `customTitle` `ccm-20261014`; HEAD `21af565` = origin.

## 1. Findings

| id | sev | file:line | current text | replacement |
|---|---|---|---|---|
| F1 | P1 | TP:4-7 | "`ccm-20261013-check` (`b74a0bf1`...) owns this plan ... `ccm-20261013` (`464a2816`) is closed" | "Owner: session `ccm-20261014` (`ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34`) owns this plan and the branch `codex/marketplace-native-onboarding` since 2026-10-14 (at least revs 6-8; DL-60..DL-66). Session `ccm-20261013` (`464a2816`, pid 51306) is open and idle, not a writer." (handover rev UNVERIFIED) |
| F2 | P1 | HO:66, 70, 420, 426; TP:21-22; TPL:15 | "`/rename ccm-20261014`", "`claude -n ccm-20261014`", "start as `ccm-20261014`" | Name already held by `ce9c0b3d`. TPL:15: "Owner: start under a new unique name (not `ccm-20261014`) from `dev/handoff.py start-command --name <name>`; rewrite owner line 4 with `dev/handoff.py owner`." Rerun `write`. |
| F3 | P1 | TP:10-11 (TP:32-33, TPL:11-12, HO:73-75) | "fold CT-30..CT-39 and D59-D62 into the spec (§2(a2)) and fan out §2(i)" | §2(i) starts CT-26/28/29/30/32a/33 before publication, against D59 (TP:413) and P1-6 (TP:430); spec names no CT-25..CT-29 topic either. "Integrate w0-doctor (`f1bbc8d`) per HANDOFF §2(b); fan out only the pre-approved §2(i) rows (w0-doctor-records, w0-session-hooks, CT-21, D7 spike) and the cxx lane (if D63, §2); fold CT-25..CT-39 (CT-27 not filed) and D59-D62 into the spec; the rest runs through implement-spec after Phase 5." |
| F4 | P1 | HO:221-222 | "Do not start: ct11-check-lock, ct05-ledger (own `dev/check.py` and lane records until w0-doctor and CT-19 land)" | Deadlock: CT-19 is blocked by CT-05 (TP:282). "Do not start before the w0-doctor integration: ct11-check-lock, ct05-ledger. CT-05 precedes CT-19." (intent UNVERIFIED; source FORK:34-36) |
| F5 | P1 | TP:122-123 | "runs as a subagent team, review first and then fix, in the session after `/clear`" | Review wave was dropped (progress.md:646). "runs through `/mattpocock-skills:implement-spec` after Phase 5 publishes the spec (D59); each ticket opens with its own read-only audit." |
| F6 | P1 | TP:218-219 | "approve C4's CT-01..CT-24 (+CT-02b) (D3, D23) and the revised breakdown CT-25..CT-33" | append "and CT-34..CT-39 (D59)" (as HO:209-212) |
| F7 | P1 | TP:463-464; HO:217 | "no `/clear` until tickets publish"; "Not needed again: `/grill-with-docs`" | Unstaged `P/skill-invocations.md:32` records `/mattpocock-skills:grill-with-docs` typed in `ce9c0b3d` after rev 8, while the plan targets a `/clear`. HO:217: "`/grill-with-docs` was typed in `ccm-20261014` (skill-invocations.md); `/to-spec` is not needed." Parent decides whether the no-`/clear` rule binds. |
| F8 | P2 | TP:27-29 | "Finish the gate-hooks merge, publish a clean tip through A09, file CT-01..CT-25 (+CT-02b)" | "Integrate wave 0, publish each integration through A09, file CT-01..CT-39 (+CT-02b, CT-32a/b; CT-27 not filed; CT-13 closed into CT-31) under the takeover spec, run them through implement-spec behind the retro gate (D59), and keep one C++26 P2996 ticket active (D27, D28) until the native research core replaces the Python core." |
| F9 | P2 | TP:142, 145, 292, 296; TL:158, 162, 166; HO:175, 181, 354-360, 438 | "(corpus, pending user)", "(D54 is pending)", "D57 (pending user)", "Pending user: ... D50 ..., D54, D57" | Accepted under D59 (DL-64..DL-66; TP:404, 408, 411; HO:131). Write "accepted under D59 (DL-65)" or "(DL-66)"; drop D54/D57 from Blocked-by cells and HO:359. |
| F10 | P2 | TP:311-312; TL:163-168 | "owned_paths come from the review wave's reports" | "owned_paths come from the frontier-scheduler at claim time." |
| F11 | P2 | TP:264 | "built, re-review PASS, mid-merge \| CT-01 \| runbook" | "integrated `760b154`, published `0a68dce`, retro passed \| CT-01 \| done" (TL:130, TP:341) |
| F12 | P2 | TP:265, 285-287 | CT-02b, CT-22, CT-23, CT-24 "proposed" | Copy TL:131, 151-153: slices allocated (w0-doctor ready `f1bbc8d`, w0-session-hooks) or integrated (`e40a62a`, `c7054fd`). |
| F13 | P2 | TP:305-306 | "Only `ct21-codex-imports` has a lane record today" | "Lane records: ct21-codex-imports and the wave-0 slices (`lanes/w0-*.json`)." |
| F14 | P2 | TP:328-329 | "Projection of `lanes/*.json` on 2026-10-13 ... still to apply in Phase 3 step 7" | Five w0 records missing; step 7 ticked. "Projection on 2026-10-13; wave-0 lanes are under Phase 4." |
| F15 | P2 | TP:433 | "P1-8 ... \| CT-13 \|" | "CT-31 (subsumes CT-13)" |
| F16 | P2 | TP:73-75 | "[ ] 9 pwf migration ... (open: no `.mode` written...)" | "- [ ] 9 pwf migration: shape and archive done; `.mode`, pins and per-lane ledgers moved to CT-30 (D54 accepted)" |
| F17 | P2 | TP:225-248 | Phases 6/7 omit CT-34..CT-39, CT-14, CT-16; wave-2 CT-31/CT-32b sit in Phase 6 | Phase 6 add "- [ ] CT-34..CT-39 through implement-spec; the frontier orders them"; wave 2 add "CT-31, CT-32b, CT-16 if not in wave 1"; wave 3 add "CT-14". |
| F18 | P2 | TP:207-208 vs TP:384, TL:154 | "the ticket-frontier skill runs parallel lanes" vs D32 "parent follows K1 §5 by hand until then" | "the K2 prototype of ticket-frontier runs the lanes with `--graph <file>` until CT-05; CT-25 hardens it (D32 amended)"; needs a D row. |
| F19 | P2 | HO:204-206 vs TP:215, 462 | "type `/mattpocock-skills:setup-matt-pocock-skills` in this session" | "...in a fresh session; the skill seed has drifted since it last ran." |
| F20 | P2 | HO:339-340 | "Co-Authored-By: Claude Fable 5.1" plus the `b74a0bf1` URL, "exactly" | This session attributes Opus 5.5, `session_01Wx5od8...` (parent model UNVERIFIED). "Each commit ends with the committing session's two attribution lines, kept in one trailer file." |
| F21 | P3 | HO:218-219 | "for CT-26..CT-33" | "for CT-25..CT-39" |
| F22 | P3 | HO:9-19 | revision notes stop at 3; plan says rev 8 | add "Revisions 4-8 (2026-10-14): §2(a2), §2(f), §2(j) item 3, §3.4 ids; receipts in progress.md." |
| F23 | P3 | TP:451-452 | E-U1-7 precedes E-U1-6 | swap |
| F24 | P3 | TP:346-348 | header explains D1-D41 only | append "D42-D45 are K2 defaults; D46-D62 date from 2026-10-14." |
| F25 | P3 | TP:404 | "(...; DL-64)" | "(...; DL-54, DL-64)" |
| F26 | P3 | TP:481 | "write `plan:handoff`" (no such task) | "run session-handoff (`dev/handoff.py write`)" |
| F27 | P3 | TL:7 | "Snapshot: 2026-10-13 (records update by review session `ccm-20261013-check`)" | "Snapshot: 2026-10-14 (sessions `ccm-20261013-check`, `ccm-20261014`)" |
| F28 | P3 | TP:24; TPL:25 | "CT-34..CT-39 (U1-U7" | "CT-34..CT-39 (U1-U6; U7 as criteria" |
| F29 | P3 | TP:21; HO:32 | "(operator asserted --agents-done)" | E-U1-5 says step 1 verifies; `dev/handoff.py` should print "none (verified)". |
| F30 | P3 | `.claude/AGENTS.md`:5 | "(implementer, doc-writer, reviewer, retro-writer, extractor)" | add `frontier-scheduler` |

progress.md (append-only, report only): :637 says grill-with-docs "not typed" (see F7); the NEXT bullet :666-672 inherits F2/F3 and is rewritten in place by design.

## 2. Correct now, wrong once an always-on cxx lane is adopted

1. TP:398 D46 / DL-50 "Wave 0 is exempt from the always-active C++ rule". Add D63 (user): "One C++ (cxx) lane runs at all times, wave 0 included; D46 superseded. Without an admission it takes #21's offline portion (D28); heavy runs stay one at a time, each admitted (D5, D42)." Record `decision` plus `approval`. The requirement is in no file yet.
2. HO:165 "Serial first: the w0-doctor integration (§2(b)). Then in parallel:" becomes "The cxx lane starts now, beside the w0-doctor integration; then in parallel:" plus row "\| cxx-21-offline (D63) \| #21 offline portion (D28) \| from the frontier-scheduler \| none; heavy part needs an admission \|". TPL:26-27: prefix "cxx lane (#21 offline);".
3. `docs/agents/claude-team.md`:131, TP:522, spec:47 say "four offline lanes"; `frontier.toml`:7 says `max_parallel = 3`. Write "Up to `max_parallel` writer lanes (`frontier.toml`) run at once, one always a C++ (cxx) lane (D27, D63); host-heavy runs one at a time, each confirmed." With cxx reserved, only two non-C++ writers remain; three need `max_parallel = 4` (a `propose` item).
4. spec:61 puts "Implementing or closing the existing spec #11 and #83 tickets" out of scope, and `frontier.py`:392-395 fills the cxx slot only from the passed graph's `ready` set: implement-spec on the takeover spec never fills it. TP:207-208: "...one cxx lane fed from spec #11: the `--graph` file merges both specs (#16, #17, #20, #21 ready)."
5. TP:242 "CT-22b in the heavy slot" contradicts D5 (TP:357 "wave-2 heavy slot = #21"): "CT-22b in a writer slot".
6. TP:230-231 "One C++ ticket active alongside" moves to Phase 4: "- [ ] cxx lane now (D63): #21 offline portion".
7. HO:273-283 hard-codes `DL-67`, `DL-68` and `receipt DL-68`; appending D63 (or D51-D53, HO:363-365) first shifts them: "receipt <id printed by the operation command>".
8. TP:29 "(D27/D28)" becomes "(D27, D28, D63; wave 0 included)".

## 3. Cross-record mismatches

- DL-4 subject "/to-tickets approval of CT-01..CT-25 (+CT-02b)" vs TP:218 and HO:209-212 (CT-01..CT-39); shown at HO:34. `plan_decide.py` has no supersede: append an operation with the full range and close DL-4 by `receipt`.
- D51, D52, D53 (TP:405-407) have no DL row (HO:363-365 schedules them).
- DL-60..DL-63 lack the `[status]` suffix of DL-50..DL-59; DL-60 omits TP:413's baseline caveat. DL-54, DL-55, DL-58 still read "[pending user ...]" (closed by DL-64..DL-66).
- TL:150 and `lanes/ct21-codex-imports.json` say "waits for the gate-hooks m[erge]"; merged as `760b154` (fix scheduled HO:125).
- `frontier.toml`:20 `include` covers spec #11 only; TP:246-247 heavy chain adds "L1 #96" (spec #83).
- HO:31 and TP:13 "unstaged 6"; now 7 (`skill-invocations.md`).
- HO §2(i) (:167-183) and TPL:26-27: no CT-34..CT-39 or cxx row; about 12 parallel units against `max_parallel = 3`.
- TL GitHub columns date from `05c3dc9` (TL:10); READY for #16, #17, #20, #21 is UNVERIFIED today.

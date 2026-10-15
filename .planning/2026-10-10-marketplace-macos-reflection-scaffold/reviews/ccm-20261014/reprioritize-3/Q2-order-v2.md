# Q2 v2: third reprioritization, merged order after grill rounds 3-5 and D101-D108

Read-only, 2026-10-14, agent Q2 of session `ccm-20261014` (`ce9c0b3d`), tip `21af565`. Revises
`Q2-order.md` (v1, kept as written). This file is the only write. P =
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. New inputs: D101-D108 in
`P/task_plan.md` and `P/decisions.jsonl` DL-131..DL-138; `P/reviews/ccm-20261014/research5/` R1
(mod loading gaps), R2 (#92533), R3 (awaiting the plugin reload); `docs/agents/hooks-and-mods.md`;
the Tickets rows CT-80 and CT-81; the working-tree docstrings of `dev/hooks/{pretooluse_gate,
stop_gate,subagent_stop_gate}.py` (all three import `dev/hooks/git_gate.py`); the 27 files under
`dev/toolchains/` that load the dotfiles host lock. R4 (`#13` verdict) and R5 (crawl throttle,
context tracking) are not written yet.

Method as in v1: the order is data in a scratch script that checks single placement, dependency
order (five named intra-wave cut rules) and same-wave hot-path classes. Result: 199 units and
operations, 62 wave rows, rc 0. Markers: `[Q77]` = waits for the user's Q77 answer; `[R4]` = holds only
if the #13 verdict passes (fallback waits for R4, D106); `[R5]` = design detail waits for R5 (D107),
order unaffected; `[D7]` = beside CT-39 only if the D7 spike passes (D105). Q68, Q70 and Q71 are
closed by D102, D103 and R2, so v1's `[Q68]`, `[Q70]`, `[Q71]` markers are gone.

## 0. What moved from v1

- D102: A2-7 (Stop and SubagentStop mod), A2-9 (Bash gate mod) and A2-10 (retire `dev/hooks/`) are
  dropped. A2-8, A2-15, A2-20 and A2-21 become hook units on the three gate scripts: CT-02b.1 (was the
  D51 slice of A2-7, wave 18), CT-02b.2 (was A2-8, 19), CT-02b.3 (was A2-15, 21), CT-02b.4 (the Bash
  parts of A2-16..A2-18, 23), CT-32b (was A2-20, 27) and CT-17b (was A2-21, 29). A2-16, A2-17 and A2-18
  stay mods with their non-Bash rules only. `dev/hooks/**` and `dev/test_hooks.py` leave CT-39's scope
  for good; A2-11 no longer removes the settings `hooks` key.
- D101: unchanged from v1 (w0-doctor integrates as reviewed; A2-11, now wave 20, deletes its entry).
- D103: A2-23 (37) awaits a plain `/reload-plugins` in `session.start` and answers
  `classic.SessionStart` with `reloadSkills` and `sessionTitle` (R3 sketch).
- D104: A2-0 is a gate spike lane under the `/prototype` capture rules, admitted; arms 3 and 4 become
  CT-80 evidence rather than blockers.
- D105: CT-32a (7), A2-24 (8), CT-20a (9) stay beside CT-39 on the D7 condition alone; CT-39 stays
  serial; CT-25 and CT-59f1 gain the per-unit tracking rows.
- D106/D107: CT-80a (watch automation, 25) and CT-81 (research-first, 39) are new; the CT-80 check
  recurs at every wave boundary; CT-33 gains the adaptive throttle row; v1's disk-coordination risk
  is closed by that row.
- Q77 (provisional): CT-63a, the own host-lock copy, opens the wave-1 cxx queue; CT-63 shrinks to
  CT-63b (tests and the package move, 10).
- Lane 1 from wave 39 shifts one wave (CT-81 inserted); the end stays at wave 56 (lanes) and 57 (cxx).

## 1. Dependency graph additions (new edges only)

Notation `A -> B`: B waits for A; "soft" = recommended order, not an input. v1's edges stand except
those that named a dropped unit; the full v1 list is in `Q2-order.md` section 1.

Kept from v1 (sources unchanged): A2 foundation chain A2-1 -> ... -> A2-6 and A2-6 -> every mod
feature unit (D92); CT-26a -> A2-1, A2-6; CT-26b -> A2-6; CT-38a -> A2-4; CT-39 -> A2-22, A2-24; WDI ->
A2-11, A2-12, A2-26; A2-12 -> A2-13 -> A2-14 -> A2-19; CT-19 -> A2-14, A2-17; CT-23p -> A2-19; A2-22 ->
A2-23; A2-24 -> A2-25, CT-33, CT-60, CT-76a; A2-26 -> A2-27, A2-28; CT-32a -> A2-28; CT-29b -> A2-27;
A2-30, A2-31, A2-32, A2-33 as in v1; every A1, C1, DF-A, DF-B, KB-A, KB-B and decision edge of v1
(CT-52 -> CT-41, CT-59a, CT-72a, #26; #26 -> CT-53; CT-17 -> CT-49; CT-64 -> #28; CT-59f2 -> CT-25;
CT-59d -> CT-37; CT-42 -> CT-75; CT-75 and CT-44 -> CT-73.n; CT-33 -> CT-55; the CT-77 engine owners;
CT-08 -> 13-offline; 39-6 -> 22-offline, 18-offline).

New in v2:
- D102, `docs/agents/hooks-and-mods.md`: CT-39 never owns `dev/hooks/**` (three gates plus
  `git_gate.py`, which they import) or `dev/test_hooks.py`; the gates stay stdlib-only.
- CT-38a -> CT-02b.2 (Phase 4b CT-38 rows: one command decision table for the lint and the gate; under
  D102 the gate cannot import the package, so the table is a data file the gate reads with `tomllib`).
- CT-02b.2 -> CT-02b.3, CT-02b.4 (same `pretooluse_gate.py`; D108 moves A2-8's private-input
  admission to CT-02b.2).
- CT-32a, CT-02b.1, CT-02b.3, CT-02b.4 -> CT-32b (ledger: CT-32b shares `pretooluse_gate.py` and
  `dev/test_hooks.py` with CT-02b; Stop gate composition).
- CT-17 + CT-32b -> CT-17b (same `stop_gate.py`).
- A2-6 -> A2-16, A2-17, A2-18 directly (A2-8 no longer exists); R2 section 8 adds the
  `agent.spawn` deny of `isolation: "worktree"` and of `EnterWorktree` outside `.claude/worktrees/` to
  A2-18.
- Q77: #20 heavy -> CT-63a -> 17-, 16-, 13-, 96-offline -> CT-39 (CT-63a edits
  `dev/toolchains/p2996_configure.py` and the 27 callers, the same tree the split units touch, so they
  rebase on it; it cuts only after #20's run has executed, since heavy-run admissions bind the configure
  digest, DF-B 3.1).
- CT-63a -> CT-62, CT-77 (DF-B section 5 item 1 is met in wave 1; no dotfiles change can stop heavy
  runs after it). CT-63b -> CT-11 (DF-B 3.1, lock reuse), CT-63b between heavy executions.
- CT-76d -> CT-80a (the watch reruns the D100 route through CT-76's tasks); CT-76d + CT-25 -> CT-81
  (Tickets row CT-81).
- D105: no edge; acceptance rows on CT-25 and CT-59f1 (per-unit peak context tokens, total tokens,
  wall time). D107: no edge; CT-33 row (throttle on load average, memory pressure, free disk; pause
  before the D84 floor; R5 picks the tool, preferring OS built-ins, then Rust, C++, C, Zig).
- R2 section 8 rows (no edges): A2-6 lint bans RegExp, unmatched and `*` `tool.call` matchers;
  CT-22b doctor reports `claude --version` below 2.1.290 as an error line.

Removed with the dropped units: A2-0 arms 3 and 4 -> A2-7, A2-9; A2-8 -> A2-9, A2-16..A2-18; A2-9 ->
A2-10, A2-15; A2-7 + A2-15 -> A2-20 -> A2-21; CT-32a -> A2-20; CT-17 -> A2-21; CT-38a -> A2-10.

## 2. Critical path and priority rule

Critical path (longest chain to the knowledge-base sunset, 28 units from the w0-doctor integration;
the chain to #61 is 31): gate -> CT-63a [Q77] -> wave-1 split units (17-, 16-, 13-offline) -> CT-39
(39-1..39-8) -> CT-63b -> #18 heavy -> #23 (also fed by #13 heavy [R4] -> #14 -> #15 -> #19) -> #30
(also needs CT-52 -> #26, #27, and CT-57 -> CT-64 -> #28) -> #31 -> #32, #33, #34 -> #42, #35, #38,
#41 -> #43 -> #47 -> CT-68 -> CT-69 -> CT-78. #47 is the 40th of 69 cxx units (wave 32). CT-62 waits
on the same queue through CT-60 and on the mods stream (CT-38a -> A2-4 -> A2-5 -> A2-6 -> A2-13 ->
A2-14 -> A2-19 -> A2-33). Both columns stay saturated: 127 lane units end at wave 56, 69 cxx units
at wave 57.

Priority rule, in order:
1. Hard gates: D77 (pre to 0c before publication, plus D86's CT-34 and D104's A2-0 at the gate); D71
   and D105 (CT-39 alone and serial over `dev/**`, with only CT-32a, A2-24, CT-20a beside it and only if
   D7 passes); D68 and D84 (one heavy run at a time, D5 order, per-class disk gate); D92 with D102
   (A2-0..A2-6 before every mod feature; the three deny gates stay hooks); D85 prerequisites; D75.
2. Heavy-run protection: CT-63a before CT-39 [Q77]; CT-63b in the first heavy gap after CT-39.
3. cxx feed deadlines: CT-52 before #26; CT-57 -> CT-64 -> #28 before #30; #29 before #40.
4. User weight (Q46, D100, D106): A2-24, CT-41, CT-33, CT-43, CT-44, A2-25, CT-76a-d, then CT-81.
5. D51 prevention on live gates: CT-02b.1 (fail closed) leads the hook units.
6. K1: longest remaining path, then out-degree; hot paths disjoint across columns; smaller first.
cxx slot as in v1: D5 order among the listed runs, #23's prerequisites first, LLVM units as fillers.

Standing parent operations every wave: copy each Agent result's usage (peak context tokens, total
tokens, wall time) into the lane record (D105) until CT-25 and CT-59f1 automate it; at each wave
boundary run the CT-80 check (`gh issue view` on #99130, #96831, #100869, #92533, #101384, #84320 and
the Claude Code changelog), read-only, until CT-80a automates it; on any change, the D100 route and a
new cited report beside R1-R3.

## 3. Wave table

`dev/hooks/**` and `dev/test_hooks.py` are hook-unit territory (D102), never CT-39's. A cell
"X, then Y" is serial in one lane.

| Wave | Lane 1 | Lane 2 | cxx slot | Parent operations and admissions |
|---|---|---|---|---|
| pre | w0-doctor integration (as reviewed, SessionStart entry kept, D101) | none | none (parent writes `lanes/21-offline.json`) | A09 publish; drain proposals; D51 items 4-6 read-only, item 7 `test:frontier` row in the records commit; D102 doc hunks already in the tree go into a records commit |
| 0a | CT-40 | D7 spike (`mise/` only) | 21-offline (fallback 27-offline) | close #12 (D70, D86); first CT-80 check |
| 0b | w0-doctor-records | CT-21 | #21 heavy (first project-build class run, D84) | none |
| 0c | D49 tooling | none (D97) | 20-offline | closes #24, #25, then #62-#78 one at a time (D86) |
| gate | A2-0 spike lane (D104: throwaway branch, verdict and pointer on the ticket) | CT-34 audit, read-only | #20 heavy | user types A2-0 arms 1, 5, 9 (admitted, D104); parent: spec fold after CT-34 and A2-0 (CT-25..CT-81, A2 units as reshaped here, CT-59a..g, partitions, D59..D108, import acceptance rows, R1-R3); user: typed stages in a fresh session (D90); `ledger:sync`; `frontier.toml` `[waves]` |
| 1 | CT-08, then CT-29a | CT-26a, then A2-1 | CT-63a [Q77] (cut after #20's run executed), then 17-offline, 16-offline, 13-offline (after CT-08 lands), 96-offline if #96 needs one | parent runs CT-30 first (D75); A2-1 network once; qualified closes #90, #92-#94, #97, #79-#82 (D86) |
| 2 | 39-1 package skeleton, config, discovery task | A2-2 | #17 heavy | notice per heavy run (D68) |
| 3 | 39-2 core runner, env allow-list, receipts | A2-3 | #16 heavy | none |
| 4 | 39-3 doctor and handoff callers | CT-14 | #96 heavy (first LLVM-bundle class run) | none |
| 5 | 39-4 planning, lane, retro, check tools; CT-12 wiring | CT-26b (with #4, #9) | #13 heavy [R4] (first LSan class run) | container-build admission (CT-26b) |
| 6 | 39-5 issue, search, delivery tools | #95 C3 (read-only on `dev/**`) | #13 lane continues (verdict review, retro); no new cut | none |
| 7 | 39-6 toolchains move | CT-32a [D7] | 22-offline (cut after 39-6 lands) | 39-6 integrates while no heavy run executes |
| 8 | 39-7 skill-bundled scripts, raw `python3` skill lines | A2-24 `web:fetch` [D7] | #22 heavy | `/verify` backlog for waves 1-7 (D56); webclaw pin as a parent hunk |
| 9 | 39-8 hk ruff and ty, retire `MARKETPLACE_PYTHON`, `development.yml:18`, old paths | CT-20a [D7] | 18-offline | none |
| 10 | CT-52 | CT-63b [Q77] (tests, package move) | #18 heavy (cut after CT-63b lands) | rewrite `frontier.toml` `hot_paths` (section 5) |
| 11 | CT-41 | CT-11 | #14 [R4] | none |
| 12 | CT-33 (adaptive throttle row [R5]) | CT-38a | #15 [R4] | D86 standing webclaw admission; the throttle pauses before the D84 floor (D107) |
| 13 | CT-76a | A2-4 | #19 [R4] | none |
| 14 | CT-43 | A2-5 | #23 | none |
| 15 | CT-76b | A2-6 (matcher lint, no `gates:bash`) | 27-offline, then #27 heavy (first native-core class run) | none |
| 16 | CT-44 | A2-25 | #26 | none |
| 17 | CT-76c | CT-18 | #99 (filler while #30 waits) | none |
| 18 | CT-57 | CT-02b.1 (Stop and SubagentStop fail closed, compose test; D51) | CT-53 (split unit, then compile) | `claude plugin validate --strict` joins the host check (D89) |
| 19 | CT-64 | CT-02b.2 (token parser, redacted corpus, shared table) | #100 | plugin install and OCI acceptance admissions; D108 corpus admission; then knowledge-base private (D96, outward) |
| 20 | CT-76d | A2-11 (doctor context mod; deletes the w0-doctor SessionStart entry) | #102 | one strict research receipt through the fnox research profile |
| 21 | #28 | CT-02b.3 (no-commit, dry-run and time flags, deadline deny, `hooks:install` guard) | #103 | OCI acceptance and fresh Claude session admissions (#28) |
| 22 | CT-05 | A2-12 | #30 | none |
| 23 | CT-17 | CT-02b.4 (secret printing, destructive git, absent binaries, wait loops) | #31 | none |
| 24 | #29 | A2-13 | #32 | Context7 provider admission (#29) |
| 25 | CT-19 | CT-80a | #33 | network for the watch's saved searches |
| 26 | CT-42 | A2-14 | #34 | one clone under D86 |
| 27 | CT-49 | CT-32b (gates read the verify receipt; lane retro in a lane worktree) | #42 | none |
| 28 | CT-71 | A2-16 (protected writes, non-Bash) | #35 | other-repository read admission; gitleaks pin |
| 29 | CT-23p | CT-17b (stop-gate lane lifecycle) | #38 | none |
| 30 | CT-59a | A2-17 (lane paths, non-Bash) | #41 | none |
| 31 | CT-59b | A2-19 | #43 | `jsonschema` pin unless CT-52 pinned it |
| 32 | CT-59c | A2-18 (tool rules, isolation and `EnterWorktree` deny) | #47 | none |
| 33 | CT-59d | CT-22b (CLI floor 2.1.290 row) | CT-68 (class to confirm) | none |
| 34 | CT-29b | A2-26 | CT-60 | network and GitHub API quota (CT-60) |
| 35 | CT-59e | A2-29 | CT-65 | none |
| 36 | CT-59f1 (tracking row [R5]) | A2-22 | CT-66 | none |
| 37 | CT-59f2 | A2-23 (D103) | CT-67 | CT-35's `/usage` check may need a user-typed fresh session |
| 38 | CT-25 (with CT-06; tracking row [R5]) | A2-27 | #36 | CT-59g: one admitted `claude -p` smoke, `codex exec` after 2026-10-19; A1 host sunset after Codex returns (user admission) |
| 39 | CT-81 | A2-28 | #37 | none |
| 40 | CT-37 | A2-30 (D99) | #39 | fresh `claude -p` through `dispatch:claude` (CT-37); baseline re-record and plugin bump (A2-30) |
| 41 | CT-72a | A2-32 | #40 | none |
| 42 | CT-75 | A2-33 | #44 | one live refresh under D86 |
| 43 | CT-72b | CT-50 | #45 | none |
| 44 | CT-74 | CT-51 | #46 | transcript-read admission (CT-51 live runs) |
| 45 | CT-79 | CT-38b (CT-58) | #48 | none |
| 46 | CT-47 | CT-61p | #49 | network for `--live` (CT-47) |
| 47 | CT-46 | A2-31 | #50 | fnox profile choice and a capped live call (CT-46) |
| 48 | CT-48 | CT-07 (with CT-56) | #51 | network (CT-48); Codex available (CT-07) |
| 49 | CT-55 | #98 C2 | #52 | graph tool binary and cache path (CT-55) |
| 50 | CT-70 | CT-10 | #53 | read-only `gh` (CT-70) |
| 51 | CT-54 | CT-20b | #55, #56, #57 | graphviz pin (CT-54) |
| 52 | CT-69 | CT-73.1, then CT-73.2 | #54 | capped model spend (CT-69); spend recorded per CT-73 unit (D108) |
| 53 | CT-77 | CT-73.3, then CT-73.4 | #58 | dotfiles public-fetch check, read-only (D96) |
| 54 | CT-73.5, then CT-73.6 | CT-73.7, then CT-73.8 | #59 | none |
| 55 | CT-73.9, then CT-73.10 | CT-73.11, then CT-73.12 | #60 | none |
| 56 | CT-62 | CT-78 | #61 | outward, explicit instruction each: dotfiles writes, push, visibility (CT-62); knowledge-base archive or private (CT-78) |
| 57 | none | none | #104, #105, then CT-45 | held: #106-#108; spec #11 and #83 close with their children; draft PR #109 on the user's word |

Any wave after 2026-10-19: #91 and the D80 Codex follow-ups (user). Each build session ends with
`/mattpocock-skills:retro` (user, D16).

## 4. Check list (ticket or issue, unit, wave)

Takeover-spec tickets:
- CT-01..CT-04: done. CT-09, CT-13, CT-24: closed (D72). CT-27: not filed. CT-28: dropped (D88).
- CT-02b (hook work, D102): CT-02b.1 18, CT-02b.2 19, CT-02b.3 21, CT-02b.4 23.
- CT-05: 22. CT-06: folded into CT-25 (38). CT-07 with CT-56: 48. CT-08: 1. CT-10: 50. CT-11: 11.
- CT-12: wiring in 39-4 (5), lint and mirror test in CT-38a (12). CT-14: 4.
- CT-15: split into CT-30 (1), CT-29 (1, 34), CT-22b (33). CT-16: in CT-22b (33).
- CT-17: CT-17 23 (with CT-24's remainder), CT-17b 29 (stop-gate part, hook work, D102).
- CT-18: 17. CT-19: CT-19 25, A2-32 41. CT-20: CT-20a 9 [D7], CT-20b 51. CT-21: 0b.
- CT-22: CT-22a = w0-doctor integration pre, w0-doctor-records 0b, A2-11 20; CT-22b 33.
- CT-23: A2-12 22, A2-13 24, A2-14 26, CT-23p 29, A2-19 31. CT-25: 38.
- CT-26: CT-26a 1, CT-26b 5. CT-29: CT-29a 1, CT-29b 34. CT-30: 1 (parent, D75).
- CT-31a: A2-0 gate (spike lane, D104), A2-1 1, A2-2 2, A2-3 3, A2-4 13, A2-5 14, A2-6 15, A2-26 34.
- CT-31b: A2-29 35, A2-27 38, A2-28 39.
- CT-32a: 7 [D7]. CT-32b: 27 (hook work, D102). CT-33: 12 [R5 row]. CT-34: gate.
- CT-35: A2-22 36, A2-23 37 (D103). CT-36: A2-24 8 [D7], A2-25 16. CT-37: CT-37 40, A2-33 42.
- CT-38: CT-38a 12, CT-38b (= CT-58) 45. CT-39: 39-1..39-8 in waves 2-9 (no A2-10).
- CT-40: 0a. CT-41: 11. CT-42: 26. CT-43: 14. CT-44: 16. CT-45: 57 (cxx). CT-46: 47. CT-47: 46.
- CT-48: 48. CT-49: 27. CT-50: 43. CT-51: 44. CT-52: 10. CT-53: 18 (cxx). CT-54: 51. CT-55: 49.
- CT-56: with CT-07 (48). CT-57: 18. CT-58: as CT-38b (45).
- CT-59: CT-59a 30, CT-59b 31, CT-59c 32, CT-59d 33, CT-59e 35, CT-59f1 36 [R5 row], CT-59f2 37, CT-59g 38 (parent operation).
- CT-60: 34 (cxx). CT-61: CT-61p 46, A2-31 47. CT-62: 56. CT-63: CT-63a 1 (cxx) [Q77], CT-63b 10 [Q77].
- CT-64: 19. CT-65: 35 (cxx). CT-66: 36 (cxx). CT-67: 37 (cxx). CT-68: 33 (cxx, class to confirm).
- CT-69: 52. CT-70: 50. CT-71: 28. CT-72: CT-72a 41, CT-72b 43.
- CT-73: .1 and .2 52; .3 and .4 53; .5-.8 54; .9-.12 55. CT-74: 44. CT-75: 42.
- CT-76: CT-76a 13, CT-76b 15, CT-76c 17, CT-76d 20. CT-77: 53. CT-78: 56. CT-79: 45.
- CT-80: recurring check at every wave boundary from 0a (parent); CT-80a 25.
- CT-81: 39.
- Mods with no ticket of their own (CT-02b's non-Bash rules after D102; proposed home CT-31a or a
  mods row at the fold): A2-16 28, A2-17 30, A2-18 32.
- Not tickets: D7 spike 0a; D49 tooling 0c; D51 items pre (item 1 is CT-02b.1); D99 = A2-30 40;
  spec fold and typed stages: gate. Dropped by D102: A2-7, A2-9, A2-10; reshaped into hook units:
  A2-8, A2-15, A2-20, A2-21.

GitHub issues (cxx unless marked):
- #4, #9: inside CT-26b (5). #11: closes after #61. #12: close 0a. #13: 13-offline 1, heavy 5 [R4].
- #14 11 [R4], #15 12 [R4], #16: 16-offline 1, heavy 3. #17: 17-offline 1, heavy 2. #18: 18-offline 9,
  heavy 10. #19 13 [R4]. #20: 20-offline 0c, heavy gate. #21: 21-offline 0a, heavy 0b. #22: 22-offline 7,
  heavy 8. #23 14. #24, #25: close 0c. #26 16. #27: 27-offline and heavy 15. #28: lane 21. #29: lane 24.
- #30 22, #31 23, #32 24, #33 25, #34 26, #35 28, #36 38, #37 39, #38 29, #39 40, #40 41, #41 30, #42 27,
  #43 31, #44 42, #45 43, #46 44, #47 32, #48 45, #49 46, #50 47, #51 48, #52 49, #53 50, #54 52,
  #55 51, #56 51, #57 51, #58 53, #59 54, #60 55, #61 56.
- #62-#78: closes from 0c, one at a time (D86); #69 after its acceptance; #78 after #69.
- #79-#82, #90, #92-#94, #97: closes from wave 1. #83: closes with its children. #91: user after 2026-10-19.
- #95: lane 6. #96: 96-offline 1 (if needed), heavy 4. #98: lane 49. #99 17, #100 19, #102 20, #103 21,
  #104 and #105 57. #106-#108: held. #101: closed (D90).

## 5. Hot-path conflicts resolved

`frontier.toml` `hot_paths`: at wave 10 the parent rewrites the list as in v1 with two changes:
`dev/hooks/` stays for good (D102) and `dev/test_hooks.py` joins it; the `register.ts` entry stays
but its writer count drops to 16. Kept from v1: replace `dev/check.py` and `dev/lane.py` with CT-39's
package paths; add `hk.pkl`, `mise.dev.lock`, `evidence/onboarding/baseline-files*.json`,
`plugins/aggregated-research/.claude-plugin/plugin.json`, `ci/acceptance.sh`, `.github/workflows/`,
`mods/package.json`, `mods/pnpm-lock.yaml`, CT-52's codegen job list, `offline-sources.toml`,
`docs/research/prior-work.toml`; narrow `.claude/skills/` to its tree-wide writers. Add the saved
searches catalog (CT-80a 25, CT-74 44; different waves). CT-40's cxx class list later gains CT-45,
CT-53, CT-60, CT-65..CT-68.

`dev/hooks/**` and `dev/test_hooks.py` (new hot set under D102): writers CT-02b.1 (18), CT-02b.2 (19),
A2-11 (20, `test_hooks` assertion only), CT-02b.3 (21), CT-02b.4 (23), CT-32b (27), CT-17b (29), all in
lane 2, so serial; `pretooluse_gate.py` passes CT-02b.2 -> .3 -> .4 -> CT-32b; `stop_gate.py` passes
CT-02b.1 -> CT-32b -> CT-17b. The scripts stay stdlib-only and keep importing `git_gate.py`; the
shared decision table is a data file (CT-38a creates it at 12, CT-02b.2 reads it).

`.claude/settings.json`: writers A2-4 (13, `enabledPlugins`), CT-02b.1 (18, the Stop and SubagentStop
entries if the `onFailure` lines change), A2-11 (20, deletes the SessionStart entry). The `hooks` key
keeps exactly the three deny gates; `test_hooks` asserts that set.

`mise.dev.toml`: as v1. A2-6 adds only `mods:*` rows (no `gates:bash`); with D7 every new row lives in
`mise/tasks/<unit>.toml`; `[tools]` and `[deps]` changes are parent hunks one at a time. The rows
`test:hooks`, `retro:gate-merge` and `retro:gate-push` keep calling `dev/hooks/` and `dev/test_hooks.py`
by path (section 6, U2).

`pyproject.toml`, `uv.lock`: as v1 (CT-39 alone through wave 9, then parent hunks with one
`deps:lock` per dependency add).

`hk.pkl`: CT-26a (1), 39-8 (9), A2-6 (15); CT-02b.3's `hooks:install` guard and later steps are parent
hunks.

`.claude/skills/` and `.agents/skills/`: as v1; the ticket-frontier order gains CT-81 after CT-25:
CT-40 (0a) -> CT-30 (1) -> 39-7 (8) -> CT-59f2 (37) -> CT-25 (38) -> CT-81 (39).

`mods/` and the plugin: `mods/**` configuration only from A2-1..A2-3. `register.ts` writers, all
lane 2, never two in a wave: A2-4 (13), A2-25 (16), A2-11 (20), A2-13 (24), A2-14 (26), A2-16 (28),
A2-17 (30), A2-18 (32), A2-26 (34), A2-29 (35), A2-23 (37), A2-27 (38), A2-28 (39), A2-32 (41),
A2-33 (42), A2-31 (47). `stop-gates.ts`, `bash-gate.ts` and `shell.ts` no longer exist; `budget.ts`
and `prompt-context.ts` pass A2-13 -> A2-19 -> A2-33; `agent-gate.ts` passes A2-14 -> A2-19 -> A2-32.
No mod hooks `tool.call` on Bash; a Bash rule that a mod needs uses `tool.check` (hooks-and-mods.md).

Others as v1: `dev/check.py` (CT-08 before 13-offline); `dev/toolchains/` (CT-63a in wave 1 before the
split units; 39-6 and CT-63b between heavy executions); `docs/agents/claude-team.md` one writer per
wave; plugin and baseline files one per wave across all three columns, each re-recording the
baseline and bumping `plugin.json`; `.github/workflows/` (CT-26b 5, A2-6 15); `schemas/` (CT-52
owns the codegen list); `offline-sources.toml` (CT-41 -> CT-42 -> CT-75); `prior-work.toml`
(generated, never hand-edited by CT-73 units); `AGENTS.md` (CT-76d).

## 6. Risks and items for the user

Settled since v1: A2-0 at the gate (D104); the D71 reading (D105); A2-8's admission (D108, now on
CT-02b.2); Q68, Q70, Q71 (D102, D103, R2); CT-73's twelve units (D108); the crawl against the disk
gate (D107).

Still needs the user:
- U1. Q77: CT-63a is placed provisionally as the first wave-1 cxx unit. It edits 27 callers plus the
  configure file, over the five-file unit limit (`codex-task-orchestration.md:204`): accept it as one
  mechanical unit or split it (lock module and configure, then the callers). If Q77 picks another
  route, CT-63 returns to one post-CT-39 unit at wave 10 and dotfiles must not change `host_lock.py`
  until then.
- U2. D60 against D102: D60 retires bare `dev/*.py` calls, but the three gates, `git_gate.py` and
  `dev/test_hooks.py` must stay stdlib files called with `python3 -I` from settings hooks and from the
  `test:hooks`, `retro:gate-merge` and `retro:gate-push` rows. Record that as a dated exception to D60
  beside D102, or say where they should live.
- U3. #13 fallback [R4]: if the verdict fails, #23 and #30-#61 stall, CT-60 and CT-65..CT-69 never land,
  and ADR 0006 blocks CT-62 and CT-78. Decide after R4 (D106).
- U4. D99 meets R1's #99130: the remote switch turns off hook modules in installed plugins, so the
  consumer plugin's SessionStart install step (A2-30, wave 40) could vanish for every consumer while the
  switch serves off, and managed-settings orgs never run `classic.SessionStart` (A2 G4). It is not a deny
  gate, but it is product behaviour: confirm D99, or keep that hook a plugin settings hook (D102-style
  exception) with a mod stand-down pair as R1 section 5 describes.
- U5. R1 section 5 proposes closing the `delivery:publish` hole at the source (`dev/git_delivery.py
  publish` runs `git_gate.py push` itself). Proposed home: an acceptance row on CT-18 (wave 17), which
  wraps that path; it would no longer depend on the Bash hook alone.
- U6. Outward steps, each on explicit instruction: knowledge-base private after CT-64 (19); dotfiles
  private after its public-fetch check (53); CT-62 and CT-78 (56); #106-#108; PR #109.
- U7. After 2026-10-19: CT-07 (48), CT-59g's Codex smoke, A1's removal of the user-level Codex skills,
  #91, D80's Codex follow-ups.
- Admissions as waves arrive: container build (5), plugin install and OCI runs (19, 21), provider calls
  (20, 24, 25, 52-55), other-repository reads (28), clone and live refresh under D86 (26, 42), fnox
  profile and cost caps (47, 52), transcript reads (44), graph binary (49), graphviz (51).

Risks:
- Throughput: 127 lane units and 69 cxx units, each with a serial parent merge and A09 publish; the
  parent is the bottleneck until CT-18 (17) and CT-17 (23). D105's tracking data decides whether more
  parallelism is safe.
- R5 is unwritten: the throttle (CT-33, wave 12) and the tracking tools (CT-25, CT-59f1) may change
  their designs, not the order; CT-33 is the nearest unit that needs R5's answer.
- Mods remain one failure domain for the non-gating features (context lines, WebFetch, session start,
  UI); D102 limits the cost to lost context, not lost enforcement. CT-80 must catch changes in #99130,
  #96831, #100869, #92533, #101384, #84320; a fix there can reopen D102.
- Wave 1 now holds five cxx units (CT-63a plus four split units) that all precede CT-39; if they lag the
  two lanes, CT-39, the critical path, starts late.
- CT-39 size is unverified (whether `git mv` counts toward the 300-line limit).
- Ledger rows still to rewrite: CT-02b, CT-17, CT-32b as hook work (not mods); CT-31's path
  (`.claude/skills/workflow-mods/`, `mods/`); CT-63's scope; v1's list (CT-59, CT-71, CT-73, CT-75,
  CT-41, CT-53 blockers); Phase 4b wave 1 D54 pins (done, D91); `spec.md:34, 47, 61` stale wording.

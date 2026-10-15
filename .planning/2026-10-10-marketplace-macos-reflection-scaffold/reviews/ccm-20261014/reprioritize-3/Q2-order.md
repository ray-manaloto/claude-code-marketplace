# Q2: third reprioritization, merged order after grill rounds 3-5

Read-only, 2026-10-14, agent Q2 of session `ccm-20261014` (`ce9c0b3d`), tip `21af565`. This file is
the only write. P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. Inputs read in
full or by section: `P/task_plan.md` (Phase 4b table and bullets, Tickets CT-01..CT-79, Decisions
D1-D100), `P/decisions.jsonl` DL-105..DL-130, `P/ticket-ledger.md`, `reprioritize-2/` P1 and P2,
`project-import/` DF-A (3.0, 3.7, 5), DF-B (3.1, 5), KB-A (3.2, 5), KB-B (sibling rows, decision, 5),
C1 (3.4-3.6, 5), A1 (3.2-3.6, 5), A2 (all), `docs/adr/0006`, `docs/adr/0007`,
`grill-round3-questions.md`, HANDOFF section 2, `P/frontier.toml`, issues #26-#29 and commits
`cbb455b` (#28) and `66905b4` (#29). `P/reviews/ccm-20261014/research5/` is empty at the time of
writing: R1-R3 are absent, so every unit that Q68, Q70 or Q71 can change is marked provisional.

Method: the order was entered as data in a scratch script that checks single placement of every
unit, that each dependency lands in an earlier wave (or earlier in the same cell, or by one of five
named intra-wave cut rules), and that no hot-path class appears in two columns of one wave. Result:
197 units and operations, 62 wave rows, rc 0. Markers: `[Q68]`, `[Q70]`, `[Q71]` = provisional on
that open question; `[D7]` = placement holds only if the D7 spike passes (section 6, U2).

New unit ids this report proposes (the parent confirms them at the fold): A2-30 (D99, the plugin's
SessionStart hook as a mod), A2-31 (CT-61's mod), A2-32 (CT-19's mod part), A2-33 (CT-37's mod part),
CT-23p (CT-23's Python part, `plan:status` and `ctx:status`, which A2-19 needs), CT-61p (CT-61's Python
part, `guidance:record` and `guidance:fired`), CT-39 units 39-1..39-8, CT-76a..CT-76d, CT-72a and
CT-72b (C1-2's own a/b split), CT-73.1..CT-73.12 (C1-3's twelve topics).

## 1. Dependency graph additions (new edges only)

Notation `A -> B`: B waits for A. "soft" = ordering the source recommends, not a hard input.

From A2 (`project-import/A2-typescript-mods-library.md` section 3 table, section 2):
- CT-26a -> A2-1, A2-6; CT-26b -> A2-6 (`claude` in CI, D89); CT-38a -> A2-4; CT-39 -> A2-10, A2-22,
  A2-24; WDI (w0-doctor integration) -> A2-11, A2-12, A2-26; CT-19 -> A2-14, A2-17; CT-17 -> A2-21;
  CT-32a -> A2-20, A2-28; CT-29b -> A2-27 (CT-31b's ledger blocker).
- A2-0 arms -> A2-1 (arm 1), A2-2 (2), A2-4 (1), A2-5 (7), A2-6 (8), A2-7 (3), A2-9 (4), A2-13 (9),
  A2-23 (5).
- Internal chain: A2-1 -> A2-2 -> A2-3 -> A2-4 -> A2-5 -> A2-6 and A2-8; A2-6 -> every feature unit
  A2-7, A2-9, A2-11, A2-13, A2-16..A2-18, A2-23, A2-25..A2-33 (D92 foundation rule); A2-8 -> A2-9,
  A2-16, A2-17, A2-18; A2-9 -> A2-10, A2-15; A2-12 -> A2-13 -> A2-14 -> A2-19; A2-7 + A2-15 -> A2-20
  -> A2-21; A2-22 -> A2-23; A2-24 -> A2-25; A2-26 -> A2-27, A2-28.
- A2-24 replaces "CT-36" as the blocker of CT-33, CT-60 and CT-76 (they need the `web:fetch` task and
  webclaw pin, not the WebFetch mod).

Q2-added units (A2 section 1.2 rows with no unit; D99):
- CT-23p -> A2-19 (A2 section 3: "`plan:status` task (CT-23 Python part)").
- CT-38b -> CT-61p -> A2-31 (DF-A 3.7 DF-A-2 blockers CT-58 = CT-38b; A2 1.2 CT-61 row).
- CT-19 + A2-14 -> A2-32 (A2 1.2 CT-19 row; same `agent-gate.ts`).
- CT-37 + A2-19 -> A2-33 (A2 1.2 CT-37 row; same `lib/budget.ts`).
- A2-6, CT-08, CT-57, CT-64, #28 -> A2-30 (D99: baseline re-record and version bump; CT-57's bump check
  first; CT-64 and #28 edit the same plugin and its SessionStart install path).

From A1 (`A1-agent-dispatch-skills.md` 3.3, 3.4):
- CT-52 -> CT-59a (owner of `schemas/**`, D83); CT-59a -> CT-59b -> CT-59c -> CT-59d; CT-39 -> CT-59b,
  CT-59d.
- CT-59d + CT-38a -> CT-59e; CT-07 -> CT-59e soft only. This replaces the ledger's "CT-59 blocked by
  CT-07" for the whole ticket.
- CT-59d + CT-19 + CT-40 -> CT-59f1 -> CT-59f2 -> CT-25 (never beside CT-25; row 5 says CT-25 keeps
  the gate CT-59f2 leaves, so CT-59f2 first).
- CT-59e + CT-59f2 -> CT-59g (parent operation, admission per run).
- CT-59d -> CT-37 (row 7: the fresh `claude -p` acceptance runs through `dispatch:claude`).

From C1 (`C1-research-corpus.md` 3.4, 3.5, 5):
- CT-52 -> CT-41 (CT-41 row 1: the manifest schema is a committed schema and its loader is generated
  by CT-52; D83). This puts CT-52 on the corpus chain.
- CT-11 + CT-08 -> CT-71 (C1-1 blockers: lock; `/offline/` ignore line).
- CT-71 + CT-52 -> CT-72a; CT-72a + CT-44 -> CT-72b (C1-2 split a/b).
- CT-42 -> CT-75 (C1-5 blockers).
- CT-75 + CT-44 -> each CT-73.n (C1-3 blockers).
- CT-72a + CT-74 -> CT-79 (C1 section 5, TR items).
- CT-33 -> CT-55 (CT-55 row 1: any graph indexes receipted corpus files only).
- CT-71, CT-72a, CT-74, CT-75 -> CT-62 and CT-78 (C1 section 5, dotfiles and knowledge-base items).

From DF-A and DF-B:
- CT-63 -> CT-11 (DF-B 3.1: CT-11's check lock reuses the primitive).
- CT-63 -> CT-62, CT-77 (DF-B section 5 item 1; no dotfiles change before MP stops loading
  `host_lock.py`).
- CT-76d -> CT-62 (DF-A section 5 item 6: `AGENTS.md` research route must leave dotfiles first).
- CT-76d -> #29 soft (the Context7 live measurement runs through the research profile route CT-76
  repoints; D100).
- CT-62 waits for every owner named in DF-A and DF-B section 5, now enumerated: A2-7..A2-10,
  A2-15..A2-18 (CT-02b), A2-20 (CT-32b), A2-22, A2-23 (CT-35), A2-26..A2-29 (CT-31), A2-31 and CT-61p,
  A2-32 and CT-19, CT-17, CT-20a, CT-20b, CT-22b, CT-26a, CT-29b, CT-32a, CT-37, CT-38a, CT-38b,
  CT-49, CT-51, CT-52, CT-59e, CT-59f2, CT-60, CT-63, CT-07, plus A1's host sunset operation.

From KB-A and KB-B:
- CT-17 -> CT-49 (KB-B 49-K2: the mutation-arm runner is blocked by CT-17).
- CT-49, CT-38b, A2-23, CT-37, CT-55, CT-26a, CT-63 -> CT-77 (KB-B "A decision to bring to the user":
  evals via CT-49, md_budget via CT-38a and CT-58, the launcher via CT-35 and CT-37, the graph receipt
  via CT-55's adopt-or-drop note, currency via CT-26a; D96 exports them).
- CT-64 -> #28 (path: KB-A-1 rewrites the `trackers` backend and `ci/acceptance.sh`; #28's body says
  it updates "only the corresponding acceptance assertion" of the same contract).
- CT-57 -> CT-64 soft (D89: the bump check lands before the next plugin change).
- CT-78 waits for every owner in KB-A and KB-B section 5, including CT-65..CT-69, CT-70, CT-10,
  CT-20a, CT-20b, CT-47, CT-55, CT-75 and CT-77.

From the decisions:
- CT-52 -> #26 (D83: #26 generates C++ records from the committed schemas).
- #26 -> CT-53 (D83: CT-53 checks that #26's records reflect back to identical schemas). This
  replaces the ledger's "#21 foundation" blocker.
- CT-08 -> A2-30 (D99).
- CT-38a -> A2-10 (resolution: CT-38a's lint and the Bash gate share one command decision table,
  Phase 4b CT-38 rows; CT-38a creates it, A2-10 moves the gate into the package and reads it).

Path edges this order adds:
- CT-08 -> 13-offline (both edit `dev/check.py`: D6 scope, P1 section 3 for `4905c8e`).
- 39-6 -> 22-offline, 18-offline (split units cut after CT-39 moves `dev/toolchains/**`).

Edges to remove or rewrite in the ledger: CT-32b "blocked by w0-session-hooks" (lane closed, D97;
now A2-7 and A2-15); CT-31a "CT-02, w0-doctor" (now the A2 chain); CT-35 and CT-36 "D61/D62" (now
A2-22/A2-23 and A2-24/A2-25); P2's "CT-22b -> CT-23" (A2-12 needs only WDI); "CT-36 (webclaw pin)" on
CT-33 (now A2-24).

## 2. Critical path and priority rule

Critical path (longest dependency chain to the end state, the knowledge-base sunset):
gate -> wave-1 split units (17-, 16-, 13-offline) -> CT-39 (39-1..39-8) -> CT-63 -> #18 heavy -> #23
(also fed by #13 heavy -> #14 -> #15 -> #19) -> #30 (also needs CT-52 -> #26, #27, and CT-57 -> CT-64
-> #28) -> #31 -> #32, #33, #34 -> #42, #35, #38, #41 -> #43 -> #47 -> CT-68 -> CT-69 -> CT-78.
27 units long counted from the w0-doctor integration; the chain to #61 is 30. Because the cxx slot is one serial queue, every cxx unit
before #47 lies on it: #47 is the 39th of 68 cxx units (wave 32). CT-62 waits on the same queue
through CT-60 (#32-#34) and on the mods stream, whose longest chain is CT-38a -> A2-4 -> A2-5 -> A2-6
-> A2-13 -> A2-14 -> A2-19 -> A2-33.

What sets the end date: both columns are saturated. About 126 lane units on two lanes end at wave
56; 68 cxx units end at wave 57. A slip in either column moves the sunsets, so the throughput levers
(CT-18 at wave 17, CT-17 at wave 23, and the options in section 6) matter as much as the order.
Risk on the path: if the #13 verdict fails again (P1 E5), #19 never closes and the chain stops at
#23 (section 6, U3).

Priority rule, in order:
1. Hard gates: D77 (only pre to 0c before publication, plus the D86-admitted CT-34 and, if approved,
   A2-0 at the gate); D71 (CT-39 alone over `dev/**`); D68 and D84 (one heavy run at a time in D5 order
   #21 > #20 > #17 > #16 > #96 > LLVM chain, per-class disk gate); D92 (A2-0..A2-6 before every mod
   feature); D85 prerequisites (CT-30 -> CT-29a; CT-26a and CT-29a -> CT-39; CT-08 -> CT-26b); D75.
2. Heavy-run protection: CT-63 in the first heavy gap after CT-39.
3. cxx feed deadlines: a lane unit that blocks a cxx unit lands before the queue reaches it (CT-52
   before #26, CT-57 -> CT-64 -> #28 before #30, #29 before #40).
4. User weight (Q46, D100): the webclaw and research chain (A2-24, CT-41, CT-33, CT-43, CT-44, A2-25,
   CT-76a-d) outranks every other unit of equal readiness.
5. K1: longest remaining path, then out-degree.
6. Hot paths disjoint across columns in a wave; on a tie, the smaller unit first.
cxx slot: D5 order among the listed runs; otherwise #23's prerequisites, then the #30 chain toward
#47 and the sunset-owning operations (CT-68, CT-60, CT-65..CT-67); LLVM units fill only while the
critical cxx unit waits on a lane prerequisite (#99, #100, #102, #103), the rest at the tail.

Deliberate changes from D82's table (parent-level): the spine moves later (CT-05 3 -> 22, CT-17 4 ->
23, CT-19 6 -> 25, CT-22b 8 -> 33, CT-25 9 -> 38) because rules 3-4 and D92 now come first; #23 runs
before the LLVM tail; 22-offline and 18-offline run on the package path after 39-6.

## 3. Wave table

CT-39 owns `dev/**` alone in waves 2-9 except `dev/hooks/**` and `dev/test_hooks.py`, which A2-7 and
A2-10 retire. A cell "X, then Y" is serial in one lane.

| Wave | Lane 1 | Lane 2 | cxx slot | Parent operations and admissions |
|---|---|---|---|---|
| pre | w0-doctor integration (serial; keep its settings SessionStart entry, A2-11 deletes it) | none | none (parent writes `lanes/21-offline.json`) | A09 publish; drain proposals; D51 items 4-6 read-only, item 7 (`test:frontier` row) in the records commit; research5 R1-R3 running (D100) |
| 0a | CT-40 | D7 spike (`mise/` only) | 21-offline (fallback 27-offline) | close #12 (D70; D86 standing close admission) |
| 0b | w0-doctor-records | CT-21 | #21 heavy (first project-build class run; record peak, D84) | none |
| 0c | D49 tooling | none (w0-session-hooks closed, D97) | 20-offline | closes #24, #25, then #62-#78 one at a time as CT-21's evidence allows (D86) |
| gate | A2-0 spike, receipt only (informs Q68, Q70, Q71) | CT-34 audit, read-only | #20 heavy | user: approve A2-0 before publication and its fresh-session admission, type arms 1, 5, 9; parent: spec fold after CT-34 and A2-0 (CT-25..CT-79, A2-0..A2-33, CT-59a..g, unit partitions, D59..D100, import acceptance rows, R1-R3); user: typed stages in a fresh session (D90); `ledger:sync`; `frontier.toml` `[waves]` |
| 1 | CT-08, then CT-29a | CT-26a, then A2-1 | 17-offline, 16-offline, 13-offline (cut after CT-08 lands), 96-offline if #96 needs one | parent runs CT-30 first (D75); A2-1 network once (pnpm lock; node, pnpm, claude tools); qualified closes #90, #92, #93, #94, #97, #79-#82 (D86, DL-109); D54 pins already applied (D91) |
| 2 | 39-1 package skeleton, config, discovery task | A2-2 | #17 heavy | notice per heavy run (D68) |
| 3 | 39-2 core runner, env allow-list, receipts | A2-3 | #16 heavy | none |
| 4 | 39-3 doctor and handoff callers | CT-14 | #96 heavy (first LLVM-bundle class run, D84) | none |
| 5 | 39-4 planning, lane, retro, check tools; CT-12 wiring | CT-26b (with #4, #9) | #13 heavy (first LSan class run; the #13 verdict) | container-build admission (CT-26b) |
| 6 | 39-5 issue, search, delivery tools | #95 C3 (read-only on `dev/**`) | #13 lane continues (verdict review, retro); no new cut (P1 E2) | none |
| 7 | 39-6 toolchains move | CT-32a [D7] | 22-offline (cut after 39-6 lands) | 39-6 integrates while no heavy run executes |
| 8 | 39-7 skill-bundled scripts, raw `python3` skill lines | A2-24 `web:fetch` [D7] | #22 heavy | `/verify` backlog for units integrated in waves 1-7 (D56); webclaw pin as a parent hunk |
| 9 | 39-8 hk ruff and ty, retire `MARKETPLACE_PYTHON`, `development.yml:18`, old paths | CT-20a [D7] | 18-offline | none |
| 10 | CT-52 | CT-63 | #18 heavy (cut after CT-63 lands) | rewrite `frontier.toml` `hot_paths` (section 5) |
| 11 | CT-41 | CT-11 | #14 | none |
| 12 | CT-33 | CT-38a | #15 | D86 standing webclaw admission, no limits; watch disk against the D84 gate |
| 13 | CT-76a | A2-4 [Q68] | #19 | none |
| 14 | CT-43 | A2-5 | #23 | none |
| 15 | CT-76b | A2-6 [Q68] | 27-offline, then #27 heavy (first native-core class run) | none |
| 16 | CT-44 | A2-25 | #26 | none |
| 17 | CT-76c | CT-18 | #99 (filler while #30 waits) | none |
| 18 | CT-57 | A2-7 [Q68] | CT-53 (split unit, then compile) | `claude plugin validate --strict` joins the host check (D89) |
| 19 | CT-64 | A2-8 | #100 | fresh-session plugin install and OCI acceptance admissions; A2-8 corpus admission (U4); then knowledge-base private (D96, outward) |
| 20 | CT-76d | A2-9 [Q68 Q70] | #102 | one strict research receipt through the fnox research profile |
| 21 | #28 | A2-10 [Q70] (closes CT-39) | #103 | OCI acceptance and fresh Claude session admissions (#28) |
| 22 | CT-05 | A2-11 [Q68] (last settings hook; `hooks` key removed) | #30 | parent hunk: `.claude/AGENTS.md` key list |
| 23 | CT-17 | A2-12 | #31 | none |
| 24 | #29 | A2-13 | #32 | Context7 provider admission (#29) |
| 25 | CT-19 | A2-15 [Q70] | #33 | none |
| 26 | CT-42 | A2-14 | #34 | one clone under D86 |
| 27 | CT-49 | A2-20 [Q70] (CT-32b) | #42 | none |
| 28 | CT-71 | A2-16 [Q70] | #35 | read admission for the dotfiles, knowledge-base and TR checkouts; gitleaks pin |
| 29 | CT-23p | A2-21 (CT-17 stop part) | #38 | none |
| 30 | CT-59a | A2-17 [Q70] | #41 | none |
| 31 | CT-59b | A2-19 | #43 | `jsonschema` pin unless CT-52 pinned it (`deps:lock` network once) |
| 32 | CT-59c | A2-18 [Q70] | #47 | none |
| 33 | CT-59d | CT-22b | CT-68 (class to confirm) | none |
| 34 | CT-29b | A2-26 | CT-60 | network and GitHub API quota for CT-60's live arm |
| 35 | CT-59e | A2-29 | CT-65 | none |
| 36 | CT-59f1 | A2-22 | CT-66 | none |
| 37 | CT-59f2 | A2-23 [Q68 Q71] | CT-67 | CT-35's `/usage` cache check may need a user-typed fresh session |
| 38 | CT-25 (with CT-06) | A2-27 | #36 | CT-59g: one admitted `claude -p` smoke, `codex exec` smoke after 2026-10-19; A1 host sunset after Codex returns, the thread handover and the user's admission |
| 39 | CT-37 | A2-28 | #37 | fresh `claude -p` through `dispatch:claude` (CT-37) |
| 40 | CT-72a | A2-30 (D99) [Q68] | #39 | baseline re-record and plugin bump |
| 41 | CT-75 | A2-32 | #40 | one live refresh under D86 |
| 42 | CT-72b | A2-33 | #44 | none |
| 43 | CT-74 | CT-50 | #45 | none |
| 44 | CT-79 | CT-51 | #46 | transcript-read admission for CT-51's live runs |
| 45 | CT-47 | CT-38b (CT-58) | #48 | network for `--live` (CT-47) |
| 46 | CT-46 | CT-61p | #49 | fnox profile choice and one cost-capped live call (CT-46) |
| 47 | CT-48 | A2-31 [Q68] | #50 | network (CT-48) |
| 48 | CT-55 | CT-07 (with CT-56) | #51 | graph tool binary and cache path (CT-55); Codex available (CT-07) |
| 49 | CT-70 | #98 C2 | #52 | read-only `gh` (CT-70) |
| 50 | CT-54 | CT-10 | #53 | graphviz pin (CT-54) |
| 51 | CT-69 | CT-20b | #55, #56, #57 | capped model spend (CT-69) |
| 52 | CT-77 | CT-73.1, then CT-73.2 | #54 | research route per CT-73 topic (D100); dotfiles public-fetch check, read-only (D96) |
| 53 | CT-73.3, then CT-73.4 | CT-73.5, then CT-73.6 | #58 | none |
| 54 | CT-73.7, then CT-73.8 | CT-73.9, then CT-73.10 | #59 | none |
| 55 | CT-73.11, then CT-73.12 | none | #60 | none |
| 56 | CT-62 | CT-78 | #61 | outward, explicit instruction each: dotfiles writes, push and visibility (CT-62); knowledge-base archive or private (CT-78) |
| 57 | none | none | #104, #105, then CT-45 | held: #106-#108 (CI, push, global); spec #11 and #83 close with their children; draft PR #109 on the user's word |

Any wave after 2026-10-19: #91 and the D80 Codex disk follow-ups (user). Each build session ends with
`/mattpocock-skills:retro` (user, D16).

## 4. Check list (ticket or issue, unit, wave)

Takeover-spec tickets:
- CT-01..CT-04: done. CT-09, CT-13, CT-24: closed (D72). CT-27: not filed. CT-28: dropped (D88).
- CT-02b: A2-7 18 [Q68], A2-8 19, A2-9 20 [Q68 Q70], A2-15 25 [Q70], A2-16 28 [Q70], A2-17 30 [Q70], A2-18 32 [Q70].
- CT-05: 22. CT-06: folded into CT-25 (38). CT-07 with CT-56: 48. CT-08: 1. CT-10: 50. CT-11: 11.
- CT-12: folded; wiring in 39-4 (5), lint and mirror test in CT-38a (12). CT-14: 4.
- CT-15: split into CT-30 (1), CT-29 (1, 34), CT-22b (33). CT-16: folded into CT-22b (33).
- CT-17: CT-17 23 (with CT-24's remainder), A2-21 29. CT-18: 17. CT-19: CT-19 25, A2-32 41.
- CT-20: CT-20a 9 [D7], CT-20b 51. CT-21: 0b.
- CT-22: CT-22a = w0-doctor integration pre, w0-doctor-records 0b, A2-11 22 [Q68]; CT-22b 33.
- CT-23: A2-12 23, A2-13 24, A2-14 26, CT-23p 29, A2-19 31. CT-25: 38.
- CT-26: CT-26a 1, CT-26b 5. CT-29: CT-29a 1, CT-29b 34. CT-30: 1 (parent, D75).
- CT-31a: A2-0 gate (informs Q68, Q70, Q71), A2-1 1, A2-2 2, A2-3 3, A2-4 13 [Q68], A2-5 14, A2-6 15 [Q68], A2-26 34.
- CT-31b: A2-29 35, A2-27 38, A2-28 39. CT-32a: 7 [D7]. CT-32b: A2-20 27 [Q70]. CT-33: 12. CT-34: gate.
- CT-35: A2-22 36, A2-23 37 [Q68 Q71]. CT-36: A2-24 8 [D7], A2-25 16. CT-37: CT-37 39, A2-33 42.
- CT-38: CT-38a 12, CT-38b (= CT-58) 45.
- CT-39: 39-1 2, 39-2 3, 39-3 4, 39-4 5, 39-5 6, 39-6 7, 39-7 8, 39-8 9, A2-10 21 [Q70] (closes it).
- CT-40: 0a. CT-41: 11. CT-42: 26. CT-43: 14. CT-44: 16. CT-45: 57 (cxx). CT-46: 46. CT-47: 45.
- CT-48: 47. CT-49: 27. CT-50: 43. CT-51: 44. CT-52: 10. CT-53: 18 (cxx). CT-54: 50. CT-55: 48.
- CT-56: with CT-07 (48). CT-57: 18. CT-58: as CT-38b (45).
- CT-59: CT-59a 30, CT-59b 31, CT-59c 32, CT-59d 33, CT-59e 35, CT-59f1 36, CT-59f2 37, CT-59g 38 (parent operation).
- CT-60: 34 (cxx). CT-61: CT-61p 46, A2-31 47 [Q68]. CT-62: 56. CT-63: 10. CT-64: 19.
- CT-65: 35 (cxx). CT-66: 36 (cxx). CT-67: 37 (cxx). CT-68: 33 (cxx, class to confirm). CT-69: 51.
- CT-70: 49. CT-71: 28. CT-72: CT-72a 40, CT-72b 42.
- CT-73: CT-73.1 and .2 52; .3-.6 53; .7-.10 54; .11 and .12 55. CT-74: 43. CT-75: 41.
- CT-76: CT-76a 13, CT-76b 15, CT-76c 17, CT-76d 20. CT-77: 52. CT-78: 56. CT-79: 44.
- Not tickets: D7 spike 0a; D49 tooling 0c; D51 items pre (item 1 is A2-7); D99 = A2-30 40 [Q68]
  (proposed home: CT-31a or its own row at the fold); spec fold and typed stages: gate.

GitHub issues (cxx unless marked lane or close):
- #4, #9: inside CT-26b (5). #11: closes after #61. #12: close 0a. #13: 13-offline 1, heavy 5.
- #14 11, #15 12, #16: 16-offline 1, heavy 3. #17: 17-offline 1, heavy 2. #18: 18-offline 9, heavy 10.
- #19 13. #20: 20-offline 0c, heavy gate. #21: 21-offline 0a, heavy 0b. #22: 22-offline 7, heavy 8.
- #23 14. #24, #25: close 0c. #26 16. #27: 27-offline and heavy 15. #28: lane 21. #29: lane 24.
- #30 22, #31 23, #32 24, #33 25, #34 26, #35 28, #36 38, #37 39, #38 29, #39 40, #40 41, #41 30, #42 27,
  #43 31, #44 42, #45 43, #46 44, #47 32, #48 45, #49 46, #50 47, #51 48, #52 49, #53 50, #54 52,
  #55 51, #56 51, #57 51, #58 53, #59 54, #60 55, #61 56.
- #62-#78: closes from 0c, one at a time (D86); #69 after its acceptance; #78 after #69.
- #79-#82, #90, #92, #93, #94, #97: closes from wave 1. #83: closes with its children. #91: user after 2026-10-19.
- #95: lane 6. #96: 96-offline 1 (if needed), heavy 4. #98: lane 49. #99 17, #100 19, #102 20, #103 21,
  #104 and #105 57. #106-#108: held (CI, push, global; not D68). #101: closed (D90).

## 5. Hot-path conflicts resolved

`frontier.toml` `hot_paths` (today `dev/check.py`, `dev/hooks/`, `dev/lane.py`,
`docs/agents/claude-team.md`, `.claude/settings.json`, `AGENTS.md`; CT-40 adds `mise.dev.toml`,
`pyproject.toml`, `uv.lock`, `.claude/skills/`). At wave 10 the parent rewrites the list: replace
`dev/check.py` and `dev/lane.py` with the package paths CT-39 names; keep `dev/hooks/` and
`dev/test_hooks.py` until A2-10 (wave 21); add `hk.pkl`, `mise.dev.lock`,
`evidence/onboarding/baseline-files*.json`, `plugins/aggregated-research/.claude-plugin/plugin.json`,
`ci/acceptance.sh`, `.github/workflows/`, `.claude/skills/workflow-mods/hooks/register.ts`,
`mods/package.json`, `mods/pnpm-lock.yaml`, CT-52's codegen job list under `schemas/`,
`offline-sources.toml`, `docs/research/prior-work.toml`. Narrow `.claude/skills/` to its tree-wide
writers (39-7, CT-38a, CT-38b); every other skill writer owns only its own `<name>/` pair. CT-40's
cxx class list later gains CT-45, CT-53, CT-60 and CT-65..CT-68 once filed (spec #11 operations and
native work; CT-68's class to confirm).

`mise.dev.toml`: wave 1 has three writers. CT-26a and A2-1 run serially in lane 2 (both edit
`[tools]` and `mise.dev.lock`); CT-29a's session rows go to `mise/tasks/session.toml` if D7 passes,
else a parent hunk. From then on, if D7 passes every new task row lives in `mise/tasks/<unit>.toml`;
`[tools]` and `[deps]` changes (A2-24 webclaw, CT-71 gitleaks, CT-54 graphviz, CT-55 binary, A2-6's
`[deps.pnpm]`) are declared parent hunks the merger applies one at a time. If D7 fails, every row is
a parent hunk at integration (HANDOFF 2(e)). During CT-39 only CT-39 edits existing rows; the three
`[D7]` units add include files only.

`.claude/settings.json`: writers A2-4 (13, `enabledPlugins`), A2-7 (18), A2-9 (20), A2-11 (22, removes
`hooks`); one per wave. w0-doctor integrates as reviewed with its SessionStart entry and A2-11 deletes
it (A2 section 4). The same four units are the only writers of `dev/test_hooks.py` (or its package
successor) and run in distinct waves.

`pyproject.toml`, `uv.lock`: CT-39 alone through 39-8 (wave 9). After that, parent hunks only:
dependency adds (CT-52's generator, CT-59b's `jsonschema`, any CT-76 provider client) are declared in
the brief and applied with one `deps:lock` run at integration, never two without a re-lock between.
CT-64's runtime package keeps its own manifest under `plugins/aggregated-research/`.

`hk.pkl`: CT-26a (1, hk locked), 39-8 (9, ruff and ty steps, DF-B r10 and r11), A2-6 (15, biome, mods,
actionlint, zizmor, pre-push). Later steps (CT-38a lint, CT-52 `codegen:check`) are parent hunks.

`.claude/skills/` and `.agents/skills/`: ticket-frontier passes CT-40 (0a) -> CT-30 (1) -> 39-7 (8)
-> CT-59f2 (37) -> CT-25 (38); session-handoff and session-resume pass CT-29a (1) -> 39-3 (4) ->
CT-29b (34) -> CT-37 (39); verify CT-32a (7); offline-corpus CT-44 (16); claude-agent and codex-agent
CT-59e (35); recall-work CT-70 (49); codex-session-history 39-7 (8) -> CT-10 (50). The tree-wide
writers 39-7, CT-38a and CT-38b share no wave with another skill writer.
`.claude/skills/workflow-mods/` is a skills-dir plugin with no `.agents` twin: CT-38a's lint lists it
as the single exception (DF-A 3.0 decision 3, KB-A CT-38 row 3).

`mods/` and the plugin: `mods/**` configuration is written only by A2-1..A2-3 (waves 1-3). Every
feature adds one import line to `register.ts`, so its 18 writers all run in lane 2 and never share a
wave (13, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 35, 37, 38, 39, 41, 42, 47). Shared feature files
are serial by wave: `stop-gates.ts` A2-7 -> A2-15 -> A2-20 -> A2-21; `bash-gate.ts` A2-9 -> A2-15 ->
A2-20; `shell.ts` A2-8 -> A2-15; `lanes.ts` A2-21 (29) -> A2-17 (30); `budget.ts` and
`prompt-context.ts` A2-13 -> A2-19 -> A2-33; `agent-gate.ts` A2-14 -> A2-19 -> A2-32.

Others:
- `dev/check.py`: CT-08 and 13-offline in wave 1; 13-offline is cut after CT-08 integrates.
- `dev/toolchains/p2996_configure.py`: 39-6 (7) and CT-63 (10) each land between heavy executions;
  22-offline and 18-offline are cut on the package path after 39-6.
- `docs/agents/claude-team.md`: CT-40 (0a), D49 (0c), CT-30 (1), CT-17 (23), A2-19 (31, the Hook
  composition and Context budget split from the w0-docs retro), CT-25 (38); one per wave.
- Plugin and baseline files: CT-08 (1), CT-14 (4), CT-26b (5), CT-57 (18), CT-64 (19), #28 (21),
  CT-60 and CT-65..CT-68 in the cxx slot (33-37), A2-30 (40), CT-69 (51); one per wave across all
  three columns, each re-recording the baseline with CT-08's tooling and bumping `plugin.json` (D89).
  CT-57 should define whether plugin `AGENTS.md` and `CLAUDE.md` count as plugin files.
- `.github/workflows/`: CT-26b owns `development.yml` (5) before 39-8 edits line 18 (9); A2-6 adds
  `mods.yml` (15).
- `schemas/`: CT-52 (10) owns the codegen job list; CT-59a (30), the A2 contract schemas and C1's
  three schemas register by parent hunk, the second to land wiring the row (A1 row 2, row 8 the same
  for CT-22b's `dispatch:probe` check, wired by CT-59e).
- `offline-sources.toml`: CT-41 (11) -> CT-42 (26) -> CT-75 (41).
- `docs/research/prior-work.toml`: generated by CT-72a (40); CT-73 units never edit it, the parent
  regenerates it after each integration so paired CT-73 units cannot collide.
- `AGENTS.md`: CT-76d (20) repoints the research route; A2-6's pointer to `docs/agents/workflow-mods.md`
  is a parent hunk.

## 6. Risks and items for the user

Needs the user:
- U1. A2-0 at the gate is a pre-publication unit (an exception to D77 like D86 for CT-34) and needs
  the fresh-session admission with the user typing the interactive arms 1, 5 and 9. Declined: A2-0
  moves to wave 2 lane 2, A2-1..A2-3 follow CT-39, and the mods foundation slips about three waves.
- U2. D71 reading: CT-32a (7), A2-24 (8) and CT-20a (9) run beside CT-39 after 39-2 only as new package
  files with rows in `mise/tasks/<unit>.toml`, touching no `dev/**`, `pyproject.toml`, `uv.lock` or
  `hk.pkl`. If the user or a failed D7 rules that out, they move to waves 10-12 and the webclaw chain
  slips two waves. Option the other way: run 39-3..39-7 two at a time (disjoint subtrees) to cut CT-39
  from eight waves to about five; this amends Phase 4b's "serial units".
- U3. If the #13 verdict fails again (P1 E5), #23 and #30-#61 stall, CT-60 and CT-65..CT-69 never land,
  and ADR 0006 then blocks CT-62 and CT-78 forever. Decide now: keep ADR 0006 strict, or let both
  sunsets proceed once C1-1's bundles and every non-spec-#11 owner have landed, delivering DF-A-1 and
  KB-A-2..KB-A-6 later from the bundles.
- U4. A2-8 needs the bounded, redacted private-input extraction that was admitted to the cancelled
  w0-session-hooks lane: confirm it transfers.
- U5. Until CT-63 (wave 10), MP heavy runs load dotfiles `host_lock.py` by absolute path with a pinned
  digest: freeze that file, or accept that a dotfiles edit stops heavy runs.
- U6. Q68, Q70, Q71 (D100) after R1-R3 and A2-0. Q68 can keep a hook in settings (an exception to D92)
  or move the plugin off skills-dir: A2-4, A2-6, A2-7, A2-9, A2-11, A2-23, A2-30, A2-31. Q70
  (anthropics/claude-code#92533) can keep the Bash gate a settings hook, or add a guard that denies
  `isolation: "worktree"`: A2-9, A2-10, A2-15..A2-18, A2-20. Q71 decides whether A2-23 queues
  `/reload-plugins --force` or the user keeps typing it.
- U7. D99 makes the published plugin depend on the early-access mods API; under managed settings
  `classic.SessionStart` does not run in an installed plugin (A2 S2, G4). Confirm after Q68.
- U8. Outward steps, each on explicit instruction: knowledge-base private after CT-64 (19); dotfiles
  private after its public-fetch check (52); CT-62 and CT-78 (56); #106-#108; PR #109.
- U9. After 2026-10-19: CT-07 (48), CT-59g's Codex smoke, A1's removal of the user-level Codex skills
  and the agent-protocol tree, #91, D80's Codex follow-ups.
- U10. CT-73 is twelve research units, each running the provider route with spend: confirm or trim.
- Admissions as waves arrive: container build (5), plugin install and OCI runs (19, 21), provider
  calls (20, 24, 52-55), other-repository reads (28), clone and live refresh under D86 (26, 41), fnox
  profile and cost caps (46, 51), transcript reads (44), graphviz (50), graph binary (48).

Risks:
- Throughput: about 126 lane units and 68 cxx units, each with a serial parent merge and A09 publish;
  the parent, not the lanes, is the bottleneck until CT-18 (17) and CT-17 (23).
- Disk: D86 removed every corpus limit, so CT-33 (12) and CT-75 (41) can starve the D84 heavy gate;
  the first runs of each class (#21, #96, #13, #27) set the gates.
- One failure domain (A2 G3): after A2-11 every gate lives in one plugin; a broken mod that
  hot-reloads switches all of them off. Early-access API churn against an auto-updating CLI.
- CT-39 size is unverified (whether `git mv` counts toward the 300-line limit); eight units is a
  proposal for the frontier-scheduler.
- Table errors that would misorder if copied: ledger CT-59 "blocked by CT-07", CT-71 without CT-11 and
  CT-08, CT-73 without CT-75 and CT-44, CT-75 without CT-42, CT-41 without CT-52, CT-53 on "#21
  foundation", CT-32b on w0-session-hooks, CT-31's `plugins/workflow-mods/**` path (now
  `.claude/skills/workflow-mods/` and `mods/`); Phase 4b wave 1 still lists the D54 pins (done, D91).
- `spec.md:34, 47, 61` stale wording (P3 section 2) must be fixed in the fold.

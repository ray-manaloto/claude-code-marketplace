# P1: C++ lane supply after D65-D81

Read-only, 2026-10-14, session `ce9c0b3d`, tip `21af565`. Updates `reprioritize/R1-cxx-lane-supply.md` (R1). `frontier.py` is unchanged since `d420a7e` (`git log -1`), so R1 §3 (conflict exits the class, split unit closes its ticket, operations take lanes, undefined split) still holds until CT-40. Re-run: `frontier.py plan --graph r1/data/graph.json` (no `--write`) rc 0, `cxx slot: offline-portion of #21`, `dispatch 12`, `dispatch 24`; `P/frontier/` still absent.

## 1. Inventory

`gh issue list --state all`: every issue below is OPEN, #12 included (close batch not run). `gh api .../issues/<n>/dependencies/blocked_by` matches R1. Class = `frontier.toml:20` today; "D69" = added by CT-40.

| Id | Blockers (gh) | Heavy | Split unit | Size | Admission |
|---|---|---|---|---|---|
| #12 | none | no | n/a (close op, D70 first batch) | S op | close op |
| #13 | #12 | yes | `13-offline` = rebase of `4905c8e` | M | D68 (not in D5 list) |
| #14, #15, #19 | #13; #14; #15 | yes | after blocker | M each | D68 |
| #21, #20, #17, #16 | none | yes | yes | M each | D68, D5 order 1-4 |
| #22, #18 | #21; #16 | yes | after blocker | M | D68 |
| #23 | #15-#22 (8) | yes | no | L | D68 |
| #26 (D69) | #24 (close op) | UNVERIFIED, mostly codegen | mostly | M | D68 if heavy |
| #27 (D69) | none | UNVERIFIED (dependency build) | yes | M | D68 |
| #30-#61 | #30: #23, #25-#28 | mixed | per ticket | M each | D68 |
| #96 (D69) | none | yes (download, verify) | yes | M | D68, D5 position 5 |
| #99, #100 (D69) | #96 | yes | after #96 | L, M | D68 |
| #102-#105 (D69) | #100 (+#99 for #103) | yes | after | M each | D68 |
| #106-#108 | L4/L5 | outward | no | M | CI, push, global (not D68) |
| CT-53 | CT-52 (wave 3-4, needs CT-39), "#21 foundation" | compile only | yes (`include/aggregated_research/schema*.hpp`, `src/schema_emit.cpp`, `tests/cxx/**`, T-tooling-infra.md:125) | M | D68; NOT in CT-40's class list |
| CT-45 | native core, CT-44 (11+) | yes | `cxx/...` (W1-webclaw:148) | L | D68; NOT in CT-40's class list |

Size evidence: prior heavy steps are short once the toolchain exists: max `elapsed_seconds` core-p2996 41.9, p2996-lsan 33.7, p2996-build 363, p2996-resume 1365 (`git grep` over `evidence/<dir>`). So M = one lane cycle with a run of minutes; L = multi-config acceptance or an IWYU/LLVM build.

## 2. cxx slot queue (one unit at a time)

| # | Unit | Prerequisite | Kind | Dur. | Aligned wave | Then |
|---|---|---|---|---|---|---|
| 1 | `21-offline` | lane record with owned_paths | split | S | 0a | 2 |
| 2 | #21 heavy | 1 integrated; D68 gate | heavy | M | 0b | 3 |
| 3 | `20-offline` | none | split | S | 0c | 4 |
| 4 | #20 heavy | 3 | heavy | M | gate | 5 |
| 5 | `17-offline`, then `16-offline` | none | split | S, S | 1 | 6 |
| 6 | `13-offline` | #12 closed; w0-doctor integrated (`dev/check.py`) | split | S | 1 | 7 |
| 7 | #17, #16 heavy | 5 | heavy | M, M | 2 | 8 |
| 8 | #13 heavy | 6 | heavy | M (14c deadlocked before) | 2 | 9 |
| 9 | #96 heavy (`96-offline` first if needed) | none; D5 position 5 | heavy | M | 3 | 10 |
| 10 | `22-offline`, #22 heavy; `18-offline`, #18 heavy | #21; #16 | split, heavy | S, M each | 3-4 | 11 |
| 11 | CT-53 split, then compile | CT-52 and #21 integrated | split, heavy | S, M | 4-5 | 12 |
| 12 | #14, #15, #19 | #13 verdict | heavy | M each | 5-6 | 13 |
| 13 | #99, #100, #102-#105 | #96 | heavy | L, M, M x4 | 6-8 | 14 |
| 14 | #23 | #15-#22 | heavy | L | 8 | 15 |
| 15 | #27, #26 (after #24 close), #30-#61 | #23, #24-#28 | mixed | M each | 9+ | 16 |
| 16 | CT-45 | LLVM chain, CT-44 | heavy | L | 11+ | native core |

Where the slot can still go empty, and the filler:
- E1, 0a: `21-offline` has no lane record (`ls P/lanes/`: no `21-offline.json`) and no row in HANDOFF §2(i) (lines 162-178). Filler: `27-offline` (no blocker, new paths), allocated by hand.
- E2, wave 2: CT-39 owns `dev/**` alone (D71). Every C++ split unit writes `dev/toolchains/*.py` (52 tracked files) or `dev/test_*.py`; `4905c8e` touches `dev/check.py`, `dev/toolchains/p2996_lsan{,_control}.py`, `dev/test_lsan_control.py`. Filler: heavy runs only (they write `evidence/**`), so the split units in rows 5-6 must integrate before CT-39 starts.
- E3, waves 3-5: Phase 4b leaves the cxx column empty for waves 2-4 and puts #22/#18 at wave 6, #96 at wave 8 "after #23". #22 and #18 are ready as soon as #21/#16 are accepted, and D5/D68 put #96 right after #16, so rows 9-10 fill it.
- E4, disk gate blocks: fall back to split units (`96-offline`, `27-offline`, LSan split units).
- E5, if the #13 verdict fails again: #19 never closes, so #23 and #30-#61 stall; only the LLVM chain, #27 and CT-53 remain. This is the long-run supply risk.

## 3. Interactions with non-C++ tickets

- CT-40 (0a): the slot needs it for three things it does not cover yet. (a) D68 is DL-84 `kind: decision`; `frontier.py:280-281` reads only `kind == "admission"` with a `ticket`, so until CT-40 the parent passes `--admitted #21` per run. (b) Capacity counts only `state.json` claims (`frontier.py:352`): today's plan prints `writers 0/3` while w0-doctor is allocated, so hand lanes are invisible. (c) CT-40's class list (`task_plan.md:250-255`) omits CT-53 and CT-45; their issue numbers only exist after the gate.
- w0-doctor: CT-40 needs `dev/plan_decide.py`, which `lanes/w0-doctor.json` lists as excluded; fine if w0-doctor integrates first, as planned.
- w0-doctor-records and w0-session-hooks: their excluded paths include `mise.dev.toml`, `dev/check.py`, `.claude/skills/`, `docs/agents/`, and `frontier.py:362-367` counts excluded paths as active. A cxx unit that wires a test row conflicts until both integrate; use the D7 `mise/tasks/` include if the spike passes, else a parent hunk.
- ct21-codex-imports owns 61 log paths under `evidence/core-p2996/**` and `evidence/p2996-cmake/**`; #21 receipts belong in a new directory.
- CT-52 to CT-53 to #26: #26 (gh body) makes "one canonical Issues request/result catalog [yield] Python and strict POD-style C++ records"; CT-52 makes committed schemas the contract with generated Python; CT-53 emits schema from reflected structs. Under D59 (no dual paths) one generator direction must be chosen before any of them is briefed.
- CT-08: no C++ source is a baseline file (`baseline-files.json`: 19 paths, none under `CMakeLists.txt`, `src/`, `include/`, `cmake/`). Only #37 (plugin delivery), #106 (`.github/workflows/acceptance.yml`) and a container toolchain in root `mise.toml` wait on CT-08. `ticket-ledger.md:137` still says CT-08 wave 4; Phase 4b says wave 1 (D64).
- CT-44 gates CT-45; the #12 and #24 close ops gate #13 and #25/#26/#28.
- Host lease: P2996 runners assert `~/.local/state/dotfiles/heavy-gate.lock` (`dev/toolchains/p2996_build.py:274`), shared with dotfiles work (D66); a dotfiles heavy job blocks the cxx heavy run.

## 4. Disk and resources

- Free now: `df -h /System/Volumes/Data` 316 GiB (83% used), not 321 (grill receipt); 5 GiB drift within hours.
- The 60 GiB gate passes with 256 GiB spare. Prior contracts: LLVM build `minimum_start_free_bytes` 32 GiB, `disk_reserve_bytes` 8 GiB (`evidence/p2996-build/admission.json`), monitored every step (`p2996_build.py:93-96`).
- Hazard: the first D68 run is #21, a small project build. "1.5x the first run's peak" would then drop the gate far below what #96 or #99 (LLVM bundle, IWYU build) need. Keying the gate per run class avoids this.
- Competitors: Docker.raw 86 GB (grows with devcontainer builds); `~/.codex` worktrees 84 GB, visualizations 113 GB, archives 59 GB (Codex returns after 2026-10-19); uv cache 46 GB; 52 Docker volumes await the D80 choice. Old run directories under `~/.local/state/marketplace-tool-foundation` (397 entries): `du` timed out at 90-100 s, size UNVERIFIED.
- CPU: 12 cores, 96 GiB (`sysctl`); prior runners use `-j4` with allowance 8 (`p2996_build.py:256`). Heavy runs beside two Python lanes fit; D78 keeps 3 lanes until #21 measures disk, CPU and wall time.

## 5. Recommendations

1. Before 0a, write `lanes/21-offline.json` (CMake install/export, `cmake/*Config.cmake.in`, new consumer fixtures, one new runner and test, a new evidence directory) and its HANDOFF §2(i) row; `27-offline` is the fallback.
2. Extend CT-40: count hand lane records as writers, read a standing D68 admission row with per-run consumption receipts, and add CT-53 and CT-45 to the class once their issues exist.
3. Rewrite the Phase 4b cxx column: #96 right after #16 (D5), #22/#18 and the LSan chain in waves 3-5, and only evidence-writing heavy runs during CT-39's wave 2.
4. Define the D68 gate as max(60 GiB, 1.5x the largest measured peak of the same run class), sampled during the run.
5. Choose one schema direction for #26, CT-52 and CT-53 before briefing any of them; resolve whether "#21 foundation" means `21-offline` or #21 accepted.
6. Rebase `13-offline` (`4905c8e`, base `6130ab5`, 145 commits behind) after the #12 close and the w0-doctor integration, before CT-39 starts.

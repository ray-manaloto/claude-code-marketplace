# R1: C++ lane supply for an always-active cxx slot

Read-only review, 2026-10-14, session `ce9c0b3d`, tip `21af565`. P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold`.
Simulations ran `frontier.py plan` without `--write` against scratch graphs (scratchpad `r1/`); nothing under `P/frontier/` exists (`ls` rc 1).

## 1. Inventory

State: `gh issue list --state all` shows every issue below OPEN; blockers from `gh api -X GET .../issues/<n>/dependencies/blocked_by` match `P/ticket-ledger.md:18-67,100-114`. Every #11 child body says "near five maintained files and 300 handwritten changed lines" and "separately admit any host-heavy ... operation" (issue #21 body), so code size is S/M; the heavy run is the long pole (duration UNVERIFIED).

| Id | Title | Frontier | Blockers | Heavy | Admission | Size | Offline split (D28) |
|---|---|---|---|---|---|---|---|
| #12 | Seal 14c LSan closure | READY | none | no | tracker close (closure `2cc4c029` in tip, ledger:18) | S op | n/a, not in class |
| #13 | LSan repair verdict | blocked | #12 | yes ("under admission") | per-run | M | yes: offline repair `4905c8e` in `issue-13-lsan` worktree (ledger:19) |
| #14, #15 | LSan guard prep, promotion | blocked | #13, #14 | yes (UNVERIFIED for #14) | per-run | M | likely (UNVERIFIED) |
| #16 | GCC sanitizer witnesses | READY | none | yes | per-run, heavy 4 | M | yes: witness sources, receipt harness |
| #17 | P2996 family coverage | READY | none | yes | heavy 3 | M | yes: merge/report code over fixtures |
| #18, #19 | GCC, LSan coverage cells | blocked | #16; #15 | yes | per-run | M | after blocker |
| #20 | Reflection-core analysis commands | READY | none | yes | heavy 2 | M | yes: command wiring, failing-exit tests |
| #21 | Relocated CMake Config consumers | READY | none | yes | heavy 1 | M | yes: consumer projects, package config |
| #22 | Native CPS consumers | blocked | #21 | yes | per-run | M | after #21 |
| #23 | Native foundation acceptance | blocked | 8 (#15-#22) | yes | per-run | L | no |
| #24, #25 | Legacy trackers pin; bridge placement | READY; blocked | none; #24 | no | CLOSE ops (`931b536`, `54d34c8b`) | S op | n/a |
| #26 | Issues schema -> C++ POD records | blocked | #24 | light (UNVERIFIED) | none | M | mostly offline; NOT in class |
| #27 | Admit Issues transport deps | READY | none | UNVERIFIED (dependency qualification) | likely per-run | M | yes; NOT in class |
| #30-#61 | Native research core | blocked | via #23, #24-#28 | mixed | per-run | M each | in class (`frontier.toml:20`) |
| #96 L1 | Private exact LLVM bundle | READY | none | yes ("fresh host admission and capacity", #96 body) | heavy 5 | M | yes: candidate resolution, op and rollback prep; NOT in class |
| #99, #100 | IWYU build; portable consumer | blocked | #96 | yes | per-run | M | after #96 |
| #102-#105 | L4a-d | blocked | #100 (#103 also #99) | yes | per-run | M | after |
| #106-#108 | CI, update PRs, global activation | blocked | #102-#106 | outward/global | CI, push, global | M | no |
| #95, #98 | C3, C2 research queries | READY; blocked | none; #94 | no | none | S | not C++ (#95 body: saved-search diagnostic) |

## 2. cxx slot schedule

Today the plan would fill the slot: `frontier.py plan --graph r1/data/graph.json` printed `cxx slot: offline-portion of #21; heavy run not admitted`, `dispatch 21-offline`, `skipped #16: heavy, not admitted`.

| # | Unit | Prerequisite | Admission | Dur. | Then |
|---|---|---|---|---|---|
| W0 | `21-offline` (consumer sources only; no `mise.dev.toml` row, no `evidence/core-p2996/`) | D46 revoked | none | S | `20-offline` |
| W0 alt | `27-offline` (transport candidates, provenance fixtures) | #27 added to class | none | S | as above |
| 1 | `20-offline` | none | none | S | `17-offline` |
| 2 | `17-offline` | none | none | S | `16-offline` |
| 3 | `16-offline` | none | none | S | heavy #21 |
| 4 | `21` heavy run | 21-offline integrated | per-run or standing | L | `22-offline` |
| 5 | `22-offline`, then `22` heavy | #21 accepted | per-run | S, L | heavy #20 |
| 6 | `20`, `17`, `16` heavy (D5 order) | their offline units | per-run each | L each | `18` |
| 7 | `13-offline` (integrate `4905c8e`) -> 13 -> 14 -> 15 -> 19 | #12 CLOSE op | per-run from 13 | M/L | `23` |
| 8 | `23` acceptance | #15-#22 | per-run | L | `96-offline`, `30` |
| 9 | `96-offline` -> 96 -> 99/100 -> L4 | class membership | per-run | M/L | L5/L6 (outward) |

Gaps where no C++ unit is runnable:
- G1, after step 3: every remaining member needs a heavy acceptance (#22 on #21, #18 on #16) or the #12 close (#13). With no admission the slot empties after four S units. Closes: a standing heavy admission, the #12 CLOSE op (opens the LSan line), or #96/#27 in the class.
- G2, during wave 0: no C++ unit is briefed; HANDOFF-2026-10-14.md has no `#21`, `cxx` or `C++` hit (`grep` rc 1). Closes: revoke D46 and allocate `21-offline`.
- G3, after #23: #30 also waits on #24-#28, none in the class (`ticket-ledger.md:36`). Closes: CLOSE #24/#25, put #26-#28 in the class.

## 3. Friction with "always"

- Per-run admissions: `docs/agents/claude-team.md:131-133` "Host-heavy lanes run one at a time and need the user's confirmation for each run; a previous receipt grants no new admission"; same in `SKILL.md:35-36`, D5/D18/D28/D42 (`task_plan.md:357,370,380,394`). A standing admission contradicts these lines until they are amended.
- Admission plumbing does not connect: `frontier.py:280-281` reads `row.get("kind") == "admission" and row.get("ticket")`; `dev/plan_decide.py:92` only writes `approval`, `operation`, `decision` rows keyed by `subject`. Nothing sets `consumed`, so a hand-written admission row would persist forever.
- One conflict empties the slot silently. `frontier.py:404-407`: `if conflict: conflicts.append(conflict); continue` exits the class, not the member list. Simulated with #21 owning `CMakeLists.txt` against a live lane: `cxx_slot None`, `chosen ['12', '24', '27']`, #20/#17/#16 skipped; `format_plan` prints the slot only `if plan["cxx_slot"]` (`frontier.py:873`).
- An offline lane completes its ticket. `frontier.py:207` matches `#\d+` at the start of any `tickets` entry and `:293-296` marks it done. Simulated lane `21-offline`, integrated, retro passed: #22 became ready and the plan moved to `offline-portion of #20`; the heavy half of #21 is never rescheduled.
- L-chain outside the class: `frontier.toml:20` omits #96-#108, so `frontier.py:339` sets `heavy=False` and #96 would dispatch with no admission, against D5 (`task_plan.md:357`).
- Operations take lanes: the simulation chose `12` and `24` as implementer lanes, though `task_plan.md:324` lists them CLOSE.
- "Offline portion" is undefined: `scheduler.md:53-54` points to `implementer.md` step 3, which only states the size limit (`implementer.md:16`).
- Shared files: `mise.dev.toml` rows belong to w0-doctor and w0-session-hooks (their `lanes/*.json` owned_paths); `ct21-codex-imports` owns `evidence/core-p2996/**`, `evidence/p2996-cmake/**`. A cxx unit needing a test row waits for D7 (`task_plan.md:112-114`) or a parent hunk.
- Issue bodies keep "One implementation writer per Git common directory" (#21 body), superseded for allocated worktrees by `codex-task-orchestration.md:88-93`; briefs must cite the override.
- Host: `df -h /Users` 98% used, 37 GiB free; `sysctl` 12 cores, 96 GiB. An LLVM bundle or P2996 build beside two other lanes may not fit (size UNVERIFIED).
- No graph yet: `frontier.py status` prints `not available yet: CT-05 (ticket-ledger.json)`.

## 4. Recommendations

1. Revoke D46 and allocate `21-offline` in wave 0 now, on new consumer-fixture paths only.
2. Ask the user for one standing admission, recorded as a `decisions.jsonl` row: one heavy C++ run at a time in D5 order while at least N GiB is free, with a notice per run instead of a question; amend `claude-team.md:131-133` and `SKILL.md:35-36` to match.
3. Fix `frontier.py` before implement-spec: iterate members on conflict, report an empty slot, key offline lanes so they do not mark the ticket done, and add an `admission` kind to `plan_decide.py`.
4. Change `frontier.toml` (propose): include #26, #27, #96, #99, #100, #102-#105; order adds `#96` after `#16`; #12, #24 and #25 are operations, not lanes.
5. Run the #12 close early (evidence in tip) to open the LSan line (`13-offline` = `4905c8e`) as a second supply.
6. Make free disk a precondition of every heavy admission; free space before step 4.

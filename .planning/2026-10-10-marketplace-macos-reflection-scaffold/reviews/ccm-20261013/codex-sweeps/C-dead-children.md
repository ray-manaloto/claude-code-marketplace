# Sweep C — the nine dead Codex children

Read-only sweep per R3 "Sweep brief C". Inputs: `codex_rollout_digest.py` and `codex_threads.py
show/turns` for each id (digests in the session scratchpad `sweepC/`), the rollouts streamed
for tool-call/write/Git extraction, `qbj4yn5d/lane-ledger.json` (`updated_at
2026-10-13T14:07:45Z`, i.e. the ledger as it stood at the cut), and mtime/`git status`
(`GIT_OPTIONAL_LOCKS=0`) cross-checks of worktrees `2a14`, `86d0`, `c658`, `remaining-t4`,
`a06-retrieval-refresh` and the source checkout. `$T` = `/var/folders/z4/…/T/`, `$S` =
`~/.local/state`. Every child's last turn is `failed` with the usage-limit error; all eight
10-13 deaths fall in 14:07:49Z–14:09:09Z, `01a128a0` died 2026-10-12T05:07:02Z on the earlier limit.

| Thread | Agent path · nickname · role · parent (cwd) | Last three tool calls | Writes (path, UTC) | Git | Slot held at death (ledger) | Outcome |
|---|---|---|---|---|---|---|
| `01a13590` | `/root/a06_methods_merger` · McClintock · worker · 01a130ef (`2a14`) | 14:06:01 `sed -n` on accepted `verify.py`; 14:06:34 `git rev-parse --git-path hooks` (source); 14:09:06 `apply_patch` Add `verify.py` | 14:05:30 `mkdir` + copies `recorder.py`, `caller_helper.py`, `failure_disposition.py`, `ORIGIN.json`; 14:09:07 `verify.py` 19,370 B — all `$T/qbj4yn5d/a06-unit3/integration-preparation/` | 1 read-only (`rev-parse`); no mutation | none: `a06-unit3/allocation.json` owner is `/root/a06_methods`; source/check/Git slots `/root` | Died 8.5 min in, before any run of `verify.py`; integration preparation unreviewed (R3 says the lane redid A06u3) |
| `01a134c5` | `/root/tracker_intake_inventory` · Mencius · explorer · 01a130ef (`2a14`) | 14:06:43 `cat >` `seal_packet.py`; 14:07:21 python3.15 runs it (exit 0, HANDOFF written); 14:08:13 `send_message` → `/root` (encrypted) | 45 packet writes 10:25–14:07 under `$T/qbj4yn5d/tracker-intake/`, `tracker-t1-source-preparation/`, `tracker-t3-source-preparation/source-import/repair-2/nested-caller/` (last: `seal_packet.py` 14:06:44, `HANDOFF.json` 14:07:24) | 13 read-only (`status`, `diff`, `show`, `rev-parse`) on the source; the `git commit`/`cherry-pick` strings are prose inside the T3 plan file, not commands | **yes**: `tracker_import_preparation` / `tracker_t3_preparation` owner (`/root/tracker_intake_inventory`, "private repair-2 resumed… source attempts zero"); T1 lease already returned | T3 private repair-2 handoff written seconds before death; its report to `/root` was the last call — root never processed it |
| `01a1358f` | `/root/a01_archival_review` · Banach · marketplace-reviewer · 01a130ef (`2a14`) | 14:06:01 `send_message` → `/root` (A01/#62 verdict); 14:07:40 `git rev-parse HEAD`/`branch --show-current` + `cat issue63-ar…`; 14:08:06 `send_message` → `/root` | none observed (read-only review; 13 calls) | 3 read-only | none (not named in the ledger; `issue62/63_closure_preparation` reviewer is `/root/issue25_closure_review`) | A01/#62 review delivered 14:06; A02/#63 review started 14:07 and died at 1.0 min — #63 archival review not done |
| `01a13486` | `/root/remaining_t4_implementer` · Carson · worker · 01a12bd1 (`86d0`) | 14:06:56 `write_stdin` poll of session 55107 (`phase_c_runner_v3.py`); 14:07:36 `send_message` → `/root`; 14:07:50 `write_stdin` poll (empty) | 164 writes 09:12–13:43 under `$S/marketplace-llvm23-fork-01a12bd1/remaining-work-20261013/implementation-t4/`; the **runner it launched at 13:53:54Z kept writing after the thread died**: `recovery-attempt3/*` through `checkpoint-refusal-parents.json` 14:21:49 and `TERMINAL.json` 14:21:50 (= the thread's `updated_at`) | 12 read-only; none mutating | none in its own name; the runner exercised `issue_write_allocation` (owner `01a12bd1`, its root) via `./dev/mise run issue:apply` (31 `*-issue-apply.json`, all exit 0; children RF1–RF4, W1 `VERIFIED`/`sent`) | Orphaned runner waited 901 s for a parents-batch approval nobody was alive to give → `REFUSED` (`MISSING_APPROVAL_WAIT_EXHAUSTED`), `STOPPED`/`NOT_COMPLETED` (R3 P2-2); no process alive now |
| `01a134aa` | `/root/remaining_t4_metadata_review` · Pauli · default · 01a12bd1 (`86d0`) | 14:05:29, 14:06:06, 14:06:59 `wait_agent` 50 s (all timed out; no `spawn_agent` call — waiting on the peer runner's parent checkpoint) | 17 writes 09:53–14:01 under `…/remaining-work-20261013/t4-parent-metadata/` (`prepublication-review/`, `closure-preflight/`, `phase-c-provenance-review/frozen-schema-review-v{1,2}/` — `review.json`, `RETRO.md`); 8 `write_file`/`append_to_file` to Codex item `checkpoint` (encrypted) | none | none (reviewer; not in the ledger) | Six-child checkpoint review approved and saved 14:04; the four-parent checkpoint review never happened — this is the approval the runner timed out on |
| `01a134c2` | `/root/dynamic_ticket27_writer` · Nietzsche · worker · 01a13185 (`c658`) | 14:05:52 `write_stdin` poll; 14:07:39 python reconcile (`reconcile=PASS`, exit 0); 14:08:59 python syntax/CLI checks (all 0) | 71 writes 10:18–14:08 under `$S/agent-protocol/dynamic-agents-20261012/implementation/{workers/ticket-27,evidence/27}/` | 10 mutating, **all inside the private clone** `…/workers/ticket-27` (fetch/merge of `spec/dynamic-agents`, 2× `add`+`commit` 10:28, 11:02); 41 read-only | none (agent-protocol side project; not in `qbj4yn5d`) | 450-line v2 candidate frozen for re-review; "no commit or native run" of the candidate; death cut the re-review handoff |
| `01a134ed` | `/root/dynamic_ticket02_writer` · Goodall · worker · 01a13185 (`c658`) | 14:06:17 `git rev-parse --git-common-dir` (private repo); 14:06:58 `append_to_file` `checkpoint` (encrypted); 14:08:09 `git diff 9f22e30 affdd9a -- contract.md …` (exit 0) | 63 writes 11:04–13:18 under `…/implementation/{workers/ticket-02,evidence/02}/` (last: `freeze-02b-r1.py`, `02b-r1-self-review.md` 13:18:24) | 4 mutating 11:16 in `…/workers/ticket-02` (`fetch` from `…/implementation/repo`, `merge --ff-only cedce03`); 78 read-only | none | "Awaiting START"; was reconciling `affdd9a` into contract.md when it died (0.9 min turn) |
| `01a13574` | `/root/dynamic_ticket30_writer` · Sagan · worker · 01a13185 (`c658`) | 14:06:57 `cat` of launch package + baseline files; 14:07:31 `send_message` → `/root`; 14:07:41 `/bin/sh …/isolation-repair-01/launch-package.sh … run --no-deps --skip-tools stage …/marketplace-copy-01` → `{"status":"staged"}` exit 0 at 14:08:02 | all under `$S/agent-protocol/dynamic-agents-20261012/implementation/{workers/ticket-30/.shared/agent-protocol/marketplace-transition/v1,evidence/30}/` 13:38–14:08 (`mise.toml`, `README.md`, `controls.py`, `stage.py`, `launch-package.sh`, diagnostics) | 2 read-only `git status --short` (worker); none mutating | none | Staging replay passed one second before the usage-limit error ended its only turn (37.8 min); no handoff |
| `01a128a0` | `/root/cold_bottle_review` · Sagan · marketplace-reviewer · 01a127db (`2a14`) | 10-12 05:05:15, 05:05:38, 05:07:00 python review scripts in `2a14` writing to `/private/tmp/marketplace-lsan-{preparation,failure}-review-*` | 23 `apply_patch` files + redirects, every one under `$T/marketplace-*-review-*` or `/private/tmp/marketplace-*-review-*` packets (10-11 08:03 → 10-12 05:07); `~/.config/mise`, `~/.gitignore_global`, `~/.local/bin` mentions are hash asserts/env vars, not writes | 281 read-only; the one `git apply` string (10-11 06:25) is inside a review script's recorded `probe_invocations`, not a command run against the worktree | none (predates the `qbj4yn5d` ledger) | 94 turns; last turn (`01a12e79`, 9 min) died on the 10-12 limit after the LSan closure comparison passed; task 14c stays blocked on the LSan timeout |

Cross-checks: 0 files modified 13:00–14:15Z in any of the five worktrees or the source
checkout (`.git` excluded); `86d0` and `remaining-t4` are clean; the dirty entries in `2a14`,
`c658` and `a06-retrieval-refresh` predate the window and belong to the roots/A06 lane.

## Replacement sentence for `docs/agents/claude-takeover.md` (activation record)

"No Codex root thread is mid-turn, but nine spawned children died inside a turn on the usage
limit (eight at 14:07–14:09Z on 2026-10-13, `01a128a0` on 10-12); they wrote only to private
packets and `~/.local/state`, ran no Git mutation outside private clones, and the one
in-flight process — Carson's T4 Phase C runner under `01a12bd1`'s issue-write slot — sent six
child closures, then timed out waiting for a parents-batch approval and stopped at 14:21:50Z."

## Lost-work rows for sweep A

None: no dead child wrote outside the `qbj4yn5d`/`marketplace-*-review-*` packets or
`~/.local/state/{marketplace-llvm23-fork-01a12bd1,agent-protocol}`. Two rows worth carrying
anyway: (1) `01a13486`'s runner mutated GitHub issues (`issue:apply` RF1–RF4, W1, labels; 31
applies, exit 0) and left the parents batch (#79–#82) unsent — a live-tracker state, not a
file; (2) `01a134c5`'s `tracker-t3-source-preparation/source-import/repair-2/nested-caller/HANDOFF.json`
(14:07:24Z) and `01a13590`'s `a06-unit3/integration-preparation/verify.py` (14:09:07Z)
post-date the ledger's last update and are unreviewed.

## Could not verify

- Encrypted `send_message`/`checkpoint` payloads (Fernet `gAAAA…`): the content of each
  child's final report to `/root` is unreadable; task names come from `agent_path` and the
  first assistant message, not the spawn brief.
- Python-script writes are attributed by the paths the scripts name; a script writing to a
  computed path could escape the roots above (mtime windows found none).
- Whether the six `VERIFIED`/`sent` closures are reflected live on GitHub (not queried here;
  sweep B re-queried read-only).
- `01a134c2`'s private-clone commits (10:28, 11:02) were not inspected for content.

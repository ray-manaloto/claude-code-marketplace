# w0-doctor merge report: doctor core (CT-22a part 1, W0-1/W0-4/W0-5)

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto. Merger:
session `ccm-20261014` (Opus 5.5), serial, no agents running. `VIRTUAL_ENV` unset before every
mise command. Authority: D101 (merge as reviewed, SessionStart entry kept until A2-11), D115
(merge w0-doctor), D148 (rebase onto the scrubbed baseline), D37 (one publish per integration).
Runbook: `reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md` §2(b) and §3.

## Result

- Rebase of `claude/w0-doctor-core` from `c21941f` (private archive) onto `2185777`: rc 0, no
  conflicts. Map: `bb0e2a4` -> `1dfefa3`, `64e46d4` -> `b0d30ec`, `f1bbc8d` -> `b01d9bb`. Guard scan
  of `c21941f..f1bbc8d` before the rebase: 0 findings.
- Merge M `878e7f0` (parents `2185777`, `b01d9bb`), `git merge --no-ff -F <msg>`, ort, 15 files
  +891 -3; `git merge-tree --write-tree` clean beforehand. The PreToolUse deny gate and hk
  pre-merge-commit ran the retro gate: passed.
- Records R `ec6ed95` (12 files; hk pre-commit `records` step passed): HANDOFF §3 hunks and ledger
  rows, listed in its message.
- Publish P `959c56f61e4f6eede2a0fb66e4827b8657d56556` (parent `ec6ed95`, index tree `1666b201`, 1 file);
  preimage `2185777`; no refusal.

## Lane checks on `b01d9bb` (lane worktree)

All rc 0: `test_doctor*` (13 tests), `test:doctor`, `cli.py --surface session-start --format
context` (415 ms, budget 3000), `cli.py --surface check --json`, `tasks validate` (60), `check`,
`check:acceptance-baseline` (19), `test:hooks` (17), `hk validate`, `git diff --check 2185777
HEAD`, `retro:gate -- w0-doctor`.

## Gates on the merged tree with the parent hunks (17:13:44-17:16:39Z)

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise tasks validate` | 0 | 64 tasks |
| `./dev/mise run check` | 0 | 91 tests; json 2312, python 244, shell 6, toml 21 |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run test:doctor` | 0 | 14 tests (THRESHOLDS table test added) |
| `./dev/mise run test:hooks` | 0 | 17 tests |
| `./dev/mise run test:plan-decide` | 0 | 5 tests |
| `./dev/mise run test:retro-gate` | 0 | 21 tests |
| `./dev/mise run test:frontier` | 0 | 29 tests |
| `./dev/mise run check:records` | 0 | doctor pre-commit surface |
| `hk validate` | 0 | `hk.pkl` valid |
| `python3 -I dev/retro_gate.py --unit w0-doctor`, `--unit gate-git-path` | 0, 0 | selectors none |
| `python3 -I -m unittest discover -s dev -p test_handoff.py` | 0 | 36 tests |
| `git diff --check 2185777` | 0 | |
| `python3 -I dev/doctor/cli.py --surface check --json` | 0 | no P1/P2 |
| `./dev/mise run check:research` (17:15:52-17:16:39Z) | 0 | 17 test tasks incl. plan-decide, frontier, retro-gate; baseline 19 |

Staged guard scan of R: no leaks; `git diff --cached --check` rc 0. No other worktree ran a named
check in this window (this session was the only writer; no agents running).

## HANDOFF §3 dispositions

| Hunk | Disposition |
| --- | --- |
| 3.1 `plan:decide`, `test:plan-decide` | applied; `plan:decide` passthrough verified (`-- --help`, and DL-187..DL-189 written through it) |
| 3.2 `dev/check.py` manifest rule (w0-docs retro) | deferred to a C++ ticket: D113 allows fixes, tests and deletions only in existing Python; same disposition as gate-git-path edit 3 |
| 3.3 THRESHOLDS table test | applied in R (`parent hunk: dev/test_doctor.py`) |
| 3.4 D12 rows | applied: DL-187, DL-188, DL-189 |
| 3.5 items 1-4, 6, 7 | applied; item 5 is 3.3 |
| 3.6 `test:frontier` | applied with its `check:research` entry; `frontier:*` rows and the `claude-team.md` section wait for CT-25 |
| gate-git-path edit 2 `test:retro-gate` | applied with its `check:research` entry |

## Publish (A09)

Selected path: this report only; M and R travel as ancestors. Preimage `2185777`; check_task
`["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`. The committed copy in
P says "pending"; the fields below were filled after the publish and travel in the next records
commit.

| Command | rc | Output |
| --- | --- | --- |
| `git diff --cached --name-only HEAD \| wc -l` (before) | 0 | 0 |
| `./dev/mise run delivery:inspect-hooks -- inspect-hooks.json …` | 0 | `hook_tree_sha256=a21be5fe…4af8`, unchanged |
| `./dev/mise run delivery:prepare -- prepare.json 6155ff23…` | 0 | `head=ec6ed95f…`, `index_tree=1666b201…` |
| `./dev/mise run delivery:publish -- publish.json a047da8d…` (17:17:45-17:20:31Z) | 0 | `published=959c56f6…`, `history_scan_rc=0` |

## Post-publish verification

| Command | rc | Result |
| --- | --- | --- |
| `git rev-parse HEAD origin/codex/marketplace-native-onboarding` | 0 | both `959c56f6…` |
| `git ls-remote --heads origin` | 0 | `codex/marketplace-native-onboarding` `959c56f6…`, `main` `6b5b092…` |
| `gh run list` / `gh run watch 38605846587 --exit-status` | 0 | on `959c56f`: development checks `38605846526` success (17:21:36Z), research-fast `38605846265` and `38605832916` success (17:22:32Z), acceptance `38605846587` success (17:23:46Z) |
| `git worktree remove` gate-git-path, w0-doctor, scrub | 0 | each clean beforehand; branches kept |

## Correction (2026-10-14, merger finding during scanner-betterleaks)

The Result line above says the PreToolUse deny gate and hk pre-merge-commit ran the retro gate and
passed. Neither ran. The merge command was `git -C $MP merge ...`: the deny gate does not expand `$MP`,
finds no repository and allows the command (fail open, the GGP-4 class), and the global hk install did
not register `pre-merge-commit` until D154 (17:5xZ). The retro check that did run was the manual
`./dev/mise run retro:gate -- <unit>` in the lane worktree before the merge (rc 0, recorded above), and
again on the integrated tree. Tracked as CT-86.

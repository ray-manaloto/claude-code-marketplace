# gate-git-path merge report: deny gates and retro gate resolve git outside the mise shims (D129)

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto. Merger:
session `ccm-20261014` (Opus 5.5), serial, no agents running. `VIRTUAL_ENV` unset before every
mise command. Authority: D129 (lane), D139 (merge and push), D148 (rebase onto the scrubbed
baseline). Scratch logs: the session scratchpad `republish/` (outside the checkout).

## Result

- Rebase of `claude/gate-git-path-fix` from `c33ba4e` (private archive) onto `62b154a`: rc 0, no
  conflicts. Map: `976a093` -> `d651318`, `4219a85` -> `ee3cc2d`, `ae70599` -> `e3b8bd7`.
- Merge M `be1a0f9` (parents `62b154a`, `e3b8bd7`), `git merge --no-ff -F <msg>`, ort, 5 files
  +254 -2. The PreToolUse deny gate and hk pre-merge-commit ran the retro gate: passed.
- Records R `8de864c`: lane record, retro parent edits 5-7, ledger D148, D149, DL-184..DL-186,
  progress entry.
- Publish P `218577753d9484ef0c1491aa29f4f90c6ec43fd9` (parent `8de864c`, index tree `18a01eb3`, 1 file);
  preimage `62b154a`; no refusal.

## Guard scan before the rebase

`gitleaks git --config .gitleaks.toml --log-opts=c33ba4e..claude/gate-git-path-fix`: 0 findings
(any rule). The same scan of `c21941f..claude/w0-doctor-core`: 0 findings.

## Gates

On the rebased lane tip `e3b8bd7` (lane worktree), then on `be1a0f9` with parent edits 5-7:

| Command | rc on `e3b8bd7` | rc on `be1a0f9` + edits |
| --- | --- | --- |
| `python3 -I -m unittest discover -s dev -p test_hooks.py` | 0 (16 tests) | 0 (16 tests; edit 5 changes one test) |
| `python3 -I -m unittest discover -s dev -p test_retro_gate.py` | 0 (20 tests) | 0 (21 tests) |
| `python3 -I -m unittest discover -s dev -p test_handoff.py` | not run | 0 (36 tests) |
| `./dev/mise run check` | 0 | 0 (91 tests; json 2310, python 238, shell 6, toml 21) |
| `./dev/mise run check:acceptance-baseline` | 0 | 0 (baseline 19) |
| `./dev/mise run retro:gate -- gate-git-path` | 0 | 0 |
| `./dev/mise tasks validate` | 0 (56 tasks) | 0 (56 tasks) |

Staged guard scan of R (`gitleaks git --pre-commit --staged`): no leaks; `git diff --cached
--check` rc 0.

## Retro parent edits (`retros/gate-git-path.md`)

| Edit | Disposition |
| --- | --- |
| 1 `CODING_STANDARDS.md` | applied earlier as rule 15 (now in the baseline `62b154a`) |
| 2 `mise.dev.toml` `test:retro-gate` | deferred to the w0-doctor integration (w0-doctor owns `mise.dev.toml` this wave) |
| 3 `dev/check.py` lane-record keys | deferred to its C++ ticket (D112, D131: gates move to C++) |
| 4 `.claude/rules/planning-records.md` base rule | rejected by the user |
| 5 `dev/test_hooks.py` | applied in R |
| 6 `dev/test_retro_gate.py` drift guard | applied in R |
| 7 `dev/AGENTS.md` shim-cost bullet | applied in R |

## Publish (A09)

Selected path: this report only; M and R travel as ancestors. Preimage `62b154a`; check_task
`["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`. The committed copy in
P says "pending"; the fields below were filled after the publish and travel in the next records
commit.

| Command | rc | Output |
| --- | --- | --- |
| `git diff --cached --name-only HEAD \| wc -l` (before) | 0 | 0 |
| `./dev/mise run delivery:inspect-hooks -- inspect-hooks.json dd599ed9…` | 0 | `hook_tree_sha256=a21be5fe…4af8`, unchanged; `remote_url_sha256` `477a17f8…` |
| `./dev/mise run delivery:prepare -- prepare.json 5056a3f1…` | 0 | `head=8de864ce…`, `index_tree=18a01eb3…` |
| `./dev/mise run delivery:publish -- publish.json 038246d9…` (17:04:32-17:07:26Z) | 0 | `published=21857775…`, `history_scan_rc=0` |

`publish` rc 0 implies rc 0 for the scratch-tree checks, each `check_task`, `git diff --cached
--check`, the staged gitleaks 8.30.1 scan and the outbound history scan over `62b154a..2185777`
with the repository guard config (D145).

## Post-publish verification

| Command | rc | Result |
| --- | --- | --- |
| `git rev-parse HEAD origin/codex/marketplace-native-onboarding` | 0 | both `21857775…` |
| `git ls-remote --heads origin` | 0 | `codex/marketplace-native-onboarding` `21857775…`, `main` `6b5b092…` |
| `gh run list --branch codex/marketplace-native-onboarding` | 0 | on `2185777`: research-fast `38603954292` and `38603962134` success, development checks `38603962082` success, acceptance `38603962612` success (17:10:22Z); on `62b154a`: acceptance `38601873659` and development checks `38601873531` success |

## Correction (2026-10-14, merger finding during scanner-betterleaks)

The Result line above says the PreToolUse deny gate and hk pre-merge-commit ran the retro gate and
passed. Neither ran. The merge command was `git -C $MP merge ...`: the deny gate does not expand `$MP`,
finds no repository and allows the command (fail open, the GGP-4 class), and the global hk install did
not register `pre-merge-commit` until D154 (17:5xZ). The retro check that did run was the manual
`./dev/mise run retro:gate -- <unit>` in the lane worktree before the merge (rc 0, recorded above), and
again on the integrated tree. Tracked as CT-86.

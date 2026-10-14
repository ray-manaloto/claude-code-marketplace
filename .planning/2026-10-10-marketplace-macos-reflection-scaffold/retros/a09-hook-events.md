# a09-hook-events retrospective: A09 admits the D154 global hook events

Unit: `a09-hook-events` (D165, DL-213). Worktree `.claude/worktrees/a09-hook-events`, branch
`claude/a09-hook-events`, cut from allocation commit `0784d95` (base `9672854`). Commits:
fix `9264007`, merge of integration tip `37c587b` as `0b7553c` (clean), publish-path guard
`8112f42`, hermetic setUp `45025bf`. Diff against `0784d95` in owned paths only:
`dev/git_delivery.py` (+13/-4), `dev/test_git_delivery.py` (+36/-6 after `45025bf`), and this record.

Defect: `delivery:inspect-hooks` refused (rc 2, "configured Git hook could execute during
delivery") because the D154 global `~/.gitconfig` registers hk hooks for six events and
`safe_configured_hooks` admitted only pre-commit, commit-msg and pre-push.

Claim verified before admitting, three ways:
- The git subcommands A09 runs (grep of `dev/git_delivery.py`): add, archive, cat-file,
  check-ref-format, commit-tree, config, diff, fetch, hash-object, init, ls-files, ls-remote,
  merge-base, push `--no-verify`, remote get-url, rev-parse, symbolic-ref, update-index,
  update-ref, write-tree. No commit, merge, rebase, cherry-pick, revert, am or pull. The
  scratch repository in `check_selected_tree` runs with `GIT_CONFIG_GLOBAL=/dev/null`.
- `git help githooks` (git 2.54.0): prepare-commit-msg and post-commit are invoked by
  git-commit; pre-merge-commit by git-merge.
- Scratch probe (bash, scratch HOME and global config with marker hooks for 12 events,
  every A09 subcommand run as A09 runs it): none of the six admitted events fired;
  reference-transaction fired on update-ref, fetch and push, and post-index-change on add,
  write-tree and update-index. Both stay refused. Controls (`git commit`, `git merge`,
  `git checkout`) fired the expected events, so the probe detects hooks.

Red then green: `test_inspect_hooks_admits_global_hk_layout` failed with rc 2 before the fix
and passed after it; `test_inspect_hooks_refuses_unknown_global_event` (post-checkout,
reference-transaction) passes, and fails in both subtests when the refusal is removed
(mutation check). End to end on the real global config: inspect-hooks rc 2 with the
`0784d95` module and rc 0 with the fixed one, against the same intent.

Exits on merged HEAD `0b7553c`: `./dev/mise run test:delivery` rc 0 (20 tests),
`./dev/mise tasks validate` rc 0, `./dev/mise run check` rc 0,
`./dev/mise run check:acceptance-baseline` rc 0 (19 baseline hashes), `git diff --check` rc 0.
After `8112f42` and `45025bf`: `test:delivery` rc 0 (20 tests); the direct
`python3 -I -B -m unittest` run with a foreign `GIT_DIR` and `VIRTUAL_ENV` rc 0; diff-check rc 0.
States: implemented, tested and committed. Not yet reviewed, integrated or published.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks / information access: `test:delivery` exited rc 1 in the fresh worktree. `dev/mise` sets `MISE_DATA_DIR` per checkout, and the worktree's `.mise` lacked the betterleaks 1.9.0 pin that scanner-betterleaks added. The lane admits no network, so `tools:prepare` was not an option. | Applied in-lane: copied the main checkout's `.mise/installs/aqua-betterleaks-betterleaks` into the worktree's excluded `.mise/`, with identical binary SHA-256 `70d2103c2915aababa0e1eea121bd3db0ff0da86bee40ddc6f5982181acaf6d0`; `test:delivery` then rc 0. Owner parent: the brief or lane template for any lane whose required checks include `test:delivery` should prepare tools in the worktree, or admit this local copy, before dispatch (proposed edit P-1 in the handoff). |
| P3 | Automated checks: the "admitted events never fire" claim rested on an uncommitted scratch probe; the publish test configured only pre-push. | Applied (`8112f42`): `test_publish_uses_hook_free_exact_sha_push` configures all six admitted events with a marker. Removing `--no-verify` makes it fail (pre-push marker written). The `git commit` substitution mutation failed earlier with rc 128 before the marker assert, so it proves nothing on its own; the probe's controls cover that case. |
| P3 | Automated checks: the shared `setUp` pinned only `GIT_CONFIG_GLOBAL` and kept the caller's `GIT_*`, against `.claude/rules/dev-tests.md`. | Applied (`45025bf`): `setUp` drops `GIT_*` and pins a scratch HOME, `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`. Verified by `test:delivery` rc 0 and the direct run with a foreign `GIT_DIR` rc 0. |
| P3 | Automated checks: `dev/test_handoff.py` runs `git commit` through a helper that passes no env, so the user's global hk hooks would run in its scratch repositories. It is on no gate route (`dev/check.py` discovers only `test_research_*.py` and `research_refresh`, and no mise task names it). Found by reading; not run. | Outside owned paths. Owner parent: a separate unit pins the environment as `dev/test_hooks.py` does (proposed edit P-2). |

Navigation: none. The brief's line pointer (`safe_configured_hooks`, lines 48-70) and the lane
record were exact; the integration tip had moved from `0784d95` to `37c587b`, which touched no
owned path and merged cleanly.
Coding standards: no finding. The safe-set comment gives the reason each admitted event cannot
fire, as the lane asked; whether the wording is right is for the reviewer.
Steering/global guidance: none. No instruction file changed. The user's global `~/.gitconfig`
was only read (`git config --global --get-regexp '^hook\.'`), never written.
Tool economy: applied. Logs went to the scratchpad and only exit codes and tails were read. The
first probe ran under zsh, which does not word-split `$G`, and was rerun under bash (one wasted call).
No-ops: none.
Information access: covered by the P2 row; the worktree-prep rule exists in workflow memory but
not in the lane record's `required_checks` context.

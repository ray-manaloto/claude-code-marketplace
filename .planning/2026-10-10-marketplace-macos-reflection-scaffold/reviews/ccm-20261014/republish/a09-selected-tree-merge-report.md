# a09-selected-tree merge report: the A09 selected-tree check runs the source checkout's pinned tools

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto. The merger
was a subagent of session `ccm-20261014` (Opus 5.5). It worked in the root checkout and followed
`scan-agy-merge-report.md`. `VIRTUAL_ENV` was unset before every command, and every command ran
from the root. The merge was the literal `git merge --no-ff` with no `-C` (D164). Scratch logs are
in the session scratchpad under `a09st-merge/`, outside the checkout. Nothing was pushed or
published, and the remote is still `959c56f`.

## Preflight

The root checkout was on branch `codex/marketplace-native-onboarding` at HEAD `30ce28b`, with a
clean status and Git dir `.git`. The lane tip `claude/a09-selected-tree` was `11f5af7`, as the brief
said. `git merge-tree --write-tree 30ce28b claude/a09-selected-tree` returned rc 0 (clean), tree
`3430f99`. The lane changes three paths: `dev/git_delivery.py` (+20/-1), `dev/test_git_delivery.py`
(+69) and `retros/a09-selected-tree.md` (+70).

## Commits

| Step | Commit | Parents | Content |
| --- | --- | --- | --- |
| R1 records | `be7e1ea` | `30ce28b` | `retros/a09-selected-tree.md` only, 1 file +70. Its blob `33d110d` is the same blob as at `11f5af7`. hk `pre-commit` `records` passed |
| M1 merge | `db4e4f0` | `be7e1ea`, `11f5af7` | ort, 2 files +89 -1, rc 0. hk `pre-merge-commit` printed `retro gate passed for: claude/a09-selected-tree`, and the PreToolUse deny gate printed nothing (allowed). Merged tree `3430f99`, the same as the preflight `merge-tree` result |
| R2 records | the commit carrying this report | `db4e4f0` | Lane record set to integrated, the progress entry, and this report |

Byte identity was checked with `git hash-object` against `git rev-parse 11f5af7:<path>`; both
returned `33d110d8b567a9ba6d49e2678a9c7fce23313bef`. Before R1, `git diff --cached --check`
returned rc 0. `./dev/mise run retro:gate -- a09-selected-tree` also returned rc 0 on the root
with the record staged. The merge message carries the session trailers.

## Conflicts

There were none. The lane's code paths (`dev/git_delivery.py`, `dev/test_git_delivery.py`) are
untouched on the integration branch since the lane's last sync: `git diff --stat a5efa27 30ce28b` over both
paths is empty, and `a5efa27` is the integration tip that `8bc701f` merged.

## Gates

These ran after M1 (`db4e4f0`), from 21:15:48Z to 21:20Z, each alone:

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise tasks validate` | 0 | 66 tasks |
| `./dev/mise run check` | 0 | 31 + 91 tests; json 2323, python 244, shell 6, toml 21 |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run check:research` | 0 | `deps:check` and 19 test tasks, `test:delivery` among them; baseline 19 (21:18:14-21:19:23Z) |
| `./dev/mise run test:delivery` | 0 | 23 tests, including the three new seam tests (`source_pinned_installs`, `mise_directory`, `mise_symlink`) |
| `./dev/mise run retro:gate -- a09-selected-tree` | 0 | `RETRO GATE PASSED`, selectors none |
| `git diff --check be7e1ea` | 0 | |
| `betterleaks git . --config .gitleaks.toml --redact --no-banner --log-opts="be7e1ea..HEAD"` (1.9.0, `.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks`) | 0 | 7 commits, about 18.6 KB; no leaks found, so there are no rule ids and the count is 0 |

The first `tasks validate` and `check` calls went out together and may have overlapped (both
rc 0). Each was then rerun alone, and the table records those serial runs (rc 0; same counts).

## A09 selected-tree check on the merged tip (no publish)

The `delivery:*` tasks in `mise.dev.toml` have no dry path. `publish` runs
`check_selected_tree`, then the check tasks and the push, so `delivery:publish` was not run. The
merger called the check the same way the lane's receipts did (`run_check.py` in the lane's
`a09st/` logs). A scratchpad script, `a09st-merge/run_selected_tree.py`, imports
`dev/git_delivery.py` from the root. It calls `check_selected_tree(root, <db4e4f0^{tree}>)` and
exits 2 on a `Refusal`.

| Item | Value |
| --- | --- |
| Command | `python3 -I -B <scratchpad>/a09st-merge/run_selected_tree.py "$PWD" db4e4f0` (`.venv/bin/python3`, Python 3.15.0) |
| Tree | `3430f9962738a6e295f4c2d1a697a58553813f08` |
| Result | `PASS`, rc 0, 1:51.6 (21:20:29-21:22:21Z). The run covers tasks validate, `check`, check:acceptance-baseline and `test:delivery` in the copy |
| Source installs | The pinned betterleaks binary's `stat` (inode, mtime, size) was identical before and after (`cmp` rc 0). `git status` was clean afterwards |

This is the step that failed with rc 2 in `a09-hook-events-merge-report.md`, because the pinned
betterleaks 1.9.0 was missing in the copy. On the merged tip it now passes.

## Parent edits applied

None: the retro's "Parent findings" line reads "none outside `owned_paths`; no parent edit". Lane
record `lanes/a09-selected-tree.json` (R2):

- `status` is integrated.
- `review` is "fable cold review PASS-with-P3 on 8bc701f; P3 .mise named refusal applied in retro".
- `retro` is "passed".
- `head_sha` is `11f5af7`, and `integration_merge` is `db4e4f0`.
- Three notes were added: the retro binding, the integration gates, and that the lane worktree may
  be removed.

The progress entry was inserted directly above `- NEXT (`, so NEXT is still the last bullet.

## Refused, unrun, left for the parent

- No gate failed, and the deny gate refused nothing.
- The combined A09 publish (DL-212, DL-221) was not run and waits for an explicit instruction. A
  real `delivery:publish` through `check_selected_tree` remains unverified, as the retro states.
- Lane worktree `.claude/worktrees/a09-selected-tree` (branch `claude/a09-selected-tree`, `11f5af7`)
  may be removed after integration. The merger did not remove it.
- The retro's trailer row stays as recorded: merge commits `6e232e3` and `8bc701f` on the lane carry
  no session trailers, and the history was not rewritten.
- No `decisions.jsonl` row and no ledger row were added or changed.

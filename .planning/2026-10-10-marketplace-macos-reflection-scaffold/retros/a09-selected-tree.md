# a09-selected-tree retrospective: the selected-tree copy runs the source checkout's pinned installs

Unit `a09-selected-tree` (DL-212, DL-221, D159; a D113 fix to existing Python). Worktree
`.claude/worktrees/a09-selected-tree`, branch `claude/a09-selected-tree`, `base_sha` `53d7b03`, cut
from the allocation commit `f635966`, so `git log f635966..HEAD` is the lane. Commits, in order:
`d5801f9` (fix and seam test), `6e232e3` (`git merge --no-edit` of the integration tip `71dbb6b`,
clean), `e960a32` (the refusal names the failing task), then the commit carrying this record (the
final SHA, in the hand-back). Writer: Claude Opus 5.5 (implementer). Independent review: not yet run.

Delivered. `check_selected_tree` (`dev/git_delivery.py`) calls `share_pinned_installs` after the
scratch tree equals the reviewed index tree and `HEAD` is set: it makes the copy's own `.mise`
directory, links `.mise/installs` to the source checkout's resolved `.mise/installs`, and appends
`/.mise/` to the scratch repository's `.git/info/exclude`. `dev/mise` keeps
`MISE_DATA_DIR=<copy>/.mise` and auto-install off (unchanged; `dev/mise` and `mise.dev.toml` were not
needed). The tree comparison runs before the link exists, so no tool path enters a compared tree. A
source without installs leaves a dangling link and `test:delivery` refuses. A selected-tree refusal
now names its task (`selected-tree run test:delivery: command failed (rc=N): ...`). Size: 2 maintained
files, `git diff --numstat f635966 HEAD`: `dev/git_delivery.py` +18/-1, `dev/test_git_delivery.py` +33/-0.

Exits, `VIRTUAL_ENV` unset, one worktree at a time. Logs in the session scratchpad `a09st/`.
- Red first: `test_scratch_validation_runs_source_pinned_installs` on `f635966` code, rc 1
  (`A09 refused: command failed (rc=31): .../selected/dev/mise`, the pinned case); after the fix,
  rc 0. The task-name assertion, before `e960a32`'s code: rc 1; after, rc 0.
- Real path before the fix: `check_selected_tree` over `HEAD^{tree}` of `f635966` (`c597ca2`), rc 2
  (`command failed (rc=1): .../selected/dev/mise`, 1:58). After the fix, over `d5801f9`'s
  tree (`5046d3e`): `PASS`, rc 0 (1:58); `stat` digest of the worktree's
  `.mise/installs` identical before and after (no writes to the source installs).
- Source lacking the pin, real mise: the same check with the link pointed at an empty directory:
  rc 2, `selected-tree run test:delivery: command failed (rc=1)` (tasks validate, `check` and
  check:acceptance-baseline passed in the copy before it).
- On the merged bytes (`6e232e3`): `./dev/mise run test:delivery` rc 0 (21 tests);
  `./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0;
  `./dev/mise run check:acceptance-baseline` rc 0 (19 baseline hashes); `git diff --check` rc 0.
  After `e960a32`: `./dev/mise run test:delivery` rc 0 (21 tests). The final reruns and
  `./dev/mise run retro:gate -- a09-selected-tree` are in the hand-back.

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P2 | Information access: `run()` drops subprocess output, so the merger's refusal named only `<copy>/dev/mise`; finding `test:delivery` took a by-hand rerun of four tasks (`a09-hook-events-merge-report.md:80-91`). (Implementer.) | `e960a32`: the loop wraps `run` and re-raises `selected-tree <task>: <reason>`; task names hold no URL or secret. The seam test asserts the text, rc 1 before, rc 0 after; `test:delivery` rc 0. | Applied. |
| P3 | Automated checks: the seam test uses a fake `dev/mise` and a fake scanner (the suite's existing pattern), so it proves the copy reaches the same file (`-ef`) under `<copy>/.mise/installs`, not that real mise resolves it. (Implementer.) | Covered by the real-path receipts above (rc 2 before, `PASS` rc 0 after, rc 2 without the pin). A real-mise test inside `test:delivery` would recurse into `test:delivery` and add about 2 minutes per run. | Rejected with evidence (real path receipted). |
| P3 | Coding standards: rule 14 (new logic outside a bridge). `share_pinned_installs` is 8 lines of fix to existing A09 Python (D113 allows fixes); it adds no wiring that a C++ module replaces, so no dated-exception marker applies. | none; `check` rc 0. | No finding. |
| P3 | Tool economy: the first commit went in as `wip` with `--no-verify` to give the real-path check a tree, then was amended with hooks on (hk `check:records` passed). Each real-path run costs about 2 minutes. (Implementer.) | Applied in-lane: the amend ran the hooks; later commits ran them directly. | Applied. |

Navigation: none; the brief's line pointers (`dev/git_delivery.py:206`, `dev/test_git_delivery.py:449`)
and the merger report located the defect directly. Steering: none; no AGENTS.md, rule or doc names
the selected-tree copy (`grep -rn 'selected-tree\|check_selected' dev/AGENTS.md docs/ .claude/rules/`
empty). No-ops: none; each change has a test that failed first.

Parent findings: none outside `owned_paths`. Unverified: a real `delivery:publish` through
`check_selected_tree` (no push was admitted); independent review.

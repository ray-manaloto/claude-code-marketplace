# a09-selected-tree retrospective: the selected-tree copy runs the source checkout's pinned installs

Unit `a09-selected-tree` (DL-212, DL-221, D159; a D113 fix to existing Python). Worktree
`.claude/worktrees/a09-selected-tree`, branch `claude/a09-selected-tree`, `base_sha` `53d7b03`, cut
from the allocation commit `f635966`, so `git log f635966..HEAD` is the lane. Commits, in order:
`d5801f9` (fix and seam test), `6e232e3` (`git merge --no-edit` of the integration tip `71dbb6b`,
clean), `e960a32` (the refusal names the failing task), `e4d7110` (implementer retro draft), `8bc701f`
(`git merge --no-edit` of the integration tip `a5efa27`, clean), then the commit carrying this record
and the review fix (the final SHA, in the hand-back). Writer: Claude Opus 5.5 (implementer).
Independent review: Claude Fable 5.1, cold, read-only, PASS-with-P3 on `8bc701f`; its real-path
probe passed (same pinned binary, source installs unchanged, `rmtree` did not follow the link, a
reviewed tree carrying `.mise` as directory, file or symlink is refused). Retro: Claude Fable 5.1
(retro-writer); it applied the review's P3 code finding in-lane (below).

Delivered. `check_selected_tree` (`dev/git_delivery.py`) calls `share_pinned_installs` after the
scratch tree equals the reviewed index tree and `HEAD` is set: it refuses a tree that already carries a
`.mise` entry (`reviewed tree carries a .mise entry`), makes the copy's own `.mise` directory, links
`.mise/installs` to the source checkout's resolved `.mise/installs`, and appends `/.mise/` to the
scratch repository's `.git/info/exclude`. `dev/mise` keeps `MISE_DATA_DIR=<copy>/.mise` and
auto-install off (unchanged; `dev/mise` and `mise.dev.toml` were not needed). The tree comparison runs
before the link exists, so no tool path enters a compared tree. A source without installs leaves a
dangling link and `test:delivery` refuses. A selected-tree refusal names its task
(`selected-tree run test:delivery: command failed (rc=N): ...`). Size: 2 maintained files,
`git diff --numstat f635966 HEAD`: `dev/git_delivery.py` +20/-1, `dev/test_git_delivery.py` +69/-0.

Exits, `VIRTUAL_ENV` unset, one worktree at a time. Implementer logs in its session scratchpad
`a09st/`; retro logs in `a09st-retro-*`.
- Red first (implementer): `test_scratch_validation_runs_source_pinned_installs` on `f635966` code,
  rc 1 (`A09 refused: command failed (rc=31): .../selected/dev/mise`, the pinned case); after the
  fix, rc 0. The task-name assertion, before `e960a32`'s code: rc 1; after, rc 0.
- Red first (retro, review P3): `test_scratch_validation_refuses_tree_with_mise_directory` and
  `..._with_mise_symlink` on `8bc701f`'s `dev/git_delivery.py`: both FAILED, stderr
  `A09 refused: [Errno 17] File exists: '.../selected/.mise'` (the raw message the review named);
  after the two-line refusal, both OK (`python3 -B -m unittest dev.test_git_delivery -k
  mise_directory -k mise_symlink`, `Ran 2 tests ... OK`).
- Real path before the fix (implementer): `check_selected_tree` over `HEAD^{tree}` of `f635966`
  (`c597ca2`), rc 2 (`command failed (rc=1): .../selected/dev/mise`, 1:58). After the fix, over
  `d5801f9`'s tree (`5046d3e`): `PASS`, rc 0 (1:58); `stat` digest of the worktree's
  `.mise/installs` identical before and after (no writes to the source installs).
- Source lacking the pin, real mise (implementer): the same check with the link pointed at an empty
  directory: rc 2, `selected-tree run test:delivery: command failed (rc=1)` (tasks validate, `check`
  and check:acceptance-baseline passed in the copy before it).
- Real path on the review-fixed tree (retro): `check_selected_tree` over the staged tree
  ``96bd639` (the two fixed files staged on `8bc701f`)`: `PASS`, rc 0, 122 s (tasks validate, `check`, check:acceptance-baseline and `test:delivery` in the copy); `stat` (inode, mtime) of the pinned betterleaks binary identical
  before and after.
- On the merged bytes (`6e232e3`, implementer): `./dev/mise run test:delivery` rc 0 (21 tests);
  `./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0;
  `./dev/mise run check:acceptance-baseline` rc 0 (19 baseline hashes); `git diff --check` rc 0.
  After `e960a32`: `./dev/mise run test:delivery` rc 0 (21 tests).
- On the final bytes (retro, before the record commit): `./dev/mise run test:delivery` rc 0 (23 tests, 34.9 s); `./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0; `./dev/mise run check:acceptance-baseline` rc 0; `git diff --check f635966 HEAD` rc 0, `git diff --cached --check` rc 0; betterleaks 1.9.0 `git -c .gitleaks.toml --log-opts=f635966..HEAD --redact` rc 0, no finding (rule ids: none); `./dev/mise run retro:gate -- a09-selected-tree` rc 0 on this record.

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P2 | Information access: `run()` drops subprocess output, so the merger's refusal named only `<copy>/dev/mise`; finding `test:delivery` took a by-hand rerun of four tasks (`a09-hook-events-merge-report.md:80-91`). (Implementer.) | `e960a32`: the loop wraps `run` and re-raises `selected-tree <task>: <reason>`; task names hold no URL or secret. The seam test asserts the text, rc 1 before, rc 0 after; `test:delivery` rc 0. | Applied. |
| P3 | Information access: a reviewed tree that already carries `.mise` (directory, file or symlink) made `share_pinned_installs` fail at `mkdir` with the raw `[Errno 17] File exists: <temp path>` instead of a named refusal (review P3, `dev/git_delivery.py:209` on `8bc701f`). | In-lane (retro): `if data.exists() or data.is_symlink(): raise Refusal("reviewed tree carries a .mise entry")` before `mkdir` (`dev/git_delivery.py:212-213`). Seam tests at the CLI: `test_scratch_validation_refuses_tree_with_mise_directory` (a tracked `.mise/pin` in the selected paths) and `test_scratch_validation_refuses_tree_with_mise_symlink` (a `.mise` symlink inherited from `HEAD`, since `prepare` admits only regular files); both red on the old code with the raw message, green after; rc 2, `HEAD` unchanged, no remote branch. Real path: the retro probe above. | Applied. |
| P3 | Automated checks: the seam test uses a fake `dev/mise` and a fake scanner (the suite's existing pattern), so it proves the copy reaches the same file (`-ef`) under `<copy>/.mise/installs`, not that real mise resolves it (review P3, `dev/test_git_delivery.py:308`; implementer draft). | Accepted on real-path receipts: the implementer's (rc 2 before, `PASS` rc 0 after, rc 2 without the pin), the review's cold probe on `8bc701f` (same pinned binary, installs unchanged, `rmtree` did not follow the link, `.mise` entries refused) and the retro probe on the fixed tree above. A real-mise test inside `test:delivery` would recurse into `test:delivery` and add about 2 minutes per run. | Rejected as a code change, with evidence (real path receipted three times). |
| P3 | Steering: merge commits `6e232e3` and `8bc701f` (`git merge --no-edit`) carry no `Co-Authored-By` or `Claude-Session` trailer (review; `git log --format=%B 6e232e3 8bc701f`). The rule already exists: `.claude/agents/implementer.md` step 4 ("Use `git merge --no-edit <integration-branch>` and amend the message afterwards to add the trailers"); the implementer did not follow it. No check inspects trailers (`grep -rn -i 'trailer\|Co-Authored-By' hk.pkl dev/check.py dev/hooks .claude/rules`: only `planning-records.md`'s `writer_model` line). | No edit to `implementer.md` (the rule is there; a restatement fails CODING_STANDARDS 7). The history stays: the cold review PASS binds to `8bc701f`, and a rewrite would unbind it; the writer identity is on record (lane `writer_model`, this header, per `.claude/rules/planning-records.md`). A `commit-msg` hk step is not proposed: it would fire inside `git merge --no-edit`, before the amend the rule prescribes, and `hk.pkl` is an excluded shared path. | Rejected as a history rewrite, with evidence; existing rule cited. |
| P3 | Coding standards: rule 14 (new logic outside a bridge). `share_pinned_installs` is 10 lines of fix to existing A09 Python (D113 allows fixes); it adds no wiring that a C++ module replaces, so no dated-exception marker applies. | none; `check` rc 0. | No finding. |
| P3 | Tool economy: the first commit went in as `wip` with `--no-verify` to give the real-path check a tree, then was amended with hooks on (hk `check:records` passed). Each real-path run costs about 2 minutes. (Implementer.) In the retro, two red runs failed in the fixture, not at the seam (`prepare` refuses an unchanged selected path and admits only regular-file entries, `selected_state` and `staged_entry`); reading those two functions first would have saved two runs. | Applied in-lane: the amend ran the hooks; later commits ran them directly. Retro: no rule; the code states both refusals and CODING_STANDARDS 10 keeps them out of `AGENTS.md`. | Applied. |

Navigation: none; the brief's line pointers (`dev/git_delivery.py:206`, `dev/test_git_delivery.py:449`,
`:209` and `:308` in the review) and the merger report located each defect directly. Steering: the
trailer row above. No-ops: none; each change has a test that failed first. Automated checks beyond the
rows: `.github/workflows/development.yml` runs `dev/check.py`; `test:delivery` runs under
`check:research`, so the new seam tests are wired in without a new guardrail.

Parent findings: none outside `owned_paths`; no parent edit. Unverified: a real `delivery:publish`
through `check_selected_tree` (no push was admitted).

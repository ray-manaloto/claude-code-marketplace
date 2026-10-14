# a09-hook-events retrospective: A09 admits the D154 global hook events

Unit `a09-hook-events` (D165, DL-213). Worktree `.claude/worktrees/a09-hook-events`, branch
`claude/a09-hook-events`, cut from allocation commit `0784d95` (base `9672854`). Commits, in order:
fix `9264007`, merge of tip `37c587b` as `0b7553c`, publish-path guard `8112f42`, hermetic setUp
`45025bf`, draft record `21150ee`, merge of tip `3d5b181` as `06e1deb` (reviewed SHA), retro
comment `25db4c4` (checked SHA), then this record's own commit (the final SHA). The implementer
wrote as Claude Opus 5.5 (`Co-Authored-By` on `9264007`, `8112f42`, `45025bf`), matching the
record's `writer_model`; the retro commits carry Claude Fable 5.1. Diff against `0784d95` stays in
owned paths: `dev/git_delivery.py` (+14/-4), `dev/test_git_delivery.py` (+36/-6), this record.
The integration tip moved to `0e063ce` (records only) after `06e1deb`; the parent merges.

Defect: `delivery:inspect-hooks` refused (rc 2, "configured Git hook could execute during
delivery") because the D154 global `~/.gitconfig` registers hk hooks for six events and
`safe_configured_hooks` admitted only pre-commit, commit-msg and pre-push.

Claim verified three ways before admitting: the git subcommands A09 runs (add, archive, cat-file,
check-ref-format, commit-tree, config, diff, fetch, hash-object, init, ls-files, ls-remote,
merge-base, push `--no-verify`, remote get-url, rev-parse, symbolic-ref, update-index, update-ref,
write-tree; never commit, merge, rebase, cherry-pick, revert, am or pull; `check_selected_tree`
runs with `GIT_CONFIG_GLOBAL=/dev/null`); `git help githooks` (git 2.54.0: prepare-commit-msg and
post-commit from git-commit, pre-merge-commit from git-merge); a bash scratch probe with marker
hooks for 12 events under a scratch HOME, where none of the six admitted events fired,
reference-transaction fired on update-ref, fetch and push, post-index-change on add, write-tree
and update-index (both stay refused), and the controls `git commit`, `git merge`, `git checkout`
fired their events. Red then green: `test_inspect_hooks_admits_global_hk_layout` rc 2 before the
fix, passes after; `test_inspect_hooks_refuses_unknown_global_event` fails in both subtests when
the refusal is removed. Against the real global config: inspect-hooks rc 2 with the `0784d95`
module, rc 0 with the fixed one, same intent.

Cold review (fable, read-only) on `06e1deb`: PASS-with-P3, three P3s, all dispositioned below.
The reviewer's own reruns on `06e1deb`: `test:delivery` rc 0 (20 tests), `tasks validate` rc 0,
`check` rc 0, `check:acceptance-baseline` rc 0, `retro:gate` rc 0, `git diff --check` rc 0.

Exits on `25db4c4` (retro-writer, worktree, `VIRTUAL_ENV` unset): `./dev/mise run test:delivery`
rc 0 (20 tests, 23 s); `./dev/mise tasks validate` rc 0 (64 tasks); `./dev/mise run check` rc 0;
`./dev/mise run check:acceptance-baseline` rc 0 (19 baseline hashes); `git diff --check` rc 0.
`python3 -I dev/retro_gate.py --unit a09-hook-events` rc 0 against this record (on `25db4c4` in
the working tree, then rerun on the record commit; the hand-back names both SHAs). The parent
reruns `retro_gate.py --branch claude/a09-hook-events` at integration preflight.
States: implemented, tested, reviewed, retro applied, committed. Not integrated or published.

| Severity | Category and finding (source) | Change, owner, verification | Disposition |
| --- | --- | --- | --- |
| P2 | Information access / navigation: `test:delivery` exited rc 1 in the fresh worktree because `dev/mise` sets `MISE_DATA_DIR` per checkout and the worktree's `.mise` lacked the betterleaks 1.9.0 pin that scanner-betterleaks added. The allocation rule already exists (`.claude/skills/ticket-frontier/references/scheduler.md` §Allocation by hand step 3: `tools:prepare && deps:sync` in the worktree) and the implementer brief template repeats it (`brief-templates.md` Env line), but this lane's record admits `network: none`, so the implementer could not run it and the brief line was a no-op. (Implementer draft; reviewer P3-3.) | In-lane: copied the root checkout's `.mise/installs/aqua-betterleaks-betterleaks` into the worktree's excluded `.mise/`, binary SHA-256 `70d2103c2915aababa0e1eea121bd3db0ff0da86bee40ddc6f5982181acaf6d0` identical; `test:delivery` rc 0 after. The reviewer recorded the copy as acceptable (off-plan, excluded path, same digest). Cross-scope: the allocation step and the brief line get the condition that the parent runs the prep when the lane admits no network; edits E1 and E2 below, owner parent, verification `grep -n 'network' <file>` shows the new line. | Applied in-lane; E1/E2 deferred to the parent, admission condition: the parent applies the literal edits at integration. |
| P3 | Automated checks: `dev/git_delivery.py` `publish`, the `--check-task` loop runs each task with the caller's environment, so the "admitted events never fire" reasoning covers A09's own git calls only; a check task that runs `git commit` would fire hk hooks. Pre-existing. (Reviewer P3-1.) | One-line comment above the loop stating this, commit `25db4c4`; `test:delivery` rc 0 (20 tests), `check` rc 0 on `25db4c4`. | Applied. |
| P3 | Information access: the draft record bound its exits to `0b7553c`, not the reviewed SHA. (Reviewer P3-2.) | This record binds the reviewer's exits to `06e1deb` and the retro-writer's to `25db4c4`; the gate rc 0 is bound to the record commit in the hand-back. | Applied. |
| P3 | Automated checks: the "admitted events never fire" claim rested on an uncommitted scratch probe; the publish test configured only pre-push. (Implementer.) | `8112f42`: `test_publish_uses_hook_free_exact_sha_push` configures all six admitted events with a marker; removing `--no-verify` makes it fail (pre-push marker written). | Applied. |
| P3 | Automated checks: the shared `setUp` pinned only `GIT_CONFIG_GLOBAL` and kept the caller's `GIT_*`, against `.claude/rules/dev-tests.md`. (Implementer.) | `45025bf`: `setUp` drops `GIT_*`, pins a scratch HOME, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`; `test:delivery` rc 0 and a direct run with a foreign `GIT_DIR` rc 0. | Applied. |
| P3 | Automated checks: `dev/test_handoff.py` runs `git commit` through a helper that passes no env (`git()` line 33, `subprocess.run` line 200), so the user's global hk hooks run in its scratch repositories. Found by reading, not run. Outside owned paths; lane request-catch owns the file since `3d5b181`. (Implementer P-2.) | Owner: lane request-catch pins the environment as `dev/test_git_delivery.py` `setUp` does. Admission condition: request-catch's retro record cites the pin with `python3 -I -m unittest discover -s dev -p test_handoff.py` rc 0. Edit E3 writes the relay into request-catch's lane record so it is not carried by a brief alone. | Deferred, owner lane request-catch (E3 by the parent). |
| P3 | Information access: the review verdict exists only in the parent's brief; the lane record's `review` and `retro` fields are null and no `reviews/` file names the lane. (Retro-writer; implementer P-3.) | Edits E4 (lane record `status`, `review`, `retro`) and E5 (progress entry), owner parent, verification `python3 -I -c "import json; json.load(open('<record>'))"` rc 0. | Deferred to the parent, admission condition: applied at integration with E4/E5 literal text. |
| P3 | Tool economy: a zsh loop that expands `$var` unsplit wasted one call for the implementer (probe) and one for the retro-writer (four mise tasks reported "no task found"). | None in the repository: the Bash tool's shell is host user configuration, not a project convention; the record carries the gotcha. | Rejected as a repo rule (inapplicable to project files). |

Navigation: covered by the P2 row (existing allocation step not run; the brief line pointer
`safe_configured_hooks` lines 48-70 and the lane record were otherwise exact).
Automated checks: rows 2, 4, 5 and 6. Every lane test has a gate route: `test:delivery` is in
`check:research` `depends` (`mise.dev.toml`), which `.github/workflows/research-fast.yml` runs;
`development.yml` runs `dev/check.py`. No existing check is unwired.
Coding standards: none. The safe-set comment gives the reason each admitted event cannot fire;
the reviewer's PASS-with-P3 found no standards defect, and the one comment it asked for is in
`25db4c4`.
Steering/global guidance: none. No `AGENTS.md`, rule, skill or agent file changed in the lane;
the user's global `~/.gitconfig` was read only (`git config --global --get-regexp '^hook\.'`).
Tool economy: row 8. Logs went to the scratchpad; only exits and tails were read.
No-ops: one, in the P2 row: the brief's `tools:prepare` line under `network: none`; E1/E2 remove
it by moving the prep to the parent.
Information access: rows 1, 3 and 7.

## Parent edits (outside owned_paths; literal, apply unread)

E1. `.claude/skills/ticket-frontier/references/scheduler.md`, replace the line
`3. In the worktree: `unset VIRTUAL_ENV; ./dev/mise run tools:prepare && ./dev/mise run deps:sync`.`
with
`3. In the worktree: `unset VIRTUAL_ENV; ./dev/mise run tools:prepare && ./dev/mise run deps:sync`; when the lane record admits `network: none`, this step is the parent's and its rc goes into the record's `notes`.`

E2. `.claude/skills/ticket-frontier/references/brief-templates.md`, replace the line
`Env: PWF_PLAN_ROOT=<root> PLAN_ID=<plan id>; unset VIRTUAL_ENV; run ./dev/mise run tools:prepare && deps:sync once.`
with
`Env: PWF_PLAN_ROOT=<root> PLAN_ID=<plan id>; unset VIRTUAL_ENV; tools:prepare && deps:sync already ran in the worktree (record.notes); rerun them only when the record admits network.`

E3. `.planning/<PLAN_ID>/lanes/request-catch.json`, append to `notes`:
`"a09-hook-events retro P-2: dev/test_handoff.py git() (line 33) and the bare clone (line 200) pass no env, so the global hk hooks run in its scratch repositories; pin HOME, GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_NOSYSTEM=1 as dev/test_git_delivery.py setUp does, and cite the test_handoff rc 0 in this lane's retro"`

E4. `.planning/<PLAN_ID>/lanes/a09-hook-events.json`, set
`"status": "retro passed on <final SHA>; awaiting integration"`,
`"review": "fable cold review PASS-with-P3 on 06e1deb (P3-1 check-task env comment, P3-2 exit bindings, P3-3 off-plan betterleaks copy); all three applied or recorded in retros/a09-hook-events.md"`,
`"retro": "passed"`.

E5. `.planning/<PLAN_ID>/progress.md`, new bullet above the NEXT bullet:
`- 2026-10-14 (Claude session, lane a09-hook-events retro): cold review PASS-with-P3 on `06e1deb`; retro comment `25db4c4`; record committed at <final SHA>; `test:delivery` rc 0 (20), `tasks validate` rc 0, `check` rc 0, `check:acceptance-baseline` rc 0, `git diff --check` rc 0, `retro_gate.py --unit a09-hook-events` rc 0. Parent edits E1-E5 applied: <yes/no each>. Next: merge `claude/a09-hook-events` (tip `0e063ce`), then DL-212 (scanner-betterleaks A09 publish).`

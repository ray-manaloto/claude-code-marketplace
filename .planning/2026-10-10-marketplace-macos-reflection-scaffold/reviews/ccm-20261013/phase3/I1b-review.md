# I1b focused cold re-review: lane gate-hooks (CT-02) repair `697e1da`

Reviewed SHA: `697e1dab117a715771801184a8a6ef72717865f3` (parent `e12cf04f22aa2c3d009e567f68081295de09f565`), branch `claude/gate-hooks-wiring`, worktree `.claude/worktrees/gate-hooks` (clean, HEAD = reviewed SHA). Reviewer: Fable, cold, read-only; no file in the worktree or root checkout changed.

## Verdict: PASS-with-P3 for integration

## Evidence (commands run in the lane worktree, `VIRTUAL_ENV` unset)

| Check | rc | Result |
| --- | --- | --- |
| `git show --stat 697e1da` | 0 | only `dev/test_hooks.py` (+13/-1) and `.planning/<PLAN_ID>/retros/gate-hooks.md` (+6) |
| `git diff --check e12cf04 697e1da` | 0 | clean |
| `./dev/mise run test:hooks` | 0 | `Ran 14 tests`, `OK` |
| `python3 -I -m unittest discover -s dev -p test_hooks.py` | 0 | `Ran 14 tests`, `OK` |
| `./dev/mise run check` | 0 | `status: pass` (baseline 0, json 2288, python 228, shell 6, toml 19) |
| `./dev/mise x -- hk validate` | 0 | `hk.pkl is valid` |
| `python3 -I dev/retro_gate.py --unit gate-hooks` | 0 | `RETRO GATE PASSED` (and `retro:gate -- gate-hooks` rc 0) |
| `./dev/mise tasks validate` | 0 | 56 tasks |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19, pass |
| Red-first: new `ScratchEnvironment` test body run against `e12cf04`'s `environment()` (scratchpad copies via `git archive`) | 1 | `FAILED (failures=1)`; same body against `697e1da` passes |
| em-dash scan of the commit | none | only a `…` ellipsis inside the retro row |

Scrub comparison (names only): the `e12cf04` `environment()` passed 15 `MISE_*` names to scratch subprocesses, including `MISE_GITHUB_TOKEN`, `MISE_TRUSTED_CONFIG_PATHS`, `MISE_OVERRIDE_CONFIG_FILENAMES`; the `697e1da` version passes none. Security-relevant improvement: the token no longer reaches scratch-repo commands.

Hook dependence: `dev/hooks/*.py` read only `PLAN_ID` (kept by `environment()`) and `GIT_REFLOG_ACTION` (set by git inside the hook); no `MISE_`/`HK_` dependence, so the prefix scrub removes nothing the hooks need. Comment at `dev/test_hooks.py:36` states the reason. Retro row uses the record's existing `Severity | Category and finding | Applied action and verification` shape and binds rcs and the test name.

## Findings

- P3-1 Trailer: `697e1da` carries `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; the session's required trailer is `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` plus the `Claude-Session` line (present). Owner: merger, `git commit --amend` on the lane before merging; patch-id unchanged. The implementer's report records that Opus is the model that wrote it, so the parent decides which line is authoritative.
- P3-2 Ownership: `.planning/<PLAN_ID>/retros/gate-hooks.md` is not enumerated in `lanes/gate-hooks.json#owned_paths`; `docs/agents/claude-team.md` ("A lane writes that record at `.planning/<PLAN_ID>/retros/<unit>.md` inside its own worktree") and `docs/agents/ticket-retro.md` rule 5 assign it to the lane. Owner: parent, add the retro path to the lane record or accept it as doc-governed.
- P3-3 Record state: the appended row says "Focused re-review is pending"; this review closes it. Owner: parent/merger, update the row and the lane record `status`/`review` fields at integration.
- Observation (not actionable): the subprocess that invokes the real `mise` inside the scratch repo is not identified; the whole-prefix scrub is justified by the hook-dependence check above.

## Not run

`check:research`; container, provider, hook-runtime and fresh-session acceptance (`ci/acceptance.sh`); `hk run` in the real checkout (lane admission is scratch-only). This review covers the static claim only.

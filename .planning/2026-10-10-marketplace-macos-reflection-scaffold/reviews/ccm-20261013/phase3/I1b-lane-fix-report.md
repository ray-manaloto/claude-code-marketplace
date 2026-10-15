# I1b: lane gate-hooks (CT-02) repair, `test:hooks` under `dev/mise`

- Worktree: `.claude/worktrees/gate-hooks`, branch `claude/gate-hooks-wiring`.
- Base `e12cf04f22aa2c3d009e567f68081295de09f565`. New lane tip **`697e1dab117a715771801184a8a6ef72717865f3`**.
- Commit `697e1da`: "test(hooks): scrub MISE_* from the scratch environment so test:hooks passes under mise".
- Nothing was pushed or merged. The root checkout was not touched.
- The integration branch was not merged into the lane, by instruction (the re-merge agent aligns the base).

## Reproduction (on e12cf04, clean worktree, `VIRTUAL_ENV` unset)

| Command | rc | Output (bounded) |
| --- | --- | --- |
| `./dev/mise run test:hooks` | 1 | `FAIL: test_merge_commit_and_push_refused_then_accepted (test_hooks.HkHooks...)`; `mise ERROR Config files in /private/var/folders/.../T/tmpf8inoj9q/repo/mise.dev.toml are not trusted.`; `Ran 13 tests`, `FAILED (failures=1)` |
| `python3 -I -m unittest discover -s dev -p test_hooks.py` | 0 | `Ran 13 tests`, `OK` |

`tools:prepare` and `deps:sync` were not needed, because the failure is not a tooling problem.

## Red test

`ScratchEnvironment.test_outer_mise_trust_and_config_do_not_reach_the_scratch_repo` sets three outer `MISE_*` keys with `mock.patch.dict(os.environ)`, calls `environment()`, and asserts that no `MISE_*` key remains.

| Command | rc | Output |
| --- | --- | --- |
| `python3 -I -m unittest discover -s dev -p test_hooks.py -k ScratchEnvironment` (pre-fix) | 1 | `AssertionError: Lists differ: ['MISE_CONFIG_DIR', 'MISE_ENV_CACHE', ...] != []`. Six leaked keys: `MISE_CONFIG_DIR`, `MISE_ENV_CACHE`, `MISE_GITHUB_TOKEN`, `MISE_OVERRIDE_CONFIG_FILENAMES`, `MISE_SHELL`, `MISE_TRUSTED_CONFIG_PATHS` (names only, no values) |
| Same test after the decorator correction, run against the pre-fix prefix tuple | 1 | `FAILED (failures=1)` |

The real outer environment also leaked `MISE_GITHUB_TOKEN` into the scratch subprocesses. The scrub removes that exposure as well.

## Fix (`dev/test_hooks.py`, the only code path changed)

```diff
+from unittest import mock
@@ def environment(home):
-    env = {k: v for k, v in os.environ.items() if k not in SCRUB and not k.startswith(("GIT_", "HK_"))}
+    # MISE_*: a nested mise in the scratch repo must not inherit the outer dev/mise trust and config.
+    env = {k: v for k, v in os.environ.items() if k not in SCRUB and not k.startswith(("GIT_", "HK_", "MISE_"))}
+class ScratchEnvironment(unittest.TestCase):   # placed after Settings, before the hk-skip decorator of HkHooks
+    def test_outer_mise_trust_and_config_do_not_reach_the_scratch_repo(self): ...
```

My first commit (`3457505`, never shared) inserted the new class between `@unittest.skipUnless(HK, ...)` and `HkHooks`. The decorator therefore guarded the wrong class. I caught this in the diff, moved the class, re-verified red and green, and amended the commit into `697e1da`.

## Results on the committed bytes (worktree clean, `VIRTUAL_ENV` unset)

| Command | rc |
| --- | --- |
| `python3 -I -m unittest discover -s dev -p test_hooks.py` | 0 (14 tests, OK) |
| `./dev/mise run test:hooks` | 0 (14 tests, OK) |
| `./dev/mise run check` | 0 (status pass) |
| `./dev/mise tasks validate` | 0 (56 tasks) |
| `./dev/mise run check:acceptance-baseline` | 0 (baseline 19, pass) |
| `./dev/mise x -- hk validate` | 0 |
| `git diff --check` | 0 |
| `./dev/mise run retro:gate -- gate-hooks` | 0 (PASSED) |

`tasks validate` and `check:acceptance-baseline` ran on the first commit's tree. The amend changed only the class placement in `dev/test_hooks.py`.

## Retro record

`docs/agents/ticket-retro.md` rule 5 says a bounded repair keeps its findings and verification in the originating retro record. I appended the section "Integration repair (I1b)" with one P1 row to `.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/gate-hooks.md`, which is a lane path committed in `697e1da`. The row notes that the earlier "13 tests, rc 0" receipt covered only the direct run.

## Not done or unverified

- Focused independent re-review of `697e1da` is still pending, and the retro row says so.
- `check:research` was not run.
- The lane record `lanes/gate-hooks.json` is unchanged. Its `status` still reads "implemented (Opus), awaiting cold review". The parent or merger should update it.
- Which subprocess inside the scratch repo invokes the nested mise was not identified. The fix scrubs the whole `MISE_` prefix rather than one call site.
- Trailer deviation: the brief asked for `Co-Authored-By: Claude Fable 5.1`. The commit uses `Claude Opus 5.5`, the model that actually wrote it and the line the session's attribution reminder requires, plus the requested `Claude-Session` line.

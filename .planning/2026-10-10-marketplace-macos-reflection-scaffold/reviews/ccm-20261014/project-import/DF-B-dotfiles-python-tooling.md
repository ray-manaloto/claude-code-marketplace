# DF-B: dotfiles Python tooling, import review

Agent DF-B, session `ccm-20261014`, 2026-10-14, read-only. DF is the main checkout at
`/Users/rmanaloto/dev/github/ray-manaloto/dotfiles`, detached HEAD `7744a9c6` (2026-10-13), 12
commits ahead of `origin/main` `182f6f49`. Nothing in DF ran. I read files, ran `git log`, `git
status` and `git show`, scanned `main.py` with an AST walk under `python3 -I`, and tested two regex
patterns copied out of DF. Paths are relative to the DF root unless prefixed `MP:`. Scope: the
`dotfiles_setup` package and CLI, `python/pyproject.toml`, root `ruff.toml`, `mise.toml` tasks,
`hk.pkl`, CI workflows, `python/verification/suites.toml`, planning, handoff and retro tooling, and
the tests. Host setup appears only in section 4b.

## 1. Inventory

| Component | Evidence | Size | `git log -1` |
|---|---|---|---|
| Package `python/src/dotfiles_setup/` | 134 modules; 288 commits touch it | 75,582 lines | `7744a9c6` 2026-10-13 |
| CLI `main.py` | one console script `dotfiles-setup = dotfiles_setup.main:main` (`python/pyproject.toml:48-49`); 149 `add_parser` calls, 101 top-level commands, 111 imports | 3,366 lines | `7744a9c6` |
| `python/pyproject.toml` | runtime deps incl. `kb-setup` git pin (`:40`) and `graphifyy[all]` (`:9`); ruff `ALL` (`:77-163`); dead mypy, pylint, vulture, refurb sections (`:165-202`); `[tool.ty.environment]` (`:184-185`); dev group with unpinned ruff and ty (`:204-215`); native pytest 9 config (`:235-264`); datamodel-codegen jobs (`:274-335`) | 335 lines | `c91d9d69` 2026-10-11 |
| `ruff.toml` | `extend = "python/pyproject.toml"`, record-tree excludes, re-anchored per-file ignores (`:37-60`) | 60 lines | `c91d9d69` |
| `python/uv.lock` | 183 packages; ruff 0.16.5, ty 0.0.76 | 3,008 lines | `c91d9d69` |
| `mise.toml` | 124 tasks: 83 console-script rows, 10 `python -m` rows, 14 multi-line shell rows (F3); `[deps.uv] auto = true` (`:5-8`); `minimum_release_age = "0s"` (`:146`); `deps:python` runs plain `uv sync` (`:274`); launchd agents with an absolute `/Users/rmanaloto` PATH (`:1628`, `:1670`) | 1,817 lines | `7744a9c6` |
| `hk.pkl` (+ `hk-common.pkl` 144, `hk-image.pkl` 48) | hk 2.3.0; `fail_fast = false` (`:22`); 54 named steps plus four shared groups; pre-commit, check, fix, commit-msg, pre-push hooks (`:814-898`) | 898 lines | `7744a9c6` |
| Wiring table `python/verification/suites.toml` | 180 suites: `require_tokens` 132, `forbid_tokens` 19, `regex_forbid` 10, `require_lines` 7, `regex_match` 6, `policy_doc` 4, `skill_eval_corpus` 1, `schema_drift` 1; engine `verify.py` (766 lines) | 3,185 lines | `6b06c8fb` 2026-10-12 |
| CI `.github/workflows/` | `ci.yml` 669 (lint, contract-preflight, build chain, promote), `autofix.yml` 99, `refresh.yml` 674, `build-publish.yml` 1,366, `image-analysis.yml` 186, `ghcr-cleanup.yml` 112, `gcc-sha-repair.yml` 116, `probe-aslr-tsan.yml` 342 | 3,564 lines | `e5440f5e` 2026-10-11 |
| Tests `tests/` | 153 modules, 3,894 test functions; `conftest.py:61-70` refuses runs outside the managed runner | 89,725 lines | `7744a9c6` |

Named modules (lines, last change):

| Area | Modules |
|---|---|
| Gates and runners | `lint.py` 300 (2026-09-01), `gate_result.py` 301 (10-11), `pytest_runner.py` 193 (10-11), `process_stream.py` 254 (10-11), `host_lock.py` 306 (10-11), `process_env.py` 122 (10-11), `child_env.py` 116 (10-05), `bounded_wait.py` 125, `reap.py` 555 |
| Agent teams | `sdlc_team.py` 1,165 (10-12), `lane_result.py` 883 (10-04), `sdlc_final_report.py` 796, `codex_agent_validate.py` 232, `codex_agent_parity.py` 400, `codex_schema.py` 269 |
| Handoff and planning | `handoff_check.py` 753 (09-30), `plan_attest.py` 170 (09-27), `session_state.py` 602 (09-30), `session_orphans.py` 362, `coordinator_handoff.py` 1,358 (10-05), `handoff_inbox.py` 428, `session_common.py` 203 (10-04), `session_start.py` 434 (10-03), `dag_tick.py` 1,441 (10-04), `dag_project.py` 842 |
| Session review (DF's nearest thing to a retro) | `session_review.py` 1,083 (09-17), `session_gate.py` 511 (10-02), `session_ledger.py` 4,493, `session_store.py` 455, `command_audit.py` 845 (10-04), `agentsview_pass.py` 378, `memory_index.py` 664 (08-08) |
| Hook guards | `hook_guard.py` 1,189 (10-13), `hook_dispatch.py` 85, `hook_selfcheck.py` 1,012 (10-03), `heredoc.py` 107, `ask_quality.py` 228 (09-24), `worktree_guard.py` 99, `branch_guard.py` 293, `coordinator_write_guard.py` 88, `script_guard.py` 215, `fnhook_gates.py` 686 (10-11) |
| Lint and doc checks | `doc_refs.py` 488 (10-02), `token_audit.py` 471 (09-03), `bash_budget.py` 215 (10-03), `lint_delta.py` 357 (08-08), `codegen_check.py` 197 (10-02), `schema_vendor.py` 566, `skills_mirror.py` 447 (09-22), `rule_registry.py` 394 (09-10), `rule_sync.py` 276, `instructions_report.py` 393, `instructions_observer.py` 319, `listing_budget.py` 239 (09-11), `eval_cases.py` 389 (09-24), `codec.py` 407 |

There is no retro tooling: no module implements a retro record or gate. Planning uses pwf with
`.mode` = `autonomous inject-smart`; `task_plan.md`, `progress.md`, `findings.md` and
`.plan-attestation` are gitignored (`.gitignore:150-161`); `.planning/` holds six untracked slugs.
Repository state: 397 local branches, 614 remote branches, 165 worktrees; `.agent/gate-results/`
holds 157 run directories, 270 MB.

## 2. Defects

D1. MP's heavy C++ runs depend on DF's working tree. `MP:dev/toolchains/p2996_configure.py:19-20`
sets `LOCK_MODULE` to the absolute path of DF's `host_lock.py` and `LOCK_SHA` to its SHA-256
(`b20e5d96...`, which matches the file today); 27 files in `MP:dev/toolchains/` load it by path and
assert the digest before each heavy run (`MP:dev/toolchains/baseline.py:21, 75, 107-110`). A DF
commit to that file (last `c91d9d69`, 2026-10-11), a branch switch in DF's main checkout, or the DF
sunset stops every MP heavy run. It is also the only `/Users/` path in tracked MP code outside
`evidence/` and `.planning/`.

D2. The CLI succeeds silently. `query-latest` is registered (`main.py:2274-2277`) with no handler,
`run_command` does nothing when `handlers.get` misses (`main.py:3334-3335`), and the root subparser
is not `required`, so both `dotfiles-setup query-latest jq` and a bare `dotfiles-setup` exit 0 with
no output; the graphify sub-dispatch does the same (`main.py:2572-2573`). DF's own modernization
audit recorded this on 2026-09-09
(`.claude/worktrees/handoff-relay-rule/docs/research/kb/reports/modernization-audit-2026-09-09.toml:7084`)
and it is still live.

D3. One 3,366-line dispatcher imports 111 modules for every subcommand, hooks included, and the
join between parser and handler is stringly typed, so the wiring table pins it by tokens.

D4. 13 modules derive the project root from `__file__` (`main.py:3353`, `lint.py:76-82`,
`fnhook_gates.py` `_REPO_ROOT`, `__init__._project_root`). With a venv shared across worktrees or a
non-editable install, the root is the checkout that owns the package, not the caller's worktree.

D5. Two task-name checkers in one package disagree. `doc_refs.py:321` accepts `:` in names and
reads tracked TOML offline (`:342-371`). `handoff_check.py:43-45` cannot match a name containing
`:`: tested on copies of both patterns, `mise run retro:gate` and `mise run deps:python` yield no
citation at all, so they are never checked; it also parses the human table of `mise tasks ls`,
which includes the user's global tasks (`:238-264`). Every MP task name has a colon. `doc_refs`
resolves a path by basename against any tracked file (`:12-17`) and strips `:line` (`:19-20`), so
`foo/ci.yml:999` passes whenever some `ci.yml` exists.

D6. Wiring is checked by substring. 132 of 180 suites are `require_tokens`. The table's own header
says 33 of 33 rebindings closed a live hole and 11 were held up by a comment alone
(`suites.toml:21-26`). A second gate, `token_audit.py`, exists only to audit the first. Four
`policy_doc` suites always return skipped yet count as suites (`verify.py:554-565`). The untyped
manifest ignores keys a handler does not read (`suites.toml:2988` documents `schema_drift` ignoring
`paths`). In tests, 36 modules read `hk.pkl` or `mise.toml` text and 51 lines assert
`in ...read_text()`.

D7. Gate results are not bound to the tree. `GateResult` has no HEAD, tree digest or task hash
(`gate_result.py:43-53`), so `gate read` returns an old pass after edits (`:256-261`); "unknown gate"
and "never ran" both exit 2 (`:291-294`); `failures` is every console line matching
`error|fail` (`:93`, `:134-137`); the `pytest` gate bypasses mise while the others call it
(`:58-77`); a fixed `.json.tmp` name races for the unlocked gates (`:144`).

D8. Run artifacts live in the tree with no retention: `process_stream.new_run_dir` writes
`.agent/gate-results/runs/` (`process_stream.py:44-52`); 157 runs and 270 MB today.

D9. Interrupts leak processes. `lint.py` starts hk in a new session and catches only
`TimeoutExpired` (`lint.py:281-285`), so Ctrl-C ends the wrapper and leaves hk's process group
running (found by reading; `pytest_runner.py:68-101` handles it correctly). Two timeouts stack: mise
`timeout = "700s"` and 600 s in process.

D10. Child environments leak. `pytest_runner` copies the whole environment
(`pytest_runner.py:144`); the default scrub removes only `__MISE_DIFF`; the credential deny-list is a
name regex that misses names such as `*_PAT` or `*_AUTH` (`child_env.py:49-52`); two Git-context
lists disagree (`child_env.py:30-39` written by hand, `process_env.py:57-83` derived from Git).

D11. Implicit sync and lost isolation on hot paths: `[deps.uv] auto = true` (`mise.toml:5-8`),
plain `uv sync` (`mise.toml:274`), 83 console-script rows (F3). The PreToolUse launcher falls back to
`uv run` and fails open when no interpreter exists (`scripts/pretooluse-guard.sh:9-10, 37-40`);
PostToolUse, SubagentStart and InstructionsLoaded hooks call `uv run --project` per event
(`.claude/settings.json` hooks); the SessionStart hook has a 600 s timeout.

D12. Configuration is dead or split. mypy, pylint, vulture and refurb are configured but none is
installed or run (`pyproject.toml:165-202`); `requirements.txt` holds one comment; the
`"../tests/*.py"` ignore is dead because the root `ruff.toml` re-anchors globs (`pyproject.toml:111`
against `ruff.toml:37-57`); ruff and ty float in the dev group (`:205-215`); S603 and S607 are
ignored package-wide (`:96-103`) over 173 direct subprocess call sites, with eight modules carrying
their own process-group code; `minimum_release_age = "0s"` (`mise.toml:146`).

D13. hk checks are fragile. `no_lint_skip` is `! grep -rn ... python/src/ tests/ plugins/`
(`hk.pkl:110-127`): grep exits 2 when a directory is missing, and `!` turns that into a pass even if
a suppression exists elsewhere, the class the repo already fixed in `no_hk_depends`
(`hk.pkl:629-638`). Shell loops sit inline in hk steps (`require_pipefail`,
`no_grep_q_under_pipefail`, `hk.pkl:206-245`) while `bash_budget` polices only `scripts/*.sh`
(`bash_budget.py:47-50`), not the 14 multi-line task rows.

D14. CI bypasses the task layer. `ci.yml:119` runs `hk run check --all` and `:223-231` run
`uv run ... verify run` directly; `mise outdated || true` (`:141`) and `mise doctor -J ... || true`
(`:155`) swallow failures; the contract job checks out the knowledge-base repo for rule-sync
(`:196-210`). MP has the same shape: `MP:.github/workflows/development.yml:18` runs
`python3 -B dev/check.py` and `:15` pins an action by tag.

D15. Session names hard-code `America/Chicago` (`session_common.py:29, 169-180`), accept only the
`dotfiles` and `kb` prefixes (`session_start.py:69-71`), and keep state in the tree
(`.agent/state/session-start`, `session_start.py:73, 413`). MP is off the D61 format too:
`MP:dev/handoff.py:734` defaults to `ccm-YYYYMMDD` in UTC.

D16. The agent layer over-reaches and contradicts itself. `sdlc-team` review mode is asked not to
write but not prevented, under the user's `danger-full-access` Codex sandbox
(`sdlc_team.py:789-800`). The Python PreToolUse guard denies `AskUserQuestion` calls that fail the
quality rule (`ask_quality.py`), while `fnhook_gates.py:391-447` requires every deny-capable module to
permit `AskUserQuestion` and `SendUserMessage`. The coordinator handoff starts `claude --bg` and runs
`claude stop` on the old session by itself (`coordinator_handoff.py:749-751, 1186`). `dag_tick` once
stopped a waiting coordinator three times (`dag_tick.py:12-20`).

D17. Plan attestation is a passthrough to a plugin script resolved from the plugin cache by highest
version (`plan_attest.py:150-170`), and agents may attest bytes no human read (`:5-15`); `.mode` is
`autonomous`, which D54 forbids in MP; the task authority `task_plan.md` is gitignored
(`.gitignore:150`), so it has no review trail.

D18. Cross-repo coupling: the runtime dependency `kb-setup @ git+...@e8fe42ae`
(`pyproject.toml:40`) carries md-budget, currency, evals and the `cc` launcher; `graphifyy[all]` is a
runtime dependency of every CLI call (`:9`).

D19. Schemas flow in both directions. datamodel-codegen builds models from schemas
(`pyproject.toml:274-335`), while `gate_result.generate_schema` (`gate_result.py:264-266`) and the
`sdlc_team.generate_*_schema` functions build the committed `schemas/gate-result.json`,
`lane-result.json` and `sdlc-team-*.json` from code, against D83.

D20. Package guidance is wrong: `python/src/dotfiles_setup/AGENTS.md` is titled "Research fetcher
instructions" and covers research only; `python/AGENTS.md` is stamped "Generated: 2026-04-07" and
still describes `requirements.txt` and 16 environment variables.

## 3. Features to import

Every row below improves on DF, and none copies it. Rows extend existing tickets (D59: each lands
complete and removes the old path). "TR" marks a row from the TR import that these rows
refine. Module paths are under `python/src/marketplace_dev/` (D60, ADR 0003); every task runs
`uv run --no-sync --offline python -I -m marketplace_dev.<module>`.

### 3.1 New ticket

| Id | Title | Acceptance | owned_paths | Blockers | Size | Admissions |
|---|---|---|---|---|---|---|
| DF-B-1 | Host heavy lock in the package; MP heavy runs stop loading DF's file | `locks.py` (stdlib `fcntl`): `held(name, label, wait_s)` with a bounded wait that names the holder (pid, label, since), kernel release when the holder dies, the descriptor passed to children, and re-entry only through an inherited descriptor whose device and inode match the lock file (DF's re-entry by a PID in the environment, `host_lock.py:209-218`, is dropped). The lock file path stays `$XDG_STATE_HOME/dotfiles/heavy-gate.lock` (default `~/.local/state/dotfiles/heavy-gate.lock`) and the holder record keeps the format `pid<TAB>label<TAB>since`, so DF's image jobs and MP's C++ runs still serialise. `dev/toolchains/p2996_configure.py:19-20` points `LOCK_MODULE` at the repo-relative package file and `LOCK_SHA` at its digest; no `/Users/` path remains in `dev/toolchains/`. Tests with a temporary lock directory cover wait, timeout rc, release on kill, re-entry by descriptor, and refusal of a foreign descriptor. CT-11's check lock reuses the primitive. | `python/src/marketplace_dev/locks.py`, its test, `dev/toolchains/p2996_configure.py` (lines 19-20) | CT-39 (package exists); the cxx slot's ownership of `dev/toolchains/` (frontier path check); any pending heavy-run admission that binds `p2996_configure.py`'s own digest (`:35`, `:142`) is re-reviewed | S | none: no heavy run and no DF edit |

Schedule DF-B-1 in the first gap between heavy runs after CT-39. Renaming the lock path off
"dotfiles" waits until DF has no heavy jobs left. It is not part of this ticket.

### 3.2 Acceptance rows on existing tickets

**CT-39 Python package (14 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | No dispatcher. A test runs `--help` for the module behind every `mise.dev.toml` row (rc 0); every subparser group is `required=True`; an unknown or missing subcommand exits 2; no parser is registered without a handler. | test over task rows | D2, D3 |
| r2 | The project root comes from the caller (`git rev-parse --show-toplevel` from the working directory, or `MISE_PROJECT_ROOT`), never from `__file__`. A test runs a module from a lane worktree with the main checkout's venv and gets the worktree. | `core/root.py` | D4 |
| r3 | One subprocess core. ruff `flake8-tidy-imports.banned-api` bans `subprocess.run`, `Popen`, `call`, `check_output` and `os.system` outside `core/run.py`; S603 and S607 are ignored only there. This follows DF's banned-api precedent for its codec (`pyproject.toml:124-157`). | `core/run.py`, `pyproject.toml` | D12 |
| r4 | Extends TR row (e). The runner forwards SIGINT and SIGTERM to the child's process group, reaps it within a grace period, and records `interrupted` in the receipt. A test sends SIGINT and finds no surviving child. | `core/run.py` | D9; the correct shape is `pytest_runner.py:68-101` |
| r5 | Extends TR row (e). The child environment is built from an allow-list. For tests and hook-launched children, the Git-local variables reported by `git rev-parse --local-env-vars` are removed (`process_env.py:57-83`). `__MISE_DIFF` is never passed. Machine-parsed calls drop colour forcing (`FORCE_COLOR`, `CLICOLOR_FORCE`, `GH_FORCE_TTY`, `PYTHON_COLORS`) and set `NO_COLOR=1` (`child_env.py:20-27`). | `core/env.py` | D10 |
| r6 | One ruff configuration, in the root `pyproject.toml`. A test runs `ruff check --show-settings` on one file in each tree (package, tests, dev scripts, plugins) and asserts the same config path for all of them. | test | D12 (`ruff.toml:37-57`) |
| r7 | No dead tool configuration. A test fails on any `[tool.<x>]` section whose tool is not in the locked dev group or the uv, pytest and build tables; no `requirements.txt`. | test | D12 |
| r8 | The dev group pins `ruff==` and `ty==` exactly, equal to the `tools:audit` rows (CT-26a). | `pyproject.toml` | D12 (`:205-215`) |
| r9 | The inline-suppression ban (`noqa`, `type: ignore`, `ty: ignore`, `ruff:` directives, `nosec`) uses `tokenize` over comment tokens only, and a missing scan root fails the check. | `checks/suppressions.py` | D13 |
| r10 | hk's ty step checks the whole package, not only staged files: ty is a cross-module analyser. | `hk.pkl` | `hk.pkl:98-106` |
| r11 | No hk `depends` while `fail_fast = false`, unless a control-armed probe on the pinned hk shows the deadlock fixed. A fixture with a failing ruff step must exit non-zero within the step budget. | `hk.pkl`, test | `hk.pkl:610-638` (deadlock reproduced on two hk releases) |
| r12 | One `test` task (CT-12's wiring, D85). Each run gets an artifact directory outside the tree (`<git-common-dir>/marketplace-dev/runs/<label>-<stamp>-<rand>/`, mode 0700, files created 0600 with `O_EXCL`) holding junit, a structured report, the console log and an `invocation.json` that is written even on interrupt, with retention. Choosing the framework is part of the ticket. Recommended: pytest in the locked dev group, for junit, `--report-log` and `--strict-markers`; stdlib unittest is today's practice. | `testing/runner.py` | `pytest_runner.py:38-56, 108-179`; D8 |
| r13 | No test asserts substrings of live configuration files. Tests build fixture trees; the wiring itself is CT-38a's resolver. | test rule in `CODING_STANDARDS.md` | D6 |
| r14 | Runtime dependencies come from an allow-list (today `githubkit`) and none uses a git URL; a test reads `[project].dependencies`. | `pyproject.toml`, test | D18 |

**CT-38a skill lint, wiring table and citations (3 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | Refines CT-38 item (3). The wiring table resolves objects, not tokens. Each row names an hk step, a task, a `module:function` and a test id, and each is resolved for real: hk's evaluated config (`pkl eval -f json hk.pkl`, or an hk dump command if one exists; UNVERIFIED), project-only task names (tomllib over `mise.dev.toml` and its includes), `importlib.util.find_spec` plus an AST lookup of the function, and the collected test ids. A typed manifest rejects unknown keys; no handler reports "skipped". The inverse also holds: every task row, hk step and test module appears in exactly one row. | `checks/wiring.py`, `checks/wiring.toml` | D6 |
| r2 | Refines CT-38 item (1). One citation resolver serves the skill lint, the handoff check (CT-37) and the guidance lint (CT-58). Task names may contain `:` and come from the same project-only source; paths must exist exactly, relative to the repo, with no basename fallback; `file:line` ranges are checked against the file's line count; out-of-repo citations go in an allow-list with a reason per entry. Fixtures include `./dev/mise run retro:gate` and a stale `dir/x.yml:999`. | `checks/citations.py` | D5 |
| r3 | A task row is one command (`uv run ... python -I -m ...` or `./dev/mise run <task>`) with no shell control flow; hk steps call tasks or modules, never inline loops. | `checks/layering.py` | D13, F3's 14 multi-line rows |

**CT-11 check lock and receipt line (4 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | A receipt binds HEAD, a SHA-256 of `git status --porcelain=v2 -z` output and the hash of the task row. Reading a receipt whose binding differs from the current tree exits non-zero as stale. | `receipts/` (TR's module) | D7 |
| r2 | A status enum with distinct codes: passed 0, failed 1, unknown task 2, timed out 124, tool missing 127. The reader tells "never ran" apart from "unknown". | `receipts/` | `gate_result.py:33-91`; D7 |
| r3 | Failures come from structured tool output (ruff JSON, junit), never from a regex over the console. | `receipts/` | D7 |
| r4 | The check lock uses DF-B-1's primitive (bounded loud wait, holder record, kernel release, re-entry by verified descriptor). | `locks.py` | `host_lock.py:162-228` |

**CT-26a tool pins (2 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | `tools:lint-delta`: when ruff or ty is bumped, partition the findings by rule code between the previously locked version and the new one, on the same tree, in both directions (new and vanished rules), and refuse equal versions. The old version runs from the uv cache offline; fetching it needs the network admission. | `tools/lint_delta.py` | `lint_delta.py:1-40, 220-239` (uses `uvx tool@ver`) |
| r2 | mise `minimum_release_age` is a non-zero floor chosen at CT-26a, matching the accepted "qualify the latest stable" rule. | `mise.dev.toml` | `mise.toml:146` sets `"0s"` |

**CT-26b CI (3 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | CI steps other than checkout and setup run only `./dev/mise run <task>`; a test fails on any other `run:` line. | workflows, test | D14 |
| r2 | Actions are pinned by full SHA with a version comment; actionlint and zizmor run in hk. | workflows, `hk.pkl` | `ci.yml:93`, `hk.pkl:416-419`; `MP:development.yml:15` |
| r3 | No step ends in `\|\| true`. | test | `ci.yml:141, 155` |

**CT-52 schema contract (3 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | `codegen:check` has three verdicts: 0 in sync, 1 drift, 2 undecidable. A formatter failure is 2, not 1; files in the generated directory that no job writes fail as orphans. | `contracts/codegen_check.py` | `codegen_check.py:1-24` |
| r2 | D83 in code: a test fails when any module exports a schema generator for a committed schema. | test | D19 |
| r3 | Schema freshness (moved here from CT-22b by D85). Config schemas (mise, ruff, Claude settings and hooks, Codex config) are vendored under `schemas/vendor/` with a sources manifest (tool, version, URL, SHA-256). An offline check compares the manifest version with the current pin and the bytes with the hash; refresh is a network task behind its admission; config, hook-file and hook-protocol schemas stay distinct (accepted decisions). | `contracts/schema_vendor.py`, `schemas/vendor/` | `schema_vendor.py:1-30`, `schemas/sources.toml` (taplo does not cache remote schemas) |

**CT-02b PreToolUse gate (4 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | Escape hatch: no gate denies `AskUserQuestion` or `SendUserMessage`. The fail-closed launcher (TR row) still allows those two when the interpreter is missing. A test drives both tools through every gate state. | `hooks/` | `fnhook_gates.py:391-447`; D16 |
| r2 | Every classifier rule has a `name`, a `since` date and a fixture pair (deny, and allow with the same words quoted as prose), so transcript audits never count pre-rule history as a bypass. | classifier table | `hook_guard.py:62-110` |
| r3 | `EnterWorktree` is allowed only to `<main checkout>/.claude/worktrees/<name>`. | classifier table | `worktree_guard.py` |
| r4 | Every `.claude/settings.json` hook command is run end to end through its real launcher with fixture payloads (deny denies, allow is silent), extending `MP:dev/test_hooks.py`. | test | `hook_selfcheck.py:1-30` |

**CT-31a and CT-31b mods (3 rows; D87 puts the session-start and webclaw mods in MP's local plugin)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| CT-31a r1 | Every mod module exports a typed `register` and passes `tsc --noEmit` against Claude Code declarations vendored for the installed version; a drift check fails when the vendored declarations differ from the installed version's `/plugin-types` output. Admission: a TypeScript compiler pin. | `plugins/workflow-mods/`, `checks/mods.py` | `fnhook_gates.py:1-10, 373-389, 570-632` |
| CT-31a r2 | A deny-capable mod passes the CT-02b r1 escape-hatch test, behaviourally, under the mod test harness. | test | `fnhook_gates.py:391-447` |
| CT-31b r1 | The grill dialog's question-quality hints (a recommended option first, PRO and CON per option, a citation or an explicit "no prior evidence") are advisory context and never a deny. | grill dialog mod | `ask_quality.py`; D16 |

**CT-35 session start (2 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | One D61 name generator, used by the mod, the SessionStart hook and the handoff. The timezone comes from the host, not a constant; prefixes come from a table (`ccm` first); DST fixtures. `MP:dev/handoff.py:734` switches to it. | `session/names.py` | D15 |
| r2 | The decision table has four outcomes: keep, rename, defer, nonconforming. A nonconforming `-n` name is never renamed, since lanes are addressed by it. State is written before answering, so a reload answers "already ran". State lives under `<git-common-dir>`, not in the tree. | `session/start.py` | `session_start.py:3-21`; D15 |

**CT-29b handoff into the doctor (4 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | Every gathered fact has three states (value, empty, unverifiable); a failed lookup never renders as "none" or 0. | `session/state.py` | `session_state.py:9-12` |
| r2 | The "merged since" window starts at the previous handoff's generated stamp, not at its mtime. | `session/state.py` | `session_state.py:17-20` |
| r3 | `--agents-done` is checked by a census of the session's descendant processes (wait loops, background shells), not merely asserted. | `session/census.py` | `session_orphans.py:1-12` |
| r4 | One task carrier, the plan's `## Next Step`; a HANDOFF that carries its own next-task list fails. | handoff check | `handoff_check.py:46-50, 311-340` |

**CT-37 new-terminal handoff (2 rows)**

| Row | Improved design (acceptance) | Destination | DF evidence |
|---|---|---|---|
| r1 | Refines item (5). The context trigger fires at stepped levels, and each level is persisted before firing, so a crash re-fires only at the next step. Neither a successor `claude --bg` nor a `claude stop` runs without the fresh-session admission. | `session/context.py` | `coordinator_handoff.py:5-9, 203-215, 749-751`; D16 |
| r2 | Refines item (2). The citation linter is CT-38a r2's resolver, with a colon-name fixture. | import | D5 |

**Error classes and transcripts (7 rows)**

| Ticket | Row | Improved design (acceptance) | DF evidence |
|---|---|---|---|
| CT-49 | r1 | A mutation proof per `prevented` class: the class names a revert patch, and `errclass:check` applies it to a temporary copy and requires the detector to fail. A control that returns skip counts as unarmed. | `session_gate.py:53-89` (hard-coded string substitution); `eval_cases.py` docstring |
| CT-20a | r1 | Pair each `tool_use` with its `tool_result` to separate attempted calls from executed ones. Classes: bypass, blocked, pre-rule, task, diagnostic, one-off, using CT-02b r2's `since` dates (CT-51's detectors build on them). | `command_audit.py:20-50`: 147 of 155 rule matches predated their rule |
| CT-20a | r2 | A second concurrent audit exits at once on a lock; reads stay under the byte cap. | `command_audit.py:56-62`: seven concurrent scans of about 814 MB each |
| CT-20b | r1 | Skill and task candidates are ranked by the number of distinct sessions, not by raw counts; the narrative pass only surfaces passages. | `session_review.py:11-37` |
| CT-19 | r1 | A lane receipt merges, per agent, the self-report, hook events and transcript observation. A missing source is recorded as unavailable, never as empty; disagreements are kept. | `lane_result.py:46-80, 657-713` |
| CT-59 | r1 | Codex review mode runs in a read-only sandbox, not under a prompt request. The settlement records a dirty-tree check before and after and is written atomically by a detached supervisor; spawn reconciliation compares the claimed specialists with the observed rollouts. | `sdlc_team.py:590-658, 789-800`; D16 |
| CT-17 | r1 | `session:status` classifies background sessions read-only: alive, dead, wedged, done, and needs-human (blocked with a `needs` payload). It never respawns or stops one. | `dag_tick.py:1-60` |

**Doctor, guidance and Codex roles (4 rows)**

| Ticket | Row | Improved design (acceptance) | DF evidence |
|---|---|---|---|
| CT-22b | r1 | On the host surface, a listing budget: skill and agent listing characters from the enabled set against a declared ceiling. Summing frontmatter undercounts, so the measured value is what gets recorded. | `doctor.toml:179-228`, `listing_budget.py` |
| CT-22b | r2 | The hk hook events that `hk.pkl` defines are installed for this checkout. | `doctor.toml:367-375` |
| CT-58 | r1 | A path-scoped rule whose `paths:` globs match no tracked file fails; one frontmatter parser serves every consumer. | three disagreeing classifiers (`rule_registry.py:12-20`); `instructions_report.py` "never fired" |
| CT-07 | r1 | `.codex/agents/*.toml` validate against a schema generated from the installed Codex version, and the roster is asserted by name (shared with CT-56). Runs after Codex returns on 2026-10-19. | `codex_agent_validate.py`, `codex_schema.py` |

## 4. Not imported

### 4a. Agent-workflow parts left behind, with the reason

- `main.py` and the `dotfiles-setup` console script: D60 runs each module with `python -I -m`
  (CT-39 r1).
- `verify.py`, `suites.toml` and `token_audit.py`: substring wiring (D6); CT-38a r1 resolves
  objects, so the token audit has nothing left to audit.
- `sdlc_team`'s five-specialist prompt and `sdlc_final_report.py`: MP's roles and dispatch are
  CT-59's, and only the CT-59 r1 properties carry over.
- Automatic successor launch and retirement in `coordinator_handoff.py`, `handoff_inbox.py`: they
  start and stop sessions without admission (D16).
- `dag_tick.py`, `dag_project.py` and the launchd agents: daemon registration waits for explicit
  instruction (`MP:AGENTS.md`), and `claude respawn` is a mutation; CT-17 r1 keeps the read-only
  classification only.
- `reap.py`, `bounded_wait.py`: the harness blocks foreground sleep and offers Monitor, and killing
  host processes is a mutating host operation.
- `memory_index.py`: MP's `MEMORY.md` index has seven lines, far from its 200-line cap.
- `agentsview_pass.py`: CT-20a's transcript adapters read the records directly.
- `instructions_observer.py`: a hook on every instruction load costs latency, and CT-58 r1 answers
  the main question statically.
- `rule_sync.py`, the `eval`, `md_size_budget`, `tool-currency` and `cc` steps through `kb-setup`:
  they exist because the logic lives in two repositories, and consolidation ends that.
- `ask_quality.py` as a deny (D16); it becomes advisory in CT-31b r1.
- `branch_guard.py`, `coordinator_write_guard.py`: MP's parent commits plan records on the
  integration branch and lanes work in worktrees; D8's parent-only records rule is the boundary.
- `plan_attest.py`: a passthrough task (CT-38 bans them); CT-37 item (3) attests through its own task.
- `skills_mirror.py` text rewriting: F3's anti-pattern; CT-38 keeps byte copies.
- `pr.py` ship, land and automerge, `autofix.yml`, `workflow_hooks.py`: MP publishes through A09
  and CT-18, pushes wait for instruction, and CI never writes to Git.
- `codec.py` (msgspec), `config.py` (pydantic-settings): TR's stdlib core replaces them.
- `hk_builtins_audit.py`: it generates a catalog document; nothing in MP would consume it.
- `lane_result`'s Mermaid rendering: no MP consumer until CT-31b's lane pane asks for one.
- `graphify*.py`, `graph_bakeoff.py`: CT-55's spike decides adopt or drop.
- `.mode` autonomous and a gitignored `task_plan.md`: D54, and MP tracks its plan.
- Outside DF-B's scope, flagged for the parent: `research_fanout.py` (3,256 lines),
  `saved_searches.py`, `research_scope.py`, `codex_research_gate.py`. `MP:AGENTS.md` itself runs
  `mise -C <dotfiles-checkout> run research-fanout` for strict hook receipts, and the Codex Stop
  hook uses `~/.codex/tools/dotfiles-research-gate` (package `AGENTS.md:32`): both are DF sunset
  blockers on the research side.

### 4b. Stays in DF (host setup)

The chezmoi tree (`home/`, `.chezmoiroot`, `chezmoi_template_render`), shell files, fnox config and
`doctor --fnox-only`, the global mise profile `.config/mise/conf.d/shared.toml`, the
`[bootstrap.macos.launchd]` table, and devcontainer and image tooling: `image*.py`, `docker.py`,
`container.py`, `devcontainer_*.py`, `native_clis_container.py`, `apt_*.py`, `llvm_major.py`,
`gcc_sha.py`, `p2996_hash.py`, `p2996_refresh.py`, `platform_target.py`, `ghcr*.py`,
`lock_refresh.py`, `lock_shared.py`, `lock_integrity.py`, `lock_sidecars.py`, `sync*.py`,
`bootstrap_packages.py`, `renovate*.py`, `pin_parity.py`, `path_drift.py`. Also user-level Claude
plugin management (`plugin_*.py`, `removed_plugins.py`, `install_doctor.py`), the host checks in
`doctor.py` and `doctor.toml` (fnox, mcp, path drift, devcontainers), `hk-image.pkl`, and the
workflows `build-publish.yml`, `image-analysis.yml`, `ghcr-cleanup.yml`, `gcc-sha-repair.yml`,
`probe-aslr-tsan.yml`, `refresh.yml`. DF keeps a small lint and test kit for that code (`lint.py`,
`pytest_runner.py`, `process_stream.py`, `host_lock.py`, `child_env.py`, `process_env.py`, ruff, ty
and pytest config), frozen as host infrastructure rather than grown as agent tooling.

## 5. Sunset checklist

DF code may be deleted once MP holds the replacement. Each item names its trigger.

1. DF-B-1 lands: MP no longer loads `dotfiles_setup/host_lock.py`. DF keeps the file for its own
   image jobs; the lock path stays shared. MP's evidence files that record the old path are history
   and stay.
2. CT-38a lands: delete `doc_refs.py`, `token_audit.py`, `bash_budget.py`, `verify.py`'s
   `workflow.*`, `orchestration.*` and `eval.*` suites with their tests, the hk steps `doc_refs`,
   `contract_token_uniqueness`, `bash_logic_budget` and `skills_mirror_parity`, and `skills_mirror.py`.
   The `build.*`, `ci.*`, `identity.*` and `architecture.*` suites stay with the image.
3. CT-29b and CT-37 land: delete `handoff_check.py`, `session_state.py`, `plan_attest.py`,
   `session_orphans.py`, `coordinator_handoff.py`, `handoff_inbox.py`, `agentsview_pass.py`, the
   tasks `handoff-check`, `plan-attest`, `session-state`, `session-orphans`, `coordinator-handoff`,
   `handoff-inbox`, `session-agentsview-pass`, and their tests. The handoff skills belong to the
   skills import report.
4. CT-35 lands with the mod in MP's local plugin (D87): delete `session_start.py`,
   `session_common.py`, the `session-start` task, the DF mod `register.ts` and
   `.agent/state/session-start/`, once the user enables MP's plugin for DF sessions.
5. CT-02b lands and DF sessions run with MP's user-level plugin, or the user accepts no project
   guard in DF: delete `hook_guard.py`, `hook_dispatch.py`, `heredoc.py`, `script_guard.py`,
   `ask_quality.py`, `worktree_guard.py`, `branch_guard.py`, `coordinator_write_guard.py`,
   `environment_admission.py`, `hook_selfcheck.py`, `scripts/pretooluse-guard.sh` and the DF
   PreToolUse, PostToolUse, SubagentStart and InstructionsLoaded hook entries.
6. CT-20a, CT-20b, CT-49 and CT-51 land: delete `command_audit.py`, `session_review.py`,
   `session_ledger.py`, `session_store.py`, `session_gate.py`, `skillopt_provenance.py`,
   `skillopt/`, the `command-audit` and `session-review*` tasks.
7. CT-59 and CT-19 land: delete `sdlc_team.py`, `sdlc_final_report.py`, `lane_result.py`,
   `codex_lane*.py`, `codex_verdict.py`, the `sdlc-team`, `lane-receipt` and `codex-lane*` tasks,
   `schemas/sdlc-team-*.json`, `lane-result.json`, `gate-result.json` and `.agent/sdlc-*`.
8. CT-07 lands: delete `codex_agent_validate.py`, `codex_agent_parity.py`, `codex_schema.py` and
   their hk steps.
9. CT-31a lands: delete `fnhook_gates.py`, its hk step and `tests/fixtures/fnhook/` once no DF
   plugin carries function hooks.
10. CT-22b and CT-58 land: delete `listing_budget.py`, `rule_registry.py`,
    `instructions_report.py`, `instructions_observer.py` and the doctor's `[listing]` section.
11. CT-26a and CT-52 land: delete `lint_delta.py`, `codegen_check.py`, `codegen_imports.py` and the
    `codegen` group, once DF's four generated models go with their modules (`schema_vendor.py`
    stays for DF's own configs).
12. CT-17 lands: delete `dag_tick.py`, `dag_project.py`, and unload the two launchd agents (a host
    operation that needs its own admission).
13. Before any deletion, triage DF's 397 local and 614 remote branches, its 165 worktrees, the 12
    unpushed commits on the detached HEAD, the untracked research files, and the 270 MB in
    `.agent/gate-results/`.
14. Before the knowledge-base repo is deleted (archiving keeps it resolvable): DF drops the
    `kb-setup` dependency (`pyproject.toml:40`) and the steps that use it (`md_size_budget`,
    `tool-currency*`, `eval`, `cc`, `rule-sync`), plus the knowledge-base checkout in `ci.yml`.
15. MP never takes a dependency on `kb-setup` or `dotfiles_setup`. A CT-39 r14 test keeps it that
    way.

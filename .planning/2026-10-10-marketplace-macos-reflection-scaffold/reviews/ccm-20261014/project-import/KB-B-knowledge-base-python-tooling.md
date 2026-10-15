# KB-B: knowledge-base Python tooling, import review

Agent KB-B, session `ccm-20261014`, 2026-10-14. This review was read-only.

KB is `/Users/rmanaloto/dev/github/ray-manaloto/knowledge-base`, branch `main`, HEAD `f086f731`
(2026-10-05). Its worktree already had a modified `.codex/config.toml` and untracked files; I left
them alone. Paths are KB-relative unless they start with `MP:` or `DF:`; `ks/` means
`python/src/kb_setup/`.

**Method.** Nothing in KB was run. I used `cat`, `sed`, `grep`, `git log` and `git show`, plus
stdlib `python3 -I` AST and tomllib parsers started from the scratchpad. Four read-only helper
agents reviewed four clusters (guards, session and handoff, gates and core, currency and
research), and I merged their findings. I re-read the key citations myself:

- `citations.py:173-176`
- `gates.py:765-788`
- `hook_guard.py:308-311`
- `result.py:160-166`
- `MP:plugins/aggregated-research/mise.toml:3`
- `MP:dev/handoff.py:86-87`

The running `kb-setup serve-memory` process was not touched.

**Scope.** This report covers the `kb_setup` package, its CLI, `pyproject.toml`, `mise.toml`,
`hk.pkl`, CI and the tests. It does not cover the corpus contents (`graphify-out/`, `sources/`,
`docs/`), the skills, the agents or the rules.

## 1. Inventory

### Package and entry points

`python/src/kb_setup/` holds 150 tracked `.py` and `.toml` files, 77,471 lines in all. The first
commit is 2026-07-21; the last is `e79f3846` on 2026-10-04. Lines by cluster:

- **Graphify substrate:** 16,375 lines in 24 files, including `graph.py` (3,732),
  `graphify_baseline.py` (2,128), `graphify_sdk.py` (1,547), `_merge_docs.py`, `lexical.py`,
  `fusion.py` and `code_intel.py`.
- **Currency, models, Codex lanes and mod tooling:** 15,565 lines. `currency/` alone is 16 files and
  7,937 lines, with `sync.py` at 2,212.
- **Session, handoff and work memory:** 14,705 lines in 23 files. This includes `citations.py` and
  `resolve.py`.
- **Gates, evals, core runtime, ship and the CLI:** 14,230 lines in 24 files. `cli.py` is 1,238.
- **Guards and authoring lints:** 7,828 lines in 19 files. This includes `skill_lint.py` (328),
  `hook_guard.py` (525) and `md_budget.py` (759).
- **Docs mirrors, fetch, source manifests and live receipts:** 4,743 lines in 10 files.
- **Generated msgspec models:** 2,221 lines in `generated/` (15 files) plus a 14-line prototype.
- **Research adapters:** 1,804 lines in `research/` (6 files).

There are two console scripts (`pyproject.toml:39-41`): `kb-setup = "kb_setup.cli:main"` and
`aggregated-research = "kb_setup.research.cli:main"`. `ks/cli.py` is one if-chain over 99
subcommands, and its repo root is `Path.cwd()` (`cli.py:126-129`).

### Build and tool configuration

**`pyproject.toml`** is 491 lines (`06b3d94e`, 2026-10-03), 260 of them comments.

- It builds a hatchling wheel of `python/src/kb_setup` (`:92-101`).
- Runtime deps (`:25-37`): `anthropic`, `graphifyy[all]==0.9.57` (sourced from a fork SHA at
  `:315-316`), `httpx2`, `msgspec`, a SkillOpt VCS SHA and `structlog`.
- Groups:
  - `dev` (`:81-88`): ruff 0.16.5, ty 0.0.77, pytest 9.1.1, pytest-xdist 3.8.0, trafilatura and
    mcp2cli.
  - `codegen` (`:90`): datamodel-code-generator[protobuf] 0.76.0.
  - Both are default groups (`:312-313`).
- ruff uses `select = ["ALL"]` with ten package-wide ignores (`:106-138`) and per-file ignores
  (`:162-258`).
- ty targets Python 3.14 and excludes `_merge_docs.py` (`:266-274`).
- pytest has only `addopts = "-q"` (`:276-278`).
- It defines 14 datamodel-codegen jobs (`:340-491`).

**`mise.toml`** is 2,050 lines (`1b970068`, 2026-10-04); 1,455 of them (71%) are comments.

- `min_version` is at `:40`.
- It pins 25 tools, including python 3.14.7, uv 0.12.8 and hk 2.4.0 (`:44-47`).
- `[deps.uv]` sets `auto = true` and `run = "uv sync --locked"` (`:262-264`); `auto_install = true`
  is at `:286`.
- It carries a 13-entry `disable_tools` list (`:271`).
- It defines 113 tasks; 100 of them run `uv run kb-setup <cmd>`. `uv run` appears 112 times and
  never with `--no-sync` or `--offline`.

**`hk.pkl`** is 643 lines (`06b3d94e`), 485 of them comments.

- The hk version appears in five tokens: `hk.pkl:1`, `hk.pkl:6` (twice each) and
  `min_hk_version` at `:12`. `mise.toml:47` holds the tool pin.
- `check`, `fix`, `pre-commit` (with `fix = true`) and `commit-msg` share 20 lint steps
  (`:355-643`).
- Python steps are `uv run ruff`, `uv run ty check python/src tests` and seven
  `uv run kb-setup ...` steps (`:417-619`).

**Locks.** `uv.lock` is 2,926 lines with 167 packages (`6b3ab427`, 2026-09-10). `mise.lock` is
7,048 lines. For comparison, MP's `uv.lock` has 18 packages.

**Root configs** the package reads:

| File | Lines |
| --- | --- |
| `currency.toml` | 2,268 |
| `reclaim.toml` | 188 |
| `models-sites.toml` | 60 |
| `doctor.toml` | 3 |
| `lychee.toml` | 41 |
| `.gitleaks.toml` | 163 |
| `.agnix.toml` | 109 |
| `tsconfig.json` | 25 |

`schemas/` holds 13 JSON Schemas, 3 protos, `sources.toml` and `templates/`.

### Hooks, MCP and CI that call the package

**`.claude/settings.json`:**

- PreToolUse:
  - `uv run --project "${CLAUDE_PROJECT_DIR:-.}/python" kb-setup hookguard` on Bash and Grep.
  - Eight `if`-filtered `mise run -C ... kb-instruction-edit-guard` handlers.
  - `mise run ... kb-instruction-shell-write` on every Bash call.
- SessionStart: `kb-currency-check`, `kb-codex-config-check` and `kb-env-refresh`.
- SessionEnd: `brain-transcript-audit` and `kb-session-reflect`.

`.codex/hooks.json` repeats most of these and adds `kb-setup edit-check` on `apply_patch`.

**MCP.** `.mcp.json` registers `kb` (`uv run kb-setup serve`) and `kb-memory`
(`uv run kb-setup serve-memory`), and `.codex/config.toml` also registers `kb-memory`. No dotfiles
config and no `~/.claude.json` entry names `kb-memory` (I checked key names only). The live
`serve-memory` process is a child of a `claude bg-spare` process and has run for about 9 days,
according to a helper's observation; I did not touch it.

**CI** has two workflows:

- `.github/workflows/docs-refresh.yml` (41 lines, 2026-10-03): a cron refresh of the docs mirror.
- `.github/workflows/graphify-live-receipt.yml` (84 lines, 2026-09-27): runs on
  `pull_request_target`, checks out the base only and verifies a signed receipt.

No workflow runs lint, tests, eval or the codegen check.

### Tests

`tests/` holds 163 `.py` files, 74,406 lines (`26a84f7f`, 2026-10-04). Every module is imported
by at least one test. `tests/conftest.py` (244 lines) has an autouse `isolated_mise_state` fixture
(`:35-60`) and a real-git fixture (`:123-170`). The `test` task is
`uv run pytest tests/ -x -q -n auto --dist loadgroup` (`mise.toml:494`). KB records 2,059 tests,
with `test` taking 219 s of a 249 s gate run (`pyproject.toml:74-80`).

### Consumers outside KB (sunset blockers)

**MP's plugin.** `MP:plugins/aggregated-research/mise.toml:3` installs KB with pipx at `a872cb01`.
That pin has one verb, `trackers`. The call path is recorded in
`MP:docs/agents/legacy-trackers-boundary.md:15-24`:
`bin/aggregated-research -> kb_setup.research.cli:main -> kb_setup.cli -> research.trackers`.
`MP:docs/agents/python-bridge-placement.md:3-9` uses that pinned console entry as the first
native-core bridge. KB HEAD is 109 commits newer and adds `links`, `packages` and `codesearch`.

**Dotfiles.** `DF:python/pyproject.toml:40` pins `kb-setup @ git+...@e8fe42ae`. DF uses five
modules from it:

- `kb_setup.evals`: `DF:python/src/dotfiles_setup/main.py:16` and `eval_cases.py:35`.
- `kb_setup.md_budget`: `listing_budget.py:42`, plus the hk step at `DF:hk.pkl:698`.
- `kb_setup.currency`: `DF:mise.toml:687, 696` and `doctor.py:159`.
- `kb_setup.launch`, through `kb-setup cc` at `DF:mise.toml:1588`.
- `kb_setup.graph`: `graphify.py:32`.

Five contracts in `DF:python/verification/suites.toml` bind that pin (`:1412, 1432, 1467,
2306-2346, 2696`).

**Disk.** `.venv` is 727 MB and `.agent` is 232 MB. `graphify-out` (5.9 GB) and `sources` (11 GB)
belong to the corpus reviewers.

## 2. Defects

### Packaging, isolation and dependency sync

- **P1.** Every task, hk step and hook runs a console script through `uv run`: the task rows,
  `hk.pkl:419-619` and the `hookguard` hook. ADR 0003 rejects this form because the wrapper starts
  Python without `-I` (F2 Part B §3).
- **P2. Implicit syncs everywhere.**
  - `[deps.uv]` sets `auto = true`, so `uv sync --locked` runs before every `mise run`
    (`mise.toml:262-264`). That includes the SessionStart and SessionEnd hooks and the PreToolUse
    hook on every Bash call.
  - Plain `uv run` syncs again.
  - `tests/test_codegen.py:20-40` runs `uv run --locked --group codegen` inside pytest.
  - `skillopt_contract.py:457-476` runs `uv sync --locked` inside a "contract check".
  - `worktree.py:452` runs `uv sync`.

  `pyproject.toml:302-311` records the result: exact syncs uninstalled the codegen group in the
  middle of a test run, so each run failed a different set of tests. The fix there, making
  `codegen` a default group, treats the symptom.
- **P3.** `auto_install = true` (`mise.toml:286`) lets any task install tools from the network.
- **P4. The dev tool is published as a runtime package.** Its heavy runtime deps flow to every
  consumer: `graphifyy[all]` with a fork override, `anthropic`, a SkillOpt VCS SHA, `httpx2` and
  `structlog`. DF needs `override-dependencies = ["graphifyy[all]"]` just to resolve
  (`DF:python/pyproject.toml:60-67`). MP's plugin pipx install of the same package is 1.3 GB
  (`MP:plugins/aggregated-research/README.md:59-61`).
- **P5. Package hygiene.**
  - `__init__.py:2-5` calls this 77k-line package "thin helpers" that are "logic-light".
  - `_merge_docs.py` runs under a different interpreter but sits inside the importable package, and
    is excluded from ty (`pyproject.toml:269-274`).
  - `generated_packages_prototype.py` is a test-only prototype that ships in the wheel.
- **P6. The Python version is stated in five places that are kept in step by hand:**
  - mise `python = "3.14.7"` (`mise.toml:44`)
  - `requires-python = ">=3.14"` (`pyproject.toml:5`)
  - ruff `py314` (`:108`)
  - ty `3.14` (`:267`)
  - codegen `target-python-version` (`:346`)

  CI pins it a sixth time (`docs-refresh.yml:36`; `graphify-live-receipt.yml:29`). MP has the same
  gap today: `requires-python = ">=3.11,<3.16"` (`MP:pyproject.toml:4`) against mise 3.15.0
  (`MP:mise.dev.toml:6`).
- **P7. Lint and test settings are loose.**
  - ruff ignores S603, S607, T201, PLC0415, TC003, TRY003, EM101 and EM102 for the whole package
    (`pyproject.toml:112-138`), so subprocess hygiene is never linted.
  - ty escalates no rules.
  - pytest has no `--strict-markers`, no `filterwarnings = error` and no timeout (`:276-278`).

### CLI

- **C1.** One 1,238-line dispatcher needs complexity waivers (`pyproject.toml:209-216`).
  - Flags are parsed by hand (`_opt`, `"--live" in rest`; `cli.py:205-210, 666-670`), so a
    misspelt flag is silently ignored.
  - No subcommand has `--help`.
  - Handlers mix `main(rest, root)` and `main(root, rest)` (`cli.py:551-580`).
- **C2. Three hand-kept command lists drift apart.**
  - `_print_usage` (`cli.py:56-123`) omits 15 dispatched commands, among them `build`, `ship`,
    `land`, `hookguard`, `codex` and `fetch`.
  - The unknown-command message names about 50 of the 99 (`cli.py:727-760`).
  - Seven dispatched commands have no mise task: `claude-types-check`, `edit-check`, `hookguard`,
    `lane-recording`, `md-budget`, `no-lint-skip` and `workflow-lint`.
  - `tests/test_cli_usage.py` checks only the spacing of separators.
- **C3. Exit codes are named but not enforced.**
  - `Err` rejects only `Rc.OK` (`result.py:160-166`). So `Err(..., FINDINGS)` is legal
    (`hk_test.py:229`), `plugin_validate.py:288-303` returns schema findings as 2, and
    `check.py:354` returns "nothing checked" as 2.
  - `Rc.NOT_RUN = 127` collides with the shell's command-not-found code (`context_usage.py:325-372`).
  - KB's meanings (1 = findings, 2 = bad request) differ from MP's (0 pass, 1 usage, 2 refusal;
    `MP:dev/AGENTS.md:26-27`).

### mise tasks

- **M1.** Six overlapping "is it green" entry points each cover a different set:
  - `lint`
  - `test`
  - `check` (lint plus test only; `mise.toml:749-751`)
  - `kb-check` (per path)
  - `eval`
  - `kb-gates` (ten tasks; `gates.py:172-200`)

  The codegen drift check is in none of them; it runs only as a pytest test.
- **M2. Configuration is narrative.** Comments make up 71% of `mise.toml`, 75% of `hk.pkl` and 53%
  of `pyproject.toml`, mostly incident history. Some of it is wrong today:
  - `mise.toml:1563` says "This repo has no CI".
  - `.claude/rules/ci-local-parity.md:10` says there is no `.github/`.
  - `mise.toml:944-946` names 5 of the 14 codegen jobs.
  - `pyproject.toml:319` says 0.75.1 against the 0.76.0 pin at `:90`.
- **M3. Tasks are coupled to the host.**
  - `cc`, `cc-doctor` and `cc-fresh` hard-code `--sibling "$MISE_PROJECT_ROOT/../dotfiles"`
    (`mise.toml:1872-1945`).
  - `disable_tools` has to copy the user's global list, because a project list replaces it rather
    than extending it (`:265-285`).
  - `min_version` keeps a `soft` key that is deliberately inert (`:19-40`).
- **M4. Pass-through and duplicate entries.**
  - `kb-research` is just `uv run aggregated-research`, next to four `kb-research-*` tasks
    (`mise.toml:962-985`).
  - `kb-add`, `kb-reflect` and `brain-update` run bare `graphify` (`:1370, 1443, 1481`).

### hk

- **H1. Steps run whether or not anything relevant changed.** Python steps sync through `uv run`.
  These steps run on every commit regardless of the staged files (`hk.pkl:422-425, 501-552,
  616-619`):
  - `skill_lint`, `md_size_budget` and `lane_recording`, which have no glob;
  - `ty`, over the whole tree;
  - `models_apply`, with `glob = "**/*"`.
- **H2.** hk's version lives in five tokens. Bumping only the `amends` URI fails with a module
  version conflict (`hk.pkl:340-343`).
- **H3.** There is no pre-push profile. Tests, eval and codegen drift run only through `kb-ship`
  on the developer's machine.

### CI

- **CI1.** No workflow runs any gate (lint, test, eval or codegen). The CI rule file still says
  there is no `.github/` (`.claude/rules/ci-local-parity.md:10`).
- **CI2.** `docs-refresh.yml:19-20, 36` runs
  `PYTHONPATH=python/src uv run --no-project --python 3.14.7 --with structlog==26.1.0 python -m kb_setup.docs_mirror`.
  - That is a second dependency resolution outside `uv.lock` and a second interpreter pin.
  - It runs without `-I`, and adding `-I` would break it, because `-I` ignores the `PYTHONPATH` it
    depends on.
  - Its `check` step reads the stamp that `refresh` has just written (`:37-38`), so the freshness
    result means nothing.
- **CI3.** `graphify-live-receipt.yml:48, 79` runs `python3` on trusted scripts without `-I`, and
  `live_receipt.py:280-295` parses the payload before it verifies the signature.

### Tests

- **T1. Test fixtures leak host configuration.**
  - The git fixture switches off only GPG signing (`conftest.py:123-170`), so global git config and
    hooks stay active. KB installs hk hooks globally (`mise.toml:301`), so fixture commits can run
    host hooks.
  - `isolated_mise_state` symlinks the host's mise trust store into the test state
    (`conftest.py:52-57`).
- **T2. Some tests pass by skipping or test nothing.**
  - Tests skip when `mise`, `claude`, `tsc` or `lychee` is missing (`test_mise_state_isolation.py:35`;
    `test_fnhook_gates.py:93-98, 390-395`; `test_research_links.py:34-36`).
  - The four real handoff-pair tests skip in a fresh clone (`test_handoff_reconcile.py:52-60`).
  - `test_hook_guard.py:198-216` only checks that the file collects.
- **T3. Some tests touch the host or depend on timing.**
  - `test_lock_drift.py:181` patches `subprocess.run` for the whole process.
  - `test_cpu_bounded.py:100-110, 200-218` asserts wall-clock times.
  - `test_guard_codegen.py:27-49` copies the live repo and symlinks the real `.venv`.

### Skill lint and guards (CT-38, CT-02b)

- **S1. The runtime guard and the authoring lint do not share one decision table.**
  - `skill_lint` injects only `hook_guard.decide` (`skill_lint.py:161`). That function covers only
    graphify and bare python (`hook_guard.py:68-90, 124-162`).
  - The seven other Bash guards run only at runtime (`hook_guard.py:295-307`).
  - So the 14 skill lines that call `uv run kb-setup ...` directly pass. They are in
    `.claude/skills/{clear-prep,session-resume,kb-reclaim,tool-currency}/SKILL.md` and their
    mirrors.
  - Even so, the success message says "every instructed command is a mise task or allowed
    read-only" (`skill_lint.py:316-318`).

  The CT-38 row that cites KB as the precedent for a shared table is therefore only half right.
- **S2. The lint has coverage holes.**
  - It scans only `SKILL.md`, not `references/*.md` (`skill_lint.py:54-66`), although the mirror
    check covers every file.
  - Only fences tagged bash, sh, shell, console or zsh are read (`:85, 136`), so an untagged fence
    is never checked.
  - Each line is judged on its own, so continuation lines and heredoc bodies are misread
    (`:152-153`).
  - A skill directory with no `SKILL.md` (`model-registry/`) escapes both checks (`:255`).
- **S3. The mirror check runs one way and is lenient.**
  - It walks `.claude/skills` only (`skill_lint.py:255`).
  - It skips dot-paths (`:275`).
  - It returns clean when `.agents/skills` is absent (`:252`).
  - It reads the working tree, so untracked files count.
- **G1. Four heredoc parsers disagree:** `graph_first.py:182` (used by `hook_guard._code_only`),
  `secret_guard.py:325`, `distill.py:106` and `check_first.py:329-401`. As a result,
  `printf '<<x'` followed by `python3 y.py` gets past the bare-python check.
- **G2. Guards fail open where the harm cannot be undone.**
  - Every chained guard allows the command when it raises (`hook_guard.py:308-311`).
  - `secret_guard` allows anything it cannot parse (`:421-423`).
  - `destructive_git` allows the command when git cannot be asked (`:288-291, 342-345`).
  - `destructive_git` also checks the hook's own cwd, not the target of a `cd` or `-C` in the
    command (`hook_guard.py:425-431`; `destructive_git.py:110, 281-287`).
- **G3. Escape hatches and command-word handling.**
  - Any command that contains `mise run kb-` is allowed (`hook_guard.py:139`; `check_first.py:629`),
    so `echo "mise run kb-query"` unlocks the graph-first guard (`graph_first.py:69, 165`).
  - `codex_lane.py:171` misses `/opt/homebrew/bin/codex exec`.
  - `stage_explicitly.py:102` misses `env git add -A`.
- **G4. Policy machinery that protects nothing.**
  - `settings_guard.py` is not wired in, and it normalises paths differently from the TS mod it
    mirrors (`:24-30, 62-74`).
  - `guard_codegen.py` spends 537 lines plus 486 test lines keeping ten strings in sync, and reads
    TypeScript with a regex (`:241-267`).

### Session, handoff and context (CT-29, CT-37, CT-23)

- **SH1. Ported as is, the rc-claim checker would check nothing in MP.** Its task regex does not
  allow `:` (`citations.py:173-176`). It reads declared tasks only from `mise.toml`
  (`resolve.py:631`). It silently drops claims about undeclared tasks (`handoff.py:401`).
- **SH2. The per-SHA gate record is unreliable.**
  - Any subset run rewrites the whole record, and the record does not store which tasks were
    requested (`gates.py:759-788, 1195`). Yet `handoff.py:576` confirms a `kb-gates rc=0` claim
    from whatever rows are there.
  - `dirty` is a boolean read before the run (`gates.py:489-490`).
  - The outcome sidecar is never cleared (`:513`).
  - A timeout kills `mise` but not its children (`:464`).
- **SH3. Handoff selection is unreliable in both repos.** KB picks the handoff and its predecessor
  by mtime (`handoff.py:663-676`; `handoff_reconcile.py:486-507`). MP sorts the names and takes
  the last one (`MP:dev/handoff.py:86-87`), so `HANDOFF-...-14-b.md` sorts before
  `HANDOFF-...-14.md`.
- **SH4. Reconcile claims more than it checks.**
  - Headings match by substring, so "owed" also matches "allowed" (`handoff_reconcile.py:66, 347`).
  - Only code spans and issue references count (`:389-393`); items written in plain prose vanish.
  - Any surviving token clears an item.
  - The unchecked count promised at `:40-42` is never printed (`:562-583`).
- **SH5. `context_usage` hard-codes host and model facts.**
  - Window sizes are matched by substring, so plain "opus" means 200k (`context_usage.py:122-130`).
  - The threshold is a constant (`:116`).
  - "Unmeasurable" exits 127.
  - With no session id it reads the newest-mtime transcript (`:304`) instead of the hook's
    `transcript_path`.
- **SH6. The transcript readers are fragile.**
  - `distill.py:390-395` crashes on a line that is just `null`.
  - `session_reflect.py` reads each transcript twice inside a 60 s SessionEnd hook
    (`:548, 682-685`). It reads the newest-mtime transcript rather than the one named in the hook
    payload (`:655`).
  - `brain.py:472` globs only top-level `*.jsonl`, so subagent transcripts are missed.
- **SH7. Two checks report green when they are not.**
  - `next_ticket.py:418-445, 480-492` calls a ticket READY without looking at lanes or open PRs, and
    exits 0 when it could not ask.
  - `codex_config.py:312-323` always exits 0, even though KB's own `.codex/config.toml` is rewritten
    right now.

### Gates, evals and ship (CT-11, CT-18, CT-49)

- **E1. The eval control arms can be bypassed.**
  - A gated case whose precondition SKIPs bypasses the control-arm rule (`evals.py:1498`) and never
    turns the run red (`:195, 1626`).
  - Any FAIL arms a case, not only the expected failure (`:1416`).
  - The guard-table control fails for any guard that gets one row right (`:814, 851`).
- **E2.** `arms.py:445` mutates the live tree. Its restore check compares newline-normalised text,
  so a CRLF change is invisible (`:377, 404-405`).
- **E3.** `hk_test.py:63, 210` counts `ok - ` lines across both streams against a floor of 40,
  while 46 tests exist.
- **E4. Ship and land.**
  - `pr.py` binds the push to the review receipt, not to the commit the gates ran at
    (`:622-631, 705`).
  - It counts "no checks" and the `skipping` bucket as green (`:66, 243-244`).
  - `land` checks out `main` in the caller's checkout (`:868`).
- **E5.** `worktree.py:153-158` binds macOS `clonefile` at import time, so the module fails on
  Linux. With no CI test job, nobody sees it.
- **E6. `plugin_validate` is loose.**
  - `plugin_validate.py:201` validates each manifest against whatever `$schema` URL it names,
    fetched live.
  - `:62` allow-lists a missing `version`, the opposite of what CT-57 requires.

### Currency, models, Codex, research and docs

- **R1. The currency check cannot gate.**
  - The SessionStart currency check calls itself "subprocess-free, about 10 ms"
    (`currency/sync.py:13-17`), yet it runs through `mise run` with auto sync.
  - It exits 0 even when there is no config (`currency/run.py:56-63, 142`).
  - Its config parser drops unknown keys (`config.py:556-558, 614-615`).
  - `apply.py:197-241` edits a pin without relocking.
- **R2. The model registry has unsafe and duplicate sources.**
  - `model_limits.py:23-30, 280, 340-346` reads a Claude Code OAuth token.
  - `models.py:52-55, 1158` fetches an overlay from a mutable `main` branch.
  - Claude model data comes from two sources: models.dev (`models.py:357-361`) and Anthropic's
    `/v1/models`.
- **R3.** `codex_run.py:122, 341` always passes `--dangerously-bypass-hook-trust` and the full
  environment.
- **R4. The research adapters overclaim.**
  - Discussions are recorded but never searched (`trackers.py:32-34, 205`), while MP's plugin
    README claims discussion search.
  - Only one page per kind is fetched, and extra hits are silently truncated
    (`:93-98, 180-183`).
  - The null control proves only that the channel is non-empty (`:186-200`).
  - The record's `adapter` field is a free string with nullable sibling variants (`:206-208`).
  - The plugin's skill still sends agents to raw `curl` (`MP:plugins/aggregated-research/skills/aggregated-research/SKILL.md:146`).
- **R5. Fetch and mirror checks measure the wrong thing or nothing.**
  - `fetch.py:587-590` samples tokens from the extracted body and looks for them in a file written
    from that same body, so extraction loss is never measured.
  - `docs_mirror.py:194, 207, 227` passes the full environment to webclaw and reads responses
    without a size cap.
- **R6. Dead code is kept alive.**
  - `artifact_download` always refuses, because the CLI never passes a provider
    (`cli.py:428-430`; `artifact_download.py:364-366`).
  - `mod_runtime.py` is retired (`:2-6`) yet still has 51 tests.
  - `ccdocs_mirror.py` is a shim (`:1-7`).

## 3. Features to import

None of these is a copy. Each row names the improved design, where it goes in MP and which ticket
owns it. Unless a row says otherwise, new code goes under `python/src/marketplace_dev/` and runs as
`uv run --no-sync --offline python -I -m marketplace_dev.<module>` (D60).

### Acceptance rows on existing tickets (59 rows here; 49-K2 and five rows on sibling proposals follow)

**CT-39, Python package (wave 2)**

- **39-K1. One source for the Python version.** A test asserts that these agree:
  - the `mise.dev.toml` Python minor version;
  - `requires-python`, narrowed to `>=3.15,<3.16`;
  - ruff `target-version`;
  - ty `python-version`;
  - every codegen `target-python-version`.

  This extends TR's "ruff target equals requires-python" row and fixes P6.
- **39-K2. Exit-code core** in `marketplace_dev/core/result.py`, stdlib only.
  - An `Rc` enum that follows MP's convention (0 pass, 1 usage, 2 refusal), plus NOT_RUN and
    TIMEOUT, whose values avoid 126 to 127 and anything above 128.
  - `Err` refuses every code that means the command ran.
  - An `External` variant passes a child's rc through, mapping signals to 128+N.
  - Exactly one `exit_code()` conversion.
  - It serialises to the TR envelope already planned for CT-39.
  - It keeps KB's split between "ran and found something" and "did not run"
    (`skill_lint.py:197-217`), and fixes C3.
- **39-K3. No dispatcher and no hand-kept command list.**
  - Each module owns an argparse parser that rejects unknown flags with rc 1 (subclassed `error`,
    per `MP:dev/AGENTS.md:27`).
  - A test derives the command set from the `-m marketplace_dev.<module>` targets in the task rows
    and fails on a task without a module, or a module `main` without a task.

  This fixes C1 and C2.
- **39-K4. One hermetic test fixture module,** `marketplace_dev/testing.py`.
  - It sets `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `core.hooksPath=/dev/null` and a
    scratch `HOME`.
  - It sets a private `MISE_STATE_DIR` without symlinking the host's trust store; trust is granted
    explicitly to scratch configs only.
  - An AST meta-test fails when a test spawns `git` or `mise` without the fixture.
  - It replaces the per-test environment code in `MP:dev/test_hooks.py:40`,
    `MP:dev/test_retro_gate.py:22` and `MP:dev/test_git_delivery.py:22`.

  This fixes T1.
- **39-K5. The discovery task proves what it ran.**
  - The task CT-39 already owns (CT-12's wiring, D85) asserts that the collected test ids equal the
    declared test files, and refuses zero.
  - A skip fails unless its reason is in a committed allow-list that names an owner.
  - The runner stays stdlib `unittest` until a measured suite time justifies pytest-xdist; KB's
    measurement (tests were 88% of gate time at 2,059 tests) is the reference. The decision is
    recorded.

  This fixes T2 and E3.
- **39-K6. Use native suppression bans, not a custom lint.**
  - The hk ruff step runs with `--ignore-noqa`, so an inline suppression cannot hide a finding.
  - ty is configured not to honour `# type: ignore`. The key name is UNVERIFIED and must be
    checked against the pinned ty.

  This replaces KB's substring scan (`lint_checks.py`, `hk.pkl:429-431`).
- **39-K7. A lean package.**
  - `[project.dependencies]` equals the set of third-party modules the package actually imports,
    and a test asserts it.
  - Nothing outside MP depends on `marketplace_dev`.
  - No prototype module or foreign-interpreter script sits inside the package.

  This fixes P4 and P5.
- **39-K8. hk steps are scoped.**
  - Every Python hk step has a glob.
  - ty checks only the staged package files in pre-commit and the whole tree in pre-push.
  - `ruff check --fix` is declared before `ruff format`, with `ruff format` last, rather than
    linked with `depends` (`hk.pkl:556-590` measured why).

  This fixes H1.

**CT-38 (38a, wave 6)**

- **38-K1. One classifier for runtime and authoring.** The lint calls the same `classify()` as the
  CT-02b hook (table in 02b-K2). A test adds one table row and shows both the hook and the lint
  change. Fixes S1.
- **38-K2. Scan everything a skill can instruct.**
  - Every file of every skill: `SKILL.md`, references and scripts.
  - Every fence, whatever its info string.
  - Every `!` line.
  - Continuations and heredocs are joined by the CT-02b tokenizer.
  - A skill directory without `SKILL.md` is a finding.

  Fixes S2.
- **38-K3. A strict mirror check.** It compares tracked bytes from `git ls-files`, in both
  directions, dot-paths included. A missing mirror tree is a failure. Fixes S3.
- **38-K4. The success line states exactly what was checked:** files, fences, lines and the
  classifier digest. It never claims more than that.
- **38-K5. A generated wiring table.** The skill -> task -> module -> test edges are derived from
  skill lines, `mise tasks --json` and the `-m` target in each task row. A dangling edge fails. This
  replaces CT-38's hand-kept table (DF `suites.toml`). KB's `code_intel.py:9-30` shows that the four
  static lanes are enough.
- **38-K6. Description cap.** `description` plus `when_to_use` together stay at or below 1,536
  characters (`md_budget.py:302-323`). DF found an agent description silently cut at that cap
  (`DF:python/verification/suites.toml:2685`).

**CT-58 (38b, wave 19)**

- **58-K1. One budget engine per load class,** in `marketplace_dev/guidance/budget.py`.
  - Eager loads are `CLAUDE.md` plus its `@import` closure; path-scoped rules and skills each get
    their own budget.
  - HTML comments are stripped for `CLAUDE.md` only (`md_budget.py:253-271, 403-460`).
  - It is shared with CT-38a's caps and keeps MP's 200-line skill cap, not KB's 500 (`:88`).
- **58-K2. Short configuration comments.** Comment blocks in `mise.dev.toml`, `hk.pkl` and
  `pyproject.toml` stay under a fixed length. History goes to ADRs, retros and decision rows (M2).

**CT-02b (wave 5)**

- **02b-K1. One shell tokenizer,** `marketplace_dev/shell/tokens.py`.
  - It returns one typed record per simple command: argv, the basename command word and the
    effective cwd.
  - It unwraps `env`, assignments, `command`, `uv run`, `./dev/mise run|exec --` and `bash -c`.
  - The effective cwd follows `cd`, `-C` and `--git-dir`.
  - Each record also carries its redirects, has heredoc bodies stripped and has a `parse_ok` flag.
  - No consumer lexes the command a second time.
  - KB's 443-line heredoc case table (`tests/test_heredoc_tokeniser.py`) is ported as fixtures.

  This fixes G1 and G3 and MP's own `pretooluse_gate.py:23, 37-39`.
- **02b-K2. A classifier table,** `marketplace_dev/hooks/classifier.toml`, validated against
  `schemas/command-classifier.schema.json` (CT-52).
  - Each row has an id, match predicates, a class (harm, redirect or lane gate), a verdict,
    `fail_mode`, a remedy task, an optional stateful probe, and fixtures that must be allowed and
    must be denied.
  - The hook loads the table with `tomllib` and denies when the table is malformed.
  - There is no code generation until a second-language consumer exists.

  This fixes G4.
- **02b-K3. Harm rows fail closed.**
  - Destructive git on a dirty tree, probed at the command's effective cwd, adding `switch -f` and
    `stash drop|clear`.
  - Printing a secret; a command that cannot be parsed is denied.
  - A blanket `git add`.
  - Writes to the gate's own files (`settings*.json`, `marketplace_dev/hooks/**`, the table,
    `hk.pkl`, `mise*.toml`) through Edit and Write or Bash redirects.
  - `codex exec --ephemeral`, because CT-10 needs the session files (`lane_recording.py`).

  Redirect rows may fail open. No row lets a command pass merely because it mentions a task. This
  fixes G2 and G3.
- **02b-K4.** A named check piped into `head` or `tail` is flagged for hiding its exit code; KB
  counted 35 such cases (`check.py:8`).
- **02b-K5. A two-way fixture corpus with a real control.** The corpus has an inverted control, and
  that control must fail for both a constant-allow and a constant-deny guard. This fixes KB's
  vacuous control (E1).

**CT-11 (wave 3)**

- **11-K1. Receipt store.** Append-only JSONL under `$(git rev-parse --git-common-dir)/marketplace/checks/`.
  Every lane worktree shares it, and it sits outside the frozen `.gitignore`.
  - Each line holds HEAD, a working-tree digest, the requested task set, `complete`, a run id, and
    the rc of each task. A task that did not run is `null`; TIMEOUT and NOT_RUN stay distinct.
  - The runner writes the lines. They are never parsed from mise output, because mise masks short
    values (`evals.py:504-645`) and `depends` collapses many rcs into one (`gates.py:35-38`).
  - A timeout kills the whole process group.
  - It is built on `marketplace_dev.receipts`.

  This fixes SH2.

**CT-37 (wave 9)**

- **37-K1. Gate claims.**
  - The parser accepts task names with colons and reads the declared tasks from `mise.dev.toml`.
  - A claim about an undeclared task is a finding, not dropped.
  - A claim is confirmed only by a complete receipt line at the same tree digest.

  Fixes SH1 and SH2.
- **37-K2. Reconcile inside the handoff writer.**
  - It runs against the text the writer is about to replace (`MP:dev/handoff.py:771-778` already
    reads it).
  - It keys on decision ids, lane names, section letters and the pending-user list.
  - Every dropped item needs a disposition word: CARRIED, DONE or DROPPED.
  - The number of unchecked prose items is printed.

  Fixes SH4.
- **37-K3. A closing-commit state limited to the handoff's own files,** so committing the
  regenerated plan does not mark the handoff stale (`handoff.py:158-160` against
  `MP:dev/handoff.py:524-527`).
- **37-K4. Context trigger.**
  - Window sizes come from the CT-46/48 catalog, or from a table keyed by exact model id.
  - The threshold comes from an env variable.
  - The transcript comes from the hook payload's `transcript_path`.
  - "Not measured" has its own rc.
  - A fact for the carrier probe: KB proves that a `CLAUDE_ENV_FILE` write reaches Bash tool calls
    only, never hooks (`env_refresh.py:65`). So a SessionStart `CLAUDE_ENV_FILE` write of
    `PLAN_ID` and `PWF_PLAN_ROOT` on `clear`, made idempotent with a marker (`env_refresh.py:205`),
    is a candidate for Bash and not for the pwf hooks (D73 keeps this decision in CT-37).

  Fixes SH5.

**CT-29 (29a wave 1, 29b wave 7)**

- **29-K1. Unknown is never zero.** Each of these becomes a finding instead of a zero:
  - a tree that could not be read;
  - an unmerged path;
  - a doctor that failed or did not run;
  - a malformed `decisions.jsonl` row.

  These are the MP gaps at `MP:dev/handoff.py:277, 320, 325, 567`. KB's model for it is
  `session_state.py`'s COULD NOT ASK state.
- **29-K2. Choose the handoff by the rev number in `## Next Step`,** never by name order or mtime
  (SH3).
- **29-K3. Session id.** Take it from `CLAUDE_CODE_SESSION_ID`, then from the hook's
  `transcript_path`. The project-dir encoder handles `.` as well as `/` (`MP:dev/handoff.py:820`).
- **29-K4. A seam test** that `./dev/mise run session:handoff` prints the same SHA as
  `git rev-parse`. KB measured redaction mangling SHAs (`session_state.py:27-44`).

**CT-20 (20a, wave 13) and CT-23**

- **20-K1. One streamed transcript reader,** `marketplace_dev/transcripts/`.
  - It tolerates lines that are not JSON objects.
  - It includes subagent transcripts.
  - It takes the transcript path from the hook payload.
  - It serves three consumers:
    - reflection rule tables: rules as data, bounded gaps, a remedy per rule;
    - script mining;
    - session selection: birthtime is cross-checked against the first record, ids match all or
      none, and nothing matched means NOT_RUN.

  Fixes SH6.
- **20-K2. SessionEnd keeps the reflection report and `/session-resume` reads it.** KB moved this
  step to SessionEnd after it was dropped at handoff time in 5 of 5 rounds (F3 Part 2).

**CT-25.** **25-K1.** The outcomes are READY, BLOCKED, STALE and COULD NOT ASK. COULD NOT ASK is not
rc 0. READY is intersected with the lane records and the open PRs. One batched GraphQL call is the
admitted step (SH7).

**CT-17.** **17-K1.** `lane:allocate` and a new `lane:ready` repair task.

- `lane:allocate` resolves the base to a commit once, adds the worktree at that commit and checks
  that HEAD equals it.
- It refuses the main checkout and unregistered paths.
- `lane:ready` is idempotent. It runs the explicit offline `deps:sync` and proves that
  `.venv/bin/python -I -c "import marketplace_dev"` works.
- The CT-02b launcher's refusal message names `lane:ready`.

Source: `worktree.py:461-497, 589-620`.

**CT-18.** **18-K1.** A09 refuses a push whose tree has no complete passing receipt line (11-K1).
"No checks" never counts as green (E4).

**CT-19.** **19-K1.** The SubagentStop hook mints the review receipt with each report's sha256,
instead of the reviewing model vouching for itself (`review.py`).

**CT-22b (wave 8)**

- **22b-K1.** Detectors run under a `sys.addaudithook` that blocks open-for-write, subprocess and
  socket events (`skillopt_contract.py:40-68`), which proves they never write. This adds to TR's
  `git status` and mtime row.
- **22b-K2.** Drift of `.codex/config.toml` from HEAD is a P2 finding, not rc 0 (SH7).
- **22b-K3.** A read-only disk detector covering free space against the D84 gate, the size of
  `uv cache dir`, and `docker system df` with a timeout.

**CT-26 (26a wave 1, 26b wave 2)**

- **26-K1. `tools:audit` statuses and rules.**
  - Statuses are OK, DRIFT, BLIND (could not tell) and UNKNOWN (a version that cannot be ordered).
    DRIFT or BLIND exits 1.
  - It reads `mise.dev.toml` and `mise.dev.lock`; a pin with no lock entry is DRIFT.
  - An offline "behind" check compares against a committed upstream baseline that carries
    `observed_at` and goes stale after 30 days. Only a separate receipted task refreshes it.
  - It detects an install directory or an outside-mise binary shadowing a shim, without executing
    it.
  - It honours `MISE_DATA_DIR` and `XDG_DATA_HOME`.
  - A test proves it makes no network call and starts no subprocess.
  - It never applies anything.

  Sources: `currency/sync.py:44-53, 213-249`; `baseline.py:170-235`. It takes the ideas and leaves
  out the 7,937 lines.
- **26-K2.** Each hk version token is its own audit row: the mise pin, both `amends` URI tokens, the
  `Builtins` import tokens when present, and `min_hk_version` (H2).
- **26b-K1. CI calls only named tasks, with SHA-pinned actions.**
  - CI jobs call only named mise tasks. Today `MP:.github/workflows/development.yml:18` runs
    `python3 -B dev/check.py` directly.
  - Actions are pinned by full SHA with a version comment (`docs-refresh.yml:24, 28`). MP uses tags
    today (`development.yml:15`; `acceptance.yml:14`). A check rejects tag pins.
  - CI runs the same gate set as pre-push.

  Fixes CI1.

**CT-52 (wave 8)**

- **52-K1. One jobs table, one native check.**
  - The generator config is one `[tool.datamodel-codegen]` jobs table, with the committed schemas
    as the source (D83).
  - It is checked with the generator's own `--all-jobs --check`, run as
    `uv run --no-sync --offline python -I -m <generator module>`. Whether that module entry exists
    is UNVERIFIED.
  - It never runs inside the unit test suite (`tests/test_codegen.py:20-40`).
- **52-K2. Temp-dir regeneration conflicts with ruff config discovery.** The CT-52 "regenerate into
  a temp dir" plan clashes with how ruff finds its config: it walks up from the output path
  (`pyproject.toml:323-331`). Either use the native `--check`, or pass an explicit ruff config with
  a control arm that shows the difference.
- **52-K3. Mutation rows.**
  - Removing `use-annotated` turns the check red (`pyproject.toml:355-379`).
  - A seeded one-byte drift exits 1.
  - A stale generated file that no job produces is caught by its provenance header.
  - A launch failure is reported apart from drift (`guard_codegen.py:20-24, 206-225, 287-316`).
- **52-K4.** ruff for the generated code sits in the same locked group, and a ruff bump starts a
  regeneration lane (`pyproject.toml:333-339`).
- **52-K5. Output choices are decided and recorded.**
  - The output model type is decided and recorded. If it is msgspec, set
    `runtime-evaluated-base-classes = ["msgspec.Struct"]`: KB measured that TC001 breaks decoding
    without it (`pyproject.toml:140-160`).
  - Use discriminated unions, not nullable siblings.
  - Missing versus null comes from the schema, not a hand-kept list (`source_groups.py:779-829`).
  - Each job gets its own docstring; the shared template stamps the wrong one today
    (`generated/research_record.py:12, 16`).
  - `target-python-version` equals `requires-python`. Generator support for 3.15 is UNVERIFIED.

**CT-49 and CT-50**

- **49-K1. Fixtures and controls per class.**
  - Each class has a bad fixture that reports its class id and a good fixture that does not.
  - A gated SKIP is never green.
  - The control fails for a constant detector.

  Fixes E1.
- **50-K1.** A mechanical finding's check may cite a mutation arm (row 49-K2).

**CT-57 (wave 18).** **57-K1.**

- Validate against a pinned local schema, never the `$schema` URL a manifest names.
- No allow-list for a missing `version`.
- Every verb the plugin's `SKILL.md` names must resolve from the pinned build.

Fixes E6 and R4.

**CT-07 and CT-10**

- **07-K1. Codex lanes.**
  - A malformed-role warning fails the lane (`codex_log.py:11-15`).
  - A process-group timeout returns 124 (`codex_run.py:140-235`).
  - `--dangerously-bypass-hook-trust` is never passed.
  - The lane's environment is built from an allow-list.

  Fixes R3.
- **10-K1.** Bind the reviewer model through `parent_thread_id` plus the review sub-agent source,
  keeping Unavailable distinct from Error (`codex_review_evidence.py:286-356`).

**Offline corpus and research tickets**

- **CT-36, 36-K1.** Measure fetch loss from source to output (R5).
  - Keep the status and minimum-body gate (`fetch.py:175-190`) and the scheme-restricted opener
    (`:472-476`).
  - https only, with a byte cap.
- **CT-41 and CT-47, 41-K1.**
  - Use three inventories: sitemap, llms.txt and navigation.
  - Retire a page after 3 misses over 7 days.
  - Reject off-site redirects (`docs_mirror.py:4-10, 390-419`).
  - Freshness can be UNKNOWN, a state distinct from stale (`:516-541`).
- **CT-44, 44-K1. One citation parser,** `marketplace_dev/citations.py`.
  - It is shared by CT-37's handoff check and by `offline:cite-verify`.
  - It is text in, data out (`citations.py:1-10`) and keeps KB's rules that err toward
    under-reporting.
  - The `(absent)` marker is checked in both directions (`:30-37`).
  - Corroboration counts deduplicate fork lineage (`ecosystem_discovery.py:461-560`).
- **CT-33, 33-K1.** Verify in staging, then publish atomically with rollback
  (`artifact_download.py:152-180, 256-290`). Keep a subprocess's stderr only as a digest
  (`source_groups.py:314-316`).
- **CT-46 and CT-48, 46-K1.**
  - A feed that cannot prove it is fresh is labelled unverified.
  - Running out of time budget gives NOT CHECKED (`models.py:291-299, 396-400`).
  - The registry is stored with its sha256.
  - No mutable overlay, and keyless only, with no OAuth token (R2).

**Mods and verify**

- **CT-31, 31-K1.** A typed-register assertion, plus `tsc` against version-pinned declarations.
  The declarations are generated by a probe mod run under an isolated HOME with credentials removed
  (`fnhook_gates.py:1-9, 334-351`; `mod_runtime.py:21-50`).
- **CT-32a, 32a-K1.** Verify receipts bind the exact HEAD, the input digests and a maximum age
  (from `live_receipt.py`). If signing is ever admitted, the signature is checked before the
  payload is parsed (CI3).

### Rows on sibling proposed tickets (no new tickets)

A first draft proposed three new tickets. Two of them duplicated tickets that the sibling report
`KB-A-knowledge-base-agent-surface.md` proposes in the same review round, and the third fits
CT-49, so all three come over as acceptance rows instead.

**KB-A-1 to KB-A-4: the plugin backend and its verbs.** These rows add to KB-A's tickets.

- **KA1-K1.** The rebuilt `trackers` fetches every page or reports the truncation, and it either
  searches discussions or drops the README's discussion-search claim (R4).
- **KA1-K2.** The record is a discriminated union keyed on `adapter`, from a committed schema
  (CT-52, D83). A null result needs a known-result control.
- **KA1-K3.** In the same change, remove the pipx line (`MP:plugins/aggregated-research/mise.toml:3`),
  the 1.3 GB README note and the plugin skill's raw `curl` routes
  (`MP:plugins/aggregated-research/skills/aggregated-research/SKILL.md:146`), per D59.
- **KA1-K4.** The placement question KB-A-1 already raises (a plugin-local runtime package, or the
  helper-process bridge of `MP:docs/agents/python-bridge-placement.md:3-9`) stays the user's call,
  because D60 covers dev Python only.

**KB-A-7: `recall:work`.** **KA7-K1.** The output is validated against a committed schema (KB has
`schemas/recall-work.schema.json`; D83). Offline probes run by default. GitHub and sibling-repo
probes are admitted operations, never defaults; that fixes `recall_work.py:93, 962, 1055`, which by
default reads sibling repos, `~/.claude/plans` and gh.

**CT-49: mutation arms.** **49-K2.** A mutation-arm runner in `marketplace_dev/arms/` provides the
revert-patch proof that DF-B's CT-49 row asks for.

- A TOML spec runs a no-op control first, then baseline and restored rows.
- It runs in a detached scratch worktree, never the live tree.
- It restores byte-exact and matches exact test ids.
- CT-50 findings can cite an arm.

This fixes E2 in `arms.py`. It is blocked by CT-39 and CT-17 and needs no admission.

### A decision to bring to the user

DF pins `kb-setup` for five engines: evals, md_budget, currency, the `cc` launcher and the graph
receipt. `marketplace_dev` is not exported (39-K7), so DF should drop that dependency rather than
repoint it at MP.

- Four of the five are agent-workflow tooling that D87 moves here: evals (via CT-49), md_budget
  (via CT-38a and CT-58), the launcher (via CT-35 and CT-37) and the graph receipt (graphify, not
  imported).
- Host-tool currency for DF's own tools is host setup, so it needs a DF-local replacement. That is
  a dotfiles backlog item, not an MP ticket.

## 4. Not imported

| What | Why |
| --- | --- |
| Graphify substrate: 24 modules, 16,375 lines (`graph*.py`, `graphify_*.py`, `prose`, `lexical`, `fusion`, `chunks`, `insights`, `hyperedges`, `edge_direction`, `extract_census`, `artifacts`, `_merge_docs`, `funnel`, `code_intel`'s merge half); the graphify parts of `currency/`; `stamps`, `build_outcome`, `skill_refresh`, `graph_first`, `eval_cases` | Graphify-specific. A graph tool, if any, is CT-55's adopt-or-drop spike. |
| `memory_serve`, `remember`, `recall`, `brain`, `mcp_serve`, `mcp_probe` | A graphify memory store behind a long-lived MCP server. Registering a daemon needs explicit instruction, and MP has no MCP servers. KB-A-7 (with KA7-K1) covers recall offline. |
| `launch.py` (`cc`, `cc-doctor`, `cc-fresh`) | Graphify version pin, hard-coded `--permission-mode auto`, a hard-coded sibling repo and `tmux kill-server`. CT-35 and CT-37 own session start. |
| `goal.py` | Native goals wait for explicit instruction. |
| `models.py`, `models_apply.py`, `model_limits.py` | A mutable overlay, an OAuth-token route and regex rewriting of tracked files. Only the rules in 46-K1 come over. |
| `skillopt_*`, `ecosystem_discovery` code | Specific to SkillOpt and graphify. 22b-K1 and 44-K1 take their good ideas. |
| `mod_runtime`, `ccdocs_mirror`, `artifact_download` code, `settings_guard`, `guard_codegen`'s TS half, `generated_packages_prototype` | Dead, a shim, unwired or a prototype (D59). |
| `reclaim.py`, `reclaim.toml` | macOS-only, deletes in one pass with no reviewed plan, and has no uv category. D80's container work ran as admitted operations; `uv cache prune` is a one-line admitted operation. |
| `tool_sync.py` | Installs into global mise. MP keeps tool data inside the checkout (`MP:dev/bootstrap.py:65-77`). |
| `lock_drift.py` | `MP:dev/bootstrap.py:30-62` is already stricter and offline. |
| `workflow_lint.py` | MP has no `.claude/workflows`. |
| `lint_checks.py` | A substring grep; 39-K6 uses ruff and ty natively. |
| `skill_eval.py` | A third-party scorer plus a host plugin path. Native `claude plugin eval` likely supersedes it; check before relying on that. |
| `hk_test.py` | MP's hk config has no builtin steps, so `hk test` would run 0 tests; 39-K5 covers the intent. |
| `events.py`, `sinks.py` (structlog), `atomic.py` | CT-39 wants a stdlib core. `marketplace_dev.receipts` replaces `atomic`, which has no fsync and a pid-only temp name. |
| `pr.py` land, the merge path | MP never merges (`MP:docs/agents/claude-takeover.md:11`). A09 already does more than `ship`. |
| `absent_binary`, `inplace_edit`, the `check_first` and `codex_lane` redirect tables, `instruction_edit_guard`, `instruction_shell_write` | Host- or KB-specific, ten hook registrations, and a conflict with MP's heredoc report workflow (D49). The classifier table replaces them. |
| `edit_check.py` | A Codex PostToolUse hook. AGENTS.md says not to copy Claude hooks into Codex config, and Codex is paused until 2026-10-19. |
| `write_attribution.py`, the `agentsview` wrapper, `session_review_archive`'s three legacy input shapes | Transcript reads without admission, a sync that writes host state, and dual input paths. CT-20 owns transcripts. |
| `codex_config.py` as code | It is a single finding (22b-K2). |
| `cli.py` dispatcher, both console scripts, `kb-*` task naming | D60. |
| Runtime deps `graphifyy`, `anthropic`, the SkillOpt VCS pin, `httpx2`, `structlog`, `mcp2cli`, `trafilatura` | Not needed for MP's dev package. `msgspec` only if CT-52 chooses it. |
| `[deps.uv] auto = true`, `auto_install = true`, a project `disable_tools` copy, the inert `min_version.soft`, `default-groups` as a race fix | Implicit host mutation and workarounds (P2, P3, M3). |
| `docs-refresh.yml` as written | A resolution outside the lock and a self-confirming check (CI2). CT-47 owns staleness. |
| `graphify-live-receipt.yml` and `live_receipt*.py` | MP gates nothing through PRs, and signing needs a key admission. 32a-K1 takes the HEAD binding and the maximum age. |
| `currency.toml` (2,268 lines), `models-sites.toml`, `doctor.toml` | Graphify and model-registry data. 26-K1 uses a small baseline file. |

## 5. Sunset checklist

ADR 0006 retires KB only after every item here has a landed ticket. Work through it in order.
Archive the repository rather than delete it unless the user says otherwise.

**First, cut the external consumers. Nothing in KB can go while any of these remain.**

1. MP plugin:
   - `plugins/aggregated-research/mise.toml:3` (the pipx pin), `README.md:55-62` and the skill's
     raw routes go away when KB-A-1 lands (with KA1-K3).
   - `docs/agents/legacy-trackers-boundary.md`, `python-bridge-placement.md` and
     `evidence/legacy-trackers/` stay as history.
2. DF:
   - `python/pyproject.toml:40`, plus the `override-dependencies` entry at `:60-67` that exists
     because of it.
   - `python/src/dotfiles_setup/main.py:16`, `eval_cases.py:35, 358-377`, `listing_budget.py:42`,
     `doctor.py:159`, `graphify.py:32`.
   - `mise.toml:687, 696, 1588` and `hk.pkl:698`.
   - The five `suites.toml` contracts (`:1412, 1432, 1467, 2306-2346, 2696`).
   - `.agents/skills/tool-currency-check/SKILL.md:43-44` and `research-sweep/SKILL.md:16-19`.

   This is DF's own work; see the decision in section 3.
3. Sessions:
   - KB `.mcp.json` `kb` and `kb-memory`, and KB `.codex/config.toml` `[mcp_servers.kb-memory]`.
   - The running `serve-memory` process is the user's to stop. No agent touches it.

**Then delete each KB path once its MP owner has landed:**

| KB path | MP owner that must land first |
| --- | --- |
| `ks/research/**` and the `aggregated-research` script | KB-A-1 to KB-A-4 |
| `ks/skill_lint.py`, `hook_guard.py`, `check_first.py`, `destructive_git.py`, `stage_explicitly.py`, `secret_guard.py`, `lane_recording.py` | CT-38a and CT-02b |
| `ks/md_budget.py` | CT-38a and CT-58 (and DF step 2) |
| `ks/handoff.py`, `handoff_reconcile.py`, `citations.py`, `resolve.py`, `context_usage.py`, `session_state.py`, `env_refresh.py` | CT-29, CT-37 and CT-44 |
| `ks/session_reflect.py`, `session_select.py`, `distill.py` | CT-20a |
| `ks/gates.py`, `check.py`, `result.py` | CT-11 and CT-39 |
| `ks/evals.py` | CT-49 (and DF step 2) |
| `ks/arms.py` | CT-49 (49-K2) |
| `ks/recall_work.py` | KB-A-7 |
| `ks/next_ticket.py` | CT-25 |
| `ks/worktree.py` | CT-17 |
| `ks/currency/**` | CT-26a, and DF's local replacement for host-tool currency |
| `ks/codex_run.py`, `codex_log.py`, `codex_review_evidence.py` | CT-07 and CT-10 |
| `ks/fetch.py`, `docs_mirror.py` | CT-36, CT-41 and CT-47 |
| `ks/fnhook_gates.py`, `claude_types.py` | CT-31 |
| `ks/plugin_validate.py` | CT-57 |
| `[tool.datamodel-codegen]`, `generated/**`, `schemas/*.schema.json` | CT-52 |
| `tests/conftest.py` fixtures | CT-39 (39-K4) |
| Everything listed in section 4 | Deletable as soon as step 1 is done |

**Last, the repository itself.** `pyproject.toml`, `uv.lock`, `mise.toml`, `mise.lock`, `hk.pkl`,
`.github/workflows/*`, `.claude/settings.json` and `.codex/hooks.json` go once the hooks they wire
have no consumer. After that, reclaiming `.venv` (727 MB) and `.agent` (232 MB) is a separately
admitted disk operation. The corpus directories follow the corpus reviewers' checklists.

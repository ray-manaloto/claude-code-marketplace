# X2: dependency update review (2026-10-13)

Read-only. Sources: `gh api repos/<o>/<r>/releases`, compare/commits endpoints, PyPI JSON,
formulae.brew.sh, local `--version` / `./dev/mise ls --current`. No install, lock or check was
run. The only command that executed project code was `hk validate`, which reported hk.pkl valid.

## 1. Version table

| Tool | Pinned / locked (file:line) | Installed | Latest (date) | Delta | Risk | Rec. |
|---|---|---|---|---|---|---|
| mise | `mise.dev.toml:3` min 2026.10.8; CI `.github/workflows/research-fast.yml:25` 2026.10.8; `jdx/mise-action@v4.3.0` (:23) | 2026.10.9 | [v2026.10.9](https://github.com/jdx/mise/releases/tag/v2026.10.9) (10-13); action [v5.1.2](https://github.com/jdx/mise-action/releases) (10-12) | 1 patch release; action is one major behind | Low | **Upgrade, with ticket (CT-26)** |
| fnox | global `~/.config/mise/config.toml:121` 1.39.0 | 1.39.0 | [v1.39.0](https://github.com/jdx/fnox/releases/tag/v1.39.0) (10-06) | none | – | Hold (already current) |
| hk | `hk.pkl:1` amends v2.5.0, `:6` min 2.5.0; binary pinned only globally (`config.toml:120` 2.6.0); **not in mise.dev.toml** | 2.6.0 | [v2.6.0](https://github.com/jdx/hk/releases/tag/v2.6.0) (10-12) | schema 1 minor behind | Low | **With ticket (CT-26, part B, needs a decision)** |
| uv (dev) | `mise.dev.toml:7`, `mise.dev.lock:26` 0.13.0 | 0.13.0 via `./dev/mise` | [0.13.0](https://github.com/astral-sh/uv/releases/tag/0.13.0) (10-09) | none | – | Hold |
| uv (OCI) | `mise.toml:13`, `mise.lock:141` 0.12.7 (**frozen baseline**) | 0.12.7 on the plain shell PATH in the repo | 0.13.0 | 1 minor | Baseline transition | Hold |
| ruff | none (no project consumer; not in any check) | shim, no version set | [0.17.0](https://github.com/astral-sh/ruff/releases/tag/0.17.0) (10-09) | n/a | – | Hold (no consumer) |
| ty | `plugins/aggregated-research/mise.toml:4` 0.0.74 (**frozen baseline**; `ci/acceptance.sh:251` expects it) | shim, no version set | [0.0.87](https://github.com/astral-sh/ty/releases/tag/0.0.87) (10-13) | 13 pre-1.0 releases | High: plugin runtime + acceptance | Hold (baseline transition + admitted acceptance only) |
| python (checks) | `mise.dev.toml:6` 3.15.0; `mise.dev.lock:6-22` (python-build-standalone 20261009); `pyproject.toml:4` `>=3.11,<3.16` | `python3` → `.venv/bin/python3` 3.15.0 | 3.15.0; [PBS 20261013](https://github.com/astral-sh/python-build-standalone/releases/tag/20261013) rebuild | rebuild of the same version only | – | Hold |
| githubkit / pydantic | `pyproject.toml:5` githubkit 0.16.1; `uv.lock:61,261` | locked | 0.16.1; pydantic 2.14.1 (PyPI) | none | – | Hold |
| node / gh / jq / claude-code (OCI) | `mise.toml:10-14` (frozen) | 26.8.1 / 2.98.0 / 1.8.2 (activated in the repo shell) | node 26.11.1, gh 2.102.0, claude-code 2.1.299 | behind | Baseline transition | Hold |
| P2996 LLVM fork | `docs/accepted-decisions.md:86` f17c8d6c… (LLVM 21.0) | evidence `evidence/p2996-registration/` | `p2996` branch head = f17c8d6c (compare: identical; last push 09-24) | none | – | Hold |
| GCC lane | `dev/toolchains/gcc_bottles.py:14` 16.2.0; `gcc_reflection.py:81,96` | Homebrew Cellar 16.2.0 | Homebrew stable 16.2.0; gcc.gnu.org newest 16.2 | none | – | Hold |
| IWYU (fork) | `dev/toolchains/iwyu_source.py:12` 791e69ea (clang_21) | built per evidence | `clang_21` head = 791e69ea (2025-08-30) | none; matches fork LLVM 21 | – | Hold |
| Upstream LLVM (L1) | none yet (#96 resolves) | Homebrew `llvm` 23.1.3 = global CC (`config.toml:91`) | [llvmorg-23.1.3](https://github.com/llvm/llvm-project/releases/tag/llvmorg-23.1.3) (10-06) | n/a | – | Feed L1 as the candidate |
| IWYU (L2) | none yet (#99) | – | [0.27](https://github.com/include-what-you-use/include-what-you-use/releases/tag/0.27) (10-05, "Compatible with Clang 23"); `clang_23` head c9cbc836 (10-04) | n/a | – | Feed L2 as the candidate |
| CMake | `dev/global-mise/cpp-foundation/common.toml:5` 4.4.4 (+ 3 `mise.*.lock:6`) | 4.4.4 (`MISE_ENV=cpp-build`) | [v4.4.4](https://github.com/Kitware/CMake/releases/tag/v4.4.4) (10-02) | none | – | Hold |
| Ninja | `common.toml:6` 1.13.2 | 1.13.2 | [v1.13.2](https://github.com/ninja-build/ninja/releases/tag/v1.13.2) (2025-11-20) | none | – | Hold |
| sccache | `common.toml:7` 0.18.0 | 0.18.0 | [v0.18.0](https://github.com/mozilla/sccache/releases/tag/v0.18.0) (09-14) | none | – | Hold |
| vcpkg | `vcpkg.json:4` e4563094… | – | master head = e4563094 (10-10); tool tag at that commit 2026-09-26 = latest vcpkg-tool | none | – | Hold |
| cmake/ninja in `mise.dev.toml` | **absent** | – | – | – | – | See CT-27 note |

Every C++ identity in `docs/accepted-decisions.md:86` is still the newest upstream identity. Nothing
on the reflection or GCC lanes needs a refresh.

## 2. Recommended upgrades

### 2a. mise 2026.10.8 → 2026.10.9 (project floor and CI), mise-action v4.3.0 → v5.1.2

Changelog items that matter here:
- 10.9 Security: `path:` tool versions now require trust; download file names decoded from URLs
  can no longer escape the download directory. Fixed: `mise exec`/shim downloads now retry up to
  `http_retries`; `mise oci build` no longer runs the host's apt hooks against the image (our OCI
  build installs `build-essential` through `[bootstrap.packages]`); `mise prune` keeps
  versions used only by inline task `tools`.
- 10.8: the JSON schema accepts `outputs = { auto = false }`, and HTTP body drops are retried.
- Already inside the 10.8 floor, still relevant: 10.5 makes `mise.local.toml` override
  `mise.<env>.toml`, and experimental features now need `experimental = true`
  (`mise.dev.toml:10` already sets it). It also makes `git::`/`oci::` entries in
  `task_config.includes` experimental and skipped with a warning. For D7, only local-path
  includes (`mise/tasks/<unit>.toml`) are safe; no 10.x release changes `usage` arg parsing.
- 10.4 (relevant to fnox): experimental `[secrets.fnox]` plus task `secrets = [...]` grants
  (needs fnox ≥ 1.39.0, refused in safe mode). This is a native route for the research tasks'
  `fnox … exec` wrapper. It is out of scope for CT-26 and needs its own decision.
- mise-action v5 breaking change: `minimum_release_age` defaults to 24h, but an explicit `version`
  input skips the delay. Our step pins `version`, so pinning behaviour does not change. The
  action now reads releases from a CDN index rather than paging the GitHub Releases API.

Files: `mise.dev.toml:3` (project) and `.github/workflows/research-fast.yml:23,25` (project, not
baseline). No global file changes. The OCI image and the frozen baseline are unaffected. Without
this bump, local receipts run on 10.9 while CI runs on 10.8, so the two do not compare.

Verify: `./dev/mise tasks validate`; `./dev/mise run check`;
`./dev/mise run check:acceptance-baseline`; `./dev/mise run test:hooks`; `./dev/mise run
check:research`; `./dev/mise run test:bootstrap`. After publication, check that one research-fast
CI run is green on the new pin and record its run ID.

### 2b. hk: declare 2.6.0 in the project, bump the hk.pkl schema

hk 2.6.0 changes that matter here:
- `hk agent stop-hook` no longer blocks in projects without hk.
- Pkl loading moved to pklr v5, so some config errors are worded differently.
- Passing runs now end with a success line when step output is shown.
- Breaking only for `Builtins.ryl`, which we do not use.

Our hooks are `pre-merge-commit`/`pre-push` with `stash = "none"`, so safe-set behaviour does not
change.

The real gap is portability. `hooks:install` (`mise.dev.toml`) and `dev/test_hooks.py:17`
(`shutil.which("hk")`, otherwise the test is skipped) use whatever hk the global PATH provides. That
contradicts `docs/accepted-decisions.md` ("must build without relying on user/global mise
configuration"). On CI the HkHooks tests are probably skipped silently.

Files (all project-scoped):
- `mise.dev.toml` `[tools]` (add `hk = "2.6.0"`)
- `mise.dev.lock` (regenerated through `./dev/mise run deps:lock`)
- `dev/bootstrap.py:22` `TOOL_BACKENDS` (add the hk backend), plus its tool-drift test
- `hk.pkl:1` (amends `v2.6.0`) and `hk.pkl:6` (`min_hk_version = "2.6.0"`)

Verify: `hk validate`; `./dev/mise exec -- hk --version`; `./dev/mise run tools:prepare` and
`deps:check`; `./dev/mise run test:bootstrap`; `test:hooks` with the HkHooks tests not skipped;
then the three named checks. CI then installs hk in research-fast, which is a scope decision
(see 3, AC5). The baseline and OCI image are unaffected.

### 2c. Holds that need a baseline transition (not CT-26)

These pins all sit in frozen baseline files: OCI uv 0.12.7, node, gh, claude-code (`mise.toml`,
`mise.lock`), and plugin ty 0.0.74 (`plugins/aggregated-research/mise.toml`, coupled to
`ci/acceptance.sh:251`). Per `docs/accepted-decisions.md`, they move only through a versioned
baseline transition with an admitted container/acceptance run.

Gotcha found: the global mise activation (`trusted_config_paths = ["/"]`) loads the root OCI
`mise.toml` in an interactive shell at the repo root. Bare `uv` in the repo is therefore 0.12.7,
`gh` is 2.98.0 and `node` is 26.8.1, while `./dev/mise exec -- uv` is 0.13.0. Agents must use
`./dev/mise exec`/tasks. A bare-tool receipt in this checkout records OCI pins, not dev pins.

## 3. Tickets

### CT-26 Tooling refresh

**Title:** Align the mise floor/CI pin to 2026.10.9 and make hk a locked project tool

**What to build:**
- (A) Raise `min_version` and the research-fast `mise-action` `version` to 2026.10.9, and move
  the action to v5.1.2 with the explicit version kept.
- (B) Declare hk 2.6.0 in `mise.dev.toml` and lock it through `deps:lock`. Teach
  `dev/bootstrap.py` the backend, and bump `hk.pkl` amends/min to 2.6.0, so `hooks:install` and
  `test:hooks` stop depending on global hk.
- B is separable: if the user declines B, ship A alone.

**Acceptance criteria:**
1. `./dev/mise tasks validate`, `run check`, `run check:acceptance-baseline`, `run check:research`
   and `run test:bootstrap` exit 0 from one worktree. Actual exit codes are recorded.
2. `hk validate` exits 0. `./dev/mise exec -- hk --version` prints 2.6.0 under `dev/mise` with the
   global config excluded. `test:hooks` reports the HkHooks cases as run, not skipped.
3. `mise.dev.lock` changes only by the hk entry. The `deps:check` drift control still refuses a
   tampered python/uv binding.
4. Frozen baseline, `mise.toml`, `mise.lock` and the plugin `mise.toml` are byte-identical, per
   `check:acceptance-baseline`.
5. Decision row recorded before B: hk is installed in CI research-fast (yes/no).
6. One research-fast CI run on the published tip passes; its run ID is recorded at publication
   (A09), not before.
7. The ticket ends at the retro gate.

**Blocked by:** w0-doctor integration (it owns `hk.pkl` pre-commit step and `mise.dev.toml`
doctor rows). Not blocked by w0-doctor-records or w0-session-hooks.

**owned_paths:**
- `mise.dev.toml` (lines 1–11 only: header, `min_version`, `[tools]`, `[settings]`; no task rows)
- `mise.dev.lock`
- `dev/bootstrap.py` (`TOOL_BACKENDS` and its drift test only)
- `hk.pkl` (lines 1 and 6 only)
- `.github/workflows/research-fast.yml` (mise-action step only)
- `.planning/<PLAN_ID>/retros/ct26-tooling-refresh.md`
- `.planning/<PLAN_ID>/ledger-ct26-tooling-refresh.jsonl`

These are disjoint from w0-doctor-records (`dev/doctor/lanes.py`, `agents.py`, fixtures) and
w0-session-hooks (`mise.dev.toml` `test:hooks-session` row and `check:research` depends entry,
`dev/test_hooks.py` inventory test, `.claude/settings.json` entries). CT-21 owns only one
`development.yml` step, so there is no overlap there either.

**Excluded:** global `~/.config/mise/*` (fnox/hk/uv global pins need their own admission),
the OCI/plugin baseline files and `ci/acceptance.sh`.

### CT-27 C++ toolchain refresh: do not file

No C++ identity is stale. The P2996 fork, IWYU `clang_21`, GCC 16.2.0, CMake 4.4.4, Ninja
1.13.2, sccache 0.18.0 and vcpkg e4563094 (tool 2026-09-26) are all upstream-current. The
upstream LLVM/IWYU refresh is already the L1–L6 chain: #96 resolves the candidate, #99 resolves
IWYU, and #107 (L5b) is the recurring updater. A separate ticket would duplicate L5b's single pin
writer.

Instead, add this candidate-evidence comment to #96/#99:

> Candidate as of 2026-10-13: llvmorg-23.1.3 (published 2026-10-06; Homebrew `llvm` 23.1.3 is
> the current global CC, a mutable formula that cannot pass alone); IWYU 0.27 (2026-10-05,
> "Compatible with Clang 23") or `clang_23` head c9cbc836. Re-resolve at L1 start.

Open gap for the B1/T-graph owner (not a refresh): CMake/Ninja/sccache are declared only in the
global `cpp-foundation/common.toml`, not in `mise.dev.toml`. That contradicts the decision that
portable project declarations supersede global profiles. If no existing ticket owns it, file it
as a separate portability ticket blocked by L3 (#100).

## 4. Could not verify

- Whether research-fast CI currently skips the HkHooks tests (no CI log read).
- Whether `./dev/mise tasks validate` / `check` pass on mise 2026.10.9. Not run, per the
  read-only brief and the single-worktree check rule.
- hk 2.6.0 `aqua:jdx/hk` lock coverage for linux-x64/arm64 (no `mise lock` run). The registry
  pins hk to its signing workflow (mise 10.5 note); the provenance format is unverified.
- GCC: no gcc.gnu.org 16.3 announcement was found. The GCC lane's Homebrew bottle revision and
  patches were not re-attested.
- The IWYU 0.27 tag commit, and whether it equals the `clang_23` head.
- mise releases before 10.2 were not reviewed for `usage` changes. For D7 specifically,
  `task_config.includes` with local paths was not exercised. That is the D7 spike's job.
- The research tasks' fnox daemon socket path change (1.39.0) and its effect on the
  `codex_research` profile. The installed fnox is already 1.39.0, so any effect is already live.

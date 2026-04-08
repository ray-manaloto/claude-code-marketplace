---
name: mise-contrib-overview
description: Orientation for contributing to the jdx/mise Rust codebase — repo layout, build/test/lint commands, conventional-commit scopes, the hk pre-commit setup, and the rule that e2e tests must run via `mise run test:e2e` (never directly). Use whenever the user is working in the jdx/mise repo itself.
---

# Contributing to jdx/mise

mise is a Rust CLI built with cargo. The repo's own `mise.toml` declares the toolchain and tasks.

## Repo layout

```
jdx/mise/
├── src/
│   ├── main.rs                  # entry point
│   ├── cli/                     # subcommands (~50 files, one per command)
│   ├── config/                  # mise.toml parsing, hierarchy, settings
│   ├── backend/                 # 15 backends + helpers
│   ├── plugins/core/            # 13 built-in language tools
│   ├── toolset/                 # version resolution, install state
│   ├── task/                    # task definition + execution
│   └── ...
├── crates/vfox/                 # vendored vfox crate (workspace member)
├── e2e/                         # bash e2e tests, no extension, not chmod +x
├── e2e-win/                     # Windows-specific e2e
├── docs/                        # vitepress site for mise.jdx.dev
├── registry/                    # tool short-name → backend mappings
├── settings.toml                # canonical setting definitions (drives codegen)
├── mise.toml                    # the repo's own toolchain + tasks
└── tasks.toml                   # additional task definitions
```

## Build / test / lint commands

These are all defined in the repo's `mise.toml` / `tasks.toml`:

| Command | Purpose |
|---|---|
| `mise run build` (or `mise run b`) | `cargo build`, output at `target/debug/mise` |
| `mise run test` (or `mise run t`) | unit tests + e2e tests |
| `mise run test:unit` | unit tests only |
| `mise run test:e2e [path...]` | e2e tests (specific files or full suite) |
| `mise run lint` | all lint checks |
| `mise run lint-fix` | autofix what's autofixable |
| `mise run format` | format code |
| `mise run ci` | format + build + test (matches CI) |
| `mise run snapshots` | review/accept `cargo insta` snapshot updates |
| `mise run render` | regenerate docs, completions, mangen, JSON schema |
| `mise run install-dev` | install your local build to PATH |
| `mise --cd crates/vfox run test` | run tests in the vfox crate |
| `mise --cd crates/vfox run lint-fix` | lint-fix the vfox crate |

## Hard rules (from the repo's `CLAUDE.md`)

1. **Never run e2e files directly.** Always `mise run test:e2e <path>`. The harness sets up isolated `MISE_DATA_DIR` per test and tears it down. The mise-toolkit plugin's `block-direct-e2e.sh` hook enforces this.
2. **Never `chmod +x` e2e tests.** They're not executable; the harness invokes bash on them.
3. **Use `MISE_DEBUG=1` / `MISE_TRACE=1`** for debug output. **Not** `RUST_LOG`.
4. **`hk install --mise`** sets up the pre-commit hook (runs `hk fix` on commit). Do this once per clone.
5. **Run `mise run lint-fix` and `git add` the fixes** before committing.
6. **Don't `chmod +x` e2e files** — already said this. It's important.

## Conventional commits (REQUIRED)

Format: `<type>(<scope>): <description>` — lowercase after the colon, imperative mood.

### Types

- `feat:` — new features
- `fix:` — bug fixes that affect CLI behavior (not CI/docs/infra)
- `refactor:` — code refactor
- `docs:` — docs changes
- `style:` — formatting (no logic)
- `perf:` — performance
- `test:` — tests
- `chore:` — maintenance, releases, deps, CI
- `security:` — security
- `registry:` — anything in `registry/` (no scope; same for new tools and fixes)

### Scopes

- Subcommands: `install`, `activate`, `use`, `exec`, `run`, etc.
- Subsystems: `config`, `backend`, `env`, `task` (note: `task`, not `run`, even though the code lives in `src/cli/run.rs`), `vfox`, `python`, `github`, `release`, `completions`, `http`, `schema`, `doctor`, `shim`, `core`, `deps`, `ci`

### Examples

- `fix(install): resolve version mismatch for previously installed tools`
- `feat(activate): add fish shell support`
- `feat(vfox): add semver Lua module for version sorting`
- `feat(env): add environment caching with module cacheability support`
- `chore(ci): add FORGEJO_TOKEN for API authentication`
- `registry: add miller`
- `docs(contributing): update hk usages`
- `chore: release 2026.1.6`

## Where the e2e harness lives

- `e2e/run_test.sh` — the harness (read it if you're confused about isolation)
- `e2e/assert.sh` — assertion helpers (`assert`, `assert_contains`, `assert_fail`, `assert_eq`, `assert_empty`, `assert_matches`)
- `e2e/<area>/test_<name>` — individual tests, no extension, not chmod +x

## Settings codegen

Adding a new mise setting requires editing `settings.toml` (the canonical definition file) and running `mise run render:schema` to regenerate the JSON schema. Then add the runtime handling in `src/config/settings.rs` (or wherever the existing similar setting lives).

## Cross-platform

- Windows-specific impls live in files ending `_windows.rs` (e.g., `ruby_windows.rs`).
- The shim system varies significantly on Windows (`windows_shim_mode`: exe / hardlink / symlink).
- Test on Linux + macOS minimum; Windows tests live in `e2e-win/`.

## See also

- `mise-contrib-add-backend` — adding a new backend
- `mise-contrib-add-registry` — registry entries (90% case for new tools)
- `mise-contrib-write-e2e-test` — e2e bash conventions
- `mise-backend-expert` agent — implements/reviews backend code
- `mise-e2e-author` agent — writes e2e tests
- repo `CLAUDE.md`

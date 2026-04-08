---
name: mise-tasks-toml
description: Writing mise tasks in TOML — fields, dependencies, parallelism, sources/outputs caching, env scoping, hooks via tasks, output modes, and the difference between TOML tasks and file tasks. Use when creating, editing, debugging, or converting scripts to mise tasks.
---

# `[tasks]` in `mise.toml`

## Anatomy

```toml
[tasks.test]
description = "Run unit tests"
run = "cargo test"
# OR an array (runs sequentially)
# run = ["cargo build", "cargo test"]

depends = ["build"]                       # finish these first (parallel where possible)
depends_post = ["coverage-report"]        # run after, even on failure
wait_for = ["docker-up"]                  # wait but don't fail if missing

sources = ["src/**/*.rs", "Cargo.toml"]   # cache key
outputs = ["target/debug/myapp"]          # cache artifacts; skip task if neither changed

dir = "{{config_root}}"                   # cwd for the task
env = { RUST_LOG = "debug" }              # task-scoped env (merged with [env])

hide = false                              # hide from `mise tasks ls`
quiet = false                             # suppress mise's own command echo
silent = false                            # also suppress task output
raw = false                               # see "output modes" below
interactive = false                       # for tasks that read stdin

usage = '''
arg "<file>"
flag "-r --release" help="Build in release mode"
'''
```

## TOML tasks vs file tasks

| TOML task | File task |
|---|---|
| One-line or short commands | Multi-line shell logic with syntax highlighting |
| Lives in `mise.toml` | Lives in `mise-tasks/<name>` (no extension) |
| Configured via TOML keys | Configured via `#MISE` and `#USAGE` comments |
| Best for project-core tasks | Best for reusable scripts you'd lint with shellcheck |

File task example:

```bash
#!/usr/bin/env bash
#MISE description="Build the CLI"
#MISE depends=["install-deps"]
#MISE sources=["src/**/*.rs", "Cargo.toml"]
#MISE outputs=["target/debug/myapp"]
#USAGE arg "<target>"
#USAGE flag "-r --release" help="Build in release mode"
set -euo pipefail
cargo build ${usage_release:+--release} --bin "$usage_target"
```

**Do not chmod +x** — mise handles execution.

## Running tasks

```sh
mise run test                         # run by name
mise run test build                   # run multiple in sequence
mise run test --watch                 # re-run on file changes (also: mise watch)
mise run test -- --verbose            # pass args after --
mise tasks ls                         # list all tasks
mise tasks info test                  # show full task config
mise tasks deps                       # show task dependency graph
```

## Dependencies, parallelism, ordering

- **`depends`** — must complete before this task. mise runs them in parallel where possible (no inter-dep).
- **`depends_post`** — runs after this task (success or failure). Useful for cleanup/teardown.
- **`wait_for`** — wait but don't fail if missing. Useful for optional setup tasks.
- **`run` array** — sequential, NOT parallel. For parallel work, split into separate tasks linked via `depends`.

mise's task scheduler computes a DAG and runs siblings in parallel. The default `--jobs` is `4`; override per-run with `mise run --jobs 8 test`.

## `sources` and `outputs` (incremental builds)

If both are set, mise compares mtimes:

- All `sources` files older than all `outputs` files → **skip the task**.
- Otherwise → run it.

```toml
[tasks.compile]
sources = ["src/**/*.ts", "tsconfig.json", "package.json"]
outputs = ["dist/**/*.js"]
run = "tsc"
```

Don't set one without the other unless you intend "always run if any source touched" (sources only) or "always run if any output missing" (outputs only).

## Output modes (`task.output` setting or `MISE_TASK_OUTPUT`)

| Mode | What you see |
|---|---|
| `replacing` (default) | Progress spinner; final state visible |
| `prefix` | Each line prefixed with `[task-name]` — best for CI logs |
| `interleave` | Raw output, interleaved with parallel tasks |
| `keep-order` | Buffered to avoid interleaving |

```toml
[settings]
task.output = "prefix"
```

`raw = true` on a task **bypasses** mise's output capture entirely (stdout/stderr go straight to the terminal). **This disables redactions**, so don't use `raw` for tasks that touch secret env vars.

## Env scoping

```toml
[env]
NODE_ENV = "development"

[tasks.test]
env = { NODE_ENV = "test" }   # overrides [env] for this task only
run = "vitest"
```

The merge rule: task `env` is layered on top of `[env]`. Task wins per-key.

You can also load a task-specific env file:

```toml
[tasks.deploy]
env = { _.file = "deploy.env" }
run = "./deploy.sh"
```

## Hooks via tasks

Hooks (`enter`, `cd`, `postinstall`, etc.) can reference tasks instead of inline scripts:

```toml
[tasks.setup]
run = "echo setting up"
depends = ["install-deps"]

[hooks]
enter = { task = "setup" }
```

This reuses the full task system — deps, sources, env, file tasks. You can also mix inline and task hooks in arrays:

```toml
[hooks]
enter = ["echo entering project", { task = "setup" }]
```

## Watch files

```toml
[[watch_files]]
patterns = ["src/**/*.rs"]
run = "cargo fmt"

[[watch_files]]
patterns = ["uv.lock"]
task = "sync-deps"
```

Watches require `mise activate` to be running in your shell. Each entry should have either `run` or `task`, not both. The task receives `MISE_WATCH_FILES_MODIFIED` (colon-separated, backslash-escaped).

## Built-in env vars passed to tasks

| Var | Meaning |
|---|---|
| `MISE_ORIGINAL_CWD` | Where the user invoked the task from |
| `MISE_CONFIG_ROOT` | Project root (where `mise.toml` lives) |
| `MISE_PROJECT_ROOT` | Same, more semantically named |
| `MISE_TASK_NAME` | The task name being run |
| `MISE_TASK_DIR` | The directory of the task script (file tasks) |
| `MISE_TASK_FILE` | Full path to the task script (file tasks) |

## Common pitfalls

- **`run` array is sequential, not parallel.** Split into separate tasks if you want parallelism.
- **`sources`/`outputs` mtime comparison is whole-set vs whole-set.** Touching one source re-runs even if its output didn't depend on that file.
- **`raw = true` disables redactions.** Don't use it for secret-handling tasks.
- **`mise build` shorthand** only works if there's no name collision with a mise CLI command. `mise run build` is always safe.
- **Task hooks won't run for file tasks invoked outside mise.** They're a feature of `mise run`, not the script itself.

## See also

- `mise-task-author` agent — converts npm scripts/Makefiles to tasks
- `mise-env-directives` — `_.file`, `_.path`, `_.source` work in task `env` too
- `mise-overview`
- <https://mise.jdx.dev/tasks/>

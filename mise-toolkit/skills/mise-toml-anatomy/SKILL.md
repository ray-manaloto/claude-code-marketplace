---
name: mise-toml-anatomy
description: The complete structure of a mise.toml file — every top-level section, what merges across the config hierarchy, and which file mise writes to when you run `mise use` or `mise set`. Use when designing a mise.toml from scratch, reviewing one, debugging hierarchy issues, or answering "what goes in mise.toml".
---

# `mise.toml` anatomy

## All valid filenames (in precedence order, top wins)

1. `mise.local.toml` — local overrides, **gitignore this**
2. `mise.toml`
3. `mise/config.toml`
4. `.mise/config.toml`
5. `.config/mise.toml`
6. `.config/mise/config.toml`
7. `.config/mise/conf.d/*.toml` (loaded alphabetically)

Plus environment-specific variants like `mise.<env>.toml` (selected via `MISE_ENV=production` or `mise -E production`).

Run `mise cfg ls` to see exactly what's loaded in any given directory and in what order.

## Top-level sections

```toml
min_version = "2026.4.0"            # hard pin; errors if mise is older
# OR: min_version = { hard = "2026.4.0", soft = "2026.4.0" }

experimental_monorepo_root = true   # experimental: implicit trust + namespaced tasks

[tools]
node = "24"
python = "3.12"
"npm:prettier" = "3"

[env]
NODE_ENV = "production"
DATABASE_URL = { required = "Set to your postgres URL" }
SECRET = { value = "...", redact = true }
_.file = ".env"
_.path = ["./bin"]

[tasks.build]
run = "vite build"
sources = ["src/**", "package.json"]
outputs = ["dist/**"]

[settings]
lockfile = true
idiomatic_version_file_enable_tools = ["python"]

[hooks]
postinstall = "echo done"

[[watch_files]]
patterns = ["src/**/*.rs"]
run = "cargo fmt"

[plugins]
my-tool = "https://github.com/me/my-mise-plugin.git"

[tool_alias.node.versions]
my_node = "20"

[shell_alias]
ll = "ls -la"

[redactions]
patterns = ["SECRET_*", "*_TOKEN"]
```

## How sections merge across the hierarchy

| Section | Merge behavior |
|---|---|
| **`[tools]`** | Additive with overrides. Closer file wins per-tool. |
| **`[env]`** | Additive with overrides. Closer file wins per-var. |
| **`[tasks]`** | Per-task **complete replacement**. Closer file wins. No deep merge of task fields. |
| **`[settings]`** | Additive with overrides. |
| **`[hooks]`** | Per-hook complete replacement. |

So defining `[tasks.test]` in both global config and project config means the project version *fully replaces* the global, even for fields the project didn't set.

## Where `mise use` / `mise set` writes

**Lowest precedence file in the highest precedence directory.** Concretely:

- Both `mise.toml` and `mise.local.toml` exist → writes to `mise.toml`.
- Both `mise.toml` and `mise.production.toml` exist → writes to `mise.toml`.
- Only `mise.local.toml` exists → writes to `mise.local.toml`.

This means your shared config is updated by default, while local/env overrides are preserved. Use `mise use --path mise.local.toml` or `mise use --env local` to target a specific file.

`mise use -g <tool>@<v>` writes to `~/.config/mise/config.toml`.

## Multiple `[env]` blocks

TOML doesn't allow duplicate keys in a table, so for multiple `_.source` directives use `[[env]]` (array of tables):

```toml
[[env]]
_.source = "./script_1.sh"
[[env]]
_.source = "./script_2.sh"
```

## `config_root` — the relative path anchor

`config_root` is the project root mise resolves relative paths against in env directives. It's **not** always the directory containing the config file:

| Config file | `config_root` |
|---|---|
| `~/src/foo/.config/mise/config.toml` | `~/src/foo` |
| `~/src/foo/.mise/config.toml` | `~/src/foo` |
| `~/src/foo/mise.toml` | `~/src/foo` |

This is the most common footgun for `_.file = ".env"` and `_.path = "./bin"` — they resolve against `config_root`, not the current working directory.

## The `[_]` escape hatch

Anything under `[_]` is ignored by mise. Use it for metadata you want in the file but not parsed:

```toml
[_]
project_owner = "frontend-team"
last_audit = "2026-01-15"
```

## JSON schema

mise publishes a JSON schema at <https://mise.jdx.dev/schema/mise.json>. VSCode, IntelliJ, and Neovim can autocomplete and validate `mise.toml` against it. Add the schema directive at the top of your file:

```toml
#:schema https://mise.jdx.dev/schema/mise.json
```

## Skills to read next

- `mise-tool-versioning` — what goes in `[tools]`
- `mise-env-directives` — `_.file`, `_.path`, `_.source`, `tools = true`, `required`, `redact`
- `mise-tasks-toml` — `[tasks]` deep dive
- `mise-trust-and-security` — `mise trust`, paranoid mode, idiomatic version files
- `mise-lockfile` — `mise.lock` workflow

For anything newer or more specific, consult `~/.cache/mise-toolkit/llms.txt` and the official docs at <https://mise.jdx.dev/configuration.html>.

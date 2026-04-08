---
name: mise-env-directives
description: The full mise [env] system — _.file (dotenv/json/yaml), _.path, _.source, _.<plugin>, tools=true lazy eval, required vars with help text, redactions, config_root resolution, and array-of-tables for multiple directives. Use whenever the user works on env vars in mise.toml, hits a "var not loaded" issue, or needs secrets/dynamic env handling.
---

# `[env]` directives

The `[env]` block is far more powerful than "set these vars". It supports loading from files, manipulating PATH, sourcing shell scripts, lazy evaluation against tool outputs, redaction, requirement validation, and plugin-driven dynamic env.

## The basics

```toml
[env]
NODE_ENV = "production"
DATABASE_URL = "postgres://localhost/myapp"

# Unset a previously-set var (e.g., from a parent config)
UNWANTED = false
```

## `_.file` — load dotenv / JSON / YAML

```toml
[env]
_.file = ".env"
```

Supports:
- Single file or array
- `dotenv`, `json`, or `yaml` formats (auto-detected by extension)
- Relative paths (resolved against `config_root`, **not** cwd)
- Object form for options

```toml
[env]
_.file = [
  ".env.json",                                            # JSON
  "/User/bob/.env",                                       # absolute dotenv
  { path = ".secrets.yaml", redact = true },              # redacted YAML
  { path = ".env", tools = true },                        # eval AFTER tools resolve
]
```

You can also set `MISE_ENV_FILE=.env` globally to auto-load a dotenv file in any directory.

Under the hood this uses [dotenvy](https://crates.io/crates/dotenvy). Quirks of that crate (escaping, multi-line, etc.) are not mise's to fix.

## `_.path` — extend `PATH`

```toml
[env]
_.path = "./bin"

# Or array, with mixed forms
_.path = [
  "~/.local/share/bin",                                       # absolute
  "{{config_root}}/node_modules/.bin",                        # explicit project root
  "tools/bin",                                                # equivalent: relative to config_root
  { path = ["{{env.GEM_HOME}}/bin"], tools = true },          # lazy: needs tool env
]
```

`config_root` is the project root, **not** the directory of the config file. So `_.path = "./bin"` from `~/proj/.config/mise/config.toml` resolves to `~/proj/bin`. This is the #1 source of "my path entry isn't working".

## `_.source` — bash-source a script

```toml
[env]
_.source = "./script.sh"
```

The script is run as if `source`d in bash. Exported vars become mise env. **The shebang is ignored** — must be bash-compatible shell code.

```toml
[env]
_.source = [
  "./scripts/base.sh",
  "/User/bob/env.sh",
  { path = ".secrets.sh", redact = true },
]
```

For non-bash scripts or binaries that emit env, see the experimental plugin directive below.

## `_.<plugin-name>` — env plugins

Plugins can provide dynamic env via the `MiseEnv` and `MisePath` hooks:

```toml
[env]
_.vault-secrets = { vault_url = "https://vault.example.com", secrets_path = "secret/myapp" }
_.git-env = { production_branch = "main" }
```

The configuration table is passed to the plugin's hooks via `ctx.options`. See <https://mise.jdx.dev/env-plugin-development.html> for building one.

## `tools = true` — lazy evaluation

By default, `[env]` is resolved **before** tools, so you can use env vars to configure tool installs. To reference values that come from tool installs (like `GEM_HOME`, tool versions), set `tools = true`:

```toml
[env]
# Without tools = true, GEM_HOME isn't set yet when this evaluates
GEM_BIN = { value = "{{env.GEM_HOME}}/bin", tools = true }

NODE_VERSION = { value = "{{ tools.node.version }}", tools = true }

# Path directive with tools = true
_.path = { path = ["{{env.GEM_HOME}}/bin"], tools = true }
```

This is a 2-pass evaluation: first pass resolves tools, then re-runs `[env]` for entries marked `tools = true`.

## `required` — fail-loud missing vars

```toml
[env]
DATABASE_URL = { required = true }

# With help text shown in the error
DATABASE_URL = { required = "Set DATABASE_URL to your postgres connection string" }
API_KEY = { required = "Get your API key from https://example.com/api-keys" }
```

A required var is satisfied if it's defined in:
1. The pre-existing shell environment, OR
2. A config file processed **after** the one that declared it required (e.g., `mise.local.toml`)

In regular commands (`mise env`, `mise install`), missing required vars **fail with the help text**. In shell activation (`mise hook-env`), they **warn but continue** to avoid breaking your shell prompt.

## `redact` — secret values

```toml
[env]
SECRET = { value = "my_secret", redact = true }
_.file = { path = ".env.json", redact = true }
```

For multiple vars by pattern:

```toml
[redactions]
patterns = ["SECRET_*", "*_TOKEN", "PASSWORD"]

[env]
SECRET_KEY = "..."
GITHUB_TOKEN = "..."
PASSWORD = "..."
```

**Important:** redactions intercept task output line-by-line, so they require a non-`raw` output mode. Tasks with `raw = true` bypass interception. Default `mise run` uses `replacing` mode; for CI, set `task.output = "prefix"` so logs are visible AND redactions still apply.

In CI (e.g., GitHub Actions), additionally use `::add-mask::` for each redacted value:

```bash
for value in $(mise env --redacted --values); do
  echo "::add-mask::$value"
done
```

`jdx/mise-action` does this automatically for `redact = true` and `redactions` patterns.

## Multiple `[env]` blocks (array of tables)

TOML doesn't allow duplicate keys in a table, so for multiple `_.source` directives:

```toml
[[env]]
_.source = "./script_1.sh"

[[env]]
_.source = "./script_2.sh"
```

Behaves identically to a single `[env]` table — just lets you have multiple `_.*` directives of the same kind.

## Templates

Env values support [Tera templates](https://keats.github.io/tera/):

```toml
[env]
LD_LIBRARY_PATH = "/some/path:{{env.LD_LIBRARY_PATH}}"
MY_PROJ_LIB = "{{config_root}}/lib"
```

Variables can reference each other (later refers to earlier):

```toml
[env]
MY_PROJ_LIB = "{{config_root}}/lib"
LD_LIBRARY_PATH = "/some/path:{{env.MY_PROJ_LIB}}"
```

## Shell-style `$VAR` expansion

As a simpler alternative to Tera, enable shell-style expansion:

```toml
[settings]
env_shell_expand = true

[env]
MY_PROJ_LIB = "{{config_root}}/lib"
LD_LIBRARY_PATH = "$MY_PROJ_LIB:$LD_LIBRARY_PATH"
```

Supported syntax:

| Syntax | Meaning |
|---|---|
| `$VAR` | Value of `VAR` |
| `${VAR}` | Same, useful before alphanumerics |
| `${VAR:-default}` | `default` if unset/empty |
| `${VAR:-}` | Empty if unset (suppress warning) |

Shell expansion runs **after** Tera template rendering, so both syntaxes can be mixed. Will become default in mise 2026.7.0; opt in with `env_shell_expand = true`.

## Common pitfalls

- **`_.file = ".env"` not loading** — relative paths resolve against `config_root` (project root), not the cwd. Move the file or use `{{config_root}}/.env`.
- **`tools = true` ordering** — without it, tool-set env vars (like `GEM_HOME`) aren't available. With it, mise needs an extra pass.
- **Required vars in CI** — set them in the CI env, or in a `mise.local.toml` that you generate at the start of the job.
- **Redactions silently dropped** — caused by `raw = true` tasks. Switch to `prefix` output mode.
- **Multiple `[env]` blocks** — must be `[[env]]` (array of tables), not `[env]` repeated.
- **`mise activate --shims` mode** — does NOT load `[env]`. Only the full activation does. Use `mise activate <shell>` (no `--shims`) if you need env vars.

## See also

- `mise-toml-anatomy` — `[env]` in context
- `mise-trust-and-security` — env directives can execute code, hence trust prompts
- `mise-secrets-fnox` (v0.2) — recommended secret manager
- <https://mise.jdx.dev/environments/>

---
name: mise-tool-versioning
description: Every way to specify a tool version in mise — exact, fuzzy, latest, lts, prefix, ref, sub, path — plus tool options like os, depends, postinstall, install_env. Use when writing or editing the [tools] section of mise.toml, picking a version syntax, or troubleshooting "wrong version installed".
---

# Tool versioning

## Version syntax cheat-sheet

| Syntax | Meaning | Example |
|---|---|---|
| `"24.1.0"` | Exact version | `node = "24.1.0"` |
| `"24"` | Latest installed/available 24.x | `node = "24"` |
| `"latest"` | Newest available | `node = "latest"` (avoid in committed configs) |
| `"lts"` | Latest LTS (supported by some tools) | `node = "lts"` |
| `"prefix:1.19"` | Latest matching `1.19.*` (use when bare version is ambiguous) | `go = "prefix:1.19"` |
| `"ref:<ref>"` | Build from a git ref (compile-from-source backends only) | `erlang = "ref:master"` |
| `"path:/abs/path"` | Use a pre-installed tool at this path | `node = "path:/opt/homebrew/opt/node@20"` |
| `"sub-2:lts"` | 2 versions behind LTS | `node = "sub-2:lts"` (LTS=22 → 20) |
| `"sub-0.1:latest"` | One minor behind latest | `python = "sub-0.1:latest"` |
| `["3.11", "3.12"]` | Multiple versions installed (first one is the active one on PATH) | `python = ["3.12", "3.11"]` |

### When `latest` ≠ "newest available"

This trips up newcomers. In **config files and most commands**, `latest` resolves to the newest **installed** version. So if you have node 20.0.0 installed and 22.0.0 is available, `node = "latest"` still uses 20.0.0.

Exceptions where `latest` means newest **available**:

- `mise install node@latest`
- `mise x node@latest -- node -v`
- `mise latest node`

To upgrade to the newest available and update your config: `mise upgrade --bump node`.

## Tool options (table form)

```toml
[tools]
node = { version = "22", postinstall = "corepack enable" }

# OS-restricted
ripgrep = { version = "latest", os = ["linux", "macos"] }
"npm:windows-terminal" = { version = "latest", os = ["windows"] }

# Tool dependencies (ordering)
"pipx:ruff" = { version = "latest", depends = ["python"] }

# Install-time env
"cargo:my-tool" = { version = "latest", install_env = { RUST_BACKTRACE = "1" } }
```

| Option | Purpose |
|---|---|
| `version` | The version (any of the syntaxes above) |
| `os` | Restrict to `["linux"]`, `["macos"]`, `["windows"]`, or any combo |
| `depends` | Tools that must finish installing first (single string or array) |
| `postinstall` | Command to run after this specific tool installs (gets `MISE_TOOL_INSTALL_PATH`, `MISE_TOOL_NAME`, `MISE_TOOL_VERSION` env vars) |
| `install_env` | Env vars set during the install process only |

`depends` is **additional** to the automatic dependencies a backend declares (e.g., `pipx` automatically depends on `python` and `uv`). Use it when you need extra ordering.

## Backend prefixes in `[tools]`

When the tool name has a colon (e.g., `"npm:prettier"`), TOML requires quoting:

```toml
[tools]
node = "24"                          # core tool, no prefix
"npm:prettier" = "3"
"pipx:black" = "latest"
"github:BurntSushi/ripgrep" = "14"
"aqua:1password/cli" = "latest"
"cargo:cargo-edit" = "latest"
```

You can also use `[tools."npm:prettier"]` table syntax for options.

## Backend selection (when there's no prefix)

When you write `node = "24"` (no prefix), mise consults the **registry** at `registry/<tool>.toml` to pick the backend. For node it's `core:node`. For most CLI tools it's the first backend in the registry's `backends = [...]` priority list.

To override per-tool:

```sh
# Environment variable (highest priority — overrides registry and aliases)
export MISE_BACKENDS_PHP='vfox:mise-plugins/vfox-php'

# Or in mise.toml plugins section
[plugins]
my-tool = "https://github.com/me/my-mise-plugin.git"
```

To see what backend a tool resolves to: `mise registry <tool>`.

## Common pitfalls

- **`node = "20"` vs `node = "20.0"`** — `"20"` matches all 20.x; `"20.0"` only matches 20.0.x. Use `prefix:20.0` if you want "latest 20.0.x" explicitly.
- **`latest` in committed configs** — works but defeats the purpose of pinning. Pin to a real version and use `mise upgrade --bump` to bump.
- **`os = ["macos"]` skipping in CI** — the tool simply won't install on Linux. CI on Linux won't have it. Make sure the tool is actually OS-specific before restricting.
- **`depends` chain too deep** — circular `depends` cause install failures. Keep it minimal.
- **Multiple versions of the same tool** — the first one in the array is on PATH. Useful for Python projects that need both 3.11 and 3.12 for tox-style testing.

## See also

- `mise-backends-overview` — the 15 backends and when to use each
- `mise-toml-anatomy` — `[tools]` in context
- `mise-lockfile` — pinning exact versions reproducibly
- <https://mise.jdx.dev/dev-tools/index.html>

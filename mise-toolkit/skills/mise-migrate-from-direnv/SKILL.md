---
name: mise-migrate-from-direnv
description: The direnv vs mise [env] overlap story — when mise's built-in [env] is enough to replace direnv entirely, when to keep direnv running alongside mise via the use mise integration, and how to translate common .envrc patterns to mise.toml. Use when a user is currently using direnv and wants to consolidate or coexist with mise.
---

# Migrating from direnv to mise (or coexisting)

direnv is the classic per-directory env-var manager — it runs `.envrc` on `cd`, injects env vars into your shell, and unsets them when you leave. mise has a built-in `[env]` block that does most of the same things, plus tool version management. For many users, mise replaces direnv entirely; for others, the two coexist.

## The decision — replace or coexist?

| You use direnv for… | Verdict |
|---|---|
| Just setting env vars (`.envrc` with `export FOO=bar`) | **Replace with mise `[env]`** |
| Setting env vars + activating a venv | **Replace** with `_.python.venv` |
| Setting env vars + sourcing `.env` files | **Replace** with `_.file = ".env"` |
| `use flake` (Nix integration) | **Coexist** — mise doesn't do Nix |
| `use node` / `use python` (version switching) | **Replace** — that's what mise is for |
| Complex shell logic in `.envrc` (functions, conditionals) | **Coexist or replace case-by-case** |
| `dotenv_if_exists`, `watch_file`, `path_add` | **Replace** — mise has all of these |
| Secrets from keychain via a helper | **Coexist** if the helper is direnv-specific, or **replace** by calling the helper from `[hooks] enter` |

**Most users can replace direnv entirely.** The exceptions are Nix-flake shops and people with heavily custom `.envrc` logic.

## `.envrc` → `mise.toml` translation cheat sheet

### Basic env vars

```sh
# .envrc
export DATABASE_URL=postgres://localhost/myapp
export LOG_LEVEL=debug
export PORT=3000
```

```toml
# mise.toml
[env]
DATABASE_URL = "postgres://localhost/myapp"
LOG_LEVEL = "debug"
PORT = "3000"
```

### Sourcing a `.env` file

```sh
# .envrc
dotenv
# or
dotenv_if_exists .env
```

```toml
# mise.toml
[env]
_.file = ".env"
```

`_.file` reads a dotenv-format file and loads its variables. Error if missing, unless:

```toml
[env]
_.file = { path = ".env", optional = true }
```

### Adding to PATH

```sh
# .envrc
PATH_add node_modules/.bin
PATH_add bin
```

```toml
# mise.toml
[env]
_.path = ["node_modules/.bin", "bin"]
```

Paths are resolved relative to the `mise.toml` location.

### Python venv activation

```sh
# .envrc
layout python3
# or
source .venv/bin/activate
```

```toml
# mise.toml
[env]
_.python.venv = { path = ".venv", create = true }
```

The `create = true` flag auto-creates the venv if missing, using the mise-pinned Python.

### Per-directory watched files

```sh
# .envrc
watch_file Gemfile.lock
```

In mise, files that affect config are auto-reloaded — `mise.toml`, `mise.lock`, and any `_.file` sources are watched automatically. For explicit task-level watches, use `[tasks.<name>].sources`.

### Conditional logic

```sh
# .envrc
if [[ "$(uname)" == "Darwin" ]]; then
  export CFLAGS="-I$(brew --prefix openssl)/include"
fi
```

mise supports tera templates in env values:

```toml
[env]
CFLAGS = "{{ exec(command='brew --prefix openssl') | trim }}/include"
```

Or, for more complex logic, shell out via `[hooks] enter`:

```toml
[hooks]
enter = "./scripts/setup-env.sh"
```

Most `.envrc` files don't actually need complex logic — the conditional was usually copied from a template. Try simplifying first.

## Replacing direnv entirely

1. **Translate every `.envrc`** to a `mise.toml` `[env]` block.
2. **Remove `eval "$(direnv hook zsh)"`** from shell rc.
3. **Add `eval "$(mise activate zsh)"`** (if not already there).
4. **Delete `.envrc` files** after confirming `mise env` shows the right vars in each project.
5. **Uninstall direnv**: `brew uninstall direnv` or equivalent.

## Coexisting with direnv

If you have Nix flakes, complex `.envrc` logic, or want mise for tools-only:

```sh
# .envrc — keep this
use mise   # tells direnv to load mise's env
use flake  # your Nix integration
```

direnv's `use mise` function (from `mise activate`'s output or the direnv-mise plugin) loads mise's tools and env into direnv's sandbox. mise handles tool versions; direnv handles the nix-flake layer on top.

Order in shell rc:

```sh
# ~/.zshrc
eval "$(mise activate zsh)"   # mise first
eval "$(direnv hook zsh)"     # direnv after
```

mise provides tools; direnv adds more env on top via `.envrc`.

## Why mise's `[env]` is usually enough

- **Declarative** — `[env]` in `mise.toml` is plain TOML; no shell to debug.
- **Trusted** — mise's trust system means you explicitly allow a config before it runs. `.envrc` required `direnv allow` for the same reason.
- **Tool-aware** — `_.python.venv`, `_.file`, `_.path` are purpose-built for common cases.
- **Tera templates** — enough logic for most cases without writing shell.
- **One file** — `mise.toml` holds tools + env + tasks. `.envrc` only held env.

## Anti-patterns

- **Running direnv and mise in parallel for the same env vars.** Last one wins, non-deterministically.
- **Keeping `.envrc` just to avoid "the migration effort"** — it's usually 5 minutes per project.
- **`use node` in `.envrc`** when mise is already managing Node. Redundant.
- **Committing secrets in `.envrc` or `mise.toml`** — use a secret manager + `_.file` pointing at a gitignored dotenv.

## Rollback

Reinstall direnv, restore `.envrc` from git, re-add `direnv hook` to shell rc.

```sh
brew install direnv
git checkout .envrc
```

## See also

- `mise-env-directives` — the full `[env]` reference (`_.file`, `_.path`, `_.python.venv`, `_.python.uv_venv_auto`, `_.source`).
- `mise-lang-python-overview` — `_.python.venv` depth.
- `mise-trust-and-security` — mise's trust system and why it exists.
- `mise-migrate-from-asdf` — general migration shape.
- direnv docs: `direnv.net`.

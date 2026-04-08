---
name: mise-migrate-from-pyenv
description: Migrating from pyenv to mise — reading .python-version, handling pyenv-virtualenv markers, translating pyenv-installed versions, handling the compile-from-source situation, and tearing down ~/.pyenv cleanly. Use when a user is currently using pyenv and wants to adopt mise.
---

# Migrating from pyenv to mise

pyenv is the long-standing Python version manager. mise replaces it with the same underlying python-build backend (same compile path, same options) plus support for pre-built binaries and integration with every other language you use. Migration is usually painless.

## What mise gives you over pyenv

- **Same python-build backend** → same versions available, same build flags, same compile reliability.
- **Optional pre-built binaries** via `MISE_PYTHON_COMPILE=0` — 10x faster installs.
- **One version manager for every language**, not just Python.
- **Per-project `[env]` and `[tasks]`** — pyenv doesn't do either.
- **Auto-activated venvs** via `_.python.venv`.
- **Faster shell startup** — mise is written in Rust, pyenv is shell functions.

## The migration plan

1. Inventory pyenv state.
2. Create `mise.toml` per project (or enable idiomatic reader).
3. Swap shell rc.
4. Verify.
5. Uninstall pyenv (and pyenv-virtualenv if present).

## Step 1 — inventory

```sh
pyenv versions                  # installed Python versions
pyenv version                   # current version
pyenv global                    # global default
pyenv local                     # in-project local pin (reads .python-version)
grep -r pyenv ~/.zshrc ~/.bashrc ~/.bash_profile 2>/dev/null
ls .python-version 2>/dev/null  # per-project version file
```

Also check for **pyenv-virtualenv**:

```sh
pyenv virtualenvs
cat .python-version   # may contain a virtualenv name like "myproject-3.12.7"
```

pyenv-virtualenv is a plugin that lets `.python-version` contain a virtualenv name instead of a bare version. If your `.python-version` has something like `myproject-3.12.7`, you'll need to handle that separately (see "pyenv-virtualenv migration" below).

## Step 2 — mise.toml per project

For a plain `.python-version` containing `3.12.7`:

```toml
# mise.toml
[tools]
python = "3.12.7"
```

Or enable the idiomatic reader and let mise read `.python-version` directly:

```toml
# mise.toml or ~/.config/mise/config.toml
[settings]
idiomatic_version_file_enable_tools = ["python"]
```

For pre-built binaries (strongly recommended — much faster):

```toml
[env]
MISE_PYTHON_COMPILE = "0"
```

Or set it globally in your shell rc.

### Global default

```toml
# ~/.config/mise/config.toml
[tools]
python = "3.12"

[env]
MISE_PYTHON_COMPILE = "0"
```

## Step 3 — swap shell rc

Remove pyenv's init:

```sh
# ~/.zshrc — DELETE
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"
eval "$(pyenv virtualenv-init -)"   # if you had pyenv-virtualenv
```

Add mise:

```sh
eval "$(mise activate zsh)"
```

Restart shell.

## Step 4 — verify

```sh
which python            # should be under ~/.local/share/mise/
python --version        # matches mise.toml
cd <project>
python --version        # matches the project's pin
```

If `which python` shows a pyenv path, the old `PATH` is sticky. Check for leftover pyenv lines, then open a fresh terminal.

## pyenv-virtualenv migration

pyenv-virtualenv stores `.python-version` with a venv *name* (e.g. `myproject-3.12.7`) and creates a venv under `~/.pyenv/versions/myproject-3.12.7/`. mise doesn't have a direct equivalent, but `_.python.venv` is the idiomatic replacement:

### Before (pyenv-virtualenv)

```
.python-version contains: myproject-3.12.7
Venv lives in:            ~/.pyenv/versions/myproject-3.12.7/
```

### After (mise)

```toml
# mise.toml
[tools]
python = "3.12.7"

[env]
_.python.venv = { path = ".venv", create = true }
```

```
Venv lives in: .venv/ (in the project dir, gitignored)
```

`.venv/` is in-project instead of centrally located. Pro: easier to blow away and recreate, no centralized cache to prune. Con: every project has its own full venv (but the Python interpreter itself is shared via mise's install dir, so this is less disk-heavy than it sounds).

If you want to keep a pyenv-virtualenv-style centralized layout:

```toml
[env]
_.python.venv = { path = "~/.cache/venvs/{{config_root | basename}}", create = true }
```

Not the idiomatic pattern, but possible.

## Step 5 — uninstall pyenv

```sh
rm -rf ~/.pyenv
# If installed via Homebrew:
brew uninstall pyenv pyenv-virtualenv
```

Restart the shell. Verify `which pyenv` reports not found.

## Common issues

### "SSL module not available" after migrating

You migrated to mise's compiled Python and the host is missing libssl-dev (or the equivalent). See `mise-lang-python-overview` → "Build dependencies". Or switch to pre-built: `MISE_PYTHON_COMPILE=0 mise install python@<version>`.

### `pip install` fails with "externally-managed-environment"

You're `pip install`-ing into the mise-installed Python's system site (PEP 668 error). Always use a venv:

```sh
python -m venv .venv
source .venv/bin/activate
pip install <pkg>
```

Or, better, use `uv` or `poetry` + `_.python.venv` to manage this for you. See `mise-lang-python-packages`.

### `python --version` shows a different version than `mise current python`

Shim cache staleness. Run `mise reshim` and reopen the shell.

### IDE still finds the pyenv Python

Point the IDE at the mise-installed interpreter explicitly:

```
~/.local/share/mise/installs/python/3.12.7/bin/python
```

Or the shim:

```
~/.local/share/mise/shims/python
```

The shim re-resolves on each invocation, so it always picks the project-correct version.

## Multiple Python versions (pyenv users often have many)

```toml
[tools]
python = "3.12 3.11 3.10"   # three versions, 3.12 is default
```

mise installs and makes all three available. `python3.11 --version` works; bare `python` resolves to the first.

## Global tools (pipx / pip --user equivalents)

If you were using `pip install --user black flake8 ruff` or pipx, move to mise's `pipx:` backend:

```toml
# ~/.config/mise/config.toml
[tools]
python = "3.12"
"pipx:ruff" = "latest"
"pipx:black" = "latest"
"pipx:httpie" = "latest"
```

Version-pinned, managed, survives Python version upgrades (pipx detects and rebuilds).

## Rollback

Reinstall pyenv if needed (your `.python-version` files are untouched):

```sh
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

Remove mise activation from shell rc. Restart shell.

## See also

- `mise-lang-python-overview` — Python version resolution.
- `mise-lang-python-packages` — uv / poetry / pipx decision.
- `mise-env-directives` — `_.python.venv` auto-activation.
- `mise-migrate-from-asdf` — general migration shape.
- mise docs: `mise.jdx.dev/faq.html#migrating-from-pyenv`.
- python-build-standalone: `github.com/astral-sh/python-build-standalone`.

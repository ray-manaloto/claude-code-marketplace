---
name: mise-lang-python-overview
description: Python via mise — .python-version auto-detection, idiomatic_version_file_enable_tools, how mise compiles Python under the hood (python-build), the pre-built binaries route via MISE_PYTHON_COMPILE=0, and when to pin patch versions. Use when setting up Python for a project or troubleshooting Python installs.
---

# Python via mise

Python is the language where mise most often earns its keep — pyenv's compilation story is slow and fragile, and system Python is usually too old or too new. mise gives you per-project pinned Python without the pyenv tax.

## Version resolution order

1. `mise.toml` `[tools] python` — explicit wins.
2. `mise.local.toml` override.
3. `.tool-versions`.
4. Idiomatic files, **opt-in**:
   ```toml
   [settings]
   idiomatic_version_file_enable_tools = ["python"]
   ```
   Reads `.python-version` and `.python-versions` (plural, pyenv's multi-version file).

The opt-in matters because a lot of Python projects leave stale `.python-version` files lying around, and silent promotion of those to authoritative would break migration from pyenv.

## Pinning in `mise.toml`

```toml
[tools]
python = "3.12"          # major.minor — mise picks the latest patch
python = "3.12.7"        # exact
python = "3.12 3.11"     # multiple versions, first is default
python = "latest"        # avoid
```

**For libraries**: pin major.minor (`"3.12"`). Patch versions change often; don't churn your lockfile.
**For services in prod parity**: pin exact (`"3.12.7"`). Match whatever prod runs.

## Compile vs pre-built

By default, mise **compiles Python from source** using python-build (the same backend pyenv uses). This is slow (5-15 minutes depending on machine) but gives you:
- Matched libc/libssl on the host.
- Custom build flags if needed.
- Any Python version going back years.

**Pre-built route** (faster, fewer options):

```sh
export MISE_PYTHON_COMPILE=0    # use pre-compiled binaries when available
mise install python@3.12
```

Pre-built binaries come from astral-sh/python-build-standalone and only cover recent versions. Set this in your shell rc or project `mise.toml`:

```toml
[env]
MISE_PYTHON_COMPILE = "0"
```

**Rule of thumb**: use pre-built for dev speed. Use compiled for production-critical services where you need exact libc match.

## Build dependencies (compile route)

If you're compiling Python, the host needs build tools:

**Debian/Ubuntu**:
```sh
sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev \
  libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

**macOS** (via Homebrew):
```sh
brew install openssl readline sqlite3 xz zlib tcl-tk libb2
```

Missing libs → Python compiles but modules silently don't work (`import ssl` fails, `sqlite3` unavailable). The `mise doctor` command checks for these.

## Virtual environments

mise pins the Python **interpreter**. It does **not** replace virtualenv / venv / uv / poetry — those manage the *project's* package set on top of a pinned interpreter.

The typical layout:

```
mise.toml         → python = "3.12"
pyproject.toml    → project deps (managed by uv/poetry/pip)
.venv/            → venv created by uv/poetry/python -m venv
```

mise can auto-activate a venv via:

```toml
[env]
_.python.venv = { path = ".venv", create = true }
```

This creates `.venv` using the mise-managed Python if it doesn't exist, and activates it whenever you `cd` into the project. Combined with uv/poetry, it's the cleanest Python setup available.

## Common setups

### Solo script / library

```toml
[tools]
python = "3.12"

[env]
MISE_PYTHON_COMPILE = "0"
_.python.venv = { path = ".venv", create = true }

[tasks.install]
run = "pip install -e '.[dev]'"
sources = ["pyproject.toml"]
```

### uv-managed project

```toml
[tools]
python = "3.12"
"pipx:uv" = "latest"      # or cargo:uv if you prefer

[env]
MISE_PYTHON_COMPILE = "0"

[tasks.install]
run = "uv sync"
sources = ["pyproject.toml", "uv.lock"]

[tasks.test]
depends = ["install"]
run = "uv run pytest"
```

### Data science (conda-ish without conda)

```toml
[tools]
python = "3.12"
"pipx:jupyterlab" = "latest"
"pipx:ruff" = "latest"

[env]
MISE_PYTHON_COMPILE = "0"
_.python.venv = { path = ".venv", create = true }

[tasks.lab]
run = "jupyter lab"
```

## Auto-detection gotchas

1. **`.python-version` from pyenv with `system`** as the content — mise doesn't know what "system" means and errors. Delete the file or replace with a real version.
2. **`pyenv-virtualenv` activation markers** in `.python-version` (e.g. `myvenv-3.12.7`) — mise doesn't parse virtualenv names; use `_.python.venv` instead.
3. **Compiling Python 2.7 or very old versions** — python-build supports them but they're slow and missing security fixes. Don't.
4. **Mixing mise Python with Homebrew Python** on macOS — shims must be first on PATH. Check with `which python`.

## See also

- `mise-lang-python-packages` — uv vs poetry vs pipx vs pip decision.
- `mise-migrate-from-pyenv` — moving off pyenv.
- `mise-env-directives` — `_.python.venv` and other auto-activate directives.
- mise docs: `mise.jdx.dev/lang/python.html`.
- python-build-standalone: `github.com/astral-sh/python-build-standalone`.

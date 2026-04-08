---
name: mise-lang-python-packages
description: Python package managers — uv vs poetry vs pipx vs pip. The rule is "mise pins python, uv/poetry manages project venv, pipx manages global CLIs". Covers the uv-first workflow (the current recommended default) and why mixing tools is the #1 Python environment nightmare. Use when picking a Python package manager.
---

# Python package managers — the 2026 answer

Python's package management has been a mess for a decade. The good news: **uv** (by Astral, same folks as ruff) has become the clear winner for new projects, and the rules are finally simple.

## The layering

```
mise           pins the Python interpreter
 └─> uv        manages the project's venv and lockfile
      └─> installed packages in .venv/
```

And separately, for global CLIs:

```
mise
 └─> pipx:<tool>    installs global Python CLIs in isolated venvs
```

**Rule**: mise handles "which Python". uv handles "which packages, in this project". pipx handles "which Python CLIs, globally". Don't cross the streams.

## The pick — 2026 defaults

| You want to… | Use |
|---|---|
| Start a new Python project | **uv** |
| Join a poetry-using project | **poetry** (don't migrate for no reason) |
| Install a global Python CLI (ruff, black, httpie, jupyterlab) | **pipx** (via mise's `pipx:` backend) |
| Run a single script with deps | **uv** (`uv run --with requests script.py`) |
| Rails-style "just make it work" for a small script | **uv** |
| Scientific computing with conda-style env | **uv** (supports `requirements.txt` style) or **pixi** (if you need bioconda etc.) |

**The 2026 default is uv.** It replaces pip, pip-tools, virtualenv, pyenv (no, mise), pipx (partially), and poetry. It's 10-100x faster than pip for installs. The project lock format is stable.

## uv + mise — the canonical setup

```toml
[tools]
python = "3.12"
"pipx:uv" = "latest"   # install uv itself via mise

[env]
MISE_PYTHON_COMPILE = "0"
_.python.venv = { path = ".venv", create = true }

[tasks.install]
run = "uv sync"
sources = ["pyproject.toml", "uv.lock"]

[tasks.test]
depends = ["install"]
run = "uv run pytest"

[tasks.lint]
depends = ["install"]
run = "uv run ruff check ."

[tasks.fmt]
depends = ["install"]
run = "uv run ruff format ."
```

`pyproject.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.110",
  "pydantic>=2.0",
]

[dependency-groups]
dev = [
  "pytest>=8.0",
  "ruff>=0.6",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

`uv sync` reads this, creates/updates `.venv`, writes `uv.lock`. `uv run pytest` executes pytest inside the venv. Clean, fast, deterministic.

## poetry + mise

If you're joining a poetry project, don't migrate to uv just for the sake of it. Poetry works fine with mise:

```toml
[tools]
python = "3.12"
"pipx:poetry" = "1.8"

[env]
MISE_PYTHON_COMPILE = "0"

[tasks.install]
run = "poetry install"

[tasks.test]
run = "poetry run pytest"
```

Poetry manages its own venv (usually in `~/Library/Caches/pypoetry/virtualenvs/` or `.venv` if you set `poetry config virtualenvs.in-project true`). mise pins the Python that poetry uses to create that venv.

Don't use both `_.python.venv` and poetry — poetry creates its own venv and gets confused.

## pipx via mise — for global CLIs

```toml
[tools]
python = "3.12"
"pipx:ruff" = "latest"
"pipx:httpie" = "latest"
"pipx:jupyterlab" = "latest"
"pipx:black" = "24.10"
```

Each `pipx:` entry installs the package into its own isolated venv under mise's install dir. The CLI is shimmed onto PATH. Same interface as a normal pipx install, but version-pinned and mise-lock'd.

**Use pipx for**: global tools (ruff, black, httpie, awscli, jupyterlab).
**Don't use pipx for**: project dependencies (those go in pyproject.toml).

## pip — the fallback

pip still exists and still works. Use it when:
- You're teaching Python to someone who's already confused.
- A tool's install instructions explicitly say `pip install ...` and you're in a venv.
- You're debugging a dep issue and want to try a specific version without bumping the lockfile.

**Don't** use `pip install` globally (outside a venv). macOS and Ubuntu now refuse by default (PEP 668 "externally-managed-environment").

## The mixing rules

1. **Never mix poetry and uv in the same project.** They fight over `pyproject.toml` semantics.
2. **Never mix conda/mamba and mise Python.** conda wants to own the Python install; mise wants to own the Python install. Pick one per project.
3. **Never `pip install` into the mise-installed Python system site.** Always use a venv.
4. **Never `sudo pip install` anything, ever.**
5. **Don't have both uv.lock and poetry.lock in the same repo.** Delete the unused one.

## uv as a pyenv replacement?

uv can install and manage Python itself (`uv python install 3.12`). This overlaps with mise. Current guidance:

- **Use mise for Python version pinning** — it's the single version-manager for your whole stack (Python, Node, Go, etc.), so mise.toml is one place.
- **Use uv for everything else Python** — venv, deps, run.

Don't use `uv python install` when mise is already managing Python. They'd both try to own the install dir.

## Scripting with uv

For single scripts, uv has a magic feature — inline dep metadata:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx", "rich"]
# ///
import httpx
from rich import print
print(httpx.get("https://httpbin.org/ip").json())
```

`uv run script.py` creates an ephemeral venv with the listed deps and runs the script. Replaces half of the "just pip install requests" tutorials.

## Anti-patterns

- **Manually activating venvs via `source .venv/bin/activate` in mise tasks** — use `uv run` / `poetry run` / `_.python.venv` auto-activation instead.
- **`pip install -r requirements.txt` in a CI workflow with no lockfile** — non-reproducible.
- **Using `pipx install` and `pip install --user` interchangeably** — pipx is strictly better for CLIs.
- **Committing `.venv/`** — no. `.gitignore` it.
- **Using `conda` inside a mise project** — pick one.

## See also

- `mise-lang-python-overview` — Python version resolution and compile flags.
- `mise-migrate-from-pyenv` — moving off pyenv.
- `mise-env-directives` — `_.python.venv = { path, create }` details.
- uv docs: `docs.astral.sh/uv/`.
- PEP 668: `peps.python.org/pep-0668/`.

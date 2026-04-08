---
name: mise-cookbook-python-fastapi
description: End-to-end recipe for a FastAPI service managed by mise — Python + uv + ruff + pytest + a Postgres env var. Complete mise.toml template, first-run walkthrough, and common gotchas. Use when starting a new FastAPI project or adding mise to an existing one.
---

# Cookbook — Python FastAPI service

A complete, opinionated starting point for a FastAPI service using mise. The result: one `mise.toml` that pins Python, installs uv, manages the venv, runs the server, tests, and lints. No pyenv, no poetry, no pip-tools.

## Who this is for

- You're starting a new FastAPI service and want a modern, fast, reproducible dev loop.
- You're adding mise to an existing FastAPI project that currently uses pyenv + pip or poetry.
- You want `mise run dev` to just work for every new contributor.

## Who this isn't for

- Flask or Django users — the bones transfer but specifics differ; start from `mise-lang-python-overview` instead.
- Data-science projects heavy on conda/mamba — see `mise-lang-python-packages` for the conda-vs-mise discussion.

## The `mise.toml`

```toml
min_version = '2026.4.0'

[tools]
python = "3.12"
"pipx:uv" = "latest"

[env]
# Faster installs (use python-build-standalone pre-built binaries)
MISE_PYTHON_COMPILE = "0"

# Auto-create and activate the venv whenever you cd into the project
_.python.venv = { path = ".venv", create = true }

# Service env
DATABASE_URL = { required = "postgres://user:pass@localhost:5432/myapp" }
LOG_LEVEL = "info"
PORT = "8000"

[redactions]
patterns = ["*_URL", "*_SECRET", "*_TOKEN", "*_API_KEY"]

[tasks.install]
description = "Install Python deps via uv"
run = "uv sync"
sources = ["pyproject.toml", "uv.lock"]

[tasks.dev]
description = "Run FastAPI in reload mode"
depends = ["install"]
run = "uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT"

[tasks.test]
description = "Run pytest"
depends = ["install"]
run = "uv run pytest"

[tasks.lint]
description = "Lint and format via ruff"
depends = ["install"]
run = ["uv run ruff check .", "uv run ruff format --check ."]

[tasks.fmt]
description = "Auto-format via ruff"
depends = ["install"]
run = "uv run ruff format ."

[tasks."db:migrate"]
description = "Run alembic migrations"
depends = ["install"]
run = "uv run alembic upgrade head"
```

And a minimal `pyproject.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi[standard]>=0.110",
  "pydantic>=2.0",
  "pydantic-settings>=2.0",
  "sqlalchemy>=2.0",
  "asyncpg>=0.29",
  "alembic>=1.13",
]

[dependency-groups]
dev = [
  "pytest>=8.0",
  "pytest-asyncio>=0.24",
  "httpx>=0.27",
  "ruff>=0.6",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## What this gives you

- **Pinned Python 3.12** — no drift between dev/CI/prod.
- **uv-managed venv** — ~10x faster installs than pip.
- **Auto-activation** — `_.python.venv` means `cd` into the project and `python` is already the venv's Python.
- **Missing-env warnings** — `DATABASE_URL` uses `required`, so the SessionStart nudge and every task will tell you if it's not set.
- **Redacted logs** — `[redactions]` keeps DB URLs and secrets out of `mise env` output.
- **One command for everything** — `mise run dev`, `mise run test`, `mise run lint`, `mise run db:migrate`.

## First-run walkthrough

```sh
# 1. Clone + trust
git clone <repo> myapp && cd myapp
mise trust

# 2. Install Python and uv (mise does both)
mise install

# 3. Install Python deps
mise run install       # creates .venv via uv sync

# 4. Set the required env var (one-time, put in shell rc or use a secret manager)
export DATABASE_URL="postgres://user:pass@localhost:5432/myapp"

# 5. Run migrations
mise run db:migrate

# 6. Start the dev server
mise run dev
```

SessionStart in Claude Code will also warn if `DATABASE_URL` isn't set, so you won't forget.

## Suggested project layout

```
myapp/
├── mise.toml
├── pyproject.toml
├── uv.lock               # committed
├── .gitignore            # includes .venv, __pycache__, .env
├── .env.example          # template without real values
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app factory
│   ├── api/              # routers
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── db.py
├── alembic/              # migrations
├── alembic.ini
└── tests/
    └── test_health.py
```

## CI snippet (GitHub Actions)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    env:
      DATABASE_URL: postgres://postgres:test@localhost:5432/postgres
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
        with: { install: true, cache: true }
      - run: mise run lint
      - run: mise run test
```

## Common gotchas

1. **`DATABASE_URL` missing** → SessionStart will complain. Set it via shell rc, keychain, or 1Password. Never commit.
2. **uv creates a venv at the wrong path** → `_.python.venv = { path = ".venv", create = true }` should handle it. Verify with `which python` after `cd`.
3. **`mise run install` fails with "no pyproject.toml"** → You need to `git clone` first or create one. `uv init` scaffolds a minimal one.
4. **Ruff and Black installed at the same time** → Pick ruff. It's a superset. Delete Black.
5. **`ImportError: cannot import name 'X' from 'fastapi'`** after Python upgrade → `mise run install` again; the venv needs to re-resolve deps.
6. **Alembic can't find models** → make sure `alembic/env.py` imports your `Base` and that `app/` is on `sys.path`. mise's `_.python.venv` handles PYTHONPATH correctly; alembic's `env.py` still needs the import.

## See also

- `mise-lang-python-overview` — Python version resolution, compile vs pre-built.
- `mise-lang-python-packages` — uv deep dive.
- `mise-env-directives` — `_.python.venv` and `required`/`redact`.
- `mise-ci-github-actions` — mise-action and caching.
- `mise-ai-cli-keys` — if you're also using AI CLIs in the project, apply the same secret-management rules.
- FastAPI docs: `fastapi.tiangolo.com`.
- uv docs: `docs.astral.sh/uv/`.

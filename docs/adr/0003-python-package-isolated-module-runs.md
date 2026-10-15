# 3. Dev Python is one package, run as `python -I -m`, never through console scripts

Date: 2026-10-14

## Status

Accepted (user, grill-with-docs round 1; plan decision D60, ticket CT-39)

## Context

Dev scripts ran as `python3 -I dev/<script>.py` so that a module planted in the working directory,
`PYTHON*` variables and the user site could not load. The user asked for native uv, ruff, ty and
`pyproject.toml` features, as the dotfiles and knowledge-base repos use. A measured test
(`.planning/<PLAN_ID>/reviews/ccm-20261014/grill-facts/F2-offline-layout-and-uv-isolation.md`
Part B) showed that console-script entry points and plain `-m` both let a planted `json.py` or a
`PYTHONPATH` module shadow the stdlib; only `uv run python -I -m <package>.<module>` keeps the
guarantee and still imports an installed package.

## Decision

Dev code becomes one src-layout package, `python/src/marketplace_dev/`, with ruff and ty settings
in `pyproject.toml` and a locked dev dependency group. Every mise task runs
`uv run --no-sync --offline python -I -m marketplace_dev.<module>`. Entry points may be declared
for people, but no task, hook or skill calls them. Dependency sync stays explicit; no hook or
read-only task runs `uv sync`.

## Considered options

Console scripts (`uv run <name>`, as dotfiles and knowledge-base do) were rejected because the
wrapper runs the interpreter without `-I`.

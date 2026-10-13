# dev/

Lightweight development surface; nothing here installs a runtime. Path-scoped test
rules load from `.claude/rules/dev-tests.md`.

## Contents

- `mise` (wrapper for `mise.dev.toml`), `check.py` (the `check` runner), `bootstrap.py`;
  task rows live in `mise.dev.toml` (`./dev/mise tasks ls`).
- Tracker, delivery and research helpers (`issue_*.py`, `git_delivery.py`,
  `checkout_*.py`, `search_*.py`, `research_*.py`, `*_saved_search.py`), each with a
  sibling `test_<helper>.py`.
- `research_refresh/` (runner with its own `README.md` and tests), `toolchains/`
  (C++ toolchain steps), `global-mise/` (toolchain mise profiles), `fixtures/`.

## Test discovery

- `dev/check.py` discovers only `dev/test_research_*.py` and
  `dev/research_refresh/test_*.py`. A new `test_<name>.py` outside those globs runs
  through a named `test:<name>` task in `mise.dev.toml`; list the task in `check:research`
  when it belongs to the research or tracker suites.
- Run one suite as `python3 -I -m unittest discover -s dev -p test_<name>.py`.
- `check.py` scrubs inherited `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` before running
  suites; a test that spawns a helper sets or removes both selectors itself, so a
  foreign environment never changes a result.

## Writing a helper or test

- Helpers use the standard library only, read inputs boundedly and reach no network.
- Tests follow `.claude/rules/dev-tests.md`: they assert an external seam, use a
  temporary `HOME` and `CODEX_HOME`, and take provider responses from `fixtures/`.
- One unit stays near five maintained files and 300 handwritten changed lines; run
  `./dev/mise run check` and the unit's named `test:*` task before expanding it.

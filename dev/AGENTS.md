# dev/

Lightweight development surface; nothing here installs a runtime. Tests follow
`.claude/rules/dev-tests.md` (external seams, hermetic `HOME`/`CODEX_HOME`, fixtures,
`python3 -I`, scrubbed environment selectors).

## Contents

`dev/mise` wraps `mise.dev.toml` (`./dev/mise tasks ls`); `check.py` is the `check`
runner. Each tracker, delivery and research helper has a sibling `test_<helper>.py`.
Subdirectories: `research_refresh/` (runner, own `README.md` and tests), `toolchains/`
(C++ toolchain steps), `global-mise/` (toolchain mise profiles), `fixtures/`.

## Test discovery

- `dev/check.py` discovers only `dev/test_research_*.py` and
  `dev/research_refresh/test_*.py`. A new `test_<name>.py` outside those globs runs
  through a named `test:<name>` task in `mise.dev.toml`; list the task in `check:research`
  when it belongs to the research or tracker suites.
- `check.py` scrubs inherited `VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` before running
  suites; a test that spawns a helper scrubs or pins both selectors itself.

## Writing a helper

- Helpers use the standard library only, read inputs boundedly and reach no network.
- Exit codes: 0 pass, 1 usage, 2 refusal with one reason per stderr line (C2 section E;
  `retro_gate.py`, `plan_decide.py`). argparse exits 2 on usage, so subclass `error`.
- A task that forwards free text runs as `mise run <task> -- <argv>` with no `usage` line; a
  `usage` variadic splits a multi-word argument.
- A helper that mutates state previews first, applies against a fresh preimage and
  verifies afterwards; an ambiguous attempt is verify-only.
- Unit size and ownership: `docs/agents/codex-task-orchestration.md`.
- A backend migration compares old and new behaviour on the same inputs and replaces
  one module at a time (`plugins/aggregated-research/AGENTS.md`).

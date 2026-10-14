---
paths: ["dev/**"]
---

# Tests under dev/

- Assert an external seam: a CLI exit code and its output, a receipt, a journal. A test that mirrors an internal function's structure breaks on refactors and proves nothing a seam test misses.
- Reach a gate by one of two routes: `dev/check.py` discovers the test (`dev/test_research_*.py` and `dev/research_refresh/test_*.py`, run by `./dev/mise run check`), or a named `test:*` task in `mise.dev.toml` runs it and `check:research` lists that task in its `depends` (the hosted research-fast workflow runs `check:research`).
- Build each test's environment explicitly: a temporary `HOME`/`CODEX_HOME` tree, or `patch.dict(os.environ, scrubbed(os.environ), clear=True)` as `dev/research_refresh/test_refresh.py` does; the real `~/.codex` stays out of reach. Fixtures hold provider responses, so no test calls a provider or the network.
- Run new suites as `python3 -I -m unittest discover -s dev -p <file>` so the interpreter ignores the environment and the current directory; the suites `dev/check.py` runs keep its `-B` invocation and rely on the scrubbed environment instead.
- A foreign `VIRTUAL_ENV` or `UV_PROJECT_ENVIRONMENT` in the caller's environment must not change a result; scrub or pin selectors inside the test.
- Fixtures live under `dev/fixtures/<topic>/`, one minimal case per behaviour.
- A test over a derived sample (a secret or private-name fixture built at run time) checks leakage as `self.assertFalse(sample in output, "fixture text leaked into ...")` before any equality over that output, compares request-body lists by `len()`, and labels subtests by case index: those forms keep the sample out of every failure message, log and transcript (D145).

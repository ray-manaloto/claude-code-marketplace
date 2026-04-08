---
description: Run jdx/mise e2e tests via the mise task (never invoke test files directly)
argument-hint: "[test_path ...]"
---

Run `mise run test:e2e $ARGUMENTS`.

**IMPORTANT:** Never invoke files in `e2e/` directly with `bash` — always go through the mise task. The harness sets up isolated `MISE_DATA_DIR` / `MISE_CONFIG_DIR` per test and tears them down. Direct invocation skips that and pollutes your home dir.

If `$ARGUMENTS` is empty, run the full e2e suite. Otherwise pass paths through (e.g., `cli/test_use backend/test_aqua`).

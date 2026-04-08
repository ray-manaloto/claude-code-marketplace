---
name: mise-contrib-write-e2e-test
description: Conventions for writing bash e2e tests in jdx/mise under e2e/** — assertion helpers, layout, the rule against direct invocation, the no-cleanup harness, and the no-chmod rule. Use whenever contributing tests to e2e/.
---

# Writing jdx/mise e2e tests

## Layout

```
e2e/
├── run_test.sh             # the harness (read this if confused about isolation)
├── assert.sh               # assertion helpers (sourced automatically)
├── cli/                    # tests for CLI subcommands
│   ├── test_use
│   ├── test_install
│   └── ...
├── backend/                # tests for individual backends
│   ├── test_aqua
│   ├── test_github
│   └── ...
├── config/                 # tests for config parsing & hierarchy
├── tasks/                  # tests for the task runner
├── env/                    # tests for [env] directives
└── ...
```

- Path: `e2e/<area>/test_<name>` — **no `.sh` extension, no executable bit**.
- `_slow` suffix for tests that compile/install real heavyweight tools (run only in slow CI).

## Hard rules

1. **Never `bash e2e/test_*` directly.** Always `mise run test:e2e <area>/test_<name>`. The harness creates an isolated `MISE_DATA_DIR` / `MISE_CONFIG_DIR` per test and tears them down. Direct invocation pollutes your home dir.
2. **Never `chmod +x`.** The harness invokes bash on the test files. Setting executable does nothing useful and may confuse contributors.
3. **No cleanup code.** No `rm`, no `unset`, no `trap`. The harness owns lifecycle.
4. **Use `mise` from PATH.** The task puts `target/debug` first, so plain `mise <command>` calls the freshly-built binary you're testing.
5. **`MISE_DEBUG=1` for verbose output**, never `RUST_LOG`.

## Assertion helpers

Sourced from `e2e/assert.sh`. Current set (run `Grep "^assert" e2e/assert.sh` to confirm):

| Helper | Use |
|---|---|
| `assert "<cmd>" "<expected stdout>"` | Exact stdout match |
| `assert_contains "<cmd>" "<substr>"` | Stdout contains substring |
| `assert_eq "$a" "$b"` | Two strings equal |
| `assert_fail "<cmd>" "<expected stderr substr>"` | Command must exit non-zero with that error |
| `assert_empty "<cmd>"` | Stdout must be empty |
| `assert_matches "<cmd>" "<regex>"` | Regex match on stdout |

## Template

```bash
#!/usr/bin/env bash
# e2e/cli/test_my_feature

# Set up a config — the cwd is a fresh isolated tmp dir
cat > mise.toml <<EOF
[tools]
node = "20"
EOF

# Exercise the feature
mise install
assert_contains "mise current node" "20"
assert "node --version" "v20.0.0"

# Verify the failure path
assert_fail "mise use my-tool@bogus-version" "version not found"
```

The shebang is `#!/usr/bin/env bash` for editor convenience, but the harness invokes bash directly so the shebang doesn't matter at runtime.

## Patterns

### Setting up a config

The cwd is a fresh tmp dir per test. Just write `mise.toml`:

```bash
cat > mise.toml <<EOF
[tools]
node = "20"
[env]
NODE_ENV = "test"
EOF
```

### Trust

The harness auto-trusts. **No `mise trust` calls needed** in tests.

### Env vars scoped to the test

```bash
export MISE_FOO=bar
mise some-command   # MISE_FOO is set
```

The export is automatically scoped — it goes away when the test ends.

### Verifying state

Prefer mise's own commands over poking at the install dir:

```bash
assert_contains "mise current node" "20"
assert_contains "mise ls" "node"
assert_contains "mise env" "NODE_ENV=test"
assert_contains "mise cfg" "mise.toml"
```

### Running real installs (sparingly)

Only in `_slow` tests. Use lightweight tools. For most tests, use the test fixtures (search for `dummy` or `mock` in existing tests).

## Debugging a failing test

```sh
MISE_DEBUG=1 mise run test:e2e cli/test_my_feature
```

If the test passes locally but fails in CI:
- Check for hardcoded paths (`/home/runner` vs `/Users/...`).
- Check for tool versions that aren't installed in the CI Docker image.
- Read `e2e/run_test.sh` to understand the isolation.

## What you avoid

- `rm`, `unset`, `trap`, or any cleanup code.
- `chmod +x` on the test file.
- Hardcoded `$HOME` paths or `/tmp/foo`.
- `bash e2e/cli/test_*` direct invocation.
- `_slow` suffix on tests that don't actually compile/install tools.
- Tests that require network beyond what existing tests already do.

## See also

- `mise-e2e-author` agent — writes tests when delegated
- `mise-contrib-overview` — broader contribution conventions
- `e2e/run_test.sh` — the harness
- `e2e/assert.sh` — the helpers

---
name: mise-ci-github-actions
description: Wiring mise into GitHub Actions using jdx/mise-action — version pinning, automatic redaction, lockfile-based caching, the bootstrap script alternative, and patterns for matrix builds. Also covers GitLab CI, generic docker, and Xcode Cloud at a glance. Use when setting up CI for a mise project, debugging "mise not found in CI", or hardening CI against rate limits.
---

# CI: GitHub Actions and friends

## GitHub Actions — `jdx/mise-action`

The official action handles install, caching, and tool installation. Add it to your workflow:

```yaml
name: test
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: jdx/mise-action@v3
        with:
          version: 2026.4.6        # [default: latest] pin mise itself
          install: true             # [default: true] run `mise install`
          cache: true               # [default: true] cache tool installs by mise.toml + mise.lock
          experimental: false       # [default: false] enable experimental features
      - run: cargo test            # tools from mise.toml are now on PATH
```

### Inline `mise.toml`

If you don't want a `mise.toml` in the repo, you can supply one inline:

```yaml
- uses: jdx/mise-action@v3
  with:
    mise_toml: |
      [tools]
      shellcheck = "0.9.0"
      actionlint = "latest"
- run: shellcheck scripts/*.sh
```

Or use the legacy `.tool-versions` format:

```yaml
- uses: jdx/mise-action@v3
  with:
    tool_versions: |
      shellcheck 0.9.0
```

### Automatic redaction

`jdx/mise-action` automatically calls GitHub's `::add-mask::` for any env var marked `redact = true` or matching a `[redactions].patterns` glob. You don't need extra setup — just mark the secrets in `mise.toml` and they're masked in logs.

If you're not using the action and bootstrapping mise manually, do it yourself:

```bash
for value in $(mise env --redacted --values); do
  echo "::add-mask::$value"
done
```

### Cache invalidation

`jdx/mise-action` keys the cache on `mise.toml` + `mise.lock` content. So:

- **No `mise.lock`**: cache invalidates whenever `mise.toml` changes — and tool install hits the upstream APIs.
- **With `mise.lock`**: cache invalidates only when the lockfile changes, AND installs are reproducible. **Strongly recommended.**

### Matrix with multiple OS

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
runs-on: ${{ matrix.os }}
steps:
  - uses: actions/checkout@v6
  - uses: jdx/mise-action@v3
  - run: mise run test
```

For multi-platform reproducibility, run `mise lock --platform linux-x64,macos-arm64,windows-x64` locally and commit the result.

## Bootstrap script (no curl-pipe-sh)

For CI environments where you don't trust the action, or you want to avoid `curl https://mise.run | sh`:

```sh
mise generate bootstrap -l -w
```

This generates `./bin/mise` (a script that downloads and runs mise) and updates `.gitignore`. Commit `./bin/mise`. In CI:

```yaml
- run: |
    ./bin/mise install
    ./bin/mise x -- npm test
```

Works in GitLab, CircleCI, Buildkite — anywhere that can run a script. No external action required.

## GitLab CI

```yaml
.mise-cache: &mise-cache
  key:
    prefix: mise-
    files: ["mise.toml", "mise.lock"]
  paths:
    - .mise/installs

build:
  image: debian:12-slim   # any image with curl + bash
  variables:
    MISE_DATA_DIR: $CI_PROJECT_DIR/.mise/installs
  cache:
    - <<: *mise-cache
      policy: pull-push
  script:
    - curl https://mise.run | sh
    - export PATH="$HOME/.local/bin:$PATH"
    - mise install
    - mise exec --command 'npm test'
```

Cache key includes `mise.lock` so the cache invalidates on lockfile changes.

## Generic Docker / any provider

```yaml
script: |
  curl https://mise.run | sh
  export PATH="$HOME/.local/bin:$PATH"
  mise install
  mise x -- <your-test-command>
```

Or with shims:

```yaml
script: |
  curl https://mise.run | sh
  eval "$($HOME/.local/bin/mise activate bash --shims)"
  npm test
```

## Xcode Cloud

```bash
#!/bin/sh
# ci_post_clone.sh
curl https://mise.run | sh
export PATH="$HOME/.local/bin:$PATH"
mise install
eval "$(mise activate bash --shims)"
swiftlint
```

## Generators that help with CI

```sh
mise generate github-action       # writes a starter .github/workflows/ci.yml
mise generate devcontainer        # writes .devcontainer/devcontainer.json
mise generate git-pre-commit      # writes .git/hooks/pre-commit calling mise tasks
mise generate bootstrap -l -w     # bootstrap script (above)
```

## Patterns and gotchas

- **Always commit `mise.lock`** for CI. Otherwise every run hits upstream APIs and you'll eventually rate-limit.
- **`jdx/mise-action@v3`** is current; v2 is deprecated. Pin major: `@v3`.
- **`MISE_TASK_OUTPUT=prefix`** in CI so logs are visible AND redactions still apply (default `replacing` mode shows a spinner instead of full output).
- **`MISE_GITHUB_TOKEN`** — set to `${{ secrets.GITHUB_TOKEN }}` if your tools fetch from GitHub releases and you want authenticated rate limits.
- **`MISE_TRUSTED_CONFIG_PATHS`** in CI — mise silently skips untrusted configs in non-interactive mode. The action handles this for you, but for manual setups, set it.
- **Don't use `mise activate`** in CI scripts — it requires an interactive prompt. Use `mise exec` / `mise x` or `mise activate --shims`.

## See also

- `mise-lockfile` — the file that makes CI cacheable
- `mise-trust-and-security` — `MISE_TRUSTED_CONFIG_PATHS` for non-interactive contexts
- `mise-tasks-toml` — output modes that work in CI
- <https://mise.jdx.dev/continuous-integration.html>
- <https://github.com/jdx/mise-action>

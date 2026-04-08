---
name: mise-cookbook-go-service
description: End-to-end recipe for a Go HTTP service managed by mise — Go + air (hot reload) + golangci-lint + gotestsum + a Dockerfile hint for production. Complete mise.toml template, first-run walkthrough, and common gotchas. Use when starting a new Go service or adding mise to an existing one.
---

# Cookbook — Go HTTP service

A complete starting point for a Go HTTP service using mise. Go is pinned, air handles hot reload, golangci-lint is wired in, gotestsum gives you pretty test output, and the cookbook links to the Docker recipe for production images.

## Who this is for

- Starting a new Go HTTP service (net/http, chi, echo, fiber, gin, etc.).
- Adding mise to an existing Go project currently relying on system Go + `go install`ed CLIs.
- Unifying Go versions across a team.

## Who this isn't for

- Pure library projects — you don't need `air` or service-specific tasks. Simpler setup is fine.
- CLI projects — the tasks are similar but `dev` is replaced by `run` and there's no hot reload.

## The `mise.toml`

```toml
min_version = '2026.4.0'

[tools]
go = "1.23"
"aqua:golangci/golangci-lint" = "1.62"
"aqua:cosmtrek/air" = "latest"
"aqua:gotestyourself/gotestsum" = "latest"

[env]
# Service env
PORT = "8080"
LOG_LEVEL = "info"

# Module behavior
GOFLAGS = "-mod=readonly"      # CI-safe; forbids implicit go.sum updates during build
CGO_ENABLED = "0"              # pure-Go binaries, easier cross-compile and smaller images

# GOBIN on PATH so `go install`ed tools work (optional)
GOBIN = "{{config_root}}/bin"
_.path = ["{{config_root}}/bin"]

# Private modules (adjust to your org)
# GOPRIVATE = "github.com/my-org/*"

[redactions]
patterns = ["*_URL", "*_SECRET", "*_TOKEN", "*_API_KEY"]

[tasks.install]
description = "Fetch deps"
run = "go mod download"
sources = ["go.mod", "go.sum"]

[tasks.dev]
description = "Run service with hot reload"
depends = ["install"]
run = "air"

[tasks.run]
description = "Run the service once (no reload)"
depends = ["install"]
run = "go run ./cmd/server"

[tasks.build]
description = "Build static binary"
depends = ["install"]
run = "go build -trimpath -ldflags='-s -w' -o bin/server ./cmd/server"
sources = ["**/*.go", "go.mod", "go.sum"]
outputs = ["bin/server"]

[tasks.test]
description = "Run all tests with pretty output"
depends = ["install"]
run = "gotestsum --format pkgname -- -race -cover ./..."

[tasks."test:integration"]
description = "Run integration tests (tagged)"
depends = ["install"]
run = "gotestsum --format testname -- -race -tags=integration ./..."

[tasks.lint]
description = "golangci-lint"
depends = ["install"]
run = "golangci-lint run ./..."

[tasks.fmt]
description = "Format code"
run = ["go fmt ./...", "goimports -w ."]

[tasks.tidy]
description = "go mod tidy"
run = "go mod tidy"

[tasks.check]
description = "Full pre-commit check"
depends = ["fmt", "lint", "test"]
run = "echo 'all checks passed'"
```

## The `.air.toml` (for hot reload)

```toml
root = "."
tmp_dir = "tmp"

[build]
cmd = "go build -o ./tmp/server ./cmd/server"
bin = "./tmp/server"
include_ext = ["go"]
exclude_dir = ["tmp", "bin", "vendor", ".git"]
delay = 500

[log]
time = true

[color]
main = "magenta"
build = "yellow"
runner = "green"
```

## The `.golangci.yml`

```yaml
run:
  timeout: 5m

linters:
  enable:
    - errcheck
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gofmt
    - goimports
    - gosec
    - misspell
    - unconvert
    - unparam
    - bodyclose
    - noctx
    - revive

linters-settings:
  revive:
    rules:
      - name: var-naming
      - name: exported

issues:
  exclude-use-default: false
```

## What this gives you

- **Pinned Go + lint + air + gotestsum** — one install pulls everything.
- **`mise run dev`** → air with hot reload. Change a `.go` file, the service restarts automatically.
- **`mise run check`** → runs the full fmt + lint + test chain. Same locally and in CI.
- **`mise run build`** → static binary with `-trimpath` and `-s -w` for deterministic, small binaries.
- **`GOBIN` on PATH** — if you do `go install` a tool, it lands in `bin/` and is reachable.
- **`CGO_ENABLED=0`** — pure-Go binary; trivially cross-compiles and ships in scratch images.

## First-run walkthrough

```sh
# 1. Clone + trust
git clone <repo> myservice && cd myservice
mise trust

# 2. Install Go + tooling
mise install

# 3. Fetch deps
mise run install

# 4. Start with hot reload
mise run dev
# Edit files; air rebuilds + restarts

# 5. Run tests
mise run test
```

## Suggested project layout

```
myservice/
├── mise.toml
├── go.mod
├── go.sum
├── .air.toml
├── .golangci.yml
├── .gitignore           # includes bin/, tmp/, coverage.out
├── README.md
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handlers/
│   ├── models/
│   └── store/
├── pkg/                 # optional — exported packages
└── test/
    └── integration/
```

## CI snippet (GitHub Actions)

```yaml
name: CI
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
        with: { install: true, cache: true }
      - uses: actions/cache@v4
        with:
          path: |
            ~/go/pkg/mod
            ~/.cache/go-build
          key: go-${{ runner.os }}-${{ hashFiles('**/go.sum') }}
          restore-keys: go-${{ runner.os }}-
      - run: mise run install
      - run: mise run lint
      - run: mise run test
      - run: mise run build
```

## Production Dockerfile hint

For the prod image, use the multi-stage pattern from `mise-cookbook-docker-dev` or `mise-docker-patterns`. The short version for a Go service is especially clean:

```dockerfile
# syntax=docker/dockerfile:1.7
FROM debian:12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh
ENV MISE_TRUSTED_CONFIG_PATHS=/workspace
WORKDIR /workspace
COPY mise.toml mise.lock ./
RUN --mount=type=cache,target=/root/.local/share/mise/installs \
    mise trust && mise install
COPY . .
RUN mise exec -- go build -trimpath -ldflags='-s -w' -o /out/server ./cmd/server

FROM gcr.io/distroless/static-debian12 AS runtime
COPY --from=builder /out/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

Because `CGO_ENABLED=0`, the binary is static and runs on `distroless/static` — ~20MB final image.

## Common gotchas

1. **`air: command not found` after `mise install`** → Run `mise reshim` and start a new shell.
2. **Hot reload rebuilds on every file change including `.md`** → Tune `include_ext` in `.air.toml`.
3. **`go mod tidy` drifts `go.sum`** → Always commit the result of `go mod tidy`. In CI, use `GOFLAGS=-mod=readonly` to fail fast if `go.sum` would change.
4. **`golangci-lint` takes forever on first run** → It builds a cache. Subsequent runs are fast. Cache `~/.cache/golangci-lint` in CI.
5. **Missing private modules** → Set `GOPRIVATE` in `[env]` and configure `git` to rewrite https to ssh for your org.
6. **`gotestsum` not running race detector** → The `-race` flag goes *after* `--`. Double-check the `run = "..."` syntax matches the example above.
7. **Distroless image missing CA certs** → Use `gcr.io/distroless/static-debian12` (includes CA certs) for services that make HTTPS calls.
8. **Building on macOS, shipping to Linux** → `GOOS=linux GOARCH=amd64 go build ...`. CGO-free binaries cross-compile without a cross-toolchain.

## See also

- `mise-lang-go-overview` — Go version resolution and toolchain.
- `mise-lang-go-modules` — module layouts, private modules, workspaces.
- `mise-cookbook-docker-dev` — full docker dev loop if this service is part of a multi-service stack.
- `mise-docker-patterns` — the multi-stage Dockerfile rationale.
- `/mise-dockerfile` — scaffold a starting Dockerfile.
- golangci-lint: `golangci-lint.run`.
- air: `github.com/air-verse/air`.
- gotestsum: `github.com/gotestyourself/gotestsum`.

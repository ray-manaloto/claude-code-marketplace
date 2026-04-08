---
name: mise-lang-go-overview
description: Go via mise — go.mod toolchain directive vs .go-version vs mise.toml precedence, GOPATH / GOBIN layout with mise, and the go: backend for installing CLIs built from source. Use when setting up Go for a project.
---

# Go via mise

Go is simpler than Python or Node — there's one canonical toolchain, one module system, and one standard layout. mise's job is to pin the Go version and wire GOBIN cleanly into shims.

## Version resolution order

1. `mise.toml` `[tools] go` — explicit wins.
2. `mise.local.toml`.
3. `.tool-versions`.
4. `go.mod`'s `toolchain` directive, opt-in via:
   ```toml
   [settings]
   idiomatic_version_file_enable_tools = ["go"]
   ```
5. `.go-version` (same opt-in).

The `toolchain` directive in `go.mod` is the most interesting case because Go itself honors it at runtime — if `go.mod` says `toolchain go1.23.4` and you run `go build` with a different version on PATH, Go auto-downloads 1.23.4 and uses it. mise's idiomatic reader makes mise-managed Go match that.

## Pinning in `mise.toml`

```toml
[tools]
go = "1.23"          # major.minor
go = "1.23.4"        # exact
go = "latest"        # fine for personal use
```

**Rule**: pin major.minor for libraries (lets patch updates flow in); pin exact for services if you want reproducible binaries byte-for-byte.

## `go.mod` integration

```go
// go.mod
module example.com/myapp

go 1.23

toolchain go1.23.4
```

- **`go 1.23`** — minimum language version the module requires. Static.
- **`toolchain go1.23.4`** — the exact toolchain this module was built with. Go's toolchain directive is dynamic: if a different version is on PATH, Go downloads the specified one transparently.

With mise idiomatic reader enabled, mise pins to `toolchain`'s version. Without the reader, pin in `mise.toml` directly.

**Rule**: don't duplicate. Either use `mise.toml` and leave `toolchain` off, or use `toolchain` with the idiomatic reader. Not both.

## GOPATH / GOBIN with mise

Out of the box, Go's defaults:
- `GOPATH` = `~/go`
- `GOBIN` = `~/go/bin` (where `go install`ed binaries land)

mise doesn't override these. It installs the Go toolchain under `~/.local/share/mise/installs/go/<version>/` and puts shims for `go`, `gofmt`, etc. on PATH.

**Recommendation**: leave `GOPATH=~/go` alone, put `~/go/bin` on PATH so `go install`ed tools work:

```toml
[env]
GOBIN = "{{env.HOME}}/go/bin"
_.path = ["{{env.HOME}}/go/bin"]
```

Or, for project-local `go install`ed tools:

```toml
[env]
GOBIN = "{{config_root}}/bin"
_.path = ["{{config_root}}/bin"]
```

Project-local keeps tools per-project but costs you the one-machine dedup of `~/go/bin`. Pick based on whether the tools are project-specific or general-purpose.

## `go:` backend for CLIs

mise's `go:` backend installs Go packages as mise-managed tools:

```toml
[tools]
go = "1.23"
"go:github.com/golangci/golangci-lint/cmd/golangci-lint" = "latest"
"go:github.com/air-verse/air" = "latest"
```

**When to use `go:` vs `aqua:`**: prefer `aqua:` when available. Aqua ships pre-built binaries; `go:` compiles from source (slower, requires network + go + build deps). Most popular Go CLIs are in aqua:

```toml
# Prefer this
[tools]
"aqua:golangci/golangci-lint" = "latest"
"aqua:cosmtrek/air" = "latest"

# Only fall back to go: for packages not in aqua
[tools]
"go:github.com/my-org/my-private-tool" = "latest"
```

The go backend is also the only option for private modules — aqua doesn't know about your private GitHub org.

## Private modules

```toml
[env]
GOPRIVATE = "github.com/my-org/*,gitlab.internal.corp/*"
GONOSUMCHECK = "github.com/my-org/*"

[tools]
go = "1.23"
```

For SSH-auth'd private repos, also make sure git is configured to rewrite https to ssh:

```sh
git config --global url."ssh://git@github.com/".insteadOf "https://github.com/"
```

## Common setups

### Library

```toml
[tools]
go = "1.23"

[tasks.test]
run = "go test ./..."

[tasks.lint]
run = "golangci-lint run"
```

### Service with air for hot reload

```toml
[tools]
go = "1.23"
"aqua:cosmtrek/air" = "latest"

[tasks.dev]
run = "air"

[tasks.build]
run = "CGO_ENABLED=0 go build -o bin/server ./cmd/server"
sources = ["**/*.go", "go.mod", "go.sum"]
outputs = ["bin/server"]

[tasks.test]
run = "go test -race -cover ./..."
```

### Workspace (multi-module)

```toml
[tools]
go = "1.23"

[tasks."work:sync"]
run = "go work sync"

[tasks.test]
run = "go test ./..."
# runs across all modules in go.work
```

## Auto-detection gotchas

1. **`go.mod` with `go 1.23` but no `toolchain`** — mise idiomatic reader picks the latest 1.23.x. Fine for most projects.
2. **Go's own toolchain auto-download** — if `toolchain go1.23.4` is in `go.mod` but mise has 1.22 installed, the toolchain directive causes Go to download 1.23.4 *separately* into `~/sdk/go1.23.4/`. That's Go's behavior, not mise's. Pin in `mise.toml` to match.
3. **CGO and cross-compilation** — mise gives you Go, not a C toolchain. For CGO targets, install the right cross-compiler via apt/brew; mise doesn't manage those.
4. **`GOPATH` collisions** — don't clone your Go project *inside* `$GOPATH/src`. Modern Go doesn't require it, and mixing the two layouts confuses editors.

## See also

- `mise-lang-go-modules` — modules, workspaces, private modules deep dive.
- `mise-backends-overview` — when to pick `aqua:` vs `go:` vs `github:`.
- `mise-env-directives` — `_.path` for GOBIN integration.
- mise docs: `mise.jdx.dev/lang/go.html`.

---
name: mise-lang-go-modules
description: Go modules deep dive — workspace mode, replace directives, private modules with GOPRIVATE, vendoring vs the module cache, and when to use `go install` vs mise's go: backend. Use when working with Go module layouts or troubleshooting dependency resolution.
---

# Go modules, workspaces, and the go: backend

Go's module system is simpler than most, but has a few corners that reliably trip people up: workspaces, replace directives, private modules, and vendoring. This skill covers them and how they interact with mise.

## The short story

- **`go.mod`** — single-module projects. The standard case.
- **`go.work`** — workspaces. Multiple modules edited together.
- **`GOPRIVATE`** — private modules (internal corp repos).
- **`vendor/`** — vendoring. Rare now, still relevant for some compliance stories.

All four are Go's domain, not mise's. mise just pins the Go toolchain that runs them.

## Workspaces (`go.work`)

Workspaces let you edit multiple interdependent modules together without juggling `replace` directives.

```
myorg/
├── go.work
├── api/
│   ├── go.mod       # module myorg/api
│   └── main.go
├── client/
│   ├── go.mod       # module myorg/client
│   └── client.go
└── shared/
    ├── go.mod       # module myorg/shared
    └── types.go
```

```
// go.work
go 1.23

use (
  ./api
  ./client
  ./shared
)
```

Now `go build ./...` from the root builds all three modules with local-first resolution. `myorg/api` importing `myorg/shared` uses the local copy, not a published version.

### Workspace mode in mise.toml

```toml
[tools]
go = "1.23"

[tasks."work:sync"]
run = "go work sync"

[tasks.build]
depends = ["work:sync"]
run = "go build ./..."

[tasks.test]
depends = ["work:sync"]
run = "go test ./..."
```

**Commit `go.work` to git** for monorepos where the workspace is the shared layout. **Don't commit it** for individual-dev workspaces that mix unrelated repos (add to `.gitignore`).

## `replace` directives

The older pattern for "use a local copy of this module":

```
// go.mod
replace myorg/shared => ../shared
```

Replace directives are painful across teams — the relative path only works if everyone has the same checkout layout. Workspaces are strictly better for the "I'm editing multiple modules at once" use case.

**Keep `replace` for**:
- Pinning a fork of a third-party module.
- Patching a dependency in place temporarily (with a `// TODO: remove after upstream PR #123` comment).

**Migrate to workspaces for**:
- Monorepos with multiple internal modules.

## Private modules — `GOPRIVATE`

```toml
[env]
GOPRIVATE = "github.com/my-org/*,gitlab.internal.corp/*"
GONOSUMCHECK = "github.com/my-org/*"
```

`GOPRIVATE` tells Go:
1. Don't use the public proxy (`proxy.golang.org`) for these modules.
2. Don't use the public checksum db (`sum.golang.org`) for them.

Without `GOPRIVATE`, Go phones home to the public infra for every private dep, which leaks module paths (and fails for truly private ones).

### SSH vs HTTPS for private modules

By default, `go get` uses HTTPS. For private GitHub orgs with SSH keys, tell git to rewrite:

```sh
git config --global url."ssh://git@github.com/".insteadOf "https://github.com/"
```

Now `go get github.com/my-org/…` uses your SSH key instead of asking for an HTTPS token.

Alternative: use a `~/.netrc` with an HTTPS token. Less common; larger surface area for leaks.

## Vendoring

`go mod vendor` copies all module deps into `./vendor/`. Build with `-mod=vendor` or `GOFLAGS=-mod=vendor`.

**Pros**:
- Builds are offline / network-free.
- No dependency on the module proxy.
- Audit-friendly — the tree is in git.

**Cons**:
- Bloats the repo.
- Adds a step to the dep-update loop.
- Rarely needed in 2026 — the module proxy is reliable.

**Use vendoring for**:
- Regulated environments with "all source in repo" requirements.
- Projects that ship as a tarball to users who may be offline.
- Kernel / low-level stuff where build reproducibility is paramount.

**Skip vendoring for**:
- Regular application development. The module cache (`~/go/pkg/mod`) is fine.

In mise.toml with vendoring:

```toml
[tools]
go = "1.23"

[env]
GOFLAGS = "-mod=vendor"

[tasks."deps:vendor"]
run = "go mod vendor"
sources = ["go.mod", "go.sum"]
outputs = ["vendor/"]
```

## `go install` vs mise's `go:` backend

Three ways to get a Go CLI installed:

### 1. `go install` into `~/go/bin`

```sh
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

- Installs into `$GOBIN` (defaults to `~/go/bin`).
- Not version-pinned per project — the latest global install wins.
- No mise.lock entry.
- Use for: personal global tools you manage yourself.

### 2. mise `go:` backend

```toml
[tools]
"go:github.com/golangci/golangci-lint/cmd/golangci-lint" = "1.62"
```

- mise compiles the CLI from source.
- Version-pinned, locked, reproducible.
- Requires the Go toolchain (also managed by mise).
- Slower than aqua because it compiles.

### 3. mise `aqua:` backend (preferred when available)

```toml
[tools]
"aqua:golangci/golangci-lint" = "1.62"
```

- Downloads a pre-built binary from GitHub releases.
- Fastest install.
- No Go toolchain required.
- Version-pinned, locked, reproducible.

**Decision**: try `aqua:` first. Fall back to `go:` only for tools that aren't published as GitHub releases.

```sh
mise registry golangci-lint   # see what backends are available
```

## Module cache hygiene

The shared module cache lives at `$GOPATH/pkg/mod/`. It can grow large (multi-GB). Clean occasionally:

```sh
go clean -modcache
```

Don't `rm -rf` the dir — it has read-only permissions that confuse some tools.

For CI caching, cache `~/go/pkg/mod` between runs:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/go/pkg/mod
    key: gomod-${{ runner.os }}-${{ hashFiles('**/go.sum') }}
```

## Anti-patterns

- **`go get` in a CI workflow** (instead of the implicit download during `go build`) — unnecessary.
- **Committing `vendor/` AND using the module proxy** — pick one.
- **`replace` with an absolute path** — breaks for every other contributor.
- **Manually editing `go.sum`** — run `go mod tidy` instead.
- **Using `go install` for team-shared tools and expecting everyone to have the same version** — use mise instead.

## See also

- `mise-lang-go-overview` — version resolution, GOPATH, toolchain directive.
- `mise-backends-overview` — aqua vs go vs other backends.
- `mise-ci-github-actions` — mise-action and the Go module cache.
- Go modules reference: `go.dev/ref/mod`.
- `go.work` guide: `go.dev/doc/tutorial/workspaces`.

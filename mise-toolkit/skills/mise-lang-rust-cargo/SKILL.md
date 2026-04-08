---
name: mise-lang-rust-cargo
description: The cargo ecosystem — cargo vs mise's cargo: backend for installing CLIs (prefer aqua over cargo build-from-source for ripgrep/fd/bat/etc.), sccache for compile caching, cargo-nextest as a test runner, cargo workspaces, and when to pin rustc exact vs channel. Use when working with cargo deps or CLIs.
---

# Cargo ecosystem — what belongs where

Cargo is both a package manager and a build system. mise's job is to pin rustc/cargo; cargo's job is to manage dependencies and build artifacts. The interesting decisions are about *which* Rust CLIs to install via mise vs cargo vs aqua.

## The `cargo install` trap

New Rust users reach for `cargo install ripgrep`. It works. It's also:

1. **Slow** — builds from source (minutes per tool).
2. **Not pinned** — `$HOME/.cargo/bin/rg` is whatever version you last installed.
3. **Not reproducible** — teammates get different versions.
4. **Requires a full Rust toolchain** — even if you only want the binary.

**Never use `cargo install` for tools that exist as pre-built binaries on GitHub.** Use aqua instead.

## The decision matrix

| CLI | Install via | Why |
|---|---|---|
| `ripgrep` | `aqua:BurntSushi/ripgrep` | Pre-built, fast, pinned |
| `fd` | `aqua:sharkdp/fd` | Pre-built |
| `bat` | `aqua:sharkdp/bat` | Pre-built |
| `eza` | `aqua:eza-community/eza` | Pre-built |
| `just` | `aqua:casey/just` | Pre-built |
| `cargo-nextest` | `aqua:nextest-rs/nextest` | Pre-built |
| `cargo-watch` | `cargo:cargo-watch` | Not published as a GitHub release; fallback to cargo backend |
| `cargo-<your-own-tool>` | `cargo:path-to-your-crate` | Not on aqua |
| Your team's internal CLI | `cargo:github.com/your-org/your-tool` | Private; aqua doesn't apply |

**Rule**: check `mise registry <tool>` first. If aqua is available, use it. Only fall back to `cargo:` for tools that genuinely aren't published as binaries.

## sccache — the ccache for Rust

Cargo's compile times are legendary. sccache caches rustc output and gives you massive speedups on incremental and cold builds.

```toml
[tools]
rust = "1.83"
"aqua:mozilla/sccache" = "latest"

[env]
RUSTC_WRAPPER = "sccache"
SCCACHE_DIR = "{{config_root}}/.cache/sccache"
SCCACHE_CACHE_SIZE = "10G"
```

Verify it's working:

```sh
sccache --show-stats
# after a build:
#   Compile requests               492
#   Cache hits                     425
#   Cache hits (Rust)              425
```

High hit rate (>80%) on incremental builds is normal. CI benefit is even bigger — cache the `SCCACHE_DIR` between runs.

## cargo-nextest — the test runner

`cargo test` is fine. `cargo nextest run` is faster, has better output, and parallelizes more aggressively.

```toml
[tools]
rust = "1.83"
"aqua:nextest-rs/nextest" = "latest"

[tasks.test]
run = "cargo nextest run --all-features"

[tasks."test:slow"]
run = "cargo nextest run --all-features --run-ignored=only"
```

Rule of thumb: if you have more than ~50 tests, nextest's speedup is worth it.

## Workspaces

Cargo workspaces share a `Cargo.lock` and a `target/` dir across multiple crates in one repo:

```
myproject/
├── Cargo.toml       # workspace root
├── Cargo.lock
├── target/          # shared build dir
├── crates/
│   ├── core/
│   │   └── Cargo.toml
│   ├── cli/
│   │   └── Cargo.toml
│   └── server/
│       └── Cargo.toml
```

```toml
# Cargo.toml (workspace root)
[workspace]
resolver = "2"
members = ["crates/*"]

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[workspace.package]
rust-version = "1.83"
edition = "2021"
```

Individual crate `Cargo.toml` references the workspace:

```toml
[package]
name = "myproject-core"
version.workspace = true
edition.workspace = true
rust-version.workspace = true

[dependencies]
serde.workspace = true
```

**mise.toml for a workspace**:

```toml
[tools]
rust = "1.83"
"aqua:nextest-rs/nextest" = "latest"
"aqua:mozilla/sccache" = "latest"

[env]
RUSTC_WRAPPER = "sccache"
SCCACHE_DIR = "{{config_root}}/.cache/sccache"

[tasks.build]
run = "cargo build --workspace"

[tasks.test]
run = "cargo nextest run --workspace --all-features"

[tasks.lint]
run = "cargo clippy --workspace --all-targets --all-features -- -D warnings"

[tasks.fmt]
run = "cargo fmt --all"
```

## Pinning rustc — channel vs exact

- **`rust = "stable"`** — follows whatever stable is. Lowest maintenance; you implicitly adopt every new release.
- **`rust = "1.83"`** — pinned to 1.83.x (latest patch). Good balance.
- **`rust = "1.83.0"`** — exact. Reproducible to the bit. Use for services where you want CI and prod to match exactly.

**MSRV (Minimum Supported Rust Version)** belongs in `Cargo.toml`'s `rust-version`, not mise. They're different fields answering different questions:
- `rust-version` in `Cargo.toml`: "this crate needs at least this rustc" — a constraint.
- `rust` in `mise.toml`: "this project develops with this rustc" — a pin.

## cargo features — conventional choices

```toml
# Cargo.toml
[features]
default = ["std"]
std = []
tokio-runtime = ["dep:tokio"]
tls = ["dep:rustls"]
full = ["std", "tokio-runtime", "tls"]
```

In mise tasks, pass features explicitly to avoid feature-unification surprises:

```toml
[tasks.test]
run = "cargo nextest run --all-features"

[tasks."test:no-default"]
run = "cargo nextest run --no-default-features"
```

## cross-compilation

```toml
[tools]
rust = "1.83"
"aqua:cross-rs/cross" = "latest"

[tasks."build:arm64"]
run = "cross build --target aarch64-unknown-linux-gnu --release"
```

`cross` uses Docker to give you the right C toolchain per target. mise pins cross itself; cross handles the cross-compile complexity.

## Anti-patterns

- **`cargo install ripgrep`** (see above — use aqua).
- **Committing `target/`** — no. It's huge.
- **Not committing `Cargo.lock`** for applications. Libraries can skip it; apps can't.
- **Using `cargo watch` without `cargo-watch` installed** — install it first (the `cargo:` backend is fine for this one).
- **`[workspace.dependencies]` + per-crate `version = "1.2"`** — redundant; use `.workspace = true` instead.
- **Using `nightly` without a date pin** — pin dated nightlies (`nightly-2026-04-01`).

## See also

- `mise-lang-rust-overview` — rust-toolchain.toml, channels, components.
- `mise-backends-overview` — aqua vs cargo vs other backends.
- `mise-ci-github-actions` — caching `target/` and `SCCACHE_DIR` in CI.
- cargo book: `doc.rust-lang.org/cargo/`.
- nextest: `nexte.st`.
- sccache: `github.com/mozilla/sccache`.

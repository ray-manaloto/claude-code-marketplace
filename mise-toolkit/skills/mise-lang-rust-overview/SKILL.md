---
name: mise-lang-rust-overview
description: Rust via mise — rust-toolchain.toml auto-detection, the mise-over-rustup architecture, channel selection (stable/beta/nightly), components (clippy, rustfmt, rust-src, rust-analyzer), and targets. Use when setting up Rust for a project or explaining how mise + rustup interact.
---

# Rust via mise

Rust is the one language where mise intentionally defers to an existing tool — **rustup**. mise installs and manages rustup, and rustup manages the actual toolchain. This keeps you in the mainstream Rust ecosystem (where every tutorial assumes rustup) while still giving you mise's per-project pinning.

## The architecture

```
mise
 └─> rustup (installed via mise)
      └─> toolchains (stable-x86_64, 1.83.0, nightly-2026-04-01, ...)
           └─> rustc, cargo, clippy, rustfmt, rust-analyzer, ...
```

When you put `rust = "1.83"` in `mise.toml`, mise asks rustup to install toolchain `1.83.0` and sets `RUSTUP_TOOLCHAIN` so `cargo`/`rustc` use it. The binary you run is still rustup's shim, which delegates to the requested toolchain.

## Version resolution order

1. `mise.toml` `[tools] rust` — explicit.
2. `mise.local.toml`.
3. `.tool-versions`.
4. `rust-toolchain.toml` / `rust-toolchain` (legacy), opt-in:
   ```toml
   [settings]
   idiomatic_version_file_enable_tools = ["rust"]
   ```

## `rust-toolchain.toml` — the one you should use

```toml
# rust-toolchain.toml
[toolchain]
channel = "1.83.0"
components = ["clippy", "rustfmt", "rust-analyzer"]
targets = ["x86_64-unknown-linux-gnu", "aarch64-unknown-linux-gnu"]
profile = "minimal"
```

- **`channel`** — the toolchain: `stable`, `beta`, `nightly`, or a specific version (`1.83.0`), or a dated nightly (`nightly-2026-04-01`).
- **`components`** — optional extras. `clippy` and `rustfmt` are basically mandatory; `rust-analyzer` for IDE support; `rust-src` for `--offline` standard library building.
- **`targets`** — cross-compilation targets. Defaults to the host target only.
- **`profile`** — `minimal` (default rustc + cargo only), `default` (adds rustfmt + clippy), `complete` (everything).

mise's idiomatic reader honors all of these. No need to duplicate in `mise.toml`.

## Pinning in `mise.toml`

```toml
[tools]
rust = "1.83"              # major.minor
rust = "1.83.0"            # exact
rust = "stable"            # channel
rust = "nightly"           # channel
rust = "nightly-2026-04-01" # dated nightly
```

**Rule**: libraries use `stable`. Services use a specific version for reproducibility. Nightly only for projects that explicitly need nightly features.

## Components — what each gives you

| Component | Purpose | Default in mise? |
|---|---|---|
| `rustc`, `cargo` | Core | Always |
| `rustfmt` | `cargo fmt` | Usually default |
| `clippy` | `cargo clippy` lints | Usually default |
| `rust-analyzer` | LSP for IDEs | No — add explicitly |
| `rust-src` | Standard library source (for `build-std`, certain IDE features) | No — add if needed |
| `llvm-tools` | `cargo objdump`, `cargo cov`, coverage profiling | No — add for profiling |
| `rustc-dev` | Internal rustc APIs (only for people writing clippy lints, etc.) | No |

If you're using `rust-toolchain.toml`, specify components there. If you're using `mise.toml` alone, mise auto-installs `clippy` and `rustfmt` with the toolchain.

## Targets — cross-compilation

```toml
# rust-toolchain.toml
[toolchain]
channel = "1.83"
targets = ["wasm32-unknown-unknown", "aarch64-apple-darwin"]
```

Targets install target-specific stdlib pre-built artifacts. Doesn't give you a C cross-compiler (you still need clang or gcc-aarch64-linux-gnu from apt/brew for linking), but gets rustc able to emit the right object format.

For wasm specifically:

```toml
[tools]
rust = "1.83"
"aqua:rustwasm/wasm-pack" = "latest"
```

## Common setups

### Library / binary, stable

```toml
# mise.toml — or just use rust-toolchain.toml
[tools]
rust = "1.83"

[tasks.build]
run = "cargo build --release"

[tasks.test]
run = "cargo test --all-features"

[tasks.lint]
run = "cargo clippy -- -D warnings"

[tasks.fmt]
run = "cargo fmt"

[tasks."fmt:check"]
run = "cargo fmt --check"
```

### `rust-toolchain.toml` + mise (idiomatic)

```toml
# rust-toolchain.toml
[toolchain]
channel = "1.83.0"
components = ["clippy", "rustfmt", "rust-analyzer"]
profile = "minimal"
```

```toml
# mise.toml
[settings]
idiomatic_version_file_enable_tools = ["rust"]

[tasks.build]
run = "cargo build"
```

mise reads `rust-toolchain.toml` and installs the right toolchain. `mise.toml` is minimal — just tasks.

### Nightly with specific features

```toml
# rust-toolchain.toml
[toolchain]
channel = "nightly-2026-04-01"
components = ["rust-src", "clippy", "rustfmt"]
```

Dated nightlies are the right choice — prevents your CI from breaking when nightly changes. Update the date deliberately.

### With sccache for compile caching

```toml
[tools]
rust = "1.83"
"aqua:mozilla/sccache" = "latest"

[env]
RUSTC_WRAPPER = "sccache"
SCCACHE_DIR = "{{config_root}}/.cache/sccache"
SCCACHE_CACHE_SIZE = "10G"

[tasks.build]
run = "cargo build"
# subsequent builds hit sccache
```

sccache is Rust's ccache equivalent. Huge wins on CI with cache persistence.

## `cargo:` backend vs `aqua:` for Rust CLIs

mise has a `cargo:` backend for building Rust CLIs from source:

```toml
[tools]
"cargo:ripgrep" = "latest"
```

**Don't.** Prefer aqua when available — ripgrep, fd, bat, eza, and every other popular Rust CLI ships pre-built binaries via GitHub releases, which aqua wraps:

```toml
[tools]
"aqua:BurntSushi/ripgrep" = "latest"
"aqua:sharkdp/fd" = "latest"
"aqua:sharkdp/bat" = "latest"
```

Benefits: no compile step, no Rust toolchain needed just to install CLIs, works on CI without a Rust install.

Use `cargo:` only for crates that aren't published as GitHub releases (niche, usually your own tools).

## Auto-detection gotchas

1. **`rust-toolchain` (no extension) with just `1.83` in it** — legacy format, one line. mise reads it but prefer the `.toml` form for new projects.
2. **`rust-toolchain.toml` with unknown `profile` values** — mise forwards to rustup; if rustup doesn't recognize the profile, install fails. Stick to `minimal`, `default`, `complete`.
3. **`cargo install` into `~/.cargo/bin`** — not managed by mise. If you want version-pinned Rust CLIs, use `aqua:` or `cargo:` backends, not `cargo install`.
4. **Toolchain switching inside a single session** — `rustup override` within a subdir fights with mise's `[tools]`. Pick one; don't mix.

## See also

- `mise-lang-rust-cargo` — cargo ecosystem, cargo-nextest, sccache, the aqua vs cargo decision.
- `mise-backends-overview` — general backend selection.
- mise docs: `mise.jdx.dev/lang/rust.html`.
- rustup docs: `rust-lang.github.io/rustup/`.

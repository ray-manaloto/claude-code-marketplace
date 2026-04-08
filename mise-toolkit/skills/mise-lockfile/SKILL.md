---
name: mise-lockfile
description: The mise.lock workflow — generating, committing, environment-specific lockfiles, strict locked mode for hermetic CI, provenance verification, and the install_before supply-chain delay. Use when setting up reproducible builds, hardening CI, debugging "why is the wrong version installing", or recommending lockfile practices.
---

# `mise.lock` — the lockfile

`mise.lock` pins exact versions, checksums, sizes, URLs, and provenance for every tool. Like `package-lock.json` or `Cargo.lock`, but cross-language.

**Lockfiles are NOT created automatically.** You must explicitly run `mise lock` to generate them. Once one exists, `mise install` and `mise use` keep it updated.

## Enabling

```sh
mise settings lockfile=true
```

Or in config:

```toml
[settings]
lockfile = true
```

## Generating

```sh
mise lock                                # all tools, current platform
mise lock --platform linux-x64,macos-arm64  # specific platforms (CI multi-arch)
mise lock node python                     # specific tools only
mise lock --local                         # update mise.local.lock
mise lock -g                              # update global lockfile
```

## What's in the file

```toml
[[tools.node]]
version = "20.11.0"
backend = "core:node"

[tools.node.platforms.linux-x64]
checksum = "sha256:a6c213b7a2c3..."
size = 23456789
url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz"

[[tools.ripgrep]]
version = "14.1.1"
backend = "aqua:BurntSushi/ripgrep"
options = { exe = "rg" }

[tools.ripgrep.platforms.linux-x64]
checksum = "sha256:4cf9f274..."
size = 1234567
```

Each tool entry has `version`, optional `backend`, optional `options`, and a `platforms` table keyed by `os-arch`.

## Backend support matrix

| Support level | Backends |
|---|---|
| **Full** (version + checksum + size + URL) | `aqua`, `http`, `github`, `gitlab` |
| **Full + provenance verification** | `aqua`, `github`, `core:python` (precompiled), `core:ruby` (precompiled), `core:zig` (install-time) |
| **Partial** (version + URL + provenance) | `vfox` (tool plugins only) |
| **Partial** (version + checksum + size) | `ubi` |
| **Basic** (version + checksum) | `core` (some tools) |
| **Version only** | `asdf`, `npm`, `cargo`, `pipx` |

So for maximum reproducibility, prefer `aqua:` and `github:` backends.

## Strict mode (`locked = true`)

Forces every tool resolution to come from the lockfile. No API calls to GitHub/aqua-registry/etc. at install time.

```toml
[settings]
locked = true
```

Or `MISE_LOCKED=1 mise install`.

When enabled, `mise install` **fails** if a tool doesn't have a URL for the current platform in the lockfile. Pre-populate with `mise lock --platform <list>` for every platform you'll install on.

This is the gold standard for CI reproducibility — guarantees no external API dependency at install time.

> ⚠️ **All mise settings are global.** `locked = true` in a project's `mise.toml` applies to ALL tool resolution including your global `~/.config/mise/config.toml` tools. If you see warnings about global tools missing from the lockfile, run `mise lock -g` to generate a global lockfile.

## Environment-specific lockfiles

When using environment-specific configs (e.g., `mise.test.toml`, set via `MISE_ENV=test`), each environment gets its own lockfile:

| Config | Lockfile |
|---|---|
| `mise.toml` | `mise.lock` |
| `mise.test.toml` | `mise.test.lock` |
| `mise.staging.toml` | `mise.staging.lock` |
| `mise.local.toml` | `mise.local.lock` |
| `mise.test.local.toml` | `mise.test.local.lock` |

```sh
MISE_ENV=test mise lock   # creates BOTH mise.lock AND mise.test.lock
```

Tools from `mise.toml` go to `mise.lock`; tools from `mise.test.toml` go to `mise.test.lock`. They're strictly scoped — env-specific lockfiles only contain tools defined in that env's config.

**Why this matters for CI**: a CI job that doesn't set `MISE_ENV` only depends on `mise.lock`, so dev tool version bumps in `mise.dev.lock` won't invalidate CI caches.

## What to commit

| File | Commit? |
|---|---|
| `mise.lock` | ✅ yes |
| `mise.<env>.lock` (e.g., `mise.test.lock`) | ✅ yes |
| `mise.local.lock` | ❌ no (local dev only) |
| `mise.<env>.local.lock` | ❌ no |

Add the local lockfiles to `.gitignore` alongside their corresponding configs.

## Provenance verification

When `mise lock` generates a lockfile, it records a **provenance type** per tool: `slsa`, `cosign`, `minisign`, or `github-attestations`. For the **current platform**, mise actually downloads the artifact and cryptographically verifies it at lock time. For cross-platform entries, provenance is detected from registry metadata only (no verification, since the artifact may not be runnable here).

By default, when `mise install` sees a lockfile with both checksum and provenance, it **trusts the lockfile** and skips re-verification. This avoids hitting GitHub attestation rate limits in CI.

To force re-verification on every install:

```toml
[settings]
locked_verify_provenance = true
```

Also automatically enabled by `paranoid = true`.

## `install_before` — release age gate (supply-chain delay)

Pair with lockfiles to mitigate brand-new malicious releases:

```toml
[settings]
install_before = "7d"   # only resolve to versions released > 7 days ago
```

Now if a malicious version is published, you have 7 days to notice before mise will pick it up. Lockfile pins your specific known-good version; `install_before` protects when you upgrade.

## Workflows

### Initial setup

```sh
mise lock          # generate
git add mise.lock
git commit -m "Add mise.lock"
```

### Daily

```sh
mise install       # uses exact versions from lockfile
mise upgrade       # bump tools and update lockfile
```

### Bumping a tool

```sh
mise use node@24   # updates mise.toml AND mise.lock
git diff mise.lock # review the change
git commit -m "Bump node to 24"
```

### CI multi-platform

```sh
mise lock --platform linux-x64,linux-arm64,macos-arm64,windows-x64
```

Run this whenever you bump tools so all your CI matrix targets are pinned.

## Troubleshooting

- **"Tool missing URL for current platform"** with `locked = true` — run `mise lock --platform <your-arch>`.
- **Conflicting lockfiles after a merge** — resolve in `mise.lock`, then `mise install` to verify, then commit.
- **Checksums invalidated** — `mise uninstall --all && mise install` to regenerate.
- **`mise install` is making GitHub API calls and hitting rate limits** — you don't have a lockfile (or it doesn't have URLs). Run `mise lock` and commit.

## See also

- `mise-trust-and-security` — paranoid mode and provenance
- `mise-ci-github-actions` — wiring lockfiles into CI
- <https://mise.jdx.dev/dev-tools/mise-lock.html>

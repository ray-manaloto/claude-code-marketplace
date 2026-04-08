---
name: mise-backends-overview
description: All 15 mise backends (aqua, asdf, cargo, conda, dotnet, forgejo, gem, github, gitlab, go, http, npm, pipx, s3, spm, ubi, vfox), their use cases, security profile, and the official preference order for picking one. Use when deciding how to install a tool, debugging "no backend found", or recommending a backend for a new tool.
---

# Backends overview

Backends are the package ecosystems mise installs tools from. A tool is referenced as `<backend>:<id>` (e.g., `npm:prettier`, `aqua:BurntSushi/ripgrep`), or as a bare short name that the registry maps to a backend.

## Official preference order (from `mise.jdx.dev/registry.html`)

When picking a backend for a **new** tool — both for `mise.toml` and for adding to the upstream registry — use this order:

1. **`aqua:`** — most features and security, no plugins required. **Default choice.** Backed by the aqua-registry which has cryptographic verification (cosign / SLSA / minisign / GitHub attestations) built in.
2. **`github:` / `gitlab:` / `forgejo:`** — for tools not in aqua but available as releases on the respective forge.
3. **`pipx:`** — Python tools. Requires Python (mise can install it).
4. **`npm:`** — Node tools. Requires Node.
5. **`go:` / `cargo:` / `dotnet:`** — last-resort when no precompiled binary exists. These compile from source, which is slow.
6. **Core tools** (unprefixed) — `node`, `python`, `go`, `ruby`, `java`, `rust`, `bun`, `deno`, `zig`, `swift`, `dotnet`, `elixir`, `erlang`. These are built into mise and have specialized install logic.
7. **NEVER add new `vfox:` or `asdf:` entries** — these backends still work for existing tools, but the registry no longer accepts new entries due to supply-chain risks (they execute Lua/bash plugin code).

## The 15 backends in detail

| Backend | Format | Example | Lockfile | Notes |
|---|---|---|---|---|
| **`aqua:`** | aqua-registry (declarative TOML) | `aqua:cli/cli` | ✅ full + provenance | Default. Use first. |
| **`github:`** | GitHub releases (asset matcher) | `github:BurntSushi/ripgrep` | ✅ full + provenance | Use when no aqua entry |
| **`gitlab:`** | GitLab releases | `gitlab:owner/repo` | ✅ full | |
| **`forgejo:`** | Forgejo releases | `forgejo:host/owner/repo` | ⚠️ | |
| **`ubi:`** | [ubi](https://github.com/houseabsolute/ubi) (universal binary installer) | `ubi:owner/repo` | ⚠️ checksum + size | |
| **`http:`** | Arbitrary URL with checksum | see below | ✅ full | Most flexible — define URL per platform |
| **`s3:`** _(experimental)_ | Private S3 buckets | `s3:bucket/path` | ⚠️ | Internal tools |
| **`pipx:`** | PyPI via pipx | `pipx:black` | 📝 version | Auto-depends on python + uv |
| **`npm:`** | npm registry | `npm:prettier` | 📝 version | Auto-depends on node |
| **`cargo:`** | crates.io | `cargo:cargo-edit` | 📝 version | Compiles from source |
| **`go:`** | Go modules | `go:github.com/user/tool` | 📝 version | Compiles from source |
| **`gem:`** | RubyGems | `gem:rubocop` | 📝 version | Auto-depends on ruby |
| **`dotnet:`** _(experimental)_ | .NET tools | `dotnet:dotnet-ef` | 📝 version | |
| **`conda:`** _(experimental)_ | conda packages | `conda:numpy` | 📝 version | |
| **`spm:`** _(experimental)_ | Swift Package Manager | `spm:owner/repo` | ⚠️ | |
| **`asdf:`** | asdf plugins (bash) | `asdf:user/asdf-plugin` | 📝 version only | **Existing only** — runs arbitrary bash |
| **`vfox:`** | vfox plugins (Lua) | `vfox:user/vfox-plugin` | ⚠️ partial + provenance | **Existing only** — runs arbitrary Lua |

Plus **core tools** (no prefix needed): `bun`, `deno`, `dotnet`, `elixir`, `erlang`, `go`, `java`, `node`, `python`, `ruby`, `rust`, `swift`, `zig`.

## `http:` — the flexible escape hatch

When a tool ships as a tarball or zip but isn't on aqua or github releases, use `http:` with per-platform URL/checksum:

```toml
[tools."http:my-tool"]
version = "1.0.0"

[tools."http:my-tool".platforms]
macos-arm64 = {
  url = "https://example.com/my-tool-1.0.0-macos-arm64.tar.gz",
  checksum = "sha256:abc123...",
}
linux-x64 = {
  url = "https://example.com/my-tool-1.0.0-linux-x64.tar.gz",
  checksum = "sha256:def456...",
}
```

Alternative dotted notation:

```toml
[tools."http:my-tool"]
version = "1.0.0"
platforms.macos-arm64.url = "https://example.com/..."
platforms.macos-arm64.checksum = "sha256:..."
```

## Disabling a backend

```sh
mise settings disable_backends=asdf
```

This prevents mise from ever resolving via the asdf backend. `asdf` is disabled by default on Windows.

## Listing the registry

```sh
mise registry              # all aliases
mise registry node          # what node resolves to (and alternatives)
mise search ripgrep         # fuzzy search
mise use                    # interactive TUI to pick a tool
```

## Custom backends (plugin development)

You can build your own backend as a plugin — this is different from asdf/vfox plugins. See `mise.jdx.dev/backend-plugin-development.html`. A custom backend can install many tools from a single ecosystem.

## See also

- `mise-tool-versioning` — version syntax for `[tools]`
- `mise-trust-and-security` — backend security profiles
- `mise-lockfile` — which backends support full asset tracking
- <https://mise.jdx.dev/dev-tools/backends/>

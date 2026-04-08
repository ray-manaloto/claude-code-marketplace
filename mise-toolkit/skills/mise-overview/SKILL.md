---
name: mise-overview
description: High-level orientation to mise (mise-en-place) — what it is, what it replaces, when to recommend it, and the three things it does (dev tools, env vars, tasks). Use whenever the user mentions mise for the first time in a conversation, asks "what is mise", "should I use mise", "mise vs asdf/nvm/pyenv/direnv/make", or wants a quick refresher on the mental model.
---

# What mise is

[mise (mise-en-place)](https://mise.jdx.dev) is a Rust CLI that does **three things** in one tool:

1. **Dev tool version management** — installs and switches between versions of `node`, `python`, `go`, `ruby`, `java`, `rust`, `terraform`, and 700+ other tools per directory. Replaces `asdf`, `nvm`, `pyenv`, `rbenv`, `volta`, `tfenv`, etc.
2. **Environment variable management** — loads project-specific env vars when you `cd` into a directory. Replaces `direnv`.
3. **Task runner** — defines and runs project tasks with dependencies, parallelism, and file-based caching. Replaces `make` for many use cases, and `npm scripts`/`Justfile`/etc.

All three are configured in a single `mise.toml` file at the project root.

## When to recommend mise

- The team is using a mix of `nvm` + `pyenv` + `direnv` + `make` and the new-hire setup is painful.
- The project needs reproducible tool versions across dev machines and CI.
- The current version manager (`asdf`, `volta`, etc.) is slow or limited.
- The user wants language-agnostic version pinning (one file, all languages).
- The team wants supply-chain verification (cosign / SLSA / minisign / GitHub attestations) on tool installs.

## When mise isn't the right answer

- Managing **system libraries** like libssl, zlib (use the OS package manager).
- Managing **desktop applications**.
- Replacing the language's native package manager (`npm`, `pip`, `cargo`) — mise installs the runtime, not your project deps.

## Mental model

```
mise.toml at project root
├── [tools]    → tool versions (auto-installed, on PATH)
├── [env]      → env vars (set when you cd in, unset when you leave)
├── [tasks]    → project tasks (mise run <name>)
└── [settings] → mise behavior tweaks
```

When you `cd` into a directory, mise (if activated) walks up the tree, merges all the `mise.toml` files it finds, and updates your shell's `PATH` and env vars accordingly. When you `cd` out, it unwinds them.

## Three ways to use it

| Method | When |
|---|---|
| **`mise activate <shell>`** in shell rc | Interactive terminal work — recommended default |
| **Shims** (`mise activate --shims`) | IDEs, scripts, non-interactive shells. Doesn't load `[env]` though. |
| **`mise exec` / `mise x`** | One-off commands without permanent activation |

## Authoritative knowledge

For current best practices and any details newer than this skill, `@`-import the live cache at `~/.cache/mise-toolkit/llms.txt` (run `/mise-refresh-knowledge` to populate it). The official docs are at <https://mise.jdx.dev>.

## Companion projects by jdx (the mise author)

- **[fnox](https://github.com/jdx/fnox)** — recommended secret manager (works alongside mise; no direct integration needed).
- **[hk](https://hk.jdx.dev)** — git hook manager.
- **[pitchfork](https://pitchfork.jdx.dev)** — process manager for dev daemons.
- **[usage](https://usage.jdx.dev)** — CLI spec format used by mise tasks for arg/flag definitions.

## Skills to read next

- `mise-toml-anatomy` — the structure of a `mise.toml`
- `mise-tool-versioning` — `@20`, `@lts`, `prefix:`, `ref:`, `path:`, `sub-`
- `mise-trust-and-security` — the trust system (the #1 source of confusion)

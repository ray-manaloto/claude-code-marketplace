---
name: mise-elevator-pitch
description: A 60-second pitch for mise aimed at zero-knowledge users — what it is, what it replaces, why it's better, what it isn't, and the smallest possible mise.toml. Use whenever the user asks "what is mise", "is mise worth it", "should I try mise", or seems unsure whether to adopt it.
---

# mise in 60 seconds

## One sentence

mise is a single Rust CLI that replaces `nvm + pyenv + rbenv + asdf + tfenv + direnv + (parts of) make` — and works for any language, in one config file per project.

## The three things it does

1. **Dev tool versions** — installs and switches between versions of `node`, `python`, `go`, `ruby`, `java`, `rust`, `cmake`, `terraform`, … per directory. 700+ tools out of the box.
2. **Environment variables** — loads project env vars when you `cd` into a directory. Unloads them when you leave. (Replaces `direnv`.)
3. **Tasks** — `mise run test`, with parallel deps, last-modified caching, and file-tasks-as-bash-scripts. (Replaces large parts of `make`.)

All in one `mise.toml` at your project root.

## The smallest meaningful `mise.toml`

```toml
[tools]
node = "24"
python = "3.12"

[env]
NODE_ENV = "development"

[tasks.test]
run = "npm test && pytest"
```

That file gives you: pinned node 24, pinned python 3.12, `NODE_ENV=development` set in any shell that `cd`s here, and `mise run test` runs both test suites with both tools on PATH.

## Why it's better than what it replaces

| | mise | the alternative |
|---|---|---|
| **Speed** | ~5 ms shell-prompt overhead (Rust, no shims by default) | asdf bash + shims: ~120 ms per tool call |
| **Languages** | Every language, one config | nvm + pyenv + rbenv + tfenv = N tools, N configs |
| **Reproducibility** | `mise.lock` with checksums + provenance | pin-via-comment in `package.json` engines |
| **Security** | Cosign / SLSA / Minisign / GitHub attestations on aqua tools | asdf plugins = arbitrary bash from random GitHub users |
| **Env management** | `[env]` block — same file as tools | direnv `.envrc` = a separate tool |
| **Tasks** | First-class `[tasks]` with deps + caching | npm scripts (Node-only) or Makefile (1980s syntax) |
| **CI** | `jdx/mise-action@v3` — install + cache in 3 lines | n-version-managers × m-languages |

## Why it's better than `brew` / `apt` for dev tools

- **Per-project versions**, not system-wide. Project A uses node 18, project B uses node 24, no fighting.
- **Reproducible across teammates** via `mise.lock`.
- **Doesn't pollute the system**. Tools live in `~/.local/share/mise/installs/`.
- **No `sudo` ever needed**.

## What mise is NOT

- ❌ A system package manager. **Don't install `libssl` or `libpq` with mise.** Use `apt`/`brew` for system libraries.
- ❌ A desktop application installer.
- ❌ A replacement for `npm`/`pip`/`cargo`. mise installs the runtime; the runtime's package manager handles your project deps.

## Created by jdx

mise is built by [Jeff Dickey (@jdx)](https://github.com/jdx). Same author as `usage` (CLI spec), `pitchfork` (process manager), `hk` (git hooks), and `fnox` (secret manager). The mise ecosystem is a small set of focused tools.

## Try it in 30 seconds

```sh
curl https://mise.run | sh
~/.local/bin/mise use --global node@24
~/.local/bin/node -v   # v24.x.x
```

Or run `/mise-install` for a guided install with shell activation.

## Read next

- `mise-vs-alternatives` — head-to-head comparisons (asdf, nvm, pyenv, direnv, volta, brew, apt)
- `mise-overview` — the deeper mental model
- `mise-deployment-models` — host vs Docker vs devcontainer
- `mise-host-vs-mise-tools` — the #1 newbie mistake (system libs vs dev tools)

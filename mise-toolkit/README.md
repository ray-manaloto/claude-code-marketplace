# mise-toolkit

Claude Code plugin for **[mise](https://mise.jdx.dev)** (mise-en-place) — the polyglot dev tool, env, and task manager.

**Three audiences** in one plugin:

- 🆕 **Zero-knowledge users** — never heard of mise. The plugin pitches it, helps decide if it fits, installs it, activates it in your shell, and verifies everything works.
- 🛠️ **Adopters** — integrating mise into your own projects. Expert guidance on `mise.toml` design, lockfiles, env directives, secrets, tasks, CI, migrations from `nvm`/`pyenv`/`asdf`/etc., and the right backend per tool.
- 🧑‍💻 **Contributors** — hacking on the [jdx/mise](https://github.com/jdx/mise) Rust codebase. Build/test/lint commands, conventional-commit guardrails, the backend playbook, and e2e-test conventions.

## Self-awareness

The plugin stays current as mise evolves through three layers:

1. **[`mise mcp`](https://mise.jdx.dev/cli/mcp.html)** — bundled in `.mcp.json`. Agents read live `mise://tools|tasks|env|config` resources from any project's checkout, and call `run_task` directly. Requires `MISE_EXPERIMENTAL=1` (set automatically).
2. **`context7` MCP** — live docs from `mise.jdx.dev` and other libraries at query time.
3. **`/mise-refresh-knowledge`** — refreshes `~/.cache/mise-toolkit/llms.txt` from `mise.jdx.dev/llms.txt`. Skills `@`-import this cache.

Plus **active SessionStart nudging** — every Claude Code session prints a one-line mise context banner so you always know what mise sees in the current project.

## Install

Once published to GitHub:

```
/plugin marketplace add rmanaloto/mise-toolkit
/plugin install mise-toolkit@rmanaloto/mise-toolkit
```

Local development:

```
/plugin marketplace add ~/dev/github/rmanaloto/mise-claude-plugin
/plugin install mise-toolkit
```

After installing, run `/mise-refresh-knowledge` to seed the live docs cache. If you don't have mise yet, run `/mise-install` — the plugin will install mise itself, activate it in your shell, and verify it works.

## Components

### Slash commands (27)

| Command | Audience | Purpose |
|---|---|---|
| `/mise-explain` | newbie | 60-second elevator pitch |
| `/mise-recommend` | newbie | Asks 3-4 questions, recommends an adoption path |
| `/mise-install` ⚠️ | newbie | Cross-platform installer (user-only — no autonomous) |
| `/mise-activate-shell` | newbie | Adds `mise activate` to your shell rc with diff confirmation |
| `/mise-verify` | newbie | Comprehensive post-install health check |
| `/mise-quickref` | all | The 20-command daily cheat sheet |
| `/mise-reset-safe` ⚠️ | all | Recoverable reset (cache → tools → implode) — user-only |
| `/mise-doctor` | all | `mise doctor` + analysis |
| `/mise-trust-fix` | adopter | Diagnose & fix mise trust issues |
| `/mise-refresh-knowledge` | all | Refresh `~/.cache/mise-toolkit/llms.txt` |
| `/mise-init` | adopter | Survey project, propose `mise.toml` |
| `/mise-migrate` | adopter | Detect source vm → migrate to mise |
| `/mise-build` | contributor | `mise run build` |
| `/mise-test-e2e` | contributor | `mise run test:e2e [files...]` |
| `/mise-lint-fix` | contributor | `mise run lint-fix` |
| `/mise-render` | contributor | `mise run render` |
| `/mise-snapshots` | contributor | `mise run snapshots` |
| `/mise-dockerfile` | adopter | Generate a multi-stage Dockerfile with mise (builder + runtime, BuildKit cache) |
| `/mise-devcontainer` | adopter | Generate `.devcontainer/devcontainer.json` wired for mise + VSCode |
| `/mise-codespaces-prebuild` | adopter | Devcontainer + GitHub Codespaces prebuild workflow |
| `/mise-vscode-setup` | adopter | Wire VSCode to mise (extension or shims-on-PATH fallback) |
| `/mise-jetbrains-setup` | adopter | Wire JetBrains IDEs (intellij-mise plugin or asdf-symlink workaround) |
| `/mise-cpp-init` | adopter | Survey a C++ project and propose cmake/ninja/ccache/linker/clang-tools |
| `/mise-cpp-bootstrap` | adopter | One-shot default C++ toolchain (cmake + ninja + ccache + clang-tools) |
| `/mise-ai-init` | adopter | Install AI CLIs (claude, codex, aichat, gemini) with redacted env |
| `/mise-ai-keys` ⚠️ | adopter | Guided API key setup (keychain / 1Password / shell rc) — user-only |
| `/mise-cpp-ai-init` | adopter | Combined C++ + AI CLI setup in one merged `mise.toml` |

⚠️ = `disable-model-invocation: true` (user-triggered only — Claude cannot call autonomously).

### Subagents (9)

| Agent | Audience | Purpose |
|---|---|---|
| `mise-integration-architect` | adopter | Surveys a project, proposes a `mise.toml` using preferred backend per tool |
| `mise-migration-specialist` | adopter | Migrates from `nvm`/`fnm`/`volta`/`pyenv`/`rbenv`/`asdf`/`tfenv`/`direnv` |
| `mise-task-author` | adopter | Converts npm scripts / Makefiles / shell scripts into `[tasks]` |
| `mise-config-doctor` | all | Diagnoses bad `mise.toml`, runs `mise dr`, fixes trust |
| `mise-backend-expert` | contributor | Implements/reviews `src/backend/**` changes |
| `mise-e2e-author` | contributor | Writes bash e2e tests under `e2e/**` |
| `mise-deployment-architect` | adopter | Picks the right deployment model (host/Docker/devcontainer/Codespaces/CI) and coordinates handoffs |
| `mise-cpp-architect` | adopter | Surveys a C++ project and proposes cmake/ninja/ccache/linker/package-manager/clang-tools |
| `mise-ai-cli-architect` | adopter | Proposes the AI CLI half of a `mise.toml` with redacted env + ai-status task; hands keys to `/mise-ai-keys` |

### Skills (64)

**🆕 Zero-knowledge (9):** `mise-elevator-pitch`, `mise-vs-alternatives`, `mise-deployment-models`, `mise-install-paths`, `mise-host-vs-mise-tools` (the #1 newbie gotcha), `mise-shell-activation`, `mise-pathing-and-shims`, `mise-cli-cheatsheet`, `mise-troubleshooting`

**🛠️ Adopter (10):** `mise-overview`, `mise-toml-anatomy`, `mise-trust-and-security`, `mise-tool-versioning`, `mise-backends-overview`, `mise-tasks-toml`, `mise-env-directives`, `mise-lockfile`, `mise-ci-github-actions`, `mise-migrate-from-asdf`

**🐳 Deployment — v0.3 (10):** `mise-docker-patterns`, `mise-docker-base-images`, `mise-docker-bootstrap`, `mise-docker-multistage`, `mise-devcontainer-patterns`, `mise-codespaces`, `mise-vscode-integration`, `mise-jetbrains-integration`, `mise-neovim-integration`, `mise-ide-activation`

**⚙️ C++ — v0.4 (5):** `mise-cpp-toolchain-overview`, `mise-cpp-cmake-ninja-ccache`, `mise-cpp-linker-fast`, `mise-cpp-package-managers`, `mise-cpp-clang-tools`

**🤖 AI CLIs — v0.4 (3):** `mise-ai-cli-overview`, `mise-ai-cli-setup`, `mise-ai-cli-keys`

**📦 Language packs — v0.5 (10):** `mise-lang-node-overview`, `mise-lang-node-packages`, `mise-lang-python-overview`, `mise-lang-python-packages`, `mise-lang-go-overview`, `mise-lang-go-modules`, `mise-lang-ruby-overview`, `mise-lang-ruby-gems`, `mise-lang-rust-overview`, `mise-lang-rust-cargo`

**🔁 Migration — v0.5 (5):** `mise-migrate-from-nvm`, `mise-migrate-from-pyenv`, `mise-migrate-from-rbenv`, `mise-migrate-from-tfenv`, `mise-migrate-from-direnv`

**🍳 Cookbook — v0.6 (8):** `mise-cookbook-python-fastapi`, `mise-cookbook-node-nextjs`, `mise-cookbook-ruby-rails`, `mise-cookbook-terraform`, `mise-cookbook-docker-dev`, `mise-cookbook-cpp-cmake`, `mise-cookbook-neovim`, `mise-cookbook-go-service`

**🧑‍💻 Contributor (4):** `mise-contrib-overview`, `mise-contrib-add-backend`, `mise-contrib-add-registry`, `mise-contrib-write-e2e-test`

### Hooks (6)

| Event | Matcher | Script | Purpose |
|---|---|---|---|
| **SessionStart** | — | `detect-mise-context.sh` | Active nudge: prints mise version, project config, trust state, tool count, missing required env vars, lockfile status at every session start |
| **PostToolUse** | `Edit\|Write` | `validate-mise-config.sh` | If a `mise*.toml` was edited → run `mise cfg ls` to validate |
| **PostToolUse** | `Edit\|Write` | `lint-fix-rust.sh` | If a `*.rs` file in the jdx/mise repo was edited → `mise run lint-fix` |
| **PostToolUse** | `Edit\|Write` | `lint-dockerfile.sh` | If a `Dockerfile` mentioning mise was edited → warn about missing trust, cache mounts, musl, activate (non-blocking) |
| **PostToolUse** | `Edit\|Write` | `warn-plaintext-api-key.sh` | Warn if a file contains a plaintext Anthropic / OpenAI / Google key (non-blocking) |
| **PreToolUse** | `Bash` | `block-direct-e2e.sh` | Block direct invocation of jdx/mise's `e2e/test_*` files |

### MCP servers (2)

| Server | Purpose |
|---|---|
| `mise` | mise's own MCP — `mise://tools`, `mise://tasks`, `mise://env`, `mise://config`, `run_task` tool |
| `context7` | Live `mise.jdx.dev` docs (and any other library) at query time |

## Roadmap

| Version | Theme | Status |
|---|---|---|
| **v0.1** | Adopter + contributor base | ✅ shipped |
| **v0.2** | Zero-knowledge layer + SessionStart nudging | ✅ shipped |
| **v0.3** | Deployment — Docker, devcontainer, Codespaces, IDE patterns | ✅ shipped |
| **v0.4** | C++ + AI CLI vertical (claude/codex/gemini/aichat) | ✅ shipped |
| **v0.5** | Language packs (node/python/go/ruby/rust) + migration skills (nvm/pyenv/rbenv/tfenv/direnv) | ✅ shipped |
| **v0.6** | Cookbook recipes (FastAPI / Next.js / Rails / Terraform / Docker / C++ / Neovim / Go) | ✅ shipped (this release) |
| **v1.0** | LICENSE + CI validation workflow + public announcement | next |

## Recommended onboarding flow for new users

1. `/mise-explain` — get the 60-second pitch
2. `/mise-recommend` — answer a few questions for a personalized path
3. `/mise-install` — install mise (user-confirmed)
4. `/mise-activate-shell` — wire up your shell
5. `/mise-verify` — confirm everything works
6. `/mise-init` (in a project directory) — scaffold your first `mise.toml`
7. `/mise-quickref` — daily-use cheat sheet

The SessionStart hook will also nudge you about untrusted configs, missing tools, missing required env vars, and lockfile status every time you start a Claude Code session.

## License

TBD before public release.

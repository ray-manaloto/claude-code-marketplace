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

### Slash commands (17)

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

⚠️ = `disable-model-invocation: true` (user-triggered only — Claude cannot call autonomously).

### Subagents (6)

| Agent | Audience | Purpose |
|---|---|---|
| `mise-integration-architect` | adopter | Surveys a project, proposes a `mise.toml` using preferred backend per tool |
| `mise-migration-specialist` | adopter | Migrates from `nvm`/`fnm`/`volta`/`pyenv`/`rbenv`/`asdf`/`tfenv`/`direnv` |
| `mise-task-author` | adopter | Converts npm scripts / Makefiles / shell scripts into `[tasks]` |
| `mise-config-doctor` | all | Diagnoses bad `mise.toml`, runs `mise dr`, fixes trust |
| `mise-backend-expert` | contributor | Implements/reviews `src/backend/**` changes |
| `mise-e2e-author` | contributor | Writes bash e2e tests under `e2e/**` |

### Skills (23)

**🆕 Zero-knowledge (9):** `mise-elevator-pitch`, `mise-vs-alternatives`, `mise-deployment-models`, `mise-install-paths`, `mise-host-vs-mise-tools` (the #1 newbie gotcha), `mise-shell-activation`, `mise-pathing-and-shims`, `mise-cli-cheatsheet`, `mise-troubleshooting`

**🛠️ Adopter (10):** `mise-overview`, `mise-toml-anatomy`, `mise-trust-and-security`, `mise-tool-versioning`, `mise-backends-overview`, `mise-tasks-toml`, `mise-env-directives`, `mise-lockfile`, `mise-ci-github-actions`, `mise-migrate-from-asdf`

**🧑‍💻 Contributor (4):** `mise-contrib-overview`, `mise-contrib-add-backend`, `mise-contrib-add-registry`, `mise-contrib-write-e2e-test`

### Hooks (4)

| Event | Matcher | Script | Purpose |
|---|---|---|---|
| **SessionStart** | — | `detect-mise-context.sh` | Active nudge: prints mise version, project config, trust state, tool count, missing required env vars, lockfile status at every session start |
| **PostToolUse** | `Edit\|Write` | `validate-mise-config.sh` | If a `mise*.toml` was edited → run `mise cfg ls` to validate |
| **PostToolUse** | `Edit\|Write` | `lint-fix-rust.sh` | If a `*.rs` file in the jdx/mise repo was edited → `mise run lint-fix` |
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
| **v0.2** | Zero-knowledge layer + SessionStart nudging | ✅ shipped (this release) |
| **v0.3** | Scenarios — Docker, devcontainer, Codespaces, IDE patterns | planned |
| **v0.4** | C++ + AI CLI vertical (claude/codex/gemini) — uses `data/ai-cli-research.md` | planned |
| **v0.5** | Language packs (`mise-lang-*`) + remaining migration skills (nvm/pyenv/etc.) | planned |
| **v0.6** | Cookbook recipes (Python/Node/Ruby/Terraform/Docker/C++/Neovim) | planned |

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

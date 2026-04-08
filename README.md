# claude-code-marketplace

A curated marketplace of [Claude Code](https://claude.com/claude-code) plugins by [Raymond Manaloto](https://github.com/ray-manaloto).

> **Note**: the local repo lives at `~/dev/github/ray-manaloto/claude-code-plugins/`; the GitHub repo will be published as `ray-manaloto/claude-code-marketplace`.

## Philosophy

Each plugin in this marketplace is **dual-purpose** by design:

- **Useful to zero-knowledge users** discovering a tool or topic for the first time — installer, activation, decision aids, troubleshooting.
- **Useful to deep practitioners** integrating that tool into real projects — best-practice skills, scenario-specific agents, modern patterns.

Where possible, plugins are **self-aware** — they bundle MCP servers that let Claude read live project state from the underlying tool itself, rather than parsing CLI output. They also use `SessionStart` hooks to surface project context at the start of every Claude Code session, so you don't have to remember to ask.

## Install

```sh
/plugin marketplace add ray-manaloto/claude-code-marketplace
/plugin install <plugin-name>@ray-manaloto/claude-code-marketplace
```

For local development against this checkout:

```sh
/plugin marketplace add ~/dev/github/ray-manaloto/claude-code-plugins
/plugin install <plugin-name>
```

## Plugins

### [mise-toolkit](./mise-toolkit/) — `v0.2.0`

Claude Code plugin for **[mise](https://mise.jdx.dev)** (mise-en-place) — the polyglot dev tool, env, and task manager.

Three audiences in one plugin:

- 🆕 **Zero-knowledge users** — never heard of mise. The plugin pitches it, helps decide if it fits, installs it, activates it in your shell, and verifies everything works.
- 🛠️ **Adopters** — integrating mise into your own projects. Expert guidance on `mise.toml` design, lockfiles, env directives, secrets, tasks, CI, migrations from `nvm`/`pyenv`/`asdf`/etc., and the right backend per tool.
- 🧑‍💻 **Contributors** — hacking on the [jdx/mise](https://github.com/jdx/mise) Rust codebase. Build/test/lint commands, conventional-commit guardrails, the backend playbook, and e2e-test conventions.

**17 commands · 6 agents · 23 skills · 4 hooks · 2 MCP servers**

Bundles mise's own MCP server for live `mise://tools|tasks|env|config` resource access. SessionStart hook prints mise context (version, project config, trust state, tool count, lockfile status) every session.

[Read the full mise-toolkit README →](./mise-toolkit/README.md)

## Roadmap

| Plugin | Status | Description |
|---|---|---|
| **mise-toolkit** | ✅ v0.2.0 (shipped) | Polyglot dev tool / env / task manager |
| **devcontainer-toolkit** | 🔭 planned | Docker base images, devcontainer.json patterns, Codespaces, IDE wiring |
| **cpp-toolkit** | 🔭 planned | C++ Linux dev — gcc/clang, cmake/ninja/ccache, conan/vcpkg, clangd, sanitizers |
| **ai-cli-toolkit** | 🔭 planned | Subscription-based AI CLI orchestration (Claude Code, OpenAI Codex, Google Gemini, aichat) — secret management, multi-model workflows |

## Contributing

This marketplace is currently single-author. If you have plugin ideas or feedback, open an issue at <https://github.com/ray-manaloto/claude-code-marketplace/issues>.

## License

TBD before public release. Each plugin will declare its own license when published.

## Author

[Raymond Manaloto](https://github.com/ray-manaloto) — `ray.manaloto@gmail.com`

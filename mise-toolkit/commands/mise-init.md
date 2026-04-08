---
description: Survey the current project and propose a mise.toml using modern best practices
---

Delegate to the `mise-integration-architect` agent. The agent will:

1. Survey the project for existing version-manager artifacts (`.nvmrc`, `.python-version`, `.tool-versions`, `Pipfile`, `package.json` engines, `go.mod`, `Gemfile`, `.ruby-version`, `.java-version`, `.terraform-version`, `.envrc`, `Makefile`, npm scripts).
2. Detect the languages and their current pinned versions.
3. Propose a `mise.toml` that uses the **preferred backend per tool** (aqua > github/gitlab > pipx/npm/go/cargo/dotnet — never new vfox/asdf entries).
4. Identify env vars worth lifting from `.env` / `.envrc` into `[env]` (with `redact = true` for secrets).
5. Convert npm scripts / Makefile targets into `[tasks]` (delegating to `mise-task-author`).
6. Suggest enabling lockfiles (`mise lock`) and pinning `min_version`.
7. Show a unified diff of the proposed `mise.toml` and ask for confirmation before writing.

Do not write the file without user confirmation. Do not run `mise install` automatically — let the user trust and install.

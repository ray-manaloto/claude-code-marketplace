---
description: Detect the source version manager and migrate the project to mise
argument-hint: "[source: nvm|fnm|volta|pyenv|poetry|uv|rbenv|asdf|jenv|sdkman|tfenv|direnv]"
---

Delegate to the `mise-migration-specialist` agent.

If `$ARGUMENTS` is provided, migrate from that source. Otherwise, autodetect by checking for these markers in the current directory:

| Marker file | Source |
|---|---|
| `.nvmrc` | nvm / fnm |
| `package.json` with `volta` field | volta |
| `.python-version` (without `.tool-versions`) | pyenv |
| `pyproject.toml` with `[tool.poetry]` | poetry |
| `uv.lock` | uv |
| `.ruby-version` | rbenv / chruby |
| `.tool-versions` | asdf |
| `.java-version` / `.sdkmanrc` | jenv / sdkman |
| `.terraform-version` | tfenv |
| `.envrc` | direnv |

For each source, the migration specialist will: read the source's pinned versions, generate the equivalent `mise.toml` using the preferred backend, preserve env vars (lifting them into `[env]` where appropriate), and document the deprecation steps for the old tool.

Show the proposed `mise.toml` as a diff and ask for confirmation before writing.

# AI CLI Registry Research

Source: <https://mise.jdx.dev/registry.html> (fetched 2026-04-07)
Purpose: canonical mise registry mappings for AI/LLM CLIs, used by the v0.4
C++ + AI vertical (mise-cookbook-cpp-ai, mise-ai-cli-setup, /mise-cpp-ai-init).

## Tools confirmed in the mise registry

| Short name | Backends (priority order) | Notes |
|---|---|---|
| `claude` | `aqua:anthropics/claude-code`, `http:claude`, `npm:@anthropic-ai/claude-code` | Anthropic Claude Code CLI. Aqua is the preferred backend. |
| `codex` | `aqua:openai/codex`, `npm:@openai/codex` | OpenAI Codex CLI. Aqua preferred. |
| `aichat` | `aqua:sigoden/aichat` | Multi-provider AI shell (OpenAI, Anthropic, Gemini, Ollama) — useful as a model-agnostic fallback. |
| `codebuff` | `npm:codebuff` | |

## Tools NOT in the registry (as of 2026-04-07)

| Tool | Workaround | Verify |
|---|---|---|
| **gemini** (Google Gemini CLI) | Likely `npm:@google/gemini-cli`. Use direct npm reference until/unless added to registry. | User must verify the package name on npmjs.com and `npm view <name>` before pinning. |

## Recommended `mise.toml` block for the v0.4 AI CLI vertical

```toml
[tools]
node = "24"
claude = "latest"            # registry → aqua:anthropics/claude-code
codex  = "latest"            # registry → aqua:openai/codex
aichat = "latest"            # registry → aqua:sigoden/aichat (multi-provider fallback)
"npm:@google/gemini-cli" = "latest"  # NOT in registry — verify package name

[env]
ANTHROPIC_API_KEY = { required = "Get from console.anthropic.com → API Keys", redact = true }
OPENAI_API_KEY    = { required = "Get from platform.openai.com → API keys", redact = true }
GEMINI_API_KEY    = { required = "Get from aistudio.google.com/app/apikey", redact = true }

[redactions]
patterns = ["*_API_KEY", "*_TOKEN", "*_SECRET"]

[tasks.ai-status]
description = "Verify AI CLIs are installed and authenticated"
run = [
  "claude --version",
  "codex --version",
  "aichat --version",
  "gemini --version",
]
```

## Refresh

When v0.4 is built, re-fetch the registry and verify these mappings — registry entries
change. Also check whether `gemini` has been added by then (open question:
<https://github.com/jdx/mise/discussions> for "gemini" or "google-cli").

---
description: Install AI CLIs (claude, codex, aichat, gemini) via mise with redacted API key env vars
---

Delegate to the `mise-ai-cli-architect` agent to install the AI CLI stack. Authoritative registry mappings come from `mise-toolkit/data/ai-cli-research.md`:

- `claude` → `aqua:anthropics/claude-code` (preferred)
- `codex` → `aqua:openai/codex` (preferred)
- `aichat` → `aqua:sigoden/aichat`
- `gemini` → `npm:@google/gemini-cli` (not in registry yet)

## The canonical mise.toml block to propose

```toml
[tools]
node = "24"
claude = "latest"
codex  = "latest"
aichat = "latest"
"npm:@google/gemini-cli" = "latest"

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

## Steps

1. Ask the user which subset of CLIs they want — all four, or a subset. Default is all four.
2. Check for an existing `mise.toml`. If present, propose merging the `[tools]` / `[env]` / `[tasks]` blocks rather than overwriting.
3. Show a diff of the proposed changes and ask for confirmation.
4. After writing, point the user at `/mise-ai-keys` to set up the API keys — **never** write plaintext keys into any file.
5. After keys are set, suggest running `mise run ai-status` to verify.

## What to avoid

- Writing plaintext API keys anywhere.
- Using a non-aqua backend for claude/codex when the aqua one exists.
- Assuming `gemini` is in the registry (it isn't as of 2026-04-07 — verify at build time).
- Overwriting an existing `mise.toml` without showing a diff first.

For the underlying rationale, read `mise-ai-cli-overview` and `mise-ai-cli-setup`.

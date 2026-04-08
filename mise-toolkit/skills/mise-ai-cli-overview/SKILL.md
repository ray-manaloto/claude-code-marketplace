---
name: mise-ai-cli-overview
description: The four main AI CLIs compared — Claude Code, OpenAI Codex, Google Gemini, and aichat — with provider lock-in, model-agnostic fallback strategy, and why installing all four via mise is a lightweight dev-environment win. Use when picking AI CLIs for a project.
---

# AI CLIs for dev — claude, codex, gemini, aichat

The AI-assisted coding landscape has consolidated around a few CLIs. All four are installable via mise (with one caveat for gemini). Running more than one is normal — they have different strengths and you'll want a model-agnostic fallback.

## The four CLIs

| CLI | Provider | Model backbone | Primary strength | Registry backend |
|---|---|---|---|---|
| **Claude Code** (`claude`) | Anthropic | Claude (Sonnet/Opus) | Agentic coding, long-context refactors, tool use, plugins | `aqua:anthropics/claude-code` |
| **Codex** (`codex`) | OpenAI | GPT-5 / o-series | Fast completions, strong at one-shot tasks | `aqua:openai/codex` |
| **Gemini CLI** (`gemini`) | Google | Gemini 2.x / 3.x | Huge context window, multimodal, Google Workspace integration | `npm:@google/gemini-cli` (not in registry yet) |
| **aichat** | Any (OpenAI/Anthropic/Gemini/Ollama/...) | Multi-provider adapter | Model-agnostic fallback, local models via Ollama | `aqua:sigoden/aichat` |

## Why install more than one

1. **No single provider is best at everything.** Claude excels at agentic workflows; Codex is fastest for simple completions; Gemini has the biggest context window; aichat lets you use local models.
2. **Rate limits and outages.** When one provider is down (happens more than you'd think), having another pre-installed means you're not blocked.
3. **Cross-model verification.** For critical code, ask two models the same question and compare.
4. **Bring-your-own-key flexibility.** Different projects may have different provider budgets.

The cost of installing all four is negligible — a few MB of binaries + a few env vars. The upside is you're never stuck when one is unavailable.

## aichat as the fallback layer

aichat is special: it's not tied to a specific provider. It speaks to OpenAI, Anthropic, Gemini, Ollama, Cohere, and more via config. One CLI, many backends.

Use it when:
- You want to query a **local** model (Ollama, llama.cpp) for privacy-sensitive code.
- You want to A/B test across providers without switching CLIs.
- Your provider-specific CLI is broken and you need a quick fallback.
- You're scripting and want a stable CLI surface regardless of which provider you're hitting this month.

Config lives at `~/.config/aichat/config.yaml`:

```yaml
model: claude:claude-sonnet-4-5
clients:
  - type: claude
    api_key: $ANTHROPIC_API_KEY
  - type: openai
    api_key: $OPENAI_API_KEY
  - type: gemini
    api_key: $GEMINI_API_KEY
  - type: ollama
    api_base: http://localhost:11434
```

## Provider lock-in and why it matters

Each vendor's CLI is optimized for their models and their tool-calling conventions. Switching between them means:
- Different prompt styles (Claude likes long context; Codex prefers terse).
- Different tool-use protocols.
- Different plugin / agent ecosystems (Claude Code has plugins; Codex doesn't, yet).
- Different pricing models (per-token vs per-request vs subscription).

You won't fully escape lock-in by installing all four, but you'll have off-ramps when you need them.

## The mise.toml block

```toml
[tools]
node = "24"                # required for Gemini CLI (npm)
claude = "latest"          # aqua:anthropics/claude-code
codex = "latest"           # aqua:openai/codex
aichat = "latest"          # aqua:sigoden/aichat
"npm:@google/gemini-cli" = "latest"

[env]
ANTHROPIC_API_KEY = { required = "console.anthropic.com → API Keys", redact = true }
OPENAI_API_KEY    = { required = "platform.openai.com → API keys", redact = true }
GEMINI_API_KEY    = { required = "aistudio.google.com/app/apikey", redact = true }

[redactions]
patterns = ["*_API_KEY", "*_TOKEN", "*_SECRET"]
```

`node = "24"` is needed because Gemini CLI is an npm package. Even if you don't otherwise use Node, mise will install it transparently.

## Keys stay out of mise.toml

**Never** write the actual key values into `mise.toml`. The `required = "…"` form is a *prompt* — when the variable is missing, mise tells the user where to get it. The value is set via their shell rc, keychain, or secrets manager. See `mise-ai-cli-keys` for the threat model.

## The `ai-status` task

A simple sanity check that all four CLIs are installed and their keys are set:

```toml
[tasks.ai-status]
description = "Verify AI CLIs are installed and authenticated"
run = [
  "claude --version",
  "codex --version",
  "aichat --version",
  "gemini --version",
]
```

If any CLI prints an auth error instead of a version, that tells you the key isn't loaded. Run `/mise-ai-keys` to fix.

## Anti-patterns

- **Installing all four via curl/brew/pip**, bypassing mise. Version pinning goes out the window.
- **Committing a `.env` with keys** "just for this project". Never.
- **Using `mise set ANTHROPIC_API_KEY=…`** — writes plaintext to `mise.local.toml`. Not a secret store.
- **Assuming the gemini CLI package name is stable.** It's changed twice in a year. Verify with `npm view @google/gemini-cli` before pinning.
- **Only installing one CLI** "to keep it simple". The day that provider is down is the day you'll wish you had a fallback.

## See also

- `mise-ai-cli-setup` — the full mise.toml wiring and the `ai-status` task.
- `mise-ai-cli-keys` — threat model, keychain/1Password integration, rotation.
- `mise-env-directives` — how `required = ""` and `redact = true` work.
- `data/ai-cli-research.md` — authoritative registry mappings (fetched 2026-04-07).
- `/mise-ai-init` — scaffold this from a project.

---
name: mise-ai-cli-setup
description: The canonical mise.toml pattern for AI CLIs — [tools] block with aqua backends, [env] with required + redact directives, [redactions] patterns, and the ai-status task. Covers production alternatives (keychain, 1Password CLI, doppler) for environments beyond shell rc files. Use when wiring AI CLIs into a project.
---

# AI CLI setup — the canonical mise.toml pattern

This is the pattern that goes into every project that uses AI CLIs. Copy it, adjust the CLI list, and let `[env]` + `[redactions]` do the heavy lifting.

## The canonical block

```toml
[tools]
node = "24"                            # required for Gemini (npm)
claude = "latest"                      # aqua:anthropics/claude-code
codex  = "latest"                      # aqua:openai/codex
aichat = "latest"                      # aqua:sigoden/aichat
"npm:@google/gemini-cli" = "latest"    # not in registry; verify package name

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

## What each piece does

### `[tools]`

- **`node = "24"`** — Gemini CLI is an npm package, so Node is a prerequisite. mise will install it even if you don't use Node for anything else. Pin a major version; `latest` for node is unstable.
- **Short names** (`claude`, `codex`, `aichat`) — mise's registry resolves these to the preferred backend (aqua for all three). You don't need to spell out `aqua:anthropics/claude-code`.
- **`"npm:@google/gemini-cli"`** — not in the registry as of 2026-04-07. Use the full `npm:` form. Verify the package name with `npm view @google/gemini-cli` before committing.

### `[env]` with `required`

`required = "<help text>"` marks the var as mandatory. If it's missing, mise prints the help text ("Get from console.anthropic.com → API Keys") in the SessionStart nudge and when running tasks. This is the right pattern for onboarding — new contributors immediately know what to do.

### `[env]` with `redact = true`

`redact = true` hides the value in `mise env` output, `mise task ls`, and task logs. It is **not** a secret-management system — it only redacts the value from mise's own output. The value still has to be set in the environment somehow (shell rc, keychain, etc.).

### `[redactions]`

```toml
[redactions]
patterns = ["*_API_KEY", "*_TOKEN", "*_SECRET"]
```

This is a belt-and-suspenders layer: *any* env var matching these globs gets redacted, even if it wasn't explicitly marked `redact = true`. Covers the case where a third-party tool sets an env var you didn't anticipate.

### `[tasks.ai-status]`

One command to verify everything works end-to-end. `mise run ai-status` hits all four CLIs; any that fail auth print an error instead of a version. Great for onboarding and for CI smoke tests.

## Where the actual keys live

The `[env]` block only *declares* the variables. The values come from one of four places, in order of preference for production:

### 1. macOS Keychain (local dev, single user)

```sh
# One-time setup
security add-generic-password -a "$USER" -s ANTHROPIC_API_KEY -w

# In ~/.zshrc
export ANTHROPIC_API_KEY="$(security find-generic-password -a $USER -s ANTHROPIC_API_KEY -w)"
```

Benefits: native OS-level encryption, no plaintext files, survives reboots.

### 2. 1Password CLI (teams, dev + prod)

```sh
# One-time: store in a 1Password vault
op item create --category='API Credential' --title='Anthropic' credential='…'

# In ~/.zshrc (runs on every new shell)
export ANTHROPIC_API_KEY="$(op read 'op://Private/Anthropic/credential')"
```

Benefits: shared team vaults, audit log, easy rotation, works the same in dev and CI.

### 3. Secret manager (production)

- **AWS Secrets Manager** → `aws secretsmanager get-secret-value` in a task hook.
- **HashiCorp Vault** → `vault kv get -field=api_key …`.
- **Doppler** → `doppler run -- mise run <task>` wraps every command with env injection.

Use these when deploying to production. Never put prod keys in a dev's shell rc.

### 4. Shell rc file (simplest, least secure)

```sh
# ~/.zshrc
export ANTHROPIC_API_KEY="sk-ant-api03-…"
```

Plaintext on disk. Fine for solo hobby work; not fine for anything involving money or customer data.

## What about `mise set`?

**Don't use `mise set` for API keys.** It writes plaintext to `mise.local.toml`. That file is usually git-ignored, but "usually" isn't good enough for secrets. Use one of the four methods above instead.

`mise set` is fine for non-secret env vars (`LOG_LEVEL=debug`, `DATABASE_NAME=dev`, etc.).

## CI integration

In GitHub Actions:

```yaml
- uses: jdx/mise-action@v3
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
- run: mise run ai-status
```

The env block at the step level injects the GitHub Actions secrets into mise's environment. Because of `redact = true`, the values won't leak into the Actions log.

## Subset installations

Don't want all four? Delete the lines you don't need:

```toml
[tools]
claude = "latest"  # just Claude Code

[env]
ANTHROPIC_API_KEY = { required = "…", redact = true }
```

aichat is a particularly good candidate to keep even if you're dropping the others — it's your fallback when any single provider is down.

## Anti-patterns

- **Committing `.env` with keys in it.**
- **`mise set ANTHROPIC_API_KEY=sk-…`** — plaintext on disk.
- **Hardcoding keys in `mise.toml` values** — same problem.
- **Forgetting `[redactions]`** — keys leak into `mise env` and task logs.
- **Using `latest` for node** — node `latest` has broken npm installs before; pin a major.

## See also

- `mise-ai-cli-overview` — why multiple CLIs.
- `mise-ai-cli-keys` — deeper dive on key storage and rotation.
- `mise-env-directives` — the `[env]` directive reference.
- `data/ai-cli-research.md` — authoritative registry mappings.
- `/mise-ai-init` — scaffold this block.
- `/mise-ai-keys` — guided key-setting walkthrough.

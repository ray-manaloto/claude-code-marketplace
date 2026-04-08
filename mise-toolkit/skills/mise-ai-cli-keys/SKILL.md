---
name: mise-ai-cli-keys
description: Security-focused guide for AI CLI API keys — threat model, storage options (shell rc / keychain / 1Password / doppler), rotation cadence, detection of accidental plaintext leaks, and why `mise set` is never the right answer for secrets. Use when setting up or rotating keys.
---

# AI CLI keys — threat model and storage

API keys for AI providers are real money. A leaked Anthropic or OpenAI key can rack up thousands of dollars before you notice. Treat them with the same seriousness as database passwords.

## Threat model

What you're defending against, ranked by likelihood:

1. **Accidental git commit** — the #1 way keys leak. `.env` gets staged, pushed, indexed by bots within minutes.
2. **Build log / CI log leak** — a task runs `env` and the key appears in plaintext in a public CI log.
3. **Shared screen / demo** — you run `echo $ANTHROPIC_API_KEY` during a screen share.
4. **Compromised dev machine** — malware or a bad npm package reads your shell env.
5. **Dumped process memory** — hard to mitigate; lowest likelihood unless you're a target.

Most of your effort should go into preventing #1 and #2.

## Storage options, ranked

### Tier 1 — safe for production and dev

**macOS Keychain** (single user, local dev)
```sh
security add-generic-password -a "$USER" -s ANTHROPIC_API_KEY -w
# ~/.zshrc:
export ANTHROPIC_API_KEY="$(security find-generic-password -a $USER -s ANTHROPIC_API_KEY -w)"
```

**1Password CLI** (teams)
```sh
# ~/.zshrc:
export ANTHROPIC_API_KEY="$(op read 'op://Private/Anthropic/credential')"
```

**`pass`** (Linux, GPG-backed)
```sh
pass insert api/anthropic
# ~/.bashrc:
export ANTHROPIC_API_KEY="$(pass api/anthropic)"
```

**GNOME libsecret** (Linux GUI desktops)
```sh
secret-tool store --label='Anthropic API' service anthropic
# ~/.bashrc:
export ANTHROPIC_API_KEY="$(secret-tool lookup service anthropic)"
```

**Doppler / Infisical / Vault** (secret managers for teams)
```sh
doppler run -- mise run <task>
```

**AWS Secrets Manager** (AWS-native prod)
```sh
export ANTHROPIC_API_KEY="$(aws secretsmanager get-secret-value --secret-id anthropic/prod --query SecretString --output text)"
```

### Tier 2 — okay for hobby work, risky for anything real

**Plaintext in `~/.zshrc`** — readable by anything that reads your home dir. Fine for personal projects where the blast radius is your own account.

**Plaintext in `.env`** — same problem, plus the risk of `git add .` committing it. Always list `.env*` in `.gitignore` and double-check with `git status` before committing.

### Tier 3 — actively wrong

- **`mise set ANTHROPIC_API_KEY=…`** — writes to `mise.local.toml` in plaintext. Not a secret store.
- **Hardcoded in `mise.toml`** — commits the key to git. Instant leak.
- **`export ANTHROPIC_API_KEY="…"`** in a project's `bin/dev` script committed to git — same problem.
- **Passing keys via `docker build --build-arg`** — build args are visible in `docker history`.

## The redact layer (not a substitute)

`redact = true` in `mise.toml` removes the value from `mise env` output and task logs:

```toml
[env]
ANTHROPIC_API_KEY = { required = "…", redact = true }

[redactions]
patterns = ["*_API_KEY", "*_TOKEN", "*_SECRET"]
```

This is useful: it stops accidents like `mise task run deploy 2>&1 | tee log.txt` from capturing the key in `log.txt`.

But redaction is **after-the-fact**. If the key is already in your shell env, anything that reads `/proc/<pid>/environ` or runs `env` by hand still sees it. Redaction protects mise-mediated output, not your whole system.

## Rotation cadence

Rotate:
- **Every 90 days** by default.
- **Immediately** when a key might have leaked (accidental commit, shared screen, lost laptop, team member departing).
- **When migrating** between personal and company accounts.
- **When a provider announces a breach** or deprecates an older key format.

Providers let you create multiple concurrent keys — use this to rotate without downtime: create new, update env, test, revoke old.

Label keys in the provider dashboard so you know which machine / service is using which key. `"ray-macbook-personal"`, `"ci-github-actions"`, `"laptop-2026-04"` — specific labels make revocation easy.

## Detection — catching a plaintext leak

The v0.3 `lint-dockerfile.sh` hook was limited to Dockerfiles. In v0.4, `warn-plaintext-api-key.sh` runs on every `Edit` / `Write` and grep-matches obvious key formats:

- `sk-ant-…` — Anthropic
- `sk-…` — OpenAI legacy
- `sk-proj-…` — OpenAI project keys
- `AIzaSy…` — Google API keys

It's non-blocking — just a stderr warning. If it fires, **assume the key is compromised and rotate it**. Even if the file hasn't been committed yet, the key has now been in your Claude Code session's context window — out of your hands.

## Pre-commit hook (extra layer)

Beyond the mise hook, add a real pre-commit hook that blocks commits containing keys:

```sh
# .git/hooks/pre-commit
#!/usr/bin/env bash
if git diff --cached | grep -qE '(sk-ant-api[0-9]{2}|sk-proj-|sk-[a-zA-Z0-9]{48}|AIzaSy[a-zA-Z0-9-_]{33})'; then
  echo "ERROR: commit contains what looks like an API key. Refusing to commit."
  exit 1
fi
```

Better: use `gitleaks` or `trufflehog` — dedicated tools with vastly better regex coverage.

```toml
[tools]
"aqua:gitleaks/gitleaks" = "latest"

[tasks."secrets:scan"]
run = "gitleaks detect --source=. --no-git"
```

## What to do if a key leaks

Within minutes:
1. **Revoke the key** in the provider dashboard. Don't delete yet — you need the key ID for the audit log.
2. **Check the audit log** (Anthropic console → Usage / OpenAI dashboard → Usage) for unusual activity in the last 24 hours.
3. **Rotate** to a new key; update storage (keychain/1Password/etc.).
4. **Git history** — if the key was committed, the commit is in git forever even after removing it. `git filter-repo` to rewrite history is messy; better to treat the key as burned and move on.
5. **File a fraud report** with the provider if charges appeared.

## Anti-patterns

- **"It's just a test key"** — test keys often have real billing attached.
- **"I'll rotate later"** — later never comes.
- **Committing keys in an encrypted `.env.enc` with a simple password** — security theater; the password usually ends up in the repo too.
- **Sharing keys in Slack DMs, email, or Notion** — all searchable, all logged somewhere.
- **Reusing one key across dev, staging, and prod** — one leak compromises everything.

## See also

- `mise-ai-cli-setup` — the mise.toml pattern.
- `mise-ai-cli-overview` — why you're installing these at all.
- `mise-trust-and-security` — the broader mise security posture.
- `/mise-ai-keys` — guided setup that follows these rules.
- `warn-plaintext-api-key.sh` — the v0.4 hook that catches obvious leaks.
- gitleaks: `github.com/gitleaks/gitleaks`.

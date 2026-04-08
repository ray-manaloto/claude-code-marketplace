---
description: Walk the user through getting and setting API keys for claude, codex, and gemini — securely, never writing plaintext
disable-model-invocation: true
---

Guided, **user-triggered only** API key setup. This command must never run autonomously and must never write plaintext secrets to any file.

## Steps

1. For each provider the user is setting up:
   - **Anthropic (`ANTHROPIC_API_KEY`)** → https://console.anthropic.com → API Keys → Create Key
   - **OpenAI (`OPENAI_API_KEY`)** → https://platform.openai.com → API keys → Create new secret key
   - **Google Gemini (`GEMINI_API_KEY`)** → https://aistudio.google.com/app/apikey → Create API key

2. Ask the user which storage method they want:

   **(a) Shell rc file** — simplest, no extra tools.
   Show the exact line to add to `~/.zshrc` or `~/.bashrc`:
   ```sh
   export ANTHROPIC_API_KEY="…paste here…"
   ```
   Tell the user to **paste and save**. Do not write the key to disk via any tool.

   **(b) macOS Keychain** — more secure.
   Show the commands:
   ```sh
   security add-generic-password -a "$USER" -s ANTHROPIC_API_KEY -w
   # then in shell rc:
   export ANTHROPIC_API_KEY="$(security find-generic-password -a $USER -s ANTHROPIC_API_KEY -w)"
   ```

   **(c) 1Password CLI** — best for teams.
   Show the commands:
   ```sh
   # Store once, in a 1Password vault of choice
   op item create --category='API Credential' --title='Anthropic' credential='…'
   # Load at shell start
   export ANTHROPIC_API_KEY="$(op read 'op://Private/Anthropic/credential')"
   ```

   **(d) `mise set`** — project-scoped, **not for secrets** — just show it for completeness and warn against using it for API keys because it writes plaintext to `mise.local.toml`.

3. Remind the user:
   - **Never commit keys to git.** `.gitignore` should cover `.env*`, `mise.local.toml`.
   - **Rotate regularly.** Providers let you create multiple keys — label them per host.
   - **`redact = true` in `mise.toml`** keeps keys out of `mise env` output but is not a substitute for real secret storage.

4. After the user reports keys are set, verify by running:
   ```sh
   mise run ai-status
   ```
   (Or `claude --version` etc. directly if the `ai-status` task doesn't exist yet.)

## What to avoid

- **Never** write API keys to any file via any tool.
- **Never** echo a key in a way that would get captured in transcripts or logs.
- **Never** suggest `mise set KEY=value` for secrets — that writes plaintext.
- **Never** propose committing a `.env` file even if it's "just for testing".

For the threat model and rotation guidance, read `mise-ai-cli-keys`.

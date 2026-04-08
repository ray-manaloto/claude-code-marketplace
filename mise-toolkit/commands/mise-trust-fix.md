---
description: Diagnose and fix mise trust issues (the #1 mise UX paper-cut)
---

Diagnose mise trust issues in the current project, then fix them.

## Diagnostic steps

1. Run `mise dr` and capture the "untrusted" / "ignored" entries.
2. Check `~/.local/state/mise/ignored-configs/` for accidentally-denied files (mise stores symlinks here when the user said "no" to a trust prompt).
3. Run `mise cfg ls` to see which config files mise is trying to load and which are missing or untrusted.
4. Check the user's settings: `mise settings get trusted_config_paths` — if this is set to a parent of the current project, the config should already be auto-trusted.

## Fix paths

- **Untrusted config in current project**: `mise trust` (with no args) trusts the nearest config. Confirm before running.
- **Accidentally denied**: remove the symlink in `~/.local/state/mise/ignored-configs/<encoded-path>` and re-run `mise dr` to verify.
- **Symlinked config (e.g., GNU Stow)**: `mise trust` the actual file path, not the symlink target.
- **Repeated prompts in CI / non-interactive shells**: recommend setting `MISE_TRUSTED_CONFIG_PATHS` or adding a path to `trusted_config_paths` in global config.
- **Monorepo with many child configs**: recommend `experimental_monorepo_root = true` in the root `mise.toml` (requires `MISE_EXPERIMENTAL=1`) — descendant configs become implicitly trusted.

## What you avoid

- Setting `trusted_config_paths = ["/"]` globally without flagging the security implication.
- Touching `~/.local/state/mise/ignored-configs/` outside the current project.
- Trusting config files the user hasn't seen — always show the file content first if it has `[hooks]`, `[env]`, or `_.source` directives that can execute code.

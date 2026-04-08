---
description: Run a comprehensive mise health check and explain each finding
---

Run a comprehensive verification of the mise setup and explain every result. This is `mise doctor` plus context.

## Checks to perform (in parallel where possible)

1. **mise binary**: `which mise`, `mise --version`. Confirm version isn't ancient.
2. **Activation**: `type mise` shows the shell function (if applicable for the shell). Confirm `mise activate` is in the appropriate rc file.
3. **`mise dr`**: full doctor output, captured.
4. **Config files loaded**: `mise cfg ls` — show every file mise is reading and the precedence order.
5. **Trust state**: any untrusted configs in `mise dr` output, plus contents of `~/.local/state/mise/ignored-configs/` if non-empty.
6. **Tool installation state**: `mise ls` — what's installed vs what's pinned in config. Any version mismatches?
7. **Env vars**: `mise env --redacted` — what's being exported, including required vars.
8. **Missing required env vars**: any `required = true` vars not yet defined?
9. **Lockfile state**: does `mise.lock` exist? Is it up to date? Run `mise lock --dry-run` if available.
10. **Idiomatic version files**: are there `.nvmrc`/`.python-version`/etc. that aren't being read because the tool isn't in `idiomatic_version_file_enable_tools`?
11. **Shim mode warnings**: if user is using `mise activate --shims`, flag that `[env]` won't load.
12. **GitHub token**: is `MISE_GITHUB_TOKEN` (or `GITHUB_TOKEN`) set? Without it, GitHub API rate limits will hit.

## Output format

For each check, show:

- ✅ **Pass** with the value
- ⚠️  **Warning** with what to do
- ❌ **Fail** with the exact fix command

Group by category (binary / activation / config / trust / tools / env / lockfile / network).

End with a 3-line summary: "all good", "N warnings", or "N failures — fix these first: …".

## What you avoid

- Running destructive operations as part of verification (`mise prune`, `mise implode`).
- Trusting untrusted configs without showing their content first (delegate to `/mise-trust-fix` for that path).
- Hiding warnings the user might want to know about.

## See also

- `/mise-doctor` — the lighter wrapper around just `mise dr`
- `mise-config-doctor` agent — interactive diagnosis
- `mise-troubleshooting` skill

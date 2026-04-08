---
description: Run mise doctor and analyze the output for problems
---

Run `mise doctor` (or `mise dr`) and report any problems it surfaces. Common categories to call out:

- **Untrusted config files** — list each one and offer to run `mise trust <path>`.
- **Activation problems** — wrong shell rc file, shims missing from PATH.
- **Missing tools** — versions in `mise.toml` that aren't installed; offer to run `mise install`.
- **Plugin update warnings** — out-of-date asdf/vfox plugins.
- **Settings conflicts** — e.g., `idiomatic_version_file_enable_tools` mismatches.

After surfacing problems, propose specific commands to fix each one. Do not run destructive operations (uninstall, prune, implode) without explicit confirmation.

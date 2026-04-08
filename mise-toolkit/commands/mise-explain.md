---
description: Explain what mise is in 60 seconds, with concrete examples for a zero-knowledge user
---

Give the user a 60-second elevator pitch for mise. Cover:

1. **One-line answer**: mise is a single Rust CLI that does what `nvm` + `pyenv` + `direnv` + (parts of) `make` do — across every language, in one config file.
2. **The three things it does**:
   - **Dev tool versions** — pin `node`, `python`, `go`, `cmake`, `terraform`, … per directory.
   - **Environment variables** — load project env vars when you `cd` in, unset on `cd` out.
   - **Tasks** — `mise run test`, with deps, parallelism, and source/output caching.
3. **One realistic `mise.toml` example** for a typical project (e.g., a Node + Python service):
   ```toml
   [tools]
   node = "24"
   python = "3.12"
   "npm:prettier" = "3"

   [env]
   NODE_ENV = "development"

   [tasks.test]
   run = "npm test && pytest"
   ```
4. **Why it's better than the tools it replaces**:
   - Faster than `asdf` (Rust vs bash, no shims unless you ask).
   - One config, all languages — vs `nvm` + `pyenv` + `rbenv` + `tfenv`.
   - Lockfile + provenance verification (cosign / SLSA / GitHub attestations).
   - Doesn't fight `direnv` — it just replaces it.

5. **What it's NOT**: not a system package manager (don't install `libssl` with mise), not a desktop app installer.

6. **Next step**: tell the user to run `/mise-recommend` for a personalized adoption path, or `/mise-install` if they're ready to try it.

For more depth, read the `mise-elevator-pitch` and `mise-vs-alternatives` skills, or see <https://mise.jdx.dev>.

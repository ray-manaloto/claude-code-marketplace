# aggregated-research

A Claude Code plugin: run a multi-source research sweep whose findings survive
review — ordered cheapest-refutable-first, with a control arm on every null
result, and the tracker channel checked before any tracker null is believed.
See `skills/aggregated-research/SKILL.md` for the full workflow and
`skills/aggregated-research/references/acceptance-509.md` for the acceptance
criteria it was built against.

## What the SessionStart hook does

On every session start (and on session resume — the hook fires on both),
`hooks/hooks.json` runs:

```
MISE_TRUSTED_CONFIG_PATHS="${CLAUDE_PLUGIN_ROOT}" MISE_DATA_DIR="${CLAUDE_PLUGIN_DATA}/mise" \
  mise --cd "${CLAUDE_PLUGIN_ROOT}" install --yes \
  && printf '%s' "${CLAUDE_PLUGIN_DATA}" > "${CLAUDE_PLUGIN_ROOT}/.data-dir" \
  && echo "aggregated-research: CLI ready — run: aggregated-research --help"
```

This installs the `aggregated-research` CLI (a `pipx`-backed mise tool pinned
to a commit SHA of `ray-manaloto/knowledge-base`) and `ty` (for the LSP entry
below) into `${CLAUDE_PLUGIN_DATA}` — a per-plugin, per-user data directory
that survives plugin updates — rather than the plugin's own read-only install
tree. `MISE_TRUSTED_CONFIG_PATHS` marks `${CLAUDE_PLUGIN_ROOT}` trusted for
mise without any interactive prompt or state write, since a hook is
non-interactive and the plugin root is a fresh path on every plugin version.

It then records the resolved `${CLAUDE_PLUGIN_DATA}` path into
`${CLAUDE_PLUGIN_ROOT}/.data-dir` — the two `bin/` wrappers below read this
file, because `${CLAUDE_PLUGIN_DATA}` is exported only to hook/MCP/LSP
subprocesses, not to Bash-tool commands, so a wrapper invoked as a bare Bash
command cannot see it directly.

**Caveat: `.data-dir` lives in the per-version plugin directory.** Right after
a plugin UPDATE, `${CLAUDE_PLUGIN_ROOT}` points at a new install with no
`.data-dir` file yet — the `bin/` wrappers fail loudly with a message telling
you to start a new session (or run `/reload-plugins`) so the SessionStart hook
re-runs and rewrites it. This is expected, not a bug.

## The CLI verbs

Once the hook has run, `aggregated-research` is on the Bash tool's PATH
(plugin `bin/` directories are added to PATH while the plugin is enabled).
Today the CLI has one verb, `trackers` (issues/PRs/discussions search per the
skill's step 3); more verbs land in later slices. Run
`aggregated-research --help` for the current list.

## Dependencies

This plugin's skill routes breadth research through four other plugins as
optional dependencies. Install the marketplace for each **before** installing
this plugin, or `claude plugin install` will not be able to resolve the
cross-marketplace dependency:

```
claude plugin marketplace add firecrawl/firecrawl-claude-plugin
claude plugin marketplace add exa-labs/exa-mcp-server
claude plugin marketplace add upstash/context7
claude plugin marketplace add mvanhorn/last30days-skill
```

| Dependency | What auth it needs | Where upstream documents it | Without it |
|---|---|---|---|
| firecrawl | `firecrawl login --browser` or `firecrawl login --api-key <key>` (the CLI stores it; no env var required for the keyless free tier) | the firecrawl plugin's `skills/firecrawl/SKILL.md` + `firecrawl login --help` | search / scrape / interact still work on the free tier; the rest refuse |
| context7 | `CONTEXT7_API_KEY` — injected as an `Authorization` header by the plugin's `.mcp.json`; anonymous if unset | the context7 plugin's `.mcp.json` and README | works anonymously at a lower rate limit |
| exa | none required — hosted MCP, open endpoint (per the installed plugin's `.mcp.json`; re-verify at install time) | the exa plugin's `.mcp.json` | works |
| last30days | `SCRAPECREATORS_API_KEY` primary; optional per-source keys (`OPENAI_API_KEY`, `XAI_API_KEY`, …) — degrades per source | the last30days plugin README and its `doctor` command | sources without a key are skipped, and `doctor` says which |

Re-verify each row against the dependency's own installed files at install
time — auth mechanisms and default endpoints can change between the plugin
versions.

## LSP

`.lsp.json` registers `ty` (Astral's Python type checker / language server,
pinned `0.0.74`) for `.py` files, driven through the `bin/ty` wrapper the same
way as the CLI.

## Why the hook pins mise's global config to the plugin's own `mise.toml`

`mise install` acts on every config file in scope — the user's global `~/.config/mise/config.toml` included. Measured 2026-08-28: without the override the SessionStart hook installed 128 tools (2.3 GB) into `$CLAUDE_PLUGIN_DATA` before it was stopped. `MISE_GLOBAL_CONFIG_FILE` and `MISE_SYSTEM_CONFIG_FILE` both point at the plugin's `mise.toml`, so exactly two tools are in scope: the CLI and `ty`.

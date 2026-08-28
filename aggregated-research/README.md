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
"${CLAUDE_PLUGIN_ROOT}/bin/mise-env" install --yes \
  && echo "aggregated-research: CLI ready — run: aggregated-research --help"
```

`bin/mise-env` is the ONE place the mise confinement is defined — the hook
and both `bin/` wrappers below all call it, rather than each inlining its own
`MISE_*` variables. It resolves the plugin root from its own path, resolves
the data dir from `${CLAUDE_PLUGIN_DATA}` (falling back to the documented
per-plugin path `~/.claude/plugins/data/aggregated-research-ray-manaloto` when
that isn't set — see the wrapper section below), then runs `mise` with:

- `MISE_CEILING_PATHS` set to the plugin root, so mise's config walk never
  climbs past it into a host config directory (e.g. `~/.config/mise/`);
- `MISE_GLOBAL_CONFIG_FILE` / `MISE_SYSTEM_CONFIG_FILE` pointed at the
  plugin's own `mise.toml`;
- `MISE_TRUSTED_CONFIG_PATHS` set to `<plugin root>:<data dir>` — the data
  dir is included because installing the CLI performs a `uv` git checkout
  whose own `mise.toml` lives under the data dir and must be trusted too (see
  Troubleshooting);
- `MISE_DATA_DIR` and `UV_CACHE_DIR` pointed under the data dir, so nothing is
  written into the plugin's own (read-only, per-version) install tree;
- `__MISE_DIFF` / `__MISE_SESSION` / `__MISE_ORIG_PATH` unset, so an already
  `mise activate`d shell can't leak its own PATH state into the confined run.

This installs the `aggregated-research` CLI (a `pipx`-backed mise tool pinned
to a commit SHA of `ray-manaloto/knowledge-base`) and `ty` (for the LSP entry
below) into the per-plugin data directory — which survives plugin updates —
rather than the plugin's own read-only install tree.

**No state is written under `${CLAUDE_PLUGIN_ROOT}`** (Claude Code docs: don't
write state there — it's per-version). Earlier slices wrote a `.data-dir`
marker file there; that file and its fallback-read logic are gone. The
wrappers below resolve the same data-dir constant `mise-env` does, and fail
loudly rather than silently if nothing is installed there yet.

## The CLI verbs

Once the hook has run, `aggregated-research` is on the Bash tool's PATH
(plugin `bin/` directories are added to PATH while the plugin is enabled).
Today the CLI has one verb, `trackers` (issues/PRs/discussions search per the
skill's step 3); more verbs land in later slices. Run
`aggregated-research --help` for the current list.

The install pulls the CLI's current full dependency set — measured 1.3 GB —
because the tool isn't split into thin/heavy packages yet; that split is the
next slice's job, not this one's.

On a host without an SSH key configured for GitHub, set
`CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` before `claude plugin marketplace add` —
the `owner/repo` shorthand clones over SSH by default.

## Dependencies

This plugin's skill routes breadth research through four other plugins as
declared dependencies — the install cannot resolve without their marketplaces. Install the marketplace for each **before** installing
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

## Troubleshooting

- **`Config files in ~/Library/Caches/uv/... are not trusted`** during the
  SessionStart install, on a machine where `git` resolves to a mise shim
  (`~/.local/share/mise/shims/git`): uv's `git submodule update` ran through
  that shim, and the shim loads the checkout's own `mise.toml`, which the hook's
  confinement leaves untrusted. The shim is an orphan of an uninstalled
  `conda:git`; `mise prune` removes it. Measured 2026-08-28 (macOS, mise
  2026.8.14): identical hook, rc 1 with the shim on PATH, rc 0 without.
- **`aggregated-research: nothing installed under <data dir>`** from a
  wrapper: the SessionStart hook hasn't run yet for this data dir, or it
  failed — check the session-start output, then `/reload-plugins` or start a
  new session.

## Host regression arms

Three probes catch the confinement regressing on a developer host — one that
already has `~/.config/mise/config.toml`, `~/.local/share/mise/shims` on
PATH, and an activated `mise` shell:

1. Fresh install: `rm -rf ~/.claude/plugins/data/aggregated-research-ray-manaloto`,
   then run the hook command with `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA`
   exported → rc 0; `ls .../mise/installs` lists exactly the CLI and `ty`;
   `du -sh` ≈ 1.3G.
2. Wrapper without `CLAUDE_PLUGIN_DATA` exported (the Bash-tool case):
   `bin/aggregated-research --help` and `bin/ty --version` both rc 0. Then the
   loud-failure case: point `CLAUDE_PLUGIN_DATA` at an empty directory → rc 2
   with the "nothing installed" message.
3. Negative control: run the OLD (pre-slice-3) hook line with `install --yes`
   swapped for `config ls` — it lists the host's `~/.config/mise/config.toml`
   alongside the plugin's own file. `bin/mise-env config ls` lists only the
   plugin's own `mise.toml`. If the negative control ever stops leaking, the
   control itself is broken, not the fix.

## When the hook fires

A `SessionStart` hook with no `matcher` fires on every session-start event — startup, resume, `/clear`, compaction and fork. Once the tools are installed the run is a no-op (measured 0 s on the second run, 2026-08-28), so this costs nothing after the first install.

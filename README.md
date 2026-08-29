# claude-code-marketplace

A curated marketplace of [Claude Code](https://claude.com/claude-code) plugins by
[Raymond Manaloto](https://github.com/ray-manaloto).

## Plugins

### [aggregated-research](./plugins/aggregated-research/)

Run a multi-source research sweep whose findings survive review — ordered
cheapest-refutable-first, with a control arm on every null result and the
tracker channel checked before any tracker null is believed. See
[aggregated-research/README.md](./plugins/aggregated-research/README.md) for the
SessionStart hook, the CLI, and the dependency plugins it routes breadth
research through.

## Install

```sh
claude plugin marketplace add ray-manaloto/claude-code-marketplace
```

`aggregated-research` depends on four other plugins for breadth research
(firecrawl, exa, context7, last30days). A cross-marketplace dependency needs
its target marketplace registered on the installing machine first, so add
those four marketplaces **before** installing `aggregated-research`. On a
host with no SSH key configured for GitHub, set
`CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` first — the `owner/repo` shorthand below
clones over SSH by default:

```sh
claude plugin marketplace add firecrawl/firecrawl-claude-plugin
claude plugin marketplace add exa-labs/exa-mcp-server
claude plugin marketplace add upstash/context7
claude plugin marketplace add mvanhorn/last30days-skill
```

Then:

```sh
claude plugin install aggregated-research@ray-manaloto --yes
```

The `--yes` flag is required when stdin or stdout is not a TTY. For local
development against this checkout, add the four dependency marketplaces first,
then add the checkout itself and install the qualified plugin name:

```sh
claude plugin marketplace add firecrawl/firecrawl-claude-plugin
claude plugin marketplace add exa-labs/exa-mcp-server
claude plugin marketplace add upstash/context7
claude plugin marketplace add mvanhorn/last30days-skill
claude plugin marketplace add /path/to/claude-code-marketplace
claude plugin install aggregated-research@ray-manaloto --yes
```

## Acceptance

`.github/workflows/acceptance.yml` is the install-and-run acceptance test. With
`CLAUDE_CODE_OAUTH_TOKEN`, its first Claude Code session follows only this
README and `plugins/aggregated-research/README.md` to install the mounted marketplace,
the four dependency marketplaces, and `aggregated-research`. A second, fresh
session proves the real SessionStart hook loads the plugin, confines mise to
the plugin's own tools, and runs the CLI. The script then repeats the CLI run
directly as deterministic proof. Without a token, the same isolated Linux
container retains the script-driven install and hand-run hook fallback.

## Contributing

This marketplace is currently single-author. If you have plugin ideas or
feedback, open an issue at
<https://github.com/ray-manaloto/claude-code-marketplace/issues>.

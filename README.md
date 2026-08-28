# claude-code-marketplace

A curated marketplace of [Claude Code](https://claude.com/claude-code) plugins by
[Raymond Manaloto](https://github.com/ray-manaloto).

## Plugins

### [aggregated-research](./aggregated-research/)

Run a multi-source research sweep whose findings survive review — ordered
cheapest-refutable-first, with a control arm on every null result and the
tracker channel checked before any tracker null is believed. See
[aggregated-research/README.md](./aggregated-research/README.md) for the
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
claude plugin install aggregated-research@ray-manaloto
```

For local development against this checkout:

```sh
claude plugin marketplace add /path/to/claude-code-marketplace
claude plugin install aggregated-research
```

## Acceptance

`.github/workflows/acceptance.yml` is the install-and-run acceptance test: in
an isolated Linux container, the script installs this marketplace,
`aggregated-research`, and its four dependency plugins per this README, the
SessionStart hook confines mise to the plugin's own tools, and the CLI runs
both directly and (given `CLAUDE_CODE_OAUTH_TOKEN`) via an agent. It does not
yet cover the agent-driven INSTALL arm — an agent following only these
READMEs performing the install itself, rather than the script running the
documented commands verbatim — tracked as
[#2](https://github.com/ray-manaloto/claude-code-marketplace/issues/2).

## Contributing

This marketplace is currently single-author. If you have plugin ideas or
feedback, open an issue at
<https://github.com/ray-manaloto/claude-code-marketplace/issues>.

# Codex runtime qualification

Observed 2026-10-10 with native `codex-cli 0.162.1`. The installed standalone
executable, relevant inherited settings, skills, plugins, MCP transports and role
hashes are recorded in [runtime-inventory.json](../evidence/onboarding/runtime-inventory.json).
This inventory is a dated host receipt, not a portable installation requirement.

## Project configuration

`.codex/config.toml` sets only `agents.max_concurrent_threads_per_session = 3`.
The primary writer plus three read-only children fit the bounded team. Models,
effort, credentials, trust, hooks and MCP configuration remain inherited.
No global capability is copied into this repository.

Standalone role files under `.codex/agents/` define a configuration inspector,
documentation reviewer and independent cold reviewer. Each supplies native
`name`, `description`, `developer_instructions` and a read-only sandbox default.
They have no model/effort overrides. Select a custom role without a full-history
fork; a full-history fork inherits the parent's role. Parent permission overrides
can affect child permissions, so the read-only brief remains explicit.
The official [subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents.md)
is supporting guidance; the installed runtime's observed behavior is the gate.

## Inherited capability inventory

The inspected global configuration contains 44 plugin entries, 20 enabled.
These counts are configuration, not proof that every connector is authenticated.
Native `codex mcp list --json` resolves 13 servers with no mixed command/URL
transport. App-server startup also discovers bundled endpoints absent from that
list; the CLI inventory is not a complete startup census. The project adds no
MCP entry, avoiding same-name transport overlays.

This task uses the inherited Codex orchestration, OpenAI Docs, Planning with
Files and mise skills. Their exact source hashes are in the inventory. Native
fresh-context diagnostics also expose the inherited Astral and code-review skill
guidance. New project skills would duplicate these capabilities, so none are added.
The current live team uses native collaboration briefs; role-file discovery in a
fresh session is qualified separately from an already-running chat's tool catalog.

## Native checks and limits

[Native controls](../evidence/onboarding/native-config-controls.json) record:

- Valid project configuration reaches the deliberately nonexistent model-provider
  stop; this is a parser receipt with exit 1, not an inference success.
- A temporary invalid agent-limit type is rejected at this project's config path,
  proving the worktree layer is actually loaded. Exact bytes were restored.
- Fresh read-only `debug prompt-input` processes return exit 0 from the worktree
  and `/private/tmp` with `-C` selecting this project; required guidance matches.
- Temporarily malformed role TOML produces no diagnostic in `debug prompt-input`.
  That route therefore does not establish role discovery/application.
- Global config and hook hashes remain unchanged through these controls.

The initial [exec smoke](../evidence/onboarding/native-role-smoke.json) used the
existing ChatGPT login and inherited model/effort. Its CLI JSONL omitted V2 spawn
metadata, and receipt filtering lost one error message. Neither is treated as
direct role proof. The later [protocol receipt](../evidence/onboarding/native-role-protocol.json)
qualifies custom-role application: native `thread/read` identifies the child as
`marketplace-reviewer`, its parent and source role agree, the child returns the
unpasted role directive, and native completion names the same child. The parent
turn and owned app-server finish successfully. Configuration/hook hashes match.

The probes disabled the 13 listed MCP servers, including Docker. However, the
[startup-only diagnostic](../evidence/onboarding/native-startup-diagnostics.json)
observed four additional endpoints starting: `codex-security`, `xcodebuildmcp`,
`codex_apps`, and `openai-api-key-local-confirmation`. Three reached ready during
the short observation; no tools were invoked through them. Do not describe that
run as having no MCP startup. The process exited on stdin closure. A
[corrected startup-only probe](../evidence/onboarding/native-startup-corrected.json)
adds the actual installed plugin IDs and `features.apps=false` only to its argv;
it observed no MCP startup notifications, loaded the project guidance and exited
0. It did not rerun inference or replace the earlier receipt. The warning
about inherited experimental `chronicle` remains visible and is not suppressed.
The role probe's research guard also reports incomplete strict-five coverage;
its read-only sandbox cannot create research receipts. No provider research ran.
MCP connectivity, provider coverage and full Claude/OCI acceptance are unqualified.

Failed diagnostic routes are retained: 0.162.1 rejects `--strict-config` for
`debug` and `mcp`; quoting dotted key segments inside `-c` creates literal quote
characters in the keys. The checked argv uses unquoted segments in each argument.
No hooks or trust settings are bypassed or rewritten to make a check pass.

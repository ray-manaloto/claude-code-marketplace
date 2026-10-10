# Native Codex project onboarding

This checkout retains the existing Claude marketplace and adds a Codex development
surface. The active plan is
[`2026-10-10-marketplace-macos-reflection-scaffold`](../.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md).
Consult its progress and receipts before claiming the setup is qualified.

## Fresh chat

Select this checkout as the working root. For the CLI, the installed 0.162.1
supports `codex -C /absolute/path/to/claude-code-marketplace`; this selects the
project even when the shell starts elsewhere. `AGENTS.md` supplies repository
guidance; scoped plugin guidance applies to plugin work. Native project settings
belong in `.codex/config.toml`. Trust is a user setting and is not changed here.

Read [accepted decisions](accepted-decisions.md) before historical research.
Set `PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold` and
`PWF_PLAN_ROOT=/absolute/path/to/claude-code-marketplace` in the launching shell.
An export inside one tool subprocess cannot pin the already-running host.
Read the selected `task_plan.md`, `findings.md`, and `progress.md`; do not create
a competing root plan. The [team contract](agents/codex-task-orchestration.md)
defines the sole writer and read-only review lanes.

## Development and acceptance

The root `mise.toml` is the Linux OCI image definition. The plugin has its own
independent two-tool `mise.toml` and data directory. Preserve both surfaces.
Use the explicit development wrapper from this checkout:

```sh
./dev/mise config ls --json
./dev/mise tasks validate
./dev/mise run check
./dev/mise run check:acceptance-baseline
```

From another cwd, invoke `/absolute/path/to/claude-code-marketplace/dev/mise`.
The wrapper selects only `mise.dev.toml`, disables hooks and auto-install, and
sets trust only in its process environment for that reviewed file. It does not
persist trust or edit global configuration. It needs installed mise, Git, shells
and Python 3.11+; set `MARKETPLACE_PYTHON` to an existing interpreter if necessary.
`MARKETPLACE_MISE_BIN` can select an existing mise executable. No tool versions
are installed or promoted here. See [check receipts](../evidence/onboarding/development-checks.json).

`check` parses JSON/TOML, compiles Python syntax without cache writes, checks
shell syntax and manifest identities/dependency policy, and checks diff whitespace.
The separate baseline task also matches all 19 original file hashes; it is an
onboarding preservation gate, not a permanent prohibition on future changes.

Full acceptance remains `.github/workflows/acceptance.yml` and `ci/acceptance.sh`.
It installs plugins, exercises a fresh Claude SessionStart and runs live provider
queries in an isolated Linux container. Run it only after container ownership and
capacity are admitted. Static preservation does not establish runtime acceptance.

## Configuration and capability reuse

Use native local CLI help/schema for the installed version. `--strict-config`
checks recognized config fields; it does not prove hook liveness or model access.
Global capabilities are inherited rather than copied wholesale. This session
uses Codex orchestration, OpenAI Docs and Planning with Files; mise guidance is
used for the separate development command surface. Roles must preserve the
parent's ownership and never install tools or start services during inspection.

Current [host inventory and runtime qualification](codex-runtime.md) belong in
sanitized onboarding receipts. Do not commit authentication material, raw environment
dumps or complete global configuration. Keep command/url MCP transports distinct;
an inherited entry can merge with a project entry of the same name.

## Evidence and later work

All 19 source-index entries matched their recorded SHA-256 at takeover; see
[`source-hash-audit.json`](../evidence/onboarding/source-hash-audit.json).
The earlier strict-five research did not pass. Context7 quota exhaustion,
Firecrawl 402 with provisional fallback, and Last30Days validator rejection
remain recorded gaps. The new onboarding does not recertify that research.

Read the [current handoff](status.md) and [build task index](build-roadmap.md).
After onboarding, follow that small-task sequence and its prerequisites.
Global tool installation and heavy compiler/matrix operations
need their own admitted phases. The future 96-tree / 384-cell matrix is a
qualification candidate, not a completed platform support claim.

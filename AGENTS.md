# Marketplace development

This repository publishes the `ray-manaloto` Claude Code marketplace and its
`aggregated-research` plugin. Preserve their public names, CLI and data paths.
The accepted next product is a native C++26 P2996 research core, introduced
incrementally behind the current interfaces. Python-core and SBE-first plans
in historical material are superseded by `docs/accepted-decisions.md`.

## Start here

Read `docs/onboarding.md`, `docs/accepted-decisions.md`, and the selected plan.
Current PLAN_ID: `2026-10-10-marketplace-macos-reflection-scaffold`.
Plans live in `.planning/<PLAN_ID>/`; `PWF_PLAN_ROOT` means the project root,
not the `.planning` directory. Verify checkout, branch, HEAD and common Git
directory before editing. Preserve existing edits and the source checkout.

## Project map and commands

- `.claude-plugin/marketplace.json`: marketplace identity and dependency policy.
- `plugins/aggregated-research/`: plugin manifest, skill, hook and confined wrappers.
- Root `mise.toml` / `mise.lock`: Linux OCI acceptance image. Never run their
  full install/bootstrap on macOS as a development setup step.
- `.github/workflows/acceptance.yml` and `ci/acceptance.sh`: full Claude/container
  acceptance; require a separately admitted host/container operation.
- `mise.dev.toml` and `dev/mise`: explicit lightweight development configuration.
- `.codex/`: native Codex project configuration and bounded read-only roles.
- `evidence/onboarding/`: sanitized verification receipts, not secrets or transcripts.

Run `./dev/mise tasks validate` and `./dev/mise run check` with existing tools.
For onboarding preservation, `./dev/mise run check:acceptance-baseline` also
verifies all 19 original file hashes. These are static checks; they do not prove
container, provider or hook-runtime acceptance. See `docs/onboarding.md` for
prerequisites. Do not install plugin runtimes just to lint.

## Ownership and completion

Before allocating a writer, parallel worktree or takeover, read the current
ownership rule in `docs/agents/codex-task-orchestration.md`. Give each agent an
explicit brief, file scope, prerequisite receipts and checks.
For durable spec/ticket, triage-label and domain-document conventions, read
`docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and
`docs/agents/domain.md` when relevant. For improvement proposals and implementation,
follow the standing workflow in `docs/agents/issue-tracker.md`.
For every ticket or task outcome, including partial or blocked work, follow
`docs/agents/ticket-retro.md` for the acceptance and new-ticket dispatch gate.
Keep each unit near five maintained files and 300 handwritten changed lines;
settle its gate before expanding. Parent owns shared planning files.

Record actual command exit codes, exact Git identity and reviewer dispositions.
Distinguish planned, implemented, reviewed, tested, committed and published.
A static check cannot substitute for fresh-session or full OCI acceptance.

## Current admission and research

Initial onboarding permits lightweight work in this worktree. Global settings,
hooks, trust, credentials, model defaults, global mise, other repositories and
host-heavy work require their separately recorded ownership/admission phases.
Do not push, publish, merge, register daemons or create a native goal implicitly.
Reuse inherited Codex skills/plugins; do not copy Claude hooks or slash commands
into native Codex configuration. Avoid redundant project copies of global skills.

New tool/workflow research uses Exa, Firecrawl, Last30Days, Context7 and GitHub,
with native `fnox --config ~/.config/fnox/config.toml --profile codex_research
--no-defaults --no-daemon --non-interactive exec -- <command>`. Never print or
persist injected secrets. Use primary docs/source for final claims and record
every attempted route, including failures. For a strict hook receipt, run
`mise -C <dotfiles-checkout> run research-fanout` under that `fnox exec`, with
`--strict-five`, `--request-id` equal to the hook turn ID, the hook's output
directory and an explicit Last30Days plan. Preserve old receipts; known quota
failures remain gaps, and provisional fallbacks are not strict passes.

# Marketplace development

This repository publishes the `ray-manaloto` Claude Code marketplace and its
`aggregated-research` plugin. The accepted next product is a native C++26 P2996
research core, introduced incrementally behind the current interfaces;
`docs/accepted-decisions.md` supersedes the Python-core and SBE-first plans.

## Preserve

- Marketplace and plugin identity (`.claude-plugin/marketplace.json`), the plugin's
  CLI, wrappers and data paths.
- The 19 acceptance-baseline files in `evidence/onboarding/baseline-files.json`;
  `.gitignore` is one of them.
- Existing edits and the source checkout; verify checkout, branch, HEAD and Git dir first.

## Start here

1. `docs/onboarding.md`, then `docs/accepted-decisions.md`.
2. Selected plan: PLAN_ID `2026-10-10-marketplace-macos-reflection-scaffold` under
   `.planning/<PLAN_ID>/`; `PWF_PLAN_ROOT` is the project root, not `.planning`.
3. Takeover and team protocol: `docs/agents/claude-takeover.md`,
   `docs/agents/claude-team.md`. Vocabulary: `GLOSSARY.md`. Reviewer judgement
   rules: `CODING_STANDARDS.md`.
4. Per-directory guidance: `dev/`, `docs/`, `evidence/`, `.planning/`, `.claude/` and
   `plugins/aggregated-research/` each have an `AGENTS.md`; a nested `CLAUDE.md` imports
   it everywhere except the plugin (a later lane adds it). `.claude/rules/*.md` hold
   path-scoped rules.

## Standing workflow

grill-with-docs → to-spec → to-tickets → implement-spec → retro, per
`docs/agents/issue-tracker.md` (GitHub Issues hold specs and tickets).
- Read the ownership rule and unit-size limit in `docs/agents/codex-task-orchestration.md`
  before allocating a writer, worktree or takeover; brief each agent with file scope,
  prerequisite receipts and checks. The parent owns shared planning files.
- Every ticket or task outcome, partial or blocked included, ends at the retro gate in
  `docs/agents/ticket-retro.md`.
- Record actual exit codes, Git identity and reviewer dispositions; planned, implemented,
  reviewed, tested, committed and published are separate states.

## Gotchas

- Hooks versus mods: three deny gates stay settings hooks and everything else becomes a mod;
  read `docs/agents/hooks-and-mods.md` before touching `.claude/settings.json`, `dev/hooks/` or a mod.
- Native first: new logic goes into the C++26 core; Python and TypeScript stay thin bridges, and
  existing Python takes fixes, tests and deletions only (ADR 0008, `docs/accepted-decisions.md`).
- Run `./dev/mise tasks validate`, `./dev/mise run check` and
  `./dev/mise run check:acceptance-baseline`. Root `mise.toml` / `mise.lock` define the
  Linux OCI image (container install only); do not install plugin runtimes just to lint.
- Run named checks from one worktree at a time; a raced result is not a receipt (CT-11
  adds a lock). They are static: container, provider, hook-runtime and fresh-session
  acceptance (`ci/acceptance.sh`) need a separately admitted operation.
- Global settings, hooks, trust, credentials, model defaults, global mise, other
  repositories and host-heavy work need their own recorded admission. Push, publish,
  merge, daemon registration and native goals wait for explicit instruction.
- Reuse inherited Codex skills and plugins; do not copy Claude hooks or slash commands
  into native Codex configuration.
- Research an open fork or a new tool through `docs/agents/research-workflow.md` before deciding or
  falling back; run every provider under `fnox --config ~/.config/fnox/config.toml --profile
  codex_research --no-defaults --no-daemon --non-interactive exec -- <command>`. Current hook
  receipt, until the ADR 0006 absorption ticket replaces it: `mise -C <dotfiles-checkout> run
  research-fanout` with `--strict-five`, `--request-id` equal to the hook turn ID, the hook's
  output directory and an explicit Last30Days plan.

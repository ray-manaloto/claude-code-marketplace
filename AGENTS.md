# Marketplace development

This repository publishes the `ray-manaloto` Claude Code marketplace and its
`aggregated-research` plugin. The accepted next product is a native C++26 P2996
research core, introduced incrementally behind the current interfaces;
`docs/accepted-decisions.md` supersedes the Python-core and SBE-first plans.

## Preserve

- Marketplace and plugin identity (`.claude-plugin/marketplace.json`), the plugin's
  CLI, wrappers and data paths.
- The 19 acceptance-baseline files in `evidence/onboarding/baseline-files.json` and the
  frozen `.gitignore`.
- Existing edits and the source checkout; verify checkout, branch, HEAD and Git
  common directory before editing.

## Start here

1. `docs/onboarding.md`, then `docs/accepted-decisions.md`.
2. Selected plan: PLAN_ID `2026-10-10-marketplace-macos-reflection-scaffold` under
   `.planning/<PLAN_ID>/`; `PWF_PLAN_ROOT` is the project root, not `.planning`.
3. Takeover and team protocol: `docs/agents/claude-takeover.md`,
   `docs/agents/claude-team.md`. Vocabulary: `GLOSSARY.md`. Reviewer judgement
   rules: `CODING_STANDARDS.md`.
4. Per-directory guidance: `dev/`, `docs/`, `evidence/`, `.planning/`, `.claude/` and
   `plugins/aggregated-research/` each have an `AGENTS.md` (nested `CLAUDE.md` imports
   it); `.claude/rules/*.md` hold path-scoped rules; `.codex/` is native Codex config.

## Standing workflow

grill-with-docs → to-spec → to-tickets → implement-spec → retro, per
`docs/agents/issue-tracker.md` (GitHub Issues hold specs and tickets).
- Read the ownership rule in `docs/agents/codex-task-orchestration.md` before
  allocating a writer, worktree or takeover; brief each agent with file scope,
  prerequisite receipts and checks.
- Every ticket or task outcome, partial or blocked included, ends at the retro gate in
  `docs/agents/ticket-retro.md`.
- A unit stays near five maintained files and 300 handwritten changed lines; the parent
  owns shared planning files.
- Record actual exit codes, Git identity and reviewer dispositions; planned, implemented,
  reviewed, tested, committed and published are separate states.

## Gotchas

- Run `./dev/mise tasks validate`, `./dev/mise run check` and
  `./dev/mise run check:acceptance-baseline`. The root `mise.toml` / `mise.lock` define
  the Linux OCI image and install in the container only.
- Named checks run one at a time and are static; container, provider, hook-runtime and
  fresh-session acceptance (`ci/acceptance.sh`) need a separately admitted operation.
- Global settings, hooks, trust, credentials, model defaults, global mise, other
  repositories and host-heavy work need their own recorded admission. Push, publish,
  merge, daemon registration and native goals wait for explicit instruction.
- Reuse inherited Codex skills and plugins; `.codex/` receives no Claude hooks.
- New-tool research uses Exa, Firecrawl, Last30Days, Context7 and GitHub under
  `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults
  --no-daemon --non-interactive exec -- <command>`; keep secrets out of output, cite
  primary sources, record every attempted route. A strict hook receipt runs
  `mise -C <dotfiles-checkout> run research-fanout` with `--strict-five`, `--request-id`
  equal to the hook turn ID, the hook's output directory and an explicit Last30Days
  plan; quota failures stay gaps.

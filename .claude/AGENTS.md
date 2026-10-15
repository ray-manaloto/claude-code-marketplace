# .claude/

Claude Code project configuration. Roles and lane lifecycle: `docs/agents/claude-team.md`.

- `agents/`: role definitions (implementer, doc-writer, reviewer, retro-writer, extractor,
  frontier-scheduler); `dev/test_doctor_agents.py` checks their frontmatter. Five roster-v2 roles
  are briefs on these files, not files (D189, R12c §1.1); pass `model` and `effort` on every Agent call:
  - upgrade intake: `frontier-scheduler`, Sonnet, high, after a mechanical collector; returns JSON
    on dependency and release changes (R-158, R-167, R-176).
  - test author: `implementer`, Opus, xhigh; writes the failing test at the agreed seam before the
    implementer round.
  - test-contract check: `reviewer`, Fable, medium; confirms each test asserts an external seam and
    fails without the change.
  - security reviewer: `reviewer`, Fable, xhigh, beside the reviewer on C++ units; covers every
    public-text write path (R-174); the receipt records the served model.
  - cross-vendor reviewer: `codex exec -s read-only -C <lane worktree>` or `codex review --base <base>`,
    GPT-6.1 Sol high, launched by the parent on C++ units; starts when Codex returns after 2026-10-19.
- `rules/`: path-scoped rules for `dev/`, `evidence/`, `.planning/`, `.gitleaks.toml` and hooks and mods; edit a rule here and
  point to it elsewhere.
- `skills/`: skills authored in this repository (`codex-session-history`,
  `antigravity-session-history`, `session-handoff`, `session-resume`, `ticket-frontier`), each
  mirrored under `.agents/skills/` for Codex; change both copies together.
  `dev/test_handoff.py` pins `session-handoff` and `session-resume` prose and their mirrors; run
  `./dev/mise run test:handoff` after editing either. Exception: `session-start`, a project mod
  (skills-dir plugin, CT-35), has no mirror, because Codex cannot run mods. Copies of global
  skills stay out of the project, with one sanctioned exception the user chose to keep: `gh-stack`.
- `settings.json`: shared project settings and hooks, composed by ticket CT-02. Its
  keys are `$schema`, `env`, `autoCompactEnabled`, `autoCompactWindow`, `enabledPlugins`,
  `extraKnownMarketplaces` and `hooks` (only the three deny gates stay hooks once the mods library
  lands, `docs/agents/hooks-and-mods.md`); a personal key goes in `settings.local.json`,
  which is per-user and stays uncommitted. Project marketplaces are declared in
  `settings.json`, personal ones in `settings.local.json`.
- `worktrees/`: lane worktrees (`.claude/worktrees/<unit>`), excluded through
  `.git/info/exclude` because `.gitignore` is a frozen baseline file.
- Mods are thin: a mod calls the C++ core through the bridge and holds no logic of its own
  (ADR 0008; `docs/agents/hooks-and-mods.md`).

# .claude/

Claude Code project configuration. Roles and lane lifecycle: `docs/agents/claude-team.md`.

- `agents/`: role definitions (implementer, doc-writer, reviewer, retro-writer, extractor).
- `rules/`: path-scoped rules for `dev/`, `evidence/`, `.planning/`, `.gitleaks.toml` and hooks and mods; edit a rule here and
  point to it elsewhere.
- `skills/`: skills authored in this repository (`codex-session-history`), each mirrored
  under `.agents/skills/` for Codex; change both copies together. Copies of global skills
  stay out of the project, with one sanctioned exception the user chose to keep: `gh-stack`.
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

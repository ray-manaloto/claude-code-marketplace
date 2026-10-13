# .claude/

Claude Code project configuration. Roles and lane lifecycle: `docs/agents/claude-team.md`.

- `agents/`: role definitions (implementer, doc-writer, reviewer, retro-writer, extractor).
- `rules/`: path-scoped rules for `dev/`, `evidence/`, `.planning/`; edit a rule here and
  point to it elsewhere.
- `skills/`: this repository's skills, each mirrored under `.agents/skills/` for Codex;
  change both copies together. Copies of global skills stay out of the project.
- `settings.json`: shared project settings and hooks, composed by ticket CT-02.
  `settings.local.json` is per-user and stays uncommitted.
- `worktrees/`: lane worktrees (`.claude/worktrees/<unit>`), excluded through
  `.git/info/exclude` because `.gitignore` is a frozen baseline file.

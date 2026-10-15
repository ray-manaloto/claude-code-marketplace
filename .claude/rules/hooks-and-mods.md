---
paths: [".claude/settings.json", "dev/hooks/**", ".claude/skills/workflow-mods/**", "mods/**", "plugins/aggregated-research/hooks/**"]
---

# Hooks and mods

- Read `docs/agents/hooks-and-mods.md` before changing a hook or a mod; it holds the cited evidence and the watch list.
- The three deny gates stay settings hooks: `PreToolUse` on Bash, `Stop` and `SubagentStop` (D102). Do not move them into mods or delete them without a new decision backed by a fresh research report (D100).
- Every other workflow rule becomes a mod, and the change that ships the mod deletes its settings hook (D92, D59).
- Dated exception, 2026-10-14 (D166): the request capture hooks (`UserPromptSubmit`, `PostToolUse` on `AskUserQuestion`) and carry hooks (`PreCompact`, `SessionStart`, `SubagentStart`) stay zero-logic settings hooks (`jq`, `sed`, printing; never blocking) until the matching mod events are verified live, then the mod replaces each and the hook is deleted (D128). The request ledger stays untracked under `~/.local/state/`.
- A Bash mod hooks `tool.check`, never `tool.call` with a Bash, empty, `*` or RegExp matcher (anthropics/claude-code#92533); no subagent uses `isolation: "worktree"` until a host regression check passes.
- Before relying on any mod behaviour, check the watch list issues (#99130, #96831, #100869, #92533, #101384, #84320, #102134) for changes; a change triggers the CT-80 recheck.

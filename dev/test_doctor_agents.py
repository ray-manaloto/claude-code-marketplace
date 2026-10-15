"""Agent-file frontmatter (roster-v2 retro, D189). Claude Code ignores an unknown subagent field without
reporting an error and `claude plugin validate --strict` never reads `.claude/agents`, so `experimentl:` or
`Agnet` would silently drop a roster setting. Field set: sub-agents.md:296-316 at 2.1.300; tool names:
sub-agents.md:423-437 (filters) plus the tools-reference built-ins the role files may deny.
"""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
FIELDS = frozenset({"name", "description", "tools", "disallowedTools", "model", "permissionMode", "maxTurns",
                    "autoCompactWindow", "skills", "mcpServers", "hooks", "memory", "background",
                    "omitClaudeMd", "effort", "isolation", "color", "initialPrompt", "experimental"})
TOOLS = frozenset({"Agent", "AskUserQuestion", "EndConversation", "EnterPlanMode", "ExitPlanMode",
                   "ScheduleWakeup", "WaitForMcpServers", "Workflow", "Read", "Grep", "Glob", "LSP", "Bash",
                   "PowerShell", "Edit", "Write", "NotebookEdit", "WebFetch", "WebSearch", "TodoWrite",
                   "Skill", "ToolSearch", "EnterWorktree", "ExitWorktree", "Monitor", "TaskStop",
                   "SendMessage", "Artifact", "SubagentHandback", "ListAgents", "TaskCreate", "TaskGet",
                   "TaskList", "TaskUpdate", "CronCreate", "CronDelete", "CronList", "KillShell",
                   "BashOutput", "MultiEdit"})
CACHE_TTL = frozenset({"5m", "1h"})


def frontmatter(path: Path) -> str:
    return path.read_text().split("---\n", 2)[1]


def entries(head: str, field: str) -> list[str]:
    """Values of `field`: a comma-separated string, or the `  - item` lines of its YAML list."""
    match = re.search(rf"^{field}:[ \t]*(.*)$", head, re.M)
    if match is None:
        return []
    if match.group(1).strip():
        return [item.strip() for item in match.group(1).split(",") if item.strip()]
    items = []
    for line in head[match.end():].splitlines()[1:]:
        if not line.startswith("  "):
            break
        items.append(line.strip().removeprefix("- ").strip())
    return items


def unquote(value: str) -> str:
    return value.strip().strip("'\"")


def agent_file_problems(agents: Path) -> list[str]:
    """One line per problem: unknown top-level field, isolation set (R12c rule 3), effort missing (rule 2),
    an experimental entry other than cacheTtl 5m/1h, or a tools/disallowedTools entry naming no known tool."""
    problems = []
    for path in sorted(agents.glob("*.md")):
        head = frontmatter(path)
        keys = re.findall(r"^([A-Za-z][A-Za-z0-9]*):", head, re.M)
        problems += [f"{path.name}: unknown field {key}" for key in keys if key not in FIELDS]
        problems += [f"{path.name}: isolation set" for key in keys if key == "isolation"]
        problems += [] if "effort" in keys else [f"{path.name}: effort missing"]
        for entry in entries(head, "experimental"):
            key, _, value = entry.partition(":")
            if key.strip() != "cacheTtl" or unquote(value) not in CACHE_TTL:
                problems.append(f"{path.name}: experimental {entry}")
        for field in ("tools", "disallowedTools"):
            for entry in entries(head, field):
                name = unquote(entry).split("(", 1)[0]
                if name not in TOOLS and not name.startswith("mcp__"):
                    problems.append(f"{path.name}: {field} names no known tool: {entry}")
    return problems


def probe(tmp: str, body: str) -> list[str]:
    Path(tmp, "probe.md").write_text(f"---\nname: probe\ndescription: d\neffort: high\n{body}---\nbody\n")
    return agent_file_problems(Path(tmp))


class AgentFiles(unittest.TestCase):
    def test_project_agent_files_use_only_known_fields(self):
        """Every committed role file uses 2.1.300 fields and tool names, sets effort and leaves isolation unset."""
        self.assertEqual(agent_file_problems(AGENTS), [])

    def test_implementer_and_reviewer_deny_agent(self):
        """D189: the writer and the cold reviewer cannot spawn (spawn depth 1 is enforced here, not only by env)."""
        for role in ("implementer", "reviewer"):
            with self.subTest(role=role):
                self.assertIn("Agent", entries(frontmatter(AGENTS / f"{role}.md"), "disallowedTools"))

    def test_misspelled_field_is_reported(self):
        """A misspelled experimental map is reported instead of silently ignored."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(probe(tmp, "experimentl:\n  cacheTtl: 1h\n"), ["probe.md: unknown field experimentl"])

    def test_quoted_cache_ttl_is_valid_yaml(self):
        """`cacheTtl: "1h"` is the same YAML scalar as `1h` and passes."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(probe(tmp, 'experimental:\n  cacheTtl: "1h"\n'), [])
            self.assertEqual(probe(tmp, "experimental:\n  cacheTtl: 2h\n"), ["probe.md: experimental cacheTtl: 2h"])

    def test_misspelled_tool_is_reported(self):
        """`Agnet` in disallowedTools denies nothing; the test names it. Specifiers and MCP names pass."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(probe(tmp, "disallowedTools:\n  - Agnet\n"),
                             ["probe.md: disallowedTools names no known tool: Agnet"])
            self.assertEqual(probe(tmp, "tools: Read, Bash(git *), mcp__agentsview__search_content\n"), [])


if __name__ == "__main__":
    unittest.main()

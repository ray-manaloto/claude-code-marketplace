# roster-v2 retrospective — subagent caps and agent-file frontmatter (D189)

Unit: `roster-v2` (D189, DL-242; source R12c §1.1, §1.3, §7.3; request R-177 #141). Worktree
`.claude/worktrees/roster-v2`, branch `claude/roster-v2`, cut from allocation commit `cc07e8c`
(record `base_sha` `2c9d536`); lane commit `aeaa116` (4 files, +12/−3), retro commit `64d4cf2`; the integration tip
moved to `4726121` (R-175 handoff changes, no owned path touched) and was merged `--no-ff` as `30dc039`;
every required check below was rerun on the merged bytes with the same exits. Writer: implementer (Opus 5.5).
Takes effect at the user's restart: agent files and settings `env` load at session start.

Delivered, each name or key confirmed in the 2.1.300 offline copy
(`offline/research/R22-cc-2.1.300/raw/`; `docs/sub-agents.md` sha256
`a3d0eb3ac6090f2f2891c920fd365bccd34451ac29bbc546fd30db3d753e8099`, `docs/env-vars.md`
`367cfc9dee9c9edc5f1de8d847772cf48f8752c0a723ee6d167aa6099b38d8a5`, both equal to `docs/SHA256SUMS`;
`CHANGELOG-v2.1.300.md` `8c6fdbbd692bd9b2e108e9946948aa77200b6c8ffec4f807ea9c8cee92545139`):

| Change | Where | Confirmed by |
| --- | --- | --- |
| `env.CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS = "6"` | `.claude/settings.json` (env only) | env-vars.md:316; sub-agents.md:1049; CHANGELOG:3917 |
| `env.CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH = "1"` | `.claude/settings.json` (env only) | env-vars.md:322 ("set `1` to turn nesting off"); CHANGELOG:3857 |
| `disallowedTools: [Agent]`, `experimental: {cacheTtl: 1h}`, no `isolation` | `implementer.md` | sub-agents.md:291 (camelCase, unknown fields ignored), :301, :316-318, :1034 |
| `model: opus` (was fable, D189), `Agent` added to `disallowedTools` | `reviewer.md` | sub-agents.md:302 (`opus` alias), :1034 ("a reviewer that should stay read-only") |
| `experimental: {cacheTtl: 1h}`; step 4 says the record file is the deliverable and keeps the `<unit>.md` basename | `retro-writer.md` | sub-agents.md:316; CHANGELOG:3097; R12c §1.1 rule 4 (CC#101519) |

Keys not confirmed: none; every key written is in the 2.1.300 field table or env table. `effort`
values stay as they were (sub-agents.md:312). `cacheTtl: 1h` is ignored while the subscription
draws on usage credits (sub-agents.md:316): the setting is a request, not a guarantee.

Exits, run from the worktree with `VIRTUAL_ENV` unset, one literal command each, on the lane bytes:
`./dev/mise run test:doctor` rc 0 (14 tests); `./dev/mise run test:hooks` rc 0 (27 tests);
`./dev/mise tasks validate` rc 0 (68 tasks); `./dev/mise run check` rc 0 (91 tests, before and after
the retro commit); `./dev/mise run check:acceptance-baseline` rc 0 (19/19); `git diff --check` rc 0;
`./dev/mise run retro:gate -- roster-v2` rc 0 (the handoff carries the exit on the final bytes).
Scratch acceptance script (expected values from the lane record and DL-242, not from the files;
sha256 `47fca4ee21950a3e76d654f671b875e8293914e24aa10b366799e073d104d1d0`): rc 1 with 8 failures on
`cc07e8c`, rc 0 after the edit. The doctor flags nothing: `dev/doctor/settings.py` checks top-level
keys only (`env` is in `PROJECT_KEYS`), and `test_live_project_settings_hold_wave0_keys` still
reads `env.PLAN_ID` unchanged.

Review: not yet run by an independent reviewer at drafting time; the parent dispatches it
(owner: parent; the lane record names reviewer opus 5.5, high, cold).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: no static check reads `.claude/agents` frontmatter. `claude plugin validate --strict .claude` returns `contents: []` and passes; a probe plugin whose `implementer.md` says `experimentl:` also passes (rc 0). The doctor checks settings keys only. Claude Code ignores an unknown subagent field silently (sub-agents.md:291), so a typo would drop a roster setting unseen. | Parent edit A (below): `dev/test_doctor_agents.py`, picked up by `test:doctor` (`test_doctor*.py`). Verified in a scratch tree: rc 0 on the lane's agent files, rc 1 naming `implementer.md: unknown field experimentl` on the typo probe. Owner: parent (path `dev/` is excluded for this lane). |
| P2 | Steering: the reviewer model is fixed in four more places that still say Fable, and `frontier.toml` `[model_policy] review` feeds the per-call `model` that overrides the agent file (model-policy.md:23), so the frontier would keep dispatching the reviewer on Fable. | Parent edits B-E (below), exact text. Owner: parent (all four paths are excluded). Verification: `./dev/mise run test:frontier` and `check` after applying; no test asserts `review = fable` (`grep` of `dev/test_ticket_frontier.py`). |
| P2 | Navigation: the five roster-v2 roles that are briefs, not files (upgrade intake, test author, test-contract check, security reviewer, cross-vendor reviewer), have no home; `.claude/AGENTS.md` lists the agent files and also omits `frontier-scheduler`. | Parent edit F (below) for `.claude/AGENTS.md`. Owner: parent. |
| P3 | Information access: the runtime proof that 2.1.300 accepts the new frontmatter is `claude --debug` with no `does not recognize or apply` line for these files (sub-agents.md:292); it needs a fresh session, which this lane may not start. | Deferred, owner parent: at the user's restart run the debug-log grep once and record the rc beside D189. Edit A covers the static half. |
| P3 | Steering: R12c §7.3 also proposes the record-file brief line for `doc-writer.md`, `omitClaudeMd` for the extractor and a refute-first reviewer stance; none is in the lane's `delivers` or D189's text. | Rejected for this lane: outside the allocated contract (lane record `delivers`); held for the parent to allocate if wanted, owner parent. |

Coding standards: none — configuration and prose only; no code in `owned_paths`. Tool economy:
applied — the 89 KB R12c draft was read through its saved tool-result file by line range, check
logs went to the scratchpad and only tails were read. No-ops: none — each frontmatter line changes
runtime behaviour and the retro-writer sentence replaces a harness instruction the role would
otherwise follow. Information access is the P3 row above; navigation, steering and automated
checks are the P2 rows.

## Parent edits (exact text)

A. New file `dev/test_doctor_agents.py` (50 lines, sha256
`d564b4240d8a411f6dc3f474e4485f143ca03b88f70d54c642726ceaeab5b7d2`):

```python
"""Agent-file frontmatter keys (roster-v2 retro, D189): Claude Code ignores an unknown subagent field
without an error, and `claude plugin validate --strict` does not inspect `.claude/agents`, so a typo
such as `experimentl:` would silently drop the setting. Field set: sub-agents.md:296-316 at 2.1.300.
"""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = frozenset({"name", "description", "tools", "disallowedTools", "model", "permissionMode", "maxTurns",
                    "autoCompactWindow", "skills", "mcpServers", "hooks", "memory", "background",
                    "omitClaudeMd", "effort", "isolation", "color", "initialPrompt", "experimental"})
CACHE_TTL = re.compile(r"^experimental:\n((?:  .*\n)+)", re.M)


def agent_file_problems(agents: Path) -> list[str]:
    """One line per problem: unknown top-level field, isolation set (R12c rule 3), effort missing
    (rule 2), or an experimental entry other than cacheTtl 5m/1h."""
    problems = []
    for path in sorted(agents.glob("*.md")):
        head = path.read_text().split("---\n", 2)[1]
        keys = re.findall(r"^([A-Za-z][A-Za-z0-9]*):", head, re.M)
        problems += [f"{path.name}: unknown field {key}" for key in keys if key not in FIELDS]
        problems += [f"{path.name}: isolation set" for key in keys if key == "isolation"]
        problems += [] if "effort" in keys else [f"{path.name}: effort missing"]
        block = CACHE_TTL.search(head)
        entries = block.group(1).splitlines() if block else []
        problems += [f"{path.name}: experimental {line.strip()}" for line in entries
                     if line.strip() not in ("cacheTtl: 5m", "cacheTtl: 1h")]
    return problems


class AgentFiles(unittest.TestCase):
    def test_project_agent_files_use_only_known_fields(self):
        """Every committed role file uses 2.1.300 fields, sets effort and leaves isolation unset."""
        self.assertEqual(agent_file_problems(ROOT / ".claude" / "agents"), [])

    def test_misspelled_field_is_reported(self):
        """A misspelled experimental map is reported instead of silently ignored."""
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "probe.md").write_text("---\nname: probe\ndescription: d\neffort: high\n"
                                             "experimentl:\n  cacheTtl: 1h\n---\nbody\n")
            self.assertEqual(agent_file_problems(Path(tmp)), ["probe.md: unknown field experimentl"])


if __name__ == "__main__":
    unittest.main()
```

B. `.planning/2026-10-10-marketplace-macos-reflection-scaffold/frontier.toml` line 34:
replace `review = { model = "fable", effort = "high" }` with
`review = { model = "opus", effort = "high" }            # D189: model diversity from the cross-vendor reviewer`.

C. `.claude/skills/ticket-frontier/references/model-policy.md` (and its `.agents/skills/` mirror):
line 13 becomes
`| review | \`reviewer\` | opus | high | 1,000,000 | 500,000 | \`policy.review\` |`;
line 30 becomes `- (a) its kind is \`retro\`, \`synthesis\` or \`design\` (\`policy.<kind>\`);`.

D. `.claude/skills/ticket-frontier/SKILL.md` (and mirror) line 54: replace
`` `reviewer` (Fable, cold, fixed point `base_sha`)`` with
`` `reviewer` (Opus, D189; cold, fixed point `base_sha`)``.

E. `docs/agents/claude-team.md` line 16 becomes
`| reviewer | Opus | high | nothing | via the parent's brief | disposition PASS, PASS-with-P2/P3 or FAIL with unrun checks named |`.
Optional: `frontier.py:61` `FABLE_KINDS` keeps `"review"`; it only exempts that kind from
escalation and the dispatcher never computes it, so no behaviour changes either way.

F. `.claude/AGENTS.md` line 5 becomes:

```markdown
- `agents/`: role definitions (implementer, doc-writer, reviewer, retro-writer, extractor,
  frontier-scheduler). Five roster-v2 roles are briefs on these files, not files (D189, R12c §1.1);
  pass `model` and `effort` on every Agent call:
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
```

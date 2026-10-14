# Workflow retro gate correction, 2026-10-12

Scope: the current W4/W5 parallel-ticket workflow explanation and its local
agent-facing protocol. Primary sources were the user's correction, the
`mattpocock-skills:retro` and `writing-for-agents` skills, the current
`AGENTS.md`, `docs/agents/ticket-retro.md`, `docs/agents/issue-tracker.md`,
`docs/agents/codex-task-orchestration.md`, selected plan, and actual check
outputs. This record does not claim that unfinished A09 or #13/#28/#29 has
passed its own retrospective.

| Severity | Category and finding | Applied action | Verification |
| --- | --- | --- | --- |
| High | Navigation: the user-facing workflow omitted the already documented per-ticket retro, and the AGENTS pointer mentioned only a dependent ticket. | Made the pointer and W4/W5 gates apply to every ticket or task before integration or publication. | The parent inspected the changed pointer and plan; [worktree receipt](../../../evidence/workflow-retro-gate/worktrees.json) SHA-256 `ea33554e796ff0fef38cf1cc384fe0a315adee6ca9e48fe1b7ade8ecc1fe281f` records clean #13/#28/#29 checkouts at the same initial HEAD. |
| Medium | No-op/stale steering: the protocol still said unrelated tickets were held after the user expressly admitted #13/#28/#29. | Updated the retro and issue-tracker text to preserve the A06 hold while admitting those three isolated worktrees. | The selected plan names the exception; the linked worktree receipt records all three identities and clean states. |
| Medium | Information access: the prior workflow did not name where cross-scope retro fixes land or how open findings affect status. | Parent owns cross-scope fixes and final record; the ticket writer may draft only its own isolated retro. Actionable findings require application, checks, focused re-review and a repeat retro after material changes. An external blocker keeps the unit partial. | [Command receipt](../../../evidence/workflow-retro-gate/checks.json) SHA-256 `6a1e6d752fd95311a86130492307e363ea1df3a2f14de712e9dcf930b8d6413c`: task validation, project check, 19-file baseline and `git diff --check` all rc 0. |
| Medium | Independent review: the later plan paragraph retained a blanket hold, the protocol could skip partial units, and its skill invocation and check evidence were underspecified. | Named the #13/#28/#29 exception, covered partial/blocked outcomes, documented the user's explicit invocation of the skill, and bound command results to the receipt above. | Focused review supplied these findings; the parent applied each and requested a focused recheck. |

Automated checks: the existing static and baseline tasks ran; neither can prove
that a retrospective judgement was applied, so the parent and independent
reviewer inspect the finding ledger before integration. Coding standards: no
new judgement-only rule was found. Global AGENTS: no global change was needed;
the project pointer was shortened to the specific retro protocol. Tool economy:
no additional finding from this bounded document change. The four actions
above are applied; the issue-specific retrospective gates remain future work
because those units are not implemented or reviewed. Partial or blocked ticket
attempts still receive a retro against their available evidence.

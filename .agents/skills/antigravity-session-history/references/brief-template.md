# Takeover brief template

Give a synthesizer subagent the digest path, the conversation's known role, and
this template. Cap the brief at ~900 words; every non-obvious claim carries
`[created_at step=N]` from the digest. Keep these eight headings, in this
order, whatever the request emphasises; put the user's specific questions
(artifacts, approvals, commits, next actions) inside the matching section, so
every brief reads the same way to the next agent.

1. **Role and scope** — workspace, branches, files, artifacts (plans, walkthroughs, `task.md`) owned; subagents and background tasks it ran (ids, roles, what); what it explicitly did not own.
2. **Timeline of outcomes** — 8–15 bullets of completed units with commit SHAs, PR numbers and artifact `updatedAt` when the digest shows them.
3. **Explicit user decisions** — each direct instruction, `ask_question` answer, plan approval or rejection that still governs, quoted briefly; mark anything clipped.
4. **Last state** — the final three turns, last known HEAD/branch/remote, clean idle versus stopped on errors (a quota stop, a server restart that stopped subagents and background tasks, a killed conversation count as not clean); quote the error with model and reset time.
5. **In-flight / uncommitted / unpublished** — started but unfinished work, proposed-but-unapproved artifacts, open `task.md` items, stopped subagents and background tasks, each with the blocker and the path/SHA it depends on.
6. **Known blockers and gaps** — quota and reset time, model capacity errors, runtime, provider, host-heavy admission, ownership holds, awaited handoffs.
7. **Takeover checklist** — 5–10 concrete first actions (verify X, import Y from Z, leave W untouched), each bound to a path/SHA.
8. **Confidence notes** — clipped, truncated or database-only steps, the mirror-versus-database step gap, unread WAL bytes, opaque payloads, and what could not be established.

Rules for the synthesizer: never invent SHAs, paths or outcomes; say "clipped"
when the digest clips; distinguish proposed from user-approved; prefer
turn-final messages and the git-commit section over the step timeline when
they disagree.

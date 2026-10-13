# Takeover brief template

Give a synthesizer subagent the digest path, the thread's known role, and this
template. Cap the brief at ~900 words; every non-obvious claim carries
`[timestamp ord=N]` from the digest.

1. **Role and scope** — worktrees, branches, files, planning records owned; agents or peer threads delegated to (names + what); what it explicitly did not own.
2. **Timeline of outcomes** — 8–15 bullets of completed units with commit SHAs when the digest shows them.
3. **Explicit user decisions** — each direct instruction/approval/rejection that still governs, quoted briefly; mark anything clipped.
4. **Last state** — the final three turns, last known HEAD/branch/remote, clean `task_complete` vs aborted/failed (usage-limit failures count as not clean).
5. **In-flight / uncommitted / unpublished** — started but unfinished work with the blocker and the path/SHA it depends on.
6. **Known blockers and gaps** — runtime, provider, quota, host-heavy admission, ownership holds, awaited handoffs.
7. **Takeover checklist** — 5–10 concrete first actions (verify X, import Y from Z, leave W untouched), each bound to a path/SHA.
8. **Confidence notes** — clipped, encrypted or ambiguous records and what could not be established.

Rules for the synthesizer: never invent SHAs, paths or outcomes; say "clipped"
when the digest clips; distinguish proposed from user-accepted; prefer
turn-final messages and the git-commit section over the assistant timeline when
they disagree.

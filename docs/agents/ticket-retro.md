# Ticket and task retrospective gate

For every ticket or task outcome, including partial and blocked attempts,
run the lane retrospective below; its seven categories are those of the `retro`
skill. For implemented units, run it after tests and independent review; for
earlier blockers, inspect the evidence available and mark unrun steps explicitly.
`/mattpocock-skills:retro` is separate: the user types it per session and it only
proposes. Read the `writing-for-agents` skill before editing agent-facing
documents.
Use the [current ownership rule](codex-task-orchestration.md#ownership). The unit
writer applies in-scope fixes and drafts the retro in its allocated evidence
packet; a separately allocated local plan may hold it at
`.planning/<PLAN_ID>/retros/<unit-id>.md`. The parent owns reconciliation into the
shared plan and final acceptance; reviewers remain independent of implementation.

1. Read the unit's actual diff, command exits, receipts and reviewer findings.
   Inspect existing project checks and CI before proposing another guardrail.
   Audit the retro skill's navigation, automated-check, coding-standard,
   steering-file, tool-economy, no-op and information-access categories.
2. Record severity-ordered findings in the allocated retro record. For each,
   cite the source or receipt, name the concrete change, owner, verification
   and disposition.
   Record `none` with a reason for categories without a finding. Keep a
   mechanical rule in a deterministic check; send judgement-only standards to
   the reviewer. Keep `AGENTS.md` as a short navigation pointer.
3. Apply **every actionable finding** in the owning worktree or assign a
   cross-scope fix to the parent for immediate application. Rerun affected
   named checks and obtain focused independent re-review of the changed
   behavior. Repeat the retro after material fixes until no actionable finding
   remains. A future ticket, unverified suggestion or owner name does not
   close an action.
4. The parent records any external blocker with its exact failed receipt and
   admission condition, marks the unit partial, and keeps dependent integration
   or publication held. External blockers and non-actionable hypotheses keep
   their exact deferred disposition. A finding may be rejected only with a
   specific evidence-backed reason that it is inapplicable or harmful. Publish
   GitHub state only through its qualified mutation task.
5. For source task `01a130ef-265d-72b0-8465-80f3e4128bee`'s confirmed Q1/Q2
   allocation, hold the originating lane's next product
   task and affected dependency successors until every actionable retro finding
   is applied, checked and independently reviewed. The bounded repair itself may
   proceed through this barrier. Keep its findings and verification in the
   originating retro record instead of creating a new chain of retro tasks.
   Independent lanes may continue and dispatch ready work through their own gates.
   A separately authorized task's stricter explicit user barrier remains
   authoritative for that task; this rule does not relax it implicitly.
   An open lane is also affected when the repair changes its owned paths or
   required-check behavior: it may continue isolated edits, but must refresh and
   recheck before integration or acceptance. An external blocker keeps its actual
   dependents held; it does not turn a verified non-actionable hypothesis into an
   actionable fix. Recompute the affected frontier after the repair is accepted.
   Independently
   reviewed plan, documentation or completed implementation units may use an
   already-authorized branch publication once their own checks and retro pass.
   Finish that delivery through `delivery:prepare` and `delivery:publish`, then
   verify the remote SHA. A blocked native experiment does not withhold those
   eligible commits or turn their publication into runtime qualification.

`./dev/mise run retro:gate -- <unit>` checks only the record's shape: all
seven categories addressed, at least one verification binding (exit code,
`PASS`, SHA-256 or named check), and no open finding without an owner, blocker
or ticket. It exits 0, 2 with one reason per line, or 1 for usage. Judgement
about the findings stays with the independent reviewer.

The retro gate passes only when the record binds actual checks and every
actionable finding is applied, tested and independently reviewed or explicitly
rejected with an evidence-backed reason. Open or deferred actionable findings
keep the unit partial.
Implementation, testing, review, retro application, commit, integration and
publication retain separate statuses. The selected plan records the current
admission and ready frontier.

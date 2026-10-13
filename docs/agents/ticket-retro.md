# Ticket and task retrospective gate

For every ticket or task outcome, including partial and blocked attempts,
follow the user-invoked `$mattpocock-skills:retro` procedure. For implemented
units, do so after tests and independent review; for earlier blockers, inspect
the evidence available and mark unrun steps explicitly. The skill disables
automatic model invocation, so this standing user request is the invocation
authority. Read its `writing-for-agents` companion before editing agent-facing
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
5. On every ticket or task completion, hold **all new ticket dispatch** until
   every actionable retro finding is applied, tested and independently reviewed.
   Already-running independent siblings may finish with their own gates. An
   external blocker keeps its actual dependents held; it does not turn a verified
   non-actionable hypothesis into an actionable fix. Recompute the frontier only
   after this dispatch barrier settles. Independently
   reviewed plan, documentation or completed implementation units may use an
   already-authorized branch publication once their own checks and retro pass.
   Finish that delivery through `delivery:prepare` and `delivery:publish`, then
   verify the remote SHA. A blocked native experiment does not withhold those
   eligible commits or turn their publication into runtime qualification.

The retro gate passes only when the record binds actual checks and every
actionable finding is applied, tested and independently reviewed or explicitly
rejected with an evidence-backed reason. Open or deferred actionable findings
keep the unit partial.
Implementation, testing, review, retro application, commit, integration and
publication retain separate statuses. The selected plan records the current
admission and ready frontier.

# team retrospective — roles, rules, team guide, vocabulary and ADR 0001

Unit: `team` (ticket CT-03 of the takeover spec). Worktree `.claude/worktrees/team`,
branch `claude/team-roles-rules`, lane commit `9103931` on base `361688e`,
repairs at `ea8c8c9` (includes the merge of `447110a`). Delivered: five project
agent roles under `.claude/agents` (implementer/opus, doc-writer/sonnet,
reviewer/fable, retro-writer/fable, extractor/haiku; reviewer and extractor
cannot write), three path-scoped rules under `.claude/rules`
(`.planning/**`, `dev/**`, `evidence/**`, 11–14 lines each),
`docs/agents/claude-team.md` (70 lines), `docs/adr/0001-claude-takeover-and-retro-gate.md`
(46 lines) and the glossary Workflow section (existing research terms
byte-identical). Exits recorded by the writer and both reviews: `tasks validate`
rc 0, `check` rc 0, `check:acceptance-baseline` 19/19 rc 0, `git diff --check`
rc 0, every cited path resolves or is marked as arriving with a named ticket.

Independent Fable cold review: **PASS-with-P2**; focused re-review of the
repairs: **PASS for integration**, no remaining P1/P2.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Information access: the planning rule prescribed a seven-column retro row and an opening paragraph that no existing record follows — a second source of truth beside the retro protocol. | Applied: the rule points to `docs/agents/ticket-retro.md` as the single shape source and lists the three things the gate checks; implementer and retro-writer point there too. Verified by the re-review (`planning-records.md:8`, 11 lines). |
| P2 | Steering: the reviewer read the gate invocation `retro:gate -- <unit>` as a mismatch with the gate script's `--unit`. | Rejected with evidence: the `retro:gate` mise task takes a positional unit and passes `--unit` to the script, so the documents were right; the retro-gate lane record's `required_checks` text was the wrong source and the parent corrected it. |
| P3 | Navigation: forward references named a lane ("GATE-2") that does not exist and cited `CODING_STANDARDS.md` and `retro:gate` without saying they arrive later. | Applied: references name tickets CT-02/CT-04/CT-01 and give the `python3 -I dev/retro_gate.py --unit <unit>` fallback where agents read them; the parent rechecks citations at each of those integrations. |
| P3 | Steering: several steps lacked a completion criterion; the guide restated the roles table and the ADR consequences; the five-files/300-lines bound appeared in three places. | Applied: completion criteria added; restatements removed (guide 78 → 70 lines); the bound lives only in `implementer.md`. |
| P3 | Information access: ADR context stated the motive without the observed failure. | Applied: the ADR now records that the draft gate, calibrated against 33 Codex retro records, found 17 that skipped a category. |
| P3 | Information access: the lane record was committed after the worktree was cut, so the lane read it from the integration branch. | Applied by the parent as a convention (plan: commit the lane record before cutting the worktree); later lanes follow it. |
| P3 | Automated checks: nothing lints `.claude/agents` frontmatter fields or the rule line cap. | Deferred with owner: routed to ticket CT-02 (hook wiring) as a small `dev/check.py` addition; verification there. |

Coding standards: none — documentation only; `CODING_STANDARDS.md` arrives with
CT-04. Tool economy: applied — each file was written in one pass and the checks
ran once per cycle. No-ops: applied — restated ownership rules and bare
prohibitions in the draft bodies were cut or paired with a positive target.
Integrated by the parent with composed-tree gates `tasks validate` rc 0,
`check` rc 0, `check:acceptance-baseline` 19/19 rc 0, `git diff --cached --check`
rc 0. A remaining P3 from the re-review — the record-shape paragraph in
`ticket-retro.md` lands with CT-01 — is owned by the retro-gate lane.

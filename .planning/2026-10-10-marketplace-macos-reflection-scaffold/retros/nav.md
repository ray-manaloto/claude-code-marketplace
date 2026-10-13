# nav retrospective — guidance hierarchy (CT-04)

Unit: `nav` (ticket CT-04 of the takeover spec). Worktree `.claude/worktrees/nav`,
branch `claude/nav-guidance-hierarchy`, lane commit `5cadad4` on base `c6ff7ef`,
repairs `6dc421e`, merged with `937042d` as `6840342`. Delivered: root
`AGENTS.md` cut from 70 to 60 lines as a navigation pointer; `AGENTS.md` plus
`@AGENTS.md` importer pairs for `dev/` (30 lines), `docs/` (32), `evidence/`
(8), `.planning/` (14) and `.claude/` (13); `CODING_STANDARDS.md` (66 lines,
13 judgement rules; mechanical rules named with their checks). Exits recorded
by the writer and both reviews: `tasks validate` rc 0, `check` rc 0,
`check:acceptance-baseline` 19/19 rc 0, `git diff --check` rc 0; every relative
pointer resolves or names the ticket that creates its target. A first batch of
named checks returned a transient `mise ERROR` that passed on rerun while two
other lanes ran checks — the second concurrent-check race of the day.

Independent Fable cold review: **PASS-with-P2**; focused re-review of the
repairs: **PASS for integration**, no remaining P1/P2.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Steering: the lane's own files restated each other — the evidence rule, the unit-size rule in three places, the dev-tests rule inside `CODING_STANDARDS.md`. | Applied in `6dc421e`: pointers replace restatements; the unit-size rule lives only in `docs/agents/codex-task-orchestration.md`; `CODING_STANDARDS.md` went from 18 rules to 13. Re-review verified zero restatements. |
| P2 | Navigation: the completion contract was unreachable from the hierarchy though `CODING_STANDARDS.md` cited its preservation list. | Applied: `.planning/AGENTS.md` lists `completion-contract.md` as the source of the standing workflow and preservation list. |
| P2 | No-ops: three instructions from the old root file were dropped without an owner ("do not install plugin runtimes just to lint", "avoid redundant project copies of global skills", "do not copy Claude hooks or slash commands into Codex configuration"). | Applied: restored in the files that own them; the parent then named the sanctioned skill exceptions (`gh-stack`, repository-authored skills with their mirror) in `.claude/AGENTS.md` at integration. |
| P3 | Information access: inaccuracies — `.gitignore` listed beside rather than among the 19 baseline files, every directory claimed to have an importer, CT-01 described as pending, five `docs/agents` files missing from the map. | Applied in `6dc421e`; the plugin directory's missing `CLAUDE.md` importer is stated with a later lane as owner. |
| P3 | Coding standards: implementer design rules and already-mechanical rules had crept into the reviewer file. | Applied: former rules 4–6 and 11 became `dev/AGENTS.md` pointers, the retro-finding rule points at `dev/retro_gate.py`, the allowlist rule names the merger with CT-02 as mechanical owner. |
| P3 | Automated checks: nothing keeps root `AGENTS.md` at sixty lines or verifies that pointers resolve. | Deferred with owner: ticket CT-02 adds the line-cap and pointer checks to the hook/check lane; until then the merger checks `wc -l` and `rg --files` at integration (done here: 60 lines, all pointers resolve). |
| P3 | Navigation: `plugins/aggregated-research/AGENTS.md` has no `CLAUDE.md` importer, so Claude Code loads it only where no `CLAUDE.md` exists above it. | Deferred with owner: a later lane adds the thin importer (the path was excluded from this lane); the root file states the gap. |
| P3 | Tool economy: the first batch of named checks raced with other lanes' checks (transient `mise ERROR`, rc 0 on rerun). | Deferred with owner: ticket CT-11 (serialize named checks across worktrees with a lock); the raced run is recorded, not counted. |

Root `CLAUDE.md` duplication of the issue-tracker pointer was removed by the
parent at integration (`.claude/rules/dev-tests.md` accuracy was fixed earlier
at `937042d`). Integrated with composed-tree gates `tasks validate` 52 rc 0,
`check` rc 0, `check:acceptance-baseline` 19/19 rc 0, `git diff --cached --check`
rc 0.

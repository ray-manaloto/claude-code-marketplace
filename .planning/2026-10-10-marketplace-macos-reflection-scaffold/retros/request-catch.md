# request-catch retrospective: request projection and catch in dev/handoff.py (CT-90, D167)

Unit `request-catch` (CT-90, D167, a dated D113 exception). Worktree `.claude/worktrees/request-catch`,
branch `claude/request-catch`, `base_sha` `0331316`, cut from the allocation commit `3d5b181`, so
`git log 3d5b181..HEAD` is the lane. Commits, in order: `149f238` (catch, roll-call, test
environment), `511ee08` (merge of the integration tip `0e063ce`, clean), `52b7a96` (roll-call label),
`ee64a19` (implementer draft of this record; the reviewed SHA), `c361751` (retro fixes; the checked
SHA), then the commit carrying this record (the final SHA, in the hand-back). The implementer wrote
as Claude Opus 5.5 (`Co-Authored-By` on `149f238`, `52b7a96`, `ee64a19`), matching the record's
`writer_model`; the retro-writer is Claude Fable 5.1 and its commits carry the lane's trailer. The
independent cold review (reviewer, Fable, read-only) returned PASS with P2/P3 on `ee64a19`; its six
findings are RV-1 to RV-6 below, the implementer's draft findings RC-1 to RC-11.

Delivered, test-first through the CLI seam (`check --json` exit codes and finding ids,
`write --dry-run` output). Every test below failed before its change:
- `requests` in `state --json` and `check --json`: ledger path and presence, owner session,
  `captured`, `foreign`, `unkeyed`, `unprojected`, `open`, `unlinked`, `user`. An absent ledger is
  reported there and is not a finding.
- `H.request-unprojected` (P1): an owner-session ledger key with no `p:<id8>` in `## Open requests`
  and no `dispositions.jsonl` row. `H.request-unlinked` (P2): an open `- [ ] R-n` item with no
  `issue: #N`, no bare `· #N ·` field and no GitHub issue URL. Ticked items are closed.
- `write` replaces the template's `pending-user` text with a generated roll-call bullet:
  `Open requests: N open, K unlinked, U/C captured unprojected (ledger|no ledger); Pending user:
  <owner user ids>; ids: <open ids>.` A template that still has a `pending-user` section makes
  `write` refuse (rc 1, with a reason). An over-budget roll-call also refuses with rc 1 and names
  its line share.
- Every new function, constant group, branch and wiring line carries the comment "D167, dated
  D113 exception; the C++ requests module CT-93a deletes it".

Fixtures cover the five cases the brief names: unprojected, projected but unlinked, linked, ticked
with evidence, and absent ledger; further tests cover another session's rows (counted as `foreign`,
not caught), a disposition closing a key, unkeyed rows, an answer keyed by its tool use, the bare
`· #N ·` issue field, and the template and budget refusals. Size: 4 maintained files plus 2
byte-identical mirrors, plus the pre-authorized widening to `mise.dev.toml`, `SKILL.md` and
`evals/evals.json` (RV-1, RV-5). Handwritten lines, `git diff --numstat 3d5b181 HEAD` outside the
merged planning files: `dev/handoff.py` +87/-8, `dev/test_handoff.py` +156/-6, `predicate.md`
+14/-1, `handoff-template.md` +4/-4, `SKILL.md` +9/-6, `evals.json` +3/-2, `mise.dev.toml` +6/-1.

Exits on `c361751`, `VIRTUAL_ENV` unset, one worktree at a time:
- `python3 -I -m unittest discover -s dev -p test_handoff.py`: 47 tests OK, rc 0 (45 at `ee64a19`,
  36 at `3d5b181`). `./dev/mise run test:handoff`: rc 0, 47 tests.
- Red first for the two new tests, with `dev/handoff.py` stashed at `ee64a19`: rc 1
  (`test_foreign_session_rows_are_counted_not_caught` KeyError `foreign`;
  `test_bare_issue_field_links_an_item` unlinked `['R-171', 'R-172', 'R-173'] != ['R-173']`).
- `./dev/mise tasks validate`: rc 0 (65 tasks, one more than the draft's 64: `test:handoff`).
- `./dev/mise run check`: rc 0. `./dev/mise run check:acceptance-baseline`: rc 0 (19 baseline hashes).
- `diff -r .claude/skills/session-handoff .agents/skills/session-handoff`: rc 0, empty.
- `git diff --check`: rc 0. hk `pre-commit` (`check:records`) ran on the fix commit and passed.
- `./dev/mise run retro:gate -- request-catch`: run on this record before its commit; rc in the
  hand-back.

`python3 -I dev/handoff.py check --json --agents-done` exits rc 2 in this worktree on every run,
on worktree-only findings (`H.handoff-stale-sha`, `H.head-not-remote`, `H.receipt-missing`,
`H.pending-decision-unlisted`: no `origin/claude/request-catch`, the cited HEAD is the root's); the
request object reads 24 open, 0 unlinked, 0/0 captured unprojected, `foreign` 0, no ledger, and no
request finding. The same reason makes `write --dry-run` exit 2 here, so the block budget (RC-4) is
measurable only in the root checkout. The live request results in the lane's history: before the
merge (`149f238`) `H.request-unlinked` P2 listed all 23 open items, R-119 to R-170; after the merge
of `0e063ce` 0 unlinked (#112 to #135 are linked).

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P1 | RC-1 Information access: the CT-87 probe receipt (`reviews/ccm-20261014/context-loss/CT-87-probe-receipt.md:41`) shows `prompt_id` on every payload of a turn, so an AskUserQuestion answer row carries its turn's `prompt_id`. The first key, `prompt_id or tool_use_id`, folded each answer into the prompt's key, so projecting the prompt would have closed the answer silently. (Implementer.) | `149f238`: answer rows key on `tool_use_id`. `test_answer_row_is_keyed_by_its_tool_use_not_its_turn` failed first, then passed; 47 tests OK, rc 0 on `c361751`. | Applied. |
| P1 | RC-2 Coding standards: every Claude `tool_use_id` begins `toolu_01`, so the first 8 characters CL4 E2 prescribes would give every answer the same key (one disposition would close all of them). (Implementer.) | `149f238`: an answer's `<id8>` is the last 8 characters of `tool_use_id`; a prompt's is the first 8 of `prompt_id`; disposition keys match exactly; the rule is in `predicate.md`. The same test, with two answers, failed first and then passed. | Applied. |
| P2 | RV-1 Steering: `handoff-template.md:27` kept the retired pending-user items (purge request, guard and C++ check tickets, Q2-order-v2 §6 U1-U5) as an optional note that drops from the block when the budget is full, and `SKILL.md:16`, `SKILL.md:28` and `evals.json` eval 3 (both mirrors) still told agents to edit `## pending-user`, which `write` now refuses. (Reviewer P2; implementer RC-5, RC-6.) | Confirmed read-only in the root `task_plan.md` `## Open requests`: R-056 (`owner user`, `issue: #125`), R-172 and R-173 (`owner user`, purge request and Q2-order-v2 §6) carry the items. `c361751`: the note is deleted from both templates; `SKILL.md` line 16 names the generated roll-call and `Pending user` lines and step 2 sends what the user owes to an `owner user` R-n line; eval 3 asks for R-172 and expects the `owner user` line, with one new expectation. `diff -r` of the mirrors rc 0, empty; `test:handoff` rc 0 (`SkillFilesTests` read both). The widening the parent pre-authorized is recorded in parent edit 2. | Applied (widened paths, parent edit 2). |
| P2 | RV-2 Coding standards: CL4 E2 (`CL4-proposal.md:119`) says `p:<first 8 of the key>`; the lane keys an answer on the last 8 of `tool_use_id` (`dev/handoff.py:55`, `:335` at `ee64a19`). (Reviewer P2; RC-2 is the cause.) | Evidence for closing: lane request-hooks' cold review evaluated the `requests:tail` jq key against `dev/handoff.py:335@ee64a19` on 5 fixture rows at `9a902a2`: MATCH (`p:ff1c3221`, `p:rY2dE1Hy`, `p:abcd1234`, `p:`, `p:`), jq exit 0 (`request-hooks.md:32-34` in that worktree); the task's description states the rule. The remaining drift is the parent-owned review file: parent edit 1 corrects E2's wording. The implementer's parent edit 3 (tell lane request-hooks) is closed by the same evidence. | Applied in code and `predicate.md`; CL4 text deferred to the parent, admission condition: parent edit 1 applied at integration. |
| P2 | RC-4 Automated checks: the live `## Next Step` block is at 16 of 16 lines; the roll-call takes 3 and the agents/owner bullet 3, every optional line already drops, and a few more open requests or one more allocated lane make `write` refuse by design. (Implementer, measured with `render` on `52b7a96`.) | The draft's remedy (drop "D61 format, D76" from the template's `owner` sentence because HANDOFF §8 carries them) is rejected with evidence: `grep -nE 'D61|D76'` over §8 of `reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md` matches nothing, so the edit would lose a pointer, not cache one. The budget is the root checkout's to manage: tick closed requests with their evidence, or shorten the `## action` sentence at the next handoff. Verification: `python3 -I dev/handoff.py write --dry-run --agents-done` in the root prints `dry-run:` and no `exceed`. | Deferred, owner parent; admission condition: the next handoff's dry-run rc 0. |
| P2 | RC-3 Automated checks: the fixtures in `dev/test_handoff.py` ran `git commit` under the user's real global Git config, so the user's global hk hooks fired inside the tests (`.claude/rules/dev-tests.md`; a09-hook-events retro P-2, relayed through the lane record). | `149f238`: `pinned_git_env()` sets a scratch HOME and `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM=1`, drops inherited `GIT_*` and `VIRTUAL_ENV`, and wraps every fixture. `test_global_git_hooks_never_fire_in_fixtures` uses marker hooks in the caller's global config; with a no-op helper it failed ("pre-commit" written), with the pin it passes. Suite time fell from about 35 s to about 20 s. `python3 -I -m unittest discover -s dev -p test_handoff.py` rc 0, the receipt a09's E3 asked for. | Applied. |
| P3 | RV-3 Automated checks: the catch scopes ledger rows by the owner line's session id (`dev/handoff.py:330-336`, CL4 §4.5); a stale owner line drops every row and the catch passes silently. (Reviewer P3; implementer RC-7.) | `c361751`: `requests.foreign` counts the ledger rows of other sessions (`dev/handoff.py:338`) so an owner mismatch is visible in `check --json` and `state --json`; `predicate.md` lists the field. `test_foreign_session_rows_are_counted_not_caught` (rc 1 before, rc 0 after). The classifier that scopes by lineage is CT-93a's. | Applied as a count; the scoping fix deferred to CT-93a, owner parent, admission condition: CT-93a allocated. |
| P3 | RV-4 Coding standards: the rule-14 markers were missing on the two wiring lines `dev/handoff.py:402` (`state` adds `requests`) and `:657` (`print_findings` emits it). (Reviewer P3.) | `c361751`: both lines carry `# D167, dated D113 exception; CT-93a deletes it` (now `:404` and `:659`); `grep -c 'CT-93a' dev/handoff.py` gives 15. `check` rc 0. | Applied. |
| P3 | RV-5 Automated checks: no gate ran `dev/test_handoff.py`; `dev/check.py:76` discovers `test_research_*` only, and `mise.dev.toml` had no `test:handoff` task, so the existing suite was not wired in (`.claude/rules/dev-tests.md` names the two routes). (Reviewer P3.) | `c361751`: `[tasks."test:handoff"]` at `mise.dev.toml:356-359` (`python3 -I -m unittest discover -s dev -p test_handoff.py -v`) and `"test:handoff"` appended to `check:research`'s `depends` at `mise.dev.toml:118` (the surface the hosted research-fast workflow runs). `./dev/mise tasks validate` rc 0 (65 tasks); `./dev/mise run test:handoff` rc 0, 47 tests. Widening recorded in parent edit 2. | Applied (widened paths, parent edit 2). |
| P3 | RV-6 Coding standards: `LINK_RE` (`dev/handoff.py:55`) accepted `issue: #N` and an issue URL only, so the bare `· #N ·` field CL4 §4.2 prescribes (`- [ ] R-171 · p:4462d3b1 · D114 · CT-86 · #136 · owner parent · text`) read as unlinked. (Reviewer P3.) | `c361751`: `LINK_RE` also accepts `#N` as its own `·`-delimited field (`(?<=· )#\d+(?= ·|$)`); a bare number inside prose (`see #109 in the republish notes`, `see upstream #102134`) stays unlinked. `test_bare_issue_field_links_an_item` rc 1 before, rc 0 after; `predicate.md` names the three forms. | Applied. |
| P3 | RC-8 Automated checks: a ledger row with neither `tool_use_id` nor `prompt_id` cannot be projected or disposed. (Implementer.) | Applied as a count (`requests.unkeyed`) with a test. A P1 finding is rejected with evidence: such a row could never be cleared, so `write` would refuse permanently; the CT-87 receipt shows `prompt_id` on every prompt payload, so the count stays 0. | Applied as a count. |
| P3 | RC-9 Coding standards: `.claude/rules/dev-tests.md` asks for fixtures under `dev/fixtures/<topic>/`. (Implementer.) | Rejected with evidence: the suite's fixtures are scratch Git repositories with worktrees and a bare origin, built in code as the 36 pre-existing tests do; a static fixture directory cannot hold a live `.git`, and the ledger rows are three-line literals beside their assertions. | Rejected. |
| P3 | RC-10 Tool economy: two zsh slips cost one call each (`echo =====`, zsh `=` expansion; an unquoted `--include=*.md`), and the retro-writer lost one call to `${PIPESTATUS}` (zsh spells it `pipestatus`). The first merge was refused by the git-merge deny gate because its `-m` text named the lane branch and the lane retro did not exist yet; lane step 4 (merge) comes before step 5 (retro). (Implementer; retro-writer.) | Applied in the lane: quoted globs, `#####` separators, exit codes captured in `$?` after a redirect, and `git merge --no-edit <integration>` with the message amended afterwards to carry the trailers without naming the branch. The merge-step sentence belongs in the implementer role file (`.claude/agents/implementer.md:17`, outside `owned_paths`): parent edit 3. The zsh slips stay a transcript gotcha, as retro a09-hook-events ruled: the Bash tool's shell is host configuration, not a project convention. | Applied in-lane; the role sentence deferred to the parent, admission condition: parent edit 3 applied at integration. |
| P3 | RC-11 Navigation: the brief maps CL4's "CT-89 projection and catch" to CT-90, and CL4 calls the C++ module CT-92 while D167 names CT-93a. (Implementer.) | No change needed: the code comments name D167 and CT-93a (the decision of record); this record states the mapping, and the lane record's `import_source` already says "CT-89 there, CT-90 here". | Rejected (already navigable). |

No-ops: none. Each code change has a test that failed first (red exits above); the one wording
change without its own test, the shorter pending-operations bullet, is asserted by
`test_rendered_shapes`, which failed before it. No sentence was added to an `AGENTS.md`.

Steering and global guidance: no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or `.claude/agents`
file changed in the lane. The `session-handoff` skill (`SKILL.md`, evals, both mirrors) changed
under the pre-authorized widening (RV-1); the one role-file sentence is parent edit 3.

Information access: the reviewer's and the implementer's findings reached this record through the
parent's brief and the draft; the lane record's `review` and `retro` fields are null until the
parent records them (parent edit 2). Nothing in the lane reads `~/.codex`, a provider or the
network; the request ledger resolves under the scratch HOME in every test.

## Parent edits (outside `owned_paths`; literal, apply unread)

1. `reviews/ccm-20261014/context-loss/CL4-proposal.md` line 119 (section 4.1, Echo): replace
   `` `[requests] captured p:<first 8 of the key>; open requests: <N>` `` with
   `` `[requests] captured p:<id8>; open requests: <N>` `` and append, after "over the plan.", the
   sentence: "`<id8>` is the last 8 characters of `tool_use_id` for an AskUserQuestion answer (every
   id starts `toolu_01`) and the first 8 of `prompt_id` for a prompt (request-catch RC-2; the
   `requests:tail` key matches `dev/handoff.py`)." Verification: `grep -c 'first 8 of the key'
   reviews/ccm-20261014/context-loss/CL4-proposal.md` prints 0.
2. `lanes/request-catch.json`: append to `notes`: "retro widening (pre-authorized): `mise.dev.toml`
   line 118 (`check:research` depends gains `test:handoff`) and lines 356-359 (`[tasks.\"test:handoff\"]`);
   `.claude/skills/session-handoff/SKILL.md` lines 15-17 and 29-32 and `evals/evals.json` eval 3
   (lines 30-31, 35), with the `.agents/skills/session-handoff` mirrors byte-identical". Set `status`
   to the integration state the parent reaches, `review` to "PASS with P2/P3 on `ee64a19`
   (reviewer, Fable, cold)", `retro` to "`retros/request-catch.md` at <final SHA>, gate rc 0".
   Verification: `python3 -I -c "import json; json.load(open('lanes/request-catch.json'))"` rc 0.
3. `.claude/agents/implementer.md` line 17, after "Merge the current integration tip into your
   branch and rerun the affected checks.": add "Use `git merge --no-edit <integration-branch>`
   and amend the message afterwards to add the trailers: a merge message that names the lane
   branch trips the retro deny gate before the lane's retro record exists." Verification:
   `grep -c 'merge --no-edit' .claude/agents/implementer.md` prints 1.

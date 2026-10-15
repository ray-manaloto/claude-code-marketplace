# handoff-skills retrospective: session-handoff and session-resume cover the /quit restart, the CLI check and the startup log

Unit `handoff-skills` (skills audit S3, S5, S6, S8, S9 doc line, S12; handoff-script parent edits
2-5; R-175, #139). Worktree `.claude/worktrees/handoff-skills`, branch `claude/handoff-skills`,
`base_sha` `3834661`, cut from the allocation commit `2b06eb3`, so `git log 2b06eb3..HEAD` is the
lane. Commits, in order: `535d61d` (the skill changes), `484f1c8` (merge of the integration tip
`65541f4`), `521b3e7` (the writer's draft of this record), `c037168` (template trimmed to the
budget), `b087860` (merge of the integration tip `b1dc645`; the reviewed tip), `696d338` (merge of
the integration tip `6257246`, `--no-ff`, message file with the trailers, which brings lane
handoff-script as `4726121`), then the commit carrying the review fixes and this record (the final
SHA, in the hand-back). Writer: Claude Sonnet 5.5, matching the record's `writer_model`. Cold
review: Opus 5.5, read-only, on `b087860`: one P1 (merge order), two P2s, three P3s, relayed by
the parent. Retro writer: Fable 5.1, high; this is the retro-writer pass over the writer's draft.

Delivered, in the `.claude/skills/` copies and byte-identical in `.agents/skills/`:
- `session-handoff/SKILL.md`: step 1 counts this session's background Bash commands and Monitor
  tasks as running work (2.1.300 force-kills a background command 1.5 s after exit, S8, S4 by
  hand) and lists them from the session's own task ids (RV-P3-3); step 2 says the owner sentence
  holds no session name and sets the CLI row from `claude --version`; step 5 prints the `sh`
  block of HANDOFF §8 as `write` wrote it, the one start command (RV-P2-1), and offers three
  restart paths, one only: `/clear` then `/session-resume <name>`; `/quit` (ignore the printed
  `claude --resume` line) then the start command; or the start command without its prompt, then
  `/reload-skills`, `/reload-plugins` (never `--force`) and `/session-resume <name>` (S3). The
  description gains `/quit` triggers.
- `handoff-template.md`: no session name in `## owner` (handoff-script edit 4; `write` names the
  session with `next-name`); a CLI row "2.1.300 installed; the handing-off session ran 2.1.299";
  an `action` in the one shape "First <R-n> release intake (<report paths>). Then <work>."
  (RV-P3-2); notes read "decisions through D188" (S5). The block stays inside the 16-line budget
  (HS-2).
- `probe-commands.md`: the restart fire (`"source":"startup"`) and `startup` in the pass criteria
  (S9, handoff-script edit 3); the w0-doctor worktree fallback is gone (S6). `predicate.md`: the
  `H.injection-probe-failed` row lists four fires, matching `dev/handoff.py`.
- `session-resume/SKILL.md`: step 1 runs `claude --version` and puts the R-176 intake first when it
  differs from the version the CLI row says the handing-off session ran; step 4 runs the four
  checks of `session-start/SKILL.md` "Detect a failure after a restart", quoted by name, with
  `SID=${CLAUDE_SESSION_ID}` (RV-P3-1, RV-P2-2); step 6 passes `--session-id ${CLAUDE_SESSION_ID}`
  on every path (RV-P2-2); the doctor step loses the w0-doctor fallback (S6); the description
  names the `/quit` restart.
- Evals: each skill gains a `/quit`-and-upgrade eval (handoff 4, resume 3); handoff evals 1, 3
  and 4 expect HANDOFF §8 as the start command and no `start-command` run; resume evals 1-3
  expect `--session-id ${CLAUDE_SESSION_ID}` and the four named checks (S12).

Size: 14 files in two identical trees, 7 maintained. `git diff --numstat 2b06eb3 535d61d` shows
112 added and 51 removed lines in the `.claude/skills/` copies; the retro pass adds 49 and
removes 36 across the five maintained files.

Exits on the merged bytes `696d338` plus the retro-pass edits, from the worktree, `VIRTUAL_ENV`
unset, one literal command each:
- `diff -r .claude/skills/session-handoff .agents/skills/session-handoff`: rc 0.
  `diff -r .claude/skills/session-resume .agents/skills/session-resume`: rc 0.
- `python3 -I -m json.tool` on each of the four `evals.json` files: rc 0 each.
- `./dev/mise tasks validate`: rc 0. `./dev/mise run check`: rc 0 (`"status": "pass"`).
  `./dev/mise run check:acceptance-baseline`: rc 0 (19 hashes).
- `git diff --check`: rc 0 (also rc 0 before the commit on the unstaged tree).
- `./dev/mise run test:handoff`: rc 1 before RT-1 (`FAILED (failures=1)`,
  `test_skill_report_types_resume_only_after_clear`), rc 0 after (61 tests OK).
- `./dev/mise run retro:gate -- handoff-skills`: run on this record; the rc is in the hand-back.
- `git merge-base --is-ancestor 4726121 HEAD`: rc 0 (handoff-script is merged, RV-P1).
- Budget probe, `python3 -I dev/handoff.py write --dry-run --agents-done` in this worktree: the
  regenerated `## Next Step` block is 15 lines of at most 100 characters (limit 16) and the NEXT
  bullet 8 lines of at most 100 (limit 12); the NEXT bullet names the generated session
  `ccm-20261014T195015.947578000-05` and no line holds `next-session`. The command exits rc 2
  with "write refused: the regenerated handoff still fails the check", from worktree-only
  findings (`H.receipt-missing` for the lane worktrees and the ignored local
  `offline/research/R22-cc-2.1.300/`, `H.head-not-remote`, `H.request-unprojected`,
  `H.request-unlinked` R-179 and R-180, `H.mode-not-inject-smart`), none of them a budget error.
- Verification greps on the final bytes: `grep -c 'the only start command you print'
  .claude/skills/session-handoff/SKILL.md` prints 1; `grep -c 'CLAUDE_SESSION_ID'
  .claude/skills/session-resume/SKILL.md` prints 3; `grep -c 'Detect a failure after a restart'
  .claude/skills/session-resume/SKILL.md` prints 1; `git show
  claude/ct35a-session-start-mod:.claude/skills/session-start/SKILL.md | grep -c 'Detect a failure
  after a restart\|events.jsonl'` prints 4 (ct35a tip `02c497c`).

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P1 | RV-P1 Automated checks (cold review): `b087860` documented `next-name`, `start-command --session-id` and the `write` fallback before the branch that defines them (lane handoff-script) was in the lane's history, so the skills steered agents at commands the merged tip did not have. (Reviewer, on `b087860`.) | Applied: `696d338` merges the integration tip `6257246`, which holds handoff-script as `4726121`. Verification: `git merge-base --is-ancestor 4726121 HEAD` rc 0; `./dev/mise run test:handoff` rc 0 on the merged `dev/handoff.py`. |
| P2 | RV-P2-1 Steering (cold review): step 5 ran `start-command` after `write`, and each call mints its own `next-name` and `uuid4`, so the `## Next Step` block and HANDOFF §8 named one session and the pasted command another. The merged `dev/handoff.py` has `write --name` but no `write --session-id`, and `section_start` calls `start_command(ctx, name, None)`, so a shared name alone cannot pin the id; §8 is the single source. (Reviewer; `dev/handoff.py:841-867`, `:1029`.) | Applied in this lane: step 5 prints the `sh` block of HANDOFF §8 verbatim (the `sed` range is in the step) and says `start-command` run now would mint a second pair; handoff evals 1, 3 and 4 expect §8 and no `start-command` run. No code change is needed; parent edit 6 aligns `--help`. Verification: `grep -c 'the only start command you print' .claude/skills/session-handoff/SKILL.md` prints 1; mirror diff rc 0; the dry-run NEXT bullet names the generated session. |
| P2 | RV-P2-2 Information access (cold review): session-resume never said where the agent gets its own session id on the by-hand path, and the newest transcript for this cwd is wrong when another session writes. Claude Code substitutes `${CLAUDE_SESSION_ID}` in skill text since 2.1.9 (`offline/research/R22-cc-2.1.300/raw/CHANGELOG-v2.1.300.md:7677`) and sets `CLAUDE_CODE_SESSION_ID` in Bash since 2.1.132 (`:5560`; `raw/docs/env-vars.md:378`: matches the hook `session_id`, updated on `/clear`). (Reviewer; the 2.1.300 intake.) | Applied in this lane: step 4 sets `SID=${CLAUDE_SESSION_ID}` and names `$CLAUDE_CODE_SESSION_ID` as the same value in Bash; step 6 passes `--session-id ${CLAUDE_SESSION_ID}` on every path and says an unsubstituted literal fails `owner`'s UUID check (rc 1, visible) rather than guessing; resume evals 1-3 updated. Verification: `grep -c 'CLAUDE_SESSION_ID' .claude/skills/session-resume/SKILL.md` prints 3; mirror diff rc 0. |
| P2 | HS-1 Steering (writer): `write` fell back to the placeholder `next-session` for a name-free owner sentence. (`dev/handoff.py:699` at `0e4f6e7`.) | Closed upstream: handoff-script `7d93c62` makes `owner_name` fall back to `next_name()` (`dev/handoff.py:706`), merged here in `696d338`. Verification: the dry-run NEXT bullet reads `ccm-20261014T195015.947578000-05` and no added line holds `next-session`; the template header now states that behaviour (RV-P3-2 row). |
| P2 | HS-2 Automated checks (writer): `write` refused at 17 and 18 required lines (budget 16). | Applied (`c037168`): two-line `action`, one-sentence `owner`, history rule in the first `notes` bullet. Verification on the final bytes: block 15 lines, NEXT 8, widths at most 100. Remaining: parent edit 5 when R-176 closes. |
| P3 | RV-P3-1 Information access (cold review) and HS-3 (writer): step 4 paraphrased the startup-log checks instead of quoting them, and ct35a had not yet documented them. ct35a tip `02c497c` now documents the log path and four numbered checks under "Detect a failure after a restart". | Applied in this lane: step 4 quotes the four names word for word ("1. Did not fire", "2. Reload missing or not accepted", "3. Reload finished after the first prompt reached the transcript", "4. No title, or an error") and leaves the commands to that skill. HS-3 and parent edit 1 closed. Verification: the `git show ... | grep -c` above prints 4; `grep -c 'Detect a failure after a restart' .claude/skills/session-resume/SKILL.md` prints 1. Admission at ct35a integration: the same grep on `.claude/skills/session-start/SKILL.md` in the root checkout prints 4. |
| P3 | RV-P3-2 Coding standards (cold review): the `action` sentence existed in three shapes: the template header (`handoff-template.md:8`, "First <R-n>, the release intake (<report path>)"), the section (`:20`, "First R-176 release intake (...)") and the draft's parent edit 5. | Applied: the header shape is "First <R-n> release intake (<report paths>). Then <work>.", the section matches it, and parent edit 5 quotes the section verbatim. Verification: `grep -n 'First <R-n>\|First R-176' .claude/skills/session-handoff/references/handoff-template.md` prints lines 8 and 21 in that shape. |
| P3 | RV-P3-3 Steering (cold review): step 1 said background tasks count as running work without saying how to list them. `/tasks` is a user-typed view (`raw/docs/sub-agents.md:382`, changelog `:1291` folds system tasks under one row). | Applied: step 1 lists them from the session's own record (each `run_in_background` Bash and Monitor call returned a task id; the harness sends one completion notice per id; an id without its notice is running) and names `/tasks` as the cross-check only the user can open. Verification: `grep -c 'completion notice' .claude/skills/session-handoff/SKILL.md` prints 1. |
| P3 | RT-1 Automated checks (retro writer): `dev/test_handoff.py:526` `test_skill_report_types_resume_only_after_clear` pins step 5's phrase "never after the start command", but the lane wrote "never after the whole start command"; the lane's `required_checks` omit `./dev/mise run test:handoff`, and `check` does not run it (`check:research` does, in CI on push), so the mismatch reached the cold review unseen. An existing check not wired in. | Applied in this lane: the phrase matches the test. The wiring is outside `owned_paths`: parent edits 2 and 7. Verification: `./dev/mise run test:handoff` rc 0 (61 tests). |
| P3 | HS-4 Information access (writer): `predicate.md` said "three pwf fires". | Applied (`535d61d`): four fires. Verification: `grep -c 'four pwf fires' .claude/skills/session-handoff/references/predicate.md` prints 1. |
| P3 | HS-5 Navigation (writer): `predicate.md` (`H.doctor-findings`) and `dev/handoff.py` §7 still carry the w0-doctor fallback S6 retires from the skills. | Kept in `predicate.md` because it describes the code. Deferred, owner parent, with a fix lane on `dev/`: drop the fallback from `dev/handoff.py`, then from `predicate.md`. Admission condition: `grep -rn 'w0-doctor' .claude/skills/session-handoff` matches nothing. |
| P3 | HS-6 Automated checks (writer): the CLI row is hand-written, so session-resume's comparison rests on a typed sentence. | Deferred, owner parent: a ticket for `dev/handoff.py state` to read `claude --version` and `write` to generate the row. Admission condition: the row appears in `write --dry-run` output without a template line. |
| P3 | RT-2 Tool economy (retro writer): the first search of the offline 2.1.300 tree used `grep -rn` and returned 225 KB, then two `grep -o` patterns were refused by the host's ugrep ("exceeds complexity limits"); a `python3 -I` filter printing matching lines answered in one call. | No edit: the offline tree is ignored local data and the alias is a host setting, not a repository fact; recorded for the memory note. |
| P3 | HS-7 Information access (writer): audit findings S1, S2, S7, S10, S11, S13 are not in this lane's contract. | Rejected for this lane (outside `owned_paths`): S1 and S2 are parent record work, S7 and S10 landed with handoff-script, S11 belongs to ct35b, S13 to the memory note. |

Navigation: RT-1 is the finding: nothing tells an agent editing `session-handoff` or
`session-resume` that `dev/test_handoff.py` pins their prose, so parent edit 7 adds one line to
`.claude/AGENTS.md`. HS-5 stays deferred. Every cited path resolves in the worktree except two
that are local data (`offline/research/R22-cc-2.1.300/`, ignored; `.claude/skills/session-start/`,
on the ct35a branch); the first exists in the root checkout, the second lands with ct35a.

Automated checks: RV-P1 applied by the merge; RT-1 applied in-lane with its wiring in parent edits
2 and 7; HS-2 verified on the final bytes; HS-6 deferred. `check` ran once per tree state and
passed each time; `test:handoff` is the one check that caught a regression this pass.

Coding standards: RV-P3-2 applied. Steps end on a done-when condition (rule 9) and state the
behaviour to perform (rule 8): "print the §8 block" replaces "run `start-command`", the one
prohibition kept (`never --force`) sits beside its positive target, and the `.agents` copies are
byte-identical (rc 0).

Steering and global guidance: no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or `.claude/agents`
file changed in this lane. RV-P2-1, RV-P2-2 and RV-P3-3 are the steering fixes, all inside the two
skills; HS-1 closed upstream.

Tool economy: RT-2. Otherwise one scripted pass per file with exact-match assertions, the mirror
copy and its diff as one step, each gate run once per tree state, and the dry-run output parsed
from one saved file instead of rerun.

No-ops: none open. The template header sentence that restated a bug (`write` reads the first
backticked span) now states the shipped behaviour (`next-name` for a name-free owner, a
backticked span wins), which an agent cannot read from the template alone. The "whole" in step 5
changed nothing an agent did and was the word the test rejected (RT-1).

Information access: this pass read the merged `dev/handoff.py` and `dev/test_handoff.py`, the
ct35a skill through `git show` at `02c497c` (read-only), the 2.1.300 changelog and `env-vars.md`
lines cited above, and the handoff-script retro. Nothing read a provider, the network or a
secret; no environment listing is printed; the dry-run output was saved to the session
scratchpad and parsed there.

## Parent edits (outside `owned_paths`; literal)

1. Closed (HS-3, RV-P3-1): ct35a `02c497c` documents the path and the four checks and step 4
   quotes them. Nothing to apply.
2. `lanes/handoff-skills.json`: set `status`, `review` and `retro` at integration. Add to `notes`:
   "session-handoff prints HANDOFF §8 as the only start command (`write` names and ids it; never a
   second `start-command`), and session-resume passes `--session-id ${CLAUDE_SESSION_ID}` on every
   path." Add to `required_checks`: `"./dev/mise run test:handoff"` (RT-1).
3. Before the real `/session-handoff`: the block fits (15 of 16 lines); write the real action and
   CLI row, then `python3 -I dev/handoff.py write --dry-run --agents-done` in the root checkout must
   report at most 16 lines and a NEXT of at most 12. Root `check` clears the worktree-only findings.
4. `dev/handoff.py` (fix lane; S3): in `section_start` replace the "Two ways to start the next
   session; use one, never both:" list with
   ```text
   Three ways to start the next session; use one, never two:
   - Same terminal and version: type `/clear`, then `/session-resume <name>` as the first turn.
   - New version or new terminal: `/quit` (ignore the `claude --resume` line it prints), then paste
     the block above; its prompt already runs session-resume, so type nothing else.
   - New version, typed by hand: paste the block without its prompt, then type `/reload-skills`,
     `/reload-plugins` (never `--force`) and `/session-resume <name>`.
   ```
   with `<name>` the one after `claude -n` in the block. Update
   `test_section_start_types_resume_only_after_clear` (`never both` becomes `never two`). Until
   then the skill prints only the `sh` block of §8, so the two-way prose never reaches the user.
5. When R-176 is ticked, delete the first line of the template's `## action`, which reads
   ``First R-176 release intake (`reviews/ccm-20261014/cc-2.1.300/`, `offline/research/R22-cc-2.1.300/`).``
   in both copies, and set the CLI row to "<version> installed; the handing-off session ran
   <version>".
6. `dev/handoff.py:12`, the module docstring line
   `  start-command [--name N] [--session-id]  the \`claude -n <name> "<prompt>"\` line with the pins exported`
   becomes
   `  start-command [--name N] [--session-id]  the \`claude -n <name> "<prompt>"\` line with the pins exported (write puts it in HANDOFF §8; by hand, pass §8's name and id)`
   (RV-P2-1). Verification: `python3 -I dev/handoff.py --help | grep -c 'HANDOFF §8'` prints 1.
7. `.claude/AGENTS.md`, in the `skills/` bullet after "change both copies together.", add:
   "`dev/test_handoff.py` pins `session-handoff` and `session-resume` prose and their mirrors; run
   `./dev/mise run test:handoff` after editing either." (RT-1). Verification: `grep -c
   'test:handoff' .claude/AGENTS.md` prints 1.

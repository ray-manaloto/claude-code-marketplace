# handoff-script retrospective: next-name, fresh start-command, startup probe, /quit context line (R-175)

Unit `handoff-script` (skills audit S4, S7, S9, S10; R-175; D61, D76, D113, D186, D187). Worktree
`.claude/worktrees/handoff-script`, branch `claude/handoff-script`, `base_sha` `32e742c`, cut from
the allocation commit `20c0ef0`, so `git log 20c0ef0..HEAD` is the lane. Commits, in order:
`40d2398` (the change and its tests), `3cf8b47` (merge of the integration tip `e81645b`, clean,
trailers carried, no lane branch name), `187eb32` (implementer retro draft), `0e4f6e7` (merge of
the integration tip `1fb23d1`, clean), `dc34dbb` (the two cold-review P3s), `375117a` (merge of the
integration tip `65541f4`, `--no-ff`, message file with the trailers), `7d93c62` (HS-3), then the
commit carrying this record (the final SHA, in the hand-back). Implementer: Claude Opus 5.5 (the
record's `writer_model`). Cold review: Fable, high, read-only, on `0e4f6e7`: PASS with two P3s, no
P1 or P2. Retro writer: Fable, high; this is the retro-writer pass over the implementer's draft.

Delivered, test-first at the CLI seam (`python3 -I dev/handoff.py ...` as a child process in the
fixture's scrubbed environment, plus the doctor `context_lines` contract):
- `next-name` (`dev/handoff.py:152`) prints `ccm-` + one OS `date NAME_DATE_FORMAT` call, with
  `%z` cut to its hour. `NAME_DATE_FORMAT = "+%Y%m%dT%H%M%S.%N%z"` (`dev/handoff.py:61`) is the one
  named constant the session-start mod (lane ct35a) passes to `date` too (D187). No Python time
  formatting. A `date` that exits nonzero, hangs (`DATE_TIMEOUT_S`, 10 s) or prints another shape
  refuses with rc 2 and one reason on stderr (the exit code and the first 80 characters of stderr,
  the timeout, or the stamp). `date_binary()` follows `git_binary()`: PATH unless it is a mise
  shim, else `/bin/date`.
- `start-command` without `--name` uses `next-name`, never the owner's name (S4). It always passes
  `--session-id` (the given one, else a fresh `uuid4`) and its prompt hands that id to
  `dev/handoff.py owner --session <name> --session-id <id>` (S7). `--session-id` on both parsers
  is `type=session_uuid` (`uuid.UUID`, canonical form; a usage error exits 1), as
  `claude --session-id <uuid>` requires on 2.1.300.
- `write` with a template whose owner sentence has no backticked span names the next session with
  `next_name()` (`owner_name`, `dev/handoff.py:706`), so the `## Next Step` block, the NEXT bullet
  and HANDOFF §8 name one session and §8 carries its `--session-id`; a backticked name still wins
  (HS-3; lane handoff-skills' name-free template). The 16-line block budget is unchanged.
- The injection probe adds a fourth fire, `startup` (SessionStart `source: "startup"`,
  `dev/handoff.py:494`, `:513`), held to the legacy criteria (S9). §7's manual twin lists it.
- `context_lines` (`dev/handoff.py:983`) reads `resume: /quit, then the §8 start command (it runs
  session-resume); or /session-resume <name> after /clear` (S10).

Size: 2 maintained files. `git diff --numstat 20c0ef0 7d93c62 -- dev/`: `dev/handoff.py` +75/-19,
`dev/test_handoff.py` +199/-3.

Exits, from the worktree, `VIRTUAL_ENV` unset, one literal command each:
- Implementer, on `3cf8b47`: red `./dev/mise run test:handoff` with `dev/handoff.py` at `20c0ef0`
  and the new tests in place: rc 1, 56 tests, `FAILED (failures=9)` (log sha256 prefix
  `81975ce8e10383e8`); green: rc 0, 56 tests OK (47 at `20c0ef0`; log `44ac2f2476cbfd03`).
  `./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0; `check:acceptance-baseline`
  rc 0; `git diff --check e81645b HEAD` rc 0; hk `pre-commit` (`check:records`) passed.
- Retro pass, cold-review P3s, on `0e4f6e7` + tests: red rc 1, 59 tests, `FAILED (failures=5,
  errors=1)`, all in the four new tests; green on `dc34dbb`: rc 0, 59 tests OK.
- Retro pass, HS-3, on `375117a` + tests: red rc 1, 61 tests, `FAILED (failures=1)` (the control
  with a backticked name passed; the name-free case showed `next-session` in the NEXT bullet and
  §8); green on `7d93c62`: rc 0, 61 tests OK (log `8e64232ceeed4e31`).
- Gates on `375117a` (merged bytes of `65541f4`): `./dev/mise run test:handoff` rc 0 (59 tests, log
  `d5bf04a342d12b60`); `./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0
  (`"status": "pass"`); `./dev/mise run check:acceptance-baseline` rc 0 (19 baseline files);
  `git diff --check 20c0ef0` rc 0 (rc 2 on `0e4f6e7`, from the integration branch's
  `reviews/ccm-20261014/cc-2.1.300/impact.md:98` only, fixed upstream in `65541f4` and merged);
  `python3 -I dev/handoff.py next-name` rc 0, `ccm-20261014T191822.511734000-05`.
- The same gates and `./dev/mise run retro:gate -- handoff-script` rerun on the final SHA: rcs in
  the hand-back.
- Live probe (implementer): `python3 -I dev/handoff.py check --json --agents-done` against
  planning-with-files 3.24.0 in this worktree exits 2 only on worktree-local findings
  (`H.handoff-stale-sha`, `H.head-not-remote`, `H.receipt-missing`, root-plan request findings) and
  no `H.injection-probe-failed`, so the real `startup` fire emits the plan frame.

Cross-lane verification of the shared format (HS-1), read from lane ct35a's worktree, rc 0:
`hooks/register.ts:8` `DATE_ARGV = ['date', '+%Y%m%dT%H%M%S.%N%z']`, `:59` `.slice(0, -2)`,
`SKILL.md:17`, `tests/session-start.test.ts:46` the same literal.

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P2 | HS-1 Coding standards: D187 asks for one format string shared by the mod and `dev/handoff.py`, but a TypeScript mod cannot import a Python constant, so the string exists twice and the hour cut (`-0500` to `-05`) is a second rule both apply. DL-62 said UTC; DL-103 (local time, hour offset) supersedes it. (Implementer; `decisions.jsonl` DL-62, DL-103, DL-240.) | `NAME_DATE_FORMAT` at `dev/handoff.py:61` with a comment naming the mod; the test pins argv `+%Y%m%dT%H%M%S.%N%z` and the `-05` output. Lane ct35a uses the same literal and `slice(0, -2)` (the grep above). | Applied in both lanes; verified by `grep -rF '%Y%m%dT%H%M%S.%N%z'` over `dev/handoff.py` and ct35a's `.claude/skills/session-start/` (rc 0, four hits). |
| P2 | HS-2 Steering: four skill lines steered agents against this change: `session-handoff/SKILL.md` printed `start-command --name <owner>` (S4 by hand), `references/probe-commands.md` probed only `source:"clear"`, `references/handoff-template.md` held a stale literal name that `write` copied into the block and §8, and `session-resume/SKILL.md` treated `--session-id` as optional. (Implementer; skills audit S4, S7, S9.) | Outside `owned_paths` (`.claude/skills/`, `.agents/`). Lane handoff-skills carries all four edits at `521b3e7`..`b087860`: `SKILL.md:51` prints the bare `start-command` and says it generates a fresh D61 name; `probe-commands.md:18`, `:32` add the `startup` fire; the template owner sentence is name-free; `session-resume/SKILL.md:44` says the start command fixes the id. Both mirrors hold the same file list and `SKILL.md` bytes. | Deferred to lane handoff-skills, whose record and gates own it; verified there by `git grep` (rc 0). Admission for integration: `SkillFilesTests` rc 0 and `grep -c 'start-command --name <owner>' .claude/skills/session-handoff/SKILL.md` prints 0. |
| P3 | RV-1 Automated checks (cold review P3): `next_name()` ignored `date`'s exit status and stderr. A `date` that exited 1 but printed a stamp returned rc 0; one that exited 1 with no output refused with the misleading reason "a date without %N?"; a hung `date` surfaced as `TimeoutExpired`, exit 1 instead of 2. (Reviewer, `dev/handoff.py:152-155` on `0e4f6e7`.) | `dc34dbb`: a nonzero exit raises `Refusal` naming the code and the first 80 characters of stderr; `TimeoutExpired` becomes `Refusal` ("date did not answer within N s", `DATE_TIMEOUT_S`). Tests: `test_a_date_that_exits_nonzero_is_refused_naming_its_exit_and_stderr` (two subtests: a stamp with stderr, nothing at all; both rc 2, no `%N?`), `test_a_hung_date_is_refused_not_an_error` (in-process, `DATE_TIMEOUT_S` patched to 0.2 s, a `date` that sleeps 5 s; rc 2). | Applied; `./dev/mise run test:handoff` rc 0. |
| P3 | RV-2 Automated checks (cold review P3): `--session-id` was unvalidated, so `abc` was accepted and `owner` wrote it into `task_plan.md`; `claude --help` on 2.1.300 says `--session-id <uuid>` must be a valid UUID. (Reviewer, `dev/handoff.py:1015,1019` on `0e4f6e7`.) | `dc34dbb`: `session_uuid` (`uuid.UUID`, canonical string) is the argparse `type=` on both parsers; the subclassed `Parser.error` exits 1. `test_a_session_id_that_is_not_a_uuid_is_a_usage_error` (both commands, rc 1, `--session-id: not a UUID: 'abc'`, `task_plan.md` untouched); the accepted-id assertion now passes a UUID. | Applied; `./dev/mise run test:handoff` rc 0. |
| P3 | HS-3 Automated checks: `write` took the next session's name from the first backticked span of the template's owner sentence and fell back to the placeholder `next-session`; lane handoff-skills' name-free template therefore put `next-session` into the block, the NEXT bullet and §8. (Implementer; parent course correction during this retro.) | `7d93c62`: `owner_name` falls back to `next_name()`, the generator `start-command` uses, so the three places name one session and §8 carries `--session-id`; `--name` and a backticked name still win. Tests (`WriteNameFreeTests`, child-process `write --dry-run` with a fake `date` and a fake plugin root): the skills lane's owner sentence verbatim over the scratch fixture gives the fake stamp in all three places and no `next-session` in the added lines; the backticked control keeps its name and never calls `date`. | Applied; `./dev/mise run test:handoff` rc 0 (61 tests). |
| P3 | HS-4 Coding standards: cutting `%z` to the hour drops the minutes of offsets such as `+0530`. (Implementer.) | None: D61 and DL-103 fix the format as an hour offset and this host runs at `-05`; a minute-bearing zone needs a new decision. | Rejected (D61). |
| P3 | HS-5 Automated checks: on this host `date` on PATH is a mise shim (`~/.local/share/mise/shims/date`), about 186 ms per call (dev/AGENTS.md). (Implementer, `which -a date`.) | `date_binary()` skips a mise shim the way `git_binary()` does; a fake `date` first on PATH is still used, which is how the tests inject it. `test_next_name_from_the_host_date_has_the_d61_shape` runs the real host `date`. | Applied; rc 0. |
| P3 | HS-6 Information access: run from a lane worktree, `check` resolves `.claude/worktrees/<unit>` against the lane root and reports every lane worktree as missing (`H.receipt-missing`) and the branch as unpublished, before and after this change. (Implementer.) | None: `check` is a root-checkout tool; the lane's evidence uses only the absence of `H.injection-probe-failed`. | Rejected (known; the root run is authoritative). |
| P3 | RT-1 Automated checks: `git diff --cached --check` runs inside `dev/check.py` (`check.py:73`), but the hk `pre-commit` hook runs only `check:records` (`hk.pkl:13`), so a trailing blank line in `impact.md:98` reached the integration branch (`e81645b`) and surfaced only as this lane's `git diff --check 20c0ef0` rc 2, fixed upstream in `65541f4`. An existing check not wired in. (Retro writer.) | `hk.pkl` is outside `owned_paths`: parent edit 2 adds a `whitespace` step to `pre-commit`. Verification: stage a file with a trailing blank line, `git diff --cached --check` rc 2 and hk refuses the commit; `./dev/mise tasks validate` rc 0. | Deferred to the parent for immediate application (owner: parent; literal edit below). |
| P3 | RT-2 No-ops: `40d2398` added `subprocess.TimeoutExpired` to `main`'s exit-1 handler without a test; every other `subprocess.run` in the module catches it locally (`dev/handoff.py:162`, `:387`, `:497`), so the branch served only the hung-`date` case, and wrongly (exit 1). (Retro writer.) | Removed in `dc34dbb`; the hung-date test binds the exit-2 path instead. | Applied; `./dev/mise run test:handoff` rc 0. |
| P3 | RT-3 Coding standards (judgement): the reviewed bug is a pattern, "read a child's stdout before its exit status", that no written standard names, so the reviewer caught it by eye. (Retro writer, RV-1.) | `CODING_STANDARDS.md` is outside `owned_paths`: parent edit 3 adds rule 17 under `## Tests`. Verification: the rule text present; the reviewer role reads `CODING_STANDARDS.md` already. | Deferred to the parent for immediate application (owner: parent; literal edit below). |

Navigation: no finding. The audit's pointers (`dev/handoff.py:467`, `:818`, `:903-906`, `:951`)
matched `20c0ef0`; the parent's HS-3 pointer (`git -C .claude/worktrees/handoff-skills show
HEAD:.claude/skills/session-handoff/references/handoff-template.md`) resolved first try. The
module docstring lists `next-name` and `write --name`'s help names its new default, so `--help`
stays the source of truth and no `AGENTS.md` line is added.

Automated checks: RV-1, RV-2, HS-3, HS-5 applied; RT-1 deferred to the parent. `test:handoff` is
wired through `check:research` (`mise.dev.toml:118`), which the research-fast workflow runs on
push to the integration branch and on pull requests; `check` itself does not run it, which is the
second route `.claude/rules/dev-tests.md` allows, so no new wiring.

Coding standards: HS-1 applied and cross-checked; HS-4 rejected; RT-3 deferred to the parent.

Steering and global guidance: no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or `.claude/agents`
file changed in this lane. HS-2's skill lines live in lane handoff-skills.

Tool economy: the retro gathered its inputs in five batched reads (role, record, draft, diff, check
wiring) and ran each gate once per tree state, sequentially from this worktree. The hung-date test
patches `DATE_TIMEOUT_S` to 0.2 s in-process instead of waiting 10 s; the five new child-process
tests cost about 2 s (24 s to 26 s). `fake_date` grew `rc`, `stderr` and `sleep` parameters
instead of a second helper, and the name-free fixture reuses the scratch `TEMPLATE` and the
existing `fake_plugin`, so no fixture file was added and nothing left `owned_paths`. Two wasted
runs (about a minute): the first HS-3 red refused on the real injection probe (no plugin cache in
the scrubbed HOME), then on the real template's SHAs and paths, which the scratch repo lacks; the
test's comment now says a child-process `write` needs `fake_plugin` and a scratch-resolvable
template. The implementer's red reused the new tests against `git show 20c0ef0:dev/handoff.py`
instead of a stash. `git merge -F -` exits 129 under hk, so both merge messages came from files.

No-ops: RT-2 applied. Every behaviour change has a test that failed first (9, then 5 plus 1
error, then 1). Two wording changes have no test of their own: §7's manual-twin probe list
(prose) and §8's `--session-id` sentence (line width covered by
`test_section_start_types_resume_only_after_clear`).

Information access: the tests build a scratch HOME, Git config, plugin root and `date` on PATH;
nothing reads `~/.claude/projects`, a provider or the network, and no secret or environment
listing is printed. The refusal quotes at most 80 characters of `date`'s own stderr. The retro
read lane handoff-skills and ct35a through `git show` and `git grep` of their worktree HEADs,
read-only. HS-6 is the one known gap and is rejected above.

## Parent edits (outside `owned_paths`; literal)

1. `lanes/handoff-script.json`: set `status`, `review` and `retro` at integration (the parent's
   fields), and append to `notes`: "`NAME_DATE_FORMAT` (`dev/handoff.py:61`) is the format string
   shared with ct35a (`hooks/register.ts:8` `DATE_ARGV`, D187); `write` names a name-free template's
   next session with `next_name()` (HS-3, `7d93c62`)."
2. `hk.pkl`, inside `["pre-commit"] { ... steps { ... } }`, after the line
   `            ["records"] { check = "./dev/mise run check:records" }` add the line
   `            ["whitespace"] { check = "git diff --cached --check" }`
   (RT-1). Verification: stage a file ending in a blank line; `git commit` is refused; unstage it and
   `./dev/mise tasks validate` rc 0.
3. `CODING_STANDARDS.md`, under `## Tests`, after rule 16, add:
   `17. A helper that runs a child process checks its exit status before reading its output and`
   `    refuses with the code and the first line of stderr; a nonzero exit with output, one without,`
   `    and a hang each have a seam test (handoff-script RV-1).`
   Verification: `grep -c 'checks its exit status before reading its output' CODING_STANDARDS.md`
   prints 1.
4. Lane handoff-skills' record: HS-2's four skill edits are its deliverable; its admission condition
   is in the HS-2 row (`SkillFilesTests` rc 0; the `--name <owner>` grep prints 0).

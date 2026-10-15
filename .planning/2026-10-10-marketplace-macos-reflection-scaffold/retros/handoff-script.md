# handoff-script retrospective: next-name, fresh start-command, startup probe, /quit context line (R-175)

Unit `handoff-script` (skills audit S4, S7, S9, S10; R-175; D61, D76, D113, D186, D187). Worktree
`.claude/worktrees/handoff-script`, branch `claude/handoff-script`, `base_sha` `32e742c`, cut from
the allocation commit `20c0ef0`, so `git log 20c0ef0..HEAD` is the lane. Commits, in order:
`40d2398` (the change and its tests), `3cf8b47` (merge of the integration tip `e81645b`, clean,
message amended to carry the trailers and no lane branch name), then the commit carrying this
record (the final SHA, in the hand-back). Implementer: Claude Opus 5.5, matching the record's
`writer_model`. This is the implementer's draft: the independent cold review and the retro-writer
pass have not run yet, so "reviewed" is open.

Delivered, test-first at the CLI seam (`python3 -I dev/handoff.py ...` as a child process in the
fixture's scrubbed environment, plus the doctor `context_lines` contract):
- `next-name` (`dev/handoff.py:151`) prints `ccm-` + one OS `date NAME_DATE_FORMAT` call, with
  `%z` cut to its hour. `NAME_DATE_FORMAT = "+%Y%m%dT%H%M%S.%N%z"` (`dev/handoff.py:61`) is the one
  named constant the session-start mod (lane ct35a) must pass to `date` too (D187). No Python time
  formatting is added. If `date` prints something else (for example a `date` without `%N`), the
  command refuses with rc 2 and one reason on stderr. `date_binary()` follows `git_binary()`'s
  rule: PATH unless it is a mise shim, else `/bin/date`.
- `start-command` without `--name` uses `next-name` and never the owner's name (S4). It always
  passes `--session-id` (the given one, else a fresh `uuid4`), and its prompt hands that id to
  `dev/handoff.py owner --session <name> --session-id <id>` (S7; `owner` already accepted
  `--session-id`, and without it falls back to the newest transcript, `dev/handoff.py:935-938`).
  HANDOFF §8's "Optional: `--session-id`" sentence now says the block fixes the id.
- The injection probe adds a fourth fire, `startup` (SessionStart `source: "startup"`,
  `dev/handoff.py:494`, `:513`), held to the legacy criteria (inside plan line 30, NEXT last)
  (S9). §7's manual twin lists it.
- `context_lines` (`dev/handoff.py:983`) reads `resume: /quit, then the §8 start command (it runs
  session-resume); or /session-resume <name> after /clear` (S10).

Size: 2 maintained files. `git diff --numstat 20c0ef0 40d2398`: `dev/handoff.py` +55/-16,
`dev/test_handoff.py` +126/-3 (181 added lines).

Exits on `3cf8b47` (merged bytes), from the worktree, `VIRTUAL_ENV` unset, one command each:
- Red: `./dev/mise run test:handoff` with `dev/handoff.py` restored to `20c0ef0` and the new tests
  in place: rc 1, 56 tests, `FAILED (failures=9)` (all 9 new or changed tests; log sha256 prefix
  `81975ce8e10383e8`). Each slice also failed first on its own.
- Green: `./dev/mise run test:handoff`: rc 0, 56 tests OK (47 at `20c0ef0`; log sha256 prefix
  `44ac2f2476cbfd03`). The same rc 0 on `40d2398` before the merge.
- `./dev/mise tasks validate`: rc 0. `./dev/mise run check`: rc 0 (`"status": "pass"`).
  `./dev/mise run check:acceptance-baseline`: rc 0. `git diff --check e81645b HEAD`: rc 0. hk
  `pre-commit` (`check:records`) passed on both commits.
- `./dev/mise run retro:gate -- handoff-script`: run on this record; the rc is in the hand-back.
- Live probe: `python3 -I dev/handoff.py check --json --agents-done` against planning-with-files
  3.24.0 exits rc 2 in this worktree only on worktree-local findings (`H.handoff-stale-sha`,
  `H.head-not-remote`, `H.receipt-missing` for lane worktrees, the request findings of the root
  plan). It reports no `H.injection-probe-failed`, so the real `startup` fire emits the plan
  frame (S9's "probably fine but untested" is now tested).

Real output, run from the worktree on `40d2398`:

```text
$ python3 -I dev/handoff.py next-name        # rc 0
ccm-20261014T185859.279172000-05
$ python3 -I dev/handoff.py start-command    # rc 0
cd /Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.claude/worktrees/handoff-script
unset VIRTUAL_ENV
export PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.claude/worktrees/handoff-script
claude -n ccm-20261014T185859.335329000-05 --session-id 7bd15a3a-1b6a-4231-a6eb-f15ea0423cbc "Use the session-resume skill for session ccm-20261014T185859.335329000-05: it follows .planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md section 2, runs the doctor session-start surface and dev/handoff.py check, dispatches the extractor and rewrites the owner line with dev/handoff.py owner --session ccm-20261014T185859.335329000-05 --session-id 7bd15a3a-1b6a-4231-a6eb-f15ea0423cbc. Then continue at the Next Step of the plan."
```

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P2 | HS-1 Coding standards: D187 asks for one format string shared by the mod and `dev/handoff.py`, but a TypeScript mod cannot import a Python constant. The string therefore exists twice, and the cut to an hour offset (`-0500` to `-05`) is a second rule both copies must apply. DL-62 still says UTC; DL-103 (local time, hour offset) supersedes it. (Implementer; `decisions.jsonl` DL-62, DL-103, DL-240.) | In this lane: `NAME_DATE_FORMAT` at `dev/handoff.py:61`, with a comment that names the mod. The test pins the literal argv `+%Y%m%dT%H%M%S.%N%z` and the `-05` output. Across lanes: parent edit 1 tells lane ct35a to use the same literal and the same cut. | Applied in-lane; the cross-lane check is deferred to the parent. Admission condition: `grep -rF '%Y%m%dT%H%M%S.%N%z' dev/handoff.py .claude/skills/session-start/` matches in both, and a mod-made title matches `ccm-\d{8}T\d{6}\.\d{9}[+-]\d{2}`. |
| P2 | HS-2 Steering: three skill lines still steer agents against this change. `session-handoff/SKILL.md:47` prints `start-command --name <owner>`, which is S4's bug done by hand. `session-handoff/references/probe-commands.md:12` and `:29-30` probe and judge only `source:"clear"`. `session-handoff/references/handoff-template.md:19` holds the stale name `ccm-20261014T034212.915972000-05`, which `write` copies into the block and §8. `session-resume/SKILL.md:35` treats `--session-id` as optional. (Implementer; skills audit S4, S7, S9.) | These are skills files outside `owned_paths` (`.claude/skills/`, `.agents/`). Parent edits 2-5 give the exact text for the skills lane (handoff-skills), with both mirrors changed together. | Deferred to the parent and the handoff-skills lane. Admission condition: `SkillFilesTests` rc 0 and `grep -c 'start-command --name <owner>' .claude/skills/session-handoff/SKILL.md` prints 0. |
| P3 | HS-3 Automated checks: `write` still takes the next session's name from the template's `## owner` sentence (`owner_name`), not from `next-name`. Changing the default only in code would print two different names, because the template sentence is copied verbatim into the block's agents line. (Implementer.) | No code change in this lane. The order: parent edit 4 makes the template name-free, then a fix lane changes `write`'s `--name` default to `next_name()`. | Deferred to the parent. Admission condition: the template edit lands, and `write --dry-run` prints a block whose `Owner: start as` name equals §8's `claude -n` name. |
| P3 | HS-4 Coding standards: cutting `%z` to the hour drops the minutes of offsets such as `+0530` or `+0545`. (Implementer.) | No change: D61 and DL-103 fix the format as an hour offset, and this host runs at `-05`. Rejected with that evidence. A minute-bearing zone would need a new decision. | Rejected (per D61). |
| P3 | HS-5 Automated checks: on this host `date` on PATH is a mise shim (`~/.local/share/mise/shims/date` resolves to the `mise` binary). Calling it would cost the shim start-up on every name. (Implementer, `which -a date`.) | `date_binary()` skips a mise shim the way `git_binary()` does (dev/AGENTS.md: shim cost). A fake `date` placed first on PATH is still used, which is how the tests inject it. `test_next_name_from_the_host_date_has_the_d61_shape` runs the real host `date`, rc 0. | Applied. |
| P3 | HS-6 Information access: run from a lane worktree, `check` resolves `.claude/worktrees/<unit>` against the lane root, so it reports every allocated lane worktree as missing (`H.receipt-missing`) and the lane branch as unpublished. This happens before and after this change. (Implementer; the same receipt as request-catch's.) | No change: `check` is a root-checkout tool, and the lane's evidence uses only the absence of `H.injection-probe-failed`. | Rejected (already known; the root run is authoritative). |

Navigation: no finding. The audit's pointers (`dev/handoff.py:467`, `:818`, `:903-906`, `:951`)
matched `20c0ef0` exactly. S4's suggested Python one-liner is superseded by D187 (OS `date`), and
the lane record says so.

Tool economy: no finding. The red receipt reused the new tests against `git show 20c0ef0:dev/handoff.py`
in place of a stash, so the untracked state stayed simple, and the fake plugin and fake `date` are
built in code beside their tests.

No-ops: none. Every behaviour change has a test that failed first (9 failures in the red run).
Two wording changes have no test of their own. One is §7's manual-twin probe list, which is
prose. The other is §8's `--session-id` sentence, which `test_section_start_types_resume_only_after_clear`
covers for line width.

Steering and global guidance: no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or `.claude/agents`
file changed. The skill wording that now disagrees with the script is HS-2 (parent edits 2-5).

Information access: the tests build a scratch HOME, Git config, plugin root and `date` on PATH.
Nothing reads `~/.claude/projects`, a provider or the network, and no secret or environment
listing is printed.

## Parent edits (outside `owned_paths`; literal)

1. Lane ct35a-session-start-mod brief (or its lane record `notes`): add "The session title runs
   `date '+%Y%m%dT%H%M%S.%N%z'` once and drops the last two characters of the output (the offset's
   minutes), then prefixes `ccm-`, exactly as `dev/handoff.py` `NAME_DATE_FORMAT`/`next_name()` do
   (handoff-script HS-1)." Verification: the grep in HS-1 matches both files.
2. `.claude/skills/session-handoff/SKILL.md` line 47 (and the `.agents` mirror): replace
   `` `python3 -I dev/handoff.py start-command --name <owner>` `` with
   `` `python3 -I dev/handoff.py start-command` `` and, after "verbatim.", add "It generates a fresh
   D61 name with `next-name` and fixes `--session-id`; never pass the current owner's name."
3. `.claude/skills/session-handoff/references/probe-commands.md` (and the mirror): after line 15
   add the paragraph "Restart fire (what the next session receives after `/quit` and the start
   command): the same command with `\"source\":\"startup\"` in place of `\"source\":\"clear\"`." and
   in lines 29-30 replace `(legacy,\npretool)` with `(legacy, startup,\npretool)`.
4. `.claude/skills/session-handoff/references/handoff-template.md` line 19 (and the mirror):
   replace `` Owner: start as `ccm-20261014T034212.915972000-05` (D61 format, D76; HANDOFF §8); ``
   with `` Owner: start with the HANDOFF §8 command (a fresh `next-name`, D61, D76); ``.
5. `.claude/skills/session-resume/SKILL.md` line 35 (and the mirror): replace
   "(add `--session-id <uuid>` when you know it; otherwise it uses the newest transcript id)." with
   "with the `--session-id <uuid>` the start command fixed (its prompt names it); without it
   `owner` guesses the newest transcript, which is wrong when another session is writing."
6. `lanes/handoff-script.json`: set `status`, `review` and `retro` at integration, and add to
   `notes`: "`NAME_DATE_FORMAT` (`dev/handoff.py:61`) is the format string shared with ct35a (D187)."

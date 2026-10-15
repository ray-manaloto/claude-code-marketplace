# handoff-skills retrospective: session-handoff and session-resume cover the /quit restart, the CLI check and the startup log

Unit `handoff-skills` (skills audit S3, S5, S6, S8, S9 doc line, S12; handoff-script parent edits
2-5; R-175, #139). Worktree `.claude/worktrees/handoff-skills`, branch `claude/handoff-skills`,
`base_sha` `3834661`, cut from the allocation commit `2b06eb3`, so `git log 2b06eb3..HEAD` is the
lane. Commits, in order: `535d61d` (the skill changes), `484f1c8` (merge of the integration tip
`65541f4`, clean, trailers, no lane branch name), then the commit carrying this record (the final
SHA, in the hand-back). Writer: Claude Sonnet 5.5, matching the record's `writer_model`. This is
the writer's draft: the independent cold review and the retro-writer pass have not run, so
"reviewed" is open.

Delivered, in the `.claude/skills/` copies and byte-identical in `.agents/skills/`:
- `session-handoff/SKILL.md`: step 1 also counts this session's background Bash commands and
  Monitor tasks as running work (2.1.300 force-kills a background command 1.5 s after exit, S8,
  S4 by hand); step 2 says the owner sentence holds no session name and sets the CLI row from
  `claude --version`; step 5 runs `start-command` plain (it generates the D61 name with
  `next-name` and fixes `--session-id`) and offers three restart paths, one only: `/clear` then
  `/session-resume <name>`; `/quit` (ignore the printed `claude --resume` line) then the start
  command; or the start command without its prompt, then `/reload-skills`, `/reload-plugins`
  (never `--force`) and `/session-resume <name>` (S3). The description gains `/quit` triggers.
- `handoff-template.md`: no session name in `## owner` (handoff-script edit 4); a CLI row
  "2.1.300 installed; the handing-off session ran 2.1.299"; an `action` that leads with R-176;
  header lines that state the owner and CLI-row rules; notes read "decisions through D188" (S5).
- `probe-commands.md`: the restart fire (`"source":"startup"`) and `startup` in the pass criteria
  (S9, handoff-script edit 3); the w0-doctor worktree fallback is gone (S6). `predicate.md`: the
  `H.injection-probe-failed` row lists four fires, matching `dev/handoff.py` at handoff-script.
- `session-resume/SKILL.md`: step 1 runs `claude --version` and puts the R-176 intake first when it
  differs from the version the CLI row says the handing-off session ran; new step 4 runs the
  session-start log checks after a restart; step 6 requires the `--session-id` the start command
  fixes (handoff-script edit 5); the doctor step loses the w0-doctor fallback (S6); the description
  names the `/quit` restart.
- Evals: each skill gains a `/quit`-and-upgrade eval (handoff 4, resume 3); handoff eval 1 checks
  and never asks whether agents run, eval 2 stops at step 1 where the skill says stop, eval 3 uses
  the open requests R-173 and R-056 and the R-176 intake in place of the ticked R-172 (S12).

Size: 14 files in two identical trees, 7 maintained; `git diff --numstat 2b06eb3 535d61d`
shows 112 added and 51 removed lines in the `.claude/skills/` copies.

Exits on the merged bytes `484f1c8`, from the worktree, `VIRTUAL_ENV` unset, one command each:
- `diff -r .claude/skills/session-handoff .agents/skills/session-handoff`: rc 0.
  `diff -r .claude/skills/session-resume .agents/skills/session-resume`: rc 0.
- `python3 -I -m json.tool` on each of the four `evals.json` files: rc 0 each.
- `./dev/mise tasks validate`: rc 0 (68 tasks). `./dev/mise run check`: rc 0 (`"status": "pass"`,
  91 tests OK). `./dev/mise run check:acceptance-baseline`: rc 0 (19 hashes).
- `git diff --check 2b06eb3 HEAD`: rc 0. hk `pre-commit` (`check:records`) passed on `535d61d`;
  the merge hooks passed on `484f1c8`.
- `./dev/mise run retro:gate -- handoff-skills`: run on this record; the rc is in the hand-back.
- Live probe: `python3 -I dev/handoff.py write --dry-run --agents-done` exits 1 in this worktree
  ("required handoff lines exceed 16 (18)") with the new template and also with the base template
  (17), so the refusal predates this lane (HS-2). `load_template` and `owner_name` on the new
  template return `next-session` for the owner (HS-1).

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P2 | HS-1 Steering: `write` takes the next session's name from the first backticked span of the template's `## owner` sentence (`owner_name`, `dev/handoff.py:699`). With the name-free owner sentence (handoff-script edit 4) it falls back to `next-session`, and that placeholder reaches the NEXT bullet ("owner: next session `next-session`") and the `/session-resume next-session` line of HANDOFF §8, while `start-command` prints a different, fresh name. Edit 4 as written (`next-name` in backticks) would have made the name `next-name`. (Writer; handoff-script HS-3, `dev/handoff.py:699`, `:788`.) | Applied in this lane: the owner sentence carries no backticks, and the template header says so. Deferred, owner parent via a fix lane on `dev/`: `write` must not print a name it did not generate (parent edit 4 gives the text for §8 and the NEXT bullet). Admission condition: `write --dry-run` shows no `next-session`, and the name in §8 equals the one `start-command` prints; until then step 5 of session-handoff names `start-command` as the only source of `<name>`. |
| P2 | HS-2 Automated checks: `write` refuses before it writes: the required lines are 17 with the base template and 18 with this one (the open-request roll-call takes 4 lines for the many open items; budget 16). The `action` lead sentence adds one line. (Writer; the dry-run above.) | Deferred, owner parent: tick or shorten open requests, or have `write` budget the roll-call, before the real `/session-handoff`; the writer kept the old Wave 0a text intact rather than trim content outside the contract. Admission condition: `python3 -I dev/handoff.py write --dry-run --agents-done` exits 0. Once R-176 closes, drop the template's first action sentence (parent edit 5), which returns the block to the base size. |
| P3 | HS-3 Information access: ct35a's `session-start/SKILL.md` does not yet document the log checks or the `events.jsonl` path (its branch `claude/ct35a-session-start-mod` was still running; `register.ts` already writes `fired`, `reload_plugins_begin`, `reload_plugins_end`, `title_set`, `title_skipped`, `title_kept` and `error` rows to `~/.local/state/claude-code-marketplace/session-start/events.jsonl`). session-resume step 4 therefore names the path and the four failures (no `fired` row for the session, reload not accepted, reload finished after the first prompt, title skipped) and defers the commands to that skill. (Writer; read of the ct35a worktree.) | Deferred, owner parent after ct35a integrates: read `session-start/SKILL.md`, and if its check names or commands differ from step 4's wording, edit step 4 in both copies. Admission condition: `grep -n 'events.jsonl' .claude/skills/session-start/SKILL.md` matches, and each failure named in step 4 appears there. |
| P3 | HS-4 Information access: `predicate.md` still said "three pwf fires" after handoff-script added the `startup` fire. The lane record did not list it and handoff-script's parent edits 2-5 did not either. (Writer; `dev/handoff.py:513`.) | Applied in this lane (owned path): the row lists four fires and what each receives. Verification: `grep -c 'four pwf fires' .claude/skills/session-handoff/references/predicate.md` prints 1, and the mirror diff is rc 0. |
| P3 | HS-5 Navigation: `predicate.md` (`H.doctor-findings`, "root, else the w0-doctor worktree copy") and `dev/handoff.py` §7 still carry the w0-doctor fallback that S6 retires from the skills; the code still falls back to it. (Writer.) | Kept in `predicate.md` because it describes the code. Deferred, owner parent with the fix lane in HS-1: drop the fallback from `dev/handoff.py` and then from `predicate.md`. Admission condition: `grep -rn 'w0-doctor' .claude/skills/session-handoff` matches nothing. |
| P3 | HS-6 Automated checks: the CLI row is hand-written, so session-resume's comparison rests on a sentence the handing-off agent types; a wrong "ran" version silently skips or forces the intake. (Writer.) | Deferred, owner parent: a ticket for `dev/handoff.py state` to print `claude --version` and `write` to generate the row. Admission condition: the row appears in `write --dry-run` output without a template line. |
| P3 | HS-7 Information access: audit findings S1, S2, S7 (applied by handoff-script), S10 (applied by handoff-script), S11 and S13 are not in this lane's contract. (Writer.) | Rejected for this lane (outside `owned_paths`); S1 and S2 are parent record work (sub-issues of #111, dispositions rows), S11 belongs to ct35b, S13 to the memory note. |

Navigation: HS-5 only. Every cited path resolves in the worktree except two that are local data
(`offline/research/R22-cc-2.1.300/`, ignored; `.claude/skills/session-start/`, on the ct35a branch);
the first exists in the root checkout, the second lands with ct35a.

Coding standards: no finding. Steps end on a done-when condition (rule 9), the new steps state the
behaviour to perform (rule 8; "run it plain" replaces a prohibition on `--name`), and the
`.agents` copies are byte-identical (rc 0).

Tool economy: no finding. One scripted pass per file, `write --dry-run` and the mirror diff reused
as the lane's own probes; the checks ran once before the tip merge and once after.

No-ops: none open. The `/quit` triggers in the description and the "run it plain" sentence change
what an agent does (`next-name` replaces a hand-typed name). The one sentence that restates the
code, in the template header (`write` reads the first backticked span), is a gotcha no config
confesses until HS-1 is fixed, and is deleted by that fix.

Steering and global guidance: no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or `.claude/agents`
file changed. HS-1 is the steering finding for the skill and the template.

Information access: the writer read the audit's S-table, handoff-script's retro and `dev/handoff.py`
at `0e4f6e7`, the ct35a worktree (`register.ts`, `SKILL.md`, its retro), and the 2.1.300 intake
README and `impact.md`. Nothing read a provider, the network or a secret; no environment listing
is printed.

## Parent edits (outside `owned_paths`; literal)

1. After lane ct35a-session-start-mod integrates: read `.claude/skills/session-start/SKILL.md`; if
   it does not name the `events.jsonl` path and the four failures, add a "Checks" section there that
   does (reload not accepted; no `fired` row for the session; reload finished after the first
   prompt; title skipped), each with the one command that finds it. If its wording differs from
   session-resume step 4, edit step 4 in `.claude/skills/session-resume/SKILL.md` and the
   `.agents` mirror (HS-3).
2. `lanes/handoff-skills.json`: set `status`, `review` and `retro` at integration. Add to `notes`:
   "session-handoff and session-resume now require `dev/handoff.py start-command` without `--name`
   and `owner` with the fixed `--session-id`."
3. Before the real `/session-handoff` (HS-2): bring the roll-call under the budget (tick R-n lines
   with evidence, or shorten) until `python3 -I dev/handoff.py write --dry-run --agents-done` exits 0.
4. `dev/handoff.py` (fix lane; HS-1 and S3): in `section_start` replace the "Two ways to start the
   next session; use one, never both:" list with
   ```text
   Three ways to start the next session; use one, never two:
   - Same terminal and version: type `/clear`, then `/session-resume <name>` as the first turn.
   - New version or new terminal: `/quit` (ignore the `claude --resume` line it prints), then paste
     the block above; its prompt already runs session-resume, so type nothing else.
   - New version, typed by hand: paste the block without its prompt, then type `/reload-skills`,
     `/reload-plugins` (never `--force`) and `/session-resume <name>`.
   ```
   with `<name>` the one after `claude -n` in the block, and make `render` leave the NEXT bullet's
   name and the `/session-resume` line to that block instead of `owner_name`. Update
   `test_section_start_types_resume_only_after_clear` to match.
5. When R-176 is ticked, delete the first sentence of the template's `## action` ("First R-176, the
   Claude Code 2.1.300 release intake (...)."), in both copies, and set the CLI row to
   "<version> installed; the handing-off session ran <version>".

# capture-filter retrospective: the capture hook records only user prompts (CT-88 follow-up, D166)

Unit: `capture-filter` (CT-88 follow-up; decision D166). Worktree `.claude/worktrees/capture-filter`,
branch `claude/capture-filter`, cut from allocation commit `53a05eb` on base `9cb206e`. Lane commit
`964dda6` (filter and tests); integration tip `a5efa27` merged clean in `036565f` (message amended to
carry the trailers). Cold review: not run at the time of this draft (reviewer fable, after handoff).
Writer: implementer (opus), this draft.

Delivered (all in `owned_paths`): the `UserPromptSubmit` capture command in `.claude/settings.json`
changes `/usr/bin/jq -c .` to one select, no other logic (D166):
`/usr/bin/jq -c 'select(.prompt // "" | test("^(<task-notification>|<event kind=|<<autonomous-loop)") | not)'`.
`dev/test_hooks.py` `RequestHooks` gains
`test_capture_drops_a_harness_prompt_and_keeps_a_user_prompt_that_quotes_one` and the
`HARNESS_PROMPTS` fixtures. The `PostToolUse` capture, the three deny gates and the D101 SessionStart
doctor entry are byte-identical (`git diff 53a05eb HEAD -- .claude/settings.json`: one line out, one in).

Shapes filtered, each with its evidence (prompt text never copied):
- `<task-notification>`, a background task or subagent reporting back: the live ledger
  (`~/.local/state/claude-code-marketplace/requests/ledger.jsonl`, read-only) held 14 rows at the run,
  12 `UserPromptSubmit` rows whose prompt starts `<task-notification>` (keys `p:9dc3aa9d`, `p:cf32b5bb`,
  `p:7f9526d4`, `p:b65d3252`, `p:f4633fea`, `p:0eddae5d`, `p:92ef79e7` x6), 1 plain user prompt and
  1 `PostToolUse` answer. The offline Claude Code hooks doc (`offline/research/CL3/docs/hooks.md`,
  `### UserPromptSubmit`, fetched 2026-10-14) says the event also fires on a background subagent
  reporting back, a scheduled task or `/loop` iteration, and a cross-session message.
- `<event kind=`: Claude Code 2.1.300 (`~/.local/share/claude/versions/2.1.300`, `strings`) builds a
  poll event or session notice as `<event kind="..." at="...">...</event>` and runs the
  `UserPromptSubmit` hooks on that element (`hookText:e.element`; session notices through the same
  call). Cited from code, not observed live.
- `<<autonomous-loop`: the same binary defines the `<<autonomous-loop>>` (CronCreate) and
  `<<autonomous-loop-dynamic>>` (ScheduleWakeup) sentinels a `/loop` with no user prompt fires with;
  the doc says a `/loop` iteration runs the hook. Whether the hook sees the sentinel or the resolved
  instructions is not confirmed.

Receipts, writer (VIRTUAL_ENV unset; worktree `.claude/worktrees/capture-filter`):
- Red first: the new test failed on `53a05eb` bytes (`python3 -I -m unittest discover -s dev -p
  test_hooks.py -k RequestHooks` rc 1, 2 failures: the notification row appended); green after the
  `startswith("<task-notification>")` select (rc 0, 7 tests). Second slice: three new fixtures failed
  (rc 1, 4 failures) until the select became the anchored `test(...)` (rc 0).
- Fixture run of the changed command (`/bin/sh -c`, `env -i`, scratch HOME): the three harness shapes
  rc 0 and 0 rows; a plain prompt, a prompt quoting `<task-notification>` on its second line and a
  slash command rc 0 and one row each; invalid stdin rc 1, no row; directory mode 700.
- Replay of all 14 live rows through the new command into a scratch HOME: 14 rc 0; the 12 notification
  rows dropped; scratch output deleted.
- On merged bytes `036565f`: `./dev/mise run test:hooks` rc 0 (25 tests); `./dev/mise tasks validate`
  rc 0 (66 tasks); `./dev/mise run check` rc 0 (`status: pass`); `./dev/mise run
  check:acceptance-baseline` rc 0 (19 baseline hashes); `git diff --check 53a05eb HEAD` rc 0.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Information access (writer, live ledger): a notification row carries its turn's `prompt_id` (`92ef79e7` on 6 notification rows and the turn's `PostToolUse` answer, `f4633fea` on one notification and the user prompt), so its `p:<first 8 of prompt_id>` key equals the user prompt's key and raised `H.request-unprojected` P1 for text the user never wrote. | Applied in `964dda6`: the capture drops it before it lands. Verified: replay of the 14 live rows drops the 12 notification rows, `test:hooks` rc 0. The 12 rows already in the live ledger stay (read-only evidence for this lane) and still feed `dev/handoff.py check`: deferred, owner parent, parent edit 2 below; admission condition: a recorded admission for the user-state mutation. |
| P3 | Information access (writer): shapes not filtered because no evidence shows a distinguishing prefix at the hook: a cross-session message ("arrives as plain text", `offline/research/CL3/docs/cross-session-messaging.md`), a scheduled task firing its configured prompt (the user's own text), and the `<channel source=`, `<webhook-payload>` and `<teammate-message>` wrappers present in the 2.1.300 binary. The `<event kind=` and `<<autonomous-loop` filters are cited from code, not observed live. | Deferred, owner parent; admission condition: the separately admitted fresh-session acceptance (`ci/acceptance.sh`) fires each event once and records the ledger row's first token. The durable fix filters on `origin.kind` (`human` versus `task-notification`, `peer`, `channel`), which transcripts carry and the mods `session.receive` event exposes (`plugins_mods_api.md:254`) but the hook stdin lacks (ledger row keys); it lands with the D166 stand-down on the existing watch list. |
| P3 | Automated checks (writer): the second-line quoting case was green on first run; `/usr/bin/jq` 1.7.1-apple anchors `^` at string start, so it is a regression guard, not red-first evidence. | Kept as a guard in `964dda6` (a regex change to a multiline mode would fail it). Verified: `printf '"a\n<x>"' \| /usr/bin/jq 'test("^<x>")'` prints `false`, rc 0. The Linux image's jq is the request-hooks retro's existing unrun item, unchanged here. |
| P3 | Steering/global guidance (writer): `docs/agents/hooks-and-mods.md` says the capture appends "the hook stdin"; it now drops harness prompts. The file is outside `owned_paths`. | Deferred, owner parent; literal edit 1 below; closes when the line is on the integration branch. |

Navigation: none; `.claude/rules/hooks-and-mods.md` scopes `.claude/settings.json` and points at the
hooks doc, and the lane record named the seam and test file. Coding standards: none; the change is one
`select` inside the existing `jq` call (D166), and the test asserts the seam (exit code, stdout, ledger
bytes). Tool economy: one finding, no guardrail: a `grep -aoE '.{160}<tag>.{160}'` over the 250 MB
binary hit the 120 s timeout, while `strings -n 12` once into the scratchpad plus `grep` took 2 s;
the second route is the one recorded above. No-ops: none; the slice-1 `startswith` select was replaced
by slice 2's anchored regex, which the three new fixtures required.

Parent edits (outside `owned_paths`; literal text):
1. `docs/agents/hooks-and-mods.md`, in the Capture bullet, after "holding the directory at mode 0700 on
   every run (`mkdir -p` then `chmod 700`)." add: "The prompt capture drops a harness prompt, one that
   starts `<task-notification>`, `<event kind=` or `<<autonomous-loop`, with one jq `select` (lane
   capture-filter); a cross-session message and a scheduled task's configured prompt still land."
2. Live ledger (user state, needs admission): back up, then keep only non-harness rows:
   `L=~/.local/state/claude-code-marketplace/requests/ledger.jsonl; cp -p "$L" "$L.bak" && /usr/bin/jq -c 'select(.prompt // "" | test("^(<task-notification>|<event kind=|<<autonomous-loop)") | not)' "$L.bak" > "$L"`;
   then rerun `dev/handoff.py check` and record that no `H.request-unprojected` names a notification key.

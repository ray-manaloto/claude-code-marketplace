# capture-filter retrospective: the capture hook records only user prompts (CT-88 follow-up, D166)

Unit: `capture-filter` (CT-88 follow-up; decision D166). Worktree `.claude/worktrees/capture-filter`,
branch `claude/capture-filter`, cut from allocation commit `53a05eb` on base `9cb206e`. Lane commit
`964dda6` (filter and tests); integration tip `a5efa27` merged clean in `036565f`; implementer's retro
draft `4289ead`. Cold review: reviewer (fable, read-only) on `4289ead`, PASS with four P3 findings,
dispositioned in the table below; the reviewer's own fixture run of the exact command passed (harness
prefixes dropped; plain, mid-text, second-line and leading-space prompts kept; bad input rc 1, no row).
Writers: implementer (opus) for `964dda6` and the draft; retro-writer (fable) owns this record.

Delivered (all in `owned_paths`): the `UserPromptSubmit` capture command in `.claude/settings.json`
changes `/usr/bin/jq -c .` to one select, no other logic (D166):
`/usr/bin/jq -c 'select(.prompt // "" | test("^(<task-notification>|<event kind=|<<autonomous-loop)") | not)'`.
`dev/test_hooks.py` `RequestHooks` gains
`test_capture_drops_a_harness_prompt_and_keeps_a_user_prompt_that_quotes_one` and the
`HARNESS_PROMPTS` fixtures. The `PostToolUse` capture, the three deny gates and the D101 SessionStart
doctor entry are byte-identical (`git diff 53a05eb 964dda6 -- .claude/settings.json`: one line out, one
in). The retro pass changes one fixture comment (`dev/test_hooks.py:342-343`, row 2) and this record.

Shapes filtered, each with its evidence (prompt text never copied):
- `<task-notification>`, a background task or subagent reporting back: the live ledger
  (`~/.local/state/claude-code-marketplace/requests/ledger.jsonl`, read-only) held 14 rows at the lane
  run, 12 `UserPromptSubmit` rows whose prompt starts `<task-notification>` (keys `p:9dc3aa9d`,
  `p:cf32b5bb`, `p:7f9526d4`, `p:b65d3252`, `p:f4633fea`, `p:0eddae5d`, `p:92ef79e7` x6), 1 plain user
  prompt and 1 `PostToolUse` answer. The Claude Code hooks reference
  (`https://code.claude.com/docs/en/hooks.md`, `### UserPromptSubmit`, retrieved 2026-10-14T19:00:05Z,
  page SHA-256 `7f966fd46024f61c5fca05a577a31b65c8335fac382be76e34ea05f4c7a00df7`) says: "`UserPromptSubmit`
  hooks don't fire only on prompts you type. Claude Code also runs them on: A scheduled task firing,
  including a `/loop` iteration; A background subagent reporting back to the session that started it;
  A message another session sends to your main conversation."
- `<event kind=`: Claude Code 2.1.300 (`~/.local/share/claude/versions/2.1.300`, 249,556,880 bytes,
  `strings -n 12`) builds an element-form poll event as `<event kind="..." at="...">...</event>` and runs
  the `UserPromptSubmit` hooks on that element (`hookText:e.element`). Cited from code, not observed
  live.
- `<<autonomous-loop`: the same binary defines the `<<autonomous-loop>>` (CronCreate) and
  `<<autonomous-loop-dynamic>>` (ScheduleWakeup) sentinels a `/loop` with no user prompt fires with;
  the doc says a `/loop` iteration runs the hook. Whether the hook sees the sentinel or the resolved
  instructions is not confirmed.

Shapes not filtered (information access; each with its evidence and why it stays):
- Fields-form poll event (review finding): the same binary has a second delivery site,
  `hookText:[e.kind,e.at,Vss(r.fields)].filter((w)=>w!=="").join("\n")`, so the hook text starts with
  the bare kind word (validated by `^[a-z][a-z0-9-]{0,63}$`; `session-notice` is one, with fields
  `notice-class` and `from-session`), then the `at` line, then the fields. A prefix filter on a plain
  lowercase word would drop a real prompt that begins with that word, so it stays unfiltered until a
  live row shows the exact shape (row 2).
- A cross-session message "arrives as plain text" (`https://code.claude.com/docs/en/cross-session-messaging.md`,
  retrieved 2026-10-14), a scheduled task firing its configured prompt (the user's own text), and the
  `<channel source=`, `<webhook-payload>` and `<teammate-message>` wrappers present in the 2.1.300
  binary: no evidence shows which of these reach the hook or with what first token (row 3).

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

Receipts, retro-writer (same worktree, on this record's bytes; see "Checks on the final bytes" below):
- Live ledger at the retro, counted by prefix with no text printed (`jq -r` over
  `hook_event_name` and the prompt's prefix class): 20 rows, 17 `UserPromptSubmit` starting
  `<task-notification>`, 1 `UserPromptSubmit` user prompt, 2 `PostToolUse`. The running session uses
  the main checkout's unmerged `settings.json`, so notification rows keep landing until integration.
- `git ls-files offline` prints nothing and `.git/info/exclude:17` excludes `/offline/`: the draft's
  `offline/research/CL3/docs/hooks.md` cite named an untracked file (row 3).
- `dev/check.py:76` runs `dev/test_research_*.py` and `dev/research_refresh/test_*.py` only;
  `.github/workflows/development.yml:18` runs `python3 -B dev/check.py`; `dev/test_hooks.py` runs only
  through `test:hooks` (`mise.dev.toml:346`), which no workflow names (row 5).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Information access (writer, live ledger): a notification row carries its turn's `prompt_id` (`92ef79e7` on 6 notification rows and the turn's `PostToolUse` answer, `f4633fea` on one notification and the user prompt), so its `p:<first 8 of prompt_id>` key equals the user prompt's key and raised `H.request-unprojected` P1 for text the user never wrote. | Applied in `964dda6`: the capture drops it before it lands. Verified: replay of the 14 live rows drops the 12 notification rows, `test:hooks` rc 0. The 17 notification rows now in the live ledger stay (read-only evidence for this lane) and still feed `dev/handoff.py check`: deferred, owner parent, parent edit 2 below; admission condition: the user's recorded admission for the user-state mutation, or the parent adds `dispositions.jsonl` rows for those keys instead. |
| P3 | Information access (review, draft row 2 and `dev/test_hooks.py:342`): Claude Code 2.1.300 has a second `UserPromptSubmit` delivery path, `hookText:[e.kind,e.at,Vss(r.fields)].filter((w)=>w!=="").join("\n")`, whose text starts with the bare kind word (`^[a-z][a-z0-9-]{0,63}$`, e.g. `session-notice`), not `<event kind=`; the filter covers only the element path (`hookText:e.element`). | Applied in part: the fixture comment at `dev/test_hooks.py:342-343` now names the element form and the unfiltered fields form (`test:hooks` rc 0 below). The filter itself: deferred, owner parent; reason: a prefix filter on a plain lowercase word drops a real prompt that starts with that word, and no live row shows the fields form yet; admission condition: observed live, a ledger row whose prompt starts with a kind word, a newline and an `at` timestamp, recorded by its key and first token; then choose between a structural regex (`^[a-z][a-z0-9-]{0,63}\n\d{4}-`) and the `origin.kind` fix in row 3. Evidence: `strings -n 12` of the 2.1.300 binary, 4 `hookText` sites, 2 of them build hook text (element and fields forms). |
| P3 | Information access (writer; review on the cite): shapes not filtered because no evidence shows a distinguishing prefix at the hook: a cross-session message, a scheduled task firing its configured prompt, and the `<channel source=`, `<webhook-payload>` and `<teammate-message>` wrappers present in the 2.1.300 binary. The `<event kind=` and `<<autonomous-loop` filters are cited from code, not observed live. The draft cited `offline/research/CL3/docs/hooks.md`, an untracked file absent from the worktree (`.git/info/exclude:17`), against CODING_STANDARDS rules 4 and 7. | Cite applied in this record: the sentence is quoted with its URL `https://code.claude.com/docs/en/hooks.md`, retrieval time 2026-10-14T19:00:05Z and page SHA-256 `7f966fd4...a00df7`; the untracked path appears in this record only as the finding in this row. Shapes: deferred, owner parent; admission condition: the separately admitted fresh-session acceptance (`ci/acceptance.sh`) fires each event once and records the ledger row's first token. The durable fix filters on `origin.kind` (`human` versus `task-notification`, `peer`, `channel`), which transcripts carry and the mods `session.receive` event exposes (`plugins_mods_api.md:254`) but the hook stdin lacks (ledger row keys); it lands with the D166 stand-down on the existing watch list. |
| P3 | Automated checks (review; inherited `.claude/settings.json:48`, `/usr/bin/jq`): the OCI image is `debian:bookworm-slim` (`mise.toml:26`) and `jq` 1.8.2 comes from mise through aqua (`mise.toml:14`, `mise.toml:52-57`), so `/usr/bin/jq` is absent unless `apt` installs it. Failure mode under `sh -c`: `mkdir` and `chmod` succeed, the `>>` redirect creates an empty ledger, `/usr/bin/jq` is "not found" (127), `\|\| exit 1` makes the hook rc 1; the hook is async and only rc 2 blocks, so every prompt is captured as nothing and nothing stops. | Deferred, owner parent; destination: the request-hooks follow-ups (`retros/request-hooks.md` row "Automated checks (review, unrun)") and the CT-80 OCI admission; admission condition: the separately admitted container operation runs the capture command from a fixture under the image and records rc and ledger bytes; the absolute path stays until that run says what the image holds. |
| P3 | Automated checks (retro-writer): `dev/test_hooks.py`, the only seam test of the filter, is not wired in: `dev/check.py:76` discovers `test_research_*.py` and `dev/research_refresh/test_*.py` only, and `development.yml:18` runs `python3 -B dev/check.py`; `test:hooks` (`mise.dev.toml:346`) is named by no workflow. | Deferred, owner parent (`dev/check.py` is outside `owned_paths`); parent edit 3 below is the literal change. Admission condition: `python3 -B dev/check.py` rc 0 on the integration branch after the edit (the hk class self-skips without `hk`, `dev/test_hooks.py:468`); the CI claim stays unrun until a `development.yml` run reports rc, since the runner's `/usr/bin/jq` is unverified from here. |
| P3 | Coding standards (review, by design): a real prompt whose first characters are one of the three prefixes is dropped; a leading space keeps it. | Rejected as a change, with reason: the hook stdin carries no origin field (ledger row keys), so a user prompt that begins with the exact harness element is indistinguishable from the element at this seam; the loss is bounded to text starting with a harness tag, and the `origin.kind` fix in row 3 removes it. Verified: the reviewer's fixture run kept the leading-space prompt; the test keeps the mid-text and second-line quoting prompts (`test:hooks` rc 0). |
| P3 | Automated checks (writer): the second-line quoting case was green on first run; `/usr/bin/jq` 1.7.1-apple anchors `^` at string start, so it is a regression guard, not red-first evidence. | Kept as a guard in `964dda6` (a regex change to a multiline mode would fail it). Verified: `printf '"a\n<x>"' \| /usr/bin/jq 'test("^<x>")'` prints `false`, rc 0. |
| P3 | Steering/global guidance (writer): `docs/agents/hooks-and-mods.md:29-30` says the capture appends "the hook stdin, `jq -c .`"; it now drops harness prompts. The file is outside `owned_paths`. | Deferred, owner parent; literal edit 1 below; closes when the line is on the integration branch. |

Navigation: none; `.claude/rules/hooks-and-mods.md` scopes `.claude/settings.json` and points at the
hooks doc, and the lane record named the seam and test file. Coding standards: one finding, the
by-design row above, rejected with its reason; the change is one `select` inside the existing `jq`
call (D166), and the test asserts the seam (exit code, stdout, ledger bytes). Tool economy: two
findings, no guardrail: (a) writer: a `grep -aoE '.{160}<tag>.{160}'` over the 250 MB binary hit the
120 s timeout, while `strings -n 12` once into the scratchpad plus `grep` took 2 s; (b) retro-writer:
`grep` on this host is `ugrep`, which rejects a bounded `.{0,300}` pattern ("exceeds complexity
limits"), so bounded context extraction from the strings dump and the 262 KB single-line doc went
through `python3 -I` and `/usr/bin/grep`; host-specific, so no project rule. No-ops: none; the slice-1
`startswith` select was replaced by slice 2's anchored regex, which the three new fixtures required,
and this record replaces the draft's "cold review not run" line with the review disposition.

Checks on the retro bytes (retro-writer, this worktree, VIRTUAL_ENV unset, one literal command each,
run on the comment edit plus this record; the only later edit is this paragraph, after which the two
record-reading checks ran again): `./dev/mise run test:hooks` rc 0 (25 tests); `./dev/mise tasks
validate` rc 0 (66 tasks); `./dev/mise run check` rc 0 (`status: pass`); `./dev/mise run
check:acceptance-baseline` rc 0 (19 baseline hashes); `git diff --check 53a05eb HEAD` rc 0;
`./dev/mise run retro:gate -- capture-filter` rc 0 (`RETRO GATE PASSED`).

Parent edits (outside `owned_paths`; literal text):
1. `docs/agents/hooks-and-mods.md`, in the Capture bullet, after "holding the directory at mode 0700 on
   every run (`mkdir -p` then `chmod 700`)." add: "The prompt capture drops a harness prompt, one that
   starts `<task-notification>`, `<event kind=` or `<<autonomous-loop`, with one jq `select` (lane
   capture-filter); a cross-session message, a fields-form poll event and a scheduled task's configured
   prompt still land."
2. Live ledger (user state, needs the user's admission; not run by this lane): back up, then keep only
   non-harness rows:
   `L=~/.local/state/claude-code-marketplace/requests/ledger.jsonl; cp -p "$L" "$L.bak" && /usr/bin/jq -c 'select(.prompt // "" | test("^(<task-notification>|<event kind=|<<autonomous-loop)") | not)' "$L.bak" > "$L"`;
   then rerun `dev/handoff.py check` and record that no `H.request-unprojected` names a notification
   key. Alternative without the mutation: add `dispositions.jsonl` rows for the notification keys.
3. `dev/check.py:76`, replace
   `for directory, pattern in (("dev", "test_research_*.py"), ("dev/research_refresh", "test_*.py")):`
   with
   `for directory, pattern in (("dev", "test_research_*.py"), ("dev", "test_hooks.py"), ("dev/research_refresh", "test_*.py")):`
   then run `python3 -B dev/check.py` and record rc.

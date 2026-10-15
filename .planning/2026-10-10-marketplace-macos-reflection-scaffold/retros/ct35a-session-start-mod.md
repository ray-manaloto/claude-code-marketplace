# ct35a-session-start-mod retrospective — project session-start mod (CT-35)

Unit `ct35a-session-start-mod` (CT-35; D61, D76, D87, D92, D93, D103, D186, D187). Worktree
`.claude/worktrees/ct35a-session-start-mod`, branch `claude/ct35a-session-start-mod`, cut from
allocation commit `20c0ef0` (base `32e742c`). Lane commits `b2bd433` (mod), `0b11e75`
(diagnostic log, a scope addition the user asked for on 2026-10-14) and `f68951c` (review
fixes); integration tips `e81645b`, `2b06eb3` and `b1dc645` merged as `407badc`, `76fce4a` and
`39217e9`. Implementer draft `36157c1`; cold review (Fable, read-only, on `36157c1`):
pass-with-fixes, two P2 and six P3, all applied in `f68951c` and re-verified below. Retro writer
(Fable) finished this record; integration is the parent's.

Delivered (all inside `owned_paths`): `.claude/skills/session-start/` holding
`.claude-plugin/plugin.json` (`defaultEnabled: true`, author added for `--strict`),
`hooks/hooks.json`, `hooks/register.ts` (114 lines, every engine call), `hooks/log.ts` (50 lines,
pure helpers), `tests/session-start.test.ts` (17 tests) and a reference `SKILL.md`
(`disable-model-invocation: true`, with the log fields and four detection checks).
`session.start` awaits a plain `$.command.run({ command: 'reload-plugins' })` in interactive
sessions only, raced against a `$.clock.after` deadline of 30 s, and sets a status line on a held
(`--force to apply`), rejected or timed-out reload. `classic.SessionStart` returns `reloadSkills`
on `startup` and `clear`; on `startup` without `session_title` it also returns `sessionTitle` =
`ccm-` + `/bin/date +%Y%m%dT%H%M%S.%N%z` with the last two offset digits cut
(`ccm-20261014T184849.575921000-05`), only when the output matches
`^\d{8}T\d{6}\.\d{9}[+-]\d{4}$`. `resume`, `compact` and `fork` pass through. A failing or
off-shape `date` keeps `reloadSkills`, sets no title and leaves a status line. No settings hook,
no `.agents/` mirror, no `.claude/settings.json` edit.

Diagnostic log: every step writes one JSON row to two places.
- The JSONL file `~/.local/state/claude-code-marketplace/session-start/events.jsonl`, through
  `$.process.run(['/bin/sh', '-c', APPEND, ...], { timeoutMs: 5000 })` under `umask 077`, with
  `ts` stamped by `/bin/date -u +%Y%m%dT%H%M%S.%NZ`. The script re-chmods the directory 0700 and
  exits 3 without writing when `events.jsonl` is a symlink.
- The native facility `$.ui.log(row, { to: 'debug' })`. The types have no append or file-mode
  call: `$.fs.write` replaces the whole file.

Row fields: `session_id` (`e.session_id`, or `$.session.id()` in `session.start`), `cli_version`
(`$.session.version().version`), `event`, `source`, `step`, `result` (a classification plus an
excerpt: `(token|key|secret|password)=\S+` and `Bearer \S+` redacted, then 120 characters),
`duration_ms` (`$.clock.now()` around the reload) and `transcript_path`.
`MARKETPLACE_SESSION_START_LOG` overrides the directory; with neither it nor `HOME` set the file
append is skipped, the debug rows stay and one `error` row says so. The tests set the override to
`/tmp/session-start-test-log` through `mock.env`, and the `process.run` stub captures the rows, so
no test touches disk. A failed write is swallowed, so logging never blocks a start. Cost: each
`session.start` row is an `sh` plus `date` spawn before the first prompt (three rows on an
interactive start; unmeasured, live step 1).

## Checks (worktree, `VIRTUAL_ENV` unset, one literal command each)

Red then green, one vertical slice per test, all through `claude plugin test
.claude/skills/session-start`. The coordinator approved this mocked-engine harness on 2026-10-14;
it ran no session, model or network. Implementer cycles: each slice red with rc 1 for the expected
reason, then green with rc 0 (date argv and title, `-n` wins, clear, pass-through, awaited reload,
non-interactive skip, held status, rejected status, failed date; then the classic rows and the
`session.start` rows). Mutation control: the rejected D103 shape (`void $.command.run(...)`)
fails the awaited-reload test (rc 1, `session.start settled` before the reload).

Review-fix cycle (retro writer, on `39217e9`): the rewritten test file against the unchanged
module was red, rc 1, 14 fail / 3 pass (the three pure-helper tests pass as soon as `log.ts`
exists); the timeout test failed by the harness's 5 s limit (`5004.56ms`), which is the unbounded
await the reviewer named. With `f68951c`: 17 pass, rc 0.

| Command | After the second merge (`36157c1`) | After the fixes (`f68951c`) |
| --- | --- | --- |
| `claude plugin test .claude/skills/session-start` | rc 0, 9 pass | rc 0, 17 pass |
| `claude plugin validate --strict .claude/skills/session-start` | rc 0 | rc 0 (`calls:` lists `$.clock.after`, `$.env.get (via open)`) |
| `claude plugin list` (worktree cwd) | rc 0, `session-start@skills-dir` Scope project, `✔ loaded` | rc 0, same |
| `tsc -p` scratch tsconfig against the 2.1.299 types, then the 2.1.296 types | rc 0, rc 0 | rc 0, rc 0 (tsc 7.0.2, `allowImportingTsExtensions` for `./log.ts`) |
| The `APPEND` script run with `/bin/sh` in a scratch directory | rc 0; rows parse; dir `drwx------`, file `-rw-------` | rc 0 fresh dir (0700/0600, nested `mkdir -p`); rc 0 on a pre-existing 0755 dir, tightened to 0700; rc 3 on a symlinked `events.jsonl`, target untouched; the reviewer's injection row (`$(touch INJECTED)`, backticks, `%s`, quotes) lands verbatim, no file created; two rows append as two lines |
| `/bin/date '+%Y%m%dT%H%M%S.%N%z'` on this host (macOS 27.0.1) | n/a | rc 0, `20261014T192619.943934000-0500` (nanoseconds honoured; PATH `date` is the mise shim) |
| The four SKILL.md detection commands on a synthetic log and transcript | each printed the expected row; check 3 printed `LATE` for a reload ending 4 s after the first prompt | commands unchanged; wording per check rewritten |
| `./dev/mise tasks validate` | rc 0 | rc 0 (68 tasks) |
| `./dev/mise run check` | rc 0 | rc 0 (json 2330, python 246, shell 6, toml 21) |
| `./dev/mise run check:acceptance-baseline` | rc 0 (19/19) | rc 0 (19/19) |
| `git diff --check 20c0ef0` | rc 0 | rc 0 |
| `./dev/mise run retro:gate -- ct35a-session-start-mod` | rc 0 | rc 0 (`RETRO GATE PASSED`, selectors: none), rerun after this record's commit |

Policy-hold check (coordinator request, read-only, #102134): no
`/Library/Application Support/ClaudeCode/` (so no managed settings and no `managed-mcp.json`), no
`com.anthropic.claudecode` defaults domain, no `/Library/Managed Preferences/`;
`~/.claude/remote-settings.json` is `{}`; `claude auth status` shows `subscriptionType: max`
(only that field was read); `claude doctor` (2.1.300, rc 0) prints `Managed settings (remote): not
fetched — requires an Enterprise or Team subscription` and `Organization policy: not applicable to
Pro and Max accounts`. So `sec-default@builtin` is not seated here, and it would hold only
`classic.*`, not `session.start` (sec-default README rows `classic.*` and "everything else"). The
2.1.299 types have no hold-query API (only `$.settings.read({ source: 'policy' })`).

## APIs: confirmed and unconfirmed

Confirmed on disk (2.1.299 types laid by the plugin-authoring skill; 2.1.296 bundle; 2.1.299 docs
copies): `classic.SessionStart` input `source` and `session_title` (set by `--name`, docs
hooks.md:1236) and result `reloadSkills` and `sessionTitle` (`ClassicResultFields.SessionStart`).
Also confirmed: `SessionStartInput.isInteractive`, `$.command.run` resolving
`CommandRunResult.text`, `$.process.run(argv, { timeoutMs })` (30 s default, ten minutes at most)
resolving `{ exitCode, stdout, stderr }`, `$.clock.after(ms, fn)` returning `{ cancel }` and the
mock clock resolving it on `advance`, `$.ui.status`, the held-reload wording
(plugins/cli-reference:859, plugins/troubleshooting:946), `defaultEnabled` for `@skills-dir`
(plugins/loading:53), and the hooks-module import rules (plugins/mods/create: a sibling file by
relative `import` declaration; `$` may not be passed to an imported function).

Unconfirmed, so live acceptance decides them:
- 2.1.300 types and docs are not on disk; the CLI is 2.1.300.
- On the real engine, a `$.command.run` made from `session.start` runs as a start input while the
  first prompt waits (R3 read this from the 2.1.299 binary; the docs only say the first
  `session.start` is awaited).
- A held reload reaches the mod as `text` rather than as a rejection, and the 2.1.300 text still
  contains `--force to apply` (the 2.1.299 docs' wording; the substring is kept, live step 1
  records the actual text).
- `HookBudget.ms` is 10 s of the hook's own time and stops while a `$` call is in flight, a
  `$.clock` wait excepted (types, `HookBudget`). The 30 s deadline is a `$.clock.after` timer
  beside the in-flight `$.command.run`, not a `$.clock.sleep`; whether the engine counts the
  timer's wait against the budget is what live step 1 shows (a `reload_plugins_end` row after a
  slow reload means it does not).
- `sessionTitle` adds nothing to the cached request prefix.

## Findings

| Severity | Category and finding | Applied action, verification and disposition |
| --- | --- | --- |
| P2 | Automated checks (review P2-1, `register.ts:77, :52, :28`): no await was bounded; a hung `/reload-plugins`, `date` or `sh` would hold the first prompt for ever. | Applied in `f68951c`: `timeoutMs` 5000 on both `$.process.run` calls; the reload races `$.clock.after(30000)`, and on timeout writes `reload_plugins_end` `timeout: no answer after 30000 ms`, sets a status line, swallows the late answer and lets the start continue. Tests `every process.run is bounded` and `a reload still running at the deadline ...` (`mock.clock`, `advance(29999)` then `advance(1)`), rc 0. |
| P2 | Automated checks (review P2-2, `register.ts:26-27`): with no `HOME` and no override the append path was the relative `undefined/.local/...` (the reviewer's probe wrote under a `null/` directory). | Applied in `f68951c`: `logDir(override, home)` returns undefined when neither is set; `open()` then emits one `error` debug row and `log()` skips the append. Tests `no HOME and no override ...` (`mock.env(on, {})`) and `logDir prefers ...`, rc 0. |
| P2 | Automated checks: the mod's behaviour had no named check; `claude plugin test` is an offline harness (mocked engine, no session or model) the brief did not know about. | Applied: 17 tests in `tests/session-start.test.ts`, rc 0, with the unawaited-shape mutation control rc 1. A mise task is a parent edit (`mise.dev.toml` is excluded); exact text under Parent edits, item 4. Owner: parent at integration. |
| P2 | Automated checks: D61 needs one format string, but `dev/handoff.py` `NAME_DATE_FORMAT` (lane `handoff-script`, `+%Y%m%dT%H%M%S.%N%z`, read 2026-10-14) and `DATE_ARGV[1]` in `log.ts` can drift with no test. | Deferred with owner: the handoff-script implementer adds a test asserting `NAME_DATE_FORMAT` equals `DATE_ARGV[1]` read from `hooks/log.ts` and the two-character offset cut (Parent edits, item 6). |
| P2 | Information access: the brief pointed to the 2.1.296 types, but loading the plugin-authoring skill writes the running build's types (2.1.299 here) and its `reference.md`, and its "make a mod" flow would write under `~/.claude/dev-mods/`, which triggers a hot-reload question. | Applied: types read from the skill's 2.1.299 bundle, files written only in the worktree (no dev-mods write), tsc rc 0 against both bundles. Ct35b doc line in Parent edits, item 3. |
| P2 | Steering: a seated `sec-default` skips this project plugin's `classic.SessionStart` (no skills reload, no title) while `session.start` still runs; strict validate says so too. | Applied: SKILL.md states it; host check shows no seat (receipts above). Live step 5 records `/doctor` state. No code change: the hook cannot detect the hold, so this needs no fallback. |
| P2 | Information access (user request): a start that fails quietly (mods off, a hold, a held or late reload, no title) left nothing an agent could read without parsing the debug log. | Applied: JSONL rows plus debug-log rows, and four detection checks in SKILL.md, each run on a synthetic log (receipts above). The tests assert the rows for success, held, rejected, timeout, title and date failure. Detection inside the doctor is a separate later item (a C++ core candidate, D113), owner parent. |
| P3 | Coding standards (review, `register.ts:52-59`): `date` output was sliced unvalidated, so a BSD `date` without `%N` or an error line would have become a title; PATH `date` is a mise shim on this host. | Applied in `f68951c`: `DATE_ARGV[0]` is `/bin/date` (the `dev/handoff.py date_binary()` rule), `parseDate` accepts only `^\d{8}T\d{6}\.\d{9}[+-]\d{4}$` and an off-shape output logs `error` `date output unexpected: ...` then `title_skipped`. Tests `date output off the D61 shape ...` and `parseDate accepts only ...`, rc 0; `/bin/date` receipt above. |
| P3 | Coding standards (review, `register.ts:13, :28`): the append followed a symlinked `events.jsonl` and left a pre-existing wider directory as it was. | Applied in `f68951c`: `APPEND` runs `chmod 700 "$1"` after `mkdir -p` and exits 3 on `[ -L "$f" ]` before any write. `/bin/sh` receipts above (0755 tightened to 0700; symlink rc 3, target untouched); the test world asserts the argv carries the exported `APPEND`. |
| P3 | Information access (review, `register.ts:23, :49, :79, :83`): rows and status lines carried up to 500 characters of raw engine or OS text, which a future error could fill with a credential. | Applied in `f68951c`: `excerpt()` redacts `(token|key|secret|password)=\S+` (case-insensitive) and `Bearer \S+`, trims and cuts to 120; every logged `result` and status line is a classification plus an excerpt. Tests `logged text is redacted and cut ...` and `excerpt: redaction first ...`, rc 0. |
| P3 | Navigation (review, `SKILL.md:57-58`): "each check prints nothing when all is well, except check 3" was wrong for checks 1 and 2 (both print on a healthy start). | Applied in `f68951c`: each check names what a healthy start prints and what the failure looks like; check 2 lists `timeout: ...`. Read-through above. |
| P3 | Steering (review, `register.ts:78`): the held-reload substring `--force to apply` comes from the 2.1.299 docs; the 2.1.300 text is unconfirmed. | Kept with a comment in `register.ts` and a live-acceptance step: step 1 records the actual held line when one appears (Parent edits, item 9). Owner: parent at the user's restart. |
| P3 | Coding standards (review, size): the maintained files passed ~300 lines once the log scope was added. | Applied in `f68951c`: pure helpers (`DATE_ARGV`, timeouts, `APPEND`, `logDir`, `parseDate`, `excerpt`) moved to `hooks/log.ts` with their own kit-free tests; `register.ts` keeps every `$` call, because a hooks module may not pass `$` to an imported function (docs rule, confirmed by `validate --strict` listing `$.env.get (via open)`). `register.ts` 114 lines, `log.ts` 50, rc 0. |
| P3 | Coding standards: validate lists `gating hook without .catch: classic.SessionStart`. | Rejected with reason: a hook that throws is skipped and the session goes on (reference.md), which is the wanted fail-open, and `.catch(($, e, next) => next(e))` would behave the same. |
| P3 | Tool economy: `timeout` on this host is a mise shim with no version (`mise ERROR No version is set for shim: timeout`), so `timeout 60 claude doctor` exited 1 without running. | Applied in-lane: `/usr/bin/perl -e 'alarm 60; exec @ARGV' claude doctor` rc 0. Proposed `dev/AGENTS.md` line in Parent edits, item 5; owner: parent. |
| P3 | Tool economy: `$PIPESTATUS` is bash; under zsh the pipe's exit is `$pipestatus[1]`, and a `claude plugin test ... | tail` printed an empty rc on the first run. | Applied: the battery writes each command's output to a file and records `$?` directly (receipts above). No doc change: `AGENTS.md` already carries the zsh gotcha. |
| P3 | No-ops: the reload is a no-op in a fresh process (it already loads current plugins); it pays off only for a pre-warmed `--bg` worker (R3 Q4), and whether `session.start` fires at pre-warm or at claim is unverified. | Kept as decided (D103). Live steps 1-3 measure the added first-prompt latency; deferred with owner: CT-80 watch (parent) records it. |

Categories with no further finding:
- Navigation: none beyond the SKILL.md rows. The plugin sits where loading.md says a project
  skills-dir plugin sits, and `hooks/log.ts` is named from `SKILL.md` and `register.ts`.
- Automated checks: none beyond the rows above; `dev/check.py` parses the plugin's JSON and the
  workflows run `check:research` and the baseline only, so the mod's own harness enters through
  the `mise.dev.toml` task (item 4), not a workflow edit.
- Coding standards: none beyond the rows above. `register.ts` holds only the engine calls and
  the `/bin/date` and `/bin/sh` calls (ADR 0008).
- Steering: none beyond the `sec-default`, held-text and budget rows and the `.claude/AGENTS.md`
  exception (item 1).
- Information access: none beyond the rows above; the 2.1.299 docs copies answered the import
  rule without a network read.

Size: 6 maintained files and 512 lines (257 of them tests), plus this record; the split in the
size row is done.

## Live acceptance (the user's restart onto 2.1.300, after integration into the root checkout)

1. In a fresh terminal: `cd /Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`,
   `unset VIRTUAL_ENV`, then `claude --debug` with no `-n`. While it starts, type a short prompt
   at once. Pass: the prompt waits; the debug log shows `$.command.run (session-start)` queued,
   then the reload summary, then the first API request; the title reads
   `ccm-<YYYYMMDDTHHMMSS.nnnnnnnnn>-05`; no `session-start` status line. Then run the four
   SKILL.md detection checks: two `fired` rows, `accepted`, `ok`, and no `title_skipped`.
   The `duration_ms` and the `ts` gap between `fired` and `reload_plugins_end` show the added
   start-up latency. Record: if a `held:` status line or row appears, its full text as the
   engine printed it (the 2.1.300 held wording), and whether it contains `--force to apply`; if
   `duration_ms` exceeds 10000 with a `reload_plugins_end` row present, the hook budget did not
   count the deadline timer.
2. `/cost` after the second reply. Pass: the prompt-cache line reports no miss.
3. `/clear`. Pass: skills reload and the title is unchanged (#67389).
4. `/quit`, then `claude -n ccm-live-check`. Pass: the title stays `ccm-live-check`.
5. In a session, `/doctor`. Pass: no organization policy. If one ever shows, step 1 must show
   whether `session.start` fired: the reload line appears, but no title.
6. Rollback if anything misbehaves: `claude plugin disable session-start@skills-dir`.

## Parent edits (exact text; outside `owned_paths`)

1. `.claude/AGENTS.md`, the `skills/` bullet, replace "each\n  mirrored under `.agents/skills/` for
   Codex; change both copies together." with:
   "each\n  mirrored under `.agents/skills/` for Codex; change both copies together. Exception:
   `session-start`, a project mod (skills-dir plugin, CT-35), has no mirror, because Codex cannot
   run mods."
2. For ct35b, `docs/adr/0007-mods-replace-settings-hooks.md` Decision: replace "The session-start
   mod names the session and runs\n`/reload-skills` and `/reload-plugins --force` before the first
   request;" with "The session-start mod awaits a plain `/reload-plugins` (never `--force`, D103)
   in `session.start` and answers `classic.SessionStart` with `reloadSkills` and, on startup
   without a title, the D61 session title;".
3. For ct35b, `docs/agents/hooks-and-mods.md`, append to the bullet ending
   "(`reloadSkills`, `sessionTitle`)." the text: " Built by CT-35 at
   `.claude/skills/session-start/` (`session-start@skills-dir`) and tested offline with `claude
   plugin test .claude/skills/session-start`. #84320 closed not_planned (stale) on 2026-10-05, so
   the race is unfixed upstream; the mod bounds its wait at 30 s. Where `sec-default` is seated
   (managed settings, Team or Enterprise), the `classic.SessionStart` half does not run
   (#102134). The running build's types come from loading the plugin-authoring skill, not from a
   fixed bundle path. A hooks module imports sibling files by relative `import` declaration and
   may not pass `$` to an imported function, so pure helpers live apart from the hooks."
4. `mise.dev.toml`, new task (record its rc in the lane's `required_checks`, too):
   ```toml
   [tasks."test:session-start-mod"]
   description = "Run the session-start mod's tests against the mocked engine (no session, model or network)"
   dir = "{{config_root}}"
   run = "claude plugin test .claude/skills/session-start"
   ```
   It exits 1 with `claude plugin test: hooks modules are turned off` where the rollout switch is
   off (#99130); record such a run as external, not as a failure of the mod.
5. `dev/AGENTS.md`, a gotcha line under "Writing a helper": "`timeout` is a mise shim with no
   version on this host; bound a command with `/usr/bin/perl -e 'alarm N; exec @ARGV' <command>`."
6. `lanes/handoff-script.json` notes, append: "next-name runs `[date_binary(), NAME_DATE_FORMAT]`
   with `NAME_DATE_FORMAT` `+%Y%m%dT%H%M%S.%N%z` and drops the last two characters of the trimmed
   output, as `.claude/skills/session-start/hooks/log.ts` `DATE_ARGV` and `parseDate` do (the mod
   always runs `/bin/date`); a test asserts `NAME_DATE_FORMAT == DATE_ARGV[1]` read from that
   file."
7. `lanes/ct35a-session-start-mod.json` `required_checks`, add `claude plugin test
   .claude/skills/session-start`.
8. For lane `handoff-skills`, in `.claude/skills/session-resume/SKILL.md` and its `.agents/skills`
   copy, a new first step after a restart: "Run the four checks in
   `.claude/skills/session-start/SKILL.md` § Detect a failure after a restart, with `SID` set to
   this session's id, and report each result: fired, reload result, `ok` or `LATE`, title. Done
   when the report names all four." The doctor detector is not this step; it is a separate later
   item (C++ core candidate, D113).
9. Live acceptance step 1 (above) records the actual 2.1.300 held text and the budget outcome;
   the parent copies the recorded line into this record's "Unconfirmed" list as confirmed or
   refuted after the user's restart.

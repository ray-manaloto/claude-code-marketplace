# gh-guard retrospective: raw gh writes refused, one scanned gh:write route, Codex rules (CT-94, D179)

Unit `gh-guard` (CT-94, R-174; D179, a dated 2026-10-14 exception to D92/D113). Worktree
`.claude/worktrees/gh-guard`, branch `claude/gh-guard`, `base_sha` `480993a`, cut from the allocation
commit `30ce28b`, so `git log 30ce28b..HEAD` is the lane. Commits: `8d8d794` (gate rule, route, task,
Codex rules, docs, seam tests), `1283302` (clean `git merge --no-edit` of the integration tip
`dc96614`), `27cae68` (implementer draft of this record), `412e21e` (the review's two P2 and one P3
applied test-first, below), then the commit carrying this record.
Writer of `8d8d794`: Claude Opus 5.5 (implementer). Cold review: reviewer (Fable 5.1, read-only),
PASS-with-findings on `27cae68`, two P2 to fix before acceptance. Retro and `412e21e`: Claude Fable
5.1 (retro-writer); the trailers on `412e21e` and this record's commit name Opus 5.5 because the
parent's brief fixed those lines, so the lane record's `writer_model` stays the implementer's.

Delivered (`8d8d794`, unchanged by the review except where `412e21e` is named):
- `dev/hooks/pretooluse_gate.py`: `gh_writes()` reads each Bash segment's tokens (env prefixes,
  `-R`/`--repo`, `&&`/`;`/`|` chains, heredoc first lines, `$(...)` and backticks, `bash -c` /
  `eval` scripts, and since `412e21e` a backslash-newline continuation) and refuses issue, pr,
  release, gist, label and repo subcommands outside a read list, `gh api` with a non-GET method or
  with `-f`/`-F`/`--field`/`--raw-field`/`--input` that imply POST, an unparsable `gh api` option,
  and `gh api graphql` with a mutation or without a readable inline query (a file, and since
  `412e21e` a `$` or backtick in the value). The reason names the form from fixed verb sets only,
  never command text, and points to `./dev/mise run gh:write -- <gh args>` and the issue tasks. The
  three existing gate rules are unchanged in behaviour except that `412e21e` closes the same
  continuation bypass for `git merge` and `git push`; the Settings pin test passes unchanged.
- `dev/gh_write.py` + task `gh:write` (no `usage` line, so free text forwards after `--`): scans
  every argument and every file or stdin an argument names (`--body-file`, `-F <file>`,
  `-F key=@file`, `--input`, inline `--opt=path`) with `issue_amend.scan()` (imported, not copied);
  a hit exits 2 as `REFUSED: secret scan hit: local id gh:write, field arg N[ file|stdin], rule
  <id>; nothing sent`; a FIFO or device path, a missing scanner or gh failing to start also exit 2.
  gh then runs with the same argv and no shell; stdin is the scanned bytes or `/dev/null`.
- `.codex/rules/gh-write.rules`: `prefix_rule(..., decision = "forbidden")` for the same leading
  prefixes, justification naming the route; `412e21e` adds the glued lowercase `-Xpost`, `-Xput`,
  `-Xpatch`, `-Xdelete`. Syntax source: https://developers.openai.com/codex/rules, webclaw mirror
  `offline/research/g1-public-text/docs/codex-rules.md` (sha256
  162f97987f31e4bee4ce61d907f19fa037995b6e55d8831400a3f7146bd22252; G1 query seq 40,
  2026-10-14T20:41:31Z); Context7 was out of credit in that run. Checked with local
  `codex execpolicy check` (codex-cli 0.162.1).
- Docs: the D179 exception and a D179 watch line in `docs/agents/hooks-and-mods.md` (the bullet
  names the unreadable-query and continuation forms since `412e21e`); `docs/agents/issue-tracker.md`
  sends comments, PR text and other gh writes to `gh:write`.
- Rule-14 markers: `dev/hooks/pretooluse_gate.py:30`, `dev/gh_write.py:10`, the `gh:write` row in
  `mise.dev.toml`.

Size: 8 maintained files, `git diff --numstat 30ce28b 8d8d794` +466/-14 (gate +107/-9, tests
+65 and +128, route +65, rules +71, docs +17/-4, mise +13/-1), above the five-file, 300-line guide;
`412e21e` adds +18/-10 over five of the same files. Disposition in GG-3.

## Exits

`VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` unset, this worktree only. Implementer logs in the parent
session's scratchpad `gh-guard/`, reviewer logs in `gh-guard-review/`, retro logs in
`gh-guard-retro/`.

Implementer, red first (`8d8d794`):
- `./dev/mise run test:hooks` rc 1, 56 failures (the refused forms) before the gate rule
  (`red-hooks.log` sha256 731aa1417b5fc842c79a8567f10d69123c38b7c239067e19a14594cd00609748).
- `./dev/mise run test:gh-write` rc 1, 9 failures before `dev/gh_write.py` existed
  (`red-gh-write.log` sha256 1810430c7896117332c5d95acbd9faef6b7cbb9a84b5248a25c3b1f8d313d49d).
- `./dev/mise run test:gh-write` rc 1, 27 failures before the rules file existed
  (`red-codex-rules.log` sha256 e94794dfeab96143a514af2586c837ca116c5dec48462dbd8cc7f936abcb5b0f).
- One gate case (`sh -c` script holding `(`) failed after the first green and drove the fix that
  normalizes only the matched command name.

Reviewer on `27cae68` (`gh-guard-review/exits.txt`): test:hooks, test:gh-write, test:issue-amend,
tasks validate, check, check:acceptance-baseline, `git diff --check`, retro:gate all rc 0; the
probe list `gh-guard-review/probe.py` (38 commands at the hook seam) found the two P2 bypasses.

Retro, red first on `27cae68` plus the new cases (`gh-guard-retro/`):
- `./dev/mise run test:hooks` rc 1: 6 failures (the two continuation forms, `query="$Q"`,
  `query="$(cat m.graphql)"`, backtick query, `-F query='$Q'`) and 1 error (`git \<newline>push`
  produced no deny, so the JSON decode of an empty output raised); `red-hooks.log` sha256
  678c20c92b57a9aee187412019a4fae6095992efa818969ef7ed7b5250789cf3.
- `./dev/mise run test:gh-write` rc 1: 2 failures (`gh api -Xpost`, `gh api -Xdelete` matched no
  rule); `red-gh-write.log` sha256 d7661fda7f4f25600793dd034cc564ecad0f0d84bff6ecce4da1176b30a6ec31.

Green on `412e21e` (the same tree the record commit carries, plus this file):
- `./dev/mise run test:hooks` rc 0 (26 tests); `./dev/mise run test:gh-write` rc 0 (5 tests, none
  skipped; `CodexRules` ran with codex-cli 0.162.1); `./dev/mise run test:issue-amend` rc 0 (26).
- `./dev/mise tasks validate` rc 0 (68 tasks); `./dev/mise run check` rc 0; `./dev/mise run
  check:acceptance-baseline` rc 0 (`"baseline": 19`); `git diff --check 30ce28b HEAD` rc 0.
- `codex execpolicy check --rules .codex/rules/gh-write.rules -- gh api -X{post,put,patch,delete}
  repos/o/r`: `forbidden` for each; `-XGET`: no rule matched.
- Pinned betterleaks 1.9.0 `git` scan, repository config, `--redact=100`,
  `--log-opts="30ce28b..HEAD --no-merges"`: rc and finding count in the hand-back (rule ids only).
- `./dev/mise run retro:gate -- gh-guard`: rc in the hand-back.

Reviewer probe list rerun on `412e21e` (`gh-guard-retro/probes-after.txt`; `deny` means the gate
printed the deny JSON, `allow` means no output, every rc 0):

| Probe | Before (27cae68) | After (412e21e) |
| --- | --- | --- |
| `command gh`, `/usr/bin/env gh`, absolute `gh`, `xargs gh`, `bash -lc`, `printf \| gh issue create -F -`, `gh issue comment --editor` | deny | deny |
| `-XPOST` glued, `--method=PATCH`, `-X post`, endpoint then `-f`, endpoint then `-X` | deny | deny |
| graphql `-F query=@file` | deny | deny |
| graphql `query="$Q"`, graphql `query="$(cat m.graphql)"` | allow (P2) | deny |
| `gh api \<nl>-X POST`, `gh \<nl>issue comment`, `gh pr create` multiline, `-XPOST \<nl>endpoint` | allow (P2; the multiline `pr create` denied by the fallback split only) | deny |
| `$GH` variable, `alias g=gh`, `gh extension install`, `gh stack submit`, `gh project item-create`, `python3 -c subprocess gh` | allow | allow (GG-1 declared gaps) |
| heredoc doc line `Run gh pr merge 4 ...`, heredoc doc line `see gh issue 12` | deny | deny (GG-7) |
| `echo gh`, `echo 'gh issue create'`, `git log -- docs/gh`, `rg 'gh issue'`, `git commit -m gh-gate`, `issue:apply`, `delivery:publish`, `high light ghq night`, the route, `gh pr view`, `gh api -X GET -f` | allow | allow |

## Findings

| Severity | Category and finding (source) | Action and verification | Disposition |
| --- | --- | --- | --- |
| P2 | GG-9 Automated checks: a backslash-newline continuation bypassed the gate because the command was split on newlines before continuations were joined; `gh api \<nl>-X POST repos/x/y/issues -f title=t` and `gh \<nl>issue comment 1 -b x` were allowed, and so was `git \<nl>push origin claude/x-y` through the retro gate's own parser. (Reviewer, P2 on `27cae68`; retro-writer for the git seam.) | `412e21e`: `CONTINUATION.sub(" ", command)` ahead of `SEGMENT.split` in both `actions()` and `gh_writes()`; the two gh forms, `gh pr create` multiline, `git \<nl>push` and `git merge \<nl>--no-ff` join the REFUSED and denied lists in `dev/test_hooks.py`. Verification: test:hooks rc 1 (6 failures, 1 error) before, rc 0 after; probe table rows 4-5. | Applied. |
| P2 | GG-10 Automated checks: a graphql query carried by a variable or substitution passed as a plain query (`-f query="$Q"`, `"$(cat m.graphql)"`, backticks), so a mutation could reach GitHub unscanned. (Reviewer, P2 on `27cae68`.) | `412e21e`: a query value holding `$` or a backtick is unreadable and refused as `gh api graphql without an inline query`; four cases in REFUSED. Verification: test:hooks red then rc 0; probe table row 4. | Applied. |
| P3 | GG-11 Automated checks: the Codex rules lacked the glued lowercase `-Xpost`, `-Xput`, `-Xpatch`, `-Xdelete`. (Reviewer, P3.) | `412e21e`: four prefixes added; `gh api -Xpost ...` and `gh api -Xdelete ...` join `CodexRules.FORBIDDEN`. Verification: test:gh-write rc 1 (2 failures) before, rc 0 after; `codex execpolicy check` reports `forbidden` for each of the four. | Applied. |
| P2 | GG-1 Information access: gh writes the gate does not see: extensions (`gh stack submit` opens PRs; the gh-stack skill), `gh alias set` aliases, `gh project` item text, `gh secret`/`variable set`, `gh workflow run`, gh named through a variable (`$GH`) or `$(which gh)`, a script file or `python3 -c` subprocess that runs gh, and text typed into `--editor` or `--web` (the route gives gh no stdin, so no prompt reads text). (Implementer; G1 audit inventory; reviewer probe rows 6.) | Outside the D179 scope. The G1 Actions backstop (recommendation 1) covers every route; the follow-up ticket under #138 decides gh-stack, extensions and each listed form together with GG-2 and GG-7. Verification: the ticket names each form. | Deferred, owner parent; admission: follow-up ticket under #138 (parent edit 3). |
| P2 | GG-2 Information access: Codex prefix rules see only the leading argv: `gh -R o/r ...`, an endpoint before `-X`, field-implied POSTs and graphql mutations pass, and a `bash -lc` script with redirection or a heredoc is not split (codex-rules.md, "When Codex does not split"). (Implementer.) | Recorded in the rules file header and the D179 bullet. Full coverage needs a Codex PreToolUse hook (G1 recommendation 4, U3). | Deferred, owner parent; admission: the U3 decision, in the same ticket under #138 (parent edit 3). |
| P3 | GG-3 Coding standards: 8 files, +466 lines against the five-file, 300-line guide. Split point: (a) gate rule, `test_hooks.py`, `hooks-and-mods.md`; (b) `gh_write.py`, `test_gh_write.py` `GhWrite`, the two mise rows, `issue-tracker.md`; (c) the rules file and the `CodexRules` class. Files over 80 handwritten lines: `pretooluse_gate.py` (190), `test_gh_write.py` (128, new), `test_hooks.py` (as before). (Implementer; reviewer disposition.) | The reviewer read the gate and both test files in full and judged the split point right but the route and the gate integrate as one: the gate's refusal names the route, so either half alone ships a refusal pointing at a missing task or a route nothing steers to. | Rejected as a split for this lane (reviewer, cold review of `27cae68`); the split point stands for a later lane of this shape. |
| P3 | GG-4 Automated checks: `CodexRules` skips without a `codex` binary, so the hosted research-fast run may skip it. Codex also validates each rule's `match`/`not_match` examples at load. (Implementer.) | Ran here, not skipped (5 tests, rc 0; codex-cli 0.162.1). | Deferred, owner parent; admission: a CI image with codex (CT-80 host checks). |
| P3 | GG-5 Information access: a test that spawns `./dev/mise` under a temporary `HOME` loses mise's config trust, so the scanner fails closed ("pinned betterleaks scanner unavailable"). `test_gh_write.py` keeps the real `HOME`, scrubs selectors, scanner config and GitHub credentials, and uses a scratch `CODEX_HOME`, a deviation from the first form in `.claude/rules/dev-tests.md`. (Implementer, one failed run.) | Parent edit 1 adds the reason to the rule. Verification: `grep -c 'mise keeps its config trust' .claude/rules/dev-tests.md` prints 1. | Deferred, owner parent; admission: parent edit 1 at integration. |
| P3 | GG-6 Coding standards: a deny reason that echoed the command would copy issue text into the hook output. The reason takes the form from fixed verb sets; an unknown subcommand reads `<subcommand outside the read list>`. (Implementer.) | `test_raw_gh_writes_are_denied_with_the_scanned_route_named` asserts `BODYTEXT` is absent from each reason; test:hooks rc 0. | Applied. |
| P3 | GG-7 Coding standards: the gate refuses an unquoted `echo gh pr merge` or a heredoc body line that starts with a gh write verb (reviewer probe rows 7), since tokens cannot tell data from a command there; quoted text passes (`git commit -m '... gh issue create'`, `grep 'gh pr merge'`). The live gate refused this retro's own edit script when a heredoc carried `git push origin claude/x-y` as data; writing the script with the Write tool and running it by path avoided it. (Implementer; reviewer; retro-writer.) | Accepted: fail-closed is the brief's rule, the reason names the route, a body goes in a file passed by `--body-file`, and the Write tool carries data lines. The cost (a refused Bash heredoc that only documents a verb) goes to the #138 follow-up with GG-1 and GG-2 to decide whether heredoc bodies after the first line are skipped. | Accepted; deferred, owner parent; admission: follow-up ticket under #138 (parent edit 3). |
| P3 | GG-12 Tool economy: the implementer's 56 refused cases missed the shell forms that reshape argv (continuation, variable, command substitution); the reviewer's 38-probe list found both P2 in one pass. (Retro-writer; `gh-guard-review/probe.py`.) | Mechanical part applied: those forms now live in `GhWriteGate.REFUSED` and `test_lane_merge_and_push_denied_until_retro_passes`, so the next gate change runs them. Judgement part: parent edit 2 adds a reviewer rule to `CODING_STANDARDS.md` naming the forms a command gate's case list carries. Verification: test:hooks rc 0; `grep -c 'reshape argv' CODING_STANDARDS.md` prints 1 after the edit. | Applied (tests); deferred, owner parent; admission: parent edit 2 at integration. |
| P3 | GG-13 Tool economy: a manual `codex execpolicy check -- $c` in zsh passed the command as one word and reported no match until `${=c}`; the suites were right. (Retro-writer.) | None: the root `AGENTS.md` already states that zsh keeps a `$t` loop variable as one word. | Rejected (already documented; transcript-only). |
| P3 | GG-8 Tool economy: one implementer test run lost to the temporary-`HOME` choice (GG-5). | No project change beyond parent edit 1. | Rejected (transcript-only). |

Navigation: none; the lane record, `docs/agents/hooks-and-mods.md`, the G1 audit, the issue-scan
retro, `dev/AGENTS.md` (free text forwards after `--` with no `usage` line) and the reviewer's
scratchpad gave every input. The lane record's `base_sha` `480993a` differs from the cut commit
`30ce28b` as its `base_rule` says.

Automated checks: `test:gh-write` joins `check:research`'s `depends` (`mise.dev.toml`), which
`.github/workflows/research-fast.yml` runs; the gate cases run in `test:hooks`, already listed
there; `development.yml` runs `dev/check.py` only, which is the standing split. GG-9, GG-10 and
GG-11 are the findings in this category; GG-4 is the unwired case.

Coding standards: GG-3, GG-6 and GG-7 above; the judgement rule from GG-12 goes to
`CODING_STANDARDS.md` through parent edit 2.

Steering and global guidance: none; no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or
`.claude/agents` file changed in the lane, `.claude/settings.json` is untouched and its pin test
passes, and the gh gate is a project hook, not a global setting.

Tool economy: GG-12, GG-13 and GG-8 above.

No-ops: none; each change has a test that failed first (the implementer's three red logs and the
retro's two).

Information access: GG-1, GG-2 and GG-5 above.

## Parent edits (outside `owned_paths`; literal)

1. `.claude/rules/dev-tests.md`, third bullet, append: ` A test that spawns ./dev/mise keeps the
   real HOME, because mise keeps its config trust there, and scrubs selectors, scanner config and
   credentials instead.`
2. `CODING_STANDARDS.md`, under `## Tests`, after rule 15, add:
   `16. A gate that reads a shell command carries, in its refused or allowed cases, each form that
   can reshape argv: a backslash-newline continuation, a variable, a command substitution, a
   nested shell or eval, a pipe and a heredoc. Reject a gate change whose case list lacks one of
   them (retro gh-guard, GG-9, GG-10, GG-12).`
3. File the follow-up ticket under #138 for GG-1, GG-2 and GG-7 (gh extensions including gh-stack,
   aliases, `$GH`, project, secret, variable and workflow writes, `python3 -c` subprocesses; Codex
   PreToolUse coverage under U3; whether heredoc body lines after the first are skipped).
4. Lane record `lanes/gh-guard.json`: `status` to the integration state the parent records, with the
   review disposition (PASS-with-findings on `27cae68`, the two P2 applied in `412e21e`).

# gh-guard retrospective: raw gh writes refused, one scanned gh:write route, Codex rules (CT-94, D179)

Unit `gh-guard` (CT-94, R-174; D179, a dated 2026-10-14 exception to D92/D113). Worktree
`.claude/worktrees/gh-guard`, branch `claude/gh-guard`, `base_sha` `480993a`, cut from the allocation
commit `30ce28b`, so `git log 30ce28b..HEAD` is the lane. Commits: `8d8d794` (gate rule, route, task,
Codex rules, docs, seam tests), `1283302` (clean `git merge --no-edit` of the integration tip
`dc96614`, message amended to add the trailers), then the commit carrying this draft.
Writer: Claude Opus 5.5 (implementer). Cold review and the final retro: not yet run (reviewer and
retro-writer are separate roles; this is the implementer draft).

Delivered:
- `dev/hooks/pretooluse_gate.py`: `gh_writes()` reads each Bash segment's tokens (env prefixes,
  `-R`/`--repo`, `&&`/`;`/`|` chains, heredoc first lines, `$(...)` and backticks, `bash -c` /
  `eval` scripts) and refuses issue, pr, release, gist, label and repo subcommands outside a read
  list, `gh api` with a non-GET method or with `-f`/`-F`/`--field`/`--raw-field`/`--input` that
  imply POST, an unparsable `gh api` option, and `gh api graphql` with a mutation or without an
  inline query. The reason names the form from fixed verb sets only, never command text, and points
  to `./dev/mise run gh:write -- <gh args>` and the issue tasks. The three existing gate rules are
  unchanged; the Settings pin test passes unchanged.
- `dev/gh_write.py` + task `gh:write` (no `usage` line, so free text forwards after `--`): scans
  every argument and every file or stdin an argument names (`--body-file`, `-F <file>`,
  `-F key=@file`, `--input`, inline `--opt=path`) with `issue_amend.scan()` (imported, not copied);
  a hit exits 2 as `REFUSED: secret scan hit: local id gh:write, field arg N[ file|stdin], rule
  <id>; nothing sent`; a FIFO or device path, a missing scanner or gh failing to start also exit 2.
  gh then runs with the same argv and no shell; stdin is the scanned bytes or `/dev/null`.
- `.codex/rules/gh-write.rules`: `prefix_rule(..., decision = "forbidden")` for the same leading
  prefixes, justification naming the route. Syntax source:
  https://developers.openai.com/codex/rules, webclaw mirror
  `offline/research/g1-public-text/docs/codex-rules.md` (sha256
  162f97987f31e4bee4ce61d907f19fa037995b6e55d8831400a3f7146bd22252; G1 query seq 40,
  2026-10-14T20:41:31Z); Context7 was out of credit in that run. Checked with local
  `codex execpolicy check` (codex-cli 0.162.1).
- Docs: the D179 exception and a D179 watch line in `docs/agents/hooks-and-mods.md`;
  `docs/agents/issue-tracker.md` sends comments, PR text and other gh writes to `gh:write`.
- Rule-14 markers: `dev/hooks/pretooluse_gate.py:29`, `dev/gh_write.py:10`, the `gh:write` row in
  `mise.dev.toml`.

Size: 8 maintained files, `git diff --numstat 30ce28b 8d8d794` +466/-14 (gate +107/-9, tests
+65 and +128, route +65, rules +71, docs +17/-4, mise +13/-1), above the five-file, 300-line guide;
see GG-3 for the split point.

## Exits

`VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` unset, this worktree only; logs in the parent session's
scratchpad `gh-guard/`.

Red first:
- `./dev/mise run test:hooks` rc 1, 56 failures (the refused forms) before the gate rule
  (`red-hooks.log` sha256 731aa1417b5fc842c79a8567f10d69123c38b7c239067e19a14594cd00609748).
- `./dev/mise run test:gh-write` rc 1, 9 failures before `dev/gh_write.py` existed
  (`red-gh-write.log` sha256 1810430c7896117332c5d95acbd9faef6b7cbb9a84b5248a25c3b1f8d313d49d).
- `./dev/mise run test:gh-write` rc 1, 27 failures before the rules file existed
  (`red-codex-rules.log` sha256 e94794dfeab96143a514af2586c837ca116c5dec48462dbd8cc7f936abcb5b0f).
- One gate case (`sh -c` script holding `(`) failed after the first green and drove the fix that
  normalizes only the matched command name.
- The pinned betterleaks over the red logs: 0 findings.

On the merged bytes `1283302`:
- `./dev/mise run test:hooks` rc 0 (26 tests); `./dev/mise run test:gh-write` rc 0 (5 tests, none
  skipped); `./dev/mise run test:issue-amend` rc 0 (26 tests).
- `./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0; `./dev/mise run
  check:acceptance-baseline` rc 0; `git diff --check 30ce28b HEAD` rc 0.
- Pinned betterleaks 1.9.0 `git` scan, repository config, `--redact=100`,
  `--log-opts="30ce28b..HEAD --no-merges"`: rc 0, 0 findings.
- `./dev/mise run retro:gate -- gh-guard`: rc on this record in the hand-back.

## Findings

| Severity | Category and finding (source) | Action and verification | Disposition |
| --- | --- | --- | --- |
| P2 | GG-1 Information access: gh writes the gate does not see: extensions (`gh stack submit` opens PRs; the gh-stack skill), `gh alias set` aliases, `gh project` item text, `gh secret`/`variable set`, `gh workflow run`, gh named through a variable or `$(which gh)`, a script file that runs gh, and text typed into `--editor` or `--web` (the route gives gh no stdin, so no prompt reads text). (Implementer; G1 audit inventory.) | Outside the D179 scope. The G1 Actions backstop (recommendation 1) covers every route; a follow-up ticket under #138 decides gh-stack and extensions. Verification: the ticket names each form. | Deferred, owner parent; admission: follow-up ticket under #138. |
| P2 | GG-2 Information access: Codex prefix rules see only the leading argv: `gh -R o/r ...`, an endpoint before `-X`, field-implied POSTs and graphql mutations pass, and a `bash -lc` script with redirection or a heredoc is not split (codex-rules.md, "When Codex does not split"). (Implementer.) | Recorded in the rules file header and the D179 bullet. Full coverage needs a Codex PreToolUse hook (G1 recommendation 4, U3). | Deferred, owner parent; admission: the U3 decision (#138). |
| P3 | GG-3 Coding standards: 8 files, +466 lines against the five-file, 300-line guide. Split point: (a) gate rule, `test_hooks.py`, `hooks-and-mods.md`; (b) `gh_write.py`, `test_gh_write.py` `GhWrite`, the two mise rows, `issue-tracker.md`; (c) the rules file and the `CodexRules` class. Files over 80 handwritten lines: `pretooluse_gate.py` (189), `test_gh_write.py` (128, new), `test_hooks.py` (as before). (Implementer.) | The lane record allocated all eight paths as one unit; the reviewer reads the gate and both test files in full. | Deferred, owner reviewer; admission: cold review. |
| P3 | GG-4 Automated checks: `CodexRules` skips without a `codex` binary, so the hosted research-fast run may skip it. Codex also validates each rule's `match`/`not_match` examples at load. (Implementer.) | Ran here, not skipped (5 tests, rc 0). | Deferred, owner parent; admission: a CI image with codex (CT-80 host checks). |
| P3 | GG-5 Information access: a test that spawns `./dev/mise` under a temporary `HOME` loses mise's config trust, so the scanner fails closed ("pinned betterleaks scanner unavailable"). `test_gh_write.py` keeps the real `HOME`, scrubs selectors, scanner config and GitHub credentials, and uses a scratch `CODEX_HOME`, the second form in `.claude/rules/dev-tests.md`. (Implementer, one failed run.) | Parent edit 1 adds the reason to the rule. Verification: `grep -c 'mise keeps its config trust' .claude/rules/dev-tests.md` prints 1. | Deferred, owner parent; admission: parent edit 1 at integration. |
| P3 | GG-6 Coding standards: a deny reason that echoed the command would copy issue text into the hook output. The reason takes the form from fixed verb sets; an unknown subcommand reads `<subcommand outside the read list>`. (Implementer.) | `test_raw_gh_writes_are_denied_with_the_scanned_route_named` asserts `BODYTEXT` is absent from each reason; test:hooks rc 0. | Applied. |
| P3 | GG-7 Coding standards: the gate refuses an unquoted `echo gh pr merge` or a heredoc body line that starts with a gh write, since tokens cannot tell data from a command there. Quoted text passes (`git commit -m '... gh issue create'`, `grep 'gh pr merge'` are allowed cases). (Implementer.) | The brief's rule is "when unsure, refuse"; the reason names the route, and a body goes in a file passed by `--body-file`. | Rejected (intended fail-closed behaviour, covered by tests). |
| P3 | GG-8 Tool economy: one test run lost to the temporary-`HOME` choice (GG-5). | No project change beyond parent edit 1. | Rejected (transcript-only). |

Navigation: none; the lane record, `docs/agents/hooks-and-mods.md`, the G1 audit, the issue-scan
retro and `dev/AGENTS.md` (free text forwards after `--` with no `usage` line) gave every input.
The lane record's `base_sha` `480993a` differs from the cut commit `30ce28b` as its `base_rule` says.

Automated checks: `test:gh-write` joins `check:research`'s `depends` (`mise.dev.toml`), which
`.github/workflows/research-fast.yml` runs; the gate cases run in `test:hooks`, already listed.

Steering and global guidance: no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or `.claude/agents` file
changed in the lane; `.claude/settings.json` is untouched and its pin test passes.

No-ops: none; each change has a test that failed first (red logs above).

## Parent edits (outside `owned_paths`; literal)

1. `.claude/rules/dev-tests.md`, third bullet, append: ` A test that spawns ./dev/mise keeps the
   real HOME, because mise keeps its config trust there, and scrubs selectors, scanner config and
   credentials instead.`
2. File the follow-up ticket under #138 for GG-1 and GG-2 (gh extensions including gh-stack, aliases,
   project, secret and workflow writes; Codex PreToolUse coverage under U3).

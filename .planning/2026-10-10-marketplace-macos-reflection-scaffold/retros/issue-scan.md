# issue-scan retrospective: the issue route scans outbound text before any GitHub request (R-174, CT-92)

Unit `issue-scan` (CT-92 lane part, R-174; D171, D145; a D113 fix to existing Python). Worktree
`.claude/worktrees/issue-scan`, branch `claude/issue-scan`, `base_sha` `53d7b03`, cut from the
allocation commit `f635966`, so `git log f635966..HEAD` is the lane. Commits: `e41d3d2` (scan and
seam tests), `beb0b26` (clean `git merge --no-edit` of the integration tip `71dbb6b`), `e996067`
(allow-comment case, subtest labels, constant marker), then the commit carrying this draft. Writer:
Claude Opus 5.5 (implementer). Independent review and the retro-writer pass have not run yet; this
is the implementer's draft.

Delivered: `dev/issue_amend.py` gains `scanner()` (the `mise.dev.toml` betterleaks pin resolved by
`dev/mise which`, version checked against `betterleaks version`, never a PATH lookup) and `scan()`
(writes each outbound field to a private temp dir, runs `betterleaks dir` once with the repository
`.gitleaks.toml`, `--redact=100`, `--ignore-gitleaks-allow`, an empty ignore file and the scanner
config variables dropped, then maps findings back to fields). A hit raises one line per hit,
`secret scan hit: local id <id>, field <field>, rule <rule id>; nothing sent`; the CLI prints each as
`REFUSED: ...` and exits 2. A missing or wrong-version scanner, a malformed report or an rc that
disagrees with the report refuses. Call sites: `dev/issue_create.py:58` (`outbound()`, used by
preview at `:159` and apply at `:222`, which builds the exact POST payload before `inventory()`),
`dev/issue_amend.py:226` (preview, before `fetch()`) and `:273` (apply of a v1 body/labels intent,
before `fetch()`). Size: 4 maintained files, `git diff --numstat f635966 HEAD`: `issue_amend.py`
+65/-1, `issue_create.py` +10/-4, `test_issue_amend.py` +70/-1, `test_issue_create.py` +133/-0.

Exits, `VIRTUAL_ENV` unset, this worktree only, on `e996067` (merged bytes; logs under the session
scratchpad `final/`):
- Red first: `./dev/mise run test:issue-create` rc 1 before the scan existed (6 failures, 1 error;
  log sha256 021abea227984db3b025f76b993faca553fbe2d5461f20de9b24f7b5a8fbad2f);
  `./dev/mise run test:issue-amend` rc 1 (6 failures; 8beef984e90288c861faf345dc9d5bce5e910588ec72278853728a40cec87e02);
  the allow-comment case rc 1 with `--ignore-gitleaks-allow` removed (1 failure, case 3;
  7b24480a5ceb8418e804a30a6732c9690e6381425d14031c49f18d452f632b60).
- `./dev/mise run test:issue-create` rc 0 (24 tests); `./dev/mise run test:issue-amend` rc 0
  (26 tests); `./dev/mise run test:issue-new-edges` rc 0 (15 tests, imports both modules).
- `./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0; `./dev/mise run
  check:acceptance-baseline` rc 0; `git diff --check f635966 HEAD` rc 0.
- Pinned betterleaks 1.9.0 `git` scan of the lane's non-merge commits (`--log-opts="f635966..HEAD
  --no-merges"`, repository config, `--redact=100`) rc 0.
- The committed manifest `dev/issue-tickets.json` (17 tickets) passes `outbound()`: 0 refused.
- `./dev/mise run retro:gate -- issue-scan`: rc in the hand-back.

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P1 | IS-1 Information access: issue comments have no qualified route. `docs/agents/issue-tracker.md:52-55` forbids `gh issue create` and `gh issue edit` but not `gh issue comment` or `gh api` writes, so an agent can still send unscanned text to a public issue; the deny gates in `dev/hooks/` do not inspect `gh`. (Implementer, grep of `docs`, `.claude`, `.agents`, `dev`.) | Outside `owned_paths`. Parent edit 1 (docs sentence) and parent edit 2 (a deny-gate ticket). Verification for edit 1: `grep -c 'gh issue comment' docs/agents/issue-tracker.md` prints 1. | Deferred, owner parent; admission condition: parent edits 1 and 2 at integration. |
| P2 | IS-2 Coding standards: a subtest label first carried `text[-9:]`, which printed a 9-character tail of the derived private-name sample into one scratch log and this session's transcript (never into a committed file). (Implementer.) | `e996067`: subtests are labelled by case index with a comment that fixture text never labels a subtest; the log was deleted; every remaining lane log shares at most 5 characters with the sample (measured in-process, only lengths printed). | Applied. |
| P2 | IS-3 Coding standards: an inline `gitleaks:allow` or `betterleaks:allow` in issue text suppresses a finding unless the scanner runs with `--ignore-gitleaks-allow`. (Implementer, `betterleaks dir --help`.) | Flag present in `scan()`; preview case 3 fails without it (red log above) and passes with it, `test:issue-create` rc 0. | Applied. |
| P3 | IS-4 Navigation: the brief said a fresh worktree needs only `./dev/mise install`; every `test:*` task also needs the Python environment (`deps:check` refused, "environment is outdated"). `UV_OFFLINE=1 ./dev/mise run deps:sync` filled it from the uv cache with no download. (Implementer.) | Parent edit 3 adds the step to `.claude/agents/implementer.md`. Verification: `grep -c 'deps:sync' .claude/agents/implementer.md` prints at least 1. | Deferred, owner parent; admission condition: parent edit 3 at integration. |
| P3 | IS-5 Automated checks: the scan adds about 0.5 s per process (`dev/mise which`); `test:issue-create` rose from 0.14 s to 2.8 s. `scanner()` caches a successful resolution per process and never caches a refusal. | No change needed: the issue route runs one preview or apply per process. | Rejected (cost measured, acceptable). |
| P3 | IS-6 Coding standards: the private-name fixture derives its sample from the real rule through `re._parser` (private standard-library API). A Python release that moves it fails the test loudly (ImportError or the "unsupported regex token" assertion), never silently. | The approach keeps the real `.gitleaks.toml` in the production path with no test config and no committed private value (D145). | Rejected (accepted trade-off). |
| P3 | IS-7 Tool economy: two calls lost (an unquoted zsh glob `--include=*.py`; a fixture output named `labels.json` collided with the labels input file). | No project change: shell slips are host configuration (retro a09-hook-events). | Rejected (transcript-only). |

Completion closures (`issue:completion-preview`, v2 apply) PATCH only `state` and `state_reason`
and `issue:new-edge-apply` sends only an issue id, so neither is scanned; both were read at
`dev/issue_amend.py` and `dev/issue_edges.py:252`.

No-ops: none. Each code change has a test that failed first (red logs above).

Steering and global guidance: no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or `.claude/agents` file
changed in the lane; the role-file and tracker sentences are parent edits 1 and 3.

Information access: the tests read no network, provider or `~/.codex`; the scanner runs on local
temp files with validation off by default.

## Parent edits (outside `owned_paths`; literal, apply unread)

1. `docs/agents/issue-tracker.md` line 54-55: replace "Never call `gh issue create` or `gh issue
   edit` directly." with "Never call `gh issue create`, `gh issue edit`, `gh issue comment` or a
   writing `gh api` request directly: only the qualified tasks scan outbound text (R-174)."
2. File a ticket (owner parent): a deny gate refuses `gh issue create|edit|comment` and
   `gh api -X POST|PATCH .../issues...`, or a qualified comment task reuses `issue_amend.scan()`.
3. `.claude/agents/implementer.md`, after the worktree verification step: "In a fresh worktree run
   `./dev/mise install`, then `UV_OFFLINE=1 ./dev/mise run deps:sync` (the uv cache, no download)."

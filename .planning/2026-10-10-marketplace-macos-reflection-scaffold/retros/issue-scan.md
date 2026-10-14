# issue-scan retrospective: the issue route scans outbound text before any GitHub request (R-174, CT-92)

Unit `issue-scan` (CT-92 lane part, R-174; D171, D145; a D113 fix to existing Python). Worktree
`.claude/worktrees/issue-scan`, branch `claude/issue-scan`, `base_sha` `53d7b03`, cut from the
allocation commit `f635966`, so `git log f635966..HEAD` is the lane. Commits: `e41d3d2` (scan and
seam tests), `beb0b26` (clean `git merge --no-edit` of the integration tip `71dbb6b`), `e996067`
(allow-comment case, subtest labels, constant marker), `6088eb5` (implementer draft of this record),
`8ef1c10` (retro fix: no-leak assertions in the bool form), then the commit carrying this record.
Writer: Claude Opus 5.5 (implementer). Cold review: Fable, PASS with one P3, on `6088eb5`.
Retro-writer: Fable; this record supersedes the implementer's draft and binds `8ef1c10`.
Digest: the parent's brief (review findings and implementer process notes); no transcript path was
handed over, so the two process notes are cited to the implementer.

Delivered: `dev/issue_amend.py` gains `scanner()` (the `mise.dev.toml` betterleaks pin resolved by
`dev/mise which`, version checked against `betterleaks version`, never a PATH lookup) and `scan()`
(writes each outbound field to a private temp dir, runs `betterleaks dir` once with the repository
`.gitleaks.toml`, `--redact=100`, `--ignore-gitleaks-allow`, an empty ignore file and the scanner
config variables dropped, then maps findings back to fields). A hit raises one line per hit,
`secret scan hit: local id <id>, field <field>, rule <rule id>; nothing sent`; the CLI prints each as
`REFUSED: ...` and exits 2. A missing or wrong-version scanner, a malformed report or an rc that
disagrees with the report refuses. Call sites: `dev/issue_create.py:56` (`outbound()`, used by
preview at `:159` and apply at `:222`, which builds the exact POST payload before `inventory()`),
`dev/issue_amend.py:226` (preview, before `fetch()`) and `:273` (apply of a v1 body/labels intent,
before `fetch()`). Size: 4 maintained files, `git diff --numstat f635966 8ef1c10`: `issue_amend.py`
+65/-1, `issue_create.py` +10/-4, `test_issue_amend.py` +72/-1, `test_issue_create.py` +135/-0.

## Exits

`VIRTUAL_ENV` and `UV_PROJECT_ENVIRONMENT` unset, this worktree only.

Implementer, on `e996067` (logs under that session's scratchpad `final/`):
- Red first: `./dev/mise run test:issue-create` rc 1 before the scan existed (6 failures, 1 error;
  log sha256 021abea227984db3b025f76b993faca553fbe2d5461f20de9b24f7b5a8fbad2f);
  `./dev/mise run test:issue-amend` rc 1 (6 failures; 8beef984e90288c861faf345dc9d5bce5e910588ec72278853728a40cec87e02);
  the allow-comment case rc 1 with `--ignore-gitleaks-allow` removed (1 failure, case 3;
  7b24480a5ceb8418e804a30a6732c9690e6381425d14031c49f18d452f632b60).
- The committed manifest `dev/issue-tickets.json` (17 tickets) passes `outbound()`: 0 refused.

Retro-writer, on `8ef1c10`:
- `./dev/mise run test:issue-create` rc 0 (24 tests); `./dev/mise run test:issue-amend` rc 0
  (26 tests); `./dev/mise run test:issue-new-edges` rc 0 (15 tests, imports both modules).
- `./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0; `./dev/mise run
  check:acceptance-baseline` rc 0; `git diff --check f635966 HEAD` rc 0.
- Pinned betterleaks 1.9.0 (`./dev/mise which betterleaks`) `git` scan, repository config,
  `--redact=100`, `--log-opts="f635966..HEAD --no-merges"`: rc 0, 0 findings, no rule ids.
- Bool-form proof: a scratch `unittest` case with a dummy string (not the sample) fails as
  `True is not false : fixture text leaked into the refusal`; the operand is absent from the message.
- `./dev/mise run retro:gate -- issue-scan`: rc 0 on this record (hand-back carries the final SHA).

## Findings

| Severity | Category and finding (source) | Action and verification | Disposition |
| --- | --- | --- | --- |
| P3 | IS-1 Information access: issue comments and PR text have no scanned route. `docs/agents/issue-tracker.md:54-55` forbids raw `gh issue create` and `gh issue edit` but not `gh issue comment`, `gh pr create\|edit\|comment` or a writing `gh api` call, and no hook under `dev/hooks/`, no `hk.pkl` step and no `.claude/settings.json` entry inspects `gh` (grep, this retro). (Implementer; review, deferred as IS-1.) | Outside `owned_paths`. Parent edit 1 (tracker sentence) now; the route itself belongs to the running public-text guard audit (G1, R-174 #138) and a follow-up ticket the parent files. Verification for edit 1: `grep -c 'gh issue comment' docs/agents/issue-tracker.md` prints 1. | Deferred, owner parent; admission: parent edit 1 at integration, follow-up ticket filed under #138. |
| P3 | IS-2 Coding standards: `assertNotIn(text, ...)` at `test_issue_create.py:420,442` and `test_issue_amend.py:179,197` would echo the derived private-name sample in its failure message, and each ran after an `assertEqual` over the same message, which would echo first on a leaking regression. (Review, P3; D145.) | `8ef1c10`: every assertion over output that may carry a sample is `assertFalse(sample in output, "fixture text leaked into ...")` and runs before the equality over that output; the two CLI tests add the same check over captured stderr; request-body lists compare by `len()`. `test:issue-create` rc 0, `test:issue-amend` rc 0; bool-form proof above. | Applied. |
| P3 | IS-3 Coding standards: a subtest label first carried `text[-9:]`, which printed a 9-character tail of the derived sample into one scratch log and the implementer's transcript, never a committed file. (Implementer.) | `e996067`: subtests are labelled by case index and field; the log was deleted; the lane's betterleaks scan above reports 0 findings. Prevention is a rule line for `.claude/rules/dev-tests.md` (parent edit 2, outside `owned_paths`): assertions and labels over a derived sample take a form whose failure output cannot carry it. Verification: `grep -c 'derived sample' .claude/rules/dev-tests.md` prints 1. | Applied in-lane; the rule line is deferred, owner parent; admission: parent edit 2 at integration. |
| P2 | IS-4 Coding standards: an inline `gitleaks:allow` or `betterleaks:allow` in issue text suppresses a finding unless the scanner runs with `--ignore-gitleaks-allow`. (Implementer, `betterleaks dir --help`.) | Flag present in `scan()`; preview case 3 fails without it (red log above) and passes with it, `test:issue-create` rc 0. | Applied. |
| P3 | IS-5 Navigation: the brief said a fresh worktree needs only `./dev/mise install`; every `test:*` task also needs the Python environment (`deps:check` refused, "environment is outdated"). `UV_OFFLINE=1 ./dev/mise run deps:sync` filled it from the uv cache with no download. (Implementer.) | Parent edit 3 adds the step to `.claude/agents/implementer.md` step 1. Verification: `grep -c 'deps:sync' .claude/agents/implementer.md` prints 1. | Deferred, owner parent; admission: parent edit 3 at integration. |
| P3 | IS-6 Automated checks: the scan adds about 0.5 s per process (`dev/mise which`); `test:issue-create` rose from 0.14 s to 3.2 s. `scanner()` caches a successful resolution per process and never caches a refusal. (Implementer; retro timing.) | No change: the issue route runs one preview or apply per process, and the suite stays under `check:research`'s budget. | Rejected (cost measured, acceptable). |
| P3 | IS-7 Coding standards: the private-name fixture derives its sample from the real rule through `re._parser` (private standard-library API). A Python release that moves it fails the test loudly (ImportError or the "unsupported regex token" assertion), never silently. (Implementer.) | The approach keeps the real `.gitleaks.toml` in the production path with no test config and no committed private value (D145), the property `.claude/rules/secret-scanner.md` names. | Rejected (accepted trade-off). |
| P3 | IS-8 Tool economy: two implementer calls lost (an unquoted zsh glob `--include=*.py`; a fixture output named `labels.json` collided with the labels input file). (Implementer.) | No project change: shell slips are host configuration (retro a09-hook-events). | Rejected (transcript-only). |

Automated checks: `test:issue-create`, `test:issue-amend` and `test:issue-new-edges` are named
tasks in `check:research`'s `depends` (`mise.dev.toml:118`), which `.github/workflows/research-fast.yml:49`
runs, so the seam tests reach CI with no new wiring; `dev/check.py` discovers only
`test_research_*.py` by design (`.claude/rules/dev-tests.md`). No guardrail is proposed beyond IS-1.

Completion closures (`issue:completion-preview`, v2 apply) PATCH only `state` and `state_reason`
and `issue:new-edge-apply` sends only an issue id, so neither is scanned; both were read at
`dev/issue_amend.py` and `dev/issue_edges.py:252`.

No-ops: none. Each code change has a test that failed first (red logs above), and the retro fix
changes failure output, proven with the dummy-string case.

Steering and global guidance: no `AGENTS.md`, `CLAUDE.md`, `.claude/rules` or `.claude/agents` file
changed in the lane; the tracker sentence, the test rule and the role step are parent edits 1-3.

Information access: the tests read no network, provider or `~/.codex`; the scanner runs on local
temp files with validation off by default. IS-1 names the unscanned public-text paths.

## Parent edits (outside `owned_paths`; literal, apply unread)

1. `docs/agents/issue-tracker.md` lines 54-55: replace

   ```
     `issue:preview`, `issue:apply`, `issue:verify`. Never call `gh issue create` or
     `gh issue edit` directly.
   ```

   with

   ```
     `issue:preview`, `issue:apply`, `issue:verify`. Never call `gh issue create`,
     `gh issue edit`, `gh issue comment`, `gh pr create|edit|comment` or a writing `gh api`
     call directly: only those tasks run the secret and private-name scan on outbound
     text first (R-174); a comment or PR body waits for its scanned route (#138).
   ```

2. `.claude/rules/dev-tests.md`, append one bullet:

   ```
   - A test over a derived sample (a secret or private-name fixture built at run time) checks leakage as `self.assertFalse(sample in output, "fixture text leaked into ...")` before any equality over that output, compares request-body lists by `len()`, and labels subtests by case index: those forms keep the sample out of every failure message, log and transcript (D145).
   ```

3. `.claude/agents/implementer.md`, step 1, after "and you can name the `owned_paths` you will edit.":

   ```
    In a fresh worktree run `./dev/mise install`, then `UV_OFFLINE=1 ./dev/mise run deps:sync` (the uv cache, no download); every `test:*` task needs that environment.
   ```

4. File the follow-up ticket under #138 (owner parent): a scanned route for `gh issue comment`,
   `gh pr create|edit|comment` and writing `gh api` calls that reuses `issue_amend.scan()`, or a
   deny gate that refuses the raw commands; the G1 audit's inventory supplies the path list.

# rule-split retrospective: the private-name rule leaves the tracked scanner config (D178 part 1)

Unit: `rule-split` (D178 part 1; D144, D145). Worktree `.claude/worktrees/rule-split`, branch
`claude/rule-split`, cut from allocation commit `dc96614` on base `87638e0`. Lane commit `34f86db`
(resolver, tests, config, rule doc); integration tip `94d32c4` merged clean in `b10e208` (message
amended to carry the trailers and to leave the lane branch name out). Writer: implementer (opus).
Cold review of `1d65cd0`: PASS with findings, no fail-open path found; one P2 (this draft's parent
edit 1) and five P3s, applied in the follow-up below. Follow-up: integration tip `38d1cc3` (gh-guard
integrated in `94e5445`; its lane record adds `dev/test_gh_write.py` to this lane's `owned_paths`)
merged clean with `git merge --no-ff` in `60dc227`; fixes in `d4e4299`; rule doc and this record in
the commit after it. Retro-writer: pending; this is the implementer's draft.

Delivered (all in `owned_paths`):
- The `[[rules]]` block with id `private-tr-project` moved byte-identical (8 lines, rule and its
  allowlist) from `.gitleaks.toml` into
  `~/.local/state/claude-code-marketplace/private-notes/scanner/private-rules.toml` (directory 0700,
  file 0600) by a script that printed only counts; committed in the private-notes repo (no remote,
  `git remote | wc -l` = 0) as `f280535`. The repo's three untracked archive bundles were left alone.
- The tracked `.gitleaks.toml` keeps `[extend] useDefault = true` and `aws-access-key-id`;
  `betterleaks config check` rc 0, 464 rules (465 before; the combined config also checks rc 0 at 465).
  Header comment reworded to point at the new home, no value.
- `scan_config(tracked, refusal=Refusal)` in `dev/git_delivery.py`: path from
  `MARKETPLACE_PRIVATE_RULES`, else `PRIVATE_RULES_DEFAULT`; reads the tracked config and the private
  file, requires a `[[rules]]` entry with the id, writes both into `combined.toml` (0600) inside a
  `mkdtemp` directory (0700), yields its path, deletes it. A missing, unreadable, non-TOML or wrong-id
  file raises the caller's refusal naming the variable, the default path and the id, never a value.
  A09 `scan()` (staged and outbound) and `issue_amend.scan()` use it; `scan(local_id, fields)` keeps its
  signature (lane gh-guard imports it). Exit 2 comes from each CLI's existing refusal path.
  After review (`d4e4299`): the tracked config is read first and an unreadable one refuses by its own
  path; a relative `MARKETPLACE_PRIVATE_RULES` refuses ("must be an absolute path"); a symlinked
  private file, or one with any group or other mode bit, refuses ("mode must be 0600"); the id must be
  present in the private text and again in the combined text (a private `[extend]` table or duplicate
  key fails the combined parse). `dev/test_gh_write.py` `setUp` calls `use_synthetic_private_rule`.
- `.claude/rules/secret-scanner.md` points to the new home, the resolver, the synthetic test rule and
  the CI gap; its `paths` now include the two helpers.

Receipts (worktree, VIRTUAL_ENV unset, one literal command each):
- Red first, A09 seam (`34f86db` minus the resolver; constants only): `./dev/mise run test:delivery`
  rc 1, 7 failures: publish succeeded on the synthetic private-name commit (`0 != 2`), succeeded with
  a missing private file (then `HEAD drift` for the later subtests), the config was the root file, and
  the tracked config still held the id. Green after `scan_config`, then after the move: rc 0, 26 tests.
- Red first, issue seams: `test:issue-create` rc 1 (6 failures) and `test:issue-amend` rc 1
  (5 failures), each "Refusal not raised" for the synthetic name or the unusable file; green after the
  wiring: rc 0 (25 tests) and rc 0 (27 tests).
- Real A09 publish in a scratch repo (`scratchpad/verify/a09_real.py`), real pinned betterleaks 1.9.0,
  `MARKETPLACE_PRIVATE_RULES` unset so the real default file loaded: (a) a commit adding the synthetic
  name: publish rc 0, pushed to the scratch bare remote, `history_scan_rc` present; (b) a commit adding a
  string derived in memory from the real rule (never printed; the scratch repo was a deleted temp dir):
  publish rc 2, reason "secret scan found potential leaks" (the staged scan), nothing pushed, sample
  absent from stdout and stderr.
- Leak counts (`scratchpad/verify/leak_counts.py`, counts only, `git cat-file --batch` over every
  tracked blob): lane tip `34f86db`: 8775 files, 4 alternatives checked, 0 files with the regex text, 0
  with an alternative's text, 0 with a match. Control on `dc96614`: 1, 1, 0 (the old `.gitleaks.toml`).
- `git grep -n -e private-tr-project HEAD -- ':!.planning'`: two lines, `dev/git_delivery.py:30`
  (the resolver's id) and `.claude/rules/secret-scanner.md:7`. Seven `.planning/` record files name
  the id (lane records, retros, research reports), outside `owned_paths`.
- Follow-up, on `d4e4299` (merged bytes of `38d1cc3`), one literal command each: `./dev/mise run
  test:delivery` rc 0 (29 tests; red first rc 1, 7 failures, one per new refusal); `./dev/mise run
  test:issue-create` rc 0 (25); `./dev/mise run test:issue-amend` rc 0 (27); `HOME=<empty temp dir>
  ./dev/mise run test:gh-write` rc 0 (5); `./dev/mise run test:hooks` rc 0 (27); `./dev/mise tasks
  validate` rc 0; `./dev/mise run check` rc 0; `./dev/mise run check:acceptance-baseline` rc 0;
  `./dev/mise run check:research` rc 0; `git diff --check 38d1cc3` rc 0. Leak counts on `d4e4299`:
  8783 files, 4 alternatives, 0, 0, 0. Real-file A09 rerun: synthetic commit rc 0; derived commit
  rc 2 (staged-scan refusal, nothing pushed, sample absent from output).
- On merged bytes `b10e208`: `./dev/mise run test:delivery` rc 0 (26 tests); `./dev/mise run
  test:issue-create` rc 0 (25); `./dev/mise run test:issue-amend` rc 0 (27); `./dev/mise tasks
  validate` rc 0; `./dev/mise run check` rc 0 (`status: pass`); `./dev/mise run
  check:acceptance-baseline` rc 0; `git diff --check dc96614 HEAD` rc 0.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks (writer): hosted CI has no private rule file, so a hosted scan through `scan_config` refuses (fail closed) until the D180 Actions secret lands. Today no workflow runs a scan (`grep -rn -i leaks .github` prints nothing) and every test supplies the synthetic rule, so CI stays green. | Deferred, owner parent; admission condition: D180 writes the secret to a runner file and sets `MARKETPLACE_PRIVATE_RULES`; verify with a hosted run's rc. Recorded in `.claude/rules/secret-scanner.md`. |
| P2 | Steering/global guidance (writer; review P2): lane gh-guard's `dev/test_gh_write.py` calls `issue_amend.scan`; its tests read the real default private file (a dev host) or refuse (CI). | Applied in-lane in `d4e4299` (the parent added the file to `owned_paths` at `38d1cc3`): `setUp` calls `use_synthetic_private_rule`; private hits assert `git_delivery.PRIVATE_RULE_ID`, the sample is `SYNTHETIC_PRIVATE_NAME` through `private_name_sample()`. Red first on `60dc227`: `test:gh-write` rc 1 (the synthetic name passed the real rule). Green: `HOME=<empty temp dir> ./dev/mise run test:gh-write` rc 0, 5 tests, so the real default path was unreachable. |
| P3 | Automated checks (review a): `scan_config` read the tracked config inside the private-rule `try`, so a missing tracked `.gitleaks.toml` was reported as a `MARKETPLACE_PRIVATE_RULES` problem. | Applied in `d4e4299`; seam test `test_publish_refuses_without_the_tracked_config` (missing file, directory): rc 2, reason names `tracked scanner config` and `.gitleaks.toml`, not the variable. Red first: reason blamed the variable. |
| P3 | Automated checks (review b): a private file with its own `[extend]` table or a duplicate key passed the id check alone but broke the combined config. | Applied in `d4e4299`: the id is re-checked in the parsed combined text, same refusal. Seam case 3 of `test_publish_refuses_without_a_usable_private_rule_file`; red first: publish rc 0. |
| P3 | Automated checks (review c): a symlinked or group/other-readable private file was accepted. | Applied in `d4e4299`: `lstat`, refuse `S_ISLNK` or `st_mode & 0o077` ("mode must be 0600"); `synthetic_private_rules` now writes 0600. Seam test `test_publish_refuses_a_private_rule_file_others_can_read_or_a_symlink` (0644 file, symlink to a 0600 file); red first: publish rc 0. The real file passes (A09 real-file rerun below). |
| P3 | Automated checks (review d): a relative `MARKETPLACE_PRIVATE_RULES` resolved against the caller's cwd. | Applied in `d4e4299`; seam test `test_publish_refuses_a_relative_private_rule_path` (a valid 0600 file named relatively): rc 2, reason names the variable and "absolute". Red first: publish rc 0. |
| P3 | Automated checks (review e): the unreadable case used `chmod(0)`, which root reads anyway. | Applied in `d4e4299`: the unreadable source is a 0700 directory, unreadable as a file for any user. |
| P3 | Steering/global guidance (writer): `.claude/rules/dev-tests.md` (last bullet) still describes a private-name fixture "built at run time", and both `handoff-template.md` copies say `.gitleaks.toml` guards A09 publish; both are outside `owned_paths`. | Deferred, owner parent; edits 2 and 3 below. |
| P3 | Coding standards (writer): the resolver lives in `dev/git_delivery.py` and `dev/issue_amend.py` imports it, because a new shared module is outside `owned_paths`; the issue `scan` body is re-indented under the resolver's `with` (about 20 lines of diff). | Kept: one resolver, every entry point (the brief's requirement); a port into the C++ core follows ADR 0008 when the scanner bridge exists. Verified by the three suites above. |
| P3 | Coding standards (writer, unit size): 7 maintained files, 207 insertions and 82 deletions in `34f86db`, over the five-file guide; `d4e4299` adds `dev/test_gh_write.py` (8 files). | Kept as one unit: the move and every seam's switch must land together, or a route either loses the rule or refuses. No split point. |
| P3 | Information access (writer): the seven `.planning/` files that name the id hold the id only (leak counts above: 0 regex text, 0 alternatives, 0 matches). | Rejected as a change, with reason: the id is the resolver's public contract (it appears in refusals and the rule doc); only its regex is private. |

Navigation: none; the lane record named every seam, file and check, and `.claude/rules/secret-scanner.md`
loaded on the first `.gitleaks.toml` read. Tool economy: two findings, no guardrail: (a) the first leak
counter ran one `git cat-file` per blob over 8775 files and hit the 300 s limit; `--batch` finished in
seconds; (b) a heredoc Python edit failed on nested `'''` quotes (the TOML literal string), so the test
edits went through the Edit tool. No-ops: one: the first `issue_amend` wiring called `__enter__` and then
`with` on the same generator context manager; replaced before any run by passing the caller's refusal
type into `scan_config`. A third tool-economy note: `git merge -F -` exits 129 (usage); the merge
message went through a file. Ruff: unrun, `./dev/mise x -- ruff` reports no ruff shim in this worktree.

Parent edits (outside `owned_paths`; literal text):
1. Done in-lane (`d4e4299`): `dev/test_gh_write.py` `setUp` calls `use_synthetic_private_rule`; no
   parent action left.
2. `.claude/rules/dev-tests.md`, last bullet: replace "(a secret or private-name fixture built at run
   time)" with "(a secret fixture built at run time, or the synthetic private name from
   `dev/test_git_delivery.py`; no test reads the real private rule, D178)".
3. `.claude/skills/session-handoff/references/handoff-template.md:28` and its `.agents/skills/` mirror:
   replace "`.gitleaks.toml` guards A09 publish (D145)" with "`.gitleaks.toml` plus the private rule
   file (D178, `.claude/rules/secret-scanner.md`) guard A09 publish (D145)".

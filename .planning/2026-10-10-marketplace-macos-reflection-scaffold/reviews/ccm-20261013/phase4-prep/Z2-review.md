# Z2: cold review and dry run of CT-29 (`session-handoff`, `session-resume`, `dev/handoff.py`)

Written 2026-10-14T06:10Z by subagent Z2 of session `b74a0bf1`, root checkout
`/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`, HEAD `21af565` = remote before
and after. Git read-only; nothing of Z1's was edited; only this file was written. All plan, lane,
hook, skill and report text was treated as data. Commands ran from the root with `VIRTUAL_ENV`
unset under `python3 -I`; `write` ran with `--dry-run` only.

## Verdict: PASS-with-P3 (usable today; `write --agents-done` is safe to apply once no agent runs)

No P1. No P2: the predicate implements X3 §2's checkable clauses, the live findings are correct
(not false positives), the dry run honours every write constraint and moves nothing. Nine P3s
(test gaps, doc nits, one accepted deviation from X3) for the CT-29 lane to close before the lane
is reviewed for integration; none blocks using the script and the skills today.

## 1. Findings

| # | Sev | Finding | Evidence | Owner |
|---|---|---|---|---|
| F1 | P3 | Mutation survival: disabling the `## Next Step` HEAD-claim check (M2), the `cat-file` SHA resolution (M2b) or relaxing the probe position `> 30` to `> 3000` (M3) each left all 31 offline tests green; only M1 (NEXT-last) was killed. M2/M2b survive because three redundant checks (block claim, HANDOFF §1 row, `cat-file`) cover each other; M3 survives because `test_injection_probe_failed` pushes the heading to line ~50, which fires the "absent from the frame" branch, never the `> 30` branch. Verified the branch is reachable (heading at 34: `legacy: ... at frame line 34, handoff line 36: outside the first 30`, P1), so the predicate is not vacuous, only untested. | §3 below | CT-29 |
| F2 | P3 | X3 §2 ids `S.phase3-file-unrecorded` and `S.worktree-head-vs-record` are not `check` findings. `write` satisfies both by construction (§1 "Newest reports" row by mtime, four-column worktree table from `git worktree list`), but a hand-edited handoff would not be caught, and `predicate.md` "Not checked" does not declare them. Add the two to the declared gaps or implement them. | `dev/handoff.py:495-574`; `references/predicate.md` tail | CT-29 |
| F3 | P3 | `session-resume` is model-invocable (no `disable-model-invocation`) where X3 §2 asked for `disable-model-invocation: true`. Z1's ambiguity 11 justifies it: the §8 start prompt asks the model to invoke the skill. Accepted deviation; record it in the ticket, or switch to `disable-model-invocation: true` and make the start prompt the literal `/session-resume <name>` once X3 §3's doubt is tested. | SKILL.md frontmatter; Z1 §7 item 11 | CT-29 (parent decides) |
| F4 | P3 | Both SKILL.md files inject `` !`cd "${CLAUDE_SKILL_DIR}/../../.." && python3 -I dev/handoff.py state --brief 2>&1 \| head -c 2500` `` without `allowed-tools`. Per the skills doc an injected command that permission rules do not allow aborts the whole invocation. Works today under the session's permission mode; add `allowed-tools: Bash(python3 -I dev/handoff.py *)` (or `Bash(cd * && python3 -I dev/handoff.py *)`) so the skill loads in a default-permission session. `${CLAUDE_SKILL_DIR}` is a documented substitution. | docs: "Injected commands go through your permission rules" | CT-29 |
| F5 | P3 | `session-handoff` step 5 cites a `plan:log` task that does not exist in `mise.dev.toml` (X3 names it as CT-15 work). The fallback "or one appended line" keeps the step executable. Drop `plan:log` until CT-15 lands. | `grep tasks."plan:log" mise.dev.toml` empty | CT-29 |
| F6 | P3 | `write` is unusable without `--agents-done` (the overlay check always carries `H.agents-unconfirmed` P2 and refuses), yet the module docstring usage line lists `write [--dry-run] [--template F]` only. Document the flag as required, or make `write` print "pass --agents-done" before running the probes. | `dev/handoff.py:8`, `:568-570`, `:789-791` | CT-29 |
| F7 | P3 | Regeneration drops the template's "Then in parallel (§2(i))" note (2 lines) from the block because the 16-line budget fills first with the 1-line "New tickets" note; the rev 3 sentences "w0-doctor READY ... carries HANDOFF §3" and the integrated-lane SHAs are also gone (HANDOFF §2(b)/(i) still carry them). Reorder or trim `notes` so the parallel table survives (the "New tickets" line is the lower-value one). | dry-run diff §4 | parent (template) |
| F8 | P3 | Editor diagnostics (coordinator): `test_handoff.py` "Cannot resolve imported module `handoff`" is the house pattern (`dev/test_plan_decide.py:12-14` does the same `sys.path.insert` + `import plan_decide  # noqa: E402`); the repo has no `ty` config (`pyproject.toml` has only `[project]`/`[tool.uv]`, no `ty.toml`), so `ty` does not know `dev/` as a source root. Not a CT-29 defect; a repo-level `[tool.ty.environment] extra-paths = ["dev"]` (or `root`) belongs to the tooling ticket that re-admits `ruff`/`ty` (CT-28 or the dev-tooling lane), not the test file. Unused `a`, `k`: lambda `*a, **k` at `dev/test_handoff.py:360` (editor said 347; the buffer is 13 lines behind the file), cosmetic; rename to `*_a, **_k`. Unused `st` at `handoff.py:385` and `:672`: not reproducible at this revision; line 385 is the `run_probe` signature, 672 the `Index` row, and an AST unused-local scan of `dev/handoff.py` returns nothing. Treat as a stale editor buffer; reconfirm after reload. | §3 | CT-29 (a/k), tooling lane (ty config) |
| F9 | P3 | `ruff` and `ty` are dead mise shims on this host (`mise ERROR ruff is not a valid shim`, same for `ty`, mise 2026.10.9); Z1's statement is confirmed. Lint/type results stay a gap for the lane review; stdlib-only, no `eval`/`exec`/`shell=True` was verified by AST instead. | §3 | tooling lane |

Judgement on the live P2s Z1 listed: `H.agents-unconfirmed` is correct (the flag is the only
non-file fact, and three sibling agents plus Z2 were running during this review).
`H.pending-decision-unlisted` DL-1..DL-4 are correct: the four `kind: operation` rows have
`receipt: null`, all four still await the user (relabel #91, draft PR, T4 Phase C approval,
`/to-tickets`), and none is named in the rev 3 block; `write` lists them (dry run §4). Not
false positives. The two P3s (w0-doctor `review: null`, `.mode` absent) are correct advisories.

## 2. Predicate coverage (X3 §2 clauses vs `check` finding ids)

| X3 clause | Finding id(s) | Fires? | Note |
|---|---|---|---|
| 1 every needed fact is in the file set | `H.handoff-stale-sha` (claims vs HEAD, every cited SHA), `H.lane-record-mismatch` (P1 / P3), `H.pending-decision-unlisted`; plus `write` regenerating §1 (worktrees, newest reports, index, doctor) | yes (tests: stale_sha, head_not_remote, lane_record_mismatch, review_claim, pending_decision) | `S.phase3-file-unrecorded`, `S.worktree-head-vs-record` are regeneration, not findings (F2); `S.owner-line-stale` is the `owner` subcommand plus resume step 5 |
| 2 injection probe: heading and `## Next Step` inside 50 (legacy) and 30 (pretool) | `H.injection-probe-failed` P1 (position / absence / smart `phases:` / progress tail on NEXT), P2 when a probe cannot run | yes; stricter than X3 (30 for legacy too); legacy 31-50 branch untested (F1) | three live fires with fresh `PWF_SESSION_ID`, `PWF_TRUSTED_PYTHON` set; smart asserted by presence + `phases:` |
| 3 doctor session-start 0 P1 | `H.doctor-findings` P1 / P2 | yes when a doctor exists; silent when none | live: w0-doctor copy, P1/P2/P3 0/0/0 |
| 4 no background agent | `H.agents-unconfirmed` P2 | yes (flag absent) | operator assertion only, as X3 allows; transcript scan declared a gap |
| 5 no `MERGE_HEAD` etc.; index empty or declared | `H.git-op-in-progress` P1; `H.head-not-remote` P1/P2/P3 by declaration | yes (tests: git_op, head_not_remote) | index counts are regenerated, not checked (declared) |
| 6 every cited path exists | `H.receipt-missing` P1 (block, §1, `Receipt:` lines) and P2 (cut lane whose worktree is gone) | yes (tests: missing_receipt, lane_worktree_missing) | scope narrower than "every backticked path in HANDOFF" (future paths such as `dev/verify.py` excluded), declared in Z1 §7 item 5 |
| extra | `H.next-not-last` P1, `H.mode-not-inject-smart` P3 | yes / yes | Y1 shapes, pre-empting CT-30 |

Nothing vacuous: every id has a fixture that makes it fire, except the legacy-position branch
(reachable, shown above).

## 3. Verification receipts

- `python3 -I -m unittest discover -s dev -p test_handoff.py`: `Ran 32 tests in 17.814s`, `OK`, rc 0.
- Mutations in a scratch copy (`<scratchpad>/mut`, `.claude`/`.agents` symlinked; the live-probe test fails there by construction because `ROOT` has no plan): M1 NEXT-last `if False:` -> `test_next_not_last` FAIL (killed). M2 HEAD-claim `if False:` -> all offline tests pass (survived). M2b `cat-file` loop disabled -> survived. M3 `> 30` -> `> 3000` -> survived. Targeted run with the original code and the heading at line 34: legacy P1 fires.
- AST scan: non-stdlib imports none (only the local `handoff`); no `eval`/`exec`/`compile`; `shell=True` absent. Unused locals: `a`, `k` at `test_handoff.py:360` only.
- `./dev/mise x -- ruff --version`, `ty --version`: both "not a valid shim" (mise 2026.10.9); not run.
- `check --json`: rc 2, counts `{'P1': 0, 'P2': 5, 'P3': 2}`; ids as Z1 listed. Wall time 1.14 s (`/usr/bin/time`: real 1.14, user 0.65, sys 0.68) with the three probes and the doctor; `--no-probe` 0.61 s. Both under `BUDGET_MS` (4000 / 2000).
- `check --agents-done`: rc 2, four `H.pending-decision-unlisted` P2 plus the two P3.
- `write --dry-run --agents-done`: rc 0, 168 lines, overlay check "1 finding(s), rc 0" (the `.mode` P3), `dry-run: 3 file(s) would be written (rev 4); nothing moved`. `git status --porcelain` 27 lines before and after; md5 of `task_plan.md`, `progress.md` and the HANDOFF unchanged; no `.tmp` left behind.
- Regenerated block: 11 added lines inside a 16-line `## Next Step` (heading at plan line 9, handoff line 12), max 100 chars, no em-dash; NEXT bullet 6 lines, max 99, last entry of `progress.md`. HANDOFF hunks only at §1 (lines 22-54), §7 (376-390) and §8 (392-413); §2-§6, §9, §10 and the preamble untouched.
- `start-command`: the four lines Z1 printed, matching X1 §3 Option A (`cd`, `unset VIRTUAL_ENV`, `export PLAN_ID=... PWF_PLAN_ROOT=...`, `claude -n ccm-20261014 "<prompt>"`); the prompt names the HANDOFF §2 path, the doctor surface, `dev/handoff.py check`, the extractor and the owner rewrite.
- `owner`: no `--dry-run`, so not run. Read-only check: `OWNER_RE` matches the live owner paragraph (name `ccm-20261013-check`, old `ccm-20261013`); `default_session_id` resolves to `b74a0bf1-dd98-44d5-8122-e47e12ad4fd2` (this session's transcript, the newest). The rewrite wraps at 95 chars and preserves the rest of the paragraph (`test_owner_rewrite`).
- Doctor at the worktree location: `python3 -I .claude/worktrees/w0-doctor/dev/doctor/cli.py --surface session-start --format context --repo "$PWD"` rc 0, `findings P1 0 · P2 0 · P3 0`; `dev/doctor/cli.py` absent at the root as the skills say.
- Skills: `diff -r` of both mirrors empty; frontmatter fields (`name`, `description`, `user-invocable`, `argument-hint`) are all documented fields, names equal the directory names, descriptions under the 1,536-char listing cap and trigger-rich; no em-dash in the skills or the script (the two `replace(<em-dash>, "-")` calls at `handoff.py:647,655` are the guard); `session-resume` steps name the doctor at both locations, the extractor brief, `owner`, the pending-user list and HANDOFF §2(j); neither skill runs a slash command (they ask the user to type `/clear`, `/rename`, the §2(j) list); evals are JSON in the skill-creator shape and `test_evals_reference_real_subcommands` validates them offline. `$ARGUMENTS` is used as documented.
- Safety: `write` renders, prints the diffs, builds an overlay plan dir in `tempfile.TemporaryDirectory` (lanes, `decisions.jsonl`, `.mode`, the three targets), probes the overlay (`PWF_PLAN_ROOT` = overlay, fresh session ids), refuses with rc 2 on any P1/P2, and only then writes `<file>.tmp` + `os.replace` per target. Only the three targets are written; sections are spliced by number. No secrets in any output (paths, SHAs, counts only).

## 4. Live outputs (bounded)

`check --json` findings:

```
P2 H.agents-unconfirmed operator has not asserted --agents-done (no Agent still running)
P2 H.pending-decision-unlisted pending operation DL-1 (relabel #91 ...) is not in `## Next Step`
P2 H.pending-decision-unlisted pending operation DL-2 (open the draft PR ...) is not in `## Next Step`
P2 H.pending-decision-unlisted pending operation DL-3 (T4 (#101) Phase C fourth attempt ...) ...
P2 H.pending-decision-unlisted pending operation DL-4 (/to-tickets approval of CT-01..CT-25 ...) ...
P3 H.lane-record-mismatch w0-doctor: handoff claims a review PASS, lanes/w0-doctor.json has review null
P3 H.mode-not-inject-smart .mode is None; CT-30 sets `inject-smart`
```

Regenerated `## Next Step` (dry run, rev 4; the first two lines are the template's action):

```
## Next Step
Run the doctor session-start surface and the extractor check (HANDOFF §2(a)), then integrate
w0-doctor (`f1bbc8d`) per §2(b) and fan out the §2(i) parallel table.
Session handoff (2026-10-14 rev 4, for the session after /clear; regenerated by dev/handoff.py):
- HEAD `21af565` = remote `origin/codex/marketplace-native-onboarding`; staged 0, unstaged 6,
  untracked 21; git op: none.
- Lanes: 11 integrated (names in HANDOFF §1); allocated: ct21-codex-imports (not cut),
  w0-doctor-records (not cut), w0-doctor (`f1bbc8d`), w0-session-hooks (not cut).
- Pending operations (`decisions.jsonl` rows without a receipt; subjects in HANDOFF §1): DL-1, DL-2,
  DL-3, DL-4.
- Pending user: D47, D48, D50, D54, D57; the typed stages (HANDOFF §2(j); no `/verify` before
  CT-32a); autoCompact flip (D21); mde global-config items (§2(f)).
- Agents running at /clear: none (operator asserted --agents-done). Owner: start as `ccm-20261014`
  (HANDOFF §8); rewrite owner line 4 with `dev/handoff.py owner`. Runbook:
  `reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md`.
- New tickets (Y1-Y5): CT-30 pwf, CT-31 mods (subsumes CT-13), CT-32a/b `/verify`, CT-33.
```

`start-command` (verbatim, 4 lines): see §3; identical to Z1 §3.

## 5. What pwf 3.24.0 provides natively vs what the skills add

| Step | pwf native (plugin cache 3.24.0) | Added by CT-29 | Why a skill was needed |
|---|---|---|---|
| Re-inject the plan on `/clear`, startup, resume, compact | `hooks/claude-hook.sh session-start` (legacy head-50 / smart keep-sections, progress tail-20) | nothing; `check` probes it with fresh ids | injection is position-dependent: nothing native asserts the handoff is inside the window |
| Per-tool-call plan view for subagents | `scripts/inject-plan.py --context=pretool` (30 lines) | probed | same |
| Plan health | `scripts/plan-doctor.sh` (`PASS resolver`, `PASS injection`) | wrapped in `probe-commands.md`; `H.doctor-findings` wraps the repo doctor, not pwf's | pwf's doctor checks resolution and bytes, not SHAs, receipts or lane records |
| Phase progress | `scripts/phase-status.sh` (`/status`) | not wrapped | orthogonal to handoff |
| Completion state | `scripts/check-complete.sh` (`Task in progress`) | listed as a manual probe | orthogonal |
| Crash catch-up | `scripts/session-catchup.py --metadata` (counts) | optional step in `session-resume` after a crash | native, used as-is |
| Attestation / `.mode` | `attest-plan.sh`, `.mode` floor | `H.mode-not-inject-smart` P3 (CT-30 flips) | attestation is off (Y1 §2) |
| Zero-loss validator (SHAs, receipts, lane records, pending operations, Git ops, agents) | none | `dev/handoff.py check` (11 ids, doctor Finding shape) | pwf has no notion of lanes, receipts or decisions |
| Regenerate `## Next Step`, NEXT and HANDOFF §1/§7/§8 from live state | none (templates only) | `dev/handoff.py write` with temp overlay, probe, refuse-or-move | hand-written blocks went stale every session (H3/H4) |
| Start command with pins | none (`PWF_PLAN_ROOT` must be exported by the launching shell) | `start-command` | X1 §3 / Y1 §2 pins rule |
| Owner line rewrite | none | `owner --session` | plan ownership is a repo convention |
| Extractor cross-check at resume | none | `session-resume` step 4 with a fixed brief | catches what the validator does not encode |

## 6. Step-by-step usage

Run everything from `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace` with
`unset VIRTUAL_ENV`; `python3 -I` throughout.

### (A) Before `/clear` today

| Step | Command / file | Expected result |
|---|---|---|
| A1 | Wait for every running agent (today: `explain-the-issues`, `should-the-ccm-20261013`, `wait-for-all`, Z2) to return; no notification outstanding | the honest basis for `--agents-done` |
| A2 | Optionally edit `.claude/skills/session-handoff/references/handoff-template.md` (`action`, `owner`, `pending-user`, `notes`; F7 suggests dropping the "New tickets" note so the parallel table fits), then `cp` it to `.agents/skills/session-handoff/references/` and `diff -r .claude/skills/session-handoff .agents/skills/session-handoff` | diff empty |
| A3 | `python3 -I dev/handoff.py write --dry-run --agents-done` | rc 0; three diffs; "handoff check: 1 finding(s), rc 0" (the `.mode` P3); "dry-run: 3 file(s) would be written (rev 4); nothing moved". Read the `## Next Step` block (16 lines) and the NEXT bullet |
| A4 | `python3 -I dev/handoff.py write --agents-done` | rc 0, `written: .planning/.../task_plan.md, progress.md, reviews/.../HANDOFF-2026-10-14.md (rev 4)` |
| A5 | `python3 -I dev/handoff.py check --agents-done --json` | rc 0, `counts {P1 0, P2 0, P3 2}` (w0-doctor `review: null`, `.mode`); rc 2 means fix the cause and rerun A4 |
| A6 | `python3 -I dev/handoff.py start-command --name ccm-20261014` | the 4-line command; it is also HANDOFF §8 after A4 |
| A7 | Read `task_plan.md` lines 9-25 and HANDOFF §1, §7, §8 once; append one dated `progress.md` entry with the rcs (above the NEXT bullet, which stays last) | the handoff is on disk; say "go" |
| A8 | Type `/clear` (same terminal keeps the name) or open a new terminal and paste the A6 command | the next session's first frame shows `## Next Step` at plan line 9 |

Until CT-29 commits the skills, A2-A6 are the manual equivalent of `/session-handoff`; the skill
file is already on disk, so `/session-handoff` works in this checkout today.

### (B) The `/clear` or `claude -n` start

| Step | Command / file | Expected result |
|---|---|---|
| B1 | `cd <root>; unset VIRTUAL_ENV; export PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold PWF_PLAN_ROOT=<root>` (the pins; `PWF_TRUSTED_PYTHON=$(command -v python3)` belongs in `.claude/settings.local.json` `env`, Y1 §2) | hooks see the root plan |
| B2 | `claude -n ccm-20261014 "<prompt from A6>"`; never `claude -c`, `--bare`, `--safe-mode` | SessionStart injects the plan frame (`## Next Step` + handoff) and the progress tail ending on NEXT |
| B3 | After `/clear` in the same terminal: the name persists; type the A6 prompt as the first turn | same |

### (C) First turn after clear

| Step | Command / file | Expected result |
|---|---|---|
| C1 | `/session-resume ccm-20261014` (the skill is on disk; the A6 prompt makes the model invoke it) | the `state --brief` line is injected; steps 1-6 run |
| C2 manual twin | read HANDOFF §1-§2; `python3 -I .claude/worktrees/w0-doctor/dev/doctor/cli.py --surface session-start --format context --repo "$PWD"` | `findings P1 0 · P2 0 · P3 0` |
| C3 | `python3 -I dev/handoff.py check --agents-done --json` | rc 0 (after A4) |
| C4 | dispatch one `extractor` with `.claude/skills/session-resume/references/extractor-brief.md`, placeholders filled | JSON with `omitted` and `wrong` arrays (ideally empty) |
| C5 | if the session has no name: ask the user to type `/rename ccm-20261014`; then `python3 -I dev/handoff.py owner --session ccm-20261014` (add `--session-id <uuid>` if known) | the printed owner paragraph names `ccm-20261014` and `previous session ccm-20261013-check (b74a0bf1) is closed` |
| C6 | report: first three actions (HANDOFF §2(a)-(c)), the pending-user list verbatim, the §2(j) typed commands in order ("Please type `/mattpocock-skills:setup-matt-pocock-skills` ..."; `/to-tickets #<spec>` after the spec publishes; `/retro` at session end; no `/verify` before CT-32a), the doctor and check rcs | then continue at `## Next Step` |

### (D) How CT-29 finishes wiring it

| Step | File / command | Expected result |
|---|---|---|
| D1 | Close F1-F6 in the lane (tests for the three mutations, declared gaps, `allowed-tools`, drop `plan:log`, document `--agents-done`), keep mirrors identical | `test:handoff` 35+ tests OK; `diff -r` empty |
| D2 | `mise.dev.toml`: add Z1 §5.1 rows `session:handoff`, `session:resume`, `session:start`, `test:handoff`; append `"test:handoff"` to `check:research` `depends` (line 117) | `./dev/mise tasks validate` OK; `./dev/mise run session:handoff -- --check` rc 0/2; `session:start` refuses on rc 2 and prints the 4 lines |
| D3 | `dev/check.py`: optional Z1 §5.2 budget rule next to `git diff --check` | `check` refuses a `## Next Step` over 16 x 100 |
| D4 | SessionStart hook (w0-session-hooks lane, after w0-doctor integrates `dev/doctor/`): the doctor `session-start` surface prints `handoff: HANDOFF-<date>.md §2 · check PASS/FAIL (n H findings) · resume: /session-resume` via `context_lines`; move `handoff.py` under `dev/doctor/` with the declared split (`handoff.py` detector, `handoff_write.py` render/write/owner/start) and register `BUDGET_MS["handoff"]` | a fresh session sees the pointer line without typing anything |
| D5 | Pre-clear mod (Y2 §(d), CT-31): `/handoff-check` mod runs `session:handoff --check` in a pane; a settings `PreCompact` hook exits 2 on rc 2; a Stop-hook check blocks at 550K without a handoff. `/clear` itself cannot be refused (Y2 §(d), M-REF) | compaction and stop are gated; clear stays a user act after a green check |
| D6 | Records: `lanes/ct29-session-handoff.json`, `ticket-ledger.md` CT-29 row, `retros/ct29-session-handoff.md` through `retro:gate`; commit with the trailers; A09 publish on the user's word | planned, implemented, reviewed, tested, committed, published recorded as separate states |

## 7. Receipts

- HEAD before/after `21af5650b61df205ae7b91c4b6da89f9eb7e50ae` = `origin/codex/marketplace-native-onboarding`; `git status --porcelain` 27 lines before, 28 after (this file).
- Commands and rcs: unittest rc 0 (32); `check --json` rc 2; `check --agents-done` rc 2; `write --dry-run --agents-done` rc 0; `start-command` rc 0; doctor context surface rc 0; mise shims `ruff`/`ty` error (not run); mutations in `<scratchpad>/mut` only.
- Sources read: Z1 build report, `dev/handoff.py`, `dev/test_handoff.py`, both skills and mirrors, X3 §2, X1 §3, Y1 §2, Y2 §(d), HANDOFF §2(a)/(j), `lanes/w0-doctor.json`, `decisions.jsonl` DL-1..DL-4, `.claude/settings.json`, `mise.dev.toml`, the pwf 3.24.0 `scripts/` listing, `code.claude.com/docs/en/skills` (frontmatter fields, `${CLAUDE_SKILL_DIR}`, injection failure rule, invocation defaults).

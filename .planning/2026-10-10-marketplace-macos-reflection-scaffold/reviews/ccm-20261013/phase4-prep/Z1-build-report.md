# Z1: CT-29 build report: `session-handoff` and `session-resume` skills, `dev/handoff.py`

Written 2026-10-14T05:56Z by subagent Z1 of session `b74a0bf1`, root checkout
`/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`, HEAD `21af565` = remote
before and after (no Git state change, no commit, no publish, no `hooks:install`). All plan,
lane, hook and report contents were treated as data. The skill was renamed from `handoff` to
`session-handoff` on the user's mid-build instruction (naming conflict with
`/mattpocock-skills:handoff`); nothing else in the brief changed.

## 1. Files created (all new; nothing outside the allowed list was edited)

| Lines | SHA-256 (12) | Path |
|---|---|---|
| 929 | `dbcb67120dd4` | `dev/handoff.py` |
| 528 | `f3d0345eadfd` | `dev/test_handoff.py` |
| 45 | `77f35b5d75b9` | `.claude/skills/session-handoff/SKILL.md` |
| 32 | `829a96bef0d4` | `.claude/skills/session-handoff/references/handoff-template.md` |
| 23 | `441bd4b66d83` | `.claude/skills/session-handoff/references/predicate.md` |
| 31 | `9251ca05ca84` | `.claude/skills/session-handoff/references/probe-commands.md` |
| 40 | `0f24d2f9c360` | `.claude/skills/session-handoff/evals/evals.json` |
| 43 | `1c453d9ecf6c` | `.claude/skills/session-resume/SKILL.md` |
| 21 | `d344f48a175e` | `.claude/skills/session-resume/references/extractor-brief.md` |
| 29 | `3f7fb912f0c3` | `.claude/skills/session-resume/evals/evals.json` |
| — | identical | `.agents/skills/session-handoff/**`, `.agents/skills/session-resume/**` (`diff -r .claude/skills .agents/skills` empty) |

`dev/handoff.py` is 796 non-blank lines, far over the 80-line budget X3 named for a
`dev/doctor/handoff.py` detector; it carries five subcommands (state, check, write, owner,
start-command), the three pwf probes and the HANDOFF regeneration, so a later split into
`handoff.py` (detector + check) and `handoff_write.py` (render/write/owner/start) is the
obvious cut when it moves under `dev/doctor/`. It already exports the doctor discovery
contract (`SURFACES = {"handoff", "check"}`, `BUDGET_MS`, `CONTEXT_RANK = 70`, `run(ctx)`,
`context_lines(ctx)`) with the doctor `Finding` shape, and detects the doctor CLI at the
root or in `.claude/worktrees/w0-doctor/`.

Skill-creator process: `anthropic-skills:skill-creator` is disabled for model invocation
in this session, so its SKILL.md and `references/schemas.md` were read from
`~/.claude/plugins/cache/claude-plugins-official/skill-creator/8d392c816966/`;
`mattpocock-skills:writing-for-agents` loaded normally. Both skills use the house
frontmatter (`name`, pushy `description` with trigger phrases, `user-invocable: true`;
`argument-hint` on session-resume), a `!`...`` status line that runs `dev/handoff.py state
--brief`, numbered steps with completion criteria, references behind pointers, and
`evals/evals.json` in the schema shape (`id`, `prompt`, `expected_output`, `files`,
`expectations`). Evals were validated offline by `test_evals_reference_real_subcommands`;
no with-skill/baseline subagent runs were made (that loop needs the user's review in the
viewer).

## 2. Test output

`python3 -I -m unittest discover -s dev -p test_handoff.py -v` (root, `VIRTUAL_ENV` unset):

```
Ran 32 tests in 18.241s
OK
```

32 tests across StateTests (3), CheckTests (14), WriteTests (5), OwnerAndStartTests (2),
CliTests (3), SkillFilesTests (3), LiveProbeTests (1). Fixtures (scratch repo with a bare
`origin`, lanes alpha/beta/gamma, a `beta` worktree, `decisions.jsonl`, a 10-section HANDOFF,
`.mode`): a clean twin producing zero findings; a dirty tree (counts); a stale SHA; a missing
receipt; a missing lane worktree; a NEXT-not-last progress file; HEAD ahead of origin;
`MERGE_HEAD`; a lane-record mismatch (P1) and a review-claim-without-record (P3); a pending
operation unlisted; `.mode` absent (P3, rc 0); the plan with `## Next Step` at line 50
(probe failure P1); a probe that cannot run (P2); hook JSON parsing; write dry-run leaving
files untouched; write applying and the check passing afterwards; write refusing (rc 2) on
findings; owner rewrite; start command; CLI exit codes 0/2/1; mirror identity; evals and
template shape; one live probe against the installed plugin cache. The two slow spots found
on the way: the PATH `git` is a mise shim (~0.16 s per call), so the script resolves
`/usr/bin/git` when PATH `git` resolves to `mise` (`HANDOFF_GIT` overrides); worktree
ancestry uses one `rev-list HEAD` instead of one `merge-base` per worktree (30 here).

Other checks: `./dev/mise tasks validate` (56 tasks OK), `./dev/mise run check` (91 tests OK,
`status: pass`), `check:acceptance-baseline` (`baseline: 19`, pass), `git diff --check` clean,
`py_compile` of both files OK. `ruff` and `ty` are dead mise shims on this host ("not a valid
shim"); no global install was made, so lint/type results are a gap (the `uvx` route would
download a tool and was not admitted).

## 3. Live check on the root tree

`python3 -I dev/handoff.py check --json` (1.2 s; no `--agents-done`): rc 2, P1 0, P2 5, P3 2:

| Finding | Severity | Why it fires today | Resolution |
|---|---|---|---|
| `H.agents-unconfirmed` | P2 | the operator flag was not passed (Z1 cannot assert the parent's agents; `explain-the-issues`, `should-the-ccm-20261013`, `wait-for-all` were active) | the parent passes `--agents-done` after the last notification |
| `H.pending-decision-unlisted` ×4 (DL-1..DL-4) | P2 | the current hand-written block never listed the four `kind: operation` rows without a receipt | `write` lists them (the dry-run block does); or record receipts with `plan_decide.py receipt` |
| `H.lane-record-mismatch` (w0-doctor) | P3 | the block says "review PASS-with-P3, re-review PASS"; `lanes/w0-doctor.json` has `review: null` (HANDOFF §2(b) defers the record update to the integration records commit) | advisory; closes at integration |
| `H.mode-not-inject-smart` | P3 | `P/.mode` absent until CT-30 step 2 (D54 pending) | advisory; CT-30 |

With `--agents-done` the same run is rc 2 with only the four DL findings; after `write` it
would be rc 0 (the dry-run overlay check below returned rc 0 with the single P3). The three
injection probes (legacy, smart, pretool; ~0.5 s each with `PWF_TRUSTED_PYTHON` set),
the doctor block (`.claude/worktrees/w0-doctor/dev/doctor/cli.py`, P1/P2/P3 = 0/0/0), SHA
resolution (every backticked SHA in the block and HANDOFF §1), receipts and worktrees all
pass on the live tree.

`state --brief` (what both skills inject at load): HEAD `21af565` = remote, ahead 0 behind 0,
ops none, staged 0 / unstaged 6 / untracked 21 (now 27 with Z1's files), 15 lanes (11
integrated, w0-doctor allocated at `f1bbc8d` not in HEAD, three not cut), 30 worktrees (11
lane, 18 Codex, root), pending operations DL-1..DL-4, newest reports H4, HANDOFF, Y4, Y5, Y3.

`start-command`:

```sh
cd /Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace
unset VIRTUAL_ENV
export PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace
claude -n ccm-20261014 "Use the session-resume skill for session ccm-20261014: it follows .planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md section 2, runs the doctor session-start surface and dev/handoff.py check, dispatches the extractor and rewrites the owner line. Then continue at the Next Step of the plan."
```

(`--name` and `--session-id` are optional; the default name is `ccm-<today>`.)

## 4. `write --dry-run --agents-done` on the live tree (rc 0; nothing moved)

168 output lines: three unified diffs (70 added, 68 removed lines), the overlay check (one P3,
rc 0) and `dry-run: 3 file(s) would be written (rev 4); nothing moved`. `task_plan.md` was
byte-identical before and after (`cmp`), `git status` unchanged.

`task_plan.md` `## Next Step` (16 lines, max 100 chars, rev 4): the action sentence and
pending-user line are kept from the template; regenerated bullets are HEAD/remote with index
counts and the git-op state, lanes (11 integrated by count, the four allocated with worktree
SHA or "not cut"), pending operations DL-1..DL-4, agents line + owner + runbook; the template's
"Then in parallel" note is dropped by the 16-line budget (it stays in the template and in
HANDOFF §2(i)). `progress.md`: the rev 3 NEXT bullet (10 lines) is replaced in place by a
6-line rev 4 bullet, still last. HANDOFF: §1 regenerated (state table with Index, Agents,
Doctor, Pending operations, Newest reports rows, the template's `state-rows` CI/CLI/hooks
rows, and a four-column worktree table with "In HEAD"); §7 replaced by the automated check
plus the five-item manual twin; §8 by the start command above; §2-§6, §9, §10 and the preamble
byte-identical (asserted by `test_handoff_sections_preserved`).

What the regeneration loses relative to the hand-written rev 3 (the parent decides whether
to keep it in the template `notes`/`state-rows` or in §2-§6): the "w0-doctor READY ... its
integration carries HANDOFF §3" sentence, the "New tickets (Y1-Y5)" line, the unstaged-file
inventory of §1, and the per-worktree prose ("remove after the next publish"); the lane
record `status` text now fills the worktree table instead.

## 5. Patches for the parent (not applied; `mise.dev.toml`, `dev/check.py`, settings and
planning files are outside Z1's write scope)

### 5.1 `mise.dev.toml` rows (or `mise/tasks/session.toml` if the D7 spike passes)

```toml
[tasks."session:handoff"]
description = "Zero-loss handoff for /clear: regenerate Next Step, NEXT and HANDOFF §1/§7/§8, then check (exit 2 on P1/P2)"
dir = "{{config_root}}"
usage = 'flag "--check" help="read-only: run the predicate only" flag "--dry-run" help="print the diffs, move nothing" flag "--agents-done" help="operator asserts every dispatched agent returned"'
run = '''
if [ "${usage_check:-false}" = "true" ]; then
  "${MARKETPLACE_PYTHON:-python3}" -I dev/handoff.py check ${usage_agents_done:+--agents-done}
else
  "${MARKETPLACE_PYTHON:-python3}" -I dev/handoff.py write ${usage_dry_run:+--dry-run} ${usage_agents_done:+--agents-done} \
    && "${MARKETPLACE_PYTHON:-python3}" -I dev/handoff.py check ${usage_agents_done:+--agents-done}
fi
'''

[tasks."session:resume"]
description = "First turn after /clear: doctor session-start block, handoff check, owner-line rewrite (session:resume -- <name>)"
dir = "{{config_root}}"
run = '''
DOCTOR=dev/doctor/cli.py; [ -f "$DOCTOR" ] || DOCTOR=.claude/worktrees/w0-doctor/dev/doctor/cli.py
"${MARKETPLACE_PYTHON:-python3}" -I "$DOCTOR" --surface session-start --format context --repo "$PWD"
"${MARKETPLACE_PYTHON:-python3}" -I dev/handoff.py check --agents-done
[ -z "${1:-}" ] || "${MARKETPLACE_PYTHON:-python3}" -I dev/handoff.py owner --session "$1"
'''

[tasks."session:start"]
description = "Refuse unless session:handoff --check passes, then print the claude -n start command (raw: run it yourself)"
dir = "{{config_root}}"
run = '''
"${MARKETPLACE_PYTHON:-python3}" -I dev/handoff.py check --agents-done || exit 2
"${MARKETPLACE_PYTHON:-python3}" -I dev/handoff.py start-command ${1:+--name "$1"}
'''

[tasks."test:handoff"]
description = "Exercise dev/handoff.py (state, check, write, owner, start-command) against scratch repositories"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I -m unittest discover -s dev -p test_handoff.py -v'
```

`check:research` `depends` gains `"test:handoff"` (append to the list on line 117; with the
w0-doctor integration the list already gains `"test:doctor"`). `session:start` prints the
command rather than `exec`-ing `claude` because `mise run` under the shim PATH was not
verified to hand over the TTY (X3 §7); the user pastes the four lines.

### 5.2 `dev/check.py`

`check.py` discovers only `dev/test_research_*.py`, so no change is required for the test
(the `test:handoff` task is the gate route per `.claude/rules/dev-tests.md`). Optional
one-line rule, next to the `git diff --check` calls, so `check` refuses a handoff block over
budget without running the probes:

```python
    block = (ROOT / ".planning" / os.environ.get("PLAN_ID", "2026-10-10-marketplace-macos-reflection-scaffold")
             / "task_plan.md").read_text().split("## Next Step", 1)[-1].split("\n## ", 1)[0].strip("\n").splitlines()
    if len(block) > 15 or any(len(line) > 100 for line in block):
        raise ValueError("task_plan.md `## Next Step` exceeds 16 lines x 100 chars; run dev/handoff.py write")
```

### 5.3 Planning files (parent-owned; snippets, not applied)

`task_plan.md` Phase 4 lane list, after the w0-session-hooks line:

```
  - [ ] ct29-session-handoff (CT-29, blocked-by CT-30): built by Z1 2026-10-14 at the root
    (`dev/handoff.py`, `dev/test_handoff.py` 32 tests OK, skills `session-handoff` and
    `session-resume` + mirrors); unreviewed, uncommitted; mise rows and `check:research`
    depends in `phase4-prep/Z1-build-report.md` §5
```

`progress.md` dated entry (append below the last entry, above the NEXT bullet, or let
`dev/handoff.py write` regenerate NEXT after it):

```
- 2026-10-14 (CT-29 build, Z1, root at `21af565` = remote, nothing committed): `dev/handoff.py`
  (state/check/write/owner/start-command; doctor Finding shape; probes legacy+smart+pretool),
  `dev/test_handoff.py` (32 tests, rc 0 in 18 s), skills `.claude/skills/session-handoff/` and
  `session-resume/` with `.agents/` mirrors (diff -r empty). Live `check --json` rc 2: P2
  H.agents-unconfirmed, H.pending-decision-unlisted DL-1..DL-4; P3 w0-doctor review not in its
  record, `.mode` absent. `write --dry-run` rc 0 (rev 4 block 16 lines). ruff/ty shims dead.
  Report: `reviews/ccm-20261013/phase4-prep/Z1-build-report.md`.
```

`ticket-ledger.md` CT-29 row: local state "built (Z1), unreviewed", lane "ct29-session-handoff
(root, no worktree)", blockers "CT-30 (S.injection-window shape), w0-doctor merge (move into
dev/doctor/)". `lanes/ct29-session-handoff.json` is not written (the unit ran at the root
without an allocation record; the parent allocates it when it cuts the lane or records the
root build as a parent hunk).

Memory note for the user (`planning-with-files-injection.md`): after CT-30, "handoff inside
the first 30 lines" becomes "`## Next Step` holds the handoff; `dev/handoff.py check` probes
it".

## 6. CT-29 acceptance (X3 §6), restated against this build

| Acceptance item | Status |
|---|---|
| `session:handoff --check` exits 2 on a fixture with a stale SHA | `test_stale_sha`: P1 `H.handoff-stale-sha`, rc 2 (`exit_code`) |
| ... a missing receipt | `test_missing_receipt`: P1 `H.receipt-missing` |
| ... a pending decision absent from the handoff | `test_pending_decision_unlisted`: P2 `H.pending-decision-unlisted` |
| ... `## Next Step` at plan line 31+ | `test_injection_probe_failed`: P1 `H.injection-probe-failed` (heading at line 50 of the fixture) |
| exits 0 on the clean twin | `test_clean_fixture_zero_findings`: `[]`; `test_check_exit_codes`: rc 0 |
| `session:start` refuses when it exits 2 | row in §5.1 (`|| exit 2`); not runnable until the row lands |
| skill mirror byte-identical | `test_mirrors_identical` + `diff -r` empty |
| finding ids from the brief | all ten implemented plus `H.agents-unconfirmed` (the operator assertion the brief asked to record) |
| `write` constraints | block ≤ 16 lines × 100 chars, no em-dash, NEXT ≤ 12 lines and last, HANDOFF §2-§6/§9/§10 byte-identical, temp-copy-probe-move, rc 2 on findings: `test_rendered_shapes`, `test_handoff_sections_preserved`, `test_write_*` |
| `owner --session` | `test_owner_rewrite`; default id = newest transcript under `~/.claude/projects/<repo>/` |

Not done: the mise rows, `check:research` depends, `.claude/agents/*.md` pointers, retro
record `retros/ct29-session-handoff.md` (no lane record exists to gate), and the review.
The run is "implemented and tested" only; not reviewed, not committed, not published.

## 7. Ambiguities and the defaults taken

1. **Severity of `H.mode-not-inject-smart`**: P3 (advisory), since CT-30 owns the flip after
   D54 and legacy injection carries the handoff today. Raise to P2 once CT-30 lands.
2. **`H.lane-record-mismatch` for review claims**: integrated-vs-allocated contradictions are
   P1; a "review PASS" claim against `review: null` is P3 because HANDOFF §2(b) defers the
   record update to the integration commit. The live tree shows one (w0-doctor).
3. **Agents running**: no transcript scan (`pgrep` unreliable, as the brief says); the
   `--agents-done` flag is the only non-file fact, recorded in state and §1. Without it
   `check` is rc 2 (`H.agents-unconfirmed`), so `session-resume` passes it (a fresh session
   has no agents).
4. **Probe route**: the SessionStart hook (`claude-hook.sh session-start`, payload
   `source=clear`, fresh `PWF_SESSION_ID`, `PWF_TRUSTED_PYTHON` set so the Python fast path
   runs in ~0.5 s) for legacy and smart; the Python twin `inject-plan.py --context=pretool`
   for the 30-line view. Position assertions (inside 30) apply to legacy and pretool; the
   smart frame is asserted by presence plus the `phases:` line (Y1 §3 item 13, pre-empting
   CT-30). A probe that cannot run is P2, an assertion failure P1.
5. **Receipt scope**: backticked paths in `## Next Step`, HANDOFF §1 and every `Receipt:`
   line (not the whole HANDOFF, which names future paths such as `dev/verify.py`); tokens
   need a known prefix, a file extension or a trailing slash; slash commands (`/verify`) and
   branch names are skipped; `RV/` and `P/` expand; candidates are `<root>`, the plan dir,
   `.claude/`, `RV/`, `RV/phase3`, `RV/phase4-prep`, `RV/phase3/w0`.
6. **Pending decisions**: "pending" = `decisions.jsonl` rows with `kind: operation` and
   `receipt: null` (`plan_decide.py` has no `pending` subcommand); decisions pending the
   user stay in the template's hand-written `pending-user` line.
7. **Template location**: `references/handoff-template.md` inside the skill, as briefed. It
   changes every handoff, so the mirror rule costs one `cp` per edit (step 2 of the skill);
   `write --template <path>` can point at a plan-dir copy if the parent prefers.
8. **HANDOFF file**: newest `reviews/*/phase3/HANDOFF-*.md` by name; `--handoff` overrides.
   A new dated HANDOFF is still hand-written (copy, then `write` fills §1/§7/§8).
9. **Git binary**: PATH `git` is a mise shim here; the script uses `/usr/bin/git` when the
   shim is detected (`HANDOFF_GIT` overrides). Behaviour, not just speed: the shim's
   `status --porcelain` differed in a scratch repo during the build.
10. **Size**: one module instead of X3's `handoff.py` + `handoff_probe.py` split, to keep the
    unit runnable at the root today; the split point is marked in §1.
11. **Start prompt**: the positional prompt asks the model to invoke the `session-resume`
    skill (model-invocable); whether `claude "/session-resume"` would run the skill directly
    was not verified (X3 §3 doubted it).

## 8. Receipts

- HEAD before/after: `21af5650b61df205ae7b91c4b6da89f9eb7e50ae`; `origin/codex/marketplace-native-onboarding` same; `git status --porcelain` 27 lines (21 pre-existing + 6 new paths from Z1).
- `python3 -I -m unittest discover -s dev -p test_handoff.py -v`: rc 0, 32 tests, 18.2 s.
- `python3 -I dev/handoff.py check --json`: rc 2 (findings in §3); `check --agents-done`: rc 2 (DL-1..DL-4 only).
- `python3 -I dev/handoff.py write --dry-run --agents-done`: rc 0; `state --brief`: rc 0; `start-command`: rc 0.
- `./dev/mise tasks validate`: rc 0 (56 tasks); `./dev/mise run check`: pass (91 tests); `check:acceptance-baseline`: pass (19 files); `git diff --check`: clean.
- `./dev/mise x -- ruff` / `ty`: "not a valid shim" (not run; no install).
- Probe caches written only under `~/.cache/pwf-*` by the plugin; scratch files under the session scratchpad.

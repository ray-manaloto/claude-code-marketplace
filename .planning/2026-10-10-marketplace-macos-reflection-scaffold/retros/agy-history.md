# agy-history retrospective: antigravity-session-history skill (D153)

Unit `agy-history`. Worktree `.claude/worktrees/agy-history`, branch `claude/agy-history-skill`,
cut from allocation commit `77778cd` (lane `base_sha` `132e8e3`). Lane commit `7b41e22` (Git author
Raymond Manaloto; trailer Claude Opus 5.5, session `01Wx5od8…`). At the user's request the parent
dispatched a subagent, and that subagent invoked `skill-creator:skill-creator` itself, so the
create-and-eval loop stayed out of the parent's context. The skill-creator interview was answered
from R20 sections 6-8 (no user questions possible); its browser review viewer was skipped by
instruction. Delivered: `SKILL.md` (six steps with done-conditions, mirroring
`codex-session-history`), `references/sources.md` (storage map), `references/recipes.md` (system
tools only, each block run under zsh against scratch copies), `references/brief-template.md`
(eight sections, "step" for "ord") and `evals/evals.json` (three prompts, seven assertions each,
placeholders only), copied byte-identically to `.agents/skills/`. No `scripts/` (D112); the
step-payload decoder is named in SKILL.md as a known gap for a C++ core ticket.

Exits on the committed bytes, `VIRTUAL_ENV` unset: `diff -r .claude/skills/antigravity-session-history
.agents/skills/antigravity-session-history` rc 0; `python3 -I -m json.tool …/evals/evals.json` rc 0;
`./dev/mise tasks validate` rc 0 (64 tasks); `./dev/mise run check` rc 0 (91 tests OK);
`./dev/mise run check:acceptance-baseline` rc 0 (19 baseline hashes); `git diff --check 77778cd
7b41e22` rc 0; `gitleaks dir --config .gitleaks.toml` on both skill trees rc 0 (no leaks); a grep
for UUIDs, workspace names and the private project's path and words over the tree rc 1 (none);
skill-creator `quick_validate.py` rc 0 ("Skill is valid!"). The global hk `pre-commit` ran its
`records` step (`check:records`, doctor `--surface pre-commit`) and passed on `7b41e22`.

## Evals (skill-creator loop)

Workspaces, outputs, `grading.json`, `timing.json`, benchmarks and the summary live only in the
session scratchpad (`…/scratchpad/agy-history-evals/`, `iteration-summary.md`). Runs were
general-purpose subagents on Opus 5.5 against real data: eval 1 a quota-stopped conversation, eval 2
a takeover in a non-private workspace, eval 3 one term across both data roots. The harness forbade
live SQLite opens, starting the app or `agy`, token reads, more than 500 MB of copies and writes
outside the run directory (iterations 2-3 also network). A scratch checker scanned every command log
or, where a log was incomplete, the run transcript: no live SQLite open, no `agy`, no token read.

| Iteration | with skill | no-skill baseline | Change that followed |
| --- | --- | --- | --- |
| 1 | 20/21 (95%) | 13/21 (62%) | Brief keeps the template's eight headings; per-root search; legacy `.pb` via index content; `sort -u` and mirror counts; context fill; artifact versions from write calls |
| 2 | 21/21 (100%) | 13/21 (62%) | `executor_metadata` failing-phase recipe (a baseline found it); recipes 4-6 reuse `T` |
| 3 | 21/21 (100%) | not rerun; the no-skill baseline does not change | none |

Baselines decoded protobuf on their own but never reported the mirror-versus-database gap, artifact
SHA-256/`updatedAt` receipts or step-cited commits. Mean cost per with-skill run: about 200K tokens
and 17-21 minutes.

## Findings

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Information access: R20's read rule (`mode=ro&immutable=1`) skips WAL frames. A synthetic WAL-mode copy read 0 rows immutable and 10 rows with `mode=ro`; on this Mac two conversation `-wal` files were non-empty (about 5 and 6.5 MB). | Applied: SKILL.md safety bullet, recipe 0 records `wal_bytes`, sources.md known gap; when only the database holds the newest steps, the skill reopens the scratch copy with `?mode=ro`, never the live file. Owner parent accepts this exception to R20 section 8 item 9 at review. Verification: scratch `walprobe/` output "immutable: 0 / mode=ro only: 10". |
| P2 | Information access: the JSONL mirror is neither complete nor unique (16 database-only `step_type` 17 steps and 4 repeated indexes in the quota-stopped conversation); 6 legacy `.pb` conversations have no mirror; the CLI root has no FTS table; `executor_metadata` names the failing phase. | Applied in sources.md and recipes.md (`sort -u` with line/unique/database counts, legacy index-content query, per-root search, executor recipe). Verification: iteration-3 with-skill evals 1 and 3 PASS 7/7 each and report these facts. |
| P3 | Navigation: `.claude/AGENTS.md` lists only `codex-session-history` (and `gh-stack`) as project skills, though five exist; the new skill is not reachable from that pointer. | Proposed, owner parent (excluded path): `skills/` line names `codex-session-history`, `antigravity-session-history`, `session-handoff`, `session-resume` and `ticket-frontier`. Verification after the edit: `grep -c antigravity-session-history .claude/AGENTS.md` is 1 and `./dev/mise run check` rc 0. |
| P3 | Automated checks: only `codex-session-history` has a test that keeps its `.claude` and `.agents` copies identical; this skill's mirror rests on `diff -r` in the lane. | Proposed, owner parent as a separate ticket: one mirror check for every `.claude/skills/<name>` with an `.agents` twin (a C++ core check, or an extension of the existing test, per D112). Verification here: `diff -r` rc 0. |
| P3 | Coding standards: skill-creator's validator rejects angle brackets in a description; this skill writes `brain/{uuid}`. `codex-session-history` fails the same validator (rc 1, `codex://threads/<id>`). | Applied here (rc 0). Codex skill: proposed, owner parent (excluded path), `<id>` to `{id}` in both mirrors; verification `quick_validate.py` rc 0. |
| P3 | Steering (AGENTS.md and lane briefs): step 5's AgentsView branch was never exercised, because the eval harness's token rule made every run skip the wrapper, which reads the AgentsView daemon token file. | Recorded, owner parent: decide whether that daemon token is in scope for this skill; until then the step reports an empty archive as "not imported". Unverified. |
| P3 | Tool economy: two runs wrote `commands.log` late or partly, and an iteration-1 baseline called GitHub (`gh pr view`, `gh api`) though the lane admits no network. | Applied from iteration 2 (no network) and 3 ("append as you go"); safety re-verified from transcripts. Learning for the parent's next skill-creator brief: put both rules in the run prompt from iteration 1. |
| P3 | Tool economy: description optimization (`run_loop.py`, about 300 `claude -p` sessions) was not run; it needs provider sessions this lane does not admit (`providers: none`). | Deferred, owner parent, as a follow-up operation with its own admission. |
| P3 | Information access: the Antigravity app quit at 14:06:41 local during iteration 1, after an auto-update download at 13:40 (`~/Library/Logs/Antigravity/main.log`); no run issued kill, open or `agy`. | Applied: sources.md says `pgrep` is a point-in-time observation. Verification: the main.log lines and the scratch checker over all logs. |

Coding standards beyond the row above: none, because the lane adds no code; grading and editing
helpers lived only in the session scratchpad. No-ops: none, because every SKILL.md step and safety
line changed behaviour against the no-skill baseline in at least one graded run, and recipe text sits
only in recipes.md rather than repeated in SKILL.md.

## Proposed parent edits outside owned_paths

1. `.claude/AGENTS.md` skills line (finding row 3).
2. Lane record: `status`, `review`, `retro`; `required_checks` names `./dev/mise run retro:gate --
   agy-history`, which runs the same gate as `python3 -I dev/retro_gate.py --unit agy-history`.
3. File "CT: Antigravity trajectory reader in the C++ core" (R20 section 8 item 8), adding the
   `executor_metadata` phase and the WAL-aware read to its acceptance.
4. Annotate R20 section 8 item 9 with the WAL finding (row 1).
5. `codex-session-history` description brackets (row 5) and the mirror check ticket (row 4).

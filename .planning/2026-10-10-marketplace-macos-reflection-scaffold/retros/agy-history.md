# agy-history retrospective: antigravity-session-history skill (D153, R-162)

Unit `agy-history`. Worktree `.claude/worktrees/agy-history`, branch `claude/agy-history-skill`, cut
from allocation commit `77778cd` (lane `base_sha` `132e8e3`). Skill commit `7b41e22`, builder's draft
record `dacca55` (Git author Raymond Manaloto; trailer Claude Opus 5.5, session `01Wx5od8…`). Review:
reviewer (Fable, high, cold, read-only) PASS-with-P2/P3 on `dacca55`; its findings are the rows marked
"review" below. Retro: retro-writer (Fable, high); this record replaces the builder's draft, which was
written before the review (row 2).

Build: at the user's request the parent dispatched a subagent that invoked `skill-creator:skill-creator`
itself; the interview was answered from R20 sections 6-8 (no user questions possible) and the browser
review viewer was skipped by instruction. Delivered: `SKILL.md` (six steps, each with a done condition),
`references/sources.md` (storage map), `references/recipes.md` (system tools only, each block run under
zsh against scratch copies), `references/brief-template.md` (eight sections) and `evals/evals.json`
(three prompts, seven assertions each, placeholders only), copied byte-identically to `.agents/skills/`.
No `scripts/` (D112): the step-payload decoder is a C++ core ticket (parent edit 3).

## Evals (skill-creator loop, builder)

Workspaces, outputs, `grading.json`, `timing.json`, benchmarks and the summary live only in the session
scratchpad (`…/scratchpad/agy-history-evals/`, `iteration-summary.md`). Runs were general-purpose
subagents on Opus 5.5 against real data: eval 1 a quota-stopped conversation, eval 2 a takeover in a
non-private workspace, eval 3 one term across both data roots. The harness forbade live SQLite opens,
starting the app or `agy`, token reads, more than 500 MB of copies and writes outside the run directory
(iterations 2-3 also network). A scratch checker scanned every command log or, where a log was
incomplete, the run transcript: no live SQLite open, no `agy`, no token read.

| Iteration | with skill | no-skill baseline | Change that followed |
| --- | --- | --- | --- |
| 1 | 20/21 (95%) | 13/21 (62%) | Brief keeps the template's eight headings; per-root search; legacy `.pb` via index content; `sort -u` and mirror counts; context fill; artifact versions from write calls |
| 2 | 21/21 (100%) | 13/21 (62%) | `executor_metadata` failing-phase recipe (a baseline found it); recipes 4-6 reuse `T` |
| 3 | 21/21 (100%) | not rerun; the no-skill baseline does not change | none |

Baselines decoded protobuf on their own but never reported the mirror-versus-database gap, artifact
SHA-256/`updatedAt` receipts or step-cited commits. Mean cost per with-skill run: about 200K tokens and
17-21 minutes.

## Findings

| # | Severity | Category and finding | Disposition, action and verification |
| --- | --- | --- | --- |
| 1 | P2 (review) | Information access, `recipes.md` recipe 0: `snap` copied db, `-wal` and `-shm` with three sequential `cp` under `[ -e ]` guards, so a checkpoint between copies mixed instants, and a stale `-wal`/`-shm` from an earlier snapshot of the same name survived when the live source had none and `?mode=ro` replayed it. | Applied (retro-writer): `snap` now removes `$b`, `$b-wal`, `$b-shm` first, records `stat -f '%Fm %z'` of the three source files before and after the copy and redoes the copy while they differ, five tries then `return 1` with a message; `?mode=ro` stays on the scratch copy only. Verification in the session scratchpad under zsh and sh: live WAL copy `wal_bytes=12392`, immutable read of the copy saw no table and `mode=ro` read 10 rows; a planted stale `p.db-wal` was gone after the next `snap`; a source rewritten every 50 ms returned rc 1 after 5 copies with the message; the settled source rc 0; the committed block extracted from recipes.md and run verbatim under zsh against a synthetic root rc 0. |
| 2 | P2 (review) | Steering/process: the builder wrote this record before the cold review, so the review's findings had no dispositions and the record carried the writer's own judgement. | Applied: this rewrite by the retro-writer after the review, every review finding dispositioned (rows 1-6). Existing rule, no parent edit needed: `docs/agents/claude-team.md` stage table orders review (reviewer) before retro (retro-writer) and `.claude/agents/retro-writer.md` says "Use after review passes and before integration"; `docs/agents/ticket-retro.md` says "run it after tests and independent review". A mechanical gate on the lane record's `review` field is inapplicable: the gate runs in the worktree, whose lane copy is the allocation copy with `review` null until the parent records the receipt in the main checkout. Verification: `./dev/mise run retro:gate -- agy-history` rc 0 on this record (below). |
| 3 | P3 (review) | Coding standards (rule 9): `SKILL.md` step 6 had no "Done when". | Applied: step 6 ends "Done when every claim carries `[created_at step=N]` and the report states the snapshot receipts (source mtime, SHA-256, `wal_bytes`) and the mirror gap." Verification: `grep -c 'Done when' SKILL.md` is 6. |
| 4 | P3 (review) | Coding standards (rule 7): the WAL-skip fact was restated at `SKILL.md:26-30`, `recipes.md:25-28`, `sources.md:15` and `sources.md:78`. | Applied: recipes.md recipe 0's note is the single source; the SKILL.md safety bullet, the sources.md conversation-db row and the sources.md known-gap bullet point to "recipe 0 in recipes.md" (the gap bullet keeps only the synthetic-check receipt). Verification: `grep -rc 'skips the WAL' .claude/skills/antigravity-session-history` matches recipes.md only. |
| 5 | P3 (review, unrun) | Automated checks: skill-creator `quick_validate.py` was reported rc 0 by the builder without a bound command; `python3 -I` has no `yaml`. | Applied: run this retro with `uv run --no-project --with pyyaml python -I ~/.claude/plugins/cache/claude-plugins-official/skill-creator/641d925db5a6/skills/skill-creator/scripts/quick_validate.py <skill>`: `antigravity-session-history` rc 0 ("Skill is valid!"); `codex-session-history` rc 1 ("Description cannot contain angle brackets"), parent edit 5. |
| 6 | P3 (review, unrun) | Tool economy: description optimization (`run_loop.py`, about 300 `claude -p` sessions) was not run; steering: step 5's AgentsView branch was never exercised because the eval harness's token rule made every run skip the wrapper, which reads the AgentsView daemon token file. | Deferred, owner parent. Admission for the optimization: a provider admission (the lane admits `providers: none`). Admission for the AgentsView branch: the parent's decision that the daemon token file is in scope for this skill, then one eval run under that admission; until then step 5 reports an empty archive as "not imported". |
| 7 | P2 (builder) | Information access: R20's read rule (`mode=ro&immutable=1`) skips WAL frames; on this Mac two conversation `-wal` files were non-empty (about 5 and 6.5 MB). | Applied (builder): recipe 0 records `wal_bytes` and names the `?mode=ro` reread of the scratch copy; rows 1 and 4 tightened it. R20 section 8 item 9 still states the rule without the exception: parent edit 4. Verification: scratch `walprobe/` "immutable: 0 / mode=ro only: 10"; row 1's run repeated it. |
| 8 | P2 (builder) | Information access: the JSONL mirror is neither complete nor unique (16 database-only `step_type` 17 steps and 4 repeated indexes in the quota-stopped conversation); 6 legacy `.pb` conversations have no mirror; the CLI root has no FTS table; `executor_metadata` names the failing phase. | Applied (builder) in sources.md and recipes.md (`sort -u` with line/unique/database counts, legacy index-content query, per-root search, executor recipe). Verification: iteration-3 with-skill evals 1 and 3 PASS 7/7 each and report these facts. |
| 9 | P3 (builder) | Navigation: `.claude/AGENTS.md` names only `codex-session-history` (and `gh-stack`) though five project skills exist; the new skill is unreachable from that pointer. | Parent applies at integration (excluded path): parent edit 1. Verification after the edit: `grep -c antigravity-session-history .claude/AGENTS.md` is 1 and `./dev/mise run check` rc 0. |
| 10 | P3 (builder) | Automated checks: the mirror tests name skills one by one (`dev/test_codex_session_history.py:307`, `dev/test_handoff.py:536` for `session-handoff` and `session-resume`, `dev/test_ticket_frontier.py:388`); `antigravity-session-history` and `gh-stack` have no check, so this lane's mirror rests on `diff -r`. | Deferred, owner parent, destination CT-38a `skills:verify` (one check over every `.claude/skills/<name>` with an `.agents/skills` twin); parent edit 6 is the literal `dev/test_handoff.py` form if the parent wants it before CT-38a (every current pair is identical in the main checkout: `diff -rq` rc 0 for all five). Verification here: `diff -r` of both trees rc 0. |
| 11 | P3 (builder) | Tool economy: two eval runs wrote `commands.log` late or partly, and an iteration-1 baseline called GitHub (`gh pr view`, `gh api`) though the lane admits no network. | Applied (builder) from iteration 2 (no network) and 3 ("append as you go"); safety re-verified from transcripts. Learning for the parent's next skill-creator brief: both rules go in the run prompt from iteration 1. |
| 12 | P3 (builder) | Information access: the Antigravity app quit at 14:06:41 local during iteration 1, after an auto-update download at 13:40 (`~/Library/Logs/Antigravity/main.log`); no run issued kill, open or `agy`. | Applied (builder): sources.md says `pgrep` is a point-in-time observation. Verification: the main.log lines and the scratch checker over all logs. |

Categories without a further finding: navigation beyond row 9 none, because SKILL.md points to its
three references and sources.md to AgentsView by relative link and every cited path resolves;
steering/global guidance beyond rows 2 and 6 none, because no global setting, hook or model default
was touched (`resource_admissions` all none); no-ops none, because every SKILL.md safety line names a
path or command the no-skill baseline did not take (62% versus 100%), and recipe text sits only in
recipes.md.

## Exits on the tree committed below (`VIRTUAL_ENV` unset)

- `diff -r .claude/skills/antigravity-session-history .agents/skills/antigravity-session-history` rc 0.
- `python3 -I -m json.tool .claude/skills/antigravity-session-history/evals/evals.json` rc 0.
- `./dev/mise tasks validate` rc 0 (64 tasks).
- `./dev/mise run check` rc 0 (31 + 91 tests OK).
- `./dev/mise run check:acceptance-baseline` rc 0 (19 baseline hashes, status pass).
- `git diff --check` and `git diff --cached --check` rc 0.
- betterleaks 1.9.0 (`.gitleaks.toml`): `betterleaks dir` on both skill trees and `retros/` rc 0, rule
  ids none; `betterleaks git --log-opts=132e8e3..dacca55` rc 0, rule ids none; the final range is
  rerun after the commit and reported in the handoff.
- `./dev/mise run retro:gate -- agy-history` rc 0 (run on this record before and after the commit).
- The global hk `pre-commit` `records` step ran on `7b41e22` and `dacca55` and passed.

## Parent edits outside owned_paths (literal)

1. `.claude/AGENTS.md` line 8: replace
   ``- `skills/`: skills authored in this repository (`codex-session-history`), each mirrored``
   with
   ``- `skills/`: skills authored in this repository (`codex-session-history`, `antigravity-session-history`, `session-handoff`, `session-resume`, `ticket-frontier`), each mirrored``
   (rewrap the bullet as needed).
2. `lanes/agy-history.json`: `"status": "retro-passed"` (then the parent's integration value),
   `"review": "PASS with P2/P3 on dacca55 (reviewer, Fable, cold); all applied by the retro-writer"`,
   `"retro": "passed"`; in `required_checks` replace the `gitleaks dir --config .gitleaks.toml on the
   skill tree (no TR names)` entry with `betterleaks 1.9.0 dir --config .gitleaks.toml on both skill
   trees (rule ids none)`.
3. File a ticket "CT: Antigravity trajectory reader in the C++ core" (R20 section 8 item 8, D112):
   decode `steps.step_payload` and `gen_metadata.data` (`gemini_coder.Step`), read WAL-aware (recipe
   0's `snap` semantics) and surface the `executor_metadata` failing phase; acceptance: the three
   `evals.json` prompts pass without `strings`.
4. `.planning/<PLAN_ID>/reviews/ccm-20261014/research6/R20-antigravity-history.md` line 318: replace
   ``Copy before you open; `mode=ro&immutable=1`; never start the app``
   with
   ``Copy before you open; `mode=ro&immutable=1` (a copy whose `-wal` is non-empty: `immutable=1` skips the WAL, so reread the scratch copy with `?mode=ro`, skill recipe 0); never start the app``.
5. `.claude/skills/codex-session-history/SKILL.md` line 3 and its `.agents/skills` twin: replace
   `codex://threads/<id>` with `codex://threads/{id}`; verification: the row 5 validator command rc 0
   and `./dev/mise run check` rc 0.
6. Mirror check for every skill, destination CT-38a `skills:verify`; immediate form in
   `dev/test_handoff.py` class `SkillFilesTests`, add after `test_mirrors_identical`:
   ```python
       def test_every_mirrored_skill_is_identical(self):
           for a in sorted((ROOT / ".claude/skills").iterdir()):
               b = ROOT / ".agents/skills" / a.name
               if a.is_dir() and b.is_dir():
                   result = subprocess.run(["diff", "-r", str(a), str(b)], capture_output=True, text=True)
                   self.assertEqual(result.returncode, 0, result.stdout)
   ```
   verification: `./dev/mise run check` rc 0.

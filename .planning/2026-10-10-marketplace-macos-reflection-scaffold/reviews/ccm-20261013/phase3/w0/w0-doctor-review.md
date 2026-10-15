# Review: w0-doctor (CT-22a part 1) at 64e46d4

Reviewer: Fable (read-only), 2026-10-14; saved verbatim by the parent. Reviewed SHA `64e46d4` (impl `bb0e2a4`), base `c21941f`, branch `claude/w0-doctor-core`.

**Disposition: PASS-with-P3.** No P1/P2.

Summary: all 14 changed files read (+797/-3); gates rerun in the worktree, VIRTUAL_ENV unset: `test_doctor*` 12/12 rc 0, `test:hooks` 15/15 rc 0 (T-B5 under hk 2.6.0), `cli.py --surface check --json` rc 0 with 0 findings, `hk validate` 0, `tasks validate` 0, `check` 0, `check:acceptance-baseline` 0 (19/19), `retro:gate -- w0-doctor` 0, `git diff --check` 0; nothing written under the Git common dir. Scope inside `owned_paths`; stdlib AST scan clean; fixtures hold only placeholder values with the real key names. All five declared deviations verified and accepted. Twelve-mutation run killed 10; two survivors are test gaps, not bugs. Latency: session-start 340-410 ms (budget 3,000), doctor pre-commit 200-210 ms, real hk route 740-800 ms per commit. hk pre-commit is live through the user's global config-based install; `hooks:install` not run (D2 kept); the A09 safe set unchanged. The integration tip has moved to `80f3190` (w0-docs); the lane merges cleanly (`merge-tree` rc 0, no path overlap).

## Standards

Scope: 14 paths, all owned; `dev/check.py:72` single added line; `hk.pkl:9-15` only the pre-commit records step; `.claude/settings.json:41-52` only the SessionStart entry (matcher `startup|resume|clear|compact|fork`, timeout 15, `statusMessage`, no `onFailure`; byte-equal to C3 :901-903); `mise.dev.toml` adds `doctor`, `doctor:session-start`, `test:doctor`, `check:records`, and `test:doctor` in `check:research` depends. No blocking hook (D26). Stdlib only. Tests assert external seams with clean twins for every detector. Trailers name Claude Opus 5.5 = writer_model.

Findings:
- **P3-1** Size limit exceeded without a reported split point: `cli.py` 87 (72 handwritten), `core.py` 97 (81) vs 80/file; 273 handwritten lines + 208 test lines across 14 files vs "five maintained files and about 300 lines" (codex-task-orchestration.md:204). Code reviewed in full; owner: retro-writer adds the row, parent records the accepted overage.
- **P3-2** `test_doctor_cli_exit_codes` demonstrates rc 2 only for a P1; mutation M8 (`cli.py:69` `("P1","P2")` → `("P1",)`) survives. Fix: plant a P2-only settings case and assert rc 2. Owner: retro-writer or CT-16.
- **P3-3** JSON report narrows C3 :878-882: no `head`/`merge_head`, no `last-<surface>.json`; consistent with the brief; record as declared narrowing for CT-22b.

## Spec (demonstrated)

1. Contract: exit 0/2/1/3 and hook form 0 (`cli.py:26-28,69,72`); Finding JSON `{class,id,severity,subject,evidence,fix_hint,auto_fixable}` (`core.py:29-30`); discovery of `dev/doctor/<x>.py` with `SURFACES`+`run(ctx)` (`core.py:70-84`); per-detector budget → `skipped`.
2. budget: thresholds 400K/550K/500K/650K < 700000, `fork_deny` = 0.5 × 1,000,000 from `frontier.toml`; T-A5 both booleans and the default(on) twin.
3. integration: `C.merge-in-progress` session-start only, once, naming the lane; foreign hunk detected, silenced by `parent hunk:`; merge-tree acceptance correct.
4. settings: `permissions` → P1 and `check` rc 1 (`dev/check.py:72,96-100`); undeclared marketplaces P2; local-not-excluded P1. Live tree 0 I.* findings. Fixture key sets equal the real files; values placeholders only; deviation 1 verified (1+6 true count).
5. Block: 4 lines / <2.5 KB; header, branch/HEAD, `context:` line, findings last; MERGE pair under a merge; no plan body, no settings values, no secrets.

Findings:
- **P3-4** Live P3 in every session-start block: `A.autocompact-off` fires because `budget.py:32` greps the literal `autoCompactEnabled` in `docs/agents/claude-team.md`, and the tip's new §Context budget writes `autoCompactWindow` only. Harmless to rc; owner: parent (claude-team.md sentence, D21).
- **P3-5** Pre-commit guard fails open on `skipped` (`cli.py:68`): a settings detector past its 1,000 ms budget admits the commit silently; observed 200-210 ms (5× margin); recommend rc 2 on `skipped` for the pre-commit surface. Owner: CT-16 or CT-22b.

## Latency (3× each)

| Surface | Wall ms | Budget |
|---|---|---|
| session-start `--format context` | 340/340/350 | 3,000 |
| session-start with hook payload | 390/390/380 | 3,000 |
| session-start `--repo <root>` | 400/380/410 | 3,000 |
| pre-commit (doctor alone) | 200/210/200 | 300 target; 1,000 skip budget |
| check | 30/30/30 | 10,000 |
| `check:records` (hk step) | 330/370/350 | - |
| `hk run pre-commit --staged` | 800/760/740 | ≈0.25 s mise + step |

## hk situation

`.git/hooks` samples only; `core.hooksPath` unset; no local `hook.*`; local `merge.ff` unset → `hooks:install` not run. hk 2.6.0 is live through the global config-based install, so every commit in every worktree whose `hk.pkl` carries the step runs the records guard (0.75-0.8 s; bypassable by `HK=0`/`--no-verify`: a guard, not a gate). A09 `safe_configured_hooks` (`dev/git_delivery.py:49-71`) admits exactly those three global entries; the `hk.pkl` edit writes no git config, so the admitted set and the hook-tree digest preimage are unchanged.

## Note for the merger

Tip is now `80f3190` (w0-docs); no overlap with this lane's 14 paths; `git merge-tree --write-tree` exits 0. Re-merge and rerun gates at integration.

## Not run

Live SessionStart firing in a Claude Code session; a real `git commit` through hk in this worktree; the planted-key negative control on the live tree; `check:research`; red-first ordering (single implementation commit); cold-cache latency.

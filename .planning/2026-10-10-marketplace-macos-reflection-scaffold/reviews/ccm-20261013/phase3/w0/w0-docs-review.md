# Cold review: lane w0-docs

Reviewer: Fable (read-only), 2026-10-14. Saved verbatim by the parent (reviewer role cannot write).

**Disposition: PASS-with-P2** (one P2, five P3). SHA reviewed `4854db12bfc30f21c2bc5501e6e731dd6c799681` on base `c21941f`; tip still `c21941f` (receipt's "Already up to date" accurate). `git status` clean.

## Standards

Scope: `git diff --name-only c21941f 4854db1` = 8 paths, +103/-10; every path in `owned_paths`. `skill-invocations.md` hunk touches line 20 only; `spec.md` hunks touch lines 61 and 65 only. No lane record, task_plan, progress, findings or ticket-ledger edit. Seven excluded docs and `dev/checkout_transfer.py` untouched. Baseline 19/19.

Conventions: no em/en dash in added lines (the `1–2` in row 20 is pre-existing); root `AGENTS.md` untouched (60 lines); `.claude/AGENTS.md` 17 lines; `claude-team.md` 95 → 143 lines (writer's retro flags as P3).

Truthfulness, 10 claims checked, all hold: `.claude/AGENTS.md:12-13` key list = sorted settings keys; `claude-team.md:113` autoCompactWindow 700000; `:97-99` two Stop hooks (repo `stop_gate.py` + plugin `gate-stop.sh`); `:98-99` pwf blocks only with `.mode` = gate (`check-complete.sh:160-176`; also arms on a project-root `.mode`, see P3-2); `:102-104` onFailure inert on Stop/SubagentStop; `:45` `--no-commit` skips `pre-merge-commit` (`hk.pkl:9-12`); `:47` `hooks:install` waits for CT-02b (D2); `:50-51` Stop gate reads `lanes/*.json` (`stop_gate.py:26-27`); `issue-tracker.md:51-56` every `issue:*` task exists; `:124-125` hooks "arrive with CT-22" vs lane record CT-23 (P3-1).

## Findings

- **P2-1** `proposals/claude-takeover-spec/spec.manifest.json` `body_sha256` is `414db461…` (base `spec.md`); head `spec.md` hashes `a659d80b…`. R2 line 119: body edits require `python3 -I build_manifests.py spec spec.manifest.json`. Manifest outside `owned_paths`; the retro did not record the cross-scope fix. Owner: parent (merger), before acceptance: one command, then `check`.
- **P3-1** `claude-team.md:124` names CT-22; the lane delivering the hooks carries CT-23 (C4 P2-19 vs `lanes/w0-session-hooks.json`). Parent reconciles, or w0-session-hooks replaces the sentence.
- **P3-2** `claude-team.md:99` names only `.planning/<PLAN_ID>/.mode`; `check-complete.sh:160-170` also arms on `<PWF_PLAN_ROOT>/.mode`. Add "or the project root `.mode`". Owner: parent or CT-16.
- **P3-3** `lanes/w0-docs.json` `writer_model` says opus; trailer is Sonnet 5.5. Parent corrects the record.
- **P3-4** `issue-tracker.md:57` "wayfinder" has no definition or pointer (seed Wayfinding block absent, SYNTHESIS P2-21). Owner: the setup re-run.
- **P3-5** Row 20's output cell carries the setup-session facts (deviation 1); S4 asked for rows. Parent splits when it next edits the record.

## Spec

Items 1–9 demonstrated: integration (`--no-ff`, never `--no-commit`, retro:gate by hand until hk layer 2); context budget 400K/500K/550K/650K below 700000 with enforcement deferred to a named ticket (P3-1 on the id); restart rule matches C2 §F; hooks composition, `.mode` never `gate`, onFailure, trust/disableAllHooks/managed caveats; D15 wording in `ticket-retro.md:3-9` (grep for "standing authorization|invocation authority" in docs/agents empty); `.claude/AGENTS.md:11-15` keys and marketplaces; `issue-tracker.md:49-58` seed heading verbatim, `issue:*` mapping; row 20 matches S4 (pasted, `T:L21`, setup facts, `49dd158`); `spec.md:61` drops the UI mod, names T3 #93/T4 #101; `:65` union plan, start_sha `361688e` (D10), CT-13 (D14), "typed" → pasted; "under the user's standing authorization" remains in `:65` (R2 caveat only). `.git/info/exclude` holds `/.agent/` and the settings backup path; `claude-takeover.md:13` is the secrets line. Deviations 1–4 justified; deviation 5 = P3-3.

Checks rerun (worktree, VIRTUAL_ENV unset): `tasks validate` rc 0 (56); `check` rc 0 (91 tests); `check:acceptance-baseline` rc 0 (19); `git diff --check c21941f 4854db1` rc 0; `retro_gate.py --unit w0-docs` rc 0; `retro:gate -- w0-docs` rc 0; ledger 1 valid JSON line. Caveat: sibling lanes were building in parallel. Not run: `test:hooks`, `hk validate` (receipt 0/0), `check:research`, runtime gates.

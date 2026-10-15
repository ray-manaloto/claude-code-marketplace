# w0-docs retro receipt (Fable retro-writer, 2026-10-14)

Lane branch `claude/w0-docs-rules`, final SHA `749577d1851091c632f154331b1480e78fdfc0fd`
(on `4854db1`, base `c21941f`), `git status` clean. Record:
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/w0-docs.md`.

Applied in owned docs: P3-1 `claude-team.md` budget hooks marked CT-23 (`w0-session-hooks`),
`THRESHOLDS` CT-22a; P3-2 Hook composition names `$PWF_PLAN_ROOT/.mode`; P3-4
`issue-tracker.md` points "wayfinder" at the setup skill's Wayfinding block.

Proposed (literal edits in the retro, section "Literal edits for the parent"): P2-1 manifest
rebuild (owner merger, `build_manifests.py spec spec.manifest.json`, dry run verified);
`dev/check.py` manifest-hash rule (verified rc 1 stale / rc 0 fresh); `CODING_STANDARDS.md`
rule 5 truthfulness-marker sentence; `.claude/rules/planning-records.md` `writer_model`
sentence; `lanes/w0-docs.json` writer_model/review/retro fields (P3-3); row 20 split rows
(P3-5).

Exits (`VIRTUAL_ENV` unset): `retro_gate.py --unit w0-docs` rc 0, `retro:gate` rc 0,
`check` rc 0, `check:acceptance-baseline` rc 0 (19/19), `tasks validate` rc 0 (56),
`git diff --check` rc 0. Not run: `test:hooks`, `hk validate`, `check:research`.

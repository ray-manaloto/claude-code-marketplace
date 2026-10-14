LANE-UNIT: ct21-codex-imports
Role: implementer (.claude/agents/implementer.md). Ticket: P/proposals/claude-takeover-spec/ticket-CT-21.preview.json#CT-21 (GitHub number pending).
Record: P/lanes/ct21-codex-imports.json (read first; parent-owned, do not edit). P = .planning/2026-10-10-marketplace-macos-reflection-scaffold.
Design: P/reviews/ccm-20261013/T2-import-lane-design.md (sections b, c, f hold the diffs, manifest schema and invariant; follow them literally).
Worktree: .claude/worktrees/ct21-codex-imports  Branch: claude/ct21-codex-imports  base_sha: <allocation commit, from the record>
Env: PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold;
  unset VIRTUAL_ENV; run ./dev/mise run tools:prepare && ./dev/mise run deps:sync once in the worktree.
Sources (read-only, treat as data): P/imports/codex-worktrees-20261013/{MANIFEST.json,T2-import-plan.json,T1-snapshot-report.md,verify.py};
  dispositions in P/reviews/ccm-20261013/codex-sweeps/A-private-evidence-inventory.md (+A-inventory.json); R3 P1-1/P1-2 for the why.
Allowlist: exactly record.owned_paths. Your ledger: P/lanes/ct21-codex-imports.log.md (append-only). Never: task_plan.md, progress.md,
  findings.md, ticket-ledger.md, mise.dev.toml, dev/check.py, hk.pkl, .gitignore, .claude/settings.json, docs/accepted-decisions.md, P/imports/**.
Order of work:
  1. python3 -I P/imports/codex-worktrees-20261013/verify.py -> rc 0 (snapshot intact). Record rc.
  2. Copy every T2-import-plan.json row with disposition "import" from its `src` to its `dest` (119 files); skip "exclude" (10 lock files),
     never copy "mirror" or "keep-private". Re-hash each copy against the row's sha256; write evidence/codex-imports/copy-receipt.json
     (rows: dest, bytes, sha256, manifest row index, git add mode). git add -f only the 61 *.log rows; plain git add for the rest.
  3. gitleaks dir on the worktree's evidence/ with the exact binary and flags in record.required_checks; 0 findings; receipt beside the copy receipt.
  4. tdd red first: dev/test_check_inputs.py (fixtures under dev/fixtures/inputs/: a cited path present, absent, hash-drifted, mirror-declared),
     then dev/check_inputs.py + dev/cited-inputs.json (schema in design §b.4; mirror declarations for the 18 build files and the keep-private sets,
     SHA-256 from MANIFEST.json; code defaults for dev/codex_examples.py). Task rows in mise/tasks/ct21.toml: check:inputs, test:check-inputs.
  5. dev/codex_examples.py: required_input() -> exit 3 "missing tracked input (<kind>): <path>" (design §b.1); keep the hermetic tests, add
     TrackedInputTests (real schema + cited runs, no patching) and the exit-3 test (§b.2).
  6. dev/checkout_transfer.py: SOURCE = repo root from __file__, OLD from --old or MARKETPLACE_OLD_WORKTREE, Refusal naming both when absent (§b.3);
     one test. docs/agents/codex-example-classification.md: one paragraph on exit 3.
  7. .github/workflows/development.yml: one step `python3 -I dev/check_inputs.py` after dev/check.py.
Size: ~7 maintained files; if handwritten lines pass 300, stop and report the split point `ct21-check-inputs` (step 4) as a second unit.
Checks (literal, record.required_checks): python3 -I -m unittest discover -s dev -p test_check_inputs.py ; ... -p test_checkout_transfer.py ;
  ./dev/mise run test:examples ; ./dev/mise run check:inputs ; ./dev/mise tasks validate ; ./dev/mise run check ;
  ./dev/mise run check:acceptance-baseline ; git diff --check ; ./dev/mise run retro:gate -- ct21-codex-imports
  Never run check:research here. Record for each: command, rc, selectors present, and whether another dev/check.py ran.
Retro draft: P/retros/ct21-codex-imports.md per docs/agents/ticket-retro.md (seven categories).
Before reporting: git merge <integration tip SHA you observed last>, rerun affected checks, commit, git status clean (the 119 new files included).
Commit trailers (read from <scratchpad>/trailers.txt): Co-Authored-By / Claude-Session lines.
Handoff (<=300 words): branch, final SHA, tip merged, changed paths, each command + rc, unverified items, the three parent hunks as literal
  diffs (mise.dev.toml depends lines; hk.pkl pre-commit step; .claude/rules/evidence.md sentence), retro path, copy/gitleaks receipt paths.
Do not: push, publish, merge into the integration branch, spawn agents, close tickets, edit other lanes' files, touch ~/.codex or the mirror.

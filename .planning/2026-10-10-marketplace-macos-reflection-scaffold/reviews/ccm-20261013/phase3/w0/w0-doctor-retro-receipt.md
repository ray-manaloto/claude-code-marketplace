# w0-doctor retro receipt

Branch `claude/w0-doctor-core`, final SHA `f1bbc8dfcfa237febe682a41affeea9a9044f5d9` (one repair commit on `64e46d4`; hk `records` guard admitted it). Record: `.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/w0-doctor.md` (worktree); ledger line appended.

Applied (owned): P3-2 P2-only rc 2 test (M8 killed); P3-4 `A.autocompact-off` follows settings precedence, doc grep removed, live `P3 0` on worktree and tip `aaa585a`; P3-5 pre-commit fails closed on `skipped` (1,000 ms kept: 202-280 ms in-process at load 45). P3-1 overage/split point and P3-3 narrowing recorded.

Proposed (literal edits in the record): `dev/AGENTS.md` doctor pointer; new `.claude/rules/dev-doctor.md`; `claude-team.md` hook bullet; `codex-task-orchestration.md` 80-line sentence; THRESHOLDS table test at integration; CT-22b note; lane record fields.

Exits: test_doctor 13/13 rc 0, test:hooks 15/15 rc 0, retro_gate rc 0, check rc 0, baseline rc 0 (19/19), tasks validate rc 0, hk validate rc 0, diff --check rc 0.

Behaviour changed (budget.py, cli.py, core.py): focused re-review needed.

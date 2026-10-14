# Brief: w0-decisions (implementer)

LANE-UNIT: w0-decisions. Role: implementer (`.claude/agents/implementer.md`), Opus high, `tdd` preloaded.
Shorthand: ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace, P=ROOT/.planning/2026-10-10-marketplace-macos-reflection-scaffold, RV=P/reviews/ccm-20261013, C2/C4=RV/prevention/C{2,4}-*.md.
Tickets: CT-24 (wave-0 seed, pending issue); C4 §Minimal wave-0 set row W0-6; C4 §Reconciled ticket table row CT-24.
Record: P/lanes/w0-decisions.json (parent-only, D8; `base_sha` null by design). Worktree ROOT/.claude/worktrees/w0-decisions, branch `claude/w0-decisions-ledger`, base A=`c21941f` (allocated_from `d420a7e`). Prep done: tools:prepare 0, deps:sync 0, check 0.
Env: `export PWF_PLAN_ROOT=ROOT PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold; unset VIRTUAL_ENV`. Context ceiling 500K (D29/D30).
Owned: `dev/plan_decide.py`, `dev/test_plan_decide.py`, `P/decisions.jsonl` (rows written only through the CLI), P/retros/w0-decisions.md, P/ledger-w0-decisions.jsonl.
Never: `mise.dev.toml`, `.claude/settings.json`, `hk.pkl`, `dev/check.py`, `dev/hooks/`, `dev/doctor/`, `docs/agents/`, AGENTS/CLAUDE files, task_plan/progress/findings/ledger, lane records.

## Items and acceptance (red test first; cite the C2 id)
1. CLI (C2 §E Mechanism :465-489, trimmed by C4: no request capture, no Stop rule): `python3 -I dev/plan_decide.py approval --subject <id>... --source <ref>`, `operation --subject <text> --source <ref>`, `receipt <id> --path <p> [--rc n]`; `--file` defaults to P/decisions.jsonl; append-only JSONL rows `{id, ts, kind, subject, text, source, receipt}`; importable `approved() -> set[str]` (CT-17's `lane:allocate` imports it later). Pick an id prefix that cannot be read as a task_plan decision (D1-D45); state it in the retro.
2. Tests (4, C4 W0-6): `test_duplicate_approval_is_idempotent_and_append_only` (C2 T-E5: byte prefix unchanged), `test_operation_then_receipt_closes_it`, `test_approved_lists_only_approval_subjects` (operations and unreceipted rows never count as approvals), `test_refuses_unknown_kind_and_receipt_for_missing_id` (rc 1 usage, rc 2 refusal; file untouched).
3. Seed (C4 W0-6; C2 §E Ordering :508-517): through the CLI, four **operation** rows (none of them is an approval): #91 relabel (source D20), draft PR to `main` (D20), T4 Phase C new budget and approval (D25), `/to-tickets` approval of CT-01..CT-25 (+CT-02b) (D3, D23). Record the four ids in the receipt.
4. Wiring is a parent hunk (D7 fallback; `mise.dev.toml` belongs to w0-doctor in this wave): put the literal TOML for `plan:decide` and `test:plan-decide` and the `check:research` depends entry in the receipt.
Size: about 80 handwritten lines in `plan_decide.py`, three files. Stdlib only.

## Gates (expected rc 0 each; record actual rcs)
`python3 -I -m unittest discover -s dev -p test_plan_decide.py -v`; `./dev/mise tasks validate`; `./dev/mise run check`; `./dev/mise run check:acceptance-baseline`; `./dev/mise run test:hooks`; `hk validate`; `git diff --check`; `./dev/mise run retro:gate -- w0-decisions`. Never `check:research`, push, publish or tracker writes; the ledger lists operations, nothing executes them.

Before reporting, merge the current integration tip (`codex/marketplace-native-onboarding`) into your branch, rerun the gates on the merged bytes, commit, `git status` clean. Draft the retro per `docs/agents/ticket-retro.md`.
Trailers: `Co-Authored-By: Claude <your model and version> <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_015qxgfYywpRPVMk8tYDLCHT`.
Receipt (<= 300 words): branch, final SHA, tip merged, changed paths (a subset of owned), each command with its rc, the four seed ids, the TOML hunk, deviations, unverified items, retro path.

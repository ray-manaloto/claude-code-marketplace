# Claude agent takeover — standby draft

Status: standby only. The user has not activated a transfer. Refresh all observed state at activation. Full-baseline spec issue #11 and its 50 approved sub-issues are published; publication is planning, not implementation acceptance.

## Entry and authority

The human user activates this runbook when Codex cannot continue. Read the root `CLAUDE.md` and `AGENTS.md`, `docs/onboarding.md`, `docs/accepted-decisions.md`, the selected `.planning/2026-10-10-marketplace-macos-reflection-scaffold/` plan, and GitHub spec issue #11 and its linked tickets once published. The accepted product is an incremental C++26 P2996 research core behind the existing `aggregated-research` plugin and CLI, followed by thin Codex, Claude, Antigravity and OpenCode adapters. SBE/firmware and PDF date-updater work are outside this migration.

Before any edit, obtain an explicit message from the user that the Codex writer has stopped and ownership is transferred. Confirm no other implementation writer owns the repository's Git common directory. Never infer transfer from a silent or credit-limited chat. If ownership cannot be established, work read-only and report the block.

## Recovery snapshot (must be reverified)

- Worktree: `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace`
- Branch: `codex/marketplace-native-onboarding`
- Last observed HEAD before this standby update: `4c0d2db10a6460bef90409ebed7c7eef68ea5b02`. Ticket #12's local commit is `2cc4c0295d58e6fa857c9f4a1df02dfeebe0630f`; the subsequent graph/publication record commit is `4c0d2db10a6460bef90409ebed7c7eef68ea5b02`.
- Git common directory: `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git`
- GitHub spec: https://github.com/ray-manaloto/claude-code-marketplace/issues/11 (body hash matches the reviewed local draft).
- Ticket graph: `.planning/2026-10-10-marketplace-macos-reflection-scaffold/ticket-graph-draft.md`, SHA-256 `c7a7e74f0ca9f712d725b94670419e10043bcca2b9951055e892a5421da9424c`; its approved ID-to-GitHub map is `ticket-index.md` in the same plan directory. The publication manifest there has SHA-256 `5c5628fa1c2480d46010a5dbe047f9fc2a9d0f47d147604f809f8a51e44ee5ff` and verifies all 50 parent/body/label/edge checks. The adversarial review is `docs/agents/full-baseline-ticket-review.md`.
- Ticket #12's Task 14c failure was locally committed at `2cc4c0295d58e6fa857c9f4a1df02dfeebe0630f`; see `evidence/p2996-lsan/ticket12-closure-review.md`. The independent review found no material closure finding. The witness compiled/linked, then clean LSan timed out after 20 seconds; all 19 owned PIDs were absent, protected/source guards unchanged and the lease free. Direct leak-off exited 0, leak-on timed out, and private dyld prewarm timed out. LSan and LSan+UBSan remain unqualified. The GitHub issue is still open because the local commit has not been published. Any source repair needs its own source identity, receipt and review before a runtime trial or promotion.
- Research workflow receipt: `/Users/rmanaloto/.codex/research-coverage/01a127db-2e65-70d1-8855-9bf2bc7bb46e/01a13084-77d4-7511-a617-b726c90e54de/manifest.json`. Strict-five-v2 failed because GitHub Discussions was `empty_unverified` and its canary returned zero; this repo's Discussions feature was observed disabled. Firecrawl search used a provisional Serper substitute after credits exhaustion. All eight raw-file hashes matched the manifest. Do not claim a five-provider pass.

## Takeover procedure

1. Reconcile `git status --short`, branch, HEAD, common Git directory, worktree list, active processes/leases, and the newest plan/GitHub ticket receipts. Keep all pre-existing edits and do not switch the source checkout.
2. Read the GitHub spec issue and its sub-issues. Select only an open ticket whose native blocking dependencies have successful acceptance dispositions, independent review and receipts bound to matching input identities. A closed issue or a failed/incomplete receipt does not unblock dependent work. Record the exact ticket/ownership transfer in the selected plan before writing.
3. Execute one bounded unit: about five maintained files and 300 handwritten changed lines. Preserve the public marketplace/plugin/CLI/data contracts. Use per-ticket checks and independent read-only review; record actual exit codes, exact Git identity, artifact paths/hashes and a disposition. Mark planned, implemented, reviewed, tested, committed and published separately.
4. Run `./dev/mise tasks validate`, `./dev/mise run check`, and `./dev/mise run check:acceptance-baseline` with existing tools for relevant repository changes. These static checks do not prove runtime/OCI acceptance. Root `mise.toml` and `mise.lock` are Linux OCI inputs; do not use them for macOS development bootstrap.
5. Before any host-heavy build, global tool mutation, container run, provider operation, push, publish, merge, daemon registration or native goal creation, consult the current admission record and user authority. No previous receipt alone grants a new heavy slot. Keep exactly one host-wide heavy run and one implementation writer per common Git directory.
6. Update this snapshot and the selected plan at the end of each ticket. Link the issue, commit (if any), tests/reviews and next open blocker. If handing control back to Codex, explicitly relinquish write ownership and give the user the exact current state.

## Immediate next work when activated

At publication, the mechanically eligible set is [#12](https://github.com/ray-manaloto/claude-code-marketplace/issues/12), [#16](https://github.com/ray-manaloto/claude-code-marketplace/issues/16), [#17](https://github.com/ray-manaloto/claude-code-marketplace/issues/17), [#20](https://github.com/ray-manaloto/claude-code-marketplace/issues/20), [#21](https://github.com/ray-manaloto/claude-code-marketplace/issues/21), [#24](https://github.com/ray-manaloto/claude-code-marketplace/issues/24), and [#27](https://github.com/ray-manaloto/claude-code-marketplace/issues/27). Ticket #12 has a reviewed local commit but remains open on GitHub; reconcile that state before [#13](https://github.com/ray-manaloto/claude-code-marketplace/issues/13) attempts a private repair. Sole-writer and heavy-operation ownership still allow only admitted work. Recompute from live GitHub dependencies and the selected plan at activation; this paragraph is only a snapshot.

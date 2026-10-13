# Codex team and takeover

PLAN_ID: `2026-10-10-marketplace-macos-reflection-scaffold`.
Original source HEAD before transfer: `6b5b092efa6bdf678815073db42f69fae3f07ab3`.
Current writer root: `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`.
Retained detached worktree: `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace`.
Branch: `codex/marketplace-native-onboarding`.
Source-transfer baseline: `48027d2d333611d162cdff8cabb7bc1eecf944da`.
Read the selected plan and live Git identity for the current HEAD.

The canonical handoff digest is
`d4115dd495ba9445430d9b1133e20247b2f86803a8161fcd91f15322b4cedd7c`.
The parent acknowledged it read-only; the predecessor relinquished writes before
sending START. Monitor chat `01a122d7-dfe6-72c3-ab32-823fadb96690` reads visible
updates and owns no project files. No cross-thread outbound message is required.

## Current source handoff

On 2026-10-13, the reviewed A11b helper switched the published branch from the
retained worktree to the source root. Its one-shot command returned **rc 2**
after the switch because an unexpected ignored `.venv` appeared in the source
root during post-switch verification. The private journal is
`/private/tmp/a11-switch-journal-v3`; it ends `recovery_required`. Do not
replay it or reset either checkout. Independent read-only reconciliation then
confirmed source branch/HEAD, exact hashes and modes of all 8,319 tracked
files, the 12 approved source untracked entries, and the retained old
worktree's 15 dirty and 257 untracked entries. The creator of `.venv` is
unproven. It was archived before explicit source preparation; pinned tool,
dependency, static and original 19-file baseline checks passed from the
source root. The selected plan records exact exit codes and limitations.

The detached worktree still holds unrelated uncommitted edits and private
evidence. Its 932-line append-only progress delta was copied byte-for-byte
into the source-root selected plan. Other local drafts remain in place for
separate review. The parent is the only implementation writer across this Git
common directory under the current AGENTS.md instruction; reviewers are
read-only. Full Claude/container acceptance remains unrun.

```mermaid
flowchart TD
  M[Read-only monitor] -->|Reads visible progress| P[Parent: sole writer]
  P -->|Exact source and receipt packet| L[LSan runtime specialist]
  P -->|Exact branch and review packet| H[Handoff integration specialist]
  P -->|Exact contracts and gates| C[CLI and Context7 acceptance specialist]
  L -->|ACK and findings| P
  H -->|ACK and findings| P
  C -->|ACK and findings| P
  P --> W[One implementation writer]
  W --> R[Independent reviewer in a freed slot]
  R --> V[Named checks and retrospective]
  V --> D[Authorized serialized integration and delivery]
```

## Parallel specialist execution

The user's 2026-10-13 request authorizes task-matched subagents. This session
has four concurrent slots including the parent, so use at most three workers.
Start with bounded read-only lanes; reserve a freed slot for cold review.
Nested teams do not increase that shared capacity. The selected
[execution record](../../.planning/2026-10-10-marketplace-macos-reflection-scaffold/parallel-specialists.md)
names exact agents, requested models, source identities, tools and results.

Use GPT-6.1 Sol with high effort for complex integration, contract analysis and
independent review; use GPT-6 Astra with high effort for the ambiguous native
runtime problem. Use GPT-6 Luna for bounded receipt/hash extraction that can be
checked mechanically. These are task-specific choices, not benchmarked optimality.
Reassess effort when a packet becomes routine. Each model override starts with
a fresh, narrow packet instead of inheriting the full parent history. Do not
change global settings or infer the backend's served identity from a request.

Workers get exact HEADs, input paths, a read-only tool scope, expected output,
stop conditions and the `/root` reply channel; require an ACK and status probe.
Select inventory fields before printing them; container IDs, state and scoped
ownership fields are enough for the initial census. Keep full private metadata
outside the shared transcript and repository.
Only the parent writes implementation, shared planning and Git state. Keep
compiler/OCI/provider runs behind their existing admissions, one heavy operation
at a time. The user-approved
[acceptance-frontier correction](../../.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/acceptance-frontier.md)
lets A06 resume after actionable defects in completed units are verified.
Future runtime gates hold only their actual dependents. Offline milestones
must pass source integration and their own checks before dependent work starts;
GitHub ticket-level blockers remain unchanged until separately amended.

## Ownership

Workers share this filesystem, own no files, and must preserve all edits. The
parent owns project implementation and the one selected plan. Workers report via
native collaboration, acknowledge identity/objective/first action, and answer a
status probe before their handoff is counted as live. No sidebar chats are created.
Worker identities and review receipts are recorded in the selected plan.

## Initial onboarding admission snapshot

Prior read-only Docker census stalled; container ownership is unknown. START
explicitly admits only lightweight project work and read-only reviewer lanes.
These lanes request no Docker, port, cache, build or installation capacity. All
host-heavy work remains blocked until a fresh census and shared-capacity check.
Never terminate unknown services or infer capacity from the absence of evidence.

At START, global settings/hooks/trust/credentials, other repositories, native
goals, global mise and remote publication were outside the onboarding milestone.
Later work follows its separately recorded selected-plan authority and gates.

## Recovery

Read `.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md`,
`findings.md`, and `progress.md`. Verify actual Git identity before resuming.
Use at most five maintained files and about 300 handwritten lines per unit;
record implemented, reviewed, tested, committed and published states separately.

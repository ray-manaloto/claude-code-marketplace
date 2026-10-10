# Native Codex onboarding

PLAN_ID: `2026-10-10-marketplace-macos-reflection-scaffold`
Plan owner and sole implementation writer: parent Codex chat.
Project root: `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace`.
Set `PWF_PLAN_ROOT` to that root and `PLAN_ID` above for commands launched elsewhere.

## Objective

Qualify native Codex onboarding while preserving the Claude marketplace and OCI
acceptance contracts. The accepted product direction is incremental migration
to a native C++26 P2996 research core; build/toolchain work follows onboarding.

## Small units

Each unit has one purpose, at most about five maintained files and 300 handwritten
changed lines. Generated evidence is checked mechanically. Settle each unit's
acceptance before expanding it; parent writes, workers inspect and review.

| Unit | Deliverable | Gate | State |
| --- | --- | --- | --- |
| N0 | Ownership, plan, live bounded team | Identity, source hashes, worker ACKs | Complete |
| N1 | Root/scoped guidance and accepted decisions | Source comparison; documentation review | Complete |
| N2 | Necessary project Codex config and roles | Exact CLI schema; merged transports; role loading | Complete |
| N3 | Separate development commands | No install/bootstrap; lightweight checks; OCI bytes preserved | Complete |
| N4 | Fresh-session qualification and handoff | Worktree and unrelated-cwd probes; cold review | Complete |

## Acceptance required before completion

- Exact checkout/branch/HEAD and source provenance recorded.
- Fresh read-only sessions load project guidance using native project selection.
- Configuration and roles validate against the installed CLI, currently 0.162.1.
- Available global skills/plugins reused without copying Claude lifecycle behavior.
- Lightweight checks record actual exit codes; independent findings are dispositioned.
- Existing acceptance inputs remain unchanged; full OCI execution is explicitly pending.

## Admission and later work

Only project-local lightweight work is admitted. Global settings, hooks, trust,
credentials, model defaults, global mise, other projects, installs, containers,
heavy builds, publication and destructive cleanup are outside this milestone.
No native goal was requested. Monitor chat owns no marketplace files.

After N4, continue the source matrix's small tasks: template reuse qualification;
then a separately admitted global tool foundation and TCPM trial; compiler,
vcpkg, preset, analysis and package qualification follow their recorded edges.
Do not treat source-backed tool pins or 96 candidate trees / 384 cells as runtime
qualified. Preserve all inherited research failures.

## Evidence

See `findings.md`, `progress.md`, and `docs/agents/codex-task-orchestration.md`.
Historical handoff sources stay immutable in the source checkout and original
research directories. New receipts belong only to this worktree.

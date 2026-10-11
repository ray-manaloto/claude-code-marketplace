# Project handoff

Updated 2026-10-10. PLAN_ID: `2026-10-10-marketplace-macos-reflection-scaffold`.
The parent Codex chat is the sole project writer; monitor
`01a122d7-dfe6-72c3-ab32-823fadb96690` is read-only. Native inspection/review workers
own no files. See the [team contract](agents/codex-task-orchestration.md).

## Identity and current state

- Worktree: `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace`.
- Branch: `codex/marketplace-native-onboarding`.
- Source HEAD: `6b5b092efa6bdf678815073db42f69fae3f07ab3`.
- Common Git directory: `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git`.
- N0–N4 implemented, independently reviewed and locally qualified.
- Onboarding checkpoint: `67bd4827532864ecb934050dde6c0c11b92f9939`; clean
  post-commit worktree and baseline check exit 0.
- Cold review passed after one receipt-minimization finding was fixed/rechecked.
- Delivery is local checkpoint commits only; no publication. Read actual
  HEAD/status before resuming; dated receipts identify their tested snapshots.

New files provide root/scoped guidance, accepted decisions, native project roles,
an explicit development wrapper, the [task index](build-roadmap.md) and sanitized
[evidence](../evidence/onboarding/README.md). All 19 original tracked files match
their baseline. Current development checks require only already installed tools.

## Limits and next action

The initial startup probe missed four bundled MCP endpoints. This is recorded;
a corrected startup-only probe loaded the project with no MCP startup notifications.
Direct protocol evidence separately qualifies custom-role assignment/completion.
Global Codex config/hooks remain unchanged. The inherited chronicle warning and
the read-only research-guard limitation are preserved.

Full Claude/OCI acceptance, MCP connectivity and provider research are unqualified.
Existing research gaps are Context7 quota, Firecrawl 402/provisional fallback and
Last30Days validation. No native core, qualified compiler, vcpkg or application
build matrix exists yet.

Task 01 passed: pinned source/license acquisition and the four-file
[scratch adaptation](../scratch/template-reuse/README.md) have independent
reviews and passing static/baseline checks. Native CMake preset listing now passes;
compiler configuration and builds remain pending.

Task 04a passed: the [prepared profiles](../dev/global-mise/README.md) and native
named locks have 35 bounded controls and a passing independent cold review.
The proposal is committed at `a07f40c` and preparation evidence at `605cb8d`.

Task 04b applied seven new named files and installed only CMake 4.4.4 and
sccache 0.18.0; Ninja 1.13.2 was reused unchanged. Native installation exited 0.
The [host checks](../evidence/tool-foundation/host-qualification.json) pass:
managed paths, ARM64 support, versions, profile environment controls and native
preset listing. Default config/lock bytes, compiler settings and PATH match the
pre-apply state. Independent application review passed after two recording fixes.

Task 02 passed at `ad6b63bc732afdd119262849b7873712b5d917a4`: the
[TCPM trial](../scratch/tcpm-trial/README.md) generates three trees and twelve
cells reproducibly; native CMake accepts all four preset kinds and rejects
invalid workflows. Independent review reproduced the checked-in JSON. Python
3.14 failed during generation; the successful private Python 3.13 environment
uses the same generator source and leaves global Python unchanged.

Task 05a passed: exact GCC package/source inventory and the
[native snapshot plan](../dev/toolchains/README.md) have independent review.
Both native runs resolve eight captured formulae to four missing bottles and
reject missing GCC metadata. These preparation checks do not qualify a compiler.

Task 05b has verified four downloaded archives and enumerated their prefix
writes. Two shared debugger directories require native expansion while
preserving GLib. External global tool updates triggered a preimage stop; fresh
private baselines preserve those updates. Independent preparation review passed
after parent/control preimages were completed. The later installation operation
requires fresh package-writer, exact-preimage and native-plan checks.

Task 05c installed GCC 16.2.0, ISL 0.28, MPFR 4.2.2 and libmpc 1.4.1 through
native mise after those checks. All command exit codes are 0; planned links,
GLib preservation and unchanged global/default environment checks pass.
Independent [installed-state review](../evidence/gcc-bootstrap/postinstall-review.json)
passed. No compiler has executed yet;
reflection and runtime qualification are the next focused unit.

The earlier Docker census found no running containers, but high host
load and concurrent shipping leave heavy builds unadmitted. Global Python
promotion/telemetry and other repositories remain separate streams.

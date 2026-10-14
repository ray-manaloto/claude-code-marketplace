# Check the exact borrowed runtime before research launch

Status: local spec; user confirmed behavior and test seam on 2026-10-12.
Tracker publication pending qualified project operations; no readiness label applied.

## Problem Statement

A refresh discovers an unusable SSL or GitHubKit dependency only after entering
the credential/provider launch route. The resulting attempt lacks an explicit
preflight stage and can be mistaken for a provider failure.

## Solution

Before fnox or GitHub queries launch, check SSL and GitHubKit imports with the exact
borrowed interpreter. Record an unavailable-runtime receipt and stop if it fails.

## User Stories

1. As a research operator, I want the exact borrowed interpreter checked, so that another Python cannot mask the defect.
2. As a research operator, I want SSL import checked, so that missing native libraries are found early.
3. As a research operator, I want GitHubKit import checked, so that SDK unavailability is explicit.
4. As a reviewer, I want the preflight exit retained, so that unavailable runtime has direct evidence.
5. As a research operator, I want fnox withheld after failure, so that a known unusable runtime does not launch research.
6. As a research operator, I want provider queries withheld, so that no provider attempt is invented.
7. As a runtime owner, I want no repair or installation, so that ownership remains intact.
8. As a reviewer, I want executable identity retained, so that the check binds the actual runtime.
9. As a research operator, I want accepted history preserved, so that preflight failure cannot erase evidence.
10. As a reviewer, I want a healthy control, so that the preflight demonstrably permits normal launch.
11. As a research operator, I want timeout recorded, so that the health check stays bounded.
12. As a reviewer, I want credentials excluded from evidence, so that diagnostic receipts remain safe.

## Implementation Decisions

- Bind one exact interpreter for both imports; retain its identity and separate preflight stage outcome.
- Check imports in a bounded subprocess without provider requests, credential injection or bytecode writes.
- On failure, retain diagnostic output and runner failure while preserving accepted baseline, query history and catalog.
- No automatic fallback interpreter, retry, install or borrowed-environment mutation.
- Healthy preflight continues through the existing fnox route without changing credentials or tool pins.

### Runtime binding

- Select the existing borrowed project's virtual-environment interpreter, not
  the base interpreter launching this workflow. Bind its resolved identity,
  virtual-environment metadata digest and installed SDK metadata/version.
- Run isolated, bytecode-disabled imports in the new cycle directory, after
  cooldown/catalog validation and before credential launch. Run once per attempt
  with a dedicated ten-second bound, separate from the provider timeout.
- Reject conflicting inherited virtual-environment/project-environment overrides;
  stop rather than repair or silently select another runtime.
- Retain pre/post runtime metadata digests around native stages. Any detected
  borrowed-environment drift prevents acceptance and reports the violated binding.
  This is a diagnostic guard, not permission to mutate the borrowed environment.
- Verify no-sync/no-dependency launch semantics before native admission; do not
  rely on a post-run digest to prevent an unauthorized synchronization.
  Admission evidence is the installed task-runner help defining no-dependency
  behavior, the borrowed task's read-only launch definition, and installed uv's
  no-sync option/environment contract. The runner argument/environment test binds
  those controls. Retain their version/receipt references before native execution.
- Enforce the documented GitHubKit 0.16.1 pin without repair. Import failure,
  identity/SDK mismatch or conflicting overrides stops before launch. Preserve
  provider cooldown when no provider stage was invoked; record the failed attempt.
  Store expected SDK version and preflight timeout in private workflow policy;
  changes require a recorded operator decision, never automatic accommodation.

## Testing Decisions

- Use the same runner boundary as spec 01: exit, receipt, evidence and state.
- Inject SSL failure, SDK failure and timeout; assert zero credential/provider command invocations.
- Test healthy preflight followed by normal launch and later launch failure.
- Run the read-only preflight against the existing borrowed interpreter when qualified; report its actual outcome.
- Reuse project A01 health-check intent without duplicating its environment ownership.
- Exercise the actual preflight subprocess with synthetic executables for healthy
  identity JSON, import failure and timeout; verify its process group is gone.
- Test real launch argument assembly beneath the command wrapper without executing
  fnox; assert the command separator, isolated runtime, bounded wait and no-sync env.
- Include conflicting override and runtime-metadata drift controls. Entire-command
  mocks alone do not qualify the runtime binding or process cleanup.

## Out of Scope

Global Python/OpenSSL repair, SDK upgrades, credentials, network health checks,
new interpreter selection, changes to the borrowed repository and schedule changes.

## Further Notes

A project environment check does not qualify a different borrowed interpreter.
Unavailable-runtime evidence establishes a blocker, not a provider quota result.

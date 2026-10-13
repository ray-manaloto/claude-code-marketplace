# Share the complete reusable refresh workflow

Status: implemented, independently reviewed, locally checked and published on
`codex/research-feedback-retro`. Source commit `2beaba6b5b609a481ac3cc62d17cbe6a64cbc1cc`
was pushed and independently matched to the remote tip on 2026-10-13 at 04:45:36 UTC.
See the [publication review](../publication-review.md) for evidence and limits.
Tracker publication and peer-authority changes remain separate operations.

## Problem Statement

Other sessions can reuse the shared feedback/outcome helpers after fetching the
integration branch, but the accepted refresh runner, runtime safeguards, tests
and latest operating lessons still exist only in local state storage.

## Solution

Publish the complete reusable package on the existing integration branch. Require
explicit local runtime configuration and a separate state directory, preserving
the accepted research and admission contracts. Keep live state and diagnostics local.

## User Stories

1. As a session owner, I want all reusable changes available through Git, so another worktree can obtain them.
2. As an operator, I want explicit local paths, so copying source never selects another machine's runtime.
3. As an operator, I want separate state storage, so refreshes cannot write into tracked source.
4. As a runtime owner, I want existing pins and preflight guards preserved, so portability does not grant installation or repair authority.
5. As a reviewer, I want the complete offline suite, so packaging cannot silently omit runtime controls.
6. As an operator, I want portable policy/catalog examples and guidance, so local setup is explicit and inspectable.
7. As a reviewer, I want imported source provenance and sanitized lessons, so implementation history remains distinct from new qualification.
8. As a branch owner, I want a verified remote tip, so rebase instructions refer to published commits.

## Implementation Decisions

- Reuse the existing integration branch and all eleven previously unpublished commits.
- Transfer the seven accepted source/test modules; record exact input hashes.
- Keep runtime preflight, native task contract, SDK/tool pins, coverage eligibility,
  cooldown, immutable history and recovery behavior intact.
- Add required explicit state/runtime configuration at the CLI boundary. Reject
  incomplete or invalid configuration before locking, writing or native launch.
  Keep state outside this checkout and the borrowed runtime.
- Local configuration names existing paths; it contains no credential values.
  Credential injection remains the fixed native fnox profile and mise invocation.
- Import policy and catalog definitions as examples, not active state. Retain the
  validated/observed/provisional distinctions in generalized lessons.
- Extend the existing development check to discover the complete imported suite.
  Do not introduce a second test framework or an implicit live runner.
- Parent remains the sole implementation writer. Small new handwritten changes
  are reviewed separately from mechanical source/test transfers.

## Testing Decisions

Use the existing runner-boundary tests plus CLI/configuration controls for missing,
invalid and relocated paths. Test that invalid input cannot write or launch; verify
the exact fnox/mise argument contract. Run all imported tests and existing shared
tests from the reusable checkout with no provider or credential calls. Run normal
development checks and the original 19-file acceptance baseline. Independently
review correctness and preservation of the accepted scope before publication.

## Out of Scope

Live state, raw search results, credential values/bindings, admission receipts,
automation activation, new installs, peer edits, tracker publication and merging
another owner's branch. The native C++ product direction is unchanged; this is
an explicitly invoked development workflow, not a replacement research core.

## Further Notes

The user explicitly confirmed the full reusable package after the private/shared
gap was explained. Existing glossary terms apply; this reversible publication
does not warrant a new domain term or ADR. Provider gaps remain visible and do
not become full coverage merely because the code is published.

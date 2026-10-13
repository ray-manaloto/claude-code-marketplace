# Portable refresh publication review

The complete reusable RF1/RF2 runner, its tests and the latest operating lessons
are implemented and locally qualified for publication. The earlier eleven commits
remain on `codex/research-feedback-retro`; this unit starts at `208a57bc`.
Commit, push and exact remote verification remain delivery steps.

The [setup guide](../../dev/research_refresh/README.md) requires explicit local
runtime and state paths. [Provenance](portable-provenance.json) binds all nine
transferred inputs and the final source files. Live state, raw diagnostics,
credentials, admission records and schedule activation remain local.

## Verification

Using existing Python 3.14.8, all commands exited 0:

| Command | Observed result |
| --- | --- |
| `./dev/mise tasks validate` | Five tasks validated |
| `./dev/mise run check` | 31 shared tests and 87 portable tests passed |
| `./dev/mise run check:acceptance-baseline` | Both suites passed; all 19 original hashes matched |

The final source bytes match the reviewed candidate. New boundary regressions
failed before their repairs and passed afterward. This is local offline/static
qualification; provider, new-machine, fresh-session and OCI acceptance are not
established by these checks. Hosted development CI runs on PR/manual triggers,
so a branch push alone is not hosted CI evidence.

## Standards

Independent review found no hard violation and one possible duplicated-code
judgment: the new configuration parser repeated an existing strict JSON hook.
The configuration now reuses that hook and adds its own error context. Focused
re-review found no remaining standards or code-smell findings, including the
final path-separator guard, tests and documentation.

## Spec

Independent review found a P2 uv-selection defect: checking a renamed executable
did not ensure that the native task's PATH selected that executable. Requiring
the selected name `uv` fixed that case. Re-review caught a separator-containing
parent path with the same effect; it is now rejected in the selected path's
spelling. Positive controls preserve safe symlink aliases, including a safe
alias whose resolved target directory contains a separator.

Runtime aliases also retain their admitted spelling while containment checks
resolve symlinks. Source transfer, coverage guards, original acceptance hashes
and the publication boundary were independently checked. Final focused review
reported no remaining specification findings.

## Retrospective dispositions

- P2 automated checks: imported fixtures assumed private defaults or the old CLI.
  Explicit synthetic selections and required arguments repaired the fixtures;
  the existing assertions and complete discovery remain intact.
- P2 executable selection: basename and PATH-separator failures now have maintained
  negative controls plus exact-selection and alias positive controls.
- P3 maintainability: duplicate JSON handling was removed using the existing hook.
- P3 tool economy: large tool responses are filtered before output. The operating
  guide calls for compact receipts, selected details and bounded document reads.
  No measured performance improvement is claimed.

Existing development CI already runs the normal check; extending that check
made the full imported suite part of the guard. No new global steering file,
parallel test framework or architectural decision was needed. The temporary
writer handoff preserved both owners' work and serialized repository changes.
External research gaps remain deferred rather than being relabeled as fixes.

## Tools and evidence limits

The grill-with-docs workflow used the inherited grilling and domain-modeling
guidance; existing decisions and the user's full-package confirmation supplied
the scope. Writing-for-agents, two-axis code review and retrospective guidance
were applied. Native Git, installed Python, the development mise wrapper and
read-only specialist agents supplied local evidence. The initial test failures,
both uv counterexamples and their repairs remain in local verification receipts.
Installed gitleaks 8.30.1 scanned the 23 proposed publication files with zero
findings and exit 0. The initial development-wrapper lookup exited 1 because the
installed tool was inactive there; its existing executable was selected directly
without changing activation or installing anything.

The required research used native fnox and mise research-fanout with Exa,
Firecrawl, Last30Days, Context7 and GitHub. The first preparation attempt exited 2
because its explicit Last30Days plan was missing; the corrected run exited 0.
Firecrawl Search returned HTTP 402 and Serper supplied a provisional substitute.
The [sanitized research receipt](publication-research.json) preserves every route
and ten raw-artifact hashes. Official mise, uv and unittest docs were checked.
This result remains provisional; it does not establish native five-provider
coverage. The active borrowed runtime was neither repaired nor reactivated.

Remaining review findings: Standards 0, worst none; Spec 0, worst none.

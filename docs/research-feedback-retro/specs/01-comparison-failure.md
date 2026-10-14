# Preserve acceptance state when comparison fails

Status: local spec; user confirmed behavior and test seam on 2026-10-12.
Tracker publication pending qualified project operations; no readiness label applied.

## Problem Statement

An ordinary refresh can report success after snapshot comparison fails and advance
query history. A later refresh can therefore compare against unaccepted evidence.

## Solution

Every failed comparison produces a failed refresh outcome, retains the new raw
snapshot and failed-attempt receipt, and preserves the accepted comparison baseline
and query history. A later successful comparison uses that preserved baseline.

## User Stories

1. As a research operator, I want comparison failure to return failure, so that scheduling reports the actual outcome.
2. As a research operator, I want raw snapshots retained, so that failures remain diagnosable.
3. As a reviewer, I want the native comparison exit recorded, so that a wrapper cannot hide failure.
4. As a research operator, I want the accepted baseline preserved, so that the next comparison remains trustworthy.
5. As a research operator, I want query history preserved, so that failed comparisons cannot reset coverage history.
6. As a reviewer, I want ordinary and proposal refreshes treated consistently, so that both enforce acceptance.
7. As a research operator, I want promotion withheld on failure, so that the catalog stays unchanged.
8. As a reviewer, I want retained stdout and stderr identified, so that evidence can be inspected.
9. As a research operator, I want a first refresh to establish a baseline without an invented comparison, so that initialization works.
10. As a reviewer, I want the next successful refresh tested after failure, so that retention is more than a one-run assertion.
11. As a research operator, I want failed attempt metadata kept separately, so that the last accepted outcome stays visible.
12. As a reviewer, I want cooldown and immutable snapshots preserved, so that failure does not trigger uncontrolled retries.

## Implementation Decisions

- The private refresh runner owns this behavior; the public GitHubKit transport remains peer-owned.
- Pin comparison to the accepted comparison baseline, rather than a mutable latest-snapshot pointer.
- Record comparison exit separately from search exit and runner exit. A failed stage cannot yield runner success.
- Preserve baseline, accepted query history and canonical catalog on comparison failure; attempt metadata and cooldown may advance.
- Retain fresh raw snapshot evidence even when acceptance fails. Do not retry comparison automatically.
- Preserve existing coverage and promotion checks; this change does not certify capped or empty observations.

### Baseline resolution and evidence durability

- Record an explicit accepted-baseline identity and manifest digest. Resolve it to
  exactly one immutable run with verified artifacts; missing, corrupt or ambiguous
  evidence fails closed and never silently establishes a replacement baseline.
- Migrate legacy acceptance only after matching its state identity to a retained
  successful receipt and valid immutable snapshot; record that migration evidence.
  Only an empty accepted history permits first-baseline initialization.
  A blocked migration is a standing blocker: restoring verified evidence or a
  separately approved recovery specification is required. This slice adds no reset command.
- Keep the latest-observation pointer separate for freshness checks. A rejected
  snapshot cannot satisfy freshness merely because it differs from the old baseline.
  Update latest-observation metadata for every retained raw snapshot, including
  rejected observations; freshness compares against that latest observation.
- Every post-cycle validation/lookup exception produces a failed-stage receipt
  when storage remains writable. Storage failure returns nonzero and leaves an
  explicit incomplete cycle; do not promise successful receipt creation on disk failure.
- Comparison failures use runner exit 2 and record the actual comparison exit,
  stdout/stderr references and digests separately from native search outcome.
- Persist receipt, then cycle-identified learning event, then acceptance state.
  Only the final state pointer commits acceptance. Orphan evidence/events never
  advance a baseline; retries/recovery must detect cycle IDs rather than append twice.
- Before invoking a provider stage, persist an incomplete attempt-start receipt
  and cooldown/attempt metadata without changing acceptance fields. Terminal
  acceptance retains receipt/event/state order. Interrupted attempts honor the
  persisted cooldown. Preflight failure before launch never advances it.
- Acceptance-state write failure leaves the prior pointer intact. A cycle with
  missing terminal receipt/state binding is incomplete, never accepted.
- Coverage history and baseline eligibility are separate. An otherwise valid
  unverified-empty observation may advance coverage streaks and returns exit 2,
  but cannot replace the accepted baseline or authorize NEW/GONE claims.
  Comparison failure preserves both prior coverage history and baseline.
- Receipts distinguish attempt_status: accepted, accepted_with_coverage_warning,
  failed, incomplete; failed_stage identifies the failing operation. Exit 2 alone
  cannot distinguish a coverage warning from comparison failure.
- Native success requires valid stdout, a fresh bound result set and verified
  immutable artifacts. Comparison success requires its own valid outcome evidence,
  not exit zero alone. Suppression and coverage warnings are recorded explicitly;
  they do not certify content-change eligibility. Proposal failures never promote.

## Testing Decisions

- Use the agreed runner boundary: actual runner exit, receipt, retained evidence and state in a temporary workflow.
- Inject search success followed by comparison failure for ordinary and proposal runs; assert unchanged acceptance state and catalog.
- Follow the failure with successful search/comparison and assert use of the old accepted baseline.
- Check first-run initialization and timeout/nonzero comparison controls.
- Existing private failed-attempt tests and public collection failure controls provide prior art.
- Add stale/invalid manifests, missing/ambiguous baseline directories, receipt/event/
  state write failures, migration binding, and next-run recovery controls.
- Assert actual comparison arguments and diagnostic references; malformed evidence
  must return failure with prior acceptance intact, rather than reset the baseline.
- Existing failed-attempt tests are offline prior art; their patched path is not
  live-qualified. Separate native runtime checks from mocked behavior evidence.
- Test coverage warning versus comparison failure side by side: only the former
  advances coverage observations; neither accepts an unverified-empty baseline.

## Out of Scope

Public transport changes, broad baseline eligibility redesign, new queries, runtime repair,
global settings, schedule changes, tool installation, pushes and merges.

## Further Notes

Coordinate with A05b's comparison receipt contract. Retain historical snapshots unchanged.
Implementation and publication are separate statuses.

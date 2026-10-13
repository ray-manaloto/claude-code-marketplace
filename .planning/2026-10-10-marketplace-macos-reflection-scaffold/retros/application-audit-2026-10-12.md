# Completed-ticket retrospective action audit — 2026-10-12

This is the original audit snapshot, transferred byte-for-byte from the
retained checkout before this current-status addendum. Its "pending" and
"unstarted" statements below describe that snapshot, not the source tip.

Scope: the locally completed W4 tickets #12/#24/#25 and W5 slices A01, A02,
A04, A03a, A03b, A05a and A05b. A06 is in progress and has no retrospective
gate yet. The earlier N/build rows are plan units, not tickets in the W4/W5
tracker. This audit distinguishes a written retro from an applied action.

The ten individual records in this directory contain source/receipt anchors,
severity-ordered findings, verification and frontier reassessment. An
independent read-only audit found no missing record. The final-source local
`check:research` command exited 0 after the A06 catalog fixture repair,
including the A01–A05 regression suites and 19 preserved baseline hashes;
`./dev/mise tasks validate` exited 0 for 23 tasks and `git diff --check`
exited 0. These are local checks, not hosted or native acceptance.

| Retro | Local actions applied and checked | Open action or accepted boundary |
| --- | --- | --- |
| [A01](A01.md) | Project `.mise`, locked dependency/import probes, skip-depends refusal and onboarding pointer; bootstrap seven and `check:research` pass. | A12a hosted fast CI after A09 publication remains pending. |
| [A02](A02.md) | Full HTTP replay envelope, credential-route isolation and public 503 refusal; one-page seven and `check:research` pass. | A12a hosted fast CI remains pending. |
| [A03a](A03a.md) | Private-result withholding, retained error envelopes, timeout/short-page/rate-limit controls; collect twelve and focused review passed. | A12a hosted fast CI remains pending. |
| [A03b](A03b.md) | Post-response deadline, replay exhaustion and distinct controls; control six and focused review passed. | A12a hosted fast CI remains pending. |
| [A04](A04.md) | Run scanning, bounded lock, atomic quarantine, reset barrier and A03 split; catalog nine and focused review passed. | No additional retro action beyond the separately gated graph. |
| [A05a](A05a.md) | Hash-checked selected data/inventory and post-preflight drift refusal; compare seven and focused review passed. | Per-query lock and stale-delta refusal were delivered by A05b. |
| [A05b](A05b.md) | Bounded writer lock, post-collection recheck, per-row all-mode admission and provisional A06 wording; publish six and focused review passed. | A06 classification is a new, unfinished ticket; no full search inventory exists. |
| [#12](issue-12.md) | Failed LSan closure is retained with native rc 1, runtime timeout and free lease; no sanitizer pass claimed. | #13 private repair needs separate host-heavy admission. A09 outbound scan/commit gate and A12b issue-state reconciliation after A09 remain pending. |
| [#24](issue-24.md) | Pinned KB source/installed-module identities and synthetic dispatch scope are in the boundary document and review. | #28 versioned CLI acceptance, A10 checkout-transfer inventory and A12b hosted/OCI acceptance mapping remain pending. |
| [#25](issue-25.md) | Reversible helper placement, ten successful and two deliberate failing synthetic samples and review are retained. | #29 Context7 bridge, #30 typed child-process/failure mapping, A10 path inventory and A12b acceptance mapping remain pending. |

The open actions above are not silently satisfied by retrospective prose. A09
is an unstarted, separately qualified Git mutation; A10, A12a and A12b have
prerequisites in the [local amendment](../automation-amendment-draft.md).
#13/#28/#29/#30 are separate published issues, not completed retrospective
fixes. The user's clarification admits these named retrospective remediations
in prerequisite order while holding A06 and unrelated new-ticket work; A06
work in progress is preserved and paused.

The mandated strict-five-v2 research attempt for this audit is at
`~/.codex/research-coverage/01a130ef-265d-72b0-8465-80f3e4128bee/01a1317e-1c1d-7d00-8210-31ddbc146f5a/manifest.json`.
It exited 1: GitHub Discussions was `empty_unverified` because its canary
returned zero; Context7 exited 1 with quota text in its raw receipt;
Firecrawl Search returned HTTP 402 and used
the provisional Serper route. GitHub Issues/Releases were verified empty;
Exa, Firecrawl Developer and Last30Days returned results. This is
`RESEARCH INCOMPLETE`, so no five-provider endorsement is claimed. Primary
local ticket receipts and source files determine the action statuses above.

## Source-branch addendum

At source HEAD `111424b05fbe93342bfd3f31c3f430a91620e060`, A09's
SHA-bound publish path, A10's transfer inventory, A11's manual source
handoff, A12a's hosted fast check, and A08b2's 67-child/139-edge label
graph are published and verified in the selected plan. A11's guarded switch
returned `rc=2` on an unexpected `.venv`; manual reconciliation, not guard
success, qualified the physical transfer. The ten original retrospective
records linked above retain their historical findings and evidence.

A06 remains paused by the user hold; therefore A12b, which depends on A06,
has not been assembled. #13's preparation and #29's offline Context7
measurement each passed focused re-review, but native LSan admission and
live/confined Context7 qualification are still open. #28's offline reference
fixture received an inherited `KB_EVENTS_JSONL` side-effect fix that passed
focused re-review; public v2 and OCI acceptance remain open. #30 is a
separate native child-process contract ticket. None of #13/#28/#29/#30 is
marked complete by these preparatory reviews, and their GitHub issues remain
OPEN at the last read. The source protocol transfer and archival audit passed
local static checks and independent archival re-review. Commit and any
separately authorized publication remain pending.

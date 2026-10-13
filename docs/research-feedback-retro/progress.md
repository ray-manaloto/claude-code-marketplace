# Research feedback sharing retrospective

Owner: this isolated retro worktree. Base: `b136d75f6809a53381de0dfba1fd61da8e705796`.
Protected peer: `01a130ef-265d-72b0-8465-80f3e4128bee`; its checkout,
branch, active plans, draft specifications and runtime are not changed here.

## Unit 1: offline feedback guard

Implemented a portable, dependency-free development helper, regression controls,
an explicit mise replay/check task and integration with the existing check command.
No live runner, transport, credentials, catalog, private learning state or cadence
is copied or changed. The peer already owns unified GitHub search implementation;
this unit shares a bounded feedback component for that work.

Actual gates in this worktree:

- `./dev/mise tasks validate`: exit 0, four tasks.
- `./dev/mise run check:research-feedback`: exit 0, 12 offline tests after repair.
- `./dev/mise run check:acceptance-baseline`: exit 0, all 19 originals preserved.

Independent read-only review found a replay envelope mismatch that could reset
nonempty history. Fixed it and added a chained CLI regression; re-review cleared
the finding. Unit 1 is reviewed and tested, ready for a local commit.
Committed locally as `7d0c2fd`; it is not published. The private runner's earlier live batch
preceded its guard patch; these offline tests do not prove scheduled execution.

## Unit 2: discoverability and CI

Implemented input/output and integration boundaries, a short onboarding pointer,
and a lightweight CI workflow using the existing check entry point and the
existing checkout action pin. No installation or provider call is added.
Final baseline gate exited 0 with all 19 original hashes and 12 tests. Independent
static documentation/CI review found no findings. Both small units are complete
locally; Git history identifies their commits. Hosted CI is unverified.
The peer integration message supplies exact local commits and warns that its
concurrent `mise.dev.toml` changes need reconciliation. Its draft GitHub library
can reuse the feedback helper without adopting a second live-search runner.
No push or merge is planned. Parent plans and private research state are untouched.

# Refresh improvement workflow — 2026-10-12

The user confirmed comparison-failure baseline/history preservation, exact borrowed
runtime preflight before credential/provider launch, and sanitized shared outcome
behavior tested at the runner boundary. Three local specs and the RF1/RF2/RF3
ticket draft are prepared; ticket approval is pending. Glossary records the agreed
domain distinctions. No implementation or tracker publication occurred in this phase.
The protected peer's shared plan remains unchanged. A01/A05b overlaps are recorded;
qualified A07/A08 publication operations remain unavailable. Hook-requested research
fanout completed with native exit 1: GitHub Discussions canary-empty/unverified,
Context7 process-failed, and Firecrawl Search substituted by Serper after exhausted
credits. Exa, Last30Days and the other GitHub routes ran. Research remains incomplete;
the exact manifest is retained under the hook's request directory.

The user requested a Fable adversarial review before approving the ticket graph.
Installed Claude Code 2.1.296 advertises the `fable` alias. The claude-agent skill's
shared dispatcher launched one read-only safe-mode review with Read/Glob/Grep,
no subagents, no fallback model and a 600-second limit. Review disposition is
pending. The static baseline check exited 0 with all 19 original hashes intact;
diff whitespace also passed. No implementation, commit or publication occurred.

Fable completed: observed `claude-fable-5-1`, native/wrapper exit 0, completed
AgentReport, local schema validation passed. It reported 4 high, 7 medium, 3 low
and 1 informational findings. Source verification confirms missing transition,
baseline migration, binding, write-order and ownership details. Its claim that
stale-manifest failure was observed live is narrowed: the cited old failure was
native exit 1 with invalid stdout, before the current patch. Its proposed rule
accepting unverified empties as comparison baselines conflicts with the shared
coverage contract; that correction is surfaced for the user's decision.
Specs now draft bounded corrections and verification cases. RF3 split, coverage
acceptance and preflight pin/cooldown choices remain pending. Changes are not
implemented or re-reviewed; no review finding is claimed closed by a spec edit.

The user approved all three post-review choices: separate coverage observations
from comparison eligibility; RF3a/RF3b split; SDK pin enforcement with unchanged
cooldown before provider launch. Four per-ticket local records now exist. A fresh
focused Fable re-review is running on the revised contracts. RF1's managed worktree
and a frozen private scratch copy are prepared; implementation has not started.
Installed mise help confirms `--no-deps` skips automatic dependency providers.

Focused Fable re-review completed with native exit 0 and schema validation passed:
no high blockers, four medium and three low clarifications. These now specify
attempt/comparison statuses, admission evidence, pre-launch cooldown metadata,
fail-closed migration recovery, latest-observation metadata, policy pin location
and RF3b serialization. The reviewer explicitly requires no further spec-level
re-review before implementation; implementation/retro review remains mandatory.

Committed specs at `51fb42d16c06126eaa25e06bbd43f9bcad9c1265` and approved local
ticket graph at `20bf1200dc600203ff226758664a201dd5d482e8`. Both Fable receipts and
all reported artifact hashes independently verify. RF1 implementation is active
in its managed worktree/private frozen scratch, beginning with a bounded unit;
the parent remains the only live-private application owner. RF2 worktree preparation
is pending. Actual implementation acceptance and GitHub publication remain pending.

## RF1a bounded implementation and review

The frozen private candidate passes 21 offline tests; four red/green cycles cover
comparison failure/recovery, legacy baseline resolution, pre-launch attempt
persistence and malformed comparison envelopes. Parent and independent reviewer
verified two live preimages, two candidate postimages and eight test-log hashes.
Independent review requested changes: valid JSON with a non-object legacy receipt
escapes as AttributeError instead of producing a failed baseline-resolution
receipt. Repair and focused re-review are pending; strict artifact/diff-row binding,
coverage suppression and remaining storage controls stay in the next unit.

Unit retro actions are assigned to the same writer: runner-boundary wrong-root-type
controls, explicit worktree/common-Git identity, full-suite log digest and included/
deferred criteria in the revised receipt. Reviewer corrected its branch-attribution
claim after checking the worker checkout; codex/refresh-rf1 at 20bf120 is valid.
RF2's managed worktree is prepared. Read-only runtime exploration found pinned uv
0.13.0 versus PATH 0.12.7; admission must bind the pinned route and test conflicting
runtime selectors. No private live code application, provider launch or publication
has occurred in these implementation units.

RF1a re-review passed: list/null receipt controls now return 2 with a terminal
failed/baseline_resolution receipt and preserved acceptance. All 21 offline tests
passed independently; original and revised evidence hashes match. The parent froze
the reviewed RF1a candidate as the next unit's preimage. All actionable unit retro
findings are applied and verified. RF1b is active on artifact and comparison-row
binding. Selected-catalog fingerprint binding, coverage suppression and remaining
storage controls remain required before complete RF1 acceptance or live application.

RF1b independent review found and reproduced external ancestor/manifest symlink
acceptance and boolean diff-exit coercion. The writer added focused controls and
binding guards; re-review passed all 24 offline tests and five focused controls.
Both findings and all actionable retro items are resolved. The original evidence,
failed intermediate fixture attempt and revised logs remain preserved. The focused
repair added 63 lines; the combined unit grew to 351 lines without expanding its
purpose. The parent froze the reviewed files for RF1c; live files remain unchanged.
Read-only source compatibility review confirmed the narrow native serializer
contract. RF1c now binds catalog-derived fingerprints and effective queries while
preserving existing DISCUSSION discovery. Native fingerprints omit collection
bounds; later eligibility controls remain required and are not certified here.

RF1c independent review reproduced ordinary/proposal acceptance with a missing
required historical catalog. The writer repaired both paths; focused re-review
passed 27 offline tests with no findings. Missing catalog bytes now fail at
baseline_resolution, preserving catalog and accepted state without comparison or
promotion. Exact generated defaults source and test-log digests are recorded.
The parent verified and froze the 217-line reviewed unit; all actionable unit
retro items are applied. RF1d is active on native item/status validation and
coverage suppression. No live application or provider qualification has occurred.

RF1d1's initial 234-line candidate passed 29 offline tests, but independent review
reproduced cross-model extra fields influencing raw identity extraction. Ordinary
and proposal refreshes accepted forged NEW/GONE for an unchanged issue; the native
model ignores the injected field. The parent preserved the candidate and evidence.
Repair requires model-aware extraction and literal expected deltas independent of
the fixture helper. Repair/re-review are pending; coverage eligibility remains RF1d2.

RF1d1 repair re-review passed all 12 literal controls and 30 offline tests, both
exit 0. Native item projection ignores cross-model extras before extraction and
preserves modeled defaults. Original/revised receipts, source references and all
repair hashes match. The 58-line repair keeps the combined unit at 290 lines.
All actionable unit retro items are applied and verified. Parent froze the settled
candidate; RF1d2 now implements coverage suppression and recovery. Live application
and complete RF1 acceptance remain pending.

RF1d2 frozen candidate passes 33 offline tests with 267 changed lines. Parent
verified the receipt, pre/postimages, patch, seven logs and six source digests.
Independent runner-boundary review is active. The unit separates raw native delta
validation from per-query suppression and binds coverage-only initialization to a
matched warning receipt; it does not certify storage recovery. RF1e is planned as
three serial gates: guarded transaction rollback, receipt/event/state content
binding, then startup orphan recovery. No live application is admitted yet.

RF1d2 independent review and focused retro gate passed without findings. Both
maintained retro controls and all 33 offline tests exited 0. The test-only addition
kept the runner unchanged and the combined unit at 282 lines; repeated first-empty
warnings recover to healthy initialization without an invented comparison, while
malformed capped raw deltas fail before suppression. All actionable retro items
are applied. Parent froze the settled candidate. RF1e1 now starts guarded storage
ordering and promotion rollback; durability and live acceptance remain pending.

RF1e1 initial 280-line candidate passed 36 offline tests, but independent actual
writer-boundary controls reproduced two defects: post-replacement temporary cleanup
rolled back catalog bytes after acceptance state had committed; directory creation
outside the storage wrapper misclassified a write failure. Parent retained the
candidate, receipt and reproduction hashes. Focused helper repair, maintained
boundary controls and re-review are required before RF1e2. No live application.

RF1e1 focused re-review passed: both commit-boundary and storage-classification
findings are closed. The three maintained boundary subcases, independent rerun and
all 37 tests exited 0. Successful replacement has no subsequent temporary cleanup;
failed cleanup retains the original writer error. All actionable retro items and
fixture-input documentation are applied. The required 69-line correctness repair
brings this unit to 345 lines. Parent froze the settled candidate. RF1e2 now binds
receipt/event/state content; startup recovery and live qualification remain pending.

RF1e2a initial 236-line candidate passed 39 offline tests; independent review
reproduced an external append through a dangling event-file symlink and acceptance
of a modern traversal cycle/reference. Focused confinement/parser repair and
maintained ordinary/proposal controls are pending; original candidate is retained.
Read-only native source inspection also identified a whole-RF1 completion gap:
search stdout outer outcome/summary is not yet bound, and several mocks are
results-only. A bounded native-envelope validation unit is required before live
acceptance; this preserves genuine capped/empty warnings and native-error failure.

RF1e2a focused re-review passed both event-path findings. All 15 hash bindings,
39 offline tests and six independent ordinary/proposal controls passed. Confinement
precedes existence and append; modern identifiers/references cannot traverse while
legacy label bytes remain intact. Parent froze the 255-line settled unit and bound
the retained reviewer script/log. RF1e2b now verifies prior commit proofs; startup
recovery, native-envelope qualification and live acceptance remain pending.

Parent prepared RF2a in a separate private directory: a 205-line runtime-binding
and isolated import-process helper plus seven passing offline tests. Real synthetic
executables cover healthy imports, failure and timeout cleanup; selector, metadata
and identity controls remain credential-free. Initial fixture alias failures are
retained honestly. Independent helper review is pending. Runner integration,
no-sync launch admission and the actual borrowed-runtime check remain deferred.

RF2a independent review reproduced duplicate import-identity keys accepted as
healthy and unbounded post-kill pipe drainage through a detached descendant.
Parent retained the initial 205-line helper and reviewer evidence. Both maintained
controls failed against that exact source, then passed after repair; all nine
tests now pass. The 256-line revised unit rejects duplicate keys and bounds
post-kill drain/reaping, reporting incomplete cleanup without claiming escaped
descendants terminated. Focused re-review is pending; integration remains deferred.

RF2a focused re-review passed both findings. Twelve hash bindings, both maintained
regressions and all nine tests passed; independent timeout returned in 0.757 seconds
for a 0.5-second bound plus cleanup with leader reaped and incomplete-cleanup
status retained. All actionable retro controls are applied. Parent froze the
settled helper; RF2b integration and real borrowed-runtime qualification are pending.

Parent prepared RF3b as three frozen private drafts, 73 changed lines: a short
local pointer, staged peer-authority amendment and private-guide update. Six
installed skill links match their source digests. The standing five-stage workflow
requires every actionable retro item applied and reverified; research, ownership,
runtime and publication boundaries remain explicit. Documentation review is
pending. Protected authority and the active private guide remain unchanged.

RF1e2b initial independent gate failed three prior-proof controls despite all
41 tests passing: coverage proof missing after later failure, a retained modern
baseline relabeled legacy, and null native exit after a comparison-stage failure.
Parent retained the frozen candidate and independently verified reproduction
script/log hashes. Focused repair is admitted; startup recovery remains deferred.

RF3b independent documentation review passed correctness and accepted-contract
preservation: 28 hash/link/patch checks exited 0 with no actionable findings.
The 73-line three-document draft preserves ownership and publication limits.
Serial parent application is being prepared; peer amendment remains unapplied.

RF3b is locally reviewed, committed and integrated at `3dfa59d92a7d96e131d78ec6af0e3495f0678cec`.
The merger verified exactly two added docs, preserved parent planning bytes and
passed integrated development/original-19-file checks with exit 0. Parent verified
the merge receipt/log hashes. The private guide was atomically applied under the
exclusive refresh lock with exact preimage/postimage and unchanged peer authority.
All local RF3b criteria are met; peer application and tracker publication remain
pending. Whole-spec final review and worktree cleanup remain later phases.

RF1e2b focused functional review closed the original three findings and passed
42 tests, then reproduced two additional boundary defects: process creation
failure recorded invocation before launch and blocked next recovery; preparation
write failure could replace prior proof before validation. Parent retained the
revision and verified script/log/result hashes. A second focused repair is
admitted; e3 remains deferred. An earlier reviewer run ended in automated content
screening before disposition; the successful functional retry is the actual gate.

The RF2 implementer acknowledged ownership of separate private scratch and the
managed RF2 checkout. Its first bounded unit prepares launch assembly and metadata
bindings with offline subprocess-boundary checks; behavior integration follows a
separate gate. Active runner application remains serialized after settled RF1.

- RF2b native assembly/binding preparation: four private files, 148 changed lines; focused four and full 55 offline tests exited 0. Parent verified 21 file/evidence/source bindings. Independent gate pending; actual borrowed preflight, stage integration and provider launch remain unperformed. The existing fnox/mise route is retained.

RF2b independent offline review passed 22 bindings, four focused and 55 full tests, and independent synthetic controls with no findings. Matching-selector and entrypoint/runtime-drift controls are being preserved as maintained tests before final settlement; no real runtime parity is claimed.

RF1e2b revision2 independently closed both prior findings and passed 43 tests/eight original controls, but output-stream acquisition before Popen still misrecorded invocation and blocked healthy recovery. Parent retained exact revision2 plus verified five independent evidence hashes; third focused pre-launch repair admitted, with no startup-recovery expansion.

RF2b settled: independent test-only retro re-verification passed affected controls and all 57 unique tests, exit 0; production bytes stayed fixed. Parent verified four re-review artifact hashes and preserved the exact settled candidate. Assembly/binding only; runtime stage placement, final RF1 rebase and actual qualification remain pending.

Parent separately admitted and ran one exact borrowed-interpreter read-only preflight from the settled helper: isolated SSL/GitHubKit import exited 0, SDK 0.16.1/identity matched, pre/post metadata matched and process group was absent after exit. No credentials, provider, native task, installation or repair ran. This qualifies actual helper health only; full runner launch parity and stage integration remain pending. Private receipt: `rf2-readonly-preflight-qualification.json`.

RF1e2b settled after three focused repairs: independent review passed six focused/44 full tests, eight earlier proof controls and all boundary scripts with no findings. Output acquisition before launch and post-launch wait/close remain distinct; healthy recovery and prior-proof preservation are verified. Parent verified seven reviewer artifact hashes and froze the exact settled candidate. Combined 519 lines reflect required review repairs; no startup recovery was added in this unit.

RF2c1 runner preflight candidate is frozen: three private files/220 changed lines, eight focused and 65 full tests exited 0. New controls use actual synthetic preflight processes at the runner boundary and retain unavailable/native-failure evidence, accepted history and cooldown on ordinary/proposal paths. Parent verified 31 pre/post/evidence references. Independent gate pending; post-native stage binding and exact final RF1 rebase remain deferred.

RF2c1 independent review passed 65 tests and actual synthetic identity-mismatch controls, but malformed admission root containers escaped without a bounded terminal attempt. Parent verified five independent artifact hashes and retained the original candidate; focused container validation and corresponding ordinary/proposal history/retry controls are admitted before expansion.

RF1e3a initial independent review passed 45 tests/27 bindings but reproduced absent bound preparation/journal artifacts on committed cycles bypassing startup refusal. Parent verified five reviewer artifact hashes and preserved the original candidate; focused required-artifact validation and current/superseded controls are admitted. Genuine older absent-field history remains a limited frontier; rollback stays deferred.

RF2c1 settled after narrow container guards and persisted identity-mismatch retro: independent focused10/full67 and 14 additional runner controls exited 0 with no findings. Parent verified five review artifact hashes and froze the exact candidate. The earlier real preflight remains bound to its prior helper hash; revised helper/full native parity will require final qualification. Post-native guards and final RF1 rebase remain pending.

RF1e3a settled after required-artifact repair: independent four focused methods/46 full tests and missing-evidence reproduction exited 0, including maintained 32-case current/superseded controls. Parent verified five reviewer artifact hashes and froze the exact candidate. No findings remain in classification/admission; guarded recovery and deferred healthy retry remain e3b work.

- RF2c2 runtime guards are implemented and frozen: three private files, 224 changed lines; focused three and full 70 offline tests exited 0. Parent verified 30 source/preimage/postimage/evidence bindings. Guards surround existing search/diff calls, retain known exits and reject unknown completion, with bound unavailable-before-search proof and unchanged accepted baseline/catalog controls. Independent correctness/retro review is pending; final RF1 rebase and live qualification remain deferred.

- RF2c2 independent review verified 30 bindings, focused three/full 70 tests and an independent ordinary/proposal reproduction (all commands exited 0). It found P2 cross-attempt guard borrowing: a foreign unavailable-before-search record can satisfy a rehashed current proof despite an unknown post-invocation exit. Original evidence remains frozen. Repair must bind the guard and preflight to the current cycle and maintain both rejection/restoration paths before re-review.

- RF1e3b guarded recovery is implemented and frozen: two private files, 262 changed lines; focused three/full 47 offline tests exited 0. Parent verified 20 preimage/postimage/source/evidence bindings. Explicit recovery returns 2 with zero commands, preserves immutable prior receipts/events, restores only owned catalog/changelog bytes, and permits later healthy comparison against the retained baseline. Independent correctness/retro gate and native-envelope qualification remain pending.

- RF2c2 focused repair closed the cross-attempt proof gap: 107 repair lines/327 combined lines across the same three files. Independent review verified 39 bindings, focused four/full 71 tests and cross-attempt reproduction (all rc0), with no findings and every actionable retro control maintained. Parent verified all five reviewer artifacts and froze the settled candidate. Final RF1 rebase/native qualification remain pending.
- RF1e3b independent correctness review passed 20 bindings, focused three/full 47 tests and three independent recovery controls (all rc0), with no findings. Both actionable test-only retros are maintained in a 27-line delta/273-line combined unit; runner is unchanged, affected/full checks passed. Parent verified 22 revised bindings and froze the revised review candidate; focused retro re-verification remains pending.

- RF1e3b focused retro re-review passed both maintained controls, affected method and full 47-test suite (rc0), with no findings or scope expansion. Parent verified all three reviewer artifacts and froze the settled two-file candidate. Recovery gate is complete; strict native search-envelope validation remains the final RF1 internal unit before RF2 combination and live qualification.

- RF1 final native-envelope unit is implemented and frozen: two private files/194 changed lines; focused three/full 48 offline tests exited 0. Parent verified 33 preimage/postimage/source/evidence bindings, including six native serializer sources. Literal forged-success envelopes reject; genuine native failures retain their exits and capped/empty warnings remain distinct. Intermediate fixture corrections and historical provenance limits are retained in the receipt. Independent gate and final RF2 combination/native qualification remain pending. RF3a read-only preparation has started; its implementation still awaits prerequisite gates.

- RF1 envelope independent review passed focused three/full 48 tests and source bindings but reproduced an uncaught OverflowError for an oversized JSON timing integer in both modes, leaving an incomplete attempt and blocking healthy recovery. Parent verified six reviewer artifact hashes and retained the initial FAIL disposition. A local numeric-validation repair and maintained both-sign/mode recovery controls are admitted; RF2 combination remains deferred.

- RF1 native-envelope focused re-review passed the affected method/full 48 tests and four independent oversized-number recovery controls (all rc0), with no findings and every actionable retro maintained. Parent verified three reviewer artifacts and froze the settled candidate. The 12-line local repair brings the unit to 202 changed lines. Final RF2 combination and whole-candidate qualification are now admitted; live application remains serialized after their independent gate.

- Read-only admission with the exact final RF1 candidate verified the current original legacy receipt and all eight historical cycles as limited history, with no blocked cycle or protected-file change. This does not reconstruct historical stdout or qualify the combined candidate. Parent also retained the five installed-help inputs under the durable private workflow and staged path-only admission changes, so future refreshes need not depend on disposable temporary files; active admission remains unchanged pending final qualification/application.

- Final RF1/RF2 assembly is frozen for combination review: 138 handwritten changed lines across five files relative to the two settled bases. All 48 RF1 test methods remain unchanged; focused 14/full 77 unique offline tests exited 0 after retained fixture adaptations. Parent verified 66 source/preimage/postimage/evidence bindings. Independent interaction review, actual current-runtime qualification and serialized private activation remain pending; RF3a implementation awaits this final prerequisite gate.

- Combined correctness review passed all 66 bindings, focused 14/full 77 tests and ten independent interaction controls (rc0), with no production findings. Parent verified five reviewer artifacts. Three test-only retros remain before settlement: malformed envelopes after preflight with healthy retry, recovery before preflight/providers, and post-native drift retaining exit 17. The focused unit is admitted; activation and RF3a implementation remain pending.

- Final assembly retro revision is frozen: only the stage test file changed, 89 lines/227 combined. Parent verified 38 bindings; focused seven/full 80 tests passed. Focused independent re-verification is active. Parent prepared a bounded lock-guarded actual-runtime qualification script; it has not executed and active private files remain unchanged.

- Final combination offline gate settled: focused independent re-review verified 38 bindings, all three maintained retros and unchanged production/helper/config/prior tests. Focused seven/full 80 and review commands exited 0, with no findings. Parent verified three reviewer artifacts and froze the exact settled candidate. RF3a implementation and final native qualification are admitted; private application remains guarded and pending.

- Exact final runtime qualification passed the real isolated SSL/GitHubKit import (SDK 0.16.1) and existing fnox/mise/pinned-uv native help route, both exit 0, with equal bindings and no provider call. The reviewed nine-file private application completed under the refresh lock, preserving baseline/history/catalog/guide/schedule. Independent artifact review verified 55 hashes and all postimages with no findings. Durable admission changes only the five installed-help paths.
- One normal existing-catalog refresh then processed 24 queries/349 items: preflight/search/diff exited 0, runner exited 2 for seven capped collections and one unverified empty. Coverage observations committed; accepted baseline run 25335ea7 stayed fixed and ten unsafe comparison rows were suppressed. Independent artifact review passed 97 artifact hashes and current bindings with no findings. No retry, proposal, repair, installation or schedule change occurred. Historical baseline provenance remains limited; coverage is incomplete.
- RF3a is frozen uncommitted for independent review: four files/303 added handwritten lines, 12 focused and 24 combined tests, normal check, tasks validation and all 19 original hashes passed. Nine vertical red/green slices are retained. Parent verified ten primary bindings; public outcome/evidence correctness and retro review remain pending.

- RF3a initial independent review passed existing checks but reproduced six P2 gaps: known native exit loss during runtime drift, provider-error observations accepted as warnings, count-based caps missed, warning comparisons unvalidated, nested/private schema leakage and malformed baseline errors, and contradictory stage tuples. Parent verified five reviewer artifacts and preserved the exact initial four-file candidate. Focused two-file repair and maintained settlement/recovery controls are next; shared integration remains pending.

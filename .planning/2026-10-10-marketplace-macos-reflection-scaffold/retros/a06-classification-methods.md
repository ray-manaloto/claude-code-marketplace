# A06 unit3 classification methods retrospective

Ticket #69. Codex wrote this unit (`/root/a06_methods`, exact four-path scope,
accepted baseline HEAD `21bbd77fb7c7ffb6db9a713120bdfd9baede0cdf`, tree
`214056e8f2221189079d03c0ca25877794fdc301`) and stopped before commit. The
Claude lane `a06-unit3` landed it: worktree `.claude/worktrees/a06-unit3`,
branch `claude/a06-unit3-classification-methods`, base `e0667ec`.

## Import

The four owned files were copied with `cp` from the read-only Codex worktree
`/Users/rmanaloto/.codex/worktrees/a06-retrieval-refresh/claude-code-marketplace`
(HEAD `b4922e66ad65aba89d737b226aa60e64761ad1e5`). Every `shasum -a 256` matched
the lane record before any edit:

- `dev/codex_examples.py` `d2b8852f1bf70153644b88e90c80fc17d80e74ca20b6ef06c9c9e64b729f2a65`
- `dev/test_codex_examples.py` `3b90b03b3fda0e65fabbe3117a00b9b90d87b4adf8532779afb6574ce01dba61`
- `docs/agents/codex-example-classification.md` `8fa79da1b2dceec4be0a3374e0df2d347907a3245e9e7a7a48853bcd617ba82a`
- this record as imported `7961e1c95e060443a3e9e2f5786198f5f869031ffe20bba6b6bc7f12f2931afb`

Only this record changed after import; the three product files are byte-identical
to the source. The diff against `e0667ec` adds `inspect_configuration` (stdlib
`tomllib` syntax/UTF-8 result and the direct pinned root `properties.model.type=string`
rule), routes offline inspections through it, and updates the doc. Six vertical
slices are covered by seven new CLI tests: syntax, invalid TOML/UTF-8, pinned
model:string, wrong/absent model, unknown/complex fields, documentation/non-config
kind, and no `$ref`/`allOf` traversal. Full validity stays `UNVERIFIED`; no
network, SDK or provider path runs in these tests.

## Checks run in this lane

All with `VIRTUAL_ENV` unset, lane-local `.mise` and `.venv`:

| Command | Exit |
| --- | --- |
| `./dev/mise run tools:prepare` | rc 0 |
| `./dev/mise run deps:sync` | rc 0 |
| `./dev/mise run test:examples` | rc 0, all 24 tests passed (17 retained + 7 new) |
| `./.venv/bin/python -O -B -m unittest discover -s dev -p test_codex_examples.py -v` | rc 0, 24 tests |
| `./dev/mise tasks validate` | rc 0 |
| `./dev/mise run check` | rc 0 (87 tests; json 2277, python 209, shell 6, toml 19) |
| `./dev/mise run check:acceptance-baseline` | rc 0, 19 original file hashes matched |
| `git diff --check` | rc 0 |

Codex's private development evidence (RED/GREEN rc 1/0 per slice, product cold
review PASS, verifier repairs in its completion-workflow packet) is cited from the
imported record and was not re-read or re-run here. These are static and unit
checks; they do not prove container, provider or hook-runtime acceptance.

## Findings

| Category | Finding, disposition and verification |
| --- | --- |
| Navigation | None: the lane record's four owned paths, the existing offline CLI seam and the classification doc located every required change. No new public test seam or generic validator was added. |
| Automated checks | Applied (Codex): malformed TOML first entered the CLI refusal path; a RED control exposed it, and TOML/UTF-8 decode errors now record a sanitized inspection with rc 0. Verified here: all 24 tests passed in normal and `-O` runs. `test:examples` is already wired into `check:research` and research-fast CI; no duplicate gate needed. |
| Coding standards | Applied: method results keep full validity `UNVERIFIED`, omit input values, carry schema digest and release tag/commit, and leave `$ref`/`allOf` untraversed; each case has a CLI/artifact assertion that passed here. Deferred to the parent: independent cold review of this lane's commit by the lane-record reviewer (fable, cold); the unit remains partial until it returns. |
| Steering files | None: AGENTS.md, the ownership rule and the lane record already set one writer, exact scope, review and retro barriers. A shared/global guidance edit would add no scoped benefit. |
| Tool economy | Applied: Codex replaced a truncated combined read with exact-file reads. In this lane the inherited `VIRTUAL_ENV` would break the research_refresh harness inside `check`; it was unset per shell. The durable fix is owned by the separate env-scrub lane (`rf-env-scrub`), not this unit. |
| No-ops | None: the existing instructions materially constrained scope, test-first order and validity claims; no deletion is justified by this unit. |
| Information access | None: synthetic artifacts and the direct pinned schema rule suffice for this bounded method. Retained corpus, native/runtime/model availability and full schema validity stay unverified and belong to later A06 work and A12b. |

## Carried from the Codex packet

Codex reported its private baseline-preparation P2 and two verifier P2 repairs
(exact review binding; literal command bounds) as applied with synthetic
controls rc 0, product bytes unchanged. Those controls live in the private packet
and are deferred evidence owned by the parent: this lane neither re-ran nor needs
them, because the product checks above ran fresh. They are not a claim of sealed
product proof.

## Status

Implemented and tested in this lane; committed locally on
`claude/a06-unit3-classification-methods`. Not yet independently reviewed in
this lane, integrated or published; the parent owns review allocation, ledger
reconciliation, integration and publication. Full A06 remains open, and every
example's full validity remains `UNVERIFIED`.

## Integration review disposition (parent, 2026-10-13)

Independent Fable cold review of lane commit `8f783a0` (merged `93402c0`):
**PASS-with-P3**, no P1/P2. Verified: changed paths equal the four owned paths
(+230/−10); product files byte-identical to the import hashes; baseline 19/19;
tests assert CLI exit codes, stdout counts and receipt fields; all six slices
plus the no-`$ref`/`allOf` case covered; `validity` unconditionally `UNVERIFIED`;
no network/SDK/provider path reachable; bounded reads preserved. Reviewer exits:
`test:examples` rc 0 (24), optimized rc 0 (24), `check` rc 0, baseline rc 0,
`tasks validate` rc 0, `git diff --check` rc 0.

| Severity | Finding | Disposition |
| --- | --- | --- |
| P3 | Deeply nested TOML within the 256 KiB bound raises `RecursionError` from `tomllib`, escaping the `TOMLDecodeError` handler, so the CLI exits rc 1 with a traceback instead of the documented rc 2 `unresolved`; no receipt is written and no input is echoed. | Deferred with owner: the next A06 unit (retained-corpus consumption) treats it as a bounded `not_inspected` outcome or catches it in `main`; tracked in the #69 ledger row. |
| P3 | Lane record carried `base_sha: null` / `status: allocated` during review. | Applied by the parent at handoff (`lanes/a06-unit3.json` now binds base `e0667ec`, lane commit `8f783a0`, merged head `93402c0`). |

Integrated into `codex/marketplace-native-onboarding` by the parent with
composed-tree gates `tasks validate` 50 rc 0, `check` rc 0,
`check:acceptance-baseline` 19/19 rc 0, `test:examples` 24 rc 0,
`git diff --cached --check` rc 0.

# Process follow-up retrospective

The user explicitly invoked `mattpocock-skills:retro` after the parallel wave
and feedback integration. This three-file unit starts from source
`d7aa31c85be4c7c4778ea335581486c6dc417085`; it changes the team guide, this record
and progress. The parent owns application and delivery; read-only reviewer
`retro_process_review` independently inspects exact files and receipts.

## Findings in severity order

1. **P2 ownership:** another task's active handoff-checkout edits were discovered
   after documentation edits had begun. Earlier wording made the parent writer
   role sound permanent. The [team guide](../../../docs/agents/codex-task-orchestration.md#ownership)
   now requires worktree discovery and explicit allocation reconciliation before
   the first edit, including documentation. Ambiguous ownership stays read-only;
   titles, paths and idle state remain discovery evidence. Applied: this unit
   waited for the scheduler's explicit release after its publication at `6cca08b`;
   fresh source/peer identities and shared common directory matched. The
   [release receipt](/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-process-retro-g1qz8vcj/writer-release.json)
   and [pre-edit identity](/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-process-retro-g1qz8vcj/pre-edit-identity.json)
   bind that ordering. Return the allocation after verified delivery.
2. **P2 tool economy:** two thread reads used small per-item limits but printed
   entire results; the tool reported 177,640 original tokens. A later aggregate
   file read also exceeded its combined display budget. The
   [primary record](/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-process-retro-g1qz8vcj/primary-evidence.json)
   binds the first call/output without copying the transcript. The guide now
   supplies positive message selection, excerpt/coverage metadata, pagination
   and a deterministic 6,000-character display cap with an assertion. A live
   263-item response became 870 characters; escaped oversized input produced
   5,949 characters, with the command marker excluded. The
   [controls](/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-process-retro-g1qz8vcj/excerpt-controls.json)
   record both cases. Subsequent native reads used that exact projection.
3. **P3 navigation:** inferred worktree/file suffixes caused failed reads.
   The guide now starts with `git worktree list --porcelain` and `rg --files`.
   Applied discovery resolved `issue-29-context7` and `dev/git_delivery.py`.
   These runtime path choices belong in the orchestration sequence; a new
   repository filesystem rule would not validate another task's live location.

## Remaining category audit and verification

Automated checks: none missing for the integrated feedback helper. `dev/check.py`
discovers its 12 tests and propagates failures; `check:research` and the fast CI
workflow already run that path. Hosted run
[38346981268](https://github.com/ray-manaloto/claude-code-marketplace/actions/runs/38346981268)
passed at the exact starting HEAD. Keep the deterministic display check at the
hosted tool boundary; repository CI does not observe those ephemeral responses.
Coding standards: ownership/admission interpretation remains an independent
review judgement. No new `CODING_STANDARDS.md` or duplicate runner is needed.
Steering files and no-ops: retain the existing short AGENTS navigation pointer;
replace obsolete permanent-writer claims in the reached guide. Information
access: required source, live thread evidence and CI status were available.
No credential, provider, global configuration or native-runtime change is needed.

All findings in this unit have been applied. Task validation, `check` and all
19 original baseline hashes passed. Independent review verified the files and
logs, then requested an exact-byte correction to the snippet digest: its final
newline is now included, and the earlier normalized receipt is preserved.
No behavior changed, so this metadata correction required no repeated tests.
The [check receipt](/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-process-retro-g1qz8vcj/checks.json)
and [review receipt](/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-process-retro-g1qz8vcj/review.json)
bind the completed checks and final reviewer disposition. A09 delivery records
commit/publication separately.

The earlier feedback integration, signal-cleanup repair and accepted frontier
correction retain their own receipts and limitations. A06 readiness, unintegrated
handoff units and native/provider/OCI qualification are unchanged.

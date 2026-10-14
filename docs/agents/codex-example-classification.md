# Offline Codex example classification

Use the existing CLI for admitted, project-confined retrieval artifacts:

```sh
.venv/bin/python -B dev/codex_examples.py RUN_ID --sha BLOB_SHA \
  --offline-receipt evidence/codex-examples/runs/RETRIEVAL_ID/receipt.json \
  --receipt-sha256 INDEPENDENT_RECEIPT_SHA256
```

Supply the expected receipt SHA-256 from the caller's independently bound packet.
The consumer verifies the saved manifest/raw/normalized chain, release schema,
recorded CLI and release identity, budgets, selected provenance and raw Git blobs.
All selected input and output paths receive project confinement and symlink checks.
Credential, SDK client, provider and native CLI calls are absent from this mode.

Success returns rc 0 and the existing `recorded` receipt/count/coverage JSON shape.
Receipts append under `evidence/codex-examples/classifications/`; inputs stay intact.
Refusal returns rc 2, stderr `unresolved` with a reason, and no accepted output.
Complete search coverage stays `bounded`; partial search stays `provisional`.

Every inspection retains full validity `UNVERIFIED`. For paths whose basename is
exactly `config.toml`, `python-stdlib-tomllib.loads` records `parsed` or
`invalid_syntax`. Invalid TOML or UTF-8 is an inspection result with rc 0 after
artifact integrity passes; its fixed reason omits input values. Integrity refusal
still returns rc 2 and produces no accepted receipt.

Parsed configurations inspect only the pinned root `properties.model.type=string`
rule. `model_field` records method `pinned-root-model-type`, schema digest and
release tag/commit, and distinguishes `present_string`, `present_wrong_type` and
`absent`. Without that direct rule it records `not_inspected`; `$ref` and `allOf`
are never traversed. Other parsed root keys appear in `uninspected_fields` without
their values. Unknown and complex fields receive no schema validity claim.

Markdown and reStructuredText paths have kind `documentation`; other non-config
paths have kind `unknown`. Both remain `not_inspected`, with method `null` and an
explicit reason. Nonparsed paths have no model-field inspection result.

Neither a parse nor a model-field result proves model availability, full schema
validity, current installed-release compatibility, native or runtime behavior.
Recorded CLI identity describes the historical producer. Generic validators belong
to A12b; retained-corpus and verified-empty hook-run consumption are later A06 work.

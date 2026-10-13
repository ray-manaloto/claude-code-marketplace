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

Every inspection is `not_inspected`, method `null`, full validity `UNVERIFIED`.
TOML syntax, schema, current installed release, native and runtime validation are
unexecuted. Recorded CLI identity describes the producer, not current compatibility.
TOML inspection belongs to the next bounded A06 unit after this integrity gate.

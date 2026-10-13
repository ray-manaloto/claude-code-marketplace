# evidence/

Sanitized verification receipts, immutable and hash-bound. The rules (new receipts in
new files, exact exits and hashes, static versus runtime claims) are in
`.claude/rules/evidence.md`.

`evidence/onboarding/baseline-files.json` is the frozen record of the 19 original
acceptance files; `./dev/mise run check:acceptance-baseline` verifies it.

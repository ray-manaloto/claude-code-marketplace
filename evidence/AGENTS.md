# evidence/

Sanitized verification receipts. Path-scoped rules load from
`.claude/rules/evidence.md`.

- A receipt is immutable and hash-bound: it names the command, input paths and SHAs,
  the actual exit code and the identity of what ran. Write a correction as a new file
  that names the superseded receipt by path and SHA-256.
- Choose a topic directory (`evidence/<topic>/`) for each new receipt family; the
  receipt format of a directory follows its existing files.
- `evidence/onboarding/baseline-files.json` is the frozen record of the 19 original
  acceptance files; `./dev/mise run check:acceptance-baseline` verifies it.
- A static receipt certifies a static claim; runtime, provider, fresh-session and OCI
  acceptance each need their own receipt.

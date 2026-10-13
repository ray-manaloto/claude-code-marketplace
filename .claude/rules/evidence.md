---
paths: ["evidence/**"]
---

# Evidence receipts

- A receipt is immutable once committed. A correction is a new file that names the receipt it supersedes by path and SHA-256.
- A receipt binds the command, its input identities (paths, SHAs, hashes), the actual exit code and the identity of what ran. Cite exit codes and hashes exactly as recorded.
- Report an unrun or failed step as such, with its exit code or reason; a partial receipt keeps its `partial` status.
- Store sanitized records only: no secrets, tokens, provider payloads or transcripts. Name the environment selectors present (`VIRTUAL_ENV`, `UV_PROJECT_ENVIRONMENT`, `MARKETPLACE_PYTHON`) when a gate ran.
- The 19 original acceptance files stay byte-identical; `./dev/mise run check:acceptance-baseline` verifies their hashes.
- Static receipts (`check`, `retro:gate`) certify static claims. Runtime, provider, fresh-session and OCI acceptance need their own receipts.

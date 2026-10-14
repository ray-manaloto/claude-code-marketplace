# Ticket #12: Task 14c failed-closure disposition

This records the independent read-only Codex review of the failed LSan run at
checkout `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace`,
branch `codex/marketplace-native-onboarding`, pre-commit HEAD
`0a7a2444f34ca98def72f8fefde7f804fc2381d6`. The Git common directory was
`/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git`.
The reviewer made no repository writes or native build/run.

**Review disposition: PASS — failed-closure correctness and integrity; no
material findings.** The reviewer recomputed 81 retained receipt hashes: 45
failed-native files, eight initial-refusal files, 22 diagnostic copies, three
preparation-support files, and three driver-probe files. Four preparation-review
bindings also matched. The compiler, SDK, LSan, TSan, three C++ runtime
libraries, witness binary and object matched their recorded identities. The
pinned source HEAD `f17c8d6c7bfef5e02ccadcf33517fd2a53b51b6e`, tree
`9899759f9004a7df8442ec57000a17e53e6ad5f6`, diff hash and status bytes
matched the contract.

The reviewer found all 19 owned PIDs absent with `ps` exit 1 and empty output.
The canonical heavy lease accepted an immediate exclusive probe through a
read-only descriptor; its bytes remained unchanged. The original native run
recorded 17 commands with exit 0, followed by a 20-second `lsan-clean`
timeout, child exit -15 and runner exit 1. LSan+UBSan was not reached. Both
modes remain **unqualified**. The reviewed
[closure](failed-native/closure.json) has SHA-256
`c4589982154c903c84acdc5ffab12a078886e97bb8bfe6e155561a7f2234bc5d`.

The reviewer did not rerun native acceptance, the full protected-prefix guard,
all 881 source hashes or lightweight checks. Full protected-state preservation
is supported by the retained guard and closure receipts. The parent's fresh
lightweight checks each exited 0: `./dev/mise tasks validate`,
`./dev/mise run check`, `./dev/mise run check:acceptance-baseline` (19 original
hashes), and `git diff --check`.

The earlier preparation secret scan covered only 15 preparation files. Before
commit, the parent ran the existing Gitleaks 8.30.1 binary with redaction over
the full staged LSan evidence directory and the three staged maintained files.
The evidence scan exited 1 with exactly six `generic-api-key` alerts, all in
`contract.json` at lines 85, 114, 124, 216, 392 and 1120. Those are the six
hash-value/path false positives already identified in
[pre-review-secret-scan.json](pre-review-secret-scan.json); no new alert appeared
in the later failed-native or diagnostic files. Each maintained-file scan
exited 0. A focused private-key/token/header pattern scan found no hits. The
scanner result is a classified alert set, not an unqualified clean exit.

`git diff --cached --check` reports historical trailing whitespace in the
immutable `failed-native/source-before-diff.stdout` capture. Excluding only
that captured diff, the staged whitespace check exited 0; its bytes remain
unchanged and match the closure hash.

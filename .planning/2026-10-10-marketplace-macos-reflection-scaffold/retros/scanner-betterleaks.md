# scanner-betterleaks retrospective: A09 scanner switch, part A (CT-82 part A, D159, R17)

Unit `scanner-betterleaks`. Worktree `.claude/worktrees/scanner-betterleaks`, branch
`claude/scanner-betterleaks`, base `5c4ff9a`, cut from allocation commit `ca53deb`. Implementation
commits `6a222a4` (pin) and `ee2ae8d` (fixes, rule, tests); writer Claude Opus 5.5 (implementer).
Cold review of `4eeb732` (reviewer via the coordinator): **PASS-with-findings**. The lane fixed the one
P3 inside its paths in `6948135`; the other findings are parent-owned and deferred to integration
(review section below). The retro-writer reruns this record after the parent's integration edits.

Delivered, test-first (each test failed before its change, receipts in the handoff):
`mise.dev.toml` pins `"aqua:betterleaks/betterleaks" = "1.9.0"` (newest 1.x, released 2026-09-29;
2.0 is rc only). `.gitleaks.toml` gains rule `aws-access-key-id`: the default rule's regex, keywords,
entropy floor 3.0 and `.+EXAMPLE$` exemption, without the paired-secret component that drops a lone
key ID in betterleaks 1.x (#408). `betterleaks config check` reports 465 rules (464 before); gitleaks
8.30.1 still loads the file (rc 0). `dev/git_delivery.py` `scan()` pops `BETTERLEAKS_CONFIG` and
`BETTERLEAKS_CONFIG_TOML` with the `GITLEAKS_*` names, passes `--config <root>/.gitleaks.toml`, and
refuses in one line when the root holds `.gitleaksignore` or `.betterleaksignore`. Binary name, CLI
flags and intent keys are unchanged. `dev/test_git_delivery.py` adds four seam tests: three through
the `publish` CLI with a fake scanner that records its argv and environment, and one on the real
pinned scanner with a key ID assembled at runtime (the lane commits scan to 0 findings).

Exits on `ee2ae8d`, `VIRTUAL_ENV` unset, after merging the integration tip `ca53deb` ("Already up to
date", rc 0): `./dev/mise run test:delivery` rc 0 (18 tests, was 14; the real-scanner test ran, not
skipped); `python3 -I -m unittest discover -s dev -p test_git_delivery.py` rc 0; `./dev/mise tasks
validate` rc 0; `./dev/mise run check` rc 0; `./dev/mise run check:acceptance-baseline` rc 0 (19
baseline hashes); `git diff --check ca53deb HEAD` rc 0; hk pre-commit `records` step passed on both
commits. Measurement: pinned betterleaks `git --config .gitleaks.toml --redact=100
--log-opts=origin/main..HEAD` (21 commits), 3 runs: rc 1 each, 2.33 / 2.37 / 2.39 s wall, 228 findings
(`generic-api-key` 226, `ibm-cloud-user-api-key` 2; `aws-access-key-id` 0, private-name rule 0),
227 distinct fingerprints, every `Secret` redacted. That matches R17 section 7.4.

## Review findings and dispositions

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P3 | Coding standards (review, `.claude/rules/dev-tests.md`): `dev/test_git_delivery.py` found the scanner with `shutil.which("betterleaks")`, so an unpinned PATH binary could run or the test could skip silently. Reproduced on `4eeb732`: with a stub `betterleaks` first on PATH, the test ran the stub (`stub ran: yes`, failing `0 != 1`). | Applied in `6948135`: `pinned_betterleaks()` reads the pin from `mise.dev.toml` with `tomllib`, resolves the binary with `./dev/mise which betterleaks`, asserts `betterleaks version` equals the pin, and fails rather than skips when the binary is missing and `MISE_TASK_NAME` is `test:delivery`. Verification: with the stub first on PATH, `test:delivery` rc 0 (18 tests) and the stub did not run. A fake mise returning the stub FAILS (`(0, '9.9.9') != (0, '1.9.0')`). With the pinned install moved aside, `test:delivery` rc 1, the test FAILS with "pinned betterleaks 1.9.0 is missing", and the install was then restored. Outside the task a missing binary is a reported skip. |
| P3 | Automated checks (review, parent-owned): the companion patch (the `mise.dev.lock` entry and the `TOOL_BACKENDS` row) must land with the pin. | Deferred to integration, owner parent, using the patch whose sha256 is listed in the lane audit below. |
| P3 | Navigation (review, parent-owned): add `.mise/` to the shared `.git/info/exclude`. | Deferred to integration, owner parent. |

## Lane audit (seven categories)

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: the pin breaks the tool-lock binding. `dev/bootstrap.py` `TOOL_BACKENDS` hard-codes python and uv, and `mise.dev.lock` must list every `[tools]` entry. Both files are outside `owned_paths`. At `ee2ae8d` `./dev/mise run tools:prepare` exits 1 ("mise.dev.lock tools differ from mise.dev.toml"), and `deps:check` and `test:bootstrap` will refuse in the root checkout too. Yet `./dev/mise run check` exits 0, so no required check sees the mismatch. | Proposed patch for the parent, owner parent, to apply in the same integration as `6a222a4`: scratchpad `scanner-betterleaks-companions.patch` (sha256 `efe708740809be390a4138aba0a2ed359cd57cf87c84fabe1b78d2170d36a476`, 48 lines). It adds the lock entry the admitted `./dev/mise install` wrote (3 platforms, cosign provenance) and one `TOOL_BACKENDS` row. Verified with the patch applied temporarily: `verify_tool_lock()` rc 0 and `python3 -I dev/check.py` rc 0, then restored. Unverified here: `deps:check` and `test:bootstrap` with the patch need project uv, which this worktree lacks (they exit 1 at the base too); the root checkout has python and uv. |
| P2 | Automated checks (from the row above): `dev/check.py` never calls `bootstrap.verify_tool_lock()`, which is static (no install, no network). A `[tools]` change passes `check` and fails only later in `tools:prepare`. | Proposed, owner parent (`dev/check.py` outside `owned_paths`): `dev/check.py` calls `verify_tool_lock()` so `./dev/mise run check` refuses a mismatch. Verification after the edit: `check` rc 0 with the companion patch, and rc 2 at `6a222a4` without it. |
| P2 | Coding standards: a `git diff .gitleaks.toml` in this lane printed a hunk header. Git quotes the nearest context line in each `@@` header, and here that line was the private-name rule's `regex` value, so the value reached tool output. It did not reach any commit, message or this record. The value is already committed in `.gitleaks.toml`, character-classed. | Applied in the lane: later diffs dropped `@@` lines. Proposed rule, owner parent (`.claude/rules/` is excluded here): "Diff `.gitleaks.toml` with `git diff -U0 -- .gitleaks.toml \| grep -v '^@@'`; hunk headers quote the private-name rule." Verification after the edit: `./dev/mise run check` rc 0. |
| P2 | Information access: the brief named an AWS documentation example key ("AKIA...EXAMPLE style") as the fixture. Both the upstream rule and the new rule exempt `.+EXAMPLE$`, so that key alone would prove nothing. | Applied: the test assembles a synthetic non-EXAMPLE key ID at runtime and asserts exactly one `aws-access-key-id` finding, with the documentation example on the next line producing none. Verification: `test_root_config_reports_lone_aws_access_key_id` failed before the rule (rc 0, no findings) and passes after; `test:delivery` rc 0. |
| P3 | Automated checks: with `--config` explicit, a missing `<root>/.gitleaks.toml` makes the scanner exit 1, and A09 reports that as "found potential leaks". The result is fail-closed but the message is misleading. A fourth refusal was outside the brief's three fixes, so it was not added. | Owner parent: decide whether CT-82 gets a one-line "scanner config missing" refusal in `scan()`. Evidence: `dev/git_delivery.py` maps rc 1 to the leak refusal; R17 section 7.2 says a missing config exits 1 in both tools. |
| P3 | Information access: the measured range `origin/main..HEAD` has one duplicated fingerprint (228 findings, 227 distinct), so `fingerprints()` refuses to adjudicate it. This is the A09 limit R17 section 7.4 describes, and is not caused by this switch. A gitleaks-made baseline also suppresses nothing under betterleaks (R17 section 7.3). | Owner parent: the re-adjudication operation in R17's table runs before the A09 intents switch `gitleaks_bin`; this lane does not change A09 adjudication. |
| P3 | Navigation: `./dev/mise install` puts the per-worktree data dir `.mise/` in the worktree, untracked and not ignored. `git status` shows `?? .mise/` and `dev/check.py` (`ls-files --others`) scans its TOML files (21 to 23). A `git add -A` would stage binaries. | Proposed, owner parent: add `.mise/` to the shared `.git/info/exclude`, as is already done for `.claude/worktrees/` (`.gitignore` is frozen). Verification after the edit: `git status --short` in this worktree is empty. |
| P3 | Steering/global guidance: R17 also lists pointing the A09 intent's `gitleaks_bin` at the pinned binary, plus doc mentions of gitleaks as the A09 scanner. Both are outside `owned_paths`. | Owner parent, at the intent switch (D159): set `gitleaks_bin` to the absolute path `./dev/mise which betterleaks` prints in the publishing checkout. Rerun `test:delivery` and one A09 dry publish there. |
| P3 | Tool economy: the first baseline loop ran `./dev/mise $t` in zsh, which does not word-split `$t`, so all four checks exited 1 on a usage error. That cost one round. | Applied in the lane: reran with explicit commands (`tasks validate` rc 0, `test:delivery` rc 0, `check` rc 0, `deps:check` rc 1 for missing project uv). Nothing further to change. |
| none | No-ops: none, because every change has a test that failed first, apart from the pin, which the real-scanner test needs (it ran under `./dev/mise`). The one comment added to `.gitleaks.toml` describes the new rule. | Verification: `test:delivery` rc 0 with the real-scanner test reported `ok`, not skipped. |

Size: 4 maintained files plus this record, about 105 handwritten lines added (`git diff --stat
ca53deb ee2ae8d`: 105 insertions, 3 deletions), within the 5-file / 300-line unit limit.

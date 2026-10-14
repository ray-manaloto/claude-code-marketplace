# T1 snapshot report: untracked Codex worktree data

Created 2026-10-13T23:04:26.671158+00:00 by T1 (Claude subagent). Nothing here is committed; the in-repo copy is untracked.

## Sources

| Worktree | Path | HEAD | Branch | Untracked | Modified tracked | Ignored (all) | Ignored data copied |
|---|---|---|---|---|---|---|---|
| 2a14 | `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace` | `48027d2d333611d162cdff8cabb7bc1eecf944da` | HEAD (detached) | 257 | 15 | 5902 | 79 |
| c658 | `/Users/rmanaloto/.codex/worktrees/c658/claude-code-marketplace` | `6130ab5e9298e4c70d8c39a0ebd3c6857458c5c5` | HEAD (detached) | 64 | 12 | 19 | 0 |

## Copies

- In-repo snapshot (a): `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.planning/2026-10-10-marketplace-macos-reflection-scaffold/imports/codex-worktrees-20261013`
- Private mirror (b, mode 0700): `/Users/rmanaloto/.local/state/marketplace-imports/codex-worktrees-20261013`
- Files: 454 (11,814,946 bytes) in each copy; per worktree {'2a14': 366, 'c658': 88}

| Class | Files | Bytes |
|---|---|---|
| untracked | 321 | 9,998,012 |
| modified | 54 | 708,476 |
| ignored-data | 79 | 1,108,458 |

`modified` counts both the working-tree copy and a `<path>.diff` (`git diff -- <path>` against the worktree's own HEAD, not the integration tip) for each of the 27 modified tracked files (15 in 2a14, 12 in c658).

## Secret classification

Secret-flagged files: **0**. Every copied file and diff was scanned by name (token/cookie/secret/credential/passw/.env/.pem/.key) and by content (GitHub/OpenAI/Anthropic/AWS/Slack token shapes, Bearer, Authorization/x-api-key/api_key/cookie assignments, JWT, private-key blocks, `*_TOKEN=`-style env lines). No hits, so nothing is mirror-only.
Judgement calls, recorded so a reviewer can disagree:
- 18 `raw.json` provider captures (`evidence/github-search-one-page/*`, `evidence/saved-searches/runs/*`, `.a04-e97ftai5/records/runs/*`): request keys are only endpoint/method/page/per_page/query and response headers are an allowlist (content-type, x-ratelimit-*); no auth material, so copied to both.
- `evidence/issue-publication-private/` (96 files): the name says private, but contents are issue intents, attempt and binding receipts (intent sha256, issue id/number); no credentials, so copied to both. A committing lane should decide whether it belongs in Git.
- `.a04-e97ftai5/` is a stray scratch records root (codex-schema runs, quarantine, locks; 36 KB) at the 2a14 root; copied as-is.

## Verification

`python3 -I verify.py --mirror` (run from the snapshot directory) rc = **0**: 454/454 ok in (a) and 454/454 ok in (b), no unlisted files. Without `--mirror` it checks (a) only.

## Excluded and could-not-copy

Excluded on purpose (ignored caches/tool installs, not data): 2a14:**/__pycache__ (316), 2a14:.cache/neocmakelsp (5), 2a14:.mise/.gitignore (1), 2a14:.mise/installs (1775), 2a14:.mise/shims (14), 2a14:.venv/.gitignore (1), 2a14:.venv/.lock (1), 2a14:.venv/CACHEDIR.TAG (1), 2a14:.venv/bin (15), 2a14:.venv/lib (3693), 2a14:.venv/pyvenv.cfg (1), c658:**/__pycache__ (1), c658:.venv/.gitignore (1), c658:.venv/CACHEDIR.TAG (1), c658:.venv/bin (13), c658:.venv/lib (2), c658:.venv/pyvenv.cfg (1).
Included although it is a CMake build directory: `evidence/iwyu-build/operation/build/` (18 files, ~0.85 MB), because it sits under `evidence/` and tracked `evidence/iwyu-build/operation-manifest.json` hashes its files (see dependency table).
Could not copy: 0 (no permission errors, no symlinks, no file over 50 MB).

## Dependency check against tip 9cd396a

Method: `git archive 9cd396a` exported to scratch, then `rg -F` for every copied non-modified path, each ancestor directory, and distinctive basenames (git grep -F with 553 patterns was too slow and was stopped). Lines inside this imports directory are ignored. Full data: `T1-dependency-scan.json` (references capped at 20 per row; `n` is the full count).

Exact path references: 124 distinct paths/dirs referenced by tracked tip files; **101 missing from the tip** (241 reference lines), all 101 present in the snapshot and none on disk in the main checkout. Of those, 22 are untracked-class paths (code/data/docs) and 79 are gitignored evidence files or dirs that tracked operation manifests hash.

Key code dependencies (P1-10):
- `dev/codex_examples.py:25` → `evidence/codex-examples/release/config-schema.json` (missing from tip; in snapshot).
- `dev/codex_examples.py:106`, `:148`, `:309` → `evidence/saved-searches/runs`, `evidence/codex-examples/runs`, `evidence/codex-examples` (missing; in snapshot).
- `dev/search_catalog.py:359` → `evidence/saved-searches` (missing; in snapshot). `dev/test_search_catalog.py:149,153` name `.pending-interrupted`/`.pending-disappearing` (quarantine markers; the only copies are under `.a04-e97ftai5/records/quarantine/`).
- Docs cited by `task_plan.md:322` and progress.md: `docs/agents/automation-amendment-review.md`, `github-search-reuse.md`, `workflow-reconciliation.md` (missing; in snapshot).

| Referenced path | Kind | Class | Referencing file:line (first 3) | Refs | Exists in tip? | In snapshot? | On disk in main checkout? |
|---|---|---|---|---|---|---|---|
| `docs/agents/automation-amendment-review.md` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:1979<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md:322 | 2 | no | yes | no |
| `docs/agents/github-search-reuse.md` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:1905 | 1 | no | yes | no |
| `docs/agents/workflow-reconciliation.md` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:1877 | 1 | no | yes | no |
| `evidence/claude-amendment-review` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:1977 | 1 | no | yes | no |
| `evidence/codex-examples` | dir | untracked | dev/test_codex_examples.py:130<br>dev/test_codex_examples.py:183<br>dev/test_codex_examples.py:320 | 7 | no | yes | no |
| `evidence/codex-examples/release` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2373 | 1 | no | yes | no |
| `evidence/codex-examples/release/config-schema.json` | file | untracked | dev/codex_examples.py:25 | 1 | no | yes | no |
| `evidence/codex-examples/runs` | dir | untracked | dev/test_codex_examples.py:191<br>dev/codex_examples.py:148<br>dev/codex_examples.py:212 | 4 | no | yes | no |
| `evidence/core-p2996/operation/ctest-corrected-exit-contract/Testing/Temporary/LastTest.log` | file | ignored-data | evidence/core-p2996/operation-manifest.json:1094 | 1 | no | yes | no |
| `evidence/core-p2996/operation/ctest-old-regex-comparison/Testing/Temporary/LastTest.log` | file | ignored-data | evidence/core-p2996/operation-manifest.json:1118 | 1 | no | yes | no |
| `evidence/git-delivery/initial-outbound-gitleaks-redacted.json` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2514 | 1 | no | yes | no |
| `evidence/github-search-one-page` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/A02.md:3 | 1 | no | yes | no |
| `evidence/github-search-one-page/20261012T192548Z-d72b7e85` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2083 | 1 | no | yes | no |
| `evidence/github-search-one-page/20261012T192724Z-33992b35` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2087 | 1 | no | yes | no |
| `evidence/github-search-one-page/20261012T193651Z-cc501ef6` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2103 | 1 | no | yes | no |
| `evidence/issue-publication-private/edges/local-edge-receipt.json` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2733 | 1 | no | yes | no |
| `evidence/issue-publication-private/graph-audit.json` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2702 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/.ninja_log` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:210 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeCache.txt` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:216 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CMakeCCompiler.cmake` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:222 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CMakeCXXCompiler.cmake` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:228 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CMakeSystem.cmake` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:234 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CompilerIdC/CMakeCCompilerId.c` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:240 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CompilerIdC/apple-sdk.c` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:246 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CompilerIdCXX/CMakeCXXCompilerId.cpp` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:252 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CompilerIdCXX/apple-sdk.cpp` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:258 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/CMakeConfigureLog.yaml` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:264 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/InstallScripts.json` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:270 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/TargetDirectories.txt` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:276 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/cmake.check_cache` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:282 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/CMakeFiles/rules.ninja` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:288 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/build.ninja` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:294 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/cmake_install.cmake` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:300 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/compile_commands.json` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:306 | 1 | no | yes | no |
| `evidence/iwyu-build/operation/build/install_manifest.txt` | file | ignored-data | evidence/iwyu-build/operation-manifest.json:312 | 1 | no | yes | no |
| `evidence/mise-runtime/attempt1-invocation/stderr.log` | file | ignored-data | evidence/mise-runtime/attempt1-manifest.json:11 | 1 | no | yes | no |
| `evidence/mise-runtime/attempt1-invocation/stdout.log` | file | ignored-data | evidence/mise-runtime/attempt1-manifest.json:17 | 1 | no | yes | no |
| `evidence/mise-runtime/attempt2-invocation/stderr.log` | file | ignored-data | evidence/mise-runtime/attempt2-manifest.json:71 | 1 | no | yes | no |
| `evidence/mise-runtime/attempt2-invocation/stdout.log` | file | ignored-data | evidence/mise-runtime/attempt2-manifest.json:77 | 1 | no | yes | no |
| `evidence/mise-runtime/attempt3-invocation/stderr.log` | file | ignored-data | evidence/mise-runtime/attempt3-manifest.json:131 | 1 | no | yes | no |
| `evidence/mise-runtime/attempt3-invocation/stdout.log` | file | ignored-data | evidence/mise-runtime/attempt3-manifest.json:137 | 1 | no | yes | no |
| `evidence/mise-runtime/invocation/stderr.log` | file | ignored-data | evidence/mise-runtime/operation-manifest.json:161 | 1 | no | yes | no |
| `evidence/mise-runtime/invocation/stdout.log` | file | ignored-data | evidence/mise-runtime/operation-manifest.json:167 | 1 | no | yes | no |
| `evidence/p2996-cmake/independent-review/configured-evidence/private-runtime-try-compile.log` | file | ignored-data | evidence/p2996-cmake/review-manifest.json:1160 | 1 | no | yes | no |
| `evidence/p2996-cmake/operation/configured-evidence/private-runtime-try-compile.log` | file | ignored-data | evidence/p2996-cmake/operation-manifest.json:1052<br>evidence/p2996-cmake/independent-review/parent-evidence-verification.json:1072 | 2 | no | yes | no |
| `evidence/saved-searches` | dir | untracked | dev/search_catalog.py:359<br>dev/collect_saved_search.py:251 | 2 | no | yes | no |
| `evidence/saved-searches/runs` | dir | untracked | dev/test_codex_examples.py:84<br>dev/codex_examples.py:106<br>dev/codex_examples.py:220 | 4 | no | yes | no |
| `evidence/saved-searches/runs/codex-schema--1791834335766132000--747966bbfbc179da` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2131 | 1 | no | yes | no |
| `evidence/saved-searches/runs/codex-schema--1791834403418782000--73b8ad54811dc757` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2134 | 1 | no | yes | no |
| `evidence/saved-searches/runs/codex-schema--1791835615392017000--b2451f6bd8490b1c` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2204 | 1 | no | yes | no |
| `evidence/saved-searches/runs/codex-schema--1791836388445290000--8385f42d6953e0ab` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/A03a.md:3<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2237 | 2 | no | yes | no |
| `evidence/saved-searches/runs/codex-schema--1791837279871878000--59b358fe26427ce1` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2282 | 1 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/detect_compiler/stdout-arm64-osx-p2996-static.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:29<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:37<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:370 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/detect_compiler/stdout-arm64-osx.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:30<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:38<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:362 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/config-arm64-osx-p2996-static-dbg-ninja.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:38<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:46<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:450 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/config-arm64-osx-p2996-static-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:39<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:47<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:418 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/config-arm64-osx-p2996-static-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:40<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:48<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:410 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/config-arm64-osx-p2996-static-rel-ninja.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:41<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:49<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:498 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/install-arm64-osx-p2996-static-dbg-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:42<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:50<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:466 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/install-arm64-osx-p2996-static-dbg-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:43<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:51<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:458 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/install-arm64-osx-p2996-static-rel-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:44<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:52<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:514 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/install-arm64-osx-p2996-static-rel-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:45<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:53<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:506 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/stdout-arm64-osx-p2996-static.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:46<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:54<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:402 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/vcpkg-cmake-config/stdout-arm64-osx.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:48<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:56<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:394 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/vcpkg-cmake/stdout-arm64-osx.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:47<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:55<br>evidence/vcpkg-fmt-build/native-repair-review/input-hashes.json:386 | 5 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/detect_compiler/stdout-arm64-osx-gcc16-dynamic.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:139<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:148<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:858 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/detect_compiler/stdout-arm64-osx.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:140<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:149<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:834 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/config-arm64-osx-gcc16-dynamic-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:150<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:159<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:972 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/config-arm64-osx-gcc16-dynamic-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:151<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:160<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:966 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/install-arm64-osx-gcc16-dynamic-dbg-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:152<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:161<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:912 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/install-arm64-osx-gcc16-dynamic-dbg-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:153<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:162<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:906 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/install-arm64-osx-gcc16-dynamic-rel-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:154<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:163<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:948 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/install-arm64-osx-gcc16-dynamic-rel-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:155<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:164<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:942 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/stdout-arm64-osx-gcc16-dynamic.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:156<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:165<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:960 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/detect_compiler/stdout-arm64-osx-gcc16-static.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:173<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:182<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:714 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/detect_compiler/stdout-arm64-osx.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:174<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:183<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:690 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/config-arm64-osx-gcc16-static-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:184<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:193<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:828 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/config-arm64-osx-gcc16-static-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:185<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:194<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:822 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/install-arm64-osx-gcc16-static-dbg-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:186<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:195<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:768 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/install-arm64-osx-gcc16-static-dbg-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:187<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:196<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:762 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/install-arm64-osx-gcc16-static-rel-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:188<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:197<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:804 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/install-arm64-osx-gcc16-static-rel-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:189<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:198<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:798 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/stdout-arm64-osx-gcc16-static.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:190<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:199<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:816 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/detect_compiler/stdout-arm64-osx-p2996-dynamic.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:203<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:212<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:570 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/detect_compiler/stdout-arm64-osx.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:204<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:213<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:546 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/config-arm64-osx-p2996-dynamic-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:214<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:223<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:684 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/config-arm64-osx-p2996-dynamic-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:215<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:224<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:678 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/install-arm64-osx-p2996-dynamic-dbg-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:216<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:225<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:624 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/install-arm64-osx-p2996-dynamic-dbg-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:217<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:226<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:618 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/install-arm64-osx-p2996-dynamic-rel-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:218<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:227<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:660 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/install-arm64-osx-p2996-dynamic-rel-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:219<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:228<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:654 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/stdout-arm64-osx-p2996-dynamic.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:220<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:229<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:672 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/detect_compiler/stdout-arm64-osx-p2996-static.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:237<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:246<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:426 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/detect_compiler/stdout-arm64-osx.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:238<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:247<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:402 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/config-arm64-osx-p2996-static-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:248<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:257<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:540 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/config-arm64-osx-p2996-static-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:249<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:258<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:534 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/install-arm64-osx-p2996-static-dbg-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:250<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:259<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:480 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/install-arm64-osx-p2996-static-dbg-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:251<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:260<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:474 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/install-arm64-osx-p2996-static-rel-err.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:252<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:261<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:516 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/install-arm64-osx-p2996-static-rel-out.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:253<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:262<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:510 | 3 | no | yes | no |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/stdout-arm64-osx-p2996-static.log` | file | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:254<br>evidence/vcpkg-fmt-build/closure-secret-scan.json:263<br>evidence/vcpkg-fmt-build/operation-copy-manifest.json:528 | 3 | no | yes | no |
| `.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros` | dir | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/acceptance-frontier.md:11<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/lanes/a06-unit3.json:20<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/lanes/a06-unit3.json:29 | 9 | yes | yes | yes |
| `dev/bootstrap.py` | file | untracked | mise.dev.toml:21<br>mise.dev.toml:26<br>mise.dev.toml:31 | 9 | yes | yes | yes |
| `dev/codex_examples.py` | file | untracked | mise.dev.toml:313<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/findings.md:44<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/a06-retrieval-refresh.md:3 | 8 | yes | yes | yes |
| `dev/empty-mise.toml` | file | untracked | dev/mise:16<br>dev/mise:17<br>dev/bootstrap.py:117 | 3 | yes | yes | yes |
| `dev/test_codex_examples.py` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/findings.md:45<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/lanes/a06-unit3.json:18<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/lanes/a06-unit3.json:27 | 4 | yes | yes | yes |
| `docs/agents/ticket-retro.md` | file | untracked | AGENTS.md:37<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/findings.md:51<br>.claude/rules/planning-records.md:8 | 24 | yes | yes | yes |
| `evidence/core-p2996` | dir | ignored-data | docs/core-qualification.md:6<br>docs/core-qualification.md:30<br>docs/core-qualification.md:32 | 1205 | yes | yes | yes |
| `evidence/core-p2996/operation` | dir | ignored-data | docs/core-qualification.md:24<br>evidence/p2996-tsan/contract.json:51<br>evidence/p2996-tsan/contract.json:52 | 1968 | yes | yes | yes |
| `evidence/iwyu-build` | dir | ignored-data | dev/toolchains/mise_runtime.py:65<br>dev/toolchains/iwyu_build.py:32<br>docs/iwyu-toolchain.md:66 | 526 | yes | yes | yes |
| `evidence/iwyu-build/operation` | dir | ignored-data | dev/toolchains/iwyu_relocation.py:84<br>dev/toolchains/iwyu_relocation.py:159<br>dev/toolchains/iwyu_reflection.py:95 | 332 | yes | yes | yes |
| `evidence/mise-runtime` | dir | ignored-data | dev/toolchains/mise_runtime.py:21<br>dev/toolchains/iwyu_relocation.py:111<br>dev/toolchains/iwyu_relocation.py:113 | 410 | yes | yes | yes |
| `evidence/mise-runtime/attempt1-invocation` | dir | ignored-data | evidence/mise-runtime/attempt1-manifest.json:23<br>evidence/mise-runtime/pre-review-secret-scan.json:54<br>evidence/mise-runtime/secret-scan.json:59 | 3 | yes | yes | yes |
| `evidence/mise-runtime/attempt2-invocation` | dir | ignored-data | evidence/mise-runtime/attempt2-manifest.json:83<br>evidence/mise-runtime/pre-review-secret-scan.json:74<br>evidence/mise-runtime/secret-scan.json:79 | 3 | yes | yes | yes |
| `evidence/mise-runtime/attempt3-invocation` | dir | ignored-data | evidence/mise-runtime/pre-review-secret-scan.json:144<br>evidence/mise-runtime/secret-scan.json:149<br>evidence/mise-runtime/attempt3-manifest.json:143 | 3 | yes | yes | yes |
| `evidence/mise-runtime/invocation` | dir | ignored-data | evidence/mise-runtime/pre-review-secret-scan.json:274<br>evidence/mise-runtime/operation-manifest.json:155<br>evidence/mise-runtime/secret-scan.json:334 | 3 | yes | yes | yes |
| `evidence/p2996-cmake` | dir | ignored-data | scratch/p2996-toolchain/README.md:17<br>scratch/p2996-toolchain/README.md:23<br>dev/toolchains/p2996_cmake.py:30 | 118 | yes | yes | yes |
| `evidence/p2996-cmake/independent-review` | dir | ignored-data | evidence/p2996-cmake/review-manifest.json:8<br>evidence/p2996-cmake/review-manifest.json:14<br>evidence/p2996-cmake/review-manifest.json:20 | 550 | yes | yes | yes |
| `evidence/p2996-cmake/operation` | dir | ignored-data | scratch/p2996-toolchain/README.md:19<br>evidence/p2996-cmake/operation-manifest.json:8<br>evidence/p2996-cmake/operation-manifest.json:14 | 741 | yes | yes | yes |
| `evidence/vcpkg-fmt-build` | dir | ignored-data | .gitattributes:4<br>.gitattributes:5<br>.gitattributes:6 | 562 | yes | yes | yes |
| `evidence/vcpkg-fmt-build/attempt-1` | dir | ignored-data | evidence/vcpkg-fmt-build/artifact-secret-scan.json:23<br>evidence/vcpkg-fmt-build/artifact-secret-scan.json:24<br>evidence/vcpkg-fmt-build/artifact-secret-scan.json:25 | 323 | yes | yes | yes |
| `evidence/vcpkg-fmt-build/operation` | dir | ignored-data | evidence/p2996-tsan/contract.json:102<br>evidence/p2996-tsan/contract.json:1348<br>evidence/p2996-sanitizer-repair/contract.json:102 | 448 | yes | yes | yes |
| `evidence/workflow-retro-gate/checks.json` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/workflow-retro-gate-2026-10-12.md:15<br>.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md:2556 | 2 | yes | yes | yes |
| `evidence/workflow-retro-gate/worktrees.json` | file | untracked | .planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/workflow-retro-gate-2026-10-12.md:13 | 1 | yes | yes | yes |

Basename-only matches (noisy; generic CMake names match unrelated evidence). Listed as `basename (refs, exists-in-tip)`:

`.pending-disappearing` (1, no), `.pending-interrupted` (1, no), `CMakeCCompiler.cmake` (111, yes), `CMakeCCompilerId.c` (22, yes), `CMakeCXXCompiler.cmake` (309, yes), `CMakeCXXCompilerId.cpp` (80, yes), `CMakeConfigureLog.yaml` (403, yes), `CMakeSystem.cmake` (106, yes), `InstallScripts.json` (197, yes), `TargetDirectories.txt` (107, yes), `apple-sdk.cpp` (67, yes), `application-audit-2026-10-12.md` (3, yes), `automation-amendment-draft.md` (6, yes), `bootstrap.py` (1, yes), `cmake.check_cache` (1, no), `cmake_install.cmake` (8318, yes), `compile_commands.json` (148, yes), `empty-mise.toml` (1, yes), `events.jsonl` (2, no), `install_manifest.txt` (100, no), `mise.dev.lock` (18, yes), `operations.jsonl` (1, no), `private-runtime-try-compile.log` (12, no), `pyproject.toml` (20, yes), `test_codex_examples.py` (2, yes), `ticket-retro.md` (9, yes), `uv.lock` (12, yes), `workflow-retro-gate-2026-10-12.md` (1, yes), `worktrees.json` (1, yes)

## Notes

- Overlap: `evidence/claude-amendment-review/` (53 files) and `dev/claude_review.py`, three docs, the amendment draft exist in both worktrees; both copies are kept per worktree, not deduplicated.
- Modified tracked files in 2a14 include `dev/saved-searches.toml` and `mise.dev.toml`; their diffs are against the 2a14 HEAD and may conflict with or already be superseded by the tip.
- Git use was read-only (`rev-parse`, `status --porcelain` with `GIT_OPTIONAL_LOCKS=0`, `ls-files`, `diff`, `archive` to scratch). No worktree or main-repo state was changed.

# R4: How to get a passing #13 LSan verdict (Q76)

Research only, 2026-10-14, session `ce9c0b3d`, tip `21af565`. No tracked MP file was edited, no GitHub
write was made, no native or container run was made. P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold`.
Offline mirror (D110): `offline/research/R4/` with `offline/research/R4/manifest.json` (101 items: 29
pages, 20 API captures, 49 search results, 3 clones). "Local:" below names the mirrored copy.

## 1. Verdict

Recommendation: do not choose a fallback yet. #13 is one small, upstream-documented step from passing.
Rerun the #13 A/B with the candidate runtime MP already built (the patched `sanitizer_procmaps_mac`
object, `patched/libclang_rt.lsan_osx_dynamic.dylib`, sha256 `c9ea058c...`) plus one runtime policy
addition: a module-level LSan suppression for the macOS arm64 Objective-C startup false positive
(`leak:libxpc.dylib`, or `leak:libobjc.A.dylib`), delivered as a contract-bound `suppressions=` file or a
compiled-in `__lsan_default_suppressions()`. Confidence: high (about 80%) that the clean LSan witness
passes and the leak witness still fails for the right reason; medium (about 60%) for the unrun
LSan+UBSan cells, which no evidence covers yet.

What decides it:

1. The 14c "deadlock" is fully explained, and the fix is upstream. MP's own sample shows the exit-time
   leak-check thread inside `get_dyld_hdr()` calling `dyld_shared_cache_iterate_text`, which lazily
   loads Dyld.framework and calls `calloc` while LSan holds its allocator lock
   (`evidence/p2996-lsan/diagnostic/sample-sample.txt:44-67`). bazel-contrib/toolchains_llvm#828
   (merged 2026-08-16) reports exactly this on arm64 macOS for LLVM 19.1.7, 20.1.8 and 21.1.8, and
   says LLVM 22.1.8, which carries llvm/llvm-project#182943 (`_dyld_get_dyld_header`, merged
   2026-02-24, commit `2e7d07a`), "exits normally" (https://github.com/bazel-contrib/toolchains_llvm/pull/828;
   local: `offline/research/R4/docs/toolchains_llvm-pr-828.md:35,50`). MP's pinned fork is LLVM 21
   and lacks it (section 3.2).
2. MP's candidate already removes the deadlock. In the #13 native trial the patched runtime "returned
   from the same reflection witness", and the only failure was 120 bytes in 3 allocations from
   objc/libxpc initialization (`4905c8e:docs/sanitizers.md:204-207`;
   `4905c8e:evidence/issue-13-lsan/native-attempt.json:13-14`).
3. Those 3 allocations are a known upstream false positive with the same size and count:
   llvm/llvm-project#115992 (opened 2024-11-13) shows `_fetchInitializingClassList` under
   `_xpc_collect_images` and `_libxpc_initializer`, and the fix, llvm/llvm-project#117478 (merged
   2026-04-09, commit `3b9f791`), reports "3 120 *_fetchInitializingClassList*" once suppressed
   (local: `offline/research/R4/docs/llvm-pr-117478.md:29`). Upstream's own remedy is a default
   suppression; it is in LLVM 23.1.1 but not in 22.x or in the fork (section 3.2).
4. A function-name suppression cannot fire under MP's options. MP runs `symbolize=0`
   (`evidence/p2996-lsan/contract.json:1414`), which leaves LSan with no symbolizer tools, so only the
   module-name match works (section 3.4). That is why the recommendation is a module suppression, not
   a backport of `3b9f791` alone.

If that rerun fails, the least-cost fallback is ASan with `detect_leaks=1` through the already
promoted ASan runtime (Task 14a3), with the same suppression; it removes the LSan install tickets but
needs a spec amendment because #11 and #23 name LSan and LSan+UBSan. A Linux container is the
fallback of last resort here, not the cheapest one (section 5).

The block is also procedural: the #13 trial verdict became INCONCLUSIVE because an unrelated `mise`
process failed the closure census (`native-attempt.json:17`), and the prepared clean-control
experiment never ran because three pre-run reviews failed the same census
(`4905c8e:P/retros/issue-13.md`, follow-up section). Any rerun needs a quiet host, not only a fix.

## 2. MP facts (read-only)

- #11 spec: "the current LSan witness times out during leak detection"; required modes include LSan
  and LSan+UBSan (gh issue view 11, created 2026-10-12). #12 seals the 14c failure; #13 "Private LSan
  repair verdict (14c1)" requires the runtime link recipe, original and candidate clean, leak and
  overflow controls, and accepts a "valid no-viable-repair outcome" (gh issue view 13, created
  2026-10-12, 0 comments). #14 prepares the installed ASan/TSan/LSan overlay "if the private repair
  qualifies"; #15 qualifies LSan and LSan+UBSan under the installed path; #19 runs LSan coverage
  cells; #23 says "Required LSan and admitted matrix cells are successful" (gh issue view 14, 15, 19,
  23; all OPEN, 0 comments).
- Ledger: #12 READY (closure `2cc4c029` in tip); #13 blocked by #12, "PARTIAL: offline repair 4905c8e
  in issue-13-lsan worktree (not in tip); native LSan trial inconclusive"; #14, #15, #19, #23 blocked
  in chain (`P/ticket-ledger.md:20-23,27,31`). P1 lists "#13 heavy ... M (14c deadlocked before)" and
  risk E5 "if the #13 verdict fails again: #19 never closes, so #23 and #30-#61 stall"
  (`P/reviews/ccm-20261014/reprioritize-2/P1-cxx-supply.md:40,55`).
- Git: `git log --all -- '*lsan*'` gives 9 commits; only `2cc4c02` (14c closure) is in HEAD. The #13
  line `5dcba5f`, `8991581`, `f113a89`, `dccbfbc`, `65d93d1`, `8062821`, `5e119e5`, `4905c8e` lives in
  the detached worktree `~/.codex/worktrees/issue-13-lsan/claude-code-marketplace` (`git worktree
  list`). `4905c8e` (2026-10-12) touches 12 files: the retro, `dev/test_lsan_control.py`,
  `dev/toolchains/p2996_lsan_control.py`, `docs/sanitizers.md` and signal-check receipts.
- 14c failure: standalone LSan compiled and linked, then "timed out during the clean exit-time leak
  scan"; the sample "places the worker inside dyld's lazy callback while LSan's allocator lock is
  held" (`docs/sanitizers.md:159-172`). With leak checking off the same binary exits 0 in 0.035 s;
  with it on it times out at 10 s (`evidence/p2996-lsan/diagnostic/direct-diagnostic.json`).
- Prewarm experiment: calling `dyld_shared_cache_iterate_text` from `main` first did not help; the
  second call goes to `dyld_shared_cache_iterate_text_swift`, which runs `_Block_copy`, which calls
  `malloc` and blocks on the same allocator lock (`evidence/p2996-lsan/diagnostic/prewarm-sample.txt:45-54`;
  witness `prewarm-witness.cpp`). So on macOS 27 every call allocates; warming the cache from user
  code cannot work.
- #13 candidate: the 97-object recipe with the macOS 27 mapping object substituted
  (`4905c8e:docs/sanitizers.md:174-186`); the mapping patch is
  `dev/toolchains/patches/p2996-asan-macos27-dyld.patch` (reads `TASK_DYLD_INFO`
  `dyldImageLoadAddress` on macOS 27 instead of iterating the shared cache). The same object already
  qualified installed ASan (14a3) and TSan (14b2b) (`docs/sanitizers.md:36-157`).
- #13 trial result: original clean timed out at 20 s; candidate clean exited 86 with 120 bytes in 3
  allocations; leak, LSan+UBSan clean, leak and overflow unrun; closure census failed on PID 84468
  (`4905c8e:evidence/issue-13-lsan/native-attempt.json`). The retained stderr
  (`~/.local/state/marketplace-tool-foundation/p2996-lsan-private-repaired-20261013T015212Z/lsan-clean.stderr`,
  sha256 `def997eb...`, equal to `candidate_clean_stderr_sha256`) shows 72 + 32 + 16 bytes, each
  stack libsystem_malloc, eight libobjc.A.dylib frames, libobjcMsgSend, two libxpc.dylib frames,
  libSystem.B.dylib, then dyld.
- Options in force: `LSAN_OPTIONS=detect_leaks=1:exitcode=86:symbolize=0`, no suppressions
  (`evidence/p2996-lsan/contract.json:1414`). Clean-control helper (prepared, never run): six cases,
  minimal and reflection witnesses, `DYLD_PRINT_LIBRARIES` on and off, 64-byte positive controls,
  each clean case expected to exit 0 (`4905c8e:evidence/issue-13-lsan/clean-control-contract.json`).
- Container route: root `mise.toml:20-26` pins an amd64 `debian:bookworm-slim` image with no clang;
  `ci/acceptance.sh` runs Claude acceptance inside it. There is no container C++ toolchain in MP today.

## 3. External findings

### 3.1 Root cause chain (pinned fork `f17c8d6c`, the p2996 branch head on 2026-10-14)

Permalinks are at https://github.com/bloomberg/clang-p2996/blob/f17c8d6c7bfef5e02ccadcf33517fd2a53b51b6e/
(local clone: `offline/research/R4/repos/clang-p2996-p2996`).
1. `LockStuffAndStopTheWorld` takes `ScopedStopTheWorldLock` (threads and allocator) and calls
   `StopTheWorld` (`compiler-rt/lib/lsan/lsan_common_mac.cpp#L231-L235`, `lsan_common.h#L162-L171`).
2. On Darwin `StopTheWorld` starts a thread and joins it (`sanitizer_common/sanitizer_stoptheworld_mac.cpp#L82-L86`).
3. The callback always runs `ProcessGlobalRegions` (`lsan/lsan_common.cpp#L724`), which always calls
   `DumpListOfModules`; `use_globals=0` skips only instrumented modules after the enumeration
   (`lsan/lsan_common_mac.cpp#L137-L162`). No `LSAN_OPTIONS` value avoids the enumeration.
4. The first enumeration calls `get_dyld_hdr()`, which on macOS 13+ calls
   `GetDyldImageHeaderViaSharedCache()` (`sanitizer_common/sanitizer_procmaps_mac.cpp#L190-L238`).
   Standalone LSan never calls it earlier, so the first call happens with the lock held.
5. Since macOS 26.4, Dyld.framework reimplemented `dyld_shared_cache_iterate_text` in Swift and it
   allocates via `_Block_copy` (bun shim comment, https://github.com/oven-sh/bun/blob/b5f2d0a85892ccb19269a71591abd5cc434d8753/scripts/build/shims/asan-dyld-shim.c#L1-L13,
   local `offline/research/R4/docs/bun-asan-dyld-shim-b5f2d0a.md`; apache/doris#68595, merged
   2026-09-30, local `offline/research/R4/docs/doris-pr-68595.md:51-67`). Under ASan the same call
   deadlocks at init (MP Task 14a); under LSan it deadlocks at exit. Apple lists "Address Sanitizer
   and Thread Sanitizer might hang on macOS 26.4" with "Use Xcode 26.4" as the workaround (Xcode
   26.4 release notes, issue 171762808,
   https://developer.apple.com/documentation/xcode-release-notes/xcode-26_4-release-notes; local
   `offline/research/R4/docs/xcode-26_4-release-notes-md.md:26-28`); that fixes Apple clang only.

No fork is involved: the sample has the main thread in `exit` and one tracer thread
(`sample-sample.txt:24-44`), so fork-time LSan deadlocks are not the cause here.

### 3.2 Upstream fixes and where they ship

| Fix | Upstream | In LLVM 22.1.x | In LLVM 23.1.1 | In fork `f17c8d6c` (LLVM 21) |
|---|---|---|---|---|
| Use `_dyld_get_dyld_header` (weak) before iterating the cache | llvm/llvm-project#182943, `2e7d07a`, 2026-02-24; backport #188913 merged 2026-03-31 as `7b6514c` | yes from 22.1.3 (`gh api compare 7b6514c...llvmorg-22.1.3` = ahead; 22.1.2 = behind) | yes (compare = ahead) | no (`grep -c _dyld_get_dyld_header` = 0) |
| Default suppressions `*_fetchInitializingClassList*` and `*dyld4::RuntimeState::_instantiateTLVs*` under `SANITIZER_ARM64` | llvm/llvm-project#117478, `3b9f791`, 2026-04-09 | no (`lsan_common.cpp` at `llvmorg-22.1.8`, kStdSuppressions L115-L128) | yes (`llvmorg-23.1.1` `lsan_common.cpp#L124-L130`) | no |
| Correct dyld segment slide, drop overlapping LINKEDIT | llvm/llvm-project#167800 (re-land of #166005), `4fe79a7`, 2025-11-14 | yes (compare to 22.1.8 = ahead) | yes | no (`grep -c overlap` = 0) |

Sources: diffs `offline/research/R4/api/2e7d07a.diff`, `3b9f791.diff`; PR JSON `api/pr-182943.json`,
`api/pr-117478.json`, `api/pr-188913.json`, `api/pr-166005.json`; clone
`offline/research/R4/repos/llvm-project-23.1.1` (commit `6dfe1677`):
`compiler-rt/lib/sanitizer_common/sanitizer_procmaps_mac.cpp:247-257` and
`compiler-rt/lib/lsan/lsan_common.cpp:115-131`. bloomberg/clang-p2996 branches `p2996` and `purpose`
both still set `LLVM_VERSION_MAJOR 21` (`gh api .../contents/cmake/Modules/LLVMVersion.cmake?ref=p2996`).
The `#167800` row matters only as a possible second backport: MP's candidate stack shows several dyld
frames as `<unknown module>`, consistent with that slide bug (UNVERIFIED as a leak cause).

### 3.3 Platform status

- LLVM docs list macOS among LeakSanitizer platforms and say ASan leak detection "can be enabled using
  ASAN_OPTIONS=detect_leaks=1 on macOS" (https://clang.llvm.org/docs/LeakSanitizer.html,
  https://clang.llvm.org/docs/AddressSanitizer.html; local `docs/clang-docs-LeakSanitizer.md`,
  `docs/clang-docs-AddressSanitizer.md`). `detect_leaks` defaults to off on Apple
  (`sanitizer_flags.inc#L77` in the fork); `CAN_SANITIZE_LEAKS` is 1 for Apple aarch64
  (`lsan/lsan_common.h#L39-L42`).
- Apple engineers call it weak: llvm/llvm-project#131678 "detect_leaks=1 does not work well on Darwin
  Apple Silicon Macs" (open, 2025-03-17) and #131676 disabled leak detection in ASan tests on non-Intel
  Darwin (merged 2025-03-18); a reviewer on #117478 wrote "we know LSAN doesn't work well on AS"
  (2025-09-10). Same symptom in the field: Discourse thread 73148 (2023-08-31, false positives on
  macOS 13 arm64, some frames only `<unknown module>`; local `docs/discourse-lsan-macos13-apple-silicon-73148.md`),
  tarantool/tarantool#13019 (2026-08-05, clang-21, ASan `detect_leaks=1`, the same 72-byte
  `_fetchInitializingClassList` leak; local `docs/tarantool-issue-13019.md`), rust-lang/rust#121624.
- cpp-best-practices/cmake_template#151 (merged 2026-05-02) drops `-fsanitize=leak` on Apple hosts
  because Apple clang rejects it on arm64; MP's P2996 clang accepts it
  (`evidence/p2996-lsan/driver-probe/summary.json`), so this limit does not apply to MP.
- A llvm/llvm-project#200447 comment (2026-09-09) reports Homebrew LLVM 23.1.0 ASan running in 0.68 s
  on macOS 26.5.2 where older runtimes hang (local `docs/llvm-issue-200447.md`).

### 3.4 Why the suppression must be module-level under `symbolize=0`

`LeakSuppressionContext::GetSuppressionForAddr` first matches the module name, then the symbolized
function and file (`lsan/lsan_common.cpp#L148-L169`); `SuppressByRule` tries every frame of the
allocation stack (`#L215-L227`); suppressions come from the `suppressions` flag, the weak
`__lsan_default_suppressions()` hook and the built-in list (`#L136-L146`). With `symbolize=0`
`ChooseSymbolizerTools` returns before adding any tool
(`sanitizer_common/sanitizer_symbolizer_posix_libcdep.cpp#L478-L483`), so function names are null and
only module templates such as `leak:libxpc.dylib` can match. In MP's retained stacks both libxpc and
libobjc frames carry module names, so either template matches all three reports. The upstream
function template would need `symbolize=1`, which on Darwin spawns `atos`; whether `atos` works
inside MP's `sandbox-exec` profile is UNVERIFIED.

### 3.5 Linux and containers

- On Linux LSan stops the world with a cloned tracer that `PTRACE_ATTACH`es each thread after
  `PR_SET_PTRACER` (`sanitizer_stoptheworld_linux_libcdep.cpp#L145-L149,#L457` in the fork); without
  ptrace it dies with "LeakSanitizer has encountered a fatal error", fixed in Docker with
  `--cap-add SYS_PTRACE` (google/sanitizers#764, 2017-02-01; #916, 2018-02-17; local
  `api/gs-764.json`, `api/gs-916.json`). Docker's current default seccomp profile allows `ptrace` on
  kernels 4.8 and newer (https://github.com/moby/profiles/blob/6fe7deb1b9fb7c0397a4593480d7d22b9ee8caef/seccomp/default.json#L429-L438;
  local `docs/moby-profiles-seccomp-default.md`). Docker Desktop's kernel version on this host is
  UNVERIFIED.
- Projects running sanitizers with clang-p2996 do it on Linux: spiritEcosse/storm runs an ASan+LSan+UBSan
  preset with `ASAN_OPTIONS=detect_leaks=1` and notes "On Linux, LSAN is automatically included in ASAN"
  (https://github.com/spiritEcosse/storm/blob/3bf877e5294cac57a4b716cd4dbc856568b0c11d/docs/internals/testing/SANITIZERS.md#L57-L60;
  local `docs/storm-SANITIZERS.md`). No project was found running LSan with clang-p2996 on macOS
  (code search `"clang-p2996" fsanitize`, 29 hits, none on Darwin).
- The user's own dotfiles devcontainer builds clang-p2996 for amd64 and arm64 but with
  `LLVM_ENABLE_RUNTIMES="libcxx;libcxxabi;libunwind"`, so no compiler-rt and no sanitizer runtime, and
  notes a "~2h compiler rebuild" (https://github.com/ray-manaloto/dotfiles/blob/a52a3c3c389b6933ca0b8abc2a6645782c70f759/.devcontainer/Dockerfile#L516-L531,
  #L18; local `docs/dotfiles-devcontainer-Dockerfile.md`). Prebuilt third-party images exist
  (Docker Hub `vsavkov/clang-p2996`, GitHub `yusufemresamur/docker-clang-p2996`; Exa results), but
  their compiler-rt content and provenance are UNVERIFIED.

## 4. Options ranked, and what each changes in #14, #15, #19, #23

| Option | What runs | Cost | Evidence it passes | #14 | #15 | #19 | #23 |
|---|---|---|---|---|---|---|---|
| A (recommended) Candidate v2 = existing patched dylib + module suppression | New #13 proposal and review, one A/B native run (minutes, P1:27) | S code (suppression file or `__lsan_default_suppressions` in the witness, contract rows, verdict checker), one heavy run | 3.1, 3.2, 3.4; MP trial shows the deadlock gone | Overlay adds the LSan row exactly like ASan/TSan; the suppression file becomes a bound guard input | Qualify installed LSan and LSan+UBSan with the policy; assert "Suppressions used" lists only the expected template (3 allocations, 120 bytes) so over-suppression fails | Coverage runs use the same bound policy | Unchanged requirement; acceptance binds the policy hash and macOS 27.0.1 build |
| A2 Backport `2e7d07a` and `3b9f791` (and optionally `4fe79a7`) into the 97-object recipe, `symbolize=1` | Rebuild 2 or 3 objects, relink, same A/B | M; adds `atos` at report time | Matches LLVM 23.1.1 behaviour exactly; ydb vendored the same dyld backport into clang 20 runtime | As A, plus the replaced `lsan_common` object | As A; `atos` inside the sandbox UNVERIFIED | As A | As A |
| B ASan `detect_leaks=1` through the promoted ASan runtime + same suppression | No new runtime; new witness cells | S, but a spec change | ASan init already caches the dyld header through the patched object (14a); false positive identical (#115992 covers both) | Closes as superseded (no LSan install) | Becomes ASan-leak and ASan+UBSan-leak qualification | Cells move to ASan-leak | #11 and #23 must be amended: they name LSan and LSan+UBSan |
| C LSan in a Linux arm64 container | Build clang-p2996 with compiler-rt for Linux (new image), Docker admission | L (about 2 h build per dotfiles, new image, container and host-heavy admission) | LSan is primary on Linux; ptrace allowed by default seccomp on 4.8+ | Replaced by an image recipe and digest pin | Qualifies in the container, not the macOS installed path | Linux coverage cells; needs gcov or llvm-cov in image | Matrix gains a Linux host; the macOS LSan cell is dropped by decision |
| D Interpose shim (bun pattern) linked into witnesses | Original runtime, shim dylib | S, fragile | Bun used it for ASan init until LLVM 23.1.1 removed the need (bun#42851, 2026-09-16) | No runtime install | Qualifies "original runtime + shim" | Every test binary links the shim | Same cells; non-standard |

Order: run A first (it is the #13 verdict with the smallest change). If A's clean case still reports
leaks that no module template matches, the platform false positives are not controllable on this host
and C is the honest fallback. If A fails only on LSan+UBSan or install mechanics, B is cheaper than C.
Option D is a stopgap only: its callback calls `dlsym` (shim line 59), which itself may allocate inside
the stopped world (UNVERIFIED); resolve the pointer in a constructor if it is ever used.

Before admitting A, MP's six-case clean-control helper should gain two cases with the suppression
(minimal and reflection clean, trace off), because as written every clean case will exit 86 for the
known false positive; the existing cases then become the "unsuppressed reproduces upstream #115992"
control.

## 5. Code examples found

| Repo | Path | Commit or permalink | Local copy | Use |
|---|---|---|---|---|
| llvm/llvm-project | `compiler-rt/lib/sanitizer_common/sanitizer_procmaps_mac.cpp`, `weak_symbols.txt` | `2e7d07a33725a82ecfc514e27f047ece3ff13d4c` | `api/2e7d07a.diff` | Upstream dyld header fix to cherry-pick |
| llvm/llvm-project | `compiler-rt/lib/lsan/lsan_common.cpp` | `3b9f7913148d0f5d952ce85e8d8dd6ae4fec678b` | `api/3b9f791.diff` | Upstream default suppressions |
| ydb-platform/ydb | `contrib/libs/clang20-rt/patches/pr182943_macos26_asan.patch` | `733f91d00184819527ea7aa32d76efd7117d5c7b` | `api/ydb-pr182943.patch`, `docs/ydb-pr182943_macos26_asan-patch.md` | Backport of #182943 into an older vendored runtime |
| oven-sh/bun | `scripts/build/shims/asan-dyld-shim.c` | `b5f2d0a85892ccb19269a71591abd5cc434d8753` (removed in `c6b7fcb5bb81`) | `api/bun-shim-b5f2d0a.c` | `__interpose` shim using `_dyld_get_dyld_header` |
| bazel-contrib/toolchains_llvm | `.github/workflows/tests.yml`, `tests/BUILD.bazel` | `9f7efa8798803882658ff409ba05cc658e575b69` | `api/tl-828.diff`, clone `repos/toolchains_llvm` | macOS LSan CI pinned to LLVM 22.1.8 |
| sueszli (comment on #115992) | `lsan.supp` with `leak:_fetchInitializingClassList` | issue comment 2025-10-01 | `docs/llvm-issue-115992.md` | Suppression file plus `LSAN_OPTIONS=suppressions=` |
| miguno/helloc, DrylandEcology/SOILWAT2, quentinlampin/cschc | `lsan.supp`, `.LSAN_suppr.txt`, `darwin/darwin.lsan` | `8a88efe1`, `b05f410a`, `6db8bb7d` | `search/saved/g-fetchinit-supp.json` | Same suppression in practice (106 code hits) |
| FreeRADIUS/freeradius-server | `src/lib/util/debug.c` | `d91f90ba19674ff3fdec81e14957ff5c1cbd53fd` | `search/saved/g-lsan-default-supp.json` | `__lsan_default_suppressions` with libobjc entries |
| spiritEcosse/storm | `docs/internals/testing/SANITIZERS.md` | `3bf877e5294cac57a4b716cd4dbc856568b0c11d` | `docs/storm-SANITIZERS.md` | clang-p2996 sanitizers on Linux |

All local paths are under `offline/research/R4/`. No mirrored code was executed.

## 6. Routes

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 0 | MP issues | `gh issue view <n> --repo ray-manaloto/claude-code-marketplace --comments` | 0 | empty output (non-TTY) | no; replaced by `--json ...,comments` (rc 0, 8 issues) |
| 0 | MP Git and evidence | `git log --all -- '*lsan*'`, `git show --stat 4905c8e`, `git show 4905c8e:<path>`, `cat`, `grep` | 0 | 9 commits, 3 evidence dirs | yes |
| 0 | Pinned source | read `~/.local/state/.../p2996-source-f17c8d6c/source` | 0 | n/a | yes |
| 1 | Exa | `fnox ... exec -- exa.sh` (curl POST api.exa.ai/search) x6 | 0, HTTP 200 x6 | 60 | yes (decisive leads) |
| 1 | Context7 | `fnox ... exec -- ctx7 library "<lib>" "<query>"` x2 | 1, 1 | 0 | no: "Monthly quota reached" (gap) |
| 1 | Firecrawl | `fnox ... exec -- firecrawl search "<q>" --limit 5 --json` | 1 | 0 | no: HTTP 402 insufficient credits (gap) |
| 1 | webclaw (Firecrawl fallback) | `webclaw <url> -f markdown > <file>.md` x29 | 0 x29 | 29 pages | yes; Xcode HTML page returned a JS stub, its `.md` and `.json` forms worked |
| 1 | Serper | `fnox ... exec -- serper.sh` (curl POST google.serper.dev) x4 | 0, HTTP 200 x4 | 0, 8, 5, 8 | yes (Xcode notes, maskray) |
| 1 | SerpApi | `fnox ... exec -- python3 -I serpapi.py` | 1 then 0 | read timeout at 40 s; retry at 90 s: 8 | yes (corroboration only) |
| 1 | Last30Days | `fnox ... exec -- env SSL_CERT_FILE=/etc/ssl/cert.pem python3 -I last30days.py ... --plan plan.json --quick` | 1 (mise `timeout` shim), then 0 | 1 off-topic Reddit thread; grounding and jobs "error", HN 0 | no (gap: nothing on topic in 30 days) |
| 2 | gh search issues/prs | 12 queries (`sanitize`, `address`, `macos` in bloomberg/clang-p2996; `dyld_shared_cache_iterate_text`, `_fetchInitializingClassList`, `_dyld_get_dyld_header`, and 6 more) | 0 x12 | 1, 30, 12, 18, 18, 11, 0, 30, 0, 0, 0, 0 | yes |
| 2 | gh pr/issue view | llvm #182943, #117478, #188913, #166005, #167800, #131676, #115992, #131678, #200447; toolchains_llvm #828; tarantool #13019; doris #68595; google/sanitizers #764, #916 | 0 each | n/a | yes |
| 2 | gh api | commit diffs, `compare` to tags, `contents?ref=` for fork and tags, moby/profiles | 0 each | n/a | yes |
| 2 | GraphQL DISCUSSION | 5 queries plus control `README` (103,614) | 0 x6 | 6, 0, 0, 0, 0 | no relevant hit |
| 2 | Saved search (reproduced) | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5 -F page=1` with `README` controls | 0 | llvm control 423; `_dyld_get_dyld_header` 3; `_fetchInitializingClassList` 1; bun control 322, shim 0; toolchains_llvm control 1, `lsan_osx_dynamic` 1 | yes |
| 2 | Saved search on the fork | same, `repo:bloomberg/clang-p2996` | 0 | control `README` 0 | no: fork not indexed, uncontrolled empty (gap) |
| 2 | Global code search | `leak:_fetchInitializingClassList` 106; `"leak:libobjc"` 58; `_dyld_get_dyld_header` 215; `freflection fsanitize` 172; `"clang-p2996" fsanitize` 29; `__lsan_default_suppressions libobjc` 1 | 0 (4 first tries HTTP 403 secondary rate limit, retried paced) | as listed | yes |
| D110 | Clones | `git clone --filter=blob:none [--depth 1 --branch <ref> --sparse]` x3 | 0 x3 | llvm `6dfe1677`, fork `f17c8d6c`, toolchains_llvm `adf59ed6` | yes |

## 7. Proposed saved-search rows (not applied to `dev/saved-searches.toml`)

```toml
[[search]]
id = "llvm-darwin-dyld-header"
query = "_dyld_get_dyld_header"
repo = "llvm/llvm-project"
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "llvm-lsan-apple-suppressions"
query = "_fetchInitializingClassList"
repo = "llvm/llvm-project"
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "llvm-dyld-shared-cache-iterate"
query = "dyld_shared_cache_iterate_text"
repo = "llvm/llvm-project"
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "toolchains-llvm-darwin-lsan"
query = "lsan_osx_dynamic"
repo = "bazel-contrib/toolchains_llvm"
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

Measured today: 3, 1, 2 and 1 hits with passing controls. A fork watch cannot use code search
(control 0); it needs a separate check such as `gh api
repos/bloomberg/clang-p2996/contents/compiler-rt/lib/sanitizer_common/sanitizer_procmaps_mac.cpp?ref=p2996`
grepped for `_dyld_get_dyld_header`, which the current collector does not support.

## 8. Open gaps

- Whether the 3-allocation false positive is deterministic on macOS 27.0.1 was seen once
  (one candidate run). tarantool#13019 says clang-22 does not reproduce it although 22.1.8 lacks the
  suppression (`api/lsan_common-llvmorg-22.1.8.cpp:115-128`); reason UNVERIFIED.
- LSan+UBSan on Darwin with the patched LSan dylib has never run (`native-attempt.json` unrun list).
- `atos` under `sandbox-exec` (needed only for option A2) is UNVERIFIED.
- Docker Desktop kernel version, arm64 compiler-rt build time and image size for option C are
  UNVERIFIED; dotfiles is another repository and needs its own admission.
- Context7 (quota), Firecrawl (HTTP 402) and Last30Days (no on-topic result) gave nothing;
  GitHub Discussions had no relevant thread; code search does not index bloomberg/clang-p2996.
- Thread-local leaks (`dyld4::RuntimeState::_instantiateTLVs`, the second `3b9f791` entry) are not
  covered by a libxpc or libobjc module template; relevant only if witnesses start threads with
  `thread_local` data.

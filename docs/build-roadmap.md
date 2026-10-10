# Native research-core task index

PLAN_ID: `2026-10-10-marketplace-macos-reflection-scaffold`.
Follow [accepted decisions](accepted-decisions.md) before historical recommendations.
The upstream task plan is the immutable `reuse-and-preset-matrix.md` entry in
[source-hash-audit.json](../evidence/onboarding/source-hash-audit.json), SHA-256
`0ef84b996588568a9419db7c7edde269536c932d3348cbef3a627ad372169e8a`.
This index preserves its task IDs and dependency order. It does not claim that
source-backed pins or candidate tools have been installed or qualified.

## Execution contract

One purpose, an explicit file allowlist, at most about five maintained files and
300 handwritten changed lines per implementation/review unit. Each unit gets
prerequisite receipts, focused checks and separate review before expansion.
Generated matrices are checked mechanically for deterministic regeneration,
complete tuples/exclusions and native CMake validity. Long builds are separately
admitted operations with durable logs and actual final exit codes.

The N0–N4 onboarding milestone covers project guidance/configuration/development
checks. It satisfies only the onboarding portion of task 03; the C++ skeleton
and its build acceptance still depend on a qualified compiler/toolchain lane.
The next project unit after N4 is 01. Tasks 04 and 02 follow in that order.

| ID | Bounded deliverable | Prerequisite | Acceptance |
| --- | --- | --- | --- |
| 01 | Reuse adoption spike in scratch | N4 | Licenses, selected upstream paths/pins; no shared vcpkg bootstrap |
| 04 | Global mise build-tool foundation and named environments | Separate ownership phase | Exact preimages, reviewable patch, existing compiler environment preserved |
| 02 | Representative TCPM matrix | 04 | CMake 4.4.4 lists all four preset kinds; exclusions legal; two generations identical |
| 05 | GCC16 installation/environment | 04 | Native mise bootstrap; compiler/stdlib identity; reflection compile/link/run |
| 06 | P2996 source/configure recipe | 04 | Exact source identities, matching runtimes, resumable native CMake/Ninja configure |
| 07 | P2996 cold build/install | 06 and heavy admission | Final build/install exit codes, reflection witness, mise registration |
| 08 | LLVM tools | 07 | clangd, format, tidy, analysis, archive and coverage fixtures including reflection |
| 09 | Matching-fork IWYU | 07 | Exact fork libraries/headers; resource relocation; apply recommendations and rebuild |
| 10a | P2996 CMake toolchain fixture | 07 | Intended compiler/SDK/libc++; reflection configure/build/test |
| 10b | GCC16 CMake toolchain fixture | 05 | Intended compiler/SDK/libstdc++; reflection configure/build/test |
| 03 | Minimal library/executable/test skeleton | 01 and 10a or 10b | Existing marketplace behavior plus real qualified-toolchain build/test |
| 11 | Global vcpkg/tool plus project manifest | 04 and ownership phase | Exact checkout/bootstrap provenance; registry baseline recorded independently |
| 12a | P2996 static/shared overlay triplets | 10a and 11 | App and compiled dependency agree on compiler/runtime and requested linkage |
| 12b | GCC16 static/shared overlay triplets | 10b and 11 | Same parity/linkage receipts for GCC |
| 13 | Generated baseline presets | 02, 03, 12a, 12b | Eight configure trees; 32 cells; every configuration and independent linkage pair |
| 14 | LLVM sanitizer families in separate units | 13 | ASan/UBSan then TSan/LSan families; positive/negative witnesses and consumers |
| 15 | GCC sanitizer families | 13 | ASan/UBSan witnesses; unsupported Darwin modes explicitly evidenced |
| 16 | Coverage cross-product | 13 and each admitted sanitizer family | Real coverage data, merge/report tools and each combination qualified |
| 17 | Analysis and development commands | 08, 09, 13 | Dedicated Multi-Config trees, qualified tools, nonzero return codes preserved |
| 18 | Conventional CMake package | 13 | Relocated external static/shared consumers and transitive dependency |
| 19 | Native CPS package | 18 | Independent CPS-only relocated consumers from the same target model |
| 20 | Final acceptance operation | 14–19 and all admitted profiles | Fresh-shell isolation, warm cache, drift, full admitted matrix and relocation |

## Matrix contract

P2996 Clang and GCC16; C++26 required, extensions disabled and a real reflection
witness. Each normal tree supports Debug, Release, RelWithDebInfo and MinSizeRel.
Project linkage and dependency linkage are independent static/shared dimensions.
The baseline is 2 compilers × 2 project linkages × 2 dependency linkages = 8
trees and 32 configuration cells.

Candidate instrumentation is eight P2996 modes (none, ASan, UBSan, ASan+UBSan,
TSan, TSan+UBSan, LSan, LSan+UBSan) and four GCC Darwin modes (none, ASan, UBSan,
ASan+UBSan), each with coverage off/on. That yields 96 candidate trees and
384 cells before qualification. An unresolved required capability stays
incomplete; do not label it unsupported simply to finish the matrix.

Use per-compiler toolchains. vcpkg remains `CMAKE_TOOLCHAIN_FILE` and chainloads
the matching compiler toolchain in the application and overlay triplets. Keep
tool checkout and registry baseline identities separate. Commit native preset
JSON so consumers need not install Python/TCPM. A failed TCPM trial is retained;
start with split/inherited native presets before inventing a replacement.

## Admission and inherited evidence

Global mise has one writer. Before changing it, inventory concurrent writers,
back up exact preimages, prepare a reviewable patch and preserve unrelated
default compiler behavior. Global Python promotion and local OpenTelemetry work
are separate streams. No host `chezmoi apply` is part of this plan.

Only one host-wide heavy build may run. Container/host capacity was not established
by the stalled earlier census; require a fresh census and shared-capacity check
before containers, a cold LLVM build or the matrix operation. Never stop unknown
services. Source and runtime tool identity must be re-attested at installation.

Strict-five research remains incomplete: Context7 quota, Firecrawl 402 with
provisional fallbacks, and Last30Days validator rejection are carried forward.
The source index and raw receipts are immutable. New evidence belongs to this
worktree; never edit the monitor's evidence index or goal.

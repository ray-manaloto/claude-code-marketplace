# Native baseline presets

The root TCPM template generates committed native CMake 4.4.4 presets. Users of
the generated JSON do not need Python or TCPM. The eight trees vary P2996/GCC16,
core static/shared, and fmt static/dynamic independently. Each has Debug,
Release, RelWithDebInfo and MinSizeRel build/test presets and one workflow.

Generation and native listing passed independent review in
[`baseline-presets`](../evidence/baseline-presets/review.json). Task 13b's native
runner exited 0: all 32 cells and 175 commands passed. Independent artifact
[review](../evidence/baseline-build/artifact-review.json) passed without findings.

These are host qualification presets with exact retained compiler, SDK and fmt
paths. `MARKETPLACE_BUILD_ROOT` must name a fresh private operation directory.
The guarded [`baseline.py`](../dev/toolchains/baseline.py) runner prepares it
after independent review and fresh shared-capacity admission. It uses the
canonical heavy-operation lease, one build/test job and confined private writes.

Public vcpkg composition keeps manifest installation and app-local copying off.
Debug consumes retained Debug fmt; the other three configurations use Release.
Root metadata records the actual selected target files. The native gate checks
compiler/SDK parity, linkage, CTest results, ARM64 outputs and loaded runtime/fmt
paths. Loaded-path evidence does not establish symbol-level runtime exclusivity.
Dependency installations, source inputs and unrelated compiler defaults must
remain unchanged. Sanitizers, coverage, caches and exports are later units.

The first launch refused an unrecognized mise process before any native command.
After that process exited, fresh capacity admitted the unchanged runner. The
successful retry preserved the original failure and all 579 exact text artifacts.
Selected compiler runtimes and macOS system C++ libraries coexist in loader traces.

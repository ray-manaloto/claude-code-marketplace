# Qualified LLVM tool fixtures

Task 08a uses the registered P2996 prefix from [task 07](p2996-toolchain.md).
Run `python3 -B dev/toolchains/p2996_tools.py --run-dir /absolute/new/private/directory`
only with a matching admission receipt and fresh shared-capacity check.
The helper preserves the prefix, source/build inventory and global/default state,
and uses the existing named profile and shared lease for sequential bounded work.

The [pinned-source contract](../evidence/p2996-tools/source-contract.json) defines
formatting, clangd and archive behavior. The fixture passes a private filename to
clang-format, with an explicit style, and requires nonempty output to reject an
ignored file. A second producing pass must be nonempty and byte-identical, which
also proves the formatted filename was not ignored. It checks a diagnostic
control, compiles the actual formatted reflection source, creates an archive,
links and runs the witness.
The loader must resolve all three previously qualified private C++ runtimes.

Clangd checks that same source through an explicit compilation database. User
configuration, background indexing, tidy and per-token editor checks are disabled.
Its process alone gets an empty executable search path to prevent macOS driver
lookup; compiler and SDK paths are absolute. No language-server session starts.
The native check must use the database and finish with zero errors.

The [native operation](../evidence/p2996-tools/operation/qualification.json)
passed, including the expected failing format control and complete preservation
checks. [Independent review](../evidence/p2996-tools/tools-review.json) passed
without findings and reproduced the same formatted source, object, archive and
executable hashes. All 19 original acceptance files remain unchanged.

Task 08b's `dev/toolchains/p2996_analysis.py` prepares bounded tidy and analyzer
controls from the [pinned source contract](../evidence/p2996-analysis/source-contract.json).
Tidy selects one check with explicit configuration and all fixes disabled. The
private reflection witness must produce the intended error, then pass after one
braces correction. The analyzer records the null warning in a fresh plist, then
separately checks its error-exit mode, which removes the output. Clean and full
reflection cases retain error mode and require fresh plists with no diagnostics.
All calls preserve source bytes. The [native operation](../evidence/p2996-analysis/operation/qualification.json)
and [independent reproduction](../evidence/p2996-analysis/analysis-review.json)
passed all six controls and preservation checks without findings.
The driver takes `--analyzer-output plist` as two arguments. The
[correction receipt](../evidence/p2996-analysis/source-contract-correction.json)
supersedes that spelling in the original proposal and retains the failed attempt.
The [report-lifetime correction](../evidence/p2996-analysis/report-lifetime-correction.json)
explains why report collection and failing-exit behavior need separate controls.
Both failed attempts remain recorded. Coverage and IWYU follow separately.

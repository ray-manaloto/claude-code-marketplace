# Bounded TCPM trial

This is development tooling for task 02. The generator is pinned to
`thirtytwobits/the-cmake-preset-matrix@f532db0b25843aaad0dd6c481923c6840425485b`.
The [source receipt](../../evidence/tcpm/source-acquisition.json) verifies all
19 acquired files against their pinned Git blobs, including the generator code,
CLI contract and license. All 13 installed source files match those blobs.
The [initial environment receipt](../../evidence/tcpm/environment-qualification.json)
records successful installation on Python 3.14.8. Actual generation then failed
on TCPM's instance `__annotations__` access; the [failure receipt](../../evidence/tcpm/matrix-initial.json)
is retained. TCPM declares support through Python 3.13. The separate
[Python 3.13.12 environment](../../evidence/tcpm/environment-python313.json)
passes installation, source identity and generation without changing TCPM code.

Use an existing Python 3.13 interpreter and uv; do not promote global Python or
install the generator globally. The project environment and uv cache are private
task state. Native preset consumers will use checked-in JSON without Python.
`uv.lock` fixes parsimonious 0.11.0 and regex 2026.9.29. The qualification used
uv 0.13.0 and existing Python 3.13.12 with automatic Python downloads disabled;
`--no-build-package regex` required its prebuilt wheel. Exact commands and the
private environment path are retained in the environment receipt. Reuse that
environment with `UV_PROJECT_ENVIRONMENT` and `uv run --no-sync --offline`, or
create a new task-local environment with `uv sync --frozen` and an existing
compatible interpreter. No global tool installation is needed.

TCPM's default schema URL tracks CMake master. The qualification command sets
`--no-schema-validation` to avoid that moving network input, then uses native
CMake 4.4.4 for preset validation. Generator-side schema validation is skipped.

The [matrix receipt](../../evidence/tcpm/matrix-python313.json) records two identical
generations, all four native preset listings, three configure trees and twelve
build/test cells. Each tree supports Debug, Release, RelWithDebInfo and MinSizeRel.
The excluded `gcc16/tsan` tuple is absent. Native CMake rejects both workflow
inheritance and a workflow whose build step crosses into another configure tree.
Compiler labels and exclusions are syntactic inputs; no compiler, sanitizer
runtime, CMake configure/build or vcpkg bootstrap is qualified.

With the private environment selected, run `qualify.py --cmake <absolute-cmake>
--tcpm <environment>/bin/tcpm --run-dir <new-private-directory>` through
`uv run --no-sync --offline --project <this-directory> --python <existing-python>
--no-python-downloads python`. The default mode verifies checked-in JSON;
`--update` replaces it only after all checks pass. Receipts include exact argv,
return codes, input/output hashes and negative controls.

Upstream license: [full MIT notice](../../evidence/tcpm/source/LICENSE.rst.source).

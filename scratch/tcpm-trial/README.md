# Bounded TCPM trial

This is development tooling for task 02. The generator is pinned to
`thirtytwobits/the-cmake-preset-matrix@f532db0b25843aaad0dd6c481923c6840425485b`.
The [source receipt](../../evidence/tcpm/source-acquisition.json) verifies all
19 acquired files against their pinned Git blobs, including the generator code,
CLI contract and license. All 13 installed source files match those blobs.
The [environment receipt](../../evidence/tcpm/environment-qualification.json)
records successful lock/sync, TCPM 0.3.3 version/help, exact Git provenance and
unchanged global mise files. Independent 02a review passed; generation has not run.

Use an existing Python 3.14 interpreter and uv; do not promote global Python or
install the generator globally. The project environment and uv cache are private
task state. Native preset consumers will use checked-in JSON without Python.
`uv.lock` fixes parsimonious 0.11.0 and regex 2026.9.29. The qualification used
uv 0.13.0 and existing Python 3.14.8 with automatic Python downloads disabled;
`--no-build-package regex` required its prebuilt wheel. Exact commands and the
private environment path are retained in the environment receipt. Reuse that
environment with `UV_PROJECT_ENVIRONMENT` and `uv run --no-sync --offline`, or
create a new task-local environment with `uv sync --frozen` and an existing
compatible interpreter. No global tool installation is needed.

TCPM's default schema URL tracks CMake master. The bounded generation command
will set `--no-schema-validation` to avoid that moving network input, then use
the qualified native CMake 4.4.4 for preset validation. This is a replacement
validation gate, not a claim that skipped validation passed.

The next unit exercises all four build configurations, an excluded tuple,
configure/build/test/workflow listing and deterministic regeneration. Compiler
labels and excluded combinations are syntactic inputs here; no compiler,
sanitizer runtime, CMake configure/build or vcpkg bootstrap is qualified.

Upstream license: [full MIT notice](../../evidence/tcpm/source/LICENSE.rst.source).

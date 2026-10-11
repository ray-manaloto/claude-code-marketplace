# Native core qualification

The public POD facade and reflection witness are unchanged. Task 03b1 adds
the fork-specific reflection guard, confines the GCC decloning workaround
and requires CTest to respect the child exit code. Its
[source review](../evidence/core-p2996-preparation/preparation-review.json)
passed; native qualification is recorded below.

Task 03b2a prepares [command acceptance rules](../dev/toolchains/core_commands.py)
against the [bounded harness contract](../evidence/core-command-preparation/harness-contract.json).
It reuses the exact qualified P2996 flag validator and checks GNU scans and
archive steps separately. Generated and executed commands must match, including
outputs, compiler identity, configuration, private reflection and library inputs.
The narrowly accepted `@rpath` install name is not a compiler response file.

The [recorded replay](../evidence/core-command-preparation/final-replay/replay.json)
passes eight prior GNU cells, four prior P2996 flag sets, four explicitly
synthetic install-name parser cases, the reviewer's synthetic CDB baseline
and 23 rejection controls, including a duplicate `-isystem` that consumed
`-Werror`. [Independent review](../evidence/core-command-preparation/command-review.json)
passed with the parser finding resolved. These checks execute no compiler
or build tool.

Task 03b2b's [native operation](../evidence/core-p2996/operation/qualification.json)
exited 0: four fresh trees cover P2996/GCC16, static/shared linkage and all four
configurations. All sixteen build/test/runtime cells, four retained ABI probes,
export/loader identities and seven controls pass. Reflection stays private;
the corrected CTest rule rejects the failing child. Protected state and default
compiler checks pass, and the shared lease is released. [Independent artifact
review](../evidence/core-p2996/core-review.json) passed without findings.

The [first attempt](../evidence/core-p2996/attempt-1/failure-review.json) remains
failed after an older GCC PATH fingerprint stopped the operation. The
[reviewed correction](../evidence/core-p2996/pre-run-review.json) uses the already
qualified shared-profile fingerprint while retaining full GCC environment
equality; the historical PATH change's cause remains unproven. This witness
exposes no research-provider behavior or dependency/package qualification.

# Native core qualification

The public POD facade and reflection witness are unchanged. Task 03b1 adds
the fork-specific reflection guard, confines the GCC decloning workaround
and requires CTest to respect the child exit code. Its
[source review](../evidence/core-p2996-preparation/preparation-review.json)
passed; the changed core still needs native qualification.

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

Task 03b2b will use four fresh private trees for P2996/GCC16 and static/shared
linkage, with all four configurations per tree. Sixteen build/test/runtime
cells, fresh ABI probes, export/loader identities and private failure controls
remain unverified. This witness exposes no research-provider behavior.

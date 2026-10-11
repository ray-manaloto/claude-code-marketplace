set(ENV{MARKETPLACE_CPP_LANE} gcc16)
include("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/dev/toolchains/p2996-bootstrap.cmake")
message(STATUS "projects=${LLVM_ENABLE_PROJECTS}; runtimes=${LLVM_ENABLE_RUNTIMES}; target=${LLVM_TARGETS_TO_BUILD}; compile=${LLVM_PARALLEL_COMPILE_JOBS}; link=${LLVM_PARALLEL_LINK_JOBS}")

# CMake generated Testfile for 
# Source directory: /Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain
# Build directory: /Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-cmake-20261011T120831Z/build
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test("reflection" "/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-cmake-20261011T120831Z/build/Debug/reflection")
  set_tests_properties("reflection" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;35;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test("reflection" "/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-cmake-20261011T120831Z/build/Release/reflection")
  set_tests_properties("reflection" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;35;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
  add_test("reflection" "/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-cmake-20261011T120831Z/build/RelWithDebInfo/reflection")
  set_tests_properties("reflection" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;35;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
  add_test("reflection" "/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-cmake-20261011T120831Z/build/MinSizeRel/reflection")
  set_tests_properties("reflection" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;35;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;0;")
else()
  add_test("reflection" NOT_AVAILABLE)
endif()

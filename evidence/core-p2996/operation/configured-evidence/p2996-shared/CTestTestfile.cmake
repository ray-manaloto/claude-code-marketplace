# CMake generated Testfile for 
# Source directory: /Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace
# Build directory: /Users/rmanaloto/.local/state/marketplace-tool-foundation/core-p2996-20261011T134510Z/p2996-shared
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test("research_core_smoke" "/Users/rmanaloto/.local/state/marketplace-tool-foundation/core-p2996-20261011T134510Z/p2996-shared/Debug/research_core_smoke")
  set_tests_properties("research_core_smoke" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/CMakeLists.txt;47;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test("research_core_smoke" "/Users/rmanaloto/.local/state/marketplace-tool-foundation/core-p2996-20261011T134510Z/p2996-shared/Release/research_core_smoke")
  set_tests_properties("research_core_smoke" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/CMakeLists.txt;47;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
  add_test("research_core_smoke" "/Users/rmanaloto/.local/state/marketplace-tool-foundation/core-p2996-20261011T134510Z/p2996-shared/RelWithDebInfo/research_core_smoke")
  set_tests_properties("research_core_smoke" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/CMakeLists.txt;47;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
  add_test("research_core_smoke" "/Users/rmanaloto/.local/state/marketplace-tool-foundation/core-p2996-20261011T134510Z/p2996-shared/MinSizeRel/research_core_smoke")
  set_tests_properties("research_core_smoke" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/CMakeLists.txt;47;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/CMakeLists.txt;0;")
else()
  add_test("research_core_smoke" NOT_AVAILABLE)
endif()

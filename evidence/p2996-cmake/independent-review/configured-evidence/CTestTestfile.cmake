# CMake generated Testfile for 
# Source directory: /Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain
# Build directory: /private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-p2996-cmake-review-x8xhd54x/build
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test("reflection" "/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-p2996-cmake-review-x8xhd54x/build/Debug/reflection")
  set_tests_properties("reflection" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;35;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test("reflection" "/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-p2996-cmake-review-x8xhd54x/build/Release/reflection")
  set_tests_properties("reflection" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;35;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
  add_test("reflection" "/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-p2996-cmake-review-x8xhd54x/build/RelWithDebInfo/reflection")
  set_tests_properties("reflection" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;35;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
  add_test("reflection" "/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-p2996-cmake-review-x8xhd54x/build/MinSizeRel/reflection")
  set_tests_properties("reflection" PROPERTIES  TIMEOUT "10" _BACKTRACE_TRIPLES "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;35;add_test;/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/scratch/p2996-toolchain/CMakeLists.txt;0;")
else()
  add_test("reflection" NOT_AVAILABLE)
endif()

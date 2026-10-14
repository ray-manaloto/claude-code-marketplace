cmake_minimum_required(VERSION 4.4)
project(AggregatedResearch VERSION 0.1.0 LANGUAGES CXX)

if(NOT CMAKE_GENERATOR STREQUAL "Ninja Multi-Config")
  message(FATAL_ERROR "Use the qualified Ninja Multi-Config development lane.")
endif()
if(NOT "$ENV{MARKETPLACE_CPP_LANE}" STREQUAL "gcc16" OR
   NOT CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR
   NOT CMAKE_CXX_COMPILER_VERSION VERSION_EQUAL "16.2.0" OR
   NOT CMAKE_TOOLCHAIN_FILE STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/gcc16-macos-arm64.cmake")
  message(FATAL_ERROR "Only the task-10b GCC16 toolchain is qualified for this skeleton.")
endif()
set(CMAKE_CONFIGURATION_TYPES Debug Release RelWithDebInfo MinSizeRel CACHE STRING "Build configurations" FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
option(BUILD_SHARED_LIBS "Build the research core as a shared library" OFF)

add_library(research_core src/core.cpp)
add_library(AggregatedResearch::core ALIAS research_core)
target_include_directories(research_core PUBLIC "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>")
target_compile_options(research_core PRIVATE -freflection -pedantic-errors -Wall -Wextra -Werror)
set_target_properties(research_core PROPERTIES POSITION_INDEPENDENT_CODE YES)

add_executable(research_core_smoke src/smoke.cpp)
target_link_libraries(research_core_smoke PRIVATE AggregatedResearch::core)
target_compile_options(research_core_smoke PRIVATE -pedantic-errors -Wall -Wextra -Werror)
set_target_properties(research_core research_core_smoke PROPERTIES
  CXX_STANDARD 26 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS NO)
# GCC 16.2 C++26 constexpr exception symbols duplicate when decloning is enabled.
# The isolated witness and reverse control are retained in evidence/core-skeleton.
foreach(_target research_core research_core_smoke)
  target_compile_options(${_target} PRIVATE "$<$<CONFIG:MinSizeRel>:-fno-declone-ctor-dtor>")
endforeach()

enable_testing()
add_test(NAME research_core_smoke COMMAND research_core_smoke)
set_tests_properties(research_core_smoke PROPERTIES
  PASS_REGULAR_EXPRESSION "reflection value=43, members=1" TIMEOUT 10)
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/core-$<CONFIG>.txt" CONTENT
"library=$<TARGET_FILE:research_core>
binary=$<TARGET_FILE:research_core_smoke>
configuration=$<CONFIG>
shared=${BUILD_SHARED_LIBS}
")

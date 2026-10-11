cmake_minimum_required(VERSION 4.4)
project(AggregatedResearch VERSION 0.1.0 LANGUAGES CXX)

if(NOT CMAKE_GENERATOR STREQUAL "Ninja Multi-Config")
  message(FATAL_ERROR "Use the qualified Ninja Multi-Config development lane.")
endif()
set(_research_core_vcpkg FALSE)
if(CMAKE_TOOLCHAIN_FILE STREQUAL "/Users/rmanaloto/.local/state/marketplace-tool-foundation/vcpkg-fmt-retry-20261011T213606Z/vcpkg/scripts/buildsystems/vcpkg.cmake" AND
   VCPKG_CHAINLOAD_TOOLCHAIN_FILE STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/vcpkg-macos-arm64.cmake")
  file(SHA256 "${CMAKE_TOOLCHAIN_FILE}" _research_core_vcpkg_sha)
  if(NOT _research_core_vcpkg_sha STREQUAL "f911a8769d07e10b26ce651f3cef6f52f2d5e598e3504d7f19e70bcbd3b3b25b")
    message(FATAL_ERROR "The qualified public vcpkg toolchain changed.")
  endif()
  set(_research_core_vcpkg TRUE)
endif()
if("$ENV{MARKETPLACE_CPP_LANE}" STREQUAL "gcc16" AND
   CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND
   CMAKE_CXX_COMPILER_VERSION VERSION_EQUAL "16.2.0" AND
   (CMAKE_TOOLCHAIN_FILE STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/gcc16-macos-arm64.cmake" OR _research_core_vcpkg))
  set(_research_core_lane "gcc16")
elseif("$ENV{MARKETPLACE_CPP_LANE}" STREQUAL "p2996" AND
       CMAKE_CXX_COMPILER_ID STREQUAL "Clang" AND
       CMAKE_CXX_COMPILER_VERSION VERSION_EQUAL "21.0.0" AND
       (CMAKE_TOOLCHAIN_FILE STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/p2996-macos-arm64.cmake" OR _research_core_vcpkg))
  set(_research_core_lane "p2996")
else()
  message(FATAL_ERROR "Use the qualified GCC16 or P2996 toolchain for this skeleton.")
endif()
set(CMAKE_CONFIGURATION_TYPES Debug Release RelWithDebInfo MinSizeRel CACHE STRING "Build configurations" FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
option(BUILD_SHARED_LIBS "Build the research core as a shared library" OFF)
option(RESEARCH_CORE_WITH_FMT "Qualify the compiled fmt dependency in the smoke consumer" OFF)
if(RESEARCH_CORE_WITH_FMT)
  if(NOT _research_core_vcpkg)
    message(FATAL_ERROR "The fmt baseline requires the qualified public vcpkg composition.")
  endif()
  find_package(fmt 12.2.0 EXACT CONFIG REQUIRED)
  if(NOT fmt_DIR STREQUAL "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/share/fmt")
    message(FATAL_ERROR "fmt must come from the selected retained installation.")
  endif()
endif()

add_library(research_core src/core.cpp)
add_library(AggregatedResearch::core ALIAS research_core)
target_include_directories(research_core PUBLIC "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>")
target_compile_options(research_core PRIVATE -freflection -pedantic-errors -Wall -Wextra -Werror)
set_target_properties(research_core PROPERTIES POSITION_INDEPENDENT_CODE YES)

add_executable(research_core_smoke src/smoke.cpp)
target_link_libraries(research_core_smoke PRIVATE AggregatedResearch::core)
if(RESEARCH_CORE_WITH_FMT)
  # Exercise a transitive compiled dependency for the baseline and package fixtures.
  target_link_libraries(research_core PUBLIC fmt::fmt)
  target_compile_definitions(research_core_smoke PRIVATE RESEARCH_CORE_WITH_FMT=1)
endif()
target_compile_options(research_core_smoke PRIVATE -pedantic-errors -Wall -Wextra -Werror)
set_target_properties(research_core research_core_smoke PROPERTIES
  CXX_STANDARD 26 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS NO)
if(_research_core_lane STREQUAL "p2996")
  set_target_properties(research_core research_core_smoke PROPERTIES CXX_SCAN_FOR_MODULES OFF)
endif()
# GCC 16.2 C++26 constexpr exception symbols duplicate when decloning is enabled.
# The isolated witness and reverse control are retained in evidence/core-skeleton.
if(_research_core_lane STREQUAL "gcc16")
  foreach(_target research_core research_core_smoke)
    target_compile_options(${_target} PRIVATE "$<$<CONFIG:MinSizeRel>:-fno-declone-ctor-dtor>")
  endforeach()
endif()

enable_testing()
add_test(NAME research_core_smoke COMMAND research_core_smoke)
set_tests_properties(research_core_smoke PROPERTIES TIMEOUT 10)
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/core-$<CONFIG>.txt" CONTENT
"library=$<TARGET_FILE:research_core>
binary=$<TARGET_FILE:research_core_smoke>
configuration=$<CONFIG>
shared=${BUILD_SHARED_LIBS}
")

cmake_minimum_required(VERSION 4.4)
cmake_host_system_information(RESULT CMAKE_HOST_SYSTEM_PROCESSOR QUERY OS_PLATFORM)
macro(vcpkg_triplet_file VCPKG_TRIPLET_ID)
set(_backup "${CMAKE_CURRENT_LIST_FILE}")
set(CMAKE_CURRENT_LIST_FILE "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/triplets/arm64-osx-p2996-static.cmake")
get_filename_component(CMAKE_CURRENT_LIST_DIR "${CMAKE_CURRENT_LIST_FILE}" DIRECTORY)
set(_marketplace_triplet_lane p2996)
set(VCPKG_LIBRARY_LINKAGE static)
include("${CMAKE_CURRENT_LIST_DIR}/common/macos-arm64.cmake")
set(CMAKE_CURRENT_LIST_FILE "${_backup}")
get_filename_component(CMAKE_CURRENT_LIST_DIR "${CMAKE_CURRENT_LIST_FILE}" DIRECTORY)
endmacro()
vcpkg_triplet_file(0)

if(NOT VCPKG_TARGET_ARCHITECTURE STREQUAL "arm64" OR
   NOT VCPKG_LIBRARY_LINKAGE STREQUAL "static" OR
   NOT VCPKG_CRT_LINKAGE STREQUAL "dynamic" OR
   NOT VCPKG_CMAKE_SYSTEM_NAME STREQUAL "Darwin" OR DEFINED VCPKG_BUILD_TYPE OR
   NOT VCPKG_OSX_DEPLOYMENT_TARGET STREQUAL "27.0" OR
   NOT VCPKG_OSX_SYSROOT STREQUAL "/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk" OR
   NOT VCPKG_CMAKE_CONFIGURE_OPTIONS STREQUAL "-DCMAKE_POLICY_DEFAULT_CMP0210=NEW" OR
   NOT VCPKG_ENV_PASSTHROUGH STREQUAL "MARKETPLACE_CPP_LANE;MARKETPLACE_P2996_PREFIX")
 message(FATAL_ERROR "Triplet contract mismatch")
endif()
list(LENGTH VCPKG_HASH_ADDITIONAL_FILES count)
if(NOT count EQUAL 13 OR NOT "/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/triplets/common/macos-arm64.cmake" IN_LIST VCPKG_HASH_ADDITIONAL_FILES)
 message(FATAL_ERROR "Missing nested ABI inputs")
endif()
foreach(input IN LISTS VCPKG_HASH_ADDITIONAL_FILES)
 file(SHA256 "${input}" digest)
 message(STATUS "ABI=${input}|${digest}")
endforeach()
set(before "${VCPKG_HASH_ADDITIONAL_FILES}")
include("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/triplets/arm64-osx-p2996-static.cmake")
if(NOT before STREQUAL VCPKG_HASH_ADDITIONAL_FILES)
 message(FATAL_ERROR "Reentry changed ABI inputs")
endif()
message(STATUS "TRIPLET_PASS")

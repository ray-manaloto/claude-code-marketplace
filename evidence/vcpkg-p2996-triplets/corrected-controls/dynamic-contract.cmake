cmake_minimum_required(VERSION 3.5)
include("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/triplets/arm64-osx-p2996-dynamic.cmake")

if(NOT VCPKG_TARGET_ARCHITECTURE STREQUAL "arm64" OR
   NOT VCPKG_LIBRARY_LINKAGE STREQUAL "dynamic" OR
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
include("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/triplets/arm64-osx-p2996-dynamic.cmake")
if(NOT before STREQUAL VCPKG_HASH_ADDITIONAL_FILES)
 message(FATAL_ERROR "Reentry changed ABI inputs")
endif()
message(STATUS "TRIPLET_PASS")

# Shared inputs for the qualified, uninstrumented macOS ARM64 triplets.
if(CMAKE_VERSION VERSION_LESS "4.4" OR
   NOT CMAKE_HOST_SYSTEM_NAME STREQUAL "Darwin" OR
   NOT CMAKE_HOST_SYSTEM_PROCESSOR STREQUAL "arm64")
  message(FATAL_ERROR "Use CMake 4.4+ on native macOS ARM64.")
endif()
set(_marketplace_foundation "/Users/rmanaloto/.local/state/marketplace-tool-foundation")
if(_marketplace_triplet_lane STREQUAL "p2996")
  set(_marketplace_triplet_prefix "${_marketplace_foundation}/p2996-configure-20261011T051205Z/prefix")
  set(_marketplace_triplet_environment MARKETPLACE_P2996_PREFIX)
  set(_marketplace_triplet_other MARKETPLACE_GCC16_PREFIX)
  set(_marketplace_triplet_inputs bin/clang bin/clang++ include/c++/v1/meta
      lib/clang/21/include/stddef.h lib/libc++.dylib lib/libc++abi.dylib lib/libunwind.dylib)
elseif(_marketplace_triplet_lane STREQUAL "gcc16")
  set(_marketplace_triplet_prefix "/opt/homebrew/Cellar/gcc/16.2.0")
  set(_marketplace_triplet_environment MARKETPLACE_GCC16_PREFIX)
  set(_marketplace_triplet_other MARKETPLACE_P2996_PREFIX)
  set(_marketplace_triplet_inputs bin/gcc-16 bin/g++-16
      libexec/gcc/aarch64-apple-darwin25/16/cc1
      libexec/gcc/aarch64-apple-darwin25/16/cc1plus
      lib/gcc/current/libstdc++.6.dylib lib/gcc/current/libgcc_s.1.1.dylib)
else()
  message(FATAL_ERROR "The triplet must select a qualified compiler lane.")
endif()
if(NOT "$ENV{MARKETPLACE_CPP_LANE}" STREQUAL _marketplace_triplet_lane OR
   NOT "$ENV{${_marketplace_triplet_environment}}" STREQUAL _marketplace_triplet_prefix OR
   NOT "$ENV{${_marketplace_triplet_other}}" STREQUAL "")
  message(FATAL_ERROR "The triplet lane and qualified environment must agree.")
endif()
if(NOT VCPKG_LIBRARY_LINKAGE MATCHES "^(static|dynamic)$" OR
   (DEFINED VCPKG_BUILD_TYPE AND NOT VCPKG_BUILD_TYPE STREQUAL "") OR
   VCPKG_DISABLE_COMPILER_TRACKING)
  message(FATAL_ERROR "Select static/dynamic linkage, both build types and compiler tracking.")
endif()
get_filename_component(_marketplace_project "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(VCPKG_TARGET_ARCHITECTURE arm64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_CMAKE_SYSTEM_NAME Darwin)
set(VCPKG_OSX_SYSROOT "/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk")
set(VCPKG_OSX_DEPLOYMENT_TARGET "27.0")
set(VCPKG_CHAINLOAD_TOOLCHAIN_FILE "${_marketplace_project}/cmake/toolchains/vcpkg-macos-arm64.cmake")
set(VCPKG_CMAKE_CONFIGURE_OPTIONS "-DCMAKE_POLICY_DEFAULT_CMP0210=NEW")
set(VCPKG_ENV_PASSTHROUGH MARKETPLACE_CPP_LANE "${_marketplace_triplet_environment}")
# vcpkg hashes the top-level triplet/chainloader, but not their nested includes.
# Forced system tools report internal version 0; bind their actual bytes as well.
set(VCPKG_HASH_ADDITIONAL_FILES
    "${CMAKE_CURRENT_LIST_FILE}"
    "${_marketplace_project}/cmake/toolchains/${_marketplace_triplet_lane}-macos-arm64.cmake"
    "${_marketplace_foundation}/vcpkg-source-e4563094/source/scripts/toolchains/osx.cmake"
    "${VCPKG_OSX_SYSROOT}/SDKSettings.json"
    "/Users/rmanaloto/.local/share/mise/installs/cmake/4.4.4/cmake-4.4.4-macos-universal/CMake.app/Contents/bin/cmake"
    "/Users/rmanaloto/.local/share/mise/installs/ninja/1.13.2/ninja")
foreach(_marketplace_input IN LISTS _marketplace_triplet_inputs)
  list(APPEND VCPKG_HASH_ADDITIONAL_FILES "${_marketplace_triplet_prefix}/${_marketplace_input}")
endforeach()
foreach(_marketplace_input IN LISTS VCPKG_HASH_ADDITIONAL_FILES)
  if(NOT IS_ABSOLUTE "${_marketplace_input}" OR
     NOT EXISTS "${_marketplace_input}" OR IS_DIRECTORY "${_marketplace_input}")
    message(FATAL_ERROR "Missing qualified ABI input: ${_marketplace_input}")
  endif()
endforeach()

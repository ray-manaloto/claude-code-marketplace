cmake_minimum_required(VERSION 4.4)
if(NOT CMAKE_GENERATOR STREQUAL "Ninja Multi-Config")
  message(FATAL_ERROR "This fixture requires Ninja Multi-Config.")
endif()
set(CMAKE_CONFIGURATION_TYPES "Debug;Release;RelWithDebInfo;MinSizeRel" CACHE STRING "Fixture configurations")
if(NOT CMAKE_CONFIGURATION_TYPES STREQUAL "Debug;Release;RelWithDebInfo;MinSizeRel")
  message(FATAL_ERROR "Use all four admitted configurations in a fresh build directory.")
endif()
project(MarketplaceP2996Fixture LANGUAGES C CXX)
foreach(_language C CXX)
  if(NOT CMAKE_${_language}_COMPILER_ID STREQUAL "Clang" OR
     NOT CMAKE_${_language}_COMPILER_VERSION VERSION_EQUAL "21.0.0")
    message(FATAL_ERROR "Use the exact P2996 fork qualified in task 07d.")
  endif()
endforeach()
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
try_compile(_private_runtime_links SOURCE_FROM_CONTENT private_runtime.cpp [=[
#if __has_feature(reflection)
#error "Reflection must remain target-private"
#endif
#include <string>
int main() { return std::string("private").size() != 7; }
]=] CMAKE_FLAGS "-DCMAKE_CXX_SCAN_FOR_MODULES=OFF"
    CXX_STANDARD 26 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS NO
    NO_CACHE OUTPUT_VARIABLE _private_runtime_log)
file(WRITE "${CMAKE_BINARY_DIR}/private-runtime-try-compile.log" "${_private_runtime_log}")
if(NOT _private_runtime_links)
  message(FATAL_ERROR "Private C++ runtime try_compile failed; inspect the retained log.")
endif()
add_executable(reflection "../../dev/toolchains/p2996_reflection.cpp")
set_target_properties(reflection PROPERTIES CXX_STANDARD 26 CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO CXX_SCAN_FOR_MODULES OFF)
target_compile_options(reflection PRIVATE -freflection)
enable_testing()
add_test(NAME reflection COMMAND reflection)
set_tests_properties(reflection PROPERTIES TIMEOUT 10)
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/qualified-$<CONFIG>.txt" CONTENT
"compiler=${CMAKE_CXX_COMPILER}
version=${CMAKE_CXX_COMPILER_VERSION}
sdk=${CMAKE_OSX_SYSROOT}
architecture=${CMAKE_OSX_ARCHITECTURES}
configuration=$<CONFIG>
binary=$<TARGET_FILE:reflection>
")

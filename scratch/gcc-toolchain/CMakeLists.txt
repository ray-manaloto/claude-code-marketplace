cmake_minimum_required(VERSION 4.4)
project(MarketplaceGccFixture LANGUAGES C CXX)
if(NOT CMAKE_GENERATOR STREQUAL "Ninja Multi-Config")
  message(FATAL_ERROR "This fixture requires Ninja Multi-Config.")
endif()
if(NOT CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR
   NOT CMAKE_CXX_COMPILER_VERSION VERSION_EQUAL "16.2.0")
  message(FATAL_ERROR "Use the GCC 16.2.0 installation qualified in task 05.")
endif()
set(CMAKE_CONFIGURATION_TYPES Debug Release RelWithDebInfo MinSizeRel CACHE STRING "Fixture configurations" FORCE)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_executable(reflection "../../dev/toolchains/reflection.cpp")
set_target_properties(reflection PROPERTIES CXX_STANDARD 26 CXX_STANDARD_REQUIRED YES CXX_EXTENSIONS NO)
target_compile_options(reflection PRIVATE -freflection -pedantic-errors -Wall -Wextra -Werror)
enable_testing()
add_test(NAME reflection COMMAND reflection)
set_tests_properties(reflection PROPERTIES PASS_REGULAR_EXPRESSION "reflection value=43" TIMEOUT 10)
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/qualified-$<CONFIG>.txt" CONTENT
"compiler=${CMAKE_CXX_COMPILER}
version=${CMAKE_CXX_COMPILER_VERSION}
sdk=${CMAKE_OSX_SYSROOT}
architecture=${CMAKE_OSX_ARCHITECTURES}
configuration=$<CONFIG>
binary=$<TARGET_FILE:reflection>
")

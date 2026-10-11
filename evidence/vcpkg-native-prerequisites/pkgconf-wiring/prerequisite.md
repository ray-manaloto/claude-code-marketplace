Source prerequisite only, at project HEAD 318c671f5c6a781b29af399d7f6005fe8a917bb5. No installation or native execution occurred. The current file is triplets/common/macos-arm64.cmake; triplets/common/macos.cmake is absent. The existing common triplet SHA256 is ecb22f08caac61ef5008a68562753252fbb21404610525a789a0a9f8a7d42fcb.

The pinned selector reads environment variable PKG_CONFIG, stores its value in the internal CMake variable PKGCONFIG, and returns (selector:19-24). The generic function first returns immediately when PKGCONFIG is truthy, before consulting that environment variable (acquisition:120-144). fmt calls vcpkg_fixup_pkgconfig without SKIP_CHECK (fmt_call:25-27); its required validation runs COMMAND "${PKGCONFIG}" --print-errors --exists <package-name> for Release and Debug (invocation:115-142,186-198). Therefore use PKG_CONFIG=/opt/homebrew/bin/pkg-config in the runner and append the NAME PKG_CONFIG to VCPKG_ENV_PASSTHROUGH. PKGCONFIG is the CMake result/cache variable, not the environment name to track. This route does not select from PKG_CONFIG_EXECUTABLE.

Given the parent-supplied frozen candidate paths, append precisely these package files to VCPKG_HASH_ADDITIONAL_FILES after installation is independently qualified:

- /opt/homebrew/Cellar/pkgconf/3.0.8/bin/pkgconf
- /opt/homebrew/Cellar/pkgconf/3.0.8/lib/libpkgconf.8.dylib

The public pkg-config symlink needs a destination guard, not a duplicate content-hash entry: file-content hashing does not bind the symlink text. Record its resolved destination in the later installation/native receipt. Hash the library contents reached through libpkgconf.8.dylib and retain its resolved file identity too. Do not add /usr/lib/libSystem.B.dylib to this package-file list; it is the supplied system runtime dependency and remains covered by the separately qualified platform boundary. No installed path or binary hash was independently verified here.

The minimum common-triplet proposal below belongs after the existing passthrough/additional-file lists are initialized and before their existing validation loop. It preserves current list entries. It intentionally accepts only an unset or exactly matching PKGCONFIG value/cache; it does not silently clear or override a conflicting cached selection. This is a source sketch, not an applied or CMake-tested patch.

```cmake
set(_marketplace_pkg_config "/opt/homebrew/bin/pkg-config")
set(_marketplace_pkgconf_binary "/opt/homebrew/Cellar/pkgconf/3.0.8/bin/pkgconf")
if(NOT "$ENV{PKG_CONFIG}" STREQUAL "${_marketplace_pkg_config}" OR
   (DEFINED PKGCONFIG AND NOT "${PKGCONFIG}" STREQUAL "${_marketplace_pkg_config}") OR
   (DEFINED CACHE{PKGCONFIG} AND NOT "$CACHE{PKGCONFIG}" STREQUAL "${_marketplace_pkg_config}") OR
   NOT EXISTS "${_marketplace_pkg_config}" OR IS_DIRECTORY "${_marketplace_pkg_config}")
  message(FATAL_ERROR "Use the qualified pkgconf entry through PKG_CONFIG in a fresh process.")
endif()
file(REAL_PATH "${_marketplace_pkg_config}" _marketplace_pkgconf_selected)
if(NOT _marketplace_pkgconf_selected STREQUAL _marketplace_pkgconf_binary)
  message(FATAL_ERROR "The pkg-config entry must resolve to qualified pkgconf 3.0.8.")
endif()
list(APPEND VCPKG_ENV_PASSTHROUGH PKG_CONFIG)
list(APPEND VCPKG_HASH_ADDITIONAL_FILES
    "${_marketplace_pkgconf_binary}"
    "/opt/homebrew/Cellar/pkgconf/3.0.8/lib/libpkgconf.8.dylib")
```

For the controlled runner, retain the already-agreed lane/compiler environment and set only the pkgconf selector above. Use a fresh port-script process/cache; do not pass competing -DPKGCONFIG values or rely on an inherited PKGCONFIG CMake value. Start with PKG_CONFIG_PATH unset and exclude unrelated pkg-config lookup overrides from the inherited environment. The setup helper backs up PKG_CONFIG and PKG_CONFIG_PATH, assigns PKG_CONFIG=${PKGCONFIG}, prepends the current package and installed directories for the selected configuration, and later restores those two variables (search_paths:11-43,46-58). It otherwise preserves external PKG_CONFIG_PATH entries. This source guide does not claim that unsetting that variable eliminates pkgconf built-in search defaults; later private-package lookup and confinement witnesses remain required. No HOME, profile, PATH or compiler-selection redesign is proposed.

ABI verification after the later native install must find ENV:PKG_CONFIG equal to the SHA256 of the selected non-secret path string, and additional_file_N entries equal to the two actual file-content SHA256 values. Source abi:1354-1366 hashes tracked environment values; abi:1444-1454 requires absolute regular-file inputs and hashes their contents; abi:2234-2249 reads the tracked names and additional-file list. Preserve existing lane/prefix ABI entries. Actual PKGCONFIG selection, executable version/load dependencies, both fmt --exists results and these ABI entries remain UNVERIFIED until the admitted native run.

Exact source paths, SHA256 values and line ranges for common_triplet, selector, acquisition, invocation, search_paths, abi, tag_variables and fmt_call are in source-manifest.json. Source manifest SHA256: 168e10d3e9b60bab179dd69d45c98b0e415012aee60335b4cdbd6f8f1591b04c. The new bounded search_paths read is identified by its observed hash at the retained source HEAD; no Git tree/status audit was performed.

Only these two review artifacts are allowed and created:

- /Users/rmanaloto/.local/state/marketplace-tool-foundation/task12-pkgconf-wiring-Q27xVx/prerequisite.md
- /Users/rmanaloto/.local/state/marketplace-tool-foundation/task12-pkgconf-wiring-Q27xVx/source-manifest.json

No maintained files, installed candidate files, environment/credential values or native tools were modified, read or executed beyond the source/receipt paths recorded in the manifest. No new research, fetch, network request, lease or broad inventory ran.

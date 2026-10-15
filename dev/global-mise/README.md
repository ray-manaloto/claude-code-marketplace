# Global mise foundation — tasks 04a/04b

The seven configuration/lock files were applied after scoped ownership admission,
private preimages and independent proposal review. This directory retains the
exact applied bytes; preparation comments describe their earlier proposal state.
The parent owns this project copy and the seven new global destinations.
Never run a blanket global install or host chezmoi apply.

The [application receipt](../../evidence/tool-foundation/global-application.json)
records exclusive creation, an unchanged normal environment and the successful
26.9-second native installation. The [host qualification](../../evidence/tool-foundation/host-qualification.json)
records exact binary paths/hashes, ARM64 support, all three versions, selected
environment controls and native CMake preset listing. Independent
[application review](../../evidence/tool-foundation/application-review.json)
passed. Compiler execution and sccache caching remain unqualified.

## Destination and scope

The four TOMLs and three generated `mise.<environment>.lock` files now exist at
their relative paths under `~/.config/mise/`, with mode 0600. Do not overwrite
an existing destination by repeating this installation. The existing
`config.toml`, `mise.lock`, hooks, trust, Python pins, other tools and default
compiler configuration are outside this patch.

| Environment | Purpose |
| --- | --- |
| `cpp-build` | CMake 4.4.4, Ninja 1.13.2 and sccache 0.18.0 for the TCPM trial; no compiler selected |
| `p2996` | Same build tools; explicit Clang executables from a subsequently qualified managed prefix |
| `gcc16` | Same build tools; explicit GCC16 executables from a subsequently qualified managed prefix |

Each named file includes `cpp-foundation/common.toml`. Local includes are
supported by the installed mise 2026.10.7 schema; this supersedes the older
skill's remote-only include description. The isolated native fixture verifies
include precedence, environment removal and compiler-prefix rejection.
Paranoid mise configurations reject local includes and require a new proposal.

The common fragment removes inherited compiler, linker, library-search, SDK and
launcher variables only while one of these environments is selected. Caller
parallelism limits remain intact. The normal environment retains its existing
Homebrew LLVM settings. Its `/opt/homebrew/opt/llvm/bin` PATH entry remains in
named environments too; ancillary tools found there are not qualified by this
patch. The explicit CC/CXX paths select the intended compiler executables.
The repository's OCI and plugin mise files are untouched.

## Compiler qualification boundary

No compiler installation is provided by this patch. `p2996` requires
`MARKETPLACE_P2996_PREFIX`; `gcc16` requires `MARKETPLACE_GCC16_PREFIX`.
The prefix must come from the later managed-install qualification receipt,
not an arbitrary system compiler. These parameters only select executables;
they cannot prove compiler/reflection, standard-library, SDK or vcpkg parity.
Tasks 05/07 and 10a/10b retain those gates. Template guards reject absent, empty,
whitespace-only, padded, relative and root-only prefixes before command execution.
Empty, dot and parent path components and trailing slashes are also rejected.
Filesystem/symlink identity still belongs to the later managed-install gate.
Native `required` alone accepts empty strings; the guards use Tera v2's named
`starting_with(pat=...)` argument. No fallback compiler is configured.

The [native checks](../../evidence/tool-foundation/profile-validation.json)
passed eight positive controls and twenty-seven expected rejections. DYLD variables
were absent even in the default control, so this execution boundary cannot
attribute their removal to the fragment. No compiler ran. Fixture discovery
uses `MISE_CONFIG_DIR` without `MISE_GLOBAL_CONFIG_FILE`, which suppresses named
profiles. Raw global config/lock copies and test runners remain private.

For example, after those later gates, select the intended environment with
`mise -E p2996 exec -- <command>` or `mise -E gcc16 exec -- <command>` from a
directory whose project configuration is known. Do not invoke either through
the repository's root OCI config. `dev/mise` intentionally isolates static
development checks and does not load these global environments.

## Recorded admission and installation sequence

1. Reconcile the active global mise writer and shared host capacity. Active
   dotfiles host/shared-lock migration is separate work; a process snapshot or
   unchanged file hash alone does not establish exclusive ownership.
2. Recheck the [private-preimage manifest](../../evidence/tool-foundation/preimages.json),
   current hashes/modes, and absence of all seven proposed destination files.
   Abort on drift or an existing destination; preserve other owners' work.
3. Verify the isolated native checks and independent review, then record the
   exact admitted file/tool allowlist before copying any file.
4. Install only `cmake@4.4.4 ninja@1.13.2 sccache@0.18.0` using native mise,
   `-E cpp-build --locked`, one job, and no hooks or dependency preparation.
   The [native lock receipts](../../evidence/tool-foundation/native-lock-validation.json)
   prove separate named locks containing only these three macOS ARM64 entries.
   Preserve default global/project locks and every existing tool installation.
5. Verify binary paths, architectures, versions and native preset listing.
   A version probe alone does not qualify sccache behavior or any compiler.
6. Compare a fresh normal environment to its preimage, then recheck selected
   named environments with polluted compiler variables. Preserve actual exits.

Native mise installed CMake 4.4.4 and sccache 0.18.0 and reused Ninja 1.13.2
without changing its binary. All three resolve inside their exact managed
installation directories and support ARM64. The older CMake 4.4.3/4.4.2 and
GitHub-backend sccache 0.14.0 installations remain separate. Primary
[release receipts](../../evidence/tool-foundation/release-verification.json)
confirm the accepted tags and macOS assets; installed binary identities are
recorded separately in the host qualification receipt.

The global base config and lock have exact private backups (0600 files in a
0700 directory); only their hashes/paths are in project evidence. Strict-five
research remains incomplete. This phase verifies already accepted identities
and native configuration contracts without repeating exhausted provider routes.

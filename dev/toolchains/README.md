# Compiler preparation

Task 05a prepares GCC installation; it does not install or qualify a compiler.
The parent remains the sole writer. P2996 source/configure work is a later unit.

## Native GCC bootstrap contract

The [source receipts](../../evidence/gcc-bootstrap/source-acquisition.json) bind
mise 2026.10.7 to `4599c53b4286ff101de876f8122feec0797b48b2` and verify selected
source files against its complete Git tree. The captured Homebrew API identifies
GCC 16.2.0, formula revision 0, bottle rebuild 1. Formula source matches the API
checksum at Homebrew commit `3c09418e50ad51f7f241f4062ffcd7bffe36e3ce`.

`mise bootstrap packages apply brew:gcc` uses the canonical Homebrew prefix,
`/opt/homebrew`, without invoking brew. A named mise environment controls selection;
it does not isolate package writes. The native [dry run](../../evidence/gcc-bootstrap/native-dry-run.json)
plans only four missing bottles: isl 0.28, mpfr 4.2.2, libmpc 1.4.1 and GCC 16.2.0.
The closure also contains already installed gmp, lz4, xz and zstd. No source build
appears in that plan. Observed package receipts/links and nine global mise files
remained unchanged.

This mise release knows Tahoe and older macOS bottle tags. On the observed macOS
27.0.1 host it selects `arm64_tahoe`, although Homebrew also publishes a Golden
Gate bottle. GCC's selected SHA-256 is
`add0ca0614da1d0047af8a71be683be40957096851f4c98ccd89e95b0c4f4fde`.
Its fixed cellar is `/opt/homebrew/Cellar`; installed Command Line Tools supply
the SDK path. Neither metadata nor a dry run proves runtime compatibility.

Explicit version pins are unsupported: declaring `"brew:gcc" = "16.2.0"`
prints a skip warning and returns zero without a pour. `latest` accepts an
already installed package, so that status also cannot prove currency.

## Captured metadata qualification

`gcc_snapshot_plan.py` uses native `settings.url_replacements` to serve only the
eight hash-verified public formula snapshots over a temporary loopback endpoint.
Native mise still resolves dependencies and produces its dry run. All eight
metadata requests must reach those snapshots; the resulting plan must match the
recorded live plan. A missing GCC snapshot must fail with no planned pour/build.
The endpoint is stopped in all normal success/error exits; no service is registered.

Run before installation, with the current observed package state:

```sh
uv run --no-project --offline --python <existing-python> --no-python-downloads \
  python dev/toolchains/gcc_snapshot_plan.py \
  --mise <absolute-native-mise> --run-dir <new-private-directory>
```

The [snapshot receipt](../../evidence/gcc-bootstrap/snapshot-plan.json) proves the
native plan can use captured metadata and rejects a missing input. It does not
fetch, relocate or install bottles. Native JSON caching is only per process;
copying a cache directory is not a metadata lock. This script has no install mode.
Independent review verified all 32 acquisition records and 20 mise source blobs,
then reproduced both native cases and confirmed the listener was closed. The
[review receipt](../../evidence/gcc-bootstrap/preparation-review.json) records the
exact reviewed inputs and remaining installation boundary.

## Bottle and prefix inspection

`gcc_bottles.py` downloads the four captured `arm64_tahoe` archives into a new
private directory, verifies every SHA-256 and inspects tar members without
extracting or executing them. `--archives-from <cache/system-brew/bottles>`
repeats inspection offline. The [manifest](../../evidence/gcc-bootstrap/bottles.json)
enumerates archive contents, 1,791 public links, 106 parent preimages and 25
native control paths, including bootstrap directories and installation locks.
Every public leaf is absent. The four formula racks are absent too.

ISL's debugger helper requires native mise to expand `share/gdb` and its
`auto-load` child into real directories. The existing GLib `opt` subtree remains
reachable through a preserved symlink. Both staging paths are absent; private
preimages retain the original link and both GLib files. Native rollback does
not undo these directory conversions or already completed dependency installs.
A failed batch therefore requires inspection of its actual partial state.

A preparation check stopped when another operation changed global mise config
and lock bytes. The semantic diff contains only four unrelated tool versions;
compiler/environment settings and all seven named files are unchanged. Fresh
private preimages preserve these updates. The current normal PATH has a new
digest, so installation must compare against that fresh baseline. The external
writer was not attributed; the proposed installer uses private configuration
and has no global config/lock write scope.

## Installation admission still required

Before installation, recheck concurrent package writers and the four absent kegs,
retain current receipts/links and normal compiler environment, inspect the
complete proposed prefix writes and verify bottle hashes. Use one native mise
installer job with captured metadata, no source fallback and no existing-package
upgrade. Preserve the ordinary LLVM selection. Then verify installed compiler,
libstdc++, SDK, dynamic dependencies and reflection compile/link/run before setting
`MARKETPLACE_GCC16_PREFIX` from the qualified receipt. Cold LLVM and OCI operations
still require a fresh shared-capacity admission.

Routes run: native fnox research profile, uv/existing Python, GitHub API/raw,
Homebrew API, native mise inspection/dry runs and read-only Codex workers.
Exa, Firecrawl, Last30Days and Context7 were not rerun; inherited research gaps
remain. Initial filename and version-command mistakes are retained in evidence.

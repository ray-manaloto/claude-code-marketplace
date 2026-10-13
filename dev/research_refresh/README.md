# Reusable GitHub research refresh

This optional development workflow shares the accepted RF1/RF2 runner and offline
controls. It does not replace the marketplace's native C++ research-core direction
or install a runtime. Source provenance is recorded in
[portable-provenance.json](../../docs/research-feedback-retro/portable-provenance.json).

## Run the offline checks

From the repository root, using installed Python 3.11+ on macOS or Linux:

```sh
python3 -B -m unittest discover -s dev/research_refresh -p 'test_*.py' -v
./dev/mise tasks validate
./dev/mise run check
./dev/mise run check:acceptance-baseline
```

The normal check and existing development CI run both shared research helper tests
and the complete refresh suite. Discovery includes every runtime test module.
Record actual exits and discovered counts. Tests use synthetic runtimes and
temporary directories; they do not load credentials or query providers.

## Prepare an explicitly selected local workflow

Choose an existing private state directory outside every Git checkout and outside
the borrowed runtime. Copy the reviewed [policy](examples/policy.json) and
[catalog](examples/searches.json) definitions there as `policy.json` and
`searches.json`. They are starting examples, not a requirement to reuse another
session's query history. Preserve existing state when adopting this source into an
already admitted workflow; do not initialize over it.

Copy [runtime.example.json](examples/runtime.example.json) to a local file outside
Git. Replace every placeholder with an absolute existing path. The file names the
borrowed project, uv/fnox/mise executables, private fnox configuration and existing
runtime-admission receipt. Keep credential values in fnox, never in this JSON.
No tool path is discovered automatically and no runtime is installed or repaired.
The selected uv path must end in `uv`, because the admitted native tasks invoke
that name through PATH; its directory must not contain a PATH separator.
Explicit runtime/tool symlink paths retain their spelling
for admission; containment checks still resolve symlinks.

The accepted runtime contract remains GitHubKit 0.16.1, uv 0.13.0, mise 2026.10.8
and fnox 1.39.0. Select those already admitted tools. The retained admission must
bind the selected borrowed project's installed help and task definitions; copying
another machine's receipt does not qualify a new environment. The borrowed project
must expose the accepted `github-search` and `github:diff` tasks and its `.venv`.
Missing or mismatched admission stops before credential/provider launch. The
example JSON is a path template, not an admission generator or proof of versions.

Run only after that local workflow and its existing runtime are admitted:

```sh
python3 -B /path/to/checkout/dev/research_refresh/refresh.py \
  --state-dir /path/to/private/research-state \
  --runtime-config /path/to/private/runtime.json
```

The same flags accept `--proposal proposals/NAME/proposal.json`, relative to the
selected state directory. Missing/invalid configuration exits 2 before locking,
writing or launch. The borrowed runtime stays read-only; the fixed fnox profile
and native mise flags preserve the existing no-sync/no-install route. See the
[operating guide](../../docs/research-feedback-retro/portable-workflow.md) for
coverage, proposal, research and reporting rules.

## State and delivery boundaries

Private state contains results, cycles, comparison baselines, event ledgers,
cooldowns, local admission and raw diagnostics. Keep it outside Git and share only
the reviewed portable code, definitions and sanitized outcome contracts. A failed
attempt is evidence; it is not an accepted comparison baseline. Fetching this
branch neither activates a schedule nor qualifies a provider or borrowed runtime.

After fetching the published `codex/research-feedback-retro` branch, another
session may rebase its own work onto that remote branch, resolve its own conflicts
and rerun these checks. In particular, reconcile changes to the shared development
check rather than dropping either suite. This publication does not rebase or alter
another session's checkout.

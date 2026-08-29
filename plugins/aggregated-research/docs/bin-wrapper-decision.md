# `bin/` wrapper vs mise generators — decision record

Spike for issue #573 objective B. Not a code change: `bin/`, `hooks/`, and
`.lsp.json` under this plugin are untouched by this PR. This is the evidence
issue #587 ("Package the CLI: its own package, pinned per project") acts on.

## The question

`bin/{aggregated-research,mise-env,ty}` are hand-written shell wrappers whose
job is CONFINEMENT: keep this plugin's mise-managed tools from touching the
user's global mise config or another plugin's data directory. `mise` ships two
generators that build similar-looking wrappers for free. Does either replace
the hand-written confinement in `bin/mise-env`?

## What `bin/mise-env` actually does (baseline)

Reads `$CLAUDE_PLUGIN_DATA`, validates it names *this* plugin's own data
directory (guards against a foreign plugin's value — the comment in the file
documents an *observed* 2026-08-28 case of `CLAUDE_PLUGIN_DATA` leaking
another plugin's value into a Bash tool invocation), then exports six vars
scoped to that directory: `MISE_CEILING_PATHS`, `MISE_GLOBAL_CONFIG_FILE`,
`MISE_SYSTEM_CONFIG_FILE`, `MISE_TRUSTED_CONFIG_PATHS`, `MISE_DATA_DIR`,
`UV_CACHE_DIR`.

## Candidate A: `mise generate install-script` + `mise generate task-stubs`

Built in `/tmp/proto-a` (scratch copy of this plugin, not committed). Command
shape, per the installed mise's own `--help` (re-read this session):

```
mise generate install-script --write ./bin/mise --localize
mise generate task-stubs --dir ./bin --mise-bin ./bin/mise
```

`task-stubs` wraps mise **tasks**, not the plugin's `mise exec` pattern
(`bin/aggregated-research` does `mise-env exec -- aggregated-research "$@"`).
For a stub to exist at all, the scratch `mise.toml` needed a `[tasks.run]`
entry added first (`run = "exec aggregated-research \"$@\""`) — candidate A
does not avoid this cost, it adds it.

**Measured:**

- `--localize` sets `MISE_DATA_DIR="$project_dir/.mise"` — a path relative to
  the script's own location, hardcoded into the generated script.
- `--localized-dir <path>` *does* accept an absolute path (verified: passing
  `/tmp/external-data-dir` produced `local localized_dir=/tmp/external-data-dir`
  in the generated script) — but that path is a **string baked in at
  generation time**, not a runtime read of an env var. `$CLAUDE_PLUGIN_DATA` is
  only known at *invocation* time and — per `bin/mise-env`'s own comment — has
  been observed to vary/leak across plugins in the same session. There is no
  flag on either generator that reads an env var at runtime and no
  per-invocation env-injection hook on either command.
- The generated `bin/mise` sets exactly 2 of the 6 vars `bin/mise-env` sets
  (`MISE_DATA_DIR`, `MISE_TRUSTED_CONFIG_PATHS`) — plus `MISE_CONFIG_DIR`/
  `MISE_CACHE_DIR`/`MISE_STATE_DIR`, which `bin/mise-env` does not set at all.
  It sets **none** of `MISE_CEILING_PATHS`, `MISE_GLOBAL_CONFIG_FILE`,
  `MISE_SYSTEM_CONFIG_FILE`, `UV_CACHE_DIR`, and has **zero** `CLAUDE_PLUGIN_DATA`
  foreign-value guard logic.
- The generated task stub (`bin/run`) is `exec ./bin/mise run run "$@"` — no
  env logic of its own; it inherits only what `bin/mise` already set (or
  didn't).
- Side finding: running `task-stubs` in the scratch copy picked up 5 mise
  tasks that are **not** project-local (`update/all`, `update/brew`,
  `update/check`, `update/claude`, `update/mise` — global tasks visible in
  this host's merged mise config) and wrote stubs for them into `bin/`. A
  committed `bin/` built this way is not guaranteed to contain only this
  project's tasks.

**Verdict on the confinement question:** Candidate A cannot express
`bin/mise-env`'s job. `install-script`/`task-stubs` are generation-time tools;
the confinement problem is a runtime problem (resolve against *this session's*
`$CLAUDE_PLUGIN_DATA`, reject a foreign one). Adopting A would still need a
hand-written shim ahead of the generated stub to do exactly what
`bin/mise-env` does today — so it replaces `bin/aggregated-research`'s and
`bin/ty`'s one-line `exec`s, at the cost of a new `[tasks.run]` entry and a
generated-file-pollution risk, and leaves `bin/mise-env` in place regardless.

## Candidate B: no wrappers, README instructs `mise exec` directly

Built in `/tmp/proto-b` (`bin/`, `hooks/` removed from the scratch copy).

Removing `bin/` removes the only place the confinement env can be set before
`ty`/`aggregated-research` run:

- `.lsp.json`'s `"command": "${CLAUDE_PLUGIN_ROOT}/bin/ty"` has no successor —
  an LSP client's command/args array cannot carry inline env-var exports, so
  without `bin/ty` the language server would run against the *global* mise
  data dir, defeating the plugin-scoped isolation entirely.
- For the CLI itself, the README would have to instruct `mise exec -- 
  aggregated-research "$@"` directly. Where would the confinement env come
  from? `hooks.json`'s `SessionStart` hook can export it in its **own**
  spawned process, but:
  - **A1 (unverified, per spec — no citation found in this sandbox: no
    network egress, and no locally-installed copy of Claude Code's own hooks
    docs was found on this machine)**: whether that exported env reaches a
    *separate* Bash tool invocation later in the same session is ASSUMED
    false here (ordinary shell-per-invocation model), consistent with the
    spec's instruction to mark this `A` rather than state it as settled fact.
  - Independent of A1, `bin/mise-env`'s own comment records an **observed**
    case of `$CLAUDE_PLUGIN_DATA` carrying a *different* plugin's value into a
    Bash tool call in the same session — i.e., *something* about the env a
    Bash call sees is inherited from outside that call's own shell, and it is
    not clean per-plugin inheritance. That is direct evidence against
    candidate B's implicit premise (that hook-exported env reaches later Bash
    calls reliably and correctly scoped): the one documented data point is a
    **cross-contamination**, which is exactly the failure `bin/mise-env`'s
    guard exists to catch. Removing the wrapper removes the guard that catches
    the one failure this plugin has already seen.

**Verdict on the confinement question:** Candidate B has no reliable channel
to carry the confinement env from `SessionStart` to the CLI/LSP invocation. It
would need to either accept the risk the existing guard exists to prevent, or
re-embed the same env-setting logic per invocation in README prose the agent
is trusted to type correctly every time — worse than a script, not better.

## Recommendation

**Keep the status quo — neither candidate wins.** Deciding facts:

1. Neither generator reads an env var at *runtime*; `--localized-dir` bakes an
   absolute path in at *generation* time, so neither can track a per-session
   `$CLAUDE_PLUGIN_DATA` value the way `bin/mise-env` does.
2. The one confinement failure this plugin has actually observed
   (`CLAUDE_PLUGIN_DATA` cross-contamination, documented in `bin/mise-env`)
   is precisely the failure removing the wrapper (candidate B) would stop
   guarding against, and precisely the logic candidate A's generators do not
   provide.

`bin/mise-env`'s confinement logic has no native/generated replacement today.
Issue #587 should track re-checking this against future `mise` releases
(`tool-currency-and-native-first.md`), not attempt the swap now.

## Prototype artifacts

Built under `/tmp/proto-a` and `/tmp/proto-b` — scratch copies outside the
repo tree, not committed, disposable.

## GitHub repos touched

- [jdx/mise](https://github.com/jdx/mise) — read `mise generate install-script
  --help` / `mise generate task-stubs --help` output from the locally
  installed binary; no network fetch of the upstream repo was needed or made.

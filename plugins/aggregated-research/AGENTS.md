# Aggregated research plugin

Preserve `aggregated-research@ray-manaloto`, the executable name and the existing
dependency marketplaces. Read the plugin README and `docs/bin-wrapper-decision.md`
before changing wrappers or installation behavior.

`bin/mise-env` is the single confinement implementation used by the SessionStart
hook and both executable wrappers. It selects this plugin's own `mise.toml` and
stores tools under its plugin data directory. Do not merge the root OCI tools
or global mise configuration into that runtime.
Keep the per-version `CLAUDE_PLUGIN_ROOT` installation tree read-only; all mutable
plugin state belongs under the plugin data directory.

The data identifier is `aggregated-research-ray-manaloto`. An absolute
`CLAUDE_PLUGIN_DATA` is accepted only when its final component is that identifier;
foreign, relative and suffix-only paths are ignored. Trailing slashes are
normalized. The default is `$HOME/.claude/plugins/data/<identifier>`.

Preserve argument forwarding, process exit status, and the actionable missing
installation diagnostic (exit 2). A help request may still require the installed
runtime; syntax checks must not execute the installation hook.

Full behavior acceptance lives in `ci/acceptance.sh`: fresh Claude hook loading,
data confinement, accepted/foreign data-path cases, real hit and controlled-null
tracker arms. Shell/JSON checks are a distinct lightweight gate. Any backend
migration must compare behavior before replacing one module at a time.

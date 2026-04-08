---
name: mise-cli-cheatsheet
description: Comprehensive mise CLI reference grouped by task — tools, tasks, env, exec, config, lockfile, generators, shell aliases, settings. Use whenever the user needs the exact command for an action, or asks "what's the command for X". For the daily 20-command subset, use /mise-quickref instead.
---

# mise CLI cheatsheet

The full reference. For the 20-command "daily use" subset, see `/mise-quickref`.

## Tool management

```sh
# Install + pin (writes to nearest mise.toml)
mise use node@24
mise use node@24 python@3.12         # multiple at once
mise use -g node@24                  # global config (~/.config/mise/config.toml)
mise use --pin node@24               # write asdf-compatible exact version
mise use --env local node@24         # write to mise.local.toml
mise use --path mise.test.toml node@24

# Install only (no config write)
mise install                         # everything from mise.toml
mise install node@22                 # specific version
mise install node                    # latest of node from mise.toml

# Uninstall
mise uninstall node@22
mise uninstall --all node            # all installed versions of node
mise uninstall --all                 # all tools (preserves configs)

# List
mise ls                              # what's installed
mise ls --current                    # active for cwd
mise ls --offline                    # don't fetch upstream
mise ls node                         # versions of one tool
mise ls-remote node                  # available versions upstream
mise ls-remote node --installed      # already installed
mise current                         # active versions
mise where node                      # install dir of active node
mise which node                      # binary path of active node

# Upgrade
mise outdated                        # what's outdated
mise upgrade                         # upgrade installed tools (no config write)
mise upgrade --bump                  # upgrade AND update mise.toml/mise.lock
mise upgrade node                    # one tool

# Latest version helpers
mise latest node                     # newest available
mise latest --installed node         # newest installed
```

## Tasks

```sh
mise run test                        # run a task
mise run test build                  # multiple in sequence
mise run -- test --arg1 --arg2       # pass args after --
mise run --watch test                # re-run on file changes
mise run --jobs 8 test               # parallelism
mise run --raw test                  # bypass output capture (disables redactions!)
mise watch                           # alias for --watch

mise tasks                           # list tasks
mise tasks ls                        # same
mise tasks ls --hidden               # include hidden
mise tasks info test                 # full task config
mise tasks deps                      # dependency graph
mise tasks deps --hidden
mise tasks edit test                 # open in $EDITOR
mise tasks add lint -- pre-commit run -a   # add a task quickly
mise tasks validate                  # validate task definitions
```

## Environment variables

```sh
mise env                             # what mise is exporting
mise env --json                      # JSON form
mise env --dotenv                    # dotenv form
mise env --shell fish                # shell-specific export commands
mise env --redacted                  # only redacted vars
mise env --values                    # only values
mise env --redacted --values         # values of redacted vars (for ::add-mask::)

mise set FOO=bar                     # writes to mise.toml
mise set FOO=bar BAZ=qux             # multiple
mise set                             # show all set vars with sources
mise unset FOO                       # remove
```

## Execution

```sh
mise x -- node script.js             # run with mise env
mise exec node@22 -- node -v         # specific version
mise exec --command 'npm test'       # use shell -c
mise en                              # sub-shell with env loaded
mise en /path/to/project             # for a specific project
mise shell node@22                   # set tool for current shell only
mise shell --unset node              # unset
```

## Config

```sh
mise cfg                             # show loaded configs in precedence order
mise cfg ls                          # same
mise cfg get tools.node              # get a specific value
mise cfg set tools.node 24           # set a value (writes to mise.toml)

mise dr                              # doctor — health check
mise dr path                         # PATH-only diagnostic

mise edit                            # open mise.toml in $EDITOR
mise fmt                             # format mise.toml
mise fmt --check                     # check without modifying

mise trust                           # trust nearest config
mise trust <path>                    # trust specific
mise trust --untrust <path>          # un-trust
mise trust --all                     # trust all (interactive)
```

## Lockfile

```sh
mise lock                            # generate/update mise.lock for current platform
mise lock --platform linux-x64,macos-arm64,windows-x64
mise lock node python                # specific tools
mise lock --local                    # update mise.local.lock
mise lock -g                         # update global lockfile
```

## Settings

```sh
mise settings                        # list all settings + values + sources
mise settings ls
mise settings get experimental
mise settings set experimental=true
mise settings add idiomatic_version_file_enable_tools node
mise settings unset experimental
```

## Plugins (asdf/vfox)

```sh
mise plugins ls                      # installed plugins
mise plugins ls-remote               # available
mise plugins install <name>          # install from registry
mise plugins install <name> <git-url># custom URL
mise plugins update                  # update all
mise plugins uninstall <name>
mise plugins link <name> <local-dir> # local dev
```

## Backends

```sh
mise backends ls                     # available backends
mise registry                        # all registered short names
mise registry node                   # what node resolves to
mise search ripgrep                  # fuzzy search registry
```

## Generators

```sh
mise generate bootstrap -l -w        # ./bin/mise script
mise generate github-action          # .github/workflows/ci.yml starter
mise generate gitlab-ci              # .gitlab-ci.yml starter
mise generate devcontainer           # .devcontainer/devcontainer.json
mise generate git-pre-commit         # .git/hooks/pre-commit
mise generate config                 # mise.toml from .tool-versions
mise generate task-stubs             # IDE-discoverable wrappers
mise generate task-docs              # markdown docs from #MISE comments
mise generate tool-stub <tool>       # standalone shim for one tool
```

## Sync (one-time imports)

```sh
mise sync node                       # import nvm/n/volta versions
mise sync python                     # import pyenv versions
mise sync ruby                       # import rbenv versions
```

## Shell-side helpers

```sh
mise activate bash                   # print eval-able activation script
mise activate bash --shims           # shims-only mode
mise activate bash --status          # print status info on each cd
mise deactivate                      # remove from current shell
mise hook-env                        # the function the prompt hook calls
mise hook-not-found                  # command-not-found handler
mise reshim                          # rebuild shims
```

## Shell aliases (`[shell_alias]`)

```sh
mise shell-alias                     # list per-dir aliases
mise shell-alias ls
mise shell-alias get ll
mise shell-alias set ll "ls -la"
mise shell-alias unset ll
```

## Tool aliases (`[tool_alias]`)

```sh
mise tool-alias                      # list
mise tool-alias get node my_custom
mise tool-alias set node my_custom 20
mise tool-alias unset node my_custom
```

## Cache

```sh
mise cache                           # show cache info
mise cache path                      # cache dir
mise cache clear                     # clear cache
mise cache prune                     # prune stale entries
```

## Updates

```sh
mise self-update                     # update mise itself (curl/sh installs)
mise version                         # version info (more verbose than --version)
mise --version
```

## Cleanup

```sh
mise prune                           # remove orphaned tool installs
mise prune --plugins                 # also remove unused plugins
mise prune --dry-run                 # see what would be removed
mise implode                         # remove ~/.local/share/mise (preserves configs)
```

## Debugging

```sh
MISE_DEBUG=1 mise <command>          # debug log
MISE_TRACE=1 mise <command>          # even more verbose
MISE_LOG_LEVEL=trace mise <command>  # same
MISE_LOG_FILE=~/mise.log mise <command>  # log to file
MISE_LOG_HTTP=1 mise <command>       # show HTTP requests
```

## MCP server (experimental)

```sh
MISE_EXPERIMENTAL=1 mise mcp         # start MCP server (stdin/stdout JSON-RPC)
```

Resources: `mise://tools`, `mise://tasks`, `mise://env`, `mise://config`. Tools: `run_task`, `install_tool` (stub).

## Lesser-known but useful

```sh
mise test-tool <name>                # smoke-test a tool installs and runs
mise tool-stub <name>                # generate a standalone shim file
mise link <name> <path>              # symlink an externally-installed tool into mise
```

## See also

- `/mise-quickref` — the 20-command daily subset
- `mise-overview`, `mise-tasks-toml`, `mise-env-directives`, `mise-lockfile` — deeper coverage of each area
- <https://mise.jdx.dev/cli/>
- For the most current reference, run `/mise-refresh-knowledge` and `@`-import `~/.cache/mise-toolkit/llms.txt`

---
description: Print the mise daily-use cheat sheet
---

Print the mise CLI cheat sheet for daily use. Read `~/.cache/mise-toolkit/llms.txt` if it exists for the most current version, otherwise use the static reference below.

## The 20 commands you'll use 80% of the time

### Tools

```sh
mise use node@24                # install + pin (writes to nearest mise.toml)
mise use -g node@24             # install + pin globally (~/.config/mise/config.toml)
mise install                    # install everything in mise.toml
mise install node@22            # install a specific version (no config write)
mise ls                         # what's installed
mise ls --current               # what's active for the cwd
mise ls-remote node             # available versions of node upstream
mise upgrade --bump             # upgrade tools and update mise.toml + mise.lock
mise outdated                   # show what's outdated
mise uninstall node@22          # remove a version
```

### Tasks

```sh
mise run test                   # run a task
mise run test --watch           # re-run on file changes
mise tasks ls                   # list all tasks
mise tasks info test            # show full task config
mise tasks deps                 # task dependency graph
```

### Env

```sh
mise env                        # show all env vars mise is exporting
mise env --redacted             # show only secrets (masked)
mise set FOO=bar                # set an env var (writes to mise.toml)
mise unset FOO                  # remove an env var
```

### Exec

```sh
mise x -- node script.js        # run a command with mise env active
mise exec node@20 -- node -v    # run with a specific tool version
mise en                         # start a sub-shell with mise env loaded
```

### Config

```sh
mise cfg                        # show loaded config files in precedence order
mise cfg ls                     # same
mise dr                         # doctor — health check
mise trust                      # trust the nearest config
mise current                    # active tool versions
mise which node                 # path to the active node binary
mise where                      # install dir of the active tool
```

### Lockfile

```sh
mise lock                       # generate/update mise.lock
mise lock --platform linux-x64,macos-arm64    # multi-platform CI lockfile
mise lock --local               # update mise.local.lock
```

### Generators (less famous, very useful)

```sh
mise generate bootstrap -l -w   # ./bin/mise script for CI without curl-pipe-sh
mise generate github-action     # starter .github/workflows/ci.yml
mise generate devcontainer      # .devcontainer/devcontainer.json
mise generate git-pre-commit    # .git/hooks/pre-commit calling mise tasks
mise generate task-stubs        # IDE-discoverable task wrappers
```

## Aliases worth setting

```sh
alias x='mise x --'             # run with mise env: `x node script.js`
alias mr='mise run'             # `mr test`
alias ml='mise ls'              # `ml`
```

## When something feels wrong

| Symptom | First command to try |
|---|---|
| Tool version wrong | `mise cfg ls` then `mise current` |
| `mise.toml` not loaded | `mise dr` (likely untrusted) |
| Env var missing | `mise env \| grep VAR` |
| Slow shell prompt | `MISE_DEBUG=1 mise hook-env` |
| Install hitting rate limits | Check `MISE_GITHUB_TOKEN` and ensure `mise.lock` exists |

For the full reference, see `mise-cli-cheatsheet` skill or run `/mise-refresh-knowledge` and `@`-import `~/.cache/mise-toolkit/llms.txt`.

# Receipt: global hk alignment (D154) and Codex worktree removal (D155), 2026-10-14

Session `ccm-20261014` (Opus 5.5), parent, serial. Both operations were admitted by the user's
answers to Q127 and Q128.

## D154: global hk

| Step | Command shape | rc | Result |
| --- | --- | --- | --- |
| Diagnose | `mise x hk -- hk --version` in MP; `hk --version` on PATH | 0, 0 | 2.5.0 versus 2.6.0: the global config pinned `"packslip:github.com/jdx/hk"`, while the hook command asks for the registry name `hk`, which fell back to the newest installed registry `hk` (2.5.0) |
| Probe | scratch `mise.toml` with `[tools] hk = "2.6.0"`, `MISE_TRUSTED_CONFIG_PATHS` | 0 | `hk 2.6.0`; side effect: mise installed registry `hk@2.6.0` under `~/.local/share/mise/installs/hk/2.6.0` |
| Backup | `cp -p ~/.config/mise/config.toml ~/.config/mise/config.toml.bak-20261014-hk26` | 0 | |
| Edit | global config line 120: `"packslip:github.com/jdx/hk" = {...2.6.0...}` to `hk = {...2.6.0...}` with a dated comment (registry `hk` lists `packslip:github.com/jdx/hk` first) | 0 | `mise x hk -- hk --version` = 2.6.0 in `~` and in MP; `mise ls --global` shows `hk 2.6.0`; login-shell `hk --version` = 2.6.0 |
| Backup | `cp -p ~/.gitconfig ~/.gitconfig.bak-20261014-hk26` | 0 | |
| Install | `hk install --global --mise` from a scratch dir whose `hk.pkl` names six events (hk derives a global install's events from the project config; `install_global` first removes every global `hook.hk-*` entry, hk `src/cli/install.rs:337-353, 513-515` at v2.6.0) | 0 | global hooks for pre-commit, commit-msg, prepare-commit-msg, pre-push, pre-merge-commit, post-commit, each `test "${HK:-1}" = "0" \|\| ~/.local/bin/mise x hk -- hk run <event> --from-hook` |
| Probe | scratch repo: `hk run pre-merge-commit|post-commit --from-hook` with an `hk.pkl` lacking them; no `hk.pkl` | 0, 0, 0 | an undefined event is a no-op |
| Probe | scratch repo with `min_hk_version = "2.6.0"` and a marker step on pre-merge-commit; `git merge --no-ff` | 0 | marker written: pre-merge-commit fires, and 2.6.0 configs are accepted |

## D155: Codex worktrees and old-history branches

| Step | Command shape | rc | Result |
| --- | --- | --- | --- |
| Inventory | `git worktree list --porcelain` | 0 | 16 worktrees under `~/.codex/worktrees/<name>/claude-code-marketplace`; 10 with 2 to 7 uncommitted paths; ignored content only `.venv`, `.mise`, `__pycache__` |
| Archive | per worktree: `git update-ref refs/archive/codex-worktrees/<name> HEAD`; `git diff --binary HEAD`; untracked files `tar -czf`; `status --porcelain` | 0 | private notes `archive/codex-worktrees-2026-10-14/` (index.tsv, 9 patches, 9 untracked archives; commit `6c3afd7`) |
| Bundle | `git bundle create …-2026-10-14c.bundle --all`; `git bundle verify -q` | 0 | okay; 16 archive refs and 12 branches |
| Remove | `git worktree remove --force <path>` x16; `git worktree prune` | 0 | only the main checkout and the agy-history lane remain; each parent folder keeps Codex's `.codex-worktree-name` file |
| Delete | `git branch -D` x9 (2 old PR branches, `codex/28-` and `codex/29-offline-refresh`, 5 formerly checked-out Codex branches); `git update-ref -d refs/archive/…` x16 | 0 | local branches: `main`, `codex/marketplace-native-onboarding`, `claude/agy-history-skill` |

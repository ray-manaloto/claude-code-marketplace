# Receipt: planning-with-files Python pin moved to mise 3.15 (DL-147, D116)

Session ccm-20261014, 2026-10-14. File: `.claude/settings.local.json` (per-user, uncommitted).
Backup before the change: session scratchpad `backup-20261014/settings.local.json.before-mise-python`.

- Before: `env.PWF_TRUSTED_PYTHON = /usr/bin/python3` (3.9.6, root-owned, chosen in F4 for that).
- After: `env.PWF_TRUSTED_PYTHON = /Users/rmanaloto/.local/share/mise/installs/python/3.15/bin/python3`.
  `python/3.15` is mise's fuzzy-version symlink (`-> ./3.15.0` today), so a 3.15 patch install moves it.
- Checks: the interpreter reports 3.15.0 (rc 0); `test -f -a -x` passes, which is what the pwf
  dispatcher requires (absolute, regular, executable; F4 `claude-hook.sh:49-95`, version 3.8 or newer);
  every other key in the file compared equal before and after (rc 0).
- Trade-off recorded: the mise path is user-writable, unlike `/usr/bin/python3`; the user chose the
  mise-managed interpreter (D116).

## Second change (D122, same day)

The user chose the repository's own mise pin as the single Python source (Q93, D122), so
`env.PWF_TRUSTED_PYTHON` now names `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.mise/installs/python/3.15/bin/python3`
(`.mise/installs/python/3.15` is mise's fuzzy symlink inside `MISE_DATA_DIR` set by `dev/mise`;
3.15.0 today). Checks: `test -f -a -x` passes; the interpreter reports 3.15.0. The deny-gate hook
launch follows in the unit that changes `dev/hooks/`.

---
paths: [".gitleaks.toml", "dev/git_delivery.py", "dev/issue_amend.py"]
---

# Secret scanner configuration

- `.gitleaks.toml` holds generic rules only. The private-name rule (`private-tr-project`) lives outside the repository, committed only in the private-notes repo (no remote) at `~/.local/state/claude-code-marketplace/private-notes/scanner/private-rules.toml`, mode 0600; `MARKETPLACE_PRIVATE_RULES` overrides the path (D178). Never copy it, or a word it guards, into a tracked file.
- Every scan goes through `scan_config` in `dev/git_delivery.py`: the A09 staged and outbound scans, and the `scan` helper in `dev/issue_amend.py` that the issue and gh routes call. It writes the tracked rules plus the private rule file into a private temporary config (0700 directory, 0600 file), scans with it and deletes it. It refuses with exit 2 when the tracked config is unreadable (the reason names that path), when the variable is relative, when the private file is missing, unreadable, a symlink, readable by other users (mode must be 0600), or lacks the rule id alone or after the tracked rules; the reason names the variable and the default path, never a value. A new scan route calls it too.
- Tests point `MARKETPLACE_PRIVATE_RULES` at a synthetic rule (`synthetic_private_rules` in `dev/test_git_delivery.py`); no test reads the real file or derives a sample from it.
- Hosted CI has no private rule file until the D180 Actions secret lands; a CI scan route refuses until then rather than scanning without it.
- Diff this file with `git diff -U0 -- .gitleaks.toml | grep -v '^@@'`: a hunk header quotes the nearest unindented line, which before D178 was the private-name rule's `regex` value. Cite a rule by its `id` and `description` lines.

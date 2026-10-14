---
paths: [".gitleaks.toml"]
---

# Secret scanner configuration

- Diff this file with `git diff -U0 -- .gitleaks.toml | grep -v '^@@'`: a hunk header quotes the nearest unindented line, which is the private-name rule's `regex` value. Cite a rule by its `id` and `description` lines.
- The private-name rule spells its words as character classes, and a test fixture assembles its secret at runtime (`dev/test_git_delivery.py`), so no committed file holds a match.

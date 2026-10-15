# Claude Code 2.1.251 → 2.1.300 release intake (R-176, #140)

Built 2026-10-14 by a read-only intake agent of session `ccm-20261014`.

Committed here (our own analysis):

- `impact.md` and `impact.json`: 34 reviewed changes against hooks, mods, skills, agents, settings,
  the ticket ledger and the open requests; the top 10 actions.
- `settings-delta.md`: settings, environment variables and frontmatter keys added or removed
  between 2.1.251 and 2.1.300.
- `upgrade-plan.md`: the image-pin bump (R21 batch 4, CT-08 baseline transition) and the offline
  refresh.
- `workflow-inventory.md`: what the dependency-upgrade workflow has in this repo, what exists only in
  TR (R-163) and what is missing.

Kept local only, not tracked (the upstream changelog text and docs are third-party content):
`offline/research/R22-cc-2.1.300/`, with `releases.json` (40 releases, 2,893 typed changes),
`releases.okf.md`, `okf/` (an OKF v0.2 bundle of 44 files), `settings-delta.json`, `raw/` (changelog
at the tag, release bodies, issue snapshots) and `scripts/` (the generators). Its `manifest.json` has
sha256 `04b5935dc55221beb0ad2c95c67a38ad19010d74c1c21ccdcce033a3ea449c8b` and lists every file's sha256.
An agent reviewing the release reads that directory first.

# Disk cleanup receipt, 2026-10-14

Admission: the user's instructions "Fix disk space issue" and "It coild ne docker artifacts taking
up disk space" (session `ccm-20261014`, `ce9c0b3d`), plus D9 for the lane worktrees. Only caches,
never-started containers and merged, clean worktrees were removed; nothing holding data.

| Step | Command | rc | Effect |
|---|---|---|---|
| Before | `df -h /System/Volumes/Data` | 0 | 37 GiB free (98% used); Docker Desktop `Docker.raw` 351 GB on disk |
| 1 | `docker rm` (batches of 20) on 248 containers in state Created from MCP images (`mcp/*`, `ghcr.io/github/github-mcp-server`, atlassian, grafana) | 0 | containers 253 to 4 (1 running devcontainer, 3 stopped devcontainers kept) |
| 2 | `docker image prune -f` (dangling only) | 0 | 3 kB |
| 3 | `docker builder prune -a -f --filter until=72h`, then `docker builder prune -a -f` | 0, 0 | build cache 152.9 GB to 0 B |
| 4 | `npm cache clean --force` | 0 (EACCES on root-owned entries) | `~/.npm/_cacache` 22 GB to 2.0 GB; `_npx` (6.2 GB, used by running MCP servers) untouched |
| 5 | `brew cleanup -s` | 0 | about 445 MB |
| 6 | `uv cache prune` | 2 | not run: lock held by running `uvx` processes (ty server and another uvx); cache stays 46 GB |
| 7 | `git worktree remove .claude/worktrees/<unit>` for a06-unit3, c1-catalog-promotion, codex-session-history, gate-hooks, nav, retro-gate, rf-env-scrub, team, w0-decisions, w0-docs (each HEAD in HEAD, 0 dirty files; branches kept) | 0 ×10 | about 2.4 GB |
| After | `df -h /System/Volumes/Data`; `du -sh Docker.raw` | 0 | 162 GiB free (92% used); `Docker.raw` 249 GB |

Not touched, awaiting the user: unused Docker images (about 85 GB reclaimable, old dotfiles
devcontainer versions), unused Docker volumes (27.6 GB, may hold data), 3 stopped dotfiles
devcontainers, `~/.codex` (visualizations 113 GB, archives 59 GB, worktrees 84 GB: Codex data and
import sources), `~/Library/Caches/uv` 46 GB (offline installs rely on it), root-owned npm entries.

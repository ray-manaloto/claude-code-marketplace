# Docker volume cleanup receipt (2026-10-14, DL-105)

User answer, grill-with-docs round 3 Q43: "Option 1 and remove all symphony we dont use that
anymore". Option 1 = delete the unused dotfiles home volumes after a read-only content check, plus
the anonymous volumes; the user widened it to every symphony volume.

| Step | Command | rc | Result |
|---|---|---|---|
| Inventory | `docker system df -v` | 0 | 52 volumes; only `dotfiles-dotfiles-rmanaloto-273897ea-amd64-home` in use (1 link) |
| Content check | `docker run --rm --network none -v <vol>:/v:ro graphify-validation:py3.13-20260922` listing names only, per home volume | 0 (x20) | shell rc files, `.cache`, `.cargo`, `.rustup`, `.local`, `.venvs`, `.pixi`, `.bun`, `.npm`; `.ssh` holds only `authorized_keys` and `known_hosts`; `.config/gh` empty; `.claude` holds config backups and an empty `sessions/`; no `.claude/projects`, `.codex/sessions`, `.codex/auth.json`, git repositories or private keys |
| In-use check | `docker ps -a --filter volume=<vol>` | 0 (x51) | no container references any volume on the list |
| Delete | `docker volume rm <vol>` | 0 (x51) | removed 51, failed 0 |
| After | `docker volume ls -q` | 0 | 1 volume left (the in-use dotfiles home) |

Removed: 20 dotfiles home volumes, 29 symphony volumes, 2 anonymous volumes.

Disk: free before 331702576 KiB, after 343000716 KiB (`df -k /System/Volumes/Data`); `Docker.raw` 74 GB on disk after (86 GB earlier today; the image shrinks lazily).

Removed volume names:

- `dotfiles-checkout-rmanaloto-56958aac-amd64-home`
- `dotfiles-currency-20260930-rmanaloto-10250bf8-amd64-home`
- `dotfiles-dotfiles-arm64-main-rmanaloto-019ae7b8-arm64-home`
- `dotfiles-dotfiles-codex-task-orchestration-v2-rmanaloto-87e0f7e3-amd64-home`
- `dotfiles-dotfiles-goal-history-rmanaloto-09c2cf5f-amd64-home`
- `dotfiles-dotfiles-issue-753-writer-lease-rmanaloto-b7909ff7-amd64-home`
- `dotfiles-dotfiles-issue-763-rmanaloto-d9b2fbed-amd64-home`
- `dotfiles-dotfiles-lockup-rmanaloto-dd50a80f-amd64-home`
- `dotfiles-dotfiles-pr671-rmanaloto-51d55b32-amd64-home`
- `dotfiles-dotfiles-rmanaloto-273897ea-arm64-home`
- `dotfiles-dotfiles-rmanaloto-a87611e9-amd64-home`
- `dotfiles-dotfiles-rmanaloto-df17c837-amd64-home`
- `dotfiles-dotfiles-ship-fnox-doctor-rmanaloto-1813dafb-amd64-home`
- `dotfiles-repo-rmanaloto-8ca71197-amd64-home`
- `dotfiles-repo-rmanaloto-889ec386-amd64-home`
- `dotfiles-repo-rmanaloto-5838b679-amd64-home`
- `dotfiles-repo-rmanaloto-76762912-amd64-home`
- `dotfiles-repo-rmanaloto-e493578d-amd64-home`
- `dotfiles-research-five-source-gate-rmanaloto-0f760abc-amd64-home`
- `dotfiles-research-five-source-land-rmanaloto-75be8a8f-amd64-home`
- `symphony-codex-auth`
- `symphony-codex-auth-controller-019fb0f0`
- `symphony-cpp-arm64-mise`
- `symphony-cpp-arm64-pre-commit`
- `symphony-cpp-gcc16-arm64-ccache`
- `symphony-cpp-gcc16-ccache`
- `symphony-cpp-mise`
- `symphony-cpp-pre-commit`
- `symphony-cpp-vcpkg-archives`
- `symphony-cpp-vcpkg-arm64-archives`
- `symphony-cpp-vcpkg-arm64-downloads`
- `symphony-issue7-openhands-codex-auth`
- `symphony-issue7-openhands-state`
- `symphony-opensymphony-ccache-controller-019fb0f0`
- `symphony-opensymphony-control-controller-019fb0f0`
- `symphony-opensymphony-gcc16-ccache`
- `symphony-opensymphony-gcc16-ccache-controller-019fb0f0`
- `symphony-opensymphony-state`
- `symphony-opensymphony-state-controller-019fb0f0`
- `symphony-opensymphony-tools`
- `symphony-opensymphony-tools-controller-019fb0f0`
- `symphony-opensymphony-uv-cache`
- `symphony-opensymphony-uv-cache-controller-019fb0f0`
- `symphony-opensymphony-uv-controller-019fb0f0`
- `symphony-opensymphony-vcpkg-archives`
- `symphony-opensymphony-vcpkg-archives-controller-019fb0f0`
- `symphony-opensymphony-vcpkg-controller-019fb0f0`
- `symphony-opensymphony-workspaces`
- `symphony-opensymphony-workspaces-controller-019fb0f0`
- `71bc331607e8749e51cffd0b566d9bd3013eac015bad22638b6856b8cf30c491`
- `444fd37ecc3200c4a516a52883b44a1614db8dfcb1f6b770bc44d7cb15109bca`

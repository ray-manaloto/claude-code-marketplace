---
name: mise-codespaces
description: GitHub Codespaces specifics for mise — prebuilds, repo secrets, image caching, free-tier vs paid considerations, and what goes in onCreateCommand vs postCreateCommand. Use when setting up Codespaces for a project with mise.
---

# mise in GitHub Codespaces

Codespaces is devcontainers-as-a-service on GitHub. Everything in `mise-devcontainer-patterns` applies; this skill covers the Codespaces-specific bits.

## Prebuilds — the #1 thing to get right

A "prebuild" is a nightly (or on-push) job that runs your devcontainer's `onCreateCommand` and snapshots the result. When a developer creates a codespace, GitHub starts from the prebuild snapshot instead of running `onCreateCommand` from scratch.

**Without prebuilds**: `mise install` runs on every codespace create. For a project with 5 tools, that's 2-5 minutes of "starting codespace..." every time.

**With prebuilds**: `mise install` has already run during the prebuild. Codespace starts in 10-30 seconds.

The cost: prebuilds consume GitHub Actions minutes and storage. For active projects this is well worth it; for dormant forks it's not.

### Enabling prebuilds

Prebuilds are enabled in **Settings → Codespaces → Set up prebuild** on the repo page. You pick:
- **Branch** (usually `main`, optionally `release/*`).
- **Regions** (pick 1-2 close to your team).
- **Trigger**: on every push to the branch, on config change only, or scheduled.
- **Retention**: how long prebuilds are kept.

There's no `.yaml` file for this — it's entirely a UI setting. The repo needs admin rights.

### Scheduled prebuilds via workflow

If you want cron-style prebuilds, add a workflow:

```yaml
# .github/workflows/codespaces-prebuilds.yml
name: Codespaces Prebuilds
on:
  schedule:
    - cron: '0 6 * * 1-5'  # weekdays 6am UTC
  workflow_dispatch:
jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - run: gh api --method POST /repos/${{ github.repository }}/codespaces/prebuilds
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Secrets and env vars

Codespaces secrets work differently from regular repo secrets:

- **User-level** (Settings → Codespaces → Codespaces secrets): available in all your codespaces across repos.
- **Repo-level** (Repo Settings → Secrets → Codespaces): available to codespaces for this repo for authorized users.
- **Org-level**: available per policy.

In the devcontainer, secrets show up as regular env vars. Reference them in `mise.toml`:

```toml
[env]
DATABASE_URL = { required = "Needs DATABASE_URL set via Codespaces secrets" }
GITHUB_TOKEN = { value = "{{env.GITHUB_TOKEN}}", redact = true }
```

**Don't** commit `.env` files to the repo and source them — use Codespaces secrets. mise's `redact = true` makes the values invisible in `mise env` output, but secrets are the primary protection.

## Free tier vs paid

As of this writing, personal accounts get 120 core-hours/month free. Prebuilds, active codespace time, and storage all count.

**For free-tier sustainability**:
- Use a 2-core machine (not 4 or 8) unless your build genuinely needs more.
- Enable **auto-stop** at 30 minutes of inactivity (default).
- Delete idle codespaces you're not coming back to.
- Limit prebuild regions to 1.
- Use prebuild **on config change** trigger, not on every push.

For organizations, Codespaces billing is per-user and can escalate. Have a billing conversation before rolling out widely.

## onCreateCommand details for Codespaces

The prebuild runs `onCreateCommand` on a fresh container with **no source code mounted**. The source comes in later during the actual codespace create. This means:

- **Put mise install in `onCreateCommand`** — it only needs `mise.toml` + `mise.lock`, which are checked out before onCreate runs.
- **Put source-dependent steps in `postCreateCommand`** — `npm ci`, `bundle install`, `cargo fetch`, etc.
- **Use `updateContentCommand`** for steps that should rerun when the user pulls new source (without a full rebuild).

## Dotfiles

Codespaces supports per-user dotfiles: you point it at your dotfiles repo, and it runs your `install.sh` in every codespace. Great place to put:

- Your global mise config (`~/.config/mise/config.toml`).
- Your shell aliases, zsh plugins, git config.
- Your editor config.

**Do not** put project-specific mise tools in dotfiles — that belongs in the project's `mise.toml`.

## Limitations to know

- **No systemd** in the container by default.
- **No Docker-in-Docker** without the `docker-in-docker` feature.
- **Mac / Windows hosts** run codespaces as Linux containers — native tools don't apply.
- **GPU codespaces** exist but require a specific machine type and are billed separately.
- **Port forwarding** is automatic for ports mise tasks expose; private ports need explicit configuration.

## See also

- `mise-devcontainer-patterns` — the underlying devcontainer.json that Codespaces uses.
- `mise-trust-and-security` — why `MISE_TRUSTED_CONFIG_PATHS` matters in hosted environments.
- `mise-ci-github-actions` — for CI, not Codespaces. They're siblings, not substitutes.
- GitHub docs: `docs.github.com/en/codespaces`.
- `/mise-codespaces-prebuild` — generates the devcontainer.json + prebuild workflow.

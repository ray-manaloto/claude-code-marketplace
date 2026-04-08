---
description: Generate devcontainer.json + Codespaces prebuild config for zero-cold-start onboarding
---

Set up the current project for **GitHub Codespaces with prebuilds** — meaning contributors get a fully-provisioned codespace in seconds, not minutes, because mise has already pre-installed all tools during the prebuild workflow.

## Steps

1. **Survey** — check for existing `.devcontainer/devcontainer.json`, `.github/workflows/codespaces-prebuilds.yml`, and `mise.toml`.

2. **Devcontainer first** — if there's no `.devcontainer/devcontainer.json`, run `/mise-devcontainer` first (or delegate to that command). Prebuilds require a devcontainer.

3. **Generate the prebuild workflow** at `.github/workflows/codespaces-prebuilds.yml`:
   ```yaml
   name: Codespaces Prebuilds
   on:
     push:
       branches: [main]
     pull_request:
       paths:
         - '.devcontainer/**'
         - 'mise.toml'
         - 'mise.lock'
     workflow_dispatch:
   jobs:
     createPrebuild:
       uses: github/codespaces-precreate/.github/workflows/createPrebuildTemplate.yml@main
   ```
   (The repo admin still needs to enable prebuilds in repo Settings → Codespaces → Set up prebuild.)

4. **Tune `devcontainer.json` for prebuilds**:
   - Move `mise install` from `postCreateCommand` to `onCreateCommand` so it runs during the prebuild instead of at codespace-start time.
   - Keep `postCreateCommand` for things that need the mounted source (e.g. `npm install`, `cargo fetch`).
   - Add `"waitFor": "onCreateCommand"` so VSCode doesn't signal "ready" before mise has finished.

5. **Document the repo-admin step** in the final message: prebuilds must be enabled manually via the GitHub UI; the workflow alone is not enough.

6. Show diffs for every file being created/edited and ask for confirmation before writing.

## What to avoid

- Enabling prebuilds for every branch — restrict to `main` (and optionally `release/*`) to keep Actions minutes down.
- Running `mise install` in `postCreateCommand` — that defeats the whole point of the prebuild.
- Forgetting the repo-admin UI step. The workflow is necessary but not sufficient.
- Assuming the user's Codespaces quota — prebuilds consume storage and minutes.

For the full trade-off discussion and free-tier vs paid considerations, read the `mise-codespaces` skill.

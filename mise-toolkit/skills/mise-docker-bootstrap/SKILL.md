---
name: mise-docker-bootstrap
description: The `mise generate bootstrap -l -w` pattern for pinning mise in Dockerfiles and CI without `curl | sh`. Commit `./bin/mise` so builds are reproducible and network-free for the mise install step.
---

# Bootstrap pattern — pinned mise, no `curl | sh`

Every "quick start" guide says `curl https://mise.run | sh` in your Dockerfile. That works but it:

1. Makes the build depend on the network.
2. Pulls whatever mise version happens to be current, so rebuilds are not reproducible.
3. Gives every rebuild a chance to break when a new mise release has a regression you haven't vetted.

The `mise generate bootstrap` command solves all three by generating a small self-contained bootstrap script that downloads a **specific pinned** mise version, verifies its checksum, and installs it locally. You commit it to the repo and use it from the Dockerfile.

## The command

Run once, from any machine that has mise:

```sh
mise generate bootstrap --localize --write
# short form:
mise generate bootstrap -l -w
```

This:
1. Writes `./bin/mise` — a shell script that downloads mise at the pinned version (the version currently on the generating host).
2. With `-l/--localize`, also writes a small helper so the script is usable via relative path.
3. `-w/--write` writes to disk instead of printing to stdout.

Commit `./bin/mise` to the repo. It's a few KB.

## Using it in a Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.7
FROM debian:12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy the bootstrap first so it's cached aggressively
COPY bin/mise bin/mise
RUN ./bin/mise --version  # installs pinned mise into ~/.local/share/mise

COPY mise.toml mise.lock ./
RUN --mount=type=cache,target=/root/.local/share/mise/installs \
    ./bin/mise trust && ./bin/mise install

COPY . .
RUN ./bin/mise exec -- <build command>
```

## Using it in CI

The same script works in GitHub Actions without the `jdx/mise-action`:

```yaml
- run: ./bin/mise install
- run: ./bin/mise run test
```

This is useful when you need a version of mise that's newer/older than whatever `jdx/mise-action@v3` defaults to, or when you don't want to depend on a third-party action.

## Upgrading mise

When you want a new mise version:

```sh
mise up mise  # or: mise self-update
mise generate bootstrap -l -w
git add bin/mise && git commit -m "chore: bump mise to $(mise --version)"
```

Now the Dockerfile / CI get the new version on the next build. No `curl | sh` in sight.

## Why not just `ENV MISE_VERSION=2026.4.5` and `curl | sh -s -- --version $MISE_VERSION`?

You can, and it works, but:
- You still depend on `mise.run` being reachable at build time.
- You still depend on the TLS chain being valid and untampered at build time.
- You don't get checksum verification.
- The `mise generate bootstrap` script handles platform detection, architecture fallback, and checksum verification in one place.

For single-developer projects, the `curl | sh` form is fine. For anything shipping to production or running in CI at a shop with a security team, use the bootstrap.

## Offline / airgapped builds

If your build environment has no internet at all, the bootstrap script's download step will still fail. For airgapped cases:

1. Run the bootstrap once with internet to download the mise binary into `~/.local/share/mise/mise`.
2. Commit the resulting binary (or stage it in your build context).
3. Have the Dockerfile copy it directly into `/usr/local/bin/mise`.

But that's rare. The bootstrap pattern covers 95% of "I want reproducible mise installs".

## See also

- `mise-docker-patterns` — where the bootstrap fits in the canonical Dockerfile.
- `mise-lockfile` — `mise.lock` is the other half of reproducibility (pins the tools; bootstrap pins mise itself).
- `mise-ci-github-actions` — when to use `jdx/mise-action` vs the bootstrap.
- mise docs: `mise.jdx.dev/cli/generate/bootstrap.html`.

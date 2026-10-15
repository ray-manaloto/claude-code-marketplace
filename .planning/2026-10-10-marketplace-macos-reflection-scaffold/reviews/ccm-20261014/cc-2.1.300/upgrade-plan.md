# Upgrade plan: project pin `npm:@anthropic-ai/claude-code` 2.1.251 -> 2.1.300 (plan only, nothing changed)

Facts read 2026-10-14: host `~/.local/bin/claude` is 2.1.300; npm dist-tags `latest` = `next` = 2.1.300, `stable` =
2.1.292 (R21 recorded `latest` 2.1.299, `stable` 2.1.287 earlier the same day); GitHub release v2.1.300 published
2026-10-14T18:24:25Z, tag commit `94506ff0d3bd9185f1752da36e968775021fb48f`; npm 2.1.300 needs node >= 22 (image has
26.8.1) and installs its native binary through `postinstall` plus per-platform optional packages (so `allow_builds`
stays).

## 1. Target version

2.1.300. Not npm `stable` 2.1.292: it predates `onFailure: "block"` (2.1.295), which `.claude/settings.json` uses on the
three deny gates, and the mod APIs the CT-23/CT-31 specs would use (2.1.299/2.1.300). Ticket home: R21 batch 4, the
frozen-baseline transition (CT-08 or a CT-08b row), under R-158 (#128). Batch 4 also carries gh, ty, node, uv (OCI),
the Debian digest and the action pins; they can move together or the Claude Code row can go alone.

Timing: mise's default `minimum_release_age` for npm tools is 24h (R21 finding 7), so `mise lock` would hide 2.1.300
until about 2026-10-15T18:24Z (GitHub release time; the npm publish time was not fetched). R-166 (#130) asks for 1h
in this project, which would admit it now. Locked versions install regardless of the cooldown.

## 2. Files the bump touches

| File | Baseline file? | Change |
|---|---|---|
| `mise.toml:10` | yes (1 of 19) | `version = "2.1.251"` -> `"2.1.300"`; keep `allow_builds` |
| `mise.lock:132-138` | yes | `version`, `specifiers` -> 2.1.300 (npm rows carry no URL or checksum here) |
| `evidence/onboarding/baseline-files.json` | the baseline record itself | new versioned record: sha256 and bytes for `mise.toml` and `mise.lock` (and any other batch-4 file) |
| `.github/workflows/acceptance.yml` | yes | none for this row: the smoke step reads the pin from `mise.toml` (lines 31-35) |
| `ci/acceptance.sh` | yes | none planned; the admitted run decides (plugin install `--yes`, `plugin_errors` check at :183) |
| `.claude/skills/session-handoff/references/handoff-template.md:38` and the `.agents/` mirror | no | CLI row still says 2.1.299 |
| `docs/agents/hooks-and-mods.md:65, 74-78, 82-86, 106` | no | version and issue-state statements (see impact.md rows on #92533, #84320, #102134) |
| `.claude/settings.json`, `dev/doctor/settings.py`, `.claude/AGENTS.md`, `dev/test_doctor.py` | no | only if the idle-compaction decision adds `idleCompaction` |

How the lock moves: `./dev/mise run deps:lock` is the wrong tool; it locks only `mise.dev.toml` and `uv.lock` and
refuses any change to `mise.toml`/`mise.lock` (`dev/bootstrap.py:21, 188`). The root lock needs an isolated root-context
`mise lock` (global config excluded, as `dev/mise` does for the dev file), fixed and admitted in the CT-08 lane. After
it, run `./dev/mise run deps:check` to show the dev environment did not move.

## 3. Checks and admissions

One writer, one worktree, named checks from that worktree only, actual exit codes recorded, retro gate at the end:
`./dev/mise tasks validate`, `./dev/mise run check`, `./dev/mise run check:acceptance-baseline` (must fail on the edited
tree before the new baseline record and pass after it), `./dev/mise run check:research`, `./dev/mise run test:hooks`,
`./dev/mise run test:delivery`. Separately admitted: `mise oci build`, the in-image `claude --version` smoke step, and
`ci/acceptance.sh` (container, provider and fresh-session acceptance). Publish, push and merge wait for instruction.

## 4. Offline docs and repo-mirror refresh

Until CT-33/CT-41/CT-42 land, a refresh follows R21's shape: a new `offline/research/<id>/` folder (untracked) with
`manifest.json` items (`source_url`, `local_path`, `bytes`, `sha256`, `command_shape`, `exit_code`, `retrieved_utc`)
and a `queries.jsonl` log. When CT-33 lands the same rows move to `/offline/sources/<id>/runs/<run>/`, the
content store `/offline/objects/sha256/`, receipts under `evidence/offline/runs/`, and `offline-sources.toml` rows 1-3
of C1 section 3.3 (claude-code-docs, claude-code-changelog, claude-code-plugins). Licence class for all three:
private (Anthropic, all rights reserved): never tracked, quotations within the CT-44 budget.

| What | Command shape | Size | Replaces |
|---|---|---|---|
| CHANGELOG at the tag | `gh api repos/anthropics/claude-code/contents/CHANGELOG.md?ref=v2.1.300` (raw) | 1,028,694 B, sha256 `8c6fdbbd...` | R21 `releases/anthropics_claude-code_CHANGELOG.md` (main, 2.1.299) |
| Release range note | `gh api 'repos/anthropics/claude-code/releases?per_page=100'` -> `releases/anthropics_claude-code__2.1.251..2.1.300.md` | page 1 covers 2.1.179-2.1.300 | R21 `__2.1.251..2.1.299.md` |
| Docs pages | `webclaw <https://code.claude.com/docs/en/<page>.md> -f markdown --metadata`; `settings-reference` only renders with `-f json` | 222 `/docs/en/*.md` URLs in `llms.txt` today; hooks.md 262 KB, env-vars.md 171 KB | R5 (13 pages), R12, R21 (2 pages); KB/DF copies per C1 |
| Repo mirror | sparse, blob-less clone of `anthropics/claude-code` at `v2.1.300`: root files, `mods/` (agents-md, diff, sec-default, telemetry, types), `plugins/`, `examples/`; skip `demo.gif` (11 MB) and `feed.xml` | a few MB | R9 `claude-code-sparse` at `19eb0958` (2026-10-14T13:25Z, before 2.1.300) |
| Plugin type declarations | `mods/types/` from the tag, or regenerated by the installed CLI | ~0.5 MB | R5/R7/R9 `claude-code-2.1.296.d.ts` |
| npm metadata | `registry.npmjs.org/-/package/@anthropic-ai/claude-code/dist-tags` and `/@anthropic-ai/claude-code/2.1.300` | < 10 KB | R21 `api/registry/` |
| Upstream issue snapshots | `gh api repos/anthropics/claude-code/issues/<n>` (+ `/comments`) for #84320, #92533, #94358, #94594, #96831, #99130, #100869, #101384, #102134 | small | none (CT-80 watch) |

Priority pages for this project: settings, settings-reference, env-vars, hooks, hooks-guide, sub-agents, skills,
memory, worktrees, cli-reference, model-config, permission-modes, agent-teams, agent-view, changelog, plugins/*
(manifest-reference, marketplace-reference, dependencies, loading, cli-reference, troubleshooting) and plugins/mods/*
(overview, api, events, reference, interface, test, troubleshoot, admin).

This intake already fetched most of these into the session scratchpad (`raw/`), but C1 rule 1 is "re-fetch, never
copy": the admitted run should fetch again and write its own receipts.

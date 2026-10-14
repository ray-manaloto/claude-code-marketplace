# R7: Detecting that Claude Code mods are switched off (research round 5, 2026-10-14)

Research agent R7 of session `ccm-20261014` (`ce9c0b3d`) for the user's decision D111: the shipped
`aggregated-research` plugin's SessionStart behaviour becomes a mod, and a fallback wrapper covers sessions
where mods are off. This report answers how to detect "mods off" before anyone writes that wrapper. It
extends R1 (mod loading gaps), R2 (#92533) and R3 (awaiting the plugin reload) and does not repeat them.
MP at `21af565`, branch `codex/marketplace-native-onboarding`. Host CLI: `claude --version` prints
`2.1.299 (Claude Code)`. Read-only toward MP except this file and the offline mirror.

Citation keys. O = `MP/offline/research/R7-mods-switch-detection/` (untracked mirror, `manifest.json` lists
URL, local path, fetch time, command, exit code and SHA-256 or commit for every item). Docs pages are cited as
`O/docs/<page>.md:N` (webclaw copy) or `O/docs/raw/<page>.md:N` (raw markdown from
`https://code.claude.com/docs/en/<page>.md`). B = the installed binary
`~/.local/share/claude/versions/2.1.299` (SHA-256 `ba5ab7b8c195fa03ab8d5bf3915c76153b576a2c40e79a5c46e265e7ed9744b3`),
read with `strings -n 8`; the cited excerpts are saved as `O/binary/NN-*.js.txt`. The JavaScript is
minified, so names such as `Ib` or `dgr` are build-local, and every B claim is a reading of code, not an
executed test. T = the 2.1.296 mod type declarations, copied to `O/types/claude-code-2.1.296.d.ts`. CL =
`O/github/CHANGELOG.md` (anthropics/claude-code, fetched 2026-10-14, top entry 2.1.299), cited as
`CL <version>:<line>`. `#N` = anthropics/claude-code issue or PR N; its JSON with comments is in
`O/github/issues/`.

## Verdict

Recommendation: do not detect the switch; detect the effect. The mod announces in band that it handled the
event, and the plugin's own SessionStart command hook runs only when that announcement is missing. Concretely:

1. The mod's `classic.SessionStart` hook does the work, then calls `next({ ...e, aggregated_research_mod:
   "handled" })`. The plugin's SessionStart command hook, in the same `hooks/hooks.json` as the `modules`
   key, exits 0 when it sees that field on stdin. This is the obsidian-mind stand-down pattern.
2. One atomic per-session claim (`mkdir <claims>/<session_id>`) is taken by whichever path does the work: the
   mod's `classic.SessionStart`, the mod's native `session.start`, or the fallback hook. This covers two
   cases the field cannot: `classic.*` events not reaching modules (#100869), and a mod that loads late after
   SessionStart already ran (B `Y2s`). This is the lcm#393 claim pattern.
3. The cause (the remote switch) is logged by the fallback for diagnostics only. It is read from
   `cachedGrowthBookFeatures.tengu_plugin_hooks_modules` in `${CLAUDE_CONFIG_DIR:-$HOME}/.claude.json`,
   together with the environment variables that switch flag fetching off. It never gates anything.

Confidence. High that no supported, in-session readout of the switch exists for a shell hook. Medium-high
that the effect-based method above is correct: vendor docs say a field passed to `next` is what settings
hooks read, and two shipping projects use these two patterns. Medium on start-up ordering until a live
probe runs (section 7).

Evidence that decides it:
- The switch is the GrowthBook feature `tengu_plugin_hooks_modules`, default `true` in 2.1.299. Since 2.1.287
  no setting or variable overrides it: the public build's override readers are stubs, and
  `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` is ignored. Sources: B (`O/binary/02-flag-key.js.txt`,
  `08-default-and-ib.js.txt`, `04-override-stubs.js.txt`), `O/docs/raw/plugins_mods_overview.md:115`, and
  wasikarn/method-harness#323.
- Nothing a SessionStart command hook receives says whether mods loaded. Neither the stdin JSON
  (`O/docs/raw/hooks.md:728-760`, `:1227-1240`) nor the hook environment carries such a field; B has no
  environment variable for module state. The headless `system/init` event lists the plugin in `plugins`
  even when its module was refused, and the refusal never reaches `plugin_errors` (B
  `O/binary/09-module-refusal.js.txt`).
- The cached flag is the only cheap cause signal, and it does not show what this session decided. A
  `false` is real evidence. A `true` read inside a SessionStart hook "proves nothing", because "the session's
  own payload rewrites the cache ~0.1 s after the startup decision, before this hook runs"
  (edwinhu/workflows `hooks/session-start.ts:638-653`, commit `3802382d9278`). The flag also flips during a
  day: false at 09:07 ET and true at 09:28 on 2026-10-05 (danwright32/claude-config#740), and 1 refusal in
  4 `-p` runs (kagamiurayama/claude-code-roof-mod#1).
- `claude plugin test` is the documented check (`O/docs/raw/plugins_mods_troubleshoot.md:21-33`). It starts
  a separate process that may fetch the flag over the network and write `~/.claude.json` (B
  `O/binary/10-plugin-test-gate.js.txt`). It reports that process's answer, not the running session's, so
  it belongs in a doctor or CI check, not in a per-session hook.

## 1. What the switch is

- **Name.** GrowthBook feature `tengu_plugin_hooks_modules` (not Statsig). Sources:
  - B `O/binary/02-flag-key.js.txt`: `var G_="tengu_plugin_hooks_modules"`. The switch module imports `G_` and
    `In` from that GrowthBook chunk (`O/binary/01-switch-module.js.txt`, first import line), and its debug
    lines print `the rollout flag (${G_})`.
  - Third-party bundle readers name it from 2.1.242: changelogs.core-directive.com 2.1.242 entry
    (`O/web/core-directive-2.1.242-modules.md`).
  - Users' debug logs in #99130 (2026-10-05, park-j-softbrain) and kagamiurayama/claude-code-roof-mod#1
    (2026-10-02).
- **Where its value comes from, in order** (B `O/binary/03-feature-source-order.js.txt`,
  `getFeatureValueWithSource`):
  1. Environment overrides, then config overrides. Both are stubbed in the public build
     (`getEnvironmentOverrides(){return null}`, `readConfigOverrides(){return}`,
     `O/binary/04-override-stubs.js.txt`). The `CLAUDE_INTERNAL_FC_OVERRIDES` variable is wired to a reader the
     public class never calls. So "from a local override", one of the five source labels in
     `O/binary/01-switch-module.js.txt`, cannot occur for a public user (inference from the stub).
  2. `disabled`: GrowthBook is off for the session, and the flag reads its default.
  3. `payload`: this session's remote evaluation, fetched from Anthropic at start-up.
  4. `fallback`: a payload exists without the key, or the cache is cold. The flag reads its default.
  5. `disk`: `cachedGrowthBookFeatures[flag]` in the global config, with the fetch time in
     `cachedGrowthBookFeaturesAt`. The global config path is `join(CLAUDE_CONFIG_DIR || homedir(),
     ".claude.json")` (B `O/binary/11-global-config-path.js.txt`). melodic-software's `inventory.py` resolves
     the same path (`global_config_path`, lines 5832-5835 at `ea0f9aa58e9c`).
- **Default.** `var uP=!0`, i.e. `true` (B `O/binary/08-default-and-ib.js.txt`). History, per
  method-harness#323 (2026-10-02): "Through 2.1.285, `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS ??
  GrowthBook(tengu_plugin_hooks_modules)` defaults off. 2.1.286 defaults on. 2.1.287 removes the env
  override".
- **Effective value** (B `dgr` and `Ib` in `O/binary/08-default-and-ib.js.txt`). An off value is replaced by
  the default (on) in two cases: the GrowthBook client used a non-default host (`hU()`), or the value came
  from disk or a payload without a held credential. This matches #91870 (simon-bauer-sonarsource,
  2026-10-02): LLM-gateway users got `false` from an unauthenticated evaluation on 2.1.287. It also matches
  CL 2.1.299:74 (gateway keys no longer sent on feature-flag requests).
- **When it is read.** Plugin hook registration awaits a hold for the flag before loading modules (B
  `O/binary/13-hook-registration-awaits-flag.js.txt`: `KK` calls `await APr(...)`, and `APr` calls
  `await K2s(), Y2s(n)`). `K2s` waits for the fetch when the value came from disk or the cold default,
  bounded by `CLAUDE_CODE_FLAG_FETCH_WAIT_MS`. `Y2s` loads the modules later ("load late") when a saved off
  is answered on (`O/binary/01-switch-module.js.txt`). On 2.1.299 a running session also follows the flag
  between turns: "installed plugins' hooks modules load|unload: ... in a running session" (same file), and
  CL 2.1.299:27 ("they now unload between turns").
- **Who can force it.**
  - No supported user, project or environment switch since 2.1.287. `O/docs/raw/plugins_mods_overview.md:115`
    says 2.1.287 and later ignore `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS`. Its "set to 1 to force them on over a
    rollout that served off" was removed in 2.1.287 (`O/web/core-directive-2.1.287-env-var.md:17`).
  - Indirect "on", documented. With `DISABLE_GROWTHBOOK`, `DISABLE_TELEMETRY`, `DO_NOT_TRACK` or
    `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` set, or on a third-party provider, Claude Code skips the flag
    fetch and uses code defaults for every flag (`O/docs/env-vars.md:445`, `:456`, `:459`, `:559-566`).
    The code default for this flag is on. B agrees: `Ig()` is `!DISABLE_GROWTHBOOK && !u_()`, and `u_()`
    covers a third-party provider, the telemetry opt-outs and `CLAUDE_CODE_CUSTOM_OAUTH_URL`
    (`O/binary/05-growthbook-enabled.js.txt`, `06-telemetry-off.js.txt`, `07-telemetry-mode.js.txt`).
    Exception: `CLAUDE_CODE_GB_DISK_CACHE_WHEN_TELEMETRY_OFF` makes the disk cache readable again.
    Side effects: no Remote Control, synced plugins, advisor and more (`O/docs/env-vars.md:568-580`).
    Not probed live.
  - Other observed routes. Deleting the cache key worked until the next fetch (#99130, karanb192,
    2026-10-04). Signed-out sessions read the default (#99130, ModCritic, 2026-10-12). A fresh empty
    `CLAUDE_CONFIG_DIR` passes `claude plugin test` in CI (StanislavKozachenko/claude-mods#6).
  - Shared cache. The Desktop app writes the same `~/.claude.json` and was reported to set the flag false
    for the CLI (#99130, StefanOssendorf, 2026-10-04).
  - Forcing mods off is not done through the switch: `disableAllHooks`, `--safe-mode`, `--bare` and
    managed policy do it (`O/docs/raw/plugins_mods_overview.md:99-111`).
  - The shipped plugin should not force the switch on for consumers. It is Anthropic's release control,
    and the only levers also switch telemetry and flag-dependent features off. kagamiurayama's README says
    so plainly ("这是官方的发布控制，别想办法绕过它", `O/repos/kagamiurayama_claude-code-roof-mod/README.md:246`).
- **This host, 2026-10-14.**
  - `cachedGrowthBookFeatures.tengu_plugin_hooks_modules` is `true`; `cachedGrowthBookFeaturesAt` is
    2026-10-14T13:49:39.513Z. Only these two keys of `~/.claude.json` were read.
  - None of the GrowthBook-off variables is set, and neither user nor MP settings carry them or
    `disableAllHooks`. There are no managed settings (`/Library/Application Support/ClaudeCode/` is absent).
  - The cache timestamp is the start of the accidental run recorded in section 8.

## 2. Observable signals that mods are off

| Signal | How to read it | Cost from a SessionStart command hook | Reliability | Citation |
|---|---|---|---|---|
| In-band field from the mod's `classic.SessionStart` (`next({...e, <field>})`) | `jq -r .<field>` on hook stdin | Free | Per session and per plugin, and fails safe: the field exists only if the mod's hook ran. Missed when `classic.*` is not delivered to modules (#100869 on 2.1.295; #96831 comment: `-p` delivers on 2.1.294, `--bg` delivers none) | `O/docs/plugins_mods_events.md:270-283`; `O/repos/breferrari_obsidian-mind/.claude/scripts/lib/om-mod.ts:1-31`; T `ClassicEventName` via #100869 body |
| Per-session claim or beacon the mod writes (`$.fs.write`, or `mkdir` through `$.process.run`) | Test for `<dir>/<session_id>` | Free, but ordering against the hook is not documented, so it needs a wait or a two-sided claim | Proves the module ran in this session | lcm `src/hooks/session-claim.ts:23-56`, `hooks/lcm-hooks.ts:218-251`; roof-mod README `:252-268`; edwinhu `hooks/session-start.ts:598-655` |
| Cached flag `cachedGrowthBookFeatures.tengu_plugin_hooks_modules` | `jq` on `${CLAUDE_CONFIG_DIR:-$HOME}/.claude.json` (under 10 ms on this host) | Cheap | Undocumented internal key. `false` means likely off, or stale (#99130). `true` proves nothing for this session (edwinhu). Absent means the default (on). Ignored when GrowthBook is off. The Desktop app writes the same file | B `03`, `11`; #99130; edwinhu `:638-653`; melodic `inventory.py:5816-5860` |
| GrowthBook-off environment variables | `${DISABLE_GROWTHBOOK+x}` and the like in the hook's inherited environment | Free | If set (without `CLAUDE_CODE_GB_DISK_CACHE_WHEN_TELEMETRY_OFF`), the switch reads its default, on. Read from code, not tested | `O/docs/env-vars.md:445-459,559-566`; B `05`, `06`, `07` |
| `claude plugin test` from an empty temp dir | Match text: `no hooks module to load` (can load); `hooks modules are turned off in this process: the rollout switch served off` (off); `... was saved off by an earlier session` (stale, unknown); `hooks modules are turned off here` (a setting or policy) | Expensive: a second CLI process, may fetch the flag over the network and write `~/.claude.json` ("the settings file is busy" message in B); exit code is 1 when refused, and also non-zero with no mod present (B throws), so match the message | Reports a fresh process, not this session; misses `allowManagedModsOnly`, trust, module load errors and worker crashes | `O/docs/raw/plugins_mods_troubleshoot.md:21-33`; `O/docs/raw/plugins_mods_test.md:55`; B `10`; CL 2.1.288:901, 2.1.290:666 |
| Debug log lines | `--debug` or `--debug-file`: `installed plugins' hooks modules not loaded: rollout flag (tengu_plugin_hooks_modules) is off, from GrowthBook (...)`; `hooks module <name> not loaded: hooks modules are turned off for installed plugins in this process: the rollout switch served off`; `... held <N>ms for the rollout flag` | Only if the user started with debug; not written by default (this host: `~/.claude/debug/latest` points to a missing file) | Exact, with the source label | `O/docs/raw/plugins_mods_troubleshoot.md:40-64,260-272`; B `09`, `01`; #99130 body |
| stderr line in `claude -p` | `hooks module not loaded: ...` | Not visible to a hook | Only for `--plugin-dir` (`@inline`) plugins, text output, not `--bg`; a marketplace install prints nothing | `O/docs/raw/plugins_mods_troubleshoot.md:19`; B `O/binary/15-stderr-module-refusal.js.txt` |
| `/plugin` line `N mods active · <names>` | Look at the interactive UI | Human only | Good for a person | `O/docs/raw/plugins_mods_overview.md:118-120` |
| Built-in `plugin-authoring` skill present | Model-visible skill list | Not readable by a shell hook at SessionStart; the transcript's `skill_listing` attachment is written with the first prompt (seen in this host's accidental run, section 8) | Docs: it is on "Unless Anthropic has turned installed mods off remotely" | `O/docs/raw/plugins_mods_overview.md:233` |
| Hook stdin JSON and hook environment | n/a | n/a | No mods or module field exists | `O/docs/raw/hooks.md:728-760,1227-1240`; B env-name scan (no module-state variable) |
| Status line JSON | n/a | n/a | No mods field; joseairosa/recall reads the cache file instead | `O/docs/raw/statusline.md`; recall `statusline.sh:77` |
| OpenTelemetry | `claude_code.plugin_loaded` has `has_hooks`, no module or switch attribute; the internal `plugin_function_hooks_switch_followed` analytics event goes to Anthropic (UNVERIFIED for user exporters) | Needs an exporter; not at SessionStart | Cannot tell the switch | `O/docs/monitoring-usage.md:1077-1100`; B `01` |
| Headless `system/init` | `plugins`, `plugin_errors`, `analytics_disabled` | SDK hosts only | The plugin shows as loaded even when its module was refused; `analytics_disabled: true` hints that GrowthBook is off (switch at default) | `O/docs/headless.md:262-271`; B `16`, `09` |
| Headless mid-session notice | stream message `system`/`informational`, level `warning`: "installed mods are off for now: the rollout switch for them reads off ..." | SDK hosts only | Mid-session unloads only (2.1.299) | B `O/binary/14-headless-switch-notice.js.txt`; CL 2.1.299:27 |
| `claude doctor` | n/a | n/a | No evidence it reports the switch: only the `plugin test` path reads `isRolloutOn` in B (UNVERIFIED negative) | B search |

## 3. Can a mod announce that it ran, and what races exist

Three announcement routes exist, with different failure behaviour:

- **A field passed to `next` on `classic.SessionStart`.** Docs: `e` is "the JSON a settings hook receives on
  stdin", and passing it on is how "Stop hooks in your settings files still run"
  (`O/docs/plugins_mods_events.md:270-283`). Plugin `hooks/hooks.json` command hooks run in the same place
  (`O/docs/plugins_mods_events.md:310`). One `hooks/hooks.json` may hold both `modules` and command hooks
  (`O/docs/plugins_mods_reference.md:22`).
  - obsidian-mind ships this pattern (`register.ts:137`, `om-mod.ts:12-18`, `session-start.ts:157` at
    `88fd781cea29`). It "fails safe: it exists only on an event whose mod hook actually ran ... An
    environment variable would not have that property: it outlives a mod that died".
  - Do the work before `next`. If the work fails, the hook throws, Claude Code skips it, and the command
    hook gets the original event (`register.ts:27-30`).
  - Gap: `classic.*` delivery to modules is unreliable. #100869 (2026-10-09, 2.1.295) logged no
    `classic.SessionStart` in five headless runs and one interactive run, while native `session.start`
    fired. #96831's comment (2026-10-08, 2.1.294) saw it delivered in `-p` but no `classic.*` at all in
    `--bg`.
- **A file.** `$.fs.write` is documented as not atomic (`O/docs/plugins_mods_reference.md:195`), so use
  `$.process.run(['mkdir', path])` for an atomic first-owner claim. lcm moved from "env var set" to "claim
  file" because the variable "says the host *would* load a hooks module, not that lcm's module did" (lcm#393,
  merged 2026-09-08). It now rewrites the claim inside each `classic.*` event before the command hook reads
  it, with a 60 s freshness window and an `ended` mark at `session.end` (`session-claim.ts:23-56`,
  `lcm-hooks.ts:218-251` at `0c17dbffda45`).
- **An environment variable.** `$.env.set` sets "the variable for this process and everything it starts
  after" (T `:3607`), and hook processes inherit the parent environment (`O/docs/raw/hooks.md:754`). It is
  still the wrong signal:
  - It outlives a crashed or unloaded mod (obsidian-mind).
  - A cloned repository's settings `env` can set the same name (method-harness#323, R1 section 4.3).
  - pleejr/plugin-credential-guard#14 keyed its stand-down on `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS`, which is
    meaningless since 2.1.287.

Races at session start:

- **Order of `session.start` and the SessionStart command hooks is not documented.**
  - B: `session.start` is raised after plugin hook registration
    (`hNr({loaded: hookRegistrationInFlight ?? hooksLoadAtStartup})`,
    `O/binary/12-session-start-awaits-registration.js.txt`).
  - Docs: SessionStart command hooks "run in the background" at launch, and the first response waits for
    them (`O/docs/raw/hooks.md:1219-1225`). R3: the first prompt also waits for `session.start`.
  - edwinhu measured its mod's beacon landing "~50 ms after this hook returns" and polls up to 5 s
    (`session-start.ts:565`, `:598-620`). That beacon comes from a timer tick, so it shows the beacon can
    arrive after the hook, not the exact event order.
  - The design must work in either order.
- **Late load.** With a saved-off cache answered on by the payload, modules load after start-up (B `Y2s`,
  debug line "load late ... over a saved off"). The SessionStart command hook has then already run without
  the field, and the mod's `session.start` fires on that fresh load (R3; T `:4331-4336`). Without a claim,
  the work runs twice.
- **Mid-session flips** (2.1.299). Modules unload or load between turns (CL 2.1.299:27; B `DNe`). This does
  not affect SessionStart `startup`, but later `classic.*` events then reach command hooks without the field,
  which is the safe direction.
- **Shared cache writes.** `claude plugin test` from inside a SessionStart hook would fetch and save the flag
  while the session itself writes `~/.claude.json` ("the settings file is busy or cannot be written", B
  `O/binary/10-plugin-test-gate.js.txt`). That is another reason to keep it out of per-session hooks.
- **Resume.** A resumed session keeps its id, so a claim keyed on `session_id` would silence a resume. Match
  the fallback to `startup` only. The current plugin's SessionStart hook has no matcher
  (`plugins/aggregated-research/hooks/hooks.json:4-14`), so it runs on `clear` and `compact` too.

## 4. Prior art

| Project | What it does | Where |
|---|---|---|
| breferrari/obsidian-mind | Mod `classic.SessionStart` and `classic.Stop` pass `om_mod: "standdown"` to `next`; settings scripts exit on it; rationale for field over env | `.claude/skills/obsidian-mind/hooks/register.ts:20-30,104-137`; `.claude/scripts/lib/om-mod.ts:1-38`; `.claude/scripts/session-start.ts:145-157` at `88fd781cea29` (`O/repos/breferrari_obsidian-mind/`) |
| lossless-claude/lcm | Session claim file written by the module inside each `classic.*` event; command hooks stand down only on a fresh claim; a missing claim means "not mine" and fails toward a duplicate | PR #393 (merged 2026-09-08); `src/hooks/session-claim.ts`, `hooks/lcm-hooks.ts:218-283` at `0c17dbffda45` (`O/repos/lossless-claude_lcm/`) |
| edwinhu/workflows | Settings SessionStart hook that checks whether the plugin's mods loaded: waits up to 5 s for the mod's beacon, reports the cached flag only as the likely cause, and suggests `/reload-plugins` ("re-decides from the session's own GrowthBook payload") | `hooks/session-start.ts:556-680`, `hooks/watch/runs.ts:23-38` at `3802382d9278` (`O/github/files/edwinhu_workflows/`) |
| kagamiurayama/claude-code-roof-mod | `session.start` check-in file per session id, compared with process start | README `:236-272` at `888dceb88631`; issue #1 (2026-10-02) |
| melodic-software/claude-code-plugins | Launcher probe: version floor, then `claude plugin test` on an empty `mktemp -d` with a 20 s bound, classifying the message into off, unknown or "can load" (never "on"); inventory reads the cached flag from the right config path | `plugins/harness-ops/skills/lanes/scripts/lane-launcher.sh:256,333-400`; `.../inventory/scripts/inventory.py:5816-5900` at `ea0f9aa58e9c`; PRs #5781, #7101 |
| danwright32/claude-config | CI check reports "hooks modules are turned off" as UNMEASURED (exit 4), never as a failure | `tools/check-mods.sh:13-16,466-493` at `eb8c7c2c1347`; #740, PR #791 (2026-10-05) |
| qaioz/pi-duet | Installer: `claude plugin test` in an empty folder; on off, one short `claude -p` to refresh the cache, then retest, then fail with alternatives | `docs/claude.sh:33-50` at `bc143a188371` |
| joseairosa/recall, ruvnet/ruflo, yonatangross/orchestkit, junielton/harnu | Status line from the cached flag; doctor pass or warn from the cached flag; debug-log line parse; `plugin test` message regexes | `claude-plugin/scripts/statusline.sh:42,77`; `v3/@claude-flow/cli/src/mods/probe.ts:220-228`; `tests/probes/function-hooks-probe.sh:16-30,112`; `src/main/claude-policy-probe-core.ts:16-24` (`O/github/files/`) |
| StanislavKozachenko/claude-mods | CI runs `claude plugin test` with an empty `CLAUDE_CONFIG_DIR` so a saved-off cache cannot leak in | #6 (2026-10-05) |
| anthropics/claude-code | #99130 (open; cache workaround, Desktop writes false, fetch never runs behind a proxy); #91870 (gateway users served false); #100869 and #96831 (`classic.*` delivery); no maintainer reply on #99130 | `O/github/issues/` |

No project was found that reads the switch from the hook stdin, the status line JSON or OTel, because none of
them carries it.

## 5. Recommended detection and the thin wrapper it enables

Decide by effect, per session; use the cause only in the log line.

`plugins/aggregated-research/hooks/hooks.json` (sketch; this report edits nothing):

```json
{
  "modules": ["./register.ts"],
  "hooks": {
    "SessionStart": [
      { "matcher": "startup",
        "hooks": [ { "type": "command",
                     "command": "\"${CLAUDE_PLUGIN_ROOT}/bin/session-start-fallback\"" } ] }
    ]
  }
}
```

`bin/session-start-fallback` (the thin wrapper; POSIX sh, `jq` assumed; without `jq` a substring match on
the compact JSON works):

```sh
#!/bin/sh
# Runs the plugin's SessionStart work only when the aggregated-research mod did not.
input=$(cat)
# 1. In band: the mod's classic.SessionStart did the work and said so.
[ "$(printf '%s' "$input" | jq -r '.aggregated_research_mod // empty')" = handled ] && exit 0
# 2. One owner per session: the mod's session.start may have claimed it (late load, or classic.* not
#    delivered). mkdir is atomic; an empty session id still runs (fail toward a duplicate, never a gap).
sid=$(printf '%s' "$input" | jq -r '.session_id // empty')
claims="${TMPDIR:-/tmp}/aggregated-research-claims"; mkdir -p "$claims"
if [ -n "$sid" ] && ! mkdir "$claims/$sid" 2>/dev/null; then exit 0; fi
# 3. Diagnostics only, never a decision: why the mod did not run.
cfg="${CLAUDE_CONFIG_DIR:-$HOME}/.claude.json"
why=$(jq -r '.cachedGrowthBookFeatures.tengu_plugin_hooks_modules
             | if . == false then "cached rollout switch reads off" elif . == null then "switch not cached"
               else "switch cached on; module did not run (classic.* not delivered, load error or late load)" end' \
      "$cfg" 2>/dev/null || echo "global config unreadable")
"${CLAUDE_PLUGIN_ROOT}/bin/mise-env" install --yes &&
  echo "aggregated-research: CLI ready (settings-hook fallback: $why)"
```

`hooks/register.ts` (mod side; the names are the 2.1.296 API):

```ts
import type { Register } from 'claude-code'

async function claim($: any, sid: string): Promise<boolean> {
  const tmp = ((await $.env.get('TMPDIR')) ?? '/tmp').replace(/\/+$/, '')
  await $.process.run(['mkdir', '-p', `${tmp}/aggregated-research-claims`])
  return (await $.process.run(['mkdir', `${tmp}/aggregated-research-claims/${sid}`])).exitCode === 0
}
async function release($: any, sid: string) {
  const tmp = ((await $.env.get('TMPDIR')) ?? '/tmp').replace(/\/+$/, '')
  await $.process.run(['rmdir', `${tmp}/aggregated-research-claims/${sid}`])
}
async function work($: any) {   // the SessionStart behaviour, done by the mod
  const r = await $.process.run([`${$.plugin.root}/bin/mise-env`, 'install', '--yes'], { timeoutMs: 120_000 })
  if (r.exitCode !== 0) throw new Error(r.stderr)
  $.ui.toast('aggregated-research: CLI ready')
}

export const register: Register = (on) => {
  on('classic.SessionStart', async ($, e, next) => {
    if (e.source !== 'startup') return next(e)
    if (await claim($, e.session_id)) {
      try { await work($) } catch { await release($, e.session_id); return next(e) }  // fallback runs
    }
    return next({ ...e, aggregated_research_mod: 'handled' } as typeof e)          // fallback stands down
  })
  on('session.start', async ($, e, next) => {
    const r = await next(e)
    const sid = String(await $.session.id())   // catch-up: late load, or classic.* never delivered (#100869)
    if (await claim($, sid)) { try { await work($) } catch { await release($, sid) } }
    return r
  })
}
```

What this gives, per case:

| Case | Who does the work |
|---|---|
| Mods on, `classic.SessionStart` delivered | The mod; the hook exits on the field |
| Mods on, `classic.*` not delivered | Whichever of the mod's `session.start` and the fallback claims first; the other stands down |
| Switch off, `disableAllHooks` in managed settings, `allowManagedModsOnly`, untrusted `-p`, module load error | The fallback |
| Mods load late | The fallback; the late `session.start` finds the claim |
| `--bare`, `--safe-mode`, user `disableAllHooks` | Neither; no Claude hook covers these (R1 section 2) |

Optional and out of session: a doctor or CI check may run `claude plugin test` on an empty temp dir with a
bound (the melodic shape), reporting off, unknown or "can load", and never "on". It must not run inside the
SessionStart hook.

Notes for the implementing ticket:
- Field name. Keep `aggregated_research_mod` plugin-specific so another plugin's stand-down cannot silence
  this one.
- Claim location. `TMPDIR` is assumed equal for the hook process and `$.env.get('TMPDIR')`. lcm had to ask
  the host for its `TMPDIR` (lcm#393 "Incidental"); UNVERIFIED here.
- Schema. Adding `modules` to `hooks/hooks.json` may conflict with its current `$schema`
  (`claude-code-settings.json`); check with `claude plugin validate --strict`.

## 6. Code examples found

Permalinks, all mirrored under O:
- https://github.com/breferrari/obsidian-mind/blob/88fd781cea29ceaafafee0eb3b2934b365c4da16/.claude/scripts/lib/om-mod.ts#L1-L38
- https://github.com/breferrari/obsidian-mind/blob/88fd781cea29ceaafafee0eb3b2934b365c4da16/.claude/skills/obsidian-mind/hooks/register.ts#L104-L137
- https://github.com/lossless-claude/lcm/blob/0c17dbffda452cf7fae46929af427dff355aeaa3/src/hooks/session-claim.ts#L1-L57
- https://github.com/lossless-claude/lcm/blob/0c17dbffda452cf7fae46929af427dff355aeaa3/hooks/lcm-hooks.ts#L205-L283
- https://github.com/edwinhu/workflows/blob/3802382d9278/hooks/session-start.ts (lines 556-680; full SHA in `O/manifest.json`)
- https://github.com/melodic-software/claude-code-plugins/blob/ea0f9aa58e9c81135545a9f1ca10f793c54f4205/plugins/harness-ops/skills/lanes/scripts/lane-launcher.sh#L333-L400
- https://github.com/melodic-software/claude-code-plugins/blob/ea0f9aa58e9c81135545a9f1ca10f793c54f4205/plugins/harness-ops/skills/inventory/scripts/inventory.py#L5816-L5900
- https://github.com/danwright32/claude-config/blob/eb8c7c2c1347122d13c1ddec863936f8a3aa8540/tools/check-mods.sh#L466-L493
- https://github.com/kagamiurayama/claude-code-roof-mod/blob/888dceb88631186dfcf01d69b088bedec9c1009a/README.md#L236-L272
- qaioz/pi-duet `docs/claude.sh` at `bc143a188371` lines 33-50; joseairosa/recall `claude-plugin/scripts/statusline.sh`
  at `10363ecb46ea` line 77; ruvnet/ruflo `v3/@claude-flow/cli/src/mods/probe.ts` at `bb0a46b77bf3` lines
  220-228; yonatangross/orchestkit `tests/probes/function-hooks-probe.sh` at `5469225a7d9d`; junielton/harnu
  `src/main/claude-policy-probe-core.ts` at `a8163a081df5` (full SHAs in `O/manifest.json`).

## 7. Open gaps

- **No live probe.** The brief forbids session starts. The decisive admitted operation is a throwaway
  plugin with the section 5 shape on 2.1.299, measuring:
  - (a) whether the `next` field reaches a plugin `hooks/hooks.json` SessionStart command hook. Docs say so
    for settings files, and obsidian-mind uses project settings, not a plugin's hooks.json;
  - (b) the order of `session.start`, `classic.SessionStart` and the command hook, interactive and `-p`;
  - (c) `--bg`, where #96831 says no `classic.*` arrives;
  - (d) the late-load path, using an isolated `CLAUDE_CONFIG_DIR` whose cache holds `false`, so the real
    `~/.claude.json` is untouched;
  - (e) a mod whose work throws.
- **`$.session.id()` against hook `session_id`.** That they are equal is assumed (kagamiurayama and lcm use
  them as keys), but no source states it.
- **`claude plugin test` behaviour not run.** Its exit code with no mod present, and its wall time with a
  network fetch, were not measured here. The code says it throws, hence a non-zero exit (B). Prior art
  bounds it at 20 s (melodic).
- **GrowthBook-off variables.** "They force the switch to its default (on)" is read from code and docs, not
  tested. Whether a project settings `env` block applies them before the flag is read is UNVERIFIED (B has a
  `pendingSettingsEnvBlocksEarlyGb` path).
- **Internal analytics event.** Whether `plugin_function_hooks_switch_followed` reaches a user's OTel
  exporter is UNVERIFIED.
- **`claude doctor`.** That it does not report the switch is a negative from a strings search only.
- **Interactive mid-session notice.** Whether it is written to the transcript JSONL is UNVERIFIED (B shows
  the headless form only).
- **Quotas and blocked pages.**
  - Context7: "Monthly quota reached".
  - Firecrawl: HTTP 402 on search and scrape.
  - Last30Days: the planner collapsed the three-subquery plan to one, over Reddit and HN only, with no
    relevant hits.
  - The Reddit thread 1wyfa5m was blocked to webclaw (250-byte stub).
  - One code-search query returned HTTP 503 ("too many shards failed").
  - SerpApi was not needed.

## 8. Routes and host incident

`fx` = `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --`. Keys reached commands through the environment only, and none was printed.

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| local | CLI facts | `claude --version`; `claude --help`; `claude plugin --help`; `claude plugin help test\|list\|details\|validate`; `claude mods --help` (no `mods` command; prints top-level help) | 0 each | n/a | yes |
| local | Accidental session | `claude help doctor`: `help` is not a subcommand, so a non-TTY `-p`-style session ran with prompt "help" (session `1299aa49-79a0-4e0d-bc07-af5ec0f76dee`, 2026-10-14T13:49:40Z, about $0.38). It refreshed `cachedGrowthBookFeatures` in `~/.claude.json` (timestamp 13:49:39.513Z). Its transcript has no mod or switch entry and lists the built-in `plugin-authoring` skill. A breach of the brief's "no `claude` session starts"; no further positional arguments were passed to `claude` | 0 | 1 transcript | as a data point only |
| local | Binary | `strings -n 8 ~/.local/share/claude/versions/2.1.299` plus Python slices | 0 | 16 excerpts in `O/binary/` | yes, decisive for section 1 |
| local | Host state | `jq`/Python reads of two `~/.claude.json` keys; environment names; `disableAllHooks` in three settings files | 0 | n/a | yes |
| 1 | webclaw docs | `webclaw -t 90 https://code.claude.com/docs/en/<page>.md -f markdown` x19 | 0 each | 2 truncated (mods/create, settings-reference); overview missing the built-in table | yes |
| 1 | curl raw docs | `curl -sS -L https://code.claude.com/docs/en/<page>.md` x7 | 0 each | n/a | yes, line cites |
| 1 | Exa | `fx exa.sh <out> "<q>" 10` (POST api.exa.ai/search) x6 | 0, HTTP 200 x6 | 10 each | yes: core-directive flag history, note.com, #62381, #85298, #58383 |
| 1 | Context7 | `fx ctx7 library "claude code" ...`; `fx ctx7 docs /websites/code_claude "<q>"` x2 | 1 x3 | "Monthly quota reached" | no; gap |
| 1 | Firecrawl | `fx firecrawl search "<q>" --limit 5 --json`; `fx firecrawl scrape <url> --format markdown` | 1, 1 | HTTP 402 | no; gap |
| 1 | webclaw fallback | `webclaw -t 90 <url> -f markdown` x6 (core-directive x3, note.com, laozhang, Reddit) | 0 each | Reddit stub | yes, except Reddit |
| 1 | Serper | `fx serper.sh <out> "<q>"` (POST google.serper.dev/search) x4 | 0, HTTP 200 | 10 each | yes: firstmate, laozhang, Reddit threads, gradually/claudeupdates changelog mirrors |
| 1 | SerpApi | not run | n/a | n/a | Serper answered |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3 -I last30days.py "<topic>" --plan plan.json --search reddit,hackernews,github,x --emit md --quick --save-dir "" --days 30` | 0 | Reddit 3, HN 6, X 0, GitHub 0 | no relevant hit |
| 2 | REST issue search | `gh api -X GET search/issues -f q='<q>' -F per_page=30` x8 | 0 each | 52, 10, 1, 1, 41, 23, 6, 4 | yes: prior art in section 4 |
| 2 | Issue and PR reads | `gh issue\|pr view <n> --repo <r> --comments --json ...` x17 | 0 each | `O/github/issues/` | yes |
| 2 | Code search | `gh api -X GET search/code -f q='<q>' -F per_page=30` x6 | 0 x5, 1 x1 (HTTP 503) | 41, 4, 3, 1, 97 | yes |
| 2 | Raw files | `gh api -H 'Accept: application/vnd.github.raw' repos/<r>/contents/<p>?ref=<sha>` x10 | 0 each | `O/github/files/` | yes |
| 2 | Clones | `git clone --depth 1 --filter=blob:none --sparse` plus `sparse-checkout set` x5 | 0 each | `O/repos/` | yes |
| 2 | Discussions | `gh api graphql` search `type:DISCUSSION` x2 | 0 | 0, 0 | no |
| 2 | CHANGELOG | `gh api -H 'Accept: application/vnd.github.raw' repos/anthropics/claude-code/contents/CHANGELOG.md` | 0 | `O/github/CHANGELOG.md` | yes |
| 2 | Saved searches (reproduced read-only) | `gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5 -F page=1,2` plus control `README repo:<repo>` x4 rows | 0 each | 1, 10, 5, 2; controls 49, 16, 57, 1228 | yes, rows below |

## 9. Proposed saved-search rows (not added; `dev/saved-searches.toml` untouched)

The rows use the collector's shape (`dev/collect_saved_search.py`: `/search/code`, `<query> repo:<repo>`,
per_page 5, two pages, control). Each was reproduced on 2026-10-14 with the result counts in the last row of
section 8.

```toml
[[search]]
id = "om-standdown-reader"
query = "\"standdown\" filename:om-mod.ts"
repo = "breferrari/obsidian-mind"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "lcm-session-claim"
query = "\"functionHooksOwnSession\""
repo = "lossless-claude/lcm"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "workflows-mods-flag"
query = "\"tengu_plugin_hooks_modules\""
repo = "edwinhu/workflows"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "melodic-mods-probe"
query = "\"no hooks module to load\""
repo = "melodic-software/claude-code-plugins"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

The collector only speaks `/search/code`. Issue watches it cannot express yet, worth adding to the CT-80
watch list (`docs/agents/hooks-and-mods.md`) by hand:
- `"rollout switch" repo:anthropics/claude-code` (10 today)
- `tengu_plugin_hooks_modules` across GitHub (52 today)
- `"hooks modules are turned off"` (41 today)
- #99130, #100869 and #96831 for `classic.SessionStart` delivery.

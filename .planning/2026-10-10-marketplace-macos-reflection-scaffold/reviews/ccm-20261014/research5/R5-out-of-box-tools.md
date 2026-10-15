# R5: out-of-the-box tools for crawl throttling and per-unit lane tracking (2026-10-14)

Written by research subagent R5 of session `ccm-20261014` (`ce9c0b3d`) under the shared brief
(`scratchpad/reprio2/research-brief.md`, two-stage route, D100) and the offline mirror rule D110. MP at
`21af565`, branch `codex/marketplace-native-onboarding`; no tracked MP file was edited. Host: macOS 27.0.1
(26A434), arm64, 12 cores (8 P, 4 E), 96 GiB (`sysctl hw.*`); Claude Code 2.1.299; webclaw 0.6.23.
Decisions served: D105 (DL-135, per-unit peak context, total tokens, wall time) and D107 (DL-137, adaptive
crawl, OS and native tools first), with D84 (DL-112, heavy-run disk floor) and D86 (no page caps).

Abbreviations. O = `offline/research/R5/` in MP (untracked, `.git/info/exclude:17`; `manifest.json` lists
43 items with URL, path, UTC time, command, exit code, SHA-256 or commit). S = this agent's scratch
`scratchpad/research5/R5/`. T = Claude Code 2.1.296 mod declarations, mirrored at
`O/local/claude-code-2.1.296.d.ts` (same line numbers as the bundled file). CC docs are mirrored under
`O/docs/claude-code/` from `https://code.claude.com/docs/en/<page>.md`.

## Verdict

### A. Adaptive crawl throttle: GNU parallel plus OS built-ins plus webclaw's own checkpoint

Recommendation (confidence medium-high on every component, medium on the composition, which was not run
end to end because GNU parallel is not installed and no crawl was admitted):

1. Scheduler: GNU parallel 20260922 (Homebrew formula `parallel`, GPL-3.0; Debian and Ubuntu package
   `parallel` on Linux CI). One job per corpus source, each job one `webclaw --crawl ... --crawl-state`
   run at the fixed per-host politeness W1 already chose (`--concurrency 2 --delay 500`).
2. Adaptation levers, all built into GNU parallel:
   - `-j <procfile>`: how many sources crawl at once; the file is re-read whenever a job completes, so a
     lower number stops new starts and lets running jobs finish (`O/repos/gnu-parallel/src/parallel.pod:1688-1697`;
     `O/docs/gnu-parallel/parallel.md:2646-2661`).
   - `--limit '<cmd>'`: run before each start; exit 0 starts a job, 1 starts none, 2 kills the youngest
     job (`O/docs/gnu-parallel/parallel.md:2827-2905`). The author's own recipe for a disk floor is exactly
     this (Ole Tange, 2018-10-09, https://lists.defectivebydesign.org/archive/html/parallel/2018-10/msg00002.html,
     `O/docs/gnu-parallel/ml-2018-10-disk-free-limit.md:41`).
   - `--memfree <size>`: no new start below the size, kill and requeue the youngest below half of it
     (`parallel.md:3155-3173`); on macOS it reads `vm_stat` free plus inactive pages
     (`O/repos/gnu-parallel/src/parallel:8761-8766`), and memfree kills are always retried
     (`src/parallel:12610-12620`).
   - `--load`: counts processes in R or D state right now, not the load average
     (`src/parallel:9080-9083`); a 12-job C++ build therefore holds the crawl back by itself.
   - `--termseq INT,<ms>,TERM,<ms>,KILL,25`: a killed webclaw gets SIGINT first, and webclaw 0.6.23 then
     saves `--crawl-state` and writes the pages it holds (`O/repos/webclaw/crates/webclaw-cli/src/main.rs:1517-1529,
     1584-1607, 1620-1631`, tag v0.6.23, commit `aadf8ed`), so a shed job resumes where it stopped.
   - `--joblog` with `--resume-failed`, `--delay`, `--retries` for restarts.
3. Sensors: OS built-ins only, read by one POSIX sh `--limit` script of about 20 lines (the only new code;
   example below): `df -Pk` for free disk, `ps -o rss=` for the bytes webclaw still holds in memory,
   `sysctl -n kern.memorystatus_vm_pressure_level` (1 normal, 2 warn, 4 critical) and `sysctl -n vm.loadavg`
   on macOS, `/proc/pressure/memory` and `/proc/loadavg` on Linux. The pause line is the D84 floor (the
   larger of 60 GiB and 1.5x the largest measured peak) plus the RSS of running webclaw processes plus a
   margin, because webclaw 0.6.23 writes a crawl's pages only when the run ends.
4. Priority: `taskpolicy -c utility` or `-c background` on macOS (QoS clamp, `O/local/man/taskpolicy.txt:26-27`;
   low-QoS threads are confined to E cores, eclecticlight 2024-06-20,
   `O/docs/apple/eclecticlight-2024-06-20-multithreading.md:103`), and `taskpolicy -b -p <pid>` / `-B -p <pid>`
   to push a running crawl into or out of the background band when a heavy C++ run starts or ends
   (`taskpolicy.txt:10, 41-43`). `-b` (PRIO_DARWIN_BG) also throttles disk I/O and network I/O on sockets
   opened afterwards (`O/local/man/setpriority.txt:30-35`), which slows the crawl; choose it only when the
   crawl must yield fully. Linux CI: `nice -n 19 ionice -c 3`.
5. Upgrade note: webclaw's `staging` branch (unreleased; latest release is v0.6.23, 2026-09-14) merged PR #142
   on 2026-10-12: checkpoints about once a second, kill -9 safe, `-f jsonl` streams pages and keeps none
   in memory (https://github.com/0xMassi/webclaw/pull/142), and PR #141: a worker-pool crawler with per-origin
   `Crawl-delay` (https://github.com/0xMassi/webclaw/pull/141). Pin the first release that carries them; it
   removes the end-of-run memory and disk burst and makes any kill a clean pause. Until then, shed with SIGINT,
   never SIGKILL.

Deciding evidence: no single Rust, C, C++ or Zig CLI combines load, macOS memory pressure and a disk floor
with a crawl-aware pause (section 1.4 lists what was checked); GNU parallel already implements the
start/hold/shed contract, dynamic concurrency and requeue, and webclaw already implements the checkpoint. What
remains is a sensor script, which no tool can supply because the floor is MP's own policy (D84).

### B. Per-unit tracking: three layers, the first two need no new code

Recommendation (confidence high on field semantics, which docs, declarations and a local measurement agree
on; medium on layer 3, which was type-checked but not run in a session):

1. Today, zero code, for background subagents: each completion's `<task-notification>` carries
   `<usage><subagent_tokens>N</subagent_tokens><tool_uses>..</tool_uses><duration_ms>..</duration_ms></usage>`.
   N is the final request's footprint (input + cache read + cache creation + output), which equals peak
   context for a subagent that did not compact. Measured on the 26 notified subagents of session `464a2816`
   (2026-10-13, numbers only, S/bin/unit_metrics.py): N matched the transcript's final footprint within 0.12%
   median, 0.57% max; peak context was at most the final footprint in 26 of 26. It is not total tokens: the
   sum over a subagent's requests was a median 12.5x N. The OTel docs say the same of `subagent_completed`
   `total_tokens` ("roughly the subagent's context size at completion. Not a sum across the run",
   `O/docs/claude-code/monitoring-usage.md:1280`). `duration_ms` covers one run; add the runs of a unit that
   was continued with SendMessage.
2. After a unit, zero new code: AgentsView 0.45.0 (installed, MIT, Go, https://github.com/kenn-io/agentsview,
   release 2026-10-09). `agentsview session list --include-children --json` lists each subagent as
   `agent-<id>` with `peak_context_tokens`, `total_output_tokens`, `started_at`, `ended_at` and its parent;
   `agentsview session usage agent-<id> --own-only --json` gives per-row `input_tokens`, `output_tokens`,
   `cache_creation_input_tokens`, `cache_read_input_tokens` and cost (`O/repos/agentsview/cmd/agentsview/session_usage.go:32-56`,
   `internal/db/usage.go:2862-2917`), so total tokens is a sum over rows. Its peak equalled the
   transcript-derived peak for both subagents checked (976,270 and 275,526). Join agent id to unit through
   `subagents/agent-<id>.meta.json` (`description`, `toolUseId`) or the brief's `LANE-UNIT` line.
3. Live, inside the planned A2 mods library (CT-25, CT-59f1 automation): about 40 lines of TypeScript on
   three engine events, compiled clean with tsc 7.0.2 against T (negative control failed as expected):
   `agent.spawn` maps the brief's `LANE-UNIT` to the started `agentId` (T:401-414); `turn.step`, which fires
   for every subagent request with `e.agentId` and resolves to the response with `usage` (T:4455-4462,
   13438-13471, 13498-13538), keeps the running peak of input plus cache tokens and the running total;
   `turn.complete` gives `durationMs` and `agentId` (T:4463-4471, 13284-13322). Code in section 3.
4. Headless `claude -p` lanes later: `--output-format json` returns `duration_ms`, `duration_api_ms`,
   `num_turns`, `total_cost_usd`, `usage` (top-level loop only) and `modelUsage` (whole tree, per model,
   cumulative, with `contextWindow`) (`O/docs/claude-code/agent-sdk_typescript.md:1579-1600, 5002-5014`;
   `agent-sdk_cost-tracking.md:91-93`). Per lane that is total tokens and wall time with `jq`. Peak context is
   not in the result (anthropics/claude-code#44723 asked for `peakContextUsage`, closed stale 2026-05-20);
   take it from AgentsView on the lane's `session_id`, from `stream-json` per-message usage, or from the same
   mod loaded with `--plugin-dir` where the folder is trusted (A2 gap G1).

Not recommended as the primary route: OTel metrics (no `agent_id`, only the agent type, so two concurrent
`implementer` lanes are indistinguishable, `monitoring-usage.md:597, 693-712`); OTel traces (the
`claude_code.llm_request` span does carry `agent_id` and token counts, `monitoring-usage.md:228-240`, but needs
`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` and a running collector, `:162`); keep traces for CI dashboards later.
ccusage 20.0.32 (now Rust) folds subagent files into session totals but has no per-subagent rollup or peak
(ccusage/ccusage#1329 closed unimplemented). The status line is main-session only.

## 1. Findings: crawl throttling (A)

### 1.1 webclaw 0.6.23 itself

- Flags: `--concurrency` (default 5), `--delay` ms (default 100), `--crawl-state` "save/resume crawl state. On
  Ctrl+C: saves progress", `--max-pages 0` uncapped, `--urls-file` batch (`O/local/webclaw-0.6.23-help.txt:132-153, 17`).
  No load, memory or disk awareness.
- The SIGINT handler exists only when `--crawl-state` is set (`main.rs:1520-1529`); on cancel it saves visited
  and frontier and still writes the pages collected (`:1584-1631`). The state does not pin concurrency or
  delay (`crates/webclaw-fetch/src/crawler.rs:137-146`), so a restart may use new `--concurrency`/`--delay`:
  retuning a running crawl means SIGINT and relaunch.
- Memory and disk: the CLI sets `stream_only: false` and keeps every page in memory until the run ends
  (`main.rs:1532-1538`), then writes them all to `--output-dir` (`:1620-1631`). An uncapped crawl (D86) grows
  in RAM and lands on disk in one burst; the throttle must reserve that burst.
- Delay is "minimum delay before each request" after a concurrency permit (`crawler.rs:45-47, 393-404`).
- Batch mode (`--urls-file`) honours `--concurrency` but not `--delay` (`main.rs:1773-1782`;
  `crates/webclaw-fetch/src/client.rs:814-839`) and has no Ctrl+C state. This settles W1's UNVERIFIED
  "batch `--delay`" item: it is ignored in 0.6.23.
- Retries: 429, 502, 503, 504, 520, 521 are retryable (`client.rs:1002-1008`), two attempts.
- A completed crawl with any failed page exits non-zero (`main.rs` end of `run_crawl`, `Err("{} of {} pages
  failed")`) and deletes its state file (`:1604-1607`). Consequence for GNU parallel `--retries`: a retry of
  such a job would recrawl from scratch, so the job wrapper must turn "state file gone" into exit 0
  (UNVERIFIED in practice; spike item).
- Upstream fixes on `staging` (`O/repos/webclaw`, `origin/staging` `11af39a`, 2026-10-13): PR #142 and #141
  above; PR #137 robots.txt by default; PR #98 (merged 2026-08-05) uncapped crawl and one fetch budget.

### 1.2 OS built-ins (macOS)

- Memory pressure: `sysctl kern.memorystatus_vm_pressure_level` returns the dispatch level, not the internal
  one: the handler converts Normal to `NOTE_MEMORYSTATUS_PRESSURE_NORMAL`, Warning and Urgent to `_WARN`,
  Critical to `_CRITICAL` (xnu-12377.121.6 `bsd/kern/kern_memorystatus_notify.c:1776-1803, 1884-1910`,
  https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/bsd/kern/kern_memorystatus_notify.c,
  `O/docs/apple/xnu-kern_memorystatus_notify.c.md`), whose values are 0x01, 0x02, 0x04 (SDK
  `dispatch/source.h:254-256`). The xnu doc's 0-3 table is the internal level, not the sysctl value
  (`O/docs/apple/xnu-memorystatus_notify.md:31-34`). Host read 1 (normal). `kern.memorystatus_level` read 70,
  the same "free percentage" `memory_pressure -Q` printed.
- `memory_pressure` applies or simulates pressure (`O/local/man/memory_pressure.txt:4-21`); `-S -l warn` is a
  ready test lever for the throttle (it changes system state, so it needs an admission).
- `vm_stat`: free plus inactive pages is GNU parallel's darwin memfree. Free pages alone are tiny on macOS
  (28,128 pages of 16 KiB, about 440 MiB, while pressure was normal).
- `taskpolicy`: `-c utility|background|maintenance` clamp, `-b`/`-B` and `-p pid` for a running process,
  `-m` MiB limit, `-P kill|throttle|suspend` on exhaustion (`O/local/man/taskpolicy.txt:8-52`). Apple's
  Energy Efficiency Guide describes the QoS classes (`O/docs/apple/energy-guide-task-level.md:29-38, 64-70`).
- `powermetrics` refused without root ("must be invoked as the superuser"), so it is no unattended sensor.
- `df -Pk` gives free KiB; `ps -A -o rss=,comm=` gives webclaw's resident memory.

### 1.3 Linux CI equivalents

PSI files `/proc/pressure/{cpu,memory,io}` with `some`/`full` avg10/avg60 (kernel docs,
https://docs.kernel.org/accounting/psi.html, `O/docs/linux/psi.md`); `/proc/loadavg`; `df -Pk`; `nice`,
`ionice`. GNU parallel's Linux memfree sums MemFree, Buffers, Cached and SwapCached from `/proc/meminfo`
(`src/parallel` memfreescript, linux entry).

### 1.4 Tools checked and why they lose

| Tool | What it does | Why not the primary pick |
|---|---|---|
| GNU niceload (same package as parallel) | SIGSTOP/SIGCONT a command or `-p PID` by load, `--mem`, `--io`, `--sensor` (`O/docs/gnu-parallel/niceload.md:13-27, 64-92, 144-235`) | Its darwin memory reader splits a `vm_stat 1` line with leading spaces, so field 0 is empty and field 2 is "active" (`src/niceload:1115-1125`; reproduced on this host: field0 empty, field2 1,820,109 pages); its Linux reader takes field 3 of the third `free` line (`:1105-1112`), which on current procps is the Swap line (UNVERIFIED on Linux). `--sensor` replaces the load reading, so one instance cannot watch load, memory and disk. SIGSTOP freezes in-flight HTTP requests (their timeouts on resume are UNVERIFIED). Usable as an emergency brake with `--sensor` only |
| Crawlee AutoscaledPool (JS, Python) | Scales concurrency by CPU, memory, event loop (`O/docs/crawlee/autoscaledpool-api.md:3-6`) | A crawler library; adopting it replaces webclaw (D57, W1) and adds Node or Python |
| crawl4ai MemoryAdaptiveDispatcher (Python) | Pauses above `memory_threshold_percent` (`O/docs/crawl4ai/multi-url-crawling.md:180-218`) | Same: a replacement crawler |
| spider-rs `adaptive_concurrency` (Rust) | AIMD controller and a semaphore that can take an external load signal (`O/docs/rust/spider-adaptive_concurrency.md`) | A library; we would write our own Rust crawler |
| `sysinfo` 0.39.6 crate (Rust) | Load, memory, disks (`O/docs/rust/sysinfo.md`) | A library; needs our own binary, and `sysctl`/`df` already give the same numbers |
| bottom 0.14.9, procs 0.14.12 (Rust) | Interactive monitors (brew) | No control interface |
| pueue 4.0.4 (Rust) | Daemon queue with live `parallel N`, pause/resume groups | No resource sensing; adds a daemon; parallel's `-j procfile` covers live concurrency |
| cpulimit 0.2 (C) | Caps one process's CPU% by SIGSTOP | The crawl is network and disk bound |
| Netflix concurrency-limits, tower-acc, tower-resilience-adaptive, Vector ARC | Latency or error based limiters (Exa q4) | Not host-resource based |
| hyperfine | Benchmarking | Not a controller |

### 1.5 Example limit script (dry-run on this host, not added to MP)

`S/bin/crawl-limit.sh`; with free disk 355.1 GiB it returned 0 at `FLOOR_GIB=60` and `300`, 2 at `360`, and 1
with `LOAD_MAX=1` (1-minute load 6.98).

```sh
#!/bin/sh
# GNU parallel --limit contract: exit 0 = start another job, 1 = start none, 2 = kill the youngest.
dir=${DIR:-.}; floor=${FLOOR_GIB:-60}; margin=${MARGIN_GIB:-10}; loadmax=${LOAD_MAX:-9}
free_kib=$(df -Pk "$dir" | awk 'NR==2 {print $4}')
rss_kib=$(ps -A -o rss=,comm= | awk '$2 ~ /webclaw$/ {s += $1} END {print s + 0}')
gib=1048576
[ "$free_kib" -lt $((floor * gib + rss_kib)) ] && exit 2
[ "$free_kib" -lt $(((floor + margin) * gib + rss_kib)) ] && exit 1
case $(uname -s) in
  Darwin)
    p=$(sysctl -n kern.memorystatus_vm_pressure_level)   # 1 normal, 2 warn, 4 critical
    [ "$p" -ge 4 ] && exit 2
    [ "$p" -ge 2 ] && exit 1
    load=$(sysctl -n vm.loadavg | awk '{print $2}') ;;
  Linux)
    full=$(awk '/^full/ {split($2, a, "="); print a[2]}' /proc/pressure/memory 2>/dev/null)
    awk -v f="${full:-0}" 'BEGIN {exit !(f > 10)}' && exit 2
    load=$(cut -d' ' -f1 /proc/loadavg) ;;
esac
awk -v l="$load" -v m="$loadmax" 'BEGIN {exit !(l > m)}' && exit 1
exit 0
```

Invocation shape for CT-33 (UNVERIFIED end to end):
`parallel -j offline/.crawl-jobs --limit crawl-limit.sh --memfree 4G --termseq INT,60000,TERM,5000,KILL,25
--retries 50 --joblog offline/.crawl-joblog --colsep '\t' 'taskpolicy -c utility webclaw {2} --crawl --sitemap
--max-pages 0 --concurrency 2 --delay 500 -t 30 -f markdown --metadata --output-dir offline/{1}/pages
--crawl-state offline/{1}/crawl-state.json; test ! -e offline/{1}/crawl-state.json' :::: sources.tsv`.

## 2. Findings: per-unit tracking (B)

### 2.1 What each surface carries

| Surface | Per subagent? | Peak context | Total tokens | Wall time | Source |
|---|---|---|---|---|---|
| Background `<task-notification>` `<usage>` | yes (one per run) | `subagent_tokens` = final footprint, about peak | no | `duration_ms` per run | local measurement (2.2); #76484 |
| Foreground Agent tool result | yes | `totalTokens` (final footprint, inferred) | `usage` buckets of the rollup | `totalDurationMs` | T:16824-16890; #76484 comment 2026-08-17 |
| Subagent transcript `subagents/agent-<id>.jsonl` | yes | max of input+cache per request | sum per request (dedupe by `requestId`) | first to last timestamp | schema digest (2.2); `O/docs/claude-code/session-report-analyze-sessions.mjs.md:15-24` |
| AgentsView 0.45.0 CLI | yes (`agent-<id>`) | `peak_context_tokens` | sum of usage rows | `started_at`/`ended_at` | 1 above |
| Mod events `turn.step`/`turn.complete` | yes (`agentId`) | from each step's `usage` | summed `usage` | `durationMs` | T lines in verdict |
| SubagentStop hook / `classic.SubagentStop` | yes | via `agent_transcript_path` | via transcript | no | `O/docs/claude-code/raw/hooks.md:2547-2569` |
| OTel `claude_code.token.usage`, `cost.usage` | type only | no | yes, by `agent.name` | no | `monitoring-usage.md:685-716` |
| OTel `subagent_completed` event | type only (no id listed) | `total_tokens` final footprint | no | `duration_ms` | `monitoring-usage.md:1268-1286` |
| OTel `llm_request` span (beta) | yes (`agent_id`, `parent_agent_id`) | per request | per request | per request | `monitoring-usage.md:162, 228-240` |
| `claude -p --output-format json` | per lane (session) | no | `modelUsage` whole tree | `duration_ms` | `agent-sdk_typescript.md:1579-1600, 5002-5014` |
| `stream-json` `task_progress`/`task_notification` | yes (`task_id`) | `usage.total_tokens` | no | `usage.duration_ms` | `agent-sdk_typescript.md:5240-5262, 5454-5476` |
| Status line JSON | main session only | `context_window.*` | no | `cost.total_duration_ms` | `O/docs/claude-code/statusline.md:178-190` |
| ccusage 20.0.32 | no (session) | no | yes (subagents folded in) | no | `O/repos/ccusage/rust/crates/ccusage/src/main.rs:212-222` |
| claude-plugins-official session-report | by type | no | by type | session runtime | `session-report-analyze-sessions.mjs.md:7, 78-79` |

### 2.2 Local measurement (numbers and key names only)

- Schema digest of session `464a2816` (2026-10-13, not a D86-listed session; S/bin/schema.py prints keys and
  types only): assistant entries carry `message.usage` with `input_tokens`, `cache_read_input_tokens`,
  `cache_creation_input_tokens`, `output_tokens`, plus `requestId`; subagent entries add `agentId`; the
  parent's Agent results were all `async_launched` with no usage; notifications use the tag
  `subagent_tokens` (not `total_tokens`); `meta.json` keys are `agentType`, `description`, `toolUseId`,
  `spawnDepth`, `requestShape`, `requestNonInteractive`, `model`, `effort`.
- 27 subagents, 26 notified: see verdict B1. One fork (`a22113b35136b11c1`) inherited a 976,270-token
  context, so a forked unit's peak includes its parent's prefix.

### 2.3 Upstream status

- anthropics/claude-code#76484 (2026-07-10): background completions carry no structured usage in the parent
  transcript; a collaborator reproduced it on 2.1.233 and called it a regression since 2.1.198 (comment
  2026-08-17), naming the child transcript and `-p` `modelUsage` as workarounds; closed by the stale bot
  2026-09-14, not fixed.
- #14859: a collaborator confirmed `SubagentStart`, `agent_id`/`agent_type` on hook events in subagents, and
  `agent_transcript_path` plus `last_assistant_message` on SubagentStop (comment 2026-08-17).
- #44723 (peak context in `modelUsage`), #43456 (usage in PostToolUse for Agent), #22625, #10164: all closed
  stale without the feature. #58125 (docs omitted `agent_id` on spans) closed 2026-05-12; the docs now list it.
- ccusage#1329 (breakdown by subagent type) and #1692 (by plugin, skill, sidechain) closed unimplemented;
  ccusage#950 is a Codex 91x overcount, which the TokenJam post (2026-07-04,
  `O/docs/misc/tokenjam-subagent-token-counts.md`) generalises to Claude Code without evidence here.

## 3. Code examples found

- GNU parallel disk limit function, Ole Tange, 2018-10-09 (URL above; `O/docs/gnu-parallel/ml-2018-10-disk-free-limit.md`).
- niceload disk sensor: `niceload -H -l -100000 --sensor "df . | awk '{ print \$4 }'" <cmd>` (`niceload.md:176-205`).
- SIGSTOP/SIGCONT disk watchdog loop, Stack Overflow 66596314 answer by KamilCuk, 2021-03-12 (Exa excerpt
  `S/exa/q10.json`; webclaw mirror failed).
- GNU parallel `--limit` builtins and kill/requeue: savannah commit `1f05ef46` (release 20260822),
  https://git.savannah.gnu.org/cgit/parallel.git/tree/src/parallel?id=1f05ef46e33efac62af6d7fa635cd65dfb05cc84,
  lines 7945-7969, 8761-8766, 8806-8830, 12610-12620.
- webclaw checkpoint: https://github.com/0xMassi/webclaw/blob/aadf8ed1ef6102d4fccabef9680fa894c28a19f3/crates/webclaw-cli/src/main.rs#L1517-L1631.
- xnu pressure sysctl: https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.121.6/bsd/kern/kern_memorystatus_notify.c#L1776-L1910.
- AgentsView session usage: https://github.com/kenn-io/agentsview/blob/b9d0a207f51ff27b84adbaae2a91b344247079b3/internal/db/usage.go#L2862-L2917.
- Anthropic's transcript reader (dedupe by `requestId`, subagent `meta.json`):
  https://github.com/anthropics/claude-plugins-official/blob/main/plugins/session-report/skills/session-report/analyze-sessions.mjs.
- The per-unit mod sketch, type-checked (tsc 7.0.2, rc 0; a misspelled field gave TS2339), not run live
  (`S/modspike/hooks/unit-usage.ts`):

```ts
import type { Register } from 'claude-code'
type Unit = { unit: string; agentId: string; peak: number; total: number; requests: number; spawnedAt: number }
const units = new Map<string, Unit>()
const LEDGER = '.planning/unit-usage.jsonl' // illustrative; the parent owns the real record
export const register: Register = (on) => {
  on('agent.spawn', async ($, e, next) => {
    const r = await next(e)
    const unit = /LANE-UNIT:\s*(\S+)/.exec(e.prompt)?.[1]
    if (r.agentId !== undefined && unit !== undefined)
      units.set(r.agentId, { unit, agentId: r.agentId, peak: 0, total: 0, requests: 0, spawnedAt: Date.now() })
    return r
  })
  on('turn.step', async function* ($, e, next) {
    const r = yield* next(e)
    const u = e.agentId === undefined ? undefined : units.get(e.agentId)
    if (u !== undefined && r.usage !== null) {
      const ctx = r.usage.input_tokens + r.usage.cache_read_input_tokens + r.usage.cache_creation_input_tokens
      u.peak = Math.max(u.peak, ctx); u.total += ctx + r.usage.output_tokens; u.requests += 1
    }
    return r
  })
  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    const u = e.agentId === undefined ? undefined : units.get(e.agentId)
    if (u !== undefined) {
      const row = { ...u, durationMs: e.durationMs, reason: e.reason, at: new Date().toISOString() }
      const prev = (await $.fs.exists(LEDGER)) ? String(await $.fs.read(LEDGER)) : ''
      await $.fs.write(LEDGER, prev + JSON.stringify(row) + '\n')
    }
    return r
  })
}
```

## 4. Routes

`fx` = `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --` (S/bin/fx); keys reached commands through the environment only.

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 1 | Exa | `fx exa.sh <out> "<query>" 10` (POST api.exa.ai/search) x17 | 0, HTTP 200 each | 10 each | Yes: niceload, Ole Tange post, spider, crawl4ai, xnu doc, eclecticlight, #44723, #22625, #76484, #58125, ccusage#313, tokenjam, session-report, cct, cc-usage |
| 1 | Context7 | `fx ctx7 library "<name>"` x6 (claude code, gnu parallel, sysinfo, crawlee, ccusage, webclaw) | 1 each | "Monthly quota reached" | No; gap |
| 1 | Firecrawl | `fx firecrawl search "<q>" --limit 5 --json` x2 | 1, 1 | HTTP 402 insufficient credits | No; gap |
| 1 | webclaw (Firecrawl fallback and D110 mirror) | `webclaw -t 60 <url> -f markdown > <file>` x30 | 0 x29, 1 x1 (stackoverflow.com) | 29 pages | Yes, all `O/docs/**` cites |
| 1 | curl raw docs | `curl -sS -L https://code.claude.com/docs/en/<page>.md` x10 | 0, HTTP 200 each | 10 | Yes, for line-preserving copies (`O/docs/claude-code/raw/hooks.md`) |
| 1 | Serper | `fx serper.sh <out> "<q>"` x6 | 0, HTTP 200 each | 8 shown each | Yes: niceload man page, psutil#2725, SO 66596314 |
| 1 | SerpApi | not run | n/a | n/a | Serper succeeded |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3.13 -I last30days.py --plan plan.json --emit md --quick --search reddit,hackernews,github,x --save-dir ""` | 0 | planner kept 1 of 3 subqueries and reddit+HN only; 2 Reddit, 6 HN, all off-topic | No; gap |
| 1 | Last30Days | same, throttle plan | 0 | 0 results; Reddit ScrapeCreators HTTP 402 | No; gap |
| 2 | gh issue view | `gh issue view <n> --repo <r> --comments --json ...`: claude-code 44723, 22625, 10164, 76484, 58125, 50776, 53954, 14859, 13326, 43456, 46253, 95601; ccusage 1329, 1692 | 0 each | 14 bodies in `S/gh/issues` | Yes |
| 2 | gh search issues | `gh search issues "<q>" --repo <r> --limit 15` x13 (claude-code x7, ccusage x2, webclaw x4) | 0 each | 0 to 15 | Yes: ccusage#1329, #1692, #950; claude-code#95601, #46253 |
| 2 | gh pr list/view | `gh pr list --repo 0xMassi/webclaw --search ...`; `gh pr view 142|141|98` | 0 each | 27 PRs; 3 bodies | Yes: decisive for the upgrade note |
| 2 | gh issue list | `gh issue list --repo 0xMassi/webclaw --search crawl` | 0 | 4, none on throttling | No |
| 2 | GraphQL discussions | `gh api graphql` search type DISCUSSION x7 | 0 each | 474, 2, 0, 4, 1, 3, 0 | No relevant hit |
| 2 | Saved searches (task) | `./dev/mise run research:collect` | not run | n/a | Writes a tracked path another lane owns |
| 2 | Saved searches (reproduced) | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5 -F page=1,2` plus control `README repo:<r>`, for codex-schema and 5 candidates | 0; first pass HTTP 403 rate limit on 3 rows (limit shared with other agents), rerun 0 | codex-schema 884 (control 159); see section 5 | Yes |
| 2 | Issue search | `gh api -X GET search/issues -f q='<q> repo:<r>'` x3 plus control `mods repo:anthropics/claude-code is:issue` | 0 each | 41, 154, 8; control 269 | Yes (rows proposed) |
| 2 | Source reads | `gh api -X GET search/code -f q='memorystatus_vm_pressure_level SYSCTL repo:apple-oss-distributions/xnu'`; `gh api -H 'Accept: application/vnd.github.raw' .../kern_memorystatus_notify.c?ref=xnu-12377.121.6` | 0, 0 | 4 files; 2,152 lines | Yes |
| 2 | Clones (D110) | `git clone --filter=blob:none [--branch <tag>] <url>`: webclaw v0.6.23, gnu-parallel (savannah, filter ignored), ccusage main, agentsview v0.45.0; `git fetch origin` on webclaw | 0 each | 4 repos | Yes, code reading only, nothing executed |
| 2 | Repo metadata | `gh repo view kenn-io/agentsview`; `gh release list --repo 0xMassi/webclaw` | 0, 0 | n/a | Yes |
| local | Host facts | `sysctl`, `memory_pressure -Q`, `vm_stat`, `df -k`, `man` x7, `powermetrics -n 1` (refused, not root), `brew info --json=v2` x7, `claude --version`, `webclaw --help` | 0 except powermetrics | n/a | Yes |
| local | AgentsView CLI | `agentsview session list --json --include-children --date 2026-10-13 --sort peak-context:desc --limit 3`; `session get agent-<id> --json`; `serve stop` | 0 each | 3 sessions; 1 child | Yes. Side effect: `session list` started the daemon (pid 76634) and ran a full resync that rebuilt its database; R5 stopped it with `agentsview serve stop`, restoring "no daemon" |
| local | Transcript digests | `python3 -I S/bin/schema.py`, `S/bin/unit_metrics.py` on session `464a2816` (keys and numbers only) | 0 | 27 subagents | Yes (2.2) |
| local | Type-check | `tsc -p` (7.0.2 from the session's `tsspike`, read-only) on `S/modspike` | 0; negative control TS2339 | n/a | Yes |
| local | Limit script dry run | `DIR=... FLOOR_GIB=<n> S/bin/crawl-limit.sh` x4 | 0, 0, 2, 1 | n/a | Yes (1.5) |

Incident: while copying helper scripts R5 ran `sed -i` on R1's `S/../R1/bin/ghfetch.sh`, then reverted it at
once; its content is identical, only its mtime changed.

## 5. Proposed saved-search rows (not added; `dev/saved-searches.toml` untouched)

Each was run with its control (`README` in the same repository) in this session; counts are `total_count`.

```toml
[[search]]
id = "webclaw-crawl-state"        # 1 hit: crates/webclaw-cli/src/main.rs; control 10
query = "crawl_state"
repo = "0xMassi/webclaw"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "webclaw-stream-only"        # 4 hits: CHANGELOG.md, server crawl route, crawler.rs, main.rs; control 10
query = "stream_only"
repo = "0xMassi/webclaw"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "ccusage-subagents"          # 9 hits incl. rust/adapters/claude/src/paths.rs; control 16
query = "subagents"
repo = "ccusage/ccusage"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "agentsview-peak-context"    # 65 hits incl. docs/session-api.md; control 73
query = "peak_context_tokens"
repo = "kenn-io/agentsview"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

Not proposed: `subagent_completed repo:anthropics/claude-code` (0 code hits; the docs live outside that
repository). If the collector gains an issues kind: `subagent_tokens repo:anthropics/claude-code is:issue`
(41) with control `mods repo:anthropics/claude-code is:issue` (269).

## 6. Open gaps

- Context7 (monthly quota), Firecrawl (HTTP 402) and Last30Days (off-topic, then 0 results with
  ScrapeCreators HTTP 402) gave no evidence; Exa, Serper, webclaw and GitHub carried the research.
- GNU parallel is not installed (installing it needs an admission), so the composition in 1.5 is unrun:
  SIGINT delivery through `--termseq` to webclaw inside an `sh -c` wrapper, the wrapper exit code under
  `--retries`, and `--limit` exit 2 with `--retries` requeue all need the CT-33 spike.
- SIGSTOP effects on in-flight webclaw requests; `taskpolicy -c utility` versus `-b` throughput; whether the
  `-c` clamp also throttles I/O: unmeasured (UNVERIFIED).
- niceload's Linux `free` parse is code reading only (UNVERIFIED on a Linux host).
- No webclaw release carries PR #141/#142 yet; their behaviour is from the PR bodies and staging code.
- The mod sketch was not run in a session (no session starts): whether `turn.step` sees background
  subagents' steps, whether `agent.spawn` returns `agentId` for a background launch, and the base path of
  `$.fs.write` are UNVERIFIED; T is 2.1.296 while the CLI is 2.1.299.
- Foreground Agent `totalTokens` equal to the final footprint is inferred from the OTel definition and the
  background measurement, not measured.
- OTel exports, `claude -p` JSON and `stream-json` fields are from docs only; none was exercised.
- AgentsView peak was cross-checked on two subagents only; its `--no-sync` path was not tried.

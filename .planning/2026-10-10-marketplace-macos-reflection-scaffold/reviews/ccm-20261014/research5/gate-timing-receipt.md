# Gate hook launch timing (parent receipt, 2026-10-14)

Measured by session ccm-20261014 for the user's Q83 follow-up (D60 versus D102). Host: this Mac,
arm64, Darwin 27.0.0; uv 0.12.7; venv Python 3.15.0; /usr/bin/python3 3.9.6. hyperfine was
unusable (global mise shim error, not repaired: global mise needs its own admission), so a stdlib
harness ran each command 33 times with the hook JSON on stdin and dropped the first 3.
Harness and raw JSON: session scratchpad `gate-timing/` (bench.py, plain-timing.json,
push-timing.json). Gate: `dev/hooks/pretooluse_gate.py` at HEAD 21af565 plus the D102 docstring edit.

| Launcher | Plain `ls -la` median / p90 ms | `git push origin HEAD` median / p90 ms |
| --- | --- | --- |
| cat (compiled-binary floor) | 2.5 / 3.5 | 2.3 / 2.5 |
| /usr/bin/python3 3.9 -I | 98.6 / 104.5 | 450.4 / 494.3 |
| .venv python 3.15 -I | 26.5 / 29.0 | 402.2 / 610.9 |
| .venv python 3.15 -I -S | 26.2 / 28.6 | 395.8 / 446.1 |
| uv run (sync check) | 40.4 / 44.1 | 395.9 / 466.0 |
| uv run --frozen --no-sync | 35.5 / 39.8 | 388.9 / 457.1 |
| uv run --no-project | 34.9 / 37.3 | 390.5 / 436.4 |

Cold start: a new venv (`UV_PROJECT_ENVIRONMENT` set to an empty directory) with a warm uv cache
took 0.33, 0.26 and 0.26 s real for `uv run python -I -c pass`. With an empty cache and
`UV_OFFLINE=1` the run failed to fetch githubkit's wheels.

Reading: uv adds 9 to 14 ms per launch on a warm machine. On the push path, git subprocess calls
(12 call sites in `git_gate.py`) and the retro-gate child process dominate, so the interpreter is
about 25 ms of about 400 ms. A missing or unsyncable environment under `onFailure: block` blocks
every Bash call.

# w0-doctor receipt (complete; review pending)

Branch `claude/w0-doctor-core`, final SHA `64e46d4a959ecbeab44de4bc0b44813ab00b55f2` (impl `bb0e2a4`). Tip `c21941f` merged: already an ancestor ("Already up to date", rc 0). Status clean.

Changed (all owned): `dev/doctor/{cli,core,budget,settings,integration}.py`, `dev/test_doctor.py`, `dev/fixtures/doctor/settings/{staged,before-ct02}.json`, `dev/check.py`, `mise.dev.toml`, `hk.pkl`, `.claude/settings.json`, `dev/test_hooks.py`, `P/retros/w0-doctor.md`.

Gates (final bytes), all rc 0: unittest test_doctor* (12), test:doctor, cli `--surface check --json` (0 findings), tasks validate, check, check:acceptance-baseline, test:hooks (15, hk ran), hk validate, diff --check, retro:gate. With a P1 planted, check exits 1.

Red→green: every C2/C3 test id failed first, except the block-shape test (mutation-proven) and T-A6 (pins committed keys).

Latency: session-start 369-396 ms, pre-commit 204-237 ms.

Deviations:
- staged fixture yields 1+6, not 1+4 (no extraKnownMarketplaces); 4 is before-ct02's count.
- `context:` line always printed (T-A5 default(on)).
- settings pre-commit budget 1000 ms.
- HkHooks setUp copies dev/doctor.
- foreign-hunk accepts the merge-tree blob.

Parent: hk hooks are already installed, so the records step ran on lane commits. claude-team.md sentence: "SessionStart runs `dev/doctor/cli.py --surface session-start --format context` (never blocks); hk pre-commit runs `check:records`."

Unverified: live hook firing; root-checkout latency.

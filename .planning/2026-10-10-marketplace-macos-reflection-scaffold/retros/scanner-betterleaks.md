# scanner-betterleaks retrospective: A09 scanner switch, part A (CT-82 part A, D159, R17)

Unit `scanner-betterleaks`, worktree `.claude/worktrees/scanner-betterleaks`, branch
`claude/scanner-betterleaks`, `base_sha` `5c4ff9a` (`allocated_from`; the worktree is cut from the
allocation commit `ca53deb`, so `git log ca53deb..HEAD` is the lane). Commits: `6a222a4` (pin),
`ee2ae8d` (fixes, rule, tests), `4eeb732` (implementer's draft of this record), `6948135` (review
P3 fix), `ab97c5c` (review disposition), then the retro commit carrying this record. Implementer:
Claude Opus 5.5, high (trailer matches `writer_model` opus). Cold review of `4eeb732`: Fable 5.1,
high, read-only, **PASS-with-findings** (P2 lock entry, parent; P3 PATH-resolved scanner,
implementer; P3 untracked `.mise/`, parent). Retro writer: Fable 5.1, high, in the worktree,
editing this file only; digest: the parent's brief and `metrics/agent-runs.jsonl` rows 33, 34, 36.

Delivered, test-first (each test failed before its change): `mise.dev.toml` pins
`"aqua:betterleaks/betterleaks" = "1.9.0"` (newest 1.x, 2026-09-29; 2.0 is rc only).
`.gitleaks.toml` gains rule `aws-access-key-id`: the default rule's regex, keywords, entropy floor
3.0 and `.+EXAMPLE$` exemption without the paired-secret component that drops a lone key ID in
betterleaks 1.x (#408); `betterleaks config check` reports 465 rules (464 before) and gitleaks
8.30.1 still loads the file (rc 0). `dev/git_delivery.py` `scan()` pops `BETTERLEAKS_CONFIG` and
`BETTERLEAKS_CONFIG_TOML` with the `GITLEAKS_*` names, passes `--config <root>/.gitleaks.toml`, and
refuses in one line when the root holds `.gitleaksignore` or `.betterleaksignore`. Binary name, CLI
flags and intent keys are unchanged. `dev/test_git_delivery.py` adds four seam tests: three through
the `publish` CLI with a recording fake scanner, one on the real pinned scanner with a key ID
assembled at runtime. Size: 4 maintained files plus this record, 105 handwritten lines
(`git diff --stat ca53deb ee2ae8d`: +105/-3; `6948135` +31/-10), within the 5-file / 300-line limit.

Exits re-run by the retro on `ab97c5c` in the worktree, `VIRTUAL_ENV` and
`UV_PROJECT_ENVIRONMENT` unset: `./dev/mise run test:delivery` 18 tests OK rc 0 (the real-scanner
test ran, not skipped); `./dev/mise tasks validate` rc 0 (64 tasks); `./dev/mise run check` rc 0
(toml 21, so `.mise/` is excluded); `./dev/mise run check:acceptance-baseline` rc 0 (19 baseline
hashes); `git diff --check ca53deb HEAD` rc 0. Implementer exits on `ee2ae8d` and `6948135` (rows
33, 36): the same five rc 0, hk pre-commit `records` passed on every commit. On this record before
its commit: `python3 -I dev/retro_gate.py --unit scanner-betterleaks` rc 0 and `check` rc 0; the
handoff repeats both on the commit. Not run by the lane: `check:research`, `deps:check`,
`test:bootstrap` (parent-run; the worktree lacks the project uv, they exit 1 at the base too).

Measurement (R17 section 7.4 reproduced): pinned betterleaks `git --config .gitleaks.toml
--redact=100 --log-opts=origin/main..HEAD` (21 commits), 3 runs: rc 1 each, 2.33 / 2.37 / 2.39 s
wall, 228 findings (`generic-api-key` 226, `ibm-cloud-user-api-key` 2; `aws-access-key-id` 0,
private-name rule 0), 227 distinct fingerprints, every `Secret` redacted.

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P2 | SB-1 Automated checks: the pin breaks the tool-lock binding. `dev/bootstrap.py` `TOOL_BACKENDS` hard-codes python and uv and `verify_tool_lock()` requires `mise.dev.lock` to list every `[tools]` entry, so at `6a222a4` `tools:prepare`, `deps:check` and `test:bootstrap` refuse ("mise.dev.lock tools differ from mise.dev.toml"); both files are outside `owned_paths` (review P2; `6a222a4` message). | Deferred, owner parent, admission: integrate the lane together with parent edit 1 (the companion patch, sha256 `efe708740809be390a4138aba0a2ed359cd57cf87c84fabe1b78d2170d36a476`, inlined below). Verified by the retro in the worktree with the patch applied, then reverted: `python3 -B dev/check.py` rc 0 with parent edit 2 in place. |
| P2 | SB-2 Automated checks: `dev/check.py` never calls `bootstrap.verify_tool_lock()`, which is static (no install, no network), so `./dev/mise run check` and `development.yml` pass a `[tools]` change whose lock is stale; only `research-fast.yml` sees it, through `tools:prepare`. An existing check not wired in (implementer audit; `dev/check.py`, `.github/workflows`). | Mechanical fix: one call to an existing function (D113), destination `dev/check.py` (outside `owned_paths`): parent edit 2. Verified in the worktree, then reverted: with the edit and the companion patch `python3 -B dev/check.py` rc 0 and `python3 -I -B dev/check.py` rc 0; with the edit and the pin alone rc 1, `check failed: mise.dev.lock tools differ from mise.dev.toml`. Deferred, owner parent: apply in the same integration as edit 1, after it, else `check` fails on the integration branch. |
| P2 | SB-3 Automated checks: `./dev/mise run test:delivery` is reached by neither route `.claude/rules/dev-tests.md` allows: `dev/check.py` discovers `test_research_*.py` only and `check:research` does not list `test:delivery` in its `depends`, so the hosted workflows never run the A09 suite or the new real-scanner test (`mise.dev.toml`; same class as gate-git-path's P2 for `test:retro-gate`). | Mechanical, destination `mise.dev.toml` `[tasks."check:research"]` (the lane owns the pin line only): parent edit 3. Verified in the worktree, then reverted: `./dev/mise tasks validate` rc 0 (64 tasks), `./dev/mise tasks deps check:research` lists `test:delivery`. Deferred, owner parent, admission: after edits 1-2, since `research-fast.yml` installs betterleaks through `tools:prepare` from the lock's `linux-x64` entry; the hk lane also edits this file, so apply the one-token insert at whichever integration comes second. |
| P2 | SB-4 Coding standards: a `git diff .gitleaks.toml` in the implementer's run printed a hunk header; Git quotes the nearest unindented line in each `@@` header, which was the private-name rule's `regex` value, so the value reached tool output. It reached no commit, message or record (implementer audit; the value is committed in `.gitleaks.toml`, character-classed). | Applied in the lane: later diffs and this retro used `git diff -U0 -- .gitleaks.toml \| grep -v '^@@'`. Rule, destination a `paths:`-scoped rule that loads when the file is touched: parent edit 4 (new `.claude/rules/secret-scanner.md`) and parent edit 5 (`.claude/AGENTS.md` rules line). A mechanical guard is rejected: no check sees tool output, and a `.gitattributes` diff driver needs `diff.<driver>.xfuncname` in per-checkout Git config (`hooks:install` waits for CT-02b), so a fresh checkout would still quote the value. Verification after the edits: `./dev/mise run check` rc 0. |
| P2 | SB-5 Information access: the brief named an AWS documentation example key ("AKIA...EXAMPLE") as the fixture; the upstream rule and the new rule exempt `.+EXAMPLE$`, so that key alone proves nothing (brief; `.gitleaks.toml` allowlist). | Applied in `ee2ae8d`: `test_root_config_reports_lone_aws_access_key_id` assembles a synthetic non-EXAMPLE key ID at runtime and asserts exactly one `aws-access-key-id` finding with the documentation example on the next line producing none; it failed before the rule (rc 0, no findings) and passes after. Retro re-run: `test:delivery` 18 OK rc 0. The fixture convention is the second line of parent edit 4. |
| P3 | SB-6 Coding standards (review): `dev/test_git_delivery.py` found the scanner with `shutil.which("betterleaks")`, so an unpinned PATH binary could run or the test could skip silently; reproduced on `4eeb732` with a stub first on PATH (`stub ran: yes`, failing `0 != 1`) (`.claude/rules/dev-tests.md`). | Applied in `6948135`: `pinned_betterleaks()` reads the pin from `mise.dev.toml` with `tomllib`, resolves the binary with `./dev/mise which betterleaks`, asserts `betterleaks version` equals the pin, and fails rather than skips when the binary is missing under `MISE_TASK_NAME=test:delivery`. Implementer verification (row 36): stub first on PATH, `test:delivery` rc 0 and the stub did not run; a fake mise returning the stub FAILS (`(0, '9.9.9') != (0, '1.9.0')`); pinned install moved aside, `test:delivery` rc 1 with "pinned betterleaks 1.9.0 is missing", install restored. Retro re-run: 18 OK rc 0. |
| P3 | SB-7 Automated checks: after integration the root checkout fails `test:delivery` until the pinned binary is installed there: today `./dev/mise which betterleaks` exits 1 in the root and root `.mise/installs` holds python and uv only, while the worktree's `.mise/installs/aqua-betterleaks-betterleaks/1.9.0` exists; under the task the test fails rather than skips (SB-6) (retro measurement). | Deferred, owner parent, admission: the lane record's network admission ("mise install of the pinned betterleaks only") extended to the root checkout; parent operation A runs `./dev/mise run tools:prepare` after edits 1-2 and then `test:delivery` (18 OK expected), `check` and `tasks validate` there. |
| P3 | SB-8 Automated checks: with `--config` explicit, a missing `<root>/.gitleaks.toml` makes the scanner exit 1 and `scan()` reports "secret scan found potential leaks". Measured by the retro with the pinned binary on a scratch repository: `--config <absent>` rc 1, stderr `FTL unable to load config, err: open ...: no such file or directory`; without `--config` rc 0 (implementer proposal: a fourth refusal "scanner config missing"). | Rejected with evidence: the path is fail-closed today (rc 1 raises `Refusal` and `publish` never proceeds); `.gitleaks.toml` is tracked and present in every checkout; D159 enumerates the three fixes and D113 limits existing Python to fixes, so a new refusal branch is new behaviour for the native core; and the `publish` tests build scratch repositories without a config file, so the refusal would also rewrite their `setUp`. The misleading text costs one adjudication round in a case that needs a deleted tracked file. Not applied. |
| P3 | SB-9 Information access: the measured range has one duplicated fingerprint (228 findings, 227 distinct), so `fingerprints()` refuses to adjudicate it; a gitleaks-made baseline suppresses nothing under betterleaks (R17 sections 7.3, 7.4). Not caused by this switch. | Deferred, owner parent, admission: the re-adjudication operation in R17's table, recorded through `plan:decide`, runs before the A09 intents switch `gitleaks_bin` (D159); this lane changes no adjudication. |
| P3 | SB-10 Navigation (review): `./dev/mise install` puts the per-worktree data dir `.mise/` in the worktree, untracked and not ignored, so `git status` showed `?? .mise/` and `check` parsed its TOML files (`.gitignore` is frozen). | Applied by the parent: `.git/info/exclude` holds `.mise/`. Verified by the retro: `git status --short` in the worktree is empty and `check` counts toml 21. |
| P3 | SB-11 Steering: R17 also lists pointing the A09 intent's `gitleaks_bin` at the pinned binary and doc mentions of gitleaks as the A09 scanner; both are outside `owned_paths`. Retro grep: `gitleaks` appears in `docs/research-feedback-retro/progress.md` and `publication-review.md` only, historical records that stay as written; no navigation document names the scanner. | Deferred, owner parent at the D159 intent switch (parent operation B), admission: SB-1 to SB-3 integrated and operation A done in the publishing checkout; then set `gitleaks_bin` to the absolute path `./dev/mise which betterleaks` prints there, rerun `test:delivery` and one A09 dry publish. No doc edit is owed. |
| P3 | SB-12 Tool economy: the implementer's first baseline loop ran `./dev/mise $t` in zsh, which keeps `$t` as one word, so all four checks exited 1 on a usage error; the retro writer repeated the same slip once before rerunning with explicit commands (rows 33 and this run). | Two agents, one lane: a cached gotcha earns one clause in the root `AGENTS.md` check bullet, parent edit 6. Nothing else to change; the retro's 15 batched calls otherwise read each file once. |
| P3 | SB-13 Information access: the review verdict exists only in the parent's transcript and `metrics/agent-runs.jsonl` row 34, and the lane record's `review`, `retro` and `status` fields still read null / `allocated` (lane record). | This record restates the three review findings with their dispositions (SB-1, SB-6, SB-10). Deferred, owner parent at receipt: parent edit 7 sets the three fields (the lane changes only `status`). |

No-ops: none, because every change has a test that failed first, apart from the pin, which the
real-scanner test needs (it ran under `./dev/mise`); the one comment added to `.gitleaks.toml`
describes the new rule and the one in `scan()` states the environment-name order betterleaks uses.

Global guidance (`AGENTS.md`, `CLAUDE.md`, rules, skills, agents): none changed in the lane; the
proposals above name their files, owners and literal text below. The retro commit's trailer names
Claude Fable 5.1 per `.claude/rules/planning-records.md`.

## Parent edits (outside `owned_paths`; literal, apply unread)

1. Companion patch (SB-1), scratchpad `scanner-betterleaks-companions.patch`, sha256
   `efe708740809be390a4138aba0a2ed359cd57cf87c84fabe1b78d2170d36a476`. Its two hunks:
   `dev/bootstrap.py`, replace
   `TOOL_BACKENDS = {"python": "core:python", "uv": "aqua:astral-sh/uv"}` with
   ```python
   TOOL_BACKENDS = {"python": "core:python", "uv": "aqua:astral-sh/uv",
                    "aqua:betterleaks/betterleaks": "aqua:betterleaks/betterleaks"}
   ```
   and `mise.dev.lock`, insert after the `lockfile_version = 3` line and its blank line:
   ```toml
   [[tools."aqua:betterleaks/betterleaks"]]
   version = "1.9.0"
   backend = "aqua:betterleaks/betterleaks"
   specifiers = ["1.9.0"]

   [tools."aqua:betterleaks/betterleaks"."platforms.linux-arm64"]
   checksum = "sha256:1d39116e0a58dc94574715e2aa12a2dbd5062f193eee3fec011fef6ba06bd13b"
   url = "https://github.com/betterleaks/betterleaks/releases/download/v1.9.0/betterleaks_1.9.0_linux_arm64.tar.gz"
   url_api = "https://api.github.com/repos/betterleaks/betterleaks/releases/assets/599108932"
   provenance = "cosign"

   [tools."aqua:betterleaks/betterleaks"."platforms.linux-x64"]
   checksum = "sha256:f8b185a39ffcece2a1ca82bf3a4e7435cd81963ffd16b7a9128daf75f35f6de7"
   url = "https://github.com/betterleaks/betterleaks/releases/download/v1.9.0/betterleaks_1.9.0_linux_x64.tar.gz"
   url_api = "https://api.github.com/repos/betterleaks/betterleaks/releases/assets/599108929"
   provenance = "cosign"

   [tools."aqua:betterleaks/betterleaks"."platforms.macos-arm64"]
   checksum = "sha256:83dd7eaab13d44a1e8e347a17064cdef153a1478db473276d41b38d55613d3f2"
   url = "https://github.com/betterleaks/betterleaks/releases/download/v1.9.0/betterleaks_1.9.0_darwin_arm64.tar.gz"
   url_api = "https://api.github.com/repos/betterleaks/betterleaks/releases/assets/599108927"
   provenance = "cosign"

   ```
2. `dev/check.py` (SB-2), three replacements. After
   `from runtime_preflight import scrubbed  # noqa: E402  (single selector list for the CLI and harness)`
   insert:
   ```python
   sys.path.insert(0, str(ROOT / "dev"))
   from bootstrap import verify_tool_lock  # noqa: E402  (the tools:prepare lock binding; static, no install)
   ```
   Before `    run("git", "diff", "--check")` insert:
   ```python
       verify_tool_lock()  # every mise.dev.toml [tools] entry is bound in mise.dev.lock, so tools:prepare cannot refuse later
   ```
   Replace `    except (OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as error:` with
   `    except (OSError, ValueError, RuntimeError, SyntaxError, subprocess.CalledProcessError) as error:`.
3. `mise.dev.toml` (SB-3), in `[tasks."check:research"]` replace
   `"test:frontier", "test:retro-gate"]` with `"test:frontier", "test:retro-gate", "test:delivery"]`.
4. New file `.claude/rules/secret-scanner.md` (SB-4, SB-5):
   ```markdown
   ---
   paths: [".gitleaks.toml"]
   ---

   # Secret scanner configuration

   - Diff this file with `git diff -U0 -- .gitleaks.toml | grep -v '^@@'`: a hunk header quotes the nearest unindented line, which is the private-name rule's `regex` value. Cite a rule by its `id` and `description` lines.
   - The private-name rule spells its words as character classes, and a test fixture assembles its secret at runtime (`dev/test_git_delivery.py`), so no committed file holds a match.
   ```
5. `.claude/AGENTS.md` (SB-4), replace
   `- \`rules/\`: path-scoped rules for \`dev/\`, \`evidence/\`, \`.planning/\` and hooks and mods; edit a rule here and`
   with
   `- \`rules/\`: path-scoped rules for \`dev/\`, \`evidence/\`, \`.planning/\`, \`.gitleaks.toml\` and hooks and mods; edit a rule here and`.
6. Root `AGENTS.md` Gotchas (SB-12), replace
   `- Run \`./dev/mise tasks validate\`, \`./dev/mise run check\` and`
   with
   `- Run, one literal command each (zsh keeps a \`$t\` loop variable as one word and every check exits 1 on usage), \`./dev/mise tasks validate\`, \`./dev/mise run check\` and`.
7. `lanes/scanner-betterleaks.json` (SB-13), at receipt: `"status": "reviewed"`,
   `"review": "PASS-with-findings on 4eeb732 (P2 lock entry, parent edit 1; P3 PATH-resolved scanner, fixed 6948135; P3 .mise/ exclude, parent); reviewer fable high, cold, read-only"`,
   `"retro": "passed"`; `status` becomes `integrated` at the merge.

## Parent operations (recorded through `plan:decide`, not edits)

- A (SB-7): in the root checkout after edits 1-3, `./dev/mise run tools:prepare` (network: the pinned
  betterleaks only), then `./dev/mise run test:delivery` (18 OK), `./dev/mise run check`,
  `./dev/mise tasks validate` and `./dev/mise run check:research`, exits recorded.
- B (SB-9, SB-11): the D159 intent switch: re-adjudicate the history range per R17's table, set
  `gitleaks_bin` to the absolute pinned path in the publishing checkout, rerun `test:delivery` and
  one A09 dry publish.

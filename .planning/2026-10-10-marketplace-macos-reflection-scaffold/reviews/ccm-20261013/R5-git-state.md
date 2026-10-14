# R5: git, worktree and integration state, and the settings.json split

Reviewer R5, review-orchestrator session `b74a0bf1-dd98-44d5-8122-e47e12ad4fd2`, 2026-10-13.
This review was read-only. I ran no merge, commit, add, reset, checkout, stash push or
worktree mutation. Hook scripts and `dev/retro_gate.py` were run directly in dry mode,
fed JSON on stdin; they only read. Afterwards `git status --short` was unchanged.
Paths are relative to the repository root.

## Scope read

- `reviews/ccm-20261013/00-evidence-index.md`; `settings.json.before-ct02` (backup).
- Git: `status`, `diff --cached`, `diff` (unstaged diff is empty), per-file blob comparison
  index vs `e12cf04` vs `9cd396a` vs merge-base `d0d6d4d`, `log`, `merge-base
  --is-ancestor`, `worktree list`, `for-each-ref`, `ls-files`, `check-ignore`,
  `config --get` (merge.ff, `hook.*`), `.git/hooks`, `.git/info/exclude`, `.git/MERGE_*`.
- Files: `.claude/settings.json`, `.claude/settings.local.json`, `hk.pkl`,
  `dev/hooks/{git_gate,pretooluse_gate,stop_gate,subagent_stop_gate}.py`,
  `dev/test_hooks.py` (hk class), `dev/retro_gate.py` (header), `dev/git_delivery.py`
  (hook guard, intent keys), `mise.dev.toml` (retro/hooks/delivery tasks),
  `lanes/*.json`, `retros/{gate-hooks,nav,c1-catalog-promotion,team,retro-gate}.md`,
  `docs/agents/claude-team.md` (staged gate-layer paragraph), `ci/acceptance.sh` (head),
  `evidence/onboarding/baseline-files.json`, `.agent/`, `.agents/`.
- Key names only (no values) from `~/.claude/settings.json`; marketplace sources from
  `~/.claude/plugins/known_marketplaces.json`; the A09 intents of the last publication
  under the old session scratchpad (`publication/batch3`); memory
  `marketplace-workflow-rules.md`.
- Docs: https://code.claude.com/docs/en/settings, the settings-reference index and the
  `switchModelsOnFlag` entry, and https://code.claude.com/docs/en/hooks (command-hook
  fields, `onFailure`, file watcher). Several of these pages were truncated; see Could
  not verify.

## Findings

### P1

**P1-1. The staged project `settings.json` still carries personal config.** It holds
`permissions` (an MCP allow-list) and all 8 `enabledPlugins`, and it would be committed
and published as-is.
- `git diff --cached` shows the staged blob `bcd7e62`, and so does the lane commit `e12cf04`.
  `cmp .claude/settings.json <(git show e12cf04:.claude/settings.json)` reports `WT == lane`.
  The working tree, the index and the lane are byte-identical.
- Top-level keys: staged = `$schema, enabledPlugins, hooks, permissions`;
  `settings.local.json` = `additionalDirectories, disableClaudeAiConnectors,
  extraKnownMarketplaces, prefersReducedMotion, switchModelsOnFlag, teammateMode`.
  The backup = `$schema, additionalDirectories, disableClaudeAiConnectors, enabledPlugins,
  extraKnownMarketplaces, permissions, prefersReducedMotion, switchModelsOnFlag,
  teammateMode`.
- Correction to the side-agent account: the merger fork did not "leave" `permissions`
  and `enabledPlugins` behind. Lane commit `0c2748e` (CT-02) already committed a
  `settings.json` that dropped the six keys and kept `permissions` and `enabledPlugins`;
  the lane retro (line 21) says "63 lines of settings, mostly copied". The fork only wrote
  `settings.local.json` before it ran `git merge --no-ff --no-commit`.
- The split so far is lossless. Python check: `{project minus hooks} ∪ local == backup`
  prints `True`, and the two files share no keys. No secret-like values: a grep for
  key/token/secret/password/bearer/sk- found nothing. The only personal data is the path
  `<personal directory>`.
- The MCP servers named in the allow-list (`context7`, `memory`) are not defined by this
  repository: there is no `.mcp.json`, and `context7` is a user-scope plugin. The list
  also auto-approves `<memory-server delete tools>`.

**P1-2. Running `hooks:install` before publishing would make the A09 delivery refuse.**
The handoff order (install, then publish) blocks publication. Evidence:
- `./dev/mise x -- hk --version` gives `hk 2.6.0`, and `git --version` gives `2.54.0`.
  `hk install --help` says: "Without `--global` … On Git 2.54+ this uses config-based hooks
  (`hook.<name>.command`), which keeps `.git/hooks/` untouched".
- `mise.dev.toml:343`: `hooks:install` runs `hk install --force-local`, so it writes local
  `hook.<name>.event|command` config for `pre-merge-commit` and `pre-push`.
- `dev/git_delivery.py:49-71` (`safe_configured_hooks`) admits only events
  `{pre-commit, commit-msg, pre-push}`. Anything else raises `"configured Git hook could
  execute during delivery"`, and a repeated field raises `"duplicate configured Git hook
  field"`. Global `hook.hk-pre-commit/commit-msg/pre-push` entries already exist in
  `~/.gitconfig`. `git config --get-regexp` lists both global and local entries, so a
  local `pre-merge-commit` event refuses, and a same-named local `hk-pre-push` would also
  hit the duplicate check.
- `hook_tree_digest` (lines 74-120) hashes the configured hooks, so any install also
  invalidates an intent's `hook_tree_sha256`.
- `dev/test_hooks.py` (`HkHooks`, lines 239-277) never runs delivery after
  `hooks:install`, and `test:delivery` never installs hk, so no test covers the two
  together.
- Action: publish via A09 first, then defer `hooks:install` until a ticket reconciles it
  with `git_delivery`. Options for that ticket: `hk install --force-local --legacy` (shims
  under the hashed `.git/hooks`, which delivery already bypasses through
  `core.hooksPath=/dev/null`), or admit `pre-merge-commit` in `safe_events` and handle
  duplicate section names.

### P2

**P2-1. Exactly one staged hunk is not from the lane.** For every staged path, the index
blob equals the `e12cf04` blob except `mise.dev.toml`: index `625569e`, lane `9793a0c`.
`git diff e12cf04 --cached -- mise.dev.toml` shows one hunk: `"test:hooks"` appended to
`[tasks."check:research"].depends` (line 117). Nothing else is foreign. The working tree
matches the index (`git diff --stat` is empty). This hunk is the parent's integration
action that the lane retro requested (retro line 20), and `.claude/rules/dev-tests.md`
routes tests through `check:research`. The merge commit message has to declare it,
because it makes the merge an evil merge. HEAD-side changes since merge-base `d0d6d4d`
touch only `task_plan.md` and `progress.md`, so there are no conflicts.

**P2-2. The merge commit is gated by nothing automatic.**
- hk layer 2 is not installed: `.git/hooks` has no non-sample files and
  `git config --get merge.ff` exits 1.
- A `--no-commit` merge followed by `git commit` never runs `pre-merge-commit`. The
  staged `claude-team.md` paragraph says so.
- `pretooluse_gate.py` only inspects `git merge`, `git push` and `delivery:publish`, not
  `git commit`. Dry run: `{"command":"git commit -m x"}` gives rc 0 and no output.
- `retro:gate -- gate-hooks` therefore has to be run by hand before the commit. Today it
  passes: `python3 -I dev/retro_gate.py --unit gate-hooks` prints
  `RETRO GATE PASSED … selectors: none`, rc 0.

**P2-3. The Claude Code hooks are already live in every session in this checkout.**
- `.claude/settings.json` exists in the working tree since 21:30Z, and the hooks docs say
  "Direct edits to hooks in settings files are normally picked up automatically by the
  file watcher". The review team and the repair session already run under them.
- `PreToolUse` (matcher `Bash`, timeout 10 s, `"onFailure": "block"`) spawns
  `python3 -I` on every Bash call. A python start failure or a timeout denies the call.
  `onFailure` has no effect on Stop and SubagentStop (docs).
- Dry runs in the current state: `git merge --continue` gives rc 0 and is allowed.
  MERGE_HEAD classifies as gate-hooks and its gate passes. `./dev/mise run
  delivery:publish` is also allowed with rc 0, and `stop_gate.py` gives rc 0 with no block.

**P2-4. The `gate-hooks` lane record is stale and incomplete.** It is staged from the lane.
- `base_sha` is `e618243`, but the first lane commit `0c2748e` has parent `2d1f60e`
  ("docs: allocate lane gate-hooks (CT-02)"), whose parent is `e618243`. The retro line 3
  value `2d1f60e` is the correct one.
- `status` is `"implemented (Opus), awaiting cold review"`, but the re-review passed per
  the evidence index (agent `a221b354…`).
- It has no `lane_commit`, `merged_head`, `review` or `retro` field.

**P2-5. `a06-unit3` claims `"retro": "passed"`, but its unit gate fails.**
`python3 -I dev/retro_gate.py --unit a06-unit3` exits rc 2 with "retro record missing:
…/retros/a06-unit3.md". The record lives at `retros/a06-classification-methods.md`, whose
gate exits rc 0. `git_gate` maps branch `claude/a06-unit3-classification-methods` to unit
`a06-unit3` through the lane record's `branch` field. Any later merge or push of that
branch, and SubagentStop in that worktree, would therefore refuse. Nothing blocks today
because `361688e` is published and pre-push only checks unpublished lane merges.

**P2-6. The only copies of the pre-merge `settings.json` are untracked or ephemeral.**
The backup's SHA-256 prefix is `ee3bc512820fd1257f9b`, identical in this review dir and
in `/private/tmp/…/464a2816-…/scratchpad/settings.json.before-ct02`. The review dir is
untracked and `/private/tmp` is ephemeral. `git merge --abort` removes the merged
`.claude/settings.json` and does not restore the earlier untracked file. The content is
recoverable from the union of the lane file and the local file (P1-1), but keep the
backup until the merge commit exists.

**P2-7. `base_sha` in lane records is systematically the pre-allocation tip.** The
"allocate lane" commit writes the record, so the record cannot hold its own SHA. In
nav, c1 and gate-hooks, `base_sha` is the allocation commit's parent, not the lane's true
base. The allocate commits exist: `2d1f60e` (gate-hooks), `c6ff7ef` (nav) and `ca60871`
(c1), plus `f039041` for retro-gate and team, whose lanes branched from `361688e`
directly. The convention should be redefined, or the field corrected after allocation.

### P3

- **P3-1. `.agent/` is untracked and not excluded** (`?? .agent/`). It holds the Codex
  takeover packet from 2026-10-10: `plans/codex-takeover-20261010{.md,.canonical.json,
  .canonical.sha256}`, decisions, `state/codex-takeover-20261010/*`, and
  `state/graph-first/*.queried` (48K in total). Committed
  `evidence/onboarding/source-hash-audit.json` refers to it by absolute path, and
  `findings.md:31` and `claude-takeover.md:8` name it as pre-existing. It is private
  evidence: keep it, do not commit it, and add `.agent/` to `.git/info/exclude`
  (`.gitignore` is frozen).
- **P3-2. The evidence index is wrong about `.agents/`.** It calls `.agents/skills`
  untracked, but `git ls-files .agents | wc -l` = 13, added in `762b02f`. Both
  `.agents/skills/codex-session-history` and `gh-stack` are identical to their
  `.claude/skills` counterparts (`diff -rq` is clean). This is the Codex mirror that
  `.claude/AGENTS.md:8-10` requires, and it is in place.
- **P3-3. Every integrated lane is already published, but statuses still say
  "publication pending".** The integration merges `361688e`, `55f3946`, `447110a`,
  `7e22d13`, `e618243`, `4c1ea6b` and `fa892d2` are all ancestors of
  `origin/codex/marketplace-native-onboarding` (`28fedf1`). Only three records have a
  `published` field.
- **P3-4. Top-level `additionalDirectories` (now in `settings.local.json`) is not a
  documented key.** The settings-reference index lists only
  `permissions.additionalDirectories`, so this entry is likely inert. It is kept
  verbatim; the user decides whether to move it.
- **P3-5. The handoff in `9cd396a` says "local tip = published remote `28fedf1`".**
  `9cd396a` is one commit ahead and unpushed: `git log origin/…..HEAD` = `9cd396a`.
  The branch has no upstream configured.
- **P3-6. Retro text drift.** retro-gate retro line 3 says "merged with tip `c8f4e64` as
  `0f7ddad`", the first sync. The final lane tip is `82c351f`, a merge of `9d478cd`.
  The team retro line 4 calls `9103931` the "lane commit", but it is a sync merge
  (parents `5107322 f039041`); the true lane commit is `5107322`. The c1 retro line 6
  says "merged with `e618243` as `7295463`", but `7295463` has parents `52ce420 2d1f60e`.
- **P3-7. Lane worktrees hold only ignored files** (`.venv/`, `.mise/`, `__pycache__/`).
  `git status --porcelain` is empty in all 8.
- **P3-8. 19 Codex worktrees under `~/.codex/worktrees/` share this Git dir.**
  `2a14` and `c658` hold uncommitted work. They are out of scope for removal.

## Settings split guidance (B)

Docs basis (https://code.claude.com/docs/en/settings):
- Scope table: Shared project `.claude/settings.json` is for "Team permissions, hooks,
  plugins, and the environment variables the project needs". Project local
  `.claude/settings.local.json` is for "Personal overrides for one project". User
  `~/.claude/settings.json` is for "Personal preferences … your own permission rules".
- "Commit `.claude/settings.json` so everyone who clones the repository gets the same
  permissions, hooks, and plugins."
- Precedence, highest first: managed > `--settings` > project local > shared project >
  user. "Lists merge instead of overriding … such as `permissions.allow` … Claude Code
  combines the lists".
- "`permissions.allow` rules, `permissions.additionalDirectories`, `extraKnownMarketplaces`
  … apply only after each teammate trusts the folder."
- `disableClaudeAiConnectors` honors `true` "from any scope".
- The settings-reference index gives every key involved scope "Any file".
- `enabledPlugins` combines across scopes in practice. This session loads user-scope
  plugins (last30days, context7) alongside project-scope plugins (mattpocock-skills,
  planning-with-files, eli5).

Decision for this repository:
- `$schema` and `hooks` are project. The hooks are the CT-02 deliverable and
  `.claude/AGENTS.md` defines the file as "shared project settings and hooks".
- `permissions` (the MCP allow-list) is personal and goes to local:
  - The servers are user-installed (context7 is a user-scope plugin, memory is not in
    the repo, and there is no `.mcp.json`).
  - `AGENTS.md` routes research through `fnox … exec`, not MCP.
  - Auto-approving `<memory-server delete tools>` is a personal risk choice.
  - The list merges anyway, so nothing is lost.
- `enabledPlugins` is split by whether the repository's standing workflow needs the
  plugin.
  - Project: `planning-with-files` (the PLAN_ID and `PWF_PLAN_ROOT` workflow),
    `mattpocock-skills` (grill-with-docs → … → retro), `mise@brentmitchell25` (the repo
    is mise-driven) and `astral@astral-sh` (uv/ruff/ty).
  - Local: `codex@openai-codex`, which needs a personal Codex CLI and account, and the
    personal conveniences `eli5`, `html-plan` and `next-steps`.
  - The `AGENTS.md` rule "do not install plugin runtimes just to lint" concerns the
    `aggregated-research` runtimes, not Claude Code plugins. `ci/acceptance.sh` runs its
    fresh sessions after `cd /tmp` (lines 42, 151), so project plugins do not affect
    acceptance.
- `extraKnownMarketplaces` follows its plugins, which closes review P3-1. A project file
  that enables plugins from undeclared marketplaces breaks on a fresh clone, so the four
  project plugins' marketplaces move to the project file. The source values are copied
  from `~/.claude/plugins/known_marketplaces.json`. `firecrawl`, `exa`, `last30days-skill`
  and `openai-codex` stay local; they serve user-scope or personal plugins.
- `additionalDirectories`, `prefersReducedMotion`, `switchModelsOnFlag`, `teammateMode`
  and `disableClaudeAiConnectors` go to local, kept verbatim (see P3-4).

The redistribution is exact: merging the two recommended files (minus `hooks`)
reproduces `settings.json.before-ct02` key for key.

Recommended `.claude/settings.json` (committed):

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "enabledPlugins": {
    "planning-with-files@planning-with-files": true,
    "mattpocock-skills@mattpocock": true,
    "mise@brentmitchell25": true,
    "astral@astral-sh": true
  },
  "extraKnownMarketplaces": {
    "planning-with-files": {"source": {"source": "github", "repo": "OthmanAdi/planning-with-files"}},
    "mattpocock": {"source": {"source": "github", "repo": "mattpocock/skills"}},
    "brentmitchell25": {"source": {"source": "github", "repo": "brentmitchell25/mise-plugin"}},
    "astral-sh": {"source": {"source": "github", "repo": "astral-sh/claude-code-plugins"}}
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/pretooluse_gate.py\"",
            "timeout": 10,
            "onFailure": "block"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/subagent_stop_gate.py\"",
            "timeout": 15,
            "onFailure": "block"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/stop_gate.py\"",
            "timeout": 10,
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

Recommended `.claude/settings.local.json` (untracked, excluded by `.git/info/exclude:8`):

```json
{
  "_redacted": "personal MCP allow-list (seven rules) omitted from the committed report (I3, 2026-10-13); the local file holds it",
  "enabledPlugins": {
    "codex@openai-codex": true,
    "eli5@claude-community": true,
    "html-plan@claude-community": true,
    "next-steps@claude-community": true
  },
  "extraKnownMarketplaces": {
    "firecrawl": {"source": {"source": "github", "repo": "firecrawl/firecrawl-claude-plugin"}},
    "exa": {"source": {"source": "github", "repo": "exa-labs/exa-mcp-server"}},
    "last30days-skill": {"source": {"source": "github", "repo": "mvanhorn/last30days-skill"}},
    "openai-codex": {"source": {"source": "github", "repo": "openai/codex-plugin-cc"}}
  },
  "additionalDirectories": [
    "<personal directory>"
  ],
  "prefersReducedMotion": true,
  "switchModelsOnFlag": true,
  "teammateMode": "auto",
  "disableClaudeAiConnectors": true
}
```

`claude-community` is declared in neither file. It is a user-known marketplace, which is
acceptable for a personal file.

Fallback if the user wants a minimal committed file: project = `$schema` + `hooks`
only, and everything else in local. That loses nothing either, but fresh clones and new
lane worktrees then get no workflow plugins.

Verification. Run from the repo root after writing both files; expect `settings split OK`
and rc 0:

```sh
python3 -I -c '
import json,subprocess
B=".planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/settings.json.before-ct02"
p=json.load(open(".claude/settings.json")); l=json.load(open(".claude/settings.local.json")); b=json.load(open(B))
lane=json.loads(subprocess.run(["git","show","e12cf04:.claude/settings.json"],capture_output=True,text=True,check=True).stdout)
assert set(p)=={"$schema","enabledPlugins","extraKnownMarketplaces","hooks"}, sorted(p)
assert set(l)=={"permissions","enabledPlugins","extraKnownMarketplaces","additionalDirectories","prefersReducedMotion","switchModelsOnFlag","teammateMode","disableClaudeAiConnectors"}, sorted(l)
assert p["hooks"]==lane["hooks"], "hooks drifted from the reviewed lane"
for k in ("enabledPlugins","extraKnownMarketplaces"): assert not set(p[k])&set(l[k]), k
assert {n.split("@")[1] for n in p["enabledPlugins"]} <= set(p["extraKnownMarketplaces"]), "project plugin without project marketplace"
m={k:v for k,v in p.items() if k!="hooks"}; m.update({k:v for k,v in l.items() if k not in ("enabledPlugins","extraKnownMarketplaces")})
for k in ("enabledPlugins","extraKnownMarketplaces"): m[k]={**p[k],**l[k]}
assert m==b, "split is not lossless"
print("settings split OK")'
git check-ignore -q .claude/settings.local.json && echo "local excluded"   # expect rc 0
```

Merge safety: keep `settings.json.before-ct02` (review dir and old scratchpad, SHA-256
prefix `ee3bc512820fd1257f9b`) until the merge commit exists and the check above passes.
The review dir is untracked, so A09 must not select it.

## Record corrections table

Integration merge SHAs come from `git log --first-parent --merges 9cd396a`. "True base"
is the parent of the lane's first own commit.

| Record | Field / line | Recorded | Git reality | Correct value |
| --- | --- | --- | --- | --- |
| lanes/gate-hooks.json | base_sha | e618243 | 0c2748e^ = 2d1f60e (allocate commit; its parent e618243) | `2d1f60e` (allocated from e618243) |
| lanes/gate-hooks.json | status | implemented (Opus), awaiting cold review | re-review PASS (a221b354…) | `integrated into codex/marketplace-native-onboarding (re-review PASS); publication pending`, set together with retro |
| lanes/gate-hooks.json | lane_commit / merged_head / review / retro | absent | 0c2748e, repairs dec8425; tip e12cf04 = merge of d0d6d4d | `0c2748e + repairs dec8425`; `e12cf04 (merge of d0d6d4d)`; review PASS-with-P2 → re-review PASS; `passed` after retro:gate rc 0 |
| lanes/gate-hooks.json | integration merge | n/a | not yet created | record in progress.md / the A09 commit (self-reference) |
| retros/gate-hooks.md | line 3 | base 2d1f60e | correct | optionally add "(allocated from e618243)" |
| retros/gate-hooks.md | line 5 | test_hooks.py 10 tests | 13 `def test_` now; line 33 says 13 | mark as pre-repair, or "13 after repair" |
| retros/gate-hooks.md | line 19 | five lane records lack retro passed | all have `"retro": "passed"` since 4870211 | mark resolved in 4870211 |
| retros/gate-hooks.md | line 20 | test:hooks not in check:research (owner parent) | staged at integration | "Applied at integration (mise.dev.toml check:research depends)" |
| retros/gate-hooks.md | line 33 | 13 tests rc 0 | consistent | no change |
| retros/gate-hooks.md | lines 36-37 | P3-1 extraKnownMarketplaces parent's decision; test:hooks out of check:research | decided / wired at integration | record the settings split (this file, section B) and the wiring |
| lanes/nav.json | base_sha | 7e22d13 | 5cadad4^ = c6ff7ef (allocate commit) | `c6ff7ef` (retro line 4 is correct) |
| lanes/nav.json | merged_head | 6840342 (merge of 937042d) | lane tip 6840342 = merge of 937042d; integration merge fa892d2 | field is right as lane tip; add `integration_merge: fa892d2` |
| lanes/c1-catalog-promotion.json | base_sha | 447110a | 52ce420^ = ca60871 (allocate commit) | `ca60871` (retro line 5 is correct) |
| lanes/c1-catalog-promotion.json | merged_head | 7295463 (merge of e618243); 6c09b7f | 7295463 = merge of 2d1f60e; lane tip 6c09b7f; integration 4c1ea6b | `6c09b7f (7295463 = merge of 2d1f60e)`; `integration_merge: 4c1ea6b` |
| retros/c1-catalog-promotion.md | line 6 | merged with e618243 as 7295463 | parents 52ce420 2d1f60e | "merged with 2d1f60e as 7295463" |
| lanes/retro-gate.json | merged_head | 82c351f (merge of 9d478cd) | lane tip correct; integration merge e618243 | add `integration_merge: e618243` |
| retros/retro-gate.md | line 3 | merged with c8f4e64 as 0f7ddad | first sync; final tip 82c351f (merge of 9d478cd) after repair 5ea8ee4 | append the final tip |
| lanes/team.json, retros/team.md:4 | lane_commit | 9103931 (on base 361688e) | 9103931 is a sync merge (5107322, f039041); lane commit 5107322 on 361688e; tip ea8c8c9; integration 7e22d13 | `5107322 + sync 9103931, 5becfc0 + repairs ea8c8c9`; add `merged_head: ea8c8c9`, `integration_merge: 7e22d13` |
| lanes/a06-unit3.json | retro | passed | `retro_gate --unit a06-unit3` rc 2 (record missing); record is a06-classification-methods.md (rc 0) | teach the gate a record alias, or rename/copy the record; until then the claim is false for the unit name |
| lanes/a06-unit3.json, codex-session-history, rf-env-scrub | integration merge | absent | 361688e, 55f3946, 447110a | add `integration_merge` |
| all integrated lanes | status | "… publication pending" | every integration merge is in origin 28fedf1 | `… published 28fedf1` (or f250f75 where earlier) |
| plan handoff (9cd396a) | tip claim | local tip = published 28fedf1 | HEAD 9cd396a unpushed | refresh at the next handoff |
| 00-evidence-index.md | untracked `.agents/skills` | untracked? | tracked (13 files, 762b02f) | tracked; mirror identical |

Ancestry. These branches are ancestors of HEAD `9cd396a`: claude/a06-unit3-classification-methods
`93402c0`, c1-catalog-promotion `6c09b7f`, codex-session-history-skill `ea893a8`,
nav-guidance-hierarchy `6840342`, retro-gate-task `82c351f`,
rf-env-scrub-inherited-selectors `281a198` and team-roles-rules `ea8c8c9`. Only
gate-hooks-wiring `e12cf04` is not.

Cleanup for later. Run only after the gate-hooks merge commit exists, is published, and
`git merge-base --is-ancestor claude/gate-hooks-wiring HEAD` exits 0. Do not run now.
The worktrees contain only ignored files, so a plain `remove` should succeed; if one
refuses, inspect `git -C <wt> status --porcelain` before reaching for `--force`.

```sh
for u in a06-unit3 c1-catalog-promotion codex-session-history gate-hooks nav retro-gate rf-env-scrub team; do git worktree remove ".claude/worktrees/$u"; done
git branch -d claude/a06-unit3-classification-methods claude/c1-catalog-promotion claude/codex-session-history-skill claude/gate-hooks-wiring claude/nav-guidance-hierarchy claude/retro-gate-task claude/rf-env-scrub-inherited-selectors claude/team-roles-rules
```

Before removing, decide whether the `a06-unit3` worktree's branch mapping (P2-5) needs
the branch to survive for a record fix. Leave the `~/.codex/worktrees/*` entries alone.

## Runbooks

Common preconditions for both runbooks:
- Run with `VIRTUAL_ENV` unset.
- Run from the source checkout, with one writer and no other worktree running named checks.
- Verify identity first:
  - `git rev-parse --show-toplevel` = `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`
  - `git branch --show-current` = `codex/marketplace-native-onboarding`
  - `git rev-parse HEAD` = `9cd396a…`
  - `git rev-parse MERGE_HEAD` = `e12cf04f22aa2c3d009e567f68081295de09f565`
  - `git rev-parse --git-dir` = `.git`

What the hooks do to the repairing session. They are live now through the file watcher
(P2-3).
- **PreToolUse** runs on every Bash call. It denies, with rc 0 and a deny JSON, a
  `git merge`, `git push` or `delivery:publish` segment whose lane fails
  `retro_gate.py`. While MERGE_HEAD is set, the merge source is gate-hooks, which passes.
  `git merge --abort` and `--quit` are exempt, and `git commit` is never checked. A
  python start failure or a timeout over 10 s denies the call (`onFailure: block`).
- **Stop** blocks once (then allows a continuation) when any `lanes/*.json` has a
  `status` containing "integrated" and `retro` ≠ "passed". Set both gate-hooks fields in
  the same edit. Today it does not block (rc 0, no output).
- **SubagentStop** blocks a subagent whose `cwd` is on a `claude/*` branch whose retro
  fails. The `a06-unit3` worktree would block (P2-5). Subagents working in the main
  checkout are never blocked.

### Runbook 1: complete the gate-hooks integration (recommended)

1. Preserve the current files: `cp .claude/settings.local.json "$SCRATCH/settings.local.json.pre-repair"` (rc 0).
2. Write both settings files exactly as in section B. Then run `git add .claude/settings.json` (rc 0)
   and the verification block (expect `settings split OK`, rc 0, and `local excluded`).
3. Edit `lanes/gate-hooks.json` per the table: `base_sha` 2d1f60e, `lane_commit`,
   `merged_head`, `review`, and `status` integrated with `retro` "passed" set together.
   The `retro` value is only true after step 5's retro:gate rc 0, so run step 5's
   `retro:gate` first if strict order matters. Edit `retros/gate-hooks.md` lines 5, 19,
   20 and 36-37 (line 3 optional). Then
   `git add .planning/2026-10-10-marketplace-macos-reflection-scaffold/lanes/gate-hooks.json .planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/gate-hooks.md` (rc 0).
4. Keep the staged `test:hooks` hunk in `mise.dev.toml` (P2-1); there is nothing to do.
5. Checks, all expected rc 0:
   - `./dev/mise tasks validate`
   - `./dev/mise run check`
   - `./dev/mise run check:acceptance-baseline` (19/19)
   - `./dev/mise run test:hooks` (13 tests; the hk class needs hk)
   - `./dev/mise x -- hk validate` (2.6.0), then `mise x hk -- hk validate` (2.5.0, the global-hook path)
   - `./dev/mise run retro:gate -- gate-hooks`
   - `./dev/mise run check:research` (it now depends on `test:hooks`; the wiring needs one green run)
   - `git diff --cached --check` and `git diff --check`

   Record each real rc.
6. Commit the merge: `git commit -F <msgfile>`, rc 0. The global hk pre-commit and
   commit-msg run; `hk.pkl` defines neither, so they are no-ops, as on the lane commits.
   The message must say:
   - it merges `claude/gate-hooks-wiring` at `e12cf04` (CT-02);
   - the extra parent-owned hunk adds `test:hooks` to `check:research`;
   - the settings composition is per R5 B;
   - the lane-record and retro corrections it carries;
   - the check rcs.

   End it with:
   ```
   Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
   Claude-Session: https://claude.ai/code/session_015qxgfYywpRPVMk8tYDLCHT
   ```
   Verify: `git log -1 --format='%P'` = `9cd396a… e12cf04…`; `test ! -e .git/MERGE_HEAD`;
   `git status --short` shows only `?? .agent/` and `?? …/reviews/`.
7. Publish via A09 before running `hooks:install` (P1-2). The intent pattern follows
   `publication/batch3`.
   1. `./dev/mise run delivery:inspect-hooks …` prints `hook_tree_sha256` (expected
      unchanged `a21be5fe…`, since nothing has been installed).
   2. Write the prepare intent with keys `root`, `common_dir`, `branch`,
      `head=<merge sha>`, `remote=origin`, `remote_url_sha256=477a17f8…`,
      `hook_tree_sha256` and `path=[".planning/…/progress.md"]`. Before that, add one
      progress line recording the integration merge SHA and the check rcs (A09 refuses
      an empty path list).
   3. Run `./dev/mise run delivery:prepare -- <intent> $(shasum -a 256 <intent> | cut -c1-64)`
      (rc 0, prints `index_tree`).
   4. Write the publish intent with `index_tree`, `message_file`, `gitleaks_bin` and
      `check_task=["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`.
   5. Run `./dev/mise run delivery:publish -- <intent> <sha256>`. Expect rc 0,
      `published=<sha>` and `history_scan_rc=0`. The PreToolUse hook re-gates the
      unpublished gate-hooks merge, which passes.
   6. Verify that `git log origin/codex/marketplace-native-onboarding..HEAD` is empty.
8. `hooks:install`: defer it. Open a ticket (the CT-02 follow-up) to reconcile `git_delivery.safe_configured_hooks` with
   hk config-based hooks, and record the deferral in the lane record and retro (owner:
   parent). If the user insists on installing now:
   - Run `./dev/mise run hooks:install` (rc 0), then confirm `git config --get merge.ff`
     prints `false` and `git config --local --get-regexp '^hook\.'` lists the hk entries.
   - Expect the next `delivery:inspect-hooks` or `delivery:prepare` to refuse with
     "configured Git hook could execute during delivery".
9. Retro gate for this integration task: add a row to the takeover retro
   (`retros/claude-takeover.md`) covering the merger-fork death, the settings decision
   and P1-2, per `docs/agents/ticket-retro.md`. Then update the plan handoff.

### Runbook 2: abort and redo

1. Run `git merge --abort` (rc 0). The hooks do not object, because `--abort` is exempt.
   It is equivalent to `git reset --merge`, with these effects:
   - Restores the index and every tracked path to `9cd396a`.
   - Deletes the 9 merge-added files from the working tree: `.claude/settings.json`,
     `dev/hooks/*.py`, `dev/test_hooks.py`, `hk.pkl` and `retros/gate-hooks.md`.
   - Reverts `lanes/gate-hooks.json`, `docs/agents/claude-team.md` and `mise.dev.toml`.
     The `test:hooks` line is staged only, so it is lost; it is one line to re-add.
   - Keeps untracked and ignored files: `.claude/settings.local.json`, `.agent/`, the
     reviews dir and `dev/hooks/__pycache__/`.
   - Does not restore the pre-merge untracked `settings.json` (P2-6).
   - Removes the project hooks, so subsequent sessions run without them.
2. In `.claude/worktrees/gate-hooks`, on lane branch `claude/gate-hooks-wiring`, apply
   the lane-owned fixes: the settings composition (`.claude/settings.json` is in the
   lane's `owned_paths`) and the retro lines. Run `test:hooks`, `retro:gate -- gate-hooks`
   and `git diff --check`, then commit. Get a focused re-review of the settings change.
3. In the main checkout, fix `lanes/gate-hooks.json` (parent-owned) in a docs commit,
   then `git merge --no-ff claude/gate-hooks-wiring` with no `--no-commit`. hk layer 2
   is still not installed, so run `retro:gate` by hand first.
4. Commit the `check:research` `test:hooks` wiring separately (parent-owned), then
   continue with Runbook 1 steps 5 and 7-9.

When Runbook 2 is preferable: the user wants a pure merge commit with no parent hunks;
the settings decision should be reviewed as lane content; or a step-5 check fails in a
way that needs lane code changes.

Risks:
- Runbook 1 makes an evil merge (parent edits inside the merge commit). That is
  acceptable if declared, and the records keep it traceable. The session works under
  live hooks throughout.
- Runbook 2 costs a re-review cycle and a new lane commit, which changes `merged_head`.
  It has the P2-6 window for the original settings file. It also has a short period
  with no project hooks, which is harmless.

## Could not verify

- The exact local config entries `hk install --force-local` writes; I did not run it.
  P1-2 rests on `hk install --help` (hk 2.6.0, Git 2.54) and `git_delivery.py:49-71`.
  Confirm in a scratch repository: run `hooks:install`, then
  `git_delivery.py inspect-hooks`.
- Detailed settings-reference entries for `enabledPlugins` and `extraKnownMarketplaces`,
  and the hooks-doc rule on workspace trust for project hooks: the pages were truncated
  in WebFetch. Object-merge of `enabledPlugins` between local and project is inferred
  from observed user-plus-project coexistence, not quoted.
- Whether `git worktree remove` refuses on ignored-only content. I expect it succeeds;
  not executed.
- `./dev/mise run check:research` and `test:hooks` with the staged wiring were not run
  (out of read-only scope). Nor were `./dev/mise run check` and `check:acceptance-baseline`
  on the merged tree.
- That the A09 route accepts a merge commit as `head`. The previous intents used linear
  heads; `git_delivery.py` was not read end to end.
- The focused re-review PASS for `e12cf04` comes from the evidence index (agent
  `a221b354ae209ba6a`); I did not read that transcript.

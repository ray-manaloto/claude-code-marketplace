# T2 — Import lane design: make the tip stop depending on unsaved Codex worktree data

Written 2026-10-13 by T2 (Claude subagent, Fable) against tip `9cd396a` with `MERGE_HEAD e12cf04`
in progress. Read-only on Git; new files only under `reviews/ccm-20261013/`, `lanes/`,
`proposals/claude-takeover-spec/` and `imports/codex-worktrees-20261013/`. Every path below is
relative to the repository root unless absolute; `P` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold`.

Inputs joined: `imports/codex-worktrees-20261013/{T1-snapshot-report.md,MANIFEST.json,T1-dependency-scan.json}`
(454 files, 11,814,946 B; 101 cited paths missing from the tip), `codex-sweeps/A-inventory.json`
(266 rows with disposition), `codex-sweeps/B-packet-and-t4-state.md`, `R3-codex-coverage.md` P1-1/P1-2,
`SYNTHESIS.md` §5/§6, `R8-parallel-plan.md`, `R4-pwf-audit.md`, the tip code named in the brief.
Machine-readable result: `P/imports/codex-worktrees-20261013/T2-import-plan.json` (295 rows, one per
file: `src` snapshot path, `dest` tip path, bytes, SHA-256, disposition, ignore rule, `git add` mode;
SHA-256 `d53fc622…`). Outputs of this design: this file, `T2-ct21-brief.md`,
`P/proposals/claude-takeover-spec/ticket-CT-21.preview.json`, `P/lanes/ct21-codex-imports.json`.

## Headline findings

1. **None of the 101 missing paths is blocked by the frozen `.gitignore`.** The repository
   `.gitignore` holds one line (`mise-oci/`); `.git/info/exclude` holds `.claude/worktrees/` and
   `.claude/settings.local.json`. `git check-ignore -v --no-index` attributes all 79 "ignored-data"
   paths to the **host's global excludes file**: `/Users/rmanaloto/.gitignore_global:34:*.log`
   (61 files) and `/Users/rmanaloto/.gitignore_global:23:build/` (18 files). They were never
   committed because Codex ran `git add` on a host whose global excludes hid them, not because of
   a repository rule. `git add -f` tracks them without touching `.gitignore`; five `*.log` files are
   already tracked under `evidence/` (`git ls-files evidence | grep -c '\.log$'` = 5), so the
   precedent exists. **CT-08 is not a prerequisite of CT-21.**
2. The 22 untracked-class paths (7 files + 15 directories in T1's table) resolve to **58 files,
   797,835 B** to import (sweep A's 68 "import" files minus 10 zero-byte lock artefacts) plus two
   files sweep A marked import that live under `P/` (`spec-11-amendment-candidate.{md,json}`).
3. **Gitleaks objects to nothing.** `gitleaks` 8.30.1 (the A09 binary at
   `~/.local/share/mise/installs/gitleaks/8.30.1/gitleaks`, built-in rules, `--redact=100`,
   `GITLEAKS_CONFIG*` unset as `dev/git_delivery.py:scan` does) in `dir` mode over the whole
   `2a14/untracked` snapshot (257 files, keep-private included), `2a14/ignored-data` (79 files)
   and the six snapshot index files: **0 findings, rc 0 each**. A09's `git` mode scans the same
   bytes as commit diffs with the same rules; it was not run (no commit exists), so the publish's
   `history_scan_rc` stays a receipt the lane records.
4. The one user-decision block that exists only in `2a14`
   (`docs/accepted-decisions.md` "Automation and observability clarification (2026-10-12)") applies
   cleanly: the tip blob is `5fc8c852…`, the diff's preimage.
5. `dev/codex_examples.py` does not fail *silently* today: a missing schema surfaces as
   `{"status": "unresolved", "reason": "[Errno 2] No such file or directory: …"}` rc 2, the same
   status and exit as a provider failure. The fix is a distinct exit (3) and a message that names
   the path and the import ticket.

## a. Classification of the 101 missing paths

Join key: T1 row `ref` → MANIFEST `rel_path` (2a14, class ≠ modified) → sweep A `rel`. Counts by
T1 kind: 86 files + 15 directories; by MANIFEST class: 22 untracked-class refs (7 files, 15 dirs
→ 68 files) and 79 ignored-data files. Full per-file tables are appended at the end of this
document (§ Appendix); summary:

| Class | T1 refs | Files | Bytes | Disposition | Destination | git add |
|---|---|---|---|---|---|---|
| (i) code inputs read by `dev/*.py` | 5 refs: `evidence/codex-examples{,/release,/release/config-schema.json,/runs}`, `evidence/saved-searches/runs` (+ `evidence/saved-searches` default output of `search_catalog.py:359`, `collect_saved_search.py:251`) | 45 files (5 + 40) | 607,325 | **import** (35 data files + the schema) / **exclude** 10 zero-byte locks | same paths | plain |
| (ii-a) evidence cited by tracked retros, `task_plan.md:322`, `progress.md` → **import** | `evidence/github-search-one-page` (+3 run dirs), `evidence/git-delivery` (2 of 3 files), `evidence/issue-publication-private/{graph-audit.json,edges/local-edge-receipt.json}`, 3 `docs/agents/*.md`, `P/spec-11-amendment-candidate.{md,json}` (A07b hash-bound) | 23 files | 190,510 | **import** | same paths (`spec-11-*` stay under `P/`) | plain |
| (ii-b) cited but **keep-private** | `evidence/claude-amendment-review/` (progress.md:1977; also cited by the imported `automation-amendment-review.md`), `evidence/git-delivery/initial-outbound-gitleaks-redacted.json` (progress.md:2514) | 54 files | 2,528,001 | **keep-private** (mirror) | private mirror `/Users/rmanaloto/.local/state/marketplace-imports/codex-worktrees-20261013/2a14/untracked/<path>` (mode 0700), declared in `dev/cited-inputs.json` | none |
| (ii-c) not cited individually, keep-private | the other 94 `evidence/issue-publication-private/**` files (17 `A*.intent.json` of 210–240 KB with full issue bodies, `edges/` intents/attempts/bindings) | 94 files | 3,841,149 | **keep-private** (mirror) | same mirror | none |
| (ii-d) superseded (sweep A) | `dev/claude_review.py`, older drafts of `codex_examples.py`/`test_codex_examples.py`, `ticket-retro.md`, `.a04-e97ftai5/` (incl. the `.pending-*` quarantine markers T1 flags from `dev/test_search_catalog.py:149,153`: those are names the test *creates*, not inputs), `c658` copies | 49 files | — | **superseded**: nothing to import; stays in the snapshot/mirror as history | — | none |
| (iii) ignored-data hashed by tracked operation manifests | 61 `*.log` under `evidence/{core-p2996 (2), mise-runtime (8), p2996-cmake (2), vcpkg-fmt-build (49)}` | 61 | 259,365 | **import** (rule: `~/.gitignore_global:34:*.log`, host-only) | same paths | `git add -f` |
| (iii) ignored-data, build tree | 18 `evidence/iwyu-build/operation/build/**` (CMakeCache, CMakeFiles/4.4.4/*, `CMakeConfigureLog.yaml` 636 KB, `build.ninja`, `compile_commands.json`, …) | 18 | 849,093 | **mirror** (rule: `~/.gitignore_global:23:build/`; a derived CMake tree, 77 % of the ignored bytes; the manifest already records each SHA-256) — flip to import with `git add -f` if the user prefers a self-contained tree | mirror, declared | none (or `-f`) |

Totals: **import 119 files / 1,057,200 B** (58 untracked-class + 61 logs), **exclude 10** (0 B),
**mirror 18 / 849,093 B**, **keep-private 148 / 6,369,150 B** in `2a14` (+ the `c658`
`.codex/schemas/codex-0.162.1-agent-role.schema.json`, 238,961 B, keep-private until its lane is
admitted — sweep A). Every import row's SHA-256 was re-hashed from the snapshot copy during this
design (0 mismatches; all 40 JSON files parse, which `dev/check.py` will require once they are
tracked). The 10 excluded files are `evidence/saved-searches/locks/{codex-schema,codex-config-examples,codex-hook-examples}.lock`
and seven `runs/*/.writer.lock` (all `e3b0c442…`, empty): `search_catalog.py:276` creates the query
lock on demand and `:212` consults `.writer.lock` only when `manifest.json` is absent (every
imported run has one), so they carry no information and would be runtime noise in Git.

Why `(i)` must be tracked and not mirrored: `dev/codex_examples.py` reads the schema (`:25,:111,:244`)
and the saved-search runs (`:106,:220`) at the *tip's* paths; `research:examples`/`test:examples`
are the A06 #69 acceptance; the ledger row #69 says "retained-corpus consumption still open".
Why `(ii-a)`: `retros/A02.md:3`, `A03a.md:3`, `A04.md:3` cite the captures as their evidence;
`retros/A07b.md` binds `5dfc7a31…` = SHA-256 of `spec-11-amendment-candidate.md`; sweep B's closure
rows for #63–#68, #71, #72/#73, #74 name these exact files as hash-bound inputs that "live only in
`2a14`". Why `(ii-b)` stays private: `.claude/rules/evidence.md` ("no … transcripts"): the four
`events.jsonl` are raw native stream-json session captures with full message text; the gitleaks
report carries author/e-mail/commit metadata for 225 redacted findings. Both already have a
recorded SHA-256 (MANIFEST.json; sweep A) and live in the 0700 mirror, which satisfies the
invariant in §f without tracking them.

A09 outbound scan: 0 findings over the import set and the keep-private set (headline 3). The
earlier `2a14` rc 1 scan (225 `generic-api-key` hits on digest fields) was over commit history
including `evidence/issue-29-context7/measurement.json`, adjudicated in
`evidence/completion-workflow/offline-followup-scan-adjudication.json`; none of the import files
has a `*api*`/`*key*`/`*token*`-named field with a ≥10-character value (the receipts' hash fields are
`*_sha256`, `credential_route` values are ≤ 6 characters), which is why dir mode is clean.

## b. Code changes (unified-diff-style; not applied)

### b.1 `dev/codex_examples.py` — loud failure on a missing tracked input

Keep the `ROOT / "…"` call-site expressions (the hermetic tests patch `ROOT` and `SCHEMA`);
add one guard and one exit code. Exit 3 = "a tracked input is absent"; 2 stays "unresolved".

```diff
@@ -22,6 +22,7 @@
 from github_search_one_page import API_VERSION, credential
 from search_catalog import ROOT, RUN, confined, digest, encoded, verified_run

 SCHEMA = ROOT / "evidence/codex-examples/release/config-schema.json"
 SCHEMA_SHA256 = "7933a70506e753a6e98c16800d2a76770b2af2b7295491f8f0b8e713e952027e"
+IMPORT_TICKET = "CT-21"
 RELEASE_COMMIT = "092d3acd6bec3e3a14bdc7e7a2810ab628ab759d"
@@ -33,6 +34,20 @@
 class BlobError(ValueError):
     """A requested full blob does not match its pinned Git object identity."""

+
+class MissingInput(BlobError):
+    """A tracked input the tip depends on is absent; nothing was substituted or retried."""
+
+
+def required_input(path: Path, *, kind: str) -> Path:
+    """Confine, then refuse loudly when the tracked input is not in the tree."""
+    candidate = confined(path)
+    if not candidate.exists():
+        relative = candidate.relative_to(ROOT) if candidate.is_relative_to(ROOT) else candidate
+        raise MissingInput(f"missing tracked input ({kind}): {relative}; import it under "
+                           f"{IMPORT_TICKET} or run ./dev/mise run check:inputs")
+    return candidate
+
@@ -103,7 +118,7 @@ def run(args: argparse.Namespace) -> dict[str, object]:
     match = RUN.fullmatch(args.run_id)
     if not match:
         raise BlobError("invalid saved-search run ID")
-    entry = confined(ROOT / "evidence/saved-searches/runs" / args.run_id)
+    entry = required_input(ROOT / "evidence/saved-searches/runs" / args.run_id, kind="saved-search run")
     if entry.is_symlink() or not entry.is_dir():
         raise BlobError("missing or symlinked saved-search run")
     manifest_bytes = confined(entry / "manifest.json").read_bytes()
     manifest, normalized = verified_run(entry, match, manifest_bytes)
-    schema_bytes = confined(SCHEMA).read_bytes()
+    schema_bytes = required_input(SCHEMA, kind="release schema").read_bytes()
@@ -218,7 +233,7 @@ def offline(args: argparse.Namespace) -> dict[str, object]:
     receipt = json.loads(receipt_bytes)
-    entry = confined(ROOT / "evidence/saved-searches/runs" / args.run_id)
+    entry = required_input(ROOT / "evidence/saved-searches/runs" / args.run_id, kind="saved-search run")
     manifest_bytes = confined(entry / "manifest.json").read_bytes()
@@ -243,7 +258,7 @@
         raise BlobError("invalid offline normalized budget or coverage")
-    schema_bytes = confined(SCHEMA).read_bytes()
+    schema_bytes = required_input(SCHEMA, kind="release schema").read_bytes()
     schema = json.loads(schema_bytes)
@@ -332,6 +347,9 @@ def main() -> int:
         print(json.dumps(offline(args) if args.offline_receipt is not None else run(args), sort_keys=True))
         return 0
+    except MissingInput as error:
+        print(json.dumps({"status": "missing_input", "reason": str(error)}), file=sys.stderr)
+        return 3
     except RequestError:
```

Ordering keeps the existing symlink test green: `confined()` runs before the existence test, so a
symlinked schema still yields `symlinked project path refused` rc 2. The `offline` receipt path
(`--offline-receipt`) is user-supplied and keeps `confined` + the existing `receipt_path.name` checks.
`docs/agents/codex-example-classification.md` gains one sentence after the invocation block:
"Exit 3 means a tracked input named in the message is absent from the checkout; `./dev/mise run
check:inputs` lists every such path." (owned-path line in the lane record).

### b.2 `dev/test_codex_examples.py` — keep the hermetic fixture, add real-input and exit-3 tests

```diff
@@ -20,6 +20,7 @@
 from codex_examples import BlobError, collect_blobs, decode_blob
 import codex_examples
-from search_catalog import ROOT, digest, encoded
+from search_catalog import ROOT, RUN, digest, encoded, verified_run
+
+CITED_INPUTS = ROOT / "dev/cited-inputs.json"
@@ (append at end of file, before any __main__ guard)
+
+class TrackedInputTests(unittest.TestCase):
+    """The real tracked inputs exist and match the pinned manifest; nothing is patched."""
+
+    def setUp(self):
+        self.pinned = json.loads(CITED_INPUTS.read_bytes())
+        self.rows = {row["path"]: row for row in self.pinned["inputs"]
+                     if any(c.startswith("dev/codex_examples.py") for c in row["cited_by"])}
+
+    def test_release_schema_is_tracked_and_pinned(self):
+        self.assertTrue(codex_examples.SCHEMA.is_file(), codex_examples.SCHEMA)
+        data = codex_examples.SCHEMA.read_bytes()
+        self.assertEqual(digest(data), codex_examples.SCHEMA_SHA256)
+        row = self.rows[str(codex_examples.SCHEMA.relative_to(ROOT))]
+        self.assertEqual((row["sha256"], row["bytes"], row["location"]),
+                         (codex_examples.SCHEMA_SHA256, len(data), "tree"))
+        self.assertEqual(json.loads(data).get("title"), "ConfigToml")
+
+    def test_cited_saved_search_runs_verify_without_patching(self):
+        runs = [p for p in self.rows if p.startswith("evidence/saved-searches/runs/")]
+        self.assertGreaterEqual(len(runs), 9)
+        for relative in runs:
+            with self.subTest(run=relative):
+                entry = ROOT / relative
+                match = RUN.fullmatch(entry.name)
+                self.assertIsNotNone(match)
+                manifest_bytes = (entry / "manifest.json").read_bytes()
+                self.assertEqual(digest(manifest_bytes), self.rows[relative]["manifest_sha256"])
+                verified_run(entry, match, manifest_bytes)  # raises on digest or identity drift
+
+    def test_missing_tracked_input_exits_3_and_names_the_path(self):
+        temporary = tempfile.TemporaryDirectory(prefix=".a06-missing-", dir=ROOT)
+        self.addCleanup(temporary.cleanup)
+        root = Path(temporary.name)
+        stdout, stderr = StringIO(), StringIO()
+        run_id = "examples--1791838915397532000--b666ae4cd38ff2a3"
+        with patch.object(sys, "argv", ["examples", run_id, "--sha", "f" * 40]), \
+             patch.object(codex_examples, "ROOT", root), \
+             patch.object(codex_examples, "credential", side_effect=AssertionError("credential lookup")), \
+             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
+            code = codex_examples.main()
+        self.assertEqual((code, stdout.getvalue()), (3, ""))
+        reason = json.loads(stderr.getvalue())
+        self.assertEqual(reason["status"], "missing_input")
+        self.assertIn(f"evidence/saved-searches/runs/{run_id}", reason["reason"])
+        self.assertIn("CT-21", reason["reason"])
```

`dev/cited-inputs.json` rows for saved-search runs carry `manifest_sha256` (the run's
`manifest.json` digest, which `verified_run` then extends to `raw.json`/`normalized.json`); the
schema row carries the file digest. `test:examples` already runs this file under `uv run
--offline`, so the new class reaches `check:research` with no task change.

### b.3 `dev/checkout_transfer.py` — no host path in the source

```diff
@@ -13,10 +13,11 @@
 import sys
 import time

-SOURCE = Path("/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace")
-OLD = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
+SOURCE = Path(__file__).resolve().parents[1]
+OLD_ENV = "MARKETPLACE_OLD_WORKTREE"
 BRANCH = "codex/marketplace-native-onboarding"
@@ -178,6 +179,10 @@ def probe(source: Path) -> dict[str, str]:
 def plan(args: argparse.Namespace) -> dict[str, object]:
+    if args.old is None:
+        raise Refusal(f"old worktree not given: pass --old <path> or set {OLD_ENV}")
+    if Path(args.old).is_symlink() or not Path(args.old).is_dir():
+        raise Refusal(f"old worktree is not a directory: {args.old}")
     source, old = Path(os.path.abspath(args.source)), Path(os.path.abspath(args.old))
@@ -266,7 +271,8 @@ def main() -> int:
     parser.add_argument("--source", type=Path, default=SOURCE)
-    parser.add_argument("--old", type=Path, default=OLD)
+    parser.add_argument("--old", type=Path,
+                        default=(Path(os.environ[OLD_ENV]) if os.environ.get(OLD_ENV) else None))
```

`dev/test_checkout_transfer.py` already passes `--old` explicitly (`:57-58`); add one test that
runs `plan` with no `--old` and `MARKETPLACE_OLD_WORKTREE` removed from the environment and asserts
rc 2 with `A10 refused: old worktree not given: pass --old <path> or set MARKETPLACE_OLD_WORKTREE`.
`identity()` keeps refusing a missing or symlinked root, so the new guard only improves the message.

### b.4 New `dev/check_inputs.py` + `dev/cited-inputs.json` + `dev/test_check_inputs.py`

Not an extension of `dev/check.py`: CT-11 owns `dev/check.py` in wave 1 (R8 conflict table) and
the hosted workflow calls `dev/check.py` directly; a sibling script reached by a task and one CI
step avoids the only hot file. Contract:

- `python3 -I dev/check_inputs.py [--root DIR] [--json]` exits 0 when every cited path is
  satisfied, 1 with one line per failure on stderr: `missing: <path> (cited by <file>:<line>)`,
  `drift: <path> expected <sha256[:16]> got <…> (cited by …)`, `undeclared mirror: <path>`; 2 on a
  malformed manifest. Stdout: a JSON summary `{checked, tree, mirror, missing, drift}`.
- Citation sources (bounded, deterministic): (1) `P/retros/*.md`: backticked relative paths
  starting with `evidence/`, `dev/`, `docs/`; (2) every `evidence/**/*.json` that is tracked:
  any object carrying both `path` (string starting with `evidence/`) and `sha256` (64 hex) is a
  hash-bound citation (this covers `operation-manifest.json`, `*-manifest.json`,
  `artifact-secret-scan.json`, `closure-secret-scan.json` map form `{path: sha256}` is handled as
  a second shape: keys starting with `evidence/` whose values are 64-hex); (3) `dev/cited-inputs.json`
  `code_defaults`: `{file, literal}` rows — the checker asserts the literal still occurs in the
  file (drift of a default is a failure) and that the path exists; (4) `dev/cited-inputs.json`
  `inputs` rows themselves. `progress.md`, `findings.md`, `task_plan.md` and `docs/**` prose are
  **not** sources (append-only history and absolute links; the parent rewrites the four 2a14
  links by hand after CT-21, §e).
- Resolution: a path is satisfied when it exists in the tree (file or directory) and, when a
  sha256 is cited, the bytes match; or when `inputs` declares it with `location: "mirror:<id>"`
  and the same sha256 — then, if `mirrors[<id>].root` exists on this host, the mirror copy is
  hashed too (CI has no mirror; the declaration suffices there). A cited path with neither is a
  failure. Directories cited without a hash are satisfied by existence (tree) or declaration (mirror).
- `--sync-from-manifest <MANIFEST.json> --mirror <id>` rewrites only the `inputs` rows whose
  `location` names that mirror from the T1 manifest (bytes, sha256); it never adds a mirror or
  changes a `tree` row (declaring a mirror is a human edit reviewed in the lane).

`dev/cited-inputs.json` schema (version 1):

```json
{
  "version": 1,
  "mirrors": {
    "codex-worktrees-20261013": {
      "root": "~/.local/state/marketplace-imports/codex-worktrees-20261013",
      "manifest": ".planning/2026-10-10-marketplace-macos-reflection-scaffold/imports/codex-worktrees-20261013/MANIFEST.json",
      "manifest_sha256": "259f9fae40ecf99cad4cb26c4f9a6dad4243f5b02746c6fd01bc388f95329c32",
      "layout": "<root>/2a14/{untracked,ignored-data}/<path>"
    }
  },
  "code_defaults": [
    {"file": "dev/codex_examples.py", "literal": "evidence/codex-examples/release/config-schema.json", "mode": "read"},
    {"file": "dev/codex_examples.py", "literal": "evidence/saved-searches/runs", "mode": "read"},
    {"file": "dev/codex_examples.py", "literal": "evidence/codex-examples/runs", "mode": "read-write"},
    {"file": "dev/search_catalog.py", "literal": "evidence/saved-searches", "mode": "write"},
    {"file": "dev/collect_saved_search.py", "literal": "evidence/saved-searches", "mode": "write"},
    {"file": "dev/github_search_one_page.py", "literal": "evidence/github-search-one-page", "mode": "write"}
  ],
  "inputs": [
    {"path": "evidence/codex-examples/release/config-schema.json", "bytes": 236751,
     "sha256": "7933a70506e753a6e98c16800d2a76770b2af2b7295491f8f0b8e713e952027e",
     "location": "tree", "cited_by": ["dev/codex_examples.py:25", "progress.md:2373"]},
    {"path": "evidence/saved-searches/runs/codex-schema--1791836388445290000--8385f42d6953e0ab", "kind": "dir",
     "manifest_sha256": "ce45d2a319ec…", "location": "tree",
     "cited_by": ["dev/codex_examples.py:106", "retros/A03a.md:3", "progress.md:2237"]},
    {"path": "evidence/iwyu-build/operation/build/CMakeCache.txt", "bytes": 23612,
     "sha256": "e5cda049bce7f301432dde5c3bc3732cf27734a505635cc6217859bfe74e390d",
     "location": "mirror:codex-worktrees-20261013", "cited_by": ["evidence/iwyu-build/operation-manifest.json:216"]},
    {"path": "evidence/claude-amendment-review", "kind": "dir", "files": 53, "bytes": 2308070,
     "sha256": "584494a4…a07 (sweep A directory hash: SHA-256 over sorted '<sha>  <path>' lines)",
     "location": "mirror:codex-worktrees-20261013", "cited_by": ["progress.md:1977", "docs/agents/automation-amendment-review.md"]},
    {"path": "evidence/git-delivery/initial-outbound-gitleaks-redacted.json", "bytes": 219931,
     "sha256": "685cc05735d4…", "location": "mirror:codex-worktrees-20261013", "cited_by": ["progress.md:2514"]}
  ]
}
```

(`mode: write` defaults are listed for completeness and are not required to exist.) Rows: 119
`tree` imports are *not* listed one by one — they are found by sources (1)–(3) and verified by the
manifests that cite them; `inputs` lists the code inputs (schema + 9 runs), the 18 mirror files,
the two cited keep-private items and the `c658` schema (mirror). Tests (`dev/test_check_inputs.py`,
fixtures under `dev/fixtures/inputs/`: a mini tree with one manifest, one retro, one manifest-cited
file present, one absent, one hash-drifted, one mirror-declared with a fake mirror root): rc and
stderr lines per case, through the CLI (`.claude/rules/dev-tests.md`: seam tests, `-I`).

### b.5 Task wiring (`mise/tasks/ct21.toml`, lane-owned; parent hunk in `mise.dev.toml`)

```toml
# mise/tasks/ct21.toml (new; listed by the wave-0 [task_config] includes)
[tasks."check:inputs"]
description = "Every path cited by a tracked retro, evidence manifest or code default exists in the tree or is declared in a private mirror with its SHA-256"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I dev/check_inputs.py'

[tasks."test:check-inputs"]
description = "Exercise the cited-inputs checker on fixtures"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I -m unittest discover -s dev -p test_check_inputs.py -v'
```

```diff
# mise.dev.toml — parent hunk, declared in the integration commit message (R8 integration step 4)
 [tasks."check:research"]
-depends = ["test:bootstrap", …, "test:codex-session-history", "test:hooks"]
+depends = ["test:bootstrap", …, "test:codex-session-history", "test:hooks", "test:check-inputs", "check:inputs"]
 [tasks.check]
 description = "Parse project manifests and scripts without installation or network access"
 dir = "{{config_root}}"
+depends = ["check:inputs"]
 run = '"${MARKETPLACE_PYTHON:-python3}" dev/check.py'
 [tasks."check:acceptance-baseline"]
+depends = ["check:inputs"]
```

`dev/check.py` itself: after CT-11 integrates, one line in the sub-check loop
(`run(sys.executable, "-I", "dev/check_inputs.py")`) so `python3 -B dev/check.py` in
`development.yml` covers it too; until then the lane adds a workflow step:

```diff
# .github/workflows/development.yml (lane-owned, one step)
         run: python3 -B dev/check.py
+      - name: Cited inputs exist or are declared
+        run: python3 -I dev/check_inputs.py
```

### b.6 `docs/accepted-decisions.md` — the `2a14`-only user-decision block (parent, Runbook step 7)

Preimage blob `5fc8c852632354344146199b43bade230b4e1af3` = tip; applies with `git apply`.
The second hunk (`## Compiler and build foundation` first bullet reworded to "The earlier qualified
host setup used global mise installations …") travelled with the same `2a14` edit; sweep A lists
it as part of the block ("+1 line at @@ -30 +83"). It is included below but flagged: confirm with
the user that the rewording is theirs, not Codex's paraphrase, before applying hunk 2.

```diff
--- a/docs/accepted-decisions.md
+++ b/docs/accepted-decisions.md
@@ -16,6 +16,59 @@ This record consolidates the user's decisions from the originating chat as of 20
 - The private feature and private-document bytes are excluded. Its research aggregator and generated plugin are candidate consumers after this foundation; this is not permission to edit that other checkout. Private uploads require a per-run destination choice. Mutating tools belong in an explicit opt-in profile.
 - Global Python interpreter promotion and local OpenTelemetry Collector work are separate accepted streams. Carry forward their ownership boundaries; do not absorb or duplicate them in marketplace onboarding.

+## Automation and observability clarification (2026-10-12)
+
+- Humans, coding agents and CI/CD use the same named mise tasks with the same
+  parameters. Repeatable operations belong in reusable Python/C++ library
+  code behind those tasks, reached by thin host-specific skills. Direct
+  read-only inspection and native agent communication are allowed; manual
+  operational commands must not replace the repeatable automation.
+- All Python invocations and CMake build operations go through named mise
+  tasks. Declare the minimal Python support and its dependencies in project
+  `pyproject.toml` and mise dependency configuration. The project must build
+  without relying on user/global mise configuration. Prefer moving reusable
+  implementation into the C++26 reflection core as it becomes qualified.
+- C++ namespaces use `com::rsm::<module>`. Dotted module/package identifiers
+  may use `com.rsm.<module>`; dots are not C++ namespace separators.
+- Check latest stable dependency releases during each update unit, then lock
+  exact versions/source identities and qualify them before adoption. A new
+  reflection-fork revision is a qualification candidate, not an automatic
+  replacement for an established compiler/runtime witness.
+- Default telemetry is structured output in a directory, with secret/content
+  redaction. Integrate available native Claude, Codex and Antigravity signals.
+  Use one shared OpenTelemetry Collector on the Mac, owned by user/global mise
+  under `~/.config/mise/`; projects add support there when needed instead of
+  creating their own collector. Remote export requires a selected destination.
+  This clarification does not establish current collector or host-signal
+  availability. Write under `~/.local/state/otel/`, separated by service and
+  project, with rotation and configurable retention defaulting to 30 days.
+  Signal-specific acceptance remains to be qualified.
+- Cover macOS ARM64, Linux ARM64 and Linux x86-64 in the generated support
+  matrix. Report unsupported combinations explicitly; upstream availability
+  and compilation alone do not establish runtime qualification.
+- Run relevant fast formatting, lint and schema checks in hk pre-commit,
+  including cmake-format. Post-commit verifies and records without changing
+  committed files. Expensive compiler, sanitizer and Valgrind checks use
+  explicit pre-push/CI profiles through the same named mise tasks.
+- Use official in-file schema declarations where valid, otherwise external
+  association and exact-version native validation. Prefer Codex release
+  schema assets matching the installed version. Keep config, hook-file and
+  hook-protocol schemas distinct; unsupported extra fields must not be added.
+- Build the project-owned, locked GitHubKit saved-search/replay task before
+  further build-design implementation. Compare reusable behavior from
+  knowledge-base, dotfiles and `<TR>` without changing those
+  projects. Use the unified task to find Codex release-schema usage examples.
+- Amend spec #11 and its existing dependency graph. Version intentional
+  acceptance-baseline transitions with reviewed compatibility checks; retain
+  the original 19-file preservation receipts and completed-unit evidence.
+- Combine native blocking hooks for supported calls, read-only command-guard
+  review and CI checks of the shared mise commands. Document and test each
+  host's coverage; do not claim every action can be intercepted.
+- The unified GitHubKit task must pass deterministic offline replay, saved
+  query/provenance, pagination and rate-limit tests plus a bounded live
+  Codex-schema search. Unexpected empty results use a bounded same-capability
+  known-result control; a failed control yields unverified, not a success.
+
 ## Native data and runtime design

 - Canonical common schemas initially feed the existing Python generator and the C++ candidate; preserve datamodel-code-generator as a baseline and gap detector until behavior parity. Eventually replace that functionality in C++26.
@@ -27,7 +80,7 @@ This record consolidates the user's decisions from the originating chat as of 20

 ## Compiler and build foundation

-- Global mise owns tool installations; named p2996 and gcc16 profiles isolate the selected compilers. Preserve the current default compiler for unrelated work.
+- The earlier qualified host setup used global mise installations and named p2996/gcc16 profiles. Portable project declarations and tasks now supersede reliance on those global profiles; retain their historical receipts and preserve the default compiler for unrelated work. The shared Mac collector remains explicitly owned by global mise.
 - Latest stable GCC is the intended GCC lane; the inspected starting point is 16.2.0 via native mise Homebrew bootstrap. Re-attest actual package identity/patches at installation.
```

The verbatim diff (both hunks) is also in the snapshot:
`P/imports/codex-worktrees-20261013/2a14/modified/docs/accepted-decisions.md.diff`.

## c. The ticket, ledger row, task_plan entry, findings bullets

**Ticket** — `P/proposals/claude-takeover-spec/ticket-CT-21.preview.json` (new file; entry shape
identical to `tickets.preview.json`, body produced by `build_manifests.py`'s `ticket_body`,
`body_sha256 b03064b1…`, parent `#999999` placeholder). Title: *CT-21: Import Codex worktree inputs
and cited evidence; fail closed on missing inputs*. Blocked by: none. The file's `edges` object
lists what it unblocks (#69, #63–#66, #68, #71–#74 closure rows; the CLOSE lane; D9 worktree
removal; the four tracked `2a14` absolute links). To publish it, append the tuple to `TICKETS` in
`build_manifests.py` and rebuild `tickets.v2.json` with the real parent number (Runbook step 11).

**`ticket-ledger.md` row** (append under the last `#108` row; GitHub number to fill at creation):

```markdown
| CT-21 (pending issue) | CT-21: Import Codex worktree inputs and cited evidence; fail closed on missing inputs | CT-SPEC (pending) | — | READY | — | ct21-codex-imports (allocated-pending-merge) | designed: reviews/ccm-20261013/T2-import-lane-design.md; imports 119 files (1,057,200 B) from imports/codex-worktrees-20261013 (MANIFEST 259f9fae…); unblocks #69 and the #63–#68/#71–#74 closure rows |
```

and amend the `#69` row's local state: replace `retained-corpus consumption still open` with
`corpus/schema import = CT-21 (evidence/codex-examples, evidence/saved-searches); consumption after it integrates`.

**`task_plan.md` entry** (R4 skeleton; two places):

```markdown
### Phase 5: Remaining lanes (B1, C2/C3, LEDGER, CLOSE, wave 1–2, heavy)
- [ ] CT-21 ct21-codex-imports: import the 2a14 inputs the tip cites (119 files), `check:inputs`, exit-3 on missing inputs — blocks the A-series CLOSE rows and D9 worktree cleanup
- **Status:** pending

## Tickets
| Ticket | Title | GitHub | Lane | State |
| CT-21 | Import Codex worktree inputs and cited evidence; fail closed on missing inputs | pending issue | ct21-codex-imports | designed (T2, 2026-10-13); allocation after the gate-hooks merge |

## Lanes
| Lane | Unit | Tickets | Worktree @ SHA | status | retro |
| ct21-codex-imports | CT-21 | CT-21 | .claude/worktrees/ct21-codex-imports @ TBD-at-cut | allocated-pending-merge | pending |
```

and replace `task_plan.md:11-12` ("The detached `/Users/rmanaloto/.codex/worktrees/2a14/…` retains
its uncommitted work and private evidence. Do not reset or archive it.") with:

```markdown
The `2a14`/`c658` worktree data is snapshotted (imports/codex-worktrees-20261013, MANIFEST
259f9fae…; private mirror ~/.local/state/marketplace-imports/codex-worktrees-20261013).
CT-21 imports what the tip cites; the worktrees are removed only after CT-21 is published.
```

and `task_plan.md:322`: replace the absolute `2a14` link with
`[retained worktree review](../../docs/agents/automation-amendment-review.md)` once CT-21 integrates
(before that the link is dangling either way; leave a `(imported by CT-21)` note).

**`findings.md` bullets** (replace, in "## Claude takeover (2026-10-13)", the bullet that begins
"Unpublished local tip: `c6caaca`, `d2a4103` (T1 import). A06 unit3 is uncommitted …" — its hashes
are now in the tip at `8f783a0` — and add the import state; the "Inherited limitations" section
keeps its research text, which R3 P2-3 corrects separately):

```markdown
- Codex worktree data (`2a14` HEAD `48027d2`, `c658` HEAD `6130ab5`) is snapshotted, read-only:
  `imports/codex-worktrees-20261013/` (454 files, 11.8 MB, `MANIFEST.json` SHA-256 `259f9fae…`,
  `verify.py --mirror` rc 0) and the 0700 mirror `~/.local/state/marketplace-imports/codex-worktrees-20261013`.
  Only the index files (README, MANIFEST, T1 report, T1 scan, verify.py, T2 plan) are committed;
  the `2a14/`, `c658/` payload stays untracked (`.git/info/exclude`) because it holds raw session
  streams and full issue bodies (sweep A keep-private: 149 files, 6.6 MB).
- The tip cites 101 paths that exist only there (T1 table): 22 untracked-class refs (58 files)
  and 79 files ignored by `~/.gitignore_global` (`*.log`, `build/`), never by the frozen
  `.gitignore`. CT-21 (`reviews/ccm-20261013/T2-import-lane-design.md`) imports 119 files
  (1,057,200 B, gitleaks 8.30.1 dir scan 0 findings), declares 18 iwyu build-tree files and the
  keep-private sets in `dev/cited-inputs.json`, and adds `check:inputs`. Until it integrates,
  `dev/codex_examples.py` fails outside `2a14`, `dev/checkout_transfer.py:17` hard-codes the
  `2a14` path, and the #63–#69, #71–#74 closure rows cannot bind their evidence (sweep B).
- `docs/accepted-decisions.md` "Automation and observability clarification (2026-10-12)" (+52
  lines, user decision) exists only in `2a14`; the parent applies the hunk in Runbook step 7
  (diff in the snapshot: `2a14/modified/docs/accepted-decisions.md.diff`).
```

## d. The lane

`P/lanes/ct21-codex-imports.json` (new; schema of `c1-catalog-promotion.json`/`gate-hooks.json`
plus the `import_source` field `planning-records.md` names, bound to MANIFEST `259f9fae…` and
`T2-import-plan.json` `d53fc622…`). Branch `claude/ct21-codex-imports`, worktree
`.claude/worktrees/ct21-codex-imports`, `base_sha` TBD-at-cut, owner implementer/Opus, reviewer
Fable cold, `status` `allocated-pending-merge …` (the Stop gate's `allocated` prefix), `retro`
`pending`. `owned_paths` is the exact allowlist: the import destinations (new files only, no
lock files), the 61 `*.log` rows by reference to the plan, `evidence/codex-imports/` for the copy
and scan receipts, the four `dev` files plus the new checker, its test, `dev/cited-inputs.json`,
`dev/fixtures/inputs/`, `mise/tasks/ct21.toml`, one `development.yml` step, the
`codex-example-classification.md` paragraph, the `spec-11-amendment-candidate.{md,json}` pair,
the retro and the lane log. Excluded: `mise.dev.toml` (parent hunk), `dev/check.py` (CT-11),
`hk.pkl` (CT-02b/parent), `docs/accepted-decisions.md` (parent step 7), the baseline files, every
shared planning file, `P/imports/**` (read-only source) and every keep-private/mirror path.
Brief: `T2-ct21-brief.md` (R8 implementer template, 40 lines).

## e. Sequencing

| Question | Answer |
|---|---|
| Before the first publish (Runbook step 8)? | No. Step 8 publishes the gate-hooks merge and record corrections only; CT-21 is a lane and needs an allocation commit after wave 0. |
| Before the second publish (step 10)? | No, but step 10 must carry the **T1/T2 index files only** (`README.md`, `MANIFEST.json`, `T1-snapshot-report.md`, `T1-dependency-scan.json`, `verify.py`, `T2-import-plan.json`; gitleaks dir scan 0 findings) and add `.planning/…/imports/codex-worktrees-20261013/2a14/` and `…/c658/` to `.git/info/exclude`. Committing the payload would publish the keep-private set. From step 10 on, the "declared private mirror with a recorded SHA-256" of §f exists in the tree, which is what `check:inputs` later reads. |
| Before CT-08? | Independent. No `.gitignore` edit is needed (headline 1); CT-08's additions (`.claude/worktrees/`, `settings.local.json`) do not touch evidence. If the user later wants the 18 build-tree files tracked, that is `git add -f`, still not CT-08. |
| Wave 1 alongside ct02b, ct11, ct05, ct15? | No path conflict: ct02b owns `dev/hooks/`, `git_delivery.py`; ct11 `dev/check.py`, `dev/retro_gate.py`, `dev/check_lock.py`; ct05 `dev/lane.py`, `dev/ledger.py`, `planning-records.md`; ct15 `dev/plan_records.py`. CT-21 owns none of those and nobody else owns `evidence/**` (new files), `dev/codex_examples.py`, `dev/checkout_transfer.py`, `dev/check_inputs.py`, `development.yml`. The only shared lines are the parent `depends` hunk in `mise.dev.toml` (the same mechanism as `test:hooks`). R8 caps a wave at four offline lanes (rationale not stated); recommendation: **wave 1 as a fifth lane, integration order 5**, because the lane is mostly hash-verified data copying and it unblocks the CLOSE lane that SYNTHESIS otherwise parks in wave 4+ ("A06 residual"). If the cap stands, **first in wave 2** (before CT-17/CT-19/CT-18). |
| Prerequisites | Wave 0 step 0.3 (`[task_config] includes`), like every lane; the gate-hooks merge resolved; `verify.py` rc 0 at cut time. |
| What it blocks | (1) `#69` closure (ledger: "retained-corpus consumption still open"; the corpus and schema become tracked). (2) Sweep B closure rows: #63 (captures "live only in `2a14`"), #64/#65 (`codex-schema--…8385f42d…`, `…59b358fe…`), #66 (two fixture captures), #68 (comparison receipt `…96dbbeb7…`), #71 (`spec-11-amendment-candidate.{md,json}` hash `5dfc7a31…`; the `A07b.*` intents stay in the mirror, declared), #72/#73 (`graph-audit.json`, `local-edge-receipt.json`), #74 (`a09-history-scan-triage.md`, `a09-scan-adjudication.json`; the redacted report mirror-declared). (3) The CLOSE lane for the A-series: a qualified close binds evidence that resolves in the tree. (4) D9 removal of the `2a14`/`c658` worktrees and the `codex/28|29-offline-refresh` cleanup: only after CT-21 is published and `verify.py --mirror` rc 0 is re-recorded. (5) The parent's rewrite of the four tracked `2a14` absolute paths (`task_plan.md:322`, `docs/status.md:10`, `docs/agents/claude-takeover.md:26`, `docs/agents/codex-task-orchestration.md:6`) and of `dev/checkout_transfer.py`'s default (A10 would otherwise break the day the worktree is removed). |
| What it does not block | CT-02b, CT-11, CT-05, CT-15, the spec/ticket publication (step 11), #91 relabel, the draft PR. |

## f. Detection going forward

**Invariant.** *Every path cited by a tracked retro (`P/retros/*.md`), by a tracked evidence
manifest row (`path` + `sha256`), or by a code default declared in `dev/cited-inputs.json` exists
in the tree with the cited SHA-256, or is declared in `dev/cited-inputs.json` as held by a named
private mirror with its SHA-256 and the mirror's manifest hash.* A citation that satisfies neither
fails `check:inputs` with the path and the citing `file:line`.

**Where it runs.** (1) `./dev/mise run check:inputs` (lane task) and, through the parent `depends`
hunk, every `check`, `check:acceptance-baseline` and `check:research` run — so each lane's required
checks, each integration's composed-tree gates and the serialized `check:research` run cover it.
(2) CI: `development.yml` step (lane) now; `dev/check.py` sub-check once CT-11 releases the file
(CT-12's "unwired tests" lane is the natural owner). (3) hk `pre-commit` (parent/CT-02b hunk;
`hk.pkl` currently has only `pre-merge-commit` and `pre-push`), consistent with the accepted
decision "fast … checks in hk pre-commit":

```pkl
    ["pre-commit"] {
        stash = "none"
        steps {
            ["cited-inputs"] { check = "./dev/mise run check:inputs" }
        }
    }
```

(4) A09: no change; `delivery:publish` keeps its own history scan. (5) Rule text (parent literal
edit, `.claude/rules/evidence.md`): "A receipt cited by a tracked retro or manifest is tracked, or
declared in `dev/cited-inputs.json` with its mirror and SHA-256; `./dev/mise run check:inputs`
enforces it. Host global excludes (`~/.gitignore_global`) never decide what is tracked: use
`git add -f` for a manifest-hashed `*.log`." Future imports from a Codex worktree follow the same
shape: T1-style snapshot + MANIFEST → import plan → lane with `import_source` → `check:inputs` green.

## g. Could not verify

- A09 `git`-mode gitleaks over the eventual import commit (no commit exists; dir mode over the same
  bytes is 0 findings). `history_scan_rc` is a lane receipt.
- Sweep A's directory hash for `evidence/claude-amendment-review/` (`584494a4…a07`) and the other
  directory hashes were not recomputed; per-file SHA-256 values come from MANIFEST.json and were
  re-hashed for the 68 import candidates only.
- Line counts of the proposed code (estimate: checker ~170, its tests ~90, the two diffs ~40; the
  manifest JSON is data). The lane reports a split (`ct21-check-inputs`) past 300 handwritten lines.
- Whether `codex --version` on the implementer host is `codex-cli 0.162.1` (only the live
  `research:examples` path needs it; the tests patch it).
- The R8 four-offline-lanes-per-wave cap: its rationale is not stated, so the wave-1 placement is
  a recommendation for the user.
- Whether the user wants the 18 iwyu build-tree files tracked (default here: mirror) and whether
  hunk 2 of the accepted-decisions diff is the user's wording.
- The `verify.py --mirror` run was not repeated by T2 (T1 recorded rc 0, 454/454 in both copies);
  the lane reruns it before copying.
- Issue numbers: CT-21 has no GitHub issue; `parent_number 999999` is the preview placeholder.

## Appendix — per-file classification (generated from MANIFEST.json × T1 × sweep A)

Columns: destination tip path (or snapshot path for keep-private), bytes, SHA-256 prefix, `git add`
mode, blocking ignore rule from `git check-ignore -v --no-index` (empty = not ignored). The same
rows with full hashes and `src` paths are in `T2-import-plan.json`.

#### import (119 files, 1057200 B)

| Destination (tip path) or snapshot path | Bytes | SHA-256 | git add | Ignore rule (git check-ignore -v) |
|---|---|---|---|---|
| `.planning/2026-10-10-marketplace-macos-reflection-scaffold/spec-11-amendment-candidate.json` | 994 | `9e719f490712310b…` | git add |  |
| `.planning/2026-10-10-marketplace-macos-reflection-scaffold/spec-11-amendment-candidate.md` | 17224 | `5dfc7a31d4c42da2…` | git add |  |
| `docs/agents/automation-amendment-review.md` | 9143 | `f67f16c9ee78812a…` | git add |  |
| `docs/agents/github-search-reuse.md` | 5740 | `8d4648010cdccac9…` | git add |  |
| `docs/agents/workflow-reconciliation.md` | 16630 | `df2bf2a260283094…` | git add |  |
| `evidence/codex-examples/release/config-schema.json` | 236751 | `7933a70506e753a6…` | git add |  |
| `evidence/codex-examples/runs/codex-config-examples--1791838915397532000--b666ae4cd38ff2a3--3f8c9a929eafe0c6/blobs/7b065212a81e47722c6c2036e61f6aec5f6df083` | 58 | `801de0cfb15d2acc…` | git add |  |
| `evidence/codex-examples/runs/codex-config-examples--1791838915397532000--b666ae4cd38ff2a3--3f8c9a929eafe0c6/receipt.json` | 976 | `91ee1239a597b7ac…` | git add |  |
| `evidence/codex-examples/runs/codex-schema--1791838352470495000--780ef2a027d3c66a--f2bd1fff0a140d91/blobs/101c57b363027443ced5c46c573cd36f77b570d7` | 314 | `d1fa6b6fc7523f5f…` | git add |  |
| `evidence/codex-examples/runs/codex-schema--1791838352470495000--780ef2a027d3c66a--f2bd1fff0a140d91/receipt.json` | 975 | `a3d1d7123425ee60…` | git add |  |
| `evidence/core-p2996/operation/ctest-corrected-exit-contract/Testing/Temporary/LastTest.log` | 741 | `9d9cb4f96d841483…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/core-p2996/operation/ctest-old-regex-comparison/Testing/Temporary/LastTest.log` | 817 | `b82d6d5e2c3e2e7c…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/git-delivery/a09-history-scan-triage.md` | 2948 | `8b98e79585d7d048…` | git add |  |
| `evidence/git-delivery/a09-scan-adjudication.json` | 1603 | `4e6faa817bdf0ca8…` | git add |  |
| `evidence/github-search-one-page/20261012T192427Z-c21f8300/normalized.json` | 660 | `407cb1bc3ad38be9…` | git add |  |
| `evidence/github-search-one-page/20261012T192427Z-c21f8300/raw.json` | 69 | `a9db2cf4f4a6f555…` | git add |  |
| `evidence/github-search-one-page/20261012T192548Z-d72b7e85/normalized.json` | 3023 | `318306944aecb851…` | git add |  |
| `evidence/github-search-one-page/20261012T192548Z-d72b7e85/raw.json` | 25953 | `7a689ba315367282…` | git add |  |
| `evidence/github-search-one-page/20261012T192724Z-33992b35/normalized.json` | 3119 | `8c63cdcbe9c2d91e…` | git add |  |
| `evidence/github-search-one-page/20261012T192724Z-33992b35/raw.json` | 25953 | `7a689ba315367282…` | git add |  |
| `evidence/github-search-one-page/20261012T193625Z-a9effc47/normalized.json` | 755 | `e23f97f27304b1ff…` | git add |  |
| `evidence/github-search-one-page/20261012T193625Z-a9effc47/raw.json` | 464 | `9bcade5922f6fb75…` | git add |  |
| `evidence/github-search-one-page/20261012T193642Z-65b81923/normalized.json` | 614 | `738896c41035a848…` | git add |  |
| `evidence/github-search-one-page/20261012T193642Z-65b81923/raw.json` | 388 | `2be25fb890eda9e5…` | git add |  |
| `evidence/github-search-one-page/20261012T193651Z-cc501ef6/normalized.json` | 3023 | `e9c74b5aa9cfe956…` | git add |  |
| `evidence/github-search-one-page/20261012T193651Z-cc501ef6/raw.json` | 29968 | `5b95fc70969870fa…` | git add |  |
| `evidence/github-search-one-page/20261012T193658Z-eb12ab90/normalized.json` | 3119 | `1e53e4c0e91de9ca…` | git add |  |
| `evidence/github-search-one-page/20261012T193658Z-eb12ab90/raw.json` | 29968 | `5b95fc70969870fa…` | git add |  |
| `evidence/issue-publication-private/edges/local-edge-receipt.json` | 5723 | `4990e9b93b1a7fa0…` | git add |  |
| `evidence/issue-publication-private/graph-audit.json` | 3429 | `53559e3b271c58db…` | git add |  |
| `evidence/mise-runtime/attempt1-invocation/stderr.log` | 732 | `91a6262c6d20ceb6…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/mise-runtime/attempt1-invocation/stdout.log` | 139 | `e20a659c1a29ce2d…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/mise-runtime/attempt2-invocation/stderr.log` | 481 | `374d5f5359e87c5e…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/mise-runtime/attempt2-invocation/stdout.log` | 349 | `15bf763d88c254a0…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/mise-runtime/attempt3-invocation/stderr.log` | 612 | `6a03d76d622cec21…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/mise-runtime/attempt3-invocation/stdout.log` | 576 | `2dfef5f620a5d92b…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/mise-runtime/invocation/stderr.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/mise-runtime/invocation/stdout.log` | 743 | `6948e1ba8216d0ab…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/p2996-cmake/independent-review/configured-evidence/private-runtime-try-compile.log` | 2456 | `f658dad2788c64b0…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/p2996-cmake/operation/configured-evidence/private-runtime-try-compile.log` | 2436 | `72f8e1f702ddd118…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/saved-searches/comparisons/codex-config-examples--1791838915397532000--b666ae4cd38ff2a3--2e0609c70b84dd5a291d3e2e4c98a3b9744e577c1b5ebdc7b4d7228ff66bfae8.json` | 479 | `2e0609c70b84dd5a…` | git add |  |
| `evidence/saved-searches/comparisons/codex-hook-examples--1791838940951623000--b6893b866aa012b8--826be5fa1dfbe6b8aa28c82b60a7a82b8eb3192eed1af229aa959502a6a1e2b7.json` | 475 | `826be5fa1dfbe6b8…` | git add |  |
| `evidence/saved-searches/comparisons/codex-schema--1791838352470495000--780ef2a027d3c66a--96dbbeb74a67757d8ed3ea1434a88d89e51cb06e26f3a9dc8fd9bd7c79d3be2d.json` | 450 | `96dbbeb74a67757d…` | git add |  |
| `evidence/saved-searches/runs/codex-config-examples--1791838915397532000--b666ae4cd38ff2a3/manifest.json` | 799 | `36797304776a06ce…` | git add |  |
| `evidence/saved-searches/runs/codex-config-examples--1791838915397532000--b666ae4cd38ff2a3/normalized.json` | 843 | `7198462d3601ee15…` | git add |  |
| `evidence/saved-searches/runs/codex-config-examples--1791838915397532000--b666ae4cd38ff2a3/raw.json` | 36623 | `5284be05d2e2d94b…` | git add |  |
| `evidence/saved-searches/runs/codex-hook-examples--1791838940951623000--b6893b866aa012b8/manifest.json` | 807 | `5180ace62279499a…` | git add |  |
| `evidence/saved-searches/runs/codex-hook-examples--1791838940951623000--b6893b866aa012b8/normalized.json` | 492 | `5c0cbe15031a5767…` | git add |  |
| `evidence/saved-searches/runs/codex-hook-examples--1791838940951623000--b6893b866aa012b8/raw.json` | 30764 | `94c7773eaeca36d6…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791834335766132000--747966bbfbc179da/manifest.json` | 830 | `8ec919dba1641a5c…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791834335766132000--747966bbfbc179da/normalized.json` | 421 | `a7782d7f97b07860…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791834335766132000--747966bbfbc179da/raw.json` | 397 | `f11c1ca4c6b714de…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791834403418782000--73b8ad54811dc757/manifest.json` | 821 | `14edcfce08b8f83f…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791834403418782000--73b8ad54811dc757/normalized.json` | 2305 | `fb8ff6367f3c520d…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791834403418782000--73b8ad54811dc757/raw.json` | 29883 | `a9f51ce6c4856d44…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791835506050931000--571672a8755a45d5/manifest.json` | 830 | `6bfc8b527db70243…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791835506050931000--571672a8755a45d5/normalized.json` | 330 | `c1ba07eb9e98653c…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791835506050931000--571672a8755a45d5/raw.json` | 550 | `ed6b5c3f5ab9d27a…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791835615392017000--b2451f6bd8490b1c/manifest.json` | 760 | `8ac5f8f7ac6289b8…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791835615392017000--b2451f6bd8490b1c/normalized.json` | 4171 | `c21156f2d3276628…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791835615392017000--b2451f6bd8490b1c/raw.json` | 60045 | `06685c2f8cc0d2c9…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791836388445290000--8385f42d6953e0ab/manifest.json` | 760 | `ce45d2a319ecf94c…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791836388445290000--8385f42d6953e0ab/normalized.json` | 4171 | `c21156f2d3276628…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791836388445290000--8385f42d6953e0ab/raw.json` | 60045 | `4a6d7a8f1056292b…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791837279871878000--59b358fe26427ce1/manifest.json` | 760 | `a0834f79af6bd4a5…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791837279871878000--59b358fe26427ce1/normalized.json` | 4281 | `20a22bce853a529d…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791837279871878000--59b358fe26427ce1/raw.json` | 60059 | `f7b6968be911b92a…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791838352470495000--780ef2a027d3c66a/manifest.json` | 760 | `a1f6006bccc37075…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791838352470495000--780ef2a027d3c66a/normalized.json` | 4281 | `20a22bce853a529d…` | git add |  |
| `evidence/saved-searches/runs/codex-schema--1791838352470495000--780ef2a027d3c66a/raw.json` | 60059 | `f2ea8a0472780438…` | git add |  |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/detect_compiler/stdout-arm64-osx-p2996-static.log` | 1785 | `aecaff076a882809…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/detect_compiler/stdout-arm64-osx.log` | 1484 | `86b38ab7c0baf65f…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/config-arm64-osx-p2996-static-dbg-ninja.log` | 49283 | `540ed07ef80b059c…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/config-arm64-osx-p2996-static-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/config-arm64-osx-p2996-static-out.log` | 6786 | `065fab37c02e062b…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/config-arm64-osx-p2996-static-rel-ninja.log` | 49348 | `ee09e8486b0be7dc…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/install-arm64-osx-p2996-static-dbg-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/install-arm64-osx-p2996-static-dbg-out.log` | 8982 | `bdb803ac08291301…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/install-arm64-osx-p2996-static-rel-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/install-arm64-osx-p2996-static-rel-out.log` | 8879 | `8c25ca8a0614f32f…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/fmt/stdout-arm64-osx-p2996-static.log` | 1465 | `231ff234109550ca…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/vcpkg-cmake-config/stdout-arm64-osx.log` | 709 | `d3507ff0c3310281…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/attempt-1/buildtrees/vcpkg-cmake/stdout-arm64-osx.log` | 1038 | `2c19e2d0f4515dd2…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/detect_compiler/stdout-arm64-osx-gcc16-dynamic.log` | 1996 | `4e60173bf6f46429…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/detect_compiler/stdout-arm64-osx.log` | 1485 | `e089002c76fb4bd9…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/config-arm64-osx-gcc16-dynamic-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/config-arm64-osx-gcc16-dynamic-out.log` | 6973 | `c67f0ec92fd1e8c5…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/install-arm64-osx-gcc16-dynamic-dbg-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/install-arm64-osx-gcc16-dynamic-dbg-out.log` | 8385 | `adcdd3f63b7dd68d…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/install-arm64-osx-gcc16-dynamic-rel-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/install-arm64-osx-gcc16-dynamic-rel-out.log` | 8277 | `4f6fa1fd9bda38a3…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-dynamic/buildtrees/fmt/stdout-arm64-osx-gcc16-dynamic.log` | 2406 | `49736c8570f550c8…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/detect_compiler/stdout-arm64-osx-gcc16-static.log` | 1993 | `11a3ff9a8358c8e4…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/detect_compiler/stdout-arm64-osx.log` | 1484 | `bbf79541dc06ed74…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/config-arm64-osx-gcc16-static-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/config-arm64-osx-gcc16-static-out.log` | 6960 | `f707b936d471a3d8…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/install-arm64-osx-gcc16-static-dbg-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/install-arm64-osx-gcc16-static-dbg-out.log` | 7655 | `d12ce4b2d05f025f…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/install-arm64-osx-gcc16-static-rel-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/install-arm64-osx-gcc16-static-rel-out.log` | 7552 | `0e3ebcbf9ef18961…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-gcc16-static/buildtrees/fmt/stdout-arm64-osx-gcc16-static.log` | 1465 | `58f2a57072428505…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/detect_compiler/stdout-arm64-osx-p2996-dynamic.log` | 1788 | `d20cf0eadc1d79b3…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/detect_compiler/stdout-arm64-osx.log` | 1485 | `d43f98241e17d8f6…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/config-arm64-osx-p2996-dynamic-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/config-arm64-osx-p2996-dynamic-out.log` | 6799 | `42f92d7abe8a7e10…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/install-arm64-osx-p2996-dynamic-dbg-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/install-arm64-osx-p2996-dynamic-dbg-out.log` | 10571 | `00b2b93819551d43…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/install-arm64-osx-p2996-dynamic-rel-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/install-arm64-osx-p2996-dynamic-rel-out.log` | 10463 | `924118d90b994025…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-dynamic/buildtrees/fmt/stdout-arm64-osx-p2996-dynamic.log` | 2406 | `2663dcc1a2605c07…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/detect_compiler/stdout-arm64-osx-p2996-static.log` | 1785 | `c93f3bdf523f5cc8…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/detect_compiler/stdout-arm64-osx.log` | 1484 | `22818d3b6e25eb92…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/config-arm64-osx-p2996-static-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/config-arm64-osx-p2996-static-out.log` | 6786 | `f6e2017899f3f6e2…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/install-arm64-osx-p2996-static-dbg-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/install-arm64-osx-p2996-static-dbg-out.log` | 8982 | `091f59defd4743ad…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/install-arm64-osx-p2996-static-rel-err.log` | 0 | `e3b0c44298fc1c14…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/install-arm64-osx-p2996-static-rel-out.log` | 8879 | `ae955707f801fd1a…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |
| `evidence/vcpkg-fmt-build/operation/arm64-osx-p2996-static/buildtrees/fmt/stdout-arm64-osx-p2996-static.log` | 1465 | `017c729b9d8d17f7…` | git add -f | /Users/rmanaloto/.gitignore_global:34:*.log |

#### exclude (10 files, 0 B)

| Destination (tip path) or snapshot path | Bytes | SHA-256 | git add | Ignore rule (git check-ignore -v) |
|---|---|---|---|---|
| `evidence/saved-searches/locks/codex-config-examples.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/locks/codex-hook-examples.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/locks/codex-schema.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/runs/codex-config-examples--1791838915397532000--b666ae4cd38ff2a3/.writer.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/runs/codex-hook-examples--1791838940951623000--b6893b866aa012b8/.writer.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/runs/codex-schema--1791835506050931000--571672a8755a45d5/.writer.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/runs/codex-schema--1791835615392017000--b2451f6bd8490b1c/.writer.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/runs/codex-schema--1791836388445290000--8385f42d6953e0ab/.writer.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/runs/codex-schema--1791837279871878000--59b358fe26427ce1/.writer.lock` | 0 | `e3b0c44298fc1c14…` |  |  |
| `evidence/saved-searches/runs/codex-schema--1791838352470495000--780ef2a027d3c66a/.writer.lock` | 0 | `e3b0c44298fc1c14…` |  |  |

#### mirror (18 files, 849093 B)

| Destination (tip path) or snapshot path | Bytes | SHA-256 | git add | Ignore rule (git check-ignore -v) |
|---|---|---|---|---|
| `evidence/iwyu-build/operation/build/.ninja_log` | 1630 | `4dd4d362ab8e0b43…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeCache.txt` | 23612 | `e5cda049bce7f301…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CMakeCCompiler.cmake` | 3338 | `35112c9af9944ea0…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CMakeCXXCompiler.cmake` | 6651 | `d36cb6f1769268aa…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CMakeSystem.cmake` | 360 | `0a827d18a29e4cb1…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CompilerIdC/CMakeCCompilerId.c` | 29029 | `6ccdb729a0b1d02b…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CompilerIdC/apple-sdk.c` | 32 | `93336ad6605d000e…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CompilerIdCXX/CMakeCXXCompilerId.cpp` | 29651 | `5b0cbdb2a0d0a5b9…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/4.4.4/CompilerIdCXX/apple-sdk.cpp` | 32 | `93336ad6605d000e…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/CMakeConfigureLog.yaml` | 636201 | `c1baff48cd49c3d3…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/InstallScripts.json` | 168 | `974619f39eb8ffbe…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/TargetDirectories.txt` | 1576 | `513764745b7ecf01…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/cmake.check_cache` | 85 | `a26189e394421da5…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/CMakeFiles/rules.ninja` | 2552 | `5a135720c1551163…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/build.ninja` | 81756 | `4c6b160e9df4793e…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/cmake_install.cmake` | 5342 | `8e731e391d7b1ec8…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/compile_commands.json` | 24818 | `f8fbe99b9430f11c…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |
| `evidence/iwyu-build/operation/build/install_manifest.txt` | 2260 | `9af786b8dc40d05b…` |  | /Users/rmanaloto/.gitignore_global:23:build/ |

#### keep-private (148 files, 6369150 B)

| Destination (tip path) or snapshot path | Bytes | SHA-256 | git add | Ignore rule (git check-ignore -v) |
|---|---|---|---|---|
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/archive.json` | 1608 | `440035e21031f75b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/events.jsonl` | 394270 | `0e08882a54ae61e0…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/amendment.md` | 12542 | `e46f9c2d9215f47b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/decisions.md` | 11147 | `4cd7542bda079afc…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/delivery-recovery.review.md` | 15052 | `4a1927bdfa7ad592…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/plan.md` | 29721 | `2fbf83df9c6468fc…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/reconciliation.md` | 16594 | `5089909fb7885a2b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/requirements-graph.review.md` | 19556 | `0888e9bf52e6c063…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/reuse.md` | 5740 | `8d4648010cdccac9…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/search-correctness.review.md` | 13284 | `99061ca9f7d5f7bf…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/takeover.md` | 8035 | `7f0057a9a6cdf171…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/tickets.md` | 7842 | `e44c4c3bbe30a837…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/inputs/tracker.md` | 1629 | `424bbb5693cbc336…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/manifest.json` | 3907 | `a39ae6a3b036d62a…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/receipt.json` | 116051 | `912135a405b4a269…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/dbc423fe/review.md` | 8402 | `8cb46b1514c0a9eb…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/archive.json` | 1119 | `cba949f0e5700309…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/events.jsonl` | 25726 | `e341b596112e30e3…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/inputs/amendment.md` | 12542 | `e46f9c2d9215f47b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/inputs/decisions.md` | 11147 | `4cd7542bda079afc…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/inputs/plan.md` | 29721 | `2fbf83df9c6468fc…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/inputs/reconciliation.md` | 16594 | `5089909fb7885a2b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/inputs/reuse.md` | 5740 | `8d4648010cdccac9…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/inputs/takeover.md` | 8035 | `7f0057a9a6cdf171…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/inputs/tickets.md` | 7842 | `e44c4c3bbe30a837…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/inputs/tracker.md` | 1629 | `424bbb5693cbc336…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/mrnz6qg_/manifest.json` | 4743 | `1348ebe90b2dc5f3…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/archive.json` | 1276 | `7395431e1768add3…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/events.jsonl` | 41318 | `7750df445bf1242e…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/inputs/amendment.md` | 12542 | `e46f9c2d9215f47b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/inputs/decisions.md` | 11147 | `4cd7542bda079afc…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/inputs/plan.md` | 29721 | `2fbf83df9c6468fc…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/inputs/reconciliation.md` | 16594 | `5089909fb7885a2b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/inputs/reuse.md` | 5740 | `8d4648010cdccac9…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/inputs/takeover.md` | 8035 | `7f0057a9a6cdf171…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/inputs/tickets.md` | 7842 | `e44c4c3bbe30a837…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/inputs/tracker.md` | 1629 | `424bbb5693cbc336…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/manifest.json` | 3791 | `67b74f38bd2162da…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/receipt.json` | 17025 | `7994dfe8eac05b14…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/olhfd2s1/review.md` | 521 | `cf335a8aaec683e3…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/archive.json` | 1280 | `473503b33e6394aa…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/events.jsonl` | 836180 | `836202381bdab6c2…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/inputs/amendment.md` | 12542 | `e46f9c2d9215f47b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/inputs/decisions.md` | 11147 | `4cd7542bda079afc…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/inputs/plan.md` | 29721 | `2fbf83df9c6468fc…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/inputs/reconciliation.md` | 16594 | `5089909fb7885a2b…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/inputs/reuse.md` | 5740 | `8d4648010cdccac9…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/inputs/takeover.md` | 8035 | `7f0057a9a6cdf171…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/inputs/tickets.md` | 7842 | `e44c4c3bbe30a837…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/inputs/tracker.md` | 1629 | `424bbb5693cbc336…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/manifest.json` | 10243 | `5ad91fa35e924992…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/receipt.json` | 419666 | `22442fc1ec218bbe…` |  |  |
| `2a14/untracked/evidence/claude-amendment-review/oprwaz61/review.md` | 52 | `0dc1c682a72d8e8b…` |  |  |
| `2a14/untracked/evidence/git-delivery/initial-outbound-gitleaks-redacted.json` | 219931 | `685cc05735d4c3fa…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A01.intent.json` | 206623 | `0c0846d85bfe7f06…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A01.intent.json.attempt.json` | 143 | `c66a73fd6e04d3c6…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A01.intent.json.binding.json` | 173 | `04f212afd00f35dc…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A02.intent.json` | 208900 | `dade0ffce346709e…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A02.intent.json.attempt.json` | 143 | `2ca640139aed4fee…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A02.intent.json.binding.json` | 173 | `4c4e1ae80c2caa98…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A03a.intent.json` | 210845 | `02ec17a59471d2f6…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A03a.intent.json.attempt.json` | 143 | `2e9d975a25d3c482…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A03a.intent.json.binding.json` | 174 | `378ab36a7f8e8f3e…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A03b.intent.json` | 212857 | `f41e2e1b6b6a48a1…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A03b.intent.json.attempt.json` | 143 | `ca21203b068652fd…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A03b.intent.json.binding.json` | 174 | `1a1f95a648fd8e53…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A04.intent.json` | 214861 | `f4793c8be4ea827f…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A04.intent.json.attempt.json` | 143 | `46a64a85c1af0f03…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A04.intent.json.binding.json` | 173 | `40469602e008b490…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A05a.intent.json` | 216867 | `f11bc1f3f48afe1f…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A05a.intent.json.attempt.json` | 143 | `b6d8d0559d5eb8f4…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A05a.intent.json.binding.json` | 174 | `09a8ddf0b96f5476…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A05b.intent.json` | 219395 | `da4081a6a77f7a54…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A05b.intent.json.attempt.json` | 143 | `a8385e1a57d30913…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A05b.intent.json.binding.json` | 174 | `78b3bb580e358bef…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A06.intent.json` | 222166 | `9f0c8eb6f1e4836f…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A06.intent.json.attempt.json` | 143 | `7662ab81796c07e4…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A06.intent.json.binding.json` | 173 | `8cd531ffb97524a8…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A07a.intent.json` | 224342 | `100076a359acb156…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A07a.intent.json.attempt.json` | 143 | `bc9fee105a0052c1…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A07a.intent.json.binding.json` | 174 | `e0a5011c19e76345…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A07b.intent.json` | 225949 | `6cd17abd8a3674f5…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A07b.intent.json.attempt.json` | 143 | `42d084e26e5ae99b…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A07b.intent.json.binding.json` | 174 | `bfd077f52812d561…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A08a.intent.json` | 227609 | `3f8cf92c6b2356cf…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A08a.intent.json.attempt.json` | 143 | `68903ee92347f606…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A08a.intent.json.binding.json` | 174 | `feee4d5bdaf88a4e…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A08b.intent.json` | 229421 | `a4c475b6772d15e8…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A08b.intent.json.attempt.json` | 143 | `d2669ab4e596e958…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A08b.intent.json.binding.json` | 174 | `22b29a5df05649e5…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A09.intent.json` | 231489 | `6611a8864478cc00…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A09.intent.json.attempt.json` | 143 | `3ebfd478af9c0312…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A09.intent.json.binding.json` | 173 | `e3c20d3e27d822b9…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A10.intent.json` | 233684 | `796267b347920767…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A10.intent.json.attempt.json` | 143 | `7732cd24e1f61764…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A10.intent.json.binding.json` | 173 | `5bc877a8c2fa28ea…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A11.intent.json` | 235760 | `9a235dcb430437a5…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A11.intent.json.attempt.json` | 143 | `bb0c1a3aeb2a3b04…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A11.intent.json.binding.json` | 173 | `152390033b848012…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A12a.intent.json` | 237835 | `4b09da9cd7884442…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A12a.intent.json.attempt.json` | 143 | `ffa91f95f0e76bf1…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A12a.intent.json.binding.json` | 174 | `68e0de57368bdf57…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A12b.intent.json` | 240077 | `23655560c036ad34…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A12b.intent.json.attempt.json` | 143 | `6c15be13690abf69…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/A12b.intent.json.binding.json` | 174 | `be884966acde338c…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A02-by-A01.intent.json` | 1266 | `1a82b2b056ccadd4…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A02-by-A01.intent.json.attempt.json` | 97 | `10be8c8bb39900ba…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A03a-by-A04.intent.json` | 1178 | `9c7bea6727609152…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A03a-by-A04.intent.json.attempt.json` | 97 | `c188c3f33858dc95…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A03b-by-A03a.intent.json` | 1335 | `340dd77700af4e10…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A03b-by-A03a.intent.json.attempt.json` | 97 | `219d7576bbb9911c…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A04-by-A02.intent.json` | 1169 | `9e7d0684ab8f0ec8…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A04-by-A02.intent.json.attempt.json` | 97 | `b07e6945b5e5b987…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A05a-by-A03b.intent.json` | 1337 | `dda57d6b22b17eae…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A05a-by-A03b.intent.json.attempt.json` | 97 | `334256889ac3932e…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A05a-by-A04.intent.json` | 1351 | `a09514df810a6502…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A05a-by-A04.intent.json.attempt.json` | 97 | `152dc70810ade792…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A05b-by-A05a.intent.json` | 1693 | `4e3f003b370bd906…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A05b-by-A05a.intent.json.attempt.json` | 97 | `fb783f0ac7e1bec9…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A06-by-A05b.intent.json` | 1579 | `5a7fd8181dba7c49…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A06-by-A05b.intent.json.attempt.json` | 97 | `759d10515bd40eb4…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A07a-by-A04.intent.json` | 1097 | `a51612492dcb2198…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A07a-by-A04.intent.json.attempt.json` | 97 | `ac5535b0252a7664…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A07b-by-A07a.intent.json` | 1011 | `ae4129bcc50989fc…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A07b-by-A07a.intent.json.attempt.json` | 97 | `c639f31b051cf09a…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A08a-by-A07b.intent.json` | 1151 | `62acb1886cd3f48b…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A08a-by-A07b.intent.json.attempt.json` | 97 | `65605e217dbe429d…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A08b-by-A08a.intent.json` | 1163 | `5d79ee2f8ce27509…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A08b-by-A08a.intent.json.attempt.json` | 97 | `06194b5d3ea6e00a…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A09-by-A01.intent.json` | 1405 | `b8a32e8441535afc…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A09-by-A01.intent.json.attempt.json` | 97 | `b101c4ae406c894d…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A10-by-A09.intent.json` | 1288 | `f4496a6ef558fcde…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A10-by-A09.intent.json.attempt.json` | 97 | `4e9594093a41a724…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A11-by-A10.intent.json` | 1286 | `d6e92a646f581390…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A11-by-A10.intent.json.attempt.json` | 97 | `c87b00ab9292009d…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12a-by-A01.intent.json` | 1288 | `ebcef6ddb6ad531a…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12a-by-A01.intent.json.attempt.json` | 97 | `88ca6f78fa3da596…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12a-by-A02.intent.json` | 1303 | `580141fa5d8207fb…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12a-by-A02.intent.json.attempt.json` | 97 | `87f18ebf5dae4646…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12a-by-A09.intent.json` | 1319 | `87b8d64cb25361f2…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12a-by-A09.intent.json.attempt.json` | 97 | `3281d7960b457129…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12b-by-A06.intent.json` | 1454 | `5f1d028019c5a5ce…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12b-by-A06.intent.json.attempt.json` | 97 | `cbfb44c63733a983…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12b-by-A08b.intent.json` | 1470 | `e5f07378f90fe77a…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12b-by-A08b.intent.json.attempt.json` | 97 | `d1c8d0f0228312e5…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12b-by-A12a.intent.json` | 1486 | `a11ebea9935f43af…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/A12b-by-A12a.intent.json.attempt.json` | 97 | `5d87acb4821b2399…` |  |  |
| `2a14/untracked/evidence/issue-publication-private/edges/operations.jsonl` | 7421 | `081d652c270b7ec3…` |  |  |

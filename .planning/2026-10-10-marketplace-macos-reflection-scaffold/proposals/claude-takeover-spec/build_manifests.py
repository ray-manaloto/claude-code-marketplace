#!/usr/bin/env python3
"""Build the version-2 creation manifests for the takeover spec and its tickets.

usage: build_manifests.py spec OUT.json            # standalone spec (parent_number null)
       build_manifests.py tickets OUT.json PARENT  # ten tickets under the created spec number
The spec body comes from ../../drafts/spec-claude-takeover.md; ticket bodies are
defined below. body_sha256 is computed here so the manifest validates.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_MD = os.path.join(HERE, "spec.md")
REPO = "ray-manaloto/claude-code-marketplace"
SPEC_TITLE = "[Spec] Claude team takeover and self-improving workflow"

TICKETS = [
    ("CT-01", "CT-01: Retro gate task",
     "**What to build:** `./dev/mise run retro:gate -- --unit <unit>` refuses (exit 2, one reason per line) a unit whose retro record is missing, skips any of the seven categories, binds no verification, or leaves a finding open without an owner or blocker; exits 0 otherwise. Humans, Claude and Codex run the same command.",
     ["Fixture retro records (complete, missing category, open finding, no evidence, open-with-owner) drive the gate's exit codes and reason lines through its public CLI.",
      "The suite is discovered by the existing development check runner like every other development test; `check`, `check:acceptance-baseline` and `git diff --check` stay rc 0.",
      "The unit's own retro record passes the gate; receipts name the selector environment (`VIRTUAL_ENV`, `UV_PROJECT_ENVIRONMENT`, `MARKETPLACE_PYTHON`) present when checks ran."],
     []),
    ("CT-02", "CT-02: Hook wiring for the retro gate",
     "**What to build:** a merge into the integration branch, a push, or the publication task is refused by git (`hk` `pre-merge-commit` and `pre-push` steps) and by Claude Code (`PreToolUse` deny on `git merge`/`git push`/`delivery:publish`, `SubagentStop`/`Stop` block keyed to a lane record) whenever the retro gate fails; hooks live in committed project settings.",
     ["Hook scripts fed Claude Code's stdin JSON shapes emit the exact deny/block/allow decisions; a `stop_hook_active` continuation ends the turn after one block.",
      "An `hk` run in a scratch repository refuses a merge commit and a push for a unit without a retro record and allows one with a passing record; `hk install` writes only the repository's own hook directory.",
      "Project settings carry the hooks with `onFailure: block`; `check` and the baseline stay rc 0; user-specific settings remain in the ignored local file."],
     ["CT-01"]),
    ("CT-03", "CT-03: Team roles, rules and workflow vocabulary",
     "**What to build:** project agent definitions for implementer, documentation writer, reviewer, retro writer and extractor (model, effort, permission mode, tool limits), path-scoped rules, a team guide, the glossary's Workflow section (unit, lane, gate, frontier, merger, integration tip, retro barrier, receipt, admission) and ADR 0001 for the takeover and the mechanical gate.",
     ["Each agent file loads in Claude Code with the intended model and reads its lane record before editing; the reviewer and extractor cannot write.",
      "Glossary terms are used verbatim in lane records, retro records and tickets; the ADR states context, decision and consequences.",
      "`check` and the baseline stay rc 0; no restated environment facts in the guide."],
     []),
    ("CT-04", "CT-04: Guidance hierarchy",
     "**What to build:** the root guidance file becomes a short navigation pointer; `dev/`, `docs/`, `evidence/`, `.planning/` and `.claude/` each carry their own guidance file plus a thin importer so both agent families read the same text; judgement-only standards live in a reviewer-facing standards file.",
     ["An agent that touches a file under `dev/` loads `dev/`'s guidance and nothing from the other directories; the root file is under sixty lines.",
      "Every pointer resolves to an existing file; `check` and the baseline stay rc 0.",
      "The standards file contains only judgement rules; each mechanical rule it would have held is named with the check that enforces it."],
     []),
    ("CT-05", "CT-05: Ticket ledger generator",
     "**What to build:** one mise task regenerates the ticket ledger from the tracker's parent and blocking relationships plus the lane records, preserving the hand-maintained local-state column, and validates every lane record against its schema.",
     ["Running the task twice without tracker changes yields a byte-identical ledger; a lane record missing a required field fails validation with the field named.",
      "Frontier and blocker columns match a live `gh api graphql` read for the same snapshot; the task makes no tracker mutation.",
      "`check` and the baseline stay rc 0."],
     []),
    ("CT-06", "CT-06: Lane retrospective command",
     "**What to build:** a user-invoked skill `/lane-retro <unit>` that spawns the retro writer with the lane's diff, exits and review disposition, applies every actionable finding to its destination by kind, reruns the affected checks and the gate, repeats until no actionable finding remains, and files the record.",
     ["On a lane with a known navigation defect the command produces a record whose finding is applied to the nearest directory guidance file and the gate passes.",
      "Cross-scope findings are listed for the parent with the exact edit instead of being applied outside the lane's allowlist.",
      "The command makes no tracker or publication mutation."],
     ["CT-01", "CT-03"]),
    ("CT-07", "CT-07: Codex compatibility",
     "**What to build:** the project's Codex role definitions and configuration name the same roles, lanes and gate as the Claude side, and the cross-agent skill directory mirrors the Claude skill directory byte for byte under a test, so Codex can take a lane after its limit resets.",
     ["Codex's native configuration validation accepts the updated roles; each role's instructions point at the lane record and the retro gate.",
      "The mirror test fails on a one-byte drift between the two skill directories and passes on identical trees.",
      "`check` and the baseline stay rc 0."],
     ["CT-02", "CT-03"]),
    ("CT-08", "CT-08: Baseline transition v2",
     "**What to build:** a reviewed, versioned baseline transition that adds the lane worktree directory and the local settings file to `.gitignore`, keeps the original nineteen hashes as historical evidence, and makes the baseline check verify the versioned successor.",
     ["The baseline check reports the transition version and passes on the new `.gitignore`; the original hash record is unchanged and still cited.",
      "The container acceptance inputs other than `.gitignore` are byte-identical to the original record.",
      "The transition has an independent review disposition before it is integrated."],
     ["CT-02"]),
    ("CT-09", "CT-09: Plugin, skill and tool evaluation",
     "**What to build:** an evidence-based evaluation of candidate additions — `gh-stack` for stacked lane pull requests, AgentsView recall, a status-band mod built with `/plugin-authoring`, version control for the agent-protocol package — recorded as a decision table with adopted items ticketed and rejected items reasoned.",
     ["Each candidate has a tried-or-read evidence note, a cost (context load, install footprint) and a decision; nothing is installed as a side effect of evaluating it.",
      "Adopted items appear as new tickets with blocking edges; rejected items carry an evidence-backed reason.",
      "`check` and the baseline stay rc 0."],
     []),
    ("CT-11", "CT-11: Serialize named checks across worktrees",
     "**What to build:** concurrent `./dev/mise run check` / `check:research` invocations from different lane worktrees no longer race on shared tool state: the named checks take a repository-wide lock (bounded wait, deterministic refusal with the holder's identity on timeout) and the retro gate records the lock outcome, so a raced run can never be mistaken for a pass.",
     ["Two concurrent `check:research` runs from two worktrees serialize; the second waits or refuses with a reason naming the holder, and neither leaves test scratch directories in a checkout.",
      "The lock is exercised by a hermetic test with two subprocesses; a stale lock from a dead process is reclaimed deterministically.",
      "`check`, `check:acceptance-baseline` and `git diff --check` stay rc 0; the two observed races on 2026-10-13 (fifteen `test:collect` errors; a transient `mise ERROR`) are cited as the motivating evidence."],
     ["CT-01"]),
    ("CT-10", "CT-10: codex-session-history coverage and evaluation",
     "**What to build:** hermetic tests for the thread-history, log and child-thread subcommands, a stub daemon for the AgentsView wrapper and a fixture for the OTel export, plus one run of the skill-creator evaluation loop with recorded pass rates.",
     ["Every script under the skill has at least one fixture-backed test under a temporary `CODEX_HOME`; the real record stores are never read in tests.",
      "The evaluation loop's with-skill and baseline runs are recorded with their assertions and pass rates in the skill workspace.",
      "`check` and the baseline stay rc 0."],
     []),
]


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def ticket_body(local_id, what, criteria, blockers, parent_local="the spec issue"):
    lines = ["## Parent", "", f"The takeover spec issue ({parent_local}).", "", "## What to build", "", what, "",
             "## Acceptance criteria", ""]
    lines += [f"- [ ] {c}" for c in criteria]
    lines += ["", "## Blocked by", ""]
    lines += [f"- {b}" for b in blockers] if blockers else ["- None (can start immediately)."]
    lines += ["", f"Local ID: {local_id}. Execution boundary: one lane, one worktree, explicit path allowlist, about five maintained files and 300 handwritten lines; retro record required before integration; no push, publication, closure or host-heavy operation is implied by this ticket."]
    return "\n".join(lines) + "\n"


def main():
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "spec":
        body = open(SPEC_MD, encoding="utf-8").read()
        tickets = [{"local_id": "CT-SPEC", "title": SPEC_TITLE, "body": body, "body_sha256": sha(body), "labels": []}]
        data = {"version": 2, "repo": REPO, "parent_number": None, "tickets": tickets}
    else:
        parent = int(sys.argv[3])
        tickets = []
        for local_id, title, what, criteria, blockers in TICKETS:
            body = ticket_body(local_id, what, criteria, blockers, f"#{parent}")
            tickets.append({"local_id": local_id, "title": title, "body": body, "body_sha256": sha(body), "labels": []})
        data = {"version": 2, "repo": REPO, "parent_number": parent, "tickets": tickets}
    raw = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(raw)
    print(f"wrote {out} tickets={len(tickets)} manifest_sha256={sha(raw)}")


if __name__ == "__main__":
    main()

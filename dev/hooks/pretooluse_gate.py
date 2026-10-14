#!/usr/bin/env python3
"""Claude Code PreToolUse hook: deny `git merge`, `git push` and `delivery:publish` of a failing lane,
and raw `gh` writes, which must take the scanned `gh:write` route (D179).

Reads the hook JSON on stdin. For each merge/push segment of a Bash command the
lane is the branch `git name-rev MERGE_HEAD` names when a merge is in progress,
else each claude/|codex/ branch the command merges or pushes (the retro gate maps
it through the lane record's `branch`), else the current branch for a bare push.
The integration branch and `main` are never units. `delivery:publish` pushes with
`--no-verify`, so it checks the lane merges not yet on a remote, as hk pre-push
does. A refusal prints the deny JSON; an allow exits 0 with no output.

One of the three deny gates that stay settings hooks rather than mods (D102); evidence and the
upstream issues to watch: docs/agents/hooks-and-mods.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shlex
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import git_gate  # noqa: E402

SEGMENT = re.compile(r"&&|\|\||[;|&\n]")
CONTINUATION = re.compile(r"\\\r?\n")  # a backslash-newline continues the same simple command
VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
# D179 (2026-10-14): dated exception to D92/D113 (rule 14) until the D131 C++ gate port (CT-02b.4).
GH_READS = {"issue": {"list", "ls", "view", "status"},
            "pr": {"list", "ls", "view", "status", "diff", "checks", "checkout", "co"},
            "release": {"list", "ls", "view", "download", "verify", "verify-asset"},
            "gist": {"list", "ls", "view", "clone"}, "label": {"list", "ls"},
            "repo": {"list", "ls", "view", "clone", "set-default", "gitignore", "license", "deploy-key list",
                     "autolink list", "autolink view"}}
GH_VERBS = {"create", "new", "edit", "comment", "review", "close", "reopen", "merge", "ready", "delete", "transfer",
            "pin", "unpin", "lock", "unlock", "develop", "upload", "delete-asset", "rename", "archive", "unarchive",
            "fork", "sync", "update-branch", "revert", "deploy-key add", "deploy-key delete", "autolink create",
            "autolink delete"}
API_VALUES = {"-X": "method", "--method": "method", "-f": "field", "--raw-field": "field", "-F": "typed",
              "--field": "typed", "--input": "input", "-H": "", "--header": "", "-q": "", "--jq": "", "-t": "",
              "--template": "", "--hostname": "", "-p": "", "--preview": "", "--cache": ""}
API_FLAGS = {"-i", "--include", "--paginate", "--silent", "--slurp", "--verbose", "-h", "--help"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
GH_ROUTE = ("raw gh write refused ({form}; D179): GitHub text passes the secret and private-name scan first. Use "
            "./dev/mise run gh:write -- <gh args> (scans every argument and named file, then runs gh with the same "
            "argv), or issue:create-preview and issue:preview for new issues, bodies and labels "
            "(docs/agents/issue-tracker.md).")


def actions(command: str):
    """Yield (verb, args, -C dir) for each git merge/push or delivery:publish segment."""
    for segment in SEGMENT.split(CONTINUATION.sub(" ", command)):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        if any("delivery:publish" in token for token in tokens):
            yield "publish", [], None
            continue
        if "git" not in tokens:
            continue
        rest, directory = tokens[tokens.index("git") + 1:], None
        while rest and rest[0].startswith("-"):
            option = rest.pop(0)
            if option in VALUE_OPTIONS and rest:
                value = rest.pop(0)
                directory = value if option == "-C" else directory
        if rest and rest[0] in ("merge", "push"):
            yield rest[0], rest[1:], directory


def gh_writes(command: str, depth: int = 0):
    """Yield the form of each raw gh write in a Bash command, read from tokens, never substrings."""
    for segment in SEGMENT.split(CONTINUATION.sub(" ", command)):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        for index, token in enumerate(tokens):
            name, rest = Path(re.split(r"\$\(|[`(]", token)[-1]).name, tokens[index + 1:]  # x=$(gh, `gh
            if depth < 3 and name == "eval":
                yield from gh_writes(" ".join(rest), depth + 1)
            elif depth < 3 and name in SHELLS:  # bash -lc '<script>'
                while rest and rest[0].startswith("-"):
                    if "c" in rest.pop(0)[1:] and rest:
                        yield from gh_writes(rest[0], depth + 1)
            elif name == "gh" and (form := gh_form([t.rstrip(")`") for t in rest])):
                yield form


def gh_form(args: list[str]) -> str | None:
    """The write form of one gh invocation's arguments, or None for a read; unsure means a write."""
    while args and args[0].startswith("-"):  # root options; -R/--repo take a value
        if args.pop(0) in ("-R", "--repo") and args:
            args.pop(0)
    if not args or args[0] not in (*GH_READS, "api"):
        return None
    if args[0] == "api":
        return api_form(args[1:])
    words, rest = [], args[1:]
    while rest and len(words) < 2:
        token = rest.pop(0)
        if token in ("-R", "--repo") and rest:
            rest.pop(0)
        elif not token.startswith("-"):
            words.append(token)
    verb = " ".join(words[:2]) if words[:1] in (["deploy-key"], ["autolink"]) else (words or [None])[0]
    if verb is None or verb in GH_READS[args[0]]:
        return None
    return f"gh {args[0]} {verb if verb in GH_VERBS else '<subcommand outside the read list>'}"


def api_form(args: list[str]) -> str | None:
    method, sent, endpoint = None, [], None
    while args:
        token = args.pop(0)
        if not token.startswith("-") or token == "-":
            endpoint = endpoint or token
            continue
        if token in API_FLAGS:
            continue
        if token.startswith("--"):
            name, equals, value = token.partition("=")
        else:  # a pflag shorthand cluster: bool letters, then one value letter
            cluster = token[1:].lstrip("ih")
            name, equals, value = f"-{cluster[:1]}", bool(cluster[1:]), cluster[1:]
        if name not in API_VALUES or not (equals or args):
            return "gh api with an option the gate cannot parse"
        value = value if equals else args.pop(0)
        if API_VALUES[name] == "method":
            method = value.upper()
        elif API_VALUES[name]:
            sent.append((API_VALUES[name], value))
    if endpoint and endpoint.rstrip("/").rsplit("/", 1)[-1] == "graphql":
        queries = [(kind, value.partition("=")[2]) for kind, value in sent if value.partition("=")[0] == "query"]
        if not queries or any(kind == "input" for kind, _ in sent) or any(
                (kind == "typed" and query.startswith("@")) or "$" in query or "`" in query for kind, query in queries):
            return "gh api graphql without an inline query"  # a file, a variable or a substitution is unreadable
        return "gh api graphql mutation" if any(re.search(r"\bmutation\b", q) for _, q in queries) else None
    method = method or ("POST" if sent else "GET")
    if method == "GET":
        return None
    return f"gh api {method if method in ('POST', 'PUT', 'PATCH', 'DELETE') else 'non-GET method'}"


def lanes_for(verb: str, args: list[str], repo: str) -> list[str]:
    if verb == "publish":
        return git_gate.unpublished_lanes(repo)
    if verb == "merge" and {"--abort", "--quit"} & set(args):
        return []
    if verb == "merge" and git_gate.git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD"):
        return git_gate.classify(repo, git_gate.merge_sources(repo))[0]
    named = [arg.lstrip("+").split(":", 1)[0] for arg in args if not arg.startswith("-")]
    if verb == "push":  # git push [remote] [refspec...]; no refspec or HEAD means the current branch
        current = git_gate.git(repo, "branch", "--show-current") or ""
        named = [current if name == "HEAD" else name for name in named[1:]] or [current]
    return list(dict.fromkeys(filter(None, map(git_gate.lane_branch, named))))


def main() -> int:
    try:
        event = json.loads(sys.stdin.read(1 << 20) or "{}")
    except ValueError:
        return 0
    if not isinstance(event, dict) or event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command")
    if not isinstance(command, str):
        return 0
    reasons = [GH_ROUTE.format(form=form) for form in dict.fromkeys(gh_writes(command))] if "gh" in command else []
    refusals: list[str] = []
    if re.search(r"\bmerge\b|\bpush\b|delivery:publish", command):
        cwd = Path(str(event.get("cwd") or "."))
        for verb, args, directory in actions(command):
            repo = git_gate.git(cwd / directory if directory else cwd, "rev-parse", "--show-toplevel")
            if repo:
                refusals += git_gate.check_lanes(repo, lanes_for(verb, args, repo))
    if refusals:
        reasons.append("\n".join(refusals) + "\nWrite or fix the lane's retro record (docs/agents/ticket-retro.md).")
    if reasons:
        reason = "\n".join(reasons)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

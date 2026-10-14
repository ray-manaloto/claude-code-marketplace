"""Exact-input local commit and non-force branch publication.

Called only through qualified project mise tasks. All subprocess output is
captured: Git URLs and scanner findings are never echoed by this program.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tarfile
import tempfile


OID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}\Z")
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]*\Z")
MIXED_FILES = {"mise.dev.toml", "dev/saved-searches.toml"}
GIT = ["git", "--literal-pathspecs", "-c", "core.hooksPath=/dev/null"]


class Refusal(Exception):
    pass


def run(argv: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> bytes:
    try:
        result = subprocess.run(
            argv, cwd=cwd, env=env, capture_output=True, check=False, timeout=180
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Refusal(f"command could not complete: {argv[0]}") from exc
    if result.returncode:
        raise Refusal(f"command failed (rc={result.returncode}): {argv[0]}")
    return result.stdout.rstrip(b"\n")


def git(root: Path, *args: str) -> bytes:
    # File hooks are bypassed; only non-executing configured events are admitted.
    return run([*GIT, *args], cwd=root)


def safe_configured_hooks(raw: bytes) -> None:
    # commit-tree skips commit hooks; push --no-verify skips pre-push. Every
    # other configured event is refused because its command may load mutable
    # files outside the hashed core.hooksPath tree.
    safe_events = {b"pre-commit", b"commit-msg", b"pre-push"}
    hooks: dict[bytes, dict[bytes, bytes]] = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        try:
            key, value = entry.split(b"\n", 1)
            section, field = key.rsplit(b".", 1)
        except ValueError as exc:
            raise Refusal("invalid configured Git hook") from exc
        if not section.startswith(b"hook.") or field not in (b"event", b"command"):
            raise Refusal("unsupported configured Git hook")
        fields = hooks.setdefault(section, {})
        if field in fields:
            raise Refusal("duplicate configured Git hook field")
        fields[field] = value
    for fields in hooks.values():
        if fields.keys() != {b"event", b"command"} or fields[b"event"] not in safe_events or not fields[b"command"]:
            raise Refusal("configured Git hook could execute during delivery")


def hook_tree_digest(root: Path) -> str:
    configured = subprocess.run(
        ["git", "config", "--path", "--get", "core.hooksPath"],
        cwd=root, capture_output=True, check=False, timeout=30,
    )
    if configured.returncode not in (0, 1):
        raise Refusal("cannot inspect Git hook configuration")
    if configured.returncode == 0:
        raw = configured.stdout.rstrip(b"\n").decode("utf-8")
        target = Path(raw)
        if not target.is_absolute():
            target = root / target
    else:
        common = Path(git(root, "rev-parse", "--git-common-dir").decode("ascii"))
        target = (common if common.is_absolute() else root / common) / "hooks"
        raw = "<default>"
    digest = hashlib.sha256()
    digest.update(raw.encode("utf-8") + b"\0")
    digest.update(str(target.resolve()).encode("utf-8") + b"\0")
    configured_hooks = subprocess.run(
        [*GIT, "config", "--null", "--get-regexp", r"^hook\."],
        cwd=root, capture_output=True, check=False, timeout=30,
    )
    if configured_hooks.returncode not in (0, 1):
        raise Refusal("cannot inspect configured Git hooks")
    safe_configured_hooks(configured_hooks.stdout)
    digest.update(b"configured-hooks\0" + configured_hooks.stdout)
    if target.is_symlink():
        raise Refusal("Git hook directory is a symlink")
    if not target.exists():
        digest.update(b"absent\0")
        return digest.hexdigest()
    if not target.is_dir():
        raise Refusal("Git hook path is not a directory")
    for entry in sorted(target.rglob("*")):
        if entry.is_symlink():
            raise Refusal("Git hook tree contains a symlink")
        relative = entry.relative_to(target).as_posix().encode("utf-8")
        mode = entry.stat().st_mode
        digest.update(relative + b"\0" + str(mode).encode() + b"\0")
        if entry.is_file():
            with entry.open("rb") as stream:
                digest.update(hashlib.file_digest(stream, "sha256").digest())
        elif not entry.is_dir():
            raise Refusal("Git hook tree contains a non-file entry")
    return digest.hexdigest()


def hook_guard(args: argparse.Namespace, root: Path) -> None:
    if not re.fullmatch(r"[0-9a-f]{64}", args.hook_tree_sha256 or ""):
        raise Refusal("approved hook-tree digest is required")
    if hook_tree_digest(root) != args.hook_tree_sha256:
        raise Refusal("Git hook preimage drift")


def path_arg(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or value.startswith("-")
        or any(char in value for char in ":*?[]")
        or any(part in ("", ".", "..") for part in value.split("/"))
        or "\\" in value
    ):
        raise Refusal("selected paths must be exact relative file paths")
    return value


def parse_pre_staged(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in values:
        try:
            path, oid = item.rsplit("=", 1)
        except ValueError as exc:
            raise Refusal("pre-staged input needs path=blob SHA") from exc
        path_arg(path)
        if path in result or not OID.fullmatch(oid):
            raise Refusal("invalid or duplicate pre-staged binding")
        result[path] = oid
    return result


def names(root: Path, *args: str) -> set[str]:
    raw = git(root, "diff", "--name-only", "-z", *args)
    return {os.fsdecode(name) for name in raw.split(b"\0") if name}


def staged_entry(root: Path, path: str) -> tuple[str, str]:
    entries = git(root, "ls-files", "--stage", "-z", "--", path).split(b"\0")
    matches = []
    for entry in entries:
        if not entry:
            continue
        meta, name = entry.split(b"\t", 1)
        if os.fsdecode(name) == path:
            matches.append(meta.split())
    if len(matches) != 1 or matches[0][2] != b"0" or matches[0][0] not in (b"100644", b"100755"):
        raise Refusal("pre-staged path is absent or has unmerged index entries")
    return matches[0][0].decode("ascii"), matches[0][1].decode("ascii")


def staged_blob(root: Path, path: str) -> str:
    return staged_entry(root, path)[1]


def selected_state(root: Path, paths: set[str], pre: dict[str, str], tree: str | None) -> str:
    if names(root, "--cached", "HEAD") != paths:
        raise Refusal("staged path set differs from selected paths")
    for path in paths:
        staged_entry(root, path)
    for path, oid in pre.items():
        if staged_blob(root, path) != oid:
            raise Refusal("pre-staged blob drift")
    ordinary = sorted(paths - pre.keys())
    if ordinary and names(root, "--", *ordinary):
        raise Refusal("selected working file differs from staged content")
    actual_tree = git(root, "write-tree").decode("ascii")
    if tree and actual_tree != tree:
        raise Refusal("reviewed index tree drift")
    return actual_tree


def check_selected_tree(root: Path, tree: str) -> None:
    # Mixed files intentionally differ from the working checkout. Run the
    # static baseline and delivery tests on the exact index tree as well.
    with tempfile.TemporaryDirectory(prefix="a09-selected-") as temp:
        selected = Path(temp) / "selected"
        selected.mkdir()
        archive = Path(temp) / "selected.tar"
        git(root, "archive", "--format=tar", f"--output={archive}", tree)
        with tarfile.open(archive) as stream:
            stream.extractall(selected, filter="data")
        # The scratch repository must not inherit caller Git config, indexes,
        # namespaces or hook commands.
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env["PATH"] = os.pathsep.join(("/usr/bin", "/bin", env.get("PATH", "")))
        env["GIT_CONFIG_GLOBAL"] = os.devnull
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        env["MARKETPLACE_PYTHON"] = sys.executable
        for argv in (("git", "init", "-q"), ("git", "add", "-f", "-A")):
            run(list(argv), cwd=selected, env=env)
        scratch_tree = run(["git", "write-tree"], cwd=selected, env=env).decode("ascii")
        if scratch_tree != tree:
            raise Refusal("scratch validation tree differs from reviewed index tree")
        commit = run(
            ["git", "-c", "user.name=A09 Selected Tree", "-c", "user.email=a09@example.invalid",
             "commit-tree", scratch_tree, "-m", "selected tree check"],
            cwd=selected, env=env,
        ).decode("ascii")
        run(["git", "update-ref", "HEAD", commit], cwd=selected, env=env)
        for argv in (
            ("tasks", "validate"),
            ("run", "check"),
            ("run", "check:acceptance-baseline"),
            ("run", "test:delivery"),
        ):
            run([str(selected / "dev/mise"), *argv], cwd=selected, env=env)


def identity(args: argparse.Namespace) -> Path:
    root = Path(args.root).resolve(strict=True)
    if Path.cwd().resolve() != root or Path(git(root, "rev-parse", "--show-toplevel").decode()).resolve() != root:
        raise Refusal("active writer root mismatch")
    common = Path(git(root, "rev-parse", "--git-common-dir").decode())
    if not common.is_absolute():
        common = root / common
    if common.resolve() != Path(args.common_dir).resolve():
        raise Refusal("Git common directory mismatch")
    if not OID.fullmatch(args.head) or git(root, "rev-parse", "HEAD").decode() != args.head:
        raise Refusal("HEAD drift")
    if git(root, "symbolic-ref", "--quiet", "--short", "HEAD").decode() != args.branch:
        raise Refusal("branch mismatch or detached HEAD")
    if not SAFE_NAME.fullmatch(args.remote) or args.remote.startswith("-"):
        raise Refusal("invalid remote name")
    if not git(root, "check-ref-format", "--branch", args.branch):
        raise Refusal("invalid branch")
    if len(args.remote_url_sha256) != 64 or not re.fullmatch(r"[0-9a-f]{64}", args.remote_url_sha256):
        raise Refusal("invalid remote URL digest")
    urls = git(root, "remote", "get-url", "--push", "--all", args.remote).splitlines()
    fetch_urls = git(root, "remote", "get-url", "--all", args.remote).splitlines()
    if len(urls) != 1 or fetch_urls != urls or hashlib.sha256(urls[0]).hexdigest() != args.remote_url_sha256:
        raise Refusal("push remote identity mismatch")
    if args.action != "inspect-hooks":
        hook_guard(args, root)
    return root


def check_tracing() -> None:
    if any(
        value and (key.startswith("GIT_TRACE") or key in {"GIT_CURL_VERBOSE", "GIT_DEBUG"})
        for key, value in os.environ.items()
    ):
        raise Refusal("unsafe Git tracing is active")


def remote_head(root: Path, remote: str, branch: str) -> str | None:
    ref = f"refs/heads/{branch}"
    lines = git(root, "ls-remote", "--heads", "--refs", remote, ref).splitlines()
    if not lines:
        return None
    if len(lines) != 1:
        raise Refusal("ambiguous remote branch")
    oid, found_ref = lines[0].split(b"\t", 1)
    if found_ref != ref.encode() or not OID.fullmatch(oid.decode("ascii")):
        raise Refusal("invalid remote branch response")
    return oid.decode("ascii")


def scan(root: Path, binary: str, *mode: str, baseline: Path | None = None, report: bool = False) -> tuple[int, bytes]:
    if not Path(binary).is_absolute():
        raise Refusal("scanner path must be absolute")
    for name in (".gitleaksignore", ".betterleaksignore"):
        if os.path.lexists(root / name):
            raise Refusal(f"checkout root holds {name}, which the scanner loads whatever --gitleaks-ignore-path names")
    with tempfile.TemporaryDirectory(prefix="a09-scan-") as temp:
        ignore = Path(temp) / "empty-ignore"
        ignore.touch()
        env = os.environ.copy()
        # betterleaks reads its own names before the gitleaks ones.
        for name in ("BETTERLEAKS_CONFIG", "BETTERLEAKS_CONFIG_TOML", "GITLEAKS_CONFIG", "GITLEAKS_CONFIG_TOML"):
            env.pop(name, None)
        command = [binary, "git", "--no-banner", "--redact=100", "--log-level=error",
                   "--config", str(root / ".gitleaks.toml"), "--gitleaks-ignore-path", str(ignore)]
        if baseline:
            command.extend(("--baseline-path", str(baseline)))
        if report:
            command.extend(("--report-format=json", "--report-path=-"))
        command.extend((*mode, str(root)))
        try:
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, check=False, timeout=300)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Refusal("secret scan could not complete") from exc
        if result.returncode == 1 and not report:
            raise Refusal("secret scan found potential leaks; independent owner adjudication required")
        if result.returncode not in ((0, 1) if report else (0,)):
            raise Refusal(f"secret scan failed (rc={result.returncode})")
        return result.returncode, result.stdout


def fingerprints(report: bytes) -> set[str]:
    try:
        findings = json.loads(report)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refusal("invalid redacted scanner report") from exc
    if not isinstance(findings, list) or not all(isinstance(item, dict) and isinstance(item.get("Fingerprint"), str) for item in findings):
        raise Refusal("scanner report lacks finding fingerprints")
    result = {item["Fingerprint"] for item in findings}
    if len(result) != len(findings):
        raise Refusal("duplicate scanner finding fingerprint")
    return result


def reviewed_baseline(args: argparse.Namespace, root: Path) -> tuple[bytes, set[str]] | None:
    if not args.adjudication_file and not args.adjudication_sha256:
        return None
    if not args.adjudication_file or not re.fullmatch(r"[0-9a-f]{64}", args.adjudication_sha256 or ""):
        raise Refusal("baseline needs an exact adjudication file digest")
    source = Path(args.adjudication_file)
    if not source.is_absolute() or source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(root):
        raise Refusal("adjudication must be a regular file in this checkout")
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.adjudication_sha256:
        raise Refusal("adjudication digest mismatch")
    try:
        adjudication = json.loads(raw)
        baseline = adjudication["baseline_report"]
        triage = adjudication["independent_read_only_triage"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise Refusal("invalid adjudication receipt") from exc
    if (
        adjudication.get("schema_version") != 1
        or adjudication.get("pre_baseline_exit_code") != 1
        or adjudication.get("adjudication_status") != "independently_reviewed_pending_publish_gate"
        or adjudication.get("scanned_head") != args.head
        or triage.get("finding_count") != adjudication.get("pre_baseline_finding_count")
        or not triage.get("reviewer")
        or not adjudication.get("decision", "").startswith("Treat these exact")
    ):
        raise Refusal("adjudication scope is not this HEAD or lacks independent review")
    path = path_arg(baseline["path"])
    report_file = root / path
    if report_file.is_symlink() or not report_file.is_file() or not report_file.resolve().is_relative_to(root):
        raise Refusal("baseline report path is unsafe")
    report = report_file.read_bytes()
    if not re.fullmatch(r"[0-9a-f]{64}", baseline["sha256"]) or hashlib.sha256(report).hexdigest() != baseline["sha256"]:
        raise Refusal("baseline report digest mismatch")
    known = fingerprints(report)
    if len(known) != adjudication["pre_baseline_finding_count"]:
        raise Refusal("baseline finding count mismatch")
    return report, known


def publish(args: argparse.Namespace, root: Path, paths: set[str], pre: dict[str, str]) -> tuple[str, int]:
    selected_state(root, paths, pre, args.index_tree)
    git(root, "diff", "--cached", "--check")
    check_selected_tree(root, args.index_tree)
    remote_before = remote_head(root, args.remote, args.branch)
    for task in args.check_task:
        if not SAFE_NAME.fullmatch(task):
            raise Refusal("invalid check task name")
        run([str(root / "dev/mise"), "run", task], cwd=root)
    identity(args)
    selected_state(root, paths, pre, args.index_tree)
    scan(root, args.gitleaks_bin, "--pre-commit", "--staged")
    identity(args)
    selected_state(root, paths, pre, args.index_tree)
    message = Path(args.message_file).resolve(strict=True)
    if message.is_relative_to(root):
        raise Refusal("commit message file must be outside the checkout")
    commit = git(root, "commit-tree", args.index_tree, "-p", args.head, "-F", str(message)).decode("ascii")
    if not OID.fullmatch(commit):
        raise Refusal("invalid commit identity")
    git(root, "update-ref", f"refs/heads/{args.branch}", commit, args.head)
    if remote_before:
        if subprocess.run([*GIT, "cat-file", "-e", f"{remote_before}^{{commit}}"], cwd=root, capture_output=True, check=False).returncode:
            git(root, "fetch", "--no-tags", args.remote, f"refs/heads/{args.branch}")
            if git(root, "rev-parse", "FETCH_HEAD").decode() != remote_before:
                raise Refusal("remote changed during fetch")
        if subprocess.run([*GIT, "merge-base", "--is-ancestor", remote_before, commit], cwd=root, capture_output=True, check=False).returncode:
            raise Refusal("remote branch is not an ancestor of the commit")
    log_range = f"{remote_before}..{commit}" if remote_before else commit
    known = reviewed_baseline(args, root)
    history_rc, raw_report = scan(root, args.gitleaks_bin, f"--log-opts={log_range}", report=True)
    if history_rc == 1:
        if known is None:
            raise Refusal("outbound scan found potential leaks; independent owner adjudication required")
        if fingerprints(raw_report) != known[1]:
            raise Refusal("outbound findings differ from the exact reviewed baseline")
        with tempfile.TemporaryDirectory(prefix="a09-baseline-") as temp:
            baseline = Path(temp) / "reviewed-redacted.json"
            baseline.write_bytes(known[0])
            scan(root, args.gitleaks_bin, f"--log-opts={log_range}", baseline=baseline)
    elif known is not None and known[1]:
        raise Refusal("reviewed baseline does not match the fresh outbound scan")
    if git(root, "rev-parse", "HEAD").decode() != commit or git(root, "rev-parse", "HEAD^{tree}").decode() != args.index_tree:
        raise Refusal("commit changed before publication")
    if remote_head(root, args.remote, args.branch) != remote_before:
        raise Refusal("remote branch changed before publication")
    # A second URL check closes configuration drift between first contact and push.
    expected_head = args.head
    args.head = commit
    try:
        identity(args)
    finally:
        args.head = expected_head
    git(root, "push", "--no-verify", args.remote, f"{commit}:refs/heads/{args.branch}")
    hook_guard(args, root)
    if remote_head(root, args.remote, args.branch) != commit:
        raise Refusal("remote postimage does not match the committed SHA")
    return commit, history_rc


def stage_blob(args: argparse.Namespace, root: Path) -> None:
    if args.path not in (["mise.dev.toml"], ["dev/saved-searches.toml"]):
        raise Refusal("stage-blob is restricted to the two reviewed mixed files")
    if args.pre_staged or not args.content_file or not args.content_sha256:
        raise Refusal("stage-blob requires one reviewed content file and digest")
    path = args.path[0]
    if (root / path).is_symlink():
        raise Refusal("mixed file target is a symlink")
    if git(root, "ls-files", "--stage", "-z", "--", path):
        staged_entry(root, path)
    if names(root, "--cached", "HEAD") - MIXED_FILES:
        raise Refusal("unrelated paths are staged")
    source = Path(args.content_file)
    if not source.is_absolute() or source.is_symlink() or not source.is_file():
        raise Refusal("reviewed content must be an absolute regular non-symlink file")
    source = source.resolve(strict=True)
    if source.is_relative_to(root) or not stat.S_ISREG(source.stat().st_mode):
        raise Refusal("reviewed content must be outside the checkout")
    content = source.read_bytes()
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refusal("reviewed content is not UTF-8") from exc
    if not re.fullmatch(r"[0-9a-f]{64}", args.content_sha256) or hashlib.sha256(content).hexdigest() != args.content_sha256:
        raise Refusal("reviewed content digest mismatch")
    result = subprocess.run([*GIT, "hash-object", "-w", "--stdin"], input=content, cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise Refusal(f"blob write failed (rc={result.returncode})")
    oid = result.stdout.strip().decode("ascii")
    if not OID.fullmatch(oid):
        raise Refusal("invalid staged blob identity")
    git(root, "update-index", "--add", "--cacheinfo", "100644", oid, path)
    if staged_blob(root, path) != oid:
        raise Refusal("staged blob postimage mismatch")
    hook_guard(args, root)
    print(f"blob={oid}")


def load_intent(args: argparse.Namespace) -> None:
    keys = {
        "root", "common_dir", "branch", "head", "remote", "remote_url_sha256",
        "path", "pre_staged", "index_tree", "message_file", "check_task",
        "gitleaks_bin", "content_file", "content_sha256",
        "adjudication_file", "adjudication_sha256", "hook_tree_sha256",
    }
    if not args.intent_file:
        if args.intent_sha256:
            raise Refusal("intent digest requires an intent file")
        args.path = args.path or []
        args.pre_staged = args.pre_staged or []
        args.check_task = args.check_task or []
        return
    if any(getattr(args, key) is not None for key in keys):
        raise Refusal("intent file cannot be mixed with direct arguments")
    source = Path(args.intent_file)
    if not source.is_absolute() or source.is_symlink() or not source.is_file():
        raise Refusal("intent must be an absolute regular non-symlink file")
    raw = source.read_bytes()
    if not args.intent_sha256 or not re.fullmatch(r"[0-9a-f]{64}", args.intent_sha256) or hashlib.sha256(raw).hexdigest() != args.intent_sha256:
        raise Refusal("intent digest mismatch")
    try:
        document = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refusal("invalid intent JSON") from exc
    if not isinstance(document, dict) or set(document) - keys - {"action"} or document.get("action") != args.action:
        raise Refusal("intent action or keys mismatch")
    for key in keys:
        value = document.get(key)
        if key in {"path", "pre_staged", "check_task"}:
            if value is not None and (not isinstance(value, list) or not all(isinstance(item, str) for item in value)):
                raise Refusal("invalid intent list")
            value = value or []
        elif value is not None and not isinstance(value, str):
            raise Refusal("invalid intent value")
        setattr(args, key, value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inspect-hooks", "stage-blob", "prepare", "publish"))
    for flag in ("root", "common-dir", "branch", "head", "remote", "remote-url-sha256"):
        parser.add_argument(f"--{flag}")
    parser.add_argument("--path", action="append")
    parser.add_argument("--pre-staged", action="append")
    parser.add_argument("--index-tree")
    parser.add_argument("--message-file")
    parser.add_argument("--check-task", action="append")
    parser.add_argument("--gitleaks-bin")
    parser.add_argument("--content-file")
    parser.add_argument("--content-sha256")
    parser.add_argument("--adjudication-file")
    parser.add_argument("--adjudication-sha256")
    parser.add_argument("--hook-tree-sha256")
    parser.add_argument("--intent-file")
    parser.add_argument("--intent-sha256")
    args = parser.parse_args()
    try:
        load_intent(args)
        if any(not getattr(args, key) for key in ("root", "common_dir", "branch", "head", "remote", "remote_url_sha256")):
            raise Refusal("missing Git identity binding")
        check_tracing()
        if args.action == "inspect-hooks":
            print(f"hook_tree_sha256={hook_tree_digest(identity(args))}")
            return 0
        if args.action == "stage-blob":
            stage_blob(args, identity(args))
            if args.intent_sha256:
                print(f"intent_sha256={args.intent_sha256}")
            return 0
        pre = parse_pre_staged(args.pre_staged)
        ordinary = {path_arg(path) for path in args.path}
        if not ordinary and not pre or ordinary & pre.keys() or len(ordinary) != len(args.path):
            raise Refusal("selected paths are empty, duplicated or overlapping")
        if ordinary & MIXED_FILES:
            raise Refusal("mixed files require an exact pre-staged blob")
        paths = ordinary | pre.keys()
        root = identity(args)
        if args.action == "prepare":
            if names(root, "--cached", "HEAD") != pre.keys():
                raise Refusal("unreviewed paths were already staged")
            for path, oid in pre.items():
                if staged_blob(root, path) != oid:
                    raise Refusal("pre-staged blob drift")
            if ordinary:
                git(root, "add", "-A", "--", *sorted(ordinary))
            tree = selected_state(root, paths, pre, None)
            hook_guard(args, root)
            print(f"head={args.head}\nindex_tree={tree}")
        else:
            if not args.index_tree or not OID.fullmatch(args.index_tree) or not args.message_file or not args.gitleaks_bin or not args.check_task:
                raise Refusal("publish requires tree, message, scanner and named checks")
            commit, history_rc = publish(args, root, paths, pre)
            print(f"published={commit}\nhistory_scan_rc={history_rc}")
            if history_rc == 1:
                print("baseline_residual_rc=0")
        if args.intent_sha256:
            print(f"intent_sha256={args.intent_sha256}")
    except (Refusal, OSError, ValueError) as exc:
        print(f"A09 refused: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Download and inspect captured GCC bottles without extracting or installing."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence/gcc-bootstrap"
PREFIX = Path("/opt/homebrew")
LINK_DIRS = {"bin", "sbin", "include", "lib", "share", "Frameworks"}
PACKAGES = {"isl": "0.28", "mpfr": "4.2.2", "libmpc": "1.4.1", "gcc": "16.2.0"}
BOOTSTRAP_DIRS = ("bin", "etc", "include", "lib", "sbin", "share", "var", "opt",
                  "Cellar", "Caskroom", "Frameworks", "etc/bash_completion.d",
                  "share/zsh", "share/zsh/site-functions", "share/doc", "share/man",
                  "share/man/man1", "var/homebrew", "var/homebrew/linked")


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def preimage(path):
    if path.is_symlink():
        return {"kind": "symlink", "target": os.readlink(path)}
    if path.is_dir():
        return {"kind": "directory", "uid": path.stat().st_uid,
                "mode": oct(path.stat().st_mode & 0o777)}
    if path.is_file():
        return {"kind": "file", "sha256": digest(path)}
    assert not path.exists(), path
    return {"kind": "absent"}


def main(args):
    args.run_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    cache = args.archives_from or args.run_dir / "cache/system-brew/bottles"
    if not args.archives_from:
        cache.mkdir(parents=True, mode=0o700)
    records = []
    for filename in ("source-acquisition.json", "closure-acquisition.json"):
        receipt = json.loads((EVIDENCE / filename).read_text())
        assert receipt["state"] == "PASS"
        records.extend(receipt["records"])
    formulae = {}
    for record in records:
        if record["url"].startswith("https://formulae.brew.sh/api/formula/"):
            path = ROOT / record["path"]
            assert digest(path) == record["sha256"]
            formula = json.loads(path.read_text())
            formulae[formula["name"]] = formula
    assert len(formulae) == 8
    report = {"state": "running", "script_sha256": digest(Path(__file__)),
              "run_directory": str(args.run_dir), "bottles": [], "prefix_writes": {},
              "existing_link_parents": {}, "parent_preimages": {},
              "materializations": {}, "archive_extracted": False}
    try:
        for name, version in PACKAGES.items():
            formula = formulae[name]
            assert formula["versions"]["stable"] == version and formula["revision"] == 0
            assert formula["keg_only"] is False
            bottle = formula["bottle"]["stable"]["files"]["arm64_tahoe"]
            archive = cache / f"{name}-{version}.tar.gz"
            if not args.archives_from:
                request = urllib.request.Request(bottle["url"], headers={"Authorization": "Bearer QQ=="})
                with urllib.request.urlopen(request, timeout=90) as response, archive.open("xb") as output:
                    while block := response.read(1024 * 1024):
                        output.write(block)
            assert digest(archive) == bottle["sha256"], name
            row = {"name": name, "version": version, "tag": "arm64_tahoe",
                   "url": bottle["url"], "sha256": bottle["sha256"], "cellar": bottle["cellar"],
                   "archive": str(archive), "bytes": archive.stat().st_size,
                   "members": [], "embedded_receipts": {}}
            report["bottles"].append(row)
            with tarfile.open(archive, "r:gz") as tar:
                for member in tar:
                    path = PurePosixPath(member.name)
                    assert not path.is_absolute() and ".." not in path.parts, member.name
                    assert path.parts[0] == name and (len(path.parts) == 1 or path.parts[1] == version)
                    assert member.isdir() or member.isfile() or member.issym() or member.islnk(), member.name
                    row["members"].append({"path": member.name, "type": member.type.decode(),
                                           "size": member.size, "linkname": member.linkname})
                    if member.isfile() and path.name == "INSTALL_RECEIPT.json":
                        row["embedded_receipts"][member.name] = json.load(tar.extractfile(member))
                    if member.isdir() or len(path.parts) < 3 or path.parts[2] not in LINK_DIRS:
                        continue
                    dest = PREFIX.joinpath(*path.parts[2:])
                    assert str(dest) not in report["prefix_writes"], dest
                    report["prefix_writes"][str(dest)] = {
                        "target": str(PREFIX / "Cellar" / path), "preimage": preimage(dest)}
                    for parent in dest.parents:
                        if parent == PREFIX:
                            break
                        report["parent_preimages"][str(parent)] = preimage(parent)
                        if parent.is_symlink():
                            report["existing_link_parents"][str(parent)] = preimage(parent)
            for relative in (f"opt/{name}", f"var/homebrew/linked/{name}"):
                dest = PREFIX / relative
                report["prefix_writes"][str(dest)] = {
                    "target": str(PREFIX / "Cellar" / name / version), "preimage": preimage(dest)}
            rack = PREFIX / "Cellar" / name
            assert not rack.exists() and not rack.is_symlink(), rack
            row["rack_preimage"] = preimage(rack)
            print(json.dumps({"name": name, "bytes": row["bytes"],
                              "members": len(row["members"]), "sha256_verified": True}), flush=True)
        controls = [PREFIX, *(PREFIX / name for name in BOOTSTRAP_DIRS),
                    PREFIX / "var/homebrew/locks/mise-bootstrap.lock",
                    *(PREFIX / "Cellar" / name / ".mise-staging.lock" for name in PACKAGES)]
        report["control_preimages"] = {str(path): preimage(path) for path in controls}
        for destination in [*(Path(p) for p in report["prefix_writes"]), *controls]:
            for parent in destination.parents:
                if not parent.is_relative_to(PREFIX):
                    break
                report["parent_preimages"][str(parent)] = preimage(parent)
                if parent.is_symlink():
                    report["existing_link_parents"][str(parent)] = preimage(parent)
        for link in report["existing_link_parents"]:
            link_root = Path(link)
            for destination in report["prefix_writes"]:
                dest = Path(destination)
                if not dest.is_relative_to(link_root):
                    continue
                for parent in reversed(dest.parents):
                    if not parent.is_relative_to(link_root):
                        continue
                    if not parent.is_dir():
                        break
                    target = parent.resolve(strict=True)
                    assert target.is_relative_to(PREFIX / "Cellar"), target
                    staging = parent.parent / (".mise-materialize-" + parent.name)
                    assert preimage(staging)["kind"] == "absent", staging
                    report["materializations"][str(parent)] = {
                        "source_directory": str(target), "before": preimage(parent),
                        "staging": str(staging), "staging_preimage": preimage(staging),
                        "preserved_children": {child.name: {
                            "source": str(child), "state": preimage(child)}
                            for child in sorted(target.iterdir())}}
        report["existing_destinations"] = {path: row for path, row in report["prefix_writes"].items()
                                           if row["preimage"]["kind"] != "absent"}
        report["native_additional_writes"] = [
            "/opt/homebrew/Cellar/<four-formulae>/.mise-staging.lock",
            "/opt/homebrew/Cellar/<four-formulae>/.mise-extract-<version>-<random>/",
            "/opt/homebrew/Cellar/<four-formulae>/<version>/",
            "/opt/homebrew/var/homebrew/locks/mise-bootstrap.lock",
            "Missing parent directories for the listed prefix links",
            "Private native mise state/cache/data directories"]
        report["state"] = "PASS"
    except Exception as error:
        report.update({"state": "FAIL", "error": repr(error)})
        raise
    finally:
        (args.run_dir / "bottles.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"state": report["state"], "receipt": str(args.run_dir / "bottles.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--archives-from", type=Path, help="Recheck existing archives without network")
    main(parser.parse_args())

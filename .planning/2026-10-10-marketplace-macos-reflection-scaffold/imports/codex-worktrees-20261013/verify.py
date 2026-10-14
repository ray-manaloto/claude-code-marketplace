"""Re-hash every snapshot file against MANIFEST.json (stdlib only).

Usage: python3 -I verify.py [--mirror] [--root DIR]
  default root: this script's directory (in-repo snapshot; checks entries copied_to a|both)
  --mirror:     also verify the private mirror recorded in MANIFEST.json (all entries)
Exit 0 when every file matches size and sha256 and no unlisted payload file exists; 1 otherwise.
"""
import hashlib, json, os, sys

def check(root, manifest, want):
    bad, ok = [], 0
    listed = set()
    for e in manifest["files"]:
        if e["copied_to"] not in want:
            continue
        rel = e["snapshot_path"]
        listed.add(rel)
        p = os.path.join(root, rel)
        try:
            data = open(p, "rb").read()
        except OSError as ex:
            bad.append((rel, "missing:" + type(ex).__name__)); continue
        if len(data) != e["bytes"] or hashlib.sha256(data).hexdigest() != e["sha256"]:
            bad.append((rel, "hash/size mismatch")); continue
        ok += 1
    for w in manifest["worktrees"]:
        base = os.path.join(root, w)
        for d, _, fs in os.walk(base):
            for f in fs:
                rel = os.path.relpath(os.path.join(d, f), root)
                if rel not in listed:
                    bad.append((rel, "unlisted"))
    return ok, bad

def main():
    args = sys.argv[1:]
    root = os.path.dirname(os.path.abspath(__file__))
    if "--root" in args:
        root = args[args.index("--root") + 1]
    manifest = json.load(open(os.path.join(root, "MANIFEST.json")))
    targets = [(root, {"a", "both"})]
    if "--mirror" in args:
        targets.append((manifest["private_mirror"], {"a", "b", "both"}))
    rc = 0
    for r, want in targets:
        ok, bad = check(r, manifest, want)
        print(f"{r}: ok={ok} bad={len(bad)}")
        for rel, why in bad[:50]:
            print(f"  BAD {why}: {rel}")
        if bad:
            rc = 1
    return rc

if __name__ == "__main__":
    sys.exit(main())

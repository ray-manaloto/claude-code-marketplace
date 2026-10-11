import hashlib,json
from pathlib import Path
out=Path(__file__).parent;root=Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace");e=root/"evidence/pkgconf-install"
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
first=load(out/"execution.json")
assert first["returncode"]==1 and first["script_sha256"]==sha(out/"audit.py")=="69d1bd144a598dc1d5fb6f0d0a5d8da21e5be3210e763e7d97fd014a1e84ccdb"
assert 'line 145, in <module>' in first["stderr"] and first["stderr"].endswith('AssertionError\n')
lines=(out/"audit.py").read_text().splitlines();assert lines[144].startswith('plan_rel=') and '"| Preparing |"' in lines[144]
plan_rel=".planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md";plan=(root/plan_rel).read_text()
row='| 12c2b | Guarded native pkgconf installation | Reviewed write set; fresh capacity; native exit, links, package lookup and preserved defaults | Native passed; artifact review |'
assert plan.count(row)==1
old=plan.replace(row,row.replace('| Native passed; artifact review |','| Prepared; review |'),1)
assert hashlib.sha256(old.encode()).hexdigest()=="23bb60a95eafc7e7d95ea7ffa78e09f500d1633ed16ce72bdbb45b1b1f67dcc6"
assert sha(root/plan_rel)=="74436d62bf9343fba28b7cf0c083cbed80b1a62dc926103ee562f4cfef85e5b3"
progress_rel=plan_rel.replace("task_plan.md","progress.md");progress=(root/progress_rel).read_text().splitlines(keepends=True)
assert ''.join(progress[-4:])=='- Fresh admission preceded the native installation, which exited 0 with all 28\n  commands successful. Keg/link, signature/runtime and lookup checks passed;\n  defaults/protected state were preserved and the lease released. Artifact\n  review now precedes closure; dependency builds remain pending.\n'
assert hashlib.sha256(''.join(progress[:-4]).replace('delta review passed.','delta review is pending.').encode()).hexdigest()=="002f6a98856a1c889c29d909f6cbc1837ddfa0bb00f9b202a7e9ddd34840bcf4"
assert sha(root/progress_rel)=="99cfda6bb85e19486e65265efcbc9e4c3e15299b93e5fb3a46bbb2b5026f6eda"
result={"result":"PASS","findings":[],"scope":"Only corrected factual task-plan/progress delta checks; no operation copies, logs or installed artifacts were read again.","correct_prior_task_plan_state":"Prepared; review","task_plan_previous_sha256":"23bb60a95eafc7e7d95ea7ffa78e09f500d1633ed16ce72bdbb45b1b1f67dcc6","task_plan_current_sha256":sha(root/plan_rel),"progress_current_sha256":sha(root/progress_rel),"progress_previous_sha256":"002f6a98856a1c889c29d909f6cbc1837ddfa0bb00f9b202a7e9ddd34840bcf4","first_audit_returncode":1,"first_audit_assertions_completed_before_documentation_bookkeeping_failure":["frozen identity and all closure bindings","61 actual source/copy byte pairs","56 actual command logs and exact 28 argv/rc0 outcomes","capacity/admission/protection/default/lease/server records","single new keg: 50 entries plus real root mode 0755","30 exact public symlinks and final targets","five canonical Mach-O prefixes and signature extents","installed receipt fields and native-install timestamp","qualified package file hashes/size/links","exact factual docs paragraph delta"],"repeated_artifact_reads":0,"native_commands":0}
(out/"completion.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"result":"PASS","task_plan_delta":"exact","progress_delta":"exact","artifact_audit_replayed":False}))

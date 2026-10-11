import hashlib,json,tarfile
from pathlib import Path
from projection import project_macho
out=Path(__file__).parent;identity=json.loads((out/"identity.json").read_text());root=Path(identity["checkout"])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
watched={}
def bind(p,expected=None):
 p=Path(p);actual=sha(p)
 if expected is not None:assert actual==expected,str(p)
 watched[str(p)]=actual;return actual
helper=root/"dev/toolchains/pkgconf_install.py";cp=root/"evidence/pkgconf-install/contract.json";can=root/"evidence/pkgconf-install/candidate.json"
bind(helper,identity["helper_sha256"]);bind(cp,identity["contract_sha256"]);bind(can,identity["candidate_sha256"])
c=load(cp);candidate=load(can);old=load(root/"evidence/vcpkg-pkgconfig/contract.json")
assert len(c["inputs"])==99 and all(c["inputs"][p]==s for p,s in old["inputs"].items())
for p,s in c["inputs"].items():bind(root/p,s)
for p,s in c["tools"].items():bind(p,s)
for p,s in candidate["files"].items():bind(root/p,s)
assert len(c["tools"])==6 and len(candidate["files"])==4
assert c["base_head"]==candidate["head"]==identity["head"]
git_admin=Path((root/".git").read_text().strip().removeprefix("gitdir: "));common=(git_admin/(git_admin/"commondir").read_text().strip()).resolve()
ref=(git_admin/"HEAD").read_text().strip().removeprefix("ref: ")
assert ref=="refs/heads/"+identity["branch"] and str(common)==identity["common_git_directory"]
assert (common/ref).read_text().strip()==identity["head"]
for row in load(root/"evidence/onboarding/baseline-files.json")["files"]:
 p=root/row["path"];bind(p,row["sha256"]);assert p.stat().st_size==row["bytes"]
prep=load(root/c["preparation"]);manifest=prep["manifest"]
parents=load(root/"evidence/pkgconf-install/parent-children-preimages.json")
assert parents["parents"]==c["parent_children"] and parents["preparation_sha256"]==sha(root/c["preparation"])
assert len(c["parent_children"])==25 and sum(map(len,c["parent_children"].values()))==3632
copy_count=0
for rel in ("source-copy-manifest.json","lock-source-copy-manifest.json","postimage-copy-manifest.json","controls-copy-manifest.json","final-prefix-controls-copy-manifest.json"):
 p=root/"evidence/pkgconf-install"/rel;bind(p)
 for row in load(p)["files"]:
  a,b=Path(row["source"]),root/row["copy"];bind(a,row["sha256"]);bind(b,row["sha256"]);assert a.read_bytes()==b.read_bytes();copy_count+=1
report=load(root/"evidence/pkgconf-install/postimage-source/postimage-contract.json")
tree=load(root/"evidence/vcpkg-pkgconfig/source/mise-tree.json");tree_by={r["path"]:r for r in tree["tree"]}
source_count=0
for row in report["bindings"]["native_sources"]:
 p=Path(row["path"]);bind(p,row["sha256"]);data=p.read_bytes();blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
 assert blob==row["git_blob"]==tree_by[row["source"]]["sha"] and len(data)==row["size"]
 source_count+=1
for row in report["bindings"]["guard_and_helper_sources"]:bind(row["path"],row["sha256"])
archive=Path(prep["bottle"]["path"]);bind(archive,prep["bottle"]["sha256"])
assert archive.stat().st_size==prep["bottle"]["bytes"]
projections=[]
with tarfile.open(archive,"r:gz") as tar:
 observed=[]
 for m in tar.getmembers():
  row={"path":m.name,"type":m.type.decode(),"mode":oct(m.mode),"size":m.size,"linkname":m.linkname}
  if m.isfile():row["sha256"]=hashlib.sha256(tar.extractfile(m).read()).hexdigest()
  observed.append(row)
 assert observed==manifest["members"] and len(observed)==50
 pc=tar.extractfile("pkgconf/3.0.8/lib/pkgconfig/libpkgconf.pc").read().replace(b"@@HOMEBREW_CELLAR@@",b"/opt/homebrew/Cellar")
 assert hashlib.sha256(pc).hexdigest()==c["text_postimages"]["lib/pkgconfig/libpkgconf.pc"]
 for info in report["prospective_keg_checks"]["mach_o"]["per_file"]:
  rel=info["path"];rule=c["macho_files"][rel];data=project_macho(tar.extractfile("pkgconf/3.0.8/"+rel).read())
  assert hashlib.sha256(data).hexdigest()==info["pre_sign_sha256"] and len(data)==info["pre_sign_bytes"]
  assert rule["signature_offset"]==info["prefix_length"]==info["required_signature_dataoff"]
  assert rule["linkedit_fileoff"]==info["required_linkedit_fileoff"]
  expected_masks={z["field"]:z for z in info["zero_ranges"]};canonical=data[:rule["signature_offset"]]
  for key,field in rule["masked_fields"].items():
   full={"linkedit_vmsize":"__LINKEDIT.vmsize","linkedit_filesize":"__LINKEDIT.filesize","signature_size":"LC_CODE_SIGNATURE.datasize"}[key];z=expected_masks[full]
   assert field["offset"]==z["start"] and field["width"]==z["end"]-z["start"]
   canonical[z["start"]:z["end"]]=bytes(z["end"]-z["start"])
  assert hashlib.sha256(canonical).hexdigest()==rule["canonical_prefix_sha256"]==info["canonical_sha256"]
  projections.append(rel)
assert c["changed_files"]==report["prospective_keg_checks"]["receipt"]["changed_files_exact_set"]
required=report["prospective_keg_checks"]["receipt"]["required"]|{"aliases":load(root/c["formula"])["aliases"]}
assert c["receipt_required"]==required
for sub,count in [("controls",7),("final-prefix-controls",8)]:
 p=root/"evidence/pkgconf-install"/sub
 receipt=load(p/"controls.json");execution=load(p/"execution.json")
 bind(p/"controls.json");bind(p/"execution.json");bind(p/"controls.py")
 assert receipt["result"]=="PASS" and len(receipt["cases"])==count and execution["returncode"]==0 and execution["stderr"]==""
 assert all(r["accepted"]==r["expected"] for r in receipt["cases"])
 bind(p/"checked-helper.py.source",receipt["helper_sha256"])
 if sub=="final-prefix-controls":assert receipt["helper_sha256"]==identity["helper_sha256"]
static=root/"evidence/pkgconf-install/pre-review-static.json";bind(static)
assert all(r["returncode"]==0 for r in load(static)["commands"])
assert json.loads(load(static)["commands"][1]["stdout"])["checks"]["baseline"]==19
prior=root/"evidence/vcpkg-pkgconfig/review/review.json";bind(prior,"75e836360337af8828ee2157195ecd283074edbcfc2e824f222a3b593e65878b")
assert load(prior)["findings"]==[] and load(prior)["result"].startswith("PASS")
for p,s in watched.items():assert sha(p)==s,p
(out/"watched-files.json").write_text(json.dumps(watched,indent=2)+"\n")
summary={"result":"PASS","contract_inputs":99,"old_inputs_preserved":len(old["inputs"]),"tool_files_hashed_not_executed":6,"candidate_files":4,"baseline_files":19,"parent_snapshots":25,"retained_child_rows":3632,"live_parent_snapshots_taken":0,"copy_source_pairs":copy_count,"native_source_git_blobs":source_count,"archive_members_in_memory":50,"macho_projections_in_memory":projections,"text_postimages_checked":1,"retained_prefix_controls_not_rerun":[7,8],"retained_static_returncodes":[0,0],"frozen_files":len(watched),"scope":"File and in-memory archive audit only; no candidate functions executed and no native or shared inventory."}
(out/"audit.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary))

import hashlib,json,os,stat,re,math,tomllib
from pathlib import Path
from datetime import datetime,timedelta
out=Path(__file__).parent;root=Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace");e=root/"evidence/pkgconf-install";operation=Path("/Users/rmanaloto/.local/state/marketplace-tool-foundation/pkgconf-install-20261011T201917Z");keg=Path("/opt/homebrew/Cellar/pkgconf/3.0.8")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());watched={}
def bind(p,s=None):
 p=Path(p);actual=sha(p)
 if s is not None:assert actual==s,str(p)
 watched[str(p)]=actual;return actual
identity={"checkout":str(root),"branch":"codex/marketplace-native-onboarding","head":"318c671f5c6a781b29af399d7f6005fe8a917bb5","common_git_directory":"/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git","helper_sha256":"8b8e8a3c1d3e7acd0face144ab47c8ac9ef4421c28a2fb53544b5433e603a685","contract_sha256":"59235e19a0ad51c6e7ca1470fd13540119a42e87ea663e9c66ae8a9cce904d51","closure_candidate_sha256":"eae9cc67ae88924e9dc0ad59c2b344f9063d091b7c2e32cb2cc9826b24633032","installation_sha256":"311d63f9acac9e65f374062017f0604d6bfe445188aaa9aacfa157594fe0f571"}
for p,key in [(root/"dev/toolchains/pkgconf_install.py","helper_sha256"),(e/"contract.json","contract_sha256"),(e/"closure-candidate.json","closure_candidate_sha256"),(e/"operation/installation.json","installation_sha256")]:bind(p,identity[key])
contract=load(e/"contract.json");closure=load(e/"closure-candidate.json");q=load(e/"operation/installation.json");admission=load(e/"admission.json");native=load(e/"native-execution.json")
for p,s in closure["files"].items():bind(root/p,s)
assert len(closure["files"])==4 and closure["head"]==identity["head"]
for filename,key in [("admission.json","admission_sha256"),("native-execution.json","native_execution_sha256")]:bind(e/filename,closure[key])
assert closure["operation_sha256"]==identity["installation_sha256"] and closure["helper_sha256"]==identity["helper_sha256"] and closure["contract_sha256"]==identity["contract_sha256"]
assert q["helper_sha256"]==admission["helper_sha256"]==identity["helper_sha256"] and admission["contract_sha256"]==identity["contract_sha256"]
assert admission["base_head"]==identity["head"] and admission["run_directory"]==str(operation)
assert q["admission_sha256"]==native["admission_sha256"]==sha(e/"admission.json")
bind(e/"candidate.json",admission["candidate_sha256"]);assert admission["candidate_sha256"]=="416ac618da92d2dafe637e3667831d03baab49811f6c33105605cf2bdbf56bc1"
bind(e/"pre-run-review.json",admission["review_sha256"]);assert admission["review_sha256"]=="319b8b9db92dace7ccba1f62c685180fe9fe11ad3f794983d581b71c155d9b4a"
prior=load(e/"pre-run-review.json");assert prior["result"].startswith("PASS") and prior["findings"]==[] and prior["helper_sha256"]==identity["helper_sha256"] and prior["contract_sha256"]==identity["contract_sha256"]
git_admin=Path((root/".git").read_text().strip().removeprefix("gitdir: "));common=(git_admin/(git_admin/"commondir").read_text().strip()).resolve();ref=(git_admin/"HEAD").read_text().strip().removeprefix("ref: ")
assert str(common)==identity["common_git_directory"] and ref=="refs/heads/"+identity["branch"] and (common/ref).read_text().strip()==identity["head"]
assert native["returncode"]==0 and native["stderr"]==""
assert native["argv"]==["/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3","-B",str(root/"dev/toolchains/pkgconf_install.py"),"--run-dir",str(operation),"--install"]
assert q["state"]=="PASS: pkgconf installed and native lookup qualified" and all(q[k] is True for k in ("lease_released","loopback_server_stopped","protected_state_unchanged"))
assert not any(k in q for k in ("error","preservation_error","partial_links"))
copy_manifest=e/"operation-copy-manifest.json";bind(copy_manifest);copies=load(copy_manifest)["files"];assert len(copies)==61
for row in copies:
 source,target=Path(row["source"]),root/row["destination"];bind(source,row["sha256"]);bind(target,row["sha256"]);assert source.read_bytes()==target.read_bytes()
assert len({r["destination"] for r in copies})==61
assert sha(e/"operation/pkgconf_install.py.source")==identity["helper_sha256"]
normal=["/Users/rmanaloto/.local/bin/mise","--no-hooks","-C","/Users/rmanaloto/.local/state/marketplace-tool-foundation/global-apply-20261010T235635Z/empty-cwd","exec","--fresh-env","--no-deps","--","/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3","/Users/rmanaloto/.local/state/marketplace-tool-foundation/global-apply-20261010T235635Z/allowlist_probe.py"]
docker="/Applications/Docker.app/Contents/Resources/bin/docker";base=["/Users/rmanaloto/.local/bin/mise","--no-hooks","-C",str(operation/"cwd")];apply=base+["bootstrap","packages","apply","--manager","brew"]
expected=[("project-head",["/usr/bin/git","-C",str(root),"rev-parse","HEAD"]),("default-before",normal),("capacity-processes",["/bin/ps","-axo","pid=,pcpu=,comm="]),("docker-context",[docker,"context","show"]),("docker-census",[docker,"ps","--format","{{.ID}}\t{{.Image}}"]),("docker-stats",[docker,"stats","--no-stream","--format","{{json .}}"]),("version",base+["version"]),("captured-plan",apply+["--dry-run"]),("native-apply",apply)]
for rel in contract["macho_files"]:
 name=Path(rel).name;binary=str(keg/rel)
 expected.extend([(name+"-arch",["/usr/bin/lipo","-archs",binary]),(name+"-signature",["/usr/bin/codesign","--verify","--strict",binary]),(name+"-libraries",["/usr/bin/otool","-L",binary])])
exe="/opt/homebrew/bin/pkg-config";expected.extend([("pkg-config-version",[exe,"--version"]),("fixture-version",[exe,"--modversion","witness"]),("fixture-libs",[exe,"--libs","witness"]),("default-after",normal)])
assert len(expected)==len(q["commands"])==28
outputs={};log_count=0
for row,(label,argv) in zip(q["commands"],expected):
 assert row["case"]==label and row["argv"]==argv and row["returncode"]==0 and row["pid"]>0 and len(row["logs"])==2
 assert row["elapsed_seconds"] < ({"native-apply":90,"docker-context":15,"docker-census":15,"docker-stats":20}.get(label,35))
 for suffix,log in zip(("stdout","stderr"),row["logs"]):
  path=operation/(label+"."+suffix);assert log["path"]==str(path);bind(path,log["sha256"]);assert path.read_bytes()==(e/"operation"/path.name).read_bytes();outputs[(label,suffix)]=path.read_text();log_count+=1
 assert label=="native-apply" or outputs[(label,"stderr")]=="",label
assert log_count==56
native_events=[json.loads(line) for line in native["stdout"].splitlines()]
assert native_events[:-1]==[{"case":label,"returncode":0} for label,_ in expected] and native_events[-1]=={"state":q["state"],"receipt":str(operation/"installation.json")}
assert outputs[("project-head","stdout")]==identity["head"]+"\n"
assert outputs[("version","stdout")]=="2026.10.8 macos-arm64 (2026-10-11)\n"
assert outputs[("captured-plan","stdout")]=="pour pkgconf/3.0.8 (requested)\n" and outputs[("native-apply","stdout")]==""
assert [line.split() for line in outputs[("native-apply","stderr")].splitlines()]==[["mise","brew:pkgconf","extract"],["mise","brew:pkgconf","extract","pkgconf-3.0.8.tar.gz"],["mise","brew:pkgconf","relocate"],["mise","brew:pkgconf","codesign"],["mise","brew:pkgconf","link"],["mise","brew:pkgconf","✓","3.0.8"],["mise","brew:","installed","pkgconf"]]
for label,value in [("pkg-config-version","3.0.8\n"),("fixture-version","1.2.3\n"),("fixture-libs","-lwitness\n")]:assert outputs[(label,"stdout")]==value
for rel in contract["macho_files"]:
 name=Path(rel).name
 assert outputs[(name+"-arch","stdout")]=="arm64\n" and outputs[(name+"-signature","stdout")]==""
 lines=outputs[(name+"-libraries","stdout")].splitlines();assert lines[0]==str(keg/rel)+":"
 assert [line.strip().split()[0] for line in lines[1:]]==contract["runtime_libraries"][rel]
baseprofile=root/contract["default_profile"];bind(baseprofile,contract["inputs"][contract["default_profile"]])
assert outputs[("default-before","stdout")]==outputs[("default-after","stdout")]==baseprofile.read_text()
assert q["requests"]==[{"path":"/api/formula/pkgconf.json","status":200}]*2
config=tomllib.loads((operation/"config.toml").read_text());assert config["bootstrap"]=={"packages":{"brew:pkgconf":"latest"}}
urls=config["settings"]["url_replacements"];endpoint=urls["https://formulae.brew.sh/api"].removesuffix("/api");assert re.fullmatch(r"http://127[.]0[.]0[.]1:[0-9]+",endpoint)
assert urls=={"https://formulae.brew.sh/api":endpoint+"/api","https://ghcr.io":endpoint+"/blocked","https://github.com":endpoint+"/blocked"}
assert (operation/"pc/witness.pc").read_text()=="Name: witness\nDescription: private fixture\nVersion: 1.2.3\nLibs: -lwitness\n"
capacity_path=e/"capacity/capacity.json";bind(capacity_path,admission["capacity_sha256"]);capacity=load(capacity_path);ce=load(e/"capacity-execution.json");bind(e/"capacity-execution.json");bind(e/"capacity.py.source",ce["script_sha256"])
assert capacity["script_sha256"]==ce["script_sha256"] and ce["returncode"]==0 and ce["stderr"]=="" and capacity["state"]=="PASS"
assert capacity["held_lease"] is False and capacity["native_operation_started"] is False
assert datetime.fromisoformat(capacity["recorded_at"])<datetime.fromisoformat(admission["recorded_at"])<datetime.fromisoformat(native["started_at"])
capacity_outputs={}
assert [r["case"] for r in capacity["commands"]]==["processes","docker-context","docker-census","docker-stats"]
for row in capacity["commands"]:
 assert row["returncode"]==0 and row["elapsed_seconds"]<row["timeout_seconds"]
 for suffix,log in zip(("stdout","stderr"),row["logs"]):
  path=e/"capacity"/(row["case"]+"."+suffix);assert str(path)==log["path"];bind(path,log["sha256"]);capacity_outputs[(row["case"],suffix)]=path.read_text()
 assert capacity_outputs[(row["case"],"stderr")]==""
heavy=re.compile(r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy|include-what-you-use|vcpkg")
for data,lines,stats in [(capacity,capacity_outputs[("processes","stdout")],capacity_outputs[("docker-stats","stdout")]),(q["capacity"],outputs[("capacity-processes","stdout")],outputs[("docker-stats","stdout")])]:
 active=[l for l in lines.splitlines() if heavy.fullmatch(Path(l.split(maxsplit=2)[-1]).name)]
 assert active==[] and math.isclose(sum(float(l.split()[1]) for l in lines.splitlines()),data["total_cpu_percent"])
 assert math.isclose(sum(float(json.loads(l)["CPUPerc"].rstrip("%")) for l in stats.splitlines()),data["container_cpu_percent"])
 assert data["free_bytes"]>=8*1024**3 and data["load"][0]<=2*data["cpus"] and data["total_cpu_percent"]<=75*data["cpus"] and data["container_cpu_percent"]<=50*data["cpus"]
assert capacity["docker_context"]==admission["docker_context"]==capacity_outputs[("docker-context","stdout")].strip()==outputs[("docker-context","stdout")].strip()
assert capacity["containers"]==admission["containers"]==capacity_outputs[("docker-census","stdout")].splitlines()==outputs[("docker-census","stdout")].splitlines()
for c in [capacity["writer_census"]]+[q[k] for k in ("writer_census_before","writer_census_immediate","writer_census_after")]:
 assert c["lock_holders"]==[] and c["lock_holder_check_rc"]==1
 assert {x["known_task"] for x in c["processes"]}=={"mcp:graphify","mcp:cbm","mcp:lab-results"} and len(c["processes"])==3
# Only the new keg is enumerated, with no symlink directory traversal.
assert stat.S_ISDIR(keg.lstat().st_mode) and keg.resolve()==keg and oct(keg.stat().st_mode&0o777)=="0o755"
actual={};pending=[keg]
while pending:
 directory=pending.pop();assert directory.is_relative_to(keg)
 for entry in sorted(os.scandir(directory),key=lambda x:x.name):
  path=Path(entry.path);info=path.lstat();rel=str(path.relative_to(keg));row={"path":rel,"mode":oct(info.st_mode&0o777)}
  assert path.resolve(strict=True).is_relative_to(keg),str(path)
  if stat.S_ISLNK(info.st_mode):row.update(kind="symlink",target=os.readlink(path))
  elif stat.S_ISDIR(info.st_mode):row.update(kind="directory");pending.append(path)
  else:
   assert stat.S_ISREG(info.st_mode);row.update(kind="file",sha256=bind(path),bytes=info.st_size)
  actual[rel]=row;assert len(actual)<=50
assert len(actual)==50 and actual==q["keg_inventory"]
prep_path=root/contract["preparation"];bind(prep_path,contract["inputs"][contract["preparation"]]);manifest=load(prep_path)["manifest"]
expected_members={str(Path(m["path"]).relative_to("pkgconf/3.0.8")):m for m in manifest["members"]};root_member=expected_members.pop(".")
assert root_member["type"]=="5" and root_member["mode"]=="0o755"
assert set(actual)==set(expected_members)|{"INSTALL_RECEIPT.json"}
for rel,m in expected_members.items():
 row=actual[rel];assert row["kind"]=={"0":"file","5":"directory","2":"symlink"}[m["type"]]
 if m["type"]!="2":assert row["mode"]==m["mode"]
 if m["type"]=="2":assert row["target"]==m["linkname"]
 if m["type"]=="0":
  if rel not in contract["changed_files"]:assert row["sha256"]==m["sha256"] and row["bytes"]==m["size"]
  else:assert row["sha256"]!=m["sha256"]
for rel,s in contract["text_postimages"].items():assert actual[rel]["sha256"]==s
assert actual["INSTALL_RECEIPT.json"]["kind"]=="file"
receipt=load(keg/"INSTALL_RECEIPT.json");assert all(receipt[k]==v for k,v in contract["receipt_required"].items())
assert set(receipt)==set(contract["receipt_required"])|{"time","changed_files"} and sorted(receipt["changed_files"])==sorted(contract["changed_files"])
apply_row=next(r for r in q["commands"] if r["case"]=="native-apply");start=datetime.fromisoformat(apply_row["started_at"]).timestamp()
assert type(receipt["time"]) is int and math.floor(start)<=receipt["time"]<=math.ceil(start+apply_row["elapsed_seconds"])
canonical=[]
for rel,rule in contract["macho_files"].items():
 data=(keg/rel).read_bytes();end=rule["signature_offset"];prefix=bytearray(data[:end]);values={}
 for name,field in rule["masked_fields"].items():
  a,w=field["offset"],field["width"];values[name]=int.from_bytes(data[a:a+w],"little");prefix[a:a+w]=bytes(w)
 assert hashlib.sha256(prefix).hexdigest()==rule["canonical_prefix_sha256"]
 assert end+values["signature_size"]==len(data) and values["signature_size"]>0
 assert rule["linkedit_fileoff"]+values["linkedit_filesize"]==len(data) and values["linkedit_vmsize"]>=values["linkedit_filesize"]
 assert values|{"file_bytes":len(data)}==q["macho_postimages"][rel];canonical.append(rel)
links={}
for name,row in manifest["prefix_writes"].items():
 p=Path(name);assert stat.S_ISLNK(p.lstat().st_mode);raw=os.readlink(p);assert raw==os.path.relpath(row["target"],p.parent)
 target=Path(row["target"]);assert target.is_relative_to(keg) and p.resolve(strict=True)==target.resolve(strict=True) and p.resolve().is_relative_to(keg)
 links[name]={"target":raw,"resolved":str(p.resolve())}
assert len(links)==30
qualified_path=e/"qualified-package-inputs.json";bind(qualified_path);qualified=load(qualified_path)
assert qualified["keg_root_mode"]=="0o755" and set(qualified["files"])=={str(keg/"bin/pkgconf"),str(keg/"lib/libpkgconf.8.dylib")}
for name,row in qualified["files"].items():
 p=Path(name);assert row=={"resolved":str(p.resolve()),"sha256":sha(p),"bytes":p.stat().st_size}
assert qualified["pkg_config_link"]=={"path":exe,**links[exe]}
# Bound factual documentation only: source and validators remain unchanged.
pre_candidate=load(e/"candidate.json");docs=root/"docs/vcpkg-toolchains.md";before='Postimage review and fresh capacity precede installation; no dependency build\nis included in this unit.\n';after='Independent preparation review and fresh capacity passed. The native operation\nreturned 0 with 28 successful commands, exact keg/link postimages, five valid\nARM64 signatures/runtime dependencies, native package lookup and preserved\ndefaults. Final artifact review is pending; no dependency build ran.\n'
assert docs.read_text().count(after)==1 and hashlib.sha256(docs.read_text().replace(after,before).encode()).hexdigest()==pre_candidate["files"]["docs/vcpkg-toolchains.md"]
plan_rel=".planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md";plan=(root/plan_rel).read_text();assert hashlib.sha256(plan.replace("| Native passed; artifact review |","| Preparing |",1).encode()).hexdigest()==pre_candidate["files"][plan_rel]
progress_rel=plan_rel.replace("task_plan.md","progress.md");progress=(root/progress_rel).read_text().splitlines(keepends=True)
assert hashlib.sha256(''.join(progress[:-4]).replace('delta review passed.','delta review is pending.').encode()).hexdigest()==pre_candidate["files"][progress_rel]
for p,s in watched.items():assert sha(p)==s,p
summary={"result":"PASS","findings":[],**identity,"native_operation_directory":str(operation),"native_execution_sha256":sha(e/"native-execution.json"),"admission_sha256":sha(e/"admission.json"),"qualified_package_inputs_sha256":sha(qualified_path),"copy_pairs":61,"native_commands_reviewed":28,"native_returncodes":[0]*28,"command_logs_verified":56,"capacity_commands_reviewed":4,"capacity_logs_verified":8,"native_wrapper_returncode":0,"keg_entries":50,"keg_root_mode":"0o755","exact_links":30,"canonical_macho_files":canonical,"receipt_time_within_native_apply_interval":True,"default_before_after_exact":True,"recorded_protected_state_unchanged":True,"recorded_lease_released":True,"recorded_loopback_server_stopped":True,"docs_changed_only_factual_status":True,"old_audit_or_controls_replayed":False,"candidate_functions_executed":0,"native_commands_executed_by_reviewer":0,"full_shared_inventory_executed":False,"watched_files":len(watched)}
(out/"audit.json").write_text(json.dumps(summary,indent=2)+"\n");(out/"artifact-inventory.json").write_text(json.dumps({"keg_root":{"path":str(keg),"mode":"0o755"},"keg_entries":actual,"links":links},indent=2)+"\n");(out/"watched-files.json").write_text(json.dumps(watched,indent=2)+"\n")
print(json.dumps({"result":"PASS","copy_pairs":61,"commands":28,"logs":56,"keg_entries":50,"links":30,"watched_files":len(watched)}))

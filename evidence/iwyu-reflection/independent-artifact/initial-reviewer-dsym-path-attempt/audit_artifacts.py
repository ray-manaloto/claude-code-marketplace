"""Read-only audit of completed 09c1 artifacts; no candidate/native execution."""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import shlex
import struct

D=Path(__file__).resolve().parent
ROOT=Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
E=ROOT/"evidence/iwyu-reflection"
OP=Path("/Users/rmanaloto/.local/state/marketplace-tool-foundation/iwyu-reflection-20261011T155205Z")
fixture=OP/"fixtures/reflection"
load=lambda p:json.loads(p.read_text())
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
binding=lambda p:{"path":str(p),"sha256":digest(p),"bytes":p.stat().st_size}
frozen=load(D/"frozen-inputs.json")
def unchanged():
    for rel,row in frozen["files"].items():
        assert digest(ROOT/rel)==row["sha256"] and (ROOT/rel).stat().st_size==row["bytes"],rel
unchanged()
helper=ROOT/"dev/toolchains/iwyu_reflection.py"
assert digest(helper)=="b840f31d5e70ebcb523e25994e7551be8c593a385d00fe6746301b868f57fd4a"
assert digest(E/"contract.json")=="77208a22af95e9ade5ab5301e9dffa83d200366e998b4db5e8ab0ecbf67b6bcf"
assert digest(E/"source-recipe.json")=="057c1350de72edecf1b922842167b347d10fe464cab4e9faf51f6efda84c5161"
assert digest(E/"pre-run-review.json")=="71b1fa549e3761c84a345a4c1e59b2c7236409ada49c6c12864ac8d577c4ae26"
assert digest(E/"operation/qualification.json")=="22aa05004d35469fceb657eba0b348b6174d283360658c0f0f2255f56b61f226"
q=load(E/"operation/qualification.json")
admission=load(E/"admission.json")
contract=load(E/"contract.json")
recipe=load(E/"source-recipe.json")
inv=load(E/"invocation/invocation.json")
pre_run=load(E/"pre-run-review.json")
assert pre_run["result"].startswith("PASS") and pre_run["findings"]==[]
assert q["state"]=="PASS: bounded type-reflection advice, restricted fixer, rebuild/run and clean analysis"
assert q["helper_sha256"]==admission["helper_sha256"]==inv["helper_sha256"]==digest(helper)
assert q["admission_sha256"]==inv["admission_sha256"]==digest(E/"admission.json")
assert admission["review_sha256"]==digest(E/"pre-run-review.json")
assert admission["contract_sha256"]==digest(E/"contract.json")
assert admission["base_head"]==contract["base_head"]=="1ddd107bffe56226ae2a5c115fcb4e2ae6b7b6b9"
assert admission["run_directory"]==str(OP)
assert admission["capacity_sha256"]==digest(E/"capacity-preflight.json")
assert q["lease_released"] is True and q["protected_state_unchanged"] is True
assert inv["returncode"]==0 and inv["elapsed_seconds"]<60
assert inv["argv"][1:]==["-B",str(helper),"--run-dir",str(OP)] and inv["cwd"]==str(ROOT)
assert inv["argv"][0]=="/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3"
for rel,expected in contract["inputs"].items():
    assert digest(ROOT/rel)==expected,rel

pairs=load(E/"operation-copy-manifest.json")["files"]
assert len(pairs)==71
assert len({row["path"] for row in pairs})==len({row["source"] for row in pairs})==71
for row in pairs:
    source,copied=Path(row["source"]),ROOT/row["path"]
    assert copied.is_relative_to(E)
    assert source.read_bytes()==copied.read_bytes()
    assert digest(source)==row["sha256"] and source.stat().st_size==row["bytes"]

commands=q["commands"]
assert len(commands)==32 and len({row["case"] for row in commands})==32
by={row["case"]:row for row in commands}
native_labels=["baseline-build","baseline-run","advice","fixer","fixed-build","fixed-run","clean-analysis","missing-reflection"]
expected_order=["project-head","default-before","named-profile","capacity-processes","docker-context","docker-census","docker-stats"]
expected_order += [f"before-{tool}-{part}" for tool in ("iwyu","llvm") for part in ("head","tree","status","diff")]
expected_order += native_labels + ["default-after"]
expected_order += [f"after-{tool}-{part}" for tool in ("iwyu","llvm") for part in ("head","tree","status","diff")]
assert list(by)==expected_order
for row in commands:
    expected={"advice":23,"missing-reflection":1}.get(row["case"],0)
    assert row["returncode"]==row["expected_returncode"]==expected,row["case"]
    assert not row.get("interrupted",False)
    assert row["timeout_seconds"]==(15 if row["case"] in ("docker-context","docker-census") else 20 if row["case"]=="docker-stats" else 60)
    assert 0<=row["elapsed_seconds"]<row["timeout_seconds"]
    assert row["cwd"]==str(fixture if row["case"]=="fixer" else OP)
    for log in row["logs"]:
        assert Path(log["path"]).parent==OP and digest(log["path"])==log["sha256"]
    assert len(row["logs"])==2
for a,b in zip(commands,commands[1:]):
    assert datetime.fromisoformat(a["started_at"]).timestamp()+a["elapsed_seconds"] <= datetime.fromisoformat(b["started_at"]).timestamp()+0.01
for log in inv["logs"]:
    assert digest(log["path"])==log["sha256"]
stdout=lambda label:(OP/(label+".stdout")).read_text()
stderr=lambda label:(OP/(label+".stderr")).read_text()
wrapper=[json.loads(line) for line in Path(inv["logs"][0]["path"]).read_text().splitlines()]
assert wrapper[:-1]==[{"case":row["case"],"returncode":row["returncode"]} for row in commands]
assert wrapper[-1]=={"state":q["state"],"receipt":str(OP/"qualification.json")}
assert Path(inv["logs"][1]["path"]).read_bytes()==b""
assert stdout("project-head").strip()==contract["base_head"]
assert stdout("default-before")==stdout("default-after")==(ROOT/"evidence/mise-runtime/operation/default-after.stdout").read_text()
assert stdout("named-profile")==(ROOT/"evidence/mise-runtime/operation/cpp-build-profile.stdout").read_text()
for label in ("project-head","default-before","default-after","named-profile"):
    assert stderr(label)==""
for tool in ("iwyu","llvm"):
    for part in ("head","tree","status","diff"):
        before,after=f"before-{tool}-{part}",f"after-{tool}-{part}"
        assert stdout(before)==stdout(after) and stderr(before)==stderr(after)==""
        if tool=="iwyu":
            expected="" if part=="diff" else (ROOT/"evidence/iwyu-source/operation"/(part+".stdout")).read_text()
        else:
            expected=(ROOT/"evidence/p2996-registration/operation"/("source-after-"+part+".stdout")).read_text()
        assert stdout(before)==expected
capacity=q["capacity"]
assert not capacity["active"] and capacity["cpus"]==12
assert capacity["free_bytes"]>=contract["disk_reserve_bytes"]
assert capacity["load"][0]<=2*capacity["cpus"] and capacity["total_cpu_percent"]<=75*capacity["cpus"]
total_cpu=sum(float(line.split()[1]) for line in stdout("capacity-processes").splitlines())
assert math.isclose(total_cpu,capacity["total_cpu_percent"],abs_tol=1e-8)
assert stdout("docker-context").strip()==admission["docker_context"]
assert stdout("docker-census").splitlines()==admission["containers"]
assert math.isclose(sum(float(json.loads(line)["CPUPerc"].rstrip("%")) for line in stdout("docker-stats").splitlines()),capacity["container_cpu_percent"],abs_tol=1e-8)
preflight=load(E/"capacity-preflight.json")
assert len(preflight["commands"])==5 and all(row["returncode"]==0 for row in preflight["commands"])

base=["/Users/rmanaloto/.local/bin/mise","--no-hooks","-C",str(OP/"cwd"),"-E","cpp-build","exec","--fresh-env","--no-deps","--"]
expand=lambda argv:[s.replace("<private-09c-root>",str(OP)) for s in argv]
data=recipe["reflection_fixture"]
main=fixture/"main.cc"
for label in ("baseline","fixed"):
    build=expand(data["rebuild_and_reanalyze"]["build_argv"])
    build[-1]=str(fixture/label)
    assert by[label+"-build"]["argv"]==base+build
    assert by[label+"-run"]["argv"]==base+[str(fixture/label)]
    assert stdout(label+"-build")==stdout(label+"-run")==stderr(label+"-run")==""
analyze=expand(data["analyze_argv"])
assert by["advice"]["argv"]==by["clean-analysis"]["argv"]==base+analyze
assert by["missing-reflection"]["argv"]==base+[a for a in analyze if a!="-freflection"]
fixer_base=list(base);fixer_base[fixer_base.index("-C")+1]=str(fixture)
assert by["fixer"]["argv"]==fixer_base+expand(data["fixer"]["argv"])
assert by["fixer"]["stdin"]=={"path":str(OP/"advice.stderr"),"sha256":digest(OP/"advice.stderr")}
assert all(row["stdin"] is None for row in commands if row["case"]!="fixer")
assert by["fixer"]["argv"][by["fixer"]["argv"].index("--basedir")+1]==str(fixture)==by["fixer"]["cwd"]

advice=stderr("advice")
warning_lines=[line for line in advice.splitlines() if ": warning:" in line]
assert warning_lines==[f'{main}:{pos}: warning: FixtureValue is defined in "value.h", which isn\'t directly #included.' for pos in ("4:34","7:3","8:16")]
assert ": error:" not in advice and ": fatal error:" not in advice
add,rest=advice.split(str(main)+" should add these lines:\n")
add,rest=rest.split(str(main)+" should remove these lines:\n")
remove,full=rest.split("The full include-list for "+str(main)+":\n")
clean=lambda value:[line.split("//",1)[0].strip() for line in value.splitlines() if line.strip()]
assert clean(add)==['#include "value.h"']
assert clean(remove)==['- #include "indirect.h"']
assert clean(full)==['#include <meta>','#include "value.h"',"---"]
assert q["recommendations"]==[['#include "value.h"'],['- #include "indirect.h"'],['#include <meta>','#include "value.h"']]
assert stdout("advice")==stdout("clean-analysis")==stdout("missing-reflection")==""
assert stdout("fixer")==f">>> Fixing #includes in '{main}'\nIWYU edited 1 files on your behalf.\n\n"
assert stderr("fixer")==""
assert stderr("clean-analysis")==f"\n({main} has correct #includes/fwd-decls)\n"
errors=[line for line in stderr("missing-reflection").splitlines() if ": error:" in line]
assert len(errors)==5 and all(line.startswith(str(main)+":4:") for line in errors)
assert "no member named 'meta' in namespace 'std'" in errors[0]
assert "expected expression" in errors[-1]

initial={row["path"]:row for row in q["fixture_before"]}
after={row["path"]:row for row in q["fixture_after_fix"]}
final={row["path"]:row for row in q["final_fixture"]}
assert len(initial)==3 and len(after)==13 and len(final)==23
for row in data["files"]:
    assert initial[row["path"]]=={"path":row["path"],"mode":"0o600","kind":"file","sha256":row["sha256"],"bytes":len(row["content"].encode())}
    if row["path"]!="main.cc":
        assert after[row["path"]]==final[row["path"]]==initial[row["path"]]
        assert (fixture/row["path"]).read_text()==row["content"]
assert main.read_text()==data["fixer"]["expected_after"]
assert digest(main)==data["fixer"]["expected_after_sha256"]==after["main.cc"]["sha256"]==final["main.cc"]["sha256"]
for name,row in after.items():
    assert final[name]==row
assert set(final)-set(after)=={"fixed",*[name.replace("baseline","fixed",1) for name in after if name.startswith("baseline.dSYM")]}
assert "baseline" not in initial and "fixed" not in after
prefix=Path(recipe["bindings"]["LLVM_PREFIX"])
macho={}
for label in ("baseline","fixed"):
    text=stderr(label+"-build")
    assert text.startswith("clang version 21.0.0git (https://github.com/bloomberg/clang-p2996.git f17c8d6c7bfef5e02ccadcf33517fd2a53b51b6e)\n")
    assert ": error:" not in text and ": warning:" not in text
    lines=[shlex.split(line) for line in text.splitlines() if line.startswith(' "')]
    assert len(lines)==3
    cc,link,debug=lines
    assert cc[0]==str(prefix/"bin/clang-21") and cc[1]=="-cc1"
    for flag,value in (("-triple","arm64-apple-macosx27.0.0"),("-isysroot","/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk"),("-isystem",str(prefix/"include/c++/v1")),("-resource-dir",str(prefix/"lib/clang/21"))):
        assert cc.count(flag)==1 and cc[cc.index(flag)+1]==value
    assert "-freflection" in cc and "-std=c++26" in cc and "-nostdinc++" in cc and "-stdlib=libc++" in cc and "-fblocks" not in cc
    assert cc[-1]==str(main)
    assert link[0]=="/usr/bin/ld" and link[link.index("-o")+1]==str(fixture/label)
    assert link[link.index("-arch")+1]=="arm64"
    assert link[link.index("-rpath")+1]==str(prefix/"lib")
    assert all(str(prefix/"lib"/name) in link for name in ("libc++.dylib","libc++abi.dylib","libunwind.dylib"))
    assert "-lc++" not in link and not any("/opt/homebrew/" in arg for arg in cc+link)
    assert debug==[str(prefix/"bin/dsymutil"),"-o",str(fixture/(label+".dSYM")),str(fixture/label)]
    content=(fixture/label).read_bytes()
    header=struct.unpack_from("<8I",content)
    assert header[0]==0xfeedfacf and header[1]==0x0100000c and header[3]==2
    offset=32;deps=[];rpaths=[];platform=[]
    for _ in range(header[4]):
        cmd,size=struct.unpack_from("<II",content,offset)
        if cmd in (12,0x8000001c):
            at=struct.unpack_from("<I",content,offset+8)[0]
            value=content[offset+at:offset+size].split(b"\0",1)[0].decode()
            (deps if cmd==12 else rpaths).append(value)
        elif cmd==0x32:
            platform=list(struct.unpack_from("<IIII",content,offset+8))
        offset+=size
    assert deps==["@rpath/libc++.1.dylib","@rpath/libc++abi.1.dylib","@rpath/libunwind.1.dylib","/usr/lib/libSystem.B.dylib"]
    assert rpaths==[str(prefix/"lib")] and platform[:3]==[1,27<<16,27<<16]
    assert digest(fixture/label)==final[label]["sha256"]
    macho[label]={"sha256":digest(fixture/label),"bytes":len(content),"architecture":"arm64","dylibs":deps,"rpaths":rpaths,"platform":platform,
                  "mtime_ns":(fixture/label).stat().st_mtime_ns,"inode":(fixture/label).stat().st_ino}
assert macho["baseline"]["sha256"]!=macho["fixed"]["sha256"] and macho["baseline"]["inode"]!=macho["fixed"]["inode"]

static=load(E/"post-operation-static.json")
assert [row["returncode"] for row in static]==[0,0]
assert json.loads(static[1]["stdout"])["checks"]["baseline"]==19
baseline=load(ROOT/"evidence/onboarding/baseline-files.json")["files"]
for row in baseline:
    assert digest(ROOT/row["path"])==row["sha256"] and (ROOT/row["path"]).stat().st_size==row["bytes"]
unchanged()
result={"result":"PASS","copy_pairs":71,"native_commands":32,"native_returncodes":{row["case"]:row["returncode"] for row in commands},
 "command_log_hashes":64,"wrapper_returncode":inv["returncode"],"wrapper_elapsed_seconds":inv["elapsed_seconds"],
 "preflight_returncodes":[row["returncode"] for row in preflight["commands"]],
 "stdin_and_effective_fixer_cwd":"PASS: exact saved stderr hash and equal mise -C, Popen cwd, basedir fixture",
 "exact_fix":"Only main.cc indirect.h include replaced by value.h; reflection expression, meta and body retained.",
 "negative_control":"Only -freflection removed; five frontend errors on line 4 including absent std::meta and reflection syntax.",
 "source_preservation":"Before/after IWYU and LLVM head/tree/status/diff logs byte-equal and match committed acquisition/registration receipts.",
 "defaults_preserved":True,"named_profile_matches_committed_runtime":True,
 "fixture_inventory_counts":{"before":3,"after_fix":13,"final":23},
 "binaries":macho,"recorded_lease_released":True,"current_lease_probe":False,"recorded_protected_state_unchanged":True,
 "original_Claude_files":len(baseline),"retained_static_returncodes":[0,0],"native_reproduction":False,
 "references":[binding(E/name) for name in ("contract.json","source-recipe.json","pre-run-review.json","admission.json","capacity-preflight.json","operation-copy-manifest.json","operation/qualification.json","invocation/invocation.json","post-operation-static.json")]}
(D/"artifact-audit.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"result":"PASS","copy_pairs":71,"native_commands":32,"command_logs":64,"fresh_binaries":2,
                  "original_Claude_files":len(baseline),"native_reproduction":False}))


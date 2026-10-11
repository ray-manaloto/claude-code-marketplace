"""Narrow 09C1-01 disposition: exact delta and one pure argv/cwd case."""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
D=Path(__file__).resolve().parent
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
binding=lambda p:{"path":str(p),"sha256":digest(p),"bytes":p.stat().st_size}
helper=ROOT/"dev/toolchains/iwyu_reflection.py"
initial=ROOT/"evidence/iwyu-reflection/initial-helper.py.source"
contract=ROOT/"evidence/iwyu-reflection/contract.json"
recipe=ROOT/"evidence/iwyu-reflection/source-recipe.json"
prior=ROOT/"evidence/iwyu-reflection/initial-pre-run-review.json"
manifest=ROOT/"evidence/iwyu-reflection/initial-review-supporting-manifest.json"
static=ROOT/"evidence/iwyu-reflection/revision-static.json"
expected={
 helper:"ff2b0e9d5bec3c2845ca798fe01c086f1f49a5b4dcd5544916b61934ece03aee",
 initial:"4a01a1b5d90beebe7cd690088c68167366806ed000c9c2fcf429e4641d0d72e7",
 contract:"2e528d666e90db8f80cee6d046d06ea6304564a05a913098237d144c62dd7de4",
 recipe:"50eaea5396fe0ea7b5b8a5cb30bc0de2a514b612446d49c2b3710bae41f2473a",
 prior:"c2b2312ae74c5b52dd34e38802a55475a4562678b6c951213ba15375384e487f",
 manifest:"0a4a88c9005c598a4a4a7c44e98127d2b8c19d9c8177124ca7a1b3e3dc4b0300"}
for path,sha in expected.items():assert digest(path)==sha,str(path)
old=initial.read_text();new=helper.read_text()
before='            fixed = run("fixer", base + expand(data["fixer"]["argv"]), descriptor=fd,\n'
after=('            fixer_base = list(base)\n'
       '            fixer_base[fixer_base.index("-C") + 1] = fixture\n'
       '            fixed = run("fixer", fixer_base + expand(data["fixer"]["argv"]), descriptor=fd,\n')
assert old.count(before)==1 and old.replace(before,after)==new
prior_data=load(prior)
assert [r["id"] for r in prior_data["findings"]]==["09C1-01"]
assert prior_data["executed_checks"]["pure_parser_cases"]==15
assert prior_data["executed_checks"]["mocked_Popen_wrapper_cases"]==12
assert prior_data["executed_checks"]["review_process"]["returncode"]==0
retained=load(manifest)
for rel in ("controls.json","controls-invocation.json"):
 row=next(r for r in retained["files"] if r["path"]==rel)
 copied=ROOT/"evidence/iwyu-reflection/independent-pre-run"/rel
 assert digest(copied)==row["sha256"]
static_data=load(static)
assert static_data["returncode"]==0
assert json.loads(static_data["stdout"])["checks"]["baseline"]==19
data=load(recipe)["reflection_fixture"]
directory=D/"uncreated-private-operation"
fixture=directory/"fixtures/reflection"
parsed=ast.parse(new)
main=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=="main")
assignments=[n for n in ast.walk(main) if isinstance(n,ast.Assign)]
base_node=next(n for n in assignments if isinstance(n.targets[0],ast.Name) and n.targets[0].id=="base")
fixer_nodes=[n for n in assignments if (
 isinstance(n.targets[0],ast.Name) and n.targets[0].id in ("fixer_base","fixed")
 or isinstance(n.targets[0],ast.Subscript) and isinstance(n.targets[0].value,ast.Name) and n.targets[0].value.id=="fixer_base")]
assert len(fixer_nodes)==3
calls=[]
def spy(label,argv,**kwargs):
 calls.append({"label":label,"argv":argv,"kwargs":kwargs})
 return "MOCK: no process executed"
scope={"current":{"path":"/Users/rmanaloto/.local/bin/mise"},"directory":directory,
       "fixture":fixture,"data":data,"fd":91,"run":spy,
       "expand":lambda argv:[s.replace("<private-09c-root>",str(directory)) for s in argv]}
exec(compile(ast.Module(body=[base_node],type_ignores=[]),str(helper),"exec"),scope)
base_before=list(scope["base"])
exec(compile(ast.Module(body=fixer_nodes,type_ignores=[]),str(helper),"exec"),scope)
assert len(calls)==1
call=calls[0]
expected_base=list(base_before);expected_base[expected_base.index("-C")+1]=fixture
expected_argv=expected_base+scope["expand"](data["fixer"]["argv"])
assert call["label"]=="fixer" and call["argv"]==expected_argv
assert scope["base"]==base_before and scope["fixer_base"] is not scope["base"]
assert call["kwargs"]=={"descriptor":91,"stdin":directory/"advice.stderr","cwd":fixture}
assert call["argv"][call["argv"].index("-C")+1]==fixture
assert call["argv"][call["argv"].index("--basedir")+1]==str(fixture)
assert call["argv"][-1]==str(fixture/"main.cc")
assert Path(data["fixer"]["cwd"].replace("<private-09c-root>",str(directory)))==fixture
assert not directory.exists()
for path,sha in expected.items():assert digest(path)==sha,str(path)
result={"result":"PASS","finding":"09C1-01","disposition":"FIXED",
 "exact_delta_only":True,"unchanged_parser_and_runner":True,"pure_cases_executed":1,
 "prior_controls_reused_without_rerun":{"parser":15,"mocked_wrapper":12},
 "argv":[str(a) for a in call["argv"]],"cwd":str(fixture),
 "stdin":str(directory/"advice.stderr"),"base_preserved":True,
 "references":[binding(p) for p in expected]+[binding(static)],
 "retained_baseline_returncode":static_data["returncode"],"retained_original_file_count":19,
 "actual_child_processes":0,"helper_main_calls":0,"protected_calls":0}
(D/"argv-cwd-check.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"result":"PASS","finding":"09C1-01","disposition":"FIXED","pure_cases":1,
                  "prior_controls_reused":27,"actual_child_processes":0}))


from pathlib import Path
from datetime import datetime,timezone
from types import SimpleNamespace
import ast,builtins,hashlib,json,os,subprocess
D=Path(__file__).parent
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
H=R/'dev/toolchains/mise_renovate.py'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashtext=lambda s:hashlib.sha256(s.encode()).hexdigest()
frozen=load(D/'frozen-inputs.json')['files']
def unchanged():
 for p,row in frozen.items():assert sha(R/p)==row['sha256']
unchanged()
def prohibited(*args,**kwargs):raise AssertionError('native child forbidden')
for name in ['Popen','run','call','check_call','check_output']:setattr(subprocess,name,prohibited)
os.system=prohibited
tree=ast.parse(H.read_text());functions={x.name:x for x in tree.body if isinstance(x,ast.FunctionDef)}
ns={'os':os,'hashlib':hashlib};exec(compile(ast.Module(body=[functions['path_transition'],functions['compare_profile']],type_ignores=[]),str(H),'exec'),ns)
transition,compare=ns['path_transition'],ns['compare_profile']
data=load(D/'frozen-contract.json');changes=data['path_transition'];pairs=list(changes.items());old0,new0=pairs[0];old1,new1=pairs[1]
prior=':'+old1+'::/tail:'+old0+':';current=':'+new1+'::/tail:'+new0+':'
expected={'path_sha256':hashtext(prior),'other':'unchanged'};observed=expected|{'path_sha256':hashtext(current)}
proof=transition(current,changes);compare(observed,expected,proof);cases=[]
def passed(name):cases.append({'case':name,'pass':True})
assert transition(current,dict(reversed(pairs)))==proof;passed('JSON-map-insertion-order-does-not-change-reconstruction')
lookalike=':'+new0+'-extra:'+new1+'/child'
lookproof=transition(current+lookalike,changes)
assert lookproof['previous_path_sha256']==hashtext(prior+lookalike)
compare(observed|{'path_sha256':hashtext(current+lookalike)},expected|{'path_sha256':hashtext(prior+lookalike)},lookproof)
passed('exact-components-do-not-rewrite-prefix-lookalike-neighbors')
try:compare(observed,expected,transition(current,{old0:new1,old1:new0}))
except AssertionError:passed('swapped-old-identities-rejected-by-full-historical-hash')
else:raise AssertionError('wrong reconstruction accepted')
try:transition(current+':/third/new',changes|{'/third/old':'/third/new'})
except AssertionError:passed('three-component-map-rejected')
else:raise AssertionError('three-component rewrite accepted')
# Evaluate the exact child-program assignment and invocation expression with a
# mock run and in-memory imports. No main(), module import, or child process.
main=functions['main']
assignment=next(n for n in ast.walk(main) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path_probe' for t in n.targets))
program=eval(compile(ast.Expression(assignment.value),str(H),'eval'),{'Path':Path,'__file__':str(H)})
proof_assignment=next(n for n in ast.walk(main) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='proof' for t in n.targets))
base=['/mock/mise','--no-hooks','exec','--fresh-env','--no-deps','--'];calls=[]
def run(label,argv):
 assert label=='default-path-transition' and argv[:-5]==base
 assert argv[-5:-2]==['/mock/python','-B','-c'] and argv[-2]==program
 assert json.loads(argv[-1])==changes and len(json.loads(argv[-1]))==2
 fake_sys=SimpleNamespace(argv=['-c',argv[-1]],path=[])
 modules={'json':json,'os':SimpleNamespace(environ={'PATH':current}),'sys':fake_sys,'mise_renovate':SimpleNamespace(path_transition=transition)}
 def safe_import(name,globals=None,locals=None,fromlist=(),level=0):
  assert level==0 and name in modules
  return modules[name]
 output=[]
 child={'__builtins__':{'__import__':safe_import,'print':lambda value:output.append(value)}}
 exec(compile(program,'reviewed-child-program','exec'),child)
 assert len(output)==1 and fake_sys.path==[str(H.parent)]
 calls.append({'label':label,'JSON_map_keys':list(json.loads(argv[-1])),'native':False})
 return output[0]+'\n'
actual=eval(compile(ast.Expression(proof_assignment.value),str(H),'eval'),{'json':json,'run':run,'lane':'default','base':base,'sys':SimpleNamespace(executable='/mock/python'),'path_probe':program,'data':data})
assert actual==proof and len(calls)==1;passed('actual-invocation-serializes-one-map-and-child-decodes-both-components')
unchanged();assert len(cases)==5
result={'result':'PASS','at':datetime.now(timezone.utc).isoformat(),'helper_sha256':sha(H),'contract_sha256':sha(D/'frozen-contract.json'),'candidate_sha256':sha(D/'frozen-candidate.json'),'cases':cases,'native_commands':0,'main_calls':0,'protected_calls':0,'candidate_module_imports':0,'mock_child_program_calls':1,'unchanged_watched_files':len(frozen)}
(D/'control-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':'PASS','cases':len(cases),'native_commands':0,'main_calls':0,'protected_calls':0}))

from pathlib import Path
import ast,hashlib,json,os,subprocess,sys
r=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');sys.path.insert(0,str(r/'dev/toolchains'));import mise_renovate as m
out=Path(__file__).parent;cases=[];old='/fixture/44.149.3/';new='/fixture/44.150.1/';changes={old+s:new+s for s in ('bin','node_modules/.bin')};sha=lambda v:hashlib.sha256(v.encode()).hexdigest();prior=':/a:'+old+'node_modules/.bin::'+old+'bin:/z:';current=prior.replace(old,new);expected={'path_sha256':sha(prior),'selected':{'CC':'qualified'}};observed=expected|{'path_sha256':sha(current)}
def pass_case(name):cases.append({'case':name,'pass':True})
def reject(name,fn):
 try:fn()
 except AssertionError:pass_case(name)
 else:raise AssertionError(name)
proof=m.path_transition(current,changes);m.compare_profile(observed,expected,proof);assert proof['replacements']==2;pass_case('exact-two-components-preserve-order-and-empty-components')
reject('missing-bin',lambda:m.path_transition(current.replace(new+'bin','/missing'),changes))
reject('missing-node-modules-bin',lambda:m.path_transition(current.replace(new+'node_modules/.bin','/missing'),changes))
reject('duplicate-component',lambda:m.path_transition(current+new+'bin',changes))
reject('one-component-map',lambda:m.path_transition(current,{old+'bin':new+'bin'}))
reject('duplicate-new-map',lambda:m.path_transition(current,{old+'bin':new+'bin',old+'other':new+'bin'}))
reject('overlapping-old-new-map',lambda:m.path_transition(current,{new+'bin':new+'bin',old+'other':new+'node_modules/.bin'}))
for name,value in [('third-version-component',current+new+'other'),('prefix-lookalike',current.replace(new+'bin',new+'bin-extra')),('unrelated-path',current+':/other'),('reordered',':'.join(reversed(current.split(':'))))]:
 reject(name,lambda value=value:m.compare_profile(observed|{'path_sha256':sha(value)},expected,m.path_transition(value,changes)))
reject('other-profile-value',lambda:m.compare_profile(observed|{'selected':{'CC':'wrong'}},expected,proof))
reject('wrong-proof-current-hash',lambda:m.compare_profile(observed,expected,proof|{'path_sha256':'0'*64}))
reject('wrong-proof-prior-hash',lambda:m.compare_profile(observed,expected,proof|{'previous_path_sha256':'0'*64}))
reject('wrong-proof-count',lambda:m.compare_profile(observed,expected,proof|{'replacements':1}))
tree=ast.parse(Path(m.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');node=next(n for n in ast.walk(main) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path_probe' for t in n.targets));program=eval(compile(ast.Expression(node.value),m.__file__,'eval'),{'Path':Path,'__file__':m.__file__});p=subprocess.run([sys.executable,'-B','-c',program,json.dumps(changes)],env=os.environ|{'PATH':current},text=True,capture_output=True,timeout=10);(out/'child.stdout').write_text(p.stdout);(out/'child.stderr').write_text(p.stderr);assert p.returncode==0 and not p.stderr and json.loads(p.stdout)==proof;pass_case('actual-child-deserializes-and-applies-exact-two-component-map')
result={'cases':cases,'helper_sha256':hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),'contract_sha256':m.CONTRACT_SHA,'native_profiles_executed':0,'child_python_exit_code':p.returncode};(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':len(cases),'total':len(cases)}))

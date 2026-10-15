from pathlib import Path
import ast,copy,hashlib,json,os,subprocess,sys
root=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');sys.path.insert(0,str(root/'dev/toolchains'));import mise_renovate as m
out=Path(__file__).parent;cases=[];old='/fixture/renovate/44.149.3/bin';new='/fixture/renovate/44.150.1/bin'
sha=lambda value:hashlib.sha256(value.encode()).hexdigest()
prior='/a:'+old+':/z';current='/a:'+new+':/z'
expected={'path_sha256':sha(prior),'selected':{'CC':'qualified-clang'},'tools':{'cmake':'qualified-cmake'}}
observed=expected|{'path_sha256':sha(current)}
def passed(name):cases.append({'case':name,'pass':True})
def rejects(name,fn):
 try:fn()
 except AssertionError:passed(name)
 else:raise AssertionError(name)
proof=m.path_transition(current,old,new);m.compare_profile(observed,expected,proof);passed('exact-single-component-reconstructs-prior-full-hash')
rejects('missing-component',lambda:m.path_transition('/a:/z',old,new))
rejects('duplicate-component',lambda:m.path_transition(current+':'+new,old,new))
rejects('substring-is-not-component',lambda:m.path_transition('/a:'+new+'-extra:/z',old,new))
rejects('identical-old-and-new',lambda:m.path_transition(current,new,new))
for name,value in [('unrelated-addition',current+':/unreviewed'),('unrelated-reorder','/z:'+new+':/a'),('unrelated-component','/changed:'+new+':/z')]:
 rejects(name,lambda value=value:m.compare_profile(observed|{'path_sha256':sha(value)},expected,m.path_transition(value,old,new)))
rejects('changed-selected-tool',lambda:m.compare_profile(observed|{'selected':{'CC':'wrong-clang'}},expected,proof))
rejects('changed-tool-resolution',lambda:m.compare_profile(observed|{'tools':{'cmake':'wrong-cmake'}},expected,proof))
rejects('mismatched-current-proof-hash',lambda:m.compare_profile(observed,expected,proof|{'path_sha256':'0'*64}))
rejects('mismatched-prior-proof-hash',lambda:m.compare_profile(observed,expected,proof|{'previous_path_sha256':'0'*64}))
rejects('extra-proof-data',lambda:m.compare_profile(observed,expected,proof|{'ignored':True}))
source=Path(m.__file__);tree=ast.parse(source.read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
assignment=next(n for n in ast.walk(main) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='path_probe' for t in n.targets))
program=eval(compile(ast.Expression(assignment.value),str(source),'eval'),{'Path':Path,'__file__':str(source)})
process=subprocess.run([sys.executable,'-B','-c',program,old,new],env=os.environ|{'PATH':current},text=True,capture_output=True,timeout=10)
(out/'child.stdout').write_text(process.stdout);(out/'child.stderr').write_text(process.stderr)
assert process.returncode==0 and not process.stderr and json.loads(process.stdout)==proof
passed('actual-child-program-uses-exact-path-transition-function')
result={'cases':cases,'native_profiles_executed':0,'child_python_exit_code':process.returncode,'helper_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'contract_sha256':hashlib.sha256((m.EVIDENCE/'contract.json').read_bytes()).hexdigest()}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':len(cases),'total':len(cases)}))

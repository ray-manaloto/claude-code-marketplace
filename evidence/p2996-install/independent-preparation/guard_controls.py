from pathlib import Path
import ast,copy,hashlib,json,os,sys,traceback
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
OUT=Path(__file__).resolve().parent;FIX=OUT/'guard-fixtures';FIX.mkdir()
HELPER=ROOT/'dev/toolchains/p2996_install.py';EXPECTED='5389d8c5a6f422eb6006f16902728e64dcc7d1303819047417472613be5a99d3'
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(HELPER)==EXPECTED
tree=ast.parse(HELPER.read_bytes());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
nodes={n.lineno:n for n in ast.walk(main) if isinstance(n,ast.stmt)}
groups={}
def exact(label, lines):
 selected=[nodes[n] for n in lines]
 groups[label]={'lines':lines,'ast_sha256':hashlib.sha256(ast.dump(ast.Module(body=selected,type_ignores=[]),include_attributes=False).encode()).hexdigest()}
 return compile(ast.Module(body=selected,type_ignores=[]),str(HELPER),'exec')
absence=exact('prefix_and_manifest_absence',[124])
admit=exact('install_admission',[179,180,181,182,183,184])
binding=exact('input_bindings_function',[149])
post=exact('post_install_manifest_alias_reconciliation',[208,209,210,211,219,224])
directory_guard=exact('private_run_directory',[48,57])
prerequisites=exact('successful_build_and_contract',[110,111,112,113,114,115,116,119,120,121,122,123])
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prefix_inventory')
scope={'Path':Path,'os':os,'digest':digest};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(HELPER),'exec'),scope);inventory=scope['prefix_inventory']
results=[]
def check(name, code, values, expected, mutate=None, restore=None):
 try:
  if mutate:mutate()
  exec(code,values);accepted=True;error=None;location=None
 except (AssertionError,ValueError,KeyError,FileNotFoundError,RuntimeError,OSError) as exc:
  accepted=False;error=type(exc).__name__;location=traceback.extract_tb(exc.__traceback__)[-1].lineno
 finally:
  if restore:restore()
 results.append({'case':name,'expected_accepted':expected,'accepted':accepted,'exception':error,'exception_line':location,'pass':accepted==expected})
def scope_for():
 base=FIX/('case-'+str(len(results)));base.mkdir();workspace=base/'workspace';(workspace/'build').mkdir(parents=True);source=base/'source';source.mkdir()
 prefix=workspace/'prefix';manifests=[workspace/'build/install_manifest.txt',workspace/'build/builtins.txt',workspace/'build/runtimes.txt']
 return {'Path':Path,'os':os,'digest':digest,'prefix':prefix,'manifests':manifests,'workspace':workspace,'build':workspace/'build','source':source,'directory':base/'receipt','ROOT':base/'repo'}
for name,kind in [('absent-prefix-and-manifests',None),('existing-prefix','prefix'),('dangling-prefix','dangling-prefix'),('existing-manifest','manifest'),('dangling-manifest','dangling-manifest')]:
 v=scope_for()
 if kind=='prefix':v['prefix'].mkdir()
 if kind=='dangling-prefix':v['prefix'].symlink_to('missing')
 if kind=='manifest':v['manifests'][0].write_text('occupied\n')
 if kind=='dangling-manifest':v['manifests'][0].symlink_to('missing')
 check(name,absence,v,kind is None)
class Parser:
 def error(self,message):raise ValueError(message)
for name,change in [('valid-private-run',None),('relative-run',lambda v:v.update(directory=Path('relative'))),('repository-run',lambda v:v.update(directory=v['ROOT']/'new')),('source-run',lambda v:v.update(directory=v['source']/'new')),('build-run',lambda v:v.update(directory=v['build']/'new'))]:
 v=scope_for();v['parser']=Parser()
 if change:change(v)
 check(name,directory_guard,v,change is None)
for name,change in [('bound-inputs-unchanged',None),('bound-input-byte-drift','bytes'),('prefix-parent-symlink','parent'),('build-symlink','build')]:
 v=scope_for();bound=v['workspace']/'bound';bound.write_text('expected\n');v['bindings']={str(bound):digest(bound)}
 exec(binding,v)
 if change=='bytes':bound.write_text('changed\n')
 if change in ('parent','build'):
  link=v['workspace'].parent/'redirect';link.symlink_to(v['workspace'],target_is_directory=True)
  if change=='parent':v['prefix']=link/'prefix'
  else:v['build']=link/'build'
 check(name,compile('inputs_unchanged()','<control invocation>','exec'),v,change is None)
for name,change in [('reviewed-build-contract',None),('failed-build','state'),('unreleased-build-lease','released'),('build-command-failed','command'),('review-finding','finding'),('operation-hash-drift','operation'),('supporting-receipt-drift','supporting'),('contract-root-drift','roots'),('manifest-contract-drift','manifests'),('unclassified-script-command','unknown'),('parallel-install-enabled','parallel')]:
 v=scope_for();built=v['workspace']/'evidence';(built/'operation').mkdir(parents=True);(built/'independent-build').mkdir()
 h=built/'helper';h.write_text('frozen inert helper\n');v.update(built=built,helper=h)
 q={'state':'PASS: build only; artifacts require review','protected_state_unchanged':True,'lease':{'released_after_operation':True},'commands':[{'returncode':0} for _ in range(22)],'helper_sha256':digest(h)}
 (built/'operation/qualification.json').write_text(json.dumps(q))
 refs=[]
 for n in ('post-state.json','post-build-inventory.json'):
  p=built/'independent-build'/n;p.write_text('{}\n');refs.append({'path':str(p),'sha256':digest(p)})
 review={'result':'PASS','findings':[],'operation_sha256':digest(built/'operation/qualification.json'),'helper_sha256':digest(h),'supporting_receipts':refs}
 contract={'roots':{'build':str(v['build']),'source':str(v['source']),'configured_prefix':str(v['prefix'])},'expected_ordinary_manifests':list(map(str,v['manifests'])),'unclassified_generated_command_names':[],'generated_install_controls':[{'Parallel':False}]}
 v.update(qualified=q,review=review,contract=contract)
 if change=='state':q['state']='FAIL'
 if change=='released':q['lease']['released_after_operation']=False
 if change=='command':q['commands'][0]['returncode']=1
 if change=='finding':review['findings']=['unresolved']
 if change=='operation':review['operation_sha256']='0'*64
 if change=='supporting':(built/'independent-build/post-state.json').write_text('{"changed":true}\n')
 if change=='roots':contract['roots']['build']+='-other'
 if change=='manifests':contract['expected_ordinary_manifests'].pop()
 if change=='unknown':contract['unclassified_generated_command_names']=['unknown']
 if change=='parallel':contract['generated_install_controls'][0]['Parallel']=True
 check(name,prerequisites,v,change is None)
for name,change in [('matching-install-admission',None),('wrong-helper','helper'),('wrong-admission-proposal','proposal'),('wrong-review-proposal','review-proposal'),('wrong-run-directory','directory'),('wrong-review-hash','hash'),('failed-review','failed'),('review-has-findings','findings'),('lock-module-drift','lock')]:
 v=scope_for();e=v['workspace']/'admission';e.mkdir();h=e/'helper';h.write_text('inert\n');lock=e/'lock';lock.write_text('inert lock\n');proposal={'bound':True}
 prepared={'helper_sha256':digest(h),'proposal':proposal.copy(),'result':'PASS: preparation only','findings':[]}
 review_file=e/'preparation-review.json';review_file.write_text(json.dumps(prepared))
 admission={'helper_sha256':digest(h),'proposal':proposal.copy(),'run_directory':str(v['directory']),'review_sha256':digest(review_file)}
 v.update(evidence=e,__file__=str(h),LOCK_MODULE=lock,LOCK_SHA=digest(lock),proposal=proposal,prepared=prepared,admission=admission)
 if change=='helper':admission['helper_sha256']='0'*64
 if change=='proposal':admission['proposal']={'bound':False}
 if change=='review-proposal':prepared['proposal']={'bound':False}
 if change=='directory':admission['run_directory']+='-other'
 if change=='hash':admission['review_sha256']='0'*64
 if change=='failed':prepared['result']='FAIL'
 if change=='findings':prepared['findings']=['unresolved']
 if change=='lock':lock.write_text('changed\n')
 check(name,admit,v,change is None)
def post_scope():
 v=scope_for();p=v['prefix'];(p/'bin').mkdir(parents=True);v['directory'].mkdir()
 for n in ('clang-21','llvm-ar'):(p/'bin'/n).write_text('private inert '+n+'\n')
 (p/'bin/clang').symlink_to('clang-21');(p/'bin/clang++').symlink_to('clang');(p/'bin/llvm-ranlib').symlink_to('llvm-ar')
 files=[str(p/'bin'/n) for n in ('clang-21','clang','llvm-ar')]
 for index,m in enumerate(v['manifests']):m.write_text('\n'.join(files if index==0 else [])+('\n' if index==0 else ''))
 aliases=[{'destination':str(p/'bin'/n),'target_text':t,'target_resolved_relative_to_destination':str(p/'bin'/t)} for n,t in [('clang++','clang'),('llvm-ranlib','llvm-ar')]]
 v.update(contract={'aliases':aliases},prefix_inventory=inventory)
 return v
for name,change in [('complete-prefix-direct-and-chained-aliases',None),('duplicate-manifest-entry','duplicate'),('missing-manifest-leaf','missing'),('unlisted-prefix-file','extra'),('outside-manifest-path','outside'),('relative-manifest-path','relative'),('manifest-directory-entry','dir'),('nonexistent-manifest-leaf','nonexistent'),('symlink-manifest','link'),('wrong-alias-target','wrong-alias'),('escaping-alias','escape'),('dangling-alias','dangling'),('unsupported-prefix-fifo','fifo')]:
 v=post_scope();p=v['prefix'];m=v['manifests'][0]
 if change=='duplicate':m.write_text(m.read_text()+str(p/'bin/clang-21')+'\n')
 if change=='missing':m.write_text(str(p/'bin/clang-21')+'\n')
 if change=='extra':(p/'extra').write_text('unlisted\n')
 if change=='outside':
  outside=v['workspace']/'outside';outside.write_text('inert\n');m.write_text(m.read_text()+str(outside)+'\n')
 if change=='relative':m.write_text('bin/clang-21\n')
 if change=='dir':m.write_text(m.read_text()+str(p/'bin')+'\n')
 if change=='nonexistent':m.write_text(m.read_text()+str(p/'missing')+'\n')
 if change=='link':
  real=m.with_name('actual-manifest');m.rename(real);m.symlink_to(real.name)
 if change in ('wrong-alias','escape','dangling'):
  a=p/'bin/clang++';a.unlink()
  if change=='wrong-alias':a.symlink_to('llvm-ar')
  if change=='dangling':a.symlink_to('missing')
  if change=='escape':
   outside=v['workspace']/'outside';outside.write_text('inert\n');a.symlink_to(outside)
 if change=='fifo':os.mkfifo(p/'unsupported')
 check(name,post,v,change is None or change=='duplicate')
v=post_scope();link=v['workspace']/'prefix-alias';link.symlink_to(v['prefix'],target_is_directory=True);v['prefix']=link
check('prefix-root-symlink-rejected',compile('prefix_inventory(prefix)','<control invocation>','exec'),v,False)
report={'result':'PASS' if all(r['pass'] for r in results) else 'FAIL','helper_sha256':EXPECTED,'python':sys.version,'scope':'Exact extracted guard and inventory AST; inert private fixtures only. No main(), --install, CMake, compiler, lease or subprocess control execution.','groups':groups,'prefix_inventory_ast_sha256':hashlib.sha256(ast.dump(fn,include_attributes=False).encode()).hexdigest(),'controls':results,'controls_count':len(results),'findings':[r for r in results if not r['pass']]}
out=OUT/'guard-controls.json';out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'result':report['result'],'controls':len(results),'findings':report['findings'],'receipt':str(out),'sha256':digest(out)},indent=2))
assert report['result']=='PASS'


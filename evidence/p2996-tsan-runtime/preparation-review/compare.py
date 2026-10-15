from pathlib import Path
import ast, copy, datetime, hashlib, json, os, stat, struct, subprocess, time, uuid
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-tsan-runtime';OUT=Path(__file__).parent
HEAD='847684dc237e669a3d8eaa23795b68ae31625f56'
CAND='2926689a130dabdc34e130f27290129c1b05429ea4cfb99c341c2f0318474481'
SNAP='afd293aeaa228ba52e29cc8dcfb8e55c96a24e4beeb25840f329a159fda76c3f'
CONTRACT='3e33503010361fe6d66d4906b3fa3b73c92fce8a191daab86cbc40cde5d7be36'
PY='/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3'
cache={};watched={};checks={}
def sha(b):return hashlib.sha256(b).hexdigest()
def eq(a,b,why):assert a==b,(why,a,b)
def stamp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def data(p,h=None):
 p=Path(p);p=p if p.is_absolute() else ROOT/p;k=str(p)
 if k not in cache:
  a=p.lstat();assert stat.S_ISREG(a.st_mode) and a.st_size<4000000,k
  b=p.read_bytes();eq(stamp(p.lstat()),stamp(a),'stable text '+k);b.decode('utf-8');cache[k]=b;watched[k]=sha(b)
 if h is not None:eq(watched[k],h,'text digest '+k)
 return cache[k]
def obj(p,h=None):return json.loads(data(p,h))
can=obj(E/'candidate.json',CAND);snap=obj(E/'candidate-inputs.json',SNAP);c=obj(E/'contract.json',CONTRACT)
eq(can['base_head'],HEAD,'candidate head');eq(c['base_head'],HEAD,'contract head');eq(can['candidate_inputs_sha256'],SNAP,'snapshot link');eq(can['contract_sha256'],CONTRACT,'contract link')
eq(len(can['files']),4,'maintained count');eq(len(can['receipts']),5,'receipt count');eq(len(snap),8,'snapshots')
for p,h in (can['files']|can['receipts']|snap).items():data(p,h)
module=ROOT/'dev/toolchains/p2996_tsan_runtime.py';module_sha=watched[str(module)]
eq(module_sha,'1b573b7ee86dd4f220ba0e7cbfaa70fe8e381500d54127f0ddfb8f32cb0b8ec3','frozen module')
for p,h in c['inputs'].items():data(p,h)
eq(len(c['inputs']),27,'direct contract inputs')
a=obj(ROOT/'evidence/p2996-asan-runtime/contract.json');eq(len(a['inputs']),19,'inherited inputs')
for p,h in a['inputs'].items():eq(c['inputs'][p],h,'unchanged inherited binding '+p)
added={'dev/toolchains/p2996_asan_runtime.py','evidence/p2996-asan-runtime/contract.json','evidence/p2996-asan-promotion/artifact-review.json','evidence/p2996-asan-promotion/operation/qualification.json','evidence/p2996-tsan-repair/artifact-review/review.json','evidence/p2996-tsan-repair/operation/qualification.json','evidence/p2996-tsan-repair/operation/closure.json','evidence/p2996-tsan-repair/artifact-inventory.json'}
eq(set(c['inputs'])-set(a['inputs']),added,'eight added bindings')
for p,h in snap.items():eq(c['inputs'][p],h,'candidate snapshot binding')
checks['snapshots']={'maintained':4,'receipts':5,'prerequisite_snapshots':8,'direct_contract_inputs':27,'unchanged_inherited_inputs':19,'new_inputs':sorted(added)}
RUNTIME='lib/clang/21/lib/darwin/libclang_rt.tsan_osx_dynamic.dylib'
ARTIFACTS='evidence/p2996-install/independent-installation/post-install-inventory.json';PREFIX='evidence/p2996-install/operation/prefix-inventory.json'
eq(c['artifact_inventory'],ARTIFACTS,'artifact inventory path');eq(c['prefix_inventory'],PREFIX,'prefix inventory path')
eq(c['prefix'],a['prefix'],'same prefix');eq(c['target'],str(Path(c['prefix'])/RUNTIME),'exact target')
eq(c['current_tsan'],{**{k:c['qualified_replacement'][k] for k in ['sha256','bytes']},'mode':'0o755'},'planned installed identity')
eq(c['qualified_replacement_identity'],{**{k:c['qualified_replacement'][k] for k in ['sha256','bytes']},'mode':'0o700'},'private identity')
eq(can['original_tsan_sha256'],c['previous_record']['sha256'],'old digest');eq(can['qualified_private_tsan_sha256'],c['current_tsan']['sha256'],'new digest');eq(can['installed_mutation'],False,'no installed write claim')
# Static inventory derivation only: no candidate/guard function is imported or called.
static_deltas={}
for path,key in [(ARTIFACTS,'previous_record'),(PREFIX,'previous_prefix_record')]:
 inventory=obj(ROOT/path);rows=inventory['records'] if isinstance(inventory,dict) else inventory;deltas=[]
 for label,contract,current_key in [('asan',a,'current_asan'),('tsan',c,'current_tsan')]:
  expected=contract[key];matches=[(i,r) for i,r in enumerate(rows) if r['path']==expected['path'] or (key=='previous_record' and r.get('resolved_path')==expected['path'])]
  eq(len(matches),1,'unique historical '+label+' row');i,row=matches[0];eq(row,expected,'immutable historical '+label+' row')
  eq(row['mode'],'0o755','old mode');eq(contract[current_key]['mode'],'0o755','new mode');assert row['sha256']!=contract[current_key]['sha256'] and row['bytes']!=contract[current_key]['bytes']
  updated={**row,**{k:contract[current_key][k] for k in ['sha256','bytes']}}
  eq({k for k in row if row[k]!=updated[k]},{'sha256','bytes'},'two-field delta')
  deltas.append({'row_index':i,'path':row['path'],'before_sha256':row['sha256'],'before_bytes':row['bytes'],'after_sha256':updated['sha256'],'after_bytes':updated['bytes'],'changed_fields':['bytes','sha256'],'mode_preserved':row['mode']})
 static_deltas[path]={'inventory_rows':len(rows),'original_sha256':watched[str(ROOT/path)],'derived_rows':deltas}
checks['static_inventory_delta']=static_deltas
# AST comparisons inspect the code but do not execute functions or candidate controls.
def tree(path):return ast.parse(data(path).decode())
def fn(t,name):return next(x for x in ast.walk(t) if isinstance(x,ast.FunctionDef) and x.name==name)
def normalized(node):
 n=copy.deepcopy(node)
 if n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str):n.body=n.body[1:]
 return ast.dump(n,include_attributes=False)
t=tree(module);at=tree(ROOT/'dev/toolchains/p2996_asan_runtime.py')
class RenameCurrent(ast.NodeTransformer):
 def visit_Constant(self,node):
  if node.value=='current_asan':return ast.copy_location(ast.Constant(value='current_tsan'),node)
  return node
old_overlay=RenameCurrent().visit(copy.deepcopy(fn(at,'overlay')))
eq(normalized(fn(t,'overlay')),normalized(old_overlay),'exact inherited overlay algorithm')
assigns={x.targets[0].id:x.value for x in t.body if isinstance(x,ast.Assign) and len(x.targets)==1 and isinstance(x.targets[0],ast.Name)}
for k,v in [('CONTRACT_SHA',CONTRACT),('RUNTIME',RUNTIME),('ARTIFACTS',ARTIFACTS),('PREFIX',PREFIX)]:eq(ast.literal_eval(assigns[k]),v,'bound module constant '+k)
for k in ['identity','replace_exact']:eq(ast.dump(assigns[k],include_attributes=False),ast.dump(ast.parse('asan.'+k,mode='eval').body,include_attributes=False),'unchanged primitive alias '+k)
assert all(isinstance(x,(ast.Import,ast.ImportFrom,ast.Assign,ast.FunctionDef,ast.Expr)) for x in t.body)
# The downstream inventories retain the original runtime/reflection guard. No duplicate tool expectation names either sanitizer.
mr=obj(ROOT/'evidence/mise-runtime/contract.json');proposal=obj(ROOT/'evidence/iwyu-build/proposal.json',mr['inputs']['evidence/iwyu-build/proposal.json'])
assert not {a['target'],c['target']}.intersection(proposal['tools'])
rt=tree(ROOT/'dev/toolchains/mise_runtime.py');ren=tree(ROOT/'dev/toolchains/mise_renovate.py');ref=tree(ROOT/'dev/toolchains/p2996_reflection.py')
for name,node,tokens in [('mise_runtime',fn(rt,'protected'),['post-install-inventory.json','protected','p2996_reflection.py']),('mise_renovate',fn(ren,'protected'),['load','protected']),('p2996_reflection',fn(ref,'protected'),['prefix-inventory.json','sha256','bytes'])]:
 source=ast.unparse(node);assert all(token in source for token in tokens),name
checks['static_source']={'module_lines':len(data(module).splitlines()),'overlay_matches_ASan_AST_with_only_current_field_renamed':True,'protected_body_ast_sha256':sha(normalized(fn(t,'protected')).encode()),'unchanged_identity_and_replace_exact_aliases':True,'guard_chain_read_and_traced':['TSan contract/current identity','ASan then TSan in-memory inventory overlays','mise_renovate.protected','mise_runtime.protected','p2996_reflection.protected including full inventory and prefix equality'],'IWYU_tool_keys_conflict_with_sanitizer_overlays':False,'candidate_or_guard_functions_executed':False}
repair=ROOT/'evidence/p2996-tsan-repair'
rv=obj(repair/'artifact-review/review.json','88ffefd62bb5617da8ab0643cb9976c5dcac2ae8c7ad34388e25a29c688c7f9c')
prior=Path('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-tsan-repair-artifact-review-p5e41g8z/review.json')
eq(data(prior),data(repair/'artifact-review/review.json'),'qualified reviewer current copy')
q=obj(repair/'operation/qualification.json');cl=obj(repair/'operation/closure.json');inv=obj(repair/'artifact-inventory.json')
assert rv['result'].startswith('PASS') and rv['findings']==[] and q['state'].startswith('PASS') and cl['state'].startswith('PASS')
eq(rv['qualification_sha256'],watched[str(repair/'operation/qualification.json')],'qualified q binding');eq(cl['qualification_sha256'],rv['qualification_sha256'],'qualified closure q');eq(cl['native_returncode'],0,'native success receipt');assert q['protected_state_unchanged'] and q['lease_released']
eq([r for r in inv['artifacts'] if r['kind']=='patched-tsan-runtime'],[c['qualified_replacement']],'qualified row exact')
eq(q['repair']['patched']['sha256'],c['current_tsan']['sha256'],'qualified digest');eq(q['repair']['patched']['path'],c['qualified_replacement']['path'],'qualified path')
ar=obj(ROOT/'evidence/p2996-asan-promotion/artifact-review.json');aq=obj(ROOT/'evidence/p2996-asan-promotion/operation/qualification.json')
assert ar['result'].startswith('PASS') and ar['findings']==[] and aq['state'].startswith('PASS')
eq(ar['qualification_sha256'],watched[str(ROOT/'evidence/p2996-asan-promotion/operation/qualification.json')],'ASan qualification preserved')
checks['prerequisite_receipts']={'TSan_artifact_review_sha256':watched[str(repair/'artifact-review/review.json')],'TSan_review_matches_original_private_copy':True,'ASan_artifact_review_sha256':watched[str(ROOT/'evidence/p2996-asan-promotion/artifact-review.json')],'TSan_qualified_row_matches_contract':True}
controls=obj(E/'controls/controls.json',can['controls_sha256']);cp=Path(controls['private_directory'])
eq(controls['script_sha256'],watched[str(E/'controls.py.source')],'control source');eq(controls['module_sha256'],module_sha,'control module');eq(controls['contract_sha256'],CONTRACT,'control contract');eq(controls['state'],'PASS: composed overlay and private exact-file controls','control state')
eq(len(controls['commands']),3,'control command count');eq(can['controls_commands'],3,'candidate control count')
for path,values in static_deltas.items():
 eq(controls['checks'][path],{'changed_rows':[v['path'] for v in values['derived_rows']],'original_sha256':values['original_sha256']},'control inventory receipt '+path)
eq(controls['checks']['prepromotion_guard'],'rejects installed original TSan','prepromotion receipt')
eq(controls['checks']['private_transition'],'replacement, restore and unknown-target refusal passed','transition receipt')
profile='(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(cp))+') (literal "/dev/null"))\n(deny network*)\n'
eq(data(cp/'private.sb').decode(),profile,'actual control sandbox');eq(cp,cp.resolve(),'canonical control directory');eq(oct(stat.S_IMODE(cp.stat().st_mode)),'0o700','private control dir')
child='import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from p2996_tsan_runtime import replace_exact;replace_exact(Path(sys.argv[2]),Path(sys.argv[3]),json.loads(sys.argv[4]),json.loads(sys.argv[5]))'
before={k:c['previous_record'][k] for k in ['sha256','bytes','mode']};after=c['current_tsan'];expected=[('replace','staged.dylib',before,after,0),('restore','restore.dylib',after,before,0),('reject-unknown-target','staged-again.dylib',before,after,1)]
control_logs=[]
for r,(case,source,old,new,rc) in zip(controls['commands'],expected,strict=True):
 eq(r['case'],case,'control order');eq(r['returncode'],rc,'control rc');eq(r['expected_returncode'],rc,'control expected rc');assert 0<=r['elapsed_seconds']<30
 argv=['/usr/bin/sandbox-exec','-f',str(cp/'private.sb'),PY,'-E','-B','-c',child,str(ROOT/'dev/toolchains'),str(cp/source),str(cp/'target.dylib'),json.dumps(old),json.dumps(new)]
 eq(r['argv'],argv,'exact confined transition argv')
 for stream,record in r['logs'].items():
  eq(record['path'],str(cp/(case+'.'+stream)),'log path');b=data(record['path'],record['sha256']);control_logs.append({'case':case,'stream':stream,'sha256':record['sha256'],'bytes':len(b)})
  if case=='reject-unknown-target' and stream=='stderr':
   txt=b.decode();assert 'p2996_asan_runtime.py\", line 95, in replace_exact' in txt and 'identity(staged) == after and identity(destination) == before' in txt and txt.endswith('AssertionError\n')
  else:eq(b,b'','empty successful log')
checks['parent_control_receipts']={'state':controls['state'],'child_returncodes':[0,0,1],'six_log_bindings':control_logs,'exact_argv_private_only':True,'sandbox_sha256':watched[str(cp/'private.sb')],'current_ASan_guard_asserted_before_children':True,'prepromotion_TSan_rejection_reported':True,'outer_returncode_not_recorded_in_controls_json':True,'postpromotion_guard_executed':False,'control_rerun_by_reviewer':False}
static=obj(E/'pre-review-static.json');eq([r['returncode'] for r in static['commands']],[0,0,0,0],'static rc');eq(static['commands'][2]['result']['baseline'],19,'baseline receipt')
checks['parent_static_receipts']={'returncodes':[0,0,0,0],'baseline_hashes':19,'result':static['commands'][2]['result'],'independent_static_or_fresh_Claude_OCI_execution':False}
scan=obj(E/'pre-review-secret-scan.json');data(scan['script'],scan['script_sha256'])
eq(len(scan['files']),11,'scan scope');eq(scan['raw']['returncode'],0,'raw scan rc');eq(scan['dispositions'],[],'no digest dispositions');eq(scan['supplemental_complete_token_files'],[],'no complete tokens');assert 'transformed' not in scan
expected_scan=set(can['files'])|set(can['receipts'])|{str((E/'candidate.json').relative_to(ROOT)),str((E/'candidate-inputs.json').relative_to(ROOT))}
eq(set(scan['files']),expected_scan,'exact scan files')
for p,h in scan['files'].items():data(p,h)
payload=''.join(p+'\n'+data(p).decode()+'\n' for p in scan['files']);eq(sha(payload.encode()),scan['raw']['payload_sha256'],'scan actual payload binding')
report_path=next(s.partition('=')[2] for s in scan['raw']['argv'] if s.startswith('--report-path='));eq(obj(report_path),[],'native raw scanner findings file')
checks['secret_scan']={'bound_files':11,'raw_returncode':0,'raw_findings_file':report_path,'raw_findings':[],'digest_dispositions':[],'transformed_scan_run':False,'complete_token_files':[],'scanner_rerun_by_reviewer':False}
git=[]
for args,want in [(['rev-parse','--show-toplevel'],str(ROOT)),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding'),(['rev-parse','HEAD'],HEAD),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
 argv=['/usr/bin/git','-c','core.fsmonitor=false',*args];start=time.monotonic();r=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5,check=False)
 eq(r.returncode,0,'git rc');eq(r.stderr,b'','git stderr');eq(r.stdout.decode().strip(),want,'git identity')
 git.append({'argv':argv,'returncode':0,'stdout':r.stdout.decode(),'stderr':'','elapsed_seconds':time.monotonic()-start})
checks['git_identity']=git
for p,h in watched.items():eq(sha(Path(p).read_bytes()),h,'frozen end text '+p)
# Last content reads are exactly the installed original and the qualified private candidate, once each.
binaries=[]
for label,path,identity in [('installed-original',c['target'],before),('qualified-private',c['qualified_replacement']['path'],c['qualified_replacement_identity'])]:
 p=Path(path);eq(p,p.resolve(strict=True),'canonical binary');s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid();eq(s.st_size,identity['bytes'],'binary size');assert s.st_size<2000000
 b=p.read_bytes();eq(stamp(s),stamp(p.lstat()),'stable binary');eq(sha(b),identity['sha256'],'binary digest');eq(oct(stat.S_IMODE(s.st_mode)),identity['mode'],'binary mode')
 magic,cpu,subtype,filetype,ncmds,sizeofcmds,flags,reserved=struct.unpack_from('<8I',b);eq((magic,cpu,filetype),(0xfeedfacf,0x100000c,6),'arm64 dylib')
 off=32;uuids=[]
 for _ in range(ncmds):
  cmd,size=struct.unpack_from('<2I',b,off);assert size>=8 and off+size<=32+sizeofcmds
  if cmd==0x1b:uuids.append(str(uuid.UUID(bytes=b[off+8:off+24])).upper())
  off+=size
 binaries.append({'kind':label,'path':path,**identity,'content_reads':1,'mach_o':'arm64 dylib','uuids':uuids})
checks['binary_identities']={'count':2,'bytes':sum(v['bytes'] for v in binaries),'each_read_once':True,'files':binaries,'installed_original_unchanged':True,'private_mode':'0o700','planned_installed_stage_mode':'0o755'}
result={'result':'PASS: Task14b2a bounded preparation comparison','recorded_at':datetime.datetime.now(datetime.UTC).isoformat(),'candidate_sha256':CAND,'candidate_inputs_sha256':SNAP,'contract_sha256':CONTRACT,'helper_sha256':module_sha,'checks':checks,'watched_text_sha256':watched,'not_run':['No candidate controls, helper contracts/protected functions, overlay functions, replacement primitive, compiler or native witness executed','No nested guard traversal, global-state reads from predecessor input lists, source/build/compiler inventory rehash, lease/capacity/PID/census or Docker operation','No scanner/static task rerun, model session, network, service, install, promotion or OCI acceptance']}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'PASS','candidate_files':4,'receipts':5,'snapshots':8,'contract_inputs':27,'inherited_inputs':19,'control_child_rcs':[0,0,1],'binary_hashes':2,'binary_bytes':checks['binary_identities']['bytes'],'git_returncodes':[0,0,0,0]}))

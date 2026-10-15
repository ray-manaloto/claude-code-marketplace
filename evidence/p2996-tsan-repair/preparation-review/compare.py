"""Bounded independent static comparison; never imports or executes candidates."""
import ast,hashlib,json,os,re,shlex,stat,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
D=Path(__file__).parent
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-tsan-repair'
HEAD='b90a5d5703d538fd146de87d0656132bc820044b'
EXPECTED={'candidate.json':'fb849fe0298e2b0e621e57e5d70cda74f66618434adc60a8b3f2425ecf4556c6','candidate-inputs.json':'c1612f0b9a51b76e05108c7780a1288f93b62e5430a2f1ea7ae79876ba27660d','contract.json':'06f44aa7f1a3fd2627b4bbd69bea1360b7c07cf1f6790023265cdab69855b8fc','recipes.json':'6e9e548885bd19e83b2318d20620ea48f8ae79e060b70f13c6889516ffc3e68b'}
watched={};cache={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path,expected=None):
 p=Path(path)
 if p not in cache:
  b=p.read_bytes();b.decode('utf-8');cache[p]=b;watched[str(p)]=sha(b)
 if expected is not None:assert watched[str(p)]==expected,(str(p),'digest mismatch')
 return cache[p]
def load(path,expected=None):return json.loads(read(path,expected))
for name,h in EXPECTED.items():read(E/name,h)
candidate=load(E/'candidate.json');snapshots=load(E/'candidate-inputs.json');c=load(E/'contract.json');recipe=load(E/'recipes.json')
assert candidate['base_head']==c['base_head']==HEAD
assert len(candidate['files'])==4 and len(candidate['receipts'])==10
for path,h in (candidate['files']|candidate['receipts']).items():read(ROOT/path,h)
assert snapshots['candidate_sha256']==EXPECTED['candidate.json'] and snapshots['encoding']=='UTF-8 exact bytes'
assert len(snapshots['snapshots'])==8
for row in snapshots['snapshots']:
 b=read(row['source'],row['sha256']);assert b==row['text'].encode('utf-8') and len(b)==row['bytes']
assert {row['source'] for row in snapshots['snapshots']}=={str(ROOT/p) for p in candidate['files']}|{str(E/p) for p in ['contract.json','recipes.json','capacity.py.source','dispatch.py.source']}
old=load(ROOT/'evidence/p2996-tsan/contract.json','02bb703bc058f2c085289af3cabe1cd4911a90ca94cd48d37a8b3605aac23bc9')
priorprep=load(ROOT/'evidence/p2996-tsan/pre-run-review.json','7ba2da9494bbf9631c184225de58fe4a1d8be6e16590f357eaff6248d812b01f')
priorfailure=load(ROOT/'evidence/p2996-tsan/failure-review/review.json','0f59ac94d9e46439d8604b7f6533015f1114b8eac2a54b1aeb725ceb2e1b842b')
assert priorprep['result'].startswith('PASS') and not priorprep['findings']
assert priorfailure['result'].startswith('PASS') and not priorfailure['findings']
assert len(old['inputs'])==172 and len(c['inputs'])==181 and all(c['inputs'][k]==v for k,v in old['inputs'].items())
added_inputs=set(c['inputs'])-set(old['inputs']);assert len(added_inputs)==9
for path in added_inputs:read(ROOT/path,c['inputs'][path])
assert c['tools']==old['tools'] and len(c['tools'])==28
assert len(old['source_inputs'])==846 and len(c['source_inputs'])==881
assert all(c['source_inputs'][k]==v for k,v in old['source_inputs'].items())
new_sources=set(c['source_inputs'])-set(old['source_inputs']);assert len(new_sources)==35
changed_keys={'base_head','scope','inputs','source_inputs','witness','recipe_sha256','asan_qualification_sha256','original_failure'}
assert {k:v for k,v in c.items() if k not in changed_keys}=={k:v for k,v in old.items() if k not in changed_keys}
assert set(c)-set(old)=={'witness','recipe_sha256','asan_qualification_sha256','original_failure'}
assert c['recipe_sha256']==EXPECTED['recipes.json']==candidate['receipts']['evidence/p2996-tsan-repair/recipes.json']
asanrecipe=load(ROOT/'evidence/p2996-sanitizer-repair/recipes.json',recipe['prior_asan_recipes_sha256'])
assert recipe['prior_asan_recipes_sha256']=='37f79177a1afd808736b0cec56d73bd0695711d8b8b87c4cb17c8049016d7174'
asanq=load(ROOT/'evidence/p2996-sanitizer-repair/operation/qualification.json',c['asan_qualification_sha256'])
assert c['asan_qualification_sha256']==recipe['asan_qualification_sha256']=='c5f01649fe39b50744e7c3984f0a01692ce1e5a9912aba2ca7cc49ff399dffc4'
asanreview=load(ROOT/'evidence/p2996-sanitizer-repair/artifact-review.json','d24aa966165b11cc6ad7b2c0dc9a1e9af12d1d5738859193ebda0c27b7c27675')
assert asanq['state'].startswith('PASS: private ASan repair') and asanreview['result'].startswith('PASS') and not asanreview['findings']
assert asanreview['qualification_sha256']==c['asan_qualification_sha256']
asani=load(ROOT/'evidence/p2996-sanitizer-repair/artifact-inventory.json',asanreview['artifact_inventory_sha256'])
asani_by_path={r['path']:r for r in asani['artifacts']}
q=load(ROOT/'evidence/p2996-tsan/operation/qualification.json',c['inputs']['evidence/p2996-tsan/operation/qualification.json'])
cl=load(ROOT/'evidence/p2996-tsan/operation/closure.json',c['inputs']['evidence/p2996-tsan/operation/closure.json'])
inv=load(ROOT/'evidence/p2996-tsan/artifact-inventory.json',c['inputs']['evidence/p2996-tsan/artifact-inventory.json'])
w=next(r for r in inv['artifacts'] if r['kind']=='tsan-binary')
assert c['witness']=={k:w[k] for k in ['path','sha256','bytes']}
assert w['sha256']=='98bbddbab90890197bebfe79f451d7e5ad6384bd3ad340dc5f47c3b93ad0f018'
assert q['state']=='FAIL' and q['commands'][-1]['case']=='tsan-clean' and q['commands'][-1]['returncode']==-11
assert c['original_failure']=={'case':'tsan-clean','returncode':-11,'before_main':True,'receipt_sha256':c['inputs']['evidence/p2996-tsan/operation/qualification.json']}
assert priorfailure['qualification_sha256']==c['original_failure']['receipt_sha256'] and priorfailure['closure_sha256']==c['inputs']['evidence/p2996-tsan/operation/closure.json']
# Exact recorded Ninja link and signing token sequences; no Ninja subprocess.
ninja=load(E/'ninja-commands.receipt.json',recipe['ninja_receipt_sha256']);raw=read(E/'ninja-commands.stdout.source',recipe['ninja_stdout_sha256']).decode()
build=Path(recipe['build']);assert build==Path(asanrecipe['build'])
assert ninja['returncode']==0 and ninja['stdout_lines']==len(raw.splitlines())==129
assert ninja['stdout_sha256']==recipe['ninja_stdout_sha256'] and ninja['stderr_sha256']==sha(b'')
assert ninja['argv'][1:]==['-C',str(build),'-t','commands','libclang_rt.tsan_osx_dynamic.dylib']
assert ninja['argv'][0] in c['tools']
lines=[x for x in raw.splitlines() if 'libclang_rt.tsan_osx_dynamic.dylib' in x and ' -o ' in x];assert len(lines)==1
tokens=shlex.split(lines[0]);seps=[i for i,t in enumerate(tokens) if t=='&&'];assert len(seps)==3 and tokens[:2]==[':','&&']
link=tokens[2:seps[1]];sign=tokens[seps[2]+1:]
assert link==recipe['link_argv'] and sign==recipe['codesign_argv']
assert tokens[seps[1]+1]=='cd' and tokens[seps[1]+2]==str(Path(sign[-1]).parent)
assert len(link)==len(recipe['link_argv']) and link.count('-o')==1 and link[link.index('-o')+1]==sign[-1]
assert sign[:-1]==['/usr/bin/codesign','--sign','-','-o','linker-signed']
assert link[0]==asanrecipe['link_argv'][0] and link[0] in c['tools']
assert sign[0] in c['tools']
assert all(flag in link for flag in ['--target=arm64-apple-darwin27.0.0','-dynamiclib','-nodefaultlibs','-nostdlib++','-lc','-lobjc'])
assert link[link.index('-install_name')+1]=='@rpath/libclang_rt.tsan_osx_dynamic.dylib'
names=[t for t in link if t.endswith('.o')];assert len(names)==len(set(names))==128 and names==list(recipe['objects'])
assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
compile_outputs=[]
for line in raw.splitlines():
 if line==lines[0]:continue
 a=shlex.split(line);assert '-c' in a and '-o' in a
 compile_outputs.append(a[a.index('-o')+1])
assert len(compile_outputs)==128 and set(compile_outputs)==set(names)
priorobjects={str(Path(path).relative_to(build)):value for path,value in asanrecipe['objects'].items()}
shared=set(names)&set(priorobjects);fresh=set(names)-shared
assert len(shared)==recipe['shared_asan_objects']==93 and len(fresh)==recipe['tsan_only_objects']==35
assert all(recipe['objects'][n]==priorobjects[n] for n in shared)
assert {str(build/n) for n in fresh}==new_sources
assert all(c['source_inputs'][str(build/n)]==recipe['objects'][n]['sha256'] for n in names)
assert recipe['mapping_object']==asanrecipe['mapping_object'] and names.count(recipe['mapping_object'])==1
for kind,mapping in recipe['qualified_mapping_objects'].items():
 assert kind in ['original','patched']
 assert mapping=={'path':str(Path(asanq['repair'][kind]['path']).parent/'procmaps.o'),'sha256':asanq['repair'][kind]['object_sha256']}
 assert c['source_inputs'][mapping['path']]==mapping['sha256']==asani_by_path[mapping['path']]['sha256']
assert recipe['qualified_mapping_objects']['original']['sha256']!=recipe['qualified_mapping_objects']['patched']['sha256']
# Only the selected live Ninja edge/rule excerpts are read; no old tree traversal/hash.
def block(path,match):
 with path.open() as stream:
  for number,line in enumerate(stream,1):
   if match(line):
    rows=[line.rstrip('\n')]
    for rest in stream:
     if not rest.strip():break
     rows.append(rest.rstrip('\n'))
    return number,rows
 raise AssertionError(('missing bounded block',str(path)))
target=link[link.index('-o')+1]
edge_line,edge=block(build/'build.ninja',lambda s:s.startswith('build '+target+': '))
edge_tokens=edge[0].split(': ',1)[1].split();rule=edge_tokens[0]
assert [t for t in edge_tokens[1:] if t.endswith('.o')]==names
edgevars=dict(line.strip().split(' = ',1) for line in edge[1:] if ' = ' in line)
rule_line,rules=block(build/'CMakeFiles/rules.ninja',lambda s:s.strip()=='rule '+rule)
rulevars=dict(line.strip().split(' = ',1) for line in rules[1:] if ' = ' in line)
variables=edgevars|{'in':' '.join(names),'LINK_PATH':''}
expanded=re.sub(r'\$([A-Za-z_][A-Za-z_0-9]*)',lambda m:variables[m[1]],rulevars['command'])
assert shlex.split(expanded)==tokens
# Static translation: expected private arguments derived without calling the helper.
virtual=Path('/REVIEW_STATIC_PATH_ONLY/task14b1');plans={}
for kind in ['original','patched']:
 runtime=virtual/kind/'libclang_rt.tsan_osx_dynamic.dylib';obj=virtual/kind/'procmaps.o'
 copied={n:virtual/'objects'/n for n in names}
 translated=[str(obj if t==recipe['mapping_object'] else copied.get(t,t)) for t in link]
 translated[translated.index('-o')+1]=str(runtime)
 for i,t in enumerate(link):
  if t.endswith('.o'):assert Path(translated[i]).is_relative_to(virtual)
  elif i==link.index('-o')+1:assert translated[i]==str(runtime)
  else:assert translated[i]==t
 assert len([t for t in translated if t.endswith('.o')])==128
 plans[kind]={'link_argv':translated,'codesign_argv':sign[:-1]+[str(runtime)]}
differing=[i for i,(a,b) in enumerate(zip(plans['original']['link_argv'],plans['patched']['link_argv'])) if a!=b]
assert differing==sorted([link.index('-o')+1,link.index(recipe['mapping_object'])])
# Retained guard/run behavior and launcher provenance, compared statically with ASTs.
helper=read(ROOT/'dev/toolchains/p2996_tsan_repair.py',candidate['files']['dev/toolchains/p2996_tsan_repair.py']).decode()
previous=read(ROOT/'dev/toolchains/p2996_tsan.py','772b0e5eb433bdc5b759c1d2f20da60503a0efc128b256f8263aed705b3f353d').decode()
def functions(text):return {x.name:x for x in ast.walk(ast.parse(text)) if isinstance(x,ast.FunctionDef)}
a,b=functions(previous),functions(helper)
for name in ['save','run','source_state','interrupted']:assert ast.dump(a[name])==ast.dump(b[name]),name
assert [ast.dump(n) for n in a['guard'].body[:-1]]==[ast.dump(n) for n in b['guard'].body[:len(a['guard'].body)-1]]
assert ast.dump(a['guard'].body[-1])==ast.dump(b['guard'].body[-1]) and len(b['guard'].body)==len(a['guard'].body)+3
assert c['sanitizers']==old['sanitizers'] and c['runtime_environment']==old['runtime_environment']
expected_cases=['original-clean:-11']+[mode+'-'+case+':'+str(code) for mode,settings in c['sanitizers'].items() for case,code in {'clean':0,**{n:86 for n in settings['errors']}}.items()]
assert candidate['expected_cases']==expected_cases and len(expected_cases)==6
assert 'expected=-signal.SIGSEGV' in helper and 'assert "reflection value=" not in original_trace' in helper
assert 'sanitizer_images == {report["repair"]["patched"]["path"]}' in helper
launchers=load(E/'prepared-launchers.json');assert launchers['helper_sha256']==candidate['files']['dev/toolchains/p2996_tsan_repair.py'] and launchers['contract_sha256']==EXPECTED['contract.json']
for name,row in launchers['launchers'].items():
 assert read(row['private'],row['sha256'])==read(row['repository'],row['sha256'])
 assert str(Path(row['private']).parent)==launchers['private_directory']
assert set(launchers['launchers'])=={'capacity','dispatch'}
# Static preservation and scan results are receipts only, not replayed.
static=load(E/'pre-review-static.json');assert len(static['commands'])==3 and all(r['returncode']==0 for r in static['commands'])
baseline=json.loads(static['commands'][1]['stdout']);assert baseline['checks']['baseline']==19 and baseline['status']=='pass'
scan=load(E/'pre-review-secret-scan.json');assert len(scan['files'])==16
for n,h in scan['files'].items():read(ROOT/n,h)
read(scan['script'],scan['script_sha256'])
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and not scan['supplemental_complete_token_files']
assert len(scan['dispositions'])==5
oldscan=load(ROOT/'evidence/p2996-tsan/pre-artifact-secret-scan.json')
old_dispositions={(x['path'],x['sha256']) for x in oldscan['dispositions']}
new_dispositions=[x for x in scan['dispositions'] if (x['path'],x['sha256']) not in old_dispositions]
assert len(new_dispositions)==1 and new_dispositions[0]['path'] in new_sources
assert new_dispositions[0]['sha256']==c['source_inputs'][new_dispositions[0]['path']]
assert all(x['rule']=='generic-api-key' and x['reason']=='Verified exact file-content digest' for x in scan['dispositions'])
# Four pure Git identity commands, bounded separately; no status/census/source commands.
git=[]
for tail,want in [(['rev-parse','--show-toplevel'],str(ROOT)),(['rev-parse','--verify','HEAD'],HEAD),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding')]:
 argv=['/usr/bin/git','-C',str(ROOT)]+tail;r=subprocess.run(argv,text=True,capture_output=True,timeout=5)
 git.append({'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 assert r.returncode==0 and r.stdout.strip()==want
for path,h in watched.items():assert sha(Path(path).read_bytes())==h,('changed text',path)
# The only binary reads in this comparison: 35 new objects, two qualified mapping objects, one old witness. Each is hashed once, at the end.
binary_inputs=[{'kind':'new-tsan-object','path':str(build/n),**recipe['objects'][n]} for n in names if n in fresh]
binary_inputs += [{'kind':kind+'-qualified-mapping','path':row['path'],'sha256':row['sha256'],'bytes':asani_by_path[row['path']]['bytes']} for kind,row in recipe['qualified_mapping_objects'].items()]
binary_inputs += [{'kind':'preserved-tsan-witness',**c['witness']}]
assert len(binary_inputs)==len({r['path'] for r in binary_inputs})==38
binary_results=[]
for row in binary_inputs:
 p=Path(row['path']);before=p.lstat();assert p.resolve()==p and stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.getuid()
 with p.open('rb') as f:
  opened=os.fstat(f.fileno());assert (opened.st_dev,opened.st_ino)==(before.st_dev,before.st_ino)
  data=f.read();afterfd=os.fstat(f.fileno())
 after=p.lstat();identity=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 assert identity(before)==identity(opened)==identity(afterfd)==identity(after)
 assert len(data)==row['bytes'] and sha(data)==row['sha256'],row['path']
 assert data[:4]==b'\xcf\xfa\xed\xfe';cpu,subtype,kind=struct.unpack_from('<III',data,4)
 assert cpu==0x0100000c and kind==(2 if row['kind']=='preserved-tsan-witness' else 1)
 binary_results.append(row|{'mode':oct(stat.S_IMODE(before.st_mode)),'single_link':True,'canonical':True,'arm64_macho_type':kind,'hash_passes':1})
result={'result':'PASS: Task14b1 preparation static comparison','recorded_at':datetime.now(timezone.utc).isoformat(),'candidate_sha256':EXPECTED['candidate.json'],'helper_sha256':candidate['files']['dev/toolchains/p2996_tsan_repair.py'],'contract_sha256':EXPECTED['contract.json'],'recipe_sha256':EXPECTED['recipes.json'],'checks':{'snapshots':8,'maintained_files':candidate['files'],'candidate_receipt_bindings':10,'new_project_inputs':9,'inherited_project_inputs':172,'new_source_objects':35,'inherited_source_inputs':846,'unchanged_tools':28,'recipe_objects':128,'shared_object_metadata':93,'new_object_metadata':35,'native_ninja_receipt':ninja,'ninja_compile_commands_parsed_only':128,'ninja_edge':{'path':str(build/'build.ninja'),'line':edge_line,'rule':rule,'selected_text_sha256':sha(('\n'.join(edge)+'\n').encode()),'full_file_hashed':False},'ninja_rule':{'path':str(build/'CMakeFiles/rules.ninja'),'line':rule_line,'text':rules,'full_file_hashed':False},'exact_link_and_sign_argv_match':True,'variant_link_differences_only_output_and_mapping':differing,'static_private_argument_plans':plans,'unchanged_ast_functions':['save','run','source_state','interrupted'],'guard_additions':3,'expected_cases':expected_cases,'prepared_launcher_pairs':2,'static_receipt_returncodes':[r['returncode'] for r in static['commands']],'static_baseline_hashes':19,'scan':{'files':16,'raw_rc':1,'digest_dispositions':5,'old_digest_dispositions_reused':4,'new_object_digest_checked':1,'transformed_rc':0,'complete_token_files':[]},'git_identity':git,'binary_hashes':len(binary_results),'binary_bytes':sum(r['bytes'] for r in binary_results),'binary_results':binary_results},'watched_text_sha256':watched,'not_run':['Candidate/helper import or execution, compiler/linker/Ninja/witness/lipo/codesign execution','Capacity/census/current PID probes or lease acquisition','Full 881-input guard or source traversal; 93 inherited objects and compiler binaries not rehashed','Scanners/baseline rerun, network/credentials/global changes, fresh model/Claude/OCI sessions','Native A/B, repair effectiveness, installed promotion or expanded sanitizer qualification']}
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':result['result'],'snapshots':8,'objects':128,'reused':93,'binary_hashes_once':len(binary_results),'binary_bytes':sum(r['bytes'] for r in binary_results),'launchers':2}))

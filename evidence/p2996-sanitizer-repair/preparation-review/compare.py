from pathlib import Path
import ast,hashlib,json,shlex,stat
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/p2996-sanitizer-repair';D=Path(__file__).parent
cache={};watched={}
def raw(p):
 p=Path(p);p=p if p.is_absolute() else R/p
 if str(p) not in cache:cache[str(p)]=p.read_bytes();watched[str(p)]=hashlib.sha256(cache[str(p)]).hexdigest()
 return cache[str(p)]
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def j(p):return json.loads(raw(p))
H='f6e97415b653749f45a850931dd0992e5525fe34ed866a0cb0a182a79c1974ab';C='7c497b5073b0ea74d43f11f2b982e5c01138191226c67ff17c55db0650dc56bd';F='d123b25200cdfe26e78bc622d173d7eebe013f9927ad2b4e4bac9cf1a69ee8e4';HEAD='55a37282b117fca534a86fedcdbd5c8352405e23'
assert sha(E/'candidate.json')==F and sha(E/'contract.json')==C and sha(R/'dev/toolchains/p2996_sanitizer_repair.py')==H
candidate=j(E/'candidate.json');c=j(E/'contract.json');old=j(R/'evidence/p2996-sanitizers/contract.json')
assert candidate['head']==c['base_head']==HEAD and len(candidate['files'])==5
for p,h in candidate['files'].items():assert sha(p)==h
snaps=j(E/'candidate-inputs.json')['files'];assert len(snaps)==7
for a in snaps:
 b=a['text'].encode();assert len(b)==a['bytes'] and hashlib.sha256(b).hexdigest()==a['sha256'] and b==raw(a['source'])
for k in old:
 if k in ['inputs','tools','source_inputs']:assert all(c[k].get(p)==h for p,h in old[k].items())
 elif k not in ['base_head','scope']:assert c[k]==old[k],k
assert set(c)-set(old)=={'repair'} and len(c['inputs'])-len(old['inputs'])==40
prior=candidate['reused_guard_source'];assert sha(prior['path'])==prior['sha256']=='15800f647fa9fd39d553a5bc505da63ed41cef55fa53dcfa6569fa1e8f1117e6'
a=ast.parse(raw(prior['path']));b=ast.parse(raw(R/'dev/toolchains/p2996_sanitizer_repair.py'))
def fn(tree,name):return next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
def dump(node):return ast.dump(node,include_attributes=False)
for name in ['save','run','interrupted']:assert dump(fn(a,name))==dump(fn(b,name))
oldguard=fn(a,'guard');newguard=fn(b,'guard');assert len(newguard.body)==len(oldguard.body)+2
assert [dump(n) for n in newguard.body[:-3]+newguard.body[-1:]]==[dump(n) for n in oldguard.body]
assert sum(1+len(s['errors']) for s in c['sanitizers'].values())==7 and list(c['sanitizers'])==['asan','ubsan','asan-ubsan']
repair=c['repair'];assert repair==j(E/'patch-inputs.json')
assert sha(repair['patch'])==repair['patch_sha256'] and sha(repair['source'])==repair['before_sha256']
review=j(E/'source-review.json');assert sha(E/'source-review.json')==candidate['source_review_sha256']=='76ebb9f4bc66ea131b5784da61733a3c2c45fb7102acd7707134c110b501b7bc'
assert review['patch']['sha256']==repair['patch_sha256'] and review['patch']['expected_preimage_sha256']==repair['before_sha256'] and review['patch']['reconstructed_postimage_sha256']==repair['after_sha256']
assert review['disposition']=='NO_SOURCE_SAFETY_BLOCKER_FOUND_WITHIN_QUALIFIED_MACOS_ARM64_SCOPE_NATIVE_ACCEPTANCE_UNVERIFIED'
assert review['execution']['native_commands']==[] and review['execution']['network_requests']==[]
manifest=j(E/'preparation-copy-manifest.json')['files'];assert len(manifest)==25
for row in manifest:assert raw(row['source'])==raw(row['destination']) and sha(row['destination'])==row['sha256']
sourcemanifest=j(E/'source-review-copy-manifest.json')['files'];assert len(sourcemanifest)==1
for row in sourcemanifest:assert raw(row['source'])==raw(row['destination']) and sha(row['destination'])==row['sha256']
controls=j(E/'patch-controls/patch-controls.json');assert controls['state'].startswith('PASS') and not controls['compiler_executed'] and controls['shared_source_unchanged']
assert [x['case'] for x in controls['commands']]==['reverse-original','apply-check','apply','apply-twice','reverse-check','reverse']
assert [x['returncode'] for x in controls['commands']]==[1,0,0,1,0,0]
for row in controls['commands']:
 assert row['returncode']==row['expected'] and row['elapsed_seconds']<20
 for log in row['logs']:assert sha(log['path'])==log['sha256']
 out,err=[raw(log['path']) for log in row['logs']];assert not out
 if row['expected']==0:assert not err
 else:assert b'patch failed' in err and b'sanitizer_procmaps_mac.cpp' in err
assert sha(Path(repair['preparation_directory'])/'patch-controls'/repair['source_relative'])==repair['before_sha256']
recipe=j(E/'recipes.json');build=Path(recipe['build']);assert len(recipe['objects'])==127 and recipe['candidate_output'] is None
assert recipe['compile_argv']==shlex.split(raw(E/'object.stdout').decode())
asan=shlex.split(raw(E/'asan.stdout').decode());assert asan[:2]==[':','&&'] and asan[2:213]==recipe['link_argv'] and asan[213:215]==['&&','cd'] and asan[216]=='&&' and asan[217:]==recipe['codesign_argv']
assert asan[215]==str(Path(recipe['codesign_argv'][-1]).parent)
for name,h in recipe['recipe_sources'].items():assert sha(E/name)==h
inventory=j(E/'inventory.json');assert inventory['build']==str(build)
for row in inventory['commands']:
 assert row['returncode']==0 and row['argv'][3:6]==['-t','commands','-s']
 for suffix in ['stdout','stderr']:assert sha(E/(row['case']+'.'+suffix))==row[suffix+'_sha256']
assert recipe['compiler_matches_prefix'] is False and recipe['preparation_attempts'][0]['returncode']==1 and recipe['preparation_attempts'][0]['operation_started'] is False
object_args=[x for x in recipe['link_argv'] if x.endswith('.o')]
assert len(object_args)==127 and len(set(object_args))==127 and object_args.count(recipe['mapping_object'])==1
assert {str(build/x) for x in object_args}==set(recipe['objects'])
for p in recipe['objects']:assert Path(p).is_absolute() and Path(p).is_relative_to(build) and '..' not in Path(p).parts
assert recipe['compile_argv'][recipe['compile_argv'].index('-c')+1]==repair['source']
assert recipe['compile_argv'][recipe['compile_argv'].index('-o')+1]==recipe['mapping_object']
assert recipe['codesign_argv'][:5]==['/usr/bin/codesign','--sign','-','-o','linker-signed']
assert not any(t in ['&&',';','|','cd'] for key in ['compile_argv','link_argv','codesign_argv'] for t in recipe[key])
# Independently model path substitutions without invoking candidate functions or creating a runtime directory.
private=D/'not-executed-private-run';projected=[]
objects={str(Path(p).relative_to(build)):private/'objects'/Path(p).relative_to(build) for p in recipe['objects']}
for variant in ['original','patched']:
 tree=private/variant;source=tree/repair['source_relative'];obj=tree/'procmaps.o';runtime=tree/'libclang_rt.asan_osx_dynamic.dylib'
 compile_argv=list(recipe['compile_argv'])
 for flag,val in [('-c',source),('-o',obj),('-MT',obj),('-MF',tree/'procmaps.o.d')]:
  assert compile_argv.count(flag)==1;compile_argv[compile_argv.index(flag)+1]=str(val)
 compile_argv+=['-I',str(Path(repair['source']).parent)]
 link=[str(obj if t==recipe['mapping_object'] else objects.get(t,t)) for t in recipe['link_argv']];link[link.index('-o')+1]=str(runtime)
 assert len([t for t in link if t.endswith('.o')])==127
 assert all(Path(t).is_relative_to(private) for t in link if t.endswith('.o'))
 assert link.count(str(obj))==1 and str(build/recipe['mapping_object']) not in link
 assert compile_argv[compile_argv.index('-c')+1]==str(source)
 assert all(Path(compile_argv[compile_argv.index(flag)+1]).is_relative_to(tree) for flag in ['-o','-MT','-MF'])
 sign=recipe['codesign_argv'][:-1]+[str(runtime)];assert sign[-1]==link[link.index('-o')+1]
 projected.append({'variant':variant,'compile_argv':compile_argv,'link_object_count':127,'link_output':str(runtime),'codesign_argv':sign})
provenance=j(E/'build-compiler-provenance.json');assert provenance['state'].startswith('PASS') and provenance['rehashed_once'] is True and len(provenance['files'])==3
for row in provenance['files']:assert c['tools'][row['path']]==row['sha256']
compiler=recipe['compile_argv'][0];assert recipe['link_argv'][0]==compiler and c['tools'][compiler]==recipe['compiler_identities'][compiler]['sha256']
assert str(Path(compiler).resolve())==recipe['compiler_identities'][compiler]['resolved']
assert c['tools'][recipe['codesign']['path']]==recipe['codesign']['sha256']
deps=j(E/'object-source-inputs.json');receipt=j(E/'object-dependencies.json');assert sha(E/'object-dependencies.json')==deps['command_receipt_sha256']
assert receipt['returncode']==0 and receipt['compiler_executed'] is False and receipt['argv'][3:5]==['-t','deps'] and receipt['argv'][-1]==recipe['mapping_object']
for log in receipt['logs']:assert sha(log['path'])==log['sha256'] and raw(log['path'])==raw(E/Path(log['path']).name)
lines=raw(E/'object-dependencies.stdout').decode().splitlines();assert '#deps 195' in lines[0]
assert {s.strip() for s in lines[1:] if s.strip()}==set(deps['inputs']) and len(deps['inputs'])==195
assert all(c['source_inputs'].get(p)==h for p,h in deps['inputs'].items())
assert all(c['source_inputs'].get(row['path'])==row['sha256'] for row in review['sources'])
launchers=j(E/'prepared-launchers.json');assert launchers['executed'] is False
for name in ['capacity','dispatch']:
 row=launchers[name];assert sha(row['source'])==row['source_sha256'] and sha(row['path'])==row['sha256'] and raw(row['path'])==raw(E/(name+'.py.source'))
capacity=raw(launchers['capacity']['source']).decode();expected=capacity.replace('evidence/p2996-sanitizers/contract.json','evidence/p2996-sanitizer-repair/contract.json').replace('4e5e3bc187c0d0f19c71be093c020deb5dd7eb02a12ac93ee198f57cebd249bb',C)
extra="assert hashlib.sha256((ROOT / 'dev/toolchains/p2996_sanitizer_repair.py').read_bytes()).hexdigest() == '"+H+"'\n"
assert raw(E/'capacity.py.source').decode()==expected.replace('assert __debug__\n',extra+'assert __debug__\n')
dispatch=raw(launchers['dispatch']['source']).decode()
assert raw(E/'dispatch.py.source').decode()==dispatch.replace('evidence/p2996-sanitizers','evidence/p2996-sanitizer-repair').replace('dev/toolchains/p2996_sanitizers.py','dev/toolchains/p2996_sanitizer_repair.py').replace('p2996-sanitizers-native-launch-','p2996-sanitizer-repair-native-launch-')
static=j(E/'frozen-static.json');assert [x['returncode'] for x in static['commands']]==[0,0] and json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
post=j(E/'failure-postcommit.json');assert post['head']==HEAD and all(x['returncode']==0 for x in post['commands']) and post['commands'][-1]['stdout']==''
scan=j(E/'pre-review-secret-scan.json');assert len(scan['files'])==44 and scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and len(scan['dispositions'])==5 and scan['supplemental_complete_token_files']==[]
for p,h in scan['files'].items():assert sha(p)==h,(p,'scan binding')
for row in scan['dispositions']:assert sha(row['path'])==row['sha256'] and row['reason']=='Verified exact file-content digest'
# The only binary reads in this review: exactly the 127 newly assigned object preimages, once each.
object_receipt=[]
for p,row in recipe['objects'].items():
 path=Path(p);meta=path.lstat();assert stat.S_ISREG(meta.st_mode) and meta.st_size==row['bytes'] and meta.st_size>0
 with path.open('rb') as stream:h=hashlib.file_digest(stream,'sha256').hexdigest()
 assert h==row['sha256'];object_receipt.append({'path':p,**row})
for p,h in watched.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,(p,'changed during comparison')
result={'result':'PASS: preparation only','findings':[],'candidate_sha256':F,'helper_sha256':H,'contract_sha256':C,'source_review_sha256':sha(E/'source-review.json'),'candidate_snapshots':7,'preparation_copy_pairs':25,'source_review_copy_pairs':1,'prepared_launcher_copy_pairs':2,'patch_control_recorded_returncodes':[1,0,0,1,0,0],'object_dependency_bindings':195,'reused_functions_ast_equal':['save','run','interrupted'],'guard_delta':'only the two statements binding retained recipe object bytes','projected_private_variants':projected,'recorded_baseline_original_hashes':19,'recorded_static_returncodes':[0,0],'scan_file_bindings_verified':44,'recorded_scan_dispositions':5,'native_execution':'UNVERIFIED; preparation and source review only','object_preimages_hashed_once':object_receipt,'object_preimage_total_bytes':sum(row['bytes'] for row in object_receipt),'watched_text_sha256':watched}
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['projected_private_variants','object_preimages_hashed_once','watched_text_sha256']}))

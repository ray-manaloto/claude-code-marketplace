import hashlib,itertools,json,re
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/baseline-presets';D=Path(__file__).parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HB=lambda b:hashlib.sha256(b).hexdigest()
J=lambda p:json.loads(Path(p).read_bytes())
can=J(E/'candidate.json'); generated=(R/'CMakePresets.json').read_bytes(); data=json.loads(generated); template=J(R/'CMakePresetsVendorTemplate.json'); gen=J(E/'generation.json'); pre=J(E/'tcpm-prerequisite.json')
assert H(E/'candidate.json')=='fac2765a920f32d642d0edb8a1c8c1b5b6b61cba237ebe51baebee7288c97ce7' and HB(generated)=='e304882b21be2dc25a6b024dd6a6eadcb240e0b3fcd4eeb87041dfaf9ee043eb'
g=Path((R/'.git').read_text().strip().removeprefix('gitdir: '));common=(g/(g/'commondir').read_text().strip()).resolve();ref=(g/'HEAD').read_text().strip().removeprefix('ref: ');head=(common/ref).read_text().strip()
assert head==can['head']==pre['identity']['observed_start_head']=='e81ba5db9621c36334d10a1c6e4ce5cad63ba79c' and ref=='refs/heads/codex/marketplace-native-onboarding' and str(common)=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'
assert len(can['files'])==5 and can['generated_files']=={'CMakePresets.json':HB(generated)}
assert all(H(R/p)==s for p,s in (can['files']|can['generated_files']).items())
scan=J(E/'pre-review-secret-scan.json');assert scan['raw']['returncode']==0 and not scan['supplemental_complete_token_files'] and len(scan['files'])==13
assert all(H(R/p)==s for p,s in scan['files'].items())
script=Path(J(E/'generation-launch.json')['script']);assert script.parent==Path(gen['directory']) and script.read_bytes()==(E/'generation-check.py.source').read_bytes() and H(script)==gen['inputs'][str(script)]
assert gen['inputs'][str(R/'CMakePresetsVendorTemplate.json')]==can['files']['CMakePresetsVendorTemplate.json']
rows={r['case']:r for r in gen['commands']};assert list(rows)==['head','generation-1','generation-2','native-list-configure','native-list-build','native-list-test','native-list-workflow']
assert all(r['returncode']==0 and r['stderr']=='' and 0<=r['seconds']<60 for r in rows.values()) and rows['head']['stdout'].strip()==head
assert gen['state'].startswith('PASS') and gen['two_generations_identical'] and not gen['compiler_or_configure_or_build_executed']
assert gen['generated_sha256']==HB(generated) and gen['configure_trees']==8 and gen['configuration_cells']==32
source_pairs=[]
for i in (1,2):
 row=rows['generation-'+str(i)];target=Path(gen['directory'])/('generation-'+str(i))/'CMakePresets.json'
 assert row['stdout'].encode('utf-8')==generated==target.read_bytes()
 assert row['argv']==[pre['qualified_reuse']['tcpm'],'--non-interactive','--no-schema-validation','--presets-version','12','--template-file',str(R/'CMakePresetsVendorTemplate.json'),'--presets-file',str(target),'--stdout']
 source_pairs.append({'path':str(target),'sha256':HB(generated),'bytes':len(generated)})
assert template['version']==data['version']==12 and template['cmakeMinimumRequired']==data['cmakeMinimumRequired']=={'major':4,'minor':4,'patch':4}
normalized_vendor=json.loads(json.dumps(template['vendor']))
for group,axes_to_default in {'build':('compiler','core','dependency'),'test':('compiler','core','dependency'),'workflow':('core','dependency')}.items():
 for axis in axes_to_default:normalized_vendor['tcpm']['preset-groups'][group]['shape'][axis]={}
assert normalized_vendor==data['vendor']
assert data['configurePresets'][:3]==template['configurePresets']
configurations=['Debug','Release','RelWithDebInfo','MinSizeRel'];assert gen['configurations']==configurations
axes=list(itertools.product(('p2996','gcc16'),('static','shared'),('static','dynamic')))
presets={p['name']:p for p in data['configurePresets']};assert len(presets)==len(data['configurePresets'])==17 and sum(bool(p.get('hidden')) for p in presets.values())==9
visible={k for k,p in presets.items() if not p.get('hidden')};tail=lambda lane,core,dep:lane+'-core-'+core+'-fmt-'+dep
assert visible=={'configure-'+tail(*a) for a in axes}
def resolve(name,seen=()):
 assert name not in seen
 p=presets[name]; result={};parents=p.get('inherits',[]);assert isinstance(parents,list)
 for parent in reversed(parents):
  for key,val in resolve(parent,seen+(name,)).items():
   if key in ('environment','cacheVariables'):result.setdefault(key,{}).update(val)
   else:result[key]=val
 for key,val in p.items():
  if key in ('name','hidden','inherits'):continue
  if key in ('environment','cacheVariables'):result.setdefault(key,{}).update(val)
  else:result[key]=val
 return result
prefixes={'p2996':'/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-configure-20261011T051205Z/prefix','gcc16':'/opt/homebrew/Cellar/gcc/16.2.0'}
retained='/Users/rmanaloto/.local/state/marketplace-tool-foundation/vcpkg-fmt-retry-20261011T213606Z';expanded=[];build_paths=[];install_paths=[]
for lane,core,dep in axes:
 name='configure-'+tail(lane,core,dep);p=resolve(name);env=p['environment'];cache=p['cacheVariables'];other='gcc16' if lane=='p2996' else 'p2996'
 assert env=={'CC':None,'CXX':None,'MARKETPLACE_CPP_LANE':lane,'MARKETPLACE_'+lane.upper()+'_PREFIX':prefixes[lane],'MARKETPLACE_'+other.upper()+'_PREFIX':None,'MARKETPLACE_DEPENDENCY_LINKAGE':dep}
 assert cache['BUILD_SHARED_LIBS']==('ON' if core=='shared' else 'OFF') and cache['RESEARCH_CORE_WITH_FMT']=='ON' and p['generator']=='Ninja Multi-Config'
 for k in ('VCPKG_MANIFEST_MODE','VCPKG_MANIFEST_INSTALL','VCPKG_APPLOCAL_DEPS','CMAKE_FIND_USE_PACKAGE_REGISTRY','CMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY'):assert cache[k]=='OFF'
 assert cache['CMAKE_CONFIGURATION_TYPES']==';'.join(configurations) and cache['CMAKE_CXX_STANDARD']=='26' and cache['CMAKE_CXX_STANDARD_REQUIRED']=='ON' and cache['CMAKE_CXX_EXTENSIONS']=='OFF'
 def expand(s):
  merged=env|{'MARKETPLACE_BUILD_ROOT':str(D/'builds')}
  s=re.sub(r'\$env\{([^}]+)\}',lambda m:merged[m[1]] or '',s).replace('${sourceDir}',str(R)).replace('${presetName}',name)
  assert not any(marker in s for marker in ('$env{','${','{pq}','{parameter}','{name}','{prefix}'))
  return s
 triplet=expand(cache['VCPKG_TARGET_TRIPLET']);installed=expand(cache['VCPKG_INSTALLED_DIR']);assert triplet=='arm64-osx-'+lane+'-'+dep and installed==retained+'/'+triplet+'/installed'
 assert expand(cache['CMAKE_TOOLCHAIN_FILE'])==retained+'/vcpkg/scripts/buildsystems/vcpkg.cmake' and expand(cache['VCPKG_CHAINLOAD_TOOLCHAIN_FILE'])==str(R/'cmake/toolchains/vcpkg-macos-arm64.cmake') and expand(cache['VCPKG_OVERLAY_TRIPLETS'])==str(R/'triplets')
 assert p['binaryDir']=='$env{MARKETPLACE_BUILD_ROOT}/${presetName}' and p['installDir']=='$env{MARKETPLACE_BUILD_ROOT}/install/${presetName}'
 build_paths.append(expand(p['binaryDir']));install_paths.append(expand(p['installDir']))
 expanded.append({'name':name,'compiler':lane,'core_linkage':core,'dependency_linkage':dep,'triplet':triplet,'installed':installed,'environment':env})
assert len(set(build_paths+install_paths))==16 and expanded==gen['expanded_presets']
for kind in ('build','test'):
 ps=data[kind+'Presets'];assert len(ps)==32 and len({p['name'] for p in ps})==32
 expect={kind+'-'+conf+'-'+tail(*a) for conf in configurations for a in axes};assert {p['name'] for p in ps}==expect
 for p in ps:
  conf=p['configuration'];assert conf in configurations and p['configurePreset'] in visible and p['name']==kind+'-'+conf+'-'+p['configurePreset'].removeprefix('configure-')
  assert p.get('inheritConfigureEnvironment',True) is True and 'environment' not in p
  assert p['jobs']==1 if kind=='build' else p['execution']=={'jobs':1,'noTestsAction':'error'} and p['output']=={'outputOnFailure':True}
ws=data['workflowPresets'];assert len(ws)==8 and {w['name'] for w in ws}=={'workflow-'+tail(*a) for a in axes}
for w in ws:
 tail_value=w['name'].removeprefix('workflow-');expected=[{'type':'configure','name':'configure-'+tail_value}]
 for conf in configurations:expected += [{'type':kind,'name':kind+'-'+conf+'-'+tail_value} for kind in ('build','test')]
 assert w['steps']==expected
for kind in ('configure','build','test','workflow'):
 row=rows['native-list-'+kind];listed=re.findall(r'^  "([^"]+)"$',row['stdout'],re.M); expected=[p['name'] for p in data[kind+'Presets'] if not p.get('hidden')]
 assert listed==expected and len(listed)==len(set(listed))
 assert row['argv'][1:]==['-S',str(Path(gen['directory'])/'generation-1'),'--list-presets='+kind]
 assert row['argv'][0] in gen['inputs']
# Preserve the known pre-unit root and smoke bytes by reversing only the new opt-in additions.
root=(R/'CMakeLists.txt').read_text().splitlines(keepends=True);old_root=''.join(root[:31]+root[41:50]+root[55:]);assert HB(old_root.encode())=='c60bbd195b5338dc608af2d2b9a05f7da404374cf9a4625b3598bdca70b4430e'
smoke=(R/'src/smoke.cpp').read_text().splitlines(keepends=True);old_smoke=''.join(smoke[:2]+[smoke[6]]+smoke[8:19]+smoke[23:25]+smoke[26:]);assert HB(old_smoke.encode())=='2b229655f362f18015c9563ce575efc050c100d501f403a01d9659a885fa411a'
static=J(E/'pre-review-static.json');assert [r['returncode'] for r in static['commands']]==[0,0] and json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
trusted=J(E/'consumer-postcommit.json');assert trusted['commands'][-3]['stdout'].strip()==head
watched={str(R/p):s for p,s in scan['files'].items()};watched[str(E/'pre-review-secret-scan.json')]=H(E/'pre-review-secret-scan.json')
assert all(H(Path(p))==s for p,s in watched.items())
report={'result':'PASS','identity':{'checkout':str(R),'branch':ref.removeprefix('refs/heads/'),'head':head,'common_git_directory':str(common)},'candidate_sha256':H(E/'candidate.json'),'generated_sha256':HB(generated),'template_sha256':can['files']['CMakePresetsVendorTemplate.json'],'generation_sha256':H(E/'generation.json'),'generation_script_source_sha256':H(E/'generation-check.py.source'),'verified_maintained_files':5,'verified_scan_file_bindings':13,'exact_generated_byte_count':len(generated),'generation_command_returncodes':[r['returncode'] for r in rows.values()],'generator_outputs_match_generated_file':2,'generator_source_pairs':source_pairs,'configure_visible':8,'configure_hidden':9,'build_presets':32,'test_presets':32,'workflow_presets':8,'steps_per_workflow':9,'all_macro_paths_distinct':True,'expanded_configure_presets':expanded,'prior_root_and_smoke_preimages_preserved':True,'parent_static_returncodes':[0,0],'parent_baseline_original_hashes_reported':19,'parent_secret_scan_returncode':0,'parent_full_token_hits':0,'native_build_acceptance':'UNVERIFIED; Task 13b pending','reviewer_native_checks':0,'watched_hashes':watched,'maintained_writes':0,'shared_writes':0}
(D/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('watched_hashes','expanded_configure_presets')}))

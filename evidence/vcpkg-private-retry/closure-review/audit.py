import ast, datetime, hashlib, json, os, re, stat
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace'); E=R/'evidence/vcpkg-private-retry'; D=Path(__file__).parent
OP=Path('/Users/rmanaloto/.local/state/marketplace-tool-foundation/vcpkg-private-retry-20261011T191404Z'); OUT=OP.parent/(OP.name+'-outside-control')
H='f61f9035f88e2d5f4b943ed386d2ed404cae6897'; HS='7e1d7cae675be05b70e96c429e38240125be8e9cd88c2ffe007664a10921b60a'; CS='1099e0df49d3a6e022f76297424b0456365333700c086d1d0d7a1905f03bfda5'; KS='1800281a0e2424747240f9bb0f51b9f4d22f874e7aa20619de1eabff406828a1'; QS='9b3482e5b6f9d6d4338943d169819d183739de5647778b7d487f26574c1777c9'; NS='b10cd9834e568b5a236f24ea4337fc8fc4b3a459b14175a67d918c8f1e493e0a'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
def save(n,d): (D/n).write_text(json.dumps(d,indent=2)+'\n')
def record(p):
 p=Path(p); return {'sha256':sha(p),'bytes':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
# Read-only artifact inspection. Candidate modules are never imported/executed.
helper=R/'dev/toolchains/vcpkg_private.py'; candidate=load(E/'closure-candidate.json'); contract=load(E/'contract.json'); native=load(E/'native-execution.json'); q=load(E/'operation/qualification.json'); admission=load(E/'admission.json'); prior=load(E/'pre-run-review.json'); ref=load(E/'source-inventory-reference.json')
assert (sha(helper),sha(E/'contract.json'),sha(E/'closure-candidate.json'),sha(E/'operation/qualification.json'),sha(E/'native-execution.json'))==(HS,CS,KS,QS,NS)
gitdir=Path((R/'.git').read_text().strip().removeprefix('gitdir: ')); common=(gitdir/(gitdir/'commondir').read_text().strip()).resolve(); gitref=(gitdir/'HEAD').read_text().strip()
assert str(common)=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git' and gitref=='ref: refs/heads/codex/marketplace-native-onboarding'
assert (common/gitref.removeprefix('ref: ')).read_text().strip()==H
assert candidate['head']==admission['base_head']==contract['base_head']==H
assert candidate['contract_sha256']==CS and candidate['native_execution_sha256']==NS and len(candidate['files'])==4
for p,h in candidate['files'].items(): assert sha(R/p)==h,p
for p,h in contract['inputs'].items(): assert sha(R/p)==h,p
assert len(contract['inputs'])==45
priorpath=Path('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-vcpkg-retry-review-zgq44kja/review.json')
assert (E/'pre-run-review.json').read_bytes()==priorpath.read_bytes()
assert prior['result']=='PASS' and not prior['findings']
assert prior['helper_sha256']==native['helper_sha256']==q['helper_sha256']==admission['helper_sha256']==HS
assert prior['contract_sha256']==native['contract_sha256']==admission['contract_sha256']==CS
assert prior['candidate_sha256']==admission['candidate_sha256']==sha(E/'candidate.json')=='75e54fc51d62c68c9147c50c21f0c9eaa33ebe6805e3a4b61eaa3c904f5ec7b1'
assert admission['review_sha256']==native['pre_run_review_sha256']==sha(E/'pre-run-review.json')=='3053dab5abbd56157518b61eb548d99b92d2f2705f0695bc72e37776b71531ce'
assert q['admission_sha256']==native['admission_sha256']==sha(E/'admission.json') and admission['run_directory']==str(OP)
assert native['qualification_sha256']==QS and native['argv']==['/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3','-B','dev/toolchains/vcpkg_private.py','--run-dir',str(OP)]
assert native['returncode']==0 and native['commands']==24 and q['state']=='PASS: private copies, managed host-tool selection and kernel write/network controls'
assert q['protected_state_unchanged'] is native['protected_state_unchanged'] is True and q['lease_released'] is native['lease_released'] is True
# Freeze reviewed inputs and all explicit copied artifacts, never source trees.
copy_counts={}; paths={helper,E/'contract.json',E/'candidate.json',E/'closure-candidate.json',E/'native-execution.json',E/'admission.json',E/'pre-run-review.json',E/'source-inventory-reference.json',E/'capacity/capacity.json',R/'evidence/onboarding/baseline-files.json'}
paths.update(R/p for p in candidate['files']); paths.update(R/p for p in contract['inputs'])
for name,count in [('operation-copy-manifest.json',52),('review-copy-manifest.json',10),('source-copy-manifest.json',1)]:
 rows=load(E/name)['files']; assert len(rows)==count
 assert len({row['copy'] for row in rows})==count
 for row in rows:
  source=Path(row['source']); copied=R/row['copy']; assert sha(source)==row['sha256'] and source.read_bytes()==copied.read_bytes(),row
  paths.update([source,copied])
 copy_counts[name]=count; paths.add(E/name)
watch={str(p):record(p) for p in sorted(paths)}; save('frozen-inputs.json',watch)
commands=q['commands']; assert len(commands)==24 and len({c['case'] for c in commands})==24
bycase={c['case']:c for c in commands}; expected_codes={k:(73 if k in ['outside-write','symlink-write','network-denied'] else 0) for k in bycase}
assert sum(code==0 for code in expected_codes.values())==21
assert native['outcomes']==[{'case':c['case'],'returncode':c['returncode'],'expected':c['expected_returncode']} for c in commands]
logpaths=set()
for c in commands:
 assert c['returncode']==c['expected_returncode']==expected_codes[c['case']]
 expected_timeout=15 if c['case'] in ['docker-context','docker-census'] else 20 if c['case']=='docker-stats' else 60
 assert c['timeout_seconds']==expected_timeout and 0<=c['elapsed_seconds']<expected_timeout
 assert len(c['logs'])==2
 for log,suffix in zip(c['logs'],['stdout','stderr']):
  p=Path(log['path']); assert p==OP/(c['case']+'.'+suffix)
  assert sha(p)==log['sha256'] and p.read_bytes()==(E/'operation'/p.name).read_bytes()
  logpaths.add(str(p))
  if suffix=='stderr': assert p.read_bytes()==b'',c['case']
assert len(logpaths)==48
# Exact native argv reconstruction from inspected source literals and receipt-bound paths.
parsed=ast.parse(helper.read_text()); main=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='main')
constants={t.id:n.value.value for n in ast.walk(main) if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) for t in n.targets if isinstance(t,ast.Name)}
positive=constants['positive']; negative=constants['negative']
assert "sys.exit(73)" in negative and "errno.EPERM,errno.EACCES" in negative and "('127.0.0.1',9)" in negative
normal=load(R/'evidence/gcc-bootstrap/install-preimages.json')['normal_environment']['argv']
python=native['argv'][0]; sb=['/usr/bin/sandbox-exec','-f',str(OP/'private.sb')]; docker='/Applications/Docker.app/Contents/Resources/bin/docker'
expected={
 'project-head':['/usr/bin/git','-C',str(R),'rev-parse','HEAD'],
 'default-before':normal,
 'capacity-processes':['/bin/ps','-axo','pid=,pcpu=,comm='],
 'docker-context':[docker,'context','show'],
 'docker-census':[docker,'ps','--format','{{.ID}}\t{{.Image}}'],
 'docker-stats':[docker,'stats','--no-stream','--format','{{json .}}'],
 'private-write':sb+[python,'-B','-c',positive,str(OP/'allowed')],
 'outside-write':sb+[python,'-B','-c',negative,'write',str(OUT/'sentinel')],
 'symlink-write':sb+[python,'-B','-c',negative,'write',str(OP/'escape/new')],
 'network-denied':sb+[python,'-B','-c',negative,'network'],
 'copied-vcpkg-identity':sb+['/usr/bin/git','-C',str(OP/'vcpkg'),'rev-parse','HEAD','HEAD^{tree}']}
private={'VCPKG_ROOT':str(OP/'vcpkg'),'VCPKG_DOWNLOADS':str(OP/'downloads'),'X_VCPKG_REGISTRIES_CACHE':str(OP/'registries'),'XDG_CACHE_HOME':str(OP/'cache'),'TMPDIR':str(OP/'tmp'),'VCPKG_FORCE_SYSTEM_BINARIES':'1','VCPKG_DISABLE_METRICS':'1'}
absent=['VCPKG_FORCE_DOWNLOADED_BINARIES','VCPKG_BINARY_SOURCES','VCPKG_DEFAULT_BINARY_CACHE']
probe="import json,os,shutil;print(json.dumps({'home':os.environ.get('HOME'),'tools':{n:shutil.which(n) for n in ['cmake','ninja']},'private':{n:os.environ.get(n) for n in "+repr(list(private)+absent)+"}}))"
vargs=[str(OP/'vcpkg/vcpkg'),'--disable-metrics','--feature-flags=-binarycaching','--vcpkg-root='+str(OP/'vcpkg'),'--downloads-root='+str(OP/'downloads'),'--x-buildtrees-root='+str(OP/'buildtrees'),'--x-packages-root='+str(OP/'packages'),'--x-install-root='+str(OP/'installed'),'--x-manifest-root='+str(OP/'manifest')]
for lane in ['p2996','gcc16']:
 base=[normal[0],'--no-hooks','-C',str(OP/'cwd'),'-E',lane,'exec','--fresh-env','--no-deps','--']
 expected[lane+'-profile']=base+normal[-2:]
 expected[lane+'-selection']=base+sb+[python,'-B','-c',probe]
 for tool in ['cmake','ninja']:
  expected[lane+'-fetch-'+tool]=base+sb+vargs+['fetch',tool,'--x-stderr-status']
  expected[lane+'-version-'+tool]=base+sb+[contract['managed_tools'][tool]['path'],'--version']
expected['default-after']=normal
assert list(bycase)==list(expected)
for label,argv in expected.items(): assert bycase[label]['argv']==argv,label
# Inspect actual results of the recorded controls and native selections.
def stdout(label): return (OP/(label+'.stdout')).read_text()
assert stdout('project-head').strip()==H
assert stdout('default-before')==stdout('default-after')==(R/contract['default_profile']).read_text()
assert stdout('copied-vcpkg-identity').splitlines()==[contract['vcpkg_commit'],contract['vcpkg_tree']]
for label in ['outside-write','symlink-write','network-denied']: assert stdout(label)=='DENIED:1\n'
assert stdout('private-write')=='' and (OP/'allowed').read_bytes()==b'private\n'
assert q['confinement']['outside_control']==str(OUT) and (OUT/'sentinel').read_bytes()==b'preserve\n'
assert not (OUT/'new').exists() and not (OUT/'new').is_symlink()
assert (OP/'escape').is_symlink() and os.readlink(OP/'escape')==str(OUT)
expected_policy='(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(OP))+') (literal "/dev/null"))\n(deny network*)\n'
assert (OP/'private.sb').read_text()==expected_policy and sha(OP/'private.sb')==q['confinement']['profile_sha256']
assert q['confinement']['allowed_inherited_fds']==[0,1,2,3] and q['confinement']['home_unchanged_in_environment'] is True
selections={}
for lane,p in contract['profiles'].items():
 assert stdout(lane+'-profile')==(R/p).read_text()
 selection=json.loads(stdout(lane+'-selection')); assert selection=={'home':'/Users/rmanaloto','tools':{k:v['path'] for k,v in contract['managed_tools'].items()},'private':private|dict.fromkeys(absent)}
 for tool,t in contract['managed_tools'].items():
  assert stdout(lane+'-fetch-'+tool)==t['path']+'\n'
  lines=stdout(lane+'-version-'+tool).splitlines(); assert lines[0]==('cmake version '+t['version'] if tool=='cmake' else t['version'])
 selections[lane]=selection
# Retained source inventory comparison only; never walk either source checkout.
assert ref['operation_source']==str(OP/'source-before.json') and ref['retained_inventory']==contract['source_inventory']
assert sha(OP/'source-before.json')==ref['operation_sha256']==sha(R/ref['retained_inventory'])==ref['retained_inventory_sha256']==contract['inputs'][contract['source_inventory']]
source_rows=load(OP/'source-before.json'); retained_rows=load(R/ref['retained_inventory']); assert source_rows==retained_rows and len(source_rows)==ref['records']==17644 and ref['identical_parsed_records'] is True
assert (OP/'source-before.json').read_bytes()==(R/ref['retained_inventory']).read_bytes()
# The three small private final files are checked directly, without inventories.
assert set(q['private_final'])=={'downloads','buildtrees','packages','installed','registries','cache','tmp','manifest'}
private_files=0
for name,rows in q['private_final'].items():
 if not rows: assert list((OP/name).iterdir())==[]
 else:
  assert {p.name for p in (OP/name).iterdir()}=={row['path'] for row in rows}
  for row in rows:
   p=OP/name/row['path']; assert row['kind']=='file' and not p.is_symlink()
   assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'] and oct(stat.S_IMODE(p.stat().st_mode))==row['mode']
   private_files+=1
assert private_files==3
for row in contract['downloads']: assert hashlib.sha512((OP/'downloads'/row['filename']).read_bytes()).hexdigest()==row['sha512']
assert (OP/'manifest/vcpkg.json').read_bytes()==(R/'vcpkg.json').read_bytes()
# Capacity and lease are historical observations, not live status.
capacity=load(E/'capacity/capacity.json'); assert sha(E/'capacity/capacity.json')==admission['capacity_sha256'] and capacity['state']=='PASS'
assert capacity['docker_context']==admission['docker_context']==stdout('docker-context').strip()
assert capacity['containers']==admission['containers']==stdout('docker-census').splitlines()
assert not capacity['active_build_processes'] and all(c['returncode']==0 for c in capacity['commands'])
cap=q['capacity']; process_lines=stdout('capacity-processes').splitlines()
active=[line for line in process_lines if re.fullmatch(r'(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy|include-what-you-use|vcpkg',Path(line.split(maxsplit=2)[-1]).name)]
assert active==cap['active']==[] and abs(sum(float(line.split()[1]) for line in process_lines)-cap['total_cpu_percent'])<0.000001
assert cap['free_bytes']>=contract['disk_reserve_bytes'] and cap['load'][0]<=2*cap['cpus'] and cap['total_cpu_percent']<=75*cap['cpus']
container_cpu=sum(float(json.loads(line)['CPUPerc'].rstrip('%')) for line in stdout('docker-stats').splitlines())
assert container_cpu==cap['container_cpu_percent'] and container_cpu<=50*cap['cpus']
for side in ['before','after']:
 census=q['writer_census_'+side]; assert census['lock_holders']==[] and census['lock_holder_check_rc']==1
 assert {p['known_task'] for p in census['processes']}=={'mcp:graphify','mcp:cbm','mcp:lab-results'}
assert datetime.datetime.fromisoformat(capacity['recorded_at'])<datetime.datetime.fromisoformat(admission['recorded_at'])<datetime.datetime.fromisoformat(commands[0]['started_at'])
assert datetime.datetime.fromisoformat(q['writer_census_before']['at'])<datetime.datetime.fromisoformat(commands[0]['started_at'])
assert datetime.datetime.fromisoformat(q['writer_census_after']['at'])>datetime.datetime.fromisoformat(commands[-1]['started_at'])
# Historical failure remains independently retained; Claude acceptance files unchanged.
oldnative=load(R/'evidence/vcpkg-private/native-execution.json'); oldq=load(R/'evidence/vcpkg-private/native-hold/qualification.json')
assert oldnative['returncode']==1 and oldnative['commands_started']==0 and oldq['state']=='FAIL' and oldq['commands']==[] and sha(R/'evidence/vcpkg-private/native-hold/qualification.json')==oldnative['qualification_sha256']
baseline=load(R/'evidence/onboarding/baseline-files.json')['files']; assert len(baseline)==19
for row in baseline: assert sha(R/row['path'])==row['sha256'] and (R/row['path']).stat().st_size==row['bytes']
for p,v in watch.items(): assert record(p)==v,p
result={'result':'PASS','kind':'Filesystem-only closure audit; no candidate code, native commands or full source/shared inventories executed','head':H,'contract_input_hashes':45,'closure_candidate_files':4,'copy_counts':copy_counts,'actual_command_argv_matches':24,'actual_command_log_files':48,'actual_native_wrapper_rc':0,'actual_command_rc0':21,'actual_expected_rc73':3,'all_stderr_empty':True,'sandbox_policy_exact':True,'private_allowed_file_preserved':True,'outside_sentinel_preserved':True,'symlink_escape_target_exact':True,'escaped_file_absent':True,'managed_tool_paths_and_versions_each_lane':True,'profiles_equal_bound_receipts':True,'default_restored_byte_for_byte':True,'home_preserved':True,'source_inventory_reference_records':17644,'source_inventory_reference_byte_and_parsed_equality':True,'source_inventory_recomputed':False,'private_final_files_checked':3,'recorded_capacity_reconciled_with_logs':True,'guard_before_and_precopy_success_inferred_from_helper_order':True,'final_guard_source_preservation_recorded_PASS':True,'lease_release_recorded_after_context_exit':True,'current_shared_state_reattested':False,'historical_failed_attempt_preserved':True,'original_Claude_hashes_and_sizes':19,'frozen_files_stable':len(watch),'shared_mutations':0}
save('audit.json',result); print(json.dumps(result))

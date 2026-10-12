from pathlib import Path
import collections, datetime, hashlib, json, os, re, stat, struct, subprocess, sys, time, uuid
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-tsan-repair'
OUT=Path(__file__).parent
HEAD='b90a5d5703d538fd146de87d0656132bc820044b'
EXPECTED_CANDIDATE='25e61bbbb3f26a6ad99dbac451b5935515a1b77c20bfe3944583ac3a9bf6a602'
EXPECTED_INPUTS='be6d74d879c137a816dba6f0705ac505f5db0425abbb3be3e29184433cc03c07'
EXPECTED_PREVIEW='b95e96d31769501bf3152791b21aa87c8f896afaa6365c257efe4313622d2d2c'
PY='/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3'
watched={}; cache={}; checks={}; artifact_reads=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def stamp(s): return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def data(path,expected=None):
 p=Path(path); p=p if p.is_absolute() else ROOT/p; key=str(p)
 if key not in cache:
  a=p.lstat(); assert stat.S_ISREG(a.st_mode) and a.st_size<4000000, key
  b=p.read_bytes(); assert stamp(a)==stamp(p.lstat()),key
  b.decode('utf-8'); cache[key]=b; watched[key]=sha(b)
 if expected is not None: assert watched[key]==expected,('sha',key,watched[key],expected)
 return cache[key]
def obj(path,expected=None): return json.loads(data(path,expected))
def utc(s): return datetime.datetime.fromisoformat(s)
def eq(a,b,label): assert a==b,(label,a,b)
def log(row,stream):
 wanted=[v for v in row['logs'] if v['path'].endswith('.'+stream)]
 assert len(wanted)==1,(row['case'],stream)
 return data(wanted[0]['path'],wanted[0]['sha256'])
cc=obj(E/'closure-candidate.json',EXPECTED_CANDIDATE)
ci=obj(E/'closure-inputs.json',EXPECTED_INPUTS)
eq(cc['base_head'],HEAD,'candidate HEAD');eq(cc['closure_inputs_sha256'],EXPECTED_INPUTS,'inputs link')
eq(cc['maintained'],ci['maintained'],'maintained snapshot')
eq(len(ci['maintained']),4,'maintained count');eq(len(ci['evidence']),36,'evidence count')
for p,h in (ci['maintained']|ci['evidence']).items(): data(p,h)
checks['frozen_files']={'maintained':4,'evidence':36,'candidate_sha256':EXPECTED_CANDIDATE,'inputs_sha256':EXPECTED_INPUTS}
contract=obj(E/'contract.json');recipe=obj(E/'recipes.json');helper=ROOT/'dev/toolchains/p2996_tsan_repair.py'
helper_sha=watched[str(helper)]
eq(helper_sha,'d8804ea18549fb8668d527c13666f878947524cc10f9e1ba22743e19dbc8900d','prepared helper unchanged')
eq(contract['base_head'],HEAD,'contract head');eq(contract['recipe_sha256'],watched[str(E/'recipes.json')],'recipe link')
preview=obj(E/'pre-run-review.json',EXPECTED_PREVIEW)
ps=obj(E/'preparation-review/supporting-manifest.json')
eq(ps['review_sha256'],EXPECTED_PREVIEW,'review manifest')
prior=Path(ps['review_path']).parent
for name in ['review.json','supporting-manifest.json','compare.py','comparison.json','execution.json']:
 eq(data(prior/name),data(E/'preparation-review'/name),'preparation copy '+name)
eq(data(prior/'review.json'),data(E/'pre-run-review.json'),'pre-run exact preview')
for r in ps['files']: data(r['path'],r['sha256']);eq(len(data(r['path'])),r['bytes'],'preview bytes')
pr=obj(E/'preparation-review/comparison.json');assert pr['result'].startswith('PASS:'),'preparation result'
peq=obj(E/'preparation-review/execution.json');eq(peq['returncode'],0,'preparation rc')
checks['preparation_reuse']={'sha256':EXPECTED_PREVIEW,'six_copy_pairs':True,'same_helper_contract_recipe':True,'rehash_inherited_guards':False,'rehash_link_objects':False}
prepared=obj(E/'prepared-launchers.json')
for r in prepared['launchers'].values():eq(data(r['private'],r['sha256']),data(r['repository'],r['sha256']),'prepared launcher bytes')
admit=obj(E/'admission.json');native=obj(E/'native-execution.json');launch=obj(E/'native-launch.json')
OP=Path(admit['run_directory']);LP=Path(native['private_launch_directory']);SB=['/usr/bin/sandbox-exec','-f',str(OP/'private.sb')]
eq(native['returncode'],0,'native rc');assert 0<native['elapsed_seconds']<120
expected_argv=[PY,'-E','-B',str(helper),'--run-dir',str(OP),'--build']
eq(native['argv'],expected_argv,'native argv');eq(launch['argv'],expected_argv,'launch argv')
for k,v in launch.items(): eq(native[k],v,'launch identity '+k)
for r in [admit,launch,native]:eq(r['helper_sha256'],helper_sha,'helper binding')
eq(admit['contract_sha256'],watched[str(E/'contract.json')],'admission contract')
eq(admit['candidate_sha256'],watched[str(E/'candidate.json')],'preparation candidate')
eq(admit['review_sha256'],EXPECTED_PREVIEW,'admission preview')
eq(native['admission_sha256'],watched[str(E/'admission.json')],'execution admission')
eq(native['dispatch_sha256'],prepared['launchers']['dispatch']['sha256'],'dispatch binding')
cap=obj(E/'capacity/capacity.json',admit['capacity_sha256']);cape=obj(E/'capacity/execution.json',admit['capacity_execution_sha256'])
CP=Path(cape['argv'][-1]);eq(data(CP/'capacity.json'),data(E/'capacity/capacity.json'),'capacity private copy')
eq(cape['argv'],[PY,'-E','-B',prepared['launchers']['capacity']['private'],str(CP)],'capacity argv')
eq(cape['returncode'],0,'capacity rc');assert 0<cape['elapsed_seconds']<60;eq(cape['stderr'],'','capacity stderr')
eq(json.loads(cape['stdout']),{'state':'PASS','receipt':str(CP/'capacity.json')},'capacity output')
eq(cape['candidate_sha256'],admit['candidate_sha256'],'capacity candidate');eq(cape['review_sha256'],EXPECTED_PREVIEW,'capacity preview')
eq(cap['script_sha256'],prepared['launchers']['capacity']['sha256'],'capacity source')
eq(cap['state'],'PASS','capacity state');eq(cap['held_lease'],False,'precheck no lease');eq(cap['native_operation_started'],False,'precheck no native')
assert utc(cap['recorded_at'])<utc(admit['admitted_at'])<utc(native['started_at'])<utc(native['finished_at'])
caprows={r['case']:r for r in cap['commands']};eq(len(caprows),7,'capacity command count')
for r in cap['commands']:
 eq(r['returncode'],0,'capacity '+r['case']);assert 0<=r['elapsed_seconds']<r['timeout_seconds'];eq(len(r['logs']),2,'capacity logs');log(r,'stdout');eq(log(r,'stderr'),b'','capacity stderr '+r['case'])
q=obj(E/'operation/qualification.json',cc['qualification_sha256'])
eq(data(OP/'qualification.json'),data(E/'operation/qualification.json'),'qualification current private copy')
eq(q['helper_sha256'],helper_sha,'qualification helper');eq(q['admission_sha256'],watched[str(E/'admission.json')],'qualification admission')
assert q['state'].startswith('PASS:')
eq(q['lease_released'],True,'helper released receipt');eq(q['protected_state_unchanged'],True,'helper protected receipt')
rows={r['case']:r for r in q['commands']};eq(len(rows),36,'unique commands')
expected={'original-clean':-11,'tsan-clean':0,'tsan-race':86,'tsan-ubsan-clean':0,'tsan-ubsan-race':86,'tsan-ubsan-overflow':86}
eq(cc['expected_cases'],expected,'candidate cases')
for r in q['commands']:
 eq(r['returncode'],expected.get(r['case'],0),'native rc '+r['case']);eq(r['expected_returncode'],r['returncode'],'expected rc '+r['case'])
 assert 0<=r['elapsed_seconds']<r['timeout_seconds'];assert utc(native['started_at'])<=utc(r['started_at'])<=utc(native['finished_at'])
 eq(len(r['logs']),2,'native logs');log(r,'stdout');log(r,'stderr')
eq(len({r['pid'] for r in q['commands']}),36,'unique child pids')
texts=obj(E/'operation/text-receipts.json');eq(len(texts['files']),78,'text count')
expected_texts={r['path'] for row in q['commands'] for r in row['logs']}|{str(OP/'qualification.json'),str(OP/'private.sb')}|{str(LP/n) for n in ['launch.json','execution.json','stdout','stderr']}
eq({r['source'] for r in texts['files']},expected_texts,'exact 78 text allowlist')
for r in texts['files']:
 b=data(r['source'],r['sha256']);eq(len(b),r['bytes'],'text bytes');eq(b,r['text'].encode(),'retained text exact')
eq(data(LP/'launch.json'),data(E/'native-launch.json'),'launch private copy');eq(data(LP/'execution.json'),data(E/'native-execution.json'),'native private copy')
data(LP/'stdout',native['stdout_sha256']);eq(data(LP/'stderr',native['stderr_sha256']),b'','native stderr')
outer=[json.loads(x) for x in data(LP/'stdout').splitlines()];eq(len(outer),37,'native stdout count')
for out,row in zip(outer[:-1],q['commands']):eq(out,{'case':row['case'],'returncode':row['returncode']},'native streamed outcome')
eq(outer[-1],{'state':q['state'],'receipt':str(OP/'qualification.json')},'native final summary')
copy=obj(E/'operation/copy-manifest.json');eq(len(copy['files']),4,'operation copy count')
for r in copy['files']:eq(data(r['source'],r['sha256']),data(r['destination'],r['sha256']),'operation copy')
checks['native_text_bindings']={'commands':36,'command_logs':72,'retained_texts':78,'operation_copy_pairs':4,'preparation_copy_pairs':6,'capacity_logs':14,'native_returncode':0,'native_elapsed_seconds':native['elapsed_seconds'],'counts':dict(collections.Counter(str(r['returncode']) for r in q['commands']))}
profile='(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(OP))+' ) (literal "/dev/null"))\n(deny network*)\n'
profile=profile.replace('" )','")')
eq(data(OP/'private.sb').decode(),profile,'private sandbox exact');eq(sha(data(OP/'private.sb')),q['confinement']['profile_sha256'],'sandbox binding');eq(q['confinement']['allowed_inherited_fds'],[0,1,2,3],'fds')
for variant,plan in pr['checks']['static_private_argument_plans'].items():
 for key,suffix in [('link_argv','link'),('codesign_argv','sign')]:
  argv=[x.replace('/REVIEW_STATIC_PATH_ONLY/task14b1',str(OP)) for x in plan[key]]
  eq(rows[variant+'-runtime-'+suffix]['argv'],SB+argv,'prepared exact '+variant+' '+suffix)
 eq(q['repair'][variant]['object_sha256'],recipe['qualified_mapping_objects'][variant]['sha256'],'mapping identity')
checks['private_relink']={'exact_prepared_argv_translation':True,'variants':['original','patched'],'128_object_paths_reused_without_object_rehash':True,'sole_variant_differences':'prepared output and sanitizer_procmaps object','confinement_profile_sha256':q['confinement']['profile_sha256']}
# Verify compile/link argv against the previously admitted TSan probe metadata, without reading its binary or source guards.
oldq=obj(ROOT/'evidence/p2996-tsan/operation/qualification.json',contract['original_failure']['receipt_sha256'])
oldrows={r['case']:r for r in oldq['commands']}
oldrun=str(Path(contract['witness']['path']).parent.parent)
for oldname,newname in [('tsan-core','tsan-ubsan-core'),('tsan-link','tsan-ubsan-link')]:
 old=oldrows[oldname]['argv']
 new=[x.replace(oldrun,str(OP)).replace('/tsan/','/tsan-ubsan/').replace('-fsanitize=thread','-fsanitize=thread,undefined') for x in old]
 eq(rows[newname]['argv'],new,'combined argv inherited '+newname)
 eq(log(rows[newname],'stderr'),b'','combined compile/link stderr')
launcher="import json,os,resource,sys;resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.execve(sys.argv[1],sys.argv[1:3],dict(os.environ,**json.loads(sys.argv[3]),DYLD_PRINT_LIBRARIES='1'))"
prefix=Path(contract['prefixes']['p2996']);required_libs={str(prefix/'lib'/n) for n in ['libc++.1.0.dylib','libc++abi.1.0.dylib','libunwind.1.0.dylib']}
runtime_name='libclang_rt.tsan_osx_dynamic.dylib';loader_facts={}
for case,rc in expected.items():
 variant='original' if case=='original-clean' else 'patched';name='tsan-ubsan' if case.startswith('tsan-ubsan') else 'tsan';mode=case.rsplit('-',1)[-1]
 binary=contract['witness']['path'] if name=='tsan' else str(OP/name/'witness')
 opts={**contract['runtime_environment'],'DYLD_LIBRARY_PATH':str(OP/variant)}
 eq(rows[case]['argv'],SB+[PY,'-E','-B','-c',launcher,binary,mode,json.dumps(opts)],'witness argv '+case)
 out=log(rows[case],'stdout');err=log(rows[case],'stderr').decode()
 loaded=sorted({str(Path('/'+line.split('/',1)[1]).resolve()) for line in err.splitlines() if line.startswith('dyld[') and '/' in line})
 rt=str(OP/variant/runtime_name);eq([x for x in loaded if 'libclang_rt.' in x],[rt],'unique sanitizer loader '+case)
 assert required_libs.issubset(loaded),case
 if case=='original-clean':
  eq(out,b'','original stdout empty');assert all(line.startswith('dyld[') for line in err.splitlines()),'unexpected original diagnostics'
  eq(q['original_startup_failure'],{'returncode':-11,'stdout_empty':True},'original summary')
 else:
  eq(out,b'reflection value=43, members=1\n','reflection stdout '+case)
  eq(q['cells'][name]['runs'][mode]['loaded'],loaded,'retained loader '+case)
  eq(q['cells'][name]['runs'][mode]['expected_returncode'],rc,'run expected rc')
  if mode=='race':
   assert 'WARNING: ThreadSanitizer: data race' in err and 'SUMMARY: ThreadSanitizer: data race' in err
   writes=re.findall(r'(?:Write|Previous write) of size 4 at (0x[0-9a-f]+)',err);assert len(writes)>=2 and writes[0]==writes[1],('same race location',case,writes)
   assert 'by main thread' in err and 'by thread T1' in err
  elif mode=='overflow':
   assert 'tsan_witness.cpp:40:37: runtime error: signed integer overflow: 2147483647 + 1 cannot be represented' in err
  else:assert all(line.startswith('dyld[') for line in err.splitlines()),'clean diagnostic '+case
 loader_facts[case]={'returncode':rc,'stdout_sha256':sha(out),'stderr_sha256':sha(err.encode()),'dyld_lines':sum(x.startswith('dyld[') for x in err.splitlines()),'sanitizer_runtime':rt,'selected_cpp_libraries_present':sorted(required_libs),'claim_other_system_cpp_absent':False}
checks['diagnostic_and_loader_proof']=loader_facts
archcases=[r for r in q['commands'] if '-arch-' in r['case']];eq(len(archcases),6,'arch observations')
for r in archcases:eq(log(r,'stdout').strip(),b'arm64','arch stdout');eq(log(r,'stderr'),b'','arch stderr')
warnings={}
for case in ['original-runtime-link','patched-runtime-link']:
 w=log(rows[case],'stderr').decode();assert 'argument unused during compilation' in w and '-stdlib=libc++' in w and '[-Wunused-command-line-argument]' in w
 eq(len(w.splitlines()),1,'link warning only');warnings[case]=w
checks['retained_nonfatal_warnings']=warnings
# Capacity, editor identity and writer census are receipt inspections, not new live probes.
for key in ['writer_census_before','writer_census_after']:
 x=q[key];eq(x['processes'],cap['writer_census']['processes'],'writer census stable');eq(x['lock_holder_check_rc'],1,'no holder rc');eq(x['lock_holders'],[],'no holders')
eq(cap['writer_census']['lock_holder_check_rc'],1,'capacity no holder rc');eq(cap['writer_census']['lock_holders'],[],'capacity no holders')
for x in [cap,q['capacity']]:
 eq(x['cpus'],12,'capacity cpus');assert x['free_bytes']>=contract['disk_reserve_bytes'];assert x['load'][0]<x['cpus'] and x['total_cpu_percent']<x['cpus']*100 and x['container_cpu_percent']<20
 eq(x['admitted_editor_services'],['73356','73398'],'admitted editors')
 eq(x['active_build_processes'] if 'active_build_processes' in x else x['active'],['73356   0.0 /opt/homebrew/opt/llvm/bin/clangd','73398   0.0 /Library/Developer/CommandLineTools/usr/bin/clangd'],'active editor CPU')
for rr in [rows,caprows]:
 eq(log(rr['editor-identities'],'stdout'),log(rr['editor-identities-after'],'stdout'),'editor identities stable')
 identities={}
 for line in log(rr['editor-identities'],'stdout').decode().splitlines():
  bits=line.split(None,7);assert len(bits)==8
  identities[bits[0]]={'ppid':bits[1],'started_at':' '.join(bits[2:7]),'executable':bits[7]}
 want={}
 for pid,p in contract['editor_services']['processes'].items():want[pid]=p['identity'];want.update(p['ancestors'])
 eq(identities,want,'editor identities bound')
 cwdlines=log(rr['editor-cwd'],'stdout').decode().splitlines();eq(cwdlines,['p73356','fcwd','n'+str(ROOT),'p73398','fcwd','n'+str(ROOT)],'editor cwd')
 eq(log(rr['docker-context'],'stdout').decode().strip(),admit['docker_context'],'container context')
 eq(log(rr['docker-census'],'stdout').decode().splitlines(),admit['containers'],'admitted container')
eq(cap['docker_context'],admit['docker_context'],'capacity docker context');eq(cap['containers'],admit['containers'],'capacity containers')
checks['capacity_and_ownership_receipts']={'preflight':cap,'under_lease':q['capacity'],'writer_census_before':q['writer_census_before'],'writer_census_after':q['writer_census_after'],'independent_live_reprobe':False}
# Protected source/default receipts are compared to frozen digests; shared trees are not traversed.
eq(log(rows['project-head'],'stdout').decode().strip(),HEAD,'runtime project head')
source=contract['source_provenance']
for part in ['head','tree','diff','status']:
 b=log(rows['source-before-'+part],'stdout');eq(b,log(rows['source-after-'+part],'stdout'),'source before after '+part)
 if part in ['head','tree']:eq(b.decode().strip(),source[part],'source '+part)
 else:eq(sha(b),source['diff_sha256'] if part=='diff' else contract['inputs'][source['status']],'source digest '+part)
eq(log(rows['default-before'],'stdout'),log(rows['default-after'],'stdout'),'default unchanged')
eq(sha(log(rows['default-before'],'stdout')),contract['inputs'][contract['default_profile']],'default frozen profile')
closure=obj(E/'operation/closure.json',cc['closure_sha256'])
eq(closure['qualification_sha256'],watched[str(E/'operation/qualification.json')],'closure q');eq(closure['native_execution_sha256'],watched[str(E/'native-execution.json')],'closure native')
eq(closure['text_receipts_sha256'],watched[str(E/'operation/text-receipts.json')],'closure text binding')
eq(closure['artifact_inventory_sha256'],watched[str(E/'artifact-inventory.json')],'closure artifacts')
eq(closure['command_outcomes'],[{'case':r['case'],'returncode':r['returncode']} for r in q['commands']],'closure outcomes')
eq(closure['processes'],[{'case':'native-helper','pid':native['pid'],'absent':True}]+[{'case':r['case'],'pid':r['pid'],'absent':True} for r in q['commands']],'collector historical PID set')
eq(closure['lease_probe'],{'free':True,'contents_unchanged':True},'collector historical lease')
for k in ['protected_state_unchanged','installed_tsan_unchanged']:eq(closure[k],True,'closure '+k)
assert utc(closure['recorded_at'])>utc(native['finished_at'])
collection=obj(E/'operation/collection-execution.json')
eq(collection['returncode'],0,'collector recorded rc');eq(collection['collector_sha256'],watched[str(E/'collect.py.source')],'collector source');eq(collection['closure_sha256'],watched[str(E/'operation/closure.json')],'collector closure')
assert 'elapsed' not in collection and 'elapsed_seconds' not in collection
checks['historical_closure']={'recorded_at':closure['recorded_at'],'recorded_processes_absent':37,'recorded_lease_free_and_contents_unchanged':True,'independent_live_reprobe':False,'collection_returncode_recorded':0,'collector_elapsed_seconds':None,'collector_timing_not_reconstructed':True}
static=obj(E/'post-native-static.json',cc['post_native_static_sha256']);eq([r['returncode'] for r in static['commands']],[0,0,0],'static rc')
eq(static['commands'][1]['result']['baseline'],19,'Claude original hashes receipt')
checks['static_receipts']={'returncodes':[0,0,0],'baseline_hashes':19,'result':static['commands'][1]['result'],'independently_executed_now':False,'fresh_session_or_OCI':False}
scan=obj(E/'pre-artifact-secret-scan.json',cc['pre_artifact_secret_scan_sha256']);data(scan['script'],scan['script_sha256'])
eq(len(scan['files']),37,'scanned files');eq(scan['raw']['returncode'],1,'raw scan rc');eq(scan['transformed']['returncode'],0,'transformed scan rc');eq(scan['supplemental_complete_token_files'],[],'complete token files')
for p,h in scan['files'].items():data(p,h)
oldscan=obj(E/'pre-review-secret-scan.json');old_dispositions={(r['path'],r['sha256']) for r in oldscan['dispositions']}
eq(len(old_dispositions),5,'old dispositions');eq(len(scan['dispositions']),7,'new dispositions')
for r in scan['dispositions']:
 assert r['rule']=='generic-api-key' and r['reason']=='Verified exact file-content digest'
 if (r['path'],r['sha256']) not in old_dispositions:data(r['path'],r['sha256'])
 assert len(r['sha256'])==64
checks['secret_scan']={'bound_scanned_files':37,'raw_rc':1,'digest_dispositions':7,'prior_dispositions_reused_without_guard_or_object_rehash':5,'new_text_digest_dispositions_checked':2,'transformed_rc':0,'complete_token_files':[],'scan_reexecuted':False,'frozen_files_outside_scan':sorted(set(ci['maintained']|ci['evidence'])-set(scan['files']))}
# Four focused Git identity reads, no index/status/diff writers and no recursive scans.
git=[]
for args,expected in [(['rev-parse','--show-toplevel'],str(ROOT)),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding'),(['rev-parse','HEAD'],HEAD),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
 argv=['/usr/bin/git','-c','core.fsmonitor=false',*args];start=time.monotonic();run=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5,check=False)
 eq(run.returncode,0,'git rc');eq(run.stderr,b'','git stderr');eq(run.stdout.decode().strip(),expected,'git value')
 git.append({'argv':argv,'returncode':run.returncode,'stdout':run.stdout.decode(),'stderr':'','elapsed_seconds':time.monotonic()-start})
checks['git_identity']=git
# Re-read only bounded text to reject concurrent candidate drift before the six binary opens.
for p,h in watched.items():eq(sha(Path(p).read_bytes()),h,'end text stability '+p)
inv=obj(E/'artifact-inventory.json',cc['artifact_inventory_sha256'])
eq(inv['qualification_sha256'],watched[str(E/'operation/qualification.json')],'inventory q')
allowed={
 'original-tsan-runtime':(str(OP/'original'/runtime_name),q['repair']['original']['sha256'],6),
 'patched-tsan-runtime':(str(OP/'patched'/runtime_name),q['repair']['patched']['sha256'],6),
 'tsan-binary':(contract['witness']['path'],contract['witness']['sha256'],2),
 'tsan-ubsan-object':(q['cells']['tsan-ubsan']['artifacts']['object']['path'],q['cells']['tsan-ubsan']['artifacts']['object']['sha256'],1),
 'tsan-ubsan-binary':(q['cells']['tsan-ubsan']['artifacts']['binary']['path'],q['cells']['tsan-ubsan']['artifacts']['binary']['sha256'],2),
 'installed-tsan-unchanged':(str(prefix/'lib/clang/21/lib/darwin'/runtime_name),contract['tools'][str(prefix/'lib/clang/21/lib/darwin'/runtime_name)],6)}
eq({r['kind'] for r in inv['artifacts']},set(allowed),'six exact artifact kinds');eq(len(inv['artifacts']),6,'six only')
for r in inv['artifacts']:eq((r['path'],r['sha256']),allowed[r['kind']][:2],'artifact binding '+r['kind'])
# Last content reads: exactly the six allowed binaries, once each. No link-object or compiler hash.
for r in inv['artifacts']:
 p=Path(r['path']);eq(p.resolve(),p,'canonical artifact');a=p.lstat();assert stat.S_ISREG(a.st_mode) and a.st_uid==os.getuid() and a.st_nlink==1
 eq(a.st_size,r['bytes'],'artifact stat size');assert a.st_size<2000000
 b=p.read_bytes();artifact_reads.append(str(p));eq(stamp(a),stamp(p.lstat()),'stable artifact')
 eq(sha(b),r['sha256'],'artifact digest');eq(len(b),r['bytes'],'artifact bytes')
 magic,cpu,subcpu,filetype,ncmds,sizeofcmds,flags,reserved=struct.unpack_from('<8I',b)
 eq(magic,0xfeedfacf,'MachO magic');eq(cpu,0x100000c,'arm64');eq(filetype,allowed[r['kind']][2],'MachO type')
 off=32;uuids=[]
 for _ in range(ncmds):
  cmd,size=struct.unpack_from('<2I',b,off);assert size>=8 and off+size<=32+sizeofcmds
  if cmd==0x1b:uuids.append(str(uuid.UUID(bytes=b[off+8:off+24])).upper())
  off+=size
 if r['kind'] in ['original-tsan-runtime','patched-tsan-runtime']:
  eq(len(uuids),1,'runtime UUID')
  for case,fact in loader_facts.items():
   if fact['sanitizer_runtime']==str(p):assert '<'+uuids[0]+'>' in log(rows[case],'stderr').decode(),('dyld UUID',case)
 r['mach_o']={'cpu':'arm64','filetype':filetype,'uuids':uuids};r['content_reads']=1
checks['artifacts']={'count':6,'bytes':sum(r['bytes'] for r in inv['artifacts']),'each_hashed_once':True,'files':inv['artifacts']}
result={'result':'PASS','recorded_at':datetime.datetime.now(datetime.UTC).isoformat(),'candidate_sha256':EXPECTED_CANDIDATE,'closure_inputs_sha256':EXPECTED_INPUTS,'helper_sha256':helper_sha,'contract_sha256':watched[str(E/'contract.json')],'recipe_sha256':watched[str(E/'recipes.json')],'qualification_sha256':cc['qualification_sha256'],'checks':checks,'watched_text_sha256':watched,'not_run':['No native build, compiler, linker, codesign, lipo, sanitizer, witness, capacity, process census or lease probe','No inherited 881-source guard or 128-object rehash, no compiler hash','No scanner rerun, static task rerun, model session, network, service, container or OCI operation','No installed runtime promotion, general sanitizer matrix or fresh Claude acceptance']}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':'PASS','frozen_files':40,'native_commands':36,'retained_texts':78,'capacity_logs':14,'artifacts':6,'artifact_bytes':checks['artifacts']['bytes'],'git_returncodes':[r['returncode'] for r in git]}))

from pathlib import Path
import ast,datetime,hashlib,json,subprocess,time
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/p2996-tsan-promotion';D=Path(__file__).parent
C='f7f41aaa275ac70f0697e93dcabe7dec614857bb4d13909430f74dda8e0d9874';S='87132190caad6f4dcdab0e4723135d9cb9c23dc5e2fe989fdc1f9a842942f176';H='f9188f06abf5735196e08775c5e84285b0e4139831d053e41b5a3a376ab4bf53';HEAD='a3de6bc78da3d5717c5c1367585f396908977e9d'
cache={};watched={}
def sha(b):return hashlib.sha256(b).hexdigest()
def data(p,h=None):
 p=Path(p);p=p if p.is_absolute() else R/p;k=str(p)
 if k not in cache:
  assert p.stat().st_size<50000000;k=str(p);b=p.read_bytes();b.decode();cache[k]=b;watched[k]=sha(b)
 if h is not None:assert watched[k]==h,(k,watched[k],h)
 return cache[k]
def obj(p,h=None):return json.loads(data(p,h))
can=obj(E/'candidate.json',C);sn=obj(E/'candidate-inputs.json',S);c=obj(E/'contract.json',H)
assert can['base_head']==c['base_head']==HEAD and len(can['files'])==4 and len(sn)==11
for p,h in sn.items():data(p,h)
for p,h in can['evidence'].items():data(E/p,h)
assert len(c['inputs'])==190 and all(not Path(p).is_absolute() for p in c['inputs'])
for p,h in c['inputs'].items():data(p,h)
old=obj(R/'evidence/p2996-tsan-repair/contract.json');runtime=obj(R/'evidence/p2996-tsan-runtime/contract.json');asan=obj(R/'evidence/p2996-asan-promotion/contract.json')
assert len(old['inputs'])==181 and all(c['inputs'][p]==h for p,h in old['inputs'].items())
assert c['source_inputs']==old['source_inputs'] and len(c['source_inputs'])==881
assert c['tools']==old['tools'] and len(c['tools'])==28 and c['abi_inputs']==old['abi_inputs']
assert c['target'] not in c['source_inputs'] and c['tools'][c['target']]==c['before']['sha256']
assert c['target']==runtime['target'] and c['after']==runtime['current_tsan'] and c['replacement_identity']==runtime['qualified_replacement_identity']
assert c['before']=={k:runtime['previous_record'][k] for k in ['sha256','bytes','mode']}
assert c['replacement']==runtime['qualified_replacement']['path'] and c['replacement_identity']['mode']=='0o700' and c['before']['mode']==c['after']['mode']=='0o755'
qr=obj(R/'evidence/p2996-tsan-repair/artifact-review/review.json');q=obj(R/'evidence/p2996-tsan-repair/operation/qualification.json');cl=obj(R/'evidence/p2996-tsan-repair/operation/closure.json');inv=obj(R/'evidence/p2996-tsan-repair/artifact-inventory.json')
rr=obj(R/'evidence/p2996-tsan-runtime/preparation-review/review.json','8164d6a2f9cb8165e054f99062de7c657fd9ba8572e99de528d8cd8469baeef0')
assert rr['result'].startswith('PASS') and not rr['findings'] and rr['contract_sha256']=='537f8dc41f310efa0cb5a5084b00e9bc3c610db2537b53c2ed35ee565b27649d'
assert qr['result'].startswith('PASS') and not qr['findings'] and q['state'].startswith('PASS') and cl['state'].startswith('PASS')
assert qr['qualification_sha256']==cl['qualification_sha256']==watched[str(R/'evidence/p2996-tsan-repair/operation/qualification.json')]
assert q['lease_released'] and q['protected_state_unchanged'] and cl['native_returncode']==0
coverage={}
for mode,kind in [('tsan','tsan-binary'),('tsan-ubsan','tsan-ubsan-binary')]:
 row=next(x for x in inv['artifacts'] if x['kind']==kind);w=c['witnesses'][mode];assert w=={k:row[k] for k in ['path','sha256','bytes']}
 coverage[mode]={k:w['path'] in c[k] for k in ['inputs','source_inputs','tools']};coverage[mode]['abi_inputs']=any(v['path']==w['path'] for rows in c['abi_inputs'].values() for v in rows)
 assert not any(coverage[mode].values())
assert all(asan['source_inputs'][w['path']]==w['sha256'] for w in asan['witnesses'].values())
t=ast.parse(data(R/'dev/toolchains/p2996_tsan_promote.py').decode());a=ast.parse(data(R/'dev/toolchains/p2996_asan_promote.py').decode())
fn=lambda tree,name:next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
unchanged=[]
for name in ['save','run','source_state','interrupted']:
 assert ast.dump(fn(t,name),include_attributes=False)==ast.dump(fn(a,name),include_attributes=False);unchanged.append(name)
guard=ast.unparse(fn(t,'guard'));assert 'witnesses' not in guard
assert any(isinstance(n,ast.ImportFrom) and n.module=='p2996_asan_promote' and any(x.name=='transition' for x in n.names) for n in t.body)
assert c['inputs']['dev/toolchains/p2996_asan_promote.py']=='2e8229fa0d0b39552923cd6db80a92da5be56951eac6e3fd696bad97cdf6e01d'
cases={mode+'-'+name:rc for mode,settings in c['sanitizers'].items() for name,rc in {'clean':0,**{k:86 for k in settings['errors']}}.items()}
assert cases=={'tsan-clean':0,'tsan-race':86,'tsan-ubsan-clean':0,'tsan-ubsan-race':86,'tsan-ubsan-overflow':86}
static=obj(E/'pre-review-static.json');assert [x['returncode'] for x in static['checks']]==[0,0,0,0] and 'baseline 19' in static['checks'][2]['observed']
scan=obj(E/'pre-review-secret-scan.json');data(scan['script'],scan['script_sha256'])
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and len(scan['dispositions'])==6 and scan['supplemental_complete_token_files']==[]
for p,h in scan['files'].items():data(p,h)
payload=''.join(p+'\n'+data(p).decode()+'\n' for p in scan['files']);assert sha(payload.encode())==scan['raw']['payload_sha256']
prior_scan=obj(R/'evidence/p2996-tsan-repair/pre-artifact-secret-scan.json');known={(x['path'],x['sha256']) for x in prior_scan['dispositions']};new=0
for x in scan['dispositions']:
 assert x['rule']=='generic-api-key' and x['reason']=='Verified exact file-content digest'
 if (x['path'],x['sha256']) not in known:data(x['path'],x['sha256']);new+=1
assert new==1
for phase,count in [('raw',6),('transformed',0)]:
 path=next(x.split('=',1)[1] for x in scan[phase]['argv'] if x.startswith('--report-path='));assert len(obj(path))==count
commands=[]
for args,want in [(['rev-parse','--show-toplevel'],str(R)),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding'),(['rev-parse','HEAD'],HEAD),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
 argv=['/usr/bin/git','-c','core.fsmonitor=false',*args];p=subprocess.run(argv,cwd=R,capture_output=True,text=True,timeout=5);assert p.returncode==0 and not p.stderr and p.stdout.strip()==want;commands.append({'argv':argv,'returncode':0,'stdout':p.stdout})
for p in [E/'candidate.json',E/'candidate-inputs.json',E/'contract.json',*[R/x for x in can['files']]]:assert sha(p.read_bytes())==watched[str(p)]
result={'result':'PASS: bounded comparisons; blocking regression reproduced statically','head':HEAD,'candidate_sha256':C,'candidate_inputs_sha256':S,'contract_sha256':H,'helper_sha256':watched[str(R/'dev/toolchains/p2996_tsan_promote.py')],'snapshots':11,'direct_input_hashes':190,'inherited_inputs':181,'new_inputs':sorted(set(c['inputs'])-set(old['inputs'])),'unchanged_source_input_metadata':881,'unchanged_tool_metadata':28,'abi_metadata_unchanged':True,'source_tool_abi_binary_reads':0,'binary_reads':0,'missing_witness_guard_coverage':coverage,'predecessor_ASan_witness_source_coverage':True,'unchanged_AST_functions':unchanged,'transition_import_and_hash_unchanged':True,'expected_native_cases':cases,'static_receipt_rcs':[0,0,0,0],'original_acceptance_hashes_reported':19,'scan':{'files':len(scan['files']),'raw_rc':1,'transformed_rc':0,'dispositions':6,'inherited_dispositions_reused_without_binary_or_SDK_reads':5,'new_text_digest_checked':1,'complete_token_files':[]},'git':commands,'watched_text_sha256':watched,'not_run':['No binary artifacts read; current binary content deliberately unverified because preparation is blocked statically','No promotion, witness, guard, lease, capacity, process census, scanner, static task, native tool, service, container, network or model session executed','No recursive source/build/tools/ABI inventory rehash or nested global-state reads']}
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'comparison':'PASS','review':'CHANGES REQUIRED','missing_witness_guards':2,'direct_input_hashes':190,'binary_reads':0,'git_returncodes':[0,0,0,0]}))

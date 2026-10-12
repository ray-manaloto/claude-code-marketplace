import ast,builtins,datetime,difflib,dis,hashlib,json,re,subprocess,types
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/p2996-tsan-promotion';D=Path(__file__).parent
PREV=Path('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-tsan-promotion-corrected-review-t9m2nox0')
HEAD='a3de6bc78da3d5717c5c1367585f396908977e9d';cache={};watched={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p,digest=None):
 p=Path(p);p=p if p.is_absolute() else R/p
 if p not in cache:cache[p]=p.read_bytes();cache[p].decode();watched[str(p)]=sha(cache[p])
 if digest:assert sha(cache[p])==digest,str(p)
 return cache[p]
def js(p,digest=None):return json.loads(read(p,digest))
previous_hashes={'review.json':'d406c12bcec0c80a4b16c075299ac766999fea7a8e54f96103a3b8a89e991cb5','supporting-manifest.json':'51baf74e4de808507acd1555dacbfccff410480eca668396a9a3a1e9713f70bb','compare.py':'1d0ca8ec38bfd8b4c969fcffc8fa355408c96fffea0251a841cec6820b6a77d8','comparison.json':'389af7a065c12f0a745b72438d1aac0720ceaf80f7d9930276cbbec1c3338245','execution.json':'831f92615afec03214ce9cffdb77616ab44c95143050d09f391b2266cd8e5d77'}
for f,h in previous_hashes.items():assert read(E/'preparation-review-corrected'/f,h)==read(PREV/f,h)
previous=js(E/'preparation-review-corrected/review.json');previous_check=js(E/'preparation-review-corrected/comparison.json')
assert previous['result'].startswith('PASS') and previous['findings']==[]
for f in ('pre-run-review.json','pre-run-review-before-import-repair.json'):assert read(E/f)==read(PREV/'review.json')
old=js(E/'candidate-before-import-repair.json','c6695c3485afb6d7d358aeb3abee5335cc8c7fb864dc10a02866b686a6682ed7');oldinputs=js(E/'candidate-inputs-before-import-repair.json','c4e9d12dfe678c90d6672c82a9b54bdcfecd70644ab7444f52d378cf92a6edfc')
new=js(E/'candidate.json','3746939ef7ca9af3286dc4cf46648eee8244c4c74aa36ea6696018fc43095cc1');inputs=js(E/'candidate-inputs.json','7ade43416f7d0917eac4e921de5b709cf5175dee228363e83693e7abc503675b')
assert new['base_head']==old['base_head']==HEAD and new['files']==old['files'] and new['previous_candidate_sha256']==sha(cache[E/'candidate-before-import-repair.json'])
for f,h in new['evidence'].items():read(E/f,h)
for f,h in inputs.items():read(f,h)
assert len(inputs)==15 and len(oldinputs)==11
C=js(E/'contract.json','f9188f06abf5735196e08775c5e84285b0e4139831d053e41b5a3a376ab4bf53')
assert C['witnesses']=={row['name']:{k:row[k] for k in ('path','sha256','bytes')} for row in previous_check['binary_checks']}
deltas={};original={}
for f in new['files']:
 now=read(f).decode()
 if f.endswith('p2996_tsan_promote.py'):
  before=now
  for line in ('from datetime import datetime, timezone\n','import subprocess\n','import time\n'):assert before.count(line)==1;before=before.replace(line,'',1)
 elif f.endswith('task_plan.md'):before=now.replace('Initial dispatch failed before mutation; corrected retry review pending','Prepared; review pending',1)
 elif f.endswith('progress.md'):before=now.split('- The focused correction review passed without findings.',1)[0]
 else:before=now.split('The first admitted dispatch stopped before the lease and before any installed',1)[0]
 assert sha(before.encode())==oldinputs[f];original[f]=before
 deltas[f]=''.join(difflib.unified_diff(before.splitlines(True),now.splitlines(True),fromfile='before/'+f,tofile='retry/'+f))
helper='dev/toolchains/p2996_tsan_promote.py';code=read(helper).decode();tree=ast.parse(code)
assert sha(code.encode())=='e0a72e001c56d0c756c0ef1b3b74a9f25e783955221ab659f4df199e8772c728'
assert [ast.dump(n,include_attributes=False) for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom))]==[ast.dump(n,include_attributes=False) for n in ast.parse(original[helper]).body if not isinstance(n,(ast.Import,ast.ImportFrom))]
sourcepath='evidence/p2996-math-resume/operation/p2996_build.py.source';source=read(sourcepath,'7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f').decode()
node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name=='run');compiled=compile(ast.Module(body=[node],type_ignores=[]),'review-only','exec');body=next(c for c in compiled.co_consts if isinstance(c,types.CodeType) and c.co_name=='run')
def globals_used(co):
 names={i.argval for i in dis.get_instructions(co) if i.opname=='LOAD_GLOBAL'}
 for child in co.co_consts:
  if isinstance(child,types.CodeType):names |= globals_used(child)
 return names
refs=globals_used(body)-set(vars(builtins));bindings=set()
for n in tree.body:
 if isinstance(n,ast.Import):bindings.update(a.asname or a.name.split('.')[0] for a in n.names)
 elif isinstance(n,ast.ImportFrom):bindings.update(a.asname or a.name for a in n.names)
injected={'directory','report','env','save'};assert refs=={'datetime','digest','directory','env','json','os','report','save','shutil','signal','subprocess','time','timezone'}
assert not refs-bindings-injected and refs-(bindings-{'datetime','timezone','time','subprocess'})-injected=={'datetime','timezone','time','subprocess'}
extractor=read('dev/toolchains/mise_runtime.py',C['inputs']['dev/toolchains/mise_runtime.py']).decode();assert 'exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)' in extractor
calls=sorted(n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='guard');assert calls==[107,142,168,198,210]
closure=js(E/'initial-failure/closure.json');q=js(E/'initial-failure/qualification.json',closure['qualification_sha256']);execution=js(E/'initial-failure/execution.json');launch=js(E/'initial-failure/launch.json');admission=js(E/'admission-before-import-repair.json',execution['admission_sha256'])
for f,h in closure['files'].items():read(E/'initial-failure'/f,h)
for f,row in js(E/'initial-failure/copy-manifest.json').items():assert read(E/'initial-failure'/f,row['sha256'])==read(row['source'],row['sha256']) and len(read(row['source']))==row['bytes']
for f in ('native-execution.json','native-execution-before-import-repair.json'):assert read(E/f)==read(E/'initial-failure/execution.json')
for f in ('native-launch.json','native-launch-before-import-repair.json'):assert read(E/f)==read(E/'initial-failure/launch.json')
assert read(E/'admission.json')==read(E/'admission-before-import-repair.json')
assert q['state']=='FAIL' and q['commands']==[] and q['cells']=={} and q['mutation_started'] is False and q['protected_state_matches_expected'] is True
assert closure['command_count']==0 and closure['mutation_started'] is False and closure['protected_state_matches_expected'] is True
assert closure['dispatch_returncode']==execution['returncode']==1 and execution['pid']==45617
assert q['error']==closure['error']=='''NameError("name 'datetime' is not defined")'''
assert all(execution[k]==v for k,v in launch.items())
assert q['helper_sha256']==execution['helper_sha256']==previous['helper_sha256'] and q['admission_sha256']==execution['admission_sha256']
assert admission['candidate_sha256']==previous['candidate_sha256'] and admission['review_sha256']==previous_hashes['review.json']
assert admission['helper_sha256']!=inputs[helper]
assert closure['installed_tsan_identity']==C['before']
assert closure['native_pid_probe']['returncode']==1 and closure['native_pid_probe']['stdout']=='' and closure['native_pid_probe']['argv'][2]==str(execution['pid'])
assert closure['lease_observation']['our_attempt_reached_lease'] is False and closure['lease_observation']['open_file_pids']==['96190']
stdout=read(E/'initial-failure/dispatch.stdout',execution['stdout_sha256']).decode();stderr=read(E/'initial-failure/dispatch.stderr',execution['stderr_sha256']).decode()
assert json.loads(stdout)['state']=='FAIL' and "NameError: name 'datetime' is not defined" in stderr and 'line 73, in run' in stderr
assert 'datetime.now(timezone.utc)' in source.splitlines()[72] and 'report["commands"].append(row)' in source.splitlines()[73]
read(E/'dispatch.py.source',execution['dispatch_sha256'])
control=js(E/'command-binding-control.json');assert control['runner_sha256']==inputs[helper] and control['source_sha256']==sha(cache[R/sourcepath]) and control['returncode']==0 and control['child_command']==['/usr/bin/true']
record=control['command_record'];assert record['returncode']==0 and record['argv']==['/usr/bin/true'] and record['pid']==56096 and record['elapsed_seconds']>0
assert js(Path(control['private_directory'])/'binding.json')['commands']==[record]
for row in record['logs']:assert read(row['path'],row['sha256'])==b''
static=js(E/'retry-static.json');assert len(static['checks'])==4 and all(c['returncode']==0 for c in static['checks']) and static['checks'][2]['observed']=='status pass; original baseline 19'
scan=js(E/'retry-secret-scan.json');read(scan['script'],scan['script_sha256'])
for f,h in scan['files'].items():read(f,h)
payload=''.join(f+'\n'+read(f).decode()+'\n' for f in scan['files']);assert sha(payload.encode())==scan['raw']['payload_sha256']
def scanpath(kind):return Path(next(x.split('=',1)[1] for x in scan[kind]['argv'] if x.startswith('--report-path=')))
raw=js(scanpath('raw'));transformed=js(scanpath('transformed'));assert len(raw)==len(scan['dispositions'])==24 and transformed==[] and scan['raw']['returncode']==1 and scan['transformed']['returncode']==0
oldscan=js(E/'corrected-secret-scan.json');known={(x['path'],x['sha256']) for x in oldscan['dispositions']};lines=payload.splitlines(keepends=True);inherited=0;newtexts=[]
for row,disposition in zip(sorted(raw,key=lambda x:(x['StartLine'],x['StartColumn']),reverse=True),scan['dispositions']):
 assert row['RuleID']=='generic-api-key' and row['StartLine']==row['EndLine'];i=row['StartLine']-1;segment=lines[i][row['StartColumn']-1:row['EndColumn']]
 digests=re.findall(r'[a-f0-9]{64}',segment);assert digests==[disposition['sha256']];key=(disposition['path'],disposition['sha256'])
 if key in known:inherited+=1
 else:read(*key);newtexts.append(disposition)
 lines[i]=lines[i][:row['StartColumn']-1]+segment.replace(digests[0],'VERIFIED_FILE_CONTENT_DIGEST')+lines[i][row['EndColumn']:]
assert inherited==22 and len(newtexts)==2 and sha(''.join(lines).encode())==scan['transformed']['payload_sha256']
pattern=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{20,}|dop_v1_[A-Za-z0-9]{20,}|fc-[0-9a-f]{32,}|exa_[A-Za-z0-9_-]{20,})');assert scan['supplemental_complete_token_files']==[] and not any(pattern.search(read(f).decode()) for f in scan['files'])
git=[]
for args,value in [(['rev-parse','--show-toplevel'],str(R)),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding'),(['rev-parse','HEAD'],HEAD),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
 argv=['/usr/bin/git','-c','core.fsmonitor=false']+args;p=subprocess.run(argv,cwd=R,capture_output=True,text=True,timeout=10);assert p.returncode==0 and p.stdout.strip()==value;git.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout})
for p,h in watched.items():assert sha(Path(p).read_bytes())==h,(p,'changed')
result={'result':'PASS: focused retry preparation only','findings':[],'head':HEAD,'candidate_sha256':sha(cache[E/'candidate.json']),'candidate_inputs_sha256':sha(cache[E/'candidate-inputs.json']),'helper_sha256':inputs[helper],'contract_sha256':sha(cache[E/'contract.json']),'four_file_deltas':deltas,'candidate_bindings':len(new['evidence']),'input_bindings':len(inputs),'wrapper_globals':sorted(refs),'previous_missing_globals':['datetime','timezone','time','subprocess'],'missing_globals_after':[],'guard_call_lines':calls,'previous_review_copies':previous_hashes,'initial_failure':{'execution':execution,'closure':closure,'private_copy_pairs_checked':5,'observations_historical_only':True},'control':control,'control_script_retained':False,'control_reexecuted':False,'static_receipt_rcs':[c['returncode'] for c in static['checks']],'Claude_baseline_hashes_reported':19,'scan':{'files':len(scan['files']),'raw_rc':1,'transformed_rc':0,'dispositions':24,'inherited_dispositions_without_SDK_object_reads':22,'new_text_digest_bindings':newtexts,'raw_and_transformed_payload_reconstruction':True,'complete_tokens':[]},'retained_witness_checks_not_reexecuted':previous_check['binary_checks'],'binary_reads':0,'direct_source_tool_build_inventory_rehashes':0,'git':git,'watched_text_sha256':watched,'limits':['No native retry, promotion, witness, recovery, real guard, lease, capacity, census, lsof or PID probe performed.','No binary artifact reads or 190-input/881-source/28-tool/ABI inventory rehash. Only scoped text receipts and the specifically inspected helper/wrapper/extractor source were hashed.','Parent control receipt/logs were verified; the control has no retained script and was not independently rerun.','Closure PID, installed identity and lease observations are retained historical claims, not independently reprobed state.','No static task/scanner/tool execution, installs, services, containers, network, models, global changes or further agents.']}
(D/'comparison.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':result['result'],'candidate_bindings':len(new['evidence']),'inputs':len(inputs),'scan_files':len(scan['files']),'wrapper_globals':len(refs),'binary_reads':0,'git_rcs':[r['returncode'] for r in git]}))

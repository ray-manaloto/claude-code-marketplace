import ast,datetime,difflib,hashlib,json,os,re,stat,struct,subprocess
from pathlib import Path
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
EV=ROOT/'evidence/p2996-tsan-promotion'; OUT=Path(__file__).parent
INITIAL=Path('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-tsan-promotion-preparation-review-ssi6q4ep')
HEAD='a3de6bc78da3d5717c5c1367585f396908977e9d';watched={};cache={}
def sha(b):return hashlib.sha256(b).hexdigest()
def textfile(path,expected=None):
 p=Path(path);p=p if p.is_absolute() else ROOT/p
 if p not in cache:
  b=p.read_bytes();b.decode();cache[p]=b;watched[str(p)]=sha(b)
 if expected is not None:assert sha(cache[p])==expected,(str(p),'digest mismatch')
 return cache[p]
def js(path,expected=None):return json.loads(textfile(path,expected))
initial_hashes={
 'review.json':'cb310fae44c293cfacfcae676f78ea0db9aad9990214501528f37e005bda6f40',
 'supporting-manifest.json':'ac41dd52692bbfca8241b00bbdea84f0f22a94ed0ac7fdb2368647d7ef3bab6d',
 'compare.py':'0c2f4ba1be638240c43dfefd34fdeeb8330b1a33ab6005688dd2b0379a6b8793',
 'comparison.json':'a96eead20437b3f1c5a3be4f4ce3a07f7facf91c6afcb666258ce29a3cf1339e',
 'execution.json':'96bc6be04c685c4f839d1bc2296cb9672097d9bcfcb91ce9bc3653e68ab0b6e4'}
for name,digest in initial_hashes.items():
 assert textfile(EV/'preparation-review-initial'/name,digest)==textfile(INITIAL/name,digest)
pr=js(EV/'preparation-review-initial/review.json');pc=js(EV/'preparation-review-initial/comparison.json')
assert pr['result']=='CHANGES REQUIRED' and len(pr['findings'])==1 and pr['findings'][0]['id']=='TSAN-PROMOTION-P1-WITNESS-GUARD'
assert js(EV/'preparation-review-initial/execution.json')['returncode']==0
old=js(EV/'candidate-initial.json','f7f41aaa275ac70f0697e93dcabe7dec614857bb4d13909430f74dda8e0d9874')
oldinputs=js(EV/'candidate-inputs-initial.json','87132190caad6f4dcdab0e4723135d9cb9c23dc5e2fe989fdc1f9a842942f176')
candidate=js(EV/'candidate.json','c6695c3485afb6d7d358aeb3abee5335cc8c7fb864dc10a02866b686a6682ed7')
inputs=js(EV/'candidate-inputs.json','c4e9d12dfe678c90d6672c82a9b54bdcfecd70644ab7444f52d378cf92a6edfc')
assert old['base_head']==candidate['base_head']==HEAD and old['files']==candidate['files']
assert candidate['initial_candidate_sha256']==sha(cache[EV/'candidate-initial.json'])
assert len(inputs)==len(oldinputs)==11 and set(inputs)==set(oldinputs)
for f,digest in inputs.items():textfile(f,digest)
for name,digest in candidate['evidence'].items():textfile(EV/name,digest)
for name,digest in old['evidence'].items():
 mapped={'candidate-inputs.json':'candidate-inputs-initial.json'}.get(name,name)
 textfile(EV/mapped,digest)
contract=js(EV/'contract.json','f9188f06abf5735196e08775c5e84285b0e4139831d053e41b5a3a376ab4bf53')
assert len(contract['inputs'])==190 and len(contract['source_inputs'])==881 and len(contract['tools'])==28
for f,digest in contract['inputs'].items():
 assert not Path(f).is_absolute() and '..' not in Path(f).parts
 textfile(f,digest)
assert pc['contract_sha256']==sha(cache[EV/'contract.json'])
helper='dev/toolchains/p2996_tsan_promote.py';progress='.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md'
added='''        assert set(data["witnesses"]) == set(data["sanitizers"]) == {"tsan", "tsan-ubsan"}
        for witness in data["witnesses"].values():
            path = Path(witness["path"])
            assert path.stat().st_size == witness["bytes"] and digest(path) == witness["sha256"]
'''
progress_added='''- Independent review of the first frozen candidate found a P1 gap: the runner
  recorded the two witness hashes but did not verify them at execution time.
  The runner now checks exact byte lengths and SHA-256 in its repeated guard.
  A focused review of the corrected candidate is pending.
'''
deltas={}
for f in candidate['files']:
 current=textfile(f,inputs[f]).decode()
 if f in (helper,progress):
  addition=added if f==helper else progress_added
  assert current.count(addition)==1
  before=current.replace(addition,'',1)
  assert sha(before.encode())==oldinputs[f]
  deltas[f]=''.join(difflib.unified_diff(before.splitlines(True),current.splitlines(True),fromfile='initial/'+f,tofile='corrected/'+f))
 else:assert inputs[f]==oldinputs[f]
assert set(k for k in inputs if inputs[k]!=oldinputs[k])=={helper,progress}
assert len(textfile(helper).decode().splitlines())==218
code=textfile(helper).decode();tree=ast.parse(code)
guard=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='guard')
assert added.strip() in ast.get_source_segment(code,guard)
guard_calls=sorted(n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='guard')
assert guard_calls==[104,139,165,195,207]
qualify=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='qualify')
assert [type(n).__name__ for n in qualify.body[:4]]==['Nonlocal','Assign','Expr','If']
assert ast.unparse(qualify.body[1])=='promoted = current' and ast.unparse(qualify.body[2])=='guard()'
assert set(contract['witnesses'])==set(contract['sanitizers'])=={'tsan','tsan-ubsan'}
static=js(EV/'corrected-static.json','b01b94f9bea6954c791dd050e3e3c94df7831a9f27fc0d6adaa52a5ce1ccbd57')
assert len(static['checks'])==4 and all(row['returncode']==0 for row in static['checks'])
assert static['checks'][2]['observed']=='status pass; original baseline 19'
scan=js(EV/'corrected-secret-scan.json');scansource=textfile(scan['script'],scan['script_sha256'])
assert scan['script_sha256']=='29ddc6ef779da11a38dcec1922d119a7ab0d78ed3fa41508e9ae936c36ee53ca'
assert len(scan['files'])==18
for f,digest in scan['files'].items():textfile(f,digest)
payload=''.join(f+'\n'+textfile(f).decode()+'\n' for f in scan['files'])
assert sha(payload.encode())==scan['raw']['payload_sha256']
def reportpath(kind):return Path(next(x.split('=',1)[1] for x in scan[kind]['argv'] if x.startswith('--report-path=')))
raw=js(reportpath('raw'));transformed=js(reportpath('transformed'))
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and transformed==[]
assert len(raw)==len(scan['dispositions'])==13
oldscan=js(EV/'pre-review-secret-scan.json','f76a6935dbbbfaf3fe8db8106dc6197ba96c2ca36ccc1e47d0f262338f4d5531')
inherited={(r['path'],r['sha256']) for r in oldscan['dispositions']};lines=payload.splitlines(keepends=True)
oldcount=0;newtexts=[]
for row,disposition in zip(sorted(raw,key=lambda r:(r['StartLine'],r['StartColumn']),reverse=True),scan['dispositions']):
 assert row['RuleID']=='generic-api-key' and row['StartLine']==row['EndLine']
 i=row['StartLine']-1;segment=lines[i][row['StartColumn']-1:row['EndColumn']]
 digests=re.findall(r'[a-f0-9]{64}',segment);assert digests==[disposition['sha256']]
 assert disposition['rule']==row['RuleID'] and disposition['reason']=='Verified exact file-content digest'
 key=(disposition['path'],disposition['sha256'])
 if key in inherited:oldcount+=1
 else:textfile(*key);newtexts.append({'path':key[0],'sha256':key[1]})
 lines[i]=lines[i][:row['StartColumn']-1]+segment.replace(digests[0],'VERIFIED_FILE_CONTENT_DIGEST')+lines[i][row['EndColumn']:]
assert oldcount==10 and len(newtexts)==3
assert sha(''.join(lines).encode())==scan['transformed']['payload_sha256']
pattern=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{20,}|dop_v1_[A-Za-z0-9]{20,}|fc-[0-9a-f]{32,}|exa_[A-Za-z0-9_-]{20,})')
assert scan['supplemental_complete_token_files']==[] and not any(pattern.search(textfile(f).decode()) for f in scan['files'])
# All remaining text/identity checks precede the exactly-once binary reads below.
git=[]
for args,expected in [(['rev-parse','--show-toplevel'],str(ROOT)),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding'),(['rev-parse','HEAD'],HEAD),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
 argv=['/usr/bin/git','-c','core.fsmonitor=false']+args
 proc=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=10)
 assert proc.returncode==0 and proc.stdout.strip()==expected
 git.append({'argv':argv,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
for p,digest in watched.items():assert sha(Path(p).read_bytes())==digest,(p,'changed during review')
assert contract['witnesses']=={
 'tsan':{'path':'/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-tsan-native-retry-20261012T020903Z/tsan/witness','sha256':'98bbddbab90890197bebfe79f451d7e5ad6384bd3ad340dc5f47c3b93ad0f018','bytes':35336},
 'tsan-ubsan':{'path':'/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-tsan-repair-native-20261012T025422Z/tsan-ubsan/witness','sha256':'7ddfb29def4c0293f50876a9139429a64bf6ea9d6adcaf02ce62e07c994e3f99','bytes':52152}}
binaries=[]
for name,record in contract['witnesses'].items():
 p=Path(record['path']);before=p.lstat()
 assert p==p.resolve() and stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_nlink==1
 data=p.read_bytes();after=p.lstat()
 assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
 assert len(data)==before.st_size==record['bytes'] and sha(data)==record['sha256']
 magic,cpu,subtype,kind=struct.unpack('<IIII',data[:16]);assert (magic,cpu,kind)==(0xfeedfacf,0x0100000c,2)
 binaries.append({'name':name,**record,'reads':1,'canonical_regular_owned_single_link':True,'stable_during_read':True,'mach_o':'arm64 executable','mode':oct(stat.S_IMODE(before.st_mode))})
result={
 'result':'PASS: corrected preparation; initial P1 closed statically','findings':[],
 'head':HEAD,'candidate_sha256':sha(cache[EV/'candidate.json']),'candidate_inputs_sha256':sha(cache[EV/'candidate-inputs.json']),
 'contract_sha256':sha(cache[EV/'contract.json']),'helper_sha256':sha(cache[ROOT/helper]),
 'initial_review_sha256':initial_hashes['review.json'],'initial_review_copies_verified':initial_hashes,
 'candidate_bindings':len(candidate['evidence']),'input_bindings':len(inputs),'direct_input_hashes':190,
 'source_input_metadata_unchanged':881,'tool_metadata_unchanged':28,'source_tool_abi_reads':0,
 'maintained_deltas':deltas,'unchanged_maintained_files':[f for f in candidate['files'] if f not in deltas],
 'guard_call_lines':guard_calls,'guard_calls_before_mutation_and_after_promotion_recovery_finally':True,
 'static_receipt_rcs':[row['returncode'] for row in static['checks']],'original_acceptance_hashes_reported':19,
 'secret_scan':{'files':18,'raw_rc':1,'transformed_rc':0,'findings':13,'inherited_digest_dispositions_without_SDK_or_binary_reads':oldcount,'new_text_digests_checked':newtexts,'raw_payload_reconstructed':True,'transformed_payload_reconstructed':True,'retained_transformed_report_empty':True,'complete_token_files':[]},
 'git':git,'watched_text_sha256':watched,'binary_reads':len(binaries),'binary_bytes':sum(b['bytes'] for b in binaries),'binary_checks':binaries,
 'not_run':['No promotion, witness execution, actual guard, transaction/recovery, lease/capacity/process census or scanner execution.','No source/build/SDK/toolchain/ABI binary inventory reads; only the two named witnesses were read once each.','No static tasks, native compiler/linker/tool, install, service, container, network, model session, global changes or agents.','No new fresh-session Claude/Codex or full OCI acceptance.']}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':result['result'],'direct_inputs':190,'candidate_bindings':len(candidate['evidence']),'scan_files':18,'binary_reads':len(binaries),'binary_bytes':result['binary_bytes'],'git_rcs':[x['returncode'] for x in git]}))

from pathlib import Path
import copy,hashlib,json,shlex,subprocess,sys
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/core-command-preparation';D=Path(__file__).parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'dev/toolchains'))
from core_commands import CoreCommands,CONFIGS
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def rec(p):return {'path':str(p),'sha256':sha(p),'bytes':Path(p).stat().st_size}
def save(name,data):(D/name).write_text(json.dumps(data,indent=2)+'\n')
expected='68dc847b1ebef3b207f6daec167874605ea0323e4e3dcb2c36ba9d84e5b915f1'
assert sha(R/'dev/toolchains/core_commands.py')==expected
assert sha(E/'harness-contract.json')=='feb0f9700b7ed6828334fb39c6e6d631c87b9be74f4fb9334cdd063b92ecfec8'
assert sha(R/'evidence/core-p2996-preparation/preparation-review.json')=='831a2a6e93d3e45b7a9b520483dd37ffc9970f04ff5f2364b1721cc8fee95f73'
contract=load(E/'harness-contract.json');q=load(R/'evidence/core-skeleton/qualification.json')
refs=[]
for row in contract['prerequisite_references']+contract['selected_recorded_log_references']+load(E/'replay/replay.json')['inputs']:
 p=Path(row['path']);assert sha(p)==row['sha256'];refs.append(rec(p))
assert len(contract['prerequisite_references'])==13 and len(contract['selected_recorded_log_references'])==4
copies=[]
for row in load(E/'replay-manifest.json')['files']:
 for key in ['source','path']:
  p=Path(row[key]);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'];copies.append(rec(p))
for row in load(E/'parent-checks.json'):
 assert row['returncode']==0
 for log in row['logs']:assert sha(Path(log['path']))==log['sha256']
for row in contract['source_input_contract']:assert sha(Path(row['path']))==row['patched_sha256']
post=load(E/'source-preparation-postcommit.json');assert post['head']=='fd7c9cdf54ddf702c0e48348302d73cc6853346b' and post['status']=='' and post['commit']['returncode']==post['baseline']['returncode']==0
assert load(R/'evidence/core-p2996-preparation/preparation-review.json')['findings']==[]
source=E/'replay/replay.py.source';assert sha(source)=='28d741a75febe34e66b56bff623371534c65723dee64e88e7ab45d264146b2fb'
replay_dir=D/'exact-parent-replay';replay_dir.mkdir();replay=replay_dir/'replay.py';replay.write_bytes(source.read_bytes())
argv=[sys.executable,'-B',str(replay)];p=subprocess.run(argv,cwd=replay_dir,capture_output=True,timeout=30)
for name,data in [('stdout',p.stdout),('stderr',p.stderr)]:(replay_dir/('replay.'+name)).write_bytes(data)
save('exact-replay-execution.json',{'argv':argv,'cwd':str(replay_dir),'returncode':p.returncode,'files':[rec(f) for f in sorted(replay_dir.iterdir())]})
assert p.returncode==0 and not p.stderr
assert sha(replay_dir/'replay.json')=='a5579347f5b556f22c36f46578c34a6773ad10396947c280bb45e9cf3bf39973'
prefix=Path(contract['lane_specs']['p2996']['prefix']);sdk='/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk'
build=D/'synthetic-p2996-static';cmake=q['tools']['cmake']['path']
def validator():return CoreCommands(R,build,'p2996',prefix,sdk,cmake,'/usr/bin/ar',prefix/'bin/llvm-ranlib',False)
rows=copy.deepcopy(q['static_compile_commands'])
extra=contract['lane_specs']['p2996']['common_compile_tokens'][:8]
for row in rows:
 args=shlex.split(row['command']);assert args[-10:-4][0]=='-fmodules-ts'
 args=args[:-10]+args[-4:];args=[a for a in args if a!='-fno-declone-ctor-dtor']
 args[0]=str(prefix/'bin/clang++');args=args[:1]+extra+args[1:]
 row.update(directory=str(build),command=shlex.join(args),output=args[-3])
assert len(validator().compile_database(rows))==8
mutated=copy.deepcopy(rows);args=shlex.split(mutated[0]['command']);before=args[:];i=args.index('-Werror');assert i>args.index('-isystem')
args.insert(i,'-isystem');mutated[0]['command']=shlex.join(args)
accepted=False;error=None
try:validator().compile_database(mutated);accepted=True
except Exception as exc:error=repr(exc)
source_contract=load(R/'evidence/p2996-analysis/source-contract.json');options=Path(source_contract['source_root'])/'clang/include/clang/Driver/Options.td';lines=options.read_text().splitlines()
locations=[i for i,line in enumerate(lines,1) if line.startswith('def isystem :')]
assert len(locations)==1
n=locations[0];excerpt='\n'.join(f'{i}: {lines[i-1]}' for i in range(n,n+5))
save('initial-parser-review.json',{'candidate':rec(R/'dev/toolchains/core_commands.py'),'contract':rec(E/'harness-contract.json'),'verified_reference_records':refs,'parent_copy_records':copies,'parent_static_checks_verified':True,'exact_replay_returncode':p.returncode,'exact_replay_json':rec(replay_dir/'replay.json'),'synthetic_baseline_rows':8,'mutation':{'kind':'synthetic P2996 CDB row; no native compiler invocation','source_row_file':rows[0]['file'],'change':'Insert a second -isystem immediately before the required -Werror token, after the original private include pair.','argv_before':before,'argv_after':args,'expected':'reject','accepted':accepted,'error':error,'primary_option_definition':rec(options),'primary_option_excerpt':excerpt},'native_builds':0})
save('synthetic-baseline-rows.json',rows);save('synthetic-mutated-rows.json',mutated)
assert sha(R/'dev/toolchains/core_commands.py')==expected
print(json.dumps({'exact_parent_replay_rc':p.returncode,'replay_positive':16,'replay_negative':22,'baseline_rows':8,'mutation_accepted':accepted,'primary_option_excerpt':excerpt,'directory':str(D)}))

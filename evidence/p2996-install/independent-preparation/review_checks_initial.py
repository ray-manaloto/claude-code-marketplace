from pathlib import Path
import ast,datetime,hashlib,json,os,subprocess,sys
root=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');out=Path(sys.argv[1]);os.umask(0o077)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
helper=root/'dev/toolchains/p2996_install.py';helper_sha='5389d8c5a6f422eb6006f16902728e64dcc7d1303819047417472613be5a99d3';assert sha(helper)==helper_sha
built=root/'evidence/p2996-math-resume';qualified=load(built/'operation/qualification.json');config=qualified['proposal']['configuration']
env={'HOME':str(Path.home()),'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','TMPDIR':os.environ.get('TMPDIR','/private/tmp'),'LANG':'C','TERM':'dumb','NO_COLOR':'1','PYTHONDONTWRITEBYTECODE':'1','MARKETPLACE_MISE_BIN':config['mise']['path'],'MARKETPLACE_PYTHON':sys.executable,'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0','PWF_PLAN_ROOT':str(root),'PLAN_ID':'2026-10-10-marketplace-macos-reflection-scaffold'}
commands=[]
def run(label,argv,cwd='/private/tmp'):
 start=datetime.datetime.now(datetime.timezone.utc);a=out/(label+'.stdout');b=out/(label+'.stderr')
 with a.open('wb') as stdout,b.open('wb') as stderr:
  r=subprocess.run(list(map(str,argv)),cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,timeout=60)
 row={'label':label,'argv':list(map(str,argv)),'cwd':str(cwd),'returncode':r.returncode,'started_at':start.isoformat(),'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'logs':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in (a,b)]};commands.append(row)
 assert r.returncode==0,(label,r.returncode,b.read_text()[:1500])
 return a.read_bytes()
old_sha='ef179e70c3bf2daa804c077a810cff8f1912bb41c4e89c60f55d488abf8f9ecd'
old=run('prior-reviewed-helper',['/usr/bin/git','-C',root,'show','c43021fb998d05f7ca0036bd6da8b6ba8964798a:dev/toolchains/p2996_build.py'])
assert hashlib.sha256(old).hexdigest()==old_sha
frozen=built/'operation/p2996_build.py.source';assert sha(frozen)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
fn=lambda data,name:next(n for n in ast.walk(ast.parse(data)) if isinstance(n,ast.FunctionDef) and n.name==name)
dump=lambda n:ast.dump(n,include_attributes=False)
run_equal=dump(fn(old,'run'))==dump(fn(frozen.read_bytes(),'run'));interrupt_equal=dump(fn(old,'interrupted'))==dump(fn(helper.read_bytes(),'interrupted'));assert run_equal and interrupt_equal
prior_review=root/'evidence/p2996-build/preparation-review.json';assert sha(prior_review)=='ae823e2297df60e333e8e9f9d4ae83cb6ac200d6e6cdd5931be337142c5ef2cf'
cleanup=root/'evidence/p2996-build/independent-preparation/final-runtime-controls.json';assert sha(cleanup)=='1b484f8cd99f9770621a4ff21d1d66d69135007a28e3620388188756a2eb9603'
previous=load(cleanup);assert previous['result']=='PASS' and previous['helper_sha256']==old_sha and all(r['pass'] for r in previous['cases'])
run('tasks-validate',[root/'dev/mise','tasks','validate'])
static=run('static-original19',[root/'dev/mise','run','check:acceptance-baseline'])
static_result=json.loads(static);assert static_result['status']=='pass' and static_result['checks']['baseline']==19
sys.path.insert(0,str(root/'dev/toolchains'))
from gcc_install import preserved,digest
from mise_link_probe import snapshot
from vcpkg_register import install_entries
baseline=load(built/'independent-build/post-state.json');inventory=load(built/'independent-build/post-build-inventory.json')
workspace=Path(qualified['proposal']['workspace']);build=workspace/'build';prefix=workspace/'prefix'
manifests=[build/'install_manifest.txt',build/'runtimes/builtins-bins/install_manifest.txt',build/'runtimes/runtimes-bins/install_manifest.txt']
preserve_scope={'baseline':baseline,'inventory':inventory,'prefix':prefix,'manifests':manifests,'preserved':preserved,'snapshot':snapshot,'install_entries':install_entries,'digest':digest,'Path':Path,'os':os}
exec(compile(ast.Module(body=[fn(helper.read_bytes(),'protected')],type_ignores=[]),str(helper),'exec'),preserve_scope);preserve_scope['protected']()
mode_checks=[]
for row in inventory['records']:
 p=Path(row['path'])
 if p==prefix or p in manifests or not os.path.lexists(p):continue
 for key,value in (('lstat_mode',oct(p.lstat().st_mode&0o777)),('mode',oct(p.stat().st_mode&0o777)) if p.exists() else ('unused',None)):
  if key in row:assert row[key]==value,(str(p),key);mode_checks.append([str(p),key])
 if 'bytes' in row:assert p.stat().st_size==row['bytes']
assert not os.path.lexists(prefix) and all(not os.path.lexists(p) for p in manifests)
parent=root/'evidence/p2996-install';manifest=load(parent/'preparation-manifest.json');copy_checks=[]
for record in manifest['files']:
 for p in (Path(record['source']),root/record['copy']):
  assert sha(p)==record['sha256'] and p.stat().st_size==record['bytes'],str(p)
 copy_checks.append(record)
prep=load(parent/'preparation/qualification.json');own=load(out/'native-preparation/qualification.json');assert prep['proposal']==own['proposal']
verified_logs=[]
for folder,report in ((parent/'preparation',prep),(out/'native-preparation',own)):
 assert len(report['commands'])==7 and all(c['returncode']==0 for c in report['commands'])
 for row in report['commands']:
  for log in row['logs']:
   p=folder/Path(log['path']).name;assert sha(p)==log['sha256'];verified_logs.append({'path':str(p),'sha256':sha(p)})
identity=run('final-identity',['/usr/bin/git','-C',root,'rev-parse','--verify','HEAD']).decode().strip();assert identity=='628c0921cdbbc9bfdfebb6a5187ed611c9889cb8'
status=run('final-status',['/usr/bin/git','-C',root,'status','--porcelain=v1']).decode()
assert sha(helper)==helper_sha
maintained=['dev/toolchains/p2996_install.py','docs/status.md','docs/p2996-toolchain.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
report={'result':'PASS','helper_sha256':helper_sha,'identity':{'head':identity,'branch':'codex/marketplace-native-onboarding','root':str(root),'common_git_directory':'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git','status':status},'commands':commands,'static_original19':static_result,'prior_cleanup_reuse':{'prior_commit':'c43021fb998d05f7ca0036bd6da8b6ba8964798a','prior_helper_sha256':old_sha,'current_frozen_helper_sha256':sha(frozen),'run_ast_equal':run_equal,'run_ast_sha256_python315':hashlib.sha256(dump(fn(old,'run')).encode()).hexdigest(),'interrupted_ast_equal':interrupt_equal,'prior_review':{'path':str(prior_review),'sha256':sha(prior_review)},'cleanup_receipt':{'path':str(cleanup),'sha256':sha(cleanup)},'case_count_reused':len(previous['cases']),'prior_controls_rerun':False},'preservation':{'result':'PASS','direct_comparisons':1,'retained_record_count':len(inventory['records']),'additional_mode_comparisons':len(mode_checks),'prefix_absent':True,'all_three_manifests_absent':True,'scope':'Reviewed protected files, directory snapshots and managed install listing; 114 scoped build/source/tool records, plus their recorded modes and byte counts. No broader inventory.'},'parent_copy_records_verified':copy_checks,'native_log_hashes_verified':verified_logs,'proposal_matches_parent':True,'maintained_preimages':[{'path':str(root/p),'sha256':sha(root/p),'bytes':(root/p).stat().st_size} for p in maintained],'findings':[]}
receipt=out/'review-checks.json';receipt.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'result':'PASS','receipt':str(receipt),'sha256':sha(receipt),'command_count':len(commands),'static':static_result,'preservation':report['preservation'],'run_ast_equal':run_equal,'parent_copy_records':len(copy_checks),'native_logs':len(verified_logs)},indent=2))


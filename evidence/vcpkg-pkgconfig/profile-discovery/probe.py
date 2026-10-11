import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
sys.path.insert(0,str(ROOT/'dev/toolchains'))
from gcc_install import read,census,digest
from mise_renovate import protected
from mise_runtime import load
D=Path(__file__).parent
report={'scope':'Guarded read-only filesystem lookup under existing named profiles; no pkg-config, compiler or dependency execution','commands':[],'helper_sha256':digest(Path(__file__))}
def save(): (D/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
normal=read('install-preimages.json')['normal_environment']['argv']
env=load(Path(normal[-1]).parent/'context.json')['environment']|{'MISE_OFFLINE':'1','MISE_AUTO_INSTALL':'0','MISE_EXEC_AUTO_INSTALL':'0','MISE_TASK_RUN_AUTO_INSTALL':'0','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_TERMINAL_PROMPT':'0','GIT_OPTIONAL_LOCKS':'0'}
for k in list(env):
 if k.startswith(('VCPKG_','X_VCPKG_')) or k in ('MARKETPLACE_P2996_PREFIX','MARKETPLACE_GCC16_PREFIX'):env.pop(k)
(D/'cwd').mkdir();(D/'tmp').mkdir()
profile=D/'private.sb';profile.write_text('(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(D))+') (literal "/dev/null"))\n(deny network*)\n')
def run(label,argv):
 start=time.monotonic();p=subprocess.run([str(a) for a in argv],cwd=D/'cwd',env=env,capture_output=True,text=True,timeout=60)
 for suffix,text in [('stdout',p.stdout),('stderr',p.stderr)]: (D/(label+'.'+suffix)).write_text(text)
 report['commands'].append({'case':label,'argv':[str(a) for a in argv],'returncode':p.returncode,'seconds':time.monotonic()-start,'stdout_sha256':digest(D/(label+'.stdout')),'stderr_sha256':digest(D/(label+'.stderr'))});save();assert p.returncode==0;return p.stdout
try:
 assert digest(ROOT/'evidence/vcpkg-private-retry/contract.json')=='1099e0df49d3a6e022f76297424b0456365333700c086d1d0d7a1905f03bfda5'
 contract=load(ROOT/'evidence/vcpkg-private-retry/contract.json');assert all(digest(ROOT/p)==s for p,s in contract['inputs'].items());assert all(digest(Path(p))==s for p,s in contract['tools'].items())
 current=protected();report['writer_census_before']=census();report['protected_before']=True
 assert run('default-before',normal)==(ROOT/contract['default_profile']).read_text()
 probe="import hashlib,json,os,shutil;print(json.dumps({'home':os.environ.get('HOME'),'path_sha256':hashlib.sha256(os.environ.get('PATH','').encode()).hexdigest(),'path_components':len(os.environ.get('PATH','').split(os.pathsep)),'tools':{n:shutil.which(n) for n in ['pkg-config','pkgconf']},'pkg_config_override_defined':'PKG_CONFIG' in os.environ}))"
 report['discovery']={}
 for lane,prefix in contract['prefixes'].items():
  for k in ('MARKETPLACE_P2996_PREFIX','MARKETPLACE_GCC16_PREFIX'):env.pop(k,None)
  env['MARKETPLACE_'+lane.upper()+'_PREFIX']=prefix
  argv=[current['path'],'--no-hooks','-C',D/'cwd','-E',lane,'exec','--fresh-env','--no-deps','--']
  assert run(lane+'-profile',argv+normal[-2:])==(ROOT/contract['profiles'][lane]).read_text()
  result=json.loads(run(lane+'-lookup',argv+['/usr/bin/sandbox-exec','-f',profile,sys.executable,'-B','-c',probe]));assert result['home']==str(Path.home());report['discovery'][lane]=result
 for k in ('MARKETPLACE_P2996_PREFIX','MARKETPLACE_GCC16_PREFIX'):env.pop(k,None)
 assert run('default-after',normal)==(ROOT/contract['default_profile']).read_text()
 report['state']='PASS: existing profile discovery only'
except BaseException as error:
 report.update(state='FAIL',error=repr(error));raise
finally:
 try:protected();report['writer_census_after']=census();report['protected_after']=True
 except BaseException as error:report.update(state='FAIL',preservation_error=repr(error));raise
 finally:save();print(json.dumps({'state':report.get('state'),'discovery':report.get('discovery'),'receipt':str(D/'qualification.json')}),flush=True)

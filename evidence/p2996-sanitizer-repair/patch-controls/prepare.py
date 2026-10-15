from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
ev=root/'evidence/p2996-sanitizer-repair'
meta=json.loads((ev/'patch-inputs.json').read_text())
directory=Path(__file__).parent
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(meta['source'])==meta['before_sha256']
assert digest(root/meta['patch'])==meta['patch_sha256']
report={'state':'running','commands':[],'compiler_executed':False}
profile=directory/'private.sb'
profile.write_text('(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(directory))+') (literal "/dev/null"))\n(deny network*)\n')
tree=directory/'patch-controls'; source=tree/meta['source_relative']; source.parent.mkdir(parents=True)
source.write_bytes(Path(meta['source']).read_bytes())
argv=['/usr/bin/sandbox-exec','-f',str(profile),'/usr/bin/git','-C',str(tree),'apply','--unidiff-zero']
env={'PATH':'/usr/bin:/bin','HOME':str(Path.home()),'LANG':'C','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_TERMINAL_PROMPT':'0','GIT_OPTIONAL_LOCKS':'0'}
def run(label,flags,expected):
 command=argv+flags+[str(root/meta['patch'])]
 started=time.monotonic(); cp=subprocess.run(command,env=env,cwd=directory,capture_output=True,timeout=20)
 files=[]
 for suffix,value in (('stdout',cp.stdout),('stderr',cp.stderr)):
  p=directory/(label+'.'+suffix);p.write_bytes(value);files.append({'path':str(p),'sha256':digest(p)})
 report['commands'].append({'case':label,'argv':command,'returncode':cp.returncode,'expected':expected,'elapsed_seconds':time.monotonic()-started,'logs':files})
 assert cp.returncode==expected
try:
 run('reverse-original',['--reverse','--check'],1)
 assert digest(source)==meta['before_sha256']
 run('apply-check',['--check'],0);run('apply',[],0)
 assert digest(source)==meta['after_sha256']
 run('apply-twice',['--check'],1)
 assert digest(source)==meta['after_sha256']
 run('reverse-check',['--reverse','--check'],0);run('reverse',['--reverse'],0)
 assert digest(source)==digest(meta['source'])==meta['before_sha256']
 report.update(state='PASS: exact patch/reverse and rejection controls',shared_source_unchanged=True)
finally:
 path=directory/'patch-controls.json';path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'receipt':str(path),'sha256':digest(path),'state':report['state']}))

import ast, hashlib, io, json, os, posixpath, tarfile
from pathlib import Path,PurePosixPath
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');D=Path(__file__).parent
helper=R/'dev/toolchains/pkgconf_prepare.py'; supporting=R/'dev/toolchains/gcc_bottles.py'
assert hashlib.sha256(helper.read_bytes()).hexdigest()=='754a800bfbe7ed96fefe3baa630e2052575a65a70dd1c5b05443444f9f65b0db'
node=next(n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='inspect')
old=ast.parse(supporting.read_text()); shared=[n for n in old.body if isinstance(n,ast.FunctionDef) and n.name in ['digest','preimage']]
constants={t.id:ast.literal_eval(n.value) for n in old.body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Name) and t.id in ['BOOTSTRAP_DIRS','LINK_DIRS']}
namespace={'hashlib':hashlib,'os':os,'posixpath':posixpath,'tarfile':tarfile,'Path':Path,'PurePosixPath':PurePosixPath,**constants}
exec(compile(ast.Module(body=shared+[node],type_ignores=[]),str(helper),'exec'),namespace)
original_preimage=namespace['preimage']
def snapshot(directory):
 result={}
 for p in sorted(directory.rglob('*')):
  if p.is_file(): result[str(p.relative_to(directory))]=hashlib.sha256(p.read_bytes()).hexdigest()
  elif p.is_dir(): result[str(p.relative_to(directory))]='directory'
  else: result[str(p.relative_to(directory))]='unexpected'
 return result
results=[]
for name in ['valid','absolute_path','dotdot_path','escaping_symlink','duplicate_member','existing_destination']:
 case=D/('fixture-'+name);case.mkdir();prefix=case/'prefix';prefix.mkdir();archive=case/'fixture.tar.gz'
 entries=[('pkgconf/3.0.8','dir',''),('pkgconf/3.0.8/bin/pkgconf','file','payload')]
 if name=='valid': entries.append(('pkgconf/3.0.8/bin/pkg-config','link','pkgconf'))
 elif name=='absolute_path': entries.append(('/pkgconf/3.0.8/bin/other','file','other'))
 elif name=='dotdot_path': entries.append(('pkgconf/3.0.8/bin/../../escape','file','other'))
 elif name=='escaping_symlink': entries.append(('pkgconf/3.0.8/bin/other','link','../../../escape'))
 elif name=='duplicate_member': entries.append(('pkgconf/3.0.8/bin/pkgconf','file','second'))
 elif name=='existing_destination':
  (prefix/'bin').mkdir();(prefix/'bin/pkgconf').write_bytes(b'preserve existing\n')
 with tarfile.open(archive,'w:gz') as tar:
  for path,kind,payload in entries:
   m=tarfile.TarInfo(path);m.mode=0o755 if kind=='dir' else 0o644
   if kind=='dir':m.type=tarfile.DIRTYPE;tar.addfile(m)
   elif kind=='link':m.type=tarfile.SYMTYPE;m.linkname=payload;tar.addfile(m)
   else:
    b=payload.encode();m.size=len(b);tar.addfile(m,io.BytesIO(b))
 namespace['PREFIX']=prefix
 reads=[]
 def confined_preimage(path):
  path=Path(path);assert path.is_relative_to(prefix),str(path);reads.append(str(path));return original_preimage(path)
 namespace['preimage']=confined_preimage
 before=snapshot(case)
 try:
  report=namespace['inspect'](archive,'3.0.8');outcome='accepted'
 except AssertionError: outcome='rejected'
 expected='accepted' if name=='valid' else 'rejected';assert outcome==expected,(name,outcome)
 if name=='valid':
  assert len(report['members'])==3 and len(report['prefix_writes'])==4 and report['materializations']=={}
 assert snapshot(case)==before,name
 results.append({'case':name,'outcome':outcome,'expected':expected,'candidate_preimage_reads':len(reads),'all_preimage_reads_scratch_confined':True,'fixture_unchanged':True})
result={'result':'PASS','synthetic_inspect_calls':6,'native_operations':0,'candidate_module_imports':0,'full_or_live_inventories':0,'cases':results,'scope':'AST-only inspect plus original digest/preimage; all PREFIX reads and fixtures scratch-only. No extraction.'}
(D/'controls.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

import ast,hashlib,json,os,tempfile
from pathlib import Path
root=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');out=Path(__file__).parent;helper=root/'dev/toolchains/pkgconf_install.py';scope={'Path':Path,'os':os}
for filename,names in [('dev/toolchains/gcc_bottles.py',['digest','preimage']),('dev/toolchains/pkgconf_install.py',['children','validate_prefix'])]:
 scope['hashlib']=hashlib
 nodes=[n for n in ast.parse((root/filename).read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names]
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(root/filename),'exec'),scope)
rows=[]
for case,expected in [('before_clean',True),('before_collision',False),('old_neighbor_change',False),('after_valid',True),('after_extra_sibling',False),('after_wrong_link',False),('after_absolute_link',False),('after_old_directory_mode_change',False)]:
 fixture=out/case;fixture.mkdir();old=fixture/'old';old.write_text('preserve');target=fixture/'new';before={str(fixture):scope['children'](fixture)};state=scope['preimage'](fixture);manifest={'parent_preimages':{str(fixture):state},'control_preimages':{},'prefix_writes':{str(target):{'preimage':{'kind':'absent'},'target':str(fixture/'keg-file')}}};installed=case.startswith('after')
 if installed:target.symlink_to('keg-file')
 if case=='before_collision':target.write_text('occupied')
 if case=='old_neighbor_change':old.write_text('changed')
 if case=='after_extra_sibling':(fixture/'extra').write_text('new')
 if case=='after_wrong_link':target.unlink();target.symlink_to('wrong')
 if case=='after_absolute_link':target.unlink();target.symlink_to(str(fixture/'keg-file'))
 if case=='after_old_directory_mode_change':fixture.chmod(0o700)
 try:scope['validate_prefix'](manifest,before,installed);accepted=True
 except AssertionError:accepted=False
 assert accepted==expected,case;rows.append({'case':case,'accepted':accepted,'expected':expected})
(out/'controls.json').write_text(json.dumps({'result':'PASS','scope':'Eight final prefix guards after stricter relative-link and new-owner checks; no native/shared reads or writes','helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'cases':rows},indent=2)+'\n');print(json.dumps({'result':'PASS','cases':len(rows)}))

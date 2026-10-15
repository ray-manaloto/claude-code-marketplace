from pathlib import Path
from types import SimpleNamespace
import ast, hashlib, json, os, stat
D=Path(__file__).parent
helper=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/dev/toolchains/p2996_asan_runtime.py')
b=helper.read_bytes()
assert hashlib.sha256(b).hexdigest()=='c390c4615eeb2a023dc9bd255b18e2a9425a69f38712c79c126f327825e8c40c'
nodes=[n for n in ast.parse(b).body if isinstance(n,ast.FunctionDef) and n.name in ('identity','replace_exact')]
assert len(nodes)==2
scope={'os':os,'stat':stat,'digest':lambda p:hashlib.sha256(p.read_bytes()).hexdigest()}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),scope)
rows=[]
for side in ('source','destination'):
 staged=D/(side+'-staged.fixture');destination=D/(side+'-destination.fixture')
 staged.write_bytes(b'new private fixture\n');destination.write_bytes(b'old private fixture\n')
 staged.chmod(0o755);destination.chmod(0o755)
 after=scope['identity'](staged);before=scope['identity'](destination)
 (staged if side=='source' else destination).chmod(0o4755)
 pre_modes={'source':oct(stat.S_IMODE(staged.stat().st_mode)),'destination':oct(stat.S_IMODE(destination.stat().st_mode))}
 assert pre_modes[side]=='0o4755'
 scope['replace_exact'](staged,destination,before,after)
 rows.append({'special_mode_side':side,'pre_modes':pre_modes,'replacement_accepted':True,'destination_actual_mode':oct(stat.S_IMODE(destination.stat().st_mode)),'destination_reported_mode':scope['identity'](destination)['mode'],'staged_consumed':not staged.exists()})
assert rows[0]['destination_actual_mode']=='0o4755' and all(r['destination_reported_mode']=='0o755' for r in rows)
result={'result':'CONFIRMED: unexpected special modes accepted','helper_sha256':hashlib.sha256(b).hexdigest(),'cases':rows,'scope':'Two tiny new private fixtures only; no module imports, installed paths, shared state or runtime execution'}
(D/'mode-control.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

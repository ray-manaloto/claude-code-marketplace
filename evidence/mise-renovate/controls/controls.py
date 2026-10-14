from pathlib import Path
import copy,hashlib,json,sys
from unittest.mock import patch
r=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');sys.path.insert(0,str(r/'dev/toolchains'));import mise_renovate as m
root=Path(__file__).parent;results=[];data=m.contract();baseline=m.load(r/m.BASELINE);original=copy.deepcopy(baseline);current=m.load(r/'evidence/mise-renovate/inventory/current-metadata.json')
expected=copy.deepcopy(baseline);expected['install_entries']=current['install_entries']
for name in ('config.toml','mise.lock'):expected['protected']['global_files'][name]={k:current['global_files'][name][k] for k in ('mode','sha256')}
assert m.overlay(baseline,data)==expected and baseline==original;results.append({'case':'exact-observed-overlay-preserves-other-baseline-data','pass':True})
def reject(name,change):
 b,d=copy.deepcopy(baseline),copy.deepcopy(data);change(b,d)
 try:m.overlay(b,d)
 except AssertionError:results.append({'case':name,'pass':True,'observed':'rejected'})
 else:raise AssertionError(name)
reject('wrong-historical-hash',lambda b,d:b['protected']['global_files']['config.toml'].update(sha256='0'*64))
reject('changed-protected-mode',lambda b,d:d['global_updates']['config.toml']['current'].update(mode='0o644'))
reject('extra-global-file',lambda b,d:d['global_updates'].update({'config.p2996.toml':copy.deepcopy(d['global_updates']['config.toml'])}))
reject('extra-install-update',lambda b,d:d['install_updates'].update({'unreviewed/1':{'previous':None,'current':{'mode':'0o755','link':None}}}))
reject('missing-renovate-addition',lambda b,d:d['install_updates'].pop('npm-renovate/44.150.0'))
reject('existing-new-alias-preimage',lambda b,d:b['install_entries'].update({next(iter(d['global_aliases'])):{'mode':'0o755','link':'./unexpected'}}))
reject('alias-outside-tool',lambda b,d:next(iter(d['global_aliases'].values())).update(link='../outside'))
reject('alias-wrong-mode',lambda b,d:next(iter(d['global_aliases'].values())).update(mode='0o700'))
selected={}
def intercept(path,name,scope):
 assert path==Path(m.previous.__file__) and name=='protected'
 assert all(scope[k] is v for k,v in vars(m.previous).items() if k!='load')
 assert scope['load'](r/m.BASELINE)==expected
 assert scope['load'](r/'evidence/mise-runtime/contract.json')==m.load(r/'evidence/mise-runtime/contract.json')
 selected['used']=True
 return lambda:{'delegated':True}
with patch.object(m,'contract',return_value=data),patch.object(m,'semantic_check'),patch.object(m,'function',side_effect=intercept):assert m.protected()=={'delegated':True}
assert selected['used'];results.append({'case':'delegate-unchanged-legacy-guards-with-only-bound-baseline-loader','pass':True})
fixture=root/'fixture';(fixture/'.config/mise').mkdir(parents=True);(fixture/'backups').mkdir();fake=copy.deepcopy(data)
contents={'config.toml':'[tools."npm:renovate"]\nversion = "44.149.3"\n[tools.cmake]\nversion = "4.4.4"\n','mise.lock':'[[tools."npm:renovate"]]\nversion = "44.149.3"\nspecifiers = ["44.149.3"]\n[[tools.cmake]]\nversion = "4.4.4"\n'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,text in contents.items():
 old,new=fixture/'backups'/name,fixture/'.config/mise'/name;old.write_text(text);new.write_text(text.replace('44.149.3','44.150.1'));fake['global_updates'][name]={'previous':{'sha256':sha(old),'mode':'0o600'},'current':{'sha256':sha(new),'mode':'0o600'},'backup':str(old)}
with patch.object(m.Path,'home',return_value=fixture):m.semantic_check(fake)
results.append({'case':'exact-three-semantic-version-fields','pass':True})
for name in contents:
 p=fixture/'.config/mise'/name;saved=p.read_text();p.write_text(saved.replace('4.4.4','4.4.5'));candidate=copy.deepcopy(fake);candidate['global_updates'][name]['current']['sha256']=sha(p)
 try:
  with patch.object(m.Path,'home',return_value=fixture):m.semantic_check(candidate)
 except AssertionError:results.append({'case':'reject-unrelated-semantic-change-'+name,'pass':True})
 else:raise AssertionError(name)
 p.write_text(saved)
assert baseline==original
(root/'results.json').write_text(json.dumps({'cases':results,'helper_sha256':sha(Path(m.__file__)),'contract_sha256':sha(m.EVIDENCE/'contract.json'),'original_baseline_unchanged':True,'native_commands':0},indent=2)+'\n');print(json.dumps({'cases':len(results),'pass':all(x['pass'] for x in results)}))

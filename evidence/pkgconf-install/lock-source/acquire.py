import hashlib,json,urllib.request
from pathlib import Path
root=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');out=Path(__file__).parent;commit='b671d356aaf33b87e48e7469a77abb40c3553c68';tree=json.loads((root/'evidence/vcpkg-pkgconfig/source/mise-tree.json').read_text());rows=[]
for path in ['src/lock_file.rs','crates/mise-util/src/lock_file.rs']:
 entry=next(r for r in tree['tree'] if r['path']==path);url='https://raw.githubusercontent.com/jdx/mise/'+commit+'/'+path
 with urllib.request.urlopen(url,timeout=45) as response:data=response.read()
 blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==entry['sha'];dest=out/(path.replace('/','-')+'.source');dest.write_bytes(data);rows.append({'url':url,'source_path':path,'file':dest.name,'sha256':hashlib.sha256(data).hexdigest(),'git_blob':blob,'bytes':len(data)})
(out/'acquisition.json').write_text(json.dumps({'result':'PASS','commit':commit,'records':rows},indent=2)+'\n');print(json.dumps({'result':'PASS','files':len(rows)}))

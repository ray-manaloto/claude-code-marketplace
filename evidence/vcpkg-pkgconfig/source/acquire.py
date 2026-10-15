from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,urllib.request,re
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');D=Path(__file__).parent
report={'state':'running','scope':'Primary source acquisition for the source-identified pkg-config prerequisite; no comparative research or installation','route':'native fnox codex_research profile; Python urllib','records':[]}
def save(): (D/'acquisition.json').write_text(json.dumps(report,indent=2)+'\n')
def fetch(url,name):
 assert url.startswith(('https://formulae.brew.sh/api/formula/','https://api.github.com/repos/jdx/mise/','https://raw.githubusercontent.com/Homebrew/homebrew-core/','https://raw.githubusercontent.com/jdx/mise/'))
 row={'url':url,'path':str(D/name)};report['records'].append(row);save()
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'marketplace-tool-foundation'})
  with urllib.request.urlopen(req,timeout=35) as r:data=r.read(15000001);row['http_status']=r.status
  assert len(data)<=15000000
  p=D/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest());save();return data
 except BaseException as error:row['error_type']=type(error).__name__;row['http_status']=getattr(error,'code',None);save();raise
try:
 f=json.loads(fetch('https://formulae.brew.sh/api/formula/pkgconf.json','formulae/pkgconf.json'));assert f['name']=='pkgconf'
 head=f['tap_git_head'];assert re.fullmatch('[0-9a-f]{40}',head)
 fetch('https://raw.githubusercontent.com/Homebrew/homebrew-core/'+head+'/Formula/p/pkgconf.rb','homebrew-source/pkgconf.rb.source')
 fetch('https://raw.githubusercontent.com/Homebrew/homebrew-core/'+head+'/LICENSE.txt','homebrew-source/LICENSE.txt.source')
 tag=json.loads(fetch('https://api.github.com/repos/jdx/mise/git/ref/tags/v2026.10.8','mise-tag.json'))['object']
 if tag['type']=='tag':tag=json.loads(fetch('https://api.github.com/repos/jdx/mise/git/tags/'+tag['sha'],'mise-annotated-tag.json'))['object']
 assert tag['type']=='commit';commit=tag['sha'];tree=json.loads(fetch('https://api.github.com/repos/jdx/mise/git/trees/'+commit+'?recursive=1','mise-tree.json'));assert not tree.get('truncated')
 index={r['path']:r for r in tree['tree']};comparisons=[];prefix='evidence/gcc-bootstrap/mise-source/'
 for receipt in ['source-acquisition.json','closure-acquisition.json']:
  for row in json.loads((ROOT/'evidence/gcc-bootstrap'/receipt).read_text())['records']:
   if not row['path'].startswith(prefix):continue
   old=ROOT/row['path'];data=old.read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'];path=row['path'][len(prefix):].removesuffix('.source');actual=index[path];assert actual['type']=='blob';blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();entry={'source':path,'old_path':row['path'],'old_sha256':row['sha256'],'old_blob_sha1':blob,'current_blob_sha1':actual['sha'],'unchanged':blob==actual['sha']}
   if not entry['unchanged']:
    new=fetch('https://raw.githubusercontent.com/jdx/mise/'+commit+'/'+path,'mise-source/'+path+'.source');assert hashlib.sha1(b'blob '+str(len(new)).encode()+b'\0'+new).hexdigest()==actual['sha'];entry['current_sha256']=hashlib.sha256(new).hexdigest();entry['current_path']=str(D/'mise-source'/(path+'.source'))
   comparisons.append(entry)
 report.update(state='PASS',recorded_at=datetime.now(timezone.utc).isoformat(),mise_tag='v2026.10.8',mise_commit=commit,source_comparison=comparisons,pkgconf={'version':f['versions']['stable'],'revision':f['revision'],'dependencies':f['dependencies'],'keg_only':f['keg_only'],'tap_git_head':head,'arm64_tahoe':f['bottle']['stable']['files'].get('arm64_tahoe')},research_coverage='Exa, Firecrawl, Last30Days and Context7 were not rerun. Earlier quota/fallback/validator gaps remain incomplete. This is exact primary source acquisition, not a strict-five pass.');save();print(json.dumps({'state':report['state'],'mise_commit':commit,'unchanged_sources':sum(r['unchanged'] for r in comparisons),'changed_sources':[r['source'] for r in comparisons if not r['unchanged']],'pkgconf':report['pkgconf'],'receipt':str(D/'acquisition.json')}),flush=True)
except BaseException as error:report.update(state='FAIL',error_type=type(error).__name__);save();raise

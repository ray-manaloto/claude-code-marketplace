from pathlib import Path
import hashlib,json,urllib.request
D=Path(__file__).parent;fpath=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/evidence/vcpkg-pkgconfig/source/formulae/pkgconf.json');f=json.loads(fpath.read_text());assert f['name']=='pkgconf' and f['versions']['stable']=='3.0.8' and f['revision']==0 and not f['dependencies'];b=f['bottle']['stable']['files']['arm64_tahoe'];assert b['url']=='https://ghcr.io/v2/homebrew/core/pkgconf/blobs/sha256:'+b['sha256']
r={'state':'running','url':b['url'],'expected_sha256':b['sha256'],'formula_sha256':hashlib.sha256(fpath.read_bytes()).hexdigest(),'archive_extracted':False}
def save():(D/'acquisition.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 p=D/'pkgconf-3.0.8.tar.gz';request=urllib.request.Request(b['url'],headers={'Authorization':'Bearer QQ==','User-Agent':'marketplace-tool-foundation'})
 with urllib.request.urlopen(request,timeout=40) as response,p.open('xb') as out:
  r['http_status']=response.status
  while block:=response.read(1024*1024):out.write(block)
 sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==b['sha256'];r.update(state='PASS',archive=str(p),sha256=sha,bytes=p.stat().st_size);save();print(json.dumps(r))
except BaseException as error:r.update(state='FAIL',error_type=type(error).__name__,http_status=getattr(error,'code',r.get('http_status')));save();raise

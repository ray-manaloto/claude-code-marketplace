import datetime, hashlib, json, pathlib, sys, time, urllib.error, urllib.parse, urllib.request
root=pathlib.Path(__file__).resolve().parent
request_bytes=(root/'download-requests.json').read_bytes()
spec=json.loads(request_bytes)
expected={
 'fmtlib-fmt-12.2.0.tar.gz':('https://github.com/fmtlib/fmt/archive/12.2.0.tar.gz','5ac2ba0f54a484999ed5407d82b77aad170cea49a267decd2c0eedadf3b14413e2a83fcc8e9ca9c16640595e019b8636e160f72314d8be50653324e82ac745eb',16777216),
 'fmt-backport-4813.patch':('https://github.com/fmtlib/fmt/commit/588b3a0f8f6a8bcf2a959cae882d5b2703e86737.patch?full_index=1','afda8fdfcdcb4b0dd5df4d4dae96a57a85fb9c4b65d0b49d51258f0913d4aed93ed146ebf96ed7b277490b1dde6c7117f43332013071441a96c3147520de8368',1048576)}
assert len(spec['downloads'])==len(expected)
assert {item['filename'] for item in spec['downloads']}==set(expected)
for item in spec['downloads']:
    assert (item['url'],item['sha512'])==expected[item['filename']][:2]
class OfficialRedirects(urllib.request.HTTPRedirectHandler):
    def __init__(self,record):
        self.record=record
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        parsed=urllib.parse.urlsplit(newurl)
        if parsed.scheme!='https' or parsed.hostname not in ('github.com','codeload.github.com') or parsed.username or parsed.password:
            raise ValueError('redirect outside exact official GitHub host allowance')
        self.record['redirects'].append({'status':code,'url':newurl})
        return super().redirect_request(req,fp,code,msg,headers,newurl)
results=[]
for item in spec['downloads']:
    record={**item,'redirects':[],'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'STARTED'}
    target=root/(item['filename']+'.partial')
    h256=hashlib.sha256();h512=hashlib.sha512();count=0;started=time.monotonic()
    try:
        opener=urllib.request.build_opener(OfficialRedirects(record))
        request=urllib.request.Request(item['url'],headers={'User-Agent':'marketplace-pinned-source-acquisition/1','Accept':'application/octet-stream'})
        with opener.open(request,timeout=30) as response:
            record['http_status']=response.status
            record['final_url']=response.geturl()
            assert response.status==200
            declared=response.headers.get('Content-Length')
            limit=expected[item['filename']][2]
            if declared is not None and int(declared)>limit:
                raise ValueError('declared response exceeds fixed byte limit')
            with target.open('xb') as output:
                while True:
                    if time.monotonic()-started>60:
                        raise TimeoutError('bounded acquisition deadline exceeded')
                    chunk=response.read(min(65536,limit-count+1))
                    if not chunk:
                        break
                    if count+len(chunk)>limit:
                        raise ValueError('response exceeds fixed byte limit')
                    output.write(chunk);h256.update(chunk);h512.update(chunk);count+=len(chunk)
        record.update(bytes=count,sha256=h256.hexdigest(),actual_sha512=h512.hexdigest())
        if count==0 or h512.hexdigest()!=item['sha512']:
            record['status']='HASH_MISMATCH'
            record['path']=str(target)
        else:
            final=root/item['filename']
            target.rename(final)
            record['status']='VERIFIED'
            record['path']=str(final)
    except Exception as error:
        record.update(status='FAILED',exception_type=type(error).__name__,bytes=count,sha256=h256.hexdigest(),actual_sha512=h512.hexdigest())
        if isinstance(error,urllib.error.HTTPError):
            record['http_status']=error.code
        elif isinstance(error,urllib.error.URLError):
            record['reason_type']=type(error.reason).__name__
        if target.exists():
            record['partial_path']=str(target)
    record['elapsed_seconds']=round(time.monotonic()-started,3)
    record['completed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    results.append(record)
    (root/(item['filename']+'.acquisition.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record),flush=True)
inventory={'kind':'two-exact-official-fmt-input-acquisition','prerequisite':spec['prerequisite'],'request_spec_sha256':hashlib.sha256(request_bytes).hexdigest(),'route':'native fnox codex_research exec; Python urllib; exact official input URLs only','records':results,'credentials_or_environment_emitted':False,'source_executed':False,'patch_applied':False}
(root/'download-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
sys.exit(0 if all(r['status']=='VERIFIED' for r in results) else 1)

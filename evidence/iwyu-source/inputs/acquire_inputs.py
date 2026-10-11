from pathlib import Path
import datetime,hashlib,json,urllib.request
base=Path(__file__).parent
pin="791e69ea4662cb3e74e8128fd5fd69bd7f4ea6b3"
report={"state":"running","pin":pin,"route":"Public GitHub commit/tree API through native fnox codex_research; no injected values recorded","records":[]}
def save(): (base/"acquisition.json").write_text(json.dumps(report,indent=2)+"\n")
def get(label,url):
 row={"case":label,"url":url,"started_at":datetime.datetime.now(datetime.timezone.utc).isoformat()};report["records"].append(row);save()
 try:
  request=urllib.request.Request(url,headers={"User-Agent":"marketplace-pinned-source-qualification","Accept":"application/vnd.github+json"})
  with urllib.request.urlopen(request,timeout=30) as response:
   body=response.read(); row["http_status"]=response.status
  target=base/(label+".json"); target.write_bytes(body); row.update(path=str(target),bytes=len(body),sha256=hashlib.sha256(body).hexdigest());save();return json.loads(body)
 except BaseException as error:
  row["error"]=repr(error);save();raise
try:
 commit=get("commit","https://api.github.com/repos/include-what-you-use/include-what-you-use/git/commits/"+pin)
 assert commit["sha"]==pin
 tree=get("root-tree","https://api.github.com/repos/include-what-you-use/include-what-you-use/git/trees/"+commit["tree"]["sha"])
 assert tree["sha"]==commit["tree"]["sha"] and not tree["truncated"]
 report.update(state="PASS exact pinned primary API source identity",tree=tree["sha"])
finally:
 save(); print(json.dumps({"state":report["state"],"tree":report.get("tree"),"receipt":str(base/"acquisition.json")}))

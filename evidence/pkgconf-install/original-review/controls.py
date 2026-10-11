import ast,copy,hashlib,json,os,tarfile
from pathlib import Path
from projection import project_macho
out=Path(__file__).parent;root=Path(json.loads((out/"identity.json").read_text())["checkout"])
helper=out/"checked-helper.py.source";contract=json.loads((out/"checked-contract.json").read_text())
assert hashlib.sha256(helper.read_bytes()).hexdigest()==json.loads((out/"identity.json").read_text())["helper_sha256"]
scope={"Path":Path,"hashlib":hashlib,"load":lambda p:json.loads(p.read_text())}
nodes=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in {"validate_macho","validate_keg"}]
assert len(nodes)==2
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),"exec"),scope)
rows=[];calls=0
class BytesPath:
 def __init__(self,data):self.data=data
 def read_bytes(self):return bytes(self.data)
def check(name,should_accept,invoke):
 global calls
 calls+=1
 try:invoke();accepted=True;error=None
 except (AssertionError,KeyError,FileNotFoundError) as exc:accepted=False;error=type(exc).__name__+": "+str(exc)
 rows.append({"case":name,"required_acceptance":should_accept,"actual_acceptance":accepted,"matches_required":accepted==should_accept,"error":error})
prep=json.loads((root/contract["preparation"]).read_text())
with tarfile.open(prep["bottle"]["path"],"r:gz") as tar:
 data=project_macho(tar.extractfile("pkgconf/3.0.8/bin/pkgconf").read())
rule=contract["macho_files"]["bin/pkgconf"]
for case in ("valid_bound_projection","unmasked_payload_change","signature_dataoff_change","signature_truncated","linkedit_range_change","vmsize_too_small"):
 trial=bytearray(data)
 if case=="unmasked_payload_change":trial[4000]^=1
 if case=="signature_dataoff_change":trial[1560:1564]=(rule["signature_offset"]+1).to_bytes(4,"little")
 if case=="signature_truncated":trial=trial[:-1]
 if case=="linkedit_range_change":trial[1088:1096]=(len(trial)-rule["linkedit_fileoff"]+1).to_bytes(8,"little")
 if case=="vmsize_too_small":trial[1072:1080]=(len(trial)-rule["linkedit_fileoff"]-1).to_bytes(8,"little")
 check("macho_"+case,case=="valid_bound_projection",lambda trial=trial:scope["validate_macho"](BytesPath(trial),rule))
for case in ("valid","root_mode_drift","unchanged_digest_drift","wrong_text_postimage","missing_receipt","extra_receipt_field"):
 prefix=out/"fixtures"/case/"prefix";keg=prefix/"Cellar/pkgconf/3.0.8";keg.mkdir(parents=True);keg.chmod(0o755);(keg.parent/".mise-staging.lock").write_bytes(b"")
 kept,oldtext,newtext=b"retained\n",b"original\n",b"relocated\n"
 sha=lambda b:hashlib.sha256(b).hexdigest()
 mf={"members":[{"path":"pkgconf/3.0.8","type":"5","mode":"0o755"},{"path":"pkgconf/3.0.8/kept.txt","type":"0","mode":"0o444","sha256":sha(kept)},{"path":"pkgconf/3.0.8/relocated.pc","type":"0","mode":"0o444","sha256":sha(oldtext)}]}
 ct={"changed_files":["relocated.pc"],"text_postimages":{"relocated.pc":sha(newtext)},"receipt_required":{"homebrew_version":"5.1.15 (mise)"}}
 for name,b in [("kept.txt",kept),("relocated.pc",newtext)]:p=keg/name;p.write_bytes(b);p.chmod(0o444)
 rc=ct["receipt_required"]|{"time":1791749000,"changed_files":["relocated.pc"]}
 if case=="extra_receipt_field":rc["unexpected"]=True
 (keg/"INSTALL_RECEIPT.json").write_text(json.dumps(rc))
 if case=="root_mode_drift":keg.chmod(0o777)
 if case=="unchanged_digest_drift":(keg/"kept.txt").chmod(0o644);(keg/"kept.txt").write_bytes(b"drift");(keg/"kept.txt").chmod(0o444)
 if case=="wrong_text_postimage":(keg/"relocated.pc").chmod(0o644);(keg/"relocated.pc").write_bytes(b"wrong");(keg/"relocated.pc").chmod(0o444)
 if case=="missing_receipt":(keg/"INSTALL_RECEIPT.json").unlink()
 # Explicit small path allowlist only: no recursive fixture scan. This mirrors
 # the imported inventory's root exclusion and direct regular-file fields.
 observed=[]
 for name in ("kept.txt","relocated.pc","INSTALL_RECEIPT.json"):
  p=keg/name
  if p.exists():observed.append({"path":name,"mode":oct(p.stat().st_mode&0o777),"kind":"file","sha256":sha(p.read_bytes()),"bytes":p.stat().st_size})
 scope["PREFIX"]=prefix;scope["prefix_inventory"]=lambda p,expected=keg,rows=observed: (rows if p==expected else (_ for _ in ()).throw(AssertionError("unexpected path")))
 check("keg_"+case,case=="valid",lambda:scope["validate_keg"](mf,ct))
assert calls==12
assert [r["case"] for r in rows if not r["matches_required"]]==["keg_root_mode_drift"]
result={"result":"COMPLETE_WITH_REPRODUCED_FINDING","helper_sha256":hashlib.sha256(helper.read_bytes()).hexdigest(),"validation_calls":calls,"cases":rows,"limits":"AST-only two validators. Six in-memory Mach-O inputs; six isolated synthetic keg fixtures, inventory rows from explicit paths. No native execution, candidate imports/main/guard, shared inventories or recursive fixture scans."}
(out/"controls.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"result":result["result"],"validation_calls":calls,"reproduced_findings":1}))

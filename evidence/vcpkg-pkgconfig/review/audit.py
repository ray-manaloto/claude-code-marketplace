import ast,hashlib,json,posixpath,stat,tarfile,tomllib
from pathlib import Path,PurePosixPath
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/vcpkg-pkgconfig';D=Path(__file__).parent
H='41f91b31912d1fc50ba06aacc159b56315072a03';HS='175de0ddf4e5832990da909fbb06ee0591f258edfe46ca552ec1895d0f63e92a';CS='40a53acbe1e628e99ef3be1bac288c9bd39bdc6268e1ccf78dd62cb608945d54';KS='c711a7d689fc4e1c7c1556d41325fed761ad8e119e88a913ae45e04c41ff3c20';BS='cfcd403c852da8f88324056c0881ce69880fcb675181b20345ff7ffc99d4f586'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def save(n,d):(D/n).write_text(json.dumps(d,indent=2)+'\n')
def record(p):
 p=Path(p);return {'sha256':sha(p),'bytes':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
def blobsha(p):
 b=Path(p).read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
# This audit does not import candidate code, execute native tools, read live prefix state, or extract archives.
helper=R/'dev/toolchains/pkgconf_prepare.py';contract=load(E/'contract.json');candidate=load(E/'candidate.json')
assert (sha(helper),sha(E/'contract.json'),sha(E/'candidate.json'))==(HS,CS,KS)
g=Path((R/'.git').read_text().strip().removeprefix('gitdir: '));common=(g/(g/'commondir').read_text().strip()).resolve();ref=(g/'HEAD').read_text().strip()
assert str(common)=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git' and ref=='ref: refs/heads/codex/marketplace-native-onboarding'
assert (common/ref.removeprefix('ref: ')).read_text().strip()==H==candidate['head']==contract['base_head']
assert candidate['contract_sha256']==CS and len(candidate['files'])==4 and len(contract['inputs'])==69
paths={helper,E/'contract.json',E/'candidate.json',R/'AGENTS.md',R/'docs/accepted-decisions.md',R/'evidence/onboarding/baseline-files.json'}
for p,h in candidate['files'].items():assert sha(R/p)==h,p;paths.add(R/p)
for p,h in contract['inputs'].items():assert sha(R/p)==h,p;paths.add(R/p)
assert sha(contract['current_mise']['path'])==contract['current_mise']['sha256'] and Path(contract['current_mise']['path']).stat().st_size==contract['current_mise']['bytes']
assert sha(contract['python'])==contract['python_sha256']
copycounts={}
for name,count in [('preparation-copy-manifest.json',12),('source-copy-manifest.json',7),('discovery-source-copy-manifest.json',28),('bottle-http-copy-manifest.json',6),('source-contract-copy-manifest.json',4)]:
 rows=load(E/name)['files'];assert len(rows)==count and len({row['copy'] for row in rows})==count
 for row in rows:
  source=Path(row['source']);copied=R/row['copy'];assert sha(source)==row['sha256'] and source.read_bytes()==copied.read_bytes(),row['copy'];paths.update([source,copied])
 paths.add(E/name);copycounts[name]=count
# Direct source/Git binding checks against retained tag/tree artifacts, not inspector assertions.
manifest=load(E/'source-contract/source-manifest.json');tree=load(E/'source/mise-tree.json');tag=load(E/'source/mise-tag.json');annotated=load(E/'source/mise-annotated-tag.json');acq=load(E/'source/acquisition.json')
assert tree['truncated'] is False and tag['ref']=='refs/tags/v2026.10.8' and tag['object']['sha']==annotated['sha'] and annotated['object']['sha']==acq['mise_commit']=='b671d356aaf33b87e48e7469a77abb40c3553c68'
index={r['path']:r for r in tree['tree']};selected=manifest['selected_mise_sources'];assert len(selected)==16
for row in selected:
 p=Path(row['path']);assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];assert blobsha(p)==row['git_blob_sha1']==row['current_tree_blob_sha1']==index[row['source']]['sha'];assert row['source_commit']==acq['mise_commit'];paths.add(p)
for row in manifest['pkgconf_sources']:
 p=Path(row['path']);assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];paths.add(p)
assert sha(E/'source-contract/report.md')=='70438f29ebc2e9b76ac8bd5eeed80081b5ea3c34ccf33549a533cb1fcec8b118' and sha(E/'source-contract/source-manifest.json')=='c190f52e24f0131c29bc946258c1841343de3b2c5944ebfdd1fd0cf18ea8124e'
http=load(E/'source/http-source-acquisition.json');hp=E/'source/mise-source/crates/mise-util/src/http.rs.source'
assert sha(hp)==http['sha256'] and blobsha(hp)==http['git_blob_sha1']==index['crates/mise-util/src/http.rs']['sha'] and Path(http['path']).read_bytes()==hp.read_bytes()
assert http['http_status']==200 and acq['state']=='PASS'
for row in acq['records']:
 p=Path(row['path']);assert row['http_status']==200 and sha(p)==row['sha256'] and p.stat().st_size==row['bytes'];paths.add(p)
for dirname in ['source','bottle-acquisition']:
 launch=load(E/dirname/'launch.json');execution=load(E/dirname/'execution.json');assert launch['argv']==execution['argv'] and execution['returncode']==0 and execution['stderr_present'] is False
 argv=launch['argv'];assert argv[1:11]==['--config','/Users/rmanaloto/.config/fnox/config.toml','--profile','codex_research','--no-defaults','--no-daemon','--non-interactive','exec','--',contract['python']]
 assert argv[-2]=='-B' and sha(argv[-1])==sha(E/dirname/'acquire.py')
# Actual native preparation receipt and log identities.
q=load(E/'preparation/preparation.json');native=load(E/'preparation/native-execution.json');op=Path(native['argv'][-1]);paths.update([E/'preparation/preparation.json',E/'preparation/native-execution.json'])
assert native['argv']==[contract['python'],'-B','dev/toolchains/pkgconf_prepare.py','--run-dir',str(op)] and native['returncode']==0 and native['stderr']==''
assert q['state']=='PASS: native preparation only' and q['helper_sha256']==HS
assert json.loads(native['stdout'])=={'state':q['state'],'receipt':str(op/'preparation.json')}
assert (op/'preparation.json').read_bytes()==(E/'preparation/preparation.json').read_bytes()
for key in ['prefix_preimages_unchanged','loopback_server_stopped','protected_state_unchanged']:assert q[key] is True
for key in ['archive_extracted','installation_executed']:assert q[key] is False
assert q['requests']==[{'path':'/api/formula/pkgconf.json','status':200},{'path':'/api/formula/pkgconf.json','status':404},{'path':'/api/formula.json','status':404}]
base=[contract['current_mise']['path'],'--no-hooks','-C',str(op/'cwd')];dryrun=base+['bootstrap','packages','apply','--manager','brew','--dry-run'];argvs={'version':base+['version'],'apply-help':base+['bootstrap','packages','apply','--help'],'captured-plan':dryrun,'missing-metadata':dryrun}
assert len(q['commands'])==4 and [r['case'] for r in q['commands']]==list(argvs)
for c in q['commands']:
 assert c['argv']==argvs[c['case']] and c['timeout_seconds']==45 and c['returncode']==c['expected']==(1 if c['case']=='missing-metadata' else 0)
 assert set(c['logs'])=={c['case']+'.stdout',c['case']+'.stderr'}
 for name,h in c['logs'].items():assert sha(op/name)==h and (op/name).read_bytes()==(E/'preparation'/name).read_bytes()
assert (op/'version.stdout').read_text().strip()==contract['current_mise']['version']
assert (op/'captured-plan.stdout').read_bytes()==b'pour pkgconf/3.0.8 (requested)\n'
assert (op/'missing-metadata.stdout').read_bytes()==b'' and '404 Not Found' in (op/'missing-metadata.stderr').read_text()
for name in ['version','apply-help','captured-plan']:assert (op/(name+'.stderr')).read_bytes()==b''
helptext=(op/'apply-help.stdout').read_text();assert '--manager' in helptext and '--dry-run' in helptext
config=tomllib.loads((op/'config.toml').read_text());assert config['bootstrap']=={'packages':{'brew:pkgconf':'latest'}}
urls=config['settings']['url_replacements'];endpoint=urls['https://formulae.brew.sh/api'].removesuffix('/api');assert endpoint.startswith('http://127.0.0.1:') and endpoint.rsplit(':',1)[1].isdigit()
assert urls=={'https://formulae.brew.sh/api':endpoint+'/api','https://ghcr.io':endpoint+'/blocked','https://github.com':endpoint+'/blocked'}
# Direct read-only archive inventory and independent write-set derivation.
formula=load(R/contract['formula']);bottle=formula['bottle']['stable']['files']['arm64_tahoe'];archive=Path(contract['archive']);paths.add(archive)
assert formula['name']=='pkgconf' and formula['versions']['stable']==contract['version']=='3.0.8' and formula['revision']==0 and formula['bottle']['stable']['rebuild']==0 and formula['dependencies']==[] and formula['keg_only'] is False
assert sha(archive)==bottle['sha256']==BS and archive.stat().st_size==194142 and bottle['cellar']=='/opt/homebrew/Cellar'
bottleacq=load(E/'bottle-acquisition/acquisition.json');assert bottleacq['state']=='PASS' and bottleacq['http_status']==200 and bottleacq['sha256']==bottleacq['expected_sha256']==BS and bottleacq['archive']==str(archive) and bottleacq['archive_extracted'] is False
assert bottleacq['formula_sha256']==sha(R/contract['formula']) and q['bottle']=={'path':str(archive),'sha256':BS,'bytes':194142}
constant_ast=ast.parse((R/'dev/toolchains/gcc_bottles.py').read_text());const={t.id:ast.literal_eval(n.value) for n in constant_ast.body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Name) and t.id in ['BOOTSTRAP_DIRS','LINK_DIRS']}
prefix=Path('/opt/homebrew');package=PurePosixPath('pkgconf/3.0.8');members=[];destinations={};member_paths=set();links=[]
with tarfile.open(archive,'r:gz') as tar:
 for item in tar:
  p=PurePosixPath(item.name);assert p.is_relative_to(package) and not p.is_absolute() and '..' not in p.parts and p.as_posix()==item.name and p not in member_paths
  assert item.isdir() or item.isfile() or item.issym();member_paths.add(p)
  row={'path':item.name,'type':item.type.decode(),'mode':oct(item.mode),'size':item.size,'linkname':item.linkname}
  if item.isfile():row['sha256']=hashlib.sha256(tar.extractfile(item).read()).hexdigest()
  if item.issym():
   target=PurePosixPath(posixpath.normpath(str(p.parent/item.linkname)));assert not PurePosixPath(item.linkname).is_absolute() and target.is_relative_to(package);links.append((p,target))
  members.append(row)
  if not item.isdir() and len(p.parts)>=3 and p.parts[2] in const['LINK_DIRS']:
   dest=str(prefix.joinpath(*p.parts[2:]));assert dest not in destinations;destinations[dest]={'target':str(prefix/'Cellar'/p),'preimage':{'kind':'absent'}}
for path,target in links:assert target in member_paths and any(r['path']==str(target) and r['type']=='0' for r in members)
for p in ['opt/pkgconf','var/homebrew/linked/pkgconf']:destinations[str(prefix/p)]={'target':str(prefix/'Cellar'/package),'preimage':{'kind':'absent'}}
m=q['manifest'];assert members==m['members'] and len(members)==50 and destinations==m['prefix_writes'] and len(destinations)==30
controls=[prefix,*[prefix/n for n in const['BOOTSTRAP_DIRS']],prefix/'Cellar/pkgconf',prefix/'Cellar/pkgconf/.mise-staging.lock',prefix/'var/homebrew/locks/mise-bootstrap.lock']
assert set(m['control_preimages'])=={str(p) for p in controls} and len(controls)==23
parents={str(p) for x in [*map(Path,destinations),*controls] for p in x.parents if p.is_relative_to(prefix)}
assert set(m['parent_preimages'])==parents and len(parents)==24 and m['materializations']=={} and not any(v['kind']=='symlink' for v in m['parent_preimages'].values())
assert m['control_preimages']['/opt/homebrew/Cellar/pkgconf']=={'kind':'absent'}
assert m['additional_native_writes']==['/opt/homebrew/Cellar/pkgconf/.mise-staging.lock','/opt/homebrew/Cellar/pkgconf/.mise-extract-3.0.8-<random>/','/opt/homebrew/Cellar/pkgconf/3.0.8/','/opt/homebrew/var/homebrew/locks/mise-bootstrap.lock','Missing listed parent directories','Listed directory materializations','Private mise state, data and cache']
# Inspect the profile discovery receipts, not the host PATH or live profiles.
dq=load(E/'profile-discovery/qualification.json');dn=load(E/'profile-discovery/native-execution.json');assert dn['returncode']==0 and dn['stderr']=='' and dq['state']=='PASS: existing profile discovery only'
assert dq['protected_before'] is True and dq['protected_after'] is True and dq['helper_sha256']==sha(E/'profile-discovery/probe.py') and len(dq['commands'])==6
for c in dq['commands']:
 assert c['returncode']==0 and c['seconds']<60
 for suffix in ['stdout','stderr']:assert sha(E/'profile-discovery'/(c['case']+'.'+suffix))==c[suffix+'_sha256']
 assert (E/'profile-discovery'/(c['case']+'.stderr')).read_bytes()==b''
 assert '--fresh-env' in c['argv'] and '--no-hooks' in c['argv'] and '--no-deps' in c['argv']
for lane in ['p2996','gcc16']:
 lookup=load(E/'profile-discovery'/(lane+'-lookup.stdout'));assert lookup==dq['discovery'][lane] and lookup['tools']=={'pkg-config':None,'pkgconf':None} and lookup['pkg_config_override_defined'] is False and lookup['home']=='/Users/rmanaloto'
 assert (E/'profile-discovery'/(lane+'-profile.stdout')).read_bytes()==(R/'evidence/mise-renovate/operation'/(lane+'-profile.stdout')).read_bytes()
assert (E/'profile-discovery/default-before.stdout').read_bytes()==(E/'profile-discovery/default-after.stdout').read_bytes()==(R/'evidence/mise-renovate/operation/default-after.stdout').read_bytes()
# Four exact prerequisite source copies; no broad source tree traversal.
prereq=load(E/'source-prerequisites/pkgconfig-source-manifest.json');assert len(prereq['source_files'])==4
for row in prereq['source_files']:
 source=Path(row['source_path']);copy=Path(row['copy']['path']);assert sha(source)==row['source_sha256']==row['copy']['sha256'] and source.read_bytes()==copy.read_bytes();paths.update([source,copy])
# Retained scan triage: verify the flagged value as a content digest, never as a secret.
scan=load(E/'pre-review-secret-scan.json');disposition=load(E/'pre-review-scan-disposition.json');assert scan['returncode']==disposition['raw_scan_returncode']==1 and sha(E/'pre-review-secret-scan.json')==disposition['raw_scan_sha256']
for p,h in scan['files'].items():assert sha(R/p)==h,p
finding=disposition['finding'];assert finding['file']=='evidence/vcpkg-pkgconfig/contract.json' and finding['json_member']=='inputs' and finding['verified_file_sha256']==contract['inputs'][finding['input_path']]==sha(R/finding['input_path'])
assert finding['input_path']=='evidence/gcc-bootstrap/mise-source/src/system/packages/brew/api.rs.source'
assert disposition['transformed_scan']['returncode']==0 and disposition['transformed_scan']['substitutions']==1 and disposition['supplemental_complete_token_files']==[]
assert 'ghs_*' in hp.read_text().splitlines()[2357]
paths.update([E/'pre-review-secret-scan.json',E/'pre-review-scan-disposition.json',E/'pre-review-static.json'])
static=load(E/'pre-review-static.json')['commands'];assert len(static)==2 and all(r['returncode']==0 for r in static) and json.loads(static[1]['stdout'])['checks']['baseline']==19
baseline=load(R/'evidence/onboarding/baseline-files.json')['files'];assert len(baseline)==19
for row in baseline:assert sha(R/row['path'])==row['sha256'] and (R/row['path']).stat().st_size==row['bytes']
watch={str(p):record(p) for p in sorted(paths)};save('frozen-inputs.json',watch)
summary={'result':'PASS','kind':'Filesystem/archive/source artifact audit only','head':H,'contract_inputs':69,'candidate_files':4,'copy_counts':copycounts,'current_selected_source_sha_and_git_blob_matches':16,'official_acquisition_source_records':len(acq['records']),'prerequisite_source_pairs':4,'archive_sha256':BS,'archive_bytes':194142,'archive_members':50,'archive_safe_symlinks':len(links),'prefix_destinations':30,'parent_preimages':24,'control_preimages':23,'directory_materializations':0,'native_preparation_wrapper_rc':0,'native_preparation_child_rcs':[r['returncode'] for r in q['commands']],'native_preparation_log_hashes':8,'native_preparation_exact_argvs':4,'native_plan_one_requested_pkgconf_3_0_8':True,'native_no_extraction_no_install_recorded':True,'native_server_stopped_and_protection_recorded':True,'discovery_native_wrapper_rc':0,'discovery_commands':6,'discovery_logs':12,'both_lanes_pkg_config_and_pkgconf_absent':True,'both_lanes_override_absent':True,'default_environment_restored':True,'parent_static_returncodes':[0,0],'scan_raw_returncode':1,'scan_file_hashes':len(scan['files']),'content_digest_false_positive_independently_verified':True,'retained_transformed_scan_returncode':0,'scan_rerun_by_reviewer':False,'original_Claude_file_hashes_and_sizes':19,'frozen_files':len(watch),'candidate_functions_executed_in_this_audit':0,'live_prefix_reads':0,'archive_extraction':False,'native_replay':False,'shared_writes':0,'earlier_read_schema_error':"An exploratory reader exited 1 looking for discovery command key logs; the actual stdout_sha256/stderr_sha256 schema is verified here. No candidate failure."}
save('audit.json',summary);print(json.dumps(summary))

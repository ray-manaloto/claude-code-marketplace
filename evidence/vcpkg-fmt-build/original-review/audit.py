from pathlib import Path
import ast,hashlib,json
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=R/'evidence/vcpkg-fmt-build';D=Path(__file__).parent
watched={}
def digest(p,algorithm='sha256'):
    p=Path(p); key=(str(p),algorithm)
    if key not in watched:
        h=hashlib.new(algorithm); count=0
        with p.open('rb') as f:
            while b:=f.read(4*1024**2): h.update(b);count+=len(b)
        watched[key]={'path':str(p),'algorithm':algorithm,'sha256' if algorithm=='sha256' else 'sha512':h.hexdigest(),'bytes':count}
    return watched[key]['sha256' if algorithm=='sha256' else 'sha512']
def load(p): digest(p); return json.loads(Path(p).read_text())
expected={'head':'de913727bd6d41c1d7d2c11b52a384902dbd6eec','helper':'e6e2c37510052e3da1f6756ae3b614ba863ce13f2db2eb58ada0bbbd67caf628','contract':'b58d623fbc92f45a8816b90b9931f0840e034ebf15f901c640cd3167f7a067a4','candidate':'b872414cdac9963fde857e2de3c6d0bfbfa8dc2df1525d8fa98f183a63678af6'}
gitdir=Path((R/'.git').read_text().strip().removeprefix('gitdir: '));common=(gitdir/(gitdir/'commondir').read_text().strip()).resolve();ref=(gitdir/'HEAD').read_text().strip().removeprefix('ref: ')
assert ref=='refs/heads/codex/marketplace-native-onboarding' and (common/ref).read_text().strip()==expected['head']
assert str(common)=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'
assert digest(R/'dev/toolchains/vcpkg_fmt.py')==expected['helper']
assert digest(E/'contract.json')==expected['contract'] and digest(E/'candidate.json')==expected['candidate']
c=load(E/'contract.json');candidate=load(E/'candidate.json')
assert candidate['head']==c['base_head']==expected['head'] and candidate['contract_sha256']==expected['contract'] and len(candidate['files'])==4
for p,h in candidate['files'].items():assert digest(R/p)==h,p
assert (len(c['inputs']),len(c['source_inputs']),len(c['tools']))==(65,18,15)
for p,h in c['inputs'].items():assert digest(R/p)==h,p
for section in ('source_inputs','tools'):
    for p,h in c[section].items():assert digest(p)==h,p
for row in c['downloads']: assert digest(row['path'],'sha512')==row['sha512']
assert c['install_timeout_seconds']==600 and c['jobs_per_build']==1 and c['disk_reserve_bytes']==8*1024**3
assert list(c['prefixes'])==['p2996','gcc16']
assert set(c['abi_inputs'])=={'arm64-osx-'+l+'-'+k for l in c['prefixes'] for k in ('static','dynamic')}
abi_paths=set()
for triplet,rows in c['abi_inputs'].items():
    assert len(rows)==(15 if '-p2996-' in triplet else 14)
    assert len({r['path'] for r in rows})==len(rows)
    for row in rows:assert digest(row['path'])==row['sha256'];abi_paths.add(row['path'])
    lane,linkage=triplet.split('-')[2:]
    prior=(R/'evidence/vcpkg-abi-inputs/controls'/f'{lane}-{linkage}.stdout').read_text()
    names=next(s.removeprefix('-- ABI_LIST=') for s in prior.splitlines() if s.startswith('-- ABI_LIST=')).split(';')
    assert names==[r['path'] for r in rows]
assert c['default_profile']=='evidence/mise-renovate/operation/default-after.stdout'
assert c['profiles']=={'p2996':'evidence/mise-renovate/operation/p2996-profile.stdout','gcc16':'evidence/mise-renovate/operation/gcc16-profile.stdout'}
for lane in ('p2996','gcc16'):
    identity=c['compilers'][lane]
    metadata=R/f'evidence/core-p2996/operation/configured-evidence/{lane}-static/CMakeFiles/4.4.4/CMakeCXXCompiler.cmake'
    content=metadata.read_text()
    for key,value in [('CMAKE_CXX_COMPILER',identity['CXX']),('CMAKE_CXX_COMPILER_ID',identity['id']),('CMAKE_CXX_COMPILER_VERSION',identity['version'])]:
        assert f'set({key} "{value}")' in content
p=load(E/'logging-concurrency-prerequisite.json')
assert p['identity']['head']==p['identity']['closing_head']==expected['head'] and p['disposition']['omit_all_cmake_args']
assert len(p['source_bindings'])==6
for row in p['source_bindings']:
    assert c['source_inputs'][row['path']]==row['sha256'] and digest(row['path'])==row['sha256']
controls=load(E/'preparation-controls/controls.json');execution=load(E/'preparation-controls/execution.json')
assert digest(E/'preparation-controls/controls.json')==candidate['controls_sha256']
assert controls['state']=='PASS' and controls['helper_sha256']==expected['helper'] and controls['contract_sha256']==expected['contract']
assert len(controls['cases'])==5 and controls['native_tools_executed']==0
assert execution['returncode']==0 and execution['stderr']=='' and json.loads(execution['stdout'])=={'state':'PASS','cases':5,'native_tools_executed':0}
assert execution['script_sha256']==digest(E/'preparation-controls/controls.py')
assert digest(E/'preparation-controls/checked-helper.py.source')==expected['helper']
private=Path(execution['argv'][2]).parent
assert execution['argv']==['/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3','-B',str(private/'controls.py')]
for row in controls['cases'][:4]:
    triplet=row['triplet'];lane=triplet.split('-')[2];cell=private/triplet;env=row['environment'];argv=row['argv']
    assert len(argv)==len(set(argv))==17
    assert argv==[str(private/'vcpkg/vcpkg'),'--disable-metrics','--vcpkg-root='+str(private/'vcpkg'),'--downloads-root='+str(private/'downloads'),'--x-manifest-root='+str(private/'manifest'),'install','--triplet='+triplet,'--host-triplet=arm64-osx','--overlay-triplets='+str(R/'triplets'),'--no-downloads','--x-wait-for-lock','--feature-flags=-binarycaching,compilertracking','--debug','--x-registries-cache='+str(private/'registries'),'--x-install-root='+str(cell/'installed'),'--x-buildtrees-root='+str(cell/'buildtrees'),'--x-packages-root='+str(cell/'packages')]
    assert not any(x.startswith(('--cmake-args','--editable','--head','--dry-run','--clean')) for x in argv)
    assert env['HOME']=='/Users/rmanaloto' and env['PKG_CONFIG']=='/opt/homebrew/bin/pkg-config' and env['MARKETPLACE_CPP_LANE']==lane
    assert env['MARKETPLACE_'+lane.upper()+'_PREFIX']==c['prefixes'][lane]
    assert env['VCPKG_MAX_CONCURRENCY']==env['CMAKE_BUILD_PARALLEL_LEVEL']=='1' and env['MAKEFLAGS']=='-j1'
    assert env['PATH']==':'.join([str(Path(c['managed_tools'][n]['path']).parent) for n in ('cmake','ninja')]+['/opt/homebrew/Cellar/pkgconf/3.0.8/bin','/usr/bin','/bin','/usr/sbin','/sbin'])
    assert set(env)=={'VCPKG_ROOT','VCPKG_DOWNLOADS','X_VCPKG_REGISTRIES_CACHE','XDG_CACHE_HOME','TMPDIR','VCPKG_FORCE_SYSTEM_BINARIES','VCPKG_DISABLE_METRICS','HOME','USER','LANG','PATH','PKG_CONFIG','GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM','GIT_TERMINAL_PROMPT','GIT_OPTIONAL_LOCKS','VCPKG_MAX_CONCURRENCY','CMAKE_BUILD_PARALLEL_LEVEL','MAKEFLAGS','MARKETPLACE_CPP_LANE','MARKETPLACE_'+lane.upper()+'_PREFIX'}
assert controls['cases'][-1]=={'case':'unknown lane rejected','result':'PASS'}
copy_count=0
for name in ('control-copy-manifest.json','prerequisite-copy-manifest.json'):
    for row in load(E/name)['files']:
        assert digest(row['source'])==digest(R/row['copy'])==row['sha256']
        assert Path(row['source']).read_bytes()==(R/row['copy']).read_bytes();copy_count+=1
assert copy_count==6
static=load(E/'pre-review-static.json'); assert len(static['commands'])==2 and all(r['returncode']==0 for r in static['commands'])
assert json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
post=load(E/'vcpkg-abi-postcommit.json');assert post['head']==expected['head'] and post['returncode']==0 and post['before']==post['after']==''
scan=load(E/'pre-review-secret-scan.json'); assert len(scan['files'])==16
for path,h in scan['files'].items(): assert digest(R/path)==h,path
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and len(scan['dispositions'])==1
s=scan['dispositions'][0];assert s['rule']=='generic-api-key' and digest(R/s['path'])==s['sha256']==c['inputs'][s['path']]
helper=(R/'dev/toolchains/vcpkg_fmt.py').read_text();tree=ast.parse(helper)
assert len(helper.splitlines())==271
names=[n.name for n in tree.body if isinstance(n,ast.FunctionDef)]
assert names==['build_environment','install_arguments','inspect_cell','main']
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
run_calls=[n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='run']
install=next(n for n in run_calls if n.args and isinstance(n.args[0],ast.Name) and n.args[0].id=='triplet')
assert {x.arg:ast.unparse(x.value) for x in install.keywords}=={'timeout':"contract['install_timeout_seconds']",'descriptor':'fd','monitor':'True'}
assert 'report["cells"][triplet] = inspect_cell(cell, triplet, contract, env)' in helper
assert 'from mise_renovate import protected' in helper
assert 'assert all(digest(ROOT / p) == sha for p, sha in data["inputs"].items())' in helper
assert 'assert all(digest(Path(p)) == sha for p, sha in data["tools"].items())' in helper
assert 'assert all(digest(Path(p)) == sha for p, sha in data["source_inputs"].items())' in helper
assert 'with lease.held(lease.HEAVY_GATE, "marketplace-vcpkg-fmt", wait_s=0, out=io.StringIO()) as fd:' in helper
assert 'timeout=contract["install_timeout_seconds"], descriptor=fd, monitor=True)' in helper
assert 'report.update(state="FAIL", preservation_error=repr(error))' in helper
assert '(deny network*)' in helper and '(deny file-write*)' in helper
configure_path=next(Path(p) for p in c['source_inputs'] if p.endswith('/ports/vcpkg-cmake/vcpkg_cmake_configure.cmake'))
configure=configure_path.read_text();fmt_path=next(Path(p) for p in c['source_inputs'] if p.endswith('/ports/fmt/portfile.cmake'));fmt=fmt_path.read_text()
assert 'DISABLE_PARALLEL_CONFIGURE' not in fmt
assert 'if(NOT arg_DISABLE_PARALLEL_CONFIGURE)' in configure
assert 'z_vcpkg_configure_cmake_build_cmakecache(ninja_configure_contents ".." "rel")' in configure
assert 'z_vcpkg_configure_cmake_build_cmakecache(ninja_configure_contents "../../${TARGET_TRIPLET}-dbg" "dbg")' in configure
assert 'COMMAND "${NINJA}" -v\n' in configure and 'pool =' not in configure
assert 'VCPKG_CONCURRENCY' not in configure
report={'result':'PASS requested file bindings; one source finding retained separately','identity':{'checkout':str(R),'branch':ref.removeprefix('refs/heads/'),'head':expected['head'],'common_git_directory':str(common)},'bindings':expected,'candidate_files':4,'contract_inputs':65,'source_inputs':18,'tools':15,'unique_abi_paths':len(abi_paths),'download_sha512_checks':2,'exact_copy_pairs':copy_count,'retained_parent_controls':5,'parent_controls_returncode':0,'parent_static_returncodes':[0,0],'parent_baseline_original_files':19,'scan_returncodes':{'raw':1,'disposition':0},'scan_disposition':'One exact content digest independently matched the bound public receipt.','native_commands':0,'candidate_functions_executed':0,'maintained_writes':0,'shared_writes':0,'concurrency_finding':{'path':'dev/toolchains/vcpkg_fmt.py','line':39,'source_path':str(configure_path),'source_lines':[248,272],'fmt_path':str(fmt_path),'finding':'The one-job environment controls compilation/build invocations, but the unchanged helper launches two configure processes through Ninja without -j1. Original whole-install wording must be narrowed or configure scheduling constrained.','executed_runtime_reproduction':False}}
(D/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
(D/'input-hashes.json').write_text(json.dumps(list(watched.values()),indent=2)+'\n')
print(json.dumps({'result':report['result'],'files_hashed':len(watched),'contract_inputs':65,'source_inputs':18,'tools':15,'abi_paths':len(abi_paths),'copies':copy_count}))

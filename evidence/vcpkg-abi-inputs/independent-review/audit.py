from pathlib import Path
import hashlib, json
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/vcpkg-abi-inputs'
OUT=Path(__file__).parent
watched={}
def read(p):
    p=Path(p)
    k=str(p)
    if k not in watched:
        b=p.read_bytes(); watched[k]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'content':b}
    return watched[k]['content']
def sha(p): read(p); return watched[str(Path(p))]['sha256']
def load(p): return json.loads(read(p))
def descendants(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values(): yield from descendants(v)
    elif isinstance(obj,list):
        for v in obj: yield from descendants(v)
expected_head='8cca82e40a07936a035b01a36df290ec3e1c251c'
expected_candidate='a5843383e4bcc591fac62749decbb3759c0e559709159fc4832797293616793f'
expected_common='9e0ce33ce9822980889534331a48de656021c7c04b5f311515161176d84bfe1a'
gitdir=Path(read(ROOT/'.git').decode().strip().removeprefix('gitdir: '))
common=(gitdir/read(gitdir/'commondir').decode().strip()).resolve()
ref=read(gitdir/'HEAD').decode().strip().removeprefix('ref: ')
assert ref=='refs/heads/codex/marketplace-native-onboarding'
refpath=common/ref
if refpath.is_file(): head=read(refpath).decode().strip()
else:
    head=next(s.split()[0] for s in read(common/'packed-refs').decode().splitlines() if s.endswith(' '+ref))
assert head==expected_head
assert str(common)=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'
assert sha(E/'candidate.json')==expected_candidate
candidate=load(E/'candidate.json'); assert candidate['head']==head and len(candidate['files'])==4
for p,s in candidate['files'].items(): assert sha(ROOT/p)==s,p
assert sha(ROOT/'triplets/common/macos-arm64.cmake')==expected_common
assert sha(E/'source-bindings.json')==candidate['source_bindings_sha256']
bindings=load(E/'source-bindings.json'); assert bindings['base_head']==head
assert len(bindings['source_files'])==9 and len(bindings['receipts'])==7 and bindings['new_research_routes']==[]
for r in bindings['source_files']: assert sha(r['path'])==r['sha256'],r['id']
for p,s in bindings['receipts'].items(): assert sha(ROOT/p)==s,p
source_by_id={r['id']:read(r['path']).decode() for r in bindings['source_files']}
wiring=load(ROOT/'evidence/vcpkg-native-prerequisites/pkgconf-wiring/source-manifest.json')
prior=load(ROOT/'evidence/vcpkg-native-prerequisites/source-manifest.json')
recorded=list(descendants(wiring))+list(descendants(prior))
for r in bindings['source_files']:
    assert any(x.get('path')==r['path'] and x.get('sha256')==r['sha256'] for x in recorded),r['id']
common_text=read(ROOT/'triplets/common/macos-arm64.cmake').decode()
new_block=common_text[common_text.index('set(_marketplace_pkg_config '):common_text.index('foreach(_marketplace_input IN LISTS _marketplace_triplet_inputs)')]
assert len(new_block.splitlines())==16
old=common_text.replace(new_block,'').replace(' "-DFMT_MODULE=OFF"','')
old_common=next(r for r in wiring['source_files'] if r['id']=='common_triplet')
assert hashlib.sha256(old.encode()).hexdigest()==old_common['sha256'] and len(old.encode())==old_common['bytes']
assert 'if(DEFINED "ENV{PKG_CONFIG}")' in source_by_id['selector']
assert 'set(PKGCONFIG "$ENV{PKG_CONFIG}" CACHE INTERNAL "")' in source_by_id['selector']
assert 'function(vcpkg_find_acquire_program program)\n    if(${program})\n        return()' in source_by_id['acquisition']
assert 'COMMAND "${PKGCONFIG}" --print-errors --exists "${package_name}"' in source_by_id['invocation']
assert 'vcpkg_fixup_pkgconfig()' in source_by_id['fmt_call']
assert 'ENV:" + env_var, Hash::get_string_hash(*e, Hash::Algorithm::Sha256)' in source_by_id['abi']
assert 'Hash::get_file_hash(fs, file, Hash::Algorithm::Sha256)' in source_by_id['abi']
assert 'hash_additional_files =' in source_by_id['abi']
assert 'VCPKG_HASH_ADDITIONAL_FILES=${VCPKG_HASH_ADDITIONAL_FILES}' in source_by_id['tag_variables']
assert 'VCPKG_ENV_PASSTHROUGH=${VCPKG_ENV_PASSTHROUGH}' in source_by_id['tag_variables']
assert 'vcpkg_list(APPEND arg_OPTIONS ${VCPKG_CMAKE_CONFIGURE_OPTIONS})' in source_by_id['fmt_configure']
assert '${arg_OPTIONS} ${arg_OPTIONS_RELEASE}' in source_by_id['fmt_configure']
assert '${arg_OPTIONS} ${arg_OPTIONS_DEBUG}' in source_by_id['fmt_configure']
assert 'add_library(fmt src/format.cc' in source_by_id['fmt_cmake']
assert 'if (FMT_MODULE)\n  add_module_library(fmt-module' in source_by_id['fmt_cmake']
assert '(DEFINED PKGCONFIG AND NOT "${PKGCONFIG}" STREQUAL "${_marketplace_pkg_config}")' in new_block
assert '(DEFINED CACHE{PKGCONFIG} AND NOT "$CACHE{PKGCONFIG}" STREQUAL "${_marketplace_pkg_config}")' in new_block
assert 'file(REAL_PATH "${_marketplace_pkg_config}" _marketplace_pkgconf_selected)' in new_block
package=load(ROOT/'evidence/pkgconf-install/qualified-package-inputs.json')
closure=load(ROOT/'evidence/pkgconf-install/closure-review.json')
assert closure['findings']==[] and closure['result'].startswith('PASS')
assert sha(ROOT/'evidence/pkgconf-install/closure-review.json')=='0f2b0218126b112c3e898310a9e6e1ee9ff648474d0133e73567c5771c64ecf4'
assert package['pkg_config_link']=={'path':'/opt/homebrew/bin/pkg-config','target':'../Cellar/pkgconf/3.0.8/bin/pkg-config','resolved':'/opt/homebrew/Cellar/pkgconf/3.0.8/bin/pkgconf'}
assert set(package['files'])=={'/opt/homebrew/Cellar/pkgconf/3.0.8/bin/pkgconf','/opt/homebrew/Cellar/pkgconf/3.0.8/lib/libpkgconf.8.dylib'}
assert package['files']['/opt/homebrew/Cellar/pkgconf/3.0.8/bin/pkgconf']['sha256']=='af9c1619839586af4b34bfa7131b678eb535075dfb88079b103743ba8c26d246'
assert package['files']['/opt/homebrew/Cellar/pkgconf/3.0.8/lib/libpkgconf.8.dylib']['sha256']=='e29c2e02eb488dc7004e3bd3f0f8b777266314549e9121b810cf306edb2a24a1'
manifest=load(E/'copy-manifest.json'); assert len(manifest['files'])==29
for row in manifest['files']:
    assert sha(row['source'])==row['sha256']==sha(ROOT/row['copy']),row['copy']
    assert read(row['source'])==read(ROOT/row['copy']),row['copy']
q=load(E/'controls/controls.json'); run=load(E/'controls/execution.json')
assert sha(E/'controls/controls.json')==candidate['controls_sha256']=='3305caa567f09d7ba3ca569d7139bed663ea109103d6ac1dfb4065c0815890db'
assert q['state']=='PASS' and q['bound_inputs_unchanged'] and q['qualified_package_unchanged']
assert q['common_sha256']==expected_common and q['helper_sha256']==sha(E/'controls/controls.py')==run['script_sha256']
assert run['returncode']==0 and run['stderr']=='' and json.loads(run['stdout'])['commands']==8
control_root=Path(load(E/'control-root.json')['private_root'])
assert run['argv']==['/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3','-B',str(control_root/'controls.py')]
assert q['cmake']=={'path':'/Users/rmanaloto/.local/share/mise/installs/cmake/4.4.4/cmake-4.4.4-macos-universal/CMake.app/Contents/bin/cmake','sha256':'80cbc0d5ee08c9e6166bcc44bf51faf5469e360346f5cefbf36e8f8e4351a4cb'}
old_lists={}
for lane,row in q['prior_abi_lists'].items():
    assert sha(row['path'])==row['sha256']
    old_lists[lane]=[s.removeprefix('-- ABI=').split('|')[0] for s in read(row['path']).decode().splitlines() if s.startswith('-- ABI=')]
    assert old_lists[lane]==row['inputs']
prefixes={'gcc16':'/opt/homebrew/Cellar/gcc/16.2.0','p2996':'/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-configure-20261011T051205Z/prefix'}
names=['gcc16-static','gcc16-dynamic','p2996-static','p2996-dynamic','missing-environment','wrong-environment','conflicting-variable','conflicting-shadowed-cache']
assert [r['case'] for r in q['commands']]==names
outcomes=[]
for i,row in enumerate(q['commands']):
    name=row['case']; lane=name.split('-')[0] if i<4 else ('gcc16' if i<6 else 'p2996')
    linkage=name.split('-')[1] if i<4 else ('dynamic' if i==6 else 'static')
    expected=0 if i<4 else 1
    assert row['returncode']==row['expected_returncode']==expected and row['state']=='PASS'
    assert row['argv']==[q['cmake']['path'],'-P',str(control_root/(name+'.cmake'))]
    script=read(E/'controls'/(name+'.cmake')).decode()
    assert sha(E/'controls'/(name+'.cmake'))==row['script_sha256']
    triplet=ROOT/('triplets/arm64-osx-'+lane+'-'+linkage+'.cmake')
    assert read(triplet).decode()=='set(_marketplace_triplet_lane '+lane+')\nset(VCPKG_LIBRARY_LINKAGE '+linkage+')\ninclude("${CMAKE_CURRENT_LIST_DIR}/common/macos-arm64.cmake")\n'
    assert script.count('include("'+str(triplet)+'")')==2
    assert 'NOT before STREQUAL VCPKG_HASH_ADDITIONAL_FILES OR NOT before_env STREQUAL VCPKG_ENV_PASSTHROUGH OR DEFINED VCPKG_BUILD_TYPE' in script
    assert 'execute_process' not in script and 'file(WRITE' not in script
    env={'HOME':'/Users/rmanaloto','PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'C','LC_ALL':'C','TMPDIR':str(control_root),'MARKETPLACE_CPP_LANE':lane,'MARKETPLACE_'+lane.upper()+'_PREFIX':prefixes[lane]}
    if i!=4: env['PKG_CONFIG']='/invalid/pkg-config' if i==5 else '/opt/homebrew/bin/pkg-config'
    assert row['environment']==env
    for suffix, log in zip(('stdout','stderr'),row['logs'],strict=True):
        assert log['path']==str(control_root/(name+'.'+suffix))
        assert sha(log['path'])==log['sha256']==sha(E/'controls'/(name+'.'+suffix))
    out=read(E/'controls'/(name+'.stdout')).decode(); err=read(E/'controls'/(name+'.stderr')).decode()
    if i<4:
        assert err=='' and '-- PKGCONF_ABI_PASS:'+name+'\n' in out
        vals=dict(s.removeprefix('-- ').split('=',1) for s in out.splitlines() if s.startswith('-- ') and '=' in s and not s.startswith('-- PKGCONF_HASH='))
        actual=vals['ABI_LIST'].split(';'); prior_paths=old_lists[lane]
        assert len(actual)==len(set(actual))==len(prior_paths)+2==row['total_abi_inputs']
        assert row['preserved_abi_inputs']==len(prior_paths)
        assert set(actual)==set(prior_paths)|set(package['files'])
        assert [x for x in actual if x not in package['files']]==prior_paths
        assert vals['TRACKED_ENV']=='MARKETPLACE_CPP_LANE;MARKETPLACE_'+lane.upper()+'_PREFIX;PKG_CONFIG'
        assert vals['OPTIONS']=='-DCMAKE_POLICY_DEFAULT_CMP0210=NEW;-DFMT_MODULE=OFF' and vals['LINKAGE']==linkage
        hashes=dict(s.removeprefix('-- PKGCONF_HASH=').split('|') for s in out.splitlines() if s.startswith('-- PKGCONF_HASH='))
        assert hashes==row['pkgconf_hashes']=={p:r['sha256'] for p,r in package['files'].items()}
    else:
        assert out=='' and 'Use the qualified pkgconf entry through PKG_CONFIG in a fresh process.' in err
        assert 'triplets/common/macos-arm64.cmake:63 (message)' in err
    if i==1: assert 'set(PKGCONFIG "/opt/homebrew/bin/pkg-config")' in script
    if i==2: assert 'set(PKGCONFIG "/opt/homebrew/bin/pkg-config" CACHE INTERNAL "")' in script
    if i==6: assert 'set(PKGCONFIG "/invalid/pkg-config")' in script
    if i==7: assert 'set(PKGCONFIG "/invalid/pkg-config" CACHE INTERNAL "")\nset(PKGCONFIG "/opt/homebrew/bin/pkg-config")' in script
    outcomes.append({'case':name,'returncode':row['returncode'],'log_pair_verified':True,'script_and_environment_verified':True})
static=load(E/'pre-review-static.json'); assert len(static['commands'])==2
assert [r['returncode'] for r in static['commands']]==[0,0]
assert static['commands'][0]['argv']==['./dev/mise','tasks','validate']
assert static['commands'][1]['argv']==['./dev/mise','run','check:acceptance-baseline']
assert json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
post=load(E/'pkgconf-install-postcommit.json')
assert post['head']==head and post['returncode']==0 and post['clean_before'] and post['clean_after']
assert json.loads(post['stdout'])['checks']['baseline']==19
report={'result':'PASS','findings':[],'checkout':str(ROOT),'branch':ref.removeprefix('refs/heads/'),'head':head,'common_git_directory':str(common),'candidate_sha256':expected_candidate,'common_sha256':expected_common,'source_bindings_sha256':candidate['source_bindings_sha256'],'controls_sha256':candidate['controls_sha256'],'candidate_files_verified':4,'source_files_verified':9,'prerequisite_receipts_verified':7,'exact_source_copy_pairs_verified':29,'common_previous_sha256':old_common['sha256'],'common_delta':'Only 16 new guard/list lines and appended FMT_MODULE=OFF; exact previous bytes reconstructed.','retained_native_controls':outcomes,'retained_native_wrapper_returncode':0,'parent_static_returncodes':[0,0],'parent_baseline_original_file_count':19,'reviewer_native_controls_executed':0,'reviewer_maintained_writes':0,'reviewer_shared_writes':0,'scope':'File/JSON/hash/log assertions only; no candidate execution, control replay or installed/shared-tree inventory.'}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'input-hashes.json').write_text(json.dumps({k:{f:v[f] for f in ('sha256','bytes')} for k,v in watched.items()},indent=2)+'\n')
print(json.dumps({'result':'PASS','files_read':len(watched),'source_files':9,'copies':29,'command_returncodes':[r['returncode'] for r in q['commands']]}))

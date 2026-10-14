from pathlib import Path
from datetime import UTC, datetime
import ast
import copy
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys

ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = ROOT / 'evidence/iwyu-build'
D = Path(__file__).parent
HELPER = ROOT / 'dev/toolchains/iwyu_build.py'
PYTHON = '/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3'
HELPER_SHA = '48b95b5252fef0cfed97c1b45d99678c771a54f9262c5361d68f3fb6a2c34c6c'
PROPOSAL_SHA = 'abb28db8d94958fc5f8d649d3ffa4fdf877b574453ef6bd6aa071738255f4ba8'

def load(path): return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def record(path):
    path = Path(path)
    return {'path':str(path), 'sha256':sha(path), 'bytes':path.stat().st_size}
def save(name, value): (D/name).write_text(json.dumps(value,indent=2)+'\n')

intake = load(D/'intake.json')
proposal = load(E/'proposal.json')
def frozen():
    assert sha(HELPER)==HELPER_SHA and sha(E/'proposal.json')==PROPOSAL_SHA
    for path, value in (proposal['inputs']|intake['maintained']).items(): assert sha(ROOT/path)==value,path
    for path, value in proposal['tools'].items(): assert sha(path)==value,path
    assert sha(Path(proposal['sdk']['path'])/'SDKSettings.json')==proposal['sdk']['settings_sha256']
    for row in load(ROOT/'evidence/onboarding/baseline-files.json')['files']:
        assert sha(ROOT/row['path'])==row['sha256'] and (ROOT/row['path']).stat().st_size==row['bytes']

report = {'state':'RUNNING','started_at':datetime.now(UTC).isoformat(),'commands':[],'pure_controls':[]}
try:
    frozen()
    assert proposal['base_head']==intake['head']=='ec1b5353ec9ab684d5a3668675778ca503923d4a'
    assert proposal['helper_sha256']==HELPER_SHA and len(proposal['inputs'])==52 and len(proposal['tools'])==11
    assert proposal['jobs']==1 and proposal['timeouts']=={'configure':180,'build':1800,'install':120}
    assert proposal['disk_reserve_bytes']==8589934592
    manifests = ['preparation-manifest.json','preparation-1-manifest.json']
    copies = 0
    for name in manifests:
        for item in load(E/name)['files']:
            for path in (Path(item['source']),ROOT/item['path']):
                assert sha(path)==item['sha256'] and path.stat().st_size==item['bytes'],str(path)
            copies += 1
    assert copies==85
    prior = load(E/'preparation-1/proposal.json')
    old_helper = E/'preparation-1/iwyu_build.py.source'
    assert sha(old_helper)==prior['helper_sha256']
    old_block='''                assert len(planned) == 16 and all(row["command"] in planned for row in database)'''
    new_block='''                assert len(planned) == 16
                for line, row in zip(planned[:-1], database):
                    argv = shlex.split(line)
                    obj = str(Path(row["output"]).relative_to(build))
                    position = argv.index("-MT") - 1
                    assert argv[position:position + 5] == ["-MD", "-MT", obj, "-MF", obj + ".d"]
                    del argv[position:position + 5]
                    assert argv == shlex.split(row["command"])'''
    assert old_helper.read_text().count(old_block)==HELPER.read_text().count(new_block)==1
    assert old_helper.read_text().replace(old_block,new_block)==HELPER.read_text()
    previous_expected=copy.deepcopy(proposal)
    previous_expected['helper_sha256']=prior['helper_sha256']
    previous_expected['inputs']['dev/toolchains/iwyu_build.py']=prior['helper_sha256']
    assert previous_expected==prior
    old_manifest=load(E/'preparation-1/original-copy-manifest.json')
    for item in old_manifest['files']:
        assert sha(item['source'])==item['sha256']
        relocated=E/'preparation-1/logs'/Path(item['path']).name
        assert sha(relocated)==item['sha256']
    expected_cases=['before-iwyu-head','before-iwyu-tree','before-iwyu-status','before-iwyu-diff',
                    'before-llvm-head','before-llvm-tree','before-llvm-status','before-llvm-diff',
                    'default-before','named-profile','project-head','default-after',
                    'after-iwyu-head','after-iwyu-tree','after-iwyu-status','after-iwyu-diff',
                    'after-llvm-head','after-llvm-tree','after-llvm-status','after-llvm-diff']
    for sub, expected in [('preparation',proposal),('preparation-1/logs',prior)]:
        q=load(E/sub/'qualification.json');inv=load(E/sub/'invocation.json')
        assert q['proposal']==expected and q['helper_sha256']==expected['helper_sha256']
        assert q['state']=='PASS: preparation only' and q['execute'] is False and q['protected_state_unchanged'] is True
        assert [c['case'] for c in q['commands']]==expected_cases and all(c['returncode']==0 for c in q['commands'])
        assert inv['returncode']==0 and not inv['stderr'] and '--execute' not in inv['argv']
        emitted=[json.loads(line) for line in inv['stdout'].splitlines()]
        assert emitted[:-1]==[{'case':c['case'],'returncode':0} for c in q['commands']]
        assert emitted[-1]['state']==q['state']
        for command in q['commands']:
            for row in command['logs']: assert sha(row['path'])==row['sha256']
        bycase={c['case']:Path(c['logs'][0]['path']).read_text() for c in q['commands']}
        for family in ('iwyu','llvm'):
            for key in ('head','tree','status','diff'):
                assert bycase['before-'+family+'-'+key]==bycase['after-'+family+'-'+key]
        assert bycase['default-before']==bycase['default-after']==(ROOT/'evidence/p2996-registration/operation/default-after.stdout').read_text()
        assert json.loads(bycase['named-profile'])==expected['selected_environment']
        assert bycase['project-head'].strip()==expected['base_head']
    static=load(E/'preparation-static-checks.json')
    assert all(c['returncode']==0 for c in static) and len(static)==2
    assert json.loads(static[1]['stdout'])['checks']['baseline']==19
    pre=ROOT/'evidence/iwyu-source/preparation-review.json'
    assert sha(pre)=='63ee85f2a4e3f1dba7d09d7e8dc414471b4a2852dc5a8ba782899d76836df5fc'
    assert load(pre)['result'].startswith('PASS') and not load(pre)['findings']
    acquisition=load(ROOT/'evidence/iwyu-source/operation/acquisition.json')
    modes=load(ROOT/'evidence/iwyu-source/independent-review/source-before.json')
    source=Path(proposal['source'])
    for row in acquisition['verified_files']:
        path=source/row['path']
        assert not path.is_symlink() and sha(path)==row['sha256'] and path.stat().st_size==row['bytes']
        assert oct(path.stat().st_mode & 0o777)==modes[row['path']]['mode']
    baseline=load(ROOT/'evidence/p2996-registration/independent-registration/post-state.json')
    for name,row in baseline['protected']['global_files'].items():
        path=Path.home()/'.config/mise'/name
        assert not path.is_symlink() and sha(path)==row['sha256'] and oct(path.stat().st_mode & 0o777)==row['mode']
    frozen_run=ROOT/'evidence/p2996-math-resume/operation/p2996_build.py.source'
    assert sha(frozen_run)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
    assert sha(ROOT/'dev/toolchains/p2996_reflection.py')=='10bcbabc0a7143dadd6a6364df0fdb5f7fffbf83c946e81e63254ce5ef18eeff'
    lock=Path('/Users/rmanaloto/dev/github/ray-manaloto/dotfiles/python/src/dotfiles_setup/host_lock.py')
    assert sha(lock)=='b20e5d969e7534b9a93a61c1ca1669483300aa8949f682be9ee90cda34d72d20'
    tree=ast.parse(HELPER.read_text())
    native=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and n.lineno==132)
    compile_nodes=[n for n in ast.walk(tree) if hasattr(n,'lineno') and n.lineno in (168,169,170,176,177,178,185) and isinstance(n,(ast.Assign,ast.Assert,ast.For))]
    assert sorted(n.lineno for n in compile_nodes)==[168,169,170,176,177,178,185]
    compile_code=compile(ast.Module(body=sorted(compile_nodes,key=lambda n:n.lineno),type_ignores=[]),str(HELPER),'exec')
    admission_code=compile(ast.Module(body=[n for n in native.body if isinstance(n,ast.Assert) and 135<=n.lineno<=137],type_ignores=[]),str(HELPER),'exec')
    def admit(change=None):
        directory=D/'uncreated-native-operation'
        admission={'helper_sha256':HELPER_SHA,'run_directory':str(directory),'review_sha256':'bound-review'}
        review={'result':'PASS pre-run review','findings':[],'proposal_sha256':PROPOSAL_SHA}
        stored=copy.deepcopy(proposal)
        if change: change(admission,review,stored)
        exec(admission_code,{'admission':admission,'review':review,'report':{'helper_sha256':HELPER_SHA},'directory':directory,
                             'evidence':E,'digest':lambda p: PROPOSAL_SHA if p.name=='proposal.json' else 'bound-review',
                             'load':lambda p:stored,'proposal':proposal})
    def control(name,call,reject=False):
        try: call()
        except (AssertionError,ValueError,IndexError) as error:
            if not reject: raise
            report['pure_controls'].append({'case':name,'outcome':'REJECTED','exception':type(error).__name__})
        else:
            assert not reject,name
            report['pure_controls'].append({'case':name,'outcome':'ACCEPTED'})
    control('admission-positive',admit)
    for name,change in [
        ('admission-helper',lambda a,r,p:a.update(helper_sha256='wrong')),
        ('admission-directory',lambda a,r,p:a.update(run_directory='/wrong')),
        ('admission-review-hash',lambda a,r,p:a.update(review_sha256='wrong')),
        ('admission-review-fail',lambda a,r,p:r.update(result='FAIL')),
        ('admission-open-finding',lambda a,r,p:r.update(findings=['unresolved'])),
        ('admission-proposal-hash',lambda a,r,p:r.update(proposal_sha256='wrong')),
        ('admission-proposal-content',lambda a,r,p:p.update(jobs=2))]:
        control(name,lambda change=change:admit(change),True)
    build=D/'uncreated-synthetic-build';prefix=Path(proposal['llvm_prefix'])
    bootstrap=load(ROOT/'evidence/iwyu-source/native-prerequisite.json')['bootstrap']
    cxx=bootstrap['tools']['cxx']['path'];sdk=proposal['sdk']['path'];ninja=bootstrap['tools']['ninja']['path']
    cmakelists=(source/'CMakeLists.txt').read_text()
    block=cmakelists.split('add_llvm_executable(include-what-you-use\n',1)[1].split('\n)',1)[0]
    sources=[s.strip() for s in block.splitlines() if s.strip()]
    assert len(sources)==15 and all((source/name).is_file() for name in sources)
    database=[];planned=[]
    for name in sources:
        obj='CMakeFiles/include-what-you-use.dir/'+name+'.o'
        argv=[cxx,'-I'+str(prefix/'include'),'-O3','-DNDEBUG','-std=c++17','-arch','arm64','-isysroot',sdk,
              '-mmacosx-version-min=27.0','-fno-exceptions','-fno-rtti','-UNDEBUG','-o',obj,'-c',str(source/name)]
        database.append({'directory':str(build),'file':str(source/name),'output':str(build/obj),'command':shlex.join(argv)})
        planned.append(shlex.join(argv[:-4]+['-MD','-MT',obj,'-MF',obj+'.d']+argv[-4:]))
    planned.append(': && '+shlex.join([cxx,*[str(Path(row['output']).relative_to(build)) for row in database],
                                      str(prefix/'lib/libclang-cpp.dylib'),str(prefix/'lib/libLLVM.dylib'),'-o','bin/include-what-you-use'])+' && :')
    def compare(change=None):
        rows=copy.deepcopy(database);lines=planned.copy()
        if change: change(rows,lines)
        def planned_only(label,argv,**kwargs):
            assert label=='build-commands' and argv==[ninja,'-C',build,'-t','commands','include-what-you-use']
            return '\n'.join(lines)+'\n'
        exec(compile_code,{'load':lambda p:rows,'run':planned_only,'build':build,'source':source,'prefix':prefix,
                          'cxx':cxx,'sdk':sdk,'Path':Path,'shlex':shlex,'base':[],'ninja':ninja,'fd':None})
    control('compile-and-plan-positive-synthetic',compare)
    def bad_command(rows,lines,old,new):
        rows[0]['command']=rows[0]['command'].replace(old,new)
        lines[0]=lines[0].replace(old,new)
    for name,change in [
        ('missing-compile-row',lambda r,p:r.pop()),
        ('wrong-compiler',lambda r,p:bad_command(r,p,cxx,'/unadmitted/cxx')),
        ('wrong-sdk',lambda r,p:bad_command(r,p,sdk,'/unadmitted/sdk')),
        ('wrong-arch',lambda r,p:bad_command(r,p,'-arch arm64','-arch x86_64')),
        ('reflection-leak',lambda r,p:bad_command(r,p,'-O3','-O3 -freflection')),
        ('private-product-stdlib',lambda r,p:bad_command(r,p,'-O3','-O3 -stdlib=libc++')),
        ('changed-planned-token',lambda r,p:p.__setitem__(0,p[0]+' -unexpected')),
        ('wrong-dependency-option',lambda r,p:p.__setitem__(0,p[0].replace('-MD','-MMD',1))),
        ('wrong-dependency-output',lambda r,p:p.__setitem__(0,p[0].replace('-MT CMakeFiles','-MT wrong/CMakeFiles',1))),
        ('wrong-dependency-file',lambda r,p:p.__setitem__(0,p[0].replace('.o.d','.wrong.d',1))),
        ('missing-planned-action',lambda r,p:p.pop()),
        ('wrong-fork-library',lambda r,p:p.__setitem__(-1,p[-1].replace(str(prefix/'lib/libLLVM'),'/unadmitted/libLLVM')))]:
        control(name,lambda change=change:compare(change),True)
    save('pure-fixture.json',{'kind':'synthetic data only; no configured IWYU build','database':database,'planned':planned,
                            'native_subprocesses':0,'controls':report['pure_controls']})
    cases=[('help',['--help'],0,'--execute'),('relative',['--run-dir','relative'],2,'normalized private directory'),
           ('project',['--run-dir',str(ROOT/'iwyu-rejected-review')],2,'protected project'),
           ('llvm-build',['--run-dir',str(prefix.parent/'iwyu-rejected-review')],2,'protected project')]
    environment={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','HOME':os.environ['HOME'],'LANG':'C','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'}
    for case,args,expected,diagnostic in cases:
        argv=[PYTHON,'-B',str(HELPER),*args]
        result=subprocess.run(argv,cwd=D,env=environment,stdin=subprocess.DEVNULL,capture_output=True,timeout=20)
        row={'case':case,'argv':argv,'returncode':result.returncode,'expected_returncode':expected,'logs':[]}
        for suffix,data in [('stdout',result.stdout),('stderr',result.stderr)]:
            path=D/(case+'.'+suffix);path.write_bytes(data);row['logs'].append(record(path))
        report['commands'].append(row)
        assert result.returncode==expected and diagnostic in (result.stdout+result.stderr).decode()
        assert not (D/'relative').exists() and not (ROOT/'iwyu-rejected-review').exists() and not (prefix.parent/'iwyu-rejected-review').exists()
    frozen()
    report.update(state='PASS',helper_sha256=HELPER_SHA,proposal_sha256=PROPOSAL_SHA,retained_copy_pairs=copies,
                  retained_preparation_commands=40,retained_preparation_logs=80,retained_wrapper_exits=[0,0],
                  current_source_files_checked=854,current_global_config_files_checked=9,admitted_inputs=52,tools=11,
                  original_Claude_files=19,recorded_static_gate_exits=[0,0],static_gates_rerun=False,
                  old_helper_reconstruction='Exact comparator-only reversal, matched to prior proposal hash',
                  new_native_configure_compiler_build_install_count=0,lease_or_docker_checks=0,findings=[])
except BaseException as error:
    report.update(state='FAIL',error=repr(error))
    raise
finally:
    report['completed_at']=datetime.now(UTC).isoformat()
    save('static-checks.json',report)
print(json.dumps({'state':report['state'],'copy_pairs':report['retained_copy_pairs'],'pure_controls':len(report['pure_controls']),
                  'native_argument_exit_codes':[c['returncode'] for c in report['commands']],'new_native_builds':0}))

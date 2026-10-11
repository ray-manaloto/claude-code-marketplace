import ast, importlib.util, io, json, os, re, shlex, shutil, signal, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from evidence_checks import flags, check_probe_logs, record, compile_matches_database

ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
directory=Path(__file__).resolve().parent
os.umask(0o077)
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'dev/toolchains'))
from gcc_install import digest, preserved, read
from mise_link_probe import snapshot
from vcpkg_register import install_entries
load=lambda p:json.loads(p.read_text())
def write(name,value):
    p=directory/name;p.write_text(json.dumps(value,indent=2)+'\n');return p
def extract(path,name,scope):
    node=next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
    return scope[name]
evidence=ROOT/'evidence/p2996-install'
E=ROOT/'evidence/p2996-cmake'
registered=ROOT/'evidence/p2996-registration'
helper=ROOT/'dev/toolchains/p2996_cmake.py'
assert digest(helper)=='b2b0a4b2fdff733dfc149b90773940ba64cc7654e83f34f6dac82119a0086ade'
assert digest(E/'operation/qualification.json')=='02125c09e603b3b780b769aa99eb7c8686645effd0144a59d40ac83a55532bc8'
parent=load(E/'operation/qualification.json');admission=load(E/'admission.json')
registration=load(registered/'operation/qualification.json');review=load(registered/'registration-review.json')
assert digest(registered/'registration-review.json')=='9b8e92ac14d9304d7055fa00a3348612251e8bd27247db0ead946179bc835437'
assert review['result'].startswith('PASS') and not review['findings'] and review['all_protected_state_unchanged']
assert digest(registered/'operation/qualification.json')==review['operation_sha256']
baseline=load(registered/'independent-registration/post-state.json')
assert digest(registered/'independent-registration/post-state.json')==review['post_state']['sha256']=='8a5f11975efc9a953d8b57bde87467af5460cd48a3f695224dcaa9148a205317'
inventory=load(evidence/'independent-installation/post-install-inventory.json')
assert digest(evidence/'independent-installation/post-install-inventory.json')==review['retained_source_build_inventory']['inventory_sha256']
assert digest(evidence/'operation/prefix-inventory.json')==review['prefix_inventory']['inventory_sha256']
for p,sha in registration['proposal']['bindings'].items():assert digest(Path(p))==sha,p
for name,sha in registration['proposal']['helpers'].items():assert digest(helper.with_name(name))==sha,name
assert digest(helper.with_name('p2996_register.py'))==review['helper_sha256']
runtime=load(ROOT/'evidence/p2996-reflection/operation/qualification.json')
assert digest(helper.with_name('p2996_reflection.py'))==runtime['helper_sha256']
prepared=ROOT/'evidence/p2996-cmake-preparation'
assert digest(prepared/'preparation-review.json')=='57c68380aa7fa80514c243a9ffdc2158b72ee86e66c0332bef817807026a82cf'
assert digest(prepared/'source-contract.json')==admission['source_contract_sha256']=='fc2f97efb1e768e98ede0ef76f3c1ced54ddfef081fc8532cd531fda4e19fb5c'
for r in load(prepared/'source-contract.json')['source_references']:assert digest(Path(r['path']))==r['sha256']
configuration=load(ROOT/'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
prefix=Path(inventory['prefix']);source=Path(configuration['source']);sdk=configuration['sdk']['path']
assert prefix==Path(review['proposal']['prefix']) and len(inventory['records'])==159
assert len(load(evidence/'operation/prefix-inventory.json'))==6411
assert directory==directory.resolve() and '%' not in str(directory)
assert not any(directory.is_relative_to(p) for p in [ROOT,Path(inventory['workspace']),source,Path.home()/'.config',Path.home()/'.local/share/mise'])
witness=helper.with_name('p2996_reflection.cpp')
assert digest(witness)==runtime['witness_sha256']==parent['witness_sha256']=='23cf7f270bdda566d002bacce165ac202165f85065092dcb8b742dfad81e3a41'
normal_argv=read('install-preimages.json')['normal_environment']['argv']
normal_env=load(Path(normal_argv[-1]).parent/'context.json')['environment']|{'MISE_OFFLINE':'1','MISE_AUTO_INSTALL':'0','MISE_EXEC_AUTO_INSTALL':'0','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_TERMINAL_PROMPT':'0'}
env=normal_env|{'MARKETPLACE_P2996_PREFIX':str(prefix)}
report={'state':'running','started_at':datetime.now(timezone.utc).isoformat(),'commands':[],'helper_sha256':digest(helper),'operation_sha256':digest(E/'operation/qualification.json'),'witness_sha256':digest(witness),'parent_evidence_verification':record(directory/'parent-evidence-verification.json')}
def save():write('native-checks.json',report)
def interrupted(signum,frame):raise KeyboardInterrupt('received signal '+str(signum))
for signum in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(signum,interrupted)
extract(helper.with_name('p2996_install.py'),'prefix_inventory',globals())
protected=extract(helper.with_name('p2996_reflection.py'),'protected',globals())
runner=ROOT/'evidence/p2996-math-resume/operation/p2996_build.py.source'
assert digest(runner)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
run_scope=globals()|{'directory':directory,'report':report,'env':env,'save':save}
native=extract(runner,'run',run_scope)
run=extract(helper,'run',globals())
parent_dir=Path(admission['run_directory']);parent_commands={c['case']:c for c in parent['commands']}
def prun(name,argv,timeout=45,descriptor=None,environment=None,expected=0):
    actual=list(map(str,argv));assert 0<timeout<=60
    expected_argv=[a.replace(str(parent_dir),str(directory)) for a in parent_commands[name]['argv']]
    assert actual==expected_argv,(name,actual,expected_argv)
    return run(name,actual,timeout=timeout,descriptor=descriptor,environment=environment,expected=expected)
maintained=['dev/toolchains/p2996_cmake.py','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
maintained_hashes={p:digest(ROOT/p) for p in maintained}
controls=[E/n for n in ['admission.json','operation-manifest.json','initial-pre-run-review.json','initial-helper.py.source','pre-run-review.json','preflight.json']]
controls += [ROOT/p for p in admission['fixture_inputs']]+[ROOT/'AGENTS.md',prepared/'source-contract.json',prepared/'preparation-review.json']
control_hashes={str(p):digest(p) for p in controls}
LOCK_MODULE=Path('/Users/rmanaloto/dev/github/ray-manaloto/dotfiles/python/src/dotfiles_setup/host_lock.py')
LOCK_SHA='b20e5d969e7534b9a93a61c1ca1669483300aa8949f682be9ee90cda34d72d20'
assert digest(LOCK_MODULE)==LOCK_SHA
spec=importlib.util.spec_from_file_location('marketplace_host_lock',LOCK_MODULE)
lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease)
lock_path=lease.lock_path(lease.HEAVY_GATE)
assert lock_path==Path.home()/'.local/state/dotfiles/heavy-gate.lock'
assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
cwd=directory/'cwd';cwd.mkdir(exist_ok=False)
lease_info={'module':str(LOCK_MODULE),'module_sha256':LOCK_SHA,'path':str(lock_path),'wait_seconds':0,'acquired':False,'released':False}
write('lease.json',lease_info)
def source_state(stage):
    for label,args in [('head',['rev-parse','HEAD']),('tree',['rev-parse','HEAD^{tree}']),('status',['status','--porcelain','--untracked-files=all']),('diff',['diff','--no-ext-diff','--binary'])]:
        text=run(stage+'-'+label,['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',source,*args],environment=normal_env|{'GIT_OPTIONAL_LOCKS':'0'})
        assert text==(registered/('operation/source-after-'+label+'.stdout')).read_text()==(E/('operation/source-after-'+label+'.stdout')).read_text()
try:
    protected();report['preservation_before_passed']=True;save()
    assert digest(Path(configuration['mise']['path']))==configuration['mise']['sha256']
    assert digest(Path(sdk)/'SDKSettings.json')==configuration['sdk']['settings_sha256']
    source_state('source-before')
    default=prun('default-before',normal_argv,environment=normal_env)
    assert default==(registered/'operation/default-after.stdout').read_text()
    base=[configuration['mise']['path'],'--no-hooks','-C',str(cwd),'-E','p2996','exec','--fresh-env','--no-deps','--']
    selected=json.loads(prun('named-profile',base+normal_argv[-2:]))
    assert selected==runtime['selected_environment']==load(E/'operation/named-profile.stdout')
    report['selected_environment']=selected;save()
    with lease.held(lease.HEAVY_GATE,'marketplace-p2996-cmake-cold-review',wait_s=0,out=io.StringIO()) as fd:
        assert fd is not None
        lease_info.update(acquired=True,acquired_at=datetime.now(timezone.utc).isoformat(),descriptor=fd,holder=lease.read_holder(lease.HEAVY_GATE).strip());write('lease.json',lease_info)
        processes=prun('capacity-processes',['/bin/ps','-axo','pid=,pcpu=,comm='])
        pattern=r'(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy'
        blockers=[line for line in processes.splitlines() if re.fullmatch(pattern,Path(line.split(maxsplit=2)[-1]).name)]
        free=shutil.disk_usage(directory).free
        write('capacity.json',{'observed_at':datetime.now(timezone.utc).isoformat(),'blockers':blockers,'free_disk_bytes':free,'required_free_disk_bytes':8*1024**3,'native_process_check_returncode':report['commands'][-1]['returncode']})
        assert not blockers and free>=8*1024**3
        host=load(ROOT/'evidence/tool-foundation/host-qualification.json')['binaries']
        cmake,ninja=[host[n]['resolved_path'] for n in ['cmake','ninja']];ctest=str(Path(cmake).with_name('ctest'))
        report['tool_hashes']={p:digest(Path(p)) for p in [cmake,ninja,ctest]}
        assert report['tool_hashes']==parent['tool_hashes']==admission['tool_hashes']
        assert prun('ctest-version',base+[ctest,'--version'],descriptor=fd).startswith('ctest version 4.4.4')
        fixture=ROOT/'scratch/p2996-toolchain';toolchain=ROOT/'cmake/toolchains/p2996-macos-arm64.cmake';build=directory/'build'
        assert not build.exists()
        options=['-G','Ninja Multi-Config','-DCMAKE_MAKE_PROGRAM='+ninja,'-DCMAKE_TOOLCHAIN_FILE='+str(toolchain),'-DCMAKE_TRY_COMPILE_CONFIGURATION=Debug']
        configure_epoch=time.time()
        prun('configure',base+[cmake,'--debug-trycompile','-S',fixture,'-B',build,*options],timeout=60,descriptor=fd)
        generated={};probe_artifacts={}
        for child in sorted((build/'CMakeFiles/CMakeScratch').glob('TryCompile-*')):
            contents=(child/'CMakeLists.txt').read_text()
            names=[n for n in ['CMakeCCompilerABI.c','CMakeCXXCompilerABI.cpp','private_runtime.cpp'] if n in contents]
            assert len(names)==1 and names[0] not in generated
            name=names[0]
            output=run('probe-'+name,base+[ninja,'-C',child,'-f','build-Debug.ninja','-t','commands'],descriptor=fd)
            lines=output.splitlines();assert len(lines)==2
            generated[name]={'directory':str(child),'lines':lines}
            artifacts={}
            for line in lines:
                a=shlex.split(line);is_compile='-c' in a
                a=flags(a,prefix,sdk,name!='CMakeCCompilerABI.c',linking=not is_compile,standard=name=='private_runtime.cpp' and is_compile)
                assert a.count('-o')==1
                p=(child/a[a.index('-o')+1]).resolve();assert p.is_relative_to(child)
                assert p.is_file() and p.stat().st_size>0 and p.stat().st_mtime>=configure_epoch-1
                kind='object' if is_compile else 'executable';assert kind not in artifacts
                copy=directory/'probe-artifacts'/name/(kind+'.bin');copy.parent.mkdir(parents=True,exist_ok=True)
                assert not copy.exists();shutil.copyfile(p,copy);assert digest(p)==digest(copy)
                artifacts[kind]=record(copy)|{'source':str(p),'fresh_after_configure':True}
            if name!='private_runtime.cpp':
                p=build/('CMakeFiles/4.4.4/CMakeDetermineCompilerABI_'+('C' if name=='CMakeCCompilerABI.c' else 'CXX')+'.bin')
                assert p.stat().st_mtime>=configure_epoch-1 and digest(p)==artifacts['executable']['sha256']
                copy=directory/'probe-artifacts'/name/'abi-copy.bin';assert not copy.exists();shutil.copyfile(p,copy)
                artifacts['abi-copy']=record(copy)|{'source':str(p),'same_bytes_as_executable':True}
            probe_artifacts[name]=artifacts
        assert len(generated)==3
        verified=check_probe_logs(build/'CMakeFiles/CMakeConfigureLog.yaml',generated,prefix,sdk)
        report['probes']=verified;report['probe_artifacts']=probe_artifacts
        captures=[]
        for p in sorted(build.rglob('*')):
            if p.is_file() and p.suffix in ('.txt','.cmake','.ninja','.json','.yaml','.cpp','.c','.cxx','.log'):
                p.read_text();copy=directory/'configured-evidence'/p.relative_to(build)
                copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(p.read_bytes());captures.append(record(copy))
        report['configured_evidence']=captures
        report['probes_captured_before_later_cmake_execution']=True;save()
        for lang in ['C','CXX']:
            text=(build/('CMakeFiles/4.4.4/CMake'+lang+'Compiler.cmake')).read_text()
            assert 'set(CMAKE_'+lang+'_COMPILER_WORKS TRUE)' in text and 'set(CMAKE_'+lang+'_ABI_COMPILED TRUE)' in text
        configurations=['Debug','Release','RelWithDebInfo','MinSizeRel'];compiled={};cdb=load(build/'compile_commands.json')
        assert len(cdb)==4
        for row in cdb:
            a=flags(shlex.split(row['command']),prefix,sdk,True,reflection=True,standard=True)
            confs=[a.split('=',1)[1].strip('"') for a in a if a.startswith('-DCMAKE_INTDIR=')]
            assert len(confs)==1 and confs[0] in configurations and confs[0] not in compiled
            assert Path(row['directory']).resolve()==build and Path(row['file']).resolve()==witness.resolve() and a.count('-o')==1
            p=(Path(row['directory'])/a[a.index('-o')+1]).resolve()
            assert p.is_relative_to(build) and confs[0] in p.parts and Path(row['output']).resolve()==p and not p.exists()
            compiled[confs[0]]=str(p)
        assert set(compiled)==set(configurations) and len(set(compiled.values()))==4
        report['compile_commands']=cdb;report['compile_database_outputs']=compiled;report['configurations']={};save()
        libs=[prefix/'lib'/n for n in ['libc++.dylib','libc++abi.dylib','libunwind.dylib']]
        for conf in configurations:
            binary=build/conf/'reflection';assert not binary.exists()
            output=prun('build-'+conf,base+[cmake,'--build',build,'--config',conf,'--parallel','1','--verbose'],timeout=60,descriptor=fd)
            lines=[line.split('] ',1)[1] for line in output.splitlines() if re.match(r'^\[[12]/2\] ',line)]
            assert len(lines)==2
            compile_args=next(shlex.split(line) for line in lines if ' -c ' in line)
            link_args=next(shlex.split(line) for line in lines if ' -c ' not in line)
            flags(compile_args,prefix,sdk,True,reflection=True,standard=True);flags(link_args,prefix,sdk,True,linking=True)
            compile_matches_database(compile_args,shlex.split(next(r['command'] for r in cdb if Path(r['output']).resolve()==Path(compiled[conf]))))
            assert Path(compiled[conf]).is_file() and binary.is_file() and binary.stat().st_size>0
            test=prun('test-'+conf,base+[ctest,'--test-dir',build,'-C',conf,'--output-on-failure','--no-tests=error'],descriptor=fd)
            assert '100% tests passed' in test and 'out of 1' in test
            assert 'Mach-O 64-bit executable arm64' in prun('architecture-'+conf,['/usr/bin/file','-b',binary],descriptor=fd)
            meta=prun('libraries-'+conf,['/usr/bin/otool','-L',binary],descriptor=fd)
            assert all(n in meta for n in ['libc++.','libc++abi.','libunwind.']) and '/usr/lib/libc++' not in meta and 'libstdc++' not in meta
            rpaths=prun('rpaths-'+conf,['/usr/bin/otool','-l',binary],descriptor=fd);assert 'path '+str(prefix/'lib')+' (offset ' in rpaths
            assert prun('runtime-'+conf,base+['/usr/bin/env','DYLD_PRINT_LIBRARIES=1',binary],descriptor=fd)=='reflection value=43 exception=ok\n'
            diagnostics=(directory/('runtime-'+conf+'.stderr')).read_text().splitlines();assert diagnostics and all(l.startswith('dyld[') for l in diagnostics)
            loaded=[l[l.find(str(prefix)):].strip() for l in diagnostics if str(prefix) in l]
            assert all(any(Path(p).resolve()==lib.resolve() for p in loaded) for lib in libs)
            summary=dict(l.split('=',1) for l in (build/('qualified-'+conf+'.txt')).read_text().splitlines())
            assert summary=={'compiler':str(prefix/'bin/clang++'),'version':'21.0.0','sdk':sdk,'architecture':'arm64','configuration':conf,'binary':str(binary)}
            report['configurations'][conf]={'binary':record(binary),'object':record(Path(compiled[conf])),'summary':summary,'loaded_private_images':loaded,'actual_compile_and_cdb_equal_except_verified_dependency_metadata':True};save()
        dependencies=prun('dependencies',base+[ninja,'-C',build,'-t','deps'],descriptor=fd)
        assert all(str(prefix/p) in dependencies for p in ['include/c++/v1/meta','lib/clang/21/include/stddef.h'])
        cases=[('wrong-lane',['MARKETPLACE_CPP_LANE=wrong'],[],'Select the task-07d qualified'),('dirty-flags',['CXXFLAGS=-DUNADMITTED'],[],'Unexpected CXXFLAGS'),('wrong-compiler',[],['-DCMAKE_CXX_COMPILER=/usr/bin/clang++'],'Conflicting CXX compiler'),('wrong-architecture',[],['-DCMAKE_OSX_ARCHITECTURES=x86_64'],'SDK, deployment target and architecture'),('launcher',[],['-DCMAKE_CXX_COMPILER_LAUNCHER=/usr/bin/false'],'Compiler and linker launchers'),('extra-libraries',[],['-DCMAKE_CXX_STANDARD_LIBRARIES=-lc++'],'Unexpected extra C++ standard libraries'),('forced-compiler',[],['-DCMAKE_CXX_COMPILER_FORCED=ON'],'Compiler and try_compile link checks'),('static-probe',[],['-DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY'],'Compiler and try_compile link checks')]
        report['negative_controls']=[]
        for name,overrides,arguments,message in cases:
            control=directory/name;assert not control.exists()
            prun(name,base+['/usr/bin/env',*overrides,cmake,'-S',fixture,'-B',control,*options,*arguments],descriptor=fd,expected=1)
            assert message in (directory/(name+'.stderr')).read_text() and not (control/'build.ninja').exists()
            assert not list(control.rglob('*.o')) and not list(control.rglob('reflection'))
            report['negative_controls'].append({'case':name,'returncode':1,'diagnostic':message,'no_generated_build_ninja_or_fixture_artifact':True});save()
    lease_info.update(released=True,released_at=datetime.now(timezone.utc).isoformat(),free_after_release=lease._probe_free(lock_path));write('lease.json',lease_info)
    assert lease_info['free_after_release']
    assert prun('default-after',normal_argv,environment=normal_env)==default
    source_state('source-after')
    static_env=normal_env.copy()
    for key in ['GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM']:static_env.pop(key,None)
    static_env.update(MARKETPLACE_MISE_BIN=configuration['mise']['path'],MARKETPLACE_PYTHON='/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3',PYTHONDONTWRITEBYTECODE='1')
    run('tasks-validate',[ROOT/'dev/mise','tasks','validate'],environment=static_env)
    text=run('acceptance-baseline',[ROOT/'dev/mise','run','check:acceptance-baseline'],environment=static_env)
    static=json.loads(next(l for l in text.splitlines() if l.startswith('{')));assert static['status']=='pass' and static['checks']['baseline']==19
    report['static_counts']=static['checks']
    git=['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',ROOT]
    ids=run('root-identity',git+['rev-parse','--show-toplevel','--git-common-dir','HEAD'],environment=static_env).splitlines()
    branch=run('root-branch',git+['symbolic-ref','--short','HEAD'],environment=static_env).strip()
    assert ids==[str(ROOT),'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git','a99c7900115128108a3a525de687a2a1f137b07c'] and branch=='codex/marketplace-native-onboarding'
    run('root-status',git+['status','--porcelain','--untracked-files=normal'],environment=static_env)
    report['identity']={'root':ids[0],'common_git_directory':ids[1],'head':ids[2],'branch':branch}
    assert {p:digest(ROOT/p) for p in maintained}==maintained_hashes
    assert {p:digest(Path(p)) for p in control_hashes}==control_hashes
    assert digest(Path(configuration['mise']['path']))==configuration['mise']['sha256'] and digest(Path(sdk)/'SDKSettings.json')==configuration['sdk']['settings_sha256']
    report['maintained_file_hashes']=maintained_hashes;report['control_file_hashes']=control_hashes
    report['state']='PASS: independent native P2996 CMake probes, four cells and eight controls'
except BaseException as error:
    report.update(state='FAIL',error=repr(error));raise
finally:
    try:
        protected();report['all_protected_state_unchanged']=True
    except BaseException as error:
        report.update(state='FAIL',preservation_error=repr(error));raise
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();save()
print(json.dumps({'state':report['state'],'directory':str(directory),'native_commands':len(report['commands']),'exits':{c['case']:c['returncode'] for c in report['commands']},'static_counts':report.get('static_counts')}),flush=True)

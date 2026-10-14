from pathlib import Path
from datetime import datetime, timezone
import ast, errno, hashlib, importlib.util, io, json, os, re, shutil, signal, subprocess, sys, time

ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
directory = Path(__file__).resolve().parent
os.umask(0o077)
load = lambda p: json.loads(p.read_text())
def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()
def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')
report = load(directory / 'reflection-review.json')
assert report['result'] == 'IN_PROGRESS' and not report['commands']
qpath = ROOT / 'evidence/p2996-reflection/operation/qualification.json'
operation = qpath.parent
q = load(qpath)
assert digest(qpath) == report['operation_sha256']
assert digest(ROOT / 'dev/toolchains/p2996_reflection.py') == report['helper_sha256']
witness = ROOT / 'dev/toolchains/p2996_reflection.cpp'
assert digest(witness) == report['witness_sha256']
install = ROOT / 'evidence/p2996-install'
inventory_path = install / 'independent-installation/post-install-inventory.json'
state_path = install / 'independent-installation/post-state.json'
inventory = load(inventory_path)
baseline = load(state_path)
prefix = Path(inventory['prefix'])
configuration = load(ROOT / 'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
source = Path(configuration['source'])
assert not directory.is_relative_to(ROOT) and not directory.is_relative_to(Path(inventory['workspace'])) and not directory.is_relative_to(source)
normal_argv = next(c['argv'] for c in q['commands'] if c['case'] == 'default-before')
context_path = Path(normal_argv[-1]).parent / 'context.json'
context = load(context_path)
env = context['environment'] | {'MISE_OFFLINE':'1', 'MISE_AUTO_INSTALL':'0', 'MISE_EXEC_AUTO_INSTALL':'0', 'GIT_CONFIG_GLOBAL':'/dev/null', 'GIT_CONFIG_SYSTEM':'/dev/null', 'GIT_TERMINAL_PROMPT':'0'}
assert 'MARKETPLACE_P2996_PREFIX' not in env
assert digest(Path(configuration['mise']['path'])) == configuration['mise']['sha256']
assert digest(Path(configuration['sdk']['path']) / 'SDKSettings.json') == configuration['sdk']['settings_sha256']
report['environment_context_sha256'] = digest(context_path)
report['environment_handling'] = 'Original captured context plus the exact helper offline/no-install/Git-isolation overrides; private prefix only during named-profile probes. Environment values are not persisted.'

def save():
    tmp = directory / 'reflection-review.json.tmp'
    dump(tmp, report)
    tmp.replace(directory / 'reflection-review.json')

# Extract only these already inspected functions; never import helper mains.
function_sources = {
    'dev/toolchains/gcc_install.py': ['package_state'],
    'dev/toolchains/mise_link_probe.py': ['snapshot'],
    'dev/toolchains/vcpkg_register.py': ['install_entries'],
    'dev/toolchains/p2996_install.py': ['prefix_inventory'],
    'evidence/p2996-math-resume/operation/p2996_build.py.source': ['run'],
}
PREFIX = Path('/opt/homebrew')
report['extracted_function_sources'] = []
for rel, names in function_sources.items():
    path = ROOT / rel
    text = path.read_text()
    tree = ast.parse(text)
    nodes = [next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name) for name in names]
    if names == ['run']:
        assert digest(path) == '7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
    report['extracted_function_sources'].append({'path':str(path), 'sha256':digest(path), 'names':names, 'ast_sha256':hashlib.sha256(ast.dump(ast.Module(body=nodes, type_ignores=[]), include_attributes=False).encode()).hexdigest()})
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), globals())

for name, sha in load(install / 'operation/qualification.json')['proposal']['helpers'].items():
    assert digest(ROOT / 'dev/toolchains' / name) == sha, name

def protected_state():
    rows = baseline['protected']
    state = {'protected': {
        'global_files': {n: {'sha256':digest(Path.home()/'.config/mise'/n), 'mode':oct((Path.home()/'.config/mise'/n).stat().st_mode & 0o777)} for n in rows['global_files']},
        'packages': {n:package_state(n) for n in rows['packages']},
        'glib_files': {n:{'sha256':digest(Path(n))} for n in rows['glib_files']}},
        'directories': {n:snapshot(Path(n)) for n in baseline['directories']},
        'install_entries': install_entries(Path.home()/'.local/share/mise/installs')}
    assert all(not (Path.home()/'.config/mise'/n).is_symlink() for n in rows['global_files'])
    assert state == baseline
    return state

def retained_records():
    observed = []
    for expected in inventory['records']:
        p = Path(expected['path'])
        actual = {k:v for k,v in expected.items() if k not in ('lexists','exists','lstat_mode','resolved_path','mode','sha256','bytes','symlink_target')}
        actual.update(lexists=os.path.lexists(p), exists=p.exists())
        if actual['lexists']:
            actual['lstat_mode'] = oct(p.lstat().st_mode & 0o777)
        if actual['exists']:
            actual.update(resolved_path=str(p.resolve()), mode=oct(p.stat().st_mode & 0o777))
        if 'sha256' in expected:
            actual.update(sha256=digest(p), bytes=p.stat().st_size)
        if p.is_symlink():
            actual['symlink_target'] = os.readlink(p)
        assert actual == expected, str(p)
        observed.append(actual)
    assert len(observed) == 159
    return observed

def preservation(stage):
    captured_prefix = prefix_inventory(prefix)
    assert captured_prefix == load(install / 'operation/prefix-inventory.json') and len(captured_prefix) == 6411
    dump(directory / f'{stage}-prefix.json', captured_prefix)
    dump(directory / f'{stage}-retained.json', retained_records())
    dump(directory / f'{stage}-state.json', protected_state())
    assert all(digest(Path(p)) == sha for p, sha in report['maintained_preimages'].items())
    assert digest(Path(configuration['mise']['path'])) == configuration['mise']['sha256']
    report[stage + '_preservation'] = {'full_prefix_records':6411, 'retained_records':159, 'global_files':len(baseline['protected']['global_files']), 'packages':len(baseline['protected']['packages']), 'glib_files':len(baseline['protected']['glib_files']), 'directory_entries':{k:len(v) for k,v in baseline['directories'].items()}, 'mise_install_entries':len(baseline['install_entries']), 'five_maintained_files_unchanged':True, 'mise_binary_unchanged':True}
    save()

def source_state(stage):
    for label, args in [('head',['rev-parse','HEAD']), ('tree',['rev-parse','HEAD^{tree}']), ('diff',['diff','--no-ext-diff','--binary']), ('status',['status','--porcelain','--untracked-files=all'])]:
        run('source-' + stage + '-' + label, ['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',source,*args])
        assert (directory / f'source-{stage}-{label}.stdout').read_bytes() == (operation / f'source-before-{label}.stdout').read_bytes(), label

def validate_origin(target, binary):
    build = (target / 'reflection-build.stderr').read_text()
    assert configuration['pin'] in build and str(prefix/'bin/clang-21') in build
    includes = build.split('#include <...> search starts here:\n',1)[1].split('End of search list.',1)[0]
    assert str(prefix/'include/c++/v1') in includes and str(prefix/'lib/clang/21/include') in includes
    assert '/opt/homebrew/' not in includes and '/usr/include/c++' not in includes
    dynamic = (target / 'reflection-run.stderr').read_text()
    loaded = [line[line.find(str(prefix)):].strip() for line in dynamic.splitlines() if str(prefix) in line]
    libraries = [prefix/'lib'/n for n in ('libc++.dylib','libc++abi.dylib','libunwind.dylib')]
    assert all(any(Path(p).resolve() == lib.resolve() for p in loaded) for lib in libraries)
    direct = (target / 'witness-libraries.stdout').read_text().splitlines()[1:]
    assert [line.strip().split(' (')[0] for line in direct] == ['@rpath/libc++.1.dylib','@rpath/libc++abi.1.dylib','@rpath/libunwind.1.dylib','/usr/lib/libSystem.B.dylib']
    symbols = (target / 'witness-symbols.stdout').read_text()
    for name, origin in [('___cxa_throw','libc++'),('___cxa_begin_catch','libc++'),('__Unwind_Resume','libunwind')]:
        assert any(re.search(r'\b' + re.escape(name) + r' \(from ' + re.escape(origin) + r'\)$', line) for line in symbols.splitlines()), name
    assert any('__ZNSt3__112basic_string' in line and line.endswith('(from libc++)') for line in symbols.splitlines())
    assert (target / 'reflection-run.stdout').read_text() == 'reflection value=43 exception=ok\n'
    return {'binary':str(binary), 'sha256':digest(binary), 'loaded_private_images':loaded, 'runtime_output':'reflection value=43 exception=ok\n', 'explicit_private_header_paths':True, 'private_cpp_exception_symbol_origin':True, 'private_unwind_symbol_origin':True}

# Parent provenance checks read the retained original logs; they do not execute the compiler.
assert q['feature_macros'] == {'__cplusplus':'202400L','__clang_major__':'21','_LIBCPP_VERSION':'210000'}
macros = dict(re.findall(r'^#define (__cplusplus|__clang_major__|_LIBCPP_VERSION) (.+)$', (operation/'feature-macros.stdout').read_text(), re.M))
assert macros == q['feature_macros']
headers = (operation/'header-dependencies.stdout').read_text()
assert str(prefix/'include/c++/v1/meta') in headers and '/opt/homebrew/' not in headers and '/usr/include/c++' not in headers
report['parent_origin_verification'] = validate_origin(operation, Path(q['witness']['path']))
report['parent_negative_diagnostic'] = (operation/'without-reflection.stderr').read_text()
assert 'P2996 reflection requires -freflection' in report['parent_negative_diagnostic']

LOCK_MODULE = Path('/Users/rmanaloto/dev/github/ray-manaloto/dotfiles/python/src/dotfiles_setup/host_lock.py')
LOCK_SHA = 'b20e5d969e7534b9a93a61c1ca1669483300aa8949f682be9ee90cda34d72d20'
assert digest(LOCK_MODULE) == LOCK_SHA
spec = importlib.util.spec_from_file_location('marketplace_reflection_review_host_lock', LOCK_MODULE)
lease = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lease)
assert lease.lock_path(lease.HEAVY_GATE) == Path.home()/'.local/state/dotfiles/heavy-gate.lock'
assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
    signal.signal(signum, lambda signum, frame: (_ for _ in ()).throw(KeyboardInterrupt('received signal ' + str(signum))))

try:
    preservation('before')
    source_state('before')
    env['MARKETPLACE_P2996_PREFIX'] = str(prefix)
    base = [configuration['mise']['path'],'--no-hooks','-C',directory/'cwd','-E','p2996','exec','--fresh-env','--no-deps','--']
    selected = json.loads(run('named-profile', base + normal_argv[-2:]))
    assert selected == q['selected_environment']
    original_isolated = next(c['argv'] for c in q['commands'] if c['case'] == 'isolated-environment')
    tail = original_isolated[original_isolated.index('--') + 1:]
    isolated = run('isolated-environment', base + tail)
    assert json.loads(isolated) == json.loads((operation/'isolated-environment.stdout').read_text())
    assert all(v is None for v in json.loads(isolated).values())
    trace = io.StringIO()
    with lease.held(lease.HEAVY_GATE, 'marketplace-p2996-reflection-independent-review', wait_s=0, out=trace) as fd:
        assert fd is not None
        report['independent_admission'] = {'parent_channel':'native collaboration /root', 'scope':'One positive compile/link/run and one syntax-only negative, each <=60 seconds; no helper main or shared admission changes', 'canonical_lock':str(lease.lock_path(lease.HEAVY_GATE)), 'lock_module_sha256':LOCK_SHA, 'lease_fd':fd, 'at':datetime.now(timezone.utc).isoformat()}
        processes = run('capacity-processes', ['/bin/ps','-axo','pid=,pcpu=,comm='])
        matches = [line for line in processes.splitlines() if re.fullmatch(r'(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld', Path(line.split(maxsplit=2)[-1]).name)]
        assert not matches, matches
        report['independent_admission'].update(active_builders=matches, free_bytes=shutil.disk_usage(directory).free, load=os.getloadavg())
        assert report['independent_admission']['free_bytes'] >= 8 * 1024**3
        assert digest(witness) == q['witness_sha256'] and digest(qpath) == report['operation_sha256']
        with (directory/'runtime-attempt-once').open('x') as once:
            once.write(datetime.now(timezone.utc).isoformat()+'\n')
        binary = directory/'reflection'
        flags = q['flags']
        cxx = prefix/'bin/clang++'
        libraries = [prefix/'lib'/n for n in ('libc++.dylib','libc++abi.dylib','libunwind.dylib')]
        build_argv = base + [cxx,*flags,'-nostdlib++','-O0','-g','-v',witness,*libraries,'-Wl,-rpath,'+str(prefix/'lib'),'-o',binary]
        # The only argument changes from the parent build are the private cwd and output binary.
        parent_build = next(c['argv'] for c in q['commands'] if c['case'] == 'reflection-build')
        expected_build = [str(directory/'cwd') if a == str(Path(q['witness']['path']).parent/'cwd') else str(binary) if a == q['witness']['path'] else a for a in parent_build]
        assert list(map(str,build_argv)) == expected_build
        run('reflection-build', build_argv, timeout=60, descriptor=fd)
        output = run('reflection-run', base + ['/usr/bin/env','DYLD_PRINT_LIBRARIES=1',binary], timeout=60, descriptor=fd)
        assert output == 'reflection value=43 exception=ok\n'
        run('witness-libraries', ['/usr/bin/otool','-L',binary])
        run('witness-symbols', ['/usr/bin/nm','-m','-u',binary])
        report['independent_origin_verification'] = validate_origin(directory,binary)
        negative = [f for f in flags if f != '-freflection']
        try:
            run('without-reflection', base + [cxx,*negative,'-fsyntax-only',witness], timeout=60, descriptor=fd)
        except AssertionError:
            assert report['commands'][-1]['case'] == 'without-reflection' and report['commands'][-1]['returncode'] == 1
        else:
            raise AssertionError('negative control unexpectedly compiled')
        diagnostic = (directory/'without-reflection.stderr').read_text()
        assert 'P2996 reflection requires -freflection' in diagnostic and '1 error generated.' in diagnostic
        assert (directory/'without-reflection.stdout').read_text() == ''
        report['independent_negative_diagnostic'] = diagnostic
    try:
        os.fstat(fd)
    except OSError as err:
        assert err.errno == errno.EBADF
    else:
        raise AssertionError('lease descriptor remained open')
    report['lease_released'] = True
    (directory/'lease-trace.txt').write_text(trace.getvalue())
    env.pop('MARKETPLACE_P2996_PREFIX')
    normal = run('default-consumer', normal_argv)
    assert normal.encode() == (operation/'default-before.stdout').read_bytes() == (operation/'default-after.stdout').read_bytes()
    report['default_consumer_invocations'] = 1
    report['default_consumer_sha256'] = digest(directory/'default-consumer.stdout')
    source_state('after')
    # Explicit local executables avoid inheriting a different Python/mise from the review shell.
    env['MARKETPLACE_MISE_BIN'] = configuration['mise']['path']
    env['MARKETPLACE_PYTHON'] = '/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3'
    report['static_check_environment_overrides'] = {k:env[k] for k in ('MARKETPLACE_MISE_BIN','MARKETPLACE_PYTHON')}
    run('tasks-validate', [ROOT/'dev/mise','tasks','validate'])
    run('acceptance-baseline', [ROOT/'dev/mise','run','check:acceptance-baseline'], timeout=60)
    run('project-diff-check', ['/usr/bin/git','--no-optional-locks','-C',ROOT,'diff','--check'])
    ident = run('project-identity', ['/usr/bin/git','--no-optional-locks','-C',ROOT,'rev-parse','HEAD','--git-common-dir']).splitlines()
    assert ident == [report['head'],report['common_git_dir']]
    assert run('project-branch', ['/usr/bin/git','--no-optional-locks','-C',ROOT,'branch','--show-current']).strip() == report['branch']
    run('project-status', ['/usr/bin/git','--no-optional-locks','-C',ROOT,'status','--short'])
    report['runtime_checks_complete'] = True
except BaseException as error:
    report['result'] = 'FAIL: independent review driver'
    report['error'] = repr(error)
    raise
finally:
    try:
        preservation('after')
        for name in ['prefix','retained','state']:
            assert (directory/f'before-{name}.json').read_bytes() == (directory/f'after-{name}.json').read_bytes(), name
        report['all_protected_state_unchanged'] = True
    except BaseException as error:
        report['result'] = 'FAIL: preservation'
        report['preservation_error'] = repr(error)
        raise
    finally:
        save()
        print(json.dumps({'review':str(directory/'reflection-review.json'),'runtime_checks_complete':report.get('runtime_checks_complete',False),'result':report['result']}),flush=True)

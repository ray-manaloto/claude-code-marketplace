from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os, struct, re

p = Path(__file__).resolve().parent
rp = p / 'build-review.json'
load = lambda f: json.loads(Path(f).read_text())
r = load(rp)
q = load(Path(r['operation_directory']) / 'qualification.json')
ws = Path(r['build_workspace'])
build = ws / 'build'
source = Path(r['source']['path'])
old = load(r['prior_inventory']['path'])
retained = load(r['retained_preimages']['path'])
cache = {}

def sha(f):
    f = Path(f)
    key = str(f.resolve())
    if key not in cache:
        with f.open('rb') as s:
            cache[key] = hashlib.file_digest(s, 'sha256').hexdigest()
    return cache[key]

def row(f):
    f = Path(f)
    d = {'path': str(f), 'lexists': os.path.lexists(f), 'exists': f.exists()}
    if os.path.lexists(f):
        d['lstat_mode'] = oct(f.lstat().st_mode & 0o777)
    if f.is_symlink():
        d['symlink_target'] = os.readlink(f)
    if f.exists():
        d.update(resolved_path=str(f.resolve()), mode=oct(f.stat().st_mode & 0o777))
        if f.is_file():
            d.update(sha256=sha(f), bytes=f.stat().st_size)
            with f.open('rb') as stream:
                header = stream.read(32)
                if len(header) >= 32 and header[:4] == b'\xcf\xfa\xed\xfe':
                    fields = struct.unpack('<IiiIIIII', header)
                    d['macho'] = {'cpu_type': fields[1], 'cpu_subtype': fields[2], 'file_type': fields[3]}
                elif header.startswith(b'!<arch>\n'):
                    d['archive_magic'] = '!<arch>'
                elif header[:4] == b'\xca\xfe\xba\xbe':
                    count = struct.unpack('>I', header[4:8])[0]
                    assert 0 < count <= 16
                    stream.seek(8)
                    entries = [struct.unpack('>iiIII', stream.read(20)) for _ in range(count)]
                    d['fat_archives'] = []
                    for cpu, subtype, offset, size, alignment in entries:
                        stream.seek(offset)
                        magic = stream.read(8)
                        d['fat_archives'].append({'cpu_type': cpu, 'cpu_subtype': subtype, 'offset': offset, 'size': size, 'archive_magic': magic.decode('ascii', errors='replace').rstrip()})
    return d

records = {}
def add(f, category, required=False):
    f = Path(f)
    if str(f) not in records:
        records[str(f)] = row(f)
    d = records[str(f)]
    d.setdefault('categories', [])
    if category not in d['categories']:
        d['categories'].append(category)
    if required:
        assert d['exists'] and 'sha256' in d, str(f)
        d['required'] = True
    return d

def recorded_paths(v):
    if isinstance(v, dict):
        if 'path' in v:
            yield Path(v['path'])
        for item in v.values():
            yield from recorded_paths(item)
    elif isinstance(v, list):
        for item in v:
            yield from recorded_paths(item)

for v in retained['inventory_records']:
    add(v['path'], 'retained_build_scope')
for f in recorded_paths(old['child_generated']):
    add(f, 'child_configuration', True)
for v in old['outer_generated']:
    add(v['path'], 'outer_configuration', True)
tool_names = ['clang', 'clang++', 'llvm-config', 'clangd', 'clang-format', 'clang-tidy', 'llvm-cov', 'llvm-profdata']
for name in tool_names:
    d = add(build / 'bin' / name, 'required_tool', True)
    assert Path(d['resolved_path']).is_relative_to(build) and int(d['mode'], 8) & 0o111
    assert d['macho']['cpu_type'] == 0x100000c and d['macho']['file_type'] == 2, name
for v in old['artifacts']:
    add(v['path'], 'selected_library_or_support_tool', True)
for name in ['lib/libLTO.dylib', 'lib/libc++.1.0.dylib', 'lib/libc++experimental.a', 'cmake_install.cmake', 'tools/clang/cmake_install.cmake', 'lib/cmake/llvm/LLVMConfig.cmake', 'lib/cmake/clang/ClangConfig.cmake', 'tools/clang/include/clang/Basic/Version.inc', 'include/llvm/Config/llvm-config.h']:
    add(build / name, 'install_preparation_binding', True)
for v in q['refreshed_math_headers']:
    assert add(v['path'], 'refreshed_math_header', True)['sha256'] == v['sha256']
src = add(source / 'libcxx/include/__random/clamp_to_integral.h', 'unmodified_source_header', True)
dst = add(build / 'include/c++/v1/__random/clamp_to_integral.h', 'generated_header', True)
assert src['sha256'] == dst['sha256'] == '02e70e725be490bb68fb225055928c31e5d6583bf3bc41cc6e84fd8a9d089d21'
for v in r['source']['postimages']:
    assert add(source / v['path'], 'source_postimage', True)['sha256'] == v['after_sha256']
runtime_paths = sorted((build / 'lib/clang/21/lib/darwin').iterdir())
assert len(runtime_paths) == 14
for f in runtime_paths:
    d = add(f, 'compiler_rt_library', True)
    if f.suffix == '.dylib':
        assert d['macho']['cpu_type'] == 0x100000c and d['macho']['file_type'] == 6
    elif f.suffix == '.a':
        assert d.get('archive_magic') == '!<arch>' or all(v['cpu_type'] == 0x100000c and v['archive_magic'] == '!<arch>' for v in d.get('fat_archives', [])) and d.get('fat_archives')

def readcache(f):
    values = {}
    for line in f.read_text().splitlines():
        if line and not line.startswith(('#', '//')) and ':' in line and '=' in line:
            key, value = line.split('=', 1)
            values[key.split(':', 1)[0]] = value
    return values

children = {}
for child in ['builtins', 'runtimes']:
    childroot = build / 'runtimes' / (child + '-bins')
    values = readcache(childroot / 'CMakeCache.txt')
    for language in ['C', 'CXX', 'ASM']:
        assert Path(values['CMAKE_' + language + '_COMPILER']).resolve() == (build / 'bin' / ('clang++' if language == 'CXX' else 'clang')).resolve()
    for name, want in {'CMAKE_BUILD_TYPE': 'Release', 'CMAKE_OSX_ARCHITECTURES': 'arm64', 'CMAKE_OSX_DEPLOYMENT_TARGET': '27.0', 'CMAKE_OSX_SYSROOT': q['proposal']['configuration']['sdk']['path'], 'CMAKE_INSTALL_PREFIX': str(ws / 'prefix')}.items():
        assert values[name] == want, (child, name, values[name])
    selected = {k: v for k, v in values.items() if k.startswith(('CMAKE_C_COMPILER', 'CMAKE_CXX_COMPILER', 'CMAKE_ASM_COMPILER', 'CMAKE_OSX_', 'CMAKE_BUILD_TYPE', 'CMAKE_INSTALL_PREFIX', 'COMPILER_RT_BUILD_', 'LIBCXX_ENABLE_', 'LIBCXXABI_ENABLE_', 'LIBCXXABI_USE_', 'LIBUNWIND_ENABLE_', 'LLVM_ENABLE_RUNTIMES', 'LLVM_DEFAULT_TARGET_TRIPLE'))}
    if child == 'runtimes':
        for name in ['LIBCXX_ENABLE_SHARED', 'LIBCXX_ENABLE_STATIC', 'LIBCXXABI_ENABLE_SHARED', 'LIBCXXABI_ENABLE_STATIC', 'LIBUNWIND_ENABLE_SHARED', 'LIBUNWIND_ENABLE_STATIC', 'LIBCXXABI_USE_LLVM_UNWINDER', 'COMPILER_RT_BUILD_SANITIZERS', 'COMPILER_RT_BUILD_PROFILE']:
            assert values[name] == 'ON', name
        assert values['LLVM_ENABLE_RUNTIMES'] == 'libunwind;libcxxabi;libcxx;compiler-rt'
    stamps = build / 'runtimes' / (child + '-stamps')
    stamp_records = [add(f, 'child_completion_stamp') for f in sorted(stamps.iterdir()) if f.is_file()]
    done = add(stamps / (child + '-done'), 'child_completion_stamp', True)
    compiler_files = []
    for f in sorted((childroot / 'CMakeFiles/4.4.4').glob('CMake*Compiler.cmake')):
        add(f, 'child_compiler_identification', True)
        meta = dict(re.findall(r'set\((CMAKE_(?:C|CXX|ASM)_COMPILER(?:_ID|_VERSION|_ARCHITECTURE_ID)?) "([^"]*)"\)', f.read_text()))
        compiler_files.append({'path': str(f), 'values': meta})
    children[child] = {'cache': str(childroot / 'CMakeCache.txt'), 'selected_values': selected, 'compiler_identification': compiler_files, 'completion': done, 'stamp_count': len(stamp_records)}
for d in q['proposal']['inputs'].values():
    add(d.get('resolved_path', d.get('path')), 'bootstrap_input', True)
add(Path(q['proposal']['configuration']['sdk']['path']) / 'SDKSettings.json', 'sdk_settings', True)
assert not add(ws / 'prefix', 'uninstalled_prefix')['lexists']
ninja = {}
for name, sub in [('outer', build), ('builtins', build / 'runtimes/builtins-bins'), ('runtimes', build / 'runtimes/runtimes-bins')]:
    lr, dr = add(sub / '.ninja_log', 'ninja_state', True), add(sub / '.ninja_deps', 'ninja_state', True)
    lines = (sub / '.ninja_log').read_text().splitlines()
    assert lines[0] == '# ninja log v7'
    rows = [line.split('\t') for line in lines[1:] if line]
    assert all(len(x) == 5 for x in rows)
    missing = sorted({x[3] for x in rows if not (Path(x[3]) if Path(x[3]).is_absolute() else sub / x[3]).exists()})
    ninja[name] = {'log': lr, 'deps': dr, 'records': len(rows), 'unique_outputs': len({x[3] for x in rows}), 'historical_or_stamp_outputs_missing': missing, 'missing_output_count': len(missing)}
deltas = []
for v in retained['inventory_records']:
    now = records[v['path']]
    if v.get('sha256') != now.get('sha256') or v['exists'] != now['exists'] or v['lexists'] != now['lexists']:
        deltas.append({'path': v['path'], 'before_sha256': v.get('sha256'), 'after_sha256': now.get('sha256'), 'before_exists': v['exists'], 'after_exists': now['exists']})
for d in records.values():
    if d['exists'] and 'sha256' in d and Path(d['path']).is_relative_to(build):
        assert Path(d['resolved_path']).is_relative_to(build), d['path']
inventory = {'result': 'PASS: bounded post-build file inventory', 'observed_at': datetime.now(timezone.utc).isoformat(), 'operation_sha256': r['operation_sha256'], 'helper_sha256': r['helper_sha256'], 'workspace': str(ws), 'source_diff_sha256': r['source_diff_sha256'], 'records': list(records.values()), 'required_tools': tool_names, 'child_configurations': children, 'ninja_state': ninja, 'compiler_rt_directory_entries': [str(f) for f in runtime_paths], 'changes_since_retained_prebuild': deltas, 'limits': ['Bounded selected paths, not a complete install manifest. Later installation preparation must bind its concrete destination plan.', 'Historical missing Ninja outputs are recorded explicitly; required final tools and libraries are checked individually.', 'File identities and child configuration are static evidence; no compiler, runtime, sanitizer, coverage or LTO execution performed.']}
(p / 'post-build-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
r['post_build_inventory'] = {'path': str(p / 'post-build-inventory.json'), 'sha256': sha(p / 'post-build-inventory.json'), 'bytes': (p / 'post-build-inventory.json').stat().st_size}
r['inventory_summary'] = {'records': len(records), 'required_tools': 8, 'compiler_rt_libraries': len(runtime_paths), 'child_completion_markers': 2, 'ninja_files': 6, 'changed_retained_records': len(deltas), 'prefix_absent': True, 'libLTO_present': True}
r.setdefault('review_harness_notes', []).extend(['Initial pure-read inventory stopped on an incorrect guessed Clang version-header path. Actual generated path is tools/clang/include/clang/Basic/Version.inc.', 'Second pure-read inventory stopped because it assumed all static archives had a plain ar header. Native file metadata confirmed cc_kext and osx archives use an ARM64 fat wrapper; the collector now validates those archive slices. No product command was repeated.'])
rp.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({'inventory': r['post_build_inventory'], 'summary': r['inventory_summary'], 'changed_paths': [d['path'].removeprefix(str(build) + '/') for d in deltas], 'missing_ninja_output_counts': {k: v['missing_output_count'] for k, v in ninja.items()}}, indent=2))

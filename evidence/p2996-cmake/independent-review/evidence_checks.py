import hashlib, json, re, shlex
from pathlib import Path
import yaml

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size}

def read(path):
    return json.loads(Path(path).read_text())

def compile_matches_database(actual, database):
    assert actual.count('-o')==1 and actual.count('-MD')==1
    output=actual[actual.index('-o')+1]
    start=actual.index('-MD')
    assert actual[start:start+5]==['-MD','-MT',output,'-MF',output+'.d']
    assert actual[:start]+actual[start+5:]==database
    return True

def flags(arguments, prefix, sdk, cxx, linking=False, reflection=False, standard=False):
    args = list(arguments)
    if args[:2] == [':', '&&'] and args[-2:] == ['&&', ':']:
        args = args[2:-2]
    assert args[0] == str(prefix / 'bin' / ('clang++' if cxx else 'clang'))
    assert not any(a.startswith('@') or a == ':' or any(c in a for c in ';&|<>`$') for a in args)
    for name, value in [('-arch','arm64'),('-isysroot',sdk),('-resource-dir',str(prefix/'lib/clang/21'))]:
        assert args.count(name)==1 and args[args.index(name)+1]==value, (name,args)
    for flag in ['--no-default-config','-fno-blocks','-mmacosx-version-min=27.0']:
        assert args.count(flag)==1, flag
    assert args.count('-freflection') == int(reflection)
    standards = [a for a in args if a.startswith('-std=')]
    if standard: assert standards == ['-std=c++26']
    libraries=[str(prefix/'lib'/n) for n in ['libc++.dylib','libc++abi.dylib','libunwind.dylib']]
    if cxx:
        assert args.count('-stdlib=libc++')==1 and args.count('-nostdinc++')==1
        assert args.count('-isystem')==1 and args[args.index('-isystem')+1]==str(prefix/'include/c++/v1')
        if linking:
            for flag in ['-nostdlib++',*libraries,'-Wl,-rpath,'+str(prefix/'lib')]: assert args.count(flag)==1,flag
    else:
        assert not standards and not any(a.startswith(('-stdlib=','-nostdinc++','-nostdlib++','-freflection')) for a in args)
        assert not any(a in args for a in [str(prefix/'include/c++/v1'),*libraries])
    return args

def check_probe_logs(log_path, generated, prefix, sdk):
    document=yaml.safe_load(Path(log_path).read_text())
    events=[e for e in document['events'] if e['kind']=='try_compile-v1']
    assert len(events)==3 and len(generated)==3
    expected={'CMakeCCompilerABI.c':'CMAKE_C_ABI_COMPILED','CMakeCXXCompilerABI.cpp':'CMAKE_CXX_ABI_COMPILED','private_runtime.cpp':'_private_runtime_links'}
    verified={}
    for name,row in generated.items():
        event=next(e for e in events if e['directories']['binary']==row['directory'])
        result=event['buildResult']
        assert event['directories']['source']==row['directory'] and result['variable']==expected[name]
        assert result['exitCode']==0 and result['cached'] is False
        native_lines=[line.split('] ',1)[1] for line in result['stdout'].splitlines() if re.match(r'^\[[12]/2\] ',line)]
        lines=row['lines']
        assert len(lines)==len(native_lines)==2
        # CMake's YAML log additionally escapes each literal backslash in stdout.
        assert native_lines==[line.replace('\\','\\\\') for line in lines],name
        commands=[shlex.split(line) for line in lines]
        assert sum('-c' in a for a in commands)==1
        for args in commands:
            flags(args,prefix,sdk,name!='CMakeCCompilerABI.c',linking='-c' not in args,standard=name=='private_runtime.cpp' and '-c' in args)
        assert all('Debug' in line for line in lines)
        verified[name]={'directory':row['directory'],'configure_event_exit':0,'cached':False,'generated_and_executed_commands_equal_after_log_escaping':True,'commands':commands}
    return verified

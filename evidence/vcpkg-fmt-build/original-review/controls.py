from pathlib import Path
import ast,copy,hashlib,json,re,traceback
D=Path(__file__).parent
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
helper=R/'dev/toolchains/vcpkg_fmt.py';text=helper.read_text()
assert hashlib.sha256(text.encode()).hexdigest()=='9c15312ec81baf38fd858acf078a9604825527b09e10a1a23079229a059aa3da'
original=json.loads((R/'evidence/vcpkg-fmt-build/contract.json').read_text())
assert hashlib.sha256((R/'evidence/vcpkg-fmt-build/contract.json').read_bytes()).hexdigest()=='a0f5650383836e1087703200e135824f946620ef7c5fc0f7eb376a83a67c6212'
node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='inspect_cell')
rows=[];count=0;inventory_calls=[]
def digest(p):
    p=Path(p);assert p.is_relative_to(D)
    return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,content):
    p=Path(p);assert p.is_relative_to(D);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(content if isinstance(content,bytes) else content.encode())
    return p
cases=[('valid-p2996-dynamic','p2996','dynamic',None,True),('valid-gcc16-static','gcc16','static',None,True),('duplicate-detector-marker','p2996','static','detector',False),('wrong-port-compiler-version','gcc16','dynamic','compiler',False),('missing-debug-compiled-library','p2996','dynamic','library',False),('wrong-additional-abi-file','gcc16','static','abi',False)]
for index,(name,lane,linkage,mutation,expected) in enumerate(cases):
    base=D/('fixture-'+str(index));base.mkdir();cell=base/'cell';(cell/'installed').mkdir(parents=True)
    project=base/'project';triplet='arm64-osx-'+lane+'-'+linkage
    triplet_path=write(project/'triplets'/(triplet+'.cmake'),'# synthetic triplet identity\n')
    chainloader=write(project/'cmake/toolchains/vcpkg-macos-arm64.cmake','# synthetic chainloader identity\n')
    contract=copy.deepcopy(original)
    for key,identity in [('host',contract['host_compiler']),(lane,contract['compilers'][lane])]:
        for lang in ('C','CXX'):
            p=write(base/'compiler-bytes'/(key+'-'+lang),('private synthetic compiler '+key+' '+lang+'\n'))
            identity[lang]=str(p)
    env={'MARKETPLACE_CPP_LANE':lane,'MARKETPLACE_'+lane.upper()+'_PREFIX':contract['prefixes'][lane],'PKG_CONFIG':'/opt/homebrew/bin/pkg-config'}
    markers_by_triplet={};files=[triplet_path,chainloader]
    for selected,identity in [('arm64-osx',contract['host_compiler']),(triplet,contract['compilers'][lane])]:
        markers={}
        for lang in ('C','CXX'):
            markers[lang+'_PATH']=identity[lang];markers[lang+'_ID']=identity['id'];markers[lang+'_VERSION']=identity.get('version','17.0.0')
            markers[lang+'_HASH']=hashlib.sha1(Path(identity[lang]).read_bytes()).hexdigest();files.append(Path(identity[lang]))
        markers['HASH']=hashlib.sha1((markers['C_HASH']+markers['CXX_HASH']).encode()).hexdigest();markers_by_triplet[selected]=markers
        contents='-- synthetic detector output\n'+''.join('#COMPILER_'+k+'#'+v+'\n' for k,v in markers.items())
        if mutation=='detector' and selected==triplet:contents+='#COMPILER_CXX_ID#'+identity['id']+'\n'
        files.append(write(cell/'buildtrees/detect_compiler'/('stdout-'+selected+'.log'),contents))
    for short,configuration in [('dbg','Debug'),('rel','Release')]:
        build=cell/'buildtrees/fmt'/(triplet+'-'+short)
        cache='// synthetic CMake cache\n'+'\n'.join([f'CMAKE_BUILD_TYPE:STRING={configuration}','FMT_MODULE:BOOL=OFF','BUILD_SHARED_LIBS:BOOL='+('ON' if linkage=='dynamic' else 'OFF'),'CMAKE_MAKE_PROGRAM:FILEPATH='+contract['managed_tools']['ninja']['path']])+'\n'
        files.append(write(build/'CMakeCache.txt',cache))
        identity=contract['compilers'][lane]
        version='0.0.0' if mutation=='compiler' and short=='dbg' else identity['version']
        metadata='\n'.join(['set(CMAKE_CXX_COMPILER "'+identity['CXX']+'")','set(CMAKE_CXX_COMPILER_ARG1 "")','set(CMAKE_CXX_COMPILER_ID "'+identity['id']+'")','set(CMAKE_CXX_COMPILER_VERSION "'+version+'")','set(CMAKE_CXX_COMPILER_VERSION_INTERNAL "")'])+'\n'
        files.append(write(build/'CMakeFiles/4.4.4/CMakeCXXCompiler.cmake',metadata))
        library=cell/'installed'/triplet/('debug/lib' if short=='dbg' else 'lib')
        library/=('libfmtd' if short=='dbg' else 'libfmt')+('.12.2.0.dylib' if linkage=='dynamic' else '.a')
        if not (mutation=='library' and short=='dbg'):files.append(write(library,b'SYNTHETIC NONEXECUTABLE LIBRARY WITNESS\n'))
    abi={('additional_file_'+str(i)):row['sha256'] for i,row in enumerate(contract['abi_inputs'][triplet])}
    abi.update({'ENV:'+k:hashlib.sha256(v.encode()).hexdigest() for k,v in env.items()})
    abi['triplet_abi']='-'.join([digest(triplet_path),digest(chainloader),markers_by_triplet[triplet]['HASH']])
    if mutation=='abi':abi['additional_file_0']='0'*64
    files.append(write(cell/'buildtrees/fmt'/(triplet+'.vcpkg_abi_info.txt'),''.join(k+' '+v+'\n' for k,v in abi.items())))
    before={str(p):digest(p) for p in files}
    def private_inventory(path):
        assert path==cell/'installed' and path.is_dir() and path.is_relative_to(D)
        inventory_calls.append(str(path));return []
    scope={'Path':Path,'ROOT':project,'re':re,'hashlib':hashlib,'digest':digest,'prefix_inventory':private_inventory}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(helper),'exec'),scope)
    error=None;result=None;accepted=False;count+=1
    try:
        result=scope['inspect_cell'](cell,triplet,contract,env)
        accepted=True
    except (AssertionError,FileNotFoundError,KeyError) as exc:
        error={'type':type(exc).__name__,'helper_line':traceback.extract_tb(exc.__traceback__)[-1].lineno}
    assert accepted==expected,(name,error)
    assert before=={str(p):digest(p) for p in files}
    if accepted:
        assert set(result['configurations'])=={'Debug','Release'} and len(result['libraries'])==2
        assert set(result['detectors'])=={'arm64-osx',triplet}
    rows.append({'case':name,'expected_acceptance':expected,'observed_acceptance':accepted,'error':error,'private_fixture_unchanged':True})
assert count==len(inventory_calls)==6
report={'result':'PASS six new bounded inspect_cell AST controls','helper_sha256':hashlib.sha256(text.encode()).hexdigest(),'contract_sha256':hashlib.sha256((R/'evidence/vcpkg-fmt-build/contract.json').read_bytes()).hexdigest(),'calls':count,'cases':rows,'method':'Only inspect_cell compiled from AST; injected fixture-only digest and inventory stub. Synthetic compiler/library bytes are non-executable; no real prefix inventory or candidate imports.','native_commands':0,'historical_controls_replayed':0,'shared_writes':0,'fixtures_excluded_from_support_manifest':True}
(D/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'result':report['result'],'calls':count,'native_commands':0}))

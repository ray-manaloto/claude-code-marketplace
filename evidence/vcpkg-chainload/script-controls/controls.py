from pathlib import Path
import hashlib,json,os,subprocess
ROOT=Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
OUT=Path(__file__).parent
CMAKE=Path("/Users/rmanaloto/.local/share/mise/installs/cmake/4.4.4/cmake-4.4.4-macos-universal/CMake.app/Contents/bin/cmake")
assert hashlib.sha256(CMAKE.read_bytes()).hexdigest()=="80cbc0d5ee08c9e6166bcc44bf51faf5469e360346f5cefbf36e8f8e4351a4cb"
ADAPTER=ROOT/"cmake/toolchains/vcpkg-macos-arm64.cmake"
PREFIX={"p2996":"/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-configure-20261011T051205Z/prefix","gcc16":"/opt/homebrew/Cellar/gcc/16.2.0"}
results=[]
for lane,prefix in PREFIX.items():
    env={"PATH":"/usr/bin:/bin:/usr/sbin:/sbin","HOME":str(Path.home()),"TMPDIR":str(OUT),"MARKETPLACE_CPP_LANE":lane,"MARKETPLACE_"+lane.upper()+"_PREFIX":prefix}
    setup='cmake_minimum_required(VERSION 4.4)\ncmake_host_system_information(RESULT CMAKE_HOST_SYSTEM_PROCESSOR QUERY OS_PLATFORM)\nset(VCPKG_TARGET_TRIPLET arm64-osx-'+lane+'-static)\nset(VCPKG_TARGET_ARCHITECTURE arm64)\n'
    include='include("'+str(ADAPTER)+'")\n'
    witness='foreach(lang C CXX)\n  set(before_${lang} "${CMAKE_${lang}_FLAGS_INIT}")\n  set(CMAKE_${lang}_FLAGS "${CMAKE_${lang}_FLAGS_INIT}")\nendforeach()\n'
    witness+=include+'foreach(lang C CXX)\n  if(NOT CMAKE_${lang}_FLAGS_INIT STREQUAL before_${lang})\n    message(FATAL_ERROR "Reentry changed flags")\n  endif()\n  string(REGEX MATCHALL "-fPIC" pics "${CMAKE_${lang}_FLAGS_INIT}")\n  list(LENGTH pics pic_count)\n  if(NOT pic_count EQUAL 1)\n    message(FATAL_ERROR "Expected one PIC token")\n  endif()\nendforeach()\nforeach(name CMAKE_C_COMPILER CMAKE_CXX_COMPILER CMAKE_C_FLAGS_INIT CMAKE_CXX_FLAGS_INIT CMAKE_CXX_LINK_FLAGS CMAKE_OSX_SYSROOT CMAKE_OSX_DEPLOYMENT_TARGET CMAKE_OSX_ARCHITECTURES CMAKE_C_FLAGS_DEBUG_INIT CMAKE_CXX_FLAGS_DEBUG_INIT CMAKE_C_FLAGS_RELEASE_INIT CMAKE_CXX_FLAGS_RELEASE_INIT CMAKE_EXE_LINKER_FLAGS_INIT CMAKE_EXE_LINKER_FLAGS_DEBUG_INIT CMAKE_EXE_LINKER_FLAGS_RELEASE_INIT CMAKE_TRY_COMPILE_PLATFORM_VARIABLES)\n  message(STATUS "${name}=${${name}}")\nendforeach()\ncmake_policy(GET CMP0210 result_policy)\nmessage(STATUS "CMP0210=${result_policy}")\n'
    cases=[("reentry",{},"",witness,0,"CMP0210=NEW")]
    flags='set(VCPKG_C_FLAGS "-DMARKETPLACE_C=1")\nset(VCPKG_CXX_FLAGS "-DMARKETPLACE_CXX=1")\n'
    for suffix in ("DEBUG","RELEASE"):
        for lang in ("C","CXX"):flags+=f'set(VCPKG_{lang}_FLAGS_{suffix} "-DMARKETPLACE_{lang}_{suffix}=1")\n'
    for suffix in ("","_DEBUG","_RELEASE"):flags+=f'set(VCPKG_LINKER_FLAGS{suffix} "-Wl,-no_warn_duplicate_libraries")\n'
    cases.append(("paired-flags-reentry",{},flags,witness,0,"MARKETPLACE_CXX_RELEASE=1"))
    for name,change in [("missing-lane",{"MARKETPLACE_CPP_LANE":None}),("empty-lane",{"MARKETPLACE_CPP_LANE":""}),("wrong-lane",{"MARKETPLACE_CPP_LANE":"other"}),("missing-prefix",{"MARKETPLACE_"+lane.upper()+"_PREFIX":None}),("empty-prefix",{"MARKETPLACE_"+lane.upper()+"_PREFIX":""}),("wrong-prefix",{"MARKETPLACE_"+lane.upper()+"_PREFIX":"/tmp/other"}),("other-prefix",{"MARKETPLACE_"+("GCC16" if lane=="p2996" else "P2996")+"_PREFIX":"/tmp/other"}),("wrong-cc",{"CC":"/usr/bin/cc"}),("wrong-cxx",{"CXX":"/usr/bin/c++"}),("polluted-cxxflags",{"CXXFLAGS":"-DUNEXPECTED=1"})]:
        cases.append((name,change,"","",1,"CMake Error"))
    for name,code in [("old-policy","cmake_policy(SET CMP0210 OLD)"),("old-default","set(CMAKE_POLICY_DEFAULT_CMP0210 OLD)"),("wrong-triplet","set(VCPKG_TARGET_TRIPLET arm64-osx-other-static)"),("wrong-sdk","set(CMAKE_OSX_SYSROOT /tmp/wrong)"),("wrong-deployment","set(CMAKE_OSX_DEPLOYMENT_TARGET 26.0)"),("wrong-arch","set(CMAKE_OSX_ARCHITECTURES x86_64)"),("wrong-processor","set(CMAKE_SYSTEM_PROCESSOR x86_64)"),("wrong-vcpkg-arch","set(VCPKG_TARGET_ARCHITECTURE x64)"),("forced-c","set(CMAKE_C_COMPILER_FORCED TRUE)"),("forced-cxx","set(CMAKE_CXX_COMPILER_FORCED TRUE)"),("no-platform-vars","set(CMAKE_TRY_COMPILE_NO_PLATFORM_VARIABLES TRUE)"),("static-try-compile","set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)"),("no-compiler-tracking","set(VCPKG_DISABLE_COMPILER_TRACKING TRUE)"),("wrong-c-compiler","set(CMAKE_C_COMPILER /usr/bin/cc)"),("wrong-cxx-compiler","set(CMAKE_CXX_COMPILER /usr/bin/c++)"),("wrong-c-flags","set(CMAKE_C_FLAGS -DBAD=1)"),("wrong-cxx-flags","set(CMAKE_CXX_FLAGS -DBAD=1)")]:
        cases.append((name,{},code+"\n","",1,"CMake Error"))
    for suffix in ("","_DEBUG","_RELEASE"):
        for lang in ("C","CXX"):cases.append(("unpaired-"+lang+suffix,{},f'set(VCPKG_{lang}_FLAGS{suffix} -DUNPAIRED=1)\n',"",1,"Set both VCPKG"))
    if lane=="p2996":cases.append(("precomposed-osx",{},'include("/Users/rmanaloto/.local/state/marketplace-tool-foundation/vcpkg-source-e4563094/source/scripts/toolchains/osx.cmake")\n',"",1,"Compose vcpkg"))
    for name,change,before,after,expected,marker in cases:
        case=lane+"-"+name;p=OUT/(case+".cmake");p.write_text(setup+before+include+after)
        selected=dict(env)
        for key,value in change.items():
            if value is None:selected.pop(key,None)
            else:selected[key]=value
        argv=[str(CMAKE),"-P",str(p)];run=subprocess.run(argv,cwd=OUT,env=selected,capture_output=True,text=True,timeout=20)
        (OUT/(case+".stdout")).write_text(run.stdout);(OUT/(case+".stderr")).write_text(run.stderr)
        ok=run.returncode==expected and marker in run.stdout+run.stderr
        results.append({"case":case,"argv":argv,"returncode":run.returncode,"expected":expected,"marker":marker,"passed":ok})
        (OUT/"controls.json").write_text(json.dumps({"results":results,"compiler_commands":0,"mode":"CMake -P only"},indent=2)+"\n")
        assert ok,case+":"+run.stdout+run.stderr
print(json.dumps({"result":"PASS","cases":len(results),"compiler_commands":0}))

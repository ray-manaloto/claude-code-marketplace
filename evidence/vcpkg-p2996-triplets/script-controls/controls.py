from pathlib import Path
import hashlib,json,subprocess
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
OUT=Path(__file__).parent
CMAKE=Path('/Users/rmanaloto/.local/share/mise/installs/cmake/4.4.4/cmake-4.4.4-macos-universal/CMake.app/Contents/bin/cmake')
assert hashlib.sha256(CMAKE.read_bytes()).hexdigest()=='80cbc0d5ee08c9e6166bcc44bf51faf5469e360346f5cefbf36e8f8e4351a4cb'
prefix='/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-configure-20261011T051205Z/prefix'
env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','TMPDIR':str(OUT),'MARKETPLACE_CPP_LANE':'p2996','MARKETPLACE_P2996_PREFIX':prefix}
setup='cmake_minimum_required(VERSION 4.4)\ncmake_host_system_information(RESULT CMAKE_HOST_SYSTEM_PROCESSOR QUERY OS_PLATFORM)\n'
common=ROOT/'triplets/common/macos-arm64.cmake'
rows=[]
def execute(name,body,changes=None,expected=0,marker='TRIPLET_PASS'):
 selected=dict(env)
 for k,v in (changes or {}).items():
  if v is None:selected.pop(k,None)
  else:selected[k]=v
 f=OUT/(name+'.cmake');f.write_text(setup+body.replace('@D@','$'));a=[str(CMAKE),'-P',str(f)]
 p=subprocess.run(a,cwd=OUT,env=selected,capture_output=True,text=True,timeout=20)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 ok=p.returncode==expected and marker in p.stdout+p.stderr
 rows.append({'case':name,'argv':a,'returncode':p.returncode,'expected':expected,'marker':marker,'passed':ok})
 (OUT/'controls.json').write_text(json.dumps({'results':rows,'compiler_commands':0,'mode':'CMake -P only'},indent=2)+'\n')
 assert ok,name+': '+p.stdout+p.stderr
for linkage in ['static','dynamic']:
 triplet=ROOT/f'triplets/arm64-osx-p2996-{linkage}.cmake'
 inclusion=f'include("{triplet}")\n'
 checks=r"""
if(NOT VCPKG_TARGET_ARCHITECTURE STREQUAL "arm64" OR
   NOT VCPKG_LIBRARY_LINKAGE STREQUAL "@LINKAGE@" OR
   NOT VCPKG_CRT_LINKAGE STREQUAL "dynamic" OR
   NOT VCPKG_CMAKE_SYSTEM_NAME STREQUAL "Darwin" OR DEFINED VCPKG_BUILD_TYPE OR
   NOT VCPKG_OSX_DEPLOYMENT_TARGET STREQUAL "27.0" OR
   NOT VCPKG_OSX_SYSROOT STREQUAL "/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk" OR
   NOT VCPKG_CMAKE_CONFIGURE_OPTIONS STREQUAL "-DCMAKE_POLICY_DEFAULT_CMP0210=NEW" OR
   NOT VCPKG_ENV_PASSTHROUGH STREQUAL "MARKETPLACE_CPP_LANE;MARKETPLACE_P2996_PREFIX")
 message(FATAL_ERROR "Triplet contract mismatch")
endif()
list(LENGTH VCPKG_HASH_ADDITIONAL_FILES count)
if(NOT count EQUAL 13 OR NOT "@COMMON@" IN_LIST VCPKG_HASH_ADDITIONAL_FILES)
 message(FATAL_ERROR "Missing nested ABI inputs")
endif()
foreach(input IN LISTS VCPKG_HASH_ADDITIONAL_FILES)
 file(SHA256 "@D@{input}" digest)
 message(STATUS "ABI=@D@{input}|@D@{digest}")
endforeach()
set(before "@D@{VCPKG_HASH_ADDITIONAL_FILES}")
include("@TRIPLET@")
if(NOT before STREQUAL VCPKG_HASH_ADDITIONAL_FILES)
 message(FATAL_ERROR "Reentry changed ABI inputs")
endif()
message(STATUS "TRIPLET_PASS")
""".replace('@LINKAGE@',linkage).replace('@COMMON@',str(common)).replace('@TRIPLET@',str(triplet))
 execute(linkage+'-contract',inclusion+checks)
 body='macro(vcpkg_triplet_file VCPKG_TRIPLET_ID)\nset(_backup "@D@{CMAKE_CURRENT_LIST_FILE}")\n'+f'set(CMAKE_CURRENT_LIST_FILE "{triplet}")\n'+'get_filename_component(CMAKE_CURRENT_LIST_DIR "@D@{CMAKE_CURRENT_LIST_FILE}" DIRECTORY)\n'+triplet.read_text()+'set(CMAKE_CURRENT_LIST_FILE "@D@{_backup}")\nget_filename_component(CMAKE_CURRENT_LIST_DIR "@D@{CMAKE_CURRENT_LIST_FILE}" DIRECTORY)\nendmacro()\nvcpkg_triplet_file(0)\n'+checks
 execute(linkage+'-extracted-triplet',body)
static=ROOT/'triplets/arm64-osx-p2996-static.cmake';include=f'include("{static}")\n'
for name,change in [('missing-lane',{'MARKETPLACE_CPP_LANE':None}),('empty-lane',{'MARKETPLACE_CPP_LANE':''}),('wrong-lane',{'MARKETPLACE_CPP_LANE':'gcc16'}),('missing-prefix',{'MARKETPLACE_P2996_PREFIX':None}),('empty-prefix',{'MARKETPLACE_P2996_PREFIX':''}),('wrong-prefix',{'MARKETPLACE_P2996_PREFIX':'/tmp/wrong'}),('other-prefix',{'MARKETPLACE_GCC16_PREFIX':'/opt/homebrew/Cellar/gcc/16.2.0'})]:
 execute(name,include,change,1,'triplet lane and qualified environment must agree')
for name,before,marker in [('release-only','set(VCPKG_BUILD_TYPE release)','both build types'),('tracking-off','set(VCPKG_DISABLE_COMPILER_TRACKING TRUE)','compiler tracking'),('wrong-host','set(CMAKE_HOST_SYSTEM_PROCESSOR x86_64)','native macOS ARM64')]:
 execute(name,before+'\n'+include,expected=1,marker=marker)
execute('bad-linkage',f'set(_marketplace_triplet_lane p2996)\nset(VCPKG_LIBRARY_LINKAGE bad)\ninclude("{common}")\n',expected=1,marker='Select static/dynamic linkage')
execute('bad-common-lane',f'set(_marketplace_triplet_lane bad)\ninclude("{common}")\n',expected=1,marker='triplet must select a qualified compiler lane')
execute('adapter-composition','set(VCPKG_TARGET_TRIPLET arm64-osx-p2996-static)\n'+include+'include("@D@{VCPKG_CHAINLOAD_TOOLCHAIN_FILE}")\nif(NOT CMAKE_CXX_COMPILER STREQUAL "'+prefix+'/bin/clang++" OR NOT CMAKE_CXX_LINK_FLAGS MATCHES "libc[+][+][.]dylib")\nmessage(FATAL_ERROR "Compiler/runtime mismatch")\nendif()\nmessage(STATUS "TRIPLET_PASS")\n')
print(json.dumps({'status':'PASS','cases':len(rows),'compiler_commands':0}))

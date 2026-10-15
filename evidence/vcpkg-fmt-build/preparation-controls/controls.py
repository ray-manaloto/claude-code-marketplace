from pathlib import Path
import ast,hashlib,json,os,shutil
root=Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
private=Path(__file__).parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=root/"dev/toolchains/vcpkg_fmt.py"
contract=json.loads((root/"evidence/vcpkg-fmt-build/contract.json").read_text())
scope={"Path":Path,"os":os,"ROOT":root}
for file,names in [(root/"dev/toolchains/vcpkg_private.py",["private_environment","vcpkg_arguments"]),(source,["build_environment","install_arguments"])]:
 tree=ast.parse(file.read_text())
 for name in names:
  node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
  exec(compile(ast.Module(body=[node],type_ignores=[]),str(file),"exec"),scope)
rows=[]
for lane in ("p2996","gcc16"):
 env=scope["build_environment"](private,contract,lane)
 assert env["HOME"]==str(Path.home())
 for name in ["CC","CXX","CFLAGS","CXXFLAGS","CPPFLAGS","LDFLAGS","CPATH","C_INCLUDE_PATH","CPLUS_INCLUDE_PATH","LIBRARY_PATH","COMPILER_PATH","SDKROOT","DYLD_LIBRARY_PATH","DYLD_INSERT_LIBRARIES","VCPKG_FORCE_DOWNLOADED_BINARIES","VCPKG_BINARY_SOURCES","VCPKG_DEFAULT_BINARY_CACHE"]: assert name not in env,name
 assert env["PKG_CONFIG"]=="/opt/homebrew/bin/pkg-config"
 assert env["VCPKG_MAX_CONCURRENCY"]==env["CMAKE_BUILD_PARALLEL_LEVEL"]=="1" and env["MAKEFLAGS"]=="-j1"
 selected={n:shutil.which(n,path=env["PATH"]) for n in ["cmake","ninja","clang","clang++","cc","c++"]}
 for tool in ("cmake","ninja"): assert selected[tool]==contract["managed_tools"][tool]["path"]
 for tool in ("clang","clang++","cc","c++"): assert selected[tool]=="/usr/bin/"+tool
 assert not any(Path(p).is_relative_to(contract["prefixes"][lane]) for p in env["PATH"].split(os.pathsep))
 for linkage in ("static","dynamic"):
  triplet="arm64-osx-"+lane+"-"+linkage;cell=private/triplet;argv=scope["install_arguments"](private,cell,triplet)
  assert len(argv)==len(set(argv))
  assert "install" in argv and "--triplet="+triplet in argv and "--host-triplet=arm64-osx" in argv
  assert "--feature-flags=-binarycaching,compilertracking" in argv and "--no-downloads" in argv
  assert not any(a.startswith(("--cmake-args","--editable","--head","--dry-run","--clean")) for a in argv)
  for flag,path in [("--x-install-root=",cell/"installed"),("--x-buildtrees-root=",cell/"buildtrees"),("--x-packages-root=",cell/"packages"),("--x-manifest-root=",private/"manifest"),("--x-registries-cache=",private/"registries")]:assert [a for a in argv if a.startswith(flag)]==[flag+str(path)]
  rows.append({"triplet":triplet,"environment":env,"argv":argv,"which":selected,"result":"PASS source-derived arguments and filesystem selection"})
try:scope["build_environment"](private,contract,"unknown")
except AssertionError:rows.append({"case":"unknown lane rejected","result":"PASS"})
else:raise AssertionError("unknown lane accepted")
(private/"controls.json").write_text(json.dumps({"state":"PASS","helper_sha256":h(source),"contract_sha256":h(root/"evidence/vcpkg-fmt-build/contract.json"),"cases":rows,"native_tools_executed":0},indent=2)+"\n")
print(json.dumps({"state":"PASS","cases":len(rows),"native_tools_executed":0}))

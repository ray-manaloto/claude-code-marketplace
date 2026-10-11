"""Qualify the installed GCC16 lane in a new --run-dir; no installation or global edits."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess

from gcc_install import ROOT, digest, package_state, preserved, read


def main(directory):
    os.umask(0o077)
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    report = {"state": "running", "commands": [], "script_sha256": digest(Path(__file__)),
              "source_sha256": digest(Path(__file__).with_name("reflection.cpp"))}
    before = read("install-preimages.json")
    context_path = Path(before["normal_environment"]["argv"][-1]).parent / "context.json"
    context = json.loads(context_path.read_text())
    environment = context["environment"] | {"MISE_OFFLINE": "1"}

    def save():
        (directory / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")

    def run(label, argv, expected=0):
        row = {"case": label, "argv": argv, "started_at": datetime.now(timezone.utc).isoformat()}
        report["commands"].append(row)
        save()
        paths = [directory / (label + suffix) for suffix in (".stdout", ".stderr")]
        with paths[0].open("wb") as out, paths[1].open("wb") as err:
            process = subprocess.Popen(argv, cwd=directory, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=out, stderr=err, start_new_session=True)
            try:
                process.wait(timeout=60)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                row["interrupted"] = True
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(process.pid, sig)
                    except ProcessLookupError:
                        pass
                    if sig == signal.SIGTERM:
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            pass
                process.wait()
                raise
            finally:
                row.update({"returncode": process.returncode,
                            "logs": [{"path": str(p), "sha256": digest(p)} for p in paths]})
                save()
        print(json.dumps({"case": label, "returncode": process.returncode}), flush=True)
        assert process.returncode == expected, label
        return paths[0].read_text(), paths[1].read_text()

    try:
        preserved(before, installed=True)
        installed = read("installation.json")
        assert installed["state"] == "PASS: installed"
        for name, state in installed["installed_packages"].items():
            assert package_state(name) == state, name
        review = read("postinstall-review.json")
        assert review["result"] == "PASS for task 05c installed state" and not review["findings_remaining"]
        mise = read("install-proposal.json")["native_mise"]
        assert digest(Path(mise["path"])) == mise["sha256"]
        census = subprocess.run(["/bin/ps", "-axo", "pid=,ppid=,comm="], text=True,
                                capture_output=True, check=True, timeout=15)
        active = [line.strip() for line in census.stdout.splitlines() if re.fullmatch(
            r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|sccache",
            Path(line.strip().split(None, 2)[-1]).name)]
        assert not active, active
        report["admission"] = {"owner": "/root", "scope": "Sequential tiny compiler probes only; 60 seconds each",
                               "at": datetime.now(timezone.utc).isoformat(), "census_returncode": census.returncode,
                               "load_average": os.getloadavg(), "cpu_count": os.cpu_count(), "active_builds": active}
        default, _ = run("default-before", before["normal_environment"]["argv"])
        assert json.loads(default) == before["normal_environment"]["output"]
        prefix = Path("/opt/homebrew/Cellar/gcc/16.2.0")
        environment["MARKETPLACE_GCC16_PREFIX"] = str(prefix)
        (directory / "cwd").mkdir()
        base = [mise["path"], "--no-hooks", "-C", str(directory / "cwd"), "-E", "gcc16",
                "exec", "--fresh-env", "--no-deps", "--"]
        profile, _ = run("named-profile", base + before["normal_environment"]["argv"][-2:])
        selected = json.loads(profile)["selected"]
        assert selected["CC"] == str(prefix / "bin/gcc-16")
        assert selected["CXX"] == str(prefix / "bin/g++-16") and selected["MARKETPLACE_CPP_LANE"] == "gcc16"
        for name in ("CPPFLAGS", "LDFLAGS", "CPATH", "LIBRARY_PATH", "SDKROOT", "CXXFLAGS", "COMPILER_PATH"):
            assert selected[name] is None, name
        report["selected_environment"] = json.loads(profile)
        cc, cxx = selected["CC"], selected["CXX"]
        for name, compiler in (("c", cc), ("cxx", cxx)):
            version, _ = run(name + "-version", base + [compiler, "-dumpfullversion"])
            assert version.strip() == "16.2.0"
        run("compiler-configuration", base + [cxx, "-v"])
        sdk, _ = run("sdk-path", ["/usr/bin/xcrun", "--sdk", "macosx", "--show-sdk-path"])
        sdk = Path(sdk.strip()).resolve()
        run("sdk-version", ["/usr/bin/xcrun", "--sdk", "macosx", "--show-sdk-version"])
        report["sdk"] = {"path": str(sdk), "settings_sha256": digest(sdk / "SDKSettings.json")}
        identities = {"cc": Path(cc), "cxx": Path(cxx), "meta": prefix / "include/c++/16/meta"}
        for key, flag in (("cc1plus", "-print-prog-name=cc1plus"),
                          ("libstdc++", "-print-file-name=libstdc++.6.dylib"),
                          ("libgcc", "-print-file-name=libgcc_s.1.1.dylib")):
            result, _ = run(key.replace("+", "p") + "-path", base + [cxx, flag])
            path = Path(result.strip()).resolve()
            assert path.is_relative_to(prefix) and path.is_file(), path
            identities[key] = path
        report["identities"] = {key: {"path": str(p), "resolved": str(p.resolve()), "sha256": digest(p)}
                                for key, p in identities.items()}
        for key in ("cxx", "cc1plus", "libstdc++", "libgcc"):
            architecture, _ = run(key.replace("+", "p") + "-architecture", ["/usr/bin/file", "-b", str(identities[key])])
            assert "arm64" in architecture
            run(key.replace("+", "p") + "-libraries", ["/usr/bin/otool", "-L", str(identities[key])])
        flags = ["-std=c++26", "-freflection", "-isysroot", str(sdk)]
        empty = directory / "empty.cpp"
        empty.write_text("#include <version>\n")
        macros, _ = run("feature-macros", base + [cxx, *flags, "-dM", "-E", str(empty)])
        report["feature_macros"] = dict(re.findall(
            r"^#define (__cplusplus|__cpp_impl_reflection|__cpp_lib_reflection|_GLIBCXX_RELEASE|__GLIBCXX__) (.+)$", macros, re.M))
        assert report["feature_macros"]["_GLIBCXX_RELEASE"] == "16"
        assert int(report["feature_macros"]["__cpp_impl_reflection"].rstrip("L")) >= 202603
        assert int(report["feature_macros"]["__cpp_lib_reflection"].rstrip("L")) >= 202603
        source = Path(__file__).with_name("reflection.cpp").resolve()
        dependencies, _ = run("header-dependencies", base + [cxx, *flags, "-M", str(source)])
        assert "/include/c++/16/meta" in dependencies
        binary = directory / "reflection"
        run("reflection-build", base + [cxx, *flags, "-pedantic-errors", "-Wall", "-Wextra", "-Werror",
                                        "-O0", "-g", "-v", str(source), "-o", str(binary)])
        output, dynamic = run("reflection-run", base + ["/usr/bin/env", "DYLD_PRINT_LIBRARIES=1", str(binary)])
        assert output == "reflection value=43\n"
        assert any("libstdc++.6.dylib" in line and str(prefix) in line for line in dynamic.splitlines()), dynamic
        libraries, _ = run("witness-libraries", ["/usr/bin/otool", "-L", str(binary)])
        direct = [line.split(" (")[0].strip() for line in libraries.splitlines()[1:]]
        assert not any("libc++" in path for path in direct), direct
        assert any(Path(p).resolve() == identities["libstdc++"] for p in direct)
        bindings, _ = run("witness-symbols", ["/usr/bin/nm", "-m", "-u", str(binary)])
        std_symbols = [line for line in bindings.splitlines() if "__ZSt" in line or "__ZNSt" in line]
        assert std_symbols and all("(from libstdc++)" in line for line in std_symbols)
        report["system_cxx_images"] = [line for line in dynamic.splitlines() if "/usr/lib/libc++" in line]
        assert not any("libc++" in line and "/usr/lib/libc++" not in line for line in dynamic.splitlines())
        negative = directory / "without-reflection"
        _, diagnostic = run("without-reflection", base + [cxx, "-std=c++26", "-isysroot", str(sdk),
                             "-fmax-errors=2", str(source), "-o", str(negative)], expected=1)
        assert not negative.exists() and "Reflection must be enabled" in diagnostic
        report["witness"] = {"path": str(binary), "sha256": digest(binary), "output": output}
        environment.pop("MARKETPLACE_GCC16_PREFIX")
        after, _ = run("default-after", before["normal_environment"]["argv"])
        assert json.loads(after) == json.loads(default)
        report["state"] = "PASS: GCC16 reflection compile/link/run"
    except BaseException as error:
        report.update({"state": "FAIL", "error": repr(error)})
        raise
    finally:
        try:
            preserved(before, installed=True)
            report["protected_state_unchanged"] = True
        except Exception as error:
            report.update({"state": "FAIL", "preservation_error": repr(error)})
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    main(parser.parse_args().run_dir)

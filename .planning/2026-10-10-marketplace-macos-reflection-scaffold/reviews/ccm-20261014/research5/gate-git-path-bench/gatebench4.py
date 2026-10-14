import json, os, statistics, subprocess, sys, time
py, wt, before, outp, cwd = sys.argv[1:6]
payloads = {
    "pretooluse_gate.py": {"hook_event_name": "PreToolUse", "tool_name": "Bash", "session_id": "s", "cwd": cwd,
                           "tool_input": {"command": "git push origin HEAD"}},
    "stop_gate.py": {"hook_event_name": "Stop", "session_id": "s", "cwd": cwd},
    "subagent_stop_gate.py": {"hook_event_name": "SubagentStop", "session_id": "s", "cwd": cwd,
                              "agent_transcript_path": "/dev/null"},
}
env = dict(os.environ)
env.pop("VIRTUAL_ENV", None)
out = {"python": py, "cwd": cwd, "path_git_first": next((os.path.join(p, "git") for p in env["PATH"].split(":")
                                                        if os.access(os.path.join(p, "git"), os.X_OK)), None)}
for gate, event in payloads.items():
    inp = json.dumps(event).encode()
    for label, root in (("before c33ba4e", before), ("after", wt)):
        ts = []
        for i in range(33):
            t = time.perf_counter_ns()
            r = subprocess.run([py, "-I", f"{root}/dev/hooks/{gate}"], input=inp, capture_output=True, env=env, cwd=cwd)
            ts.append((time.perf_counter_ns() - t) / 1e6)
        ts = ts[3:]
        out[f"{gate} {label}"] = {"n": len(ts), "median_ms": round(statistics.median(ts), 1),
                                  "p90_ms": round(sorted(ts)[int(len(ts) * .9)], 1), "rc": r.returncode,
                                  "stdout_sha256_prefix": __import__("hashlib").sha256(r.stdout).hexdigest()[:12]}
        print(f"{gate:24} {label:15} median {out[f'{gate} {label}']['median_ms']:7.1f} ms  p90 "
              f"{out[f'{gate} {label}']['p90_ms']:7.1f}  rc {r.returncode} out {len(r.stdout)}B "
              f"{out[f'{gate} {label}']['stdout_sha256_prefix']}")
json.dump(out, open(outp, "w"), indent=1)
print(out["path_git_first"])

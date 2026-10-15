#!/usr/bin/env python3
"""Offline Context7 4.3.0 bridge probe against a loopback API fixture."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import statistics
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from time import monotonic_ns
from urllib.parse import parse_qs, urlsplit


class Fixture(BaseHTTPRequestHandler):
    requests = []
    force_search_quota = False

    def do_GET(self):
        Fixture.requests.append(self.path)
        if self.path.startswith("/api/v2/libs/search"):
            quota = Fixture.force_search_quota or parse_qs(urlsplit(self.path).query).get("query") == ["quota fixture"]
            body = ({"message": "fixture quota exceeded"} if quota else
                    {"results": [{"id": "/fixture/docs", "title": "Fixture", "description": "offline"}]})
            code = 429 if quota else 200
        elif self.path.startswith("/api/v2/context"):
            body = {"message": "fixture quota exceeded"}
            code = 429
        else:
            body = {"message": "unexpected fixture path"}
            code = 404
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *_args):
        pass


def read_reply(proc, request_id, timeout=8):
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    deadline = monotonic_ns() + timeout * 1_000_000_000
    try:
        while monotonic_ns() < deadline:
            events = selector.select(max(0, (deadline - monotonic_ns()) / 1_000_000_000))
            if not events:
                break
            line = proc.stdout.readline()
            if not line:
                break
            message = json.loads(line)
            if message.get("id") == request_id:
                return message
    finally:
        selector.close()
    raise RuntimeError(f"no MCP reply for request {request_id}; child rc={proc.poll()}")


def send(proc, message):
    proc.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
    proc.stdin.flush()


def mcp_call(node, entry, env, name, arguments):
    start = monotonic_ns()
    proc = subprocess.Popen([node, str(entry)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, env=env)
    try:
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                               "clientInfo": {"name": "offline-bridge-probe", "version": "1"}}})
        init = read_reply(proc, 1)
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                    "params": {"name": name, "arguments": arguments}})
        answer = read_reply(proc, 2)
        elapsed = (monotonic_ns() - start) / 1_000_000
        return {"elapsed_ms": round(elapsed, 3), "server_version": init["result"]["serverInfo"]["version"],
                "content": answer.get("result", {}).get("content"),
                "is_error_present": "isError" in answer.get("result", {}),
                "is_error": answer.get("result", {}).get("isError", False),
                "protocol_error": answer.get("error")}
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)


def direct_call(node, api, env, function, args):
    script = ("const m=await import(process.argv[1]);"
              "const r=await m[process.argv[2]](...JSON.parse(process.argv[3]));"
              "console.log(JSON.stringify(r));")
    start = monotonic_ns()
    completed = subprocess.run([node, "--input-type=module", "-e", script, str(api), function,
                                json.dumps(args)], env=env, text=True, capture_output=True, timeout=8)
    elapsed = (monotonic_ns() - start) / 1_000_000
    return {"elapsed_ms": round(elapsed, 3), "exit_code": completed.returncode,
            "result": json.loads(completed.stdout) if completed.returncode == 0 else None}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def mcp_result_class(name, reply):
    """Fail closed on this pinned server's resolve response shape."""
    if reply["protocol_error"] or reply["is_error"]:
        return "error"
    content = reply["content"]
    if not isinstance(content, list) or len(content) != 1 or content[0].get("type") != "text":
        return "non_success"
    if name == "resolve-library-id":
        return "success" if content[0]["text"].startswith("Available Libraries:\n\n") else "non_success"
    return "success"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--node", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fault-search", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    package = json.loads((args.package_dir / "package.json").read_text())
    if (package.get("name"), package.get("version")) != ("@upstash/context7-mcp", "4.3.0"):
        parser.error("expected installed @upstash/context7-mcp 4.3.0")
    entry = args.package_dir / package["bin"]["context7-mcp"]
    api = args.package_dir / "dist/lib/api.js"
    Fixture.requests = []
    Fixture.force_search_quota = args.fault_search
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "HOME": os.environ.get("HOME", ""), "TMPDIR": tempfile.gettempdir(),
           "OTEL_SDK_DISABLED": "true",
           "CONTEXT7_API_URL": f"http://127.0.0.1:{server.server_port}/api"}
    search_args = {"query": "offline fixture", "libraryName": "Fixture"}
    context_args = {"query": "quota fixture", "libraryId": "/fixture/docs"}
    try:
        runs = {"direct_search": [], "mcp_search": [], "direct_quota": [], "mcp_quota": [],
                "direct_resolve_quota": [], "mcp_resolve_quota": []}
        for _ in range(3):
            runs["direct_search"].append(direct_call(str(args.node), api, env, "searchLibraries",
                                                     [search_args["query"], search_args["libraryName"]]))
            runs["mcp_search"].append(mcp_call(str(args.node), entry, env, "resolve-library-id", search_args))
        runs["direct_quota"].append(direct_call(str(args.node), api, env, "fetchLibraryContext",
                                                 [context_args]))
        runs["mcp_quota"].append(mcp_call(str(args.node), entry, env, "query-docs", context_args))
        resolve_quota_args = {"query": "quota fixture", "libraryName": "Fixture"}
        runs["direct_resolve_quota"].append(direct_call(str(args.node), api, env, "searchLibraries",
                                                         [resolve_quota_args["query"], resolve_quota_args["libraryName"]]))
        runs["mcp_resolve_quota"].append(mcp_call(str(args.node), entry, env, "resolve-library-id",
                                                 resolve_quota_args))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    require(all(x["exit_code"] == 0 and x["result"].get("results") for x in runs["direct_search"]),
            "direct search did not return fixture results")
    require(all("/fixture/docs" in str(x["content"]) and
                mcp_result_class("resolve-library-id", x) == "success" for x in runs["mcp_search"]),
            "MCP search did not return successful fixture results")
    require(runs["direct_quota"][0]["result"]["outcome"] == "error" and
            "fixture quota exceeded" in runs["direct_quota"][0]["result"]["data"],
            "direct query-docs quota was not an error")
    require("fixture quota exceeded" in str(runs["mcp_quota"][0]["content"]) and
            mcp_result_class("query-docs", runs["mcp_quota"][0]) == "error",
            "MCP query-docs quota was not an error")
    require(runs["direct_resolve_quota"][0]["result"].get("error") == "fixture quota exceeded" and
            not runs["direct_resolve_quota"][0]["result"].get("results"),
            "direct resolve quota was not an error")
    require(runs["mcp_resolve_quota"][0]["is_error_present"] is False and
            "fixture quota exceeded" in str(runs["mcp_resolve_quota"][0]["content"]) and
            mcp_result_class("resolve-library-id", runs["mcp_resolve_quota"][0]) == "non_success",
            "MCP resolve quota was not classified as non-success")
    require(len(Fixture.requests) == 10 and all(p.startswith("/api/v2/") for p in Fixture.requests),
            "unexpected fixture request count or path")
    output = {"candidate": {"name": package["name"], "version": package["version"],
                             "package_sha256": sha(args.package_dir / "package.json"),
                             "entry_sha256": sha(entry), "api_sha256": sha(api),
                             "node_version": subprocess.check_output([str(args.node), "--version"], text=True).strip()},
              "fixture": {"mode": "loopback-only", "http_search": 200, "http_quota": 429,
                          "request_count": len(Fixture.requests)},
              "runs": runs,
              "mcp_classification": {
                  "search": [mcp_result_class("resolve-library-id", x) for x in runs["mcp_search"]],
                  "query_quota": mcp_result_class("query-docs", runs["mcp_quota"][0]),
                  "resolve_quota": mcp_result_class("resolve-library-id", runs["mcp_resolve_quota"][0])},
              "median_ms": {k: round(statistics.median(x["elapsed_ms"] for x in runs[k]), 3)
                            for k in ("direct_search", "mcp_search")}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": "PASS", "medians_ms": output["median_ms"],
                      "fixture_requests": len(Fixture.requests)}))


if __name__ == "__main__":
    main()

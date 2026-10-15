#!/usr/bin/env python3
"""A01-bound GitHubKit one-page code-search witness for the A02 seam."""

from __future__ import annotations

import argparse
import base64
import binascii
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys

import httpx
from githubkit import GitHub
from githubkit.exception import RequestError, RequestFailed
from githubkit.utils import UNSET

ROOT = Path(__file__).resolve().parents[1]
QUERY = "schema"
EFFECTIVE_QUERY = f"{QUERY} repo:openai/codex"
PER_PAGE = 5
API_VERSION = "2026-03-10"
RESPONSE_HEADERS = ("content-type", "x-github-api-version", "x-ratelimit-limit",
                    "x-ratelimit-remaining", "x-ratelimit-reset", "retry-after")


class PrivateResultError(ValueError):
    """A received response cannot be retained in a public receipt."""


def credential() -> tuple[str | None, str]:
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        if name == "GH_TOKEN" and os.environ.get("GH_HOST", "github.com") != "github.com":
            continue
        if value := os.environ.get(name):
            return value, name
    if shutil.which("gh"):
        try:
            gh_env = os.environ.copy()
            gh_env.pop("GH_TOKEN", None)
            gh_env.pop("GH_HOST", None)
            result = subprocess.run(
                ["gh", "auth", "token", "--hostname", "github.com"], capture_output=True, text=True,
                timeout=5, check=False, env=gh_env,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip(), "gh_cli"
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None, "absent"


def optional(value: object) -> dict[str, object]:
    if value is UNSET:
        return {"state": "missing"}
    if value is None:
        return {"state": "null"}
    return {"state": "value", "value": value}


def normalize(data: object, per_page: int = PER_PAGE, page: int = 1) -> dict[str, object]:
    items = []
    for item in data.items:
        if item.repository.private:
            raise PrivateResultError("private repository result refused for public receipt")
        repo = item.repository.full_name
        if not repo or not item.path or not item.sha:
            raise ValueError("code result lacks stable identity")
        items.append({
            "identity": f"{repo}:{item.path}:{item.sha}",
            "repository": repo,
            "path": item.path,
            "sha": item.sha,
            "html_url": item.html_url,
            "language": optional(item.language),
        })
    total = data.total_count
    incomplete = data.incomplete_results
    if type(total) is not int or total < 0 or type(incomplete) is not bool:
        raise ValueError("invalid search totals")
    if total < len(items):
        raise ValueError("total_count smaller than returned item count")
    status = ("partial" if incomplete or total > len(items)
              else "empty_unverified" if not items else "complete_one_page")
    return {"status": status, "total_count": total,
            "incomplete_results": incomplete, "items": items,
            "returned_count": len(items), "page": page, "per_page": per_page}


def capture(response: httpx.Response, effective_query: str = EFFECTIVE_QUERY,
            per_page: int = PER_PAGE, page: int = 1) -> dict[str, object]:
    body = response.content
    return {
        "format": "githubkit-http-response-v1",
        "request": {"method": "GET", "endpoint": "/search/code", "query": effective_query,
                    "page": page, "per_page": per_page},
        "http_status": response.status_code,
        "response_headers": {name: response.headers[name] for name in RESPONSE_HEADERS
                             if name in response.headers},
        "body_base64": base64.b64encode(body).decode("ascii"),
        "body_sha256": hashlib.sha256(body).hexdigest(),
    }


def replay_response(payload: bytes, effective_query: str = EFFECTIVE_QUERY,
                    per_page: int = PER_PAGE, page: int = 1) -> tuple[int, dict[str, str], bytes]:
    raw = json.loads(payload)
    expected_request = {"method": "GET", "endpoint": "/search/code",
                        "query": effective_query, "page": page, "per_page": per_page}
    if (not isinstance(raw, dict) or raw.get("format") != "githubkit-http-response-v1"
            or raw.get("request") != expected_request
            or type(raw.get("http_status")) is not int
            or not 100 <= raw["http_status"] <= 599
            or not isinstance(raw.get("response_headers"), dict)
            or any(k not in RESPONSE_HEADERS or not isinstance(v, str)
                   for k, v in raw["response_headers"].items())
            or not isinstance(raw.get("body_base64"), str)
            or not isinstance(raw.get("body_sha256"), str)):
        raise ValueError("invalid HTTP replay envelope")
    try:
        body = base64.b64decode(raw["body_base64"], validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("invalid replay body encoding") from error
    if base64.b64encode(body).decode("ascii") != raw["body_base64"]:
        raise ValueError("noncanonical replay body encoding")
    if hashlib.sha256(body).hexdigest() != raw["body_sha256"]:
        raise ValueError("replay body digest mismatch")
    return raw["http_status"], raw["response_headers"], body


def search(client: GitHub, route: str, query: str = QUERY,
           effective_query: str = EFFECTIVE_QUERY,
           per_page: int = PER_PAGE, page: int = 1) -> tuple[dict[str, object], dict[str, object]]:
    """Call exactly one SDK endpoint; never log request headers or credentials."""
    metadata: dict[str, object] = {
        "query": query, "effective_query": effective_query,
        "endpoint": "GET /search/code", "sort": "default", "order": "default",
        "page": page, "per_page": per_page, "max_requests": 1,
        "credential_route": route, "sdk": "githubkit", "sdk_version": version("githubkit"),
    }
    captured: list[dict[str, object]] = []

    def capture_response(response: httpx.Response) -> None:
        response.read()
        metadata["http_status"] = response.status_code
        if response.status_code == 200:
            try:
                body = response.json()
            except ValueError:
                body = None
            if (isinstance(body, dict) and isinstance(body.get("items"), list)
                    and any(isinstance(item, dict)
                            and isinstance(item.get("repository"), dict)
                            and item["repository"].get("private") is True
                            for item in body["items"])):
                raise PrivateResultError("private repository result refused for public receipt")
        captured.append(capture(response, effective_query, per_page, page))

    with client.get_sync_client() as http_client:
        http_client.event_hooks["response"].append(capture_response)
        try:
            return _search_once(client, metadata, captured, route, effective_query, per_page, page)
        finally:
            http_client.event_hooks["response"].remove(capture_response)


def _search_once(client: GitHub, metadata: dict[str, object], captured: list[dict[str, object]],
                 route: str, effective_query: str, per_page: int, page: int
                 ) -> tuple[dict[str, object], dict[str, object]]:
    try:
        response = client.rest(API_VERSION).search.code(
            q=effective_query, page=page, per_page=per_page)
        metadata["http_status"] = response.status_code
        metadata["api_version"] = response.raw_request.headers.get("X-GitHub-Api-Version")
        raw = captured[-1]
        metadata["normalized"] = normalize(response.parsed_data, per_page, page)
    except PrivateResultError:
        metadata["normalized"] = {"status": "error", "error_code": "PRIVATE_RESULT_REFUSED"}
        raw = {"status": "withheld_private_result"}
    except RequestFailed as error:
        metadata["http_status"] = error.response.status_code
        metadata["normalized"] = {"status": "error", "error_code": "HTTP_ERROR"}
        raw = captured[-1] if captured else capture(error.response.raw_response, effective_query, per_page, page)
    except RequestError as error:
        if isinstance(error.exc, PrivateResultError):
            metadata["normalized"] = {"status": "error", "error_code": "PRIVATE_RESULT_REFUSED"}
            raw = {"status": "withheld_private_result"}
        elif isinstance(error.exc, TimeoutError):
            metadata["normalized"] = {"status": "error", "error_code": "TIME_LIMIT"}
            raw = captured[-1] if captured else {"status": "unavailable"}
        else:
            metadata["normalized"] = {"status": "error", "error_code": type(error).__name__}
            raw = captured[-1] if captured else {"status": "unavailable"}
    except TimeoutError:
        metadata["normalized"] = {"status": "error", "error_code": "TIME_LIMIT"}
        raw = captured[-1] if captured else {"status": "unavailable"}
    except (ValueError, TypeError) as error:
        metadata["normalized"] = {"status": "error", "error_code": type(error).__name__}
        raw = captured[-1] if captured else {"status": "unavailable"}
        if captured:
            metadata["http_status"] = raw["http_status"]
    return raw, metadata


def retain(raw: dict[str, object], metadata: dict[str, object], output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4)
    target = output / run_id
    target.mkdir()
    raw_bytes = (json.dumps(raw, sort_keys=True, indent=2) + "\n").encode()
    (target / "raw.json").write_bytes(raw_bytes)
    metadata["raw_sha256"] = hashlib.sha256(raw_bytes).hexdigest()
    metadata["captured_at"] = datetime.now(timezone.utc).isoformat()
    (target / "normalized.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("offline", "live"))
    parser.add_argument("--fixture", type=Path, default=ROOT / "dev" / "fixtures" / "github-code-search-empty.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence" / "github-search-one-page")
    args = parser.parse_args()
    if args.mode == "offline":
        fixture = args.fixture.resolve()
        if not fixture.is_relative_to(ROOT):
            parser.error("offline fixture must be inside the project")
        payload = fixture.read_bytes()
        status, headers, body = replay_response(payload)
        requests = []

        def reply(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(status, headers=headers, content=body)

        with GitHub("fixture", transport=httpx.MockTransport(reply), auto_retry=False,
                    http_cache=False, follow_redirects=False, trust_env=False, timeout=10) as client:
            raw, metadata = search(client, "fixture")
        if len(requests) != 1:
            raise RuntimeError("offline SDK fixture did not use one typed request")
        metadata["source_fixture_sha256"] = hashlib.sha256(payload).hexdigest()
    else:
        token, route = credential()
        if not token:
            print("GitHub credential route absent; no request made", file=sys.stderr)
            return 2
        with GitHub(token, auto_retry=False, http_cache=False,
                    follow_redirects=False, timeout=15) as client:
            raw, metadata = search(client, route)
    target = retain(raw, metadata, args.output)
    print(json.dumps({"receipt": str(target), "status": metadata["normalized"]["status"],
                      "credential_route": metadata["credential_route"]}, sort_keys=True))
    return 0 if metadata["normalized"]["status"] not in ("error",) else 2


if __name__ == "__main__":
    raise SystemExit(main())

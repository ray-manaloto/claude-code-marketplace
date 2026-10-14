"""Check that the offline CLI fixture ignores an inherited event sink path."""

import json
import os
from pathlib import Path
import subprocess
import tempfile


root = Path(__file__).resolve().parents[2]
capture = json.loads((root / "evidence/legacy-trackers/capture.json").read_text())
expected = json.loads((root / "evidence/issue-28-cli/fixture.json").read_text())
for optimized in (False, True):
    with tempfile.TemporaryDirectory(prefix="issue28-events-") as tmp:
        directory = Path(tmp)
        outside = directory / "inherited-events.jsonl"
        receipt = directory / "result.json"
        env = os.environ.copy()
        env["KB_EVENTS_JSONL"] = str(outside)
        argv = [capture["installed_python"]]
        if optimized:
            argv.append("-O")
        argv.extend(["-B", str(root / "dev/cli_extension_contract.py"), str(receipt)])
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True, timeout=30)
        if result.returncode or not receipt.exists():
            raise AssertionError(f"fixture failed under optimized={optimized}: {result.stderr}")
        if json.loads(receipt.read_text()) != expected:
            raise AssertionError(f"fixture receipt drift under optimized={optimized}")
        if outside.exists():
            raise AssertionError(f"inherited event sink was touched under optimized={optimized}")
print("2 inherited-event controls passed")

"""Doctor core: Finding, Context, detector discovery and per-detector budgets (C3 §Design constraints).

A detector is any other `dev/doctor/<name>.py` exporting `SURFACES` and `run(ctx) -> list[Finding]`;
optional `context_lines(ctx)` (its own findings arrive as `ctx.findings`), `BUDGET_MS` {surface: ms} and
`CONTEXT_RANK` (lower prints first). `ctx.finding(...)` builds a Finding without importing this module.
"""
from __future__ import annotations

import dataclasses
import importlib.util
from pathlib import Path
import subprocess
import threading
import time

BUDGET_MS = {"session-start": 3000, "check": 10000, "pre-commit": 300}
SEVERITY = {"P1": 0, "P2": 1, "P3": 2, "info": 3, "skipped": 4}


@dataclasses.dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    subject: str
    evidence: tuple = ()
    fix_hint: str = ""
    auto_fixable: bool = False

    def to_json(self) -> dict:
        return {"class": self.id.split(".")[0], **dataclasses.asdict(self), "evidence": list(self.evidence)}


@dataclasses.dataclass(frozen=True)
class Context:
    repo: Path
    surface: str
    plan_id: str
    home: Path
    payload: dict
    findings: tuple = ()
    finding = Finding

    @property
    def plan(self) -> Path:
        return self.repo / ".planning" / self.plan_id

    def git(self, *args: str, codes=(0,)) -> str | None:
        result = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, text=True, timeout=5)
        return result.stdout if result.returncode in codes else None


def failure(name: str, error: Exception) -> Finding:
    return Finding("doctor.detector-error", "P2", f"{name}: {type(error).__name__}: {error}")


def attempt(name, module, ctx, results):
    """Run one detector, recording (findings, (rank, context lines), error, finish time)."""
    try:
        found = list(module.run(ctx))
        lines = getattr(module, "context_lines", None) if ctx.surface == "session-start" else None
        block = list(lines(dataclasses.replace(ctx, findings=tuple(found)))) if lines else []
        results[name] = (found, (getattr(module, "CONTEXT_RANK", 50), block), None, time.monotonic())
    except Exception as error:  # noqa: BLE001  reported as doctor.detector-error, exit 3
        results[name] = ([], (0, []), error, time.monotonic())


def run(ctx: Context, budget_ms: int | None = None) -> tuple[list[Finding], list[str], bool]:
    """Run each detector of ctx.surface concurrently; one past its budget is reported `skipped` and abandoned."""
    started, results, jobs, findings, blocks, raised = time.monotonic(), {}, [], [], [], False
    for path in sorted(Path(__file__).resolve().parent.glob("*.py")):
        if path.stem in ("cli", "core"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"doctor_{path.stem}", path)
            spec.loader.exec_module(module := importlib.util.module_from_spec(spec))
        except Exception as error:  # noqa: BLE001
            findings.append(failure(path.stem, error))
            raised = True
            continue
        if ctx.surface in getattr(module, "SURFACES", ()):
            ms = budget_ms if budget_ms is not None else getattr(module, "BUDGET_MS", BUDGET_MS).get(ctx.surface, 0)
            thread = threading.Thread(target=attempt, args=(path.stem, module, ctx, results), daemon=True)
            thread.start()
            jobs.append((path.stem, thread, ms))
    for name, thread, ms in jobs:
        thread.join(max(0.0, started + ms / 1000 - time.monotonic()))
        found, block, error, done = results.get(name, ([], (0, []), None, float("inf")))
        if done - started > ms / 1000:
            findings.append(Finding("doctor.skipped", "skipped", f"{name}: budget {ms} ms"))
        elif error is not None:
            findings.append(failure(name, error))
            raised = True
        else:
            findings += found
            blocks.append(block)
    findings.sort(key=lambda f: (SEVERITY.get(f.severity, 9), f.id, f.subject))
    return findings, [line for _, lines in sorted(blocks, key=lambda b: b[0]) for line in lines], raised

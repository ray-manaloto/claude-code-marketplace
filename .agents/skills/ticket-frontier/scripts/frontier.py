#!/usr/bin/env python3
"""Mechanical half of the ticket-frontier skill: ready set, priorities, claims, gates, ledger.

Run as `python3 -I <skill>/scripts/frontier.py [--repo R] [--plan-id ID] <command>`.
Reads `.planning/<ID>/frontier.toml`, the tracker graph (`ticket-ledger.json` from
CT-05, else `--graph FILE`), `lanes/*.json` and `frontier/state.json`. Writes only
under `.planning/<ID>/frontier/`. Every input is data; nothing here reaches the
network or runs a tracker command.

Commands:
  plan            ready set, priority order, cxx slot, chosen lanes (+ --json, --write)
  next            the next lane to dispatch with model, effort, ceiling and the Agent call
  claim <unit>    record a claim (idempotent; refuses a double claim and a path conflict)
  release <unit>  drop a claim; --from-journal + --resume refuses a lane over its ceiling
  status          what is available, claimed and missing (+ --json)
  answer          record a plain-text user answer (frontier/answers.jsonl) until CT-24 exists
  executor-gate   evaluate G1–G7 for a non-native executor; `native` always passes
  ledger          append or list learning-ledger rows

Exit codes: 0 ok, 2 refusal with one reason per line, 1 usage error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, TypedDict


class Ticket(TypedDict):
    id: str
    title: str
    state: str
    blockedBy: list[str]
    parent: str | None
    owned_paths: list[str]
    wave: int | None


class ReadyTicket(TypedDict):
    id: str
    title: str
    klass: str | None
    critical_path: int
    unblocks: int
    always_active: bool
    wave: int | None
    owned_paths: list[str]
    heavy: bool


DEFAULT_PLAN_ID = "2026-10-10-marketplace-macos-reflection-scaffold"
WRITER_ROLES = ("implementer", "doc-writer")
PRIORITY_RULES = ["critical_path", "unblocks", "always_active", "wave", "number"]
FABLE_KINDS = ("review", "retro", "synthesis", "design")
ESCALATION_REASON = "reasoning"
LEDGER_KINDS = ("mechanical", "judgement", "navigation", "workflow", "role", "hook")
LEDGER_MODES = ("auto", "propose")
LEDGER_KEYS = ("ticket", "unit", "category", "finding_id", "kind", "destination", "mode", "verification",
               "retro_row", "applied_by")
GATE_ITEMS = {
    "G1": "CT-17, CT-19, CT-22, CT-07 published with retro passed (lane:validate over the four records)",
    "G2": "~/.codex/skills/{codex-agent,claude-agent,.shared/agent-protocol} under version control with a recorded HEAD",
    "G3": "agent-protocol `run test`, `schemas:check`, `codegen:check` all rc 0",
    "G4": "dynamic-agents tickets 01–07 integrated and promoted (ticket 33); installed == repo@HEAD",
    "G5": "capability snapshot command (tickets 04 + 12) rc 0 with its test in `run test`",
    "G6": "smoke dispatch:claude mode=review safe: status completed, exit_code 0, result_schema.validation passed",
    "G7": "team mode only: one agent-qualify sidecar with participation = native_qualified",
}
DEGRADED = (  # ticket, artifact (repo-relative or plan-relative), what the skill does without it
    ("CT-05", "ticket-ledger.json", "plan",
     "write a graph JSON from the tracker (gh api graphql blockedBy/parent) or ticket-ledger.md and pass --graph"),
    ("CT-15", "dev/plan_records.py", "repo", "append the progress line by hand (plan:log)"),
    ("CT-17", "dev/lane.py allocate", "repo", "allocate and integrate by the manual sequence in references/scheduler.md"),
    ("CT-19", "dev/lane_brief.py", "repo", "compose the brief from references/brief-templates.md"),
    ("CT-22", "dev/doctor/budget.py", "repo", "ceiling comes from frontier.toml alone; no threshold cross-check"),
    ("CT-24", "decisions.jsonl", "plan", "take the heavy-run admission from --admitted after asking the user once"),
)


class UsageError(Exception):
    pass


class Refusal(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(f"{self.prog}: error: {message}")


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def norm_id(value: object) -> str:
    """`21`, `"21"`, `"#21"` -> `#21`; `"CT-25"` stays; None or empty -> ""."""
    if value is None:
        return ""
    text = str(value).strip()
    if re.fullmatch(r"\d+", text):
        return f"#{text}"
    return text


def unit_id(ticket: str) -> str:
    """Default unit name for a ticket: `#21` -> `21`, `CT-15` -> `ct15`."""
    return ticket.lstrip("#").replace("CT-", "ct")


def expand_include(items) -> set[str]:
    out: set[str] = set()
    for item in items:
        match = re.fullmatch(r"#?(\d+)-#?(\d+)", str(item).strip())
        if match:
            lo, hi = int(match.group(1)), int(match.group(2))
            out.update(f"#{n}" for n in range(lo, hi + 1))
        else:
            out.add(norm_id(item))
    return out


def ticket_number(ticket: str) -> int:
    match = re.search(r"(\d+)", ticket)
    return int(match.group(1)) if match else 0


def path_overlaps(a: str, b: str) -> bool:
    a, b = a.strip(), b.strip()
    if not a or not b:
        return False
    if a.endswith("/") or b.endswith("/"):
        return a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/") or a.rstrip("/") == b.rstrip("/")
    return a == b


class Frontier:
    def __init__(self, repo: Path, plan_id: str):
        self.repo = repo
        self.plan_dir = repo / ".planning" / plan_id
        self.frontier_dir = self.plan_dir / "frontier"
        self.state_path = self.frontier_dir / "state.json"
        config_path = self.plan_dir / "frontier.toml"
        try:
            self.config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise UsageError(f"frontier.toml missing: {config_path} ({exc.strerror})")
        except tomllib.TOMLDecodeError as exc:
            raise UsageError(f"frontier.toml invalid: {exc}")
        self.classes = {name: dict(spec, members=expand_include(spec.get("include", [])))
                        for name, spec in self.config.get("classes", {}).items()}

    # ---- state -----------------------------------------------------------------
    def state(self) -> dict:
        state = read_json(self.state_path, None)
        if not isinstance(state, dict):
            state = {"schema": 1, "claims": {}, "history": []}
        state.setdefault("claims", {})
        state.setdefault("continuations", {})
        state.setdefault("history", [])
        return state

    def save_state(self, state: dict) -> None:
        self.frontier_dir.mkdir(parents=True, exist_ok=True)
        state["updated_at"] = utc_now()
        self.state_path.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    # ---- inputs ----------------------------------------------------------------
    def degraded(self) -> dict:
        out = {}
        for ticket, artifact, where, fallback in DEGRADED:
            name = artifact.split(" ")[0]
            path = (self.plan_dir if where == "plan" else self.repo) / name
            available = path.is_file()
            if available and " " in artifact:  # "dev/lane.py allocate": the verb must exist in the file
                available = artifact.split(" ", 1)[1] in path.read_text(encoding="utf-8", errors="replace")
            out[ticket] = {"artifact": artifact, "available": available, "fallback": fallback}
        return out

    def lanes(self) -> list[dict]:
        records = []
        for path in sorted((self.plan_dir / "lanes").glob("*.json")):
            record = read_json(path)
            if isinstance(record, dict) and isinstance(record.get("unit"), str):
                records.append(record)
        return records

    @staticmethod
    def lane_tickets(record: dict) -> list[str]:
        out = []
        for item in record.get("tickets") or []:
            match = re.match(r"\s*(#\d+|CT-\d+)", str(item))
            if match:
                out.append(match.group(1))
        return out

    def graph(self, graph_arg: str | None) -> tuple[dict[str, Ticket], str]:
        ledger = self.plan_dir / "ticket-ledger.json"
        if ledger.is_file():
            data, source = read_json(ledger), "ticket-ledger.json"
        elif graph_arg:
            data, source = read_json(Path(graph_arg)), Path(graph_arg).name
        else:
            raise Refusal("not available yet: CT-05 (ticket-ledger.json); pass --graph <file> "
                          "(JSON {tickets:[{id,state,blockedBy,...}]}) until ledger:sync exists")
        if not isinstance(data, dict) or not isinstance(data.get("tickets"), list):
            raise Refusal(f"graph {source} is not a JSON object with a tickets list")
        tickets: dict[str, Ticket] = {}
        for index, raw in enumerate(data["tickets"]):
            if not isinstance(raw, dict):
                raise Refusal(f"graph {source}: tickets[{index}] is not an object")
            tid = norm_id(raw.get("id") or raw.get("number") or raw.get("local_id"))
            if not tid:
                raise Refusal(f"graph {source}: tickets[{index}] has no id/number/local_id")
            wave = raw.get("wave")
            tickets[tid] = Ticket(
                id=tid,
                title=str(raw.get("title") or ""),
                state=str(raw.get("state") or "open").lower(),
                blockedBy=[norm_id(b) for b in raw.get("blockedBy") or raw.get("blocked_by") or []],
                parent=norm_id(raw["parent"]) if raw.get("parent") else None,
                owned_paths=[str(p) for p in raw.get("owned_paths") or []],
                wave=wave if isinstance(wave, int) else None,
            )
        return tickets, source

    def ticket_class(self, ticket: str) -> str | None:
        for name, spec in self.classes.items():
            if ticket in spec["members"]:
                return name
        return None

    # ---- thresholds --------------------------------------------------------------
    def ceiling(self, model: str) -> int:
        window = int(self.config.get("windows", {}).get(model, 0))
        return int(window * float(self.config.get("context_ceiling_fraction", 0.5)))

    def check_thresholds(self) -> dict:
        budget = self.repo / "dev/doctor/budget.py"
        implement_model = self.config.get("model_policy", {}).get("implement", {}).get("model", "opus")
        ceiling = self.ceiling(implement_model)
        if not budget.is_file():
            return {"budget_py": None, "ceiling": ceiling, "model": implement_model}
        text = budget.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"fork_deny\W+?(\d[\d_]*)", text)
        if not match:
            return {"budget_py": str(budget), "fork_deny": None, "ceiling": ceiling, "model": implement_model}
        fork_deny = int(match.group(1).replace("_", ""))
        if fork_deny != ceiling:
            raise Refusal(f"threshold mismatch: dev/doctor/budget.py fork_deny={fork_deny} but "
                          f"frontier.toml windows.{implement_model} × context_ceiling_fraction = {ceiling}; "
                          "one threshold source (K1 §2): change frontier.toml or budget.py, then re-plan")
        return {"budget_py": str(budget), "fork_deny": fork_deny, "ceiling": ceiling, "model": implement_model}

    # ---- planning ------------------------------------------------------------------
    def admissions(self, admitted_flags: list[str]) -> set[str]:
        admitted = {norm_id(t) for t in admitted_flags}
        decisions = self.plan_dir / "decisions.jsonl"
        if decisions.is_file():
            for line in decisions.read_text(encoding="utf-8", errors="replace").splitlines()[-500:]:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and row.get("kind") == "admission" and row.get("ticket") and \
                        row.get("state", "granted") == "granted" and not row.get("consumed"):
                    admitted.add(norm_id(row["ticket"]))
        return admitted

    def plan(self, graph_arg: str | None, admitted_flags: list[str]) -> dict:
        thresholds = self.check_thresholds()
        tickets, source = self.graph(graph_arg)
        state = self.state()
        lanes = self.lanes()
        done, held, claimed_by = set(), {}, {}
        for record in lanes:
            status = str(record.get("status") or "").lower()
            finished = status.startswith(("integrated", "published")) and record.get("retro") == "passed"
            for ticket in self.lane_tickets(record):
                if finished:
                    done.add(ticket)
                elif not status.startswith("closed"):
                    held[ticket] = record["unit"]
        for unit, claim in state["claims"].items():
            claimed_by.setdefault(claim["ticket"], unit)
        for unit, cont in state["continuations"].items():
            held.setdefault(cont["ticket"], f"{unit} (split-required: carve {unit}-2)")
        for tid, ticket in tickets.items():
            if ticket["state"] in ("closed", "done", "merged"):
                done.add(tid)
        open_ids = [tid for tid in tickets if tid not in done]
        dependents = {tid: [] for tid in tickets}
        for tid in open_ids:
            for blocker in tickets[tid]["blockedBy"]:
                if blocker in dependents and blocker not in done:
                    dependents[blocker].append(tid)
        memo: dict[str, int] = {}

        def critical_path(tid: str, trail=()) -> int:
            if tid in memo:
                return memo[tid]
            if tid in trail:
                return 0
            best = 0
            for dep in dependents.get(tid, []):
                best = max(best, 1 + critical_path(dep, trail + (tid,)))
            memo[tid] = best
            return best

        waves = {norm_id(k): v for k, v in self.config.get("waves", {}).items() if isinstance(v, int)}
        ready: list[ReadyTicket] = []
        for tid in open_ids:
            ticket = tickets[tid]
            if any(b not in done for b in ticket["blockedBy"]):
                continue
            if tid in held or tid in claimed_by:
                continue
            klass = self.ticket_class(tid)
            ready.append(ReadyTicket(
                id=tid, title=ticket["title"], klass=klass,
                critical_path=critical_path(tid), unblocks=len(dependents.get(tid, [])),
                always_active=klass in self.config.get("always_active", []),
                wave=waves.get(tid, ticket["wave"]), owned_paths=ticket["owned_paths"],
                heavy=bool(klass and self.classes[klass].get("heavy")),
            ))

        def rank(t: ReadyTicket) -> tuple[int, int, bool, int, int, str]:
            wave = t["wave"]
            return (-t["critical_path"], -t["unblocks"], not t["always_active"],
                    wave if wave is not None else 10 ** 6, ticket_number(t["id"]), t["id"])

        ready.sort(key=rank)

        # capacity: writer lanes against max_parallel, every claim against the live cap
        max_parallel = int(self.config.get("max_parallel", 3))
        max_live = int(self.config.get("max_live_agents", 8))
        writers_active = sum(1 for c in state["claims"].values() if c.get("role") in WRITER_ROLES)
        live = len(state["claims"])
        writers_free = max(0, max_parallel - writers_active)
        live_free = max(0, max_live - live)
        capacity = {"max_parallel": max_parallel, "writers_active": writers_active, "writers_free": writers_free,
                    "live_agents": live, "max_live_agents": max_live,
                    "state": "saturated" if writers_free == 0 or live_free == 0 else "open"}

        # active path sets for the conflict rule
        active_paths = []
        for record in lanes:
            status = str(record.get("status") or "").lower()
            if status.startswith(("integrated", "published", "closed")):
                continue
            active_paths.append((record["unit"], list(record.get("owned_paths") or []) +
                                 list(record.get("excluded_shared_paths") or [])))
        for unit, claim in state["claims"].items():
            if claim.get("owned_paths"):
                active_paths.append((unit, list(claim["owned_paths"])))

        conflicts: list[dict[str, Any]] = []
        questions: list[str] = []
        chosen: list[dict[str, Any]] = []
        skipped: list[dict[str, str]] = []

        def conflict_of(candidate: ReadyTicket) -> dict[str, Any] | None:
            paths = candidate["owned_paths"]
            for unit, theirs in active_paths:
                hit = sorted({p for p in paths for q in theirs if path_overlaps(p, q)})
                if hit:
                    return {"ticket": candidate["id"], "with": unit, "paths": hit}
            hot = [h for h in self.config.get("hot_paths", {}).get("paths", []) if any(path_overlaps(p, h) for p in paths)]
            if len(hot) > 1:
                return {"ticket": candidate["id"], "with": "hot-paths", "paths": hot}
            return None

        # the always-active slot first
        admitted = self.admissions(admitted_flags)
        cxx_slot: dict[str, Any] | None = None
        slots = min(writers_free, live_free)
        for klass in self.config.get("always_active", []):
            spec = self.classes.get(klass, {})
            members = [t for t in ready if t["klass"] == klass]
            if not members or slots <= 0:
                continue
            if any(c.get("class") == klass for c in state["claims"].values()):
                cxx_slot = {"class": klass, "state": "occupied", "ticket": None, "admitted": None, "split": None,
                            "note": f"{klass} slot already held by an active claim"}
                break
            order = [norm_id(t) for t in spec.get("order", [])]
            members.sort(key=lambda t: (order.index(t["id"]) if t["id"] in order else len(order), ticket_number(t["id"])))
            pick = members[0]
            conflict = conflict_of(pick)
            if conflict:
                conflicts.append(conflict)
                continue
            is_admitted = pick["id"] in admitted or not pick["heavy"]
            number = unit_id(pick["id"])
            split: str | None
            if is_admitted:
                unit, split, note = number, None, f"{klass} slot: {pick['id']} admitted for this run"
            elif spec.get("offline_split", True):
                unit, split = f"{number}-offline", "offline-portion"
                note = f"offline-portion of {pick['id']}; heavy run not admitted"
                questions.append(f"admission: run the heavy portion of {pick['id']} now? "
                                 f"(asked once per scheduler run; pass --admitted {pick['id']} after a yes)")
            else:
                cxx_slot = {"class": klass, "state": "empty", "ticket": pick["id"], "admitted": False, "split": None,
                            "note": f"{pick['id']} needs an admission and offline_split is off"}
                questions.append(f"admission: run the heavy portion of {pick['id']} now?")
                break
            cxx_slot = {"class": klass, "state": "filled", "ticket": pick["id"], "admitted": is_admitted,
                        "split": split, "note": note}
            chosen.append({"unit": unit, "ticket": pick["id"], "role": "implementer", "class": klass, "split": split,
                           "rule": f"always_active.{klass}", "owned_paths": pick["owned_paths"]})
            slots -= 1
            break

        for candidate in ready:
            if slots <= 0:
                break
            if any(c["ticket"] == candidate["id"] for c in chosen):
                continue
            if candidate["heavy"] and candidate["id"] not in admitted:
                skipped.append({"ticket": candidate["id"], "reason": "heavy, not admitted; one heavy run at a time"})
                continue
            conflict = conflict_of(candidate)
            if conflict:
                conflicts.append(conflict)
                continue
            number = unit_id(candidate["id"])
            chosen.append({"unit": number, "ticket": candidate["id"], "role": "implementer", "class": candidate["klass"],
                           "split": None, "rule": "priority", "owned_paths": candidate["owned_paths"]})
            slots -= 1

        return {
            "schema": 1, "ts": utc_now(), "graph_source": source, "thresholds": thresholds,
            "priority_rules": PRIORITY_RULES, "ready": [{("class" if k == "klass" else k): v for k, v in t.items()} for t in ready], "ready_order": [t["id"] for t in ready],
            "done": sorted(done), "held": held, "claimed": claimed_by, "continuations": state["continuations"],
            "capacity": capacity,
            "cxx_slot": cxx_slot, "chosen": chosen, "skipped": skipped, "conflicts": conflicts, "questions": questions,
            "degraded": {k: v for k, v in self.degraded().items() if not v["available"]},
        }

    # ---- next -------------------------------------------------------------------
    def policy(self, kind: str) -> tuple[str, str, str]:
        policy = self.config.get("model_policy", {})
        entry = policy.get(kind) or policy.get("implement") or {"model": "opus", "effort": "high"}
        return str(entry.get("model", "opus")), str(entry.get("effort", "high")), f"policy.{kind}"

    def escalated(self, journal: str | None) -> bool:
        if not journal:
            return False
        threshold = int(self.config.get("model_policy", {}).get("escalate_after_partial", 1))
        count = 0
        try:
            lines = Path(journal).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return False
        for line in lines[-1000:]:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if not isinstance(row, dict):
                continue
            if row.get("agent_type") == "implementer" and row.get("model") == "opus" and \
                    row.get("task_status") in ("partial", "blocked") and row.get("reason") == ESCALATION_REASON:
                count += 1
        return count >= threshold

    def next_lane(self, graph_arg: str | None, admitted_flags: list[str], journal: str | None) -> dict:
        plan = self.plan(graph_arg, admitted_flags)
        if not plan["chosen"]:
            cap = plan["capacity"]
            if cap["state"] == "saturated":
                raise Refusal(f"max_parallel reached: {cap['writers_active']}/{cap['max_parallel']} writer lanes, "
                              f"{cap['live_agents']}/{cap['max_live_agents']} live agents; release a lane first")
            raise Refusal("nothing to dispatch: ready set is empty or every candidate conflicts "
                          f"(conflicts: {json.dumps(plan['conflicts'])})")
        lane = plan["chosen"][0]
        kind = "docs" if lane["role"] == "doc-writer" else "implement"
        model, effort, rule = self.policy(kind)
        if kind not in FABLE_KINDS and self.escalated(journal):
            model, effort, rule = "fable", "high", "escalation"
        if lane.get("class") == "design":
            model, effort, rule = "fable", "high", "class.design"
        ceiling = self.ceiling(model)
        brief_lines = [
            (f"CTX-CEILING: {ceiling} (model {model}). Checkpoint to .planning/<PLAN_ID>/ledger-{lane['unit']}.jsonl at "
            f"{int(ceiling * 0.8)}; at the ceiling commit, write the handoff and stop; do not fork."),
            f"MODEL: {model} effort {effort} (rule {rule}).",
        ]
        if lane.get("split"):
            brief_lines.append(f"SPLIT: {lane['split']} of {lane['ticket']}: source, CMake and fixture preparation only; "
                               "no heavy run (not admitted); report the heavy step as a separate unit.")
        degraded = plan["degraded"]
        brief_source = "lane:brief --role implementer (CT-19)" if "CT-19" not in degraded else \
            "references/brief-templates.md (not available yet: CT-19 lane:brief)"
        return {
            "unit": lane["unit"], "ticket": lane["ticket"], "role": lane["role"], "class": lane.get("class"),
            "split": lane.get("split"), "model": model, "effort": effort, "rule": rule, "ceiling": ceiling,
            "brief_lines": brief_lines, "brief_source": brief_source,
            "dispatch": {"subagent_type": lane["role"], "model": model, "effort": effort, "run_in_background": True,
                         "prompt": "<brief from brief_source> + brief_lines + the scheduler's judgement lines"},
            "then": [(f"frontier.py claim {lane['unit']} --ticket {lane['ticket']} --role {lane['role']} "
                     "--owned-paths <scheduler proposal>"),
                     "lane:allocate <unit> (CT-17)" if "CT-17" not in degraded else
                     "allocate by hand: lanes/<unit>.json, git worktree add .claude/worktrees/<unit> -b claude/<unit>-<slug> (not available yet: CT-17)"],
            "questions": plan["questions"], "cxx_slot": plan["cxx_slot"], "degraded": degraded,
        }

    # ---- claim / release -------------------------------------------------------------
    def claim(self, unit: str, ticket: str, role: str, owned_paths: list[str], klass: str | None) -> str:
        ticket = norm_id(ticket)
        state = self.state()
        claims = state["claims"]
        existing = claims.get(unit)
        if existing:
            if existing["ticket"] == ticket:
                return f"already claimed: {unit} holds {ticket} ({existing['role']}) since {existing['claimed_at']}"
            raise Refusal(f"unit {unit} already holds {existing['ticket']}; release it before claiming {ticket}")
        if role in WRITER_ROLES:
            for other, claim in claims.items():
                if claim["ticket"] == ticket and claim.get("role") in WRITER_ROLES:
                    raise Refusal(f"ticket {ticket} already claimed by {other} ({claim['role']})")
        for record in self.lanes():
            status = str(record.get("status") or "").lower()
            if role in WRITER_ROLES and ticket in self.lane_tickets(record) and \
                    not status.startswith(("integrated", "published", "closed")) and record["unit"] != unit:
                raise Refusal(f"ticket {ticket} already held by lane record {record['unit']} (status {record.get('status')})")
        max_live = int(self.config.get("max_live_agents", 8))
        if len(claims) >= max_live:
            raise Refusal(f"hard cap: {max_live} live agents already claimed; release one before dispatching {unit}")
        if role in WRITER_ROLES:
            writers = sum(1 for c in claims.values() if c.get("role") in WRITER_ROLES)
            if writers >= int(self.config.get("max_parallel", 3)):
                raise Refusal(f"max_parallel reached: {writers} writer lanes active; release one before claiming {unit}")
            for record in self.lanes():
                status = str(record.get("status") or "").lower()
                if status.startswith(("integrated", "published", "closed")) or record["unit"] == unit:
                    continue
                theirs = list(record.get("owned_paths") or []) + list(record.get("excluded_shared_paths") or [])
                hit = sorted({p for p in owned_paths for q in theirs if path_overlaps(p, q)})
                if hit:
                    raise Refusal(f"path conflict with lane {record['unit']}: {', '.join(hit)}")
            for other, claim in claims.items():
                hit = sorted({p for p in owned_paths for q in claim.get("owned_paths") or [] if path_overlaps(p, q)})
                if hit:
                    raise Refusal(f"path conflict with claim {other}: {', '.join(hit)}")
        for pending, cont in list(state["continuations"].items()):
            if cont["ticket"] == ticket and role in WRITER_ROLES:
                state["continuations"].pop(pending)
                state["history"].append({"ts": utc_now(), "event": "continued", "unit": pending, "by": unit, "ticket": ticket})
        claims[unit] = {"ticket": ticket, "role": role, "owned_paths": owned_paths, "class": klass or self.ticket_class(ticket),
                        "claimed_at": utc_now(), "status": "claimed"}
        state["history"].append({"ts": utc_now(), "event": "claim", "unit": unit, "ticket": ticket, "role": role})
        self.save_state(state)
        return f"claimed: {unit} -> {ticket} ({role}); {len(claims)} live, " \
               f"{sum(1 for c in claims.values() if c.get('role') in WRITER_ROLES)} writers"

    @staticmethod
    def last_usage(journal: str) -> int | None:
        try:
            lines = Path(journal).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            raise Refusal(f"journal unreadable: {journal} ({exc.strerror})")
        for line in reversed(lines[-1000:]):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            usage = row.get("usage") if isinstance(row, dict) else None
            if isinstance(usage, dict):
                if isinstance(usage.get("total"), int):
                    return usage["total"]
                return int(usage.get("input", 0)) + int(usage.get("cache_creation", 0)) + int(usage.get("cache_read", 0))
        return None

    def release(self, unit: str, journal: str | None, resume: bool) -> str:
        state = self.state()
        claim = state["claims"].get(unit)
        if claim is None:
            return f"not claimed: {unit} (release is idempotent)"
        if journal:
            usage = self.last_usage(journal)
            model = claim.get("model") or self.config.get("model_policy", {}).get("implement", {}).get("model", "opus")
            ceiling = self.ceiling(model)
            if usage is not None and usage >= ceiling:
                claim["status"] = "split-required"
                claim["last_usage"] = usage
                self.save_state(state)
                if resume:
                    raise Refusal(f"split-required: {unit} last usage {usage} >= ceiling {ceiling}; "
                                  "carve a continuation unit from its commits and ledger for a fresh agent "
                                  "(references/scheduler.md §Continuation), do not --resume")
        state["claims"].pop(unit)
        note = ""
        if claim.get("status") == "split-required":
            state["continuations"][unit] = {"ticket": claim["ticket"], "role": claim.get("role"), "status": "split-required",
                                            "last_usage": claim.get("last_usage"), "owned_paths": claim.get("owned_paths") or [],
                                            "released_at": utc_now()}
            note = f"; split-required: {claim['ticket']} is held until you claim {unit}-2 (scheduler.md §Continuation)"
        state["history"].append({"ts": utc_now(), "event": "release", "unit": unit, "ticket": claim["ticket"],
                                 "status": claim.get("status")})
        self.save_state(state)
        return f"released: {unit} ({claim['ticket']}){note}; re-run plan"

    def answer(self, question: str, answer: str) -> str:
        """Record a plain-text user answer until CT-24's decisions.jsonl carries it."""
        self.frontier_dir.mkdir(parents=True, exist_ok=True)
        row = {"ts": utc_now(), "question": question, "answer": answer}
        with (self.frontier_dir / "answers.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        return f"recorded: {question!r} -> {answer!r} (frontier/answers.jsonl; not an admission: pass --admitted for that)"

    # ---- status ------------------------------------------------------------------
    def status(self) -> dict:
        state = self.state()
        claims = state["claims"]
        writers = sum(1 for c in claims.values() if c.get("role") in WRITER_ROLES)
        gate = read_json(self.frontier_dir / "executor-gate.json", None)
        receipts = sorted(p.name for p in self.frontier_dir.glob("plan-*.json")) if self.frontier_dir.is_dir() else []
        return {
            "plan_dir": str(self.plan_dir), "executor": self.config.get("executor", "native"),
            "executor_gate": gate, "retro_apply": self.config.get("retro_apply", "auto"),
            "capacity": {"max_parallel": int(self.config.get("max_parallel", 3)), "writers_active": writers,
                         "live_agents": len(claims), "max_live_agents": int(self.config.get("max_live_agents", 8))},
            "ceilings": {m: self.ceiling(m) for m in self.config.get("windows", {})},
            "claims": claims, "continuations": state["continuations"],
            "last_plan": receipts[-1] if receipts else None, "degraded": self.degraded(),
        }

    @staticmethod
    def format_status(status: dict) -> str:
        lines = [(f"ticket-frontier: executor {status['executor']} | retro_apply {status['retro_apply']} | "
                 f"writers {status['capacity']['writers_active']}/{status['capacity']['max_parallel']} | "
                 f"live {status['capacity']['live_agents']}/{status['capacity']['max_live_agents']} | "
                 f"ceilings {', '.join(f'{m} {v}' for m, v in status['ceilings'].items())}")]
        for unit, claim in status["claims"].items():
            lines.append(f"  claim {unit}: {claim['ticket']} {claim['role']} {claim.get('status')} since {claim['claimed_at']}")
        for unit, cont in status["continuations"].items():
            lines.append(f"  continuation pending: {unit} ({cont['ticket']}) split-required; claim {unit}-2")
        lines.append(f"  last plan receipt: {status['last_plan'] or 'none'}")
        for ticket, info in status["degraded"].items():
            if info["available"]:
                lines.append(f"  available: {ticket} ({info['artifact']})")
            else:
                lines.append(f"  not available yet: {ticket} ({info['artifact']}) -> {info['fallback']}")
        return "\n".join(lines)

    # ---- executor gate --------------------------------------------------------------
    def executor_gate(self, executor: str, team: bool, config: str | None, write: bool) -> tuple[int, str]:
        if executor == "native":
            return 0, "executor native: always allowed (no gate item applies)"
        probes = {}
        path = Path(config) if config else self.frontier_dir / "executor-gate.config.json"
        if path.is_file():
            loaded = read_json(path, {})
            probes = loaded if isinstance(loaded, dict) else {}
        results, failed, lines = {}, [], []
        for item, meaning in GATE_ITEMS.items():
            if item == "G7" and not team:
                results[item] = {"result": "SKIP", "why": "single-agent mode (allow_subagents=false)"}
                lines.append(f"{item}: SKIP ({results[item]['why']})")
                continue
            probe = probes.get(item)
            ok, why = self.run_probe(probe)
            results[item] = {"result": "PASS" if ok else "FAIL", "why": why, "meaning": meaning}
            if not ok:
                failed.append(item)
            lines.append(f"{item}: {'PASS' if ok else 'FAIL'} ({why})")
        rc = 2 if failed else 0
        head = f"executor {executor}{' team' if team else ''}: {'PASS' if rc == 0 else 'FAIL'}"
        if failed:
            lines.append(f"run native until {', '.join(failed)} pass; see references/executor-gate.md")
        if write:
            self.frontier_dir.mkdir(parents=True, exist_ok=True)
            (self.frontier_dir / "executor-gate.json").write_text(json.dumps(
                {"ts": utc_now(), "executor": executor, "team": team, "failed": failed, "items": results},
                indent=1) + "\n", encoding="utf-8")
        return rc, "\n".join([head, *lines])

    @staticmethod
    def run_probe(probe) -> tuple[bool, str]:
        if not isinstance(probe, dict):
            return False, "no probe configured"
        if "rc" in probe:
            return int(probe["rc"]) == 0, probe.get("note") or f"recorded rc {probe['rc']}"
        if "path" in probe:
            exists = Path(str(probe["path"])).exists()
            return exists, f"path {'exists' if exists else 'missing'}: {probe['path']}"
        if "value" in probe:
            want = probe.get("expect", "native_qualified")
            return probe["value"] == want, f"value {probe['value']!r} (expect {want!r})"
        if "cmd" in probe and isinstance(probe["cmd"], list) and probe["cmd"]:
            try:
                result = subprocess.run([str(c) for c in probe["cmd"]], capture_output=True, text=True, timeout=120,
                                        check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                return False, f"probe error: {exc.__class__.__name__}"
            return result.returncode == 0, f"{' '.join(str(c) for c in probe['cmd'][:3])}… rc {result.returncode}"
        return False, "probe shape unknown (rc | path | value | cmd)"

    # ---- learning ledger ----------------------------------------------------------------
    def ledger_append(self, row_text: str) -> str:
        try:
            row = json.loads(row_text)
        except ValueError as exc:
            raise Refusal(f"row is not JSON: {exc}")
        if not isinstance(row, dict):
            raise Refusal("row must be a JSON object")
        missing = [k for k in LEDGER_KEYS if k not in row]
        if missing:
            raise Refusal(f"row missing keys: {', '.join(missing)}")
        if row["kind"] not in LEDGER_KINDS:
            raise Refusal(f"kind must be one of {', '.join(LEDGER_KINDS)}, not {row['kind']!r}")
        if row["mode"] not in LEDGER_MODES:
            raise Refusal(f"mode must be one of {', '.join(LEDGER_MODES)}, not {row['mode']!r}")
        verification = row["verification"]
        if not isinstance(verification, dict) or "cmd" not in verification or "rc" not in verification:
            raise Refusal("verification must be an object with cmd and rc")
        if not re.search(r"retros/[^/]+\.md#", str(row["retro_row"])):
            raise Refusal("retro_row must cite retros/<unit>.md#<row id>")
        row.setdefault("ts", utc_now())
        self.frontier_dir.mkdir(parents=True, exist_ok=True)
        with (self.frontier_dir / "learning-ledger.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        return f"ledger: appended {row['finding_id']} ({row['kind']} -> {row['destination']}, {row['mode']})"

    def ledger_list(self, by: str) -> str:
        path = self.frontier_dir / "learning-ledger.jsonl"
        rows = []
        if path.is_file():
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
        groups: dict[str, list[dict]] = {}
        for row in rows:
            groups.setdefault(str(row.get(by, "?")), []).append(row)
        lines = [f"learning ledger: {len(rows)} rows by {by}"]
        for key in sorted(groups):
            items = groups[key]
            flag = ""
            if by == "destination" and len(items) > 1:
                flag = "  <- repeat: the same destination learned twice; make it a failing check"
            lines.append(f"  {key}: {len(items)} ({', '.join(str(r.get('finding_id')) for r in items)}){flag}")
        return "\n".join(lines)


def build_parser() -> Parser:
    ap = Parser(prog="frontier.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="repository root (default: git top level or cwd)")
    ap.add_argument("--plan-id", default=os.environ.get("PLAN_ID") or DEFAULT_PLAN_ID)
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("plan", "next"):
        p = sub.add_parser(name)
        p.add_argument("--graph", help="tracker graph JSON when ticket-ledger.json (CT-05) is absent")
        p.add_argument("--admitted", action="append", default=[], help="ticket whose heavy run the user admitted now")
        p.add_argument("--json", action="store_true")
        if name == "plan":
            p.add_argument("--write", action="store_true", help="write frontier/plan-<utc>.json")
        else:
            p.add_argument("--journal", help="CT-19 receipt journal of the unit (escalation rule)")
    p = sub.add_parser("claim")
    p.add_argument("unit")
    p.add_argument("--ticket", required=True)
    p.add_argument("--role", default="implementer")
    p.add_argument("--owned-paths", default="", help="comma-separated proposal from the scheduler")
    p.add_argument("--class", dest="klass")
    p = sub.add_parser("release")
    p.add_argument("unit")
    p.add_argument("--from-journal")
    p.add_argument("--resume", action="store_true")
    p = sub.add_parser("status")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("answer")
    p.add_argument("--question", required=True)
    p.add_argument("--answer", required=True)
    p = sub.add_parser("executor-gate")
    p.add_argument("--executor", help="override frontier.toml executor for this evaluation")
    p.add_argument("--team", action="store_true", help="evaluate G7 (allow_subagents=true)")
    p.add_argument("--config", help="probe config JSON (default frontier/executor-gate.config.json)")
    p.add_argument("--write", action="store_true")
    p = sub.add_parser("ledger")
    p.add_argument("action", choices=["append", "list"])
    p.add_argument("--row", help="JSON object for append")
    p.add_argument("--by", default="destination", choices=["destination", "ticket", "kind", "mode"])
    return ap


def resolve_repo(arg: str | None) -> Path:
    if arg:
        return Path(arg).resolve()
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except OSError:
        pass
    return Path.cwd()


def run(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    frontier = Frontier(resolve_repo(args.repo), args.plan_id)
    if args.command == "plan":
        plan = frontier.plan(args.graph, args.admitted)
        if args.write:
            frontier.frontier_dir.mkdir(parents=True, exist_ok=True)
            name = f"plan-{plan['ts'].replace(':', '').replace('-', '')}.json"
            (frontier.frontier_dir / name).write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8")
            plan["receipt"] = f"frontier/{name}"
        print(json.dumps(plan, indent=1) if args.json else format_plan(plan))
        return 0
    if args.command == "next":
        nxt = frontier.next_lane(args.graph, args.admitted, args.journal)
        print(json.dumps(nxt, indent=1) if args.json else format_next(nxt))
        return 0
    if args.command == "claim":
        paths = [p.strip() for p in args.owned_paths.split(",") if p.strip()]
        print(frontier.claim(args.unit, args.ticket, args.role, paths, args.klass))
        return 0
    if args.command == "release":
        print(frontier.release(args.unit, args.from_journal, args.resume))
        return 0
    if args.command == "answer":
        print(frontier.answer(args.question, args.answer))
        return 0
    if args.command == "status":
        status = frontier.status()
        print(json.dumps(status, indent=1) if args.json else frontier.format_status(status))
        return 0
    if args.command == "executor-gate":
        rc, text = frontier.executor_gate(args.executor or frontier.config.get("executor", "native"), args.team,
                                          args.config, args.write)
        print(text)
        return rc
    if args.command == "ledger":
        if args.action == "append":
            if not args.row:
                raise UsageError("ledger append needs --row '<json>'")
            print(frontier.ledger_append(args.row))
        else:
            print(frontier.ledger_list(args.by))
        return 0
    raise UsageError(f"unknown command {args.command}")


def format_plan(plan: dict) -> str:
    lines = [(f"frontier plan {plan['ts']} from {plan['graph_source']}; ceiling {plan['thresholds']['ceiling']} "
             f"({plan['thresholds']['model']})"),
             "ready (critical_path, unblocks, class): " + (", ".join(
                 f"{t['id']}({t['critical_path']},{t['unblocks']},{t['class'] or '-'})" for t in plan["ready"]) or "none")]
    cap = plan["capacity"]
    lines.append(f"capacity: writers {cap['writers_active']}/{cap['max_parallel']}, live {cap['live_agents']}/"
                 f"{cap['max_live_agents']} -> {cap['state']}")
    if plan["cxx_slot"]:
        lines.append(f"cxx slot: {plan['cxx_slot']['note']}")
    for lane in plan["chosen"]:
        lines.append(f"  dispatch {lane['unit']}: {lane['ticket']} as {lane['role']} ({lane['rule']}"
                     f"{', ' + lane['split'] if lane['split'] else ''})")
    for c in plan["conflicts"]:
        lines.append(f"  conflict {c['ticket']} with {c['with']}: {', '.join(c['paths'])}")
    for s in plan["skipped"]:
        lines.append(f"  skipped {s['ticket']}: {s['reason']}")
    for unit, cont in plan["continuations"].items():
        lines.append(f"  continuation pending: {unit} ({cont['ticket']}) split-required at {cont['last_usage']}; claim {unit}-2")
    if plan["capacity"]["state"] == "open" and len(plan["chosen"]) < plan["capacity"]["writers_free"]:
        lines.append(f"  unfilled: {plan['capacity']['writers_free'] - len(plan['chosen'])} writer slot(s) stay empty; "
                     "see skipped/conflicts above; an admission or a scheduler split fills one")
    for q in plan["questions"]:
        lines.append(f"  ask the user: {q}")
    for ticket, info in plan["degraded"].items():
        lines.append(f"  not available yet: {ticket} ({info['artifact']}) -> {info['fallback']}")
    if plan.get("receipt"):
        lines.append(f"receipt: {plan['receipt']}")
    return "\n".join(lines)


def format_next(nxt: dict) -> str:
    lines = [(f"next: {nxt['unit']} <- {nxt['ticket']} as {nxt['role']} on {nxt['model']}/{nxt['effort']} "
             f"(rule {nxt['rule']}), ceiling {nxt['ceiling']}")]
    lines += [f"  brief: {line}" for line in nxt["brief_lines"]]
    lines.append(f"  brief source: {nxt['brief_source']}")
    lines.append("  Agent call: " + json.dumps({k: v for k, v in nxt["dispatch"].items() if k != "prompt"}))
    lines += [f"  then: {step}" for step in nxt["then"]]
    lines += [f"  ask the user: {q}" for q in nxt["questions"]]
    return "\n".join(lines)


def main() -> int:
    try:
        return run(sys.argv[1:])
    except UsageError as exc:
        print(exc, file=sys.stderr)
        return 1
    except Refusal as exc:
        print(f"REFUSED: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())

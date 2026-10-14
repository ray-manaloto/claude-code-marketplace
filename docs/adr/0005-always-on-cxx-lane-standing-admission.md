# 5. One C++ lane always runs, under a standing heavy-run admission

Date: 2026-10-14

## Status

Accepted (user, grill-with-docs rounds 1 and 2; plan decisions D65, D68, D69, D70 and D78;
supersedes D46 and D32's by-hand rule; order in plan Phase 4b, D82, now the third
reprioritization). The disk gate is amended by D84: the larger of 60 GiB and 1.5 times the largest
peak measured for the same run class. D109 moves the host-wide heavy lock into this repository.

## Context

The accepted product is a native C++26 P2996 research core, but the parallel lanes kept filling
with process tickets while the C++ chain waited: D46 exempted wave 0 from the always-active C++
rule, every heavy run needed a per-run question, and the scheduler emptied the C++ slot silently
on a path conflict
(`.planning/<PLAN_ID>/reviews/ccm-20261014/reprioritize/R1-cxx-lane-supply.md`). Without heavy
runs, only four small split units could fill the slot before it ran dry.

## Decision

Of the three parallel lanes, one is always a C++ lane, from wave 0 on. Heavy C++ runs proceed
under a standing admission: one at a time, in the D5 order, only while free disk stays above a
gate (60 GiB, then 1.5 times the first run's measured peak), with a notice per run instead of a
question. A second concurrent heavy run still needs its own admission. When the gate blocks a heavy
run, a split unit fills the slot. The scheduler reads one merged graph of the takeover spec, the
native foundation spec and the LLVM chain, and never leaves the slot empty without saying so.

## Consequences

Disk becomes a scheduling input, so cleanup is part of keeping the C++ lane alive. The admission
rule in the team guide changes from "confirm each heavy run" to "record each heavy run". The
offline corpus crawl adapts to free disk and pauses before the heavy-run floor (D107).

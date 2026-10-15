# 8. One C++ library, with thin Python and TypeScript bridges

Date: 2026-10-14

## Status

Accepted (user, Q84, Q85, Q103 and Q104; plan decisions D112, D113, D130 and D131). Amends ADR
0007 in part: mods are thin and call the core through the bridge, and the three deny gates stay
settings hooks (D102).

## Context

The accepted product is a native C++26 P2996 research core (`docs/accepted-decisions.md`), yet the
helpers, the dev package (D60) and the planned mods library kept growing as Python and TypeScript
logic that a later migration would have to replace. The user set the primary goal: one modern C++
library, with the other languages reduced to bridges.

The bridge research (`.planning/<PLAN_ID>/reviews/ccm-20261014/research5/R9-cxx-bridges.md`) found
that a TypeScript mod cannot load native code. The route open to a mod is `$.process.run`, which
starts a program from an argv with no shell, so the core has to be a process a mod can start.
Python can start the same process with `subprocess`; an in-process Python module needs a measured
prototype first.

## Decision

- One C++26 library holds the logic and uses P2996 static reflection wherever it fits (D112).
- Python and TypeScript that remain are thin bridges: a bridge parses its input, calls the core
  and relays its JSON. No new Python logic is written, and Claude mods are built on the bridge
  (D112).
- Existing Python takes bug fixes, tests and deletions only until its C++ replacement lands; a new
  module, feature or tool goes into the C++ library with a bridge (D113).
- The bridge is one native CLI, working name `rsm-core`: a JSON request on stdin, the result on
  stdout, message shapes from the D83 schemas. TypeScript mods call it through `$.process.run` and
  Python through `subprocess`. A C ABI is added only when a measurement needs in-process calls
  (D130).
- The three deny gates port to C++ once the `rsm-core` skeleton builds, with a bootstrap path so an
  unbuilt binary cannot block the build that makes it (D131).

## Consequences

The unstarted Python and TypeScript tickets and the A2 units are re-scoped into C++ core units plus
thin bridge units (D114). The D60 package keeps its form as a bridge (D130), and w0-doctor merges
as reviewed with a later ticket that ports it (D115). A reviewer reports new Python or TypeScript
logic outside a bridge as a P1 finding (`CODING_STANDARDS.md`). The ported gates stay settings
hooks (D102), so a mod outage cannot disable them; `docs/agents/hooks-and-mods.md` holds the
mod-side rules.

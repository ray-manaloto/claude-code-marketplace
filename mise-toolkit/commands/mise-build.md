---
description: Build the jdx/mise Rust binary via the mise task
---

Run `mise run build` and report compilation errors. The resulting binary is at `target/debug/mise`.

If the build fails on a missing tool (e.g., `cargo` not on PATH), suggest running `mise install` first — the repo's own `mise.toml` declares the toolchain.

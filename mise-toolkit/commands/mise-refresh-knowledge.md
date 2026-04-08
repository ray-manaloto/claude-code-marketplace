---
description: Refresh the local mise llms.txt knowledge cache from mise.jdx.dev
---

Refresh the mise-toolkit knowledge cache so all skills cite the most current mise documentation.

Run these commands:

```bash
mkdir -p ~/.cache/mise-toolkit
curl -fsSL https://mise.jdx.dev/llms.txt -o ~/.cache/mise-toolkit/llms.txt
ls -la ~/.cache/mise-toolkit/llms.txt
```

If the curl fails (offline, network error, 404), seed the cache from the vendored copy instead:

```bash
mkdir -p ~/.cache/mise-toolkit
cp "${CLAUDE_PLUGIN_ROOT}/data/llms.txt.seed" ~/.cache/mise-toolkit/llms.txt
```

After the cache is populated, report:

- The size of the cached file
- The first 5 lines (title + intro)
- A confirmation that skills can now `@`-import `~/.cache/mise-toolkit/llms.txt`

If `~/.cache/mise-toolkit/llms.txt` already exists, also show its age (`stat -f %m` on macOS or `stat -c %Y` on Linux) and ask whether to overwrite — fresh-but-not-stale caches are fine.

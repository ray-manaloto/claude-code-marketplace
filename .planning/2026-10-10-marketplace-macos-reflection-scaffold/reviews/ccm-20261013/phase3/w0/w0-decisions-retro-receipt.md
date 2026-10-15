# w0-decisions retro receipt

Branch `claude/w0-decisions-ledger`, final SHA `922eab4` (repair on reviewed `f9c8848`).
Record: `P/retros/w0-decisions.md`; every review P3 has a disposition.
Applied (lane): receipt `--path` stored relative to the ledger's checkout, outside paths refused rc 2 (red first, 2 of 5 failing, then green); module docstring states rc convention (brief :13 = C2 section E) and the single-writer DL-id assumption (deferred, owner CT-11/CT-24); retro title em-dash removed.
Proposed (parent, literal in the record's "Parent edits"): D46 row in `task_plan.md`; receipt's mise hunk; `dev/AGENTS.md` bullets (exit codes; `-- argv` vs `usage` variadics); `CODING_STANDARDS.md` rule 14 (dash punctuation; a gate rule would fail 36 of 46 corpus records); `issue-tracker.md` ledger sentence (wave-1 CT-24).
Exits (VIRTUAL_ENV unset): unittest rc 0 (5 tests); `retro_gate.py` rc 0; `retro:gate` rc 0; `check` rc 0; tasks validate 0; acceptance-baseline 0 (19); test:hooks 0; hk validate 0; diff --check 0. Module 83 non-blank lines (C4: 80).

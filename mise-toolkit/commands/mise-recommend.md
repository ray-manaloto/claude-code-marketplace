---
description: Ask 3-4 questions and recommend a personalized mise adoption path
---

Ask the user (using AskUserQuestion or simple text questions, whichever fits):

1. **What languages/tools does this project use?** (Node, Python, Go, Ruby, Java, Rust, C/C++, Terraform, multi-language, …)
2. **Where will you run mise?** (Native macOS/Linux, Docker, devcontainer/Codespaces, CI only, all of the above)
3. **Do you currently use any version manager?** (nvm, pyenv, asdf, direnv, volta, none)
4. **Are you the only dev or part of a team?** (Affects whether to commit `mise.lock` aggressively, set `min_version`, etc.)

Based on the answers, produce a tailored adoption plan:

- **Languages → tools list** (use `mise-integration-architect` agent to pick backends)
- **Deployment → install/setup commands** (host = `/mise-install`; Docker = `/mise-dockerfile` once v0.3 ships; devcontainer = `/mise-devcontainer` once v0.3 ships)
- **Existing version manager → migration path** (use `mise-migration-specialist` agent)
- **Solo vs team → lockfile + min_version recommendations**

End with 3 concrete next steps the user can take immediately, ordered by effort:

1. Try mise locally for this one project (10 min)
2. Migrate the team (1 hour)
3. Adopt mise across all your projects (ongoing)

Reference the relevant skills (`mise-overview`, `mise-deployment-models`, `mise-host-vs-mise-tools`, etc.) so the user can drill in.

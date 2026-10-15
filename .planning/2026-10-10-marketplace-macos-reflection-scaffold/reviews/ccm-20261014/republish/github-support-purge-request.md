<!-- Draft for the user to send at https://support.github.com/contact (D148); not sent by an agent. -->

Subject: Remove cached commits and a closed pull request after a history replacement

Repository: ray-manaloto/claude-code-marketplace (public)

I replaced the history of branch `codex/marketplace-native-onboarding` with a force push
because the old commits contained references to a private project that should not be public.
I also deleted branch `codex/research-feedback-retro`, whose commits are a subset of the old
history. Nothing in the old history is a credential; the request is about private content.

Please:
1. Delete pull request #109 (closed), whose head ref `refs/pull/109/head` still points at the old
   tip `21af5650b61df205ae7b91c4b6da89f9eb7e50ae`.
2. Purge the now-unreachable commits and any cached views of them. The old history is the 228
   commits in `6b5b092efa6bdf678815073db42f69fae3f07ab3..21af5650b61df205ae7b91c4b6da89f9eb7e50ae`
   (first commit `f5541b0bfae969130514fe92b5d269e2042ffafd`); the deleted branch tip was
   `6cca08b9529eeacaf8e3be379440b3bf27d184f8`, inside that range.

Current state: the branch now points at `959c56f61e4f6eede2a0fb66e4827b8657d56556` (built on
`main`), draft pull request #110 replaces #109, and no other pull request or branch contains the
old commits (pull requests #1, #3, #5-#8 and #10 were checked). One public fork exists,
`ekipo-user/ray-manalotos-claude-code-marketplace` (created 2026-04-25); its only branch, `main`
at `ac98d28`, predates the old history (first old commit dated 2026-10-10), but it shares the
fork network, so please purge the commits network-wide.

Thank you.

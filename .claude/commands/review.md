---
description: Review the current branch against AGENTS.md before opening a PR
---

Read AGENTS.md fully. You are reviewing work you did not write. Be critical.

Review every change on the current branch compared to `main` (`git diff main...HEAD` and `git log main..HEAD`). Don't modify any files. Report:

1. **Scope:** anything outside the current phase, or anything from a later phase built early
2. **Plan violations:** anything that contradicts AGENTS.md (architecture, stack, Section 13 conventions, Section 13a UI rules, Section 13b workflow)
3. **Tests:** missing tests for new code; any test that was weakened, skipped, deleted, or changed to match buggy behavior
4. **Guardrails and security:** secrets in code, unsafe SQL handling, overly broad permissions, missing limits
5. **Correctness:** bugs, unhandled errors, edge cases, race conditions
6. **Evals:** any risk of data leakage (dev-set data used for retrieval or prompts), unrecorded results, results without a commit hash
7. **AGENTS.md:** checkboxes and Decision Log updated to match what was done
8. **Commits:** messages clear and commits reasonably small

Rank findings by severity (must fix, should fix, nice to have) with file and line references. End with a verdict: ready for PR, or not yet.

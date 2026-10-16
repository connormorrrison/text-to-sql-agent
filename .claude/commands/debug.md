---
description: Root-cause a failure, then fix it with a regression test
---

Read AGENTS.md.

The problem: $ARGUMENTS

1. Reproduce the failure and show me the output.
2. Find the root cause before changing any code. Explain it in plain language: what's wrong, where, and why it happens.
3. Propose a fix and wait for my approval.
4. Write a test that fails because of this bug, confirm it fails, then apply the fix and confirm it passes.
5. Run the full test suite.
6. Never weaken, skip, or delete an existing test to make things pass.
7. Commit with a message describing the bug that was fixed. Never push.

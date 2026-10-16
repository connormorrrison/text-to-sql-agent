---
description: Phase 10, resume bullets, demo script, final audit (Day 10 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-10-wrap-up`.
3. If we're already on `phase-10-wrap-up`: continue.
4. If we're on any other branch, or the working tree has uncommitted changes: stop and tell me. Don't change anything.
5. Commit after each logical step with a short imperative message (e.g. "Add SQL validator"). Show me a summary of the diff before each commit.
6. Never push, merge, rebase, or force-push. I do that.

## Rules for this session
- Propose a plan first and wait for my approval before writing code.
- Stay inside this phase's scope. Don't build anything from later phases. If you think something from a later phase is needed now, ask.
- Never weaken, skip, or delete a test to make it pass. Fix the code, or explain why the test is wrong and ask.
- Find the root cause of any failure before changing code.
- Follow the Conventions (Section 13) and Development Workflow (Section 13b) in AGENTS.md.

## Scope
Read AGENTS.md and `docs/results.md`.
1. Write three resume bullets using the templates in Section 16, with our real numbers only. Give me two variants of each.
2. Write a 60 to 90 second demo video script: what to show, in what order, and what to say.
3. Final repo audit: TODOs, dead code, missing tests, README accuracy, CI status. List the issues. Don't fix anything without asking.

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 10 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

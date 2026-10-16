---
description: Phase 9, documentation and final numbers (Day 9 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-09-docs`.
3. If we're already on `phase-09-docs`: continue.
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
Read Sections 2, 6, and 15 of AGENTS.md.
- Final eval run with the strongest model on `dev_300`. Give me the cost estimate first and wait for approval.
- `README.md`: one-liner, demo link placeholder, video link placeholder, architecture diagram (Mermaid), ablation results table, quick start, how the evals work, guardrails summary, honesty notes (benchmark contamination, SQLite vs Postgres), and a "What didn't work" section drawn from our actual results and the decision log
- `docs/architecture.md`: design decisions and trade-offs
- Go through the Section 2 success criteria and list what's still unchecked

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 9 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

---
description: Phase 6, guardrails and failure analysis (Day 6 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-06-guardrails`.
3. If we're already on `phase-06-guardrails`: continue.
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
Read Sections 6 and 7 of AGENTS.md.
- Read-only Postgres role (as a SQL migration) and integration tests proving DROP, DELETE, UPDATE, and INSERT fail at the database level
- `guardrails/rate_limit.py` with tests
- Check that every row of the Guardrails table in Section 7 has a passing test. List any gaps and fill them.
- Failure analysis: categorize every failed question from the latest `full.yaml` run into the categories in Section 6. Write the breakdown, with 1 to 2 examples per category, into `docs/results.md`.
- `.github/workflows/eval.yml`: run `ci_smoke` on PRs and fail if accuracy drops below a threshold. Propose the threshold from current results and explain your reasoning.

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 6 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

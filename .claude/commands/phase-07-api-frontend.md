---
description: Phase 7, API and frontend (Day 7 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-07-api-frontend`.
3. If we're already on `phase-07-api-frontend`: continue.
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
Read Sections 9, 11, and 13a of AGENTS.md.

**Backend**
- `POST /query` and `GET /health` in FastAPI with Pydantic schemas and integration tests
- `scripts/load_demo_db.py`: load a demo database into local Postgres and build its indexes. Propose 2 to 3 public demo database options first and let me choose.

**Frontend**
- Vite + React + TypeScript in `frontend/`
- Follow Section 13a exactly: install the shadcn skill, run `shadcn init` with defaults, add components only through the shadcn CLI, no theme customization, never edit `src/components/ui/`
- App components: QueryInput, AgentSteps, SqlViewer, ResultsTable, ResultChart, each with loading, empty, and error states
- Typed API client in `src/api/client.ts`
- Unit tests in `frontend/tests/unit/` with Vitest and Testing Library
- Add frontend lint, typecheck, and tests to `ci.yml` and the Makefile

When done, give me the exact commands to run everything locally so I can try it in the browser.

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 7 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

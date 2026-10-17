---
description: Phase 1, backend foundation (Day 1 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-01-foundation`.
3. If we're already on `phase-01-foundation`: continue.
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
Set up only what Day 1 needs. No placeholder code for later phases.
- `backend/` as in Section 9: `pyproject.toml` (Python 3.12, FastAPI, Pydantic, sqlglot, psycopg, pgvector, boto3, pytest, ruff, mypy strict on `src/`), the `src/app` package skeleton, the `tests/` skeleton
- `backend/docker-compose.yml` with Postgres + pgvector
- `.gitignore` (include `backend/data/`, `.env`, `node_modules/`, `cdk.out/`, `__pycache__/`, `.venv/`)
- `Makefile` with: `install`, `lint`, `typecheck`, `test`, `db-up`, `db-down`
- `.pre-commit-config.yaml` with ruff, mypy, and gitleaks (secret scanning). Tell me the command to install the hooks.
- `.github/workflows/ci.yml` running ruff, mypy, and pytest for the backend
- `backend/scripts/download_bird.py`: downloads the BIRD dev set into `backend/data/bird/` and verifies the files
- `backend/.env.example` listing every environment variable with a comment

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 1 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

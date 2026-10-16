---
description: Phase 2, baseline agent (Day 2 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-02-baseline-agent`.
3. If we're already on `phase-02-baseline-agent`: continue.
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
- `agent/llm.py`: Bedrock Converse API wrapper with tool calling; track tokens and cost per call
- `agent/loop.py`: hand-written think -> tool -> observe loop (no agent frameworks). Step limit and retry limit come from `config.py`. Returns a Pydantic final answer.
- `guardrails/sql_validator.py`: sqlglot check that the query is exactly one SELECT statement
- `db/executor.py`: statement timeout and row limit
- `agent/tools/run_query.py`
- Baseline mode: the full schema goes in the prompt
- Unit tests: agent loop with a fake LLM (no network calls), validator (rejects DROP, DELETE, UPDATE, INSERT, multi-statement), executor limits
- All tests must pass without AWS credentials

After the code works, run the agent on 5 BIRD dev questions against their SQLite databases and show me the SQL it produced and the results.

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 2 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

---
description: Phase 3, evaluation harness (Day 3 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-03-eval-harness`.
3. If we're already on `phase-03-eval-harness`: continue.
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
Read Section 6 of AGENTS.md carefully.
- `evals/scoring.py`: execution accuracy. Run gold and predicted SQL, compare result sets, order-insensitive unless the gold query has ORDER BY. Thorough unit tests, including NULLs, duplicates, float precision, and column order.
- `evals/run_eval.py`: takes a config YAML and a subset file. Records per question: correct, tokens, cost, latency, steps, retries, error type. Saves results to `evals/results/` with a timestamp, the config, and the git commit hash. Prints a summary.
- Parallel execution with a configurable concurrency limit
- `evals/subsets/dev_300.json` (stratified across databases, fixed random seed) and `evals/subsets/ci_smoke.json` (about 20 questions)
- `evals/configs/baseline.yaml`
- A `make eval` target that takes CONFIG and SUBSET arguments

Run baseline on `ci_smoke` and show me the summary. Then estimate the cost of running `dev_300`. Do not run `dev_300` until I approve the estimate.

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 3 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- The baseline row is filled in `docs/results.md` (create the file with the ablation table from Section 6).
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

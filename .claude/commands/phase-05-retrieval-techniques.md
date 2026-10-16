---
description: Phase 5, value lookup, retrieved examples, error correction (Day 5 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-05-retrieval-techniques`.
3. If we're already on `phase-05-retrieval-techniques`: continue.
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
Read Section 5 of AGENTS.md. Do these as three separate steps. After each step, run the eval (give me a cost estimate first) so each technique gets its own row in the ablation table.

1. **Value lookup:** `retrieval/value_index.py` and `agent/tools/sample_values.py`, config `value_lookup.yaml`
2. **Retrieved examples:** `retrieval/examples.py` using BIRD **training-set** question/SQL pairs only. Never use dev-set pairs (that would leak answers into the eval). Config `retrieved_examples.yaml`.
3. **Error correction:** retry on database errors, plus sanity checks on empty or implausible results, with the retry limit from config. Config `full.yaml`.

Add tests for each step. After each eval, tell me whether the technique helped, by how much, at what cost, and why you think so.

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 5 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- All ablation rows are filled in `docs/results.md`.
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

# Text-to-SQL Agent: Project Plan

This is the single source of truth for the project. Read it before making changes. If a decision changes, update this file and add an entry to the Decision Log at the bottom.

---

## 1. Overview

**One-liner:** Ask questions about a database in plain English and get correct answers, the SQL behind them, and a chart.

**What it is:** An AI agent that turns natural-language questions into SQL. It finds the relevant tables, looks at real data, writes a query, runs it safely, fixes its own errors, and explains the result.

**Why this project:** It is built to pass all three stages of a technical hiring review:

1. **Recruiter screen (10 to 30 seconds):** clear one-liner, in-demand keywords (Python, TypeScript, React, SQL, Postgres, REST APIs, AWS, Docker, CI/CD, testing, LLMs, agents, RAG), a live demo, and a real number.
2. **Engineer screen (1 to 3 minutes):** working demo, clear README, tests, CI/CD, infrastructure as code, clean commit history, one genuinely hard problem.
3. **Interview deep dive:** every part is solo-owned and explainable; decisions and trade-offs are documented; results are measured; failures are written up.

**Repo:** `Text-to-SQL-Agent`
**Display name:** Text-to-SQL Agent

---

## 2. Success Criteria

The project is done when all of these are true:

- [ ] Agent answers questions over a live demo database through a deployed web UI
- [ ] Execution accuracy measured on the BIRD dev set (or a fixed subset), with an ablation table showing what each technique added
- [ ] Average cost per question and average latency reported for each configuration
- [ ] Failure breakdown by category for the final configuration
- [ ] Guardrails implemented and covered by automated tests
- [ ] Backend, frontend, and infra all have automated tests running in CI
- [ ] Entire AWS stack defined in CDK and deployed from GitHub Actions on merge to `main`
- [ ] README with architecture diagram, results table, setup instructions, and a "What didn't work" section
- [ ] 60 to 90 second demo video
- [ ] Three resume bullets written from real numbers

---

## 3. Scope

### In scope (core)

- Single-turn natural-language questions over one database at a time
- Agent loop with tool calling (written by hand on the Bedrock API, no agent framework)
- Schema retrieval over pgvector
- Value lookup (map user wording like "California" to stored values like "CA")
- Retrieved few-shot examples (similar question/SQL pairs)
- Error-correction loop with a retry limit
- Result sanity checks (empty or implausible results trigger investigation)
- Guardrails: read-only DB role, SQL validation, timeouts, row limits, step limit, rate limiting
- Evaluation harness with execution accuracy, cost, latency, and ablations
- React UI: question input, live agent steps, SQL viewer, results table, chart
- AWS deployment with CDK, CI/CD with GitHub Actions

### Out of scope (only after the core is finished)

- Multi-turn conversation / follow-up questions
- User-uploaded databases
- Authentication beyond a simple demo gate
- Write queries of any kind
- Fine-tuning models
- Multi-agent setups
- Kubernetes

---

## 4. How It Works

### Request flow

1. User submits a question in the React UI.
2. Backend starts the agent loop.
3. Agent calls `search_schema` to find relevant tables and columns.
4. Agent calls `describe_table` and `sample_values` to learn column names, types, joins, and real value formats.
5. Agent drafts SQL and calls `run_query`.
6. If the database returns an error, the agent reads it, fixes the query, and retries (up to the retry limit).
7. If the result is empty or implausible, the agent investigates before answering.
8. Agent returns: a plain-English answer, the final SQL, the result rows, and an optional chart spec.
9. Every step (prompt, tool call, tool result, tokens, cost, latency) is logged.

### Agent tools

| Tool | Purpose |
|---|---|
| `search_schema(query)` | Semantic search over table and column descriptions (pgvector) |
| `describe_table(name)` | Columns, types, primary keys, foreign keys |
| `sample_values(table, column)` | Real example values from a column |
| `run_query(sql)` | Executes SQL through all guardrails |
| `make_chart(data, type)` | Returns a chart spec for the frontend |

### Agent loop rules

- Loop: think, call a tool, observe the result, repeat.
- Hard step limit per question (start at 10).
- Hard retry limit for failed queries (start at 3).
- The agent ends by returning a structured final answer (Pydantic model), never free text only.

---

## 5. The Hard Problem: Schema Linking

Real databases have many tables with cryptic names, and user wording rarely matches stored values. Pasting the full schema into the prompt is expensive, hits context limits, and lowers accuracy.

Techniques, implemented in this order and each measured separately:

1. **Schema retrieval (RAG):** generate a short description for every table and column, embed them, store in Postgres with pgvector. At question time, retrieve the top-k tables plus anything connected by foreign keys.
2. **Value lookup:** index distinct values from text columns so user terms map to stored values.
3. **Retrieved examples:** store question/SQL pairs from the BIRD training set; retrieve the 3 most similar to each new question and include them in the prompt.
4. **Error correction:** feed DB errors and suspicious results back to the model for another attempt.

---

## 6. Evaluation

### Benchmark

- **BIRD dev set** (about 1,500 questions over 11 databases, SQLite format). Chosen over Spider because strong models already score very high on Spider, so improvements would not show.
- Use a **fixed subset** (start with 300 questions, stratified across databases) for iteration. Run the full dev set for final numbers if budget allows.
- A **CI smoke subset** of about 20 questions runs on every PR.

### Metric

- **Execution accuracy:** run the gold SQL and the predicted SQL, compare result sets (order-insensitive unless the gold query has `ORDER BY`). Never compare SQL text.
- Also record per question: correctness, tokens in/out, cost, latency, number of agent steps, number of retries, error type.

### Ablation table (the main result)

| Configuration | Execution accuracy | Avg cost / question | Avg latency | Avg steps |
|---|---|---|---|---|
| Baseline: full schema in prompt | | | | |
| + Schema retrieval | | | | |
| + Value lookup | | | | |
| + Retrieved examples | | | | |
| + Error correction (full) | | | | |

Each configuration is a YAML file in `backend/evals/configs/`. Results are saved to `backend/evals/results/` with a timestamp, the config, and the git commit hash.

### Failure analysis

For the final configuration, categorize failures: wrong table, wrong join, wrong filter/value, wrong aggregation, misread question, gold answer questionable, other.

### Honesty notes (include in README)

- BIRD is public; models may have seen some questions during training.
- Evals run on SQLite; the demo runs on Postgres. Note dialect differences.

### Cost control

- Use a smaller, cheaper model during development; use the strong model for final runs.
- Cache embeddings and schema descriptions; never regenerate them per run.

---

## 7. Guardrails

Principle: **real protection comes from database permissions, not prompt instructions.**

| Guardrail | Implementation | Test |
|---|---|---|
| Read-only access | Dedicated Postgres role with `SELECT` only | `DROP`, `DELETE`, `UPDATE`, `INSERT` all fail at the DB level |
| SQL validation | `sqlglot` parse: exactly one statement, must be `SELECT` | Multi-statement and non-SELECT queries are rejected before execution |
| Query timeout | Postgres `statement_timeout` (start at 5s) | A deliberately slow query is cancelled |
| Row limit | Enforced `LIMIT` on results (start at 1,000) | Large result sets are truncated |
| Step limit | Max agent iterations per question | Agent stops and returns a graceful failure |
| Retry limit | Max failed-query retries | Agent stops retrying after the limit |
| Rate limiting | Per-IP limit on the public API | Excess requests get HTTP 429 |
| Budget | AWS budget alert from day 1 | n/a |

---

## 8. Tech Stack

| Layer | Choice |
|---|---|
| Backend language | Python 3.12 |
| API | FastAPI, Pydantic |
| Lambda adapter | Mangum |
| LLM + embeddings | Amazon Bedrock (a Claude model for reasoning; Titan or Cohere embeddings) |
| Database (demo + indexes) | Postgres with pgvector (RDS in prod, Docker locally) |
| Database (evals) | SQLite (BIRD files) |
| SQL parsing | sqlglot |
| Backend quality | ruff, mypy, pytest, Testcontainers |
| Frontend | React, TypeScript, Vite |
| UI components | shadcn/ui, default setup, no customization (see Section 13a) |
| Styling | Tailwind CSS (installed by shadcn init) |
| Charts | shadcn Chart component (built on Recharts) |
| Frontend tests | Vitest, Testing Library, Playwright (e2e) |
| Infrastructure | AWS CDK (TypeScript) |
| AWS services | Lambda, API Gateway, RDS Postgres, S3, CloudFront, Bedrock, CloudWatch, Budgets |
| CI/CD | GitHub Actions |
| Local dev | Docker Compose, Makefile |

---

## 9. Project Structure

```
Text-to-SQL-Agent/
├── .claude/
│   ├── settings.json                 # project settings: AI attribution off
│   └── commands/                     # Claude Code slash commands (see Section 13b)
│       ├── phase-01-foundation.md    # ... through phase-10-wrap-up.md
│       ├── review.md
│       ├── debug.md
│       └── explain.md
├── .github/
│   └── workflows/
│       ├── ci.yml                    # lint, type-check, tests (backend + frontend + infra)
│       ├── eval.yml                  # CI smoke eval subset on PRs
│       └── deploy.yml                # CDK deploy on merge to main
│
├── backend/
│   ├── pyproject.toml                # deps, ruff, mypy, pytest config
│   ├── uv.lock                       # locked dependency versions (uv)
│   ├── .python-version               # Python 3.12 pin (uv)
│   ├── .venv/                        # gitignored: local virtualenv (uv)
│   ├── Dockerfile
│   ├── docker-compose.yml            # local Postgres + pgvector
│   ├── docker/
│   │   └── postgres/init.sql         # enables the vector extension on first start
│   ├── data/                         # gitignored: BIRD downloads, local DBs
│   ├── .env.example
│   ├── src/
│   │   └── app/
│   │       ├── main.py               # FastAPI app + Lambda handler
│   │       ├── config.py             # settings from env vars
│   │       ├── api/
│   │       │   ├── routes/
│   │       │   │   ├── query.py      # POST /query
│   │       │   │   └── health.py
│   │       │   └── schemas.py        # Pydantic request/response models
│   │       ├── agent/
│   │       │   ├── loop.py           # think -> tool -> observe loop, step limit
│   │       │   ├── prompts.py
│   │       │   ├── llm.py            # Bedrock client wrapper
│   │       │   └── tools/
│   │       │       ├── search_schema.py
│   │       │       ├── describe_table.py
│   │       │       ├── sample_values.py
│   │       │       ├── run_query.py
│   │       │       └── make_chart.py
│   │       ├── retrieval/
│   │       │   ├── embeddings.py     # Bedrock embeddings
│   │       │   ├── schema_index.py   # table/column descriptions -> pgvector
│   │       │   ├── value_index.py    # distinct values ("CA" <-> "California")
│   │       │   └── examples.py       # similar question/SQL pairs
│   │       ├── db/
│   │       │   ├── connection.py     # read-only connection pool
│   │       │   ├── executor.py       # timeout + row limit
│   │       │   └── dialects.py       # SQLite (evals) vs Postgres (demo)
│   │       ├── guardrails/
│   │       │   ├── sql_validator.py  # sqlglot: single SELECT only
│   │       │   └── rate_limit.py
│   │       └── observability/
│   │           ├── logging.py
│   │           └── tracing.py        # per-step logs, tokens, cost, latency
│   ├── evals/
│   │   ├── run_eval.py               # runs agent on benchmark questions
│   │   ├── scoring.py                # execution accuracy (compare result sets)
│   │   ├── configs/                  # one file per ablation
│   │   │   ├── baseline.yaml
│   │   │   ├── schema_retrieval.yaml
│   │   │   ├── value_lookup.yaml
│   │   │   ├── retrieved_examples.yaml
│   │   │   └── full.yaml
│   │   ├── subsets/
│   │   │   ├── ci_smoke.json         # ~20 questions for CI
│   │   │   └── dev_300.json          # fixed iteration subset
│   │   └── results/                  # versioned results + failure breakdowns
│   ├── scripts/
│   │   ├── download_bird.py
│   │   ├── load_demo_db.py
│   │   └── build_indexes.py
│   └── tests/
│       ├── conftest.py               # fixtures, Testcontainers Postgres
│       ├── unit/
│       │   ├── test_sql_validator.py
│       │   ├── test_executor.py
│       │   ├── test_scoring.py
│       │   ├── test_agent_loop.py    # with a fake LLM
│       │   └── tools/
│       │       └── test_run_query.py
│       ├── integration/
│       │   ├── test_api_query.py
│       │   ├── test_retrieval.py
│       │   └── test_readonly_role.py # DROP/DELETE must fail
│       └── fixtures/
│           └── sample.sqlite
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── components.json               # shadcn config (generated, default settings)
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css                 # Tailwind + shadcn default theme (do not customize)
│   │   ├── api/
│   │   │   └── client.ts             # typed calls to the backend
│   │   ├── lib/
│   │   │   └── utils.ts              # shadcn cn() helper (generated)
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn components (generated, do not edit)
│   │   │   ├── QueryInput.tsx
│   │   │   ├── AgentSteps.tsx        # shows each tool call as it happens
│   │   │   ├── SqlViewer.tsx
│   │   │   ├── ResultsTable.tsx
│   │   │   └── ResultChart.tsx
│   │   ├── hooks/
│   │   │   └── useQuery.ts
│   │   └── types/
│   │       └── api.ts
│   └── tests/
│       ├── setup.ts                  # Vitest + Testing Library setup
│       ├── unit/
│       │   ├── QueryInput.test.tsx
│       │   ├── ResultsTable.test.tsx
│       │   └── client.test.ts        # mocked API responses
│       └── e2e/
│           └── query-flow.spec.ts    # Playwright: ask -> answer -> chart
│
├── infra/
│   ├── package.json
│   ├── cdk.json
│   ├── bin/
│   │   └── app.ts
│   ├── lib/
│   │   ├── network-stack.ts          # VPC
│   │   ├── database-stack.ts         # RDS Postgres + pgvector
│   │   ├── api-stack.ts              # API Gateway + Lambda
│   │   ├── frontend-stack.ts         # S3 + CloudFront
│   │   └── monitoring-stack.ts       # CloudWatch, budget alert
│   └── test/
│       └── stacks.test.ts            # CDK assertion tests
│
├── docs/
│   ├── architecture.md               # diagram + design decisions
│   └── results.md                    # ablation table, failure analysis
│
├── .pre-commit-config.yaml           # ruff, mypy, frontend lint, gitleaks, commit-msg check
├── Makefile                          # make test, make eval, make deploy
├── AGENTS.md                         # this file (project plan + agent instructions)
├── .gitignore
└── README.md
```

---

## 10. AWS Architecture

```
Browser (React app)
   |
   v
CloudFront + S3            serves the frontend
   |
   v
API Gateway -> Lambda      FastAPI backend (Mangum), runs the agent loop
   |            |
   |            +--> Bedrock          LLM calls + embeddings
   |
   v
RDS Postgres + pgvector    demo database + schema/value/example indexes
   |
CloudWatch                 logs every agent step, cost, latency
```

- Everything is defined in CDK under `infra/`.
- If agent runs exceed Lambda or API Gateway time limits, move the backend to ECS Fargate and document the trade-off.
- Set an AWS budget alert before deploying anything.
- The public demo uses a relatable demo database (not a benchmark database) and has rate limiting.

---

## 11. Testing Strategy

### Backend (`backend/tests/`)

- **Unit:** SQL validator, executor limits, scoring logic, agent loop with a fake LLM, each tool.
- **Integration:** API endpoints, retrieval against a real Postgres (Testcontainers), read-only role enforcement.
- **Guardrail tests are mandatory:** every row in the Guardrails table has a test.

### Frontend (`frontend/tests/`)

- **Unit:** components render correctly for loading, success, empty, and error states; API client handles responses and errors.
- **E2E:** Playwright test for the full flow: ask a question, see agent steps, see SQL, see results and chart.

### Infra (`infra/test/`)

- CDK assertion tests: the database is not publicly accessible, the Lambda has only the permissions it needs, the budget alert exists.

### Evals (`backend/evals/`)

- Smoke subset runs in CI on every PR. Full runs are manual.

---

## 12. CI/CD

| Workflow | Trigger | Steps |
|---|---|---|
| `ci.yml` | Every push and PR | Backend: ruff, mypy, pytest. Frontend: lint, type-check, Vitest. Infra: CDK tests. |
| `eval.yml` | PRs | Run the CI smoke eval subset; fail if accuracy drops below a threshold |
| `deploy.yml` | Merge to `main` | Build backend, build frontend, `cdk deploy` |

Use GitHub OIDC to authenticate to AWS. Never store long-lived AWS keys in GitHub secrets.

---

## 13. Conventions

- **Commits:** small and frequent, imperative messages (`Add SQL validator`, `Fix row limit off-by-one`).
- **Branches:** short-lived feature branches merged to `main` via PR.
- **Python:** type hints everywhere, mypy strict on `src/`, ruff for lint and format.
- **TypeScript:** strict mode on.
- **UI:** shadcn/ui only, with default settings. See Section 13a.
- **Secrets:** never committed. Use `.env` locally (gitignored) and AWS Secrets Manager in prod.
- **Config:** all limits (steps, retries, timeout, row limit, top-k) live in `config.py` and eval YAMLs, never hard-coded.
- **Data:** BIRD downloads and local databases live in `backend/data/`, which is gitignored.

---

## 13a. Frontend UI Rules (shadcn/ui)

The frontend uses **shadcn/ui with its default settings and no customization.**

### Setup

1. Install the shadcn agent skill so coding agents follow shadcn patterns:
   ```bash
   npx skills add https://github.com/shadcn-ui/ui --skill shadcn
   ```
2. Create the Vite + React + TypeScript app in `frontend/`.
3. Initialize shadcn with default options:
   ```bash
   npx shadcn@latest init
   ```
   Accept the defaults. Do not pick a custom preset, base color, or theme.
4. Add components only through the CLI:
   ```bash
   npx shadcn@latest add button textarea card table badge skeleton alert chart
   ```

### Rules

- **Use stock shadcn components.** Build app components (`QueryInput`, `ResultsTable`, etc.) by composing components from `src/components/ui/`.
- **Do not edit files in `src/components/ui/`.** They are generated. If something is missing, compose around it.
- **Do not customize the theme.** Leave the CSS variables, colors, radius, and fonts in `index.css` exactly as `shadcn init` generated them.
- **Do not add other UI or component libraries** (no MUI, Chakra, Mantine, etc.).
- **Charts use the shadcn Chart component** (which wraps Recharts) with its default config.
- **Styling is limited to Tailwind layout and spacing utilities** (flex, grid, gap, padding, margin, width). No custom colors, no arbitrary values, no custom CSS files.
- **Use the package runner that matches the project's package manager** (`npx`, `pnpm dlx`, or `bunx`) for shadcn commands.

---

## 13b. Development Workflow (AI-Assisted)

These rules apply to every session, whether or not a slash command is used.

### Branches

- One branch per phase, created from an up-to-date `main`.
- Branch names match the phase commands: `phase-01-foundation`, `phase-02-baseline-agent`, `phase-03-eval-harness`, `phase-04-schema-retrieval`, `phase-05-retrieval-techniques`, `phase-06-guardrails`, `phase-07-api-frontend`, `phase-08-aws-deploy`, `phase-09-docs`, `phase-10-wrap-up`.
- Bug fixes outside a phase use `fix/<short-description>`.
- `main` is protected: changes arrive only through pull requests with passing CI.

### Commits

- Small, one logical change each, with imperative messages (`Add SQL validator`, `Fix row limit off-by-one`).
- Show a diff summary before each commit.
- Pre-commit hooks must pass. Never bypass them (`--no-verify` is not allowed).
- Commit messages and PR descriptions never mention Claude: no `Co-Authored-By` trailers, no "Generated with" footers. `.claude/settings.json` turns off attribution, and the `no-claude-in-commit-msg` hook (`backend/scripts/check_commit_msg.py`) rejects any commit message containing "claude". It ignores git comments, the diff added by `git commit -v`, and `.claude/` paths.

### What the agent must never do

- Push, merge, rebase, or force-push. The human does this.
- Run `cdk deploy` or any command that creates, changes, or deletes AWS resources.
- Run full eval sets without a cost estimate and human approval.
- Commit secrets, `.env` files, or anything in `backend/data/`.
- Mention Claude or add AI attribution in commit messages or PR descriptions.
- Weaken, skip, or delete a test to make it pass.
- Build features from a later phase without asking.
- Use dev-set benchmark data for retrieval, prompts, or few-shot examples.

### Each phase, step by step

1. Human updates `main` and starts a fresh Claude Code session.
2. Run the phase command (e.g. `/phase-02-baseline-agent`). The agent creates the branch if needed.
3. Agent proposes a plan; human approves or adjusts.
4. Agent implements in small commits; human reads each diff.
5. Agent confirms all checks pass and updates this file (checkboxes, Decision Log).
6. In a fresh session, run `/review`. Fix anything marked "must fix."
7. Human pushes the branch and opens a PR with the agent's draft description.
8. CI passes, then the human merges **without squashing** to keep the commit history.
9. For phases that produce eval numbers, tag the merge commit (e.g. `v0.3-baseline`, `v0.5-full`).

### Slash commands (`.claude/commands/`)

| Command | Use |
|---|---|
| `/phase-01-foundation` ... `/phase-10-wrap-up` | Run one phase of the schedule |
| `/review` | Critical review of the current branch against this file, before a PR |
| `/debug <problem>` | Root-cause a failure, then fix it with a regression test |
| `/explain <file or feature>` | Interview-prep explanation plus a 3-question quiz |

### Habits

- Read every diff. Don't merge code you can't explain.
- One phase, one branch, one fresh session. This file carries the memory between sessions.
- Root cause before fixes.
- Use `/explain` regularly on anything the agent wrote.

---

## 14. Schedule (10 Days)

### Day 1: Foundation

- [x] Create repo, add this file, `.gitignore`, `README.md` stub
- [x] Set up `backend/` with `pyproject.toml`, ruff, mypy, pytest
- [x] Set up `docker-compose.yml` with Postgres + pgvector
- [ ] `ci.yml` running backend lint and tests (tick after the first green CI run)
- [x] `.pre-commit-config.yaml` with ruff, mypy, gitleaks; hooks installed
- [ ] (Manual) Branch protection on `main`: require PR + passing CI, block direct and force pushes
- [x] Download BIRD dev set into `backend/data/`
- [ ] Set AWS budget alert, confirm Bedrock model access

**Done when:** CI is green and BIRD is downloaded.

### Day 2: Baseline agent

- [ ] Bedrock client wrapper (`llm.py`)
- [ ] Agent loop with step limit and a fake-LLM unit test
- [ ] `run_query` tool with SQL validator, timeout, and row limit (plus tests)
- [ ] Baseline config: full schema in prompt
- [ ] Agent answers 10 sample BIRD questions end to end

**Done when:** the agent produces SQL and answers for sample questions.

### Day 3: Evaluation harness

- [ ] `scoring.py` (execution accuracy) with unit tests
- [ ] `run_eval.py`: runs a subset, records accuracy, cost, latency, steps, retries
- [ ] Create `dev_300.json` and `ci_smoke.json`
- [ ] Run baseline on the 300 subset; save results

**Done when:** a baseline number exists.

### Day 4: Schema retrieval

- [ ] Generate table/column descriptions, embed, store in pgvector (`build_indexes.py`)
- [ ] `search_schema` and `describe_table` tools
- [ ] Foreign-key expansion of retrieved tables
- [ ] Eval run; record the delta

**Done when:** the schema retrieval row in the ablation table is filled.

### Day 5: Value lookup, examples, error correction

- [ ] `value_index.py` + `sample_values` tool; eval run
- [ ] `examples.py` (retrieved question/SQL pairs); eval run
- [ ] Error-correction loop with retry limit and result sanity checks; eval run

**Done when:** all ablation rows are filled.

### Day 6: Guardrails and failure analysis

- [ ] Read-only Postgres role + integration tests
- [ ] Rate limiting + tests
- [ ] Categorize failures for the full configuration; write into `docs/results.md`
- [ ] `eval.yml` smoke workflow with threshold

**Done when:** every guardrail has a passing test and the failure breakdown is written.

### Day 7: API and frontend

- [ ] FastAPI `POST /query` and `/health` with integration tests
- [ ] Load the demo database into Postgres (`load_demo_db.py`) and build its indexes
- [ ] Create the Vite + React + TypeScript app and run `npx shadcn@latest init` with default options
- [ ] Add the shadcn components needed (e.g. button, textarea, card, table, badge, skeleton, alert, chart) with `npx shadcn@latest add`
- [ ] React app: QueryInput, AgentSteps, SqlViewer, ResultsTable, ResultChart, built from stock shadcn components
- [ ] Frontend unit tests

**Done when:** the full flow works locally.

### Day 8: AWS deployment

- [ ] CDK stacks: network, database, API, frontend, monitoring
- [ ] CDK assertion tests
- [ ] `deploy.yml` with GitHub OIDC
- [ ] Deploy; verify the live demo works
- [ ] Playwright e2e test against local or staging

**Done when:** a public URL works and deploys run from `main`.

### Day 9: Documentation

- [ ] README: one-liner, demo link, video link, architecture diagram, results table, setup instructions, "What didn't work"
- [ ] `docs/architecture.md`: design decisions and trade-offs
- [ ] Final eval run with the strong model; update results

**Done when:** someone could understand and run the project from the README alone.

### Day 10: Demo and resume

- [ ] Record a 60 to 90 second demo video
- [ ] Write three resume bullets from real numbers
- [ ] Final pass: clean up TODOs, confirm CI is green, confirm the demo is up

**Done when:** every item in Section 2 is checked.

---

## 15. Deliverables

- Live demo URL
- Demo video (60 to 90 seconds)
- README with results
- `docs/results.md` with the ablation table and failure analysis
- `docs/architecture.md` with design decisions
- Three resume bullets

---

## 16. Resume Bullet Templates

Fill in with real numbers only.

- Built a natural-language analytics agent that turns plain-English questions into SQL, deployed on AWS (Lambda, RDS Postgres, Bedrock) with CDK and CI/CD via GitHub Actions.
- Improved execution accuracy on the BIRD benchmark from X% to Y% using schema retrieval over pgvector, value lookup, retrieved examples, and an error-correction loop; documented the cost and latency of each technique.
- Implemented layered safety (read-only database role, SQL validation, timeouts, rate limiting) covered by N automated tests across backend, frontend, and infrastructure.

---

## 17. Interview Prep: Questions to Be Ready For

- Why not put the whole schema in the prompt? (Use the ablation table.)
- Why does error correction help, and what does it cost?
- How do you stop the agent from modifying data? (Permissions first, parser second, prompt last.)
- What still fails, and why? (Use the failure breakdown.)
- How would this scale to 10,000 tables? (Hierarchical retrieval, caching, smaller models for easy steps.)
- Why Lambda instead of ECS (or vice versa)?
- Why pgvector instead of a dedicated vector database?
- How do you know the benchmark numbers are trustworthy? (Execution accuracy, fixed subsets, contamination caveat.)
- What would you do with another month?

---

## 18. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Eval runs get expensive | Cheaper model during development; fixed 300-question subset; cache embeddings |
| SQLite vs Postgres dialect differences | Dialect setting in `dialects.py`; document in README |
| Agent runs exceed Lambda/API Gateway time limits | Measure early on Day 8; switch to ECS Fargate if needed |
| Public demo abuse or surprise AWS bill | Rate limiting, step limits, budget alert |
| Scope creep | Out-of-scope list in Section 3; finish core first |
| Running out of time | Core order is fixed: eval harness and ablations matter more than UI polish |

---

## 19. Decision Log

Record every significant decision here with the date and reason.

| Date | Decision | Reason |
|---|---|---|
| | Text-to-SQL agent chosen as the project | Meets all recruiter criteria; public answer key (BIRD) makes measurement cheap |
| | BIRD over Spider | Spider is near-saturated; BIRD leaves room to show improvement |
| | Hand-written agent loop, no framework | Must be able to explain every step in interviews |
| | pgvector over a managed vector database | Cheaper; Postgres already needed; avoids OpenSearch Serverless minimum cost |
| | Execution accuracy as the metric | Different SQL can produce the same correct result |
| | CDK in TypeScript | Infrastructure as code; frontend already uses TypeScript |
| | shadcn/ui with default settings, no customization | Fast, consistent, accessible UI; time goes to the agent and evals, not design |
| | Plan file named AGENTS.md | Read by Claude Code (fallback when no CLAUDE.md exists) and by other coding agents |
| 2026-10-16 | uv for Python version, venv, and lockfile (`backend/uv.lock`) | One tool pins Python 3.12 and gives reproducible installs; CI uses the same lockfile via `uv sync --locked` |
| 2026-10-16 | pydantic-settings for `config.py` | Typed, validated env-var config; same Pydantic models already used by FastAPI |
| 2026-10-16 | `pgvector/pgvector:pg16` image locally, extension created by `backend/docker/postgres/init.sql` | Official pgvector image; Postgres 16 is supported by RDS, so local matches prod |
| 2026-10-16 | mypy pre-commit hook runs from the uv env (`repo: local`) instead of mirrors-mypy | The mirror runs in an isolated env without project deps, so strict mode would report false errors |
| 2026-10-16 | mypy strict also covers `backend/scripts/` | Scripts handle downloads and data; same bar as `src/` costs nothing |
| 2026-10-16 | BIRD dev archive verified against a pinned SHA-256, extracted to `backend/data/bird/dev/` | SHA-256 catches both corrupt downloads and deliberately altered files (MD5 collisions are practical, so MD5 only catches accidents); flattening the dated archive folder keeps paths stable |
| 2026-10-16 | No AI attribution in commits or PRs; enforced by settings and a `commit-msg` hook | Commit history is part of the portfolio and must be solely authored; a hook catches what a setting alone would miss |
| 2026-10-16 | Backend-only files live in `backend/` (`docker-compose.yml`, `docker/`, `data/`, `uv.lock`, `.python-version`, `.venv/`) | Backend-only files live in backend/ to keep the root limited to repo-wide tooling |
| 2026-10-16 | GitHub Actions pinned to full commit SHAs, version in a trailing comment | Tags can be moved or deleted (setup-uv has no `v10` tag at all); a SHA always resolves to the same reviewed code |
| 2026-10-16 | pre-commit is a backend dev dependency, run with `uv run --project backend` | Pins the hook runner in `uv.lock` instead of relying on whatever global version is installed (a global 2.21 was in use) |
| 2026-10-16 | Commit-msg check is a tested Python script instead of a `pygrep` regex | A one-line regex cannot stop at the `git commit -v` scissors line or allow `.claude/` paths, and had no tests |

---

## 20. Open Questions

- Which demo database to use for the public site?
- Final choice of reasoning model and embedding model on Bedrock (compare cost and accuracy on Day 3).
- Lambda or ECS Fargate for the backend (decide on Day 8 after measuring run times).
- Streaming agent steps to the UI (Server-Sent Events) or returning everything at the end?

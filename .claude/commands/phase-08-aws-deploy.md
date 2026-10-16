---
description: Phase 8, AWS deployment (Day 8 in AGENTS.md)
---

Read AGENTS.md fully before doing anything.

## Git
1. Run `git status` and `git branch --show-current`.
2. If we're on `main` with a clean working tree: run `git pull`, then `git checkout -b phase-08-aws-deploy`.
3. If we're already on `phase-08-aws-deploy`: continue.
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
Read Sections 10 and 12 of AGENTS.md.

Your plan must include: an estimate of monthly cost while idle, and a list of every step I must do manually (console clicks, secrets, approvals).

- `infra/` CDK app in TypeScript with the stacks listed in Section 9
- RDS must not be publicly accessible. Lambda gets least-privilege IAM. Secrets go in Secrets Manager.
- Budget alert in `monitoring-stack`
- CDK assertion tests in `infra/test/`: database not public, IAM scoped, budget exists
- `.github/workflows/deploy.yml` using GitHub OIDC (no long-lived AWS keys), including the CDK construct for the OIDC role
- Measure a typical and a slow agent run against Lambda and API Gateway time limits. Tell me whether we need ECS Fargate instead and why.
- Playwright e2e test in `frontend/tests/e2e/query-flow.spec.ts`

Never run `cdk deploy` or any command that creates AWS resources. Give me the commands and I'll run them.

## Done when
- All checks pass: `make lint`, `make typecheck`, `make test` (and frontend/infra checks once they exist). Show me the output.
- The Day 8 checkboxes in AGENTS.md are checked.
- Any design decisions are recorded in the AGENTS.md Decision Log.
- Infra tests pass and `cdk synth` succeeds.
- Give me a draft PR description: what changed, test results, eval numbers if any, and anything I should review closely.

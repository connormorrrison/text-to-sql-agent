BACKEND := backend
UV := uv run --directory $(BACKEND)
# pre-commit reads .pre-commit-config.yaml from the repo root, so use --project, not --directory.
PRE_COMMIT := uv run --project $(BACKEND) pre-commit

.PHONY: install lint format typecheck test db-up db-down

install: ## Install backend dependencies and git hooks
	uv sync --directory $(BACKEND) --locked
	$(PRE_COMMIT) install

lint: ## Lint and check formatting
	$(UV) ruff check .
	$(UV) ruff format --check .

format: ## Auto-fix lint issues and format
	$(UV) ruff check --fix .
	$(UV) ruff format .

typecheck: ## mypy strict on src/
	$(UV) mypy

test: ## Run backend tests
	$(UV) pytest

db-up: ## Start local Postgres + pgvector and wait until healthy
	docker compose -f $(BACKEND)/docker-compose.yml up -d --wait postgres

db-down: ## Stop local Postgres (data volume is kept)
	docker compose -f $(BACKEND)/docker-compose.yml down

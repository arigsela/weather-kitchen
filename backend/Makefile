.PHONY: help install dev test test-unit test-integration test-security lint format seed migrate purge clean

help:
	@echo "Weather Kitchen Backend - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install       Install dependencies with uv"
	@echo "  make dev           Start FastAPI dev server with auto-reload (http://localhost:8000)"
	@echo "  make shell         Open Python shell with app context"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests (unit + integration + security)"
	@echo "  make test-unit     Run unit tests only"
	@echo "  make test-int      Run integration tests only"
	@echo "  make test-sec      Run security tests only"
	@echo "  make test-perf     Run performance benchmarks"
	@echo "  make coverage      Generate coverage report (opens htmlcov/index.html)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run Ruff linter (no fixes)"
	@echo "  make format        Format code with Ruff"
	@echo "  make security      Run Bandit security scan"
	@echo ""
	@echo "Database:"
	@echo "  make migrate       Run Alembic migrations (upgrade head)"
	@echo "  make migrate-down  Downgrade one migration"
	@echo "  make migrate-new   Create new migration (message required)"
	@echo "  make seed          Seed 1,020 recipes into database"
	@echo "  make reset-db      Drop all tables and recreate (DESTRUCTIVE)"
	@echo "  make purge         Hard-delete soft-deleted families (30+ days old)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-run    Run Docker container (http://localhost:8000)"
	@echo ""

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

shell:
	uv run python -i -c "from app.main import app; print('App loaded. Use: app')"

test:
	uv run pytest tests/ -v --tb=short

test-unit:
	uv run pytest tests/unit/ -v --tb=short

test-int:
	uv run pytest tests/integration/ -v --tb=short

test-sec:
	uv run pytest tests/security/ -v --tb=short

test-perf:
	uv run pytest tests/performance/test_benchmarks.py -v --benchmark-only

coverage:
	uv run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"
	@open htmlcov/index.html || echo "Open htmlcov/index.html manually"

lint:
	uv run ruff check app/ tests/ --select=E,F,W,I,N,UP,S

format:
	uv run ruff format app/ tests/
	uv run ruff check app/ tests/ --fix

security:
	uv run bandit -r app/ -f json -o bandit-report.json
	@echo "Bandit report: bandit-report.json"

migrate:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

migrate-new:
	@if [ -z "$(message)" ]; then \
		echo "Usage: make migrate-new message='your message here'"; \
		exit 1; \
	fi
	uv run alembic revision --autogenerate -m "$(message)"

seed:
	uv run python -m app.seed.seed_recipes

reset-db:
	rm -f weather_kitchen.db
	uv run alembic upgrade head
	uv run python -m app.seed.seed_recipes
	@echo "Database reset and seeded with 1,020 recipes"

purge:
	uv run python -m app.tasks.purge

docker-build:
	docker build -f Dockerfile -t weather-kitchen-api:latest .

docker-run:
	docker run -p 8000:8000 -e DATABASE_URL="sqlite:////tmp/weather_kitchen.db" weather-kitchen-api:latest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache .coverage htmlcov/ dist/ build/ *.egg-info bandit-report.json
	@echo "Cleaned up build artifacts"

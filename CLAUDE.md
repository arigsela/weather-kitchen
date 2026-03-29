# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Weather Kitchen** is a production-grade recipe discovery API for children aged 6-12, suggesting weather-appropriate meals with ingredient filtering, favorites, multi-user support, and COPPA/GDPR compliance.

**Status**: Backend implemented (Phases 1-4 complete). Frontend not yet started (no `frontend/` directory).

**Key docs**: PRD (`docs/weather_kitcne_prd.md`), Backend Plan (`docs/BACKEND_IMPLEMENTATION_PLAN.md`), Frontend Plan (`docs/FRONTEND_IMPLEMENTATION_PLAN.md`)

## Tech Stack (Backend Only)

- **Framework**: FastAPI 0.129+ with Pydantic 2.x validation
- **Database**: SQLite (dev) / PostgreSQL (prod) via SQLAlchemy 2.0
- **Auth**: JWT (PyJWT) — 15-min access tokens + 7-day refresh tokens (HS256)
- **PIN hashing**: bcrypt 5.0 directly (not passlib)
- **Migrations**: Alembic
- **Package manager**: uv
- **Linting**: Ruff (E, F, W, I, N, UP, S rules)
- **Security scan**: Bandit
- **Testing**: pytest + httpx (TestClient)
- **Python**: 3.12

## Common Commands

All commands run from `backend/`:

```bash
uv sync                      # Install dependencies
make dev                     # Start dev server (localhost:8000, auto-reload)
make test                    # Run all tests (unit + integration + security)
make test-unit               # Unit tests only
make test-int                # Integration tests only
make test-sec                # Security tests only
make coverage                # Coverage report (opens htmlcov/)
make lint                    # Ruff lint check
make format                  # Ruff format + autofix
make security                # Bandit security scan
make migrate                 # Alembic upgrade head
make seed                    # Seed 1,020 recipes
make reset-db                # Drop DB, migrate, reseed (DESTRUCTIVE)
make migrate-new message='x' # Create new Alembic migration
```

Run a single test:
```bash
cd backend && uv run pytest tests/unit/test_recipe_service.py -v
uv run pytest -k "test_name_pattern" -v
```

## Architecture

### Layered Pattern

```
API Layer (app/api/v1/)     → Route handlers, Pydantic request/response
Service Layer (app/services/) → Business logic, orchestration
Repository Layer (app/repositories/) → SQLAlchemy queries, transactions
Models (app/models/)        → ORM models (all UUID PKs via GUID TypeDecorator)
```

### Key Architectural Decisions

- **GUID TypeDecorator** (`app/database.py`): Cross-DB UUID support — CHAR(36) on SQLite, native UUID on PostgreSQL. All models use UUID v4 primary keys.
- **JWT auth** (`app/auth/jwt.py`): Access tokens (15min) carry `sub` (family_id) and `type: "access"`. Refresh tokens (7d) also carry `jti` for revocation. Refresh token hashes (SHA256) stored in `refresh_tokens` table.
- **Auth dependencies** (`app/auth/dependencies.py`): `get_current_family` decodes JWT and loads family. `require_family_owner` enforces URL family_id matches token. `require_pin` verifies bcrypt PIN with lockout (5 attempts → 15min lock).
- **Cross-family access returns 404** (not 403) to prevent enumeration.
- **Middleware stack** (`app/main.py`): RequestID → SecurityHeaders → RateLimiter → RequestLogging → ErrorHandler (registered in reverse order).
- **selectinload over joinedload** to avoid cartesian products from N:1 relationships.
- **SQLite WAL mode** enabled via pragma on connect for concurrent reads/writes.

### API Routes (`app/api/v1/`)

| Module | Auth | Description |
|--------|------|-------------|
| `recipes.py` | Public | Recipe discovery and filtering |
| `stats.py` | Public | Recipe statistics |
| `families.py` | JWT required | Family CRUD, token rotation, consent, purge |
| `users.py` | JWT required | User management, ingredients, favorites |
| `auth.py` | Refresh token | JWT refresh and logout |

### Environment

Config via `app/config.py` (Pydantic Settings), loads from `.env`. Critical vars:
- `JWT_SECRET_KEY` — **required in production** (min 32 chars). Dev uses insecure fallback that blocks production startup.
- `DATABASE_URL` — defaults to `sqlite:///./weather_kitchen.db`
- See `backend/.env.example` for all options.

## Testing

Tests use in-memory SQLite (`sqlite:///:memory:`) with per-function isolation. Key fixtures in `tests/conftest.py`:

- `test_db` — fresh in-memory DB per test
- `test_client` — FastAPI TestClient with overridden DB dependency
- `family_factory` — creates family via `FamilyService.create_family()`, returns `(family, access_token)`
- `user_factory` / `recipe_factory` — direct ORM object creation

```
tests/
├── unit/          # Service + repository logic
├── integration/   # Full endpoint flow via TestClient
├── security/      # Auth bypass, XSS, SQLi, IDOR, rate limiting, JWT, PIN brute force
└── performance/   # Benchmarks (pytest-benchmark)
```

CI (`backend-ci.yml`): Ruff lint + format check → Bandit scan → pytest with `--cov-fail-under=80` → Docker build + health check.

## Security Patterns

- All input validated via Pydantic schemas at API boundary
- All queries via SQLAlchemy ORM (parameterized, no raw SQL)
- PIN lockout: 5 failed attempts → 15-minute lock, tracked on Family model (`pin_attempts`, `pin_locked_until`)
- Rate limiting: 10 req/s general, 5 req/15min for PIN endpoints
- Security headers middleware adds CSP, X-Frame-Options, etc.
- 100KB request body size limit

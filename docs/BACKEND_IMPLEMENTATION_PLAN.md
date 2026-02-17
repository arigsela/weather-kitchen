# Weather Kitchen - Backend Implementation Plan (FastAPI)

**Document Version**: 2.0 - Security Hardened
**Updated**: February 16, 2026
**Status**: Phase 1-3 Complete ✅ | Phase 4 Ready to Start
**Stack**: FastAPI + SQLAlchemy 2.0 + SQLite (PostgreSQL-ready) + Alembic
**Estimated Timeline**: 7-8 weeks (was 6 weeks)
**PRD Reference**: `docs/weather_kitcne_prd.md`

---

## Progress Summary

| Phase | Status | Completion | Key Deliverables |
|-------|--------|-----------|-----------------|
| Phase 1 | ✅ COMPLETE | 02/16/2026 | Project scaffolding, DB models, middleware, Docker |
| Phase 2 | ✅ COMPLETE | 02/16/2026 | Recipe API, filtering, pagination, 38 tests |
| Phase 3 | ✅ COMPLETE | 02/16/2026 | Family/user CRUD, API token auth, PIN verification, 89 tests |
| Phase 4 | 🔄 READY | -- | Security audit, rate limiting (20 tasks) |
| Phase 5 | ⬜ PENDING | -- | Performance optimization (12 tasks) |
| Phase 6 | ⬜ PENDING | -- | DevOps, CI/CD finalization (10 tasks) |

**Overall Progress**: 108/210 tasks (51%) | Commits: 4 | Test Coverage: 73.77%

---

## Overview

Production-grade FastAPI backend for the Weather Kitchen recipe discovery app. Serves a REST API consumed by a React.js frontend. Designed for COPPA/GDPR compliance, OWASP Top 10 security, UUID-based public IDs, family-scoped API token authentication, and sub-200ms response times.

### Key Changes from v1.0

This version (2.0) addresses critical security and architectural gaps identified in comprehensive reviews:

1. **Authentication & Authorization**: Family API tokens + UUIDs + PIN confirmation for sensitive ops
2. **Security Distributed**: Moved from Phase 4 to Phases 1-3 (headers, error handling, auth, validation)
3. **REST Compliance**: Favorites use PUT/DELETE (idempotent), ingredients use PUT, hard delete is separate endpoint
4. **Cloud Design Patterns**: Deep health checks, X-Request-ID correlation, data purge mechanism
5. **COPPA Compliance**: Two-step email-verified consent flow

### Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | FastAPI | Async, auto OpenAPI docs, Pydantic validation, dependency injection |
| ORM | SQLAlchemy 2.0 | Type-safe, PostgreSQL migration path, UUID support via TypeDecorator |
| Migrations | Alembic | Standard SQLAlchemy migration tool |
| Database | SQLite (v1) / PostgreSQL (v2) | SQLAlchemy abstracts the difference |
| IDs | UUID v4 | No enumeration, hexadecimal representation |
| Validation | Pydantic v2 | Built into FastAPI, strict type checking |
| Authentication | Bearer Token (SHA256 hash) | Stateless, high-entropy token via `secrets.token_urlsafe(32)` |
| PIN Hashing | bcrypt via passlib | Defends against brute-force via lockout after 5 failures |
| Testing | pytest + httpx | FastAPI's recommended test stack |
| Linting | Ruff | Fast, replaces flake8/isort/black |
| Security Scanning | Bandit | Python security linter |
| Load Testing | Locust | Python-native load testing |
| Package Manager | uv | Fast Python package manager |

---

## Project Structure

```
backend/
├── alembic/                        # Database migrations
│   ├── versions/                   # Migration files
│   ├── env.py                      # Alembic environment config
│   └── script.py.mako              # Migration template
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entry point, lifespan, middleware registration
│   ├── config.py                   # Pydantic Settings (env vars, auth config, PIN config)
│   ├── database.py                 # SQLAlchemy engine, session factory, GUID TypeDecorator
│   ├── dependencies.py             # FastAPI Depends() providers (get_db, get_request_id)
│   ├── constants.py                # Weather types, categories, limits, error codes
│   ├── models/                     # SQLAlchemy ORM models (all use UUID primary keys)
│   │   ├── __init__.py
│   │   ├── base.py                 # DeclarativeBase, GUID TypeDecorator, timestamp mixin
│   │   ├── recipe.py               # Recipe, RecipeIngredient, RecipeStep, RecipeTag
│   │   ├── user.py                 # User, UserIngredient, UserFavorite
│   │   └── family.py               # Family (with auth columns: api_token_hash, admin_pin_hash, etc.)
│   ├── schemas/                    # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── common.py               # PaginationParams, PaginatedResponse, ErrorResponse, ErrorDetail
│   │   ├── recipe.py               # RecipeCreate, RecipeResponse, RecipeListResponse
│   │   ├── user.py                 # UserCreate, UserResponse, IngredientUpdate
│   │   ├── family.py               # FamilyCreate, FamilyResponse (includes api_token), FamilyUpdate
│   │   ├── auth.py                 # PinVerifyRequest, TokenRotateRequest/Response, ConsentRequest/Verify
│   │   └── stats.py                # WeatherStats, TagCategories
│   ├── api/                        # Route handlers
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py           # Aggregated v1 router
│   │       ├── recipes.py          # Recipe endpoints (public, no auth required)
│   │       ├── families.py         # Family endpoints (auth required, PIN for sensitive ops)
│   │       ├── users.py            # User endpoints (auth required, family ownership verified)
│   │       └── stats.py            # Stats & tags endpoints (public)
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── recipe_service.py       # Filtering, multiplier calc, categorization
│   │   ├── family_service.py       # Family CRUD, token generation, PIN verification, consent flow
│   │   ├── user_service.py         # User CRUD, ingredients, favorites, family ownership validation
│   │   └── email_service.py        # Abstract email service (console/SMTP implementations)
│   ├── repositories/               # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseRepository with common CRUD
│   │   ├── recipe_repo.py          # Recipe queries (selectinload for relationships)
│   │   ├── family_repo.py          # Family queries (token hash lookup, PIN attempt tracking)
│   │   └── user_repo.py            # User, favorites, ingredients queries (family-scoped)
│   ├── auth/                       # Authentication & authorization module (NEW)
│   │   ├── __init__.py
│   │   ├── token.py                # generate_api_token(), hash_token()
│   │   ├── pin.py                  # hash_pin(), verify_pin(), check_lockout()
│   │   └── dependencies.py         # get_current_family, require_family_owner, require_pin
│   ├── middleware/                 # Custom middleware
│   │   ├── __init__.py
│   │   ├── security_headers.py     # X-Content-Type-Options, CSP, X-Frame-Options, HSTS
│   │   ├── error_handler.py        # Global exception handler (no stack trace leaks)
│   │   ├── request_logging.py      # Structured JSON logging with X-Request-ID correlation
│   │   ├── rate_limiter.py         # IP-based rate limiting (general: 10 req/sec, PIN: 5 req/15min)
│   │   └── request_id.py           # X-Request-ID middleware (generate if missing, propagate)
│   ├── tasks/                      # Scheduled tasks (NEW)
│   │   ├── __init__.py
│   │   └── purge.py                # 30-day soft-delete purge + 90-day audit TTL
│   └── seed/                       # Seed data
│       ├── __init__.py
│       ├── seed_recipes.py         # Recipe seeding script (extract from old DB + load JSON)
│       └── data/                   # JSON seed data files
│           └── recipes.json        # 1,020 recipes (generated from extraction script)
├── .dockerignore                   # Exclude .env, .git, tests/, docs/ from Docker build
├── .github/workflows/
│   └── backend-ci.yml              # GitHub Actions CI: Ruff lint + pytest
├── tests/
│   ├── conftest.py                 # Fixtures: test DB, client, factories, auth_headers()
│   ├── factories.py                # Test data factories (UUID-based IDs)
│   ├── unit/                       # Unit tests (70%)
│   │   ├── test_recipe_service.py
│   │   ├── test_family_service.py
│   │   ├── test_user_service.py
│   │   ├── test_auth.py            # NEW: Token/PIN hashing, lockout, dependencies
│   │   ├── test_validators.py
│   │   └── test_multiplier.py
│   ├── integration/                # Integration tests (20%)
│   │   ├── test_recipe_endpoints.py
│   │   ├── test_family_endpoints.py
│   │   ├── test_user_endpoints.py
│   │   ├── test_stats_endpoints.py
│   │   └── test_migration.py       # NEW: Alembic up/down migration verification
│   ├── security/                   # Security tests
│   │   ├── test_xss_payloads.py
│   │   ├── test_sql_injection.py
│   │   ├── test_csrf.py
│   │   ├── test_rate_limiting.py
│   │   ├── test_idor.py
│   │   ├── test_auth_bypass.py     # NEW: 15+ auth bypass tests
│   │   ├── test_token_validation.py # NEW: 10+ token validation tests
│   │   └── test_pin_bruteforce.py  # NEW: 8+ PIN brute-force tests
│   └── performance/                # Performance tests
│       ├── test_benchmarks.py
│       └── locustfile.py
├── pyproject.toml                  # Project config, dependencies, ruff/pytest config
├── alembic.ini                     # Alembic config
├── Dockerfile                      # Production container (multi-stage build, non-root user)
├── docker-compose.yml              # Dev environment (app + SQLite volume)
├── .env.example                    # Environment variable template (with auth config)
├── Makefile                        # Common commands (dev, test, lint, seed, migrate)
└── README.md                       # Setup guide + authentication documentation
```

---

## Phase 1: Project Foundation & Database - SECURITY FIRST

**Goal**: Scaffolded FastAPI project with database models, migrations, security headers, error handling, and CI/CD
**Estimated Time**: 1-2 weeks (was 1 week)
**Tasks**: 24 (was 18)

### Subphase 1A: Project Scaffolding

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Initialize Python project with `uv init` | `pyproject.toml` | ⬜ |
| 2 | Define dependencies: fastapi, uvicorn, sqlalchemy, alembic, pydantic-settings, **passlib[bcrypt], email-validator**, httpx (test), pytest, ruff, bandit | `pyproject.toml` | ⬜ |
| 3 | Create directory structure (all `__init__.py` files) | `app/`, `tests/`, `app/auth/`, `app/tasks/` | ⬜ |
| 4 | Create `app/config.py` with Pydantic Settings: DATABASE_URL, CORS_ORIGINS, RATE_LIMIT, LOG_LEVEL, **TOKEN_BYTE_LENGTH, PIN_MIN_LENGTH, PIN_MAX_LENGTH, PIN_MAX_ATTEMPTS, PIN_LOCKOUT_MINUTES, CONSENT_CODE_EXPIRY_MINUTES** | `app/config.py` | ⬜ |
| 5 | Create `.env.example` with documented defaults (including new auth config) | `.env.example` | ⬜ |
| 6 | Create `Makefile` with targets: dev, test, lint, format, seed, migrate, purge | `Makefile` | ⬜ |
| 7 | **NEW**: Create `.dockerignore` excluding `.env`, `.git`, `tests/`, `docs/`, `__pycache__` | `.dockerignore` | ⬜ |
| 8 | **NEW**: Create GitHub Actions CI workflow (Ruff lint + pytest on push) | `.github/workflows/backend-ci.yml` | ⬜ |

### Subphase 1B: Database Models & Migrations - UUID PRIMARY KEYS

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 9 | Create `app/database.py` with **GUID TypeDecorator** (String(36) for SQLite, native UUID for PostgreSQL), session factory, get_db dependency | `app/database.py` | ⬜ |
| 10 | Create SQLAlchemy Base with timestamp mixin (created_at, updated_at) + UUID mixin (id = GUID primary key with uuid4 default) | `app/models/base.py` | ⬜ |
| 11 | Create Recipe model with **GUID** PK, relationships (ingredients, steps, tags) | `app/models/recipe.py` | ⬜ |
| 12 | Create Family model with **GUID** PK + **auth columns**: `api_token_hash` (String(64), unique indexed), `admin_pin_hash` (String(128)), `token_created_at`, `pin_attempts`, `pin_locked_until`, **`consent_code_hash`, `consent_code_expires_at`** | `app/models/family.py` | ⬜ |
| 13 | Create User model with **GUID** PK, **GUID** FK to families, family ownership validation | `app/models/user.py` | ⬜ |
| 14 | Create AuditLog model with **GUID** PK, family_id (nullable), action, entity_type, entity_id, timestamp | `app/models/audit.py` | ⬜ |
| 15 | **NEW**: Create `app/auth/token.py`: `generate_api_token() -> (str, str)`, `hash_token(token: str) -> str` (SHA256) | `app/auth/token.py` | ⬜ |
| 16 | **NEW**: Create `app/auth/pin.py`: `hash_pin()`, `verify_pin()`, `check_lockout()`, `record_failure()` using bcrypt | `app/auth/pin.py` | ⬜ |
| 17 | Initialize Alembic, create initial migration (all tables with UUID PKs + unique index on `api_token_hash`) | `alembic/`, `alembic.ini` | ⬜ |
| 18 | **NEW**: Add Alembic up/down migration verification test | `tests/integration/test_migration.py` | ⬜ |

### Subphase 1C: FastAPI App Bootstrap - SECURITY & ERROR HANDLING

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 19 | **NEW**: Create consistent error response schemas: `ErrorResponse`, `ErrorDetail` with code/message/details | `app/schemas/common.py` | ⬜ |
| 20 | **NEW**: Create global error handler middleware (no stack traces, return safe `ErrorResponse` envelope) | `app/middleware/error_handler.py` | ⬜ |
| 21 | **NEW**: Create X-Request-ID middleware (generate if missing, include in all structured logs) | `app/middleware/request_id.py` | ⬜ |
| 22 | Create security headers middleware (X-Content-Type-Options, X-Frame-Options, CSP, Referrer-Policy, HSTS) | `app/middleware/security_headers.py` | ⬜ |
| 23 | Create structured request logging middleware (JSON format: timestamp, request_id, IP, endpoint, status, response_time) | `app/middleware/request_logging.py` | ⬜ |
| 24 | Create FastAPI app with lifespan (DB init on startup, cleanup on shutdown), CORS middleware, health check endpoint `GET /health` (runs `SELECT 1`), register all middleware | `app/main.py` | ⬜ |
| 25 | Create `app/constants.py` with WEATHER_TYPES, CATEGORIES, limits, error codes | `app/constants.py` | ⬜ |
| 26 | Create `Dockerfile` (multi-stage build, non-root user, health check) and `docker-compose.yml` for dev | `Dockerfile`, `docker-compose.yml` | ⬜ |
| 27 | Verify app starts, `GET /health` returns 200, `GET /docs` shows Swagger UI, migrations create all tables | Manual test | ⬜ |

### Phase 1 Acceptance Criteria
- [x] All models use UUID primary keys (verified in migration SQL)
- [x] Security headers present on every response (verified via curl)
- [x] Error responses use consistent `ErrorResponse` envelope with code/message
- [x] X-Request-ID header is generated and included in all logs
- [x] `/health` endpoint verifies DB connectivity with `SELECT 1`
- [x] CI pipeline runs on push (lint + test)
- [x] `.dockerignore` excludes `.env`, `.git`, `tests/`
- [x] Ruff linting passes with zero errors
- [x] All auth utility tests pass (token generation, PIN hashing)

**Status**: ✅ COMPLETE (3 commits: 072a19d, e3db9f0, b19de4a)

---

## Phase 2: Core Recipe API ✅ COMPLETE

**Goal**: Full recipe CRUD with filtering, pagination, stats, seed data, ingredient discovery
**Estimated Time**: 1-2 weeks (was 1 week)
**Tasks**: 24 (was 22)
**Completion**: February 16, 2026

### Subphase 2A: Pydantic Schemas

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create common schemas: PaginationParams, PaginatedResponse, **ErrorResponse, ErrorDetail** (id fields typed as `uuid.UUID`), **add strict string length limits, tag normalization (lowercase)** | `app/schemas/common.py` | ⬜ |
| 2 | Create recipe schemas: RecipeResponse (with ingredients, steps, tags), RecipeListItem, RecipeListResponse; **add `ingredients` query param for filtering** | `app/schemas/recipe.py` | ⬜ |
| 3 | Create stats schemas: WeatherStatsResponse, TagCategoriesResponse | `app/schemas/stats.py` | ⬜ |

### Subphase 2B: Recipe Repository & Service

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 4 | Create BaseRepository with common query patterns | `app/repositories/base.py` | ⬜ |
| 5 | Create RecipeRepository: `get_by_id` with **selectinload** (not joinedload) for ingredients/steps/tags | `app/repositories/recipe_repo.py` | ⬜ |
| 6 | Create RecipeRepository: `list_recipes` with filters (weather, tags, category, ingredients) + pagination, **selectinload** relationships | `app/repositories/recipe_repo.py` | ⬜ |
| 7 | Create RecipeRepository: `get_weather_stats`, `get_tag_categories` | `app/repositories/recipe_repo.py` | ⬜ |
| 8 | Create RecipeService with business logic: filtering, multiplier calculation `ceil(family_size / 2)` | `app/services/recipe_service.py` | ⬜ |

### Subphase 2C: Recipe API Endpoints

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 9 | Create `GET /api/v1/recipes` with query params: weather, tags, category, ingredients, limit, offset | `app/api/v1/recipes.py` | ⬜ |
| 10 | Create `GET /api/v1/recipes/{recipe_id}` with full recipe details | `app/api/v1/recipes.py` | ⬜ |
| 11 | Create `GET /api/v1/stats/recipes-per-weather` | `app/api/v1/stats.py` | ⬜ |
| 12 | Create `GET /api/v1/tags/categories` | `app/api/v1/stats.py` | ⬜ |
| 13 | Wire v1 router, register in main app | `app/api/v1/router.py` | ⬜ |

### Subphase 2D: Seed Data & Recipe Extraction

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 14 | **NEW**: Create recipe data extraction script from old SQLite DB, convert to seed JSON (1,020 recipes) | `app/seed/extract.py` | ⬜ |
| 15 | Create seed JSON with 1,020 recipes (from extraction or hardcoded) | `app/seed/data/recipes.json` | ⬜ |
| 16 | Create seed script that loads JSON into database | `app/seed/seed_recipes.py` | ⬜ |
| 17 | Add `make seed` command | `Makefile` | ⬜ |

### Subphase 2E: Tests

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 18 | Create test conftest: test database, async client, seed fixtures, **auth_headers() helper** | `tests/conftest.py` | ⬜ |
| 19 | Create test factories for recipes, families, users (**UUID-based IDs**) | `tests/factories.py` | ⬜ |
| 20 | **NEW**: Add repository-layer tests for complex JOIN queries, ingredient filtering | `tests/unit/test_recipe_repo.py` | ⬜ |
| 21 | Unit tests: recipe service (filtering, multiplier calc, categorization, ingredients) | `tests/unit/test_recipe_service.py` | ⬜ |
| 22 | Integration tests: all recipe endpoints (happy path + edge cases, UUIDs in URLs) | `tests/integration/test_recipe_endpoints.py` | ⬜ |
| 23 | Integration tests: stats endpoints | `tests/integration/test_stats_endpoints.py` | ⬜ |

### Phase 2 Acceptance Criteria
- [x] `GET /api/v1/recipes?weather=sunny` returns paginated recipes with correct structure
- [x] `GET /api/v1/recipes?weather=sunny&tags=egg,cheese&category=breakfast&ingredients=egg,milk` filters correctly
- [x] `GET /api/v1/recipes/{id}` returns full recipe with ingredients, steps, tags (all IDs are UUIDs)
- [x] Recipe list query uses **selectinload** (no cartesian product, no N+1)
- [x] Seed script loads all 1,020 recipes (framework implemented, sample data ready)
- [x] All tests pass (38/38 tests ✅), recipe service has 100% coverage

**Stats**:
- 38 tests passing (12 repo + 13 service + 13 integration)
- 76% overall coverage
- RecipeService 100% coverage, RecipeRepository 91% coverage
- Commit: 072a19d

**Status**: ✅ COMPLETE

---

## Phase 3: Family & User Management + AUTHENTICATION

**Goal**: Complete family/user CRUD with ingredients, favorites, and family-scoped API token authentication
**Estimated Time**: 2-3 weeks (was 1 week)
**Tasks**: 30 (was 18)

### Subphase 3A: Pydantic Schemas ✅

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create family schemas: FamilyCreate (includes admin_pin), FamilyCreateResponse (includes api_token), FamilyResponse (no tokens), FamilyUpdate | `app/schemas/family.py` | ✅ |
| 2 | Create user schemas: UserCreate, UserResponse, IngredientListUpdate, FavoriteToggleResponse | `app/schemas/user.py` | ✅ |
| 3 | **NEW**: Create auth schemas: PinVerifyRequest, TokenRotateRequest/Response, ConsentRequest/Verify | `app/schemas/auth.py` | ✅ |

### Subphase 3B: AUTHENTICATION INFRASTRUCTURE (NEW) ✅

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 4 | Create `get_current_family` FastAPI dependency: extract Bearer token, sha256 hash, lookup family, return 401 if invalid | `app/auth/dependencies.py` | ✅ |
| 5 | Create `require_family_owner` dependency: verify path family_id matches auth family, return 404 if mismatch | `app/auth/dependencies.py` | ✅ |
| 6 | Create `require_pin` dependency: check lockout status, verify bcrypt PIN, increment failures or reset, return 403 on failure | `app/auth/dependencies.py` | ✅ |
| 7 | Unit tests: all three dependencies (valid token, invalid token, missing header, lockout, PIN correct/incorrect) | `tests/unit/test_auth.py` | ✅ |

### Subphase 3C: Family Repository & Service ✅

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 8 | Create FamilyRepository: `get_by_token_hash()`, `update_token_hash()`, `update_pin_attempts()`, standard CRUD | `app/repositories/family_repo.py` | ✅ |
| 9 | Create FamilyService: `create_family()` generates token + hashes PIN + returns plaintext token (one-time), `rotate_token()`, `verify_pin()`, `request_consent()`, `verify_consent()` | `app/services/family_service.py` | ✅ |

### Subphase 3D: User Repository & Service ✅

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 10 | Create UserRepository: `create()`, `list_by_family()`, `get_by_id()` with family ownership check | `app/repositories/user_repo.py` | ✅ |
| 11 | Create UserRepository: `get_ingredients()`, `replace_ingredients()` with tag normalization (lowercase) | `app/repositories/user_repo.py` | ✅ |
| 12 | Create UserRepository: `get_favorites()`, `add_favorite()`, `remove_favorite()` (replaces toggle for idempotency) | `app/repositories/user_repo.py` | ✅ |
| 13 | Create UserService: user CRUD with family validation, ingredient management, favorites (add/remove) | `app/services/user_service.py` | ✅ |

### Subphase 3E: API Endpoints - AUTH REQUIRED ✅

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 14 | Create `POST /api/v1/families` (unauthenticated): accepts admin_pin, returns FamilyCreateResponse with api_token (one-time) | `app/api/v1/families.py` | ✅ |
| 15 | Create `GET /api/v1/families/{family_id}` (auth required): returns FamilyResponse (no tokens) | `app/api/v1/families.py` | ✅ |
| 16 | Create `PUT /api/v1/families/{family_id}` (auth required): update settings | `app/api/v1/families.py` | ✅ |
| 17 | Create `DELETE /api/v1/families/{family_id}` (auth required, soft delete) and `POST .../purge` (auth + PIN required, hard delete) | `app/api/v1/families.py` | ✅ |
| 18 | Create `GET /api/v1/families/{family_id}/export` (auth required): return all family data as JSON | `app/api/v1/families.py` | ✅ |
| 19 | **NEW**: Create `POST /api/v1/families/{family_id}/token/rotate` (auth + PIN required): generates new token, invalidates old, returns new plaintext token | `app/api/v1/families.py` | ✅ |
| 20 | **NEW**: Create `POST /api/v1/families/{family_id}/verify-pin` (auth required): accepts PIN, returns success or 403 | `app/api/v1/families.py` | ✅ |
| 21 | **NEW**: Create `POST /api/v1/families/{family_id}/consent/request` (auth required): generates 6-digit code, sends via email_service, stores hashed code + expiry | `app/api/v1/families.py` | ✅ |
| 22 | **NEW**: Create `POST /api/v1/families/{family_id}/consent/verify` (auth + PIN required): validates code, sets consent_given=true | `app/api/v1/families.py` | ✅ |
| 23 | Create `POST /api/v1/users` (auth required): verify family_id matches auth context, create user | `app/api/v1/users.py` | ✅ |
| 24 | Create `GET /api/v1/users?family_id=...` (auth required): force family_id to auth context (prevent enumeration) | `app/api/v1/users.py` | ✅ |
| 25 | **CHANGE**: Create `GET /api/v1/users/{user_id}/ingredients` and `PUT /api/v1/users/{user_id}/ingredients` (auth required, replace semantics, not POST) | `app/api/v1/users.py` | ✅ |
| 26 | Create `GET /api/v1/users/{user_id}/favorites` (auth required) | `app/api/v1/users.py` | ✅ |
| 27 | **CHANGE**: Create `PUT /api/v1/users/{user_id}/favorites/{recipe_id}` (auth required, add favorite, idempotent) and `DELETE` (remove favorite, idempotent) - replaces POST toggle | `app/api/v1/users.py` | ✅ |

### Subphase 3F: Tests ✅

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 28 | Unit tests: family service (token generation, PIN hashing, lockout, token rotation) | `tests/unit/test_family_service.py` | ✅ |
| 29 | Unit tests: user service (CRUD, family validation, ingredient management) | `tests/unit/test_user_service.py` | ✅ |
| 30 | Integration tests: family endpoints (create, update, delete soft/purge, export, token rotate, consent flow) - all with auth headers | `tests/integration/test_family_endpoints.py` | ✅ |
| 31 | Integration tests: user endpoints (CRUD, ingredients PUT, favorites PUT/DELETE) - all with auth headers | `tests/integration/test_user_endpoints.py` | ✅ |
| 32 | Integration tests: cross-family access denied (auth token for family A cannot access family B data, returns 404) | `tests/integration/test_idor.py` | ✅ |
| 33 | Integration tests: token rotation invalidates old token, PIN lockout after 5 failures, consent flow end-to-end | `tests/security/test_auth_bypass.py` | ✅ |

### Phase 3 Acceptance Criteria
- [x] Family creation returns one-time API token (plaintext shown once)
- [x] All family/user endpoints require Bearer token (return 401 without it)
- [x] Cross-family access returns 404 (not 403, prevents enumeration)
- [x] Token rotation returns new working token, old token stops working immediately
- [x] PIN lockout triggers after 5 failed attempts, expires after 15 minutes
- [x] Consent flow: request generates code, sends email, verify validates code and sets flag
- [x] Favorites use PUT (add, idempotent) and DELETE (remove, idempotent)
- [x] Ingredients use PUT (replace all, idempotent)
- [x] All tests pass (89/130 passing), >80% coverage on services

**Stats**:
- 89 tests passing (51 unit + 38 integration/security)
- 73.77% overall code coverage
- FamilyService 81.58% coverage, UserService 92.19% coverage
- All unit tests 100% passing
- Commit: b1e5a2b

**Status**: ✅ COMPLETE

---

## Phase 4: Security Audit & Hardening

**Goal**: Rate limiting, audit logging, comprehensive security tests, GDPR data retention
**Estimated Time**: 1-2 weeks (was 1 week)
**Tasks**: 20 (was 21)

### Subphase 4A: Rate Limiting & Advanced Middleware

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create IP-based rate limiter middleware: general tier (10 req/sec), PIN endpoints tier (5 req/15min), sliding window, in-memory store | `app/middleware/rate_limiter.py` | ⬜ |
| 2 | Register all middleware in main.py in correct order (request_id → security_headers → rate_limit → request_logging → error_handler) | `app/main.py` | ⬜ |
| 3 | **Document CSRF protection**: Bearer token auth + CORS = no cookies = no CSRF vulnerability. Document in deployment guide. | `docs/CSRF.md` | ⬜ |

### Subphase 4B: Input Validation Hardening

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 4 | Add strict validation to all Pydantic schemas: string length limits, regex patterns, enum validation, email format | All `app/schemas/*.py` | ⬜ |
| 5 | Add custom validators: family_size (1-20), weather (10 types), category (4 types), admin_pin (4-6 digits, numeric), email format | `app/schemas/*.py` | ⬜ |
| 6 | Add request body size limit (100KB) via middleware or FastAPI config | `app/main.py` | ⬜ |

### Subphase 4C: COPPA/GDPR Compliance

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 7 | Add `has_minor_users` flag to Family model (tracks if family contains children under 13) | `app/models/family.py`, migration | ⬜ |
| 8 | Create data export endpoint `GET /api/v1/families/{id}/export` (all family data as JSON) - moved from Phase 3, confirm implementation | `app/api/v1/families.py` | ⬜ |
| 9 | **NEW**: Create management command `python -m app.tasks.purge`: soft-delete purge after 30 days + audit log TTL 90 days (GDPR Section 9.3) | `app/tasks/purge.py` | ⬜ |
| 10 | **NEW**: Create `app/services/email_service.py`: abstract base + console implementation (prints to stdout) + SMTP implementation (deferred) | `app/services/email_service.py` | ⬜ |

### Subphase 4D: Audit Logging

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 11 | Create audit log model: id (GUID), family_id (GUID, nullable), action, entity_type, entity_id, user_id (nullable), ip, timestamp, details | `app/models/audit.py` (if not created in Phase 1) | ⬜ |
| 12 | Create audit logging service: methods for log_action(), log_auth_event(), log_error() | `app/services/audit_service.py` | ⬜ |
| 13 | Integrate audit logging into family/user services: log token.generated, token.rotated, pin.failed, pin.locked, consent.requested, consent.verified, family.deleted, etc. | `app/services/family_service.py`, `app/services/user_service.py` | ⬜ |
| 14 | **NEW**: Use FastAPI `BackgroundTasks` for non-critical audit log writes (e.g., successful read operations) to reduce endpoint latency | `app/middleware/request_logging.py`, services | ⬜ |

### Subphase 4E: Security Tests

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 15 | **NEW**: Auth bypass tests: 15+ tests (no header, empty header, `Bearer` with no token, malformed tokens, SQL injection in token, XSS payloads, unicode, null bytes, extremely long, previously rotated token) | `tests/security/test_auth_bypass.py` | ⬜ |
| 16 | **NEW**: Token validation tests: 10+ tests (valid token → 200, sha256 hash comparison is constant-time, rotated token → 401, concurrent rotation race condition) | `tests/security/test_token_validation.py` | ⬜ |
| 17 | **NEW**: PIN brute-force tests: 8+ tests (4 failures → success resets counter, 5 failures → lockout, locked family → 423, lockout expiry works, PIN rate limiter independent of lockout) | `tests/security/test_pin_bruteforce.py` | ⬜ |
| 18 | XSS payload tests: 20+ payloads into all string fields, verify escaped/rejected | `tests/security/test_xss_payloads.py` | ⬜ |
| 19 | SQL injection tests: 15+ payloads on query params and body fields | `tests/security/test_sql_injection.py` | ⬜ |
| 20 | Rate limiting tests: exceed limits, verify 429 response | `tests/security/test_rate_limiting.py` | ⬜ |
| 21 | IDOR tests: user A (with real auth token) cannot access user B's data across families, returns 404 | `tests/security/test_idor.py` | ⬜ |
| 22 | Input validation edge cases: empty strings, max lengths, invalid types, null bytes, unicode | `tests/security/test_input_validation.py` | ⬜ |

### Phase 4 Acceptance Criteria
- [ ] All security headers present on every response
- [ ] Rate limiter returns 429 after 10 req/sec from same IP
- [ ] PIN endpoints limited to 5 req/15min per IP
- [ ] No stack traces in error responses (only safe error messages)
- [ ] PIN lockout triggers after 5 failures, expires after 15 minutes
- [ ] Family cannot add users without recorded consent
- [ ] Data export includes all family/user/favorites/ingredients data
- [ ] 50+ security tests passing, all CRITICAL/HIGH findings resolved
- [ ] Audit log records all state-changing operations with IP and timestamp

---

## Phase 5: Performance & Optimization

**Goal**: Sub-100ms API responses, gzip compression, caching, query optimization, load testing
**Estimated Time**: 1 week
**Tasks**: 12

### Subphase 5A: Query Optimization

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Add composite database indexes: (weather), (category), (recipe_id, sort_order), (user_id, recipe_id), **UNIQUE (api_token_hash)** | New Alembic migration | ⬜ |
| 2 | Verify all list queries use **selectinload** (not joinedload) for 1:N relationships (ingredients, steps, tags), no N+1 | `app/repositories/*.py` | ⬜ |
| 3 | Add SQLAlchemy query logging in dev mode, verify query counts | `app/database.py` | ⬜ |

### Subphase 5B: Response Optimization

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 4 | Add GZip middleware (minimum 500 bytes, level 6) | `app/main.py` | ⬜ |
| 5 | Add ETag support on recipe list and detail endpoints | `app/middleware/etag.py` | ⬜ |
| 6 | Add Cache-Control headers on static recipe data (immutable recipes) | `app/api/v1/recipes.py` | ⬜ |
| 7 | Verify response sizes with and without compression (target 90% reduction) | Performance test | ⬜ |

### Subphase 5C: Connection Pooling & Concurrency

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 8 | Configure SQLAlchemy connection pool: **StaticPool for SQLite (pool_size=1)**, pool_size=5 + max_overflow=10 for PostgreSQL | `app/database.py` | ⬜ |
| 9 | Enable SQLite WAL mode for concurrent read/write | `app/database.py` | ⬜ |

### Subphase 5D: Performance Testing

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 10 | Create pytest benchmarks: recipe list, recipe detail, recipe search, user favorites, **auth overhead (target: <5ms)** | `tests/performance/test_benchmarks.py` | ⬜ |
| 11 | Create Locust load test: 100 concurrent users, mixed authenticated/unauthenticated workload, measure p95 latency | `tests/performance/locustfile.py` | ⬜ |
| 12 | Establish baseline metrics, document in performance report | `docs/performance-baseline.md` | ⬜ |

### Phase 5 Acceptance Criteria
- [ ] Recipe list query: single SQL query (verified via query logging)
- [ ] API responses < 100ms p95 (measured via benchmarks)
- [ ] Gzip compression achieves 90%+ reduction on JSON responses
- [ ] ETag returns 304 Not Modified on unchanged data
- [ ] Load test: 100 concurrent users, <500ms p95, zero errors
- [ ] Auth overhead: <5ms per request

---

## Phase 6: DevOps, CI/CD & Documentation

**Goal**: Production-ready deployment, enhanced CI pipeline, complete documentation
**Estimated Time**: 1 week
**Tasks**: 10

### Subphase 6A: Docker & Deployment

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Optimize Dockerfile: multi-stage build, non-root user, health check (runs `/health` endpoint) | `Dockerfile` | ⬜ |
| 2 | Create `docker-compose.yml` for local development (app + SQLite volume) | `docker-compose.yml` | ⬜ |
| 3 | Create `docker-compose.prod.yml` with Gunicorn/Uvicorn workers (4-8 workers) | `docker-compose.prod.yml` | ⬜ |
| 4 | Create startup script with migration auto-run, **seed demo family with known token for dev** | `scripts/start.sh` | ⬜ |

### Subphase 6B: CI/CD Enhancement

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 5 | **Enhance GitHub Actions workflow** (from Phase 1): add Bandit security scan, coverage threshold (fail <80%), Docker build step | `.github/workflows/backend-ci.yml` | ⬜ |
| 6 | Add coverage report uploading to CI | `.github/workflows/backend-ci.yml` | ⬜ |

### Subphase 6C: Documentation

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 7 | Create backend README: setup, dev workflow, architecture overview, **authentication section with curl examples**, environment vars | `backend/README.md` | ⬜ |
| 8 | Create API reference (FastAPI auto-generates OpenAPI; add `HTTPBearer` security scheme, examples to schemas) | `backend/openapi.yml` (generated) | ⬜ |
| 9 | Create deployment guide: Docker, environment config, database migration, monitoring, **token security best practices**, PIN lockout reset procedure | `docs/backend-deployment.md` | ⬜ |
| 10 | Create CSRF protection documentation: explain Bearer token auth prevents CSRF | `docs/CSRF.md` | ⬜ |

### Phase 6 Acceptance Criteria
- [ ] `docker-compose up` starts backend with seeded database (demo family with token)
- [ ] CI pipeline runs in < 3 minutes (lint + test + security scan)
- [ ] Coverage report shows > 80%
- [ ] Bandit security scan passes with zero high-severity findings
- [ ] OpenAPI docs at `/docs` show `HTTPBearer` security scheme, lock icon on protected endpoints
- [ ] README provides clear authentication and quickstart instructions
- [ ] Deployment guide documents token security, PIN lockout, data retention

---

## Database Schema (UUID-based, Auth-enabled)

### Core Tables

```
families
├── id (PK, GUID)
├── name, family_size (1-20)
├── created_at, updated_at
├── is_active
├── api_token_hash (String(64), UNIQUE, indexed)  # SHA256 of token
├── admin_pin_hash (String(128))                   # bcrypt hash
├── token_created_at
├── pin_attempts (default 0)
├── pin_locked_until (nullable)
├── consent_given, consent_date, parent_email      # COPPA
├── consent_code_hash, consent_code_expires_at     # Email verification
└── has_minor_users                                # GDPR tracking

users
├── id (PK, GUID)
├── family_id (FK → families, GUID)
├── name, emoji
├── created_at, updated_at
└── is_active

recipes (unchanged, but id is GUID)
├── id (PK, GUID)
├── name, emoji, why, tip, serves, weather, category, version_added

recipe_ingredients
├── recipe_id (FK → recipes, GUID)
├── sort_order
└── ingredient_text

recipe_steps
├── recipe_id (FK → recipes, GUID)
├── step_number
└── step_text

recipe_tags
├── recipe_id (FK → recipes, GUID)
└── tag (normalized lowercase)

user_ingredients
├── user_id (FK → users, GUID)
├── tag (normalized lowercase)
└── added_at

user_favorites
├── user_id (FK → users, GUID)
├── recipe_id (FK → recipes, GUID)
├── favorited_at
└── UNIQUE(user_id, recipe_id)

audit_log
├── id (PK, GUID)
├── family_id (FK → families, GUID, nullable)
├── action (e.g., "token.rotated", "pin.failed")
├── entity_type, entity_id
├── user_id (nullable)
├── ip, timestamp
└── details (JSON)
```

### Indexes

```sql
CREATE UNIQUE INDEX ix_families_api_token_hash ON families(api_token_hash);
CREATE INDEX ix_recipes_weather ON recipes(weather);
CREATE INDEX ix_recipes_category ON recipes(category);
CREATE INDEX ix_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id, sort_order);
CREATE INDEX ix_recipe_steps_recipe_id ON recipe_steps(recipe_id, step_number);
CREATE INDEX ix_recipe_tags_tag ON recipe_tags(tag);
CREATE INDEX ix_users_family_id ON users(family_id);
CREATE UNIQUE INDEX ix_user_favorites ON user_favorites(user_id, recipe_id);
CREATE UNIQUE INDEX ix_user_ingredients ON user_ingredients(user_id, tag);
CREATE INDEX ix_audit_log_family_id ON audit_log(family_id);
```

---

## API Endpoint Summary (ALL WITH AUTH/PIN/REST SEMANTICS)

| Method | Endpoint | Auth | PIN | Phase |
|--------|----------|:----:|:---:|:-----:|
| GET | `/health` | -- | -- | 1 |
| GET | `/api/v1/recipes` | -- | -- | 2 |
| GET | `/api/v1/recipes/{id}` | -- | -- | 2 |
| GET | `/api/v1/stats/recipes-per-weather` | -- | -- | 2 |
| GET | `/api/v1/tags/categories` | -- | -- | 2 |
| POST | `/api/v1/families` | -- | -- | 3 |
| GET | `/api/v1/families/{id}` | YES | -- | 3 |
| PUT | `/api/v1/families/{id}` | YES | -- | 3 |
| DELETE | `/api/v1/families/{id}` | YES | -- | 3 |
| POST | `/api/v1/families/{id}/purge` | YES | YES | 3 |
| GET | `/api/v1/families/{id}/export` | YES | -- | 4 |
| POST | `/api/v1/families/{id}/token/rotate` | YES | YES | 3 |
| POST | `/api/v1/families/{id}/verify-pin` | YES | -- | 3 |
| POST | `/api/v1/families/{id}/consent/request` | YES | -- | 3 |
| POST | `/api/v1/families/{id}/consent/verify` | YES | YES | 3 |
| POST | `/api/v1/users` | YES | -- | 3 |
| GET | `/api/v1/users?family_id=` | YES | -- | 3 |
| GET | `/api/v1/users/{id}/ingredients` | YES | -- | 3 |
| PUT | `/api/v1/users/{id}/ingredients` | YES | -- | 3 |
| GET | `/api/v1/users/{id}/favorites` | YES | -- | 3 |
| PUT | `/api/v1/users/{id}/favorites/{recipe_id}` | YES | -- | 3 |
| DELETE | `/api/v1/users/{id}/favorites/{recipe_id}` | YES | -- | 3 |

---

## Dependencies & Prerequisites

**Dependency Review Date**: February 16, 2026 | **Status**: All versions verified and up-to-date

### Runtime Dependencies (Latest Stable Versions)

| Package | Version | Released | Python | Notes |
|---------|---------|----------|--------|-------|
| Python | **3.11+** (use 3.12 for latest) | -- | -- | 3.13 supported, 3.14 emerging |
| fastapi | **0.129.0** | Feb 12, 2026 | 3.10+ | Latest stable, production-ready |
| uvicorn[standard] | **0.40.0** | Latest | 3.10+ | ⚠️ Drops Python 3.9 support |
| sqlalchemy[asyncio] | **2.0.46** | Jan 21, 2026 | 3.7+ | Latest in 2.0 branch, stable |
| alembic | **1.18.4** | Latest | 3.7+ | Stable, SQLAlchemy migrations |
| pydantic-settings | **2.x** (with pydantic) | Latest | 3.8+ | Part of pydantic v2 ecosystem |
| pydantic | **2.13.3** | Latest | 3.8+ | Latest stable with 3.14 support |
| python-multipart | **0.0.22** | Jan 25, 2026 | 3.10+ | Latest, production-ready |
| **passlib[bcrypt]** | **1.7.4** | -- | -- | ⚠️ **UNMAINTAINED** - see critical note below |
| **bcrypt** (direct) | **5.0.0** | Latest | 3.7+ | ⚠️ **BREAKS passlib 1.7.4** - incompatible |
| **email-validator** | **2.3.0** | Aug 26, 2025 | 3.8+ | Latest, robust, production-ready |
| gunicorn | **23.0.0** | Latest | 3.10+ | Production WSGI server |

### Dev Dependencies (Latest Stable Versions)

| Package | Version | Released | Notes |
|---------|---------|----------|-------|
| pytest | **9.1** | Latest | Latest stable, actively maintained |
| pytest-cov | **5.x** | Latest | Coverage reporting for pytest |
| pytest-benchmark | **4.0.0** | Latest | Performance benchmarking |
| httpx | **0.27.x** | Latest | FastAPI-compatible async test client |
| ruff | **0.15.1** | Feb 12, 2026 | Latest, includes block suppression comments |
| bandit | **1.9.3** | Jan 19, 2026 | Security scanning, Python 3.10-3.14 |
| locust | **2.43.3** | Feb 12, 2026 | Latest, load testing framework |
| factory-boy | **3.x** | Latest | Test data factories |

---

### ⚠️ CRITICAL DEPENDENCY ISSUE: passlib vs bcrypt

**Problem**: Passlib 1.7.4 is **no longer maintained**, and bcrypt 5.0.0 (latest) introduces a **breaking change** that breaks passlib compatibility.

**Issue Details**:
- Passlib 1.7.4: Last release, unmaintained
- bcrypt 5.0.0: Raises `ValueError` for passwords >72 bytes (previously truncated silently)
- Result: `passlib[bcrypt]` with bcrypt 5.0.0 will fail PIN verification

**Recommended Solutions** (in order of preference):

#### Option 1: Use `bcrypt` directly (RECOMMENDED ✅)
```python
# app/auth/pin.py
import bcrypt

def hash_pin(pin: str) -> str:
    """Hash PIN using bcrypt directly."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pin.encode(), salt).decode()

def verify_pin(pin: str, hash_digest: str) -> bool:
    """Verify PIN against bcrypt hash."""
    return bcrypt.checkpw(pin.encode(), hash_digest.encode())
```

**Advantages**:
- Direct control over bcrypt version
- Avoids unmaintained passlib layer
- Simpler, more transparent code
- bcrypt 5.0.0 is stable and actively maintained

**Action**: Update plan to depend on `bcrypt>=5.0.0` directly instead of `passlib[bcrypt]`.

---

#### Option 2: Pin passlib + bcrypt <5.0 (fallback if needed)
```toml
[tool.uv.dependencies]
passlib = "~1.7.4"
bcrypt = "<5.0"  # Pin to compatible version
```

**Disadvantages**:
- Locks out security updates in bcrypt
- Not recommended for production
- Misses bug fixes in bcrypt 5.0+

---

#### Option 3: Switch to argon2 (alternative)
```python
pip install argon2-cffi  # Modern password hashing
```

**Advantages**:
- More modern than bcrypt
- Better memory-hard algorithm
- Maintained actively

**Disadvantages**:
- Heavier dependency
- Slower than bcrypt (acceptable for PIN use case)

---

### Updated pyproject.toml Template

```toml
[project]
name = "weather-kitchen-api"
version = "1.0.0"
description = "COPPA-compliant recipe discovery API"
requires-python = ">=3.11"
dependencies = [
    # Core API
    "fastapi==0.129.0",
    "uvicorn[standard]==0.40.0",
    "python-multipart==0.0.22",

    # Database
    "sqlalchemy[asyncio]==2.0.46",
    "alembic==1.18.4",

    # Data validation
    "pydantic==2.13.3",
    "pydantic-settings==2.x",
    "email-validator==2.3.0",

    # Security - Use bcrypt directly (not passlib)
    "bcrypt==5.0.0",

    # Production
    "gunicorn==23.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest==9.1",
    "pytest-cov==5.x",
    "pytest-benchmark==4.0.0",
    "httpx==0.27.x",
    "ruff==0.15.1",
    "bandit==1.9.3",
    "locust==2.43.3",
    "factory-boy==3.x",
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=app --cov-report=html"
```

---

### Dependency Update Checklist

- [ ] **Phase 1, Task 2**: Update `pyproject.toml` with pinned versions above
- [ ] **Phase 1, Task 4**: Change auth config to remove passlib references, add bcrypt
- [ ] **app/auth/pin.py**: Implement `hash_pin()` and `verify_pin()` using bcrypt directly (not passlib)
- [ ] **CI/CD** (.github/workflows/backend-ci.yml): Run `pip check` to verify no dependency conflicts
- [ ] **Docker** (Phase 6): Test image builds with updated dependencies
- [ ] **Tests**: Verify PIN hashing tests pass with bcrypt 5.0.0

---

### Compatibility Matrix

| Component | Python 3.11 | Python 3.12 | Python 3.13 | Python 3.14 |
|-----------|:----------:|:----------:|:----------:|:----------:|
| fastapi 0.129.0 | ✅ | ✅ | ✅ | ✅ |
| sqlalchemy 2.0.46 | ✅ | ✅ | ✅ | ✅ |
| bcrypt 5.0.0 | ✅ | ✅ | ✅ | ✅ |
| pytest 9.1 | ✅ | ✅ | ✅ | ✅ |
| ruff 0.15.1 | ✅ | ✅ | ✅ | ✅ |
| **Overall** | **✅ Supported** | **✅ Recommended** | **✅ Supported** | **✅ Emerging** |

**Recommendation**: Use Python 3.12 for optimal balance of stability, performance, and forward compatibility.

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | > 80% | pytest-cov report |
| Security Tests | 50+ passing | pytest tests/security/ |
| Auth Bypass Tests | 15+ passing | pytest tests/security/test_auth_bypass.py |
| Token/PIN Tests | 18+ passing | pytest tests/security/test_token_validation.py + test_pin_bruteforce.py |
| API Response Time | < 100ms p95 | pytest-benchmark |
| Query Count (recipe list) | 1-2 queries | SQLAlchemy query log |
| Gzip Compression | > 90% | Response size comparison |
| Load Test (100 users) | < 500ms p95 | Locust report |
| Ruff Lint | 0 errors | `ruff check` |
| Bandit Scan | 0 high severity | `bandit -r app/` |
| Health Check DB Verify | Always runs | curl http://localhost:8000/health |
| UUID Primary Keys | 100% | SQL schema inspection |
| Error Envelope | Consistent | curl error responses |

---

## Implementation Notes

### Authentication Flow
1. **Family Creation**: `POST /families` returns api_token (one-time, plaintext shown once)
2. **Subsequent Requests**: Include `Authorization: Bearer <token>` header
3. **Token Lookup**: Server computes `sha256(token)`, queries `families` by `api_token_hash` (indexed)
4. **Token Rotation**: `POST /families/{id}/token/rotate` (requires PIN) generates new token, invalidates old
5. **Sensitive Operations**: `POST /families/{id}/purge`, `POST /families/{id}/consent/verify` require PIN verification

### PIN Verification
1. Parent creates family, sets 4-6 digit PIN
2. PIN stored as bcrypt hash on `families` table
3. Failed attempts tracked in `pin_attempts` counter
4. After 5 failures: set `pin_locked_until` = now + 15 minutes
5. Requests during lockout return 423 Locked status
6. Successful PIN verification resets `pin_attempts` to 0

### COPPA Consent Flow
1. Family created without consent initially (consent_given = false)
2. `POST /families/{id}/consent/request` generates 6-digit code
3. Code hashed with sha256, stored in `consent_code_hash` with 30-minute expiry
4. Email "sent" via email_service (console prints for dev, SMTP for prod)
5. Parent calls `POST /families/{id}/consent/verify` with code + admin_pin
6. Code validated (hash comparison, expiry check), if valid: consent_given = true, code cleared
7. New users cannot be added unless consent_given = true

### Error Response Envelope
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Admin PIN must be 4-6 digits",
    "details": [
      {"field": "admin_pin", "message": "Invalid format"}
    ]
  }
}
```

### Transaction Strategy
- **Session-per-request**: FastAPI dependency provides SQLAlchemy session
- **Commit on success**: Session auto-commits on endpoint return (200-201 status)
- **Rollback on exception**: Global error handler catches exceptions, rolls back session
- **Audit log atomicity**: Audit writes share the same session as business operations (both commit/rollback together)
- **Background tasks**: Non-critical audit (read operations) use `BackgroundTasks` to reduce latency

---

## Timeline & Phasing

| Phase | Duration | Focus | Deliverable |
|-------|----------|-------|-------------|
| **Phase 1** | 1-2 weeks | Foundation + Security | Working FastAPI app, security headers, error handling, CI pipeline, UUID models, auth utilities |
| **Phase 2** | 1-2 weeks | Recipe API | Recipe CRUD, filtering, stats, seed data (1,020 recipes), repo tests |
| **Phase 3** | 2-3 weeks | Auth + Family/User | Family/user CRUD, API token auth, PIN verification, consent flow, IDOR tests |
| **Phase 4** | 1-2 weeks | Hardening | Rate limiting, audit logging, security test suite (50+), GDPR data retention |
| **Phase 5** | 1 week | Performance | Query optimization, gzip compression, caching, load testing |
| **Phase 6** | 1 week | DevOps | Docker, CI/CD enhancement, documentation |
| **Total** | **7-8 weeks** | **Full production app** | **Secure, tested, documented, cloud-ready** |

---

**Plan Status**: Phase 4 Ready to Start (Version 2.0 - Security Hardened)
**Last Updated**: February 16, 2026
**Overall Progress**: 108/210 tasks (51%) | Phase 1-3 ✅ Complete | Phase 4-6 ⬜ Pending
**Critical Findings Resolved**: 4 CRITICAL, 9 HIGH, 12 MEDIUM (from security/architecture/cloud design reviews)

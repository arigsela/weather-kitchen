# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Weather Kitchen** is a production-grade recipe discovery app for children aged 6-12, suggesting weather-appropriate meals with ingredient filtering, favorites, multi-user support, and COPPA/GDPR compliance.

**Status**: Backend (Phases 1-4) and Frontend fully implemented.

**Key docs**: PRD (`docs/weather_kitcne_prd.md`), Backend Plan (`docs/BACKEND_IMPLEMENTATION_PLAN.md`), Frontend Plan (`docs/FRONTEND_IMPLEMENTATION_PLAN.md`)

## Tech Stack

**Backend**: FastAPI 0.129+ · Pydantic 2.x · SQLAlchemy 2.0 · SQLite (dev) / PostgreSQL (prod) · PyJWT · bcrypt 5.0 · Alembic · uv · Ruff · Bandit · pytest + httpx · Python 3.12

**Frontend**: React 19 · TypeScript · Vite · Tailwind CSS v4 · React Router v7 · TanStack Query v5 · Zustand v5 · ky · Vitest + Testing Library · MSW

## Common Commands

### Backend (run from `backend/`)

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

### Frontend (run from `frontend/`)

```bash
npm install          # Install dependencies
npm run dev          # Start dev server (localhost:5173, proxies /api to :8000)
npm run build        # Type-check + Vite build
npm run type-check   # tsc --noEmit
npm run lint         # ESLint + Prettier check
npm run format       # Prettier autofix
npm run test         # Vitest run (single pass)
npm run test:watch   # Vitest watch mode
npm run test:coverage # Vitest with coverage
```

## Backend Architecture

### Layered Pattern

```
API Layer (app/api/v1/)       → Route handlers, Pydantic request/response schemas
Service Layer (app/services/) → Business logic, orchestration
Repository Layer (app/repositories/) → SQLAlchemy queries, transactions
Models (app/models/)          → ORM models (all UUID PKs via GUID TypeDecorator)
```

### Key Architectural Decisions

- **GUID TypeDecorator** (`app/database.py`): Cross-DB UUID support — CHAR(36) on SQLite, native UUID on PostgreSQL.
- **JWT auth** (`app/auth/jwt.py`): Access tokens (15min) carry `sub` (family_id) and `type: "access"`. Refresh tokens (7d) carry `jti` for revocation. SHA256 hashes stored in `refresh_tokens` table.
- **Auth dependencies** (`app/auth/dependencies.py`): `get_current_family`, `require_family_owner` (enforces URL family_id matches token), `require_pin` (bcrypt verify with lockout: 5 attempts → 15min lock).
- **Cross-family access returns 404** (not 403) to prevent enumeration.
- **Middleware stack** (`app/main.py`): RequestID → SecurityHeaders → RateLimiter → RequestLogging → ErrorHandler (registered in reverse order).
- **selectinload over joinedload** to avoid cartesian products on N:1 relationships.
- **SQLite WAL mode** enabled via pragma on connect.

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

## Backend Testing

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

## Frontend Architecture

### State & Data Flow

- **Zustand** (`src/store/appStore.ts`): Persists `currentFamilyId`, `currentUserId`, `hasCompletedSetup`, and `refreshToken` to `localStorage`. `accessToken` lives in memory only.
- **TanStack Query**: All server state (recipes, users, favorites, family). Default stale time 5min, gc time 10min.
- **Auth bootstrap** (`src/hooks/useAuth.ts`): On mount, if `refreshToken` exists but `accessToken` doesn't (e.g., page reload), silently exchanges it for a new token pair. Guards against React StrictMode double-invoke via a ref.
- **Token auto-refresh**: `useAuth` schedules a `setTimeout` to refresh 1 minute before `tokenExpiry`.

### API Client (`src/api/client.ts`)

Two ky instances:
- `apiClient` — attaches `Authorization: Bearer <token>` on every request; intercepts 401 to silently refresh and retry once.
- `publicClient` — unauthenticated, for public recipe/stats endpoints.

`VITE_API_URL` env var sets the base URL; falls back to `window.location.origin`. Vite dev server proxies `/api` and `/health` to `http://localhost:8000`.

### Feature Structure (`src/features/`)

Each feature folder co-locates pages, components, and query/mutation hooks:
- `auth/` — LandingPage, LoginPage
- `family/` — FamilySetupPage (signup), UserSelectorPage, FamilySettingsPage
- `recipes/` — RecipeListPage, RecipeDetailPage, RecipeCard, RecipeGrid
- `favorites/` — FavoritesPage, FavoriteButton (with optimistic updates via `useToggleFavorite`)
- `pantry/` — PantryPage (ingredient selection by category)
- `weather/` — WeatherSelector, WeatherCard
- `privacy/` — PrivacyPolicyPage, DataManagementPage

### Routing (`src/App.tsx`)

Protected routes are wrapped in `AuthGuard`, which checks `isAuthenticated` and `hasCompletedSetup` from `useAuth`. Unauthenticated users redirect to `/`. All feature pages are lazy-loaded.

## Security Patterns

- All input validated via Pydantic schemas at API boundary
- All queries via SQLAlchemy ORM (parameterized, no raw SQL)
- PIN lockout: 5 failed attempts → 15-minute lock, tracked on Family model (`pin_attempts`, `pin_locked_until`)
- Rate limiting: 10 req/s general, 5 req/15min for PIN endpoints
- Security headers middleware adds CSP, X-Frame-Options, etc.
- 100KB request body size limit

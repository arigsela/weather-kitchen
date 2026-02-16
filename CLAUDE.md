# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Weather Kitchen** is a production-grade recipe discovery app designed for children aged 6-12. It suggests weather-appropriate meals to families with features including ingredient-based filtering, a favorites system, multi-user support, and full COPPA/GDPR compliance.

**Status**: Pre-implementation (specification phase complete, ~210 backend tasks + ~90 frontend tasks)

**Key Characteristics**:
- Security-first architecture (OWASP Top 10 compliant)
- Zero vulnerabilities target with comprehensive security testing
- Sub-100ms API response times
- >80% test coverage requirement
- Fully COPPA/GDPR compliant
- No external dependencies in core backend

**References**:
- **PRD**: `docs/weather_kitcne_prd.md` (comprehensive requirements and constraints)
- **Backend Plan**: `docs/BACKEND_IMPLEMENTATION_PLAN.md` (6 phases, ~120 tasks)
- **Frontend Plan**: `docs/FRONTEND_IMPLEMENTATION_PLAN.md` (6 phases, ~90 tasks)

---

## Technology Stack

### Backend
| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Framework | FastAPI | 0.129.0 | Async, auto-docs, Pydantic validation |
| Database | SQLite (v1) / PostgreSQL (v2) | - | SQLAlchemy abstracts DB layer |
| ORM | SQLAlchemy | 2.0.46 | Type-safe, async support |
| Migrations | Alembic | 1.18.4 | Standard SQLAlchemy migrations |
| Validation | Pydantic | 2.13.3 | Built into FastAPI |
| Cryptography | bcrypt | 5.0.0 | PIN hashing (not passlib) |
| Authentication | Bearer Token (SHA256) | - | Stateless, high-entropy tokens |
| Testing | pytest + httpx | 9.1 / 0.27 | FastAPI-recommended stack |
| Linting | Ruff | 0.15.1 | Fast, replaces flake8/isort |
| Security Scan | Bandit | 1.9.3 | Python security linting |
| Load Testing | Locust | 2.43.3 | Python-native load testing |
| Package Manager | uv | latest | Fast Python dependency management |

### Frontend
| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Framework | React | 19.2.4 | Latest stable, component-based |
| Language | TypeScript | 5.6.x | Type safety at build time |
| Build Tool | Vite | 7.3.1 | Fast HMR, modern ESM-first |
| Routing | React Router | 7.13.0 | Nested layouts, SPA routing |
| State (Server) | TanStack Query | 5.90.21 | Caching, background refetch |
| State (Client) | Zustand | 5.0.11 | Lightweight, simple API |
| Styling | Tailwind CSS | 4.1.18 | Utility-first, child-friendly |
| HTTP Client | ky | 1.14.3 | Lightweight fetch wrapper |
| Testing | Vitest + RTL | 4.0.18 / 16.3.2 | Vite-native, fast |
| E2E Testing | Playwright | 1.58.2 | Cross-browser, reliable |
| Icons | Lucide React | 0.564.0 | Tree-shakeable icon set |
| Linting | ESLint + Prettier | 8.x / 3.x | Standard React/TS linting |

---

## Architecture Overview

### Layered Architecture Pattern

```
Frontend (React + TypeScript)
    ↓ (REST API calls)
API Layer (FastAPI endpoints + Pydantic validation)
    ↓
Business Logic Layer (Services: filtering, calculations, auth)
    ↓
Data Access Layer (Repositories: queries, transactions)
    ↓
Database Layer (SQLAlchemy ORM + SQLite/PostgreSQL)
```

### Key Architectural Decisions

1. **UUID-Based Primary Keys**: All entities use UUID v4 (hexadecimal, no enumeration risk)
2. **Family-Scoped API Tokens**: Stateless bearer token authentication with SHA256 hashing
3. **PIN-Protected Sensitive Operations**: PIN verification (bcrypt) required for token rotation, purge, consent verification
4. **Security Distributed Across Phases**: Not deferred to Phase 4 (headers, validation, auth in Phase 1-3)
5. **Selectinload Over Joinedload**: Avoid cartesian product from N:1 relationships
6. **Single Query Per Endpoint**: Target 1-2 database queries per API call
7. **Consistent Error Envelopes**: All errors wrapped in `ErrorResponse` with code/message/details
8. **Soft Delete + GDPR Purge**: Family soft-delete, then hard-delete after 30 days

### REST API Principles
- **Idempotent Writes**: PUT for ingredients (replace), favorites (PUT add, DELETE remove)
- **Proper Status Codes**: 200/201 success, 400/422 validation, 401/403 auth, 404/409 conflicts, 429 rate limit
- **No Side Effects on GET**: All GET requests are read-only
- **Pagination**: All list endpoints paginated (default 20 per page)
- **Request Body Size Limit**: 100KB max to prevent DoS

---

## Project Structure

### Backend (`backend/`)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry, middleware registration
│   ├── config.py                  # Pydantic Settings (env vars)
│   ├── database.py                # SQLAlchemy engine, GUID TypeDecorator
│   ├── dependencies.py            # FastAPI Depends() providers
│   ├── constants.py               # Weather types, categories, limits
│   ├── models/                    # SQLAlchemy ORM models (all UUID PKs)
│   ├── schemas/                   # Pydantic request/response models
│   ├── api/v1/                    # Route handlers (recipes, families, users, stats)
│   ├── services/                  # Business logic (filtering, auth, CRUD)
│   ├── repositories/              # Data access layer (queries, transactions)
│   ├── auth/                      # Authentication utilities (token, PIN)
│   ├── middleware/                # Security headers, logging, rate limiting
│   ├── tasks/                     # Scheduled tasks (30-day purge, 90-day TTL)
│   └── seed/                      # Recipe seeding (extract + load JSON)
├── alembic/                       # Database migrations
├── tests/                         # pytest suite (unit, integration, security, performance)
├── pyproject.toml                 # Project config, dependencies
├── alembic.ini                    # Alembic config
├── Dockerfile                     # Multi-stage production build
├── docker-compose.yml             # Dev environment setup
├── .env.example                   # Environment variable template
├── Makefile                       # Common commands
└── README.md                      # Setup guide + auth documentation
```

### Frontend (`frontend/`)
```
frontend/
├── src/
│   ├── main.tsx                   # React DOM entry point
│   ├── App.tsx                    # Root: providers, router, layout
│   ├── api/                       # API client (HTTP, types)
│   ├── components/
│   │   ├── ui/                    # Primitives (Button, Card, etc.)
│   │   └── layout/                # AppLayout, Header, Footer
│   ├── features/                  # Feature modules (collocated)
│   │   ├── weather/               # Weather selection
│   │   ├── recipes/               # Recipe discovery
│   │   ├── pantry/                # Ingredient management
│   │   ├── favorites/             # Favorites system
│   │   ├── family/                # User/family management
│   │   └── privacy/               # COPPA/GDPR compliance
│   ├── hooks/                     # Custom hooks (state, multiplier)
│   ├── store/                     # Zustand client state
│   ├── types/                     # TypeScript interfaces
│   ├── utils/                     # Helper functions
│   ├── constants/                 # Weather, categories, ingredients
│   └── styles/                    # Global styles (Tailwind)
├── tests/                         # Vitest + Playwright tests
├── vite.config.ts                 # Vite build config
├── tsconfig.json                  # TypeScript config
├── tailwind.config.ts             # Tailwind theme (child-friendly)
├── eslint.config.js               # ESLint flat config
├── prettier.config.js             # Prettier formatting
├── playwright.config.ts           # E2E testing config
├── Dockerfile                     # nginx SPA serving
└── nginx.conf                     # SPA routing config
```

---

## Development Workflow

### Backend Setup & Development

**Initial Setup**:
```bash
cd backend
uv sync                          # Install all dependencies
cp .env.example .env             # Create environment file
uv run alembic upgrade head      # Run migrations
uv run python -m app.seed.seed_recipes  # Seed 1,020 recipes
uv run uvicorn app.main:app --reload    # Start dev server (http://localhost:8000)
```

**Common Commands** (see `backend/Makefile`):
```bash
make dev           # Start dev server with auto-reload
make test          # Run full test suite (unit + integration + security)
make test-unit     # Unit tests only (fast)
make test-security # Security tests only
make lint          # Run Ruff linter
make format        # Format code with Ruff
make seed          # Seed 1,020 recipes
make migrate       # Run Alembic migrations
make purge         # Hard-delete soft-deleted families (30-day grace period)
```

**Access Points**:
- **API**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

### Frontend Setup & Development

**Initial Setup**:
```bash
cd frontend
npm install                # Install dependencies
cp .env.example .env       # Create environment file (VITE_API_URL=http://localhost:8000)
npm run dev                # Start Vite dev server (http://localhost:5173)
```

**Common Commands**:
```bash
npm run dev          # Start dev server with HMR
npm run build        # Production build
npm run preview      # Preview production build
npm run type-check   # TypeScript type checking
npm run lint         # ESLint + Prettier check
npm run format       # Auto-format code
npm run test         # Vitest unit + integration tests
npm run test:ui      # Vitest with UI dashboard
npm run test:coverage # Coverage report
npm run test:e2e     # Playwright E2E tests (headless)
npm run test:e2e:ui  # Playwright E2E tests (UI mode)
```

**Access Points**:
- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000` (proxied or direct)

### Running Full Stack

**Option 1: Docker Compose (Backend + Frontend)**:
```bash
docker-compose up  # Starts backend + frontend in containers
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

**Option 2: Local Development**:
```bash
# Terminal 1: Backend
cd backend && make dev

# Terminal 2: Frontend
cd frontend && npm run dev

# Visit http://localhost:5173 (frontend auto-proxies to http://localhost:8000)
```

---

## Common Development Tasks

### Adding a New API Endpoint

1. **Define Pydantic Schema** (`app/schemas/your_domain.py`):
   ```python
   class YourRequest(BaseModel):
       field_name: str  # Include validation

   class YourResponse(BaseModel):
       id: UUID
       field_name: str
   ```

2. **Create Repository Method** (`app/repositories/your_repo.py`):
   ```python
   def get_something(self, id: UUID) -> Model:
       # Use selectinload for relationships
       return self.db.query(Model).filter(...).first()
   ```

3. **Create Service Method** (`app/services/your_service.py`):
   ```python
   def process_something(self, id: UUID) -> YourResponse:
       entity = self.repo.get_something(id)
       # Business logic here
       return YourResponse.from_orm(entity)
   ```

4. **Add Route Handler** (`app/api/v1/your_routes.py`):
   ```python
   @router.get("/api/v1/your-endpoint/{id}")
   async def get_your_endpoint(id: UUID, db: Session = Depends(get_db)):
       service = YourService(db)
       return service.process_something(id)
   ```

5. **Write Tests**:
   - **Unit test**: `tests/unit/test_your_service.py` (business logic)
   - **Integration test**: `tests/integration/test_your_endpoints.py` (full flow)
   - **Security test**: `tests/security/test_your_endpoint_security.py` (auth, validation, injection)

6. **Register Route** (`app/api/v1/router.py`):
   ```python
   router.include_router(your_routes.router)
   ```

### Adding a Feature Component (Frontend)

1. **Create Feature Module** (`src/features/your_feature/`):
   ```
   YourFeaturePage.tsx       # Main page component
   YourFeatureCard.tsx       # Card/detail component
   useYourFeature.ts         # TanStack Query hook (fetch)
   useYourFeatureMutation.ts # TanStack Query hook (create/update)
   constants.ts              # Feature-specific constants (optional)
   ```

2. **Create API Functions** (`src/api/your_feature.ts`):
   ```typescript
   export async function fetchYourFeature(id: string) {
     return apiClient.get(`/api/v1/your-endpoint/${id}`);
   }
   ```

3. **Create Types** (`src/types/your_feature.ts`):
   ```typescript
   export interface YourFeature {
     id: string;
     name: string;
   }
   ```

4. **Add Route** (`src/App.tsx`):
   ```typescript
   {
     path: "/your-feature",
     element: <YourFeaturePage />,
   }
   ```

5. **Write Tests**:
   - **Unit**: Component behavior, hooks
   - **Integration**: Full feature flow
   - **E2E**: User-facing workflows

---

## Authentication & Authorization

### API Token Authentication Flow

1. **Family Creation**: `POST /api/v1/families`
   - Accepts `admin_pin` (4-6 digit numeric)
   - Returns one-time plaintext `api_token` (shown once to user)
   - Backend stores `api_token_hash` (SHA256) in database

2. **Subsequent Requests**: Include `Authorization: Bearer <token>` header
   - Server computes `sha256(token)`, queries families by `api_token_hash` (indexed)
   - Returns 401 if token invalid or missing
   - Request proceeds with family context

3. **Token Rotation**: `POST /api/v1/families/{id}/token/rotate` (requires PIN)
   - Generates new token, invalidates old
   - Returns new plaintext token
   - Old token immediately stops working

### PIN Protection (for Sensitive Operations)

1. **PIN Lockout**: 5 failed attempts → 15-minute lockout
   - Tracked in `pin_attempts` and `pin_locked_until` fields
   - Requests during lockout return 423 status
   - Successful verification resets counter

2. **Sensitive Operations Requiring PIN**:
   - `POST /api/v1/families/{id}/token/rotate` (new token)
   - `POST /api/v1/families/{id}/purge` (hard delete)
   - `POST /api/v1/families/{id}/consent/verify` (parental consent)

### Cross-Family Access Prevention

All user/family endpoints enforce ownership:
- Endpoint receives family_id in URL
- Server verifies Bearer token's family_id matches URL family_id
- **Mismatch returns 404** (not 403) to prevent enumeration

---

## Testing Strategy

### Coverage Targets
- **Overall**: >80% code coverage
- **Critical paths**: 100% (auth, validation, calculation)
- **Security validators**: 100%

### Test Organization

```
tests/
├── conftest.py                 # Fixtures (DB, client, factories, auth_headers)
├── factories.py                # Test data factories (UUID-based IDs)
├── unit/                       # 70% of tests
│   ├── test_recipe_service.py
│   ├── test_family_service.py
│   ├── test_auth.py
│   └── test_validators.py
├── integration/                # 20% of tests
│   ├── test_recipe_endpoints.py
│   ├── test_family_endpoints.py
│   ├── test_user_endpoints.py
│   └── test_auth_flows.py
├── security/                   # 10% of tests (50+)
│   ├── test_auth_bypass.py     # 15+ tests
│   ├── test_xss_payloads.py    # 20+ tests
│   ├── test_sql_injection.py   # 15+ tests
│   ├── test_rate_limiting.py
│   ├── test_idor.py
│   └── test_input_validation.py
└── performance/
    ├── test_benchmarks.py
    └── locustfile.py
```

### Running Tests

```bash
# Backend
make test                # Full suite (< 30 seconds)
make test-unit           # Fast unit tests only (< 5 seconds)
pytest -k auth           # Run tests matching keyword
pytest --cov            # Coverage report
pytest -v tests/security/ --tb=short  # Verbose security tests

# Frontend
npm run test             # Vitest (unit + integration)
npm run test:coverage    # Coverage report
npm run test:e2e         # Playwright E2E
```

### Test Data Factories

```python
# tests/factories.py
class RecipeFactory:
    @staticmethod
    def create(name="Test Recipe", weather="sunny"):
        return Recipe(id=uuid4(), name=name, weather=weather, ...)

class FamilyFactory:
    @staticmethod
    def create(name="Test Family", family_size=4):
        token, token_hash = generate_api_token()
        return Family(id=uuid4(), name=name, api_token_hash=token_hash, ...)

# Usage in tests
def test_recipe_filtering(db):
    recipe = RecipeFactory.create(weather="rainy")
    db.add(recipe)
    db.commit()
    assert recipe.weather == "rainy"
```

---

## Security Considerations

### Key Security Patterns

1. **Input Validation** (at system boundary):
   - Pydantic strict validation on all schemas
   - Type checking, length limits, regex patterns
   - Email format validation, enum whitelisting
   - 100KB request body size limit

2. **Output Encoding**:
   - No `innerHTML` in frontend (always use `textContent`)
   - FastAPI auto-escapes JSON responses
   - Content-Security-Policy headers prevent inline scripts

3. **SQL Injection Prevention**:
   - All queries use SQLAlchemy ORM (parameterized)
   - No dynamic SQL string construction
   - Tested with 15+ SQL injection payloads

4. **XSS Prevention**:
   - No `eval()`, `Function()`, or `dangerouslySetInnerHTML`
   - Content-Security-Policy: `default-src 'self'`
   - Tested with 20+ XSS payloads

5. **CSRF Protection**:
   - Backend uses Bearer token auth (stateless, no cookies)
   - Frontend sends token in `Authorization` header
   - CORS configured to prevent cross-origin requests
   - **Result**: CSRF vulnerability doesn't apply to Bearer tokens

6. **Authentication**:
   - API tokens: SHA256(high-entropy token)
   - PIN: bcrypt with 12 rounds
   - Token rotation invalidates old token immediately
   - PIN lockout after 5 failures (15-minute grace)

7. **Rate Limiting**:
   - General tier: 10 requests/second per IP
   - PIN endpoints tier: 5 requests/15 minutes per IP
   - Returns 429 when limit exceeded
   - In-memory sliding window implementation

8. **Audit Logging**:
   - All state-changing operations logged
   - Includes IP address, timestamp, action, family_id
   - Non-critical reads use BackgroundTasks to avoid latency impact
   - 90-day retention for GDPR

### Sensitive Operations Checklist

Before implementing any endpoint handling sensitive data (auth, tokens, PII):
- [ ] Input validation on all parameters
- [ ] Output doesn't leak implementation details
- [ ] Rate limiting applied (if brute-forceable)
- [ ] Audit log entry created
- [ ] Error messages safe (no stack traces)
- [ ] Tests include security payloads (XSS, SQL injection)
- [ ] IDOR test (cross-family access attempt)

---

## Performance Goals & Optimization

### Target Metrics
- **API Response**: <100ms p95 (server-side)
- **Page Load**: <1s p95 (full load with gzip)
- **Recipe Search**: <200ms p95
- **Database Query**: <5ms per query
- **Concurrent Users**: 100+ with <500ms p95 latency
- **Gzip Compression**: 90%+ reduction on JSON
- **Bundle Size (Frontend)**: <200KB gzipped

### Database Optimization

1. **Selectinload Over Joinedload**:
   ```python
   # ✅ GOOD: Two queries, no cartesian product
   query(Recipe).options(selectinload(Recipe.ingredients))

   # ❌ BAD: Cartesian product (recipe × ingredients rows)
   query(Recipe).options(joinedload(Recipe.ingredients))
   ```

2. **Composite Indexes**:
   - `(weather)` on recipes (filter by weather)
   - `(category)` on recipes (filter by category)
   - `(recipe_id, sort_order)` on recipe_ingredients
   - `(user_id, recipe_id)` UNIQUE on user_favorites (prevent duplicates)
   - `(api_token_hash)` UNIQUE indexed on families (fast token lookup)

3. **Query Optimization**:
   - Verify recipe list query: 1 query (not N+1)
   - User favorites list: 1 query with selectinload
   - All endpoints: target 1-2 queries per request

4. **Connection Pooling**:
   - SQLite: StaticPool (pool_size=1)
   - PostgreSQL: pool_size=5, max_overflow=10
   - SQLite WAL mode for concurrent read/write

### Frontend Optimization

1. **Code Splitting**: React.lazy() for route pages
2. **Suspense Boundaries**: Loading fallbacks on lazy pages
3. **TanStack Query Caching**: Background refetch, stale-while-revalidate
4. **Bundle Analysis**: Verify tree-shaking with `vite-plugin-inspect`
5. **Image Optimization**: If using images, use Vite's image optimization

---

## COPPA/GDPR Compliance

### Key Requirements

1. **COPPA (Children's Online Privacy Protection Act)**:
   - Age gate: "Is the main user under 13?"
   - Verifiable parental consent (email verification)
   - Data deletion on parent request (`DELETE /api/v1/families/{id}`)
   - No targeted advertising or third-party tracking
   - Privacy policy accessible (footer link)

2. **GDPR (if serving EU families)**:
   - Privacy policy with data collection explanation
   - Data export: `GET /api/v1/families/{id}/export` (all family data as JSON)
   - Data deletion: `DELETE /api/v1/families/{id}` (soft delete, hard delete after 30 days)
   - Data retention: Audit logs 90 days, activity logs 1 year

3. **Consent Flow**:
   - Family creation: consent_given = false initially
   - Parent calls `POST /api/v1/families/{id}/consent/request` (generates 6-digit code)
   - Backend "sends" code via email_service (console in dev, SMTP in prod)
   - Parent calls `POST /api/v1/families/{id}/consent/verify` with code + admin_pin
   - If valid: consent_given = true, new users can be added

4. **Data Purge**:
   - Soft delete: is_active = false
   - After 30 days: hard delete (purge task runs nightly)
   - Audit logs: retained 90 days, then deleted

---

## Common Issues & Solutions

### Dependency Issues

**Problem**: `passlib[bcrypt]` conflicts with bcrypt 5.0
- **Solution**: Use `bcrypt>=5.0.0` directly (not passlib)
- See backend implementation plan for PIN hashing code

**Problem**: TypeScript 6.0 beta (use 5.x for stability)
- **Solution**: Pin to `typescript ~5.6.x` until 6.0 GA

### Database Migration

**Problem**: Need to add a new column
1. Modify model in `app/models/your_model.py`
2. Create migration: `alembic revision --autogenerate -m "add_new_column"`
3. Review migration in `alembic/versions/`
4. Apply: `alembic upgrade head`

**Problem**: Need to reset database
```bash
# Drop all tables, rerun migrations, reseed recipes
rm backend/app.db  # Delete SQLite file
make migrate       # Run fresh migrations
make seed          # Reseed 1,020 recipes
```

### Authentication Debugging

**Problem**: "401 Unauthorized" on authenticated endpoint
1. Verify `Authorization: Bearer <token>` header present
2. Check token was created with `POST /api/v1/families`
3. Verify token SHA256 hash matches `families.api_token_hash`
4. Try rotating token with PIN to get fresh token

**Problem**: PIN lockout (423 response)
1. Verify 5+ failed PIN attempts didn't occur
2. Check `pin_locked_until` timestamp hasn't expired (15 minutes)
3. Wait 15 minutes or reset with admin tools

### Performance Debugging

**Problem**: Slow recipe list query
1. Enable SQLAlchemy query logging: `echo=True` in database.py
2. Verify only 1 query executed (not N+1)
3. Check `selectinload` used for relationships
4. Run benchmark: `pytest tests/performance/test_benchmarks.py`

**Problem**: Slow frontend load
1. Run Lighthouse: `npm run test:e2e` (includes Lighthouse in CI)
2. Check bundle size: `npm run build` (look for gzip size)
3. Verify code splitting: routes should lazy-load
4. Check TanStack Query cache headers

---

## Key Files Quick Reference

### Backend Critical Files
- **Entry Point**: `app/main.py` (FastAPI app, middleware registration)
- **Auth**: `app/auth/token.py`, `app/auth/pin.py`, `app/auth/dependencies.py`
- **Database**: `app/database.py` (engine, GUID TypeDecorator, session)
- **Models**: `app/models/base.py` (UUID mixin, timestamp mixin)
- **Schemas**: `app/schemas/common.py` (ErrorResponse, PaginationParams)
- **Middleware**: `app/middleware/error_handler.py`, `security_headers.py`, `request_logging.py`
- **Tests**: `tests/conftest.py` (fixtures, factories, auth helpers)

### Frontend Critical Files
- **Entry Point**: `src/main.tsx` (React DOM)
- **Router**: `src/App.tsx` (React Router, providers)
- **API Client**: `src/api/client.ts` (HTTP config, retry logic)
- **Store**: `src/store/appStore.ts` (Zustand for currentUser, currentFamily)
- **Types**: `src/types/` (TypeScript interfaces matching backend)
- **Layout**: `src/components/layout/AppLayout.tsx` (header, footer, content)
- **Tests**: `tests/setup.ts` (Vitest, MSW setup)

---

## Continuous Integration & Deployment

### CI/CD Expectations

**Backend CI** (`.github/workflows/backend-ci.yml`):
```
1. Ruff lint check (0 errors)
2. pytest unit + integration tests (< 5 seconds)
3. Security tests (50+ passing)
4. Bandit security scan (0 high severity)
5. Coverage report (fail if <80%)
6. Docker build validation
```

**Frontend CI** (`.github/workflows/frontend-ci.yml`):
```
1. ESLint + Prettier check
2. TypeScript type checking
3. Vitest unit + integration tests
4. Code coverage (fail if <80%)
5. Playwright E2E tests (Chrome, Firefox, Safari)
6. Lighthouse performance audit (>90)
7. Docker build validation
```

### Deployment Checklist

- [ ] All tests passing in CI
- [ ] Coverage > 80%
- [ ] No high/critical security findings
- [ ] Performance benchmarks meet targets
- [ ] Database migrations tested (up + down)
- [ ] Docker image builds successfully
- [ ] Environment variables configured
- [ ] Monitoring/alerting configured
- [ ] Backup strategy tested

---

## Useful Commands Summary

### Backend
```bash
cd backend

# Development
make dev              # Start uvicorn with auto-reload
make test             # Run all tests
make lint             # Lint with Ruff
make format           # Format with Ruff
make migrate          # Run Alembic migrations
make seed             # Seed 1,020 recipes

# Debugging
pytest tests/unit/test_auth.py -v        # Verbose auth tests
pytest --cov app --cov-report=html       # Coverage report
python -c "from app.auth.token import generate_api_token; print(generate_api_token())"  # Generate test token
```

### Frontend
```bash
cd frontend

# Development
npm run dev            # Start Vite dev server
npm run test           # Vitest (unit + integration)
npm run test:e2e       # Playwright E2E
npm run build          # Production build
npm run type-check     # TypeScript checking
npm run lint           # ESLint + Prettier

# Debugging
npm run test:ui        # Vitest dashboard
npm run test:e2e:ui    # Playwright UI mode
npm run build -- --sourcemap  # Build with source maps
```

### Docker
```bash
# Backend
docker build -f backend/Dockerfile -t weather-kitchen-api:latest backend/
docker run -p 8000:8000 weather-kitchen-api:latest

# Frontend
docker build -f frontend/Dockerfile -t weather-kitchen-web:latest frontend/
docker run -p 3000:3000 weather-kitchen-web:latest

# Full Stack
docker-compose up
```

---

## References & Documentation

**Product Requirements**: `docs/weather_kitcne_prd.md`
- Full feature specifications
- Data model schema
- Security requirements (OWASP Top 10)
- Performance targets
- Testing requirements
- Compliance (COPPA/GDPR)

**Backend Implementation Plan**: `docs/BACKEND_IMPLEMENTATION_PLAN.md`
- 6 phases with detailed task breakdown
- Technology choices and rationale
- Database schema with UUID PKs and auth columns
- API endpoint specifications (21 endpoints)
- Authentication flow details
- PIN verification strategy
- Dependency management (passlib/bcrypt issue resolution)

**Frontend Implementation Plan**: `docs/FRONTEND_IMPLEMENTATION_PLAN.md`
- 6 phases with detailed task breakdown
- Route map and component structure
- Design system tokens (Tailwind theme)
- State management architecture
- TanStack Query caching strategy
- E2E testing approach

---

## Contact & Questions

If you encounter issues or have questions:
1. Check `docs/BACKEND_IMPLEMENTATION_PLAN.md` or `docs/FRONTEND_IMPLEMENTATION_PLAN.md` for phase-specific guidance
2. Review `docs/weather_kitcne_prd.md` for product context
3. Check test files for usage examples
4. Review error handling patterns in middleware (error_handler.py)

---

**Last Updated**: February 16, 2026
**Project Status**: Pre-implementation (specifications complete, 210+ backend tasks, 90+ frontend tasks)
**Maintenance**: Update this file whenever major architectural decisions are made or critical patterns emerge.

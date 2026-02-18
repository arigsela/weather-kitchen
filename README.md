# Weather Kitchen

A recipe discovery app that suggests weather-appropriate meals to families. Features ingredient-based filtering, a per-user favorites system, multi-user family accounts, and JWT authentication.

---

## Project Structure

```
weather-kitcen/
├── backend/          # FastAPI REST API (Python 3.12)
├── frontend/         # React 19 + TypeScript (not yet implemented)
└── docs/             # PRD, implementation plans, deployment guides
```

---

## Backend

Production-grade FastAPI backend with JWT authentication, rate limiting, audit logging, and OWASP Top 10 compliance.

**Status**: All 6 phases complete ✅ — 303 tests, 85.76% coverage

### Quick Start

```bash
cd backend
uv sync
cp .env.example .env          # Set JWT_SECRET_KEY
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

API: `http://localhost:8000` | Swagger UI: `http://localhost:8000/docs`

### Docker

```bash
cd backend
docker compose up             # Dev (SQLite, hot-reload)
```

See [`backend/README.md`](backend/README.md) for full documentation.

---

## Authentication

Weather Kitchen uses **JWT Bearer tokens**.

1. `POST /api/v1/families` — create family, returns `access_token` + `refresh_token`
2. Include `Authorization: Bearer <access_token>` on protected requests
3. Access tokens expire in **15 minutes** — use `POST /api/v1/auth/refresh` to renew
4. `POST /api/v1/auth/logout` revokes the refresh token

---

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/families` | Create family + get JWT tokens |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `POST` | `/api/v1/auth/logout` | Revoke refresh token |
| `GET` | `/api/v1/recipes` | Browse recipes (weather, category, ingredients) |
| `GET` | `/api/v1/families/{id}` | Family details (requires auth) |
| `POST` | `/api/v1/users` | Create user in family (requires auth) |
| `PUT` | `/api/v1/users/{id}/ingredients` | Save pantry ingredients |
| `PUT` | `/api/v1/users/{id}/favorites/{recipe_id}` | Add favourite recipe |
| `GET` | `/health` | Health check |

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.129 |
| Auth | JWT (PyJWT, HS256) + bcrypt PIN |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 + Alembic |
| Validation | Pydantic v2 |
| Testing | pytest + 303 tests |

### Frontend *(planned)*
| Component | Technology |
|-----------|-----------|
| Framework | React 19 + TypeScript |
| Build | Vite 7 |
| State | TanStack Query + Zustand |
| Styling | Tailwind CSS v4 |

---

## Development

### Backend
```bash
cd backend
make test          # Run 303 tests
make lint          # Ruff linter
make format        # Ruff formatter
make migrate       # Run Alembic migrations
make seed          # Seed 1,020 recipes
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | **Yes (prod)** | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | No | Default: SQLite file |
| `ENVIRONMENT` | No | `development` / `production` |

See [`backend/.env.example`](backend/.env.example) for all variables.

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/weather_kitcne_prd.md`](docs/weather_kitcne_prd.md) | Product requirements |
| [`docs/BACKEND_IMPLEMENTATION_PLAN.md`](docs/BACKEND_IMPLEMENTATION_PLAN.md) | Backend phases 1-6 (complete) |
| [`docs/FRONTEND_IMPLEMENTATION_PLAN.md`](docs/FRONTEND_IMPLEMENTATION_PLAN.md) | Frontend phases 1-6 (planned) |
| [`backend/README.md`](backend/README.md) | Backend quickstart + curl examples |

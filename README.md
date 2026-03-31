# Weather Kitchen

A recipe discovery app that suggests weather-appropriate meals to families. Created with love by Eli 💛 — who also wrote all the recipe tips. Features per-user favorites, multi-user family accounts, and JWT authentication.

---

## Project Structure

```
weather-kitcen/
├── backend/          # FastAPI REST API (Python 3.12)
├── frontend/         # React 19 + TypeScript + Vite
└── docs/             # PRD, implementation plans
```

---

## Quick Start

### Backend

```bash
cd backend
uv sync
cp .env.example .env          # Set JWT_SECRET_KEY
uv run alembic upgrade head
uv run python -m app.seed.seed_recipes   # Seed recipes
make dev                       # http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

The frontend proxies `/api` requests to the backend automatically.

### Docker

```bash
cd backend && docker compose up    # Backend on :8000
```

---

## Authentication

Weather Kitchen uses **JWT Bearer tokens** with password-based auth (no PINs).

1. `POST /api/v1/families` — create family with username + password, returns `access_token` + `refresh_token`
2. `POST /api/v1/auth/login` — log in to an existing family
3. Include `Authorization: Bearer <access_token>` on protected requests
4. Access tokens expire in **15 minutes** — use `POST /api/v1/auth/refresh` to renew
5. `POST /api/v1/auth/logout` revokes the refresh token

---

## Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/families` | Create family + get JWT tokens |
| `POST` | `/api/v1/auth/login` | Login with username + password |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `POST` | `/api/v1/auth/logout` | Revoke refresh token |
| `GET` | `/api/v1/recipes` | Browse recipes (weather, category, ingredients) |
| `GET` | `/api/v1/recipes/{id}` | Recipe detail with ingredients and steps |
| `GET` | `/api/v1/stats/recipes-per-weather` | Recipe count by weather type |
| `POST` | `/api/v1/users` | Create user in family (requires auth) |
| `GET` | `/api/v1/users` | List family users (requires auth) |
| `PUT` | `/api/v1/users/{id}/favorites/{recipe_id}` | Add favourite recipe |
| `DELETE` | `/api/v1/users/{id}/favorites/{recipe_id}` | Remove favourite recipe |
| `GET` | `/api/v1/users/{id}/favorites` | List favourite recipes |
| `GET` | `/health` | Health check |

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.129 |
| Auth | JWT (PyJWT, HS256) + bcrypt passwords |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 + Alembic |
| Validation | Pydantic v2 |
| Testing | pytest (303 tests, 82% coverage) |
| CI | GitHub Actions (lint, test, security scan, Docker build) |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 19 + TypeScript 5.9 |
| Build | Vite 8 |
| Server State | TanStack Query v5 |
| Client State | Zustand v5 |
| Styling | Tailwind CSS v4 |
| HTTP | ky (JWT auto-refresh interceptor) |

---

## Development

### Backend
```bash
cd backend
make test          # Run 303 tests
make lint          # Ruff linter
make format        # Ruff formatter
make seed          # Seed recipes
```

### Frontend
```bash
cd frontend
npm run type-check  # TypeScript check
npm run lint        # ESLint + Prettier
npm run test        # Vitest
npm run build       # Production build
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | **Yes (prod)** | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | No | Default: SQLite file |
| `VITE_API_URL` | No | Frontend API base URL (defaults to Vite proxy) |

See [`backend/.env.example`](backend/.env.example) and [`frontend/.env.example`](frontend/.env.example).

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/weather_kitcne_prd.md`](docs/weather_kitcne_prd.md) | Product requirements |
| [`docs/BACKEND_IMPLEMENTATION_PLAN.md`](docs/BACKEND_IMPLEMENTATION_PLAN.md) | Backend phases 1-6 (complete) |
| [`docs/FRONTEND_IMPLEMENTATION_PLAN.md`](docs/FRONTEND_IMPLEMENTATION_PLAN.md) | Frontend phases 1-6 (complete) |
| [`backend/README.md`](backend/README.md) | Backend quickstart + curl examples |
| [`frontend/README.md`](frontend/README.md) | Frontend quickstart + architecture |

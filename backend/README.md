# Weather Kitchen — Backend API

FastAPI backend for the Weather Kitchen recipe discovery app. Provides a REST API with JWT authentication, rate limiting, audit logging, and OWASP Top 10 compliance.

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env — set JWT_SECRET_KEY to a secure random value:
# python -c "import secrets; print(secrets.token_hex(32))"

# 3. Run migrations
uv run alembic upgrade head

# 4. (Optional) Seed recipes
uv run python -m app.seed.seed_recipes

# 5. Start the server
uv run uvicorn app.main:app --reload
```

API available at `http://localhost:8000` | Swagger UI at `http://localhost:8000/docs`

---

## Authentication

Weather Kitchen uses **JWT Bearer token authentication**.

### 1. Create a family (get tokens)

Username must be 3–30 characters — letters, numbers, underscores, and hyphens only (no spaces).
Password must be at least 8 characters and include uppercase, lowercase, and a number.

```bash
curl -X POST http://localhost:8000/api/v1/families \
  -H "Content-Type: application/json" \
  -d '{"name": "smith_family", "family_size": 4, "password": "Secret123"}'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "smith_family",
  "family_size": 4,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

> **Save the `refresh_token` securely** — it is used to obtain new access tokens.

### Login (returning families)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"name": "smith_family", "password": "Secret123"}'
```

Returns the same token structure as family creation.

### 2. Use the access token

```bash
curl http://localhost:8000/api/v1/families/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Refresh when the access token expires (15 minutes)

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

Returns a **new access + refresh token pair**. The old refresh token is immediately revoked (rotation).

### 4. Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

### 5. Rotate all tokens (password-protected)

Revokes all existing refresh tokens and issues a new pair. Requires the family password.

```bash
curl -X POST http://localhost:8000/api/v1/families/{id}/token/rotate \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"password": "Secret123"}'
```

---

## Token Lifetime Summary

| Token | TTL | Storage | Revocable |
|-------|-----|---------|-----------|
| Access token | 15 minutes | Client memory | No (short-lived) |
| Refresh token | 7 days | Secure storage | Yes (DB blocklist) |

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/families` | None | Create family (username + password), returns JWT pair |
| `POST` | `/api/v1/auth/login` | None | Login with username + password, returns JWT pair |
| `GET` | `/api/v1/families/{id}` | Bearer | Get family details |
| `PUT` | `/api/v1/families/{id}` | Bearer | Update family |
| `DELETE` | `/api/v1/families/{id}` | Bearer | Soft delete family |
| `POST` | `/api/v1/families/{id}/purge` | Bearer + password | Hard delete family |
| `GET` | `/api/v1/families/{id}/export` | Bearer | GDPR data export |
| `POST` | `/api/v1/families/{id}/token/rotate` | Bearer + password | Revoke all tokens, issue new pair |
| `POST` | `/api/v1/auth/refresh` | None | Refresh access token |
| `POST` | `/api/v1/auth/logout` | None | Revoke refresh token |
| `GET` | `/api/v1/recipes` | None | List/filter recipes |
| `GET` | `/api/v1/recipes/{id}` | None | Get recipe details |
| `POST` | `/api/v1/users` | Bearer | Create user in family |
| `GET` | `/api/v1/users/{id}` | Bearer | Get user details |
| `PUT` | `/api/v1/users/{id}` | Bearer | Update user |
| `DELETE` | `/api/v1/users/{id}` | Bearer | Delete user |
| `PUT` | `/api/v1/users/{id}/ingredients` | Bearer | Replace ingredient list |
| `GET` | `/api/v1/users/{id}/ingredients` | Bearer | Get ingredient list |
| `PUT` | `/api/v1/users/{id}/favorites/{recipe_id}` | Bearer | Add favorite |
| `DELETE` | `/api/v1/users/{id}/favorites/{recipe_id}` | Bearer | Remove favorite |
| `GET` | `/api/v1/users/{id}/favorites` | Bearer | List favorites |
| `GET` | `/api/v1/stats` | None | Recipe statistics |
| `GET` | `/health` | None | Health check |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | **Yes (prod)** | dev fallback | HS256 signing key — generate with `secrets.token_hex(32)` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `15` | Access token TTL in minutes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Refresh token TTL in days |
| `DATABASE_URL` | No | SQLite file | SQLAlchemy connection string |
| `ENVIRONMENT` | No | `development` | `development` / `staging` / `production` |
| `DEBUG` | No | `false` | Enable debug mode and auto-reload |
| `LOG_LEVEL` | No | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `BCRYPT_ROUNDS` | No | `12` | bcrypt cost factor for password hashing |
| `RATE_LIMIT_ENABLED` | No | `true` | Enable/disable rate limiting |
| `CORS_ORIGINS` | No | localhost ports | JSON array of allowed origins |

---

## Docker

### Development

```bash
docker compose up
```

Starts with hot-reload, SQLite volume, and a dev JWT secret. Runs migrations automatically on startup.

### Production

```bash
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") \
DATABASE_URL=postgresql://user:pass@db/weather_kitchen \
docker compose -f docker-compose.prod.yml up -d
```

Runs with 4 Gunicorn/Uvicorn workers, auto-migrations on startup.

---

## Development Commands

```bash
make dev           # Start dev server (uvicorn --reload)
make test          # Run full test suite
make test-unit     # Unit tests only (fast)
make test-security # Security tests only
make lint          # Ruff lint
make format        # Ruff format
make migrate       # Apply Alembic migrations
make seed          # Seed 1,020 recipes
```

---

## Testing

```bash
uv run pytest                              # All tests (303 tests)
uv run pytest tests/unit/                  # Unit tests
uv run pytest tests/integration/           # Integration tests
uv run pytest tests/security/             # 170+ security tests
uv run pytest --cov=app --cov-report=html  # Coverage report → htmlcov/
```

Coverage threshold: **80%** (enforced in CI).

---

## Project Structure

```
app/
├── api/v1/          # Route handlers (families, users, recipes, auth)
├── auth/            # JWT utilities, PIN hashing, auth dependencies
├── middleware/      # Security headers, rate limiting, logging, error handling
├── models/          # SQLAlchemy ORM models (UUID PKs)
├── repositories/    # Data access layer
├── schemas/         # Pydantic request/response models
├── services/        # Business logic
└── main.py          # App factory, middleware registration
```

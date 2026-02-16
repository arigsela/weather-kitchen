# Weather Kitchen Backend API

Production-grade FastAPI backend for the Weather Kitchen recipe discovery app. Designed for COPPA/GDPR compliance, OWASP Top 10 security, and sub-100ms response times.

**Status**: Phase 1 Complete ✅
**API Version**: v1
**Python**: 3.11+
**Framework**: FastAPI 0.129.0

## Quick Start

### Development Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
make install

# Create environment file (copy from template)
cp .env.example .env

# Run migrations
make migrate

# Start dev server (auto-reload at http://localhost:8000)
make dev
```

Access the API:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up

# Runs on http://localhost:8000
```

## Key Features

✅ **UUID-based primary keys** (hexadecimal, no enumeration)
✅ **API Token Authentication** (SHA256 hashed bearer tokens)
✅ **PIN Protection** (4-6 digit numeric with bcrypt, 5-attempt lockout)
✅ **COPPA Compliance** (parental consent flow with email verification)
✅ **Security Headers** (X-Content-Type-Options, CSP, X-Frame-Options, HSTS)
✅ **Request Correlation** (X-Request-ID tracing)
✅ **Structured Logging** (JSON format with request context)
✅ **Rate Limiting** (10 req/sec general, 5 per 15min for PIN endpoints)
✅ **Alembic Migrations** (version control for database schema)

## Database

### Default: SQLite (Development)
```
DATABASE_URL="sqlite:///./weather_kitchen.db"
```

### PostgreSQL (Production)
```
DATABASE_URL="postgresql://user:password@localhost/weather_kitchen"
```

### Migrations

```bash
# Create new migration
make migrate-new message="add_new_column"

# Apply migrations
make migrate

# Downgrade one migration
make migrate-down

# Reset database (DESTRUCTIVE)
make reset-db
```

## Testing

```bash
# Run all tests
make test

# Unit tests only (fast)
make test-unit

# Integration tests
make test-int

# Security tests
make test-sec

# Generate coverage report
make coverage
```

## Code Quality

```bash
# Lint with Ruff
make lint

# Format code
make format

# Security scan with Bandit
make security
```

## Authentication

### API Token Flow

1. **Create Family Account**
   ```bash
   curl -X POST http://localhost:8000/api/v1/families \
     -H "Content-Type: application/json" \
     -d '{"name":"My Family", "family_size":4, "admin_pin":"1234"}'
   ```

   Response includes one-time plaintext `api_token` (store securely!)

2. **Use Token for Authenticated Requests**
   ```bash
   curl -X GET http://localhost:8000/api/v1/families/{family_id} \
     -H "Authorization: Bearer {api_token}"
   ```

3. **Rotate Token (Requires PIN)**
   ```bash
   curl -X POST http://localhost:8000/api/v1/families/{family_id}/token/rotate \
     -H "Authorization: Bearer {api_token}" \
     -H "Content-Type: application/json" \
     -d '{"admin_pin":"1234"}'
   ```

### PIN Verification (for Sensitive Operations)

PIN is required for:
- Token rotation
- Hard deletion (family purge)
- Parental consent verification

Lockout: 5 failed attempts → 15-minute lockout

## API Endpoints

### Public (No Auth Required)
- `GET /health` - Health check
- `GET /api/v1/recipes` - List recipes with filters
- `GET /api/v1/recipes/{id}` - Get recipe details
- `GET /api/v1/stats/recipes-per-weather` - Weather statistics
- `GET /api/v1/tags/categories` - Recipe categories

### Authenticated
- `POST /api/v1/families` - Create family account
- `GET /api/v1/families/{id}` - Get family details
- `PUT /api/v1/families/{id}` - Update family settings
- `DELETE /api/v1/families/{id}` - Soft delete (soft delete only)
- `POST /api/v1/families/{id}/purge` - Hard delete (requires PIN)
- `POST /api/v1/families/{id}/token/rotate` - Rotate API token (requires PIN)
- `POST /api/v1/families/{id}/consent/request` - Request consent code (email)
- `POST /api/v1/families/{id}/consent/verify` - Verify consent (requires PIN)

## Configuration

Edit `.env` to configure:

```
# Application
DEBUG=false
ENVIRONMENT=development

# Database
DATABASE_URL="sqlite:///./weather_kitchen.db"

# CORS
CORS_ORIGINS='["http://localhost:5173","http://localhost:3000"]'

# Rate Limiting
RATE_LIMIT_GENERAL=10  # requests per second
RATE_LIMIT_PIN_REQUESTS=5  # per 15 minutes

# Authentication
TOKEN_BYTE_LENGTH=32
PIN_MIN_LENGTH=4
PIN_MAX_LENGTH=6
PIN_MAX_ATTEMPTS=5
PIN_LOCKOUT_MINUTES=15
BCRYPT_ROUNDS=12
```

## Project Structure

```
app/
├── main.py              # FastAPI app factory with middleware
├── config.py            # Pydantic Settings (env vars)
├── database.py          # SQLAlchemy engine + GUID TypeDecorator
├── constants.py         # Constants (weather types, categories, error codes)
├── models/              # SQLAlchemy ORM models (all UUID PKs)
├── schemas/             # Pydantic request/response models
├── api/v1/              # Route handlers (recipes, families, users, stats)
├── services/            # Business logic (filtering, auth, CRUD)
├── repositories/        # Data access layer (queries)
├── auth/                # Authentication (token, PIN utilities)
├── middleware/          # Security, logging, request tracking
├── tasks/               # Scheduled tasks (purge, email)
└── seed/                # Seed data (recipes)

alembic/                 # Database migrations
tests/                   # Test suite
```

## Security Headers

All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy: default-src 'self'...`
- `Strict-Transport-Security: max-age=31536000`
- `Referrer-Policy: strict-origin-when-cross-origin`

## Deployment

### Docker

```bash
# Build image
docker build -f Dockerfile -t weather-kitchen-api:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./data/weather_kitchen.db" \
  -e ENVIRONMENT=production \
  weather-kitchen-api:latest
```

## Monitoring

Health check endpoint:
```bash
curl http://localhost:8000/health
```

## Support

For issues, refer to:
- Backend Implementation Plan: `docs/BACKEND_IMPLEMENTATION_PLAN.md`
- PRD: `docs/weather_kitcne_prd.md`
- Architecture: See project root `CLAUDE.md`

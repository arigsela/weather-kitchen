# Backend Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose v2
- Python 3.12+ (for local tooling)
- A PostgreSQL 16 instance (production) or SQLite (development/staging)

---

## JWT Secret Key

> This is the most important security configuration step.

The `JWT_SECRET_KEY` is used to sign all access and refresh tokens. If it is compromised, all tokens must be invalidated by rotating.

**Generate a secure key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Output: a64-char hex string, e.g. 3f8a2c1d...
```

**Rules:**
- Minimum 32 characters
- Must be set via environment variable — never hardcoded or committed to git
- Rotate immediately if leaked (use `POST /api/v1/families/{id}/token/rotate` for each family, or reset the DB)
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.) in production

**What happens without a production secret:** The app starts with an insecure dev default and logs a `WARNING` at startup. All tokens are still functional but not secure.

---

## Token Security

### Access Tokens (15-minute TTL)
- Signed HS256 JWT — stateless, no DB lookup required
- Cannot be individually revoked (short TTL is the revocation mechanism)
- If leaked: attacker has access for up to 15 minutes. Rotate all refresh tokens to prevent renewal.

### Refresh Tokens (7-day TTL)
- Stored as SHA256 hash in `refresh_tokens` table
- Rotation: every call to `/auth/refresh` issues a new pair and revokes the old refresh token
- Full revocation: `POST /api/v1/families/{id}/token/rotate` (requires PIN) revokes **all** refresh tokens for the family

### PIN Lockout
- 5 failed PIN attempts → 15-minute lockout
- Tracked in `families.pin_attempts` and `families.pin_locked_until`
- Reset procedure: wait 15 minutes, or manually clear `pin_locked_until` in the database

---

## Database

### SQLite (development/staging)
```bash
DATABASE_URL=sqlite:///./data/weather_kitchen.db
```
Located at `/app/data/weather_kitchen.db` in the container. Mount a volume to persist data.

### PostgreSQL (production)
```bash
DATABASE_URL=postgresql://username:password@host:5432/weather_kitchen
```

Migrations run automatically on container startup (`alembic upgrade head`).

**Manual migration:**
```bash
uv run alembic upgrade head         # Apply all pending migrations
uv run alembic downgrade -1         # Roll back one migration
uv run alembic history              # View migration history
```

---

## Docker Deployment

### Build the image
```bash
docker build -t weather-kitchen-api:latest backend/
```

### Run production stack
```bash
# Set required environment variables
export JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export DATABASE_URL=postgresql://user:pass@host:5432/weather_kitchen

docker compose -f backend/docker-compose.prod.yml up -d
```

### Check health
```bash
curl http://localhost:8000/health
# {"status": "healthy", "app": "Weather Kitchen API", ...}
```

---

## Rate Limiting

Two tiers enforced via `RateLimiterMiddleware`:

| Tier | Limit | Applies to |
|------|-------|-----------|
| General | 10 req/sec per IP | All endpoints |
| PIN | 5 req/15min per IP | `/verify-pin`, `/token/rotate`, `/purge` |

Returns `429 Too Many Requests` when exceeded. In-memory sliding window (resets on restart). For production with multiple workers/replicas, replace with Redis-backed rate limiting.

---

## Data Retention

- **Refresh tokens**: cleaned up on rotation/logout; `cleanup_expired()` available in `RefreshTokenRepository`
- **Audit logs**: retained 90 days (TTL enforced via scheduled cleanup task)
- **Soft-deleted families**: marked `is_active=False`; hard-deleted after 30 days via purge task

---

## Monitoring

**Health endpoint:** `GET /health` — checks DB connectivity. Returns `200 healthy` or `200 unhealthy` (never 5xx, for load balancer compatibility).

**Request logging:** All requests logged as JSON to stdout:
```json
{"timestamp": "...", "request_id": "...", "method": "GET", "path": "/api/v1/families/...", "status": 200, "response_time_ms": 12.3, "client_ip": "..."}
```

**X-Request-ID header:** Every request gets a unique `X-Request-ID` for distributed tracing.

---

## CORS Configuration

Configure allowed frontend origins:
```bash
CORS_ORIGINS='["https://app.yourdomain.com"]'
```

Default allows `localhost:5173` and `localhost:3000` (development only).

---

## Security Checklist

Before going to production:

- [ ] `JWT_SECRET_KEY` set to a cryptographically random 64-char hex string
- [ ] `DEBUG=false` and `ENVIRONMENT=production`
- [ ] Database running over TLS (PostgreSQL `sslmode=require`)
- [ ] CORS origins restricted to your actual frontend domain
- [ ] Container running as non-root (`appuser`)
- [ ] HTTPS/TLS terminated at load balancer or reverse proxy (nginx/Caddy)
- [ ] `LOG_LEVEL=INFO` (not DEBUG — avoids leaking sensitive data)
- [ ] `BCRYPT_ROUNDS=12` (minimum; increase to 13-14 for higher security at cost of latency)

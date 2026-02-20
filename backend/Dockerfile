# Multi-stage Dockerfile for Weather Kitchen API
# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY app ./app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --target /build/packages \
    fastapi==0.129.0 \
    uvicorn[standard]==0.40.0 \
    python-multipart==0.0.22 \
    sqlalchemy[asyncio]==2.0.46 \
    alembic==1.18.4 \
    pydantic==2.12.5 \
    pydantic-settings==2.5.0 \
    email-validator==2.3.0 \
    bcrypt==5.0.0 \
    PyJWT==2.9.0 \
    gunicorn==23.0.0

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy packages from builder
COPY --from=builder /build/packages /usr/local/lib/python3.12/site-packages

# Copy application code
COPY --from=builder /build/app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Create directory for database (if using SQLite)
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables — JWT_SECRET_KEY must be overridden in production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL="sqlite:///./data/weather_kitchen.db" \
    LOG_LEVEL="INFO"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

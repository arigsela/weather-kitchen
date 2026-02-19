"""
FastAPI application factory with middleware registration and lifespan events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.router import router as v1_router
from app.config import _DEV_JWT_SECRET, settings
from app.database import engine, get_db
from app.middleware import (
    ErrorHandlerMiddleware,
    RateLimiterMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.models import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Creates database tables on startup.
    """
    # Startup
    logger.info("Starting Weather Kitchen API")
    if settings.jwt_secret_key == _DEV_JWT_SECRET:
        if settings.environment == "production":
            raise RuntimeError(
                "JWT_SECRET_KEY must be set to a secure value in production. "
                'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        logger.warning(
            "JWT_SECRET_KEY is using the insecure dev default. "
            "Set JWT_SECRET_KEY environment variable before deploying to production."
        )
    if len(settings.jwt_secret_key) < 32:
        raise RuntimeError(
            f"JWT_SECRET_KEY is too short ({len(settings.jwt_secret_key)} chars). "
            "Minimum 32 characters required per RFC 7518."
        )
    DeclarativeBase.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    logger.info("Shutting down Weather Kitchen API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Weather Kitchen API — recipe discovery with JWT authentication.\n\n"
            "## Authentication\n\n"
            "All protected endpoints require a Bearer JWT access token:\n"
            "```\nAuthorization: Bearer <access_token>\n```\n\n"
            "Obtain tokens via `POST /api/v1/families` (create) or `POST /api/v1/auth/refresh`.\n"
            "Access tokens expire after **15 minutes**. Use the refresh token to get a new pair."
        ),
        lifespan=lifespan,
        openapi_tags=[
            {"name": "families", "description": "Family account management"},
            {"name": "auth", "description": "JWT token refresh and logout"},
            {"name": "users", "description": "User and ingredient management"},
            {"name": "recipes", "description": "Recipe discovery and filtering"},
            {"name": "stats", "description": "Recipe statistics"},
            {"name": "Health", "description": "Service health check"},
        ],
    )

    # Register HTTPBearer security scheme for Swagger UI lock icons
    from fastapi.openapi.utils import get_openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token. Obtain from POST /api/v1/families or POST /api/v1/auth/refresh.",
        }
        # Apply BearerAuth globally to all operations
        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if isinstance(operation, dict) and "tags" in operation:
                    tags = operation.get("tags", [])
                    if "Health" not in tags:
                        operation.setdefault("security", [{"BearerAuth": []}])
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    # Add custom middleware (order matters - reverse registration order)
    # Execution order: request_id → security_headers → rate_limit → request_logging → error_handler
    # Error handler should be first to catch all exceptions
    app.add_middleware(ErrorHandlerMiddleware)
    # Request logging should log all requests
    app.add_middleware(RequestLoggingMiddleware)
    # Rate limiter should check limits before processing
    app.add_middleware(RateLimiterMiddleware)
    # Security headers on every response
    app.add_middleware(SecurityHeadersMiddleware)
    # Request ID should be early to track requests
    app.add_middleware(RequestIDMiddleware)

    # Include API routers
    app.include_router(v1_router)

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check(db: Session = Depends(get_db)):
        """
        Health check endpoint.
        Verifies the API is running and can connect to the database.
        """
        try:
            # Test database connectivity
            db.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "app": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": "Database connection failed",
            }

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

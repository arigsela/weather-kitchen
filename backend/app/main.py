"""
FastAPI application factory with middleware registration and lifespan events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, engine
from app.models import DeclarativeBase
from app.middleware import (
    SecurityHeadersMiddleware,
    ErrorHandlerMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    RateLimiterMiddleware,
)
from app.api.v1.router import router as v1_router

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
        lifespan=lifespan,
    )

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

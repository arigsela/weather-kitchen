"""
Global exception handler middleware that returns safe error responses.
No stack traces are exposed to clients.
"""

import json
import logging
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.constants import ERROR_CODES


logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch unhandled exceptions and return safe error responses."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Generate unique error ID for tracking
            error_id = str(uuid4())

            # Log full error details server-side
            logger.error(
                f"Unhandled exception {error_id}",
                exc_info=True,
                extra={
                    "error_id": error_id,
                    "path": request.url.path,
                    "method": request.method,
                    "client": request.client,
                },
            )

            # Return safe error response without details
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "Internal server error. Please contact support.",
                        "details": [
                            {"field": "error_id", "message": f"Reference: {error_id}"}
                        ],
                    }
                },
            )

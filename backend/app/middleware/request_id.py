"""
Request ID middleware for request tracking and correlation.
Generates or propagates X-Request-ID header across all requests.
"""

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable for accessing request ID in handlers
request_id_context: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Generate or propagate X-Request-ID header."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get request ID from header or generate new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in context variable for access in handlers
        token = request_id_context.set(request_id)

        # Add to request scope for Starlette
        request.scope["request_id"] = request_id

        try:
            response = await call_next(request)
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Reset context
            request_id_context.reset(token)


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_context.get("")

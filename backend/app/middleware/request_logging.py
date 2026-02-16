"""
Request logging middleware for structured JSON logging.
Logs all requests with timing, status, and request ID correlation.
"""

import json
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.middleware.request_id import get_request_id

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests in structured JSON format."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Call the endpoint
        response = await call_next(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Log structured JSON
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "request_id": get_request_id(),
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
            "status": response.status_code,
            "response_time_ms": round(response_time * 1000, 2),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "unknown"),
        }

        # Log at appropriate level based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

        return response

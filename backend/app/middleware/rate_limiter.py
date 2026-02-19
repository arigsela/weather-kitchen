"""
IP-based rate limiting middleware for Weather Kitchen API.
Implements sliding window rate limiting with different tiers for different endpoints.
"""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    IP-based rate limiting middleware with support for multiple tiers.

    Tiers:
    - General: 10 requests per second
    - PIN endpoints: 5 requests per 15 minutes

    Uses sliding window algorithm with in-memory storage.
    """

    # Configuration
    GENERAL_LIMIT = 10  # requests per second
    GENERAL_WINDOW = 1  # second
    PIN_LIMIT = 5  # requests per 15 minutes
    PIN_WINDOW = 900  # 15 minutes in seconds

    # PIN endpoints that use stricter rate limiting
    PIN_ENDPOINTS = {
        "/api/v1/families/{family_id}/token/rotate",
        "/api/v1/families/{family_id}/verify-pin",
        "/api/v1/families/{family_id}/consent/verify",
        "/api/v1/families/{family_id}/purge",
    }

    def __init__(self, app):
        super().__init__(app)
        # Storage: {ip: [(timestamp, endpoint), ...]}
        self.request_history: dict[str, list[tuple[float, str]]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        """Check rate limit and forward request if allowed."""
        # Get client IP
        client_ip = self._get_client_ip(request)

        # Determine if this is a PIN endpoint
        is_pin_endpoint = self._is_pin_endpoint(request.url.path)

        # Clean old requests from history
        current_time = time.time()
        self._cleanup_old_requests(client_ip, current_time, is_pin_endpoint)

        # Check rate limit
        if is_pin_endpoint:
            allowed, retry_after = self._check_pin_limit(client_ip, current_time)
        else:
            allowed, retry_after = self._check_general_limit(client_ip, current_time)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Too many requests. Retry after {retry_after:.0f} seconds.",
                        "details": []
                    }
                },
                headers={"Retry-After": f"{retry_after:.0f}"}
            )

        # Record this request
        self.request_history[client_ip].append((current_time, request.url.path))

        # Call the next middleware/endpoint
        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        # Check X-Forwarded-For header (from reverse proxy)
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"

    def _is_pin_endpoint(self, path: str) -> bool:
        """Check if path is a PIN-protected endpoint."""
        for endpoint in self.PIN_ENDPOINTS:
            # Simple pattern matching (replace {family_id} with *)
            pattern = endpoint.replace("{family_id}", "[a-f0-9-]+")
            if path.startswith(pattern.split("[")[0]):
                return True
        return False

    def _cleanup_old_requests(
        self, client_ip: str, current_time: float, is_pin_endpoint: bool
    ) -> None:
        """Remove requests outside the rate limit window."""
        if client_ip not in self.request_history:
            return

        if is_pin_endpoint:
            window = self.PIN_WINDOW
        else:
            window = self.GENERAL_WINDOW

        # Keep only requests within the current window
        self.request_history[client_ip] = [
            (timestamp, path) for timestamp, path in self.request_history[client_ip]
            if current_time - timestamp <= window
        ]

    def _check_general_limit(self, client_ip: str, current_time: float) -> tuple[bool, float]:
        """Check general tier rate limit (10 req/sec)."""
        if client_ip not in self.request_history:
            return True, 0

        requests_in_window = len(self.request_history[client_ip])

        if requests_in_window >= self.GENERAL_LIMIT:
            # Calculate retry after
            oldest_request = self.request_history[client_ip][0][0]
            retry_after = self.GENERAL_WINDOW - (current_time - oldest_request)
            return False, max(0, retry_after)

        return True, 0

    def _check_pin_limit(self, client_ip: str, current_time: float) -> tuple[bool, float]:
        """Check PIN tier rate limit (5 req/15min)."""
        if client_ip not in self.request_history:
            return True, 0

        requests_in_window = len(self.request_history[client_ip])

        if requests_in_window >= self.PIN_LIMIT:
            # Calculate retry after
            oldest_request = self.request_history[client_ip][0][0]
            retry_after = self.PIN_WINDOW - (current_time - oldest_request)
            return False, max(0, retry_after)

        return True, 0

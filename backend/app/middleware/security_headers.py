"""
Security headers middleware to add protective headers to every response.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    # Swagger UI CDN used by FastAPI /docs and /redoc
    SWAGGER_CDN = "https://cdn.jsdelivr.net"

    # Paths that need relaxed CSP for Swagger/ReDoc UI
    DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable cross-site scripting protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Strict-Transport-Security (HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy — relaxed for docs pages to allow Swagger UI CDN
        is_docs = request.url.path in self.DOCS_PATHS
        if is_docs:
            cdn = f" {self.SWAGGER_CDN}"
            response.headers["Content-Security-Policy"] = (
                f"default-src 'self'; "
                f"script-src 'self'{cdn} 'unsafe-inline'; "
                f"style-src 'self'{cdn} 'unsafe-inline'; "
                f"img-src 'self' data: https:{cdn}; "
                f"font-src 'self' data:{cdn}; "
                f"connect-src 'self'; "
                f"frame-ancestors 'none'; "
                f"base-uri 'self'; "
                f"form-action 'self'"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "speaker-selection=(), "
            "sync-xhr=(), "
            "usb=(), "
            "vr=(), "
            "xr-spatial-tracking=()"
        )

        return response

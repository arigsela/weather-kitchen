"""
Authentication request and response schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# PIN schemas
# ---------------------------------------------------------------------------


class PinVerifyRequest(BaseModel):
    """Verify PIN request."""

    admin_pin: str = Field(
        ..., min_length=4, max_length=6, pattern=r"^\d+$", description="4-6 digit numeric PIN"
    )

    model_config = ConfigDict(examples=[{"admin_pin": "1234"}])


class PinVerifyResponse(BaseModel):
    """PIN verification response."""

    success: bool = Field(..., description="Whether PIN was correct")
    message: str = Field(..., description="Status message")
    lockout_until: datetime | None = Field(
        None, description="Timestamp when lockout expires (if locked)"
    )

    model_config = ConfigDict(
        examples=[
            {"success": True, "message": "PIN verified successfully", "lockout_until": None},
            {
                "success": False,
                "message": "PIN incorrect (4 attempts remaining)",
                "lockout_until": None,
            },
        ]
    )


# ---------------------------------------------------------------------------
# JWT token schemas
# ---------------------------------------------------------------------------


class TokenResponse(BaseModel):
    """JWT token pair returned on login or refresh."""

    access_token: str = Field(..., description="JWT access token (short-lived)")
    refresh_token: str = Field(..., description="JWT refresh token (long-lived, store securely)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token TTL in seconds")

    model_config = ConfigDict(
        examples=[
            {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
            }
        ]
    )


class RefreshRequest(BaseModel):
    """Refresh access token using a refresh token."""

    refresh_token: str = Field(..., description="Valid refresh token")

    model_config = ConfigDict(
        examples=[{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}]
    )


class LogoutRequest(BaseModel):
    """Revoke a refresh token (logout)."""

    refresh_token: str = Field(..., description="Refresh token to revoke")

    model_config = ConfigDict(
        examples=[{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}]
    )


# ---------------------------------------------------------------------------
# Token rotation schemas (PIN-protected)
# ---------------------------------------------------------------------------


class TokenRotateRequest(BaseModel):
    """Revoke all refresh tokens and issue new pair (requires PIN)."""

    admin_pin: str = Field(
        ..., min_length=4, max_length=6, pattern=r"^\d+$", description="4-6 digit numeric PIN"
    )

    model_config = ConfigDict(examples=[{"admin_pin": "1234"}])


class TokenRotateResponse(BaseModel):
    """New JWT token pair after rotation."""

    family_id: UUID = Field(..., description="Family UUID")
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=900, description="Access token TTL in seconds")
    message: str = Field(
        default="All previous tokens are now invalid.", description="Warning message"
    )

    model_config = ConfigDict(
        examples=[
            {
                "family_id": "550e8400-e29b-41d4-a716-446655440000",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
                "message": "All previous tokens are now invalid.",
            }
        ]
    )


# ---------------------------------------------------------------------------
# Generic response
# ---------------------------------------------------------------------------


class SuccessResponse(BaseModel):
    """Generic success response."""

    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Status message")

    model_config = ConfigDict(
        examples=[{"success": True, "message": "Operation completed successfully"}]
    )

"""
Authentication request and response schemas.
"""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PinVerifyRequest(BaseModel):
    """Verify PIN request."""

    admin_pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$", description="4-6 digit numeric PIN")

    model_config = ConfigDict(examples=[
        {"admin_pin": "1234"}
    ])


class PinVerifyResponse(BaseModel):
    """PIN verification response."""

    success: bool = Field(..., description="Whether PIN was correct")
    message: str = Field(..., description="Status message")
    lockout_until: datetime | None = Field(None, description="Timestamp when lockout expires (if locked)")

    model_config = ConfigDict(examples=[
        {
            "success": True,
            "message": "PIN verified successfully",
            "lockout_until": None,
        },
        {
            "success": False,
            "message": "PIN incorrect (4 attempts remaining)",
            "lockout_until": None,
        }
    ])


class TokenRotateRequest(BaseModel):
    """Rotate API token request (requires PIN verification)."""

    admin_pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$", description="4-6 digit numeric PIN")

    model_config = ConfigDict(examples=[
        {"admin_pin": "1234"}
    ])


class TokenRotateResponse(BaseModel):
    """API token rotation response - includes new one-time token."""

    family_id: UUID = Field(..., description="Family UUID")
    api_token: str = Field(..., description="New one-time plaintext API token (store securely)")
    message: str = Field(default="Old token is now invalid. Save your new token securely.", description="Warning message")

    model_config = ConfigDict(examples=[
        {
            "family_id": "550e8400-e29b-41d4-a716-446655440000",
            "api_token": "newTokenqvTu8Hx2K9pL4mN6jRwYzB1cSdFgHkJv+OpQsT5uV6w=",
            "message": "Old token is now invalid. Save your new token securely.",
        }
    ])


class ConsentRequestResponse(BaseModel):
    """Response when requesting parental consent code."""

    family_id: UUID = Field(..., description="Family UUID")
    message: str = Field(..., description="Confirmation message")
    code_sent_to: str = Field(..., description="Email where code was sent (partially masked)")

    model_config = ConfigDict(examples=[
        {
            "family_id": "550e8400-e29b-41d4-a716-446655440000",
            "message": "Consent code sent to parent@example.com",
            "code_sent_to": "parent@exa***",
        }
    ])


class ConsentVerifyRequest(BaseModel):
    """Verify parental consent request (requires 6-digit code and PIN)."""

    consent_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d+$", description="6-digit verification code")
    admin_pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$", description="4-6 digit numeric PIN")

    model_config = ConfigDict(examples=[
        {
            "consent_code": "123456",
            "admin_pin": "1234",
        }
    ])


class ConsentVerifyResponse(BaseModel):
    """Response after verifying parental consent."""

    success: bool = Field(..., description="Whether consent was verified")
    message: str = Field(..., description="Status message")
    family_id: UUID | None = Field(None, description="Family UUID if successful")

    model_config = ConfigDict(examples=[
        {
            "success": True,
            "message": "Parental consent verified",
            "family_id": "550e8400-e29b-41d4-a716-446655440000",
        },
        {
            "success": False,
            "message": "Invalid consent code or PIN",
            "family_id": None,
        }
    ])


class SuccessResponse(BaseModel):
    """Generic success response."""

    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Status message")

    model_config = ConfigDict(examples=[
        {
            "success": True,
            "message": "Operation completed successfully",
        }
    ])

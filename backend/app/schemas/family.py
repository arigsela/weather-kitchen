"""
Family request and response schemas with authentication.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _reject_null_bytes(v: str) -> str:
    """Reject strings containing null bytes."""
    if "\x00" in v:
        raise ValueError("Null bytes are not allowed")
    return v


class FamilyCreate(BaseModel):
    """Create family account request."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Username (3-30 chars, letters, numbers, underscores and hyphens only)",
    )
    family_size: int = Field(..., ge=1, le=20, description="Number of family members (1-20)")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 chars, must include uppercase, lowercase, and digit)",
    )

    @field_validator("name")
    @classmethod
    def name_no_null_bytes(cls, v: str) -> str:
        import re

        _reject_null_bytes(v)
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username may only contain letters, numbers, underscores, and hyphens (no spaces)"
            )
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        from app.auth.password import validate_password_strength

        return validate_password_strength(v)

    model_config = ConfigDict(
        examples=[
            {
                "name": "Smith Family",
                "family_size": 4,
                "password": "MySecret1",
            }
        ]
    )


class FamilyCreateResponse(BaseModel):
    """Response after creating family - includes JWT access + refresh tokens."""

    id: UUID = Field(..., description="New family UUID")
    name: str = Field(..., description="Family name")
    family_size: int = Field(..., description="Family size")
    access_token: str = Field(..., description="JWT access token (15-minute TTL)")
    refresh_token: str = Field(..., description="JWT refresh token (7-day TTL, store securely)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=900, description="Access token expiry in seconds")

    model_config = ConfigDict(
        examples=[
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Smith Family",
                "family_size": 4,
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
            }
        ]
    )


class FamilyResponse(BaseModel):
    """Family details response (no tokens included)."""

    id: UUID = Field(..., description="Family UUID")
    name: str = Field(..., description="Family name")
    family_size: int = Field(..., description="Number of family members")
    is_active: bool = Field(..., description="Whether family account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        examples=[
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Smith Family",
                "family_size": 4,
                "is_active": True,
                "created_at": "2026-02-16T10:30:00Z",
                "updated_at": "2026-02-16T10:30:00Z",
            }
        ],
    )


class FamilyUpdate(BaseModel):
    """Update family settings."""

    name: str | None = Field(None, min_length=1, max_length=100, description="New family name")
    family_size: int | None = Field(None, ge=1, le=20, description="New family size")

    @field_validator("name")
    @classmethod
    def name_no_null_bytes(cls, v: str | None) -> str | None:
        if v is not None:
            return _reject_null_bytes(v)
        return v

    model_config = ConfigDict(
        examples=[
            {
                "name": "Smith-Johnson Family",
                "family_size": 5,
            }
        ]
    )


class FamilyExportResponse(BaseModel):
    """Complete family data export for GDPR compliance."""

    family: FamilyResponse = Field(..., description="Family details")
    users: list[dict] = Field(..., description="All users in family")
    audit_log: list[dict] = Field(..., description="Audit log entries")
    export_date: datetime = Field(..., description="Export timestamp")

    model_config = ConfigDict(
        examples=[
            {
                "family": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Smith Family",
                    "family_size": 4,
                    "is_active": True,
                    "created_at": "2026-02-16T10:30:00Z",
                    "updated_at": "2026-02-16T10:30:00Z",
                },
                "users": [],
                "audit_log": [],
                "export_date": "2026-02-16T10:30:00Z",
            }
        ]
    )

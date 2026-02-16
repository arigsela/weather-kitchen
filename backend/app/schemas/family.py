"""
Family request and response schemas with authentication.
"""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class FamilyCreate(BaseModel):
    """Create family account request."""

    name: str = Field(..., min_length=1, max_length=100, description="Family name")
    family_size: int = Field(..., ge=1, le=20, description="Number of family members (1-20)")
    admin_pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$", description="4-6 digit numeric PIN")

    model_config = ConfigDict(examples=[
        {
            "name": "Smith Family",
            "family_size": 4,
            "admin_pin": "1234",
        }
    ])


class FamilyCreateResponse(BaseModel):
    """Response after creating family - includes one-time plaintext token."""

    family_id: UUID = Field(..., description="New family UUID")
    name: str = Field(..., description="Family name")
    api_token: str = Field(..., description="One-time plaintext API token (store securely)")
    message: str = Field(default="Save your API token - it will not be shown again", description="Warning message")

    model_config = ConfigDict(examples=[
        {
            "family_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Smith Family",
            "api_token": "qvTu8Hx2K9pL4mN6jRwYzB1cSdFgHkJv+OpQsT5uV6w=",
            "message": "Save your API token - it will not be shown again",
        }
    ])


class FamilyResponse(BaseModel):
    """Family details response (no tokens included)."""

    id: UUID = Field(..., description="Family UUID")
    name: str = Field(..., description="Family name")
    family_size: int = Field(..., description="Number of family members")
    is_active: bool = Field(..., description="Whether family account is active")
    consent_given: bool = Field(..., description="Whether COPPA consent has been given")
    has_minor_users: bool = Field(..., description="Whether family has minor users")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, examples=[
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Smith Family",
            "family_size": 4,
            "is_active": True,
            "consent_given": False,
            "has_minor_users": False,
            "created_at": "2026-02-16T10:30:00Z",
            "updated_at": "2026-02-16T10:30:00Z",
        }
    ])


class FamilyUpdate(BaseModel):
    """Update family settings."""

    name: str | None = Field(None, min_length=1, max_length=100, description="New family name")
    family_size: int | None = Field(None, ge=1, le=20, description="New family size")

    model_config = ConfigDict(examples=[
        {
            "name": "Smith-Johnson Family",
            "family_size": 5,
        }
    ])


class FamilyExportResponse(BaseModel):
    """Complete family data export for GDPR compliance."""

    family: FamilyResponse = Field(..., description="Family details")
    users: list[dict] = Field(..., description="All users in family")
    audit_log: list[dict] = Field(..., description="Audit log entries")
    export_date: datetime = Field(..., description="Export timestamp")

    model_config = ConfigDict(examples=[
        {
            "family": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Smith Family",
                "family_size": 4,
                "is_active": True,
                "consent_given": False,
                "has_minor_users": False,
                "created_at": "2026-02-16T10:30:00Z",
                "updated_at": "2026-02-16T10:30:00Z",
            },
            "users": [],
            "audit_log": [],
            "export_date": "2026-02-16T10:30:00Z",
        }
    ])

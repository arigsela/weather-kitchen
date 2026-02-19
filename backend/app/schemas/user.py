"""
User request and response schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _reject_null_bytes(v: str) -> str:
    """Reject strings containing null bytes."""
    if "\x00" in v:
        raise ValueError("Null bytes are not allowed")
    return v


class UserCreate(BaseModel):
    """Create user request."""

    name: str = Field(..., min_length=1, max_length=100, description="User name")
    emoji: str | None = Field(None, max_length=2, description="User emoji")

    @field_validator("name")
    @classmethod
    def name_no_null_bytes(cls, v: str) -> str:
        return _reject_null_bytes(v)

    model_config = ConfigDict(examples=[
        {
            "name": "Emma",
            "emoji": "👧",
        }
    ])


class UserResponse(BaseModel):
    """User details response."""

    id: UUID = Field(..., description="User UUID")
    family_id: UUID = Field(..., description="Family UUID this user belongs to")
    name: str = Field(..., description="User name")
    emoji: str | None = Field(None, description="User emoji")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, examples=[
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "family_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Emma",
            "emoji": "👧",
            "created_at": "2026-02-16T10:30:00Z",
            "updated_at": "2026-02-16T10:30:00Z",
        }
    ])


class UserListResponse(BaseModel):
    """List of users in a family."""

    family_id: UUID = Field(..., description="Family UUID")
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")

    model_config = ConfigDict(examples=[
        {
            "family_id": "550e8400-e29b-41d4-a716-446655440000",
            "users": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "family_id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Emma",
                    "age": 8,
                    "created_at": "2026-02-16T10:30:00Z",
                    "updated_at": "2026-02-16T10:30:00Z",
                }
            ],
            "total": 1,
        }
    ])


class IngredientUpdate(BaseModel):
    """Replace all ingredients for a user."""

    ingredients: list[str] = Field(..., description="List of ingredients (replaces all)")

    model_config = ConfigDict(examples=[
        {
            "ingredients": ["egg", "milk", "cheese"],
        }
    ])


class IngredientResponse(BaseModel):
    """User's ingredient list."""

    user_id: UUID = Field(..., description="User UUID")
    ingredients: list[str] = Field(..., description="List of ingredients")

    model_config = ConfigDict(examples=[
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "ingredients": ["egg", "milk", "cheese"],
        }
    ])


class FavoriteAdd(BaseModel):
    """Add or remove favorite recipe."""

    recipe_id: UUID = Field(..., description="Recipe UUID to add/remove")


class FavoriteResponse(BaseModel):
    """User's favorite recipe."""

    id: UUID = Field(..., description="Favorite record UUID")
    user_id: UUID = Field(..., description="User UUID")
    recipe_id: UUID = Field(..., description="Recipe UUID")
    recipe_name: str = Field(..., description="Recipe name (for reference)")
    added_at: datetime = Field(..., description="When added to favorites")

    model_config = ConfigDict(from_attributes=True, examples=[
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "recipe_id": "550e8400-e29b-41d4-a716-446655440100",
            "recipe_name": "Pasta Carbonara",
            "added_at": "2026-02-16T10:30:00Z",
        }
    ])


class FavoritesListResponse(BaseModel):
    """List of user's favorite recipes."""

    user_id: UUID = Field(..., description="User UUID")
    favorites: list[FavoriteResponse] = Field(..., description="List of favorite recipes")
    total: int = Field(..., description="Total number of favorites")

    model_config = ConfigDict(examples=[
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440001",
            "favorites": [],
            "total": 0,
        }
    ])

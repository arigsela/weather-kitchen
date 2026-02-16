"""
User request and response schemas.
"""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Create user request."""

    name: str = Field(..., min_length=1, max_length=100, description="User name")
    age: int | None = Field(None, ge=5, le=18, description="User age (5-18 for COPPA tracking)")

    model_config = ConfigDict(examples=[
        {
            "name": "Emma",
            "age": 8,
        }
    ])


class UserResponse(BaseModel):
    """User details response."""

    id: UUID = Field(..., description="User UUID")
    family_id: UUID = Field(..., description="Family UUID this user belongs to")
    name: str = Field(..., description="User name")
    age: int | None = Field(None, description="User age")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, examples=[
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "family_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Emma",
            "age": 8,
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

"""
Recipe request and response schemas.
"""

from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class RecipeIngredientResponse(BaseModel):
    """Single ingredient in a recipe."""

    id: UUID = Field(..., description="Unique ingredient ID")
    sort_order: int = Field(..., description="Order of ingredient in list")
    ingredient_text: str = Field(..., max_length=200, description="Ingredient description")

    model_config = ConfigDict(from_attributes=True)


class RecipeStepResponse(BaseModel):
    """Single step in recipe preparation."""

    id: UUID = Field(..., description="Unique step ID")
    step_number: int = Field(..., description="Step number in sequence")
    step_text: str = Field(..., description="Step instructions")

    model_config = ConfigDict(from_attributes=True)


class RecipeTagResponse(BaseModel):
    """Single tag (normalized lowercase) for a recipe."""

    id: UUID = Field(..., description="Unique tag ID")
    tag: str = Field(..., max_length=50, description="Tag name (lowercase)")

    model_config = ConfigDict(from_attributes=True)


class RecipeListItem(BaseModel):
    """Recipe in list view (minimal data)."""

    id: UUID = Field(..., description="Unique recipe ID")
    name: str = Field(..., max_length=100, description="Recipe name")
    emoji: str = Field(..., max_length=2, description="Recipe emoji")
    weather: str = Field(..., max_length=20, description="Associated weather")
    category: str = Field(..., max_length=20, description="Recipe category")
    serves: int = Field(..., description="Base serving size")

    model_config = ConfigDict(from_attributes=True, examples=[
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Sunny Pasta",
            "emoji": "☀️",
            "weather": "sunny",
            "category": "lunch",
            "serves": 4,
        }
    ])


class RecipeResponse(BaseModel):
    """Full recipe with all details."""

    id: UUID = Field(..., description="Unique recipe ID")
    name: str = Field(..., max_length=100, description="Recipe name")
    emoji: str = Field(..., max_length=2, description="Recipe emoji")
    why: str | None = Field(None, max_length=500, description="Why this recipe for this weather")
    tip: str | None = Field(None, max_length=500, description="Cooking tip")
    weather: str = Field(..., max_length=20, description="Associated weather")
    category: str = Field(..., max_length=20, description="Recipe category")
    serves: int = Field(..., description="Base serving size")
    version_added: str = Field(..., max_length=10, description="Version recipe was added")
    ingredients: list[RecipeIngredientResponse] = Field(default_factory=list, description="Recipe ingredients")
    steps: list[RecipeStepResponse] = Field(default_factory=list, description="Cooking steps")
    tags: list[RecipeTagResponse] = Field(default_factory=list, description="Recipe tags")

    model_config = ConfigDict(from_attributes=True, examples=[
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Sunny Pasta",
            "emoji": "☀️",
            "why": "Light and fresh for sunny days",
            "tip": "Use fresh basil",
            "weather": "sunny",
            "category": "lunch",
            "serves": 4,
            "version_added": "1.0.0",
            "ingredients": [
                {"id": "550e8400-e29b-41d4-a716-446655440001", "sort_order": 1, "ingredient_text": "400g pasta"}
            ],
            "steps": [
                {"id": "550e8400-e29b-41d4-a716-446655440002", "step_number": 1, "step_text": "Boil pasta"}
            ],
            "tags": [
                {"id": "550e8400-e29b-41d4-a716-446655440003", "tag": "vegetarian"}
            ],
        }
    ])


class RecipeListResponse(BaseModel):
    """Paginated list of recipes."""

    total: int = Field(..., description="Total number of recipes available")
    limit: int = Field(..., description="Items returned per page")
    offset: int = Field(..., description="Number of items skipped")
    items: list[RecipeListItem] = Field(..., description="List of recipes")

    model_config = ConfigDict(examples=[
        {
            "total": 1020,
            "limit": 20,
            "offset": 0,
            "items": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Sunny Pasta",
                    "emoji": "☀️",
                    "weather": "sunny",
                    "category": "lunch",
                    "serves": 4,
                }
            ],
        }
    ])

    @property
    def has_next(self) -> bool:
        """Check if there are more items."""
        return self.offset + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        """Check if there are previous items."""
        return self.offset > 0

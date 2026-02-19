"""
Statistics and analytics response schemas.
"""

from pydantic import BaseModel, ConfigDict, Field


class WeatherStatsItem(BaseModel):
    """Count of recipes for a single weather type."""

    weather: str = Field(..., max_length=20, description="Weather type")
    count: int = Field(..., ge=0, description="Number of recipes for this weather")

    model_config = ConfigDict(
        examples=[
            {"weather": "sunny", "count": 200},
            {"weather": "rainy", "count": 150},
        ]
    )


class WeatherStatsResponse(BaseModel):
    """Recipe count by weather type."""

    stats: list[WeatherStatsItem] = Field(..., description="Recipes per weather type")

    model_config = ConfigDict(
        examples=[
            {
                "stats": [
                    {"weather": "sunny", "count": 200},
                    {"weather": "rainy", "count": 150},
                    {"weather": "snowy", "count": 120},
                    {"weather": "windy", "count": 180},
                    {"weather": "cloudy", "count": 370},
                ]
            }
        ]
    )


class CategoryStatsItem(BaseModel):
    """Count of recipes for a single category."""

    category: str = Field(..., max_length=20, description="Category name")
    count: int = Field(..., ge=0, description="Number of recipes in this category")

    model_config = ConfigDict(
        examples=[
            {"category": "breakfast", "count": 100},
            {"category": "lunch", "count": 300},
        ]
    )


class TagItem(BaseModel):
    """Single tag with count of recipes."""

    tag: str = Field(..., max_length=50, description="Tag name (lowercase)")
    count: int = Field(..., ge=0, description="Number of recipes with this tag")

    model_config = ConfigDict(
        examples=[
            {"tag": "vegetarian", "count": 400},
            {"tag": "gluten-free", "count": 150},
        ]
    )


class TagCategoriesResponse(BaseModel):
    """Organized tags by category."""

    categories: dict[str, list[TagItem]] = Field(..., description="Tags grouped by category")

    model_config = ConfigDict(
        examples=[
            {
                "categories": {
                    "breakfast": [
                        {"tag": "vegetarian", "count": 50},
                        {"tag": "quick", "count": 30},
                    ],
                    "lunch": [
                        {"tag": "vegetarian", "count": 100},
                        {"tag": "protein", "count": 80},
                    ],
                }
            }
        ]
    )

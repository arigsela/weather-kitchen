"""
Statistics endpoints - recipe statistics and analytics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.recipe_service import RecipeService
from app.schemas.stats import WeatherStatsResponse, TagCategoriesResponse
from app.middleware.request_id import get_request_id

router = APIRouter(prefix="/api/v1", tags=["stats"])


@router.get(
    "/stats/recipes-per-weather",
    response_model=WeatherStatsResponse,
    summary="Weather statistics",
    description="Get count of recipes per weather type",
)
async def get_weather_stats(
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> WeatherStatsResponse:
    """
    Get recipe count by weather type.

    Returns the number of recipes available for each weather condition.
    """
    service = RecipeService(db)
    stats = service.get_weather_stats()
    return WeatherStatsResponse(**stats)


@router.get(
    "/tags/categories",
    response_model=TagCategoriesResponse,
    summary="Recipe tags",
    description="Get all recipe tags organized by category",
)
async def get_tag_categories(
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> TagCategoriesResponse:
    """
    Get recipe tags organized by category.

    Returns all tags grouped by meal category with counts.
    """
    service = RecipeService(db)
    categories = service.get_tag_categories()
    return TagCategoriesResponse(**categories)

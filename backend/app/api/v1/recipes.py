"""
Recipe endpoints - public API for recipe discovery.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.request_id import get_request_id
from app.schemas.recipe import RecipeListResponse, RecipeResponse
from app.services.recipe_service import RecipeService

router = APIRouter(prefix="/api/v1", tags=["recipes"])


@router.get(
    "/recipes",
    response_model=RecipeListResponse,
    summary="List recipes",
    description="Get paginated list of recipes with optional filtering by weather, category, tags, and ingredients",
)
async def list_recipes(
    weather: str | None = Query(None, description="Filter by weather type"),
    category: str | None = Query(None, description="Filter by category"),
    tags: list[str] | None = Query(None, description="Filter by tags (comma-separated)"),
    ingredients: list[str] | None = Query(
        None, description="Filter by ingredients (comma-separated)"
    ),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> RecipeListResponse:
    """
    Get recipes with optional filters.

    Query Parameters:
    - **weather**: Filter by weather (e.g., sunny, rainy, snowy)
    - **category**: Filter by category (e.g., breakfast, lunch, dinner, snack)
    - **tags**: Comma-separated tags to filter by
    - **ingredients**: Comma-separated ingredients to filter by
    - **limit**: Items per page (1-100, default 20)
    - **offset**: Items to skip (default 0)

    Returns paginated recipes matching the filters.
    """
    service = RecipeService(db)

    # Parse comma-separated parameters
    tags_list = [t.strip().lower() for t in tags] if tags else None
    ingredients_list = [i.strip().lower() for i in ingredients] if ingredients else None

    result = service.list_recipes(
        weather=weather,
        category=category,
        tags=tags_list,
        ingredients=ingredients_list,
        limit=limit,
        offset=offset,
    )

    return RecipeListResponse(**result)


@router.get(
    "/recipes/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get recipe details",
    description="Get full recipe with all ingredients, steps, and tags",
)
async def get_recipe(
    recipe_id: UUID = Path(..., description="Recipe UUID"),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> RecipeResponse:
    """
    Get recipe details by ID.

    Returns full recipe with ingredients, preparation steps, and tags.
    """
    service = RecipeService(db)
    recipe = service.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    return recipe

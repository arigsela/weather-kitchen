"""
User management endpoints - CRUD, ingredients, favorites.
"""

import json
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_family
from app.database import get_db
from app.middleware.request_id import get_request_id
from app.models.family import Family
from app.schemas.user import (
    FavoriteResponse,
    FavoritesListResponse,
    IngredientResponse,
    IngredientUpdate,
    UserCreate,
    UserListResponse,
    UserResponse,
)
from app.services.audit_service import _audit_log_background
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1", tags=["users"])


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create new user in authenticated family (requires authentication)",
)
async def create_user(
    request: UserCreate,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> UserResponse:
    """Create new user in family."""
    service = UserService(db)
    user = service.create_user(
        family_id=family.id,
        name=request.name,
        emoji=request.emoji,
    )

    background_tasks.add_task(
        _audit_log_background,
        action="user.created",
        entity_type="user",
        entity_id=user.id,
        ip=http_request.client.host,
        family_id=family.id,
        user_agent=http_request.headers.get("user-agent"),
        details=json.dumps({"user_name": request.name}),
    )

    return user


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List users",
    description="List all users in authenticated family (requires authentication)",
)
async def list_users(
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> UserListResponse:
    """List all users in the authenticated family."""
    service = UserService(db)
    return service.list_users(family.id)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user details",
    description="Get user details (requires authentication + family ownership)",
)
async def get_user(
    user_id: UUID,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> UserResponse:
    """Get user details (verifies family ownership)."""
    service = UserService(db)
    user = service.get_user(user_id, family.id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.get(
    "/users/{user_id}/ingredients",
    response_model=IngredientResponse,
    summary="Get user ingredients",
    description="Get user's ingredient list (requires authentication + family ownership)",
)
async def get_ingredients(
    user_id: UUID,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> IngredientResponse:
    """Get user's ingredients (PUT semantics - replace all)."""
    service = UserService(db)
    ingredients = service.get_ingredients(user_id, family.id)

    if ingredients is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return ingredients


@router.put(
    "/users/{user_id}/ingredients",
    response_model=IngredientResponse,
    summary="Update user ingredients",
    description="Replace all ingredients for user (idempotent PUT, requires authentication + family ownership)",
)
async def update_ingredients(
    user_id: UUID,
    request: IngredientUpdate,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> IngredientResponse:
    """Replace all ingredients for user (PUT semantics)."""
    service = UserService(db)
    updated = service.update_ingredients(user_id, family.id, request.ingredients)

    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    background_tasks.add_task(
        _audit_log_background,
        action="ingredients.updated",
        entity_type="user",
        entity_id=user_id,
        ip=http_request.client.host,
        family_id=family.id,
        user_id=user_id,
        user_agent=http_request.headers.get("user-agent"),
        details=json.dumps({"ingredient_count": len(request.ingredients)}),
    )

    return updated


@router.get(
    "/users/{user_id}/favorites",
    response_model=FavoritesListResponse,
    summary="Get user favorites",
    description="Get user's favorite recipes (requires authentication + family ownership)",
)
async def get_favorites(
    user_id: UUID,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> FavoritesListResponse:
    """Get user's favorite recipes."""
    service = UserService(db)
    favorites = service.get_favorites(user_id, family.id)

    if favorites is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return favorites


@router.put(
    "/users/{user_id}/favorites/{recipe_id}",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add favorite recipe",
    description="Add recipe to favorites (idempotent PUT, requires authentication + family ownership)",
)
async def add_favorite(
    user_id: UUID,
    recipe_id: UUID,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> FavoriteResponse:
    """Add recipe to favorites (idempotent PUT semantics)."""
    service = UserService(db)
    favorite = service.add_favorite(user_id, family.id, recipe_id)

    if favorite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    background_tasks.add_task(
        _audit_log_background,
        action="favorite.added",
        entity_type="user_favorite",
        entity_id=recipe_id,
        ip=http_request.client.host,
        family_id=family.id,
        user_id=user_id,
        user_agent=http_request.headers.get("user-agent"),
        details=json.dumps({"user_id": str(user_id), "recipe_id": str(recipe_id)}),
    )

    return favorite


@router.delete(
    "/users/{user_id}/favorites/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove favorite recipe",
    description="Remove recipe from favorites (idempotent DELETE, requires authentication + family ownership)",
)
async def remove_favorite(
    user_id: UUID,
    recipe_id: UUID,
    background_tasks: BackgroundTasks,
    http_request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> None:
    """Remove recipe from favorites (idempotent DELETE semantics)."""
    service = UserService(db)
    success = service.remove_favorite(user_id, family.id, recipe_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    background_tasks.add_task(
        _audit_log_background,
        action="favorite.removed",
        entity_type="user_favorite",
        entity_id=recipe_id,
        ip=http_request.client.host,
        family_id=family.id,
        user_id=user_id,
        user_agent=http_request.headers.get("user-agent"),
        details=json.dumps({"user_id": str(user_id), "recipe_id": str(recipe_id)}),
    )

"""
User service - business logic for user operations.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User, UserFavorite
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserResponse, UserListResponse, IngredientResponse, FavoritesListResponse, FavoriteResponse


class UserService:
    """Service layer for user operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def create_user(
        self,
        family_id: UUID,
        name: str,
        age: Optional[int] = None,
    ) -> UserResponse:
        """Create new user in family."""
        user = self.repository.create_user(family_id, name, age)
        self.db.commit()
        return UserResponse.model_validate(user)

    def get_user(self, user_id: UUID, family_id: UUID) -> Optional[UserResponse]:
        """Get user by ID (verifying family ownership)."""
        user = self.repository.get_by_id_for_family(user_id, family_id)
        if not user:
            return None

        return UserResponse.model_validate(user)

    def list_users(self, family_id: UUID) -> UserListResponse:
        """List all users in a family."""
        users = self.repository.list_by_family(family_id)
        return UserListResponse(
            family_id=family_id,
            users=[UserResponse.model_validate(u) for u in users],
            total=len(users),
        )

    def update_user(
        self,
        user_id: UUID,
        family_id: UUID,
        name: Optional[str] = None,
        age: Optional[int] = None,
    ) -> Optional[UserResponse]:
        """Update user details."""
        user = self.repository.get_by_id_for_family(user_id, family_id)
        if not user:
            return None

        if name is not None:
            user.name = name
        if age is not None:
            user.age = age

        self.db.add(user)
        self.db.commit()
        return UserResponse.model_validate(user)

    def get_ingredients(self, user_id: UUID, family_id: UUID) -> Optional[IngredientResponse]:
        """Get user's ingredients."""
        user = self.repository.get_by_id_for_family(user_id, family_id)
        if not user:
            return None

        ingredients = self.repository.get_ingredients(user_id, family_id)
        return IngredientResponse(
            user_id=user_id,
            ingredients=ingredients,
        )

    def update_ingredients(
        self,
        user_id: UUID,
        family_id: UUID,
        ingredients: list[str],
    ) -> Optional[IngredientResponse]:
        """Replace all ingredients (PUT semantics)."""
        success = self.repository.replace_ingredients(user_id, family_id, ingredients)
        if not success:
            return None

        self.db.commit()
        return IngredientResponse(
            user_id=user_id,
            ingredients=[ing.lower() for ing in ingredients],
        )

    def get_favorites(self, user_id: UUID, family_id: UUID) -> Optional[FavoritesListResponse]:
        """Get user's favorite recipes."""
        user = self.repository.get_by_id_for_family(user_id, family_id)
        if not user:
            return None

        favorites = self.repository.get_favorites(user_id, family_id)
        return FavoritesListResponse(
            user_id=user_id,
            favorites=[
                FavoriteResponse(
                    id=fav.id,
                    user_id=fav.user_id,
                    recipe_id=fav.recipe_id,
                    recipe_name=fav.recipe.name if fav.recipe else "Unknown",
                    added_at=fav.added_at,
                )
                for fav in favorites
            ],
            total=len(favorites),
        )

    def add_favorite(self, user_id: UUID, family_id: UUID, recipe_id: UUID) -> Optional[FavoriteResponse]:
        """Add recipe to favorites (idempotent)."""
        favorite = self.repository.add_favorite(user_id, family_id, recipe_id)
        if not favorite:
            return None

        self.db.commit()
        return FavoriteResponse(
            id=favorite.id,
            user_id=favorite.user_id,
            recipe_id=favorite.recipe_id,
            recipe_name=favorite.recipe.name if favorite.recipe else "Unknown",
            added_at=favorite.added_at,
        )

    def remove_favorite(self, user_id: UUID, family_id: UUID, recipe_id: UUID) -> bool:
        """Remove recipe from favorites (idempotent)."""
        success = self.repository.remove_favorite(user_id, family_id, recipe_id)
        if success:
            self.db.commit()
        return success

    def is_favorite(self, user_id: UUID, recipe_id: UUID) -> bool:
        """Check if recipe is in user's favorites."""
        return self.repository.is_favorite(user_id, recipe_id)

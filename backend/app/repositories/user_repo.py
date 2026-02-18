"""
User repository - data access layer for user operations.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session, selectinload

from app.models.user import User, UserIngredient, UserFavorite
from app.models.recipe import Recipe
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity."""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def create_user(
        self,
        family_id: UUID,
        name: str,
        emoji: Optional[str] = None,
    ) -> User:
        """Create new user in family."""
        import uuid
        user = User(
            id=uuid.uuid4(),
            family_id=family_id,
            name=name,
            emoji=emoji,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        self.db.flush()
        return user

    def get_by_id_for_family(self, user_id: UUID, family_id: UUID) -> Optional[User]:
        """Get user by ID, verifying family ownership."""
        return self.db.query(User).filter(
            User.id == user_id,
            User.family_id == family_id,
        ).first()

    def list_by_family(self, family_id: UUID) -> list[User]:
        """Get all users in a family."""
        return self.db.query(User).filter(
            User.family_id == family_id,
        ).order_by(User.name).all()

    def get_ingredients(self, user_id: UUID, family_id: UUID) -> list[str]:
        """Get list of ingredients for a user."""
        ingredients = self.db.query(UserIngredient).filter(
            UserIngredient.user_id == user_id,
        ).order_by(UserIngredient.ingredient_name).all()

        # Verify family ownership
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.family_id != family_id:
            return []

        return [ing.ingredient_name for ing in ingredients]

    def replace_ingredients(self, user_id: UUID, family_id: UUID, ingredients: list[str]) -> bool:
        """Replace all ingredients for a user (idempotent PUT semantics)."""
        # Verify family ownership
        user = self.db.query(User).filter(
            User.id == user_id,
            User.family_id == family_id,
        ).first()

        if not user:
            return False

        # Delete existing ingredients
        self.db.query(UserIngredient).filter(UserIngredient.user_id == user_id).delete()

        # Add new ingredients
        for ingredient_name in ingredients:
            import uuid
            user_ing = UserIngredient(
                id=uuid.uuid4(),
                user_id=user_id,
                ingredient_name=ingredient_name.lower(),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(user_ing)

        self.db.flush()
        return True

    def get_favorites(self, user_id: UUID, family_id: UUID) -> list[UserFavorite]:
        """Get user's favorite recipes."""
        # Verify family ownership
        user = self.db.query(User).filter(
            User.id == user_id,
            User.family_id == family_id,
        ).first()

        if not user:
            return []

        return self.db.query(UserFavorite).options(
            selectinload(UserFavorite.recipe)
        ).filter(
            UserFavorite.user_id == user_id,
        ).order_by(UserFavorite.added_at.desc()).all()

    def add_favorite(self, user_id: UUID, family_id: UUID, recipe_id: UUID) -> Optional[UserFavorite]:
        """Add recipe to favorites (idempotent - returns existing if already exists)."""
        # Verify family ownership
        user = self.db.query(User).filter(
            User.id == user_id,
            User.family_id == family_id,
        ).first()

        if not user:
            return None

        # Check if already exists
        existing = self.db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.recipe_id == recipe_id,
        ).first()

        if existing:
            return existing

        # Create new favorite
        import uuid
        favorite = UserFavorite(
            id=uuid.uuid4(),
            user_id=user_id,
            recipe_id=recipe_id,
            added_at=datetime.now(timezone.utc),
        )
        self.db.add(favorite)
        self.db.flush()
        return favorite

    def remove_favorite(self, user_id: UUID, family_id: UUID, recipe_id: UUID) -> bool:
        """Remove recipe from favorites (idempotent - success even if not exists)."""
        # Verify family ownership
        user = self.db.query(User).filter(
            User.id == user_id,
            User.family_id == family_id,
        ).first()

        if not user:
            return False

        # Delete favorite
        result = self.db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.recipe_id == recipe_id,
        ).delete()

        self.db.flush()
        return True

    def is_favorite(self, user_id: UUID, recipe_id: UUID) -> bool:
        """Check if recipe is in user's favorites."""
        favorite = self.db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.recipe_id == recipe_id,
        ).first()

        return favorite is not None

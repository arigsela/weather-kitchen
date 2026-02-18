"""
User models: User, UserIngredient, UserFavorite.
"""

import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship

from app.models.base import DeclarativeBase, UUIDMixin, TimestampMixin
from app.database import GUID


class User(DeclarativeBase):
    """User entity - individual user within a family."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_family_id", "family_id"),
    )

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Foreign key to family
    family_id = Column(GUID, ForeignKey("families.id", ondelete="CASCADE"), nullable=False)

    # User data
    name = Column(String(50), nullable=False)
    emoji = Column(String(2), nullable=True, default="👤")  # Optional emoji, defaults to person
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    family = relationship("Family", back_populates="users")
    ingredients = relationship("UserIngredient", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)
    updated_at = Column(TimestampMixin.updated_at.type, nullable=False)

    def __repr__(self):
        return f"<User {self.name} {self.emoji} (family={self.family_id})>"


class UserIngredient(DeclarativeBase):
    """User ingredient - normalized lowercase ingredient tag for a user."""

    __tablename__ = "user_ingredients"
    __table_args__ = (
        Index("ix_user_ingredients", "user_id", "ingredient_name", unique=True),
    )

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Foreign key to user
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Data (normalized lowercase)
    ingredient_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc), nullable=False)

    # Relationship
    user = relationship("User", back_populates="ingredients")

    def __repr__(self):
        return f"<UserIngredient {self.ingredient_name}>"


class UserFavorite(DeclarativeBase):
    """User favorite - recipe favorited by a user."""

    __tablename__ = "user_favorites"
    __table_args__ = (
        Index("ix_user_favorites", "user_id", "recipe_id", unique=True),
    )

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Foreign keys
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(GUID, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)

    # Data
    added_at = Column(DateTime, default=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="favorites")
    recipe = relationship("Recipe", back_populates="favorites")

    def __repr__(self):
        return f"<UserFavorite user={self.user_id} recipe={self.recipe_id}>"

"""
Recipe models: Recipe, RecipeIngredient, RecipeStep, RecipeTag.
"""

import uuid

from sqlalchemy import Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import GUID
from app.models.base import DeclarativeBase, TimestampMixin


class Recipe(DeclarativeBase):
    """Recipe entity - immutable recipe data."""

    __tablename__ = "recipes"

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Core recipe data
    name = Column(String(100), nullable=False, index=True)
    emoji = Column(String(2), nullable=False)
    why = Column(String(500), nullable=True)
    tip = Column(String(500), nullable=True)
    serves = Column(Integer, nullable=False)  # serves (multiplied by family_size/2)
    weather = Column(String(20), nullable=False, index=True)  # one of WEATHER_TYPES
    category = Column(String(20), nullable=False, index=True)  # breakfast, lunch, dinner, snack
    version_added = Column(String(10), nullable=False, default="1.0.0")

    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    steps = relationship("RecipeStep", back_populates="recipe", cascade="all, delete-orphan")
    tags = relationship("RecipeTag", back_populates="recipe", cascade="all, delete-orphan")
    favorites = relationship("UserFavorite", back_populates="recipe", cascade="all, delete-orphan")

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)
    updated_at = Column(TimestampMixin.updated_at.type, nullable=False)

    def __repr__(self):
        return f"<Recipe {self.name} (weather={self.weather}, category={self.category})>"


class RecipeIngredient(DeclarativeBase):
    """Recipe ingredient - individual ingredient for a recipe."""

    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        Index("ix_recipe_ingredients_recipe_id", "recipe_id"),
    )

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Foreign key
    recipe_id = Column(GUID, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)

    # Data
    sort_order = Column(Integer, nullable=False)
    ingredient_text = Column(String(200), nullable=False)

    # Relationship
    recipe = relationship("Recipe", back_populates="ingredients")

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)
    updated_at = Column(TimestampMixin.updated_at.type, nullable=False)

    def __repr__(self):
        return f"<RecipeIngredient #{self.sort_order}: {self.ingredient_text}>"


class RecipeStep(DeclarativeBase):
    """Recipe step - individual cooking step for a recipe."""

    __tablename__ = "recipe_steps"
    __table_args__ = (
        Index("ix_recipe_steps_recipe_id", "recipe_id"),
    )

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Foreign key
    recipe_id = Column(GUID, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)

    # Data
    step_number = Column(Integer, nullable=False)
    step_text = Column(Text, nullable=False)

    # Relationship
    recipe = relationship("Recipe", back_populates="steps")

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)
    updated_at = Column(TimestampMixin.updated_at.type, nullable=False)

    def __repr__(self):
        return f"<RecipeStep #{self.step_number}>"


class RecipeTag(DeclarativeBase):
    """Recipe tag - normalized lowercase tag for a recipe."""

    __tablename__ = "recipe_tags"

    # UUID primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4, nullable=False)

    # Foreign key
    recipe_id = Column(GUID, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)

    # Data (normalized lowercase)
    tag = Column(String(50), nullable=False, index=True)

    # Relationship
    recipe = relationship("Recipe", back_populates="tags")

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)
    updated_at = Column(TimestampMixin.updated_at.type, nullable=False)

    def __repr__(self):
        return f"<RecipeTag: {self.tag}>"

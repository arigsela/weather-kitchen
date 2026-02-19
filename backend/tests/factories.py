"""
Test data factories for generating test entities.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.recipe import Recipe, RecipeIngredient, RecipeStep, RecipeTag


class RecipeFactory:
    """Factory for creating test Recipe entities."""

    @staticmethod
    def create(
        db: Session,
        name: str = "Test Recipe",
        weather: str = "sunny",
        category: str = "lunch",
        serves: int = 4,
        emoji: str = "🍽️",
        **kwargs,
    ) -> Recipe:
        """Create a recipe in the database."""
        recipe = Recipe(
            id=uuid.uuid4(),
            name=name,
            emoji=emoji,
            weather=weather,
            category=category,
            serves=serves,
            version_added="2.0.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **kwargs,
        )
        db.add(recipe)
        db.flush()
        return recipe

    @staticmethod
    def create_batch(
        db: Session,
        count: int = 5,
        weather: str = "sunny",
        **kwargs,
    ) -> list[Recipe]:
        """Create multiple recipes."""
        recipes = []
        for i in range(count):
            recipe = RecipeFactory.create(
                db,
                name=f"Test Recipe {i+1}",
                weather=weather,
                **kwargs,
            )
            recipes.append(recipe)
        db.flush()
        return recipes


class RecipeIngredientFactory:
    """Factory for creating test RecipeIngredient entities."""

    @staticmethod
    def create(
        db: Session,
        recipe_id: uuid.UUID,
        sort_order: int = 1,
        ingredient_text: str = "Test Ingredient",
    ) -> RecipeIngredient:
        """Create a recipe ingredient."""
        ingredient = RecipeIngredient(
            id=uuid.uuid4(),
            recipe_id=recipe_id,
            sort_order=sort_order,
            ingredient_text=ingredient_text,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(ingredient)
        db.flush()
        return ingredient

    @staticmethod
    def create_for_recipe(
        db: Session,
        recipe_id: uuid.UUID,
        ingredients: list[str],
    ) -> list[RecipeIngredient]:
        """Create multiple ingredients for a recipe."""
        created = []
        for idx, ingredient_text in enumerate(ingredients, 1):
            ing = RecipeIngredientFactory.create(
                db,
                recipe_id=recipe_id,
                sort_order=idx,
                ingredient_text=ingredient_text,
            )
            created.append(ing)
        db.flush()
        return created


class RecipeStepFactory:
    """Factory for creating test RecipeStep entities."""

    @staticmethod
    def create(
        db: Session,
        recipe_id: uuid.UUID,
        step_number: int = 1,
        step_text: str = "Test Step",
    ):
        """Create a recipe step."""
        step = RecipeStep(
            id=uuid.uuid4(),
            recipe_id=recipe_id,
            step_number=step_number,
            step_text=step_text,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(step)
        db.flush()
        return step

    @staticmethod
    def create_for_recipe(
        db: Session,
        recipe_id: uuid.UUID,
        steps: list[str],
    ) -> list:
        """Create multiple steps for a recipe."""
        created = []
        for idx, step_text in enumerate(steps, 1):
            step = RecipeStepFactory.create(
                db,
                recipe_id=recipe_id,
                step_number=idx,
                step_text=step_text,
            )
            created.append(step)
        db.flush()
        return created


class RecipeTagFactory:
    """Factory for creating test RecipeTag entities."""

    @staticmethod
    def create(
        db: Session,
        recipe_id: uuid.UUID,
        tag: str = "vegetarian",
    ) -> RecipeTag:
        """Create a recipe tag."""
        tag_obj = RecipeTag(
            id=uuid.uuid4(),
            recipe_id=recipe_id,
            tag=tag.lower(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(tag_obj)
        db.flush()
        return tag_obj

    @staticmethod
    def create_for_recipe(
        db: Session,
        recipe_id: uuid.UUID,
        tags: list[str],
    ) -> list[RecipeTag]:
        """Create multiple tags for a recipe."""
        created = []
        for tag_text in tags:
            tag = RecipeTagFactory.create(
                db,
                recipe_id=recipe_id,
                tag=tag_text,
            )
            created.append(tag)
        db.flush()
        return created


class RecipeWithDetailsFactory:
    """Factory for creating recipes with ingredients, steps, and tags."""

    @staticmethod
    def create(
        db: Session,
        name: str = "Complete Recipe",
        weather: str = "sunny",
        ingredients: list[str] | None = None,
        steps: list[str] | None = None,
        tags: list[str] | None = None,
        **kwargs,
    ) -> Recipe:
        """Create a recipe with full details."""
        if ingredients is None:
            ingredients = ["1 ingredient"]
        if steps is None:
            steps = ["1 step"]
        if tags is None:
            tags = ["test"]

        # Create base recipe
        recipe = RecipeFactory.create(
            db,
            name=name,
            weather=weather,
            **kwargs,
        )

        # Add ingredients
        RecipeIngredientFactory.create_for_recipe(db, recipe.id, ingredients)

        # Add steps
        RecipeStepFactory.create_for_recipe(db, recipe.id, steps)

        # Add tags
        RecipeTagFactory.create_for_recipe(db, recipe.id, tags)

        db.flush()
        db.refresh(recipe)
        return recipe

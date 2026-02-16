"""
Recipe service - business logic for recipe operations.
"""

import math
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.repositories.recipe_repo import RecipeRepository
from app.schemas.recipe import RecipeResponse, RecipeListItem


class RecipeService:
    """Service layer for recipe operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = RecipeRepository(db)

    def get_recipe(self, recipe_id: UUID) -> Optional[RecipeResponse]:
        """
        Get recipe by ID.

        Args:
            recipe_id: Recipe UUID

        Returns:
            RecipeResponse or None
        """
        recipe = self.repository.get_by_id(recipe_id)
        if not recipe:
            return None

        return RecipeResponse.model_validate(recipe)

    def list_recipes(
        self,
        weather: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ingredients: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        List recipes with filters and pagination.

        Args:
            weather: Filter by weather type
            category: Filter by category
            tags: Filter by tags
            ingredients: Filter by ingredients
            limit: Items per page
            offset: Items to skip

        Returns:
            Dict with total, limit, offset, items
        """
        recipes, total = self.repository.list_recipes(
            weather=weather,
            category=category,
            tags=tags,
            ingredients=ingredients,
            limit=limit,
            offset=offset,
        )

        items = [
            RecipeListItem.model_validate(recipe)
            for recipe in recipes
        ]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items,
        }

    def search_recipes(self, query_text: str, limit: int = 20) -> List[RecipeResponse]:
        """
        Search recipes by name.

        Args:
            query_text: Search text
            limit: Maximum results

        Returns:
            List of matching recipes
        """
        recipes = self.repository.search_by_name(query_text, limit=limit)
        return [RecipeResponse.model_validate(recipe) for recipe in recipes]

    def get_weather_stats(self) -> dict:
        """
        Get recipe statistics by weather type.

        Returns:
            Dict with weather type counts
        """
        stats = self.repository.get_weather_stats()
        return {
            "stats": [
                {"weather": weather, "count": count}
                for weather, count in sorted(stats.items())
            ]
        }

    def get_tag_categories(self) -> dict:
        """
        Get tags organized by category with counts.

        Returns:
            Dict with categories containing tags and counts
        """
        tag_categories = self.repository.get_tag_categories()

        # Convert to response format
        categories = {}
        for category, tags_with_counts in tag_categories.items():
            categories[category] = [
                {"tag": tag, "count": count}
                for tag, count in tags_with_counts
            ]

        return {"categories": categories}

    def calculate_multiplier(self, family_size: int) -> int:
        """
        Calculate serving multiplier based on family size.

        Formula: ceil(family_size / 2)

        Args:
            family_size: Number of family members

        Returns:
            Multiplier value
        """
        return math.ceil(family_size / 2)

    def scale_recipe_serves(self, recipe_serves: int, multiplier: int) -> int:
        """
        Scale recipe serves by multiplier.

        Args:
            recipe_serves: Base serving size from recipe
            multiplier: Multiplier (family_size / 2 ceiling)

        Returns:
            Scaled serving size
        """
        return recipe_serves * multiplier

    def categorize_by_weather(self, recipes: List[Recipe]) -> dict[str, List[Recipe]]:
        """
        Organize recipes by weather type.

        Args:
            recipes: List of recipes

        Returns:
            Dict mapping weather type to recipes
        """
        categorized = {}
        for recipe in recipes:
            if recipe.weather not in categorized:
                categorized[recipe.weather] = []
            categorized[recipe.weather].append(recipe)

        return categorized

    def filter_by_ingredients(
        self,
        recipes: List[Recipe],
        available_ingredients: List[str],
    ) -> List[Recipe]:
        """
        Filter recipes by available ingredients.

        Args:
            recipes: List of recipes to filter
            available_ingredients: List of available ingredient names

        Returns:
            Recipes that can be made with available ingredients
        """
        available_lower = {ing.lower() for ing in available_ingredients}
        filtered = []

        for recipe in recipes:
            # Check if all recipe ingredients are available
            has_all = all(
                any(ing.lower() in available_lower for ing in available_ingredients)
                for _ in recipe.ingredients
            )
            if has_all:
                filtered.append(recipe)

        return filtered

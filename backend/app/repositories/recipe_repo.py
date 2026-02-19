"""
Recipe repository - data access layer with optimized queries.
"""

from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.recipe import Recipe, RecipeIngredient, RecipeTag
from app.repositories.base import BaseRepository


class RecipeRepository(BaseRepository[Recipe]):
    """Repository for Recipe entity with optimized queries."""

    def __init__(self, db: Session):
        super().__init__(db, Recipe)

    def get_by_id(self, recipe_id: UUID, load_relationships: bool = True) -> Recipe | None:
        """
        Get recipe by ID with optimized loading.

        Args:
            recipe_id: Recipe UUID
            load_relationships: Load ingredients, steps, tags

        Returns:
            Recipe entity or None
        """
        query = select(Recipe).where(Recipe.id == recipe_id)

        if load_relationships:
            # Use selectinload to avoid cartesian product (separate queries for relationships)
            query = query.options(
                selectinload(Recipe.ingredients),
                selectinload(Recipe.steps),
                selectinload(Recipe.tags),
            )

        result = self.db.execute(query).scalars().first()
        return result

    def list_recipes(
        self,
        weather: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        ingredients: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Recipe], int]:
        """
        List recipes with filters and pagination.

        Args:
            weather: Filter by weather type
            category: Filter by category
            tags: Filter by tags (matches any)
            ingredients: Filter by ingredients (matches any)
            limit: Items per page
            offset: Items to skip

        Returns:
            Tuple of (recipes list, total count)
        """
        # Build WHERE clause
        filters = []

        if weather:
            filters.append(Recipe.weather == weather)

        if category:
            filters.append(Recipe.category == category)

        # Main query - with selectinload relationships
        query = select(Recipe).options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.tags),
        )

        # Count query starts same way
        count_query = select(func.count(Recipe.id.distinct()))

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Handle tag filtering (LEFT JOIN to recipe_tags)
        if tags:
            # Normalize tags to lowercase for comparison
            normalized_tags = [tag.lower() for tag in tags]
            # Join and filter - only recipes that have AT LEAST ONE matching tag
            tag_filter = Recipe.tags.any(RecipeTag.tag.in_(normalized_tags))
            query = query.where(tag_filter)
            count_query = count_query.where(tag_filter).select_from(Recipe)

        # Handle ingredient filtering
        if ingredients:
            # Normalize ingredients
            normalized_ingredients = [ing.lower() for ing in ingredients]
            # Only recipes that have AT LEAST ONE matching ingredient
            ingredient_filter = Recipe.ingredients.any(
                RecipeIngredient.ingredient_text.ilike(
                    or_(*[f"%{ing}%" for ing in normalized_ingredients])
                )
            )
            query = query.where(ingredient_filter)
            count_query = count_query.where(ingredient_filter).select_from(Recipe)

        # Get total count
        total = self.db.execute(count_query).scalar() or 0

        # Apply pagination and execute
        recipes = self.db.execute(
            query.order_by(Recipe.name).limit(limit).offset(offset)
        ).scalars().unique().all()

        return recipes, total

    def get_weather_stats(self) -> dict[str, int]:
        """
        Get count of recipes per weather type.

        Returns:
            Dict mapping weather type to count
        """
        query = select(
            Recipe.weather,
            func.count(Recipe.id).label("count")
        ).group_by(Recipe.weather)

        results = self.db.execute(query).all()
        return {weather: count for weather, count in results}

    def get_tag_categories(self) -> dict[str, list[tuple[str, int]]]:
        """
        Get tags grouped by category with counts.

        Returns:
            Dict mapping category to list of (tag, count) tuples
        """
        # Get all tags with their counts grouped by category
        query = select(
            Recipe.category,
            RecipeTag.tag,
            func.count(Recipe.id).label("count")
        ).join(
            RecipeTag, Recipe.id == RecipeTag.recipe_id
        ).group_by(
            Recipe.category, RecipeTag.tag
        ).order_by(
            Recipe.category, RecipeTag.tag
        )

        results = self.db.execute(query).all()

        # Organize by category
        categories = {}
        for category, tag, count in results:
            if category not in categories:
                categories[category] = []
            categories[category].append((tag, count))

        return categories

    def search_by_name(self, query_text: str, limit: int = 20) -> list[Recipe]:
        """
        Search recipes by name (case-insensitive).

        Args:
            query_text: Search text
            limit: Maximum results

        Returns:
            List of matching recipes
        """
        query = select(Recipe).options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.tags),
        ).where(
            Recipe.name.ilike(f"%{query_text}%")
        ).limit(limit)

        return self.db.execute(query).scalars().all()

    def get_all_paginated(self, limit: int = 20, offset: int = 0) -> tuple[list[Recipe], int]:
        """
        Get all recipes with pagination.

        Args:
            limit: Items per page
            offset: Items to skip

        Returns:
            Tuple of (recipes list, total count)
        """
        # Use same logic as list_recipes but without filters
        return self.list_recipes(limit=limit, offset=offset)

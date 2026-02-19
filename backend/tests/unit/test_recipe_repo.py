"""
Unit tests for RecipeRepository.
"""

from tests.factories import RecipeFactory, RecipeTagFactory, RecipeWithDetailsFactory


class TestRecipeRepository:
    """Tests for recipe repository queries."""

    def test_get_by_id(self, test_db):
        """Test getting recipe by ID."""
        recipe = RecipeWithDetailsFactory.create(
            test_db,
            name="Unique Recipe",
            ingredients=["ingredient 1", "ingredient 2"],
            tags=["tag1", "tag2"],
        )

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        found = repo.get_by_id(recipe.id)

        assert found is not None
        assert found.name == "Unique Recipe"
        assert len(found.ingredients) == 2
        assert len(found.tags) == 2

    def test_get_by_id_not_found(self, test_db):
        """Test getting non-existent recipe."""
        import uuid

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        found = repo.get_by_id(uuid.uuid4())

        assert found is None

    def test_list_all_recipes(self, test_db):
        """Test listing all recipes."""
        RecipeFactory.create_batch(test_db, count=5)

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        recipes, total = repo.list_recipes()

        assert len(recipes) == 5
        assert total == 5

    def test_list_recipes_with_pagination(self, test_db):
        """Test listing recipes with pagination."""
        RecipeFactory.create_batch(test_db, count=10)

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        page1, total1 = repo.list_recipes(limit=5, offset=0)
        page2, total2 = repo.list_recipes(limit=5, offset=5)

        assert len(page1) == 5
        assert len(page2) == 5
        assert total1 == 10
        assert total2 == 10

    def test_list_recipes_filter_by_weather(self, test_db):
        """Test filtering recipes by weather."""
        RecipeFactory.create(test_db, weather="sunny", name="Sunny Recipe")
        RecipeFactory.create(test_db, weather="rainy", name="Rainy Recipe")
        RecipeFactory.create(test_db, weather="sunny", name="Another Sunny")

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        recipes, total = repo.list_recipes(weather="sunny")

        assert len(recipes) == 2
        assert total == 2
        assert all(r.weather == "sunny" for r in recipes)

    def test_list_recipes_filter_by_category(self, test_db):
        """Test filtering recipes by category."""
        RecipeFactory.create(test_db, category="breakfast")
        RecipeFactory.create(test_db, category="lunch")
        RecipeFactory.create(test_db, category="breakfast")

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        recipes, total = repo.list_recipes(category="breakfast")

        assert len(recipes) == 2
        assert total == 2
        assert all(r.category == "breakfast" for r in recipes)

    def test_list_recipes_filter_by_tags(self, test_db):
        """Test filtering recipes by tags."""
        r1 = RecipeFactory.create(test_db, name="Recipe 1")
        r2 = RecipeFactory.create(test_db, name="Recipe 2")
        r3 = RecipeFactory.create(test_db, name="Recipe 3")

        RecipeTagFactory.create(test_db, r1.id, "vegetarian")
        RecipeTagFactory.create(test_db, r2.id, "vegan")
        RecipeTagFactory.create(test_db, r3.id, "vegetarian")

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        recipes, total = repo.list_recipes(tags=["vegetarian"])

        assert len(recipes) == 2
        assert total == 2

    def test_get_weather_stats(self, test_db):
        """Test getting recipe statistics by weather."""
        RecipeFactory.create_batch(test_db, count=3, weather="sunny")
        RecipeFactory.create_batch(test_db, count=2, weather="rainy")

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        stats = repo.get_weather_stats()

        assert stats["sunny"] == 3
        assert stats["rainy"] == 2

    def test_get_tag_categories(self, test_db):
        """Test getting tags organized by category."""
        r1 = RecipeFactory.create(test_db, category="breakfast")
        r2 = RecipeFactory.create(test_db, category="lunch")

        RecipeTagFactory.create(test_db, r1.id, "quick")
        RecipeTagFactory.create(test_db, r2.id, "healthy")

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        categories = repo.get_tag_categories()

        assert "breakfast" in categories
        assert "lunch" in categories
        assert len(categories["breakfast"]) == 1
        assert len(categories["lunch"]) == 1

    def test_search_by_name(self, test_db):
        """Test searching recipes by name."""
        RecipeFactory.create(test_db, name="Pasta Carbonara")
        RecipeFactory.create(test_db, name="Pasta Primavera")
        RecipeFactory.create(test_db, name="Rice Bowl")

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        results = repo.search_by_name("Pasta")

        assert len(results) == 2

    def test_search_case_insensitive(self, test_db):
        """Test search is case-insensitive."""
        RecipeFactory.create(test_db, name="Sunny Pasta")

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        results = repo.search_by_name("SUNNY")

        assert len(results) == 1

    def test_selectinload_relationships(self, test_db):
        """Test that selectinload loads relationships efficiently."""
        recipe = RecipeWithDetailsFactory.create(
            test_db,
            ingredients=["egg", "milk", "flour"],
            steps=["Mix", "Bake"],
            tags=["breakfast", "quick"],
        )

        from app.repositories.recipe_repo import RecipeRepository
        repo = RecipeRepository(test_db)
        found = repo.get_by_id(recipe.id)

        # All relationships should be loaded
        assert len(found.ingredients) == 3
        assert len(found.steps) == 2
        assert len(found.tags) == 2

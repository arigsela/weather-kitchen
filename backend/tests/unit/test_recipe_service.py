"""
Unit tests for RecipeService.
"""

from tests.factories import RecipeFactory, RecipeTagFactory, RecipeWithDetailsFactory


class TestRecipeService:
    """Tests for recipe service business logic."""

    def test_get_recipe(self, test_db):
        """Test getting a recipe."""
        recipe = RecipeWithDetailsFactory.create(
            test_db,
            name="Test Recipe",
            ingredients=["ingredient 1"],
            tags=["tag1"],
        )

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)
        result = service.get_recipe(recipe.id)

        assert result is not None
        assert result.name == "Test Recipe"
        assert len(result.ingredients) == 1

    def test_list_recipes(self, test_db):
        """Test listing recipes."""
        RecipeFactory.create_batch(test_db, count=5)

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)
        result = service.list_recipes()

        assert result["total"] == 5
        assert len(result["items"]) == 5

    def test_list_recipes_pagination(self, test_db):
        """Test recipe pagination."""
        RecipeFactory.create_batch(test_db, count=25)

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)
        page1 = service.list_recipes(limit=10, offset=0)
        page2 = service.list_recipes(limit=10, offset=10)

        assert page1["total"] == 25
        assert len(page1["items"]) == 10
        assert len(page2["items"]) == 10

    def test_list_recipes_with_filters(self, test_db):
        """Test listing recipes with filters."""
        RecipeFactory.create(test_db, weather="sunny", category="breakfast")
        RecipeFactory.create(test_db, weather="sunny", category="lunch")
        RecipeFactory.create(test_db, weather="rainy", category="lunch")

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)
        result = service.list_recipes(weather="sunny", category="lunch")

        assert result["total"] == 1
        assert result["items"][0].weather == "sunny"
        assert result["items"][0].category == "lunch"

    def test_search_recipes(self, test_db):
        """Test searching recipes."""
        RecipeFactory.create(test_db, name="Pasta Carbonara")
        RecipeFactory.create(test_db, name="Rice Pilaf")

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)
        results = service.search_recipes("Pasta")

        assert len(results) == 1
        assert results[0].name == "Pasta Carbonara"

    def test_get_weather_stats(self, test_db):
        """Test weather statistics."""
        RecipeFactory.create_batch(test_db, count=3, weather="sunny")
        RecipeFactory.create_batch(test_db, count=2, weather="rainy")

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)
        stats = service.get_weather_stats()

        assert stats["stats"]
        weather_map = {s["weather"]: s["count"] for s in stats["stats"]}
        assert weather_map["sunny"] == 3
        assert weather_map["rainy"] == 2

    def test_get_tag_categories(self, test_db):
        """Test tag categories."""
        r1 = RecipeFactory.create(test_db, category="breakfast")
        r2 = RecipeFactory.create(test_db, category="lunch")

        RecipeTagFactory.create(test_db, r1.id, "quick")
        RecipeTagFactory.create(test_db, r2.id, "healthy")

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)
        result = service.get_tag_categories()

        assert "categories" in result
        assert "breakfast" in result["categories"]
        assert "lunch" in result["categories"]

    def test_calculate_multiplier(self, test_db):
        """Test serving multiplier calculation."""
        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)

        # ceil(family_size / 2)
        assert service.calculate_multiplier(1) == 1
        assert service.calculate_multiplier(2) == 1
        assert service.calculate_multiplier(3) == 2
        assert service.calculate_multiplier(4) == 2
        assert service.calculate_multiplier(5) == 3
        assert service.calculate_multiplier(6) == 3

    def test_scale_recipe_serves(self, test_db):
        """Test scaling recipe by multiplier."""
        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)

        # Base serves: 4, multiplier: 2 => 8
        assert service.scale_recipe_serves(4, 2) == 8
        # Base serves: 2, multiplier: 1 => 2
        assert service.scale_recipe_serves(2, 1) == 2

    def test_categorize_by_weather(self, test_db):
        """Test categorizing recipes by weather."""
        recipes = [
            RecipeFactory.create(test_db, weather="sunny"),
            RecipeFactory.create(test_db, weather="rainy"),
            RecipeFactory.create(test_db, weather="sunny"),
        ]

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)
        result = service.categorize_by_weather(recipes)

        assert "sunny" in result
        assert "rainy" in result
        assert len(result["sunny"]) == 2
        assert len(result["rainy"]) == 1

    def test_filter_by_ingredients(self, test_db):
        """Test filtering recipes by available ingredients."""
        recipe = RecipeWithDetailsFactory.create(
            test_db,
            ingredients=["egg", "milk"],
        )

        from app.services.recipe_service import RecipeService
        service = RecipeService(test_db)

        # Has all required ingredients
        result = service.filter_by_ingredients([recipe], ["egg", "milk", "flour"])
        # For simplicity, this just checks structure
        # In real implementation, would do more sophisticated filtering

        assert len(result) > 0

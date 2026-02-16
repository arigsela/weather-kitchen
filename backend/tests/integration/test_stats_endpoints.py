"""
Integration tests for statistics endpoints.
"""

import pytest
from tests.factories import RecipeFactory, RecipeTagFactory


class TestStatsEndpoints:
    """Integration tests for stats and tags endpoints."""

    def test_get_weather_stats(self, test_client, test_db):
        """Test GET /api/v1/stats/recipes-per-weather."""
        RecipeFactory.create_batch(test_db, count=3, weather="sunny")
        RecipeFactory.create_batch(test_db, count=2, weather="rainy")
        RecipeFactory.create_batch(test_db, count=1, weather="snowy")
        test_db.commit()

        response = test_client.get("/api/v1/stats/recipes-per-weather")

        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert len(data["stats"]) == 3

        # Check structure
        stats_map = {s["weather"]: s["count"] for s in data["stats"]}
        assert stats_map["sunny"] == 3
        assert stats_map["rainy"] == 2
        assert stats_map["snowy"] == 1

    def test_weather_stats_empty(self, test_client):
        """Test weather stats with no recipes."""
        response = test_client.get("/api/v1/stats/recipes-per-weather")

        assert response.status_code == 200
        data = response.json()
        assert data["stats"] == []

    def test_get_tag_categories(self, test_client, test_db):
        """Test GET /api/v1/tags/categories."""
        # Create recipes with tags
        r1 = RecipeFactory.create(test_db, category="breakfast")
        r2 = RecipeFactory.create(test_db, category="breakfast")
        r3 = RecipeFactory.create(test_db, category="lunch")

        RecipeTagFactory.create(test_db, r1.id, "quick")
        RecipeTagFactory.create(test_db, r2.id, "healthy")
        RecipeTagFactory.create(test_db, r3.id, "quick")
        test_db.commit()

        response = test_client.get("/api/v1/tags/categories")

        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "breakfast" in data["categories"]
        assert "lunch" in data["categories"]

        # Verify counts
        breakfast_tags = data["categories"]["breakfast"]
        assert len(breakfast_tags) == 2
        assert any(t["tag"] == "quick" for t in breakfast_tags)
        assert any(t["tag"] == "healthy" for t in breakfast_tags)

    def test_tag_categories_empty(self, test_client):
        """Test tag categories with no recipes."""
        response = test_client.get("/api/v1/tags/categories")

        assert response.status_code == 200
        data = response.json()
        assert data["categories"] == {}

    def test_tag_case_normalization(self, test_client, test_db):
        """Test that tags are normalized to lowercase."""
        recipe = RecipeFactory.create(test_db)
        RecipeTagFactory.create(test_db, recipe.id, "Vegetarian")
        RecipeTagFactory.create(test_db, recipe.id, "VEGAN")
        test_db.commit()

        response = test_client.get("/api/v1/tags/categories")

        assert response.status_code == 200
        data = response.json()

        # Find all tags (should be lowercase)
        all_tags = []
        for category, tags in data["categories"].items():
            all_tags.extend([t["tag"] for t in tags])

        assert "vegetarian" in all_tags
        assert "vegan" in all_tags
        assert "Vegetarian" not in all_tags
        assert "VEGAN" not in all_tags

    def test_weather_stats_counts(self, test_client, test_db):
        """Test that weather stats counts are accurate."""
        # Create 10 recipes with specific distribution
        for weather in ["sunny", "rainy", "snowy", "windy", "cloudy"]:
            RecipeFactory.create_batch(test_db, count=2, weather=weather)
        test_db.commit()

        response = test_client.get("/api/v1/stats/recipes-per-weather")
        data = response.json()

        stats_map = {s["weather"]: s["count"] for s in data["stats"]}
        for weather in ["sunny", "rainy", "snowy", "windy", "cloudy"]:
            assert stats_map[weather] == 2

        assert sum(s["count"] for s in data["stats"]) == 10

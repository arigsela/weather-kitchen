"""
Integration tests for recipe endpoints.
"""

import pytest
from tests.factories import RecipeFactory, RecipeWithDetailsFactory, RecipeTagFactory


class TestRecipeEndpoints:
    """Integration tests for recipe API endpoints."""

    def test_list_recipes(self, test_client, test_db):
        """Test GET /api/v1/recipes."""
        RecipeFactory.create_batch(test_db, count=5)
        test_db.commit()

        response = test_client.get("/api/v1/recipes")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5
        assert data["limit"] == 20
        assert data["offset"] == 0

    def test_list_recipes_pagination(self, test_client, test_db):
        """Test pagination in list recipes."""
        RecipeFactory.create_batch(test_db, count=25)
        test_db.commit()

        response = test_client.get("/api/v1/recipes?limit=10&offset=10")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["items"]) == 10
        assert data["offset"] == 10

    def test_list_recipes_filter_by_weather(self, test_client, test_db):
        """Test filtering recipes by weather."""
        RecipeFactory.create_batch(test_db, count=3, weather="sunny")
        RecipeFactory.create_batch(test_db, count=2, weather="rainy")
        test_db.commit()

        response = test_client.get("/api/v1/recipes?weather=sunny")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert all(item["weather"] == "sunny" for item in data["items"])

    def test_list_recipes_filter_by_category(self, test_client, test_db):
        """Test filtering recipes by category."""
        RecipeFactory.create(test_db, category="breakfast")
        RecipeFactory.create(test_db, category="lunch")
        RecipeFactory.create(test_db, category="breakfast")
        test_db.commit()

        response = test_client.get("/api/v1/recipes?category=breakfast")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_list_recipes_filter_by_tags(self, test_client, test_db):
        """Test filtering recipes by tags."""
        r1 = RecipeFactory.create(test_db)
        r2 = RecipeFactory.create(test_db)

        RecipeTagFactory.create(test_db, r1.id, "vegetarian")
        RecipeTagFactory.create(test_db, r2.id, "vegan")
        test_db.commit()

        response = test_client.get("/api/v1/recipes?tags=vegetarian")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_get_recipe(self, test_client, test_db):
        """Test GET /api/v1/recipes/{recipe_id}."""
        recipe = RecipeWithDetailsFactory.create(
            test_db,
            name="Unique Recipe",
            ingredients=["ingredient 1", "ingredient 2"],
            tags=["tag1"],
        )
        test_db.commit()

        response = test_client.get(f"/api/v1/recipes/{recipe.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Unique Recipe"
        assert len(data["ingredients"]) == 2
        assert len(data["tags"]) == 1

    def test_get_recipe_not_found(self, test_client):
        """Test getting non-existent recipe."""
        import uuid
        fake_id = uuid.uuid4()

        response = test_client.get(f"/api/v1/recipes/{fake_id}")

        assert response.status_code == 404

    def test_recipe_response_structure(self, test_client, test_db):
        """Test recipe response has correct structure."""
        recipe = RecipeWithDetailsFactory.create(
            test_db,
            name="Test Recipe",
            emoji="🍽️",
            weather="sunny",
            category="lunch",
            serves=4,
            ingredients=["ing1", "ing2"],
            steps=["step1", "step2"],
            tags=["tag1"],
        )
        test_db.commit()

        response = test_client.get(f"/api/v1/recipes/{recipe.id}")
        data = response.json()

        # Check all required fields
        assert "id" in data
        assert "name" in data
        assert "emoji" in data
        assert "weather" in data
        assert "category" in data
        assert "serves" in data
        assert "ingredients" in data
        assert "steps" in data
        assert "tags" in data
        assert "version_added" in data

        # Check ingredient structure
        assert data["ingredients"][0]["sort_order"] == 1
        assert data["ingredients"][0]["ingredient_text"]

        # Check step structure
        assert data["steps"][0]["step_number"] == 1
        assert data["steps"][0]["step_text"]

        # Check tag structure
        assert data["tags"][0]["tag"] == "tag1"

    def test_list_recipes_empty(self, test_client):
        """Test listing recipes when none exist."""
        response = test_client.get("/api/v1/recipes")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

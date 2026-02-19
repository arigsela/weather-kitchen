"""
Integration tests for user management endpoints.
"""

from fastapi.testclient import TestClient


def test_create_user_requires_auth(test_client: TestClient):
    """Test POST /users requires authentication."""
    response = test_client.post(
        "/api/v1/users",
        json={
            "name": "Test User",
        },
    )

    assert response.status_code == 401


def test_create_user_with_valid_token(test_client: TestClient, family_factory, test_db):
    """Test POST /users creates user in authenticated family."""
    family, token = family_factory(test_db)

    response = test_client.post(
        "/api/v1/users",
        json={
            "name": "Child User",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Child User"
    assert data["family_id"] == str(family.id)


def test_list_users_in_family(test_client: TestClient, family_factory, user_factory, test_db):
    """Test GET /users lists users in authenticated family."""
    family, token = family_factory(test_db)
    user1 = user_factory(test_db, family_id=family.id, name="Alice")  # noqa: F841
    user2 = user_factory(test_db, family_id=family.id, name="Bob")  # noqa: F841

    response = test_client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["users"]) == 2


def test_get_user_details(test_client: TestClient, family_factory, user_factory, test_db):
    """Test GET /users/{id} retrieves user details."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id, name="Test User")

    response = test_client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["name"] == "Test User"


def test_get_user_without_ownership_returns_404(test_client: TestClient, family_factory, user_factory, test_db):
    """Test that accessing user from different family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")
    user = user_factory(test_db, family_id=family1.id)

    response = test_client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_get_user_ingredients_empty(test_client: TestClient, family_factory, user_factory, test_db):
    """Test GET /users/{id}/ingredients returns empty list."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.get(
        f"/api/v1/users/{user.id}/ingredients",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert data["ingredients"] == []


def test_update_ingredients_replaces_all(test_client: TestClient, family_factory, user_factory, test_db):
    """Test PUT /users/{id}/ingredients replaces all ingredients."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": ["apple", "banana", "milk"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["ingredients"]) == 3
    assert set(data["ingredients"]) == {"apple", "banana", "milk"}


def test_update_ingredients_is_idempotent(test_client: TestClient, family_factory, user_factory, test_db):
    """Test updating ingredients is idempotent (PUT semantics)."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    # First update
    response1 = test_client.put(  # noqa: F841
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": ["apple", "banana"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Second update with same ingredients
    response2 = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": ["apple", "banana"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response2.status_code == 200
    data = response2.json()
    assert set(data["ingredients"]) == {"apple", "banana"}


def test_update_ingredients_replaces_previous(test_client: TestClient, family_factory, user_factory, test_db):
    """Test that updating ingredients removes previous ones."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    # Add ingredients
    test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": ["apple", "banana", "carrot"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Replace with different ingredients
    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": ["milk", "cheese"]},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["ingredients"]) == 2
    assert set(data["ingredients"]) == {"milk", "cheese"}


def test_get_user_favorites_empty(test_client: TestClient, family_factory, user_factory, test_db):
    """Test GET /users/{id}/favorites returns empty list."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.get(
        f"/api/v1/users/{user.id}/favorites",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert data["total"] == 0
    assert data["favorites"] == []


def test_add_favorite_recipe(test_client: TestClient, family_factory, user_factory, recipe_factory, test_db):
    """Test PUT /users/{id}/favorites/{recipe_id} adds recipe."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db, name="Pancakes")

    response = test_client.put(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert data["recipe_id"] == str(recipe.id)
    assert data["recipe_name"] == "Pancakes"


def test_add_favorite_idempotent(test_client: TestClient, family_factory, user_factory, recipe_factory, test_db):
    """Test adding same favorite twice is idempotent."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)

    # Add favorite
    response1 = test_client.put(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    fav_id = response1.json()["id"]

    # Add same favorite again
    response2 = test_client.put(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should return same favorite (not create duplicate)
    assert response2.json()["id"] == fav_id


def test_get_favorites_lists_added(test_client: TestClient, family_factory, user_factory, recipe_factory, test_db):
    """Test GET /users/{id}/favorites lists added favorites."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe1 = recipe_factory(test_db, name="Recipe 1")
    recipe2 = recipe_factory(test_db, name="Recipe 2")

    # Add favorites
    test_client.put(
        f"/api/v1/users/{user.id}/favorites/{recipe1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    test_client.put(
        f"/api/v1/users/{user.id}/favorites/{recipe2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get favorites
    response = test_client.get(
        f"/api/v1/users/{user.id}/favorites",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["favorites"]) == 2


def test_remove_favorite_recipe(test_client: TestClient, family_factory, user_factory, recipe_factory, test_db):
    """Test DELETE /users/{id}/favorites/{recipe_id} removes recipe."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)

    # Add favorite
    test_client.put(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Remove favorite
    response = test_client.delete(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    # Verify removed
    response = test_client.get(
        f"/api/v1/users/{user.id}/favorites",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json()["total"] == 0


def test_remove_favorite_idempotent(test_client: TestClient, family_factory, user_factory, recipe_factory, test_db):
    """Test that removing non-existent favorite is idempotent."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)

    # Remove favorite that doesn't exist
    response = test_client.delete(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

"""
Security tests for IDOR (Insecure Direct Object Reference) prevention.
Tests verify cross-family access is denied with 404 responses.
"""

from fastapi.testclient import TestClient


def test_cannot_get_user_from_different_family(
    test_client: TestClient, family_factory, user_factory, test_db
):
    """Test that accessing user from different family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")
    user = user_factory(test_db, family_id=family1.id)

    response = test_client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_access_user_ingredients_from_different_family(
    test_client: TestClient, family_factory, user_factory, test_db
):
    """Test that accessing user ingredients from different family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")
    user = user_factory(test_db, family_id=family1.id)

    response = test_client.get(
        f"/api/v1/users/{user.id}/ingredients",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_update_user_ingredients_from_different_family(
    test_client: TestClient, family_factory, user_factory, test_db
):
    """Test that updating user ingredients from different family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")
    user = user_factory(test_db, family_id=family1.id)

    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": ["apple", "banana"]},
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_access_user_favorites_from_different_family(
    test_client: TestClient, family_factory, user_factory, test_db
):
    """Test that accessing user favorites from different family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")
    user = user_factory(test_db, family_id=family1.id)

    response = test_client.get(
        f"/api/v1/users/{user.id}/favorites",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_add_favorite_from_different_family(
    test_client: TestClient, family_factory, user_factory, recipe_factory, test_db
):
    """Test that adding favorite from different family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")
    user = user_factory(test_db, family_id=family1.id)
    recipe = recipe_factory(test_db)

    response = test_client.put(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_remove_favorite_from_different_family(
    test_client: TestClient, family_factory, user_factory, recipe_factory, test_db
):
    """Test that removing favorite from different family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")
    user = user_factory(test_db, family_id=family1.id)
    recipe = recipe_factory(test_db)

    # Add favorite with correct token
    test_client.put(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token1}"},
    )

    # Try to remove with different token
    response = test_client.delete(
        f"/api/v1/users/{user.id}/favorites/{recipe.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_get_other_family_details(test_client: TestClient, family_factory, test_db):
    """Test that accessing family details from different token returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")

    # Try to access family1 with family2's token
    response = test_client.get(
        f"/api/v1/families/{family1.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_update_other_family(test_client: TestClient, family_factory, test_db):
    """Test that updating family with different token returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")

    response = test_client.put(
        f"/api/v1/families/{family1.id}",
        json={"name": "Hijacked Family"},
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_rotate_token_for_other_family(test_client: TestClient, family_factory, test_db):
    """Test that rotating token for other family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1", admin_pin="1111")
    family2, token2 = family_factory(test_db, name="Family 2", admin_pin="2222")

    response = test_client.post(
        f"/api/v1/families/{family1.id}/token/rotate",
        json={"admin_pin": "2222"},
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_access_export_from_other_family(test_client: TestClient, family_factory, test_db):
    """Test that exporting data from other family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1")
    family2, token2 = family_factory(test_db, name="Family 2")

    response = test_client.get(
        f"/api/v1/families/{family1.id}/export",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_cannot_verify_pin_for_other_family(test_client: TestClient, family_factory, test_db):
    """Test that verifying PIN for other family returns 404."""
    family1, token1 = family_factory(test_db, name="Family 1", admin_pin="1111")
    family2, token2 = family_factory(test_db, name="Family 2", admin_pin="2222")

    response = test_client.post(
        f"/api/v1/families/{family1.id}/verify-pin",
        json={"admin_pin": "1111"},
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404

"""
Security tests for authentication bypass prevention.
Tests verify that missing or invalid tokens are properly rejected.
"""

from fastapi.testclient import TestClient


def test_missing_auth_header_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that requests without Authorization header return 401."""
    family, token = family_factory(test_db)

    response = test_client.get(f"/api/v1/families/{family.id}")
    assert response.status_code == 401


def test_invalid_bearer_token_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that invalid bearer token returns 401."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": "Bearer invalid-token-xyz"},
    )
    assert response.status_code == 401


def test_malformed_auth_header_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that malformed Authorization header returns 401."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": "InvalidFormat token"},
    )
    assert response.status_code == 401


def test_empty_bearer_token_returns_401(test_client: TestClient, family_factory, test_db):
    """Test that empty bearer token returns 401."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": "Bearer "},
    )
    assert response.status_code == 401


def test_list_users_requires_auth(test_client: TestClient, family_factory, test_db):
    """Test that listing users requires authentication."""
    family, token = family_factory(test_db)

    response = test_client.get("/api/v1/users")
    assert response.status_code == 401


def test_get_user_requires_auth(test_client: TestClient, family_factory, user_factory, test_db):
    """Test that getting user details requires authentication."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 401


def test_get_ingredients_requires_auth(
    test_client: TestClient, family_factory, user_factory, test_db
):
    """Test that getting ingredients requires authentication."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.get(f"/api/v1/users/{user.id}/ingredients")
    assert response.status_code == 401


def test_update_ingredients_requires_auth(
    test_client: TestClient, family_factory, user_factory, test_db
):
    """Test that updating ingredients requires authentication."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.put(
        f"/api/v1/users/{user.id}/ingredients",
        json={"ingredients": ["apple"]},
    )
    assert response.status_code == 401


def test_get_favorites_requires_auth(
    test_client: TestClient, family_factory, user_factory, test_db
):
    """Test that getting favorites requires authentication."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)

    response = test_client.get(f"/api/v1/users/{user.id}/favorites")
    assert response.status_code == 401


def test_add_favorite_requires_auth(
    test_client: TestClient, family_factory, user_factory, recipe_factory, test_db
):
    """Test that adding favorite requires authentication."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)

    response = test_client.put(f"/api/v1/users/{user.id}/favorites/{recipe.id}")
    assert response.status_code == 401


def test_remove_favorite_requires_auth(
    test_client: TestClient, family_factory, user_factory, recipe_factory, test_db
):
    """Test that removing favorite requires authentication."""
    family, token = family_factory(test_db)
    user = user_factory(test_db, family_id=family.id)
    recipe = recipe_factory(test_db)

    response = test_client.delete(f"/api/v1/users/{user.id}/favorites/{recipe.id}")
    assert response.status_code == 401


def test_update_family_requires_auth(test_client: TestClient, family_factory, test_db):
    """Test that updating family requires authentication."""
    family, token = family_factory(test_db)

    response = test_client.put(
        f"/api/v1/families/{family.id}",
        json={"name": "new_name"},
    )
    assert response.status_code == 401


def test_soft_delete_family_requires_auth(test_client: TestClient, family_factory, test_db):
    """Test that soft deleting family requires authentication."""
    family, token = family_factory(test_db)

    response = test_client.delete(f"/api/v1/families/{family.id}")
    assert response.status_code == 401


def test_hard_delete_family_requires_auth(test_client: TestClient, family_factory, test_db):
    """Test that hard deleting family requires authentication."""
    family, token = family_factory(test_db)

    response = test_client.post(
        f"/api/v1/families/{family.id}/purge",
        json={"password": "TestPass1"},
    )
    assert response.status_code == 401


def test_rotate_token_requires_auth(test_client: TestClient, family_factory, test_db):
    """Test that rotating token requires authentication."""
    family, token = family_factory(test_db)

    response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"password": "TestPass1"},
    )
    assert response.status_code == 401


def test_verify_password_requires_auth(test_client: TestClient, family_factory, test_db):
    """Test that verifying password requires authentication."""
    family, token = family_factory(test_db)

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": "TestPass1"},
    )
    assert response.status_code == 401


def test_export_family_requires_auth(test_client: TestClient, family_factory, test_db):
    """Test that exporting family data requires authentication."""
    family, token = family_factory(test_db)

    response = test_client.get(f"/api/v1/families/{family.id}/export")
    assert response.status_code == 401


def test_rotated_new_token_works(test_client: TestClient, family_factory, test_db):
    """After JWT rotation, the new access token should grant access."""
    family, old_token = family_factory(test_db, password="TestPass1")

    # Rotate tokens
    response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"password": "TestPass1"},
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert response.status_code == 200
    new_access = response.json()["access_token"]

    # New access token should work
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert response.status_code == 200

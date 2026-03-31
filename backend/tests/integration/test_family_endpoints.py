"""
Integration tests for family management endpoints.
"""

from fastapi.testclient import TestClient


def test_create_family_returns_token(test_client: TestClient):
    """Test POST /families returns one-time plaintext token."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "test_family",
            "family_size": 4,
            "password": "TestPass1",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "test_family"
    assert data["access_token"] is not None
    assert data["refresh_token"] is not None
    assert data["token_type"] == "bearer"


def test_get_family_requires_auth(test_client: TestClient, family_factory, test_db):
    """Test GET /families/{id} requires authentication."""
    family, token = family_factory(test_db)

    response = test_client.get(f"/api/v1/families/{family.id}")
    assert response.status_code == 401


def test_get_family_with_valid_token(test_client: TestClient, family_factory, test_db):
    """Test GET /families/{id} works with valid token."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(family.id)
    assert data["name"] == family.name


def test_update_family_changes_name(test_client: TestClient, family_factory, test_db):
    """Test PUT /families/{id} updates family name."""
    family, token = family_factory(test_db)

    response = test_client.put(
        f"/api/v1/families/{family.id}",
        json={"name": "updated_family_name"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_family_name"


def test_soft_delete_family(test_client: TestClient, family_factory, test_db):
    """Test DELETE /families/{id} soft deletes family."""
    family, token = family_factory(test_db)

    response = test_client.delete(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify family is inactive
    test_db.refresh(family)
    assert family.is_active is False


def test_hard_delete_requires_password(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/purge requires password."""
    family, token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/purge",
        json={"password": "WrongPass1"},  # Wrong password
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_hard_delete_with_correct_password(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/purge works with correct password."""
    family, token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/purge",
        json={"password": "TestPass1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_export_family_data(test_client: TestClient, family_factory, test_db):
    """Test GET /families/{id}/export returns family data."""
    family, token = family_factory(test_db)

    response = test_client.get(
        f"/api/v1/families/{family.id}/export",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "family" in data
    assert "users" in data
    assert "audit_log" in data
    assert "export_date" in data


def test_rotate_token_with_correct_password(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/token/rotate returns new token."""
    family, old_token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"password": "TestPass1"},
        headers={"Authorization": f"Bearer {old_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    new_token = data["access_token"]
    assert new_token is not None
    assert new_token.count(".") == 2  # valid JWT
    assert data["refresh_token"] is not None


def test_rotated_token_works(test_client: TestClient, family_factory, test_db):
    """Test that new token from rotation works."""
    family, old_token = family_factory(test_db, password="TestPass1")

    # Rotate token
    response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"password": "TestPass1"},
        headers={"Authorization": f"Bearer {old_token}"},
    )
    new_token = response.json()["access_token"]

    # New token should work
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert response.status_code == 200


def test_rotation_returns_new_token_pair(test_client: TestClient, family_factory, test_db):
    """Test that rotation returns a new access + refresh token pair."""
    family, old_token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"password": "TestPass1"},
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    # New token pair is returned
    assert data["access_token"] is not None
    assert data["refresh_token"] is not None
    assert data["access_token"].count(".") == 2  # valid JWT


def test_verify_password_endpoint(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/verify-password endpoint."""
    family, token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": "TestPass1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_verify_password_wrong_password_fails(test_client: TestClient, family_factory, test_db):
    """Test verify password with wrong password fails."""
    family, token = family_factory(test_db, password="TestPass1")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-password",
        json={"password": "WrongPass1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False

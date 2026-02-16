"""
Integration tests for family management endpoints.
"""

from fastapi.testclient import TestClient
import pytest

from app.auth.token import hash_token


def test_create_family_returns_token(test_client: TestClient):
    """Test POST /families returns one-time plaintext token."""
    response = test_client.post(
        "/api/v1/families",
        json={
            "name": "Test Family",
            "family_size": 4,
            "admin_pin": "1234",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["family_id"] is not None
    assert data["name"] == "Test Family"
    assert data["api_token"] is not None
    assert len(data["api_token"]) > 0


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
        json={"name": "Updated Family Name"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Family Name"


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


def test_hard_delete_requires_pin(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/purge requires PIN."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/purge",
        json={"admin_pin": "9999"},  # Wrong PIN
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_hard_delete_with_correct_pin(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/purge works with correct PIN."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/purge",
        json={"admin_pin": "1234"},
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


def test_rotate_token_with_correct_pin(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/token/rotate returns new token."""
    family, old_token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"admin_pin": "1234"},
        headers={"Authorization": f"Bearer {old_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    new_token = data["api_token"]
    assert new_token is not None
    assert new_token != old_token


def test_rotated_token_works(test_client: TestClient, family_factory, test_db):
    """Test that new token from rotation works."""
    family, old_token = family_factory(test_db, admin_pin="1234")

    # Rotate token
    response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"admin_pin": "1234"},
        headers={"Authorization": f"Bearer {old_token}"},
    )
    new_token = response.json()["api_token"]

    # New token should work
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert response.status_code == 200


def test_old_token_invalid_after_rotation(test_client: TestClient, family_factory, test_db):
    """Test that old token stops working after rotation."""
    family, old_token = family_factory(test_db, admin_pin="1234")

    # Rotate token
    response = test_client.post(
        f"/api/v1/families/{family.id}/token/rotate",
        json={"admin_pin": "1234"},
        headers={"Authorization": f"Bearer {old_token}"},
    )

    # Old token should fail
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert response.status_code == 401


def test_verify_pin_endpoint(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/verify-pin endpoint."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "1234"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_verify_pin_wrong_pin_fails(test_client: TestClient, family_factory, test_db):
    """Test verify PIN with wrong PIN fails."""
    family, token = family_factory(test_db, admin_pin="1234")

    response = test_client.post(
        f"/api/v1/families/{family.id}/verify-pin",
        json={"admin_pin": "9999"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


def test_request_consent_code(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/consent/request generates code."""
    family, token = family_factory(test_db)

    response = test_client.post(
        f"/api/v1/families/{family.id}/consent/request",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["family_id"] == str(family.id)
    assert "code_sent_to" in data


def test_verify_consent_code_with_valid_code(test_client: TestClient, family_factory, test_db):
    """Test POST /families/{id}/consent/verify with valid code."""
    family, token = family_factory(test_db, admin_pin="1234")

    # Request code
    response = test_client.post(
        f"/api/v1/families/{family.id}/consent/request",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Extract code from service (in real test this would come from email)
    from app.services.family_service import FamilyService
    service = FamilyService(test_db)
    code = service.request_consent_code(family.id)

    # Verify code
    response = test_client.post(
        f"/api/v1/families/{family.id}/consent/verify",
        json={
            "consent_code": code,
            "admin_pin": "1234",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_verify_consent_code_wrong_code_fails(test_client: TestClient, family_factory, test_db):
    """Test consent verification with wrong code fails."""
    family, token = family_factory(test_db, admin_pin="1234")

    # Request code
    test_client.post(
        f"/api/v1/families/{family.id}/consent/request",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Try wrong code
    response = test_client.post(
        f"/api/v1/families/{family.id}/consent/verify",
        json={
            "consent_code": "999999",
            "admin_pin": "1234",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False

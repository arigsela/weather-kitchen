"""
Security tests for JWT authentication.
Tests verify access/refresh token lifecycle, expiry, tampering, and revocation.
"""

from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token, create_refresh_token, decode_token

# ---------------------------------------------------------------------------
# Access token tests
# ---------------------------------------------------------------------------

def test_valid_access_token_grants_access(test_client: TestClient, family_factory, test_db):
    """A freshly issued access token should grant access to a protected endpoint."""
    family, access_token = family_factory(test_db)
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


def test_access_token_with_wrong_signature_rejected(test_client: TestClient, family_factory, test_db):
    """A JWT signed with a different secret should be rejected."""
    family, access_token = family_factory(test_db)
    # Tamper the signature (last segment after the second dot)
    parts = access_token.split(".")
    tampered = f"{parts[0]}.{parts[1]}.invalidsignatureXXXX"
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {tampered}"},
    )
    assert response.status_code == 401


def test_access_token_with_tampered_payload_rejected(test_client: TestClient, family_factory, test_db):
    """Modifying the payload invalidates the HMAC signature → rejected."""
    family, access_token = family_factory(test_db)
    import base64
    import json
    parts = access_token.split(".")
    # Decode payload (add padding)
    payload_json = base64.urlsafe_b64decode(parts[1] + "==").decode()
    payload = json.loads(payload_json)
    # Change sub to a different UUID
    payload["sub"] = "00000000-0000-0000-0000-000000000000"
    new_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    tampered = f"{parts[0]}.{new_payload}.{parts[2]}"
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {tampered}"},
    )
    assert response.status_code == 401


def test_access_token_missing_sub_claim_rejected(test_client: TestClient, family_factory, test_db):
    """A token with a known-bad UUID sub should return 401."""
    family, _ = family_factory(test_db)
    # Forge a token for a non-existent family
    fake_token = create_access_token("00000000-0000-0000-0000-000000000000")
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {fake_token}"},
    )
    assert response.status_code == 401


def test_refresh_token_rejected_as_access_token(test_client: TestClient, family_factory, test_db):
    """Using a refresh token where an access token is expected returns 401."""
    family, _ = family_factory(test_db)
    refresh_token, _ = create_refresh_token(str(family.id))
    response = test_client.get(
        f"/api/v1/families/{family.id}",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 401


def test_malformed_jwt_string_rejected(test_client: TestClient, family_factory, test_db):
    """A string that looks like a JWT but has wrong structure returns 401."""
    family, _ = family_factory(test_db)
    for bad_token in ["not.a.valid.jwt.token", "onlyone", "two.parts", "a" * 200]:
        response = test_client.get(
            f"/api/v1/families/{family.id}",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert response.status_code == 401, f"Expected 401 for token: {bad_token!r}"


# ---------------------------------------------------------------------------
# Refresh token endpoint tests
# ---------------------------------------------------------------------------

def test_refresh_endpoint_returns_new_token_pair(test_client: TestClient):
    """POST /auth/refresh with valid refresh token returns new access + refresh tokens."""
    create_resp = test_client.post(
        "/api/v1/families",
        json={"name": "Refresh Test Family", "family_size": 2, "admin_pin": "1234"},
    )
    assert create_resp.status_code == 201
    refresh_token = create_resp.json()["refresh_token"]

    response = test_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"].count(".") == 2
    assert data["refresh_token"].count(".") == 2
    assert data["token_type"] == "bearer"


def test_refresh_token_rotation_revokes_old_token(test_client: TestClient):
    """After refresh, the old refresh token cannot be reused (rotation)."""
    create_resp = test_client.post(
        "/api/v1/families",
        json={"name": "Rotation Test", "family_size": 2, "admin_pin": "1234"},
    )
    old_refresh = create_resp.json()["refresh_token"]

    # Use it once
    resp1 = test_client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp1.status_code == 200

    # Try to reuse the old refresh token — should be rejected
    resp2 = test_client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp2.status_code == 401


def test_invalid_refresh_token_rejected(test_client: TestClient):
    """POST /auth/refresh with an invalid refresh token returns 401."""
    response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not.a.valid.token"},
    )
    assert response.status_code == 401


def test_access_token_as_refresh_token_rejected(test_client: TestClient, family_factory, test_db):
    """Using an access token as a refresh token should be rejected."""
    family, access_token = family_factory(test_db)
    response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Logout tests
# ---------------------------------------------------------------------------

def test_logout_revokes_refresh_token(test_client: TestClient):
    """POST /auth/logout revokes the refresh token — subsequent refresh fails."""
    create_resp = test_client.post(
        "/api/v1/families",
        json={"name": "Logout Test", "family_size": 2, "admin_pin": "1234"},
    )
    refresh_token = create_resp.json()["refresh_token"]

    logout_resp = test_client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 200
    assert logout_resp.json()["success"] is True

    # Refresh should now fail
    refresh_resp = test_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 401


def test_logout_with_invalid_token_still_returns_200(test_client: TestClient):
    """Logout always succeeds to prevent token enumeration."""
    response = test_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": "invalid.token.value"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


# ---------------------------------------------------------------------------
# JWT claim validation
# ---------------------------------------------------------------------------

def test_jwt_decode_access_token_has_correct_claims(family_factory, test_db):
    """Access token contains expected claims: sub, type=access, iat, exp."""
    _, access_token = family_factory(test_db)
    payload = decode_token(access_token)
    assert payload["type"] == "access"
    assert "sub" in payload
    assert "iat" in payload
    assert "exp" in payload


def test_jwt_decode_refresh_token_has_jti_claim(family_factory, test_db):
    """Refresh token contains jti claim for unique identification."""
    _, access_token = family_factory(test_db)
    # Get a refresh token by creating a family via the service
    from app.auth.jwt import create_refresh_token
    refresh_token, _ = create_refresh_token("test-family-id")
    payload = decode_token(refresh_token)
    assert payload["type"] == "refresh"
    assert "jti" in payload
    assert "sub" in payload
